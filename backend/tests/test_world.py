"""Money in other currencies, home countries, and bank files from outside Germany."""

import datetime as dt
import json

import pytest
from fastapi.testclient import TestClient

from groschen import db, fx, netguard, settings
from groschen.analytics import networth
from groschen.api import auth
from groschen.bank import csv_import, store, sync
from groschen.jobs import Job
from groschen.main import create_app

H = {"x-groschen": "1"}
ACCOUNT = {"name": "Alex", "username": "alex", "password": "correct horse"}

# Rates per euro, the way the ECB publishes them.
RATES = [
    ("USD", "2026-10-01", 1.10),
    ("USD", "2026-10-02", 1.12),
    ("USD", "2026-10-30", 1.08),
    ("GBP", "2026-10-01", 0.85),
    ("GBP", "2026-10-30", 0.86),
]

CHASE = b"""Transaction Date,Post Date,Description,Category,Type,Amount,Memo
10/30/2026,10/31/2026,STARBUCKS STORE 1234,Food & Drink,Sale,-5.75,
10/02/2026,10/03/2026,PAYROLL ACME INC,,Payment,"2,000.00",
10/01/2026,10/02/2026,AMAZON.COM*AB12,Shopping,Sale,-24.99,
"""

REVOLUT = b"""Type,Product,Started Date,Completed Date,Description,Amount,Fee,Currency,State,Balance
CARD_PAYMENT,Current,2026-10-01 09:12:00,2026-10-01 10:00:00,Pret A Manger,-6.50,0.00,GBP,COMPLETED,93.50
CARD_PAYMENT,Current,2026-10-30 09:12:00,,Tesco,-12.00,0.00,GBP,PENDING,
TOPUP,Current,2026-09-30 09:12:00,2026-09-30 09:13:00,Top-up,100.00,0.00,GBP,COMPLETED,100.00
"""

# Wells Fargo exports no header at all: date, amount, two empty columns, description.
WELLS = b""""10/30/2026","-42.10","*","","SAFEWAY #1234"
"10/29/2026","-8.00","*","","NETFLIX.COM"
"10/15/2026","1500.00","*","","DIRECT DEP ACME"
"""


@pytest.fixture
def client():
    auth._failures.clear()
    c = TestClient(create_app())
    assert c.post("/api/setup/account", json=ACCOUNT, headers=H).status_code == 200
    return c


def _rates(conn):
    fx.store(conn, RATES)


def _import_usd(raw: bytes = CHASE) -> int:
    """A US bank's file names no currency: the user says which one on the account."""
    r = sync.import_csv(Job(id="t", kind="import"), raw)
    with db.session() as conn:
        store.set_account_currency(conn, r["account_id"], "USD")
        fx.apply(conn)
    return r["account_id"]


# --- the ECB's files ---------------------------------------------------------------------


def test_reads_the_ecb_history_and_the_last_90_days():
    rows = fx.parse_history_csv("Date,USD,JPY,BGN,\n2026-10-30,1.0812,162.5,N/A,\n2026-10-29,1.08,162.1,N/A,\n")
    assert ("USD", "2026-10-30", 1.0812) in rows and ("JPY", "2026-10-29", 162.1) in rows
    assert not any(code == "BGN" for code, _, _ in rows)
    xml = b"""<?xml version="1.0" encoding="UTF-8"?>
<gesmes:Envelope xmlns:gesmes="http://www.gesmes.org/xml/2002-08-01" xmlns="http://www.ecb.int/vocabulary/2002-08-01/eurofxref">
<gesmes:subject>Reference rates</gesmes:subject>
<Cube><Cube time="2026-10-30"><Cube currency="USD" rate="1.0812"/><Cube currency="GBP" rate="0.8601"/></Cube>
<Cube time="2026-10-29"><Cube currency="USD" rate="1.0800"/></Cube></Cube></gesmes:Envelope>"""
    assert fx.parse_recent_xml(xml) == [
        ("USD", "2026-10-30", 1.0812),
        ("GBP", "2026-10-30", 0.8601),
        ("USD", "2026-10-29", 1.08),
    ]


def test_cross_rates_use_the_last_known_day():
    with db.session() as conn:
        _rates(conn)
        r = fx.Rates(conn, ["USD", "GBP"])
        assert r.factor("USD", "EUR", "2026-10-01") == pytest.approx(1 / 1.10)
        # A weekend takes Friday's rate; before the first day, the first one there is.
        assert r.factor("USD", "EUR", "2026-10-04") == pytest.approx(1 / 1.12)
        assert r.factor("USD", "EUR", "2020-01-01") == pytest.approx(1 / 1.10)
        assert r.factor("GBP", "USD", "2026-10-30") == pytest.approx(1.08 / 0.86)
        assert r.factor("JPY", "EUR", "2026-10-30") is None


# --- converting --------------------------------------------------------------------------


def test_a_dollar_account_is_converted_into_euros():
    with db.session() as conn:
        _rates(conn)
    account_id = _import_usd()
    with db.session() as conn:
        acc = db.one(conn.execute("SELECT currency, fx_ok FROM accounts WHERE id = ?", (account_id,)))
        assert acc == {"currency": "USD", "fx_ok": 1}
        rows = {
            x["counterparty"]: x
            for x in db.rows(
                conn.execute("SELECT date, amount, orig_amount, currency, fx_rate, counterparty FROM transactions")
            )
        }
    # Month first (10/30 can't be a day-first date), the description is the payee.
    pay = rows["PAYROLL ACME INC"]
    assert pay["date"] == "2026-10-02" and pay["orig_amount"] == 2000.0 and pay["currency"] == "USD"
    assert pay["amount"] == round(2000 / 1.12, 2)
    assert rows["STARBUCKS STORE 1234"]["amount"] == round(-5.75 / 1.08, 2)


def test_without_a_rate_the_account_is_listed_but_not_counted():
    account_id = _import_usd()
    with db.session() as conn:
        assert conn.execute("SELECT fx_ok FROM accounts WHERE id = ?", (account_id,)).fetchone()[0] == 0
        # The booking keeps what the bank booked; nothing is made up.
        assert conn.execute("SELECT amount FROM transactions WHERE counterparty LIKE 'PAYROLL%'").fetchone()[0] == 2000.0
        view = networth.overview(conn)
        assert view["net_worth"] == 0
        assert [a["counted"] for a in view["accounts"]] == [0]
        status = fx.status(conn)
        assert status["foreign"] == ["USD"] and status["uncounted"][0]["currency"] == "USD"
        # A rate arrives: now it counts.
        _rates(conn)
        fx.apply(conn)
        assert conn.execute("SELECT fx_ok FROM accounts WHERE id = ?", (account_id,)).fetchone()[0] == 1


def test_changing_the_home_currency_converts_the_other_way():
    with db.session() as conn:
        _rates(conn)
    _import_usd()
    with db.session() as conn:
        settings.put(conn, "currency", "USD")
        fx.apply(conn)
        row = db.one(
            conn.execute("SELECT amount, orig_amount, fx_rate FROM transactions WHERE counterparty LIKE 'PAYROLL%'")
        )
        assert row == {"amount": 2000.0, "orig_amount": None, "fx_rate": None}
        settings.put(conn, "currency", "GBP")
        fx.apply(conn)
        row = db.one(conn.execute("SELECT amount, orig_amount FROM transactions WHERE counterparty LIKE 'PAYROLL%'"))
        assert row["orig_amount"] == 2000.0 and row["amount"] == round(2000 / 1.12 * 0.85, 2)


def test_euro_money_is_left_alone(demo_data, run_job):
    from groschen import demo

    demo.load(today=dt.date(2026, 10, 30))
    with db.session() as conn:
        before = conn.execute("SELECT SUM(amount), COUNT(*) FROM transactions").fetchone()
        assert fx.apply(conn) == {"missing": [], "uncounted": 0}
        assert conn.execute("SELECT SUM(amount), COUNT(*) FROM transactions").fetchone() == before
        assert conn.execute("SELECT COUNT(*) FROM transactions WHERE orig_amount IS NOT NULL").fetchone()[0] == 0
        assert fx.needed(conn) == []


def test_rates_are_fetched_only_when_on_and_needed(run_job, monkeypatch):
    calls = []
    monkeypatch.setattr(fx, "history_fetcher", lambda: calls.append("history") or RATES)
    monkeypatch.setattr(fx, "recent_fetcher", lambda: calls.append("recent") or RATES[-2:])
    _import_usd()
    assert calls == []  # off until turned on
    with db.session() as conn:
        settings.put(conn, "online_rates", True)
        fx.apply_setting(conn)
    try:
        assert netguard.is_allowed(fx.HOST)
        fx.after_change()
        assert calls == ["history"]
        with db.session() as conn:
            assert conn.execute("SELECT MIN(fx_ok) FROM accounts").fetchone()[0] == 1
        fx.after_change()  # fetched a moment ago: not again
        assert calls == ["history"]
    finally:
        with db.session() as conn:
            settings.put(conn, "online_rates", False)
            fx.apply_setting(conn)
    assert not netguard.is_allowed(fx.HOST)


# --- bank files from anywhere ------------------------------------------------------------


def test_revolut_skips_pending_and_reads_the_currency_column():
    p = csv_import.parse(REVOLUT)
    assert [r["counterparty"] for r in p["rows"]] == ["Pret A Manger", "Top-up"]
    assert {r["currency"] for r in p["rows"]} == {"GBP"} and p["currency"] == "GBP"
    assert p["rows"][0]["date"] == "2026-10-01" and p["balance"] == 93.5


def test_currency_in_the_column_name_and_dutch_signs():
    raw = (
        b'"Datum","Naam / Omschrijving","Rekening","Tegenrekening","Code","Af Bij","Bedrag (EUR)",'
        b'"Mutatiesoort","Mededelingen"\n'
        b'"20261030","Albert Heijn 1234","NL20INGB0001234567","","BA","Af","12,34","Betaalautomaat","Pasvolgnr: 001"\n'
        b'"20261029","Werkgever BV","NL20INGB0001234567","","GT","Bij","2500,00","Overschrijving","Salaris"\n'
    )
    p = csv_import.parse(raw, default_currency="USD")
    shop, salary = p["rows"]
    assert shop == {**shop, "date": "2026-10-30", "amount": -12.34, "currency": "EUR", "counterparty": "Albert Heijn 1234"}
    assert salary["amount"] == 2500.0 and salary["purpose"] == "Salaris"


def test_amount_column_with_a_currency_code():
    raw = (
        b"Date,Description,Amount (USD),Running Bal.\n10/30/2026,SAFEWAY,-42.10,957.90\n10/01/2026,DEPOSIT,1000.00,1000.00\n"
    )
    p = csv_import.parse(raw)
    assert {r["currency"] for r in p["rows"]} == {"USD"}
    assert p["rows"][0]["amount"] == -42.1 and p["balance"] == 957.9


def test_day_first_slashes_follow_the_file_or_the_country():
    raw = b"Date,Description,Amount\n03/04/2026,A,-1.00\n05/06/2026,B,-2.00\n"
    assert csv_import.parse(raw)["rows"][0]["date"] == "2026-04-03"
    assert csv_import.parse(raw, month_first=True)["rows"][0]["date"] == "2026-03-04"
    # 13/04 can only be day first, whatever the country does.
    raw = b"Date,Description,Amount\n03/04/2026,A,-1.00\n13/04/2026,B,-2.00\n"
    assert csv_import.parse(raw, month_first=True)["rows"][0]["date"] == "2026-04-03"


def test_a_file_without_header_asks_once_and_is_remembered(client):
    r = client.post("/api/import/csv", files={"file": ("Checking1.csv", WELLS, "text/csv")}, headers=H)
    assert r.status_code == 422
    preview = r.json()["mapping"]
    assert preview["columns"] == [] and preview["width"] == 5 and preview["sample"][0][4] == "SAFEWAY #1234"
    mapping = {"date": 0, "amount": 1, "counterparty": 4, "currency_code": "USD"}
    with db.session() as conn:
        _rates(conn)
    r = client.post(
        "/api/import/csv",
        files={"file": ("Checking1.csv", WELLS, "text/csv")},
        data={"mapping": json.dumps(mapping)},
        headers=H,
    )
    assert r.status_code == 200, r.text
    assert r.json()["imported"] == 3
    with db.session() as conn:
        row = db.one(conn.execute("SELECT date, orig_amount, currency FROM transactions WHERE counterparty = 'NETFLIX.COM'"))
        assert row == {"date": "2026-10-29", "orig_amount": -8.0, "currency": "USD"}
    # The next file of the same kind imports by itself.
    newer = b'"10/31/2026","-3.50","*","","PEETS COFFEE"\n"10/30/2026","-42.10","*","","SAFEWAY #1234"\n'
    r = client.post("/api/import/csv", files={"file": ("Checking1.csv", newer, "text/csv")}, headers=H)
    assert r.status_code == 200, r.text
    assert r.json()["imported"] == 1


def test_not_a_table_at_all_is_still_refused(client):
    r = client.post("/api/import/csv", files={"file": ("notes.csv", b"just some words\n", "text/csv")}, headers=H)
    assert r.status_code == 400


def test_the_user_can_say_what_currency_an_account_is_in(client):
    with db.session() as conn:
        _rates(conn)
    r = sync.import_csv(Job(id="t", kind="import"), CHASE)
    assert client.patch(f"/api/accounts/{r['account_id']}", json={"currency": "XYZ"}, headers=H).status_code == 400
    assert client.patch(f"/api/accounts/{r['account_id']}", json={"currency": "usd"}, headers=H).status_code == 200
    acc = next(a for a in client.get("/api/accounts").json() if a["id"] == r["account_id"])
    assert acc["currency"] == "USD" and acc["fx_ok"] == 1
    items = client.get("/api/transactions").json()["items"]
    pay = next(i for i in items if i["counterparty"] == "PAYROLL ACME INC")
    assert pay["orig_amount"] == 2000.0 and pay["currency"] == "USD" and pay["amount"] == round(2000 / 1.12, 2)


def test_settings_take_a_country_and_currency(client):
    r = client.patch("/api/settings", json={"country": "US", "currency": "USD"}, headers=H)
    assert r.status_code == 200
    assert client.get("/api/status").json()["region"] == {"country": "US", "currency": "USD"}
    assert client.patch("/api/settings", json={"country": "XX"}, headers=H).status_code == 400
    assert client.patch("/api/settings", json={"currency": "ABC"}, headers=H).status_code == 400
    assert client.get("/api/settings").json()["fx"]["home"] == "USD"


def test_export_keeps_the_original_amount_and_adds_the_converted_one(client):
    with db.session() as conn:
        _rates(conn)
    _import_usd()
    text = client.get("/api/export/transactions.csv").content.decode("utf-8-sig")
    header, *lines = text.splitlines()
    assert header.endswith("Amount in EUR")
    payroll = next(line for line in lines if "PAYROLL" in line)
    assert ";2000,00;USD;" in payroll and payroll.endswith(f";{2000 / 1.12:.2f}".replace(".", ","))
