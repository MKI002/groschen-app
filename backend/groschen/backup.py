"""Database backups in the data folder: schedule, retention and restore.

A backup is a consistent copy of the SQLite database. The encryption key for the
bank PIN (secret.key) is deliberately not part of it: a downloaded backup never
contains anything that can unlock the bank login.

Retention works like Synology Hyper Backup:
- "last":  keep the newest N backups.
- "days":  keep every backup younger than N days.
- "smart": keep everything from the last 24 hours, then the newest backup of each
           day for N days, of each week for N weeks, of each month for N months
           and of each year for N years.
On top of any mode, "at most N backups" drops the oldest ones beyond that number.
Pinned backups are never removed and don't count toward any limit. The newest
backup always stays.
"""

import datetime as dt
import json
import logging
import re
import sqlite3
import threading
from dataclasses import dataclass

from . import config, db, settings

log = logging.getLogger("groschen.backup")

NAME_RE = re.compile(r"^groschen-(\d{8}-\d{6})(?:-(auto|manual|safety))?\.db$")
KINDS = ("auto", "manual", "safety")
INDEX = "index.json"

# Settings that describe the backups themselves. A restore keeps the current ones,
# so going back to an old state never brings back an old retention that would
# then delete the newer backups.
# Kept as they are now when a backup is restored, so a restore never changes how to log in.
LOGIN_TABLES = ("users", "sessions", "passkeys")
LOGIN_KEYS = ("session_days", "idle_minutes", "login_max_failures", "login_lock_minutes", "password_login")
POLICY_KEYS = (
    "backup_plan",
    "backup_nightly",
    "backup_schedule",
    "backup_hour",
    "backup_mode",
    "backup_keep",
    "backup_days",
    "backup_smart_days",
    "backup_smart_weeks",
    "backup_smart_months",
    "backup_smart_years",
    "backup_max",
)

_lock = threading.Lock()


class RestoreError(Exception):
    pass


# --- files and the index ----------------------------------------------------------


def _files():
    if not config.BACKUP_DIR.exists():
        return []
    return [p for p in config.BACKUP_DIR.iterdir() if p.is_file() and NAME_RE.match(p.name)]


def _when(name: str) -> dt.datetime:
    return dt.datetime.strptime(NAME_RE.match(name).group(1), "%Y%m%d-%H%M%S")


def _kind(name: str) -> str:
    return NAME_RE.match(name).group(2) or "auto"


def _load_index() -> dict:
    try:
        data = json.loads((config.BACKUP_DIR / INDEX).read_text())
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _save_index(index: dict) -> None:
    config.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    names = {p.name for p in _files()}
    index = {k: v for k, v in index.items() if k in names}
    tmp = config.BACKUP_DIR / (INDEX + ".tmp")
    tmp.write_text(json.dumps(index, indent=1, sort_keys=True))
    tmp.chmod(0o600)
    tmp.replace(config.BACKUP_DIR / INDEX)


def _open_ro(path) -> sqlite3.Connection:
    # immutable: no -wal/-shm files are created next to the backup, and nothing is written.
    conn = sqlite3.connect(f"file:{path}?mode=ro&immutable=1", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _stats(path) -> dict:
    """What is inside a backup, for the list on the Settings page."""
    try:
        conn = _open_ro(path)
        try:
            one = lambda sql: conn.execute(sql).fetchone()[0]  # noqa: E731
            return {
                "transactions": one("SELECT COUNT(*) FROM transactions"),
                "accounts": one("SELECT COUNT(*) FROM accounts"),
                "latest": one("SELECT MAX(date) FROM transactions"),
            }
        finally:
            conn.close()
    except sqlite3.Error:
        return {}


def _describe(path, index: dict) -> dict:
    entry = index.get(path.name) or {}
    if "stats" not in entry:
        entry["stats"] = _stats(path)
        index[path.name] = entry
    return {
        "name": path.name,
        "size": path.stat().st_size,
        "created_at": _when(path.name).astimezone().isoformat(timespec="seconds"),
        "kind": _kind(path.name),
        "pinned": bool(entry.get("pinned")),
        **entry["stats"],
    }


def list_backups() -> list[dict]:
    with _lock:
        index = _load_index()
        before = json.dumps(index, sort_keys=True)
        out = [_describe(p, index) for p in sorted(_files(), key=lambda p: _when(p.name), reverse=True)]
        if json.dumps(index, sort_keys=True) != before:
            _save_index(index)
    return out


def path_for(name: str):
    """Only names Groschen created itself, only inside the backup folder."""
    if not NAME_RE.match(name or ""):
        return None
    path = config.BACKUP_DIR / name
    return path if path.is_file() else None


# --- making backups ------------------------------------------------------------------


def create(kind: str = "manual", prune_after: bool = True) -> dict:
    if kind not in KINDS:
        raise ValueError(kind)
    config.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    with _lock:
        when = dt.datetime.now().replace(microsecond=0)
        while True:
            target = config.BACKUP_DIR / f"groschen-{when:%Y%m%d-%H%M%S}-{kind}.db"
            if not target.exists():
                break
            when += dt.timedelta(seconds=1)
        src = db.connect()
        try:
            dst = sqlite3.connect(target)
            try:
                src.backup(dst)
                # A standalone file: no -wal next to it, readable on any computer.
                dst.execute("PRAGMA journal_mode = DELETE")
            finally:
                dst.close()
        finally:
            src.close()
        target.chmod(0o600)
        index = _load_index()
        info = _describe(target, index)
        _save_index(index)
    if prune_after:
        prune()
    return info


def scheduled() -> None:
    if schedule() != "off":
        create("auto")


# Kept for the scheduler's older name.
nightly = scheduled


# --- schedule ------------------------------------------------------------------------


def plan_of(values: dict) -> str:
    """Smart Recycle or Custom. Installs from before the choice existed get Smart Recycle,
    unless their backup settings were clearly set by hand."""
    chosen = values.get("backup_plan")
    if chosen in ("smart", "custom"):
        return chosen
    if not values["backup_nightly"] or values["backup_schedule"] == "off":
        return "custom"
    if values["backup_mode"] == "smart":
        return "smart"
    untouched = values["backup_mode"] == "last" and values["backup_keep"] == 14 and values["backup_schedule"] == "daily"
    return "smart" if untouched else "custom"


def effective(values: dict) -> dict:
    """The backup settings that apply. Smart Recycle means one backup a day, thinned out smartly."""
    out = {**values, "backup_plan": plan_of(values)}
    if out["backup_plan"] == "smart":
        out.update(backup_nightly=True, backup_schedule="daily", backup_mode="smart")
    return out


def schedule(conn=None) -> str:
    """The backup schedule. Older installs only had the on/off switch "backup_nightly"."""
    if conn is None:
        with db.session() as c:
            return schedule(c)
    values = effective(settings.get_all(conn))
    if not values["backup_nightly"]:
        return "off"
    return values["backup_schedule"]


def cron_fields(sched: str, hour: int) -> dict | None:
    """APScheduler cron fields for a schedule; None when backups are off."""
    hour = int(hour) % 24
    if sched == "hourly":
        return {"minute": "0"}
    if sched == "6h":
        return {"hour": ",".join(str(hour % 6 + 6 * i) for i in range(4)), "minute": "0"}
    if sched == "twice":
        return {"hour": f"{hour % 12},{hour % 12 + 12}", "minute": "0"}
    if sched == "daily":
        return {"hour": str(hour), "minute": "0"}
    if sched == "weekly":
        return {"day_of_week": "sun", "hour": str(hour), "minute": "0"}
    return None


# --- retention -----------------------------------------------------------------------


@dataclass
class Policy:
    mode: str = "last"
    keep: int = 14
    days: int = 30
    smart_days: int = 7
    smart_weeks: int = 4
    smart_months: int = 12
    smart_years: int = 3
    max: int = 0  # 0 = no limit

    @classmethod
    def from_settings(cls, values: dict) -> "Policy":
        values = effective(values)
        return cls(
            mode=values["backup_mode"],
            keep=values["backup_keep"],
            days=values["backup_days"],
            smart_days=values["backup_smart_days"],
            smart_weeks=values["backup_smart_weeks"],
            smart_months=values["backup_smart_months"],
            smart_years=values["backup_smart_years"],
            max=values["backup_max"],
        )


def _smart_keep(items: list[tuple[str, dt.datetime]], p: Policy, now: dt.datetime) -> set[str]:
    keep = {name for name, when in items if now - when <= dt.timedelta(hours=24)}
    today = now.date()
    this_monday = today - dt.timedelta(days=today.weekday())
    tiers = [
        (p.smart_days, lambda d: d, lambda d: (today - d).days),
        (p.smart_weeks, lambda d: d - dt.timedelta(days=d.weekday()), lambda d: (this_monday - d).days // 7),
        (p.smart_months, lambda d: (d.year, d.month), lambda m: (today.year - m[0]) * 12 + today.month - m[1]),
        (p.smart_years, lambda d: d.year, lambda y: today.year - y),
    ]
    for count, bucket_of, age_of in tiers:
        if count <= 0:
            continue
        seen = set()
        for name, when in items:  # newest first, so the first one per bucket is its newest
            bucket = bucket_of(when.date())
            if bucket in seen:
                continue
            seen.add(bucket)
            if 0 <= age_of(bucket) < count:
                keep.add(name)
    return keep


def plan(items: list[tuple[str, dt.datetime, bool]], p: Policy, now: dt.datetime | None = None) -> set[str]:
    """Names to keep. ``items`` are (name, created, pinned)."""
    now = now or dt.datetime.now()
    free = sorted(((n, w) for n, w, pinned in items if not pinned), key=lambda x: x[1], reverse=True)
    if not free:
        return {n for n, _, _ in items}
    if p.mode == "smart":
        keep = _smart_keep(free, p, now)
    elif p.mode == "days":
        keep = {n for n, w in free if now - w < dt.timedelta(days=p.days)}
    else:
        keep = {n for n, _ in free[: max(1, p.keep)]}
    keep.add(free[0][0])
    if p.max > 0:
        ordered = [n for n, _ in free if n in keep]
        keep = set(ordered[: p.max])
    return keep | {n for n, _, pinned in items if pinned}


def _items(index: dict) -> list[tuple[str, dt.datetime, bool]]:
    return [(f.name, _when(f.name), bool((index.get(f.name) or {}).get("pinned"))) for f in _files()]


def preview(values: dict) -> list[str]:
    """Backups the given (unsaved) settings would remove at the next backup."""
    policy = Policy.from_settings(values)
    items = _items(_load_index())
    keep = plan(items, policy)
    return sorted((n for n, _, _ in items if n not in keep), reverse=True)


def prune() -> list[str]:
    with db.session() as conn:
        policy = Policy.from_settings(settings.get_all(conn))
    with _lock:
        index = _load_index()
        items = _items(index)
        keep = plan(items, policy)
        removed = []
        for name, _, _ in items:
            if name not in keep:
                (config.BACKUP_DIR / name).unlink(missing_ok=True)
                removed.append(name)
        if removed:
            _save_index(index)
    return removed


# --- pin and delete ----------------------------------------------------------------


def set_pinned(name: str, pinned: bool) -> dict | None:
    path = path_for(name)
    if not path:
        return None
    with _lock:
        index = _load_index()
        entry = index.setdefault(name, {})
        entry["pinned"] = bool(pinned)
        info = _describe(path, index)
        _save_index(index)
    return info


def delete(name: str) -> bool:
    path = path_for(name)
    if not path:
        return False
    with _lock:
        path.unlink(missing_ok=True)
        _save_index(_load_index())
    return True


# --- restore -------------------------------------------------------------------------


def _check(path) -> None:
    try:
        conn = _open_ro(path)
        try:
            if conn.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                raise RestoreError("This backup is damaged.")
            row = conn.execute("SELECT value FROM meta WHERE key = 'schema_version'").fetchone()
            conn.execute("SELECT COUNT(*) FROM transactions").fetchone()
        finally:
            conn.close()
    except sqlite3.Error as exc:
        raise RestoreError("This file is not a Groschen backup.") from exc
    if not row or int(row[0]) > db.SCHEMA_VERSION:
        raise RestoreError("This backup is from a newer Groschen version.")


def restore(name: str) -> dict:
    """Put the database back to the state of a backup.

    First saves the current state as a "safety" backup, so a restore can itself be undone.
    The login (users, sessions, passkeys and the login settings) and the backup settings
    stay as they are now.
    """
    path = path_for(name)
    if not path:
        raise FileNotFoundError(name)
    _check(path)
    safety = create("safety", prune_after=False)

    with db.session() as conn:
        login = {table: db.rows(conn.execute(f"SELECT * FROM {table}")) for table in LOGIN_TABLES}
        policy = {k: v for k, v in settings.get_all(conn).items() if k in POLICY_KEYS + LOGIN_KEYS}

    src = _open_ro(path)
    dst = db.connect()
    try:
        src.backup(dst)
    finally:
        src.close()
        dst.close()

    with db.session() as conn:
        conn.execute("PRAGMA journal_mode = WAL")
        # A backup from an older version may lack the newer login tables and columns.
        conn.executescript(db.SCHEMA)
        db.add_columns(conn)
        for table in reversed(LOGIN_TABLES):
            conn.execute(f"DELETE FROM {table}")
        for table in LOGIN_TABLES:
            for r in login[table]:
                cols = ", ".join(r)
                marks = ", ".join("?" for _ in r)
                conn.execute(f"INSERT INTO {table} ({cols}) VALUES ({marks})", tuple(r.values()))
        for key, value in policy.items():
            settings.put(conn, key, value)
    db.init()

    from .categorize.engine import Categorizer

    Categorizer._example_cache.clear()
    log.info("Restored backup %s (safety copy %s)", name, safety["name"])
    return {"restored": name, "safety": safety["name"]}
