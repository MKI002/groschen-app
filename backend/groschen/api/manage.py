"""Settings, categories, rules, groups, manual accounts, backups and export."""

import csv
import io
import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

from .. import backup, config, db, i18n, jobs, market, netguard, scheduler, settings
from ..analytics import cashflow, common, paydays
from ..categorize import embedder, engine, names
from ..categorize.seed import group_color
from .deps import current_user

router = APIRouter(dependencies=[Depends(current_user)])


# --- settings -----------------------------------------------------------------


@router.get("/settings")
def get_settings():
    with db.session() as conn:
        values = settings.get_all(conn)
        net = netguard.recent(conn)
        market_status = market.status(conn)
        counts = {
            "corrections": conn.execute("SELECT COUNT(*) FROM examples").fetchone()[0],
            "memory": conn.execute("SELECT COUNT(*) FROM merchant_memory").fetchone()[0],
            "rules": conn.execute("SELECT COUNT(*) FROM rules").fetchone()[0],
        }
        auto = conn.execute(
            "SELECT COUNT(*), SUM(CASE WHEN cat_source IN ('rule','memory','dict','model','transfer','own','refund') "
            "AND needs_review = 0 "
            "THEN 1 ELSE 0 END) FROM transactions WHERE date >= date('now', '-60 days')"
        ).fetchone()
    model = embedder.status()
    return {
        "values": {**values, "backup_plan": backup.plan_of(values)},
        "version": config.VERSION,
        "model": {**model, "label": i18n.tr(model["label"])},
        "learning": {**counts, "recent": auto[0] or 0, "recent_auto": auto[1] or 0},
        "network": {**net, "allowed_hosts": netguard.allowed_hosts()},
        "backups": backup.list_backups(),
        "next_runs": scheduler.next_runs(),
        "market": market_status,
    }


@router.patch("/settings")
def patch_settings(values: dict):
    try:
        with db.session() as conn:
            result = settings.update(conn, values)
            if "holder_names" in values:
                engine.reapply_quick(conn)  # transfers to these names are own transfers, or no longer
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if any(k in values for k in ("sync_schedule", "backup_plan", "backup_nightly", "backup_schedule", "backup_hour")):
        scheduler.reschedule()
    if "online_prices" in values:
        with db.session() as conn:
            market.apply_setting(conn)
        if result["online_prices"] and not jobs.running("prices"):
            jobs.start("prices", market.refresh)
    return {**result, "backup_plan": backup.plan_of(result)}


@router.post("/market/refresh")
def refresh_prices():
    with db.session() as conn:
        if not market.enabled(conn):
            raise HTTPException(status_code=400, detail="Online ETF prices are turned off in Settings.")
    running = jobs.running("prices")
    return (running or jobs.start("prices", market.refresh)).as_dict()


# --- salary month ---------------------------------------------------------------


class PaydayIn(BaseModel):
    key: str = Field(min_length=1, max_length=200)
    mode: str


@router.get("/paydays")
def get_paydays():
    with db.session() as conn:
        return paydays.sources(conn)


@router.patch("/paydays")
def patch_payday(body: PaydayIn):
    try:
        with db.session() as conn:
            paydays.set_mode(conn, body.key, body.mode)
            return paydays.sources(conn)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# --- categories ---------------------------------------------------------------


class CategoryIn(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    group: str = Field(min_length=1, max_length=40)
    kind: str = "expense"


@router.get("/categories")
def list_categories():
    with db.session() as conn:
        return db.rows(
            conn.execute(
                'SELECT c.id, c.name, c.grp AS "group", c.kind, c.color, '
                "(SELECT COUNT(*) FROM transactions t WHERE t.category_id = c.id) AS used "
                "FROM categories c ORDER BY c.sort, c.id"
            )
        )


@router.post("/categories")
def add_category(body: CategoryIn):
    if body.kind not in ("expense", "income", "transfer"):
        raise HTTPException(status_code=400, detail="Kind must be expense, income or transfer.")
    name, group = body.name.strip(), body.group.strip()
    with db.session() as conn:
        if conn.execute("SELECT 1 FROM categories WHERE name = ? AND grp = ?", (name, group)).fetchone():
            raise HTTPException(
                status_code=409,
                detail=i18n.t(
                    "{group} already has a category called {name}.", group=i18n.cat_name(group), name=i18n.cat_name(name)
                ),
            )
        existing = db.one(conn.execute("SELECT color FROM categories WHERE grp = ? LIMIT 1", (group,)))
        # New subcategories go to the end of their group so the picker keeps groups together.
        sort = conn.execute(
            "SELECT COALESCE((SELECT MAX(sort) FROM categories WHERE grp = ?), (SELECT MAX(sort) FROM categories), 0) + 1",
            (group,),
        ).fetchone()[0]
        conn.execute("UPDATE categories SET sort = sort + 1 WHERE sort >= ?", (sort,))
        cur = conn.execute(
            "INSERT INTO categories (name, grp, kind, color, sort) VALUES (?, ?, ?, ?, ?)",
            (name, group, body.kind, existing["color"] if existing else group_color(group), sort),
        )
        return {"id": cur.lastrowid}


@router.patch("/categories/{cat_id}")
def edit_category(cat_id: int, body: CategoryIn):
    with db.session() as conn:
        conn.execute(
            "UPDATE categories SET name = ?, grp = ?, kind = ? WHERE id = ?",
            (body.name.strip(), body.group.strip(), body.kind, cat_id),
        )
    return {"ok": True}


@router.delete("/categories/{cat_id}")
def delete_category(cat_id: int):
    with db.session() as conn:
        conn.execute(
            "UPDATE transactions SET category_id = NULL, cat_source = NULL, needs_review = 1 WHERE category_id = ?",
            (cat_id,),
        )
        conn.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
    return {"ok": True}


# --- rules --------------------------------------------------------------------


class RuleIn(BaseModel):
    field: str = "counterparty"  # counterparty | purpose | any
    op: str = "contains"  # contains | equals
    value: str = Field(min_length=1, max_length=80)
    category_id: int


@router.get("/rules")
def list_rules():
    with db.session() as conn:
        return db.rows(
            conn.execute(
                "SELECT r.id, r.field, r.op, r.value, r.category_id, c.name AS category, c.color "
                "FROM rules r JOIN categories c ON c.id = r.category_id ORDER BY r.id"
            )
        )


@router.post("/rules")
def add_rule(body: RuleIn):
    if body.field not in ("counterparty", "purpose", "any") or body.op not in ("contains", "equals"):
        raise HTTPException(status_code=400, detail="Unknown rule type.")
    with db.session() as conn:
        cur = conn.execute(
            "INSERT INTO rules (field, op, value, category_id, created_at) VALUES (?, ?, ?, ?, ?)",
            (body.field, body.op, body.value.strip(), body.category_id, db.now_iso()),
        )
        changed = engine.reapply_quick(conn)
    return {"id": cur.lastrowid, "applied": changed}


@router.delete("/rules/{rule_id}")
def delete_rule(rule_id: int):
    with db.session() as conn:
        conn.execute("DELETE FROM rules WHERE id = ?", (rule_id,))
    return {"ok": True}


# --- what the categorizer learned -----------------------------------------------


@router.get("/learned")
def list_learned():
    """Merchants remembered from the user's corrections, newest first, each with a readable name."""
    with db.session() as conn:
        rows = db.rows(
            conn.execute(
                "SELECT m.key, m.category_id, m.hits, m.updated_at, c.name AS category, c.grp AS category_group, c.color "
                "FROM merchant_memory m JOIN categories c ON c.id = m.category_id ORDER BY m.updated_at DESC, m.key"
            )
        )
    for r in rows:
        r["name"] = names.clean(r["key"].upper()) or r["key"]
    return rows


class LearnedIn(BaseModel):
    key: str = Field(min_length=1, max_length=120)
    category_id: int


@router.put("/learned")
def change_learned(body: LearnedIn):
    """Point a learned merchant at another category, for all its bookings you haven't set by hand."""
    with db.session() as conn:
        if not db.one(conn.execute("SELECT id FROM categories WHERE id = ?", (body.category_id,))):
            raise HTTPException(status_code=400, detail="Unknown category.")
        conn.execute(
            "INSERT INTO merchant_memory (key, category_id, hits, updated_at) VALUES (?, ?, 1, ?) "
            "ON CONFLICT(key) DO UPDATE SET category_id = excluded.category_id, updated_at = excluded.updated_at",
            (body.key, body.category_id, db.now_iso()),
        )
        changed = engine.apply_to_merchant(conn, body.key, body.category_id)
    return {"ok": True, "changed": changed}


@router.delete("/learned")
def forget_learned(key: str):
    with db.session() as conn:
        n = engine.forget(conn, key)
    return {"ok": True, "recategorized": n}


@router.post("/categorize/rerun")
def rerun_categorizer():
    """Re-run the categorizer on everything the user hasn't set by hand."""
    with db.session() as conn:
        n = engine.categorize(conn, "1 = 1")
    return {"categorized": n}


# --- groups ---------------------------------------------------------------------


class GroupIn(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    icon: str = "tag"
    category_ids: list[int] = []


@router.get("/groups")
def list_groups():
    with db.session() as conn:
        out = db.rows(conn.execute("SELECT id, name, icon, category_ids FROM groups ORDER BY id"))
    for g in out:
        g["category_ids"] = json.loads(g["category_ids"] or "[]")
    return out


@router.post("/groups")
def add_group(body: GroupIn):
    with db.session() as conn:
        cur = conn.execute(
            "INSERT INTO groups (name, icon, category_ids) VALUES (?, ?, ?)",
            (body.name.strip(), body.icon, json.dumps(body.category_ids)),
        )
    return {"id": cur.lastrowid}


@router.patch("/groups/{group_id}")
def edit_group(group_id: int, body: GroupIn):
    with db.session() as conn:
        conn.execute(
            "UPDATE groups SET name = ?, icon = ?, category_ids = ? WHERE id = ?",
            (body.name.strip(), body.icon, json.dumps(body.category_ids), group_id),
        )
    return {"ok": True}


@router.delete("/groups/{group_id}")
def delete_group(group_id: int):
    with db.session() as conn:
        conn.execute("DELETE FROM groups WHERE id = ?", (group_id,))
    return {"ok": True}


@router.get("/groups/{group_id}/summary")
def group_summary(group_id: int, preset: str | None = None, anchor: str | None = None):
    start, end, label = common.resolve_range(preset, anchor)
    with db.session() as conn:
        g = db.one(conn.execute("SELECT id, name, icon, category_ids FROM groups WHERE id = ?", (group_id,)))
        if not g:
            raise HTTPException(status_code=404, detail="Unknown group.")
        ids = json.loads(g["category_ids"] or "[]")
        s = cashflow.spending_for(conn, start, end, ids)
        marks = ",".join("?" * len(ids)) or "NULL"
        recent = db.rows(
            conn.execute(
                f"SELECT t.id, t.date, t.amount, t.counterparty, t.purpose, c.name AS category, c.color AS category_color "
                f"FROM transactions t LEFT JOIN categories c ON c.id = t.category_id WHERE t.category_id IN ({marks}) "
                f"AND t.date BETWEEN ? AND ? ORDER BY t.date DESC LIMIT 12",
                (*ids, start, end),
            )
        )
    return {
        "group": {**g, "category_ids": ids},
        "range": {"start": start, "end": end, "label": label},
        **s,
        "recent": recent,
    }


# --- manual accounts ------------------------------------------------------------


class ManualAccount(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    kind: str = "manual_asset"  # manual_asset | manual_liability
    balance: float


@router.post("/accounts/manual")
def add_manual_account(body: ManualAccount):
    kind = "manual_liability" if body.kind == "manual_liability" else "manual_asset"
    balance = -abs(body.balance) if kind == "manual_liability" else body.balance
    with db.session() as conn:
        cur = conn.execute(
            "INSERT INTO accounts (kind, name, balance, balance_date, manual, created_at) "
            "VALUES (?, ?, ?, date('now'), 1, ?)",
            (kind, body.name.strip(), balance, db.now_iso()),
        )
    return {"id": cur.lastrowid}


class BalanceIn(BaseModel):
    balance: float


@router.put("/accounts/{account_id}/balance")
def set_manual_balance(account_id: int, body: BalanceIn):
    with db.session() as conn:
        a = db.one(conn.execute("SELECT kind, manual FROM accounts WHERE id = ?", (account_id,)))
        if not a or not a["manual"]:
            raise HTTPException(status_code=400, detail="Only accounts entered by hand can be changed here.")
        balance = -abs(body.balance) if a["kind"] == "manual_liability" else body.balance
        conn.execute("UPDATE accounts SET balance = ?, balance_date = date('now') WHERE id = ?", (balance, account_id))
        conn.execute(
            "INSERT INTO balance_history (account_id, date, balance) VALUES (?, date('now'), ?) "
            "ON CONFLICT(account_id, date) DO UPDATE SET balance = excluded.balance",
            (account_id, balance),
        )
    return {"ok": True}


@router.delete("/accounts/{account_id}")
def delete_manual_account(account_id: int):
    with db.session() as conn:
        a = db.one(conn.execute("SELECT manual FROM accounts WHERE id = ?", (account_id,)))
        if not a or not a["manual"]:
            raise HTTPException(status_code=400, detail="Bank accounts can be hidden, not deleted.")
        conn.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
    return {"ok": True}


@router.get("/accounts")
def list_accounts():
    with db.session() as conn:
        return db.rows(
            conn.execute(
                "SELECT id, name, kind, iban, balance, balance_date, manual, enabled, connection_id "
                "FROM accounts ORDER BY manual, id"
            )
        )


# --- backups and export ---------------------------------------------------------


@router.post("/backups")
def make_backup():
    return backup.create("manual")


@router.post("/backups/preview")
def preview_backups(values: dict):
    """Which backups a retention change would remove, before it is saved."""
    with db.session() as conn:
        current = settings.get_all(conn)
        try:
            clean = {k: settings._clean(k, v) for k, v in values.items() if k in backup.POLICY_KEYS}
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"remove": backup.preview({**current, **clean})}


class PinIn(BaseModel):
    pinned: bool


@router.patch("/backups/{name}")
def pin_backup(name: str, body: PinIn):
    info = backup.set_pinned(name, body.pinned)
    if not info:
        raise HTTPException(status_code=404, detail="Unknown backup.")
    return info


@router.delete("/backups/{name}")
def delete_backup(name: str):
    if not backup.delete(name):
        raise HTTPException(status_code=404, detail="Unknown backup.")
    return {"ok": True}


@router.post("/backups/{name}/restore")
def restore_backup(name: str):
    if jobs.running("sync"):
        raise HTTPException(status_code=409, detail="A bank sync is running. Try again when it has finished.")
    try:
        result = backup.restore(name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Unknown backup.") from exc
    except backup.RestoreError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    scheduler.reschedule()
    return result


@router.get("/backups/{name}")
def download_backup(name: str):
    path = backup.path_for(name)
    if not path:
        raise HTTPException(status_code=404, detail="Unknown backup.")
    return FileResponse(path, filename=name, media_type="application/octet-stream")


def _cell(text: str | None) -> str:
    """Bank texts are written by whoever sent the money. A text starting with =, +, - or @
    would run as a formula when the file is opened in Excel, so it gets a leading quote."""
    text = text or ""
    return "'" + text if text[:1] in ("=", "+", "-", "@", "\t", "\r") else text


@router.get("/export/transactions.csv")
def export_transactions():
    with db.session() as conn:
        rows = db.rows(
            conn.execute(
                "SELECT t.date, a.name AS account, t.amount, t.currency, t.counterparty, t.purpose, t.booking_text, "
                'c.grp AS "group", c.name AS category, t.note FROM transactions t JOIN accounts a ON a.id = t.account_id '
                "LEFT JOIN categories c ON c.id = t.category_id ORDER BY t.date"
            )
        )
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=";")
    header = (
        "Date",
        "Account",
        "Amount",
        "Currency",
        "Counterparty",
        "Purpose",
        "Booking text",
        "Group",
        "Category",
        "Note",
    )
    writer.writerow([i18n.t(h) for h in header])
    for r in rows:
        writer.writerow(
            [
                r["date"],
                _cell(r["account"]),
                f"{r['amount']:.2f}".replace(".", ","),
                _cell(r["currency"]),
                _cell(r["counterparty"]),
                _cell(r["purpose"]),
                _cell(r["booking_text"]),
                _cell(i18n.cat_name(r["group"])),
                _cell(i18n.cat_name(r["category"])),
                _cell(r["note"]),
            ]
        )
    data = buf.getvalue().encode("utf-8-sig")
    return StreamingResponse(
        iter([data]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="groschen-transactions.csv"'},
    )
