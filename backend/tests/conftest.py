import datetime as dt

import pytest

from groschen import config, db, jobs, security
from groschen.bank import sync
from groschen.categorize import embedder

TODAY = dt.date.today()


@pytest.fixture(autouse=True)
def data_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "groschen.db")
    monkeypatch.setattr(config, "KEY_PATH", tmp_path / "secret.key")
    monkeypatch.setattr(config, "BACKUP_DIR", tmp_path / "backups")
    monkeypatch.setattr(config, "STATIC_DIR", tmp_path / "static")
    security.reset_cache()
    embedder.set_embedder(embedder.HashingEmbedder())
    monkeypatch.setattr(sync, "session_factory", sync.FinTSSession)
    db.init()
    yield tmp_path
    security.reset_cache()


@pytest.fixture
def conn():
    with db.session() as c:
        yield c


@pytest.fixture
def demo_data():
    from groschen import demo

    return demo.build(TODAY)


@pytest.fixture
def run_job(monkeypatch):
    """Run background jobs in the calling thread so tests can check the result straight away."""

    def start(kind, fn, *args, **kwargs):
        job = jobs.run_inline(kind, fn, *args, **kwargs)
        jobs._jobs[job.id] = job
        return job

    monkeypatch.setattr(jobs, "start", start)
    return start
