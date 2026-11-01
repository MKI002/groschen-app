"""SQLite storage.

One file in the data folder holds everything. Each request or job opens its own
short-lived connection; WAL mode lets the web UI read while a sync writes.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

from . import config

SCHEMA_VERSION = 1

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    token_hash TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS passkeys (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    credential_id TEXT UNIQUE NOT NULL,
    public_key BLOB NOT NULL,
    sign_count INTEGER NOT NULL DEFAULT 0,
    rp_id TEXT NOT NULL,
    name TEXT NOT NULL,
    transports TEXT,
    created_at TEXT NOT NULL,
    last_used_at TEXT
);

CREATE TABLE IF NOT EXISTS login_events (
    id INTEGER PRIMARY KEY,
    at TEXT NOT NULL,
    username TEXT,
    method TEXT NOT NULL,
    ok INTEGER NOT NULL,
    ip TEXT,
    agent TEXT
);

CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS connections (
    id INTEGER PRIMARY KEY,
    bank_code TEXT NOT NULL,
    bank_name TEXT NOT NULL,
    server TEXT NOT NULL,
    login_enc BLOB,
    pin_enc BLOB,
    product_id TEXT,
    state_enc BLOB,
    status TEXT NOT NULL DEFAULT 'new',
    last_sync_at TEXT,
    last_error TEXT,
    bank_login_confirmed_at TEXT,
    created_at TEXT NOT NULL
);

-- The FinTS institute list, when the user imported it: every bank's FinTS address.
CREATE TABLE IF NOT EXISTS bank_directory (
    blz TEXT NOT NULL,
    name TEXT NOT NULL,
    server TEXT,
    PRIMARY KEY (blz, name)
);

CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY,
    connection_id INTEGER REFERENCES connections(id) ON DELETE SET NULL,
    kind TEXT NOT NULL,
    name TEXT NOT NULL,
    iban TEXT,
    account_number TEXT,
    subaccount TEXT,
    bic TEXT,
    blz TEXT,
    currency TEXT NOT NULL DEFAULT 'EUR',
    balance REAL NOT NULL DEFAULT 0,  -- in the home currency (see fx.py)
    balance_date TEXT,
    enabled INTEGER NOT NULL DEFAULT 1,
    manual INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    orig_balance REAL,  -- the balance in the account's own currency, when that isn't the home currency
    fx_ok INTEGER NOT NULL DEFAULT 1  -- 0 while there's no exchange rate for it: then it isn't counted
);

CREATE TABLE IF NOT EXISTS balance_history (
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    date TEXT NOT NULL,
    balance REAL NOT NULL,
    orig_balance REAL,
    PRIMARY KEY (account_id, date)
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    grp TEXT NOT NULL,
    kind TEXT NOT NULL DEFAULT 'expense',
    color TEXT,
    sort INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    date TEXT NOT NULL,
    value_date TEXT,
    amount REAL NOT NULL,
    currency TEXT NOT NULL DEFAULT 'EUR',
    counterparty TEXT,
    counterparty_iban TEXT,
    purpose TEXT,
    booking_text TEXT,
    fingerprint TEXT NOT NULL,
    source TEXT NOT NULL,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    cat_source TEXT,
    confidence REAL,
    needs_review INTEGER NOT NULL DEFAULT 0,
    note TEXT,
    created_at TEXT NOT NULL,
    -- A booking in another currency than the home currency: amount is converted, orig_amount is
    -- what the bank booked (in currency), fx_rate what one unit of it was worth. See fx.py.
    orig_amount REAL,
    fx_rate REAL,
    UNIQUE (account_id, fingerprint)
);
CREATE INDEX IF NOT EXISTS tx_date ON transactions(date);
CREATE INDEX IF NOT EXISTS tx_account_date ON transactions(account_id, date);

CREATE TABLE IF NOT EXISTS rules (
    id INTEGER PRIMARY KEY,
    field TEXT NOT NULL,
    op TEXT NOT NULL,
    value TEXT NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS merchant_memory (
    key TEXT PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    hits INTEGER NOT NULL DEFAULT 1,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS subscription_marks (
    key TEXT PRIMARY KEY,
    state TEXT NOT NULL CHECK (state IN ('yes', 'no')),
    updated_at TEXT NOT NULL
);
-- Payments the user took out of the Investments page with one click ("not an investment in this depot").
CREATE TABLE IF NOT EXISTS invest_skips (
    tx_id INTEGER PRIMARY KEY REFERENCES transactions(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL
);

-- Where the user said a saved amount really went (Overview, "Where your savings went").
-- One row per booking; the counterparty rows carry the choice over to that counterparty's later bookings.
CREATE TABLE IF NOT EXISTS saving_dest (
    tx_id INTEGER PRIMARY KEY REFERENCES transactions(id) ON DELETE CASCADE,
    dest TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS saving_dest_cp (
    key TEXT PRIMARY KEY,
    dest TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- Money that came back for an earlier payment (a shop's refund, a friend paying back) and that payment.
-- Several refunds can belong to one payment. "auto" links Groschen redoes; "user" links stay.
CREATE TABLE IF NOT EXISTS refund_links (
    refund_id INTEGER PRIMARY KEY REFERENCES transactions(id) ON DELETE CASCADE,
    purchase_id INTEGER NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    source TEXT NOT NULL CHECK (source IN ('auto', 'user')),
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS refund_purchase ON refund_links(purchase_id);

-- Money the user said is no refund (one tap on a wrong link). It isn't linked again, and its payee's
-- money (key) is then only linked when the whole amount comes back.
CREATE TABLE IF NOT EXISTS refund_rejects (
    refund_id INTEGER PRIMARY KEY REFERENCES transactions(id) ON DELETE CASCADE,
    key TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS examples (
    id INTEGER PRIMARY KEY,
    text TEXT NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    UNIQUE (text, category_id)
);

CREATE TABLE IF NOT EXISTS holdings (
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    isin TEXT NOT NULL,
    name TEXT,
    pieces REAL NOT NULL,
    price REAL,
    price_date TEXT,
    value REAL NOT NULL,
    acquisition_price REAL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (account_id, isin)
);

CREATE TABLE IF NOT EXISTS holding_history (
    date TEXT NOT NULL,
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    isin TEXT NOT NULL,
    pieces REAL NOT NULL,
    price REAL,
    value REAL NOT NULL,
    PRIMARY KEY (date, account_id, isin)
);

CREATE TABLE IF NOT EXISTS prices (
    isin TEXT NOT NULL,
    date TEXT NOT NULL,
    price REAL NOT NULL,
    PRIMARY KEY (isin, date)
);

-- Online price history (opt-in): when each ETF was last fetched and what came back.
CREATE TABLE IF NOT EXISTS market_meta (
    isin TEXT PRIMARY KEY,
    fetched_at TEXT,
    first_date TEXT,
    last_date TEXT,
    points INTEGER,
    error TEXT,
    facts TEXT,  -- JSON from the fund's profile page: payout policy, TER, size, ...
    facts_at TEXT
);

CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    icon TEXT NOT NULL DEFAULT 'tag',
    category_ids TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS dismissed_alerts (
    key TEXT PRIMARY KEY,
    dismissed_at TEXT NOT NULL
);

-- Daily reference rates of the European Central Bank (opt-in, fx.py): units of currency per euro.
CREATE TABLE IF NOT EXISTS fx_rates (
    currency TEXT NOT NULL,
    date TEXT NOT NULL,
    rate REAL NOT NULL,
    PRIMARY KEY (currency, date)
);

-- Columns the user picked for a bank file Groschen couldn't read alone, by the file's header.
CREATE TABLE IF NOT EXISTS csv_mappings (
    signature TEXT PRIMARY KEY,
    mapping TEXT NOT NULL,  -- JSON: column numbers for date, amount, ...
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS netlog (
    id INTEGER PRIMARY KEY,
    ts TEXT NOT NULL,
    host TEXT NOT NULL,
    purpose TEXT,
    allowed INTEGER NOT NULL
);
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def connect() -> sqlite3.Connection:
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH, timeout=15, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 15000")
    return conn


@contextmanager
def session():
    """Open a connection, commit on success, roll back on error."""
    conn = connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# Columns added after a table first shipped. CREATE TABLE IF NOT EXISTS leaves existing
# tables alone, so these are added to databases from older versions on start.
ADDED_COLUMNS = {
    "sessions": {"last_seen": "TEXT", "ip": "TEXT", "agent": "TEXT", "method": "TEXT"},
    "transactions": {"orig_amount": "REAL", "fx_rate": "REAL"},
    "accounts": {"orig_balance": "REAL", "fx_ok": "INTEGER NOT NULL DEFAULT 1"},
    "balance_history": {"orig_balance": "REAL"},
}


def add_columns(conn) -> None:
    for table, columns in ADDED_COLUMNS.items():
        have = {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}
        for name, kind in columns.items():
            if name not in have:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {kind}")


def init() -> None:
    with session() as conn:
        conn.execute("PRAGMA journal_mode = WAL")
        conn.executescript(SCHEMA)
        add_columns(conn)
        conn.execute(
            "INSERT OR IGNORE INTO meta (key, value) VALUES ('schema_version', ?)",
            (str(SCHEMA_VERSION),),
        )
        from .categorize.seed import KNOWLEDGE, seed_categories, upgrade_categories

        seed_categories(conn)
        from .categorize import engine

        engine.unspread_income(conn)
        if conn.execute("SELECT 1 FROM meta WHERE key = 'refund_links'").fetchone() is None:
            # Refunds found before they were linked to their payment get their link once.
            engine.match_refunds(conn)
            conn.execute("INSERT INTO meta (key, value) VALUES ('refund_links', '1')")
        known = conn.execute("SELECT value FROM meta WHERE key = 'knowledge'").fetchone()
        stale = known is None or int(known[0]) < KNOWLEDGE
        if upgrade_categories(conn) or stale:
            # New built-in categories or merchants: sort the existing bookings again (never the user's own choices).
            engine.reapply_quick(conn)
        if stale:
            conn.execute(
                "INSERT INTO meta (key, value) VALUES ('knowledge', ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (str(KNOWLEDGE),),
            )


def rows(cur) -> list[dict]:
    return [dict(r) for r in cur.fetchall()]


def one(cur) -> dict | None:
    r = cur.fetchone()
    return dict(r) if r else None
