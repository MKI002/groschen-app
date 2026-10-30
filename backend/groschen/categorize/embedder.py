"""Text embeddings for the built-in categorizer.

The Docker image ships a small multilingual sentence model (quantized ONNX,
about 120 MB) that runs on the CPU. It is loaded when there is work to do and
unloaded again after a short idle time, so it only costs memory for a few
seconds after each sync.

If the model files are missing (for example when running the tests), a simple
character n-gram embedder is used instead. It understands spelling, not meaning,
so the categorizer is more cautious with it.
"""

import threading
import time
import zlib
from pathlib import Path

import numpy as np

from .. import config

IDLE_UNLOAD_SECONDS = 90
MAX_TOKENS = 64


class HashingEmbedder:
    name = "fallback"
    label = "Spelling-based matcher (built-in model not found)"
    high = 0.55
    low = 0.38
    dim = 2048

    def embed(self, texts: list[str]) -> np.ndarray:
        out = np.zeros((len(texts), self.dim), dtype=np.float32)
        for row, text in enumerate(texts):
            t = f"  {text.lower()}  "
            for n in (3, 4, 5):
                for i in range(len(t) - n + 1):
                    gram = t[i : i + n]
                    if gram.strip():
                        out[row, zlib.crc32(gram.encode("utf-8")) % self.dim] += 1.0
            for word in text.lower().split():
                out[row, zlib.crc32(("w:" + word).encode("utf-8")) % self.dim] += 2.0
        norms = np.linalg.norm(out, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return out / norms


class OnnxEmbedder:
    name = "model"
    label = "Built-in model (multilingual MiniLM, runs on the CPU)"
    high = 0.62
    low = 0.45

    def __init__(self, model_path: Path, tokenizer_path: Path):
        self.model_path = model_path
        self.tokenizer_path = tokenizer_path
        self._session = None
        self._tokenizer = None
        self._inputs: list[str] = []
        self._lock = threading.Lock()
        self._last_used = 0.0
        self._timer: threading.Timer | None = None

    def _load(self) -> None:
        import onnxruntime as ort
        from tokenizers import Tokenizer

        opts = ort.SessionOptions()
        # The server also runs Jellyfin, Tdarr and friends: stay on two threads.
        opts.intra_op_num_threads = 2
        opts.inter_op_num_threads = 1
        self._session = ort.InferenceSession(str(self.model_path), sess_options=opts, providers=["CPUExecutionProvider"])
        self._inputs = [i.name for i in self._session.get_inputs()]
        tok = Tokenizer.from_file(str(self.tokenizer_path))
        pad_id = tok.token_to_id("<pad>")
        if pad_id is None:
            pad_id = tok.token_to_id("[PAD]") or 0
        tok.enable_truncation(max_length=MAX_TOKENS)
        tok.enable_padding(pad_id=pad_id)
        self._tokenizer = tok

    def _schedule_unload(self) -> None:
        if self._timer:
            self._timer.cancel()
        self._timer = threading.Timer(IDLE_UNLOAD_SECONDS, self._maybe_unload)
        self._timer.daemon = True
        self._timer.start()

    def _maybe_unload(self) -> None:
        with self._lock:
            if time.monotonic() - self._last_used >= IDLE_UNLOAD_SECONDS - 1:
                self._session = None
                self._tokenizer = None

    @property
    def loaded(self) -> bool:
        return self._session is not None

    def embed(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, 384), dtype=np.float32)
        with self._lock:
            if self._session is None:
                self._load()
            chunks = []
            for start in range(0, len(texts), 64):
                batch = texts[start : start + 64]
                enc = self._tokenizer.encode_batch(batch)
                ids = np.array([e.ids for e in enc], dtype=np.int64)
                mask = np.array([e.attention_mask for e in enc], dtype=np.int64)
                feed = {}
                if "input_ids" in self._inputs:
                    feed["input_ids"] = ids
                if "attention_mask" in self._inputs:
                    feed["attention_mask"] = mask
                if "token_type_ids" in self._inputs:
                    feed["token_type_ids"] = np.zeros_like(ids)
                hidden = self._session.run(None, feed)[0]
                if hidden.ndim == 2:  # model already pooled
                    pooled = hidden
                else:
                    m = mask[:, :, None].astype(np.float32)
                    pooled = (hidden * m).sum(axis=1) / np.clip(m.sum(axis=1), 1e-9, None)
                chunks.append(pooled.astype(np.float32))
            self._last_used = time.monotonic()
        self._schedule_unload()
        out = np.vstack(chunks)
        norms = np.linalg.norm(out, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return out / norms


_embedder = None
_embedder_lock = threading.Lock()


def find_model(model_dir: Path | None = None) -> tuple[Path, Path] | None:
    base = Path(model_dir or config.MODEL_DIR)
    tokenizer = base / "tokenizer.json"
    for name in ("model_quantized.onnx", "model.onnx"):
        for candidate in (base / name, base / "onnx" / name):
            if candidate.exists() and tokenizer.exists():
                return candidate, tokenizer
    return None


def get_embedder():
    global _embedder
    with _embedder_lock:
        if _embedder is None:
            found = find_model()
            if found:
                try:
                    import onnxruntime  # noqa: F401
                    import tokenizers  # noqa: F401

                    _embedder = OnnxEmbedder(*found)
                except ImportError:
                    _embedder = HashingEmbedder()
            else:
                _embedder = HashingEmbedder()
        return _embedder


def set_embedder(embedder) -> None:
    """Swap the embedder (tests)."""
    global _embedder
    _embedder = embedder


def status() -> dict:
    emb = get_embedder()
    return {"kind": emb.name, "label": emb.label, "loaded": getattr(emb, "loaded", True)}
