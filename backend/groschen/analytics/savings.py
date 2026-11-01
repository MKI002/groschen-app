"""Where the money that was saved actually went.

"Saved" is income minus spending. This splits it by destination: ETFs (savings plan, single
purchases, Kleingeld Plus round-ups), the savings account, other own accounts, and whatever
simply stays on the current account. Moves between the user's own accounts are found by
comparing the accounts with each other: an amount leaving one account and the same amount
arriving on another within a few days is one transfer. The user can correct any of them with
one click; for transfers to an account Groschen can't see, the choice carries over to later
transfers to the same counterparty.
"""

import datetime as dt
import re

from .. import db
from ..categorize import engine
from . import common, portfolio
from .drilldown import display_name

# Shown in this order; "stays" is whatever is left over. Kleingeld Plus round-ups count as savings plan.
DESTS = ("plan", "etf", "savings", "other", "stays")
INVEST = {"plan", "etf"}
# The Overview shows only three: invested, put aside on other accounts, and what stays.
GROUP = {"plan": "invested", "etf": "invested", "savings": "aside", "other": "aside", "stays": "stays"}
OLD = {"roundup": "plan"}  # choices saved before round-ups joined the savings plan
MAX_DAYS = 4

ROUNDUP_RE = re.compile(r"KLEINGELD|AUFRUNDUNG|ROUND ?UP")
PLAN_RE = re.compile(r"SPARPLAN|DAUERAUFTRAG|SAVINGS PLAN")
# A transfer whose text talks about investing, e.g. to an investment account at another bank.
INVEST_RE = re.compile(r"INVEST|\bETFS?\b|\bDEPOT|AKTIE|BROKER|BOERSE|BÖRSE|WERTPAPIER")
# Accounts elsewhere that are savings by name: Tagesgeld, Festgeld, Bausparen, VL.
SAVINGS_RE = re.compile(r"TAGESGELD|FESTGELD|SPARKONTO|SPARBUCH|BAUSPAR|VERMOEGENSWIRKSAM|VERMÖGENSWIRKSAM|\bVL\b")


def _text(t: dict) -> str:
    return f"{t.get('counterparty') or ''} {t.get('purpose') or ''} {t.get('booking_text') or ''}".upper()


def _norm_iban(iban: str | None) -> str:
    return re.sub(r"\s+", "", iban or "").upper()


def cp_key(t: dict) -> str:
    """Who a transfer goes to: the counterparty's IBAN when the bank gives one, else its name."""
    iban = _norm_iban(t.get("counterparty_iban"))
    if iban:
        return f"iban:{iban}"
    key = engine.merchant_key(t)
    return f"name:{key}" if key else ""


def _bucket(kind: str) -> str:
    return "depot" if kind == "depot" else "savings" if kind == "savings" else "cash"


def _match(txs: list[dict], accounts: dict[int, dict]) -> dict[int, dict]:
    """Pair each transfer with its mirror image on another of the user's accounts.

    Same amount the other way round on a different account within a few days. A counterparty IBAN
    that names the other account wins over the closest date; otherwise the closest date wins.
    """
    incoming: dict[float, list[dict]] = {}
    for t in txs:
        if t["amount"] > 0:
            incoming.setdefault(round(t["amount"], 2), []).append(t)
    pairs: dict[int, dict] = {}
    for t in sorted((t for t in txs if t["amount"] < 0), key=lambda t: (t["date"], t["id"])):
        day = dt.date.fromisoformat(t["date"])
        iban = _norm_iban(t.get("counterparty_iban"))
        best, best_score = None, None
        for m in incoming.get(round(-t["amount"], 2), []):
            if m["id"] in pairs or m["account_id"] == t["account_id"]:
                continue
            gap = abs((dt.date.fromisoformat(m["date"]) - day).days)
            if gap > MAX_DAYS:
                continue
            named = bool(iban) and iban == _norm_iban(accounts.get(m["account_id"], {}).get("iban"))
            score = (0 if named else 1, gap)
            if best_score is None or score < best_score:
                best, best_score = m, score
        if best:
            pairs[t["id"]] = best
            pairs[best["id"]] = t
    return pairs


def _overrides(conn) -> tuple[dict[int, str], dict[str, str]]:
    by_tx = {r["tx_id"]: OLD.get(r["dest"], r["dest"]) for r in conn.execute("SELECT tx_id, dest FROM saving_dest")}
    by_cp = {r["key"]: OLD.get(r["dest"], r["dest"]) for r in conn.execute("SELECT key, dest FROM saving_dest_cp")}
    return by_tx, by_cp


def _plan_amounts(payments: list[dict]) -> set[int]:
    """Amounts paid into investments in at least three different months: a savings plan."""
    months: dict[int, set[str]] = {}
    for p in payments:
        if p["counted"] and p["amount"] > 0:
            months.setdefault(round(p["amount"]), set()).add(p["date"][:7])
    return {a for a, ms in months.items() if len(ms) >= 3}


def _invest_kind(t: dict, plan_amounts: set[int]) -> str:
    text = _text(t)
    if ROUNDUP_RE.search(text) or PLAN_RE.search(text) or round(-t["amount"]) in plan_amounts:
        return "plan"
    return "etf"


def destinations(conn, start: str, end: str, saved: float, txs: list[dict], payments: list[dict] | None = None) -> dict:
    """Split ``saved`` (income minus spending of ``txs``, the bookings that count for the period).

    ``payments`` (portfolio.payments) can be passed in when splitting many months in a row.
    """
    accounts = {
        a["id"]: a
        for a in db.rows(conn.execute("SELECT id, kind, name, iban FROM accounts WHERE enabled = 1 AND fx_ok = 1"))
    }
    own_ibans = {_norm_iban(a["iban"]): a for a in accounts.values() if a["iban"]}
    cats = common.categories(conn)
    payments = portfolio.payments(conn) if payments is None else payments
    counted = {p["id"]: p for p in payments if p["counted"]}
    plan_amounts = _plan_amounts(payments)
    by_tx, by_cp = _overrides(conn)

    # Transfers a few days either side, so a move that crosses the start or end of the period finds its other half.
    pad = dt.timedelta(days=MAX_DAYS + 1)
    lo = (dt.date.fromisoformat(max(start, "1900-01-10")) - pad).isoformat()
    hi = (dt.date.fromisoformat(min(end, "2999-12-20")) + pad).isoformat()
    window = db.rows(
        conn.execute(
            "SELECT t.id, t.date, t.amount, t.account_id, t.counterparty, t.counterparty_iban, t.purpose, t.booking_text, "
            "t.category_id FROM transactions t JOIN accounts a ON a.id = t.account_id "
            "WHERE a.enabled = 1 AND a.fx_ok = 1 AND t.amount != 0 AND t.date >= ? AND t.date <= ?",
            (lo, hi),
        )
    )

    def moved(t: dict) -> bool:
        return t["id"] in counted or t["id"] in by_tx or (cats.get(t["category_id"]) or {}).get("kind") == "transfer"

    transfers = [t for t in window if moved(t)]
    pairs = _match(transfers, accounts)
    is_transfer = {t["id"] for t in transfers}

    amounts = dict.fromkeys(DESTS, 0.0)
    items: list[dict] = []

    def put(t: dict, dest: str, how: str, auto: str, partner: str | None, amount: float, cp: str, count=True) -> None:
        if count:
            amounts[dest] += amount
        acc = accounts.get(t["account_id"]) or {}
        items.append(
            {
                "id": t["id"],
                "date": t["date"],
                "amount": round(amount, 2),
                "dest": dest,
                "auto": auto,
                "how": how,
                "from": acc.get("name"),
                "to": partner,
                "name": display_name(t),
                "purpose": (t.get("purpose") or "")[:140],
                "learnable": bool(cp),
            }
        )

    for t in txs:
        acc = accounts.get(t["account_id"])
        if not acc:
            continue
        here = _bucket(acc["kind"])
        if t["id"] not in is_transfer:
            # Interest on the savings account stays there; dividends booked in the depot stay invested.
            if here == "savings":
                amounts["savings"] += t["amount"]
            elif here == "depot":
                amounts["etf"] += t["amount"]
            continue
        if here == "depot":
            continue  # its other half on a normal account says where the money came from
        partner = pairs.get(t["id"])
        p_acc = accounts.get(partner["account_id"]) if partner else None
        p_bucket = _bucket(p_acc["kind"]) if p_acc else None
        if not p_acc:
            named = own_ibans.get(_norm_iban(t.get("counterparty_iban")))
            if named and named["id"] != t["account_id"]:
                p_acc, p_bucket = named, _bucket(named["kind"])
        if here == "savings":
            # Money leaving the savings account lowers what is saved there and lands where it went.
            if p_bucket == "cash" or p_bucket == "savings":
                continue  # the current-account half counts it (or it only moved between savings accounts)
            amounts["savings"] += t["amount"]
        elif p_bucket == "cash":
            continue  # between two current accounts: still money that is just there

        # Where it went, as Groschen sees it.
        key = ""
        if t["id"] in counted or p_bucket == "depot":
            auto, how = _invest_kind(t, plan_amounts), "invest" if t["id"] in counted else "mirror"
        elif p_bucket == "savings":
            auto, how = ("plan" if ROUNDUP_RE.search(_text(t)) else "savings"), "mirror"
        else:
            key = cp_key(t)
            text = _text(t)
            cat = (cats.get(t["category_id"]) or {}).get("name")
            if ROUNDUP_RE.search(text):
                auto, how = "plan", "text"
            elif INVEST_RE.search(text):
                auto, how = _invest_kind(t, plan_amounts), "text"
            elif cat == "Savings" or SAVINGS_RE.search(text):
                auto, how = "savings", "category" if cat == "Savings" else "text"
            else:
                auto, how = "other", "category"
        dest = auto
        if t["id"] in by_tx:
            dest, how = by_tx[t["id"]], "user"
        elif key and key in by_cp:
            dest, how = by_cp[key], "learned"
        partner_name = p_acc["name"] if p_acc else None
        if here == "savings" and dest == "savings":
            # The user says it stayed saved (another savings account elsewhere): undo the move out.
            amounts["savings"] -= t["amount"]
            put(t, dest, how, auto, partner_name, -t["amount"], key, count=False)
            continue
        # "Stays" is the remainder below, so a booking sent there is listed but not added.
        put(t, dest, how, auto, partner_name, -t["amount"], key, count=dest != "stays")

    placed = sum(v for k, v in amounts.items() if k != "stays")
    amounts["stays"] = saved - placed
    parts = [
        {
            "key": k,
            "group": GROUP[k],
            "amount": round(amounts[k], 2),
            "count": sum(1 for i in items if i["dest"] == k),
            "account": _savings_name(accounts, items) if k == "savings" else None,
        }
        for k in DESTS
        if abs(amounts[k]) >= 0.005 or any(i["dest"] == k for i in items)
    ]
    items.sort(key=lambda i: (i["date"], i["id"]), reverse=True)
    return {"saved": round(saved, 2), "parts": parts, "items": items}


def _savings_name(accounts: dict[int, dict], items: list[dict]) -> str | None:
    """The savings account's own name, when it is the only one and everything saved went there."""
    names = [a["name"] for a in accounts.values() if a["kind"] == "savings"]
    if len(names) != 1 or any(i["to"] != names[0] for i in items if i["dest"] == "savings"):
        return None
    return names[0]


def set_dest(conn, tx_id: int, dest: str | None, learn: bool = True) -> None:
    """The user's one-click correction; ``None`` goes back to what Groschen found by itself.

    For a payment the Investments page counts, the choice also decides whether it counts there.
    For a transfer to someone Groschen can't see, it also applies to later transfers to them.
    """
    tx = db.one(
        conn.execute(
            "SELECT id, counterparty, counterparty_iban, purpose, booking_text FROM transactions WHERE id = ?", (tx_id,)
        )
    )
    if not tx:
        raise KeyError(tx_id)
    key = cp_key(tx)
    if dest is None:
        conn.execute("DELETE FROM saving_dest WHERE tx_id = ?", (tx_id,))
        if key:
            conn.execute("DELETE FROM saving_dest_cp WHERE key = ?", (key,))
        conn.execute("DELETE FROM invest_skips WHERE tx_id = ?", (tx_id,))
        return
    conn.execute(
        "INSERT INTO saving_dest (tx_id, dest, created_at) VALUES (?, ?, ?) "
        "ON CONFLICT(tx_id) DO UPDATE SET dest = excluded.dest, created_at = excluded.created_at",
        (tx_id, dest, db.now_iso()),
    )
    if learn and key:
        conn.execute(
            "INSERT INTO saving_dest_cp (key, dest, created_at) VALUES (?, ?, ?) "
            "ON CONFLICT(key) DO UPDATE SET dest = excluded.dest, created_at = excluded.created_at",
            (key, dest, db.now_iso()),
        )
    # Keep the Investments page in step: an ETF destination counts there, anything else doesn't.
    in_payments = any(p["id"] == tx_id for p in portfolio.payments(conn))
    if in_payments:
        portfolio.set_counted(conn, tx_id, dest in INVEST)


def placed_by_hand(conn) -> set[int]:
    """Bookings the user placed somewhere on the Overview: money moved, not spent."""
    return {r[0] for r in conn.execute("SELECT tx_id FROM saving_dest")}
