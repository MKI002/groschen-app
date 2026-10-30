"""Shared helpers for the dashboard numbers."""

import calendar
import datetime as dt

from .. import db, i18n

UNCATEGORIZED = {"id": None, "name": "Uncategorized", "grp": "Uncategorized", "kind": None, "color": "muted"}


def month_key(date: str) -> str:
    return date[:7]


def months_between(start: str, end: str) -> list[str]:
    y, m = int(start[:4]), int(start[5:7])
    ey, em = int(end[:4]), int(end[5:7])
    out = []
    while (y, m) <= (ey, em):
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return out


def about_a_month(start: str, end: str) -> bool:
    """A period like the last 30 days: it may touch two calendar months but averages as one."""
    return (dt.date.fromisoformat(end) - dt.date.fromisoformat(start)).days < 45


def month_end(key: str) -> str:
    y, m = int(key[:4]), int(key[5:7])
    return f"{key}-{calendar.monthrange(y, m)[1]:02d}"


def resolve_range(
    preset: str | None,
    anchor: str | None = None,
    start: str | None = None,
    end: str | None = None,
    today: dt.date | None = None,
) -> tuple[str, str, str]:
    """Turn a period preset into (start, end, label). ``anchor`` shifts month/year presets."""
    today = today or dt.date.today()
    if start and end:
        return start, end, f"{start} – {end}"
    preset = preset or "ytd"
    if preset == "month":
        a = dt.date.fromisoformat(anchor) if anchor else today
        s = a.replace(day=1)
        e = s.replace(day=calendar.monthrange(s.year, s.month)[1])
        return s.isoformat(), min(e, today).isoformat(), f"{i18n.month_name(s.month)} {s.year}"
    if preset == "year":
        y = int(anchor[:4]) if anchor else today.year
        e = dt.date(y, 12, 31)
        return f"{y}-01-01", min(e, today).isoformat(), str(y)
    if preset == "last30":
        return (today - dt.timedelta(days=29)).isoformat(), today.isoformat(), i18n.t("Last 30 days")
    if preset == "last12":
        s = (today.replace(day=1) - dt.timedelta(days=334)).replace(day=1)
        return s.isoformat(), today.isoformat(), i18n.t("Last 12 months")
    if preset == "all":
        return "1900-01-01", today.isoformat(), i18n.t("All time")
    # year to date
    return (
        f"{today.year}-01-01",
        today.isoformat(),
        f"{i18n.month_name(1, short=True)} – {i18n.month_name(today.month, short=True)} {today.year}",
    )


def categories(conn) -> dict:
    return {c["id"]: c for c in db.rows(conn.execute("SELECT id, name, grp, kind, color FROM categories"))}


def load_transactions(conn, start: str, end: str) -> list[dict]:
    return db.rows(
        conn.execute(
            "SELECT t.id, t.date, t.amount, t.counterparty, t.counterparty_iban, t.purpose, t.booking_text, t.category_id, "
            "t.cat_source, t.account_id, "
            "a.kind AS account_kind FROM transactions t JOIN accounts a ON a.id = t.account_id "
            "WHERE t.date >= ? AND t.date <= ? AND a.enabled = 1 ORDER BY t.date",
            (start, end),
        )
    )


def classify_flow(tx: dict, cats: dict) -> tuple[str, dict]:
    """Return ("income" | "spending" | "transfer", category) for a transaction."""
    cat = cats.get(tx["category_id"]) or UNCATEGORIZED
    kind = cat.get("kind")
    # Money put into investments is moved, not spent, even when its category says otherwise.
    if kind == "transfer" or tx.get("invest"):
        return "transfer", cat
    if kind == "income":
        return "income", cat
    # Money back for a payment counts against it, also when the payment has no category yet.
    if kind == "expense" or tx.get("cat_source") == "refund":
        return "spending", cat
    return ("income" if tx["amount"] > 0 else "spending"), cat


def data_range(conn) -> tuple[str | None, str | None]:
    row = conn.execute("SELECT MIN(date), MAX(date) FROM transactions").fetchone()
    return row[0], row[1]
