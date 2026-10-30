"""Counting salary toward the month it pays for.

Many employers pay at the end of the month (around the 25th to the 30th), so the
money for October arrives in September. Sorted by booking date, every month
then shows last month's salary, and the current month looks empty until payday.

Groschen finds regular income from the same payer and moves a payment to the
next month when it arrives late in the month. Payers that normally pay at the
start of the month only move when a payment comes a few days early (before a
weekend or holiday). Everything can be changed per payer in Settings.
"""

import calendar
import datetime as dt
import statistics

from .. import db, settings
from ..categorize.engine import merchant_key
from ..categorize.names import display_name
from . import common

MIN_AMOUNT = 300.0  # smaller regular income (interest, refunds) stays in its booking month
LATE_PAYER_DAY = 20  # a payer whose usual day is on or after this pays for the next month
LATE_CUTOFF_DAY = 15  # ...and every payment of theirs from this day on moves
EARLY_PAYER_DAY = 5  # a payer who usually pays by this day...
EARLY_WINDOW = 5  # ...has a payment moved when it comes this many days before month end
MODES = ("auto", "next", "same")
LATE_GRACE = 5  # days a missing salary is still expected before Groschen looks at next month


def _days_in_month(date: dt.date) -> int:
    return calendar.monthrange(date.year, date.month)[1]


def _next_month_start(date: dt.date) -> dt.date:
    return (date.replace(day=28) + dt.timedelta(days=4)).replace(day=1)


def _income_rows(conn) -> list[dict]:
    cats = common.categories(conn)
    rows = db.rows(
        conn.execute(
            "SELECT t.id, t.date, t.amount, t.counterparty, t.purpose, t.category_id, t.cat_source FROM transactions t "
            "JOIN accounts a ON a.id = t.account_id WHERE t.amount > 0 AND a.enabled = 1 ORDER BY t.date"
        )
    )
    out = []
    for t in rows:
        flow, cat = common.classify_flow(t, cats)
        if flow == "income":
            t["category"] = cat["name"]
            out.append(t)
    return out


def _payers(rows: list[dict]) -> list[dict]:
    """Payers that look like a salary or pension: regular, monthly and large enough."""
    by_key: dict[str, list[dict]] = {}
    for t in rows:
        key = merchant_key(t)
        if key:
            by_key.setdefault(key, []).append(t)
    found = []
    for key, items in by_key.items():
        typical = statistics.median(t["amount"] for t in items)
        if typical < MIN_AMOUNT:
            continue
        dates = [dt.date.fromisoformat(t["date"]) for t in items]
        salary_cat = sum(1 for t in items if t["category"] == "Salary") * 2 >= len(items)
        months = {d.strftime("%Y-%m") for d in dates}
        if not salary_cat:
            gaps = [(b - a).days for a, b in zip(dates, dates[1:]) if (b - a).days > 3]
            if len(months) < 2 or not gaps or not 25 <= statistics.median(gaps) <= 36:
                continue
        day = round(statistics.median(d.day for d in dates))
        found.append(
            {
                "key": key,
                "name": (display_name(items[-1]) if items[-1].get("counterparty") else key.title())[:48],
                "usual_day": day,
                "amount": round(typical, 2),
                "count": len(items),
                "last_date": items[-1]["date"],
                # What "auto" does for this payer: count for the next month, only move early payments, or leave it.
                "auto": "next" if day >= LATE_PAYER_DAY else "early" if day <= EARLY_PAYER_DAY else "same",
                "items": items,
            }
        )
    found.sort(key=lambda p: -p["amount"])
    return found


def _shift(date: dt.date, usual_day: int, mode: str) -> bool:
    if mode == "same":
        return False
    if mode == "next" or usual_day >= LATE_PAYER_DAY:
        return date.day >= LATE_CUTOFF_DAY
    if usual_day <= EARLY_PAYER_DAY:
        return date.day > _days_in_month(date) - EARLY_WINDOW
    return False


def overrides(conn) -> dict:
    value = settings.get(conn, "payday_overrides")
    return value if isinstance(value, dict) else {}


def sources(conn) -> dict:
    """What Settings shows: the payers found and what happens to their payments."""
    enabled = bool(settings.get(conn, "payday_shift"))
    chosen = overrides(conn)
    out = []
    for p in _payers(_income_rows(conn)):
        mode = chosen.get(p["key"], "auto")
        moved = sum(1 for t in p["items"] if _shift(dt.date.fromisoformat(t["date"]), p["usual_day"], mode))
        out.append({k: v for k, v in p.items() if k != "items"} | {"mode": mode, "moved": moved if enabled else 0})
    return {"enabled": enabled, "sources": out}


def shifted(conn) -> dict[int, str]:
    """Transaction id -> the date (first of the next month) it counts for, for moved payments only."""
    if not settings.get(conn, "payday_shift"):
        return {}
    chosen = overrides(conn)
    out = {}
    for p in _payers(_income_rows(conn)):
        mode = chosen.get(p["key"], "auto")
        for t in p["items"]:
            d = dt.date.fromisoformat(t["date"])
            if _shift(d, p["usual_day"], mode):
                out[t["id"]] = _next_month_start(d).isoformat()
    return out


def set_mode(conn, key: str, mode: str) -> None:
    if mode not in MODES:
        raise ValueError(f"mode must be one of {', '.join(MODES)}")
    chosen = overrides(conn)
    if mode == "auto":
        chosen.pop(key, None)
    else:
        chosen[key] = mode
    settings.put(conn, "payday_overrides", chosen)


def workday_before(d: dt.date) -> dt.date:
    """Salary due on a weekend usually arrives the Friday before."""
    while d.weekday() >= 5:
        d -= dt.timedelta(days=1)
    return d


def next_payday(conn, today: dt.date | None = None) -> dict | None:
    """When the main salary (the largest regular income) should arrive next, or None if there is none."""
    today = today or dt.date.today()
    payers = _payers(_income_rows(conn))
    if not payers:
        return None
    p = payers[0]
    last = dt.date.fromisoformat(p["last_date"])
    month = last.replace(day=1)
    while True:
        date = workday_before(month.replace(day=min(p["usual_day"], _days_in_month(month))))
        # At least two weeks after the last payment, so an early or late salary isn't expected twice.
        # A salary a few days overdue is still expected, not skipped to next month.
        if (date - last).days >= 15 and date >= today - dt.timedelta(days=LATE_GRACE):
            break
        month = _next_month_start(month)
    return {
        "date": date.isoformat(),
        "late": date < today,
        "usual_day": p["usual_day"],
        "name": p["name"],
        "amount": round(p["items"][-1]["amount"], 2),  # the latest salary, raises included
        "last": p["last_date"],
        "key": p["key"],
    }
