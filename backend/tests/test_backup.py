import datetime as dt

from groschen import backup, config, db, settings
from groschen.backup import Policy, plan

NOW = dt.datetime(2026, 9, 28, 12, 0)


def daily(days: int, hour: int = 3):
    """One backup a day at 03:00 for the last ``days`` days, newest first."""
    out = []
    for i in range(days):
        when = (NOW - dt.timedelta(days=i)).replace(hour=hour, minute=0)
        out.append((f"groschen-{when:%Y%m%d-%H%M%S}-auto.db", when, False))
    return out


def test_last_keeps_the_newest():
    items = daily(30)
    keep = plan(items, Policy(mode="last", keep=5), NOW)
    assert keep == {n for n, _, _ in items[:5]}


def test_days_keeps_a_time_window():
    items = daily(30)
    keep = plan(items, Policy(mode="days", days=10), NOW)
    assert len(keep) == 10


def test_smart_thins_out_older_backups():
    items = daily(3 * 365)
    keep = plan(items, Policy(mode="smart", smart_days=7, smart_weeks=4, smart_months=12, smart_years=3), NOW)
    kept = sorted((w for n, w, _ in items if n in keep), reverse=True)
    # A week of dailies, then roughly weekly, monthly and yearly ones.
    assert all(k.date() >= (NOW - dt.timedelta(days=6)).date() for k in kept[:7])
    assert 7 + 3 <= len(kept) <= 7 + 4 + 12 + 3
    assert kept[-1].year == NOW.year - 2
    # Past the weekly window, at most one per month.
    old = [k for k in kept if (NOW - k).days > 60]
    assert len({(k.year, k.month) for k in old}) == len(old)


def test_smart_is_stable_over_time():
    """A backup the smart plan drops today never comes back, and one it keeps as a monthly stays."""
    items = daily(400)
    p = Policy(mode="smart", smart_days=7, smart_weeks=4, smart_months=12, smart_years=0)
    alive = list(items)
    for step in range(60):
        now = NOW + dt.timedelta(days=step)
        when = now.replace(hour=3, minute=0)
        alive.insert(0, (f"groschen-{when:%Y%m%d-%H%M%S}-auto.db", when, False))
        keep = plan(alive, p, now)
        alive = [i for i in alive if i[0] in keep]
    assert 7 + 3 <= len(alive) <= 7 + 4 + 12


def test_max_and_pins():
    items = daily(30)
    pinned_name = items[-1][0]
    items[-1] = (pinned_name, items[-1][1], True)
    keep = plan(items, Policy(mode="days", days=365, max=10), NOW)
    assert pinned_name in keep
    assert len(keep) == 11
    assert items[0][0] in keep


def test_newest_always_stays():
    items = daily(3)
    keep = plan(items, Policy(mode="days", days=1), NOW + dt.timedelta(days=5))
    assert keep == {items[0][0]}


def test_schedule_follows_old_switch(conn):
    assert backup.schedule(conn) == "daily"
    settings.update(conn, {"backup_nightly": False})
    assert backup.schedule(conn) == "off"
    settings.update(conn, {"backup_schedule": "weekly", "backup_plan": "custom"})
    assert backup.schedule(conn) == "weekly" and settings.get(conn, "backup_nightly") is True
    settings.update(conn, {"backup_plan": "smart"})
    assert backup.schedule(conn) == "daily"  # Smart Recycle: once a day
    assert backup.cron_fields("twice", 3) == {"hour": "3,15", "minute": "0"}
    assert backup.cron_fields("6h", 3) == {"hour": "3,9,15,21", "minute": "0"}
    assert backup.cron_fields("off", 3) is None


def test_restore_brings_back_data_and_keeps_login(conn):
    conn.execute("INSERT INTO users (username, name, password_hash, created_at) VALUES ('a', 'A', 'x', 'now')")
    conn.execute("INSERT INTO sessions (token_hash, user_id, created_at, expires_at) VALUES ('tok', 1, 'now', '2999-01-01')")
    conn.execute("INSERT INTO accounts (kind, name, created_at) VALUES ('giro', 'Giro', 'now')")
    conn.commit()
    first = backup.create("manual")
    assert first["accounts"] == 1 and first["kind"] == "manual"

    conn.execute("INSERT INTO accounts (kind, name, created_at) VALUES ('giro', 'Second', 'now')")
    conn.execute(
        "INSERT INTO sessions (token_hash, user_id, created_at, expires_at) VALUES ('tok2', 1, 'now', '2999-01-01')"
    )
    conn.commit()
    settings.update(conn, {"backup_mode": "smart"})
    conn.commit()

    result = backup.restore(first["name"])
    with db.session() as c:
        assert c.execute("SELECT COUNT(*) FROM accounts").fetchone()[0] == 1
        assert c.execute("SELECT COUNT(*) FROM sessions").fetchone()[0] == 2  # still logged in
        assert settings.get(c, "backup_mode") == "smart"  # backup settings stay current
    names = [b["name"] for b in backup.list_backups()]
    assert result["safety"] in names and first["name"] in names

    # The safety copy undoes the restore.
    backup.restore(result["safety"])
    with db.session() as c:
        assert c.execute("SELECT COUNT(*) FROM accounts").fetchone()[0] == 2


def test_restore_refuses_broken_files():
    config.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    bad = config.BACKUP_DIR / "groschen-20260101-030000-auto.db"
    bad.write_bytes(b"not a database" * 100)
    try:
        backup.restore(bad.name)
    except backup.RestoreError:
        pass
    else:
        raise AssertionError("expected RestoreError")


def test_pin_survives_prune(conn):
    settings.update(conn, {"backup_plan": "custom", "backup_mode": "last", "backup_keep": 1})
    conn.commit()
    a = backup.create("manual")
    backup.set_pinned(a["name"], True)
    backup.create("manual")
    backup.create("manual")
    names = {b["name"]: b for b in backup.list_backups()}
    assert a["name"] in names and names[a["name"]]["pinned"]
    assert len(names) == 2


def test_older_installs_get_smart_recycle():
    base = dict(settings.DEFAULTS)
    assert backup.plan_of(base) == "smart"
    old_default = {**base, "backup_mode": "last", "backup_keep": 14, "backup_schedule": "daily"}
    assert backup.plan_of(old_default) == "smart"
    old_preset = {**base, "backup_mode": "smart", "backup_schedule": "6h", "backup_max": 60}
    assert backup.effective(old_preset)["backup_schedule"] == "daily"
    assert backup.plan_of({**old_default, "backup_keep": 30}) == "custom"
    assert backup.plan_of({**base, "backup_nightly": False}) == "custom"
    assert backup.plan_of({**old_default, "backup_keep": 30, "backup_plan": "smart"}) == "smart"
