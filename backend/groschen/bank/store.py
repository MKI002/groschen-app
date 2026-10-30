"""Saving what comes from the bank or a CSV file into the database."""

import datetime as dt
import hashlib
import re
from collections import Counter

from .. import db


def _norm(text: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", "", (text or "").lower())


def _name(text: str | None) -> str:
    """The start of a counterparty name, spelled the way banks send it (no umlauts)."""
    text = (text or "").lower().translate(str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}))
    return _norm(text)[:10]


def fingerprints(account_id: int, txs: list[dict]) -> list[str]:
    """Stable ids for transactions. Identical rows on the same day get a running number."""
    seen: dict[str, int] = {}
    out = []
    for t in txs:
        base = "|".join(
            [
                str(account_id),
                t["date"],
                f"{float(t['amount']):.2f}",
                _norm(t.get("counterparty"))[:40],
                _norm(t.get("purpose"))[:80],
            ]
        )
        n = seen.get(base, 0)
        seen[base] = n + 1
        out.append(hashlib.sha1(f"{base}#{n}".encode(), usedforsecurity=False).hexdigest())
    return out


def upsert_account(conn, connection_id: int | None, acc: dict) -> int:
    existing = None
    if acc.get("iban"):
        existing = db.one(conn.execute("SELECT id FROM accounts WHERE iban = ?", (acc["iban"],)))
    if not existing and acc.get("account_number"):
        existing = db.one(
            conn.execute(
                "SELECT id FROM accounts WHERE account_number = ? AND COALESCE(blz, '') = COALESCE(?, '')",
                (acc["account_number"], acc.get("blz")),
            )
        )
    if existing:
        conn.execute(
            "UPDATE accounts SET connection_id = COALESCE(?, connection_id), kind = ?, iban = COALESCE(?, iban), "
            "account_number = COALESCE(?, account_number), subaccount = ?, bic = ?, blz = ?, currency = ? WHERE id = ?",
            (
                connection_id,
                acc["kind"],
                acc.get("iban"),
                acc.get("account_number"),
                acc.get("subaccount"),
                acc.get("bic"),
                acc.get("blz"),
                acc.get("currency") or "EUR",
                existing["id"],
            ),
        )
        return existing["id"]
    cur = conn.execute(
        "INSERT INTO accounts (connection_id, kind, name, iban, account_number, subaccount, bic, blz, currency, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            connection_id,
            acc["kind"],
            nice_name(acc),
            acc.get("iban"),
            acc.get("account_number"),
            acc.get("subaccount"),
            acc.get("bic"),
            acc.get("blz"),
            acc.get("currency") or "EUR",
            db.now_iso(),
        ),
    )
    return cur.lastrowid


def nice_name(acc: dict) -> str:
    name = (acc.get("name") or "").strip()
    if name and name.lower() not in ("account", "konto"):
        return name
    return {"checking": "Girokonto", "savings": "Extra-Konto", "depot": "Depot"}.get(acc["kind"], "Account")


def set_balance(conn, account_id: int, balance: float, date: str) -> None:
    conn.execute("UPDATE accounts SET balance = ?, balance_date = ? WHERE id = ?", (balance, date, account_id))
    conn.execute(
        "INSERT INTO balance_history (account_id, date, balance) VALUES (?, ?, ?) "
        "ON CONFLICT(account_id, date) DO UPDATE SET balance = excluded.balance",
        (account_id, date, balance),
    )


def _csv_twins(conn, account_id: int) -> dict[tuple[str, float], list[str]]:
    twins: dict[tuple[str, float], list[str]] = {}
    for r in conn.execute(
        "SELECT date, amount, counterparty FROM transactions WHERE account_id = ? AND source = 'csv'", (account_id,)
    ):
        twins.setdefault((r["date"], round(r["amount"], 2)), []).append(_name(r["counterparty"]))
    return twins


def _take_twin(twins: dict, key: tuple[str, float], party: str, alone: bool) -> bool:
    """Use up the imported CSV row that stands for this bank row, if there is one."""
    names = twins.get(key)
    if not names:
        return False
    if party in names:
        names.remove(party)
    elif not party or "" in names:
        names.remove("" if "" in names else names[0])
    elif alone and len(names) == 1:
        names.clear()
    else:
        return False
    return True


def insert_transactions(conn, account_id: int, txs: list[dict], source: str) -> list[int]:
    """Insert new transactions, skipping ones already stored. Returns the new ids.

    Bank rows that an earlier CSV import already brought in are skipped as well. The bank and
    the CSV export word the same booking differently, so they match loosely: same day, same
    amount, and the same start of the name, or no name on one side, or the only candidate.
    """
    new_ids = []
    now = db.now_iso()
    twins = _csv_twins(conn, account_id) if source == "fints" else {}
    keys = [(t["date"], round(float(t["amount"]), 2)) for t in txs]
    per_key = Counter(keys)
    for t, fp, key in zip(txs, fingerprints(account_id, txs), keys):
        if twins and _take_twin(twins, key, _name(t.get("counterparty")), per_key[key] == 1):
            continue
        cur = conn.execute(
            "INSERT OR IGNORE INTO transactions (account_id, date, value_date, amount, currency, counterparty, "
            "counterparty_iban, purpose, booking_text, fingerprint, source, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                account_id,
                t["date"],
                t.get("value_date"),
                t["amount"],
                t.get("currency") or "EUR",
                t.get("counterparty"),
                t.get("counterparty_iban"),
                t.get("purpose"),
                t.get("booking_text"),
                fp,
                source,
                now,
            ),
        )
        if cur.rowcount:
            new_ids.append(cur.lastrowid)
    return new_ids


def filter_csv_overlap(conn, account_id: int, rows: list[dict]) -> tuple[list[dict], int]:
    """Drop CSV rows that the bank sync already delivered (the formats differ slightly, so match loosely)."""
    first_synced = conn.execute(
        "SELECT MIN(date) FROM transactions WHERE account_id = ? AND source = 'fints'", (account_id,)
    ).fetchone()[0]
    existing = {}
    for r in conn.execute("SELECT date, amount, counterparty FROM transactions WHERE account_id = ?", (account_id,)):
        existing.setdefault((r["date"], round(r["amount"], 2)), []).append(_name(r["counterparty"]))
    keep, skipped = [], 0
    for row in rows:
        if first_synced and row["date"] >= first_synced:
            skipped += 1
            continue
        key = (row["date"], round(row["amount"], 2))
        if key in existing and _name(row.get("counterparty")) in existing[key]:
            skipped += 1
            continue
        keep.append(row)
    return keep, skipped


def save_holdings(conn, account_id: int, holdings: list[dict], today: str | None = None) -> float:
    today = today or dt.date.today().isoformat()
    now = db.now_iso()
    conn.execute("DELETE FROM holdings WHERE account_id = ?", (account_id,))
    total = 0.0
    for h in holdings:
        total += h["value"]
        conn.execute(
            "INSERT INTO holdings (account_id, isin, name, pieces, price, price_date, value, acquisition_price, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                account_id,
                h["isin"],
                h["name"],
                h["pieces"],
                h["price"],
                h.get("price_date"),
                h["value"],
                h.get("acquisition_price"),
                now,
            ),
        )
        conn.execute(
            "INSERT INTO holding_history (date, account_id, isin, pieces, price, value) VALUES (?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(date, account_id, isin) DO UPDATE SET pieces = excluded.pieces, price = excluded.price, "
            "value = excluded.value",
            (today, account_id, h["isin"], h["pieces"], h["price"], h["value"]),
        )
        if h.get("price") and h.get("price_date"):
            conn.execute(
                "INSERT INTO prices (isin, date, price) VALUES (?, ?, ?) "
                "ON CONFLICT(isin, date) DO UPDATE SET price = excluded.price",
                (h["isin"], h["price_date"], h["price"]),
            )
    set_balance(conn, account_id, round(total, 2), today)
    return total
