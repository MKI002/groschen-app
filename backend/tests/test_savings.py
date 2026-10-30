import pytest
from fastapi.testclient import TestClient
from test_categorize import _account, _add
from test_invest_payments import _set_category

from groschen.analytics import cashflow, portfolio, savings
from groschen.api import auth
from groschen.main import create_app

EXTRA_IBAN = "DE00500105170000000002"
OTHER_IBAN = "DE99100100100000009999"


@pytest.fixture
def october(conn):
    giro = _account(conn)
    extra = _account(conn, "Extra-Konto", EXTRA_IBAN, "savings")
    ids = {
        "salary": _add(conn, giro, "2026-10-01", 3000.0, "Arbeitgeber GmbH", "Gehalt Oktober", "Gehalt/Rente"),
        "rent": _add(conn, giro, "2026-10-02", -800.0, "Vermieter", "Miete", "Dauerauftrag"),
        # Leaves the Girokonto on the 5th, arrives on the Extra-Konto on the 6th: one transfer.
        "to_extra": _add(conn, giro, "2026-10-05", -500.0, "Alex", "Umbuchung", "Ueberweisung"),
        "extra_in": _add(conn, extra, "2026-10-06", 500.0, "Alex", "Umbuchung", "Gutschrift"),
        "buy": _add(conn, giro, "2026-10-08", -1000.0, "ING", "WP-ABRECHNUNG 123 KAUF IE00B4L5Y983", "Lastschrift"),
        "round": _add(conn, giro, "2026-10-09", -13.0, "ING", "Kleingeld Plus - Sparen", "Ueberweisung"),
        "tagesgeld": _add(conn, giro, "2026-10-10", -200.0, "C24 Bank", "Tagesgeld", "Ueberweisung"),
        "elsewhere": _add(conn, giro, "2026-10-11", -150.0, "A Beispiel", "Uebertrag", "Ueberweisung", OTHER_IBAN),
        "invest_acct": _add(conn, giro, "2026-10-13", -400.0, "Alex Beispiel", "Uebertrag Investmentkonto", "Ueberweisung"),
        "interest": _add(conn, extra, "2026-10-12", 2.0, "ING", "Zinsen", "Abschluss"),
    }
    for month in ("07", "08", "09", "10"):
        ids[f"plan{month}"] = _add(conn, giro, f"2026-{month}-15", -100.0, "ING", "Wertpapierkauf IE00BK5BQT80")
    conn.execute("UPDATE transactions SET category_id = NULL, cat_source = NULL")
    _set_category(conn, ids["salary"], "Salary")
    _set_category(conn, ids["rent"], "Rent")
    for k in ("to_extra", "extra_in", "round", "tagesgeld"):
        _set_category(conn, ids[k], "Savings")
    _set_category(conn, ids["elsewhere"], "Own transfers")
    _set_category(conn, ids["invest_acct"], "Own transfers")
    _set_category(conn, ids["interest"], "Interest & dividends")
    for month in ("07", "08", "09", "10"):
        _set_category(conn, ids[f"plan{month}"], "Investments")
    conn.commit()
    return ids


def _split(conn):
    s = cashflow.summary(conn, "2026-10-01", "2026-10-31", split=True)
    return s, {p["key"]: p["amount"] for p in s["saved_to"]["parts"]}


def test_saved_money_is_split_by_where_it_went(conn, october):
    s, parts = _split(conn)
    assert s["saved"] == 3000 + 2 - 800
    assert parts["etf"] == 1000 + 400  # the WP-ABRECHNUNG and the transfer to the investment account
    assert parts["plan"] == 100 + 13  # Kleingeld Plus counts as savings plan
    assert parts["savings"] == 500 + 200 + 2  # the Extra-Konto, the Tagesgeld elsewhere and the interest
    assert parts["other"] == 150
    assert parts["stays"] == pytest.approx(s["saved"] - 1400 - 113 - 702 - 150)
    assert sum(parts.values()) == pytest.approx(s["saved"])
    mirrored = [i for i in s["saved_to"]["items"] if i["id"] == october["to_extra"]][0]
    assert mirrored["how"] == "mirror" and mirrored["to"] == "Extra-Konto"
    # The Extra-Konto half is not counted twice.
    assert not [i for i in s["saved_to"]["items"] if i["id"] == october["extra_in"]]


def test_a_detected_purchase_is_not_spending(conn, october):
    _set_category(conn, october["buy"], "Electronics")  # wrongly sorted by the model
    s, parts = _split(conn)
    assert s["spending_total"] == 800
    assert parts["etf"] == 1400


def test_one_click_correction_carries_over_to_that_counterparty(conn, october):
    savings.set_dest(conn, october["elsewhere"], "etf")
    _, parts = _split(conn)
    assert "other" not in parts and parts["etf"] == 1550
    # The Investments page counts it now too.
    assert october["elsewhere"] in {p["id"] for p in portfolio.payments(conn) if p["counted"]}
    later = _add(conn, 1, "2026-10-20", -300.0, "A Beispiel", "Uebertrag", "Ueberweisung", OTHER_IBAN)
    _set_category(conn, later, "Own transfers")
    s, parts = _split(conn)
    assert parts["etf"] == 1850
    assert [i for i in s["saved_to"]["items"] if i["id"] == later][0]["how"] == "learned"
    savings.set_dest(conn, october["elsewhere"], None)
    _, parts = _split(conn)
    assert parts["other"] == 450


def test_taking_a_purchase_out_of_etfs_stops_counting_it(conn, october):
    savings.set_dest(conn, october["buy"], "stays")
    s, parts = _split(conn)
    assert parts["etf"] == 400
    assert s["spending_total"] == 800  # still the user's money, not spent
    assert [i for i in s["saved_to"]["items"] if i["id"] == october["buy"]][0]["dest"] == "stays"
    assert october["buy"] not in {p["id"] for p in portfolio.payments(conn) if p["counted"]}


def test_saving_dest_api(conn, october):
    auth._failures.clear()
    client = TestClient(create_app(), headers={"x-groschen": "1"})
    account = {"name": "Alex", "username": "alex", "password": "correct horse"}
    assert client.post("/api/setup/account", json=account).status_code == 200
    tx = october["elsewhere"]
    assert client.put(f"/api/savings/{tx}", json={"dest": "savings"}).status_code == 200
    assert client.put(f"/api/savings/{tx}", json={"dest": "nonsense"}).status_code == 422
    assert client.put(f"/api/savings/{tx}", json={"dest": None}).status_code == 200
    assert client.put("/api/savings/999999", json={"dest": "etf"}).status_code == 404
    assert TestClient(create_app()).put(f"/api/savings/{tx}", json={"dest": "etf"}).status_code == 403


def test_the_overview_groups_into_invested_put_aside_and_stays(conn, october):
    s, _ = _split(conn)
    groups = {}
    for p in s["saved_to"]["parts"]:
        groups[p["group"]] = groups.get(p["group"], 0) + p["amount"]
    assert set(groups) == {"invested", "aside", "stays"}
    assert groups["invested"] == pytest.approx(1400 + 113)
    assert groups["aside"] == pytest.approx(702 + 150)
