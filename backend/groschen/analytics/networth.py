"""Balances across all accounts and how they developed."""

import datetime as dt

from .. import db, i18n
from . import common, portfolio

ASSET_KINDS = {"checking", "savings", "depot", "manual_asset"}
LIABILITY_KINDS = {"loan", "credit_card", "manual_liability"}


def _account_rows(conn) -> list[dict]:
    return db.rows(
        conn.execute(
            "SELECT a.id, a.name, a.kind, a.iban, a.balance, a.balance_date, a.manual, a.connection_id, a.enabled, "
            "c.bank_name FROM accounts a LEFT JOIN connections c ON c.id = a.connection_id ORDER BY a.manual, a.id"
        )
    )


def overview(conn, today: dt.date | None = None) -> dict:
    today = today or dt.date.today()
    accounts = [a for a in _account_rows(conn) if a["enabled"]]
    for a in accounts:
        a["side"] = "liability" if a["kind"] in LIABILITY_KINDS or a["balance"] < 0 else "asset"
        if a["manual"]:
            a["source"] = i18n.t("Entered by hand")
        elif a["connection_id"]:
            a["source"] = i18n.t("{bank} · synced", bank=(a["bank_name"] or "Bank").split()[0])
        else:
            a["source"] = i18n.t("CSV import")
    assets = round(sum(a["balance"] for a in accounts if a["side"] == "asset"), 2)
    liabilities = round(sum(a["balance"] for a in accounts if a["side"] == "liability"), 2)
    series = history(conn, accounts, today)
    start_of_year = next((p["value"] for p in series if p["month"] == f"{today.year - 1}-12"), None)
    if start_of_year is None and series:
        first_this_year = [p for p in series if p["month"].startswith(str(today.year))]
        start_of_year = first_this_year[0]["value"] if first_this_year else None
    net = round(assets + liabilities, 2)
    return {
        "net_worth": net,
        "assets": assets,
        "liabilities": liabilities,
        "change_this_year": round(net - start_of_year, 2) if start_of_year is not None else None,
        "accounts": accounts,
        "series": series,
    }


def history(conn, accounts: list[dict], today: dt.date, max_months: int = 60) -> list[dict]:
    first = conn.execute(
        "SELECT MIN(d) FROM (SELECT MIN(date) AS d FROM transactions UNION SELECT MIN(date) FROM balance_history "
        "UNION SELECT MIN(date) FROM holding_history)"
    ).fetchone()[0]
    if not first:
        return []
    months = common.months_between(first[:7] + "-01", today.isoformat())[-max_months:]
    depot_values = portfolio.monthly_values(conn, months, today)

    per_account_first = {
        r["account_id"]: r["d"]
        for r in conn.execute("SELECT account_id, MIN(date) AS d FROM transactions GROUP BY account_id")
    }
    after_sums: dict[int, list[tuple[str, float]]] = {}
    for r in conn.execute("SELECT account_id, date, amount FROM transactions ORDER BY date"):
        after_sums.setdefault(r["account_id"], []).append((r["date"], r["amount"]))

    out = []
    for m in months:
        end = common.month_end(m)
        if end > today.isoformat():
            end = today.isoformat()
        total, known = 0.0, False
        for a in accounts:
            if a["kind"] == "depot":
                v = depot_values.get(m, {}).get(a["id"])
                if v is not None:
                    total += v
                    known = True
                continue
            if a["manual"]:
                total += a["balance"]
                known = True
                continue
            first_tx = per_account_first.get(a["id"])
            snap = conn.execute(
                "SELECT balance FROM balance_history WHERE account_id = ? AND date <= ? ORDER BY date DESC LIMIT 1",
                (a["id"], end),
            ).fetchone()
            if first_tx and first_tx <= end:
                later = sum(amt for d, amt in after_sums.get(a["id"], []) if d > end)
                total += a["balance"] - later
                known = True
            elif snap:
                total += snap[0]
                known = True
        if known:
            out.append({"month": m, "value": round(total, 2)})
    return out
