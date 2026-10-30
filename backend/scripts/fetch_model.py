"""Download the categorizer model while the Docker image is built.

This runs once, on GitHub's build servers. The finished image contains the
model, so Groschen itself never downloads anything.

The model is a small multilingual sentence encoder (MiniLM, 12 layers,
int8-quantized ONNX, about 120 MB) that understands German and English
merchant names and booking texts.

``model.lock.json`` next to this folder pins the exact revision and the SHA-256
of every file. When a pin is empty (before the first build), the current
revision is looked up and the hashes are recorded instead of checked; the
self-test prints them so they can be written into the lock file.
"""

import hashlib
import json
import sys
import urllib.request
from pathlib import Path

LOCK = Path(__file__).resolve().parent.parent / "model.lock.json"


def _get(url: str):
    return urllib.request.urlopen(url, timeout=120)  # noqa: S310 - fixed https URLs on huggingface.co


def resolve_revision(repo: str, revision: str) -> str:
    if len(revision) == 40:
        return revision
    with _get(f"https://huggingface.co/api/models/{repo}/revision/{revision or 'main'}") as r:
        return json.load(r)["sha"]


def fetch(repo: str, revision: str, path: str, expected: str, target_dir: Path) -> str:
    url = f"https://huggingface.co/{repo}/resolve/{revision}/{path}"
    target = target_dir / Path(path).name
    target.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    with _get(url) as response, open(target, "wb") as out:
        while chunk := response.read(1 << 20):
            digest.update(chunk)
            out.write(chunk)
    actual = digest.hexdigest()
    print(f"{path}: {target.stat().st_size / 1e6:.1f} MB sha256={actual}")
    if expected and actual != expected:
        target.unlink()
        sys.exit(f"Checksum mismatch for {path}: expected {expected}, got {actual}")
    return actual


def main() -> None:
    target_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "model")
    lock = json.loads(LOCK.read_text())
    revision = resolve_revision(lock["repo"], lock.get("revision", ""))
    if lock.get("revision") and revision != lock["revision"]:
        sys.exit("Model revision doesn't match the lock file")
    hashes = {path: fetch(lock["repo"], revision, path, expected, target_dir) for path, expected in lock["files"].items()}
    info = {"repo": lock["repo"], "revision": revision, "files": hashes, "pinned": all(lock["files"].values())}
    (target_dir / "MODEL_INFO.json").write_text(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
