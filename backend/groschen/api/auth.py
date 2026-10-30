"""First-run account creation, login (password or passkey), logout and the login security settings."""

import os
import threading
import time

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field

from .. import config, db, passkeys, security, settings
from .deps import current_user, has_users

router = APIRouter()


class NewAccount(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    username: str = Field(min_length=2, max_length=40)
    password: str = Field(min_length=8, max_length=200)


class Login(BaseModel):
    username: str
    password: str


def _https(request: Request) -> bool:
    # Behind an HTTPS proxy such as Tailscale Serve the app itself is reached over plain
    # http, but the browser's Origin header still says https.
    return request.url.scheme == "https" or (request.headers.get("origin") or "").startswith("https://")


def _set_cookie(request: Request, response: Response, token: str, days: int) -> None:
    response.set_cookie(
        security.SESSION_COOKIE,
        token,
        max_age=days * 86400,
        httponly=True,
        samesite="lax",
        secure=_https(request),
    )


def _client(request: Request) -> tuple[str, str | None]:
    return (request.client.host if request.client else "unknown"), request.headers.get("user-agent")


# Container variable for the case where every passkey is lost while the password login is
# off: set it on the container, restart, and the password works again.
RESCUE_ENV = "GROSCHEN_ALLOW_PASSWORD"


def password_allowed(conn) -> bool:
    if settings.get(conn, "password_login") or os.environ.get(RESCUE_ENV) == "1":
        return True
    # Never lock the user out: without a passkey the password always works.
    return conn.execute("SELECT 1 FROM passkeys LIMIT 1").fetchone() is None


@router.get("/status")
def status(groschen_session: str | None = Cookie(default=None)):
    with db.session() as conn:
        user = security.user_for_token(conn, groschen_session)
        setup_complete = bool(settings.get(conn, "setup_complete"))
        language = settings.get(conn, "language")
        users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        has_passkeys = conn.execute("SELECT 1 FROM passkeys LIMIT 1").fetchone() is not None
        password = password_allowed(conn)
    return {
        "version": config.VERSION,
        "has_user": users > 0,
        "setup_complete": setup_complete,
        # Shown before login too, so the login page and splash use the chosen language.
        "language": language,
        "user": user,
        # The login page offers the passkey button and hides the password form when it's off.
        "passkeys": has_passkeys,
        "password_login": password,
    }


@router.post("/setup/account")
def create_account(body: NewAccount, request: Request, response: Response):
    if has_users():
        raise HTTPException(status_code=409, detail="An account already exists. Please log in.")
    password_hash = security.hash_password(body.password)
    with db.session() as conn:
        # Check and insert in one statement, so two requests racing through the first-run
        # page can't both create an account.
        cur = conn.execute(
            "INSERT INTO users (username, name, password_hash, created_at) SELECT ?, ?, ?, ? "
            "WHERE NOT EXISTS (SELECT 1 FROM users)",
            (body.username.strip().lower(), body.name.strip(), password_hash, db.now_iso()),
        )
        if cur.rowcount != 1:
            raise HTTPException(status_code=409, detail="An account already exists. Please log in.")
        ip, agent = _client(request)
        token = security.create_session(conn, cur.lastrowid, ip=ip, agent=agent)
        days = security.session_days(conn)
    _set_cookie(request, response, token, days)
    return {"ok": True}


# Failed logins per address, kept in memory (a restart forgets them). How many are allowed
# and how long an address then waits are set under Settings → Security.
_failures: dict[str, list[float]] = {}
_failures_lock = threading.Lock()


def _limits(conn) -> tuple[int, int]:
    return int(settings.get(conn, "login_max_failures")), int(settings.get(conn, "login_lock_minutes"))


def _check_lock(conn, client: str) -> None:
    max_failures, minutes = _limits(conn)
    cutoff = time.monotonic() - minutes * 60
    with _failures_lock:
        kept = [t for t in _failures.get(client, []) if t > cutoff]
        _failures[client] = kept
    if len(kept) >= max_failures:
        raise HTTPException(status_code=429, detail=f"Too many failed logins. Try again in {minutes} minutes.")


def _record_failure(client: str) -> None:
    with _failures_lock:
        _failures.setdefault(client, []).append(time.monotonic())


def _clear_failures(client: str) -> None:
    with _failures_lock:
        _failures.pop(client, None)


@router.post("/login")
def login(body: Login, request: Request, response: Response):
    ip, agent = _client(request)
    username = body.username.strip().lower()
    with db.session() as conn:
        _check_lock(conn, ip)
        if not password_allowed(conn):
            raise HTTPException(status_code=403, detail="Password login is turned off. Log in with a passkey.")
        row = db.one(conn.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,)))
        # An unknown username costs the same hash check as a wrong password, so response
        # times don't reveal which usernames exist.
        stored = row["password_hash"] if row else security.DUMMY_HASH
        if not security.verify_password(stored, body.password) or not row:
            security.log_login(conn, username=username, method="password", ok=False, ip=ip, agent=agent)
            failed = True
        else:
            security.log_login(conn, username=username, method="password", ok=True, ip=ip, agent=agent)
            token = security.create_session(conn, row["id"], ip=ip, agent=agent, method="password")
            days = security.session_days(conn)
            failed = False
    if failed:
        _record_failure(ip)
        time.sleep(1.0)
        raise HTTPException(status_code=401, detail="Wrong username or password.")
    _clear_failures(ip)
    _set_cookie(request, response, token, days)
    return {"ok": True}


# --- passkeys --------------------------------------------------------------------------------


class PasskeyLogin(BaseModel):
    challenge_id: str = Field(max_length=100)
    credential: dict


def _relying_party(request: Request) -> passkeys.Party:
    party = passkeys.party_for(request.headers.get("origin"))
    if not party:
        raise HTTPException(
            status_code=400,
            detail="Passkeys only work when Groschen is opened over HTTPS with a name, not an IP address.",
        )
    return party


@router.post("/login/passkey/options")
def passkey_login_options(request: Request):
    party = _relying_party(request)
    ip, _ = _client(request)
    with db.session() as conn:
        _check_lock(conn, ip)
    return passkeys.login_options(party)


@router.post("/login/passkey")
def passkey_login(body: PasskeyLogin, request: Request, response: Response):
    party = _relying_party(request)
    ip, agent = _client(request)
    with db.session() as conn:
        _check_lock(conn, ip)
        user_id = passkeys.verify_login(conn, party, body.challenge_id, body.credential)
        if user_id is None:
            security.log_login(conn, username=None, method="passkey", ok=False, ip=ip, agent=agent)
        else:
            username = conn.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()[0]
            security.log_login(conn, username=username, method="passkey", ok=True, ip=ip, agent=agent)
            token = security.create_session(conn, user_id, ip=ip, agent=agent, method="passkey")
            days = security.session_days(conn)
    if user_id is None:
        _record_failure(ip)
        time.sleep(1.0)
        raise HTTPException(status_code=401, detail="That passkey didn't work. Try again or use your password.")
    _clear_failures(ip)
    _set_cookie(request, response, token, days)
    return {"ok": True}


class PasskeyNew(BaseModel):
    challenge_id: str = Field(max_length=100)
    credential: dict
    name: str = Field(default="", max_length=60)


class PasskeyRename(BaseModel):
    name: str = Field(min_length=1, max_length=60)


@router.get("/passkeys")
def list_passkeys(user=Depends(current_user)):
    with db.session() as conn:
        return passkeys.list_for(conn, user["id"])


@router.post("/passkeys/options")
def passkey_options(request: Request, user=Depends(current_user)):
    party = _relying_party(request)
    with db.session() as conn:
        return passkeys.register_options(conn, party, user)


@router.post("/passkeys")
def add_passkey(body: PasskeyNew, request: Request, user=Depends(current_user)):
    party = _relying_party(request)
    _, agent = _client(request)
    with db.session() as conn:
        item = passkeys.register(conn, party, user["id"], body.challenge_id, body.credential, body.name, agent)
    if item is None:
        raise HTTPException(status_code=400, detail="The passkey couldn't be saved. Please try again.")
    return item


@router.patch("/passkeys/{passkey_id}")
def rename_passkey(passkey_id: int, body: PasskeyRename, user=Depends(current_user)):
    with db.session() as conn:
        cur = conn.execute(
            "UPDATE passkeys SET name = ? WHERE id = ? AND user_id = ?", (body.name.strip(), passkey_id, user["id"])
        )
    if cur.rowcount != 1:
        raise HTTPException(status_code=404, detail="Not found.")
    return {"ok": True}


@router.delete("/passkeys/{passkey_id}")
def delete_passkey(passkey_id: int, user=Depends(current_user)):
    with db.session() as conn:
        cur = conn.execute("DELETE FROM passkeys WHERE id = ? AND user_id = ?", (passkey_id, user["id"]))
        if cur.rowcount != 1:
            raise HTTPException(status_code=404, detail="Not found.")
        # Without a passkey left, the password is the way in again.
        password_back = False
        if not conn.execute("SELECT 1 FROM passkeys LIMIT 1").fetchone() and not settings.get(conn, "password_login"):
            settings.put(conn, "password_login", True)
            password_back = True
    return {"ok": True, "password_login": password_back}


# --- sessions and login history -----------------------------------------------------------------


@router.get("/sessions")
def sessions(user=Depends(current_user), groschen_session: str | None = Cookie(default=None)):
    with db.session() as conn:
        return security.list_sessions(conn, user["id"], groschen_session)


@router.delete("/sessions/{session_id}")
def end_session(session_id: int, user=Depends(current_user)):
    with db.session() as conn:
        if not security.drop_session_by_id(conn, user["id"], session_id):
            raise HTTPException(status_code=404, detail="Not found.")
    return {"ok": True}


@router.post("/sessions/others")
def end_other_sessions(user=Depends(current_user), groschen_session: str | None = Cookie(default=None)):
    with db.session() as conn:
        ended = security.drop_other_sessions(conn, user["id"], groschen_session)
    return {"ended": ended}


@router.get("/logins")
def login_history(user=Depends(current_user)):
    with db.session() as conn:
        return db.rows(
            conn.execute("SELECT at, username, method, ok, ip, agent FROM login_events ORDER BY id DESC LIMIT 50")
        )


@router.post("/logout")
def logout(response: Response, groschen_session: str | None = Cookie(default=None)):
    with db.session() as conn:
        security.drop_session(conn, groschen_session)
    response.delete_cookie(security.SESSION_COOKIE)
    return {"ok": True}


class PasswordChange(BaseModel):
    current: str
    new: str = Field(min_length=8, max_length=200)


@router.post("/me/password")
def change_password(body: PasswordChange, user=Depends(current_user), groschen_session: str | None = Cookie(default=None)):
    with db.session() as conn:
        row = db.one(conn.execute("SELECT password_hash FROM users WHERE id = ?", (user["id"],)))
        if not row or not security.verify_password(row["password_hash"], body.current):
            raise HTTPException(status_code=400, detail="The current password isn't right.")
        conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (security.hash_password(body.new), user["id"]))
        # Every other browser that was logged in has to log in again with the new password.
        security.drop_other_sessions(conn, user["id"], groschen_session)
    return {"ok": True}
