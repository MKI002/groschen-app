import datetime as dt

import pytest
from fastapi.testclient import TestClient
from test_categorize import _account, _add, _category

from groschen import settings
from groschen.analytics import alerts, recurring
from groschen.api import auth
from groschen.categorize import engine
from groschen.main import create_app

TODAY = dt.date(2026, 9, 27)
PAYPAL = "PayPal Europe S.a.r.l. et Cie S.C.A"


@pytest.fixture
def client_logged_in():
    auth._failures.clear()
    client = TestClient(create_app(), headers={"x-groschen": "1"})
    account = {"name": "Alex", "username": "alex", "password": "correct horse"}
    assert client.post("/api/setup/account", json=account).status_code == 200
    return client


def _aqua(conn, acc, date, amount, ref):
    purpose = f"{ref}/PP.1329.PP/. Aqua Net works Limited, Ihr Einkauf bei Aqua Networks Limited"
    return _add(conn, acc, date, amount, PAYPAL, purpose)


def _names(conn, part="items"):
    return {s["name"]: s for s in recurring.overview(conn, TODAY)[part]}


def test_paypal_subscription_with_changing_references_and_a_trial_month(conn):
    acc = _account(conn)
    _aqua(conn, acc, "2026-06-12", -1.00, "1051920690425")  # first month at a trial price
    _aqua(conn, acc, "2026-07-13", -9.99, "1052100372231")
    _aqua(conn, acc, "2026-08-12", -9.99, "1052608563785")
    _aqua(conn, acc, "2026-09-11", -9.99, "1053100000001")
    engine.categorize(conn)
    sub = _names(conn)["Aqua Networks"]
    assert sub["interval"] == "monthly"
    assert sub["amount"] == 9.99
    assert sub["next_date"] >= TODAY.isoformat()
    # The trial month is not the old price: nothing got more expensive.
    assert sub["price_change"] == 0 and not sub["changes"]


def test_model_guessing_a_transfer_does_not_hide_a_subscription(conn):
    acc = _account(conn)
    ids = [_aqua(conn, acc, d, -9.99, r) for d, r in [("2026-07-13", "1"), ("2026-08-12", "2"), ("2026-09-11", "3")]]
    own = conn.execute("SELECT id FROM categories WHERE name = 'Own transfers'").fetchone()[0]
    for i in ids:
        conn.execute("UPDATE transactions SET category_id = ?, cat_source = 'model' WHERE id = ?", (own, i))
    assert "Aqua Networks" in _names(conn)


def test_two_charges_become_a_suggestion_and_confirming_remembers_it(conn):
    acc = _account(conn)
    _aqua(conn, acc, "2026-08-12", -9.99, "1052608563785")
    _aqua(conn, acc, "2026-09-11", -9.99, "1053100000001")
    engine.categorize(conn)
    assert "Aqua Networks" not in _names(conn)
    suggestion = _names(conn, "suggestions")["Aqua Networks"]

    recurring.set_mark(conn, suggestion["key"], "yes")
    sub = _names(conn)["Aqua Networks"]
    assert sub["confirmed"] and sub["monthly_cost"] == 9.99
    assert not _names(conn, "suggestions")

    recurring.set_mark(conn, suggestion["key"], "no")
    assert not _names(conn) and "Aqua Networks" in _names(conn, "hidden")

    recurring.set_mark(conn, suggestion["key"], "auto")
    assert "Aqua Networks" in _names(conn, "suggestions")


def test_a_single_payment_can_be_marked_as_a_subscription(conn):
    acc = _account(conn)
    _add(conn, acc, "2026-09-20", -4.99, "Some Newsletter Ltd")
    key = engine.merchant_key({"counterparty": "Some Newsletter Ltd"})
    recurring.set_mark(conn, key, "yes")
    assert _names(conn)["Some Newsletter"]["interval"] == "monthly"


def test_varying_bills_are_suggested_not_listed(conn):
    acc = _account(conn)
    for d, amount in [("2026-06-03", -21.0), ("2026-07-03", -48.5), ("2026-08-03", -12.3), ("2026-09-03", -35.0)]:
        _add(conn, acc, d, amount, "Stadtwerke Beispiel")
    assert "Stadtwerke Beispiel" not in _names(conn)
    assert _names(conn, "suggestions")["Stadtwerke Beispiel"]["varies"]


def test_groceries_are_never_subscriptions(conn):
    acc = _account(conn)
    for d in ("2026-06-03", "2026-07-03", "2026-08-03", "2026-09-03"):
        _add(conn, acc, d, -50.0, "REWE SAGT DANKE. 44667788")
    engine.categorize(conn)
    overview = recurring.overview(conn, TODAY)
    assert not overview["items"] and not overview["suggestions"]


def test_confirming_a_guess_teaches_the_whole_merchant(client_logged_in, conn):
    acc = _account(conn)
    ids = [_aqua(conn, acc, d, -9.99, r) for d, r in [("2026-07-13", "1"), ("2026-08-12", "2"), ("2026-09-11", "3")]]
    streaming = conn.execute("SELECT id FROM categories WHERE name = 'Streaming'").fetchone()[0]
    for i in ids:
        conn.execute(
            "UPDATE transactions SET category_id = ?, cat_source = 'model', needs_review = 1 WHERE id = ?", (streaming, i)
        )
    conn.commit()
    r = client_logged_in.post(f"/api/transactions/{ids[0]}/reviewed")
    assert r.json()["also_changed"] == 2
    conn.rollback()
    assert conn.execute("SELECT SUM(needs_review) FROM transactions").fetchone()[0] == 0
    # A new booking from the same shop is categorized from memory, without the model.
    new = _aqua(conn, acc, "2026-10-11", -9.99, "4")
    engine.categorize(conn)
    assert _category(conn, new) == "Streaming"
    assert conn.execute("SELECT cat_source FROM transactions WHERE id = ?", (new,)).fetchone()[0] == "memory"


def test_income_is_not_taught_to_money_going_out(client_logged_in, conn):
    acc = _account(conn)
    back = _add(conn, acc, "2026-09-05", 500.0, "Max Mustermann", "Rueckzahlung", "Gutschrift")
    lent = _add(conn, acc, "2026-01-20", -2975.0, "Max Mustermann", "Darlehen", "Ueberweisung")
    later = _add(conn, acc, "2026-09-20", 250.0, "Max Mustermann", "Rest", "Gutschrift")
    conn.commit()
    other = conn.execute("SELECT id FROM categories WHERE name = 'Other income'").fetchone()[0]
    r = client_logged_in.patch(f"/api/transactions/{back}", json={"category_id": other, "apply_to_similar": True})
    assert r.json()["also_changed"] == 1
    conn.rollback()
    assert _category(conn, later) == "Other income"
    assert _category(conn, lent) != "Other income"


def test_outgoing_bookings_lose_an_income_category_spread_to_them(conn):
    acc = _account(conn)
    other = conn.execute("SELECT id FROM categories WHERE name = 'Other income'").fetchone()[0]
    spread = _add(conn, acc, "2026-01-20", -2975.0, "Max Mustermann", "Darlehen", "Ueberweisung")
    mine = _add(conn, acc, "2026-02-20", -40.0, "Max Mustermann", "Pizza", "Ueberweisung")
    income = _add(conn, acc, "2026-03-20", 500.0, "Max Mustermann", "Rueckzahlung", "Gutschrift")
    for tx, source in ((spread, "memory"), (mine, "user"), (income, "memory")):
        conn.execute("UPDATE transactions SET category_id = ?, cat_source = ? WHERE id = ?", (other, source, tx))
    assert engine.unspread_income(conn) == 1
    assert _category(conn, spread) != "Other income"
    assert _category(conn, mine) == "Other income"  # set by hand, stays
    assert _category(conn, income) == "Other income"
    assert engine.unspread_income(conn) == 0


def test_learned_merchants_can_be_changed_and_forgotten(client_logged_in, conn):
    acc = _account(conn)
    ids = [_aqua(conn, acc, d, -9.99, r) for d, r in [("2026-08-12", "2"), ("2026-09-11", "3")]]
    engine.categorize(conn)
    conn.commit()
    streaming = conn.execute("SELECT id FROM categories WHERE name = 'Streaming'").fetchone()[0]
    gaming = conn.execute("SELECT id FROM categories WHERE name = 'Gaming'").fetchone()[0]
    client_logged_in.patch(f"/api/transactions/{ids[0]}", json={"category_id": streaming})
    learned = client_logged_in.get("/api/learned").json()
    assert [(m["key"], m["category"]) for m in learned] == [("AQUANETWORKSLIMITED", "Streaming")]
    assert learned[0]["name"] == "Aqua Networks"  # what lists show for it

    r = client_logged_in.put("/api/learned", json={"key": "AQUANETWORKSLIMITED", "category_id": gaming})
    assert r.json()["changed"] == 1
    conn.rollback()
    assert _category(conn, ids[1]) == "Gaming"
    assert _category(conn, ids[0]) == "Streaming"  # set by hand, stays

    client_logged_in.delete("/api/learned", params={"key": "AQUANETWORKSLIMITED"})
    assert client_logged_in.get("/api/learned").json() == []
    conn.rollback()
    assert conn.execute("SELECT cat_source FROM transactions WHERE id = ?", (ids[1],)).fetchone()[0] != "memory"


def test_subscription_marks_through_the_api(client_logged_in, conn):
    acc = _account(conn)
    tx = _aqua(conn, acc, "2026-09-11", -9.99, "3")
    conn.commit()
    r = client_logged_in.post(f"/api/transactions/{tx}/subscription", json={"state": "yes"})
    assert r.json()["key"] == "AQUANETWORKSLIMITED"
    page = client_logged_in.get("/api/transactions").json()
    assert page["items"][0]["subscription"] == "yes"
    assert client_logged_in.post("/api/subscriptions/mark", json={"key": "AQUANETWORKSLIMITED", "state": "no"}).json()["ok"]
    assert client_logged_in.post("/api/subscriptions/mark", json={"key": "X", "state": "maybe"}).status_code == 422


def _months(first: str, last: str) -> list[tuple[int, int]]:
    """(year, month) from ``first`` to ``last`` (YYYY-MM), both included."""
    y, m = map(int, first.split("-"))
    out = []
    while f"{y}-{m:02d}" <= last:
        out.append((y, m))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def _monthly(conn, acc, name, amount, first, last, day=5, purpose="Abo"):
    for y, m in _months(first, last):
        _add(conn, acc, f"{y}-{m:02d}-{day:02d}", -amount, name, purpose)


def _old_booking(conn, acc):
    """Something long before, so Groschen knows the data reaches back that far."""
    _add(conn, acc, "2025-01-15", -42.0, "Baumarkt Beispiel", "Werkzeug")


def test_price_changes_up_and_down(conn):
    acc = _account(conn)
    _monthly(conn, acc, "Streamio Ltd", 9.99, "2026-01", "2026-05")
    _monthly(conn, acc, "Streamio Ltd", 12.99, "2026-06", "2026-09")
    _monthly(conn, acc, "Cheaper Cloud Inc", 20.0, "2026-02", "2026-06", day=9)
    _monthly(conn, acc, "Cheaper Cloud Inc", 15.0, "2026-07", "2026-09", day=9)
    subs = _names(conn)
    assert subs["Streamio"]["price_change"] == pytest.approx(3.0)
    assert subs["Streamio"]["price_change_date"] == "2026-06-05"
    events = {(e["kind"], e["name"]): e for e in recurring.overview(conn, TODAY)["events"]}
    up = events[("price_up", "Streamio")]
    assert (up["from"], up["to"], up["per_year"]) == (9.99, 12.99, 36.0)
    assert up["key"] == "price:STREAMIO:2026-06-05"
    down = events[("price_down", "Cheaper Cloud")]
    assert (down["from"], down["to"], down["per_year"]) == (20.0, 15.0, -60.0)


def test_a_cancelled_subscription_moves_to_ended(conn):
    acc = _account(conn)
    _monthly(conn, acc, "Disney Plus", 9.99, "2025-10", "2026-06", day=12)
    out = recurring.overview(conn, TODAY)
    assert "Disney+" not in {s["name"] for s in out["items"]}
    gone = {s["name"]: s for s in out["ended"]}["Disney+"]
    assert gone["status"] == "ended" and gone["last_date"] == "2026-06-12"
    assert gone["ended_on"] == "2026-07-30"  # a month and a few days of grace after the last charge
    event = next(e for e in out["events"] if e["kind"] == "ended")
    assert (event["name"], event["date"], event["last_date"]) == ("Disney+", "2026-07-30", "2026-06-12")


def test_a_subscription_that_comes_back_after_a_pause(conn):
    acc = _account(conn)
    _monthly(conn, acc, "DAZN Limited", 34.99, "2025-06", "2025-12", day=18)
    _monthly(conn, acc, "DAZN Limited", 34.99, "2026-08", "2026-09", day=18)
    out = recurring.overview(conn, TODAY)
    sub = {s["name"]: s for s in out["items"]}["DAZN"]
    assert sub["status"] == "resumed" and sub["since"] == "2026-08-18" and sub["pause_days"] == 243
    kinds = [(e["kind"], e["date"]) for e in out["events"] if e["name"] == "DAZN"]
    assert kinds == [("resumed", "2026-08-18"), ("ended", "2026-02-04")]


def test_a_new_subscription_is_recognized(conn):
    acc = _account(conn)
    _old_booking(conn, acc)
    for d in ("2026-07-09", "2026-08-09", "2026-09-09"):
        _add(conn, acc, d, -2.99, "Apple Services", "iCloud+ 50 GB")
    engine.categorize(conn)
    sub = _names(conn)["Apple"]
    assert sub["status"] == "new" and sub["new_since"] == "2026-09-09"
    event = next(e for e in recurring.overview(conn, TODAY)["events"] if e["kind"] == "new")
    assert (event["name"], event["since"], event["key"]) == ("Apple", "2026-07-09", "sub:new:APPLESERVICES")


def test_a_streaming_service_seen_twice_needs_no_question(conn):
    acc = _account(conn)
    _old_booking(conn, acc)
    for d in ("2026-08-09", "2026-09-09"):
        _add(conn, acc, d, -2.99, "Apple Services", "iCloud+ 50 GB")
    engine.categorize(conn)
    sub = _names(conn)["Apple"]
    assert sub["status"] == "new" and sub["new_since"] == "2026-09-09"
    assert not _names(conn, "suggestions")


def test_every_four_weeks(conn):
    acc = _account(conn)
    day = dt.date(2026, 3, 3)
    while day <= TODAY:
        _add(conn, acc, day.isoformat(), -24.99, "FitX Deutschland GmbH", "Mitgliedsbeitrag")
        day += dt.timedelta(days=28)
    sub = _names(conn)["FitX"]
    assert sub["interval"] == "4-weekly"
    assert sub["monthly_cost"] == pytest.approx(27.07)
    assert sub["next_date"] == "2026-10-13"


def test_every_week(conn):
    acc = _account(conn)
    day = dt.date(2026, 7, 6)
    while day <= TODAY:
        _add(conn, acc, day.isoformat(), -7.20, "Zeitverlag Gerd Bucerius", "DIE ZEIT Abo")
        day += dt.timedelta(days=7)
    sub = _names(conn)["Zeitverlag Gerd Bucerius"]
    assert sub["interval"] == "weekly"
    assert sub["monthly_cost"] == pytest.approx(31.2)
    assert sub["next_date"] == "2026-09-28"


def test_an_irregular_hairdresser_is_not_a_subscription(conn):
    acc = _account(conn)
    day = dt.date(2026, 2, 3)
    for gap, amount in [(35, 31.0), (28, 28.0), (42, 34.0), (30, 29.0), (38, 33.0), (50, 30.0)]:
        _add(conn, acc, day.isoformat(), -amount, "Friseur Haarmonie", "Kartenzahlung")
        day += dt.timedelta(days=gap)
    out = recurring.overview(conn, TODAY)
    assert not out["items"] and not out["suggestions"]


def test_the_same_shop_a_year_apart_is_no_contract(conn):
    acc = _account(conn)
    for d in ("2024-12-18", "2025-12-18"):
        _add(conn, acc, d, -189.99, "MediaMarkt Muenchen", "VISA Debitkartenumsatz")
    engine.categorize(conn)
    out = recurring.overview(conn, dt.date(2026, 1, 10))
    assert not out["items"] and not out["suggestions"]


def test_varying_bills_of_a_contract_count_by_themselves(conn):
    acc = _account(conn)
    for d, amount in [("2026-06-03", -21.0), ("2026-07-03", -48.5), ("2026-08-03", -12.3), ("2026-09-03", -35.0)]:
        _add(conn, acc, d, amount, "Stadtwerke Beispiel", "Abschlag Strom")
    energy = conn.execute("SELECT id FROM categories WHERE name = 'Energy'").fetchone()[0]
    conn.execute("UPDATE transactions SET category_id = ?, cat_source = 'dict'", (energy,))
    sub = _names(conn)["Stadtwerke Beispiel"]
    assert sub["varies"] and not sub["changes"]
    assert not _names(conn, "suggestions")


def test_subscription_changes_become_hints(conn):
    acc = _account(conn)
    _old_booking(conn, acc)
    for d in ("2026-08-09", "2026-09-09"):
        _add(conn, acc, d, -2.99, "Apple Services", "iCloud+ 50 GB")
    _monthly(conn, acc, "Streamio Ltd", 9.99, "2026-01", "2026-08")
    _add(conn, acc, "2026-09-05", -12.99, "Streamio Ltd", "Abo")
    engine.categorize(conn)
    hints = {a["kind"]: a for a in alerts.find(conn, TODAY)}
    assert hints["sub_new"]["name"] == "Apple"
    assert (hints["price_up"]["from"], hints["price_up"]["to"]) == (9.99, 12.99)
    settings.put(conn, "alert_subscriptions", False)
    kinds = {a["kind"] for a in alerts.find(conn, TODAY)}
    assert "sub_new" not in kinds and "price_up" in kinds


def test_an_upgrade_between_two_monthly_charges_keeps_the_rhythm(conn):
    acc = _account(conn)
    for d in ("2026-06-04", "2026-07-03", "2026-08-04", "2026-09-02"):
        _add(conn, acc, d, -13.99, "VISA NETFLIX.COM")
    _add(conn, acc, "2026-09-06", -48.5, "VISA NETFLIX.COM", "upgrade")  # charged on top, four days later
    engine.categorize(conn)
    sub = _names(conn)["Netflix"]
    assert (sub["interval"], sub["amount"], sub["next_date"]) == ("monthly", 13.99, "2026-10-04")
