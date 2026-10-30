import datetime as dt

import pytest
from fastapi.testclient import TestClient

from groschen import db, settings
from groschen.analytics import alerts, paydays, upcoming
from groschen.main import create_app

TODAY = dt.date(2026, 9, 28)  # a Monday
H = {"x-groschen": "1"}


def _cat(conn, name):
    return conn.execute("SELECT id FROM categories WHERE name = ?", (name,)).fetchone()[0]


def _account(conn, kind="checking", balance=2000.0, balance_date=TODAY):
    cur = conn.execute(
        "INSERT INTO accounts (kind, name, balance, balance_date, created_at) VALUES (?, ?, ?, ?, ?)",
        (kind, kind.title(), balance, balance_date.isoformat(), db.now_iso()),
    )
    return cur.lastrowid


def _tx(conn, account, date, amount, counterparty, purpose="", category=None):
    cur = conn.execute(
        "INSERT INTO transactions (account_id, date, amount, counterparty, purpose, fingerprint, source, category_id, "
        "created_at) VALUES (?, ?, ?, ?, ?, ?, 'test', ?, ?)",
        (
            account,
            date.isoformat() if isinstance(date, dt.date) else date,
            amount,
            counterparty,
            purpose,
            f"{counterparty}-{date}-{amount}-{purpose}",
            _cat(conn, category) if category else None,
            db.now_iso(),
        ),
    )
    return cur.lastrowid


def _months_back(n):
    """The first day of each of the last ``n`` months, oldest first, ending with this month."""
    out, d = [], TODAY.replace(day=1)
    for _ in range(n):
        out.append(d)
        d = (d - dt.timedelta(days=1)).replace(day=1)
    return out[::-1]


@pytest.fixture
def household(conn):
    giro = _account(conn)
    for m in _months_back(6):
        _tx(conn, giro, m.replace(day=26), 3000.0, "Nordlicht GmbH", "Gehalt", "Salary")
        _tx(conn, giro, m.replace(day=1), -900.0, "Hausverwaltung", "Miete", "Rent")
        _tx(conn, giro, m.replace(day=6), -13.99, "Netflix", "Abo", "Streaming")
        _tx(conn, giro, m.replace(day=2), -500.0, "Me", "Sparen", "Savings")
        _tx(conn, giro, m.replace(day=10), -60.0, "REWE", "Einkauf", "Groceries")
    # The September salary came early, on Friday the 25th.
    conn.execute("UPDATE transactions SET date = '2026-09-25' WHERE date = '2026-09-26'")
    conn.commit()
    return giro


def test_next_payday_after_an_early_salary(household, conn):
    p = paydays.next_payday(conn, TODAY)
    assert p["date"] == "2026-10-26" and p["late"] is False and p["amount"] == 3000.0


def test_a_late_salary_is_still_expected(household, conn):
    p = paydays.next_payday(conn, dt.date(2026, 10, 28))
    assert p["date"] == "2026-10-26" and p["late"] is True


def test_available_until_payday(household, conn):
    a = upcoming.available(conn, TODAY)
    names = [(e["date"], e["name"]) for e in a["upcoming"]]
    # Rent, the savings order and Netflix are still to come; groceries are not fixed costs.
    assert ("2026-10-01", "Hausverwaltung") in names
    assert ("2026-10-02", "Sparen") in names
    assert ("2026-10-06", "Netflix") in names
    assert not any(n == "REWE" for _, n in names)
    assert a["fixed_total"] == pytest.approx(1413.99)
    assert a["available"] == pytest.approx(2000 - 1413.99)
    assert a["days"] == 28 and a["per_day"] == pytest.approx((2000 - 1413.99) / 28, abs=0.01)
    # The salary month began with the (early) September salary.
    assert a["since"] == "2026-09-25" and a["until"] == "2026-10-26"

    settings.put(conn, "safe_buffer", 200)
    assert upcoming.available(conn, TODAY)["available"] == pytest.approx(2000 - 1413.99 - 200)


def test_salary_month_without_a_salary(conn):
    _account(conn)
    a = upcoming.available(conn, TODAY)
    assert a["payday"] is None and a["since"] == "2026-09-01" and a["until"] == "2026-10-01"


def test_available_without_a_girokonto(conn):
    assert upcoming.available(conn, TODAY) == {"has_account": False}


def test_month_calendar(household, conn):
    sep = upcoming.month_calendar(conn, "2026-09", TODAY)
    assert {e["status"] for e in sep["entries"]} == {"paid"}
    assert sep["total"] == pytest.approx(1413.99) and sep["income"] == 3000.0

    oct_ = upcoming.month_calendar(conn, "2026-10", TODAY)
    assert {e["status"] for e in oct_["entries"]} == {"expected"}
    assert oct_["expected"] == pytest.approx(1413.99)
    assert [e["date"] for e in oct_["entries"] if e["kind"] == "income"] == ["2026-10-26"]

    # A month further out gets the salary from its usual day, moved off the weekend (29 Nov is a Sunday: 26th is Thursday).
    nov = upcoming.month_calendar(conn, "2026-11", TODAY)
    assert [e["date"] for e in nov["entries"] if e["kind"] == "income"] == ["2026-11-26"]


def test_duplicate_charge(household, conn):
    giro = household
    a = _tx(conn, giro, "2026-09-20", -49.99, "Zalando SE", "Bestellung 1", "Clothing")
    b = _tx(conn, giro, "2026-09-21", -49.99, "Zalando SE", "Bestellung 2", "Clothing")
    found = [x for x in alerts.find(conn, TODAY) if x["kind"] == "duplicate"]
    assert [x["tx_ids"] for x in found] == [[a, b]]

    # Refunded: no hint.
    _tx(conn, giro, "2026-09-24", 49.99, "Zalando SE", "Erstattung", "Clothing")
    assert not [x for x in alerts.find(conn, TODAY) if x["kind"] == "duplicate"]


def test_no_duplicate_hint_for_everyday_or_frequent_purchases(household, conn):
    giro = household
    _tx(conn, giro, "2026-09-20", -6.34, "VISA E-CENTER MUSTERMANN", "", "Groceries")
    _tx(conn, giro, "2026-09-21", -6.34, "VISA E-CENTER MUSTERMANN", "", "Groceries")
    # A shop paid all the time: the same amount twice is no surprise.
    for d in range(1, 8):
        _tx(conn, giro, f"2026-09-0{d}", -9.0 - d, "Kiosk am Eck", f"Kauf {d}", "Hobbies")
    _tx(conn, giro, "2026-09-15", -12.5, "Kiosk am Eck", "Kauf a", "Hobbies")
    _tx(conn, giro, "2026-09-16", -12.5, "Kiosk am Eck", "Kauf b", "Hobbies")
    # Two card payments a day apart are two purchases; twice on the same day looks like a double charge.
    _tx(conn, giro, "2026-09-22", -39.9, "VISA SPORTHAUS MUSTER", "", "Hobbies")
    _tx(conn, giro, "2026-09-23", -39.9, "VISA SPORTHAUS MUSTER", "", "Hobbies")
    a = _tx(conn, giro, "2026-09-24", -19.9, "VISA BUCHLADEN MUSTER", "1", "Hobbies")
    b = _tx(conn, giro, "2026-09-24", -19.9, "VISA BUCHLADEN MUSTER", "2", "Hobbies")
    assert [x["tx_ids"] for x in alerts.find(conn, TODAY) if x["kind"] == "duplicate"] == [[a, b]]


def test_unusual_needs_a_steady_merchant(household, conn):
    giro = household
    for d, amount in (("06-03", 12.99), ("06-20", 40.98), ("07-11", 116.84), ("08-02", 17.99), ("08-30", 28.99)):
        _tx(conn, giro, f"2026-{d}", -amount, "AMAZON EU S.A R.L.", d, "Online shopping")
    _tx(conn, giro, "2026-09-10", -89.99, "AMAZON EU S.A R.L.", "x", "Online shopping")  # within what is paid there
    big = _tx(conn, giro, "2026-09-20", -599.0, "AMAZON EU S.A R.L.", "y", "Online shopping")
    paypal = "PayPal Europe S.a.r.l. et Cie S.C.A"
    for d in ("2026-06-05", "2026-07-05", "2026-08-05"):
        _tx(conn, giro, d, -15.0, paypal, d)
    _tx(conn, giro, "2026-09-12", -218.95, paypal, "z")  # PayPal without the shop: nothing to compare with
    found = [(x["tx_id"], x["basis"]) for x in alerts.find(conn, TODAY) if x["kind"] == "unusual"]
    assert found == [(big, "merchant")]


def test_unusual_amount_and_dismiss(household, conn):
    giro = household
    for i in range(4):
        _tx(conn, giro, f"2026-0{4 + i}-15", -30.0, "Stadtwerke", "Abschlag", "Energy")
    big = _tx(conn, giro, "2026-09-15", -180.0, "Stadtwerke", "Nachzahlung", "Energy")
    found = [x for x in alerts.find(conn, TODAY) if x["kind"] == "unusual"]
    assert [(x["tx_id"], x["basis"], x["usual"]) for x in found] == [(big, "merchant", 30.0)]
    # A one-off back payment is not also a price rise.
    assert not [x for x in alerts.find(conn, TODAY) if x["kind"] == "price_up"]

    alerts.dismiss(conn, found[0]["key"])
    assert not [x for x in alerts.find(conn, TODAY) if x["kind"] == "unusual"]
    alerts.restore_all(conn)
    assert [x for x in alerts.find(conn, TODAY) if x["kind"] == "unusual"]

    settings.put(conn, "alert_unusual", False)
    assert not [x for x in alerts.find(conn, TODAY) if x["kind"] == "unusual"]


def test_large_payment_to_a_new_merchant(household, conn):
    tx = _tx(conn, household, "2026-09-20", -899.0, "MediaMarkt", "Fernseher", "Electronics")
    found = [x for x in alerts.find(conn, TODAY) if x["kind"] == "unusual"]
    assert [(x["tx_id"], x["basis"]) for x in found] == [(tx, "new")]
    settings.put(conn, "alert_large", 0)
    assert not [x for x in alerts.find(conn, TODAY) if x["kind"] == "unusual"]


def test_price_rise_hint(household, conn):
    conn.execute("UPDATE transactions SET amount = -15.99 WHERE counterparty = 'Netflix' AND date >= '2026-09-01'")
    found = [x for x in alerts.find(conn, TODAY) if x["kind"] == "price_up"]
    assert len(found) == 1 and found[0]["from"] == 13.99 and found[0]["to"] == 15.99
    assert found[0]["per_year"] == pytest.approx(24.0)


def test_api(household):
    client = TestClient(create_app())
    assert client.get("/api/available").status_code == 401
    r = client.post("/api/setup/account", json={"name": "Alex", "username": "alex", "password": "correct horse"}, headers=H)
    assert r.status_code == 200
    assert client.get("/api/available").json()["has_account"] is True
    assert client.get("/api/calendar?month=2026-9").status_code == 422
    assert client.get("/api/calendar?month=2026-09").json()["month"] == "2026-09"
    # The household's bookings end in September 2026, so what the hints say depends on today's date.
    items = client.get("/api/alerts").json()["items"]
    assert isinstance(items, list)
    assert client.post("/api/alerts/dismiss", json={"key": "big:1"}).status_code == 403
    assert client.post("/api/alerts/dismiss", json={"key": "big:1"}, headers=H).json() == {"ok": True}
    assert client.delete("/api/alerts/dismissed", headers=H).json() == {"restored": 1}
    assert client.get("/api/badges").json()["alerts"] == len(items)


def test_closed_month_banner_stays_hidden(conn):
    from groschen.analytics import cashflow

    monthly = [{"month": f"2026-0{m}", "income": 3000.0, "spending": 900.0} for m in range(1, 6)]
    monthly[2]["spending"] = 3000.0
    found = cashflow._insights(monthly, {}, conn, "2026-01-01")
    assert [i["key"] for i in found] == ["month:2026-03"]
    alerts.dismiss(conn, "month:2026-03")
    assert cashflow._insights(monthly, {}, conn, "2026-01-01") == []
    alerts.restore_all(conn)
    settings.put(conn, "unusual_alerts", False)
    assert cashflow._insights(monthly, {}, conn, "2026-01-01") == []


def test_only_whole_months_can_be_the_costliest(conn):
    from groschen.analytics import cashflow

    monthly = [{"month": f"2026-0{m}", "income": 3000.0, "spending": 900.0} for m in range(1, 7)]
    monthly[0]["spending"] = 3000.0  # the bank data starts on January 20: a few days, a big purchase
    assert cashflow._insights(monthly, {}, conn, "2026-01-20") == []
    assert [i["key"] for i in cashflow._insights(monthly, {}, conn, "2026-01-02")] == ["month:2026-01"]
