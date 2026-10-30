"""Start Groschen: ``python -m groschen``."""

import logging
import os

import uvicorn

from . import config, db, market, netguard, scheduler
from .bank import sync


def drop_root() -> None:
    """Hand the data folder to the app user and stop running as root.

    Unraid creates a missing appdata folder as root, so the container starts as root,
    takes ownership of the data folder and then switches for good to PUID/PGID
    (Unraid's nobody:users, 99:100, unless the template says otherwise).
    """
    if not hasattr(os, "geteuid") or os.geteuid() != 0:
        return
    uid = int(os.environ.get("PUID", "99"))
    gid = int(os.environ.get("PGID", "100"))
    if uid == 0:
        logging.getLogger("groschen").warning("PUID is 0, so Groschen keeps running as root")
        return
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    for root, dirs, files in os.walk(config.DATA_DIR):
        for name in [root, *(os.path.join(root, d) for d in dirs), *(os.path.join(root, f) for f in files)]:
            st = os.lstat(name)
            if st.st_uid != uid or st.st_gid != gid:
                os.lchown(name, uid, gid)
    os.chmod(config.DATA_DIR, 0o700)
    os.setgroups([])
    os.setgid(gid)
    os.setuid(uid)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    # Database, key and backups are readable by the app user only.
    os.umask(0o077)
    drop_root()
    # Install the network guard before anything else can open a connection.
    netguard.install()
    sync.allow_bank_hosts()
    db.init()
    with db.session() as conn:
        market.apply_setting(conn)
    scheduler.start()
    from .main import app

    logging.getLogger("groschen").info("Groschen %s listening on port %s", config.VERSION, config.PORT)
    uvicorn.run(app, host="0.0.0.0", port=config.PORT, log_level="warning", server_header=False, proxy_headers=False)


if __name__ == "__main__":
    main()
