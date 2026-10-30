"""Passkey login (WebAuthn).

A passkey is a key pair kept by the phone, laptop or security key. Groschen stores only
the public half and checks a signature over a fresh random challenge at each login.

Browsers allow passkeys only on a secure page with a real name: https://nas.example.ts.net
works, http://192.168.1.20:8420 doesn't (http://localhost is the one exception). The
name ("relying party ID") is taken from the browser's Origin header, and each passkey is
saved with the name it was made for, so it is only accepted on that same address.
"""

import ipaddress
import json
import secrets
import threading
import time
from dataclasses import dataclass
from urllib.parse import urlsplit

import webauthn
from webauthn.helpers import bytes_to_base64url
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    AuthenticatorTransport,
    PublicKeyCredentialDescriptor,
    ResidentKeyRequirement,
    UserVerificationRequirement,
)

from . import db

RP_NAME = "Groschen"
CHALLENGE_SECONDS = 5 * 60
MAX_PENDING = 200


@dataclass(frozen=True)
class Party:
    rp_id: str
    origin: str


def party_for(origin: str | None) -> Party | None:
    """The relying party for a page at ``origin``, or None where browsers don't allow passkeys."""
    if not origin:
        return None
    try:
        parts = urlsplit(origin)
        host = parts.hostname
    except ValueError:
        return None
    if not host or parts.path not in ("", "/") or parts.query or parts.username:
        return None
    if parts.scheme != "https" and not (parts.scheme == "http" and host == "localhost"):
        return None
    try:
        ipaddress.ip_address(host)
        return None
    except ValueError:
        pass
    return Party(rp_id=host, origin=f"{parts.scheme}://{parts.netloc}")


# Challenges handed out and not used yet, by a random id: (challenge, party, user id or None, expiry).
_pending: dict[str, tuple[bytes, Party, int | None, float]] = {}
_lock = threading.Lock()


def _remember(challenge: bytes, party: Party, user_id: int | None) -> str:
    now = time.monotonic()
    key = secrets.token_urlsafe(24)
    with _lock:
        for k in [k for k, v in _pending.items() if v[3] < now]:
            del _pending[k]
        while len(_pending) >= MAX_PENDING:
            del _pending[next(iter(_pending))]
        _pending[key] = (challenge, party, user_id, now + CHALLENGE_SECONDS)
    return key


def _take(key: str, party: Party, user_id: int | None) -> bytes | None:
    """The challenge for ``key``, once: a challenge can't be used twice."""
    with _lock:
        item = _pending.pop(key, None)
    if not item or item[3] < time.monotonic() or item[1] != party or item[2] != user_id:
        return None
    return item[0]


def _options(opts) -> dict:
    return json.loads(webauthn.options_to_json(opts))


def _transports(raw: str | None) -> list[AuthenticatorTransport]:
    out = []
    for name in json.loads(raw or "[]"):
        try:
            out.append(AuthenticatorTransport(name))
        except ValueError:
            continue
    return out


def register_options(conn, party: Party, user: dict) -> dict:
    existing = db.rows(
        conn.execute(
            "SELECT credential_id, transports FROM passkeys WHERE user_id = ? AND rp_id = ?", (user["id"], party.rp_id)
        )
    )
    opts = webauthn.generate_registration_options(
        rp_id=party.rp_id,
        rp_name=RP_NAME,
        user_name=user["username"],
        user_display_name=user["name"],
        user_id=f"groschen-user-{user['id']}".encode(),
        # Saved on the device, so the login page needs no username first.
        authenticator_selection=AuthenticatorSelectionCriteria(
            resident_key=ResidentKeyRequirement.REQUIRED,
            user_verification=UserVerificationRequirement.REQUIRED,
        ),
        exclude_credentials=[
            PublicKeyCredentialDescriptor(
                id=webauthn.base64url_to_bytes(r["credential_id"]), transports=_transports(r["transports"])
            )
            for r in existing
        ],
        timeout=CHALLENGE_SECONDS * 1000,
    )
    return {"challenge_id": _remember(opts.challenge, party, user["id"]), "options": _options(opts)}


def _device_name(agent: str | None) -> str:
    a = (agent or "").lower()
    for needle, name in (
        ("iphone", "iPhone"),
        ("ipad", "iPad"),
        ("android", "Android"),
        ("macintosh", "Mac"),
        ("windows", "Windows"),
        ("linux", "Linux"),
    ):
        if needle in a:
            return name
    return "Passkey"


def register(
    conn, party: Party, user_id: int, challenge_id: str, credential: dict, name: str, agent: str | None
) -> dict | None:
    challenge = _take(challenge_id, party, user_id)
    if challenge is None:
        return None
    try:
        verified = webauthn.verify_registration_response(
            credential=credential,
            expected_challenge=challenge,
            expected_rp_id=party.rp_id,
            expected_origin=party.origin,
            require_user_verification=True,
        )
    except Exception:  # noqa: BLE001 - any malformed or failed response is a failed registration
        return None
    transports = credential.get("response", {}).get("transports") if isinstance(credential.get("response"), dict) else None
    if not isinstance(transports, list) or not all(isinstance(t, str) for t in transports):
        transports = []
    cred_id = bytes_to_base64url(verified.credential_id)
    if conn.execute("SELECT 1 FROM passkeys WHERE credential_id = ?", (cred_id,)).fetchone():
        return None
    label = " ".join(name.split())[:60] or _device_name(agent)
    cur = conn.execute(
        "INSERT INTO passkeys (user_id, credential_id, public_key, sign_count, rp_id, name, transports, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            user_id,
            cred_id,
            verified.credential_public_key,
            verified.sign_count,
            party.rp_id,
            label,
            json.dumps(transports[:8]),
            db.now_iso(),
        ),
    )
    return next(p for p in list_for(conn, user_id) if p["id"] == cur.lastrowid)


def login_options(party: Party) -> dict:
    opts = webauthn.generate_authentication_options(
        rp_id=party.rp_id,
        user_verification=UserVerificationRequirement.REQUIRED,
        timeout=CHALLENGE_SECONDS * 1000,
    )
    return {"challenge_id": _remember(opts.challenge, party, None), "options": _options(opts)}


def verify_login(conn, party: Party, challenge_id: str, credential: dict) -> int | None:
    """The user id the passkey belongs to, or None if the login failed."""
    challenge = _take(challenge_id, party, None)
    cred_id = credential.get("id")
    if challenge is None or not isinstance(cred_id, str):
        return None
    row = db.one(
        conn.execute(
            "SELECT id, user_id, public_key, sign_count FROM passkeys WHERE credential_id = ? AND rp_id = ?",
            (cred_id, party.rp_id),
        )
    )
    if not row:
        return None
    try:
        verified = webauthn.verify_authentication_response(
            credential=credential,
            expected_challenge=challenge,
            expected_rp_id=party.rp_id,
            expected_origin=party.origin,
            credential_public_key=bytes(row["public_key"]),
            credential_current_sign_count=row["sign_count"],
            require_user_verification=True,
        )
    except Exception:  # noqa: BLE001 - a bad signature, a replayed counter or a malformed response
        return None
    conn.execute(
        "UPDATE passkeys SET sign_count = ?, last_used_at = ? WHERE id = ?",
        (verified.new_sign_count, db.now_iso(), row["id"]),
    )
    return row["user_id"]


def list_for(conn, user_id: int) -> list[dict]:
    return db.rows(
        conn.execute(
            "SELECT id, name, rp_id, created_at, last_used_at FROM passkeys WHERE user_id = ? ORDER BY id",
            (user_id,),
        )
    )
