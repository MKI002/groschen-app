"""Online price history for the ETFs in the depot (opt-in, off until turned on in Settings).

Banks only send today's price at each sync. With "Online ETF prices" on, Groschen asks
justETF for the daily price history of each ETF it knows. The request carries nothing
but the ISIN in the address: no account, no key, no amounts, no personal data. The
server is only let through the network guard while the setting is on, and every
lookup shows up in the connection log like the bank's.

Prices from the bank or from an imported file are never overwritten; online prices
only fill the days in between.

Once a week the fund's public profile page on the same site is read too, for the facts
that don't change often: whether it pays out or reinvests and how often, its costs (TER),
size, replication, currency and domicile.
"""

import datetime as dt
import html
import json
import logging
import re
import urllib.error
import urllib.parse
import urllib.request

from . import db, netguard, settings
from .jobs import Job, UserFacingError

log = logging.getLogger("groschen.market")

HOST = "www.justetf.com"
PURPOSE = "ETF prices"
ISIN_RE = re.compile(r"^[A-Z]{2}[A-Z0-9]{9}\d$")
TIMEOUT = 20
MAX_BYTES = 8 * 1024 * 1024


def enabled(conn) -> bool:
    return bool(settings.get(conn, "online_prices"))


def apply_setting(conn) -> None:
    """Let the price server through the network guard only while the setting is on."""
    if enabled(conn):
        netguard.allow_host(HOST)
    else:
        netguard.disallow_host(HOST)


def known_isins(conn) -> list[str]:
    rows = conn.execute(
        "SELECT isin FROM holdings UNION SELECT isin FROM holding_history UNION SELECT isin FROM prices"
    ).fetchall()
    return sorted({r[0] for r in rows if r[0] and ISIN_RE.match(r[0])})


def _url(isin: str, date_from: str | None) -> str:
    query = {
        "locale": "en",
        "currency": "EUR",
        "valuesType": "MARKET_VALUE",
        "reduceData": "false",
        "includeDividends": "false",
    }
    if date_from:
        query["dateFrom"] = date_from
        query["dateTo"] = dt.date.today().isoformat()
    return f"https://{HOST}/api/etfs/{isin}/performance-chart?{urllib.parse.urlencode(query)}"


def parse(payload: bytes) -> list[tuple[str, float]]:
    """Daily prices from a justETF answer: [(date, price)], weekdays only, sorted."""
    data = json.loads(payload)
    out: dict[str, float] = {}
    for entry in data.get("series") or []:
        try:
            date = str(entry["date"])[:10]
            value = entry["value"]
            price = float(value["raw"] if isinstance(value, dict) else value)
            day = dt.date.fromisoformat(date)
        except (KeyError, TypeError, ValueError):
            continue
        # The series repeats Friday's price over the weekend; those aren't trading days.
        if price > 0 and day.weekday() < 5:
            out[date] = round(price, 4)
    return sorted(out.items())


def fetch(isin: str, date_from: str | None = None) -> list[tuple[str, float]]:
    if not ISIN_RE.match(isin):
        raise ValueError(f"not an ISIN: {isin}")
    return parse(_get(_url(isin, date_from), "application/json"))


def _get(url: str, accept: str) -> bytes:
    headers = {"Accept": accept, "User-Agent": "Mozilla/5.0 (compatible; Groschen)"}
    req = urllib.request.Request(url, headers=headers)  # noqa: S310 - fixed https address
    with netguard.purpose(PURPOSE):
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:  # noqa: S310 - fixed https host, allowlisted
            payload = resp.read(MAX_BYTES + 1)
    if len(payload) > MAX_BYTES:
        raise ValueError("answer too large")
    return payload


FACTS_EVERY = dt.timedelta(days=7)
DOMICILES = "Ireland|Luxembourg|Germany|France|Switzerland|Netherlands|Austria|United Kingdom|Liechtenstein|Sweden"
FREQUENCIES = {
    "monthly": "monthly",
    "bi-monthly": "bimonthly",
    "quarterly": "quarterly",
    "semi annually": "semiannual",
    "semi-annually": "semiannual",
    "annually": "annual",
}


def _text(page: str) -> str:
    """The visible text of a web page on one line: no scripts, no tags, single spaces."""
    page = re.sub(r"(?is)<(script|style|noscript|svg)\b.*?</\1>", " ", page)
    page = re.sub(r"(?s)<[^>]+>", " ", page)
    return re.sub(r"\s+", " ", html.unescape(page)).strip()


def _num(text: str) -> float | None:
    try:
        return float(text.replace(",", ""))
    except ValueError:
        return None


def parse_facts(page: str) -> dict:
    """The key facts table of a justETF profile page (English). Anything not found stays out."""
    text = _text(page)

    def find(pattern: str) -> re.Match | None:
        # A label may carry a short tooltip before its value, hence the little gap allowed.
        return re.search(pattern, text, re.I)

    facts: dict = {}
    if m := find(r"Distribution policy .{0,120}?\b(Distributing|Accumulating)\b"):
        facts["policy"] = m.group(1).lower()
    if m := find(r"Distribution frequency .{0,120}?\b(Monthly|Bi-monthly|Quarterly|Semi[ -]annually|Annually|None)\b"):
        facts["frequency"] = FREQUENCIES.get(m.group(1).lower())
    if m := find(r"Total expense ratio .{0,120}?(\d+(?:\.\d+)?)\s?% p\.a\."):
        facts["ter"] = round(float(m.group(1)) / 100, 6)
    if m := find(r"Fund size .{0,120}?\b(EUR|USD|GBP|CHF) ([\d,]+(?:\.\d+)?) ?(m|bn)\b"):
        size = _num(m.group(2))
        if size is not None:
            facts["size"] = size * (1000 if m.group(3).lower() == "bn" else 1)
            facts["size_currency"] = m.group(1).upper()
    if m := find(r"Replication .{0,120}?\b(Physical|Synthetic)\b(?: \(([A-Za-z -]{3,40})\))?"):
        facts["replication"] = m.group(1).lower()
        if m.group(2):
            facts["replication_detail"] = m.group(2).strip()
    if m := find(r"Fund currency .{0,60}?\b([A-Z]{3})\b"):
        facts["currency"] = m.group(1)
    if m := find(r"Currency risk .{0,60}?\b(Currency unhedged|Currency hedged)\b"):
        facts["hedged"] = m.group(1).lower() == "currency hedged"
    if m := find(rf"Fund domicile .{{0,60}}?\b({DOMICILES})\b"):
        facts["domicile"] = m.group(1)
    if m := find(r"Inception/ ?Listing Date .{0,60}?\b(\d{1,2} [A-Z][a-z]+ \d{4})\b"):
        try:
            facts["inception"] = dt.datetime.strptime(m.group(1), "%d %B %Y").date().isoformat()
        except ValueError:
            pass
    if m := find(r"\bIndex ([^|<>]{3,90}?) Investment focus"):
        facts["index"] = m.group(1).strip(' "')
    if m := find(r"Current dividend yield .{0,60}?(\d+(?:\.\d+)?)\s?%"):
        facts["dividend_yield"] = round(float(m.group(1)) / 100, 6)
    return facts


def fetch_facts(isin: str) -> dict:
    if not ISIN_RE.match(isin):
        raise ValueError(f"not an ISIN: {isin}")
    page = _get(f"https://{HOST}/en/etf-profile.html?isin={isin}", "text/html")
    return parse_facts(page.decode("utf-8", "replace"))


# Swappable for tests.
fetcher = fetch
facts_fetcher = fetch_facts


def store(conn, isin: str, prices: list[tuple[str, float]]) -> int:
    before = conn.total_changes
    conn.executemany("INSERT OR IGNORE INTO prices (isin, date, price) VALUES (?, ?, ?)", [(isin, d, p) for d, p in prices])
    return conn.total_changes - before


def refresh(job: Job | None = None) -> dict:
    """Fetch new prices for every known ETF. Only new days after the last fetch are asked for."""
    with db.session() as conn:
        if not enabled(conn):
            raise UserFacingError("Online ETF prices are turned off in Settings.")
        apply_setting(conn)
        isins = known_isins(conn)
        meta = {r["isin"]: dict(r) for r in conn.execute("SELECT isin, last_date, facts_at FROM market_meta")}
        last = {k: v["last_date"] for k, v in meta.items()}
    if job:
        job.add_steps(*[f"Loading prices for {i}" for i in isins] or ["No ETFs yet"])
    added, failed = 0, []
    for n, isin in enumerate(isins):
        if job:
            job.step(n)
        since = None
        if last.get(isin):
            since = (dt.date.fromisoformat(last[isin]) - dt.timedelta(days=10)).isoformat()
        error = None
        prices: list[tuple[str, float]] = []
        try:
            prices = fetcher(isin, since)
        except urllib.error.HTTPError as exc:
            error = "not found" if exc.code == 404 else f"HTTP {exc.code}"
        except Exception as exc:  # network down, blocked, odd answer: note it and go on
            error = str(exc)[:200] or exc.__class__.__name__
        with db.session() as conn:
            if prices:
                added += store(conn, isin, prices)
            elif not error:
                error = "no prices"
            row = conn.execute("SELECT MIN(date), MAX(date), COUNT(*) FROM prices WHERE isin = ?", (isin,)).fetchone()
            conn.execute(
                "INSERT INTO market_meta (isin, fetched_at, first_date, last_date, points, error) VALUES (?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(isin) DO UPDATE SET fetched_at = excluded.fetched_at, first_date = excluded.first_date, "
                "last_date = CASE WHEN excluded.error IS NULL THEN excluded.last_date ELSE market_meta.last_date END, "
                "points = excluded.points, error = excluded.error",
                (isin, db.now_iso(), row[0], prices[-1][0] if prices else last.get(isin), row[2], error),
            )
        if error:
            failed.append(isin)
            log.info("Online prices for %s: %s", isin, error)
        # Fund facts change rarely: once a week is plenty. A failure here keeps the old facts.
        facts_at = (meta.get(isin) or {}).get("facts_at")
        if error != "not found" and (not facts_at or dt.datetime.fromisoformat(facts_at) < _now() - FACTS_EVERY):
            try:
                facts = facts_fetcher(isin)
            except Exception as exc:  # facts are a bonus; the prices are already stored
                log.info("Fund facts for %s: %s", isin, exc)
                facts = None
            if facts:
                with db.session() as conn:
                    conn.execute(
                        "UPDATE market_meta SET facts = ?, facts_at = ? WHERE isin = ?",
                        (json.dumps(facts), db.now_iso(), isin),
                    )
    return {"isins": len(isins), "added": added, "failed": failed}


def _now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def facts(conn, isin: str) -> dict | None:
    row = conn.execute("SELECT facts, facts_at FROM market_meta WHERE isin = ?", (isin,)).fetchone()
    if not row or not row["facts"]:
        return None
    try:
        return {**json.loads(row["facts"]), "fetched_at": row["facts_at"]}
    except ValueError:
        return None


def status(conn) -> dict:
    rows = db.rows(conn.execute("SELECT isin, fetched_at, first_date, last_date, points, error FROM market_meta"))
    return {
        "enabled": enabled(conn),
        "host": HOST,
        "last": max((r["fetched_at"] for r in rows if r["fetched_at"]), default=None),
        "funds": rows,
    }
