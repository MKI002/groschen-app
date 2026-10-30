"""Income, spending and savings for a period."""

import datetime as dt
import math
import statistics

from .. import db, settings
from . import alerts, common, paydays, portfolio, savings


def summary(conn, start: str, end: str, label: str = "", split: bool = False) -> dict:
    """``split`` adds where the saved money went (the Overview)."""
    cats = common.categories(conn)
    txs = _load(conn, start, end)
    first, last = common.data_range(conn)
    if first and start < first:
        start_eff = first
    else:
        start_eff = start
    months = common.months_between(start_eff, end) if start_eff <= end else []
    monthly = {m: {"month": m, "income": 0.0, "spending": 0.0} for m in months}

    income: dict[str, float] = {}
    income_ids: dict[str, int | None] = {}
    groups: dict[str, dict] = {}
    cat_totals: dict = {}
    cat_month: dict = {}
    for t in txs:
        flow, cat = common.classify_flow(t, cats)
        if flow == "transfer":
            continue
        m = common.month_key(t["counts_for"])
        row = monthly.setdefault(m, {"month": m, "income": 0.0, "spending": 0.0})
        if flow == "income":
            income[cat["name"]] = income.get(cat["name"], 0.0) + t["amount"]
            income_ids[cat["name"]] = cat["id"]
            row["income"] += t["amount"]
        else:
            amount = -t["amount"]
            row["spending"] += amount
            g = groups.setdefault(
                cat["grp"], {"name": cat["grp"], "color": cat.get("color") or "muted", "amount": 0.0, "categories": {}}
            )
            g["amount"] += amount
            g["categories"][cat["name"]] = g["categories"].get(cat["name"], 0.0) + amount
            ck = (cat["id"], cat["name"], cat["grp"], cat.get("color") or "muted")
            cat_totals[ck] = cat_totals.get(ck, 0.0) + amount
            cat_month.setdefault(ck, {}).setdefault(m, 0.0)
            cat_month[ck][m] += amount

    income_total = round(sum(income.values()), 2)
    spending_total = round(sum(g["amount"] for g in groups.values()), 2)
    saved = round(income_total - spending_total, 2)

    group_list = sorted(
        (
            {
                "name": g["name"],
                "color": g["color"],
                "amount": round(g["amount"], 2),
                "share": g["amount"] / spending_total if spending_total else 0,
                "categories": sorted(
                    ({"name": n, "amount": round(a, 2)} for n, a in g["categories"].items()), key=lambda x: -x["amount"]
                ),
            }
            for g in groups.values()
            if abs(g["amount"]) >= 0.005
        ),
        key=lambda g: (g["name"] == "Uncategorized", -g["amount"]),
    )
    cat_list = sorted(
        (
            {
                "id": k[0],
                "name": k[1],
                "group": k[2],
                "color": k[3],
                "amount": round(v, 2),
                "share": v / spending_total if spending_total else 0,
            }
            for k, v in cat_totals.items()
            if abs(v) >= 0.005
        ),
        key=lambda c: -c["amount"],
    )
    income_list = sorted(
        (
            {"id": income_ids[n], "name": n, "amount": round(v, 2), "share": v / income_total if income_total else 0}
            for n, v in income.items()
        ),
        key=lambda x: -x["amount"],
    )
    monthly_list = [
        {"month": r["month"], "income": round(r["income"], 2), "spending": round(r["spending"], 2)}
        for r in sorted(monthly.values(), key=lambda r: r["month"])
    ]

    insights = _insights(monthly_list, cat_month, conn, first)
    review = conn.execute(
        "SELECT COUNT(*) FROM transactions WHERE needs_review = 1 AND date >= ? AND date <= ?", (start, end)
    ).fetchone()[0]
    n_months = max(1, len([m for m in monthly_list if m["income"] or m["spending"]]))
    if common.about_a_month(start, end):
        n_months = 1
    out = {
        "range": {"start": start, "end": end, "label": label},
        "income_total": income_total,
        "spending_total": spending_total,
        "saved": saved,
        "savings_rate": saved / income_total if income_total > 0 else None,
        "months": n_months,
        "avg_income": round(income_total / n_months, 2),
        "avg_spending": round(spending_total / n_months, 2),
        "income": income_list,
        "groups": group_list,
        "categories": cat_list,
        "monthly": monthly_list,
        "trend": _trend(txs, cats, monthly_list, start_eff, end),
        "transaction_count": len(txs),
        "review_count": review,
        "insights": insights,
    }
    if split:
        out["saved_to"] = savings.destinations(conn, start, end, saved, txs)
    return out


# Accounts whose money is "just there" and carries from one month into the next on the timeline.
EVERYDAY = ("checking", "credit_card")


def timeline(conn, today: dt.date | None = None) -> dict:
    """Every month from the first booking to today, linked by the money that stays on the everyday account.

    A month starts with what came over from the month before (the everyday accounts' balance), adds its
    income, sends money to spending, investments and other accounts, and hands the rest to the next month.
    The balances are worked back from today's, month by month, so every month adds up exactly.
    """
    today = today or dt.date.today()
    first, _ = common.data_range(conn)
    if not first or first > today.isoformat():
        return {"months": [], "account": None, "known": False, "ahead": 0.0}
    start, end = first[:7] + "-01", today.isoformat()
    cats = common.categories(conn)
    txs = _load(conn, start, end)
    months = common.months_between(start, end)
    by_month: dict[str, list[dict]] = {m: [] for m in months}
    payments = portfolio.payments(conn)
    for t in txs:
        by_month[common.month_key(t["counts_for"])].append(t)

    out = []
    for m in months:
        income: dict[str, dict] = {}
        groups: dict[str, dict] = {}
        for t in by_month[m]:
            flow, cat = common.classify_flow(t, cats)
            if flow == "transfer":
                continue
            if flow == "income":
                i = income.setdefault(cat["name"], {"name": cat["name"], "id": cat["id"], "amount": 0.0})
                i["amount"] += t["amount"]
            else:
                g = groups.setdefault(cat["grp"], {"name": cat["grp"], "color": cat.get("color") or "muted", "amount": 0.0})
                g["amount"] -= t["amount"]
        income_total = sum(i["amount"] for i in income.values())
        spending_total = sum(g["amount"] for g in groups.values())
        saved = income_total - spending_total
        m_end = min(common.month_end(m), end)
        split = savings.destinations(conn, f"{m}-01", m_end, saved, by_month[m], payments)
        placed: dict[str, dict] = {}
        for p in split["parts"]:
            if p["group"] == "stays":
                continue
            g = placed.setdefault(p["group"], {"key": p["group"], "amount": 0.0, "focus": p["key"], "top": 0.0})
            g["amount"] += p["amount"]
            if abs(p["amount"]) > g["top"]:
                g["focus"], g["top"] = p["key"], abs(p["amount"])
        stays = saved - sum(g["amount"] for g in placed.values())
        out.append(
            {
                "month": m,
                "income": sorted(
                    ({**i, "amount": round(i["amount"], 2)} for i in income.values()), key=lambda x: -x["amount"]
                ),
                "spending": sorted(
                    ({**g, "amount": round(g["amount"], 2)} for g in groups.values()), key=lambda x: -x["amount"]
                ),
                "placed": [
                    {"key": g["key"], "amount": round(g["amount"], 2), "focus": g["focus"]}
                    for g in placed.values()
                    if abs(g["amount"]) >= 0.005
                ],
                "income_total": round(income_total, 2),
                "spending_total": round(spending_total, 2),
                "stays": round(stays, 2),
            }
        )

    # Today's balance, less money already there that counts for next month (salary paid early).
    accounts = db.rows(
        conn.execute(
            "SELECT id, name, balance, balance_date FROM accounts WHERE enabled = 1 AND manual = 0 AND kind IN (?, ?)",
            EVERYDAY,
        )
    )
    ids = {a["id"] for a in accounts}
    moved = paydays.shifted(conn)
    ahead = sum(
        t["amount"]
        for t in common.load_transactions(conn, f"{months[-1]}-01", end)
        if t["account_id"] in ids and moved.get(t["id"], t["date"]) > end
    )
    known = any(a["balance_date"] for a in accounts)
    carry = sum(a["balance"] for a in accounts) - ahead
    for row in reversed(out):
        row["carry_out"] = round(carry, 2)
        carry -= row["stays"]
        row["carry_in"] = round(carry, 2)
    if not known:
        # No balance from the bank yet: start the lowest point at nothing instead of guessing.
        low = min(min(r["carry_in"], r["carry_out"]) for r in out)
        for r in out:
            r["carry_in"], r["carry_out"] = round(r["carry_in"] - low, 2), round(r["carry_out"] - low, 2)
    return {
        "months": out,
        "account": accounts[0]["name"] if len(accounts) == 1 else None,
        "known": known,
        "ahead": round(ahead, 2),
    }


WEEKS = ((1, 7), (8, 14), (15, 21), (22, 31))  # the last "week" runs to the end of the month


def _rolling_weeks(txs: list[dict], cats: dict, start: str, end: str) -> list[dict]:
    """A short period that doesn't start on the 1st, like the last 30 days: even steps of about a week."""
    s, e = dt.date.fromisoformat(start), dt.date.fromisoformat(end)
    days = (e - s).days + 1
    n = math.ceil(days / 7)
    size, extra = divmod(days, n)
    points, d = [], s
    for i in range(n):
        last = d + dt.timedelta(days=size + (1 if i < extra else 0) - 1)
        points.append(
            {"key": d.isoformat(), "end": last.isoformat(), "from": d.day, "to": last.day, "income": 0.0, "spending": 0.0}
        )
        d = last + dt.timedelta(days=1)
    for t in txs:
        flow, _ = common.classify_flow(t, cats)
        p = next((p for p in points if p["key"] <= t["counts_for"] <= p["end"]), None)
        if flow == "transfer" or p is None:
            continue
        if flow == "income":
            p["income"] += t["amount"]
        else:
            p["spending"] -= t["amount"]
    return points


def _trend(txs: list[dict], cats: dict, monthly: list[dict], start: str, end: str) -> dict:
    """Income and spending over time, in steps that suit the period: weeks, months, or years."""
    if common.about_a_month(start, end) and (start[8:10] != "01" or len(monthly) > 1):
        points, unit = _rolling_weeks(txs, cats, start, end), "week"
    elif len(monthly) == 1:
        month = monthly[0]["month"]
        last = int(min(end, common.month_end(month))[8:10])
        points = [
            {"key": f"{month}-{a:02d}", "from": a, "to": min(b, last), "income": 0.0, "spending": 0.0}
            for a, b in WEEKS
            if a <= last
        ]
        for t in txs:
            flow, _ = common.classify_flow(t, cats)
            if flow == "transfer" or common.month_key(t["counts_for"]) != month:
                continue
            day = int(t["counts_for"][8:10])
            p = [p for p in points if p["from"] <= day][-1]
            if flow == "income":
                p["income"] += t["amount"]
            else:
                p["spending"] -= t["amount"]
        unit = "week"
    elif len(monthly) > 36:
        by_year: dict[str, dict] = {}
        for m in monthly:
            y = by_year.setdefault(m["month"][:4], {"key": m["month"][:4], "income": 0.0, "spending": 0.0})
            y["income"] += m["income"]
            y["spending"] += m["spending"]
        points, unit = list(by_year.values()), "year"
    else:
        points = [{"key": m["month"], "income": m["income"], "spending": m["spending"]} for m in monthly]
        unit = "month"
    for p in points:
        p["income"], p["spending"] = round(p["income"], 2), round(p["spending"], 2)
    return {"unit": unit, "points": points}


def _load(conn, start: str, end: str) -> list[dict]:
    """Transactions that count for the period: salary paid late last month is in, late this month is out."""
    moved = paydays.shifted(conn)
    invested = _invested(conn)
    # Salary from the last days of the month before counts for this period, so read a month further back.
    early = (dt.date.fromisoformat(max(start, "1900-02-01")).replace(day=1) - dt.timedelta(days=1)).replace(day=1)
    out = []
    for t in common.load_transactions(conn, early.isoformat(), end):
        t["counts_for"] = moved.get(t["id"], t["date"])
        t["invest"] = t["id"] in invested
        if start <= t["counts_for"] <= end:
            out.append(t)
    return out


def _invested(conn) -> set[int]:
    """Payments into investments, and bookings the user said were saved somewhere: moved, not spent."""
    return {p["id"] for p in portfolio.payments(conn) if p["counted"]} | savings.placed_by_hand(conn)


def _insights(monthly: list[dict], cat_month: dict, conn, first: str | None) -> list[dict]:
    """The costliest month of the period, when "Highlight expensive months" is on.

    Only whole months count: not the running one, and not the first one when the bank data
    starts in the middle of it. Price rises are hints of their own (analytics/alerts.py):
    switched off there, they stay off.
    """
    out = []
    if not settings.get(conn, "unusual_alerts"):
        return out
    running = dt.date.today().strftime("%Y-%m")
    partial = first[:7] if first and int(first[8:10]) > 3 else None
    spent = [m for m in monthly if m["spending"] > 0 and m["month"] not in (running, partial)]
    if len(spent) >= 4:
        for m in spent:
            others = [o["spending"] for o in spent if o["month"] != m["month"]]
            avg = statistics.mean(others)
            if avg > 0 and m["spending"] > avg * 1.25:
                driver, diff = None, 0.0
                for ck, per_month in cat_month.items():
                    other_vals = [v for k, v in per_month.items() if k != m["month"]]
                    base = sum(other_vals) / max(1, len(spent) - 1)
                    d = per_month.get(m["month"], 0.0) - base
                    if d > diff:
                        driver, diff = ck[1], d
                pct = round((m["spending"] / avg - 1) * 100)
                out.append(
                    {
                        "key": f"month:{m['month']}",
                        "kind": "high_month",
                        "month": m["month"],
                        "percent": pct,
                        "driver": driver,
                        "driver_amount": round(diff, 2),
                    }
                )
        out.sort(key=lambda i: -i["percent"])
    # Closed with the X: that month stays hidden (Settings can bring it back).
    gone = alerts.dismissed(conn)
    return [i for i in out if i["key"] not in gone][:1]


def spending_for(conn, start: str, end: str, category_ids: list[int]) -> dict:
    """Totals for a subset of categories (used by group pages)."""
    s = summary(conn, start, end)
    wanted = set(category_ids)
    cats = [c for c in s["categories"] if c["id"] in wanted]
    total = round(sum(c["amount"] for c in cats), 2)
    return {"total": total, "months": s["months"], "categories": cats}


def daily(conn, start: str, end: str) -> dict:
    """Spending per calendar day (refunds subtract), for the year heatmap on the Spending page."""
    cats = common.categories(conn)
    days: dict[str, dict] = {}
    invested = _invested(conn)
    for t in common.load_transactions(conn, start, end):
        t["invest"] = t["id"] in invested
        flow, _ = common.classify_flow(t, cats)
        if flow != "spending":
            continue
        d = days.setdefault(t["date"], {"date": t["date"], "amount": 0.0, "count": 0})
        d["amount"] -= t["amount"]
        d["count"] += 1
    items = [{**d, "amount": round(d["amount"], 2)} for d in sorted(days.values(), key=lambda d: d["date"])]
    first, last = common.data_range(conn)
    return {"start": start, "end": end, "first": first, "last": last, "days": items}
