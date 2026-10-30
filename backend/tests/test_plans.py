import datetime as dt

import pytest
from fastapi.testclient import TestClient
from test_categorize import _account, _add

from groschen.analytics import plans
from groschen.api import auth
from groschen.main import create_app

TODAY = dt.date(2026, 10, 7)
EXTRA_IBAN = "DE00500105170000000002"
VWCE = "IE00BK5BQT80"
EMIM = "IE00BKM4GZ66"


def _months(first: str, last: str) -> list[str]:
    y, m = map(int, first.split("-"))
    out = []
    while f"{y}-{m:02d}" <= last:
        out.append(f"{y}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def _plan(conn, acc, isin, amount, first, last, day=1):
    for month in _months(first, last):
        _add(conn, acc, f"{month}-{day:02d}", -amount, "ING-DiBa AG", f"Sparplan {isin} ETF", "Wertpapierkauf")


def _by_key(conn, today=TODAY):
    return {p["key"]: p for p in plans.find(conn, today)["items"]}


def test_one_plan_per_fund(conn):
    giro = _account(conn)
    _plan(conn, giro, VWCE, 250.0, "2026-01", "2026-10")
    _plan(conn, giro, EMIM, 50.0, "2026-04", "2026-10")
    found = _by_key(conn)
    world = found[f"etf:{VWCE}"]
    assert (world["kind"], world["amount"], world["day"]) == ("etf", 250.0, 1)
    assert (world["since"], world["streak"], world["total"]) == ("2026-01", 10, 2500.0)
    assert world["active"] and world["next_date"] == "2026-11-01"
    assert [m["amount"] for m in world["months"][-3:]] == [250.0, 250.0, 250.0]
    assert found[f"etf:{EMIM}"]["since"] == "2026-04"
    assert plans.find(conn, TODAY)["invested_monthly"] == 300.0


def test_a_raised_plan_shows_when_it_changed(conn):
    giro = _account(conn)
    _plan(conn, giro, VWCE, 200.0, "2026-01", "2026-05", day=15)
    _plan(conn, giro, VWCE, 250.0, "2026-06", "2026-09", day=15)
    plan = _by_key(conn)[f"etf:{VWCE}"]
    assert plan["amount"] == 250.0
    assert plan["changes"] == [{"month": "2026-06", "from": 200, "to": 250}]
    # October's payment is still to come on the 15th.
    assert plan["next_date"] == "2026-10-15"


def test_single_purchases_are_no_plan(conn):
    giro = _account(conn)
    for date, amount in (("2026-06-03", 1000.0), ("2026-07-20", 300.0), ("2026-08-11", 2500.0), ("2026-09-02", 80.0)):
        _add(conn, giro, date, -amount, "ING-DiBa AG", f"WP-KAUF {VWCE}", "Wertpapierkauf")
    assert not _by_key(conn)


def test_a_plan_that_stopped_pauses_then_ends(conn):
    giro = _account(conn)
    _plan(conn, giro, VWCE, 100.0, "2025-12", "2026-08")
    plan = _by_key(conn)[f"etf:{VWCE}"]  # one payment missed: still listed, maybe it goes on
    assert plan["state"] == "paused" and not plan["active"] and plan["next_date"] is None
    found = plans.find(conn, TODAY)
    assert found["monthly"] == 0 and found["running"] == 0 and not found["ended"]

    later = plans.find(conn, dt.date(2026, 11, 20))  # three payments missed: it has ended
    assert not later["items"] and [p["key"] for p in later["ended"]] == [f"etf:{VWCE}"]
    assert later["ended"][0]["state"] == "ended" and later["ended"][0]["last_date"] == "2026-08-01"


def test_an_ended_plan_comes_back_with_its_next_payment(conn):
    giro = _account(conn)
    _plan(conn, giro, VWCE, 100.0, "2025-11", "2026-02")
    assert [p["state"] for p in plans.find(conn, TODAY)["ended"]] == ["ended"]
    _plan(conn, giro, VWCE, 100.0, "2026-10", "2026-10")
    plan = _by_key(conn)[f"etf:{VWCE}"]
    assert plan["state"] == "running" and plan["since"] == "2026-10" and plan["next_date"] == "2026-11-01"
    assert plans.find(conn, TODAY)["running"] == 1


def test_a_standing_order_to_the_savings_account(conn):
    giro = _account(conn)
    _account(conn, "Extra-Konto", EXTRA_IBAN, "savings")
    for month in _months("2026-03", "2026-10"):
        _add(conn, giro, f"{month}-01", -800.0, "Alex Beispiel", "Sparen", "Ueberweisung", EXTRA_IBAN)
    plan = next(iter(_by_key(conn).values()))
    assert (plan["kind"], plan["name"], plan["amount"], plan["invested"]) == ("savings", "Extra-Konto", 800.0, False)
    assert plans.find(conn, TODAY)["saved_monthly"] == 800.0


def test_kleingeld_plus(conn):
    giro = _account(conn)
    for month, amount in (("2026-06", 13.2), ("2026-07", 9.85), ("2026-08", 15.4), ("2026-09", 11.1)):
        _add(conn, giro, f"{month}-28", -amount, "ING-DiBa AG", f"Kleingeld Plus Sparplan {VWCE}", "Wertpapierkauf")
    plan = _by_key(conn)["roundup"]
    assert (plan["kind"], plan["name"], plan["invested"]) == ("roundup", "Kleingeld Plus", True)
    assert plan["amount"] == pytest.approx(12.12)  # the average of the last three months


def test_plans_and_review_through_the_api(conn):
    auth._failures.clear()
    client = TestClient(create_app(), headers={"x-groschen": "1"})
    client.post("/api/setup/account", json={"name": "Alex", "username": "alex", "password": "correct horse"})
    giro = _account(conn)
    _plan(conn, giro, VWCE, 250.0, "2026-01", dt.date.today().strftime("%Y-%m"))
    a = _add(conn, giro, "2026-09-03", -12.5, "Kiosk am Eck", "Zeitung")
    b = _add(conn, giro, "2026-09-04", -3.2, "Baeckerei Huber", "Semmeln")
    conn.execute("UPDATE transactions SET needs_review = 1 WHERE id IN (?, ?)", (a, b))
    conn.commit()
    assert client.get("/api/plans").json()["items"][0]["isin"] == VWCE
    r = client.post("/api/transactions/reviewed", json={"ids": [a, b, a, 999999]})
    assert r.json() == {"ok": True, "accepted": 2}
    conn.rollback()
    assert conn.execute("SELECT SUM(needs_review) FROM transactions").fetchone()[0] == 0
    assert client.post("/api/transactions/reviewed", json={"ids": []}).status_code == 422


def test_a_purchase_without_fund_name_is_a_savings_plan(conn):
    giro = _account(conn)
    for month in _months("2026-07", "2026-10"):
        _add(conn, giro, f"{month}-01", -1000.0, "", "", "Wertpapierkauf")
    [plan] = plans.find(conn, TODAY)["items"]
    assert (plan["kind"], plan["name"], plan["amount"], plan["invested"]) == ("etf", "", 1000.0, True)
