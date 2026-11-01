"""Finding subscriptions, contracts and other recurring payments, and following them over time.

Payments are grouped by merchant (for PayPal by the shop behind it, so the changing PayPal
reference numbers don't matter). A merchant counts as recurring when it is charged in a steady
rhythm (every week, two or four weeks, month, two months, quarter, half year or year) with a
steady amount. Bills whose amount moves (electricity, phone) count as well when they sit in a
contract category.

Groschen then follows every one of them by itself: a new price, a payment that stopped coming
(cancelled), one that came back after a pause, and new ones. Only what it can't judge alone
becomes a question (a payment seen just twice, or amounts that move around outside the usual
bills). That answer is remembered per merchant, so it is never asked again.
"""

import calendar
import datetime as dt
import math
import statistics

from .. import db
from ..categorize.engine import merchant_key
from .drilldown import display_name

# (label, shortest gap, longest gap, typical gap in days)
INTERVALS = [
    ("weekly", 6, 8, 7),
    ("biweekly", 13, 16, 14),
    ("monthly", 25, 36, 30),
    ("bimonthly", 55, 66, 61),
    ("quarterly", 83, 99, 91),
    ("half-yearly", 170, 195, 182),
    ("yearly", 345, 385, 365),
]
# Every four weeks looks monthly at first; it is told apart by its exact 28-day gaps.
FOUR_WEEKLY = ("4-weekly", 27, 29, 28)
PER_YEAR = {
    "weekly": 52,
    "biweekly": 26,
    "4-weekly": 13,
    "monthly": 12,
    "bimonthly": 6,
    "quarterly": 4,
    "half-yearly": 2,
    "yearly": 1,
}
STEP_MONTHS = {"monthly": 1, "bimonthly": 2, "quarterly": 3, "half-yearly": 6, "yearly": 12}
STEP_DAYS = {"weekly": 7, "biweekly": 14, "4-weekly": 28}
# Charges Groschen wants to see before it lists a payment by itself.
MIN_COUNT = {
    "weekly": 4,
    "biweekly": 3,
    "4-weekly": 4,
    "monthly": 3,
    "bimonthly": 3,
    "quarterly": 2,
    "half-yearly": 2,
    "yearly": 2,
}
LOOKBACK_DAYS = 800  # two years and a bit: enough to see a yearly payment twice and a pause before it
# Everyday spending that repeats without being a contract.
EVERYDAY = ("Groceries", "Fuel", "Cash withdrawal", "Restaurants & cafés")
# A monthly payment seen only twice counts by itself in these categories; elsewhere it is a question.
SUBSCRIPTION_CATS = {
    "Streaming",
    "Software & cloud",
    "Fitness",
    "Subscriptions",
    "Internet & phone",
    "Insurance",
    "Broadcast fee",
    "Energy",
    "Rent",
}
# Bills whose amount changes from one charge to the next (electricity, phone) count by themselves here.
CONTRACT_CATS = {"Energy", "Internet & phone", "Insurance", "Broadcast fee", "Rent", "Housing", "Subscriptions"}
# Shops where the same purchase a year apart is a coincidence, not a contract (Christmas shopping).
ONE_OFF_GROUPS = {"Shopping", "Leisure & Travel", "Food & Dining"}
ENDED_SHOWN_DAYS = 400  # a payment that stopped stays under "Ended" this long
EVENT_DAYS = 365  # changes stay in the list of changes this long
LATE_DAYS = 4  # a charge this many days late (weekend, holiday) is still the expected one


def grace(step: float) -> int:
    """How late a charge may come before Groschen takes the payment as stopped."""
    return int(min(45, max(10, round(step * 0.6))))


def add_months(d: dt.date, months: int, day: int) -> dt.date:
    y, m = divmod(d.month - 1 + months, 12)
    year, month = d.year + y, m + 1
    return dt.date(year, month, min(day, calendar.monthrange(year, month)[1]))


def next_charge(last: dt.date, interval: str, day: int) -> dt.date:
    """The charge after ``last``: on the usual day of the month, or a fixed number of days later."""
    if interval in STEP_DAYS:
        return last + dt.timedelta(days=STEP_DAYS[interval])
    return add_months(last, STEP_MONTHS.get(interval, 1), day)


def _name(tx: dict) -> str:
    return display_name(tx)[:48]


def marks(conn) -> dict[str, str]:
    """The user's answers per merchant: 'yes' (a subscription) or 'no' (not one)."""
    return {r["key"]: r["state"] for r in conn.execute("SELECT key, state FROM subscription_marks")}


def set_mark(conn, key: str, state: str | None) -> None:
    if state in ("yes", "no"):
        conn.execute(
            "INSERT INTO subscription_marks (key, state, updated_at) VALUES (?, ?, ?) "
            "ON CONFLICT(key) DO UPDATE SET state = excluded.state, updated_at = excluded.updated_at",
            (key, state, db.now_iso()),
        )
    else:
        conn.execute("DELETE FROM subscription_marks WHERE key = ?", (key,))


def _charges(conn, today: dt.date) -> dict[str, list[dict]]:
    since = (today - dt.timedelta(days=LOOKBACK_DAYS)).isoformat()
    txs = db.rows(
        conn.execute(
            "SELECT t.id, t.date, t.amount, t.orig_amount, t.counterparty, t.purpose, t.category_id, t.cat_source, "
            "c.name AS category, c.kind, c.grp "
            "FROM transactions t LEFT JOIN categories c ON c.id = t.category_id "
            "WHERE t.amount < 0 AND t.date >= ? AND t.date <= ? ORDER BY t.date, t.id",
            (since, today.isoformat()),
        )
    )
    by_key: dict[str, list[dict]] = {}
    for t in txs:
        key = merchant_key(t)
        if key:
            by_key.setdefault(key, []).append(t)
    return by_key


def _excluded(items: list[dict]) -> bool:
    """Everyday spending and money moved to the user's own accounts are never subscriptions."""
    last = items[-1]
    if last["category"] in EVERYDAY:
        return True
    # A model guess of "transfer" for a shop is not trusted enough to hide it.
    return last["kind"] == "transfer" and last["cat_source"] != "model"


def _without_extras(items: list[dict]) -> list[dict]:
    """The regular charges of a monthly (or longer) payment, without extra ones in between.

    An upgrade charged a few days after the monthly fee, or credits bought on top, would
    otherwise break the rhythm. They still show up as an unusual amount (alerts.py).
    """
    dates = [dt.date.fromisoformat(i["date"]) for i in items]
    gaps = [(b - a).days for a, b in zip(dates, dates[1:]) if (b - a).days > 3]
    if len(items) < 3 or not gaps or statistics.median(gaps) < 25:
        return items
    least = statistics.median(gaps) * 0.4
    kept, last = [items[0]], dates[0]
    for item, d in zip(items[1:], dates[1:]):
        if (d - last).days >= least:
            kept.append(item)
            last = d
    return kept


def _match(gaps: list[int]) -> tuple | None:
    """The rhythm behind the gaps between charges, or None when there is no steady one."""
    if not gaps:
        return None
    if len(gaps) >= 4 and all(FOUR_WEEKLY[1] <= g <= FOUR_WEEKLY[2] for g in gaps[-6:]):
        return FOUR_WEEKLY
    gap = statistics.median(gaps)
    for iv in INTERVALS:
        if not iv[1] <= gap <= iv[2]:
            continue
        # Most gaps have to fit, so a hairdresser every four to twelve weeks isn't "every two months".
        # Pauses (a stop and a restart) don't count against it.
        regular = [g for g in gaps if g <= iv[3] + grace(iv[3])]
        fit = sum(1 for g in regular if iv[1] <= g <= iv[2])
        return iv if regular and fit >= math.ceil(len(regular) * 0.7) else None
    return None


def _analyze(items: list[dict]) -> dict:
    dates = [dt.date.fromisoformat(i["date"]) for i in items]
    gaps = [(b - a).days for a, b in zip(dates, dates[1:]) if (b - a).days > 3]
    match = _match(gaps)
    amounts = [-i["amount"] for i in items]
    # Judge the amount by recent charges, so a price change long ago doesn't count as unsteady.
    recent = amounts[-8:]
    typical = statistics.median(amounts[-6:])
    tolerance = max(1.5, typical * 0.25)
    steady = sum(1 for a in recent if abs(a - typical) <= tolerance)
    # One odd charge (a first month at a trial price, a refund) is allowed.
    stable = steady >= max(2, math.ceil(len(recent) * 0.6))
    step = match[3] if match else (statistics.median(gaps) if gaps else 30)
    # Runs of charges: a gap longer than a late charge means it stopped and started again.
    limit = step + grace(step)
    starts = [0] + [i for i in range(1, len(dates)) if (dates[i] - dates[i - 1]).days > limit]
    return {"dates": dates, "match": match, "amounts": amounts, "stable": stable, "step": step, "starts": starts}


def _changes(items: list[dict], amounts: list[float]) -> list[dict]:
    """Price changes, oldest first: the amount moved to a new level and stayed there.

    A level of a single charge is skipped as the old price: a trial month at the start, or
    one back payment in between. A new price seen once (the latest charge) counts already.
    """
    levels: list[dict] = []
    for item, a in zip(items, amounts):
        # A charge in another currency is judged by what the merchant asked, not by the exchange rate of the day.
        native = -item["orig_amount"] if item.get("orig_amount") is not None else a
        if levels and abs(native - levels[-1]["native"]) < max(0.5, levels[-1]["native"] * 0.01):
            levels[-1]["count"] += 1
            levels[-1]["amount"] = a
            levels[-1]["native"] = native
            continue
        levels.append({"amount": a, "native": native, "date": item["date"], "count": 1})
    out, prev = [], None
    for i, lv in enumerate(levels):
        settled = lv["count"] >= 2 or i == len(levels) - 1
        if not settled:
            continue
        if prev is not None and abs(lv["native"] - prev["native"]) >= 0.5:
            out.append({"date": lv["date"], "from": round(prev["amount"], 2), "to": round(lv["amount"], 2)})
        prev = lv
    return out


def _usual_day(dates: list[dt.date]) -> int:
    return round(statistics.median(d.day for d in dates[-4:]))


def _entry(key: str, items: list[dict], a: dict, today: dt.date, confirmed: bool, first_seen: dt.date | None) -> dict:
    dates, amounts, match = a["dates"], a["amounts"], a["match"]
    if match:
        label, step = match[0], match[3]
    else:
        # A payment the user confirmed but whose rhythm isn't clear yet: assume monthly.
        label, step = "monthly", 30
    last = items[-1]
    last_date = dates[-1]
    last_amount = amounts[-1]
    changes = _changes(items, amounts) if a["stable"] else []  # varying bills: a new amount isn't a price change
    recent_change = next((c for c in reversed(changes) if (today - dt.date.fromisoformat(c["date"])).days <= 365), None)
    monthly = statistics.median(amounts[-3:]) if not a["stable"] else last_amount
    day = _usual_day(dates)
    expected = next_charge(last_date, label, day)
    nxt = expected
    while nxt < today - dt.timedelta(days=LATE_DAYS):
        nxt = next_charge(nxt, label, day)

    starts = a["starts"]
    run = starts[-1]
    window = step * (2 if step < 80 else 1) + 60  # how long "new" and "back again" stay on a payment
    stopped = (today - last_date).days > step + grace(step)
    count_needed = MIN_COUNT.get(label, 3)
    detected = dates[min(len(dates), count_needed) - 1]
    # New: nothing from this merchant in the time before, although the data reaches back far enough.
    is_new = (
        match is not None
        and len(starts) == 1
        and first_seen is not None
        and (dates[0] - first_seen).days > step + grace(step)
        and (today - dates[0]).days <= window
    )
    if stopped:
        status = "ended"
    elif len(starts) > 1 and (today - dates[run]).days <= window:
        status = "resumed"
    elif is_new:
        status = "new"
    else:
        status = "active"

    # The history of stops and restarts, for the list of changes.
    runs = []
    for i, s in enumerate(starts):
        end = (starts[i + 1] if i + 1 < len(starts) else len(dates)) - 1
        runs.append({"from": dates[s].isoformat(), "to": dates[end].isoformat()})
    return {
        "key": key,
        "name": _name(last),
        # The payee page's name for it, so a click on the orbit or list opens the right page.
        "merchant": display_name(last),
        "category": last["category"],
        "group": last["grp"],
        "amount": round(last_amount, 2),
        "previous_amount": round(recent_change["from"], 2) if recent_change else round(last_amount, 2),
        "price_change": round(recent_change["to"] - recent_change["from"], 2) if recent_change else 0.0,
        "price_change_date": recent_change["date"] if recent_change else None,
        "changes": changes,
        "interval": label,
        "rhythm_known": match is not None,
        "monthly_cost": round(monthly * PER_YEAR[label] / 12, 2),
        "yearly_cost": round(monthly * PER_YEAR[label], 2),
        "count": len(items),
        "first_date": items[0]["date"],
        "since": dates[run].isoformat(),
        "last_date": last["date"],
        "next_date": nxt.isoformat(),
        "day": day,
        "varies": not a["stable"],
        "confirmed": confirmed,
        "status": status,
        "new_since": detected.isoformat() if is_new else None,
        "ended_on": (last_date + dt.timedelta(days=round(step) + grace(step))).isoformat() if stopped else None,
        "pause_days": (dates[run] - dates[run - 1]).days if len(starts) > 1 else None,
        "runs": runs,
        "history": [{"date": i["date"], "amount": round(-i["amount"], 2)} for i in items[-24:]],
        "_step": step,
    }


def _events(entries: list[dict], today: dt.date) -> list[dict]:
    """What changed with the recurring payments in the last year, newest first."""
    out = []
    oldest = today - dt.timedelta(days=EVENT_DAYS)

    def add(kind: str, date: str, key: str, e: dict, **extra) -> None:
        day = dt.date.fromisoformat(date)
        if oldest <= day <= today:
            out.append(
                {
                    "key": key,
                    "kind": kind,
                    "date": date,
                    "sub": e["key"],
                    "name": e["name"],
                    "merchant": e["merchant"],
                    "interval": e["interval"],
                    "amount": e["amount"],
                    "monthly_cost": e["monthly_cost"],
                }
                | extra
            )

    for e in entries:
        per_year = PER_YEAR[e["interval"]]
        for c in e["changes"]:
            kind = "price_up" if c["to"] > c["from"] else "price_down"
            # Same key as the price hints have always had, so a hint closed before stays closed.
            add(
                kind,
                c["date"],
                f"price:{e['key']}:{c['date']}",
                e,
                **{"from": c["from"], "to": c["to"]},
                per_year=round((c["to"] - c["from"]) * per_year, 2),
            )
        step = e["_step"]
        runs = e["runs"]
        if e["rhythm_known"]:
            for before, after in zip(runs, runs[1:]):
                stop = dt.date.fromisoformat(before["to"]) + dt.timedelta(days=round(step) + grace(step))
                gap = (dt.date.fromisoformat(after["from"]) - dt.date.fromisoformat(before["to"])).days
                if stop < dt.date.fromisoformat(after["from"]):
                    add("ended", stop.isoformat(), f"sub:ended:{e['key']}:{before['to']}", e, last_date=before["to"])
                add(
                    "resumed",
                    after["from"],
                    f"sub:back:{e['key']}:{after['from']}",
                    e,
                    pause_days=gap,
                    last_date=before["to"],
                )
            if e["status"] == "ended":
                add("ended", e["ended_on"], f"sub:ended:{e['key']}:{e['last_date']}", e, last_date=e["last_date"])
        if e["new_since"]:
            add("new", e["new_since"], f"sub:new:{e['key']}", e, since=e["first_date"])
    out.sort(key=lambda x: (x["date"], x["key"]), reverse=True)
    return out


def _clean(e: dict) -> dict:
    return {k: v for k, v in e.items() if not k.startswith("_")}


def overview(conn, today: dt.date | None = None) -> dict:
    """Recurring payments, the ones that stopped, what changed, questions, and what the user ruled out."""
    today = today or dt.date.today()
    answers = marks(conn)
    first = conn.execute("SELECT MIN(date) FROM transactions").fetchone()[0]
    first_seen = dt.date.fromisoformat(first[:10]) if first else None
    found, suggestions, hidden, ended = [], [], [], []
    for key, items in _charges(conn, today).items():
        state = answers.get(key)
        items = _without_extras(items)
        a = _analyze(items)
        if state == "no":
            hidden.append(
                {"key": key, "name": _name(items[-1]), "amount": round(a["amounts"][-1], 2), "last_date": items[-1]["date"]}
            )
            continue
        if state == "yes":
            e = _entry(key, items, a, today, True, first_seen)
        else:
            if _excluded(items) or not a["match"]:
                continue
            label = a["match"][0]
            category = items[-1]["category"]
            count = len(items)
            if count < 3 and label in ("quarterly", "half-yearly", "yearly") and items[-1]["grp"] in ONE_OFF_GROUPS:
                continue
            e = _entry(key, items, a, today, False, first_seen)
            if a["stable"] and count >= MIN_COUNT[label]:
                e["auto"] = "rhythm"
            elif a["stable"] and label == "monthly" and count == 2:
                if category in SUBSCRIPTION_CATS:
                    e["auto"] = "category"  # a streaming service charged twice is a subscription
                else:
                    e["reason"] = "twice"
            elif not a["stable"] and label in STEP_MONTHS and count >= MIN_COUNT[label]:
                if category in CONTRACT_CATS or items[-1]["grp"] in CONTRACT_CATS:
                    e["auto"] = "contract"  # electricity or phone bills move a little every month
                else:
                    e["reason"] = "varies"
            else:
                continue
            if "reason" in e:
                if e["status"] != "ended":
                    suggestions.append(e)
                continue
        if e["status"] == "ended":
            if (today - dt.date.fromisoformat(e["last_date"])).days <= ENDED_SHOWN_DAYS:
                ended.append(e)
        else:
            found.append(e)
    events = _events(found + ended, today)
    found.sort(key=lambda r: r["monthly_cost"], reverse=True)
    suggestions.sort(key=lambda r: r["monthly_cost"], reverse=True)
    ended.sort(key=lambda r: r["last_date"], reverse=True)
    hidden.sort(key=lambda r: r["name"].lower())
    return {
        "items": [_clean(e) for e in found],
        "suggestions": [_clean(e) for e in suggestions],
        "hidden": hidden,
        "ended": [_clean(e) for e in ended],
        "events": events,
    }


def detect(conn, today: dt.date | None = None) -> list[dict]:
    return overview(conn, today)["items"]
