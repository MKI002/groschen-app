import pytest

from groschen import demo
from groschen.bank import csv_ing
from groschen.jobs import UserFacingError


def test_parses_ing_export(demo_data):
    raw = demo.ing_csv(demo.GIRO_IBAN, "Girokonto", 1234.56, demo_data["giro"][:20])
    parsed = csv_ing.parse(raw)
    assert parsed["iban"] == demo.GIRO_IBAN
    assert parsed["account_name"] == "Girokonto"
    assert parsed["balance"] == 1234.56
    assert len(parsed["rows"]) == 20
    first = sorted(demo_data["giro"][:20], key=lambda t: t["date"], reverse=True)[0]
    row = parsed["rows"][0]
    assert row["date"] == first["date"]
    assert row["amount"] == first["amount"]
    assert row["counterparty"] == first["counterparty"]


def test_german_amounts():
    assert csv_ing.parse_amount("-1.234,56") == -1234.56
    assert csv_ing.parse_amount("12,5") == 12.5
    assert csv_ing.parse_amount("") == 0.0


def test_rejects_other_files():
    with pytest.raises(UserFacingError):
        csv_ing.parse(b"name,amount\nfoo,1\n")


def test_price_file(demo_data):
    rows = csv_ing.parse_prices(demo.price_csv(demo_data["prices"][:5]))
    assert rows[0][0] == demo.VWCE
    assert isinstance(rows[0][2], float)
    with pytest.raises(UserFacingError):
        csv_ing.parse_prices(b"nothing useful here")
