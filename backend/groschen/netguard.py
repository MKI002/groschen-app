"""Outbound network guard.

Groschen only ever talks to the bank, plus the ETF price server while "Online ETF
prices" is turned on in Settings (see market.py). Every name lookup in the process goes
through this guard: bank hosts and addresses on the local network are allowed,
everything else is refused. Connections are checked too, so code that skips the
name lookup and connects to a raw internet address is refused as well; only
addresses that a bank name resolved to, or local ones, get through. Each
outbound lookup is written to the connection log that the Settings page shows.
"""

import ipaddress
import logging
import socket
import threading
import time

from . import db, i18n

_original_getaddrinfo = socket.getaddrinfo
_original_connect = socket.socket.connect
_original_connect_ex = socket.socket.connect_ex
_allowed_hosts: set[str] = set()
_allowed_ips: set[str] = set()
_local = threading.local()
_last_logged: dict[tuple[str, bool], float] = {}
_lock = threading.Lock()
_installed = False

LOCAL_NAMES = {"localhost", "localhost.localdomain", ""}


def allow_host(host: str) -> None:
    _allowed_hosts.add(host.lower().rstrip("."))


def disallow_host(host: str) -> None:
    h = host.lower().rstrip(".")
    if h in _allowed_hosts:
        _allowed_hosts.discard(h)
        # Addresses aren't tracked per name; the bank's come back at its next lookup.
        _allowed_ips.clear()


def allowed_hosts() -> list[str]:
    return sorted(_allowed_hosts)


class purpose:
    """Label outbound connections made inside this block, e.g. ``with purpose("ING sync")``."""

    def __init__(self, label: str):
        self.label = label

    def __enter__(self):
        self.previous = getattr(_local, "purpose", None)
        _local.purpose = self.label

    def __exit__(self, *exc):
        _local.purpose = self.previous


def _is_local(host: str) -> bool:
    if host in LOCAL_NAMES:
        return True
    try:
        ip = ipaddress.ip_address(host.strip("[]").split("%")[0])
    except ValueError:
        return False
    return ip.is_private or ip.is_loopback or ip.is_unspecified or ip.is_link_local


def is_allowed(host: str) -> bool:
    h = host.lower().rstrip(".")
    return _is_local(h) or h in _allowed_hosts


def _log(host: str, allowed: bool) -> None:
    key = (host, allowed)
    now = time.monotonic()
    with _lock:
        # One log line per host per minute is plenty; a sync opens several connections.
        if now - _last_logged.get(key, -1e9) < 60:
            return
        _last_logged[key] = now
    try:
        with db.session() as conn:
            conn.execute(
                "INSERT INTO netlog (ts, host, purpose, allowed) VALUES (?, ?, ?, ?)",
                (db.now_iso(), host, getattr(_local, "purpose", None), int(allowed)),
            )
    except Exception as err:  # the log must never break a bank connection
        logging.getLogger("groschen.netguard").debug("Couldn't write the connection log: %s", err)


def _guarded_getaddrinfo(host, *args, **kwargs):
    if host is None:
        return _original_getaddrinfo(host, *args, **kwargs)
    name = host.decode() if isinstance(host, bytes) else str(host)
    h = name.lower().rstrip(".")
    if _is_local(h):
        return _original_getaddrinfo(host, *args, **kwargs)
    if h in _allowed_hosts:
        _log(h, True)
        result = _original_getaddrinfo(host, *args, **kwargs)
        for entry in result:
            try:
                _allowed_ips.add(str(entry[4][0]).split("%")[0])
            except (IndexError, TypeError):
                continue
        return result
    _log(h, False)
    raise socket.gaierror(socket.EAI_NONAME, f"Blocked by Groschen: {h} is not a bank server")


def _check_address(sock, address) -> None:
    if sock.family not in (socket.AF_INET, socket.AF_INET6) or not isinstance(address, tuple):
        return
    ip = str(address[0]).split("%")[0]
    if _is_local(ip) or ip in _allowed_ips:
        return
    _log(ip, False)
    raise ConnectionRefusedError(f"Blocked by Groschen: {ip} is not a bank server")


def _guarded_connect(self, address):
    _check_address(self, address)
    return _original_connect(self, address)


def _guarded_connect_ex(self, address):
    _check_address(self, address)
    return _original_connect_ex(self, address)


def install() -> None:
    global _installed
    if not _installed:
        socket.getaddrinfo = _guarded_getaddrinfo
        socket.socket.connect = _guarded_connect
        socket.socket.connect_ex = _guarded_connect_ex
        _installed = True


def recent(conn, days: int = 7) -> dict:
    since = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.time() - days * 86400))
    entries = db.rows(
        conn.execute("SELECT ts, host, purpose, allowed FROM netlog WHERE ts >= ? ORDER BY ts DESC LIMIT 200", (since,))
    )
    hosts = sorted({e["host"] for e in entries if e["allowed"]})
    blocked = sorted({e["host"] for e in entries if not e["allowed"]})
    shown = [{**e, "purpose": i18n.tr(e["purpose"])} for e in entries[:50]]
    return {"days": days, "count": len(entries), "hosts": hosts, "blocked": blocked, "entries": shown}
