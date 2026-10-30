"""The ONNX code path, exercised with a tiny stand-in model built on the fly.

The real model is only downloaded while the Docker image is built; the image
self-test (groschen.selftest) checks that one. This test makes sure the
loading, tokenizing, pooling and unloading code works without it.
"""

import numpy as np
import pytest

onnx = pytest.importorskip("onnx")
from onnx import TensorProto, helper, numpy_helper  # noqa: E402
from tokenizers import Tokenizer, models, pre_tokenizers  # noqa: E402

from groschen.categorize import embedder  # noqa: E402

WORDS = ["<pad>", "<unk>", "rewe", "edeka", "netflix", "spotify", "markt", "gmbh"]


@pytest.fixture
def tiny_model(tmp_path):
    vocab = {w: i for i, w in enumerate(WORDS)}
    tok = Tokenizer(models.WordLevel(vocab=vocab, unk_token="<unk>"))  # noqa: S106
    tok.pre_tokenizer = pre_tokenizers.Whitespace()
    tok.save(str(tmp_path / "tokenizer.json"))

    rng = np.random.default_rng(0)
    table = rng.normal(size=(len(WORDS), 384)).astype(np.float32)
    table[vocab["edeka"]] = table[vocab["rewe"]] + 0.05  # two supermarkets mean nearly the same thing
    graph = helper.make_graph(
        [helper.make_node("Gather", ["table", "input_ids"], ["last_hidden_state"])],
        "tiny",
        [
            helper.make_tensor_value_info("input_ids", TensorProto.INT64, ["b", "s"]),
            helper.make_tensor_value_info("attention_mask", TensorProto.INT64, ["b", "s"]),
        ],
        [helper.make_tensor_value_info("last_hidden_state", TensorProto.FLOAT, ["b", "s", 384])],
        [numpy_helper.from_array(table, "table")],
    )
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
    model.ir_version = 8
    (tmp_path / "onnx").mkdir()
    onnx.save(model, str(tmp_path / "onnx" / "model_quantized.onnx"))
    return tmp_path


def test_onnx_embedder(tiny_model, monkeypatch):
    found = embedder.find_model(tiny_model)
    assert found
    e = embedder.OnnxEmbedder(*found)
    vectors = e.embed(["rewe", "edeka markt", "netflix", "rewe rewe rewe"])
    assert vectors.shape == (4, 384)
    assert np.allclose(np.linalg.norm(vectors, axis=1), 1.0, atol=1e-5)
    assert vectors[0] @ vectors[3] == pytest.approx(1.0, abs=1e-5)  # padding doesn't change the meaning
    assert vectors[0] @ vectors[1] > vectors[0] @ vectors[2]
    assert e.loaded

    monkeypatch.setattr(embedder, "IDLE_UNLOAD_SECONDS", 0)
    e._maybe_unload()
    assert not e.loaded
    assert e.embed(["spotify"]).shape == (1, 384)  # loads again on demand
