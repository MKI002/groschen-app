"""User preferences, stored as JSON values in the settings table."""

import json

from . import regions

DEFAULTS = {
    "setup_complete": False,
    "categorizer": "model",  # "model" or "rules"
    "language": None,  # "de" or "en"; None follows the browser until chosen
    "country": "",  # home country (regions.py): number and date format, how bank files' dates are read; "" = not chosen
    "currency": "EUR",  # home currency: every total is shown in it, other currencies are converted (fx.py)
    "online_rates": False,  # fetch daily exchange rates from the ECB (fx.py); off until turned on
    "sync_schedule": "daily",  # "daily" (06:00), "twice" (06:00 and 18:00), "6h"
    "reminder_days": 15,  # remind this many days before the 90-day bank login is due
    "unusual_alerts": True,  # point out the costliest month on the Overview page
    "payday_shift": True,  # count end-of-month salary toward the next month (see analytics/paydays.py)
    "review_uncertain": True,
    "risk_free_rate": 1.75,  # % p.a., used for the Sharpe ratio
    "tax_allowance": 1000,  # Sparerpauschbetrag in euros (2000 for couples)
    "online_prices": False,  # fetch ETF price history from justETF (market.py); off until turned on
    "alert_duplicates": True,  # hint at the same amount charged twice
    "alert_price_up": True,  # hint when a subscription changes its price (up or down)
    "alert_subscriptions": True,  # hint at a new subscription, one that stopped and one that came back
    "alert_unusual": True,  # hint at payments far above the usual amount
    "alert_large": 250,  # also hint at a first payment to a new merchant from this amount (0 = off)
    "safe_buffer": 0,  # euros kept aside in "Available until payday"
    "backup_plan": "",  # "smart" (Smart Recycle, once a day) or "custom"; "" = not chosen yet (see backup.effective)
    "backup_nightly": True,  # master switch; off also when backup_schedule is "off" (see backup.schedule)
    "backup_schedule": "daily",  # "hourly", "6h", "twice", "daily", "weekly" (Sundays) or "off"
    "backup_hour": 3,  # hour of the day for daily/weekly backups (and the first of twice/6h)
    "backup_mode": "smart",  # retention: "last" N, all from the last N "days", or "smart" (see backup.py)
    "backup_keep": 14,
    "backup_days": 30,
    "backup_smart_days": 7,
    "backup_smart_weeks": 4,
    "backup_smart_months": 12,
    "backup_smart_years": 3,
    "backup_max": 0,  # at most this many backups in any mode (0 = no limit)
    "holder_names": [],  # the user's own names (from the bank): transfers to them are own transfers
    "session_days": 30,  # a login lasts this many days at most
    "idle_minutes": 0,  # log out after this many minutes without use (0 = never)
    "login_max_failures": 10,  # failed logins from one address before it has to wait
    "login_lock_minutes": 15,  # how long it waits
    "password_login": True,  # off only while at least one passkey exists (see update)
}


def get_all(conn) -> dict:
    values = dict(DEFAULTS)
    for row in conn.execute("SELECT key, value FROM settings"):
        try:
            values[row["key"]] = json.loads(row["value"])
        except ValueError:
            continue
    return values


def get(conn, key: str):
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    if row is None:
        return DEFAULTS.get(key)
    return json.loads(row["value"])


def put(conn, key: str, value) -> None:
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, json.dumps(value)),
    )


CHOICES = {
    "categorizer": ("model", "rules"),
    "language": ("de", "en"),
    "country": ("", *regions.COUNTRIES),
    "currency": regions.CURRENCIES,
    "sync_schedule": ("daily", "twice", "6h"),
    "backup_schedule": ("hourly", "6h", "twice", "daily", "weekly", "off"),
    "backup_mode": ("last", "days", "smart"),
    "backup_plan": ("smart", "custom"),
}
LIMITS = {
    "reminder_days": (1, 60),
    "risk_free_rate": (-5.0, 20.0),
    "tax_allowance": (0, 10000),
    "backup_keep": (1, 365),
    "backup_hour": (0, 23),
    "backup_days": (1, 3650),
    "backup_smart_days": (0, 365),
    "backup_smart_weeks": (0, 520),
    "backup_smart_months": (0, 240),
    "backup_smart_years": (0, 50),
    "backup_max": (0, 1000),
    "alert_large": (0, 100000),
    "safe_buffer": (0, 1000000),
    "session_days": (1, 365),
    "idle_minutes": (0, 1440),
    "login_max_failures": (3, 100),
    "login_lock_minutes": (1, 1440),
}


def _clean(key: str, value):
    """Check a value from the Settings page against the type and range of its default."""
    default = DEFAULTS[key]
    if isinstance(default, list):
        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            raise ValueError(f"{key} must be a list of names")
        names = list(dict.fromkeys(" ".join(v.split())[:80] for v in value if v.strip()))
        if len(names) > 6:
            raise ValueError(f"{key} takes at most 6 names")
        return names
    if key in CHOICES:
        if value not in CHOICES[key]:
            raise ValueError(f"{key} must be one of {', '.join(CHOICES[key])}")
        return value
    if isinstance(default, bool):
        if not isinstance(value, bool):
            raise ValueError(f"{key} must be true or false")
        return value
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{key} must be a number")
    lo, hi = LIMITS[key]
    if not lo <= value <= hi:
        raise ValueError(f"{key} must be between {lo} and {hi}")
    return int(value) if isinstance(default, int) else float(value)


def update(conn, values: dict) -> dict:
    """Save the known settings in ``values``. Raises ValueError before saving anything invalid."""
    clean = {k: _clean(k, v) for k, v in values.items() if k in DEFAULTS and k != "setup_complete"}
    # The schedule picker replaced the old on/off switch; keep both in step.
    if "backup_schedule" in clean:
        clean["backup_nightly"] = clean["backup_schedule"] != "off"
    elif clean.get("backup_nightly") and get(conn, "backup_schedule") == "off":
        clean["backup_schedule"] = "daily"
    # Turning the password off would lock the user out without a passkey to log in with.
    if clean.get("password_login") is False and not conn.execute("SELECT 1 FROM passkeys LIMIT 1").fetchone():
        raise ValueError("Add a passkey before turning off the password login.")
    for key, value in clean.items():
        put(conn, key, value)
    return get_all(conn)
