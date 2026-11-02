"""Fingerprint login for the Android app.

The app makes a key pair inside the phone's secure hardware (Android Keystore). The phone
only signs with it after a fingerprint, face or phone PIN check, and the private half never
leaves the chip. Groschen keeps the public half; at every login it hands out a fresh random
challenge and checks the signature over it.

Nothing secret travels to log in: no password is stored on the phone, and a signature is
good for one challenge only. That is why this also works on a plain http:// address on the
home network, where browsers refuse passkeys.

Each phone gets one login session: a new fingerprint login ends the phone's previous one, and
removing the phone (Settings → Security) ends its session too.
"""

import base64
import binascii
import secrets
import threading
import time

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

from . import db

CHALLENGE_SECONDS = 2 * 60
MAX_PENDING = 200
MAX_DEVICES = 20

# What the phone signs: a label for the purpose, then the challenge. A signature made to add
# a phone can't be replayed as a login, and the other way round.
LOGIN = b"groschen-device-login:"
REGISTER = b"groschen-device-register:"

# Challenges handed out and not used yet, by a random id: (challenge, purpose, user id or None, expiry).
_pending: dict[str, tuple[bytes, bytes, int | None, float]] = {}
_lock = threading.Lock()


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


def _unb64(text: str) -> bytes | None:
    try:
        return base64.b64decode(text, validate=True)
    except (binascii.Error, ValueError, TypeError):
        return None


def challenge(purpose: bytes, user_id: int | None = None) -> dict:
    """A fresh challenge for the phone to sign, and the id it is answered with."""
    value = secrets.token_bytes(32)
    key = secrets.token_urlsafe(24)
    now = time.monotonic()
    with _lock:
        for k in [k for k, v in _pending.items() if v[3] < now]:
            del _pending[k]
        while len(_pending) >= MAX_PENDING:
            del _pending[next(iter(_pending))]
        _pending[key] = (value, purpose, user_id, now + CHALLENGE_SECONDS)
    return {"challenge_id": key, "challenge": _b64(value)}


def _take(key: str, purpose: bytes, user_id: int | None) -> bytes | None:
    """The challenge for ``key``, once: a challenge can't be used twice."""
    with _lock:
        item = _pending.pop(key, None)
    if not item or item[3] < time.monotonic() or item[1] != purpose or item[2] != user_id:
        return None
    return item[0]


def _public_key(der: bytes) -> ec.EllipticCurvePublicKey | None:
    """A P-256 public key in the form Android hands it out (X.509 SubjectPublicKeyInfo)."""
    try:
        key = serialization.load_der_public_key(der)
    except (ValueError, TypeError):
        return None
    if not isinstance(key, ec.EllipticCurvePublicKey) or not isinstance(key.curve, ec.SECP256R1):
        return None
    return key


def _signed(key: ec.EllipticCurvePublicKey, signature: bytes, message: bytes) -> bool:
    try:
        key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
        return True
    except (InvalidSignature, ValueError):
        return False


def register(conn, user_id: int, challenge_id: str, public_key: str, signature: str, name: str) -> dict | None:
    """Add a phone: its public key, proven by a signature over a challenge. None if that fails."""
    value = _take(challenge_id, REGISTER, user_id)
    der = _unb64(public_key)
    sig = _unb64(signature)
    if value is None or not der or not sig or len(der) > 400 or len(sig) > 200:
        return None
    key = _public_key(der)
    if key is None or not _signed(key, sig, REGISTER + value):
        return None
    if conn.execute("SELECT COUNT(*) FROM devices WHERE user_id = ?", (user_id,)).fetchone()[0] >= MAX_DEVICES:
        return None
    key_id = secrets.token_urlsafe(18)
    label = " ".join(name.split())[:60] or "Android"
    cur = conn.execute(
        "INSERT INTO devices (user_id, key_id, public_key, name, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, key_id, der, label, db.now_iso()),
    )
    item = next(d for d in list_for(conn, user_id) if d["id"] == cur.lastrowid)
    return item | {"key_id": key_id}


def verify_login(conn, key_id: str, challenge_id: str, signature: str) -> tuple[int, int] | None:
    """(user id, device id) for a good signature, or None if the login failed."""
    value = _take(challenge_id, LOGIN, None)
    sig = _unb64(signature)
    if value is None or not sig or len(sig) > 200:
        return None
    row = db.one(conn.execute("SELECT id, user_id, public_key FROM devices WHERE key_id = ?", (key_id,)))
    if not row:
        return None
    key = _public_key(bytes(row["public_key"]))
    if key is None or not _signed(key, sig, LOGIN + value):
        return None
    conn.execute("UPDATE devices SET last_used_at = ? WHERE id = ?", (db.now_iso(), row["id"]))
    return row["user_id"], row["id"]


def list_for(conn, user_id: int) -> list[dict]:
    return db.rows(
        conn.execute(
            "SELECT id, name, created_at, last_used_at FROM devices WHERE user_id = ? ORDER BY id",
            (user_id,),
        )
    )


def remove(conn, user_id: int, device_id: int) -> bool:
    """Forget a phone and end its login session."""
    if conn.execute("DELETE FROM devices WHERE id = ? AND user_id = ?", (device_id, user_id)).rowcount != 1:
        return False
    conn.execute("DELETE FROM sessions WHERE device_id = ?", (device_id,))
    return True
