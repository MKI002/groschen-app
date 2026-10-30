"""Connecting a bank, syncing it, and importing CSV files."""

import datetime as dt
import logging

from .. import db, netguard, security, settings
from ..categorize import engine
from ..jobs import Job, UserFacingError
from . import csv_ing, store
from .fints_client import BANKS, FinTSSession, bank_info, public_account

log = logging.getLogger("groschen.sync")

# Swappable for tests: a callable returning an object with the FinTSSession interface.
session_factory = FinTSSession


def _host(url: str) -> str:
    return url.split("//", 1)[-1].split("/", 1)[0]


def allow_bank_hosts() -> None:
    for info in BANKS.values():
        netguard.allow_host(_host(info["server"]))


def test_connection(job: Job, bank_code: str, login: str, pin: str, product_id: str) -> dict:
    """Log in once, list the accounts and save the connection (credentials encrypted)."""
    info = bank_info(bank_code)
    job.add_steps(f"Connecting to {info['short']}", "Reading your accounts")
    job.step(0)
    with netguard.purpose(f"{info['short']} connection test"):
        with session_factory(bank_code, login, pin, product_id, None, on_wait=job.wait) as s:
            job.resume()
            job.step(1)
            accounts = s.accounts()
            balances = {}
            for acc in accounts:
                if acc["kind"] != "depot":
                    try:
                        balances[acc["account_number"]] = s.balance(acc)
                    except UserFacingError:
                        balances[acc["account_number"]] = None
            state = s.state()
            approved = getattr(s, "approved", False)

    with db.session() as conn:
        row = db.one(conn.execute("SELECT id FROM connections WHERE bank_code = ?", (bank_code,)))
        values = (security.encrypt(login), security.encrypt(pin), product_id, security.encrypt_bytes(state))
        if row:
            conn.execute(
                "UPDATE connections SET login_enc = ?, pin_enc = ?, product_id = ?, state_enc = ?, status = 'ok', "
                "last_error = NULL WHERE id = ?",
                (*values, row["id"]),
            )
            connection_id = row["id"]
            if approved:
                _logged_in(conn, connection_id)
        else:
            cur = conn.execute(
                "INSERT INTO connections (bank_code, bank_name, server, login_enc, pin_enc, product_id, state_enc, status, "
                "bank_login_confirmed_at, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, 'ok', ?, ?)",
                (bank_code, info["name"], info["server"], *values, db.now_iso(), db.now_iso()),
            )
            connection_id = cur.lastrowid
        result = []
        remember_holder(conn, *(n for acc in accounts for n in acc.get("owners") or []))
        for acc in accounts:
            account_id = store.upsert_account(conn, connection_id, acc)
            bal = balances.get(acc["account_number"])
            if bal:
                store.set_balance(conn, account_id, bal[0], bal[1])
            name = conn.execute("SELECT name FROM accounts WHERE id = ?", (account_id,)).fetchone()[0]
            result.append({**public_account(acc), "id": account_id, "name": name, "balance": bal[0] if bal else None})
    return {"connection_id": connection_id, "accounts": result}


def _logged_in(conn, connection_id: int) -> None:
    """The user approved a request in the banking app: the 90 days until the next login start again."""
    conn.execute("UPDATE connections SET bank_login_confirmed_at = ? WHERE id = ?", (db.now_iso(), connection_id))


def _since(conn, connection: dict, full: bool) -> dt.date:
    days = bank_info(connection["bank_code"])["history_days"] - 1
    earliest = dt.date.today() - dt.timedelta(days=days)
    if full or not connection.get("last_sync_at"):
        return earliest
    last = dt.date.fromisoformat(connection["last_sync_at"][:10])
    return max(earliest, last - dt.timedelta(days=10))


def sync_connection(job: Job, connection_id: int, full: bool = False, step_offset: int = 0) -> dict:
    with db.session() as conn:
        c = db.one(conn.execute("SELECT * FROM connections WHERE id = ?", (connection_id,)))
        if not c:
            raise UserFacingError("That bank connection no longer exists.")
        accounts = db.rows(
            conn.execute("SELECT * FROM accounts WHERE connection_id = ? AND enabled = 1 AND manual = 0", (connection_id,))
        )
        since = _since(conn, c, full)
    info = bank_info(c["bank_code"])
    login, pin = security.decrypt(c["login_enc"]), security.decrypt(c["pin_enc"])
    state = security.decrypt_bytes(c["state_enc"])
    new_ids: list[int] = []
    counts = {"transactions": 0, "holdings": 0}
    approved = False
    try:
        with netguard.purpose(f"{info['short']} sync"):
            job.step(step_offset + 0)
            with session_factory(c["bank_code"], login, pin, c["product_id"], state, on_wait=job.wait) as s:
                job.resume()
                job.step(step_offset + 1)
                live = {(a.get("iban") or a["account_number"]): a for a in s.accounts()}
                with db.session() as conn:
                    remember_holder(conn, *(n for a in live.values() for n in a.get("owners") or []))
                for acc in accounts:
                    remote = live.get(acc["iban"] or acc["account_number"])
                    if not remote:
                        continue
                    if acc["kind"] == "depot":
                        holdings = s.holdings(remote)
                        with db.session() as conn:
                            store.save_holdings(conn, acc["id"], holdings)
                        counts["holdings"] += len(holdings)
                        continue
                    txs = s.transactions(remote, since)
                    bal = s.balance(remote)
                    with db.session() as conn:
                        ids = store.insert_transactions(conn, acc["id"], txs, "fints")
                        new_ids.extend(ids)
                        if bal:
                            store.set_balance(conn, acc["id"], bal[0], bal[1])
                    counts["transactions"] += len(ids)
                new_state = s.state()
                approved = getattr(s, "approved", False)
    except UserFacingError as exc:
        with db.session() as conn:
            conn.execute("UPDATE connections SET status = 'error', last_error = ? WHERE id = ?", (str(exc), connection_id))
        raise
    with db.session() as conn:
        conn.execute(
            "UPDATE connections SET status = 'ok', last_error = NULL, last_sync_at = ?, state_enc = ? WHERE id = ?",
            (db.now_iso(), security.encrypt_bytes(new_state), connection_id),
        )
        if approved:
            _logged_in(conn, connection_id)
    return {"new_ids": new_ids, **counts}


def sync_all(job: Job, full: bool = False, first_run: bool = False) -> dict:
    """Sync every bank connection, then categorize what's new."""
    with db.session() as conn:
        connections = db.rows(conn.execute("SELECT id, bank_name FROM connections ORDER BY id"))
    if first_run:
        job.add_steps(
            "Connecting to ING",
            "Fetching the last 90 days from your accounts",
            "Merging with your imported history",
            "Categorizing your transactions",
            "Finding subscriptions and recurring payments",
        )
    else:
        job.add_steps("Connecting to the bank", "Fetching new transactions", "Categorizing")
    totals = {"transactions": 0, "holdings": 0, "categorized": 0}
    for c in connections:
        r = sync_connection(job, c["id"], full=full)
        totals["transactions"] += r["transactions"]
        totals["holdings"] += r["holdings"]
    cat_step = 3 if first_run else 2
    if first_run:
        job.step(2)
    job.step(cat_step)
    with db.session() as conn:
        n = conn.execute("SELECT COUNT(*) FROM transactions WHERE cat_source IS NULL OR cat_source = 'none'").fetchone()[0]
        job.step(cat_step, label=f"Categorizing {n:,} transactions".replace(",", "."))
        totals["categorized"] = engine.categorize(conn, "cat_source IS NULL OR cat_source = 'none'")
    if first_run:
        job.step(4)
        from ..analytics import recurring

        with db.session() as conn:
            totals["recurring"] = len(recurring.detect(conn))
    return totals


def _csv_kind(parsed: dict) -> str:
    """Girokonto or Extra-Konto: by the account name, else by what was booked (card payments, salary)."""
    name = (parsed["account_name"] or "").lower()
    if name.startswith(("extra", "tagesgeld", "spar")):
        return "savings"
    if name:
        return "checking"
    texts = {(r["booking_text"] or "").lower() for r in parsed["rows"]}
    cards = any((r["counterparty"] or "").upper().startswith("VISA ") for r in parsed["rows"])
    if cards or texts & {"lastschrift", "gehalt/rente", "lohn/gehalt"}:
        return "checking"
    return "savings" if texts and texts <= {"zinsgutschrift", "gutschrift", "überweisung", "abschluss"} else "checking"


def _csv_account(conn, parsed: dict) -> int | None:
    """The account a CSV file belongs to: by IBAN, else the only account of its kind."""
    if parsed["iban"]:
        row = db.one(conn.execute("SELECT id FROM accounts WHERE REPLACE(iban, ' ', '') = ?", (parsed["iban"],)))
        if row:
            return row["id"]
        # An account the bank sync knows under this IBAN is found above; one imported from a file
        # without IBAN before is the same account when it is the only one of its kind.
        rows = conn.execute(
            "SELECT id FROM accounts WHERE kind = ? AND manual = 0 AND (iban IS NULL OR iban = '')", (_csv_kind(parsed),)
        ).fetchall()
        return rows[0]["id"] if len(rows) == 1 else None
    rows = conn.execute("SELECT id FROM accounts WHERE kind = ? AND manual = 0", (_csv_kind(parsed),)).fetchall()
    return rows[0]["id"] if len(rows) == 1 else None


def remember_holder(conn, *names: str | None) -> None:
    """The account holder's name, as the bank knows it: transfers to it go to the user's own accounts.

    Bookings already there are sorted again when a name is new.
    """
    known = list(settings.get(conn, "holder_names") or [])
    seen = {engine.name_tokens(k) for k in known}
    for name in names:
        name = " ".join((name or "").split())[:80]
        tokens = engine.name_tokens(name)
        if len(tokens) >= 2 and tokens not in seen:
            known.append(name)
            seen.add(tokens)
    if known != list(settings.get(conn, "holder_names") or []):
        settings.put(conn, "holder_names", known[-6:])
        engine.reapply_quick(conn)


def import_csv(job: Job, raw: bytes, account_id: int | None = None, filename: str | None = None) -> dict:
    parsed = csv_ing.parse(raw, filename)
    with db.session() as conn:
        if account_id is None:
            account_id = _csv_account(conn, parsed)
            if account_id is not None and parsed["iban"]:
                conn.execute(
                    "UPDATE accounts SET iban = ? WHERE id = ? AND (iban IS NULL OR iban = '')", (parsed["iban"], account_id)
                )
        if parsed["holder"]:
            remember_holder(conn, parsed["holder"])
        if account_id is None:
            kind = _csv_kind(parsed)
            account_id = store.upsert_account(
                conn,
                None,
                {
                    "kind": kind,
                    "name": parsed["account_name"] or "Girokonto",
                    "iban": parsed["iban"],
                    "account_number": None,
                    "bic": BANKS["50010517"]["bic"],
                    "blz": "50010517",
                    "currency": "EUR",
                },
            )
        rows, skipped = store.filter_csv_overlap(conn, account_id, parsed["rows"])
        new_ids = store.insert_transactions(conn, account_id, rows, "csv")
        has_sync, known_date = conn.execute(
            "SELECT connection_id, balance_date FROM accounts WHERE id = ?", (account_id,)
        ).fetchone()
        latest = max((r["date"] for r in parsed["rows"]), default=dt.date.today().isoformat())
        # An older export doesn't overwrite a newer balance.
        if parsed["balance"] is not None and not has_sync and (not known_date or latest >= known_date[:10]):
            store.set_balance(conn, account_id, parsed["balance"], latest)
        engine.categorize(conn, f"id IN ({','.join(str(i) for i in new_ids) or 'NULL'})")
        dates = [r["date"] for r in rows]
        name = conn.execute("SELECT name FROM accounts WHERE id = ?", (account_id,)).fetchone()[0]
    return {
        "account_id": account_id,
        "account_name": name,
        "imported": len(new_ids),
        "skipped": skipped + (len(rows) - len(new_ids)),
        "first": min(dates) if dates else None,
        "last": max(dates) if dates else None,
    }


def import_prices(raw: bytes) -> dict:
    prices = csv_ing.parse_prices(raw)
    with db.session() as conn:
        for isin, date, price in prices:
            conn.execute(
                "INSERT INTO prices (isin, date, price) VALUES (?, ?, ?) "
                "ON CONFLICT(isin, date) DO UPDATE SET price = excluded.price",
                (isin, date, price),
            )
    isins = sorted({p[0] for p in prices})
    return {"imported": len(prices), "isins": isins, "first": min(p[1] for p in prices), "last": max(p[1] for p in prices)}
