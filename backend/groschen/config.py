"""Runtime configuration.

Everything a user can change lives in the database and is edited in the web UI.
The only values read from the environment are the ones the Docker setup decides:
where the data folder is, which port to listen on and the time zone. One more,
GROSCHEN_ALLOW_PASSWORD=1, is a way back in if every passkey is lost while the
password login is off (see api/auth.py).
"""

import os
from pathlib import Path

VERSION = "0.1.0"

DATA_DIR = Path(os.environ.get("GROSCHEN_DATA", "/data"))
PORT = int(os.environ.get("GROSCHEN_PORT", "8420"))
TZ = os.environ.get("TZ") or "Europe/Berlin"

_PKG_DIR = Path(__file__).resolve().parent
STATIC_DIR = Path(os.environ.get("GROSCHEN_STATIC", str(_PKG_DIR / "static")))
MODEL_DIR = Path(os.environ.get("GROSCHEN_MODEL", str(_PKG_DIR.parent / "model")))

DB_PATH = DATA_DIR / "groschen.db"
KEY_PATH = DATA_DIR / "secret.key"
BACKUP_DIR = DATA_DIR / "backups"
