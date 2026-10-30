"""What is still to come: fixed costs, standing orders and the next salary.

Two things are built on this:

- "Available until payday": the Girokonto balance minus every fixed cost and
  standing order still expected before the next salary, and what that leaves
  per day.
- The fixed-costs calendar: per day of a month, which fixed costs were paid and
  which are still expected.

Fixed costs are the recurring payments from the Subscriptions page. On top of
those come regular transfers out of the Girokonto, such as the savings transfer
to the Extra-Konto or an ETF savings plan: they are not spending, but the money
is gone from the Girokonto all the same.
"""

import calendar
import datetime as dt
import re
import statistics

from .. import db, settings
from ..categorize.engine import merchant_key
from ..categorize.names import display_name
from . import paydays, recurring

OVERDUE_DAYS = 4  # a charge this many days late (weekend, holiday) is still expected
MAX_SPAN_DAYS = 62  # the payday bar covers at most this many days
LOOKAHEAD_MONTHS = 12


def _nominal(last: dt.date, day: int) -> dt.date:
    """The usual date a charge was meant for: a charge on the 2nd for the 30th belongs to the month before."""
    options = [recurring.add_months(last, n, day) for n in (-1, 0, 1)]
    return min(options, key=lambda d: abs((d - last).days))


def _occurrences(last: dt.date, interval: str, day: int, start: dt.date, end: dt.date) -> list[dt.date]:
    """The charges after ``last`` from ``start`` to ``end`` (both included)."""
    out = []
    d = last if interval in recurring.STEP_DAYS else _nominal(last, day)
    while True:
        d = recurring.next_charge(d, interval, day)
        if d > end:
            return out
        if d >= start and d > last:
            out.append(d)


def _transfer_key(tx: dict) -> str:
    # One payee can have several orders (two ETF savings plans at ING), so the text counts too.
    words = re.sub(r"[\d\W_]+", " ", (tx.get("purpose") or "").lower()).split()
    return f"{merchant_key(tx)}|{' '.join(words[:4])}"


def standing_transfers(conn, today: dt.date) -> list[dict]:
    """Monthly transfers out of the Girokonto to own accounts or the depot (savings, savings plans)."""
    since = (today - dt.timedelta(days=200)).isoformat()
    txs = db.rows(
        conn.execute(
            "SELECT t.id, t.date, t.amount, t.counterparty, t.purpose, c.name AS category FROM transactions t "
            "JOIN accounts a ON a.id = t.account_id JOIN categories c ON c.id = t.category_id "
            "WHERE a.kind = 'checking' AND a.enabled = 1 AND t.amount < 0 AND c.kind = 'transfer' "
            "AND t.date >= ? AND t.date <= ? ORDER BY t.date, t.id",
            (since, today.isoformat()),
        )
    )
    by_key: dict[str, list[dict]] = {}
    for t in txs:
        by_key.setdefault(_transfer_key(t), []).append(t)
    out = []
    for key, items in by_key.items():
        months = {i["date"][:7] for i in items}
        if len(items) < 3 or len(months) < 3 or len(items) > len(months) + 1:
            continue
        dates = [dt.date.fromisoformat(i["date"]) for i in items]
        gaps = [(b - a).days for a, b in zip(dates, dates[1:])]
        if not 25 <= statistics.median(gaps) <= 36:
            continue
        amounts = [-i["amount"] for i in items]
        typical = statistics.median(amounts[-4:])
        if abs(amounts[-1] - typical) > max(1.0, typical * 0.1):
            continue  # changing amounts are manual transfers, not a standing order
        if (today - dates[-1]).days > 45:
            continue  # stopped
        last = items[-1]
        out.append(
            {
                "key": key,
                "name": (last.get("purpose") or last.get("counterparty") or "Transfer")[:48],
                "payee": display_name(last)[:48] if last.get("counterparty") else "",
                "category": last["category"],
                "amount": round(amounts[-1], 2),
                "interval": "monthly",
                "day": round(statistics.median(d.day for d in dates[-4:])),
                "last_date": last["date"],
                "kind": "transfer",
            }
        )
    return out


def _usual(conn, today: dt.date) -> dict[str, tuple[int, float]]:
    """The usual day of the month and amount each merchant charges, from its last few charges.

    The last booking alone can be off by a weekend, and one large back payment
    (a yearly electricity bill) shouldn't be expected again next month.
    """
    since = (today - dt.timedelta(days=200)).isoformat()
    seen: dict[str, list[tuple[int, float]]] = {}
    for t in db.rows(
        conn.execute(
            "SELECT date, amount, counterparty, purpose FROM transactions WHERE amount < 0 AND date >= ? ORDER BY date",
            (since,),
        )
    ):
        seen.setdefault(merchant_key(t), []).append((int(t["date"][8:10]), -t["amount"]))
    return {
        k: (round(statistics.median(d for d, _ in v[-4:])), statistics.median(a for _, a in v[-3:])) for k, v in seen.items()
    }


def fixed_items(conn, today: dt.date) -> list[dict]:
    """Every regular outgoing payment: subscriptions and contracts, then standing transfers."""
    items = []
    usual = _usual(conn, today)
    for r in recurring.detect(conn, today):
        items.append(
            {
                "key": r["key"],
                "name": r["name"],
                "payee": r["name"],
                "category": r["category"],
                "amount": round(usual[r["key"]][1], 2) if r["key"] in usual else r["amount"],
                "interval": r["interval"],
                "day": r["day"],
                "last_date": r["last_date"],
                "kind": "fixed",
            }
        )
    return items + standing_transfers(conn, today)


def expected(items: list[dict], start: dt.date, end: dt.date) -> list[dict]:
    """The charges each item should make between ``start`` and ``end``."""
    out = []
    for it in items:
        last = dt.date.fromisoformat(it["last_date"])
        for d in _occurrences(last, it["interval"], it["day"], start, end):
            out.append(it | {"date": d.isoformat()})
    out.sort(key=lambda e: (e["date"], -e["amount"]))
    return out


def _checking(conn) -> list[dict]:
    return db.rows(
        conn.execute(
            "SELECT id, name, balance, balance_date FROM accounts WHERE kind = 'checking' AND enabled = 1 ORDER BY id"
        )
    )


def available(conn, today: dt.date | None = None) -> dict:
    """The Girokonto balance minus what is still going out before the next salary."""
    today = today or dt.date.today()
    accounts = _checking(conn)
    if not accounts:
        return {"has_account": False}
    balance = round(sum(a["balance"] for a in accounts), 2)
    dates = [a["balance_date"] for a in accounts if a["balance_date"]]
    balance_date = dt.date.fromisoformat(min(dates)[:10]) if dates else today
    payday = paydays.next_payday(conn, today)
    if payday:
        until = max(dt.date.fromisoformat(payday["date"]), today)
        since = dt.date.fromisoformat(payday["last"])
    else:
        # No regular salary found: plan to the end of the month.
        until = today.replace(day=calendar.monthrange(today.year, today.month)[1]) + dt.timedelta(days=1)
        since = today.replace(day=1)
    # Where this salary month began, for the bar that shows how much of it has passed. A salary
    # missing for months would make the bar too long to read, so it covers two months at most.
    since = min(max(since, until - dt.timedelta(days=MAX_SPAN_DAYS)), today)
    # Charges after the balance was read are still to come, also those a few days late.
    start = min(balance_date, today) - dt.timedelta(days=OVERDUE_DAYS)
    upcoming = [e for e in expected(fixed_items(conn, today), start, until - dt.timedelta(days=1))]
    fixed_total = round(sum(e["amount"] for e in upcoming), 2)
    buffer = float(settings.get(conn, "safe_buffer") or 0)
    free = round(balance - fixed_total - buffer, 2)
    days = max(1, (until - today).days)
    return {
        "has_account": True,
        "balance": balance,
        "balance_date": balance_date.isoformat(),
        "balance_age_days": (today - balance_date).days,
        "payday": payday,
        "since": since.isoformat(),
        "until": until.isoformat(),
        "days": days,
        "upcoming": [
            {k: e[k] for k in ("date", "name", "payee", "amount", "kind", "category", "interval")} for e in upcoming
        ],
        "fixed_total": fixed_total,
        "buffer": round(buffer, 2),
        "available": free,
        "per_day": round(free / days, 2) if free > 0 else 0.0,
    }


def month_calendar(conn, month: str, today: dt.date | None = None) -> dict:
    """Fixed costs, standing orders and salary for each day of ``month`` (YYYY-MM): paid and expected."""
    today = today or dt.date.today()
    first = dt.date.fromisoformat(f"{month}-01")
    last = first.replace(day=calendar.monthrange(first.year, first.month)[1])
    items = fixed_items(conn, today)
    by_merchant = {it["key"]: it for it in items if it["kind"] == "fixed"}
    by_transfer = {it["key"]: it for it in items if it["kind"] == "transfer"}
    payday = paydays.next_payday(conn, today)

    entries = []
    # Paid: bookings this month from the same merchants and standing orders.
    txs = db.rows(
        conn.execute(
            "SELECT t.id, t.date, t.amount, t.counterparty, t.purpose, c.kind AS cat_kind FROM transactions t "
            "JOIN accounts a ON a.id = t.account_id LEFT JOIN categories c ON c.id = t.category_id "
            "WHERE a.enabled = 1 AND t.date >= ? AND t.date <= ? ORDER BY t.date, t.id",
            (first.isoformat(), last.isoformat()),
        )
    )
    for t in txs:
        if t["amount"] < 0:
            it = by_transfer.get(_transfer_key(t)) if t["cat_kind"] == "transfer" else by_merchant.get(merchant_key(t))
            if it:
                entries.append(_entry(it, t["date"], -t["amount"], "paid", t["id"]))
        elif payday and merchant_key(t) == payday["key"]:
            entries.append(
                {
                    "date": t["date"],
                    "name": payday["name"],
                    "amount": t["amount"],
                    "kind": "income",
                    "status": "paid",
                    "interval": "monthly",
                    "category": "Salary",
                    "tx_id": t["id"],
                }
            )
    # Expected: from today (or a few days back, for late charges) to the end of the month.
    start = max(first, today - dt.timedelta(days=OVERDUE_DAYS))
    if start <= last:
        for e in expected(items, start, last):
            entries.append(_entry(e, e["date"], e["amount"], "expected", None))
        if payday and first.isoformat() <= payday["date"] <= last.isoformat():
            entries.append(
                {
                    "date": max(payday["date"], today.isoformat()),
                    "name": payday["name"],
                    "amount": payday["amount"],
                    "kind": "income",
                    "status": "expected",
                    "interval": "monthly",
                    "category": "Salary",
                    "tx_id": None,
                }
            )
        # Later salaries in the months after the next one.
        if payday and payday["date"] < first.isoformat():
            guess = paydays.workday_before(first.replace(day=min(payday["usual_day"], last.day)))
            entries.append(
                {
                    "date": guess.isoformat(),
                    "name": payday["name"],
                    "amount": payday["amount"],
                    "kind": "income",
                    "status": "expected",
                    "interval": "monthly",
                    "category": "Salary",
                    "tx_id": None,
                }
            )
    entries.sort(key=lambda e: (e["date"], e["kind"] != "income", -e["amount"]))
    out_paid = sum(e["amount"] for e in entries if e["kind"] != "income" and e["status"] == "paid")
    out_expected = sum(e["amount"] for e in entries if e["kind"] != "income" and e["status"] == "expected")
    return {
        "month": month,
        "today": today.isoformat(),
        "entries": entries,
        "paid": round(out_paid, 2),
        "expected": round(out_expected, 2),
        "total": round(out_paid + out_expected, 2),
        "income": round(sum(e["amount"] for e in entries if e["kind"] == "income"), 2),
    }


def _entry(it: dict, date: str, amount: float, status: str, tx_id: int | None) -> dict:
    return {
        "date": date,
        "name": it["name"],
        "amount": round(amount, 2),
        "kind": it["kind"],
        "status": status,
        "interval": it["interval"],
        "category": it["category"],
        "tx_id": tx_id,
    }
