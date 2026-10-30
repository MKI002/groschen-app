import pytest
from fastapi.testclient import TestClient
from test_categorize import _account, _add

from groschen.analytics import portfolio
from groschen.api import auth
from groschen.main import create_app


def _set_category(conn, tx_id, name, source="model"):
    cat = conn.execute("SELECT id FROM categories WHERE name = ?", (name,)).fetchone()[0]
    conn.execute("UPDATE transactions SET category_id = ?, cat_source = ? WHERE id = ?", (cat, source, tx_id))


@pytest.fixture
def bookings(conn):
    acc = _account(conn)
    ids = {
        "plan": _add(conn, acc, "2026-08-01", -250.0, "ING", "Sparplan IE00BK5BQT80 Vanguard", "Wertpapierkauf"),
        "buy": _add(conn, acc, "2026-09-26", -1000.0, "ING", "WP-ABRECHNUNG 123 KAUF IE00B4L5Y983", "Lastschrift"),
        "broker": _add(conn, acc, "2026-09-10", -200.0, "Trade Republic Bank GmbH", "Einzahlung", "Ueberweisung"),
        "sale": _add(conn, acc, "2026-09-12", 400.0, "ING", "WP-ABRECHNUNG 555 VERKAUF IE00B4L5Y983", "Gutschrift"),
        "payout": _add(conn, acc, "2026-09-15", 12.3, "ING", "ERTRAG IE00B3RBWM25 Vanguard", "Gutschrift"),
        "tax": _add(conn, acc, "2026-09-16", -3.1, "ING", "VORABPAUSCHALE IE00B3RBWM25", "Lastschrift"),
        "shop": _add(conn, acc, "2026-09-17", -30.0, "REWE", "Einkauf", "Lastschrift"),
        "user_said_no": _add(conn, acc, "2026-09-18", -500.0, "Scalable Capital GmbH", "Geschenk Anna", "Ueberweisung"),
    }
    conn.execute("UPDATE transactions SET category_id = NULL, cat_source = NULL")
    _set_category(conn, ids["plan"], "Investments")
    _set_category(conn, ids["buy"], "Other income")  # wrongly sorted: still found by its text
    _set_category(conn, ids["user_said_no"], "Gifts & donations", source="user")
    conn.commit()
    return ids


def test_payments_count_the_category_and_what_looks_like_investing(conn, bookings):
    found = {p["id"]: p for p in portfolio.payments(conn)}
    assert found[bookings["plan"]]["how"] == "category"
    assert found[bookings["buy"]]["how"] == "detected" and found[bookings["buy"]]["isin"] == "IE00B4L5Y983"
    assert found[bookings["broker"]]["how"] == "detected"
    assert found[bookings["sale"]]["amount"] == -400  # money taken out of the depot
    for key in ("payout", "tax", "shop", "user_said_no"):
        assert bookings[key] not in found
    total = sum(f["amount"] for f in portfolio.contributions(conn))
    assert total == 250 + 1000 + 200 - 400


def test_one_click_takes_a_payment_out_and_puts_it_back(conn, bookings):
    portfolio.set_counted(conn, bookings["broker"], False)
    listed = {p["id"]: p for p in portfolio.payments(conn)}
    assert listed[bookings["broker"]]["counted"] is False
    assert sum(f["amount"] for f in portfolio.contributions(conn)) == 250 + 1000 - 400
    portfolio.set_counted(conn, bookings["broker"], True)
    assert sum(f["amount"] for f in portfolio.contributions(conn)) == 250 + 1000 + 200 - 400


def test_payments_api(conn, bookings):
    auth._failures.clear()
    client = TestClient(create_app(), headers={"x-groschen": "1"})
    account = {"name": "Alex", "username": "alex", "password": "correct horse"}
    assert client.post("/api/setup/account", json=account).status_code == 200
    listed = client.get("/api/investments/payments").json()["payments"]
    assert listed[0]["date"] >= listed[-1]["date"]  # newest first
    tx = bookings["buy"]
    assert client.put(f"/api/investments/payments/{tx}", json={"counted": False}).json()["counted"] is False
    again = {p["id"]: p for p in client.get("/api/investments/payments").json()["payments"]}
    assert again[tx]["counted"] is False
    assert client.put(f"/api/investments/payments/{tx}", json={"counted": True}).status_code == 200
    assert client.put("/api/investments/payments/999999", json={"counted": False}).status_code == 404
    assert TestClient(create_app()).put(f"/api/investments/payments/{tx}", json={"counted": False}).status_code == 403


def test_daily_values_follow_the_price_every_day(conn):
    import datetime as dt

    acc = _account(conn)
    depot = _account(conn, "Depot", "DE00500105170000000099", kind="depot")
    isin = "IE00BK5BQT80"
    _add(conn, acc, "2026-09-01", -1000.0, "ING", f"Sparplan {isin}", "Wertpapierkauf")
    day, price = dt.date(2026, 8, 25), 100.0
    while day <= dt.date(2026, 9, 30):
        if day.weekday() < 5:
            price *= 1.01 if day.day % 2 else 0.99
            conn.execute("INSERT INTO prices (isin, date, price) VALUES (?, ?, ?)", (isin, day.isoformat(), price))
        day += dt.timedelta(days=1)
    conn.execute(
        "INSERT INTO holdings (account_id, isin, name, pieces, price, price_date, value, updated_at) "
        "VALUES (?, ?, 'ETF', 10, ?, '2026-09-30', ?, '2026-09-30')",
        (depot, isin, price, round(10 * price, 2)),
    )
    conn.commit()
    days = portfolio.daily_values(conn, portfolio.contributions(conn), dt.date(2026, 9, 30))
    assert days[0]["date"] == "2026-09-01"  # nothing held before the first buy
    values = [d["value"] for d in days]
    ups = sum(b > a for a, b in zip(values, values[1:]))
    downs = sum(b < a for a, b in zip(values, values[1:]))
    assert ups >= 5 and downs >= 5  # real daily ups and downs, not a straight line
    assert all(dt.date.fromisoformat(d["date"]).weekday() < 5 for d in days)
    assert days[-1]["paid_in"] == 1000


def test_daily_values_per_etf_add_up_to_the_depot(conn):
    import datetime as dt

    acc = _account(conn)
    depot = _account(conn, "Depot", "DE00500105170000000099", kind="depot")
    world, em = "IE00BK5BQT80", "IE00BKM4GZ66"
    _add(conn, acc, "2026-09-01", -1000.0, "ING", f"Sparplan {world}", "Wertpapierkauf")
    _add(conn, acc, "2026-09-15", -300.0, "ING", f"Sparplan {em}", "Wertpapierkauf")
    day, pw, pe = dt.date(2026, 8, 25), 100.0, 30.0
    while day <= dt.date(2026, 9, 30):
        if day.weekday() < 5:
            pw *= 1.01 if day.day % 2 else 0.995
            pe *= 0.99 if day.day % 3 else 1.02
            conn.execute("INSERT INTO prices (isin, date, price) VALUES (?, ?, ?)", (world, day.isoformat(), pw))
            conn.execute("INSERT INTO prices (isin, date, price) VALUES (?, ?, ?)", (em, day.isoformat(), pe))
        day += dt.timedelta(days=1)
    for isin, pieces, price in ((world, 10, pw), (em, 10, pe)):
        conn.execute(
            "INSERT INTO holdings (account_id, isin, name, pieces, price, price_date, value, updated_at) "
            "VALUES (?, ?, 'ETF', ?, ?, '2026-09-30', ?, '2026-09-30')",
            (depot, isin, pieces, price, round(pieces * price, 2)),
        )
    conn.commit()
    days, by = portfolio.daily_values(conn, portfolio.contributions(conn), dt.date(2026, 9, 30), per_holding=True)
    assert set(by) == {world, em}
    assert all(len(series) == len(days) for series in by.values())
    for i, d in enumerate(days):
        assert abs(sum(by[isin][i][0] for isin in by) - d["value"]) < 0.05
        assert abs(sum(by[isin][i][1] for isin in by) - d["paid_in"]) < 0.01
    assert by[world][-1][1] == 1000 and by[em][-1][1] == 300
    before = next(i for i, d in enumerate(days) if d["date"] == "2026-09-14")
    assert by[em][before] == [0, 0]  # nothing in the second ETF before its first buy
