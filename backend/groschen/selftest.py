"""Checks the finished image before it is published: ``python -m groschen.selftest``.

It loads the bundled model, categorizes a few German bank texts and makes sure
the network guard blocks a request to the internet. The GitHub build runs this
inside the image; if it fails, the image isn't pushed.
"""

import json
import socket
import sys
import tempfile
import time


def main() -> int:
    import os

    os.environ.setdefault("GROSCHEN_DATA", tempfile.mkdtemp())
    from pathlib import Path

    from . import config, db, netguard
    from .bank import sync
    from .categorize import embedder, engine

    netguard.install()
    sync.allow_bank_hosts()
    db.init()
    failures = []

    emb = embedder.get_embedder()
    print(f"Categorizer: {emb.label}")
    info_path = config.MODEL_DIR / "MODEL_INFO.json"
    if info_path.exists():
        info = json.loads(info_path.read_text())
        files = " ".join(f"{Path(k).name}={v}" for k, v in info["files"].items())
        print(f"Model: {info['repo']} revision {info['revision']} {files}")
        if not info.get("pinned"):
            # Shows up as a note on the GitHub build, ready to copy into model.lock.json.
            print(f"::notice title=Model not pinned yet::revision={info['revision']} {files}")
    if emb.name != "model":
        failures.append("the bundled model wasn't found or couldn't be loaded")

    samples = [
        ("Hofladen Sonnenfeld", "Kartenzahlung Gemuese und Eier", -23.40, {"Groceries"}),
        ("Kino Metropol", "Eintrittskarten Abendvorstellung", -24.0, {"Entertainment"}),
        ("Stadtapotheke am Markt", "Kartenzahlung", -12.95, {"Pharmacy"}),
        ("Tierarztpraxis Dr. Weber", "Behandlung Katze", -85.0, {"Doctor & health", "Hobbies"}),
    ]
    with db.session() as conn:
        c = engine.Categorizer(conn)
        started = time.monotonic()
        txs = [{"counterparty": cp, "purpose": p, "amount": a, "booking_text": "Lastschrift"} for cp, p, a, _ in samples]
        guesses = c.model_guesses(txs)
        elapsed = time.monotonic() - started
        for (cp, _, _, _expected), g in zip(samples, guesses):
            name = c.by_id.get(g.category_id, {}).get("name")
            print(f"  {cp:28} -> {name} ({g.confidence:.2f})")
        hits = sum(1 for (_, _, _, exp), g in zip(samples, guesses) if c.by_id.get(g.category_id, {}).get("name") in exp)
    print(f"Model: {hits}/{len(samples)} as expected in {elapsed:.2f}s")
    if hits < 2:
        failures.append("the model categorized too few sample texts correctly")

    try:
        socket.getaddrinfo("example.com", 443)
        failures.append("the network guard let a request to example.com through")
    except socket.gaierror:
        print("Network guard: blocks example.com")

    for f in failures:
        print(f"FAILED: {f}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
