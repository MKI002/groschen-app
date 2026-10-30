"""Hints about bookings worth a second look.

- Duplicates: the same amount charged twice by the same merchant within a few
  days (a card payment: on the same day), unless it was refunded. Not for everyday
  shopping and not for merchants the user pays all the time: two coffees for the same
  price are no mistake.
- Subscriptions and contracts: a new price (up or down), a new one, one that stopped
  (cancelled) and one that came back after a pause. Groschen finds these by itself
  (analytics/recurring.py); the hint only says so.
- Unusual amounts: a payment far above what that merchant (or, for a new
  merchant, that category) usually costs, or a large payment to a merchant
  never seen before. A merchant whose amounts always vary (online shops) only
  counts when a payment is far above anything paid there before, and PayPal or
  Klarna without the shop behind them say nothing about what is usual.

Every hint has a stable key. Dismissed keys are stored, so a hint the user
waved away never comes back.
"""

import datetime as dt
import re
import statistics

from .. import db, settings
from ..categorize.engine import merchant_key
from ..categorize.names import display_name
from . import recurring

WINDOW_DAYS = 45  # hints look at this many days back
DUPLICATE_DAYS = 3
DUPLICATE_MIN = 5.0  # two coffees for the same price are not worth a hint
REFUND_DAYS = 21
# Spending where the same amount twice in a few days is normal (the same lunch, the same ticket).
EVERYDAY = {
    *recurring.EVERYDAY,
    "Drugstore",
    "Public transport",
    "Parking",
    "Taxi & rides",
    "Food delivery",
    "Pharmacy",
}
FREQUENT = 6  # payments to the same merchant in the 60 days before: one the user goes to all the time
CARD_RE = re.compile(r"^(VISA|MASTERCARD|MAESTRO|GIROCARD|DEBITK)", re.IGNORECASE)
# Payment services standing in for many shops: their amounts have nothing in common.
INTERMEDIARY_RE = re.compile(r"\b(PAYPAL|KLARNA|SECUPAY|RATEPAY|RIVERTY|AFTERPAY|SUMUP)\b")


def dismissed(conn) -> set[str]:
    return {r["key"] for r in conn.execute("SELECT key FROM dismissed_alerts")}


def dismiss(conn, key: str) -> None:
    conn.execute("INSERT OR IGNORE INTO dismissed_alerts (key, dismissed_at) VALUES (?, ?)", (key[:200], db.now_iso()))


def restore_all(conn) -> int:
    return conn.execute("DELETE FROM dismissed_alerts").rowcount


def _load(conn, since: str, until: str) -> list[dict]:
    return db.rows(
        conn.execute(
            "SELECT t.id, t.date, t.amount, t.counterparty, t.purpose, t.account_id, t.category_id, "
            "c.name AS category, c.kind AS cat_kind, a.name AS account FROM transactions t "
            "JOIN accounts a ON a.id = t.account_id LEFT JOIN categories c ON c.id = t.category_id "
            "WHERE a.enabled = 1 AND t.date >= ? AND t.date <= ? ORDER BY t.date, t.id",
            (since, until),
        )
    )


def _name(tx: dict) -> str:
    return display_name(tx)[:48]


def duplicates(txs: list[dict], since: str) -> list[dict]:
    groups: dict[tuple, list[dict]] = {}
    refunds: dict[tuple, list[dt.date]] = {}
    paid: dict[str, list[dt.date]] = {}
    for t in txs:
        if t["cat_kind"] == "transfer":
            continue
        key = merchant_key(t)
        k = (t["account_id"], key, round(abs(t["amount"]), 2))
        if t["amount"] < 0:
            paid.setdefault(key, []).append(dt.date.fromisoformat(t["date"]))
            if -t["amount"] >= DUPLICATE_MIN and t["category"] not in EVERYDAY:
                groups.setdefault(k, []).append(t)
        elif t["amount"] > 0:
            refunds.setdefault(k, []).append(dt.date.fromisoformat(t["date"]))
    out = []
    for k, items in groups.items():
        for a, b in zip(items, items[1:]):
            da, db_ = dt.date.fromisoformat(a["date"]), dt.date.fromisoformat(b["date"])
            days = DUPLICATE_DAYS if not CARD_RE.match(b["counterparty"] or "") else 0
            if b["date"] < since or (db_ - da).days > days:
                continue
            if any(da <= r <= db_ + dt.timedelta(days=REFUND_DAYS) for r in refunds.get(k, [])):
                continue  # one of them came back
            if sum(1 for d in paid[k[1]] if db_ - dt.timedelta(days=60) <= d < da) >= FREQUENT:
                continue  # a merchant paid all the time: the same amount twice is no surprise
            out.append(
                {
                    "key": f"dup:{a['id']}:{b['id']}",
                    "kind": "duplicate",
                    "date": b["date"],
                    "name": _name(b),
                    "amount": round(-b["amount"], 2),
                    "first_date": a["date"],
                    "account": b["account"],
                    "tx_ids": [a["id"], b["id"]],
                }
            )
    return out


def subscription_changes(conn, since: str, today: dt.date, prices: bool, others: bool) -> list[dict]:
    """What changed with subscriptions and contracts since ``since``: prices, new, stopped, back again."""
    out = []
    for e in recurring.overview(conn, today)["events"]:
        if e["date"] < since:
            continue
        price = e["kind"] in ("price_up", "price_down")
        if (price and not prices) or (not price and not others):
            continue
        out.append(e | {"kind": e["kind"] if price else f"sub_{e['kind']}"})
    return out


def unusual(txs: list[dict], since: str, large: float) -> list[dict]:
    """Payments in the window far above the usual amount for their merchant or category."""
    by_merchant: dict[str, list[float]] = {}
    by_category: dict[int, list[float]] = {}
    first_date = txs[0]["date"] if txs else since
    out = []
    for t in txs:  # oldest first, so each payment is compared with what came before it
        if t["amount"] >= 0 or t["cat_kind"] in ("transfer", "income"):
            continue
        amount = -t["amount"]
        key = merchant_key(t)
        if INTERMEDIARY_RE.search(key):
            continue  # PayPal without the shop behind it: anything from a coffee to a sofa
        seen = by_merchant.get(key, [])
        cat_seen = by_category.get(t["category_id"], []) if t["category_id"] else []
        if t["date"] >= since:
            hint = None
            if len(seen) >= 3:
                last = seen[-12:]
                usual = statistics.median(last)
                # Steady amounts (a subscription, the same bill): twice the usual is worth a look.
                # Amounts all over the place (an online shop): only far above anything paid there before.
                steady = max(last) - min(last) <= usual * 0.5
                if (steady and amount >= max(usual * 2, usual + 25)) or (
                    not steady and amount >= max(max(last) * 2, usual * 4, usual + 150)
                ):
                    hint = {"basis": "merchant", "usual": round(usual, 2)}
            elif len(cat_seen) >= 8:
                usual = statistics.median(cat_seen[-30:])
                if amount >= max(usual * 3, usual + 75, 100):
                    hint = {"basis": "category", "usual": round(usual, 2)}
            if hint is None and not seen and large and amount >= large:
                # Only once there is enough history to know the merchant is new.
                if (dt.date.fromisoformat(t["date"]) - dt.date.fromisoformat(first_date)).days >= 60:
                    hint = {"basis": "new", "usual": None}
            if hint:
                out.append(
                    {
                        "key": f"big:{t['id']}",
                        "kind": "unusual",
                        "date": t["date"],
                        "name": _name(t),
                        "amount": round(amount, 2),
                        "category": t["category"],
                        "tx_id": t["id"],
                    }
                    | hint
                )
        by_merchant.setdefault(key, []).append(amount)
        if t["category_id"]:
            by_category.setdefault(t["category_id"], []).append(amount)
    return out


def find(conn, today: dt.date | None = None) -> list[dict]:
    """Current hints, newest first, without the dismissed ones and the kinds switched off in Settings."""
    today = today or dt.date.today()
    since = (today - dt.timedelta(days=WINDOW_DAYS)).isoformat()
    prefs = settings.get_all(conn)
    out: list[dict] = []
    if prefs["alert_duplicates"] or prefs["alert_unusual"]:
        history = _load(conn, (today - dt.timedelta(days=WINDOW_DAYS + 400)).isoformat(), today.isoformat())
        if prefs["alert_duplicates"]:
            out += duplicates(history, since)
        if prefs["alert_unusual"]:
            out += unusual(history, since, float(prefs["alert_large"] or 0))
    if prefs["alert_price_up"] or prefs["alert_subscriptions"]:
        out += subscription_changes(conn, since, today, bool(prefs["alert_price_up"]), bool(prefs["alert_subscriptions"]))
    gone = dismissed(conn)
    # A duplicate is also unusually high for its merchant; the duplicate hint says more.
    dup_ids = {i for a in out if a["kind"] == "duplicate" for i in a["tx_ids"]}
    # One unusually large charge (a back payment) is not a price rise until it repeats.
    spikes = {(a["date"], a["amount"]) for a in out if a["kind"] == "unusual"}
    out = [
        a
        for a in out
        if a["key"] not in gone
        and not (a["kind"] == "unusual" and a["tx_id"] in dup_ids)
        and not (a["kind"] == "price_up" and (a["date"], a["to"]) in spikes)
    ]
    out.sort(key=lambda a: a["date"], reverse=True)
    return out
