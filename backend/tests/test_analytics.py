import datetime as dt

import pytest

from groschen import demo
from groschen.analytics import cashflow, common, drilldown, networth, portfolio, recurring

TODAY = dt.date.today()


@pytest.fixture
def loaded(run_job):
    demo.load(today=TODAY)


def test_xirr_matches_a_known_value():
    flows = [(dt.date(2025, 1, 1), -1000.0), (dt.date(2026, 1, 1), 1100.0)]
    assert portfolio.xirr(flows) == pytest.approx(0.10, abs=1e-4)


def test_xirr_needs_money_in_and_out():
    assert portfolio.xirr([(dt.date(2025, 1, 1), -1000.0)]) is None


def test_stats_skip_a_month_that_started_with_cents():
    values = [
        {"month": "2024-06", "value": 0.01},
        {"month": "2024-07", "value": 299.07},
        {"month": "2024-08", "value": 600.0},
        {"month": "2024-09", "value": 906.0},
    ]
    s = portfolio.stats(values, {"2024-07": 300.0, "2024-08": 300.0, "2024-09": 300.0}, 0.0)
    assert [r["month"] for r in s["returns"]] == ["2024-08", "2024-09"]
    assert all(abs(r["r"]) < 0.05 for r in s["returns"])
    assert s["volatility"] < 0.2


def test_stats_on_a_steady_series():
    values = [{"month": f"2026-{m:02d}", "value": 1000 * 1.01**m} for m in range(1, 9)]
    s = portfolio.stats(values, {}, 0.0)
    assert s["twr"] == pytest.approx(1.01**12 - 1, rel=1e-6)  # annualized
    assert s["max_drawdown"] == 0
    assert s["months_up"] == 7


def test_last_30_days_goes_by_even_weeks(loaded, conn):
    start, end, label = common.resolve_range("last30", today=dt.date(2026, 10, 3))
    assert (start, end, label) == ("2026-09-04", "2026-10-03", "Last 30 days")
    start, end, label = common.resolve_range("last30", today=TODAY)
    summary = cashflow.summary(conn, start, end, label)
    trend = summary["trend"]
    assert trend["unit"] == "week"
    assert [(p["key"], p["end"]) for p in trend["points"]][0][0] == start and trend["points"][-1]["end"] == end
    days = [(dt.date.fromisoformat(p["end"]) - dt.date.fromisoformat(p["key"])).days + 1 for p in trend["points"]]
    assert sum(days) == 30 and max(days) - min(days) <= 1
    assert sum(p["spending"] for p in trend["points"]) == pytest.approx(summary["spending_total"], abs=0.05)
    assert summary["months"] == 1 and summary["avg_spending"] == summary["spending_total"]


def test_timeline_links_the_months(loaded, conn):
    tl = cashflow.timeline(conn, today=TODAY)
    months = tl["months"]
    assert months[0]["month"] == common.data_range(conn)[0][:7] and months[-1]["month"] == TODAY.isoformat()[:7]
    assert tl["account"] == "Girokonto" and tl["known"]
    for before, after in zip(months, months[1:]):
        assert after["carry_in"] == before["carry_out"]
    for m in months:
        placed = sum(p["amount"] for p in m["placed"])
        out = m["carry_in"] + m["income_total"] - m["spending_total"] - placed
        assert out == pytest.approx(m["carry_out"], abs=0.05)
    # The last month ends with today's balance, less salary already paid that counts for next month.
    giro = conn.execute("SELECT balance FROM accounts WHERE name = 'Girokonto'").fetchone()[0]
    assert months[-1]["carry_out"] <= giro + 0.005
    # Each month's numbers match the Overview for that month.
    m = months[-2]
    start, end, label = common.resolve_range("month", f"{m['month']}-01", today=TODAY)
    s = cashflow.summary(conn, start, end, label, split=True)
    assert m["income_total"] == s["income_total"] and m["spending_total"] == s["spending_total"]
    stays = next((p["amount"] for p in s["saved_to"]["parts"] if p["key"] == "stays"), 0.0)
    assert m["stays"] == pytest.approx(stays, abs=0.01)


def test_demo_history(loaded, conn):
    start, end, label = common.resolve_range("last12", today=TODAY)
    summary = cashflow.summary(conn, start, end, label)
    assert summary["income_total"] > 30000
    assert 0.1 < summary["savings_rate"] < 0.6
    assert not any(g["name"] == "Transfers" for g in summary["groups"])

    nw = networth.overview(conn)
    assert {a["name"] for a in nw["accounts"]} == {"Girokonto", "Extra-Konto", "Direkt-Depot"}
    assert nw["series"] and all(p["value"] > 0 for p in nw["series"])

    inv = portfolio.overview(conn)
    assert inv["value"] > 0 and inv["paid_in"] > 0
    assert inv["stats"]["months"] >= 12
    assert inv["xirr"] is not None


def test_subscriptions_and_price_rises(loaded, conn):
    subs = {s["name"]: s for s in recurring.detect(conn, TODAY)}
    assert subs["Netflix"]["price_change"] == pytest.approx(2.0)
    assert subs["Spotify"]["interval"] == "monthly"
    assert subs["Rundfunkbeitrag"]["interval"] == "quarterly"
    assert not any("REWE" in name for name in subs)


def test_drilldown_adds_up_to_the_chart(loaded, conn):
    start, end, label = common.resolve_range("last12", today=TODAY)
    summary = cashflow.summary(conn, start, end, label)
    for g in summary["groups"]:
        out = drilldown.build(conn, start=start, end=end, label=label, group=g["name"])
        assert out["summary"]["total"] == pytest.approx(g["amount"], abs=0.01)
        assert sum(c["amount"] for c in out["categories"]) == pytest.approx(g["amount"], abs=0.01)
        assert sum(m["amount"] for m in out["monthly"]) == pytest.approx(g["amount"], abs=0.01)
    for flow, items in (("spending", summary["categories"]), ("income", summary["income"])):
        for c in items:
            # Uncategorized has no category id; the charts open it as a group.
            scope = {"category_id": c["id"]} if c["id"] is not None else {"group": "Uncategorized", "flow": flow}
            out = drilldown.build(conn, start=start, end=end, label=label, **scope)
            assert out["summary"]["total"] == pytest.approx(c["amount"], abs=0.01)
            assert out["total"] == out["summary"]["count"]


def test_drilldown_filters_and_sorts(loaded, conn):
    start, end, label = common.resolve_range("last12", today=TODAY)
    kw = {"start": start, "end": end, "label": label, "group": "Food & Dining"}
    everything = drilldown.build(conn, **kw)
    assert everything["summary"]["count"] > 10
    by_amount = drilldown.build(conn, **kw, sort="amount")
    values = [-t["amount"] for t in by_amount["items"]]
    assert values == sorted(values, reverse=True)
    assert by_amount["summary"]["largest"]["value"] == values[0]
    oldest = drilldown.build(conn, **kw, desc=False)
    assert [t["date"] for t in oldest["items"]] == sorted(t["date"] for t in oldest["items"])
    by_name = drilldown.build(conn, **kw, sort="merchant", desc=False)
    names = [t["merchant"].lower() for t in by_name["items"]]
    assert names == sorted(names)

    small = drilldown.build(conn, **kw, max_amount=10)
    assert small["items"] and all(abs(t["amount"]) <= 10 for t in small["items"])
    one = everything["categories"][0]
    only = drilldown.build(conn, **kw, sub={one["id"]})
    assert {t["category_id"] for t in only["items"]} == {one["id"]}
    assert only["categories"] == everything["categories"]  # chips keep their numbers
    shop = everything["merchants"][0]["name"]
    found = drilldown.build(conn, **kw, q=shop[:5])
    assert found["items"] and all(shop[:5].lower() in t["merchant"].lower() for t in found["items"])
    assert len(drilldown.build(conn, **kw, limit=3)["items"]) == 3


def test_drilldown_unknown_scope(loaded, conn):
    start, end, label = common.resolve_range("last12", today=TODAY)
    assert drilldown.build(conn, start=start, end=end, label=label, group="No such group") is None
    assert drilldown.build(conn, start=start, end=end, label=label, category_id=99999) is None


def test_drilldown_for_one_payee(loaded, conn):
    start, end, label = common.resolve_range("last12", today=TODAY)
    food = drilldown.build(conn, start=start, end=end, label=label, group="Food & Dining")
    shop = food["merchants"][0]
    out = drilldown.build(conn, start=start, end=end, label=label, merchant=shop["name"].upper())
    assert out["scope"]["kind"] == "merchant" and out["scope"]["name"] == shop["name"]
    assert out["summary"]["total"] == pytest.approx(shop["amount"], abs=0.01)
    assert {t["merchant"] for t in out["items"]} == {shop["name"]}
    history = out["all_time"]
    assert history["total"] >= out["summary"]["total"] and history["count"] >= out["summary"]["count"]
    assert sum(m["amount"] for m in history["monthly"]) == pytest.approx(history["total"], abs=0.01)
    salary_id = conn.execute("SELECT id FROM categories WHERE name = 'Salary'").fetchone()[0]
    salary = drilldown.build(conn, start=start, end=end, label=label, category_id=salary_id)["merchants"][0]
    assert (
        drilldown.build(conn, start=start, end=end, label=label, merchant=salary["name"])["scope"]["direction"] == "income"
    )
    assert drilldown.build(conn, start=start, end=end, label=label, merchant="Nobody at all") is None
