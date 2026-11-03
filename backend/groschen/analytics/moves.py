"""Money that only moves between the user's own pockets: neither spent nor earned.

A transfer from the current account to the savings account, a purchase for the depot, a round-up
of Kleingeld Plus or the credit card bill moves money without making the user richer or poorer.
The lists show such a booking quietly, without a sign, and when both sides of it are in Groschen
(it left one account and arrived on another) as one row: "Girokonto → Extra-Konto". A day's
round-ups fold into one line. Which bookings count is the same as in the charts
(common.classify_flow): a category of the "transfer" kind, or money Groschen counts as invested.
Changing the category to something else is the way to say a booking is real spending after all.
"""

import datetime as dt

from .. import db
from . import common

ROUNDUP_MAX = 5.0  # a round-up is small; Kleingeld Plus' monthly collection of them isn't one


def invested(conn) -> set[int]:
    """Bookings counted as put into investments, or placed somewhere by the user on the Overview."""
    from . import portfolio, savings  # portfolio imports from drilldown, which imports this module

    return {p["id"] for p in portfolio.payments(conn) if p["counted"]} | savings.placed_by_hand(conn)


def _text(t: dict) -> str:
    return f"{t.get('counterparty') or ''} {t.get('purpose') or ''} {t.get('booking_text') or ''}".upper()


def annotate(conn, items: list[dict]) -> None:
    """Add `move` (where the money went, and the other side's booking) and `roundup` to each booking.

    `move` is None for real income and spending. Otherwise it holds `from` and `to` (account names,
    None where Groschen doesn't know the account) and `mirror`, the id of the booking on the other
    account when both sides are there.
    """
    from . import savings

    for t in items:
        t["move"], t["roundup"] = None, False
    if not items:
        return
    cats = common.categories(conn)
    placed = invested(conn)

    def moving(t: dict) -> bool:
        return t["id"] in placed or (cats.get(t["category_id"]) or {}).get("kind") == "transfer"

    shown = [t for t in items if moving(t)]
    if not shown:
        return
    accounts = {a["id"]: a for a in db.rows(conn.execute("SELECT id, kind, name, iban FROM accounts WHERE enabled = 1"))}
    depots = [a["name"] for a in accounts.values() if a["kind"] == "depot"]
    # The other side of a transfer can be a few days away, also beyond the first or last booking listed.
    pad = dt.timedelta(days=savings.MAX_DAYS * 2)
    lo = (dt.date.fromisoformat(min(t["date"] for t in shown)) - pad).isoformat()
    hi = (dt.date.fromisoformat(max(t["date"] for t in shown)) + pad).isoformat()
    window = [
        t
        for t in db.rows(
            conn.execute(
                "SELECT t.id, t.date, t.amount, t.account_id, t.counterparty_iban, t.category_id "
                "FROM transactions t JOIN accounts a ON a.id = t.account_id "
                "WHERE a.enabled = 1 AND a.kind != 'depot' AND t.amount != 0 AND t.date >= ? AND t.date <= ? "
                "ORDER BY t.date, t.id",
                (lo, hi),
            )
        )
        if moving(t)
    ]
    pairs = savings.mirrors(window, accounts)
    where = {t["id"]: accounts.get(t["account_id"], {}).get("name") for t in window}
    for t in shown:
        here = where.get(t["id"], t.get("account"))
        other = pairs.get(t["id"])
        if other:
            there = accounts.get(other["account_id"], {}).get("name")
            frm, to = (here, there) if t["amount"] < 0 else (there, here)
        elif t["amount"] < 0:
            # A purchase for the depot is paid from the current account; the depot has no booking of it.
            invest = t["id"] in placed or (cats.get(t["category_id"]) or {}).get("name") == "Investments"
            frm, to = here, depots[0] if invest and len(depots) == 1 else None
        else:
            frm, to = None, here
        t["move"] = {"from": frm, "to": to, "mirror": other["id"] if other else None}
        t["roundup"] = abs(t["amount"]) < ROUNDUP_MAX and bool(savings.ROUNDUP_RE.search(_text(t)))
