"""Savings plans, found by Groschen itself.

- ETF savings plans: about the same amount into the same fund every month. ING books them as
  "Sparplan <ISIN>" on the Girokonto; a transfer to another broker counts too. One plan per fund.
- Kleingeld Plus: the round-ups ING collects from card payments and invests once a month.
- Saving by standing order: the same amount moved to the Extra-Konto (or another savings
  account) every month.

Every plan comes with its amount and day, since when it runs without a gap, what it has put
away in that time, and when the amount changed. Nothing has to be set up or confirmed: the
payments Groschen already counts as investments (Investments page) and as savings (Overview)
are all it looks at.
"""

import datetime as dt
import re
import statistics

from .. import db
from ..categorize.engine import merchant_key
from . import common, portfolio, recurring, savings
from .drilldown import display_name

# What the bank calls a fund purchase when it doesn't name the fund: the page shows "Securities savings plan".
GENERIC_NAME = re.compile(r"^(wertpapier-?kauf|wp-kauf|sparplan|kauf|wertpapiere?|fondskauf)$", re.IGNORECASE)
RECENT_MONTHS = 4  # a plan pays in at least three of these (the running month only counts once paid)
STOPPED_DAYS = 50  # no payment for this long: the plan is paused
ENDED_DAYS = 100  # about three payments missed: the plan has ended and leaves the list
SHOWN_MONTHS = 12


def _words(text: str | None) -> str:
    return " ".join(re.sub(r"[\d\W_]+", " ", (text or "").lower()).split()[:4])


def _month_add(month: str, n: int) -> str:
    y, m = map(int, month.split("-"))
    y, m = divmod(y * 12 + m - 1 + n, 12)
    return f"{y}-{m + 1:02d}"


def _plan(key: str, g: dict, today: dt.date) -> dict | None:
    """A plan from its payments, or None when they don't come every month."""
    kind = g["kind"]
    payments = sorted(g["payments"], key=lambda p: p["date"])
    if not payments:
        return None
    by_month: dict[str, float] = {}
    for p in payments:
        by_month[p["date"][:7]] = by_month.get(p["date"][:7], 0.0) + p["amount"]
    this_month = today.strftime("%Y-%m")
    day = round(statistics.median(int(p["date"][8:10]) for p in payments[-4:]))
    last_date = dt.date.fromisoformat(payments[-1]["date"])
    # The running month counts once it is paid, or once its usual day has passed without a payment.
    current_due = this_month in by_month or today.day > day + recurring.LATE_DAYS
    end = this_month if current_due else _month_add(this_month, -1)
    recent = [_month_add(end, -i) for i in range(RECENT_MONTHS)]
    paid = [m for m in recent if by_month.get(m, 0) > 0]
    quiet = (today - last_date).days
    stopped = quiet > STOPPED_DAYS
    # A plan that ran before stays known while it pauses, and comes back with its next payment.
    if len(paid) < 3 and not _ran_before(by_month, today):
        return None
    amounts = [by_month[m] for m in sorted(by_month)[-3:]]
    # Round-ups change every month, so their average says more than the middle month.
    amount = statistics.fmean(amounts) if kind == "roundup" else statistics.median(amounts)
    if kind != "roundup" and any(abs(a - amount) > max(1.0, amount * 0.15) for a in amounts[-2:]):
        return None  # changing amounts are single purchases, not a plan
    # Since when it runs without a gap, and what it has put away since then.
    month = max(by_month)
    since = month
    while by_month.get(_month_add(since, -1), 0) > 0:
        since = _month_add(since, -1)
    streak = [m for m in by_month if m >= since]
    # Changes to the amount, oldest first: a new amount the month after confirms (or the latest one).
    changes = []
    if kind != "roundup":
        months = sorted(by_month)
        level = None
        for i, m in enumerate(months):
            a = _rounded(by_month[m])
            if level is None:
                level = a
            elif abs(a - level) > max(1.0, level * 0.03):
                after = _rounded(by_month[months[i + 1]]) if i + 1 < len(months) else None
                if after is None or abs(after - a) <= max(1.0, a * 0.03):
                    changes.append({"month": m, "from": level, "to": a})
                    level = a
    nxt = None
    if not stopped:
        this = recurring.add_months(dt.date.fromisoformat(f"{this_month}-01"), 0, day)
        late = this < today - dt.timedelta(days=recurring.LATE_DAYS)
        nxt = recurring.add_months(this, 1, day) if this_month in by_month or late else this
    window = [_month_add(end, -i) for i in range(SHOWN_MONTHS - 1, -1, -1)]
    return {
        "key": key,
        "kind": kind,
        "name": g["name"],
        "isin": g["isin"],
        "invested": g["invested"],
        "amount": round(amount, 2),
        "day": day,
        "since": since,
        "streak": len(streak),
        "total": round(sum(by_month[m] for m in streak), 2),
        "total_all": round(sum(by_month.values()), 2),
        "first_date": payments[0]["date"],
        "last_date": payments[-1]["date"],
        "next_date": nxt.isoformat() if nxt else None,
        "active": not stopped,
        "state": "running" if not stopped else "ended" if quiet > ENDED_DAYS else "paused",
        "changes": changes[-6:],
        "months": [{"month": m, "amount": round(by_month.get(m, 0.0), 2)} for m in window],
    }


def _rounded(amount: float) -> float:
    """Plan amounts are round numbers; a few cents of fees or a currency rate don't make a new one."""
    return round(amount / 5) * 5 if amount >= 20 else round(amount, 2)


def _ran_before(by_month: dict[str, float], today: dt.date) -> bool:
    """A plan that stopped: at least three months in a row with a payment within the last year."""
    months = sorted(m for m in by_month if m >= _month_add(today.strftime("%Y-%m"), -12))
    run = best = 0
    prev = None
    for m in months:
        run = run + 1 if prev and _month_add(prev, 1) == m else 1
        best = max(best, run)
        prev = m
    return best >= 3


def _fund_names(conn) -> dict[str, str]:
    return {r["isin"]: r["name"] for r in conn.execute("SELECT isin, name FROM holdings WHERE name IS NOT NULL")}


def _savings_transfers(conn, today: dt.date, invest_ids: set[int]) -> dict[str, list[dict]]:
    """Monthly transfers from a current account to savings, grouped by who they go to and their text."""
    accounts = {
        a["id"]: a
        for a in db.rows(conn.execute("SELECT id, kind, name, iban FROM accounts WHERE enabled = 1 AND fx_ok = 1"))
    }
    own_savings = {savings._norm_iban(a["iban"]) for a in accounts.values() if a["kind"] == "savings" and a["iban"]}
    by_tx, by_cp = savings._overrides(conn)
    cats = common.categories(conn)
    rows = db.rows(
        conn.execute(
            "SELECT t.id, t.date, t.amount, t.account_id, t.counterparty, t.counterparty_iban, t.purpose, t.booking_text, "
            "t.category_id FROM transactions t JOIN accounts a ON a.id = t.account_id "
            "WHERE a.kind = 'checking' AND a.enabled = 1 AND a.fx_ok = 1 "
            "AND t.amount < 0 AND t.date <= ? ORDER BY t.date, t.id",
            (today.isoformat(),),
        )
    )
    out: dict[str, list[dict]] = {}
    for t in rows:
        if t["id"] in invest_ids:
            continue
        cat = cats.get(t["category_id"]) or {}
        text = savings._text(t)
        key = savings.cp_key(t)
        choice = by_tx.get(t["id"]) or by_cp.get(key)
        to_savings = (
            choice == "savings"
            or (choice is None and cat.get("name") == "Savings")
            or (choice is None and savings._norm_iban(t.get("counterparty_iban")) in own_savings)
            or (choice is None and cat.get("kind") == "transfer" and bool(savings.SAVINGS_RE.search(text)))
        )
        if to_savings:
            group = f"save:{merchant_key(t)}|{_words(t.get('purpose'))}"
            out.setdefault(group, []).append({"date": t["date"], "amount": -t["amount"], "tx": t, "accounts": accounts})
    return out


def find(conn, today: dt.date | None = None) -> dict:
    """Every savings plan, the running ones first, largest first.

    A plan that missed a payment is paused and stays in the list, since it may go on. Once about
    three payments are missing it has ended and moves to ``ended``; a new payment brings it back.
    """
    today = today or dt.date.today()
    pays = [p for p in portfolio.payments(conn) if p["counted"] and p["amount"] > 0]
    names = _fund_names(conn)
    groups: dict[str, dict] = {}
    for p in pays:
        text = f"{p['name']} {p['purpose']}".upper()
        if savings.ROUNDUP_RE.search(text):
            key, g = "roundup", {"kind": "roundup", "name": "Kleingeld Plus", "isin": None}
        elif p["isin"]:
            key, g = f"etf:{p['isin']}", {"kind": "etf", "name": names.get(p["isin"]) or p["name"], "isin": p["isin"]}
        else:
            name = "" if GENERIC_NAME.match(p["name"].strip()) else p["name"]
            key, g = f"to:{p['name'].lower()}", {"kind": "etf", "name": name, "isin": None}
        groups.setdefault(key, g | {"invested": True, "payments": []})["payments"].append(p)
    for key, items in _savings_transfers(conn, today, {p["id"] for p in pays}).items():
        t = items[-1]["tx"]
        if savings.ROUNDUP_RE.search(savings._text(t)):
            # Kleingeld Plus into the Extra-Konto instead of a fund.
            g = {"kind": "roundup", "name": "Kleingeld Plus", "isin": None, "invested": False, "payments": []}
            groups.setdefault("roundup:savings", g)["payments"].extend(items)
            continue
        acc = next(
            (
                a["name"]
                for a in items[-1]["accounts"].values()
                if a["iban"] and savings._norm_iban(a["iban"]) == savings._norm_iban(t.get("counterparty_iban"))
            ),
            None,
        )
        groups[key] = {"kind": "savings", "name": acc or display_name(t), "isin": None, "invested": False, "payments": items}
    plans = []
    for key, g in groups.items():
        plan = _plan(key, g, today)
        if plan:
            plans.append(plan)
    plans.sort(key=lambda p: (not p["active"], not p["invested"], -p["amount"]))
    running = [p for p in plans if p["active"]]
    return {
        "items": [p for p in plans if p["state"] != "ended"],
        "ended": [p for p in plans if p["state"] == "ended"],
        "running": len(running),
        "monthly": round(sum(p["amount"] for p in running), 2),
        "invested_monthly": round(sum(p["amount"] for p in running if p["invested"]), 2),
        "saved_monthly": round(sum(p["amount"] for p in running if not p["invested"]), 2),
    }
