"""One ETF in detail: its price history, returns, risk, how you bought it, and forecast inputs.

Prices come from the prices table: ING's price at each sync, an imported price file,
and, when "Online ETF prices" is on, the daily history from justETF. All returns are
price returns; distributions of distributing ETFs aren't counted.
"""

import bisect
import datetime as dt
import math
import re
import statistics

from .. import db, market, settings
from . import common, portfolio

# The long-run return the forecast leans on when an ETF's own history is short.
# Broad stock markets have returned roughly this much a year over long periods.
PRIOR_RETURN = 0.06
# Years of history that count as much as that long-run figure.
PRIOR_YEARS = 10
ISIN_RE = re.compile(r"^[A-Z]{2}[A-Z0-9]{9}\d$")
PERIODS = [("1m", 1), ("3m", 3), ("6m", 6), ("ytd", None), ("1y", 12), ("3y", 36), ("5y", 60), ("10y", 120), ("max", None)]


def price_series(conn, isin: str) -> list[tuple[str, float]]:
    return [
        (r["date"], r["price"]) for r in conn.execute("SELECT date, price FROM prices WHERE isin = ? ORDER BY date", (isin,))
    ]


def _is_daily(series: list[tuple[str, float]]) -> bool:
    if len(series) < 40:
        return False
    recent = series[-60:]
    gaps = [(dt.date.fromisoformat(b[0]) - dt.date.fromisoformat(a[0])).days for a, b in zip(recent, recent[1:])]
    return statistics.median(gaps) <= 4


def _at_or_before(dates: list[str], values: list[float], date: str) -> float | None:
    i = bisect.bisect_right(dates, date) - 1
    return values[i] if i >= 0 else None


def month_closes(series: list[tuple[str, float]]) -> list[tuple[str, float]]:
    out: dict[str, float] = {}
    for d, p in series:
        out[d[:7]] = p
    return sorted(out.items())


def _shift_months(day: dt.date, months: int) -> dt.date:
    y, m = divmod(day.year * 12 + day.month - 1 - months, 12)
    m += 1
    last = [31, 29 if y % 4 == 0 and (y % 100 or y % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
    return dt.date(y, m, min(day.day, last))


def periods(series: list[tuple[str, float]]) -> list[dict]:
    """Price change over the usual periods; three years and longer per year."""
    if len(series) < 2:
        return []
    dates = [d for d, _ in series]
    values = [p for _, p in series]
    end_date = dt.date.fromisoformat(dates[-1])
    last = values[-1]
    out = []
    for key, months in PERIODS:
        if key == "ytd":
            start = dt.date(end_date.year - 1, 12, 31)
        elif key == "max":
            start = dt.date.fromisoformat(dates[0])
        else:
            start = _shift_months(end_date, months)
        if start < dt.date.fromisoformat(dates[0]) - dt.timedelta(days=7):
            continue  # not enough history for this period
        base = _at_or_before(dates, values, start.isoformat()) or values[0]
        if not base:
            continue
        r = last / base - 1
        years = (end_date - max(start, dt.date.fromisoformat(dates[0]))).days / 365.25
        annual = key in ("3y", "5y", "10y") or (key == "max" and years >= 2)
        if annual and years > 0 and r > -1:
            r = (1 + r) ** (1 / years) - 1
        out.append({"key": key, "r": r, "annual": annual, "from": start.isoformat()})
    return out


def per_year(series: list[tuple[str, float]], start: str) -> float | None:
    """The price change per year from `start` to the last price, counted the way xirr counts.
    None when the prices begin well after `start` or cover less than three months."""
    if len(series) < 2:
        return None
    dates = [d for d, _ in series]
    values = [p for _, p in series]
    first, begin = dt.date.fromisoformat(dates[0]), dt.date.fromisoformat(start)
    if begin < first - dt.timedelta(days=7):
        return None
    base = _at_or_before(dates, values, start) or values[0]
    days = (dt.date.fromisoformat(dates[-1]) - max(begin, first)).days
    if not base or days < 91:
        return None
    return (values[-1] / base) ** (365.0 / days) - 1


def risk(series: list[tuple[str, float]], rf_percent: float) -> dict | None:
    if len(series) < 3:
        return None
    dates = [d for d, _ in series]
    values = [p for _, p in series]
    daily = _is_daily(series)
    closes = month_closes(series)
    monthly = [{"month": b[0], "r": b[1] / a[1] - 1} for a, b in zip(closes, closes[1:]) if a[1] > 0]

    vol = None
    if daily and len(values) > 60:
        tail = values[-757:]  # the last three years
        logs = [math.log(b / a) for a, b in zip(tail, tail[1:]) if a > 0 and b > 0]
        vol = statistics.stdev(logs) * math.sqrt(252) if len(logs) > 20 else None
    elif len(monthly) >= 6:
        vol = statistics.stdev([math.log(1 + m["r"]) for m in monthly[-36:]]) * math.sqrt(12)

    # Largest fall from a high, on every price we have.
    peak, peak_date = values[0], dates[0]
    worst = (0.0, dates[0], dates[0])
    for d, p in series:
        if p > peak:
            peak, peak_date = p, d
        dd = p / peak - 1
        if dd < worst[0]:
            worst = (dd, peak_date, d)
    recovered = None
    if worst[0] < 0:
        top = _at_or_before(dates, values, worst[1])
        i = bisect.bisect_right(dates, worst[2])
        recovered = next((dates[j] for j in range(i, len(dates)) if top and values[j] >= top), None)
    ath = max(values)
    ath_date = dates[values.index(ath)]
    year_ago = (dt.date.fromisoformat(dates[-1]) - dt.timedelta(days=365)).isoformat()
    last_year = [p for d, p in series if d >= year_ago]

    index, top_i, dd_monthly = 1.0, 1.0, []
    for m in monthly:
        index *= 1 + m["r"]
        top_i = max(top_i, index)
        dd_monthly.append({"month": m["month"], "dd": index / top_i - 1})

    # Every twelve months in a row, by the month they end in.
    rolling = [{"month": b[0], "r": b[1] / a[1] - 1} for a, b in zip(closes, closes[12:]) if a[1] > 0]
    twr = None
    span = (dt.date.fromisoformat(dates[-1]) - dt.date.fromisoformat(dates[0])).days / 365.25
    if span >= 1 and values[0] > 0:
        twr = (values[-1] / values[0]) ** (1 / span) - 1
    ma200 = statistics.fmean(values[-200:]) if daily and len(values) >= 200 else None
    rf = rf_percent / 100
    return {
        "volatility": vol,
        "max_drawdown": worst[0],
        "max_drawdown_from": worst[1],
        "max_drawdown_to": worst[2],
        "recovered": recovered,
        "current_drawdown": values[-1] / ath - 1,
        "ath": ath,
        "ath_date": ath_date,
        "high_52w": max(last_year) if last_year else None,
        "low_52w": min(last_year) if last_year else None,
        "cagr": twr,
        "sharpe": (twr - rf) / vol if twr is not None and vol else None,
        "months_up": sum(1 for m in monthly if m["r"] > 0),
        "months": len(monthly),
        "rolling_up": sum(1 for x in rolling if x["r"] > 0) / len(rolling) if rolling else None,
        "rolling_best": max(x["r"] for x in rolling) if rolling else None,
        "rolling_worst": min(x["r"] for x in rolling) if rolling else None,
        "rolling_count": len(rolling),
        "rolling": rolling,
        "ma200": ma200,
        "years_of_data": span,
        "monthly": monthly,
        "drawdown": dd_monthly,
    }


def calendar_years(series: list[tuple[str, float]]) -> list[dict]:
    out = []
    by_year: dict[int, tuple[float, float]] = {}
    for d, p in series:
        y = int(d[:4])
        first, _ = by_year.get(y, (p, p))
        by_year[y] = (first, p)
    years = sorted(by_year)
    for i, y in enumerate(years):
        base = by_year[years[i - 1]][1] if i and years[i - 1] == y - 1 else by_year[y][0]
        partial = i == 0 or years[i - 1] != y - 1 or y == dt.date.today().year
        if base > 0:
            out.append({"year": y, "r": by_year[y][1] / base - 1, "partial": partial})
    return out


def downsample(series: list[tuple[str, float]], limit: int = 900) -> list[dict]:
    """Enough points for a sharp chart: every day for short histories, fewer for long ones."""
    n = len(series)
    step = max(1, math.ceil(n / limit))
    picked = series[::step]
    if picked and picked[-1] != series[-1]:
        picked.append(series[-1])
    return [{"d": d, "p": round(p, 4)} for d, p in picked]


# --- does it pay out or reinvest? -------------------------------------------------------

PAYOUT_WORDS = re.compile(r"ertrag|aussch(ue|ü)tt|dividend|distribution|zinsgutschrift|ertr[aä]gnis", re.I)
NAME_ACC = re.compile(r"(\bacc\b|\bacc\.|\(acc\)|thesaur|\bthes\b|accumulating)", re.I)
NAME_DIS = re.compile(r"(\bdis\b|\bdis\.|\bdist\b|\bdist\.|\(dist?\)|aussch|distributing|\binc\b|\binc\.)", re.I)


def _frequency(count_per_year: int) -> str | None:
    if count_per_year >= 10:
        return "monthly"
    if count_per_year >= 5:
        return "bimonthly"
    if count_per_year >= 3:
        return "quarterly"
    if count_per_year == 2:
        return "semiannual"
    if count_per_year == 1:
        return "annual"
    return None


def payouts_received(conn, isin: str, today: dt.date) -> list[dict]:
    """Distributions booked on your accounts: money in whose text names this ETF's ISIN."""
    rows = conn.execute(
        "SELECT t.date, t.amount, t.purpose, t.counterparty, t.booking_text FROM transactions t "
        "WHERE t.amount > 0 AND (UPPER(t.purpose) LIKE ? OR UPPER(t.counterparty) LIKE ?) ORDER BY t.date",
        (f"%{isin}%", f"%{isin}%"),
    ).fetchall()
    out = []
    for r in rows:
        text = " ".join(x or "" for x in (r["purpose"], r["counterparty"], r["booking_text"]))
        # A sale also names the ISIN; a payout says so (Ertrag, Ausschüttung, Dividende).
        if PAYOUT_WORDS.search(text):
            out.append({"date": r["date"], "amount": round(r["amount"], 2)})
    return out


def payout(conn, isin: str, name: str | None, value: float | None, today: dt.date) -> dict:
    """Pays out or reinvests, and how often: from the fund's profile (online prices on),
    from payouts that reached your accounts, or from the fund name, in that order."""
    facts = market.facts(conn, isin) or {}
    received = payouts_received(conn, isin, today)
    year_ago = (today - dt.timedelta(days=365)).isoformat()
    last_year = [p for p in received if p["date"] > year_ago]
    total_12m = round(sum(p["amount"] for p in last_year), 2)
    months_12m = len({p["date"][:7] for p in last_year})
    held_since = conn.execute(
        "SELECT MIN(date) FROM (SELECT MIN(date) AS date FROM holding_history WHERE isin = ? "
        "UNION SELECT MIN(t.date) FROM transactions t WHERE UPPER(t.purpose) LIKE ?)",
        (isin, f"%{isin}%"),
    ).fetchone()[0]

    policy = frequency = source = None
    if facts.get("policy"):
        policy, source = facts["policy"], "profile"
        frequency = facts.get("frequency") if policy == "distributing" else None
    elif received:
        policy, source = "distributing", "bookings"
        frequency = _frequency(months_12m)
    elif name and NAME_ACC.search(name):
        policy, source = "accumulating", "name"
    elif name and NAME_DIS.search(name):
        policy, source = "distributing", "name"
    elif held_since and held_since <= year_ago:
        # Held for over a year and never a payout on the accounts: it reinvests.
        policy, source = "accumulating", "bookings"
    if policy == "distributing" and not frequency and months_12m:
        frequency = _frequency(months_12m)
    return {
        "policy": policy,
        "frequency": frequency,
        "source": source,
        "received": received[-24:],
        "received_12m": total_12m,
        "count_12m": len(last_year),
        "yield_12m": total_12m / value if value and total_12m else None,
        "dividend_yield": facts.get("dividend_yield"),
    }


# --- how the user bought it ---------------------------------------------------------------


def purchases(conn, isin: str) -> tuple[list[dict], bool]:
    """Payments into this ETF. When bank texts don't name the ISIN, they're split by current weight (estimated)."""
    flows = portfolio.contributions(conn)
    own = [f for f in flows if f["isin"] == isin]
    loose = [f for f in flows if f["isin"] is None]
    if not loose:
        return own, False
    holdings = db.rows(conn.execute("SELECT isin, SUM(value) AS value FROM holdings GROUP BY isin"))
    named = {f["isin"] for f in flows if f["isin"]}
    # Funds that already get their own named payments don't share the unnamed ones.
    sharing = [h for h in holdings if h["isin"] not in named or h["isin"] == isin and not own]
    total = sum(h["value"] for h in sharing) or 0
    mine = next((h["value"] for h in sharing if h["isin"] == isin), 0)
    if not total or not mine:
        return own, False
    weight = mine / total
    extra = [{**f, "amount": round(f["amount"] * weight, 2), "isin": isin} for f in loose]
    return sorted(own + extra, key=lambda f: f["date"]), weight < 0.999


def _months(first: str, last: str) -> list[str]:
    return [m for m in common.months_between(first[:7] + "-01", last)]


def investing(flows: list[dict], series: list[tuple[str, float]], today: dt.date) -> dict | None:
    """When and how much was paid in: rhythm, usual amount, changes to the plan, average buy price."""
    buys = [f for f in flows if f["amount"] > 0]
    if not buys:
        return None
    dates = [d for d, _ in series]
    values = [p for _, p in series]
    by_month: dict[str, float] = {}
    for f in buys:
        by_month[f["date"][:7]] = by_month.get(f["date"][:7], 0.0) + f["amount"]
    months = _months(buys[0]["date"], today.isoformat())
    monthly = [{"month": m, "amount": round(by_month.get(m, 0.0), 2)} for m in months]

    recent = [m for m in months[-7:-1] or months[-6:]]  # the last six full months
    paid_recent = [by_month[m] for m in recent if m in by_month]
    if len(buys) == 1:
        rhythm = "once"
    elif len(paid_recent) >= max(1, len(recent) - 1):
        rhythm = "monthly"
    elif len(paid_recent) >= 2 and len(recent) >= 6:
        rhythm = "quarterly" if len(paid_recent) <= 3 else "irregular"
    else:
        rhythm = "irregular"
    typical = round(statistics.median(paid_recent), 2) if paid_recent else 0.0
    day = round(statistics.median(int(f["date"][8:10]) for f in buys[-12:]))

    # What goes in per month on average over the last twelve months, this one included so a buy
    # made today already counts (or since the first payment, when that's shorter).
    window = months[-12:]
    in_window = [f for f in buys if f["date"][:7] >= window[0]]
    window_total = round(sum(f["amount"] for f in in_window), 2)
    pace = round(window_total / len(window), 2)
    # A steady plan (about the same amount nearly every month) is the best guess for the months
    # ahead. Anything else (one-off buys, round-ups, pauses) is best described by the average;
    # the median of such months would be the small round-ups and miss the big buys.
    steady = rhythm == "monthly" and typical > 0 and typical * 0.75 <= min(paid_recent) <= max(paid_recent) <= typical * 1.25
    if rhythm == "once":
        per_month, source = 0.0, "none"
    elif steady and abs(pace - typical) <= 0.25 * typical:
        per_month, source = typical, "plan"
    else:
        per_month, source = pace, "average"

    # The plan amount over time: runs of months with (about) the same payment.
    steps: list[dict] = []
    for m in months:
        a = by_month.get(m)
        if not a:
            continue
        a = round(a / 5) * 5 or round(a, 2)
        if not steps or abs(steps[-1]["amount"] - a) > max(1.0, steps[-1]["amount"] * 0.03):
            steps.append({"from": m, "to": m, "amount": a, "months": 1})
        else:
            steps[-1]["months"] += 1
            steps[-1]["to"] = m
    steps = [s for s in steps if s["months"] >= 2] or steps[-1:]

    # A steady plan that was raised over the years suggests it keeps growing; per year, from first to last step.
    raise_pa = 0.0
    if steady and len(steps) >= 2 and steps[0]["amount"] > 0:
        span = len(_months(steps[0]["from"] + "-01", steps[-1]["from"] + "-01")) / 12
        if span >= 1 and steps[-1]["amount"] > steps[0]["amount"]:
            raise_pa = min((steps[-1]["amount"] / steps[0]["amount"]) ** (1 / span) - 1, 0.1)

    units, spent, prices_paid = 0.0, 0.0, []
    for f in buys:
        p = _at_or_before(dates, values, f["date"]) if dates else None
        if p:
            f["price"] = p
            units += f["amount"] / p
            spent += f["amount"]
            prices_paid.append(p)
    avg_buy = spent / units if units else None
    avg_market = statistics.fmean(prices_paid) if prices_paid else None
    return {
        "rhythm": rhythm,
        "day": day,
        "typical": typical,
        "per_month": per_month,
        "raise_pa": raise_pa,
        "source": source,
        "steady": steady,
        "pace": pace,
        "window_months": len(window),
        "window_total": window_total,
        "window_count": len(in_window),
        "this_month": round(by_month.get(months[-1], 0.0), 2),
        "recent": round(sum(paid_recent) / max(len(recent), 1), 2),
        "steps": steps[-6:],
        "count": len(buys),
        "total": round(sum(f["amount"] for f in buys), 2),
        "first": buys[0]["date"],
        "last": buys[-1]["date"],
        "monthly": monthly[-36:],
        "purchases": [{k: f.get(k) for k in ("date", "amount", "price")} for f in buys[-400:]],
        "avg_buy": avg_buy,
        "avg_market": avg_market,
    }


def forecast_inputs(rk: dict | None) -> dict:
    """Expected return and swing for the forecast: the ETF's own past, leaning on the long-run
    figure the less history there is. A few strong years say little about the next ones."""
    vol = rk["volatility"] if rk and rk["volatility"] else None
    hist = rk["cagr"] if rk else None
    years = rk["years_of_data"] if rk else 0.0
    weight = years / (years + PRIOR_YEARS) if hist is not None else 0.0
    ret = weight * hist + (1 - weight) * PRIOR_RETURN if hist is not None else PRIOR_RETURN
    return {
        "ret": round(min(max(ret, -0.03), 0.12), 4),
        "vol": round(min(max(vol, 0.05), 0.45), 4) if vol else 0.15,
        "hist": hist,
        "weight": weight,
        "years": years,
        "prior": PRIOR_RETURN,
        "vol_known": vol is not None,
    }


def detail(conn, isin: str, today: dt.date | None = None) -> dict | None:
    today = today or dt.date.today()
    holding = db.one(
        conn.execute(
            "SELECT MAX(h.name) AS name, SUM(h.pieces) AS pieces, MAX(h.price) AS price, MAX(h.price_date) AS price_date, "
            "SUM(h.value) AS value, SUM(h.pieces * h.acquisition_price) AS cost, "
            "SUM(CASE WHEN h.acquisition_price IS NULL THEN 1 ELSE 0 END) AS no_cost "
            "FROM holdings h JOIN accounts a ON a.id = h.account_id "
            "WHERE a.enabled = 1 AND a.fx_ok = 1 AND h.isin = ? GROUP BY h.isin",
            (isin,),
        )
    )
    series = price_series(conn, isin)
    if not holding and not series:
        return None
    total = conn.execute(
        "SELECT COALESCE(SUM(h.value), 0) FROM holdings h JOIN accounts a ON a.id = h.account_id "
        "WHERE a.enabled = 1 AND a.fx_ok = 1"
    ).fetchone()[0]
    rf = float(settings.get(conn, "risk_free_rate") or 0)
    rk = risk(series, rf)
    flows, estimated = purchases(conn, isin) if holding else ([], False)
    inv = investing(flows, series, today) if holding else None
    meta = db.one(
        conn.execute("SELECT fetched_at, first_date, last_date, points, error FROM market_meta WHERE isin = ?", (isin,))
    )
    since = conn.execute("SELECT MIN(date) FROM holding_history WHERE isin = ?", (isin,)).fetchone()[0]

    position = None
    if holding:
        cost = round(holding["cost"], 2) if holding["cost"] and not holding["no_cost"] else None
        if cost is None and inv:
            cost = inv["total"]
        value = round(holding["value"], 2)
        position = {
            "pieces": holding["pieces"],
            "price": holding["price"],
            "price_date": holding["price_date"],
            "value": value,
            "cost": cost,
            "cost_source": "ing" if holding["cost"] and not holding["no_cost"] else ("payments" if cost else None),
            "avg_price": cost / holding["pieces"] if cost and holding["pieces"] else None,
            "gain": round(value - cost, 2) if cost else None,
            "share": value / total if total else 0,
            "since": min(x for x in (since, inv["first"] if inv else None) if x) if since or inv else None,
        }
        if inv:
            xf = [(dt.date.fromisoformat(f["date"]), -f["amount"]) for f in flows if f["amount"] > 0]
            xf.append((today, value))
            inv["xirr"] = portfolio.xirr(sorted(xf)) if len(xf) >= 2 and xf[0][0] < today else None
            # What the fund made over the same time, as if everything had gone in on the first day.
            # The gap to xirr is down to when the payments came.
            inv["fund_pa"] = per_year(series, inv["first"])
            inv["estimated"] = estimated

    facts = market.facts(conn, isin)
    pay = payout(conn, isin, (holding or {}).get("name"), position["value"] if position else None, today)
    if position and facts and facts.get("ter") is not None:
        position["cost_pa"] = round(position["value"] * facts["ter"], 2)
    return {
        "isin": isin,
        "name": (holding or {}).get("name") or isin,
        "facts": facts,
        "payout": pay,
        "position": position,
        "prices": downsample(series),
        "last_price": series[-1][1] if series else None,
        "last_date": series[-1][0] if series else None,
        "first_date": series[0][0] if series else None,
        "daily": _is_daily(series),
        "source": {"online": bool(meta and meta["points"]), **(meta or {})},
        "online_enabled": bool(settings.get(conn, "online_prices")),
        "periods": periods(series),
        "risk": rk,
        "years": calendar_years(series),
        "investing": inv,
        "forecast": forecast_inputs(rk),
    }


def holding_extras(conn, holdings: list[dict], today: dt.date | None = None) -> dict[str, dict]:
    """Per-ETF numbers for the holdings table: 1-year and year-to-date change, a small trend line,
    and whether it pays out."""
    today = today or dt.date.today()
    out = {}
    for h in holdings:
        isin = h["isin"]
        pay = payout(conn, isin, h.get("name"), h.get("value"), today)
        pay_short = {"policy": pay["policy"], "frequency": pay["frequency"]}
        series = price_series(conn, isin)
        if len(series) < 2:
            out[isin] = {"r1y": None, "ytd": None, "spark": [], "vol": None, "payout": pay_short}
            continue
        by_key = {p["key"]: p["r"] for p in periods(series)}
        year_ago = (dt.date.fromisoformat(series[-1][0]) - dt.timedelta(days=365)).isoformat()
        last_year = [p for d, p in series if d >= year_ago]
        step = max(1, len(last_year) // 48)
        spark = last_year[::step]
        if spark[-1] != last_year[-1]:
            spark.append(last_year[-1])
        rk = risk(series, 0)
        out[isin] = {
            "r1y": by_key.get("1y"),
            "ytd": by_key.get("ytd"),
            "spark": [round(p, 4) for p in spark] if len(spark) > 2 else [],
            "vol": rk["volatility"] if rk else None,
            "payout": pay_short,
        }
    return out


def portfolio_forecast(conn, holdings: list[dict]) -> dict:
    """Value-weighted forecast inputs over all ETFs, for the depot-wide projection."""
    total = sum(h["value"] for h in holdings)
    if not total:
        return forecast_inputs(None)
    rf = float(settings.get(conn, "risk_free_rate") or 0)
    ret = vol = years = hist = weight = 0.0
    known = False
    for h in holdings:
        w = h["value"] / total
        fi = forecast_inputs(risk(price_series(conn, h["isin"]), rf))
        ret += w * fi["ret"]
        # Adding the swings of the parts overstates the whole a little; fine for a forecast range.
        vol += w * fi["vol"]
        years += w * fi["years"]
        # An ETF without its own history counts with the long-run figure.
        hist += w * (fi["hist"] if fi["hist"] is not None else PRIOR_RETURN)
        weight += w * fi["weight"]
        known = known or fi["vol_known"]
    return {
        "ret": round(ret, 4),
        "vol": round(vol, 4),
        "years": years,
        "hist": hist if weight else None,
        "weight": weight,
        "vol_known": known,
        "prior": PRIOR_RETURN,
    }
