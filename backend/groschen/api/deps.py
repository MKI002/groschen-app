from fastapi import Cookie, HTTPException

from .. import db, security


def current_user(groschen_session: str | None = Cookie(default=None)) -> dict:
    with db.session() as conn:
        user = security.user_for_token(conn, groschen_session)
    if not user:
        raise HTTPException(status_code=401, detail="Please log in.")
    return user


def has_users() -> bool:
    with db.session() as conn:
        return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0
