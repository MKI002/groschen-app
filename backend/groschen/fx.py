"""Money in other currencies, shown in the home currency.

Every total in Groschen is in one currency, the home currency picked on first run. A booking
in another currency keeps what the bank booked (``orig_amount`` in ``currency``) and gets its
``amount`` converted at the rate of its day, so all the sums, charts and hints work with it as
with any other booking. Balances are converted at the latest rate.

The rates are the European Central Bank's daily reference rates (opt-in, "Exchange rates" in
Settings). The request is a fixed address with no question in it: no currency, no amount,
nothing about the user. The rates server is only let through the network guard while the
setting is on, and every lookup shows up in the connection log. The rates are only fetched
while some money here is in another currency than the home currency.

Without a rate (setting off, or a currency the ECB doesn't publish), a booking keeps its own
amount and its account is not counted (``fx_ok = 0``): its bookings and balance stay out of
every total until a rate is there. A wrong total would be worse than a missing account.
"""

import bisect
import datetime as dt
import io
import logging
import re
import urllib.request
import zipfile

from . import db, jobs, netguard, regions, settings
from .jobs import Job, UserFacingError

log = logging.getLogger("groschen.fx")

HOST = "www.ecb.europa.eu"
PURPOSE = "Exchange rates"
HISTORY_URL = f"https://{HOST}/stats/eurofxref/eurofxref-hist.zip"
RECENT_URL = f"https://{HOST}/stats/eurofxref/eurofxref-hist-90d.xml"
TIMEOUT = 30
MAX_BYTES = 16 * 1024 * 1024
CODE = re.compile(r"^[A-Z]{3}$")


def home(conn) -> str:
    return settings.get(conn, "currency") or "EUR"


def enabled(conn) -> bool:
    return bool(settings.get(conn, "online_rates"))


def apply_setting(conn) -> None:
    """Let the rates server through the network guard only while the setting is on."""
    if enabled(conn):
        netguard.allow_host(HOST)
    else:
        netguard.disallow_host(HOST)


# --- reading the ECB's files -------------------------------------------------------------


def parse_history_csv(text: str) -> list[tuple[str, str, float]]:
    """The full history: "Date,USD,JPY,...," and one row per day, newest first. "N/A" where a currency had none."""
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    header = [c.strip() for c in lines[0].split(",")]
    out = []
    for line in lines[1:]:
        cells = [c.strip() for c in line.split(",")]
        try:
            date = dt.date.fromisoformat(cells[0]).isoformat()
        except ValueError:
            continue
        for code, cell in zip(header[1:], cells[1:]):
            if not CODE.match(code):
                continue
            try:
                rate = float(cell)
            except ValueError:
                continue
            if rate > 0:
                out.append((code, date, rate))
    return out


def parse_history_zip(payload: bytes) -> list[tuple[str, str, float]]:
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        name = next((n for n in z.namelist() if n.lower().endswith(".csv")), None)
        if not name:
            raise ValueError("no CSV in the rates file")
        info = z.getinfo(name)
        if info.file_size > MAX_BYTES:
            raise ValueError("rates file too large")
        return parse_history_csv(z.read(name).decode("utf-8", errors="replace"))


_DAY = re.compile(r"""<Cube\s+time=["'](\d{4}-\d{2}-\d{2})["']\s*>(.*?)</Cube>""", re.S)
_RATE = re.compile(r"""<Cube\s+currency=["']([A-Z]{3})["']\s+rate=["']([0-9.]+)["']""")


def parse_recent_xml(payload: bytes) -> list[tuple[str, str, float]]:
    """The last 90 days: <Cube time="2026-10-30"><Cube currency="USD" rate="1.0812"/>...</Cube>."""
    text = payload.decode("utf-8", errors="replace")
    out = []
    for day in _DAY.finditer(text):
        for code, rate in _RATE.findall(day.group(2)):
            try:
                value = float(rate)
            except ValueError:
                continue
            if value > 0:
                out.append((code, day.group(1), value))
    return out


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Groschen"})  # noqa: S310 - fixed https address
    with netguard.purpose(PURPOSE):
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:  # noqa: S310 - fixed https host, allowlisted
            payload = resp.read(MAX_BYTES + 1)
    if len(payload) > MAX_BYTES:
        raise ValueError("answer too large")
    return payload


def fetch_history() -> list[tuple[str, str, float]]:
    return parse_history_zip(_get(HISTORY_URL))


def fetch_recent() -> list[tuple[str, str, float]]:
    return parse_recent_xml(_get(RECENT_URL))


# Tests swap these for canned answers.
history_fetcher = fetch_history
recent_fetcher = fetch_recent


def store(conn, rows: list[tuple[str, str, float]]) -> int:
    before = conn.total_changes
    conn.executemany(
        "INSERT INTO fx_rates (currency, date, rate) VALUES (?, ?, ?) "
        "ON CONFLICT(currency, date) DO UPDATE SET rate = excluded.rate",
        rows,
    )
    return conn.total_changes - before


# --- what is needed ----------------------------------------------------------------------


def foreign(conn) -> list[str]:
    """Currencies of money kept here that aren't the home currency."""
    h = home(conn)
    rows = conn.execute("SELECT DISTINCT currency FROM transactions UNION SELECT DISTINCT currency FROM accounts").fetchall()
    return sorted({r[0] for r in rows if r[0] and r[0] != h})


def needed(conn) -> list[str]:
    """Currencies a rate is needed for. All rates are per euro, so a home currency other than the euro needs its own."""
    other = foreign(conn)
    if not other:
        return []
    return sorted({c for c in [*other, home(conn)] if c != "EUR"})


class Rates:
    """Rates per euro by day. A day without one (weekend, holiday) takes the last one before it."""

    def __init__(self, conn, currencies: list[str]):
        self.days: dict[str, list[str]] = {}
        self.values: dict[str, list[float]] = {}
        for code in currencies:
            if code == "EUR":
                continue
            rows = conn.execute("SELECT date, rate FROM fx_rates WHERE currency = ? ORDER BY date", (code,)).fetchall()
            if rows:
                self.days[code] = [r[0] for r in rows]
                self.values[code] = [r[1] for r in rows]

    def per_euro(self, code: str, date: str) -> float | None:
        if code == "EUR":
            return 1.0
        days = self.days.get(code)
        if not days:
            return None
        i = bisect.bisect_right(days, date) - 1
        # Before the first known day: the first rate is the closest there is.
        return self.values[code][max(i, 0)]

    def factor(self, code: str, to: str, date: str) -> float | None:
        """What one unit of ``code`` is worth in ``to`` on ``date``."""
        if code == to:
            return 1.0
        a, b = self.per_euro(code, date), self.per_euro(to, date)
        if a is None or b is None:
            return None
        return b / a

    def latest(self, code: str) -> str | None:
        days = self.days.get(code)
        return days[-1] if days else None


# --- converting --------------------------------------------------------------------------


def _split(conn, table: str, value: str, orig: str, currency_sql: str, h: str) -> None:
    """Keep the original value of money in another currency; give money in the home currency its own back."""
    conn.execute(
        f"UPDATE {table} SET {value} = {orig}, {orig} = NULL WHERE {orig} IS NOT NULL AND {currency_sql} = ?",  # noqa: S608
        (h,),
    )
    conn.execute(
        f"UPDATE {table} SET {orig} = {value} WHERE {orig} IS NULL AND {currency_sql} != ?",  # noqa: S608
        (h,),
    )


def apply(conn) -> dict:
    """Convert everything in another currency into the home currency. Cheap when there's nothing to do."""
    h = home(conn)
    conn.execute("UPDATE transactions SET fx_rate = NULL WHERE fx_rate IS NOT NULL AND currency = ?", (h,))
    _split(conn, "transactions", "amount", "orig_amount", "currency", h)
    _split(conn, "accounts", "balance", "orig_balance", "currency", h)
    acc_currency = "(SELECT a.currency FROM accounts a WHERE a.id = balance_history.account_id)"
    _split(conn, "balance_history", "balance", "orig_balance", acc_currency, h)

    codes = foreign(conn)
    rates = Rates(conn, [*codes, h])
    missing: set[str] = set()
    unconverted_accounts: set[int] = set()

    updates = []
    for r in conn.execute(
        "SELECT id, account_id, date, currency, amount, orig_amount, fx_rate FROM transactions WHERE currency != ?", (h,)
    ):
        f = rates.factor(r["currency"], h, r["date"])
        if f is None:
            missing.add(r["currency"])
            unconverted_accounts.add(r["account_id"])
            amount, rate = r["orig_amount"], None
        else:
            amount, rate = round(r["orig_amount"] * f, 2), round(f, 8)
        if amount != r["amount"] or rate != r["fx_rate"]:
            updates.append((amount, rate, r["id"]))
    conn.executemany("UPDATE transactions SET amount = ?, fx_rate = ? WHERE id = ?", updates)

    today = "9999-12-31"  # balances count at the latest rate
    for a in db.rows(conn.execute("SELECT id, currency, balance, orig_balance FROM accounts WHERE currency != ?", (h,))):
        f = rates.factor(a["currency"], h, today)
        if f is None:
            missing.add(a["currency"])
            unconverted_accounts.add(a["id"])
            continue
        balance = round((a["orig_balance"] or 0) * f, 2)
        if balance != a["balance"]:
            conn.execute("UPDATE accounts SET balance = ? WHERE id = ?", (balance, a["id"]))
    for b in db.rows(
        conn.execute(
            "SELECT b.account_id, b.date, b.balance, b.orig_balance, a.currency FROM balance_history b "
            "JOIN accounts a ON a.id = b.account_id WHERE a.currency != ?",
            (h,),
        )
    ):
        f = rates.factor(b["currency"], h, b["date"])
        balance = round((b["orig_balance"] or 0) * f, 2) if f is not None else b["orig_balance"]
        if balance != b["balance"]:
            conn.execute(
                "UPDATE balance_history SET balance = ? WHERE account_id = ? AND date = ?",
                (balance, b["account_id"], b["date"]),
            )

    conn.execute("UPDATE accounts SET fx_ok = 1 WHERE fx_ok = 0")
    if unconverted_accounts:
        conn.execute(
            f"UPDATE accounts SET fx_ok = 0 WHERE id IN ({','.join('?' * len(unconverted_accounts))})",  # noqa: S608
            sorted(unconverted_accounts),
        )
    return {"missing": sorted(missing), "uncounted": len(unconverted_accounts)}


def fetched_lately(conn, hours: float = 8) -> bool:
    """Fetched in the last 8 hours: the ECB publishes once a day, in the afternoon."""
    row = conn.execute("SELECT value FROM meta WHERE key = 'fx_fetched_at'").fetchone()
    try:
        return bool(row) and dt.datetime.fromisoformat(row[0]) > dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours)
    except ValueError:
        return False


def _note(conn, error: str | None) -> None:
    for key, value in (("fx_fetched_at", db.now_iso()), ("fx_error", error or "")):
        conn.execute(
            "INSERT INTO meta (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value", (key, value)
        )


def refresh(job: Job | None = None) -> dict:
    """Fetch the rates: the whole history the first time, then the last 90 days. Then convert."""
    with db.session() as conn:
        if not enabled(conn):
            raise UserFacingError("Exchange rates are turned off in Settings.")
        apply_setting(conn)
        have = conn.execute("SELECT COUNT(*) FROM fx_rates").fetchone()[0]
        want = needed(conn)
        known = {r[0] for r in conn.execute("SELECT DISTINCT currency FROM fx_rates")}
    if job:
        job.add_steps("Loading exchange rates", "Converting")
        job.step(0)
    # A currency first seen now may be older than the last 90 days: then the whole history again.
    full = not have or any(c not in known for c in want)
    error = None
    rows: list[tuple[str, str, float]] = []
    try:
        rows = history_fetcher() if full else recent_fetcher()
    except Exception as exc:  # network down, blocked, odd answer: keep the rates we have
        error = str(exc)[:200] or exc.__class__.__name__
        log.info("Exchange rates: %s", error)
    if job:
        job.step(1)
    with db.session() as conn:
        added = store(conn, rows) if rows else 0
        _note(conn, error if error or rows else "no rates")
        result = apply(conn)
    if error and not added:
        raise UserFacingError("Couldn't load the exchange rates. Groschen tries again tomorrow.")
    return {"added": added, **result}


def after_change() -> None:
    """Convert new bookings; fetch rates when some are missing or old. Call after a sync, an import or a settings change."""
    with db.session() as conn:
        result = apply(conn)
        # A currency without any rate yet (a new account) is fetched at once. The ECB doesn't have
        # every currency, so a missing one is asked for again only after a few minutes.
        new = [c for c in result["missing"] if c in regions.CURRENCIES]
        start = enabled(conn) and needed(conn) and (not fetched_lately(conn) or (new and not fetched_lately(conn, 0.1)))
    if start and not jobs.running("rates"):
        jobs.start("rates", refresh)


def status(conn) -> dict:
    h = home(conn)
    codes = foreign(conn)
    rates = Rates(conn, [*codes, h])
    meta = dict(conn.execute("SELECT key, value FROM meta WHERE key IN ('fx_fetched_at', 'fx_error')").fetchall())
    latest = []
    for code in codes:
        f = rates.factor(code, h, "9999-12-31")
        day = rates.latest(code) if code != "EUR" else rates.latest(h)
        latest.append({"currency": code, "rate": round(f, 6) if f else None, "date": day})
    uncounted = db.rows(conn.execute("SELECT id, name, currency FROM accounts WHERE fx_ok = 0 AND enabled = 1 ORDER BY id"))
    return {
        "enabled": enabled(conn),
        "host": HOST,
        "home": h,
        "foreign": codes,
        "rates": latest,
        "uncounted": uncounted,
        "last": meta.get("fx_fetched_at"),
        "error": meta.get("fx_error") or None,
    }
