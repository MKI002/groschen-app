"""Bank connections, syncing, imports and background jobs."""

import datetime as dt
import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .. import db, fx, i18n, jobs, security, settings
from ..bank import banks as bank_list
from ..bank import csv_import, store, sync
from ..jobs import UserFacingError
from .deps import current_user

router = APIRouter(dependencies=[Depends(current_user)])

LOGIN_WINDOW_DAYS = 90
MAX_UPLOAD = 20 * 1024 * 1024


class BankLogin(BaseModel):
    bank_code: str = Field(default="50010517", pattern=r"^\d{8}$")
    server: str | None = Field(default=None, max_length=200)
    login: str = Field(min_length=1, max_length=40)
    pin: str = Field(min_length=1, max_length=64)
    product_id: str = Field(min_length=5, max_length=40)


class TanAnswer(BaseModel):
    tan: str | None = Field(default=None, max_length=64)


class ConnectionUpdate(BaseModel):
    login: str | None = None
    pin: str | None = None
    product_id: str | None = None
    server: str | None = Field(default=None, max_length=200)


@router.get("/banks")
def banks(q: str = ""):
    """Banks matching a name, a Bankleitzahl or an IBAN, for the bank picker."""
    with db.session() as conn:
        return bank_list.search(conn, q[:60])


@router.get("/banks/directory")
def bank_directory():
    with db.session() as conn:
        return {"banks": bank_list.directory_size(conn)}


@router.post("/banks/directory")
async def import_bank_directory(file: UploadFile = File(...)):
    """The FinTS institute list that comes with the product registration: every bank's server address."""
    raw = await _read(file)
    try:
        with db.session() as conn:
            return bank_list.import_directory(conn, raw)
    except UserFacingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/banks/{blz}")
def bank_by_code(blz: str):
    with db.session() as conn:
        try:
            return bank_list.resolve(conn, blz)
        except UserFacingError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/bank/test")
def bank_test(body: BankLogin):
    if body.server:
        try:
            bank_list.check_server(body.server)
        except UserFacingError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    job = jobs.start(
        "bank-test",
        sync.test_connection,
        body.bank_code,
        body.login.strip(),
        body.pin,
        body.product_id.strip(),
        body.server or None,
        interactive=True,
    )
    return job.as_dict()


@router.post("/jobs/{job_id}/tan")
def job_tan(job_id: str, body: TanAnswer):
    """The TAN the bank asked for, typed on the web page (or none, to cancel)."""
    job = jobs.get(job_id)
    if not job or not job.give_tan((body.tan or "").strip() or None):
        raise HTTPException(status_code=409, detail="Nothing is waiting for a TAN.")
    return {"ok": True}


@router.get("/jobs/{job_id}")
def job_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Unknown job.")
    return job.as_dict()


@router.post("/sync")
def sync_now(full: bool = False):
    running = jobs.running("sync")
    if running:
        return running.as_dict()
    return jobs.start("sync", sync.sync_all, full, interactive=True).as_dict()


@router.post("/setup/finish")
def setup_finish():
    running = jobs.running("sync")
    if running:
        return running.as_dict()
    with db.session() as conn:
        has_bank = conn.execute("SELECT COUNT(*) FROM connections").fetchone()[0] > 0

    def first_run(job):
        if has_bank:
            return sync.sync_all(job, full=True, first_run=True)
        job.add_steps("Categorizing your transactions", "Finding subscriptions and recurring payments")
        from ..analytics import recurring
        from ..categorize import engine

        with db.session() as conn:
            n = engine.categorize(conn, "cat_source IS NULL OR cat_source = 'none'")
        job.step(1)
        with db.session() as conn:
            r = len(recurring.detect(conn))
        return {"categorized": n, "recurring": r}

    return jobs.start("sync", first_run, interactive=True).as_dict()


@router.post("/setup/complete")
def setup_complete():
    with db.session() as conn:
        settings.put(conn, "setup_complete", True)
    from .. import scheduler

    scheduler.reschedule()
    return {"ok": True}


def _connection_view(conn, c: dict) -> dict:
    confirmed = c.get("bank_login_confirmed_at") or c["created_at"]
    days_used = (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(confirmed)).days
    accounts = db.rows(
        conn.execute(
            "SELECT id, name, kind, iban, balance, balance_date, enabled FROM accounts WHERE connection_id = ? ORDER BY id",
            (c["id"],),
        )
    )
    due = (dt.datetime.fromisoformat(confirmed) + dt.timedelta(days=LOGIN_WINDOW_DAYS)).date()
    try:
        info = bank_list.resolve(conn, c["bank_code"])
    except UserFacingError:
        info = {
            "short": c["bank_name"],
            "label": c["bank_name"],
            "app": None,
            "login": "generic",
            "id": "other",
            "source": "none",
        }
    return {
        "id": c["id"],
        "bank_code": c["bank_code"],
        "bank_name": c["bank_name"],
        "short": info["short"],
        "label": info["label"] if info["source"] == "known" else c["bank_name"],
        "bank_id": info["id"],
        "app": info["app"],
        "login_kind": info["login"],
        "server": c["server"],
        "status": c["status"],
        "last_sync_at": c["last_sync_at"],
        "last_error": i18n.tr(c["last_error"]),
        "login_hint": _mask(security.decrypt(c["login_enc"])),
        "product_id_set": bool(c["product_id"]),
        "bank_login_confirmed_at": confirmed,
        "login_days_left": max(0, LOGIN_WINDOW_DAYS - days_used),
        "login_due": due.isoformat(),
        "accounts": accounts,
    }


def _mask(login: str) -> str:
    return ("•" * max(0, len(login) - 3)) + login[-3:] if login else ""


@router.get("/connections")
def connections():
    with db.session() as conn:
        rows = db.rows(conn.execute("SELECT * FROM connections ORDER BY id"))
        return [_connection_view(conn, c) for c in rows]


@router.post("/connections/{connection_id}/confirm-login")
def confirm_bank_login(connection_id: int):
    with db.session() as conn:
        conn.execute("UPDATE connections SET bank_login_confirmed_at = ? WHERE id = ?", (db.now_iso(), connection_id))
        c = db.one(conn.execute("SELECT * FROM connections WHERE id = ?", (connection_id,)))
        if not c:
            raise HTTPException(status_code=404, detail="Unknown connection.")
        return _connection_view(conn, c)


@router.patch("/connections/{connection_id}")
def update_connection(connection_id: int, body: ConnectionUpdate):
    with db.session() as conn:
        c = db.one(conn.execute("SELECT id FROM connections WHERE id = ?", (connection_id,)))
        if not c:
            raise HTTPException(status_code=404, detail="Unknown connection.")
        if body.login:
            conn.execute(
                "UPDATE connections SET login_enc = ?, state_enc = NULL WHERE id = ?",
                (security.encrypt(body.login.strip()), connection_id),
            )
        if body.pin:
            conn.execute("UPDATE connections SET pin_enc = ? WHERE id = ?", (security.encrypt(body.pin), connection_id))
        if body.product_id:
            conn.execute("UPDATE connections SET product_id = ? WHERE id = ?", (body.product_id.strip(), connection_id))
        if body.server:
            try:
                server = bank_list.check_server(body.server)
            except UserFacingError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            conn.execute("UPDATE connections SET server = ?, state_enc = NULL WHERE id = ?", (server, connection_id))
    if body.server:
        sync.allow_bank_hosts()
    return {"ok": True}


@router.delete("/connections/{connection_id}")
def delete_connection(connection_id: int):
    """Forget the login. Accounts and their history stay."""
    with db.session() as conn:
        conn.execute("UPDATE accounts SET connection_id = NULL WHERE connection_id = ?", (connection_id,))
        conn.execute("DELETE FROM connections WHERE id = ?", (connection_id,))
    return {"ok": True}


class AccountToggle(BaseModel):
    enabled: bool | None = None
    name: str | None = None
    currency: str | None = None


@router.patch("/accounts/{account_id}")
def update_account(account_id: int, body: AccountToggle):
    with db.session() as conn:
        if body.enabled is not None:
            conn.execute("UPDATE accounts SET enabled = ? WHERE id = ?", (int(body.enabled), account_id))
        if body.name:
            conn.execute("UPDATE accounts SET name = ? WHERE id = ?", (body.name.strip()[:60], account_id))
        if body.currency:
            try:
                store.set_account_currency(conn, account_id, body.currency)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            fx.apply(conn)
    if body.currency:
        fx.after_change()
    return {"ok": True}


async def _read(file: UploadFile) -> bytes:
    raw = await file.read(MAX_UPLOAD + 1)
    if len(raw) > MAX_UPLOAD:
        raise HTTPException(status_code=413, detail="That file is larger than 20 MB.")
    return raw


PICK_COLUMNS = "Pick the column with the date and the one with the amount."


@router.post("/import/csv")
async def import_csv(
    file: UploadFile = File(...),
    account_id: int | None = Form(default=None),
    mapping: str | None = Form(default=None, max_length=2000),
):
    """Import a bank's CSV export. A file Groschen can't read alone answers 422 with its first rows
    under "mapping"; the page asks which column is which and sends the file again with ``mapping``."""
    raw = await _read(file)
    picked = None
    if mapping:
        try:
            picked = json.loads(mapping)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=PICK_COLUMNS) from exc
        if not isinstance(picked, dict):
            raise HTTPException(status_code=400, detail=PICK_COLUMNS)
    try:
        result = sync.import_csv(jobs.Job(id="import", kind="import"), raw, account_id, file.filename, picked)
    except csv_import.NeedsMapping as exc:
        return JSONResponse(status_code=422, content={"detail": i18n.tr(str(exc)), "mapping": exc.preview})
    except UserFacingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {**result, "file": file.filename}


@router.post("/import/prices")
async def import_prices(file: UploadFile = File(...)):
    raw = await _read(file)
    try:
        return {**sync.import_prices(raw), "file": file.filename}
    except UserFacingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
