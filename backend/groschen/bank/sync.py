"""Connecting a bank, syncing it, and importing CSV files."""

import datetime as dt
import json
import logging

from .. import db, fx, i18n, netguard, regions, security, settings
from ..categorize import engine
from ..jobs import Job, UserFacingError
from . import banks, csv_import, store
from .fints_client import HISTORY_DAYS, FinTSSession, bank_info, public_account

log = logging.getLogger("groschen.sync")

# Swappable for tests: a callable returning an object with the FinTSSession interface.
session_factory = FinTSSession


def allow_bank_hosts() -> None:
    """Let Groschen reach the FinTS servers of the banks the user connected, and nothing else."""
    with db.session() as conn:
        for (server,) in conn.execute("SELECT DISTINCT server FROM connections").fetchall():
            if banks.host_of(server):
                netguard.allow_host(banks.host_of(server))


def _release_host(server: str) -> None:
    """A test that didn't end in a saved connection takes its server off the list again."""
    with db.session() as conn:
        used = conn.execute("SELECT 1 FROM connections WHERE server = ?", (server,)).fetchone()
    if not used:
        netguard.disallow_host(banks.host_of(server))


def test_connection(job: Job, bank_code: str, login: str, pin: str, product_id: str, server: str | None = None) -> dict:
    """Log in once, list the accounts and save the connection (credentials encrypted)."""
    with db.session() as conn:
        info = banks.resolve(conn, bank_code, server)
    if not info["server"]:
        info = bank_info(bank_code)  # says what is missing
    bank = info["label"]
    job.add_steps(f"Connecting to {bank}", "Reading your accounts")
    job.step(0)
    netguard.allow_host(banks.host_of(info["server"]))
    try:
        with netguard.purpose(f"{bank} connection test"):
            with session_factory(
                bank_code, login, pin, product_id, None, on_wait=job.wait, server=info["server"], on_tan=job.ask_tan
            ) as s:
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
    except Exception:
        _release_host(info["server"])
        raise

    with db.session() as conn:
        row = _same_login(conn, bank_code, login)
        values = (security.encrypt(login), security.encrypt(pin), product_id, security.encrypt_bytes(state))
        if row:
            conn.execute(
                "UPDATE connections SET login_enc = ?, pin_enc = ?, product_id = ?, state_enc = ?, server = ?, "
                "status = 'ok', last_error = NULL WHERE id = ?",
                (*values, info["server"], row["id"]),
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


def _same_login(conn, bank_code: str, login: str) -> dict | None:
    """The saved connection for this login at this bank: testing again updates it.

    Two logins at one bank (say a joint account) are two connections.
    """
    rows = db.rows(conn.execute("SELECT id, login_enc FROM connections WHERE bank_code = ? ORDER BY id", (bank_code,)))
    for r in rows:
        try:
            if security.decrypt(r["login_enc"]) == login:
                return r
        except Exception as err:  # unreadable after a key change: treat it as another login
            log.debug("Couldn't read a saved login: %s", err)
    return None


def _logged_in(conn, connection_id: int) -> None:
    """The user approved a request in the banking app: the 90 days until the next login start again."""
    conn.execute("UPDATE connections SET bank_login_confirmed_at = ? WHERE id = ?", (db.now_iso(), connection_id))


def _since(conn, connection: dict, full: bool) -> dt.date:
    days = HISTORY_DAYS - 1
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
        info = banks.resolve(conn, c["bank_code"])
    bank = info["label"] if info["source"] == "known" else c["bank_name"]
    login, pin = security.decrypt(c["login_enc"]), security.decrypt(c["pin_enc"])
    state = security.decrypt_bytes(c["state_enc"])
    new_ids: list[int] = []
    counts = {"transactions": 0, "holdings": 0}
    approved = False
    try:
        with netguard.purpose(f"{bank} sync"):
            job.step(step_offset + 0)
            with session_factory(
                c["bank_code"], login, pin, c["product_id"], state, on_wait=job.wait, server=c["server"], on_tan=job.ask_tan
            ) as s:
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
            "Connecting to your bank",
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
    fx.after_change()
    return totals


def _csv_kind(parsed: dict) -> str:
    """Girokonto or Extra-Konto: by the account name, else by what was booked (card payments, salary)."""
    name = (parsed["account_name"] or "").lower()
    if name.startswith(("extra", "tagesgeld", "spar")):
        return "savings"
    if name.startswith(("kreditkarte", "visa", "mastercard")):
        return "credit_card"
    if name:
        return "checking"
    texts = {(r["booking_text"] or "").lower() for r in parsed["rows"]}
    cards = any((r["counterparty"] or "").upper().startswith("VISA ") for r in parsed["rows"])
    if cards or texts & {"lastschrift", "gehalt/rente", "lohn/gehalt"}:
        return "checking"
    return "savings" if texts and texts <= {"zinsgutschrift", "gutschrift", "überweisung", "abschluss"} else "checking"


def _csv_account(conn, parsed: dict) -> int | None:
    """The account a CSV file belongs to: by IBAN, else the account of its kind and currency that it shares
    bookings with, else for a German bank's export the only account of its kind."""
    if parsed["iban"]:
        row = db.one(conn.execute("SELECT id FROM accounts WHERE REPLACE(iban, ' ', '') = ?", (parsed["iban"],)))
        if row:
            return row["id"]
        # An account the bank sync knows under this IBAN is found above; one imported from a file
        # without IBAN before is the same account when it is the only one of its kind.
        candidates = conn.execute(
            "SELECT id FROM accounts WHERE kind = ? AND currency = ? AND manual = 0 AND (iban IS NULL OR iban = '')",
            (_csv_kind(parsed), parsed["currency"]),
        ).fetchall()
    else:
        candidates = conn.execute(
            "SELECT id FROM accounts WHERE kind = ? AND currency = ? AND manual = 0", (_csv_kind(parsed), parsed["currency"])
        ).fetchall()
    ids = [r["id"] for r in candidates]
    shared = [i for i in ids if _shares_bookings(conn, i, parsed)]
    if len(shared) == 1:
        return shared[0]
    # A Chase or Revolut file next to a Girokonto is another account; a German bank's export without
    # IBAN belongs to the only account of its kind, the way Groschen has always read them.
    return ids[0] if len(ids) == 1 and parsed.get("german") else None


def _shares_bookings(conn, account_id: int, parsed: dict) -> bool:
    have = {
        (r[0], round(r[1], 2))
        for r in conn.execute(
            "SELECT date, COALESCE(orig_amount, amount) FROM transactions WHERE account_id = ?", (account_id,)
        )
    }
    return any((r["date"], round(r["amount"], 2)) in have for r in parsed["rows"])


def _default_name(kind: str) -> str:
    """A name for an account from a file that doesn't name it, in the user's language."""
    return i18n.t({"savings": "Savings account", "credit_card": "Credit card"}.get(kind, "Checking account"))


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


def _saved_mapping(conn, raw: bytes) -> dict | None:
    try:
        sig = csv_import.preview(raw)["signature"]
    except UserFacingError:
        return None
    row = conn.execute("SELECT mapping FROM csv_mappings WHERE signature = ?", (sig,)).fetchone()
    return json.loads(row[0]) if row else None


def save_mapping(conn, raw: bytes, mapping: dict) -> dict:
    """Keep the columns the user picked for this kind of file, so the next one imports by itself."""
    info = csv_import.preview(raw)
    clean: dict = {"delimiter": info["delimiter"], "header_row": info["header_row"]}
    for key in csv_import.MAPPABLE:
        v = mapping.get(key)
        if isinstance(v, int) and not isinstance(v, bool) and 0 <= v < info["width"]:
            clean[key] = v
    code = mapping.get("currency_code")
    if isinstance(code, str) and code.upper() in regions.CURRENCIES:
        clean["currency_code"] = code.upper()
    conn.execute(
        "INSERT INTO csv_mappings (signature, mapping, created_at) VALUES (?, ?, ?) "
        "ON CONFLICT(signature) DO UPDATE SET mapping = excluded.mapping, created_at = excluded.created_at",
        (info["signature"], json.dumps(clean), db.now_iso()),
    )
    return clean


def _parse_csv(conn, raw: bytes, filename: str | None, account_id: int | None, mapping: dict | None) -> dict:
    """Read a bank file: by itself, else with the columns the user picked for this kind of file before."""
    home = fx.home(conn)
    default = home
    if account_id is not None:
        default = conn.execute("SELECT currency FROM accounts WHERE id = ?", (account_id,)).fetchone()[0] or home
    month_first = regions.month_first(settings.get(conn, "country"))
    options = {"default_currency": default, "month_first": month_first}
    if mapping:
        return csv_import.parse(raw, filename, mapping=save_mapping(conn, raw, mapping), **options)
    try:
        return csv_import.parse(raw, filename, **options)
    except csv_import.NeedsMapping:
        saved = _saved_mapping(conn, raw)
        if not saved:
            raise
        return csv_import.parse(raw, filename, mapping=saved, **options)


def import_csv(
    job: Job, raw: bytes, account_id: int | None = None, filename: str | None = None, mapping: dict | None = None
) -> dict:
    with db.session() as conn:
        parsed = _parse_csv(conn, raw, filename, account_id, mapping)
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
                    "name": parsed["account_name"] or _default_name(kind),
                    "iban": parsed["iban"],
                    "account_number": None,
                    "bic": None,
                    "blz": banks.blz_from(parsed["iban"] or ""),
                    "currency": parsed["currency"],
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
    fx.after_change()
    return {
        "account_id": account_id,
        "account_name": name,
        "imported": len(new_ids),
        "skipped": skipped + (len(rows) - len(new_ids)),
        "first": min(dates) if dates else None,
        "last": max(dates) if dates else None,
    }


def import_prices(raw: bytes) -> dict:
    prices = csv_import.parse_prices(raw)
    with db.session() as conn:
        for isin, date, price in prices:
            conn.execute(
                "INSERT INTO prices (isin, date, price) VALUES (?, ?, ?) "
                "ON CONFLICT(isin, date) DO UPDATE SET price = excluded.price",
                (isin, date, price),
            )
    isins = sorted({p[0] for p in prices})
    return {"imported": len(prices), "isins": isins, "first": min(p[1] for p in prices), "last": max(p[1] for p in prices)}
