"""Passwords, login sessions and encryption of the bank PIN."""

import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from cryptography.fernet import Fernet

from . import config, db

SESSION_COOKIE = "groschen_session"
SESSION_DAYS = 30

_hasher = PasswordHasher()
# Checked against when a login names an unknown user, so that costs as long as a wrong password.
DUMMY_HASH = _hasher.hash("groschen-no-such-user")
_fernet: Fernet | None = None


def _key() -> bytes:
    path = config.KEY_PATH
    if path.exists():
        return path.read_bytes().strip()
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    key = Fernet.generate_key()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as fh:
        fh.write(key)
    return key


def fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        _fernet = Fernet(_key())
    return _fernet


def reset_cache() -> None:
    """Forget the cached key (used by tests that switch data folders)."""
    global _fernet
    _fernet = None


def encrypt(text: str) -> bytes:
    return fernet().encrypt(text.encode("utf-8"))


def decrypt(blob: bytes | None) -> str:
    if not blob:
        return ""
    return fernet().decrypt(bytes(blob)).decode("utf-8")


def encrypt_bytes(data: bytes) -> bytes:
    return fernet().encrypt(data)


def decrypt_bytes(blob: bytes | None) -> bytes | None:
    if not blob:
        return None
    return fernet().decrypt(bytes(blob))


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(stored: str, password: str) -> bool:
    try:
        return _hasher.verify(stored, password)
    except (VerifyMismatchError, InvalidHashError):
        return False


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _setting(conn, key: str):
    from . import settings

    return settings.get(conn, key)


def session_days(conn) -> int:
    return int(_setting(conn, "session_days") or SESSION_DAYS)


def create_session(conn, user_id: int, *, ip: str | None = None, agent: str | None = None, method: str = "password") -> str:
    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    conn.execute(
        "INSERT INTO sessions (token_hash, user_id, created_at, expires_at, last_seen, ip, agent, method) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            _token_hash(token),
            user_id,
            now.isoformat(),
            (now + timedelta(days=session_days(conn))).isoformat(),
            now.isoformat(),
            ip,
            (agent or "")[:300] or None,
            method,
        ),
    )
    conn.execute("DELETE FROM sessions WHERE expires_at < ?", (now.isoformat(),))
    return token


# A request refreshes "last seen" at most this often, so browsing doesn't write on every click.
TOUCH_SECONDS = 60


def _expired(conn, row: dict, now: datetime) -> bool:
    if row["expires_at"] < now.isoformat():
        return True
    # A shorter lifetime chosen in Settings also ends logins that started before.
    created = datetime.fromisoformat(row["created_at"])
    if created + timedelta(days=session_days(conn)) < now:
        return True
    idle = int(_setting(conn, "idle_minutes") or 0)
    seen = row["last_seen"] or row["created_at"]
    return bool(idle) and datetime.fromisoformat(seen) + timedelta(minutes=idle) < now


def user_for_token(conn, token: str | None) -> dict | None:
    if not token:
        return None
    row = db.one(
        conn.execute(
            "SELECT u.id, u.username, u.name, s.created_at, s.expires_at, s.last_seen FROM sessions s "
            "JOIN users u ON u.id = s.user_id WHERE s.token_hash = ?",
            (_token_hash(token),),
        )
    )
    if not row:
        return None
    now = datetime.now(timezone.utc)
    if _expired(conn, row, now):
        drop_session(conn, token)
        return None
    seen = row["last_seen"] or row["created_at"]
    if datetime.fromisoformat(seen) + timedelta(seconds=TOUCH_SECONDS) < now:
        conn.execute("UPDATE sessions SET last_seen = ? WHERE token_hash = ?", (now.isoformat(), _token_hash(token)))
    return {"id": row["id"], "username": row["username"], "name": row["name"]}


def list_sessions(conn, user_id: int, current_token: str | None) -> list[dict]:
    now = datetime.now(timezone.utc)
    current = _token_hash(current_token) if current_token else ""
    out = []
    for row in db.rows(
        conn.execute(
            "SELECT rowid AS id, token_hash, created_at, expires_at, last_seen, ip, agent, method FROM sessions "
            "WHERE user_id = ? ORDER BY COALESCE(last_seen, created_at) DESC",
            (user_id,),
        )
    ):
        if _expired(conn, row, now):
            continue
        out.append(
            {
                "id": row["id"],
                "current": row["token_hash"] == current,
                "created_at": row["created_at"],
                "last_seen": row["last_seen"] or row["created_at"],
                "ip": row["ip"],
                "agent": row["agent"],
                "method": row["method"] or "password",
            }
        )
    return out


def drop_session_by_id(conn, user_id: int, session_id: int) -> bool:
    return conn.execute("DELETE FROM sessions WHERE rowid = ? AND user_id = ?", (session_id, user_id)).rowcount == 1


def drop_session(conn, token: str | None) -> None:
    if token:
        conn.execute("DELETE FROM sessions WHERE token_hash = ?", (_token_hash(token),))


def drop_other_sessions(conn, user_id: int, keep_token: str | None) -> int:
    return conn.execute(
        "DELETE FROM sessions WHERE user_id = ? AND token_hash != ?",
        (user_id, _token_hash(keep_token) if keep_token else ""),
    ).rowcount


# The latest logins and failed attempts, shown under Settings → Security.
KEEP_EVENTS = 200


def log_login(conn, *, username: str | None, method: str, ok: bool, ip: str | None, agent: str | None) -> None:
    conn.execute(
        "INSERT INTO login_events (at, username, method, ok, ip, agent) VALUES (?, ?, ?, ?, ?, ?)",
        (db.now_iso(), (username or "")[:40] or None, method, int(ok), ip, (agent or "")[:300] or None),
    )
    conn.execute(
        "DELETE FROM login_events WHERE id <= (SELECT id FROM login_events ORDER BY id DESC LIMIT 1 OFFSET ?)",
        (KEEP_EVENTS,),
    )
