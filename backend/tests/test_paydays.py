from groschen import settings
from groschen.analytics import cashflow, paydays
from groschen.bank import store

EMPLOYER = "Muster GmbH"


def _setup(conn, salary_days=("2026-06-26", "2026-07-25", "2026-08-26", "2026-09-26")):
    acc = store.upsert_account(
        conn,
        None,
        {"kind": "checking", "name": "Girokonto", "iban": "DE00500105170000000001", "account_number": "1", "blz": "1"},
    )
    rows = [
        {"date": d, "amount": 2800.0, "counterparty": EMPLOYER, "purpose": "LOHN/GEHALT", "booking_text": "Gehalt/Rente"}
        for d in salary_days
    ]
    rows += [
        {"date": "2026-09-10", "amount": 149.0, "counterparty": "Max Mustermann", "purpose": "Geld zurück"},
        {"date": "2026-09-12", "amount": -1215.0, "counterparty": "Hausverwaltung", "purpose": "Miete"},
    ]
    store.insert_transactions(conn, acc, rows, "csv")
    return acc


def test_end_of_month_salary_counts_for_next_month(conn):
    _setup(conn)
    sep = cashflow.summary(conn, "2026-09-01", "2026-09-30")
    assert sep["income_total"] == 2949.0  # August 26 salary plus the 149 €, not the September 26 one
    assert sep["saved"] == 1734.0
    oct_ = cashflow.summary(conn, "2026-10-01", "2026-10-31")
    assert oct_["income_total"] == 2800.0
    by_month = {m["month"]: m["income"] for m in cashflow.summary(conn, "2026-06-01", "2026-10-31")["monthly"]}
    assert by_month == {"2026-06": 0.0, "2026-07": 2800.0, "2026-08": 2800.0, "2026-09": 2949.0, "2026-10": 2800.0}


def test_detected_payer_is_listed(conn):
    _setup(conn)
    found = paydays.sources(conn)
    assert found["enabled"] is True
    [src] = found["sources"]
    assert src["name"] == "Muster"  # the legal form is left out
    assert src["usual_day"] == 26 and src["auto"] == "next" and src["moved"] == 4


def test_can_be_turned_off_per_payer_and_globally(conn):
    _setup(conn)
    key = paydays.sources(conn)["sources"][0]["key"]
    paydays.set_mode(conn, key, "same")
    assert cashflow.summary(conn, "2026-09-01", "2026-09-30")["income_total"] == 2949.0  # the September 26 salary
    paydays.set_mode(conn, key, "auto")
    settings.update(conn, {"payday_shift": False})
    assert cashflow.summary(conn, "2026-09-01", "2026-09-30")["income_total"] == 2949.0
    assert paydays.shifted(conn) == {}


def test_start_of_month_payer_moves_only_early_payments(conn):
    _setup(conn, salary_days=("2026-06-01", "2026-07-01", "2026-07-30", "2026-09-01"))
    by_month = {m["month"]: m["income"] for m in cashflow.summary(conn, "2026-06-01", "2026-09-30")["monthly"]}
    assert by_month == {"2026-06": 2800.0, "2026-07": 2800.0, "2026-08": 2800.0, "2026-09": 2949.0}


def test_small_or_irregular_income_stays_put(conn):
    _setup(conn, salary_days=())
    assert paydays.sources(conn)["sources"] == []


def test_trend_steps_follow_the_period(conn):
    _setup(conn)
    sep = cashflow.summary(conn, "2026-09-01", "2026-09-30")["trend"]
    assert sep["unit"] == "week"
    assert [(p["from"], p["to"]) for p in sep["points"]] == [(1, 7), (8, 14), (15, 21), (22, 30)]
    assert sep["points"][0]["income"] == 2800.0  # August's late salary counts from September 1
    assert sep["points"][1]["income"] == 149.0 and sep["points"][1]["spending"] == 1215.0
    part = cashflow.summary(conn, "2026-09-01", "2026-09-10")["trend"]
    assert [(p["from"], p["to"]) for p in part["points"]] == [(1, 7), (8, 10)]
    assert cashflow.summary(conn, "2026-06-01", "2026-10-31")["trend"]["unit"] == "month"
    assert cashflow.summary(conn, "2022-01-01", "2026-10-31")["trend"]["unit"] == "month"  # data starts in June 2026
