"""ETF depot: value over time, money paid in, and the statistics behind the charts.

Everything is computed from data already on the server: the holdings ING sends
at every sync (recorded daily), savings plan payments on the Girokonto, and an
optional price file the user imported. Nothing is fetched from the internet.
"""

import bisect
import datetime as dt
import math
import re
import statistics

from .. import db, i18n, settings
from . import common
from .drilldown import display_name

ISIN_RE = re.compile(r"\b([A-Z]{2}[A-Z0-9]{9}\d)\b")


class Prices:
    def __init__(self, conn):
        self.by_isin: dict[str, tuple[list[str], list[float]]] = {}
        rows = conn.execute("SELECT isin, date, price FROM prices ORDER BY isin, date").fetchall()
        for r in rows:
            dates, values = self.by_isin.setdefault(r["isin"], ([], []))
            dates.append(r["date"])
            values.append(r["price"])

    def at(self, isin: str, date: str, max_gap_days: int = 12) -> float | None:
        series = self.by_isin.get(isin)
        if not series:
            return None
        dates, values = series
        i = bisect.bisect_right(dates, date) - 1
        if i >= 0:
            gap = (dt.date.fromisoformat(date) - dt.date.fromisoformat(dates[i])).days
            if gap <= max_gap_days:
                return values[i]
        return None


def depot_accounts(conn) -> list[dict]:
    return db.rows(conn.execute("SELECT id, name, balance FROM accounts WHERE kind = 'depot' AND enabled = 1 AND fx_ok = 1"))


# Bookings that look like buying or selling securities, whatever category they ended up in.
TRADE_RE = re.compile(r"\bWP-ABRECHNUNG\b|\bWERTPAPIER|\bWP-(?:KAUF|VERKAUF)\b")
TRADE_WITH_ISIN_RE = re.compile(r"\b(?:VER)?KAUF\b|\bSPARPLAN\b|\bETF\b|\bFONDS\b|\bDEPOT\b")
# Money sent to a broker or robo-advisor is investing too, even without an ISIN.
BROKER_RE = re.compile(
    r"\bTRADE REPUBLIC\b|\bSCALABLE CAPITAL\b|\bSMARTBROKER\b|\bFLATEX\b|\bJUSTTRADE\b|\bDEGIRO\b|"
    r"\bFINANZEN\.NET ZERO\b|\bBAADER BANK\b|\bEBASE\b|\bFONDSDEPOT BANK\b|\bQUIRION\b|\bWHITEBOX\b|"
    r"\bGINMON\b|\bLIQID\b|\bEXTRAETF\b"
)
# Payouts, taxes, interest and fees mention the fund too but are not money put in.
NOT_TRADE_RE = re.compile(
    r"ERTRAG|AUSSCH(?:Ü|UE)TTUNG|DIVIDENDE|VORABPAUSCHALE|STEUER|\bZINS|GEB(?:Ü|UE)HR|ENTGELT|ERSTATTUNG"
)
# Cheap pre-filter so only a handful of rows reach the expressions above.
_HINTS = (
    "WP-",
    "WERTPAPIER",
    "KAUF",
    "SPARPLAN",
    "ETF",
    "FONDS",
    "DEPOT",
    "TRADE REPUBLIC",
    "SCALABLE",
    "SMARTBROKER",
    "FLATEX",
    "JUSTTRADE",
    "DEGIRO",
    "FINANZEN.NET",
    "BAADER",
    "EBASE",
    "QUIRION",
    "WHITEBOX",
    "GINMON",
    "LIQID",
    "EXTRAETF",
)
INVEST_GROUP = "Saving & investing"


def _text(r: dict) -> str:
    return f"{r['counterparty'] or ''} {r['purpose'] or ''} {r['booking_text'] or ''}".upper()


def looks_like_investment(text: str, amount: float) -> bool:
    """A booking that reads like buying (or selling) securities or paying into a broker."""
    if NOT_TRADE_RE.search(text):
        return False
    if amount > 0 and "VERKAUF" not in text:
        return False
    if TRADE_RE.search(text) or BROKER_RE.search(text):
        return True
    return bool(ISIN_RE.search(text) and TRADE_WITH_ISIN_RE.search(text))


def payments(conn) -> list[dict]:
    """Every payment into (or out of) investments on the normal accounts, oldest first.

    Counted by default: everything in the Investments category (or another category of the
    "Saving & investing" group except Savings), plus bookings that read like a securities trade
    or a transfer to a broker, unless the user filed them under another category themselves.
    The user can take any of them out with one click (invest_skips) and put it back.
    """
    hints = " OR ".join(
        "UPPER(COALESCE(t.counterparty, '') || ' ' || COALESCE(t.purpose, '') || ' ' || COALESCE(t.booking_text, '')) LIKE ?"
        for _ in _HINTS
    )
    rows = db.rows(
        conn.execute(
            "SELECT t.id, t.date, t.amount, t.purpose, t.counterparty, t.booking_text, t.cat_source, "
            "c.name AS category, c.grp AS category_group, s.tx_id IS NOT NULL AS skipped "
            "FROM transactions t JOIN accounts a ON a.id = t.account_id "
            "LEFT JOIN categories c ON c.id = t.category_id LEFT JOIN invest_skips s ON s.tx_id = t.id "
            "WHERE a.kind != 'depot' AND t.amount != 0 AND ("
            "c.name = 'Investments' OR (c.grp = ? AND c.name != 'Savings') OR " + hints + " "
            "OR t.id IN (SELECT tx_id FROM saving_dest WHERE dest IN ('plan', 'etf', 'roundup'))) "
            "ORDER BY t.date, t.id",
            (INVEST_GROUP, *(f"%{h}%" for h in _HINTS)),
        )
    )
    by_hand = {r[0] for r in conn.execute("SELECT tx_id FROM saving_dest WHERE dest IN ('plan', 'etf', 'roundup')")}
    out = []
    for r in rows:
        text = _text(r)
        if r["id"] in by_hand:
            how = "user"  # sent to ETFs on the Overview
        elif r["category"] == "Investments" or (r["category_group"] == INVEST_GROUP and r["category"] != "Savings"):
            how = "category"
        elif r["cat_source"] in ("user", "rule") and r["category"]:
            continue  # the user said what this is; don't second-guess it
        elif r["category"] == "Interest & dividends" or not looks_like_investment(text, r["amount"]):
            continue
        else:
            how = "detected"
        m = ISIN_RE.search(text)
        out.append(
            {
                "id": r["id"],
                "date": r["date"],
                "amount": round(-r["amount"], 2),
                "isin": m.group(1) if m else None,
                "how": how,
                "counted": not r["skipped"],
                "name": display_name(r),
                "purpose": (r["purpose"] or "")[:140],
                "category": r["category"],
            }
        )
    return out


def contributions(conn) -> list[dict]:
    """Money moved into investments that counts: savings plan and single purchases booked on normal accounts."""
    return [{"date": p["date"], "amount": p["amount"], "isin": p["isin"]} for p in payments(conn) if p["counted"]]


def set_counted(conn, tx_id: int, counted: bool) -> None:
    if counted:
        conn.execute("DELETE FROM invest_skips WHERE tx_id = ?", (tx_id,))
    else:
        conn.execute("INSERT OR IGNORE INTO invest_skips (tx_id, created_at) VALUES (?, ?)", (tx_id, db.now_iso()))


def _snapshot_totals(conn) -> dict[str, dict[int, float]]:
    """Recorded depot values by date: {date: {account_id: value}}."""
    out: dict[str, dict[int, float]] = {}
    for r in conn.execute("SELECT date, account_id, SUM(value) AS v FROM holding_history GROUP BY date, account_id"):
        out.setdefault(r["date"], {})[r["account_id"]] = r["v"]
    return out


def monthly_values(conn, months: list[str], today: dt.date) -> dict[str, dict[int, float]]:
    """Month-end depot values per account, from recorded snapshots or reconstructed from imported prices."""
    snaps = _snapshot_totals(conn)
    snap_dates = sorted(snaps)
    holdings = db.rows(conn.execute("SELECT account_id, isin, pieces, value FROM holdings"))
    prices = Prices(conn)
    flows = contributions(conn)
    out: dict[str, dict[int, float]] = {}
    for m in months:
        end = min(common.month_end(m), today.isoformat())
        i = bisect.bisect_right(snap_dates, end) - 1
        if i >= 0 and snap_dates[i][:7] == m:
            out[m] = dict(snaps[snap_dates[i]])
            continue
        if not holdings:
            continue
        rec = _reconstruct(holdings, flows, prices, end)
        if rec:
            out[m] = rec
    return out


def _reconstruct(holdings: list[dict], flows: list[dict], prices: Prices, date: str) -> dict[int, float] | None:
    """Estimate the depot at an earlier date by undoing later purchases at the prices of their day."""
    total_value = sum(h["value"] for h in holdings) or 1.0
    per_account: dict[int, float] = {}
    for h in holdings:
        pieces = h["pieces"]
        weight = h["value"] / total_value
        for f in flows:
            if f["date"] <= date:
                continue
            share = f["amount"] if f["isin"] == h["isin"] else (f["amount"] * weight if f["isin"] is None else 0.0)
            if not share:
                continue
            p = prices.at(h["isin"], f["date"])
            if p is None:
                return None
            pieces -= share / p
        price = prices.at(h["isin"], date)
        if price is None:
            return None
        per_account[h["account_id"]] = per_account.get(h["account_id"], 0.0) + max(pieces, 0.0) * price
    return per_account


MAX_DAILY_POINTS = 900


def _snapshot_by_isin(conn) -> dict[str, dict[str, float]]:
    """Recorded values per ETF by date: {date: {isin: value}}."""
    out: dict[str, dict[str, float]] = {}
    for r in conn.execute("SELECT date, isin, SUM(value) AS v FROM holding_history GROUP BY date, isin"):
        out.setdefault(r["date"], {})[r["isin"]] = r["v"]
    return out


def daily_values(conn, flows: list[dict], today: dt.date, current: float | None = None, per_holding: bool = False):
    """Depot value on every trading day, like the bank's own chart.

    A day ING recorded (holding_history) uses that value. Any other day takes the units held
    that day (today's units minus everything bought later, at the price of its day) times
    that day's price. It starts at the first payment or the first recorded day, not at the
    fund's launch, and stops going back once a purchase has no price to undo it with.

    per_holding also returns each ETF's own value and money paid into it on the same days,
    {isin: [[value, paid_in], ...]}, so a period can be looked at ETF by ETF.
    """
    snaps = {d: sum(v.values()) for d, v in _snapshot_totals(conn).items()}
    holdings = db.rows(conn.execute("SELECT account_id, isin, pieces, value FROM holdings"))
    starts = [d for d in (min(snaps, default=None), flows[0]["date"] if flows else None) if d]
    if not starts or (not holdings and not snaps):
        return ([], {}) if per_holding else []
    start = dt.date.fromisoformat(min(starts))
    prices = Prices(conn)
    total = sum(h["value"] for h in holdings) or 1.0

    # Per holding: the units bought after each payment (newest first), and how far back that reaches.
    plans = []
    for h in holdings:
        weight = h["value"] / total
        buys, limit = [], None
        for f in reversed(flows):
            share = f["amount"] if f["isin"] == h["isin"] else (f["amount"] * weight if f["isin"] is None else 0.0)
            if not share:
                continue
            p = prices.at(h["isin"], f["date"])
            if p is None:
                limit = f["date"]  # can't undo this purchase: no reconstruction on or before it
                break
            buys.append((f["date"], share / p))
        plans.append({"isin": h["isin"], "pieces": h["pieces"], "buys": buys, "i": 0, "limit": limit})

    days = []
    d = today
    while d >= start:
        if d.weekday() < 5:
            days.append(d.isoformat())
        d -= dt.timedelta(days=1)

    values: dict[str, float] = {}
    by_day: dict[str, dict[str, float]] = {}
    snap_isins = _snapshot_by_isin(conn) if per_holding else {}
    for day in days:  # newest first, so each holding's later purchases come off one by one
        total_value, ok, parts = 0.0, bool(plans), {}
        for pl in plans:
            while pl["i"] < len(pl["buys"]) and pl["buys"][pl["i"]][0] > day:
                pl["pieces"] -= pl["buys"][pl["i"]][1]
                pl["i"] += 1
            price = prices.at(pl["isin"], day) if not (pl["limit"] and day <= pl["limit"]) else None
            if price is None:
                ok = False
                continue
            value = max(pl["pieces"], 0.0) * price
            total_value += value
            parts[pl["isin"]] = parts.get(pl["isin"], 0.0) + value
        if day in snaps:
            values[day] = snaps[day]
            parts = snap_isins.get(day, parts)
        elif ok:
            values[day] = total_value
        if per_holding and day in values:
            by_day[day] = parts
    if current is not None and values:
        values[today.isoformat()] = current
        if per_holding:
            now: dict[str, float] = {}
            for h in holdings:
                now[h["isin"]] = now.get(h["isin"], 0.0) + h["value"]
            by_day[today.isoformat()] = now

    out, invested, fi = [], 0.0, 0
    for day in sorted(values):
        while fi < len(flows) and flows[fi]["date"] <= day:
            invested += flows[fi]["amount"]
            fi += 1
        out.append({"date": day, "value": round(values[day], 2), "paid_in": round(invested, 2)})
    # Days before the first unit was bought read as zero: leave them out.
    while len(out) > 1 and out[0]["value"] < 1 and out[1]["value"] < 1:
        out.pop(0)
    if len(out) > MAX_DAILY_POINTS:
        step = math.ceil(len(out) / MAX_DAILY_POINTS)
        out = out[::-1][::step][::-1]
    if not per_holding:
        return out
    return out, _holding_series(out, by_day, holdings, flows)


def _holding_series(days: list[dict], by_day: dict[str, dict[str, float]], holdings: list[dict], flows: list[dict]) -> dict:
    """Each current ETF's value and the money paid into it, on the days of the depot's series."""
    total = sum(h["value"] for h in holdings) or 1.0
    weights: dict[str, float] = {}
    for h in holdings:
        weights[h["isin"]] = weights.get(h["isin"], 0.0) + h["value"] / total
    out: dict[str, list[list[float]]] = {isin: [] for isin in weights}
    paid = dict.fromkeys(weights, 0.0)
    fi = 0
    for d in days:
        while fi < len(flows) and flows[fi]["date"] <= d["date"]:
            f = flows[fi]
            for isin, w in weights.items():
                # A payment without an ISIN went into the depot as a whole: split like the holdings.
                paid[isin] += f["amount"] if f["isin"] == isin else (f["amount"] * w if f["isin"] is None else 0.0)
            fi += 1
        parts = by_day.get(d["date"], {})
        for isin in weights:
            out[isin].append([round(parts.get(isin, 0.0), 2), round(paid[isin], 2)])
    return out


def xirr(flows: list[tuple[dt.date, float]]) -> float | None:
    """Money-weighted annual return. flows: (date, amount) with payments in negative, final value positive."""
    if len(flows) < 2 or not any(a > 0 for _, a in flows) or not any(a < 0 for _, a in flows):
        return None
    t0 = flows[0][0]

    def npv(rate):
        return sum(a / (1 + rate) ** ((d - t0).days / 365.0) for d, a in flows)

    lo, hi = -0.99, 10.0
    f_lo, f_hi = npv(lo), npv(hi)
    if f_lo * f_hi > 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2
        f_mid = npv(mid)
        if abs(f_mid) < 1e-7:
            break
        if f_lo * f_mid < 0:
            hi, f_hi = mid, f_mid
        else:
            lo, f_lo = mid, f_mid
    return (lo + hi) / 2


def stats(values: list[dict], flows_by_month: dict[str, float], rf_percent: float) -> dict | None:
    """values: [{month, value}] consecutive month ends."""
    if len(values) < 3:
        return None
    returns = []
    for prev, cur in zip(values, values[1:]):
        # A month that ended with only cents in the depot (the savings plan started right after)
        # is no base for a return: 300 € arriving on 0.01 € would read as -9,400 %.
        if prev["value"] < 1:
            continue
        r = (cur["value"] - flows_by_month.get(cur["month"], 0.0)) / prev["value"] - 1
        returns.append({"month": cur["month"], "r": r})
    if len(returns) < 2:
        return None
    rs = [x["r"] for x in returns]
    growth = math.prod(1 + r for r in rs)
    n = len(rs)
    twr = growth ** (12 / n) - 1 if growth > 0 else None
    vol = statistics.stdev(rs) * math.sqrt(12) if n > 1 else None
    index, peak, dd = 1.0, 1.0, []
    for x in returns:
        index *= 1 + x["r"]
        peak = max(peak, index)
        dd.append({"month": x["month"], "dd": index / peak - 1})
    worst_dd = min(dd, key=lambda d: d["dd"])
    best = max(returns, key=lambda x: x["r"])
    worst = min(returns, key=lambda x: x["r"])
    rf = rf_percent / 100
    return {
        "twr": twr,
        "volatility": vol,
        "max_drawdown": worst_dd["dd"],
        "max_drawdown_month": worst_dd["month"],
        "sharpe": (twr - rf) / vol if twr is not None and vol else None,
        "best": best,
        "worst": worst,
        "months_up": sum(1 for r in rs if r > 0),
        "months": n,
        "returns": returns,
        "drawdown": dd,
        "risk_free": rf_percent,
    }


def overview(conn, today: dt.date | None = None) -> dict:
    today = today or dt.date.today()
    accounts = depot_accounts(conn)
    holdings = db.rows(
        conn.execute(
            "SELECT h.account_id, h.isin, h.name, h.pieces, h.price, h.price_date, h.value, h.acquisition_price "
            "FROM holdings h JOIN accounts a ON a.id = h.account_id "
            "WHERE a.enabled = 1 AND a.fx_ok = 1 ORDER BY h.value DESC"
        )
    )
    value = round(sum(h["value"] for h in holdings), 2)
    flows = contributions(conn)
    has_cost = holdings and all(h["acquisition_price"] for h in holdings)
    for h in holdings:
        h["cost"] = round(h["pieces"] * h["acquisition_price"], 2) if h["acquisition_price"] else None
        h["share"] = h["value"] / value if value else 0
        h["plan"] = _plan_amount(flows, h["isin"], today)
    paid_in = round(sum(h["cost"] for h in holdings), 2) if has_cost else round(sum(f["amount"] for f in flows), 2)
    paid_in_source = i18n.t("your bank's purchase prices") if has_cost else i18n.t("payments into your depot")

    first = conn.execute(
        "SELECT MIN(date) FROM (SELECT MIN(date) AS date FROM holding_history UNION SELECT MIN(date) FROM prices)"
    ).fetchone()[0]
    series = []
    if first:
        months = common.months_between(first[:7] + "-01", today.isoformat())
        mv = monthly_values(conn, months, today)
        invested = 0.0
        flow_idx = 0
        flows_by_month: dict[str, float] = {}
        for f in flows:
            flows_by_month[f["date"][:7]] = flows_by_month.get(f["date"][:7], 0.0) + f["amount"]
        for m in months:
            end = common.month_end(m)
            while flow_idx < len(flows) and flows[flow_idx]["date"] <= end:
                invested += flows[flow_idx]["amount"]
                flow_idx += 1
            if m in mv:
                series.append({"month": m, "value": round(sum(mv[m].values()), 2), "paid_in": round(invested, 2)})
    else:
        flows_by_month = {}

    rf = float(settings.get(conn, "risk_free_rate") or 0)
    st = stats(series, flows_by_month, rf)
    xirr_flows = []
    if series:
        start_month = series[0]["month"]
        start_date = dt.date.fromisoformat(common.month_end(start_month))
        xirr_flows.append((start_date, -series[0]["value"]))
        for f in flows:
            d = dt.date.fromisoformat(f["date"])
            if d > start_date:
                xirr_flows.append((d, -f["amount"]))
        xirr_flows.append((today, value or series[-1]["value"]))
    days_recorded = conn.execute("SELECT COUNT(DISTINCT date) FROM holding_history").fetchone()[0]

    allowance_used = conn.execute(
        "SELECT COALESCE(SUM(t.amount), 0) FROM transactions t JOIN categories c ON c.id = t.category_id "
        "WHERE c.name = 'Interest & dividends' AND t.amount > 0 AND t.date >= ?",
        (f"{today.year}-01-01",),
    ).fetchone()[0]
    daily, by_holding = daily_values(conn, flows, today, value if holdings else None, per_holding=True)
    return {
        "accounts": accounts,
        "value": value,
        "paid_in": paid_in,
        "paid_in_source": paid_in_source,
        "gain": round(value - paid_in, 2) if paid_in else None,
        "holdings": holdings,
        "series": series,
        "daily": daily,
        "holding_daily": by_holding,
        "stats": st,
        "xirr": xirr(sorted(xirr_flows)) if len(xirr_flows) >= 2 else None,
        "days_recorded": days_recorded,
        "price_date": max((h["price_date"] for h in holdings if h["price_date"]), default=None),
        "monthly_plan": round(sum(h["plan"] or 0 for h in holdings), 2) or _plan_amount(flows, None, today),
        "allowance": {
            "used": round(allowance_used, 2),
            "limit": float(settings.get(conn, "tax_allowance") or 1000),
            "year": today.year,
        },
    }


def _plan_amount(flows: list[dict], isin: str | None, today: dt.date) -> float | None:
    """Typical monthly savings plan amount over the last 4 months."""
    since = (today - dt.timedelta(days=125)).isoformat()
    recent = [f for f in flows if f["date"] >= since and (isin is None or f["isin"] == isin)]
    if not recent:
        return None
    by_month: dict[str, float] = {}
    for f in recent:
        by_month[f["date"][:7]] = by_month.get(f["date"][:7], 0.0) + f["amount"]
    return round(statistics.median(by_month.values()), 2)
