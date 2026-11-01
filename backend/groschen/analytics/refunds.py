"""Money that came back for an earlier payment, and the payment it belongs to.

Groschen links most of them by itself (categorize.engine.match_refunds). Here the user sees the
links on both bookings, takes a wrong one away with one tap (which Groschen remembers) and links
money it couldn't place, like a friend paying back a share of a restaurant bill.
"""

import datetime as dt

from .. import db
from ..categorize import engine, names

CANDIDATE_DAYS = 120  # payments offered when linking by hand: this far back from the money


def _brief(tx: dict) -> dict:
    return {"id": tx["id"], "date": tx["date"], "amount": tx["amount"], "merchant": names.display_name(tx)}


def annotate(conn, items: list[dict]) -> None:
    """Add to each booking what came back for it (`refunded`) or the payment it came back for (`refund_for`)."""
    ids = [t["id"] for t in items]
    back: dict[int, float] = {}
    of: dict[int, dict] = {}
    for i in range(0, len(ids), 500):
        part = ids[i : i + 500]
        marks = ",".join("?" * len(part))
        for pid, total in conn.execute(
            "SELECT l.purchase_id, SUM(t.amount) FROM refund_links l JOIN transactions t ON t.id = l.refund_id "
            f"WHERE l.purchase_id IN ({marks}) GROUP BY l.purchase_id",
            part,
        ):
            back[pid] = round(total, 2)
        for r in db.rows(
            conn.execute(
                "SELECT l.refund_id, p.id, p.date, p.amount, p.counterparty, p.purpose, p.booking_text "
                f"FROM refund_links l JOIN transactions p ON p.id = l.purchase_id WHERE l.refund_id IN ({marks})",
                part,
            )
        ):
            of[r["refund_id"]] = _brief(r)
    for t in items:
        t["refunded"] = back.get(t["id"])
        t["refund_for"] = of.get(t["id"])


def detail(conn, tx_id: int) -> dict:
    """Both sides of a booking's links: the payment it came back for, or what came back for it."""
    tx = db.one(conn.execute("SELECT id, amount FROM transactions WHERE id = ?", (tx_id,)))
    if not tx:
        raise KeyError(tx_id)
    link = db.one(conn.execute("SELECT purchase_id, source FROM refund_links WHERE refund_id = ?", (tx_id,)))
    purchase_id = link["purchase_id"] if link else (tx_id if tx["amount"] < 0 else None)
    out: dict = {"purchase": None, "refunds": [], "refunded": 0.0, "left": None, "source": link["source"] if link else None}
    if purchase_id is None:
        return out
    p = db.one(
        conn.execute(
            "SELECT id, date, amount, counterparty, purpose, booking_text FROM transactions WHERE id = ?", (purchase_id,)
        )
    )
    refunds = db.rows(
        conn.execute(
            "SELECT t.id, t.date, t.amount, t.counterparty, t.purpose, t.booking_text, l.source FROM refund_links l "
            "JOIN transactions t ON t.id = l.refund_id WHERE l.purchase_id = ? ORDER BY t.date, t.id",
            (purchase_id,),
        )
    )
    total = round(sum(r["amount"] for r in refunds), 2)
    out.update(
        purchase=_brief(p),
        refunds=[{**_brief(r), "source": r["source"]} for r in refunds],
        refunded=total,
        left=round(-p["amount"] - total, 2),
    )
    return out


def candidates(conn, tx_id: int, q: str = "") -> list[dict]:
    """Payments the money could have come back for, likeliest first: the same payee, then payments
    the money is exactly a share of (all of it, half, a third ...), then the newest. ``share`` says
    how many ways."""
    tx = db.one(
        conn.execute("SELECT id, date, amount, counterparty, purpose, booking_text FROM transactions WHERE id = ?", (tx_id,))
    )
    if not tx:
        raise KeyError(tx_id)
    if tx["amount"] <= 0:
        return []
    since = (dt.date.fromisoformat(tx["date"]) - dt.timedelta(days=CANDIDATE_DAYS)).isoformat()
    rows = db.rows(
        conn.execute(
            "SELECT t.id, t.date, t.amount, t.counterparty, t.purpose, t.booking_text, "
            "c.name AS category, c.color AS category_color, "
            "COALESCE((SELECT SUM(r.amount) FROM refund_links l JOIN transactions r ON r.id = l.refund_id "
            "WHERE l.purchase_id = t.id AND l.refund_id != ?), 0) AS refunded "
            "FROM transactions t JOIN accounts a ON a.id = t.account_id LEFT JOIN categories c ON c.id = t.category_id "
            "WHERE t.amount < 0 AND t.date >= ? AND t.date <= ? AND a.enabled = 1 AND a.fx_ok = 1 AND a.kind != 'depot' "
            "AND (t.cat_source IS NULL OR t.cat_source NOT IN ('own', 'transfer')) ORDER BY t.date DESC, t.id DESC",
            (tx_id, since, tx["date"]),
        )
    )
    key = engine.merchant_key(tx)
    needle = q.strip().lower()
    out = []
    for r in rows:
        left = round(-r["amount"] - r["refunded"], 2)
        if left < tx["amount"] - 0.005:
            continue
        share = engine.share_of(tx["amount"], -r["amount"])
        item = {**_brief(r), "left": left, "category": r["category"], "category_color": r["category_color"], "share": share}
        if needle and needle not in f"{item['merchant']} {r['counterparty'] or ''} {r['purpose'] or ''}".lower():
            if needle.replace(",", ".") not in f"{-r['amount']:.2f}":
                continue
        same = bool(key) and engine.merchant_key(r) == key
        out.append((not same, share is None, item))
    out.sort(key=lambda x: x[:2])  # the newest first within each, as read
    return [x[2] for x in out[:60]]


def link(conn, refund_id: int, purchase_id: int) -> None:
    """The user says this money came back for that payment."""
    r = db.one(conn.execute("SELECT id, amount FROM transactions WHERE id = ?", (refund_id,)))
    p = db.one(conn.execute("SELECT id, amount, category_id FROM transactions WHERE id = ?", (purchase_id,)))
    if not r or not p:
        raise KeyError(refund_id if not r else purchase_id)
    if r["amount"] <= 0 or p["amount"] >= 0:
        raise ValueError("Only money that came in can belong to a payment that went out.")
    taken = conn.execute(
        "SELECT COALESCE(SUM(t.amount), 0) FROM refund_links l JOIN transactions t ON t.id = l.refund_id "
        "WHERE l.purchase_id = ? AND l.refund_id != ?",
        (purchase_id, refund_id),
    ).fetchone()[0]
    if r["amount"] > -p["amount"] - taken + 0.005:
        raise ValueError("That is more than is left of this payment.")
    conn.execute("DELETE FROM refund_rejects WHERE refund_id = ?", (refund_id,))
    conn.execute(
        "INSERT INTO refund_links (refund_id, purchase_id, source, created_at) VALUES (?, ?, 'user', ?) "
        "ON CONFLICT(refund_id) DO UPDATE SET purchase_id = excluded.purchase_id, source = 'user'",
        (refund_id, purchase_id, db.now_iso()),
    )
    conn.execute(
        "UPDATE transactions SET category_id = ?, cat_source = 'refund', confidence = 1, needs_review = 0 WHERE id = ?",
        (p["category_id"], refund_id),
    )
    engine.match_refunds(conn)


def unlink(conn, refund_id: int) -> None:
    """The user says this money is no refund of that payment: it stays apart from now on, and its
    payee's money is only linked by itself again when the whole amount comes back."""
    tx = db.one(
        conn.execute(
            "SELECT id, amount, counterparty, purpose, booking_text, cat_source FROM transactions WHERE id = ?", (refund_id,)
        )
    )
    if not tx:
        raise KeyError(refund_id)
    conn.execute("DELETE FROM refund_links WHERE refund_id = ?", (refund_id,))
    conn.execute(
        "INSERT INTO refund_rejects (refund_id, key, created_at) VALUES (?, ?, ?) "
        "ON CONFLICT(refund_id) DO UPDATE SET key = excluded.key",
        (refund_id, engine._named(tx) or None, db.now_iso()),
    )
    if tx["cat_source"] == "refund":
        # Sorted again like any new booking (which runs the link passes, and they leave it alone now).
        conn.execute("UPDATE transactions SET category_id = NULL, cat_source = NULL WHERE id = ?", (refund_id,))
        engine.categorize(conn, "id = ?", (refund_id,))
    else:
        engine.match_refunds(conn)
