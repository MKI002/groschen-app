import datetime as dt
import json
import socket

import pytest
from fastapi.testclient import TestClient

from groschen import db, demo, market, netguard, settings
from groschen.analytics import fund
from groschen.api import auth
from groschen.jobs import UserFacingError
from groschen.main import create_app

TODAY = dt.date.today()
VWCE = "IE00BK5BQT80"
EMIM = "IE00BKM4GZ66"
H = {"x-groschen": "1"}
ACCOUNT = {"name": "Alex", "username": "alex", "password": "correct horse"}


@pytest.fixture
def loaded(run_job):
    demo.load(today=TODAY)


@pytest.fixture
def no_price_host():
    netguard.disallow_host(market.HOST)
    yield
    netguard.disallow_host(market.HOST)


def test_parse_keeps_trading_days_only():
    payload = json.dumps(
        {
            "series": [
                {"date": "2026-09-25", "value": {"raw": 131.4, "localized": "131,40"}},  # Friday
                {"date": "2026-09-26", "value": {"raw": 131.4, "localized": "131,40"}},  # Saturday
                {"date": "2026-09-28", "value": {"raw": 132.1, "localized": "132,10"}},
                {"date": "2026-09-29", "value": {"raw": None}},
                {"date": "bad", "value": {"raw": 1}},
            ]
        }
    ).encode()
    assert market.parse(payload) == [("2026-09-25", 131.4), ("2026-09-28", 132.1)]


def test_fetch_refuses_anything_but_an_isin():
    with pytest.raises(ValueError):
        market.fetch("../../evil")


def test_price_host_is_only_allowed_while_turned_on(conn, no_price_host, monkeypatch):
    monkeypatch.setattr(netguard, "_original_getaddrinfo", lambda *a, **k: [("ok",)])
    market.apply_setting(conn)
    with pytest.raises(socket.gaierror):
        netguard._guarded_getaddrinfo(market.HOST, 443)
    settings.put(conn, "online_prices", True)
    market.apply_setting(conn)
    assert netguard._guarded_getaddrinfo(market.HOST, 443) == [("ok",)]
    settings.put(conn, "online_prices", False)
    market.apply_setting(conn)
    assert market.HOST not in netguard.allowed_hosts()


def test_refresh_needs_the_setting(conn):
    with pytest.raises(UserFacingError):
        market.refresh()


def test_refresh_fills_gaps_without_touching_bank_prices(loaded, no_price_host, monkeypatch):
    calls = []

    def fake(isin, since):
        calls.append((isin, since))
        return [("2020-01-02", 50.0), ("2020-01-03", 51.0), (TODAY.isoformat(), 1.0)]

    monkeypatch.setattr(market, "fetcher", fake)
    with db.session() as conn:
        settings.put(conn, "online_prices", True)
        bank_price = conn.execute(
            "SELECT price FROM prices WHERE isin = ? AND date = ?", (VWCE, TODAY.isoformat())
        ).fetchone()
    result = market.refresh()
    assert result["failed"] == [] and result["added"] >= 2
    assert all(since is None for _, since in calls)
    with db.session() as conn:
        assert conn.execute("SELECT price FROM prices WHERE isin = ? AND date = '2020-01-02'", (VWCE,)).fetchone()[0] == 50.0
        if bank_price:
            now = conn.execute("SELECT price FROM prices WHERE isin = ? AND date = ?", (VWCE, TODAY.isoformat())).fetchone()
            assert now[0] == bank_price[0]
        meta = db.one(conn.execute("SELECT * FROM market_meta WHERE isin = ?", (VWCE,)))
    assert meta["error"] is None and meta["first_date"] == "2020-01-02"
    # The next run only asks for the days since the last one.
    calls.clear()
    market.refresh()
    assert all(since and since < TODAY.isoformat() for _, since in calls)


def test_refresh_notes_errors_and_goes_on(loaded, no_price_host, monkeypatch):
    def broken(isin, since):
        raise OSError("Blocked by Groschen")

    monkeypatch.setattr(market, "fetcher", broken)
    with db.session() as conn:
        settings.put(conn, "online_prices", True)
    result = market.refresh()
    assert VWCE in result["failed"]
    with db.session() as conn:
        assert "Blocked" in market.status(conn)["funds"][0]["error"]


def test_fund_detail_on_demo_data(loaded, conn):
    d = fund.detail(conn, VWCE, TODAY)
    assert d["position"]["value"] > 0 and d["position"]["share"] > 0
    keys = [p["key"] for p in d["periods"]]
    assert keys[:5] == ["1m", "3m", "6m", "ytd", "1y"]
    # The demo fund swings about 14 % a year.
    assert 0.08 < d["risk"]["volatility"] < 0.22
    assert d["risk"]["max_drawdown"] < 0
    inv = d["investing"]
    assert inv["rhythm"] == "monthly" and inv["typical"] == 250 and inv["day"] == 1
    assert inv["avg_buy"] and inv["xirr"] is not None
    fc = d["forecast"]
    # Two years of history count for little against the long-run figure.
    assert 0 < fc["weight"] < 0.3 and -0.03 <= fc["ret"] <= 0.12
    assert fund.detail(conn, "XX0000000000", TODAY) is None


def test_investing_finds_a_raised_plan():
    flows = []
    for i in range(24):
        y, m = divmod(i, 12)
        flows.append({"date": f"{2024 + y}-{m + 1:02d}-15", "amount": 100.0 if i < 12 else 150.0, "isin": None})
    inv = fund.investing(flows, [], dt.date(2025, 12, 20))
    assert [s["amount"] for s in inv["steps"]] == [100, 150]
    assert inv["typical"] == 150 and inv["day"] == 15
    assert inv["raise_pa"] == 0.1  # capped


def test_investing_counts_irregular_buys_and_this_month():
    # €500 a month for four months, then only round-ups of about €13 a month, then €1,000 this month.
    flows = [{"date": f"2025-{m:02d}-03", "amount": 500.0, "isin": None} for m in (11, 12)]
    flows += [{"date": f"2026-{m:02d}-03", "amount": 500.0, "isin": None} for m in (1, 2)]
    for m in range(3, 10):
        flows += [{"date": f"2026-{m:02d}-{d:02d}", "amount": 0.65, "isin": None} for d in range(5, 25)]
    flows.append({"date": "2026-09-26", "amount": 1000.0, "isin": "IE00BK5BQT80"})
    inv = fund.investing(flows, [], dt.date(2026, 9, 28))
    # Not the €13 of the round-ups: everything paid in over the eleven months since the first payment.
    assert inv["source"] == "average"
    assert inv["window_months"] == 11 and inv["window_total"] == 3091
    assert inv["per_month"] == round(3091 / 11, 2) and inv["this_month"] == 1013
    assert inv["recent"] == 13 and inv["raise_pa"] == 0


def test_investing_keeps_a_steady_plan_and_ignores_a_single_buy():
    flows = [{"date": f"2026-{m:02d}-01", "amount": 250.0, "isin": None} for m in range(1, 10)]
    inv = fund.investing(flows, [], dt.date(2026, 9, 28))
    assert inv["source"] == "plan" and inv["per_month"] == 250
    one = fund.investing([{"date": "2026-09-10", "amount": 1000.0, "isin": None}], [], dt.date(2026, 9, 28))
    assert one["rhythm"] == "once" and one["per_month"] == 0 and one["this_month"] == 1000


def test_periods_annualise_long_ones():
    start = dt.date(2020, 1, 1)
    series = [((start + dt.timedelta(days=d)).isoformat(), 100 * 1.1 ** (d / 365.25)) for d in range(0, 6 * 366, 7)]
    by_key = {p["key"]: p for p in fund.periods(series)}
    assert by_key["5y"]["annual"] and abs(by_key["5y"]["r"] - 0.1) < 0.01
    assert not by_key["1y"]["annual"] and abs(by_key["1y"]["r"] - 0.1) < 0.01


def test_fund_return_per_year_over_the_time_you_paid_in():
    start = dt.date(2024, 1, 1)
    series = [((start + dt.timedelta(days=d)).isoformat(), 100 * 1.2 ** (d / 365.0)) for d in range(0, 731, 7)]
    assert abs(fund.per_year(series, "2024-06-01") - 0.2) < 0.002
    assert fund.per_year(series, "2023-01-01") is None  # prices start long after the first payment
    assert fund.per_year(series, series[-3][0]) is None  # two weeks say nothing about a year


def test_twelve_month_stretches_come_with_the_month_they_end_in():
    start = dt.date(2024, 1, 15)
    series = [((start + dt.timedelta(days=d)).isoformat(), 100 + d / 10) for d in range(0, 500, 3)]
    rk = fund.risk(series, 1.75)
    assert rk["rolling_count"] == len(rk["rolling"]) > 0 and rk["rolling"][0]["month"] == "2025-01"
    assert rk["rolling_up"] == 1 and rk["rolling_best"] == max(x["r"] for x in rk["rolling"])


def test_api(loaded, no_price_host, monkeypatch):
    auth._failures.clear()
    client = TestClient(create_app())
    assert client.post("/api/setup/account", json=ACCOUNT, headers=H).status_code == 200
    inv = client.get("/api/investments").json()
    assert inv["online_prices"] is False and inv["forecast"]["ret"] > 0
    assert inv["investing"]["rhythm"] == "monthly"
    assert all("r1y" in h and "spark" in h for h in inv["holdings"])
    assert client.get(f"/api/investments/{VWCE}").json()["isin"] == VWCE
    assert client.get("/api/investments/nope").status_code == 404
    assert client.post("/api/market/refresh", headers=H).status_code == 400

    monkeypatch.setattr(market, "fetcher", lambda isin, since: [("2020-01-02", 50.0)])
    r = client.patch("/api/settings", json={"online_prices": True}, headers=H)
    assert r.status_code == 200 and r.json()["online_prices"] is True
    info = client.get("/api/settings").json()
    assert info["market"]["enabled"] and market.HOST in info["network"]["allowed_hosts"]
    client.patch("/api/settings", json={"online_prices": False}, headers=H)
    assert market.HOST not in client.get("/api/settings").json()["network"]["allowed_hosts"]


PROFILE = """
<html><head><script>var x = "Distribution policy Accumulating";</script></head><body>
<table class="table">
<tr><td>Index</td><td>S&amp;P Global Clean Energy Transition</td></tr>
<tr><td>Investment focus</td><td>Equity, World</td></tr>
<tr><td>Fund size</td><td><div class="val">EUR 2,622 m</div></td></tr>
<tr><td>Total expense ratio <span class="info" title="costs">i</span></td><td>0.65% p.a.</td></tr>
<tr><td>Replication</td><td>Physical (Full replication)</td></tr>
<tr><td>Fund currency</td><td>USD</td></tr>
<tr><td>Currency risk</td><td>Currency unhedged</td></tr>
<tr><td>Inception/ Listing Date</td><td>6 July 2007</td></tr>
<tr><td>Distribution policy</td><td>Distributing</td></tr>
<tr><td>Distribution frequency</td><td>Semi annually</td></tr>
<tr><td>Fund domicile</td><td>Ireland</td></tr>
<tr><td>Fund Provider</td><td>iShares</td></tr>
</table>
<div>Current dividend yield <span>1.05%</span></div>
</body></html>
"""


def test_parse_facts_reads_the_key_facts_table():
    facts = market.parse_facts(PROFILE)
    assert facts == {
        "policy": "distributing",
        "frequency": "semiannual",
        "ter": 0.0065,
        "size": 2622.0,
        "size_currency": "EUR",
        "replication": "physical",
        "replication_detail": "Full replication",
        "currency": "USD",
        "hedged": False,
        "domicile": "Ireland",
        "inception": "2007-07-06",
        "index": "S&P Global Clean Energy Transition",
        "dividend_yield": 0.0105,
    }
    assert market.parse_facts("<html>nothing here</html>") == {}


def test_refresh_also_reads_fund_facts_once_a_week(loaded, no_price_host, monkeypatch):
    asked = []
    monkeypatch.setattr(market, "fetcher", lambda isin, since: [("2020-01-02", 50.0)])
    monkeypatch.setattr(
        market, "facts_fetcher", lambda isin: asked.append(isin) or {"policy": "accumulating", "ter": 0.0022}
    )
    with db.session() as conn:
        settings.put(conn, "online_prices", True)
    market.refresh()
    market.refresh()
    assert sorted(asked) == sorted(set(asked)) and VWCE in asked
    with db.session() as conn:
        d = fund.detail(conn, VWCE, TODAY)
    assert d["payout"]["policy"] == "accumulating" and d["payout"]["source"] == "profile"
    assert d["position"]["cost_pa"] == round(d["position"]["value"] * 0.0022, 2)


def test_payouts_found_in_bookings(loaded, conn):
    acc = conn.execute("SELECT id FROM accounts WHERE kind != 'depot' ORDER BY id LIMIT 1").fetchone()[0]
    sql = (
        "INSERT INTO transactions (account_id, date, amount, counterparty, purpose, booking_text, fingerprint, source, "
        "created_at) VALUES (?, ?, ?, 'ING', ?, 'Gutschrift', ?, 'test', ?)"
    )
    for days in (30, 120, 210):
        d = (TODAY - dt.timedelta(days=days)).isoformat()
        conn.execute(sql, (acc, d, 12.5, f"Ertragsgutschrift Vanguard ISIN {EMIM}", f"payout-{days}", d))
    # A sale names the ISIN too, but isn't a payout.
    conn.execute(sql, (acc, TODAY.isoformat(), 500.0, f"Verkauf {EMIM}", "sale-1", TODAY.isoformat()))
    p = fund.payout(conn, EMIM, "iShs Core MSCI EM IMI U.ETF Registered Shares o.N.", 1000.0, TODAY)
    assert p["policy"] == "distributing" and p["source"] == "bookings"
    assert p["frequency"] == "quarterly" and p["received_12m"] == 37.5 and abs(p["yield_12m"] - 0.0375) < 1e-9


def test_payout_from_the_name():
    assert fund.NAME_ACC.search("Vanguard FTSE All-World U.ETF Reg.Shs USD Acc. oN")
    assert fund.NAME_DIS.search("Vanguard FTSE All-World U.ETF Reg.Shs USD Dis. oN")
    assert fund.NAME_DIS.search("iShares Core MSCI World UCITS ETF (Dist)")
    assert not fund.NAME_ACC.search("iShs Core MSCI EM IMI U.ETF Registered Shares o.N.")
    assert not fund.NAME_DIS.search("iShs Core MSCI EM IMI U.ETF Registered Shares o.N.")
