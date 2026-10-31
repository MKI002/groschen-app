import string

import pytest
from fastapi.testclient import TestClient

from groschen import demo, i18n
from groschen.api import auth
from groschen.bank import sync
from groschen.categorize.seed import CATEGORY_TREE
from groschen.main import create_app

H = {"x-groschen": "1"}
DE = {**H, "x-groschen-lang": "de"}
ACCOUNT = {"name": "Alex", "username": "alex", "password": "correct horse"}


@pytest.fixture
def client():
    auth._failures.clear()
    return TestClient(create_app())


@pytest.fixture
def german():
    token = i18n.use("de")
    yield
    i18n.reset(token)


def _fields(text: str) -> list[str]:
    return sorted(f for _, f, _, _ in string.Formatter().parse(text) if f)


def test_every_german_template_keeps_its_placeholders():
    for en, de in i18n.DE.items():
        assert _fields(en) == _fields(de), en


def test_every_built_in_category_has_a_german_name():
    names = {g for g, *_ in CATEGORY_TREE} | {c for *_, cats in CATEGORY_TREE for c in cats}
    assert names - set(i18n.CATEGORY_NAMES["de"]) == set()


def test_filled_in_messages_are_translated(german):
    assert i18n.tr("ING returned an error: Zugang gesperrt") == "ING hat einen Fehler gemeldet: Zugang gesperrt"
    assert i18n.tr("Connecting to ING") == "Verbinde mit ING"
    assert i18n.tr("Something only the bank says") == "Something only the bank says"


def test_errors_follow_the_page_language(client):
    client.post("/api/setup/account", json=ACCOUNT, headers=H)
    wrong = {"username": "alex", "password": "nope"}
    assert client.post("/api/login", json=wrong, headers=H).json()["detail"] == "Wrong username or password."
    assert client.post("/api/login", json=wrong, headers=DE).json()["detail"] == "Benutzername oder Passwort falsch."
    assert client.get("/api/nothing-here", headers=DE).json()["detail"] == "Nicht gefunden."


def test_job_messages_follow_the_page_language(client, run_job, demo_data, monkeypatch):
    client.post("/api/setup/account", json=ACCOUNT, headers=H)
    monkeypatch.setattr(sync, "session_factory", demo.FakeBank(demo_data))
    job = client.post("/api/bank/test", json={"login": "123", "pin": "wrong", "product_id": "ABCDEF123"}, headers=H).json()
    assert job["error"].startswith("ING didn't accept")
    again = client.get(f"/api/jobs/{job['id']}", headers=DE).json()
    assert again["error"].startswith("ING hat Anmeldename oder PIN nicht akzeptiert")
    assert again["steps"][0]["label"] == "Verbinde mit ING"


def test_language_is_saved_and_shown_before_login(client):
    client.post("/api/setup/account", json=ACCOUNT, headers=H)
    assert client.patch("/api/settings", json={"language": "fr"}, headers=H).status_code == 400
    assert client.patch("/api/settings", json={"language": "de"}, headers=H).status_code == 200
    client.post("/api/logout", headers=H)
    assert client.get("/api/status").json()["language"] == "de"


def test_export_uses_the_chosen_language(client, run_job, demo_data):
    client.post("/api/setup/account", json=ACCOUNT, headers=H)
    csv = demo.ing_csv(demo.GIRO_IBAN, "Girokonto", 0, demo_data["giro"][:40])
    client.post("/api/import/csv", files={"file": ("Umsatzanzeige.csv", csv, "text/csv")}, headers=H)
    text = client.get("/api/export/transactions.csv?lang=de").content.decode("utf-8-sig")
    assert text.startswith("Datum;Konto;Betrag")
    assert client.get("/api/export/transactions.csv").content.decode("utf-8-sig").startswith("Date;Account")
