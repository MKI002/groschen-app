"""Timed work: the bank sync, the nightly backup and housekeeping.

Times follow the TZ of the container (set it with TZ, Unraid passes its own).
"""

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from . import backup, config, db, fx, jobs, market, settings

log = logging.getLogger("groschen.scheduler")

SCHEDULES = {
    "daily": {"hour": "6", "minute": "0"},
    "twice": {"hour": "6,18", "minute": "0"},
    "6h": {"hour": "0,6,12,18", "minute": "5"},
}

_scheduler: BackgroundScheduler | None = None


def _sync() -> None:
    from .bank import sync

    with db.session() as conn:
        ready = settings.get(conn, "setup_complete")
        has_bank = conn.execute("SELECT COUNT(*) FROM connections").fetchone()[0] > 0
    if not ready or not has_bank or jobs.running("sync"):
        return
    jobs.start("sync", sync.sync_all)


def _prices() -> None:
    with db.session() as conn:
        on = market.enabled(conn)
    if on and not jobs.running("prices"):
        jobs.start("prices", market.refresh)


def _rates() -> None:
    try:
        fx.after_change()
    except Exception:  # pragma: no cover - rates must not stop the scheduler
        log.exception("Exchange rates failed")


def _backup() -> None:
    try:
        backup.scheduled()
    except Exception:  # pragma: no cover - a failed backup must not stop the scheduler
        log.exception("Scheduled backup failed")


def _housekeeping() -> None:
    with db.session() as conn:
        conn.execute("DELETE FROM sessions WHERE expires_at < ?", (db.now_iso(),))
        conn.execute("DELETE FROM netlog WHERE ts < datetime('now', '-180 days')")


def start() -> None:
    global _scheduler
    if _scheduler:
        return
    _scheduler = BackgroundScheduler(timezone=config.TZ, job_defaults={"coalesce": True, "misfire_grace_time": 3600})
    _scheduler.add_job(_housekeeping, CronTrigger(hour="4", minute="30", timezone=config.TZ), id="housekeeping")
    # Online ETF prices (only when turned on): after the morning sync, once European markets have closed the day before.
    _scheduler.add_job(_prices, CronTrigger(hour="6", minute="40", timezone=config.TZ), id="prices")
    # Exchange rates (only when turned on and needed): the ECB publishes them around 16:00 CET.
    _scheduler.add_job(_rates, CronTrigger(hour="6,17", minute="50", timezone=config.TZ), id="rates")
    _scheduler.start()
    reschedule()


def reschedule() -> None:
    """Apply the sync time and backup schedule from the Settings page."""
    if not _scheduler:
        return
    with db.session() as conn:
        schedule = settings.get(conn, "sync_schedule")
        backup_fields = backup.cron_fields(backup.schedule(conn), settings.get(conn, "backup_hour"))
    fields = SCHEDULES.get(schedule, SCHEDULES["daily"])
    _scheduler.add_job(_sync, CronTrigger(timezone=config.TZ, **fields), id="sync", replace_existing=True)
    if backup_fields:
        _scheduler.add_job(_backup, CronTrigger(timezone=config.TZ, **backup_fields), id="backup", replace_existing=True)
    elif _scheduler.get_job("backup"):
        _scheduler.remove_job("backup")


def next_runs() -> dict:
    if not _scheduler:
        return {}
    out = {}
    for job in _scheduler.get_jobs():
        if job.next_run_time:
            out[job.id] = job.next_run_time.isoformat(timespec="minutes")
    return out


def stop() -> None:
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
