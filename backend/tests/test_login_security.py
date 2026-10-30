"""Passkeys, login sessions and the login settings under Settings → Security."""

import base64
import hashlib
import json
import os
from datetime import datetime, timedelta, timezone

import cbor2
import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi.testclient import TestClient

from groschen import db, passkeys
from groschen.api import auth
from groschen.main import create_app

ACCOUNT = {"name": "Alex", "username": "alex", "password": "correct horse"}
HOST = "nas.example.ts.net"
ORIGIN = f"https://{HOST}"
H = {"x-groschen": "1", "origin": ORIGIN}


def b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


class SoftKey:
    """A passkey in software, doing what a phone or laptop does."""

    def __init__(self, rp_id=HOST, origin=ORIGIN):
        self.key = ec.generate_private_key(ec.SECP256R1())
        self.cred_id = os.urandom(16)
        self.count = 0
        self.rp_id = rp_id
        self.origin = origin

    def _cose(self) -> bytes:
        n = self.key.public_key().public_numbers()
        return cbor2.dumps({1: 2, 3: -7, -1: 1, -2: n.x.to_bytes(32, "big"), -3: n.y.to_bytes(32, "big")})

    def _auth_data(self, attested: bool) -> bytes:
        self.count += 1
        flags = 0x01 | 0x04 | (0x40 if attested else 0)  # user present, user verified, key attached
        data = hashlib.sha256(self.rp_id.encode()).digest() + bytes([flags]) + self.count.to_bytes(4, "big")
        if attested:
            data += bytes(16) + len(self.cred_id).to_bytes(2, "big") + self.cred_id + self._cose()
        return data

    def _client_data(self, kind: str, challenge: str) -> bytes:
        return json.dumps({"type": kind, "challenge": challenge, "origin": self.origin, "crossOrigin": False}).encode()

    def create(self, options: dict) -> dict:
        cd = self._client_data("webauthn.create", options["challenge"])
        att = cbor2.dumps({"fmt": "none", "attStmt": {}, "authData": self._auth_data(True)})
        return {
            "id": b64(self.cred_id),
            "rawId": b64(self.cred_id),
            "type": "public-key",
            "response": {"clientDataJSON": b64(cd), "attestationObject": b64(att), "transports": ["internal"]},
            "clientExtensionResults": {},
        }

    def get(self, options: dict) -> dict:
        cd = self._client_data("webauthn.get", options["challenge"])
        ad = self._auth_data(False)
        sig = self.key.sign(ad + hashlib.sha256(cd).digest(), ec.ECDSA(hashes.SHA256()))
        return {
            "id": b64(self.cred_id),
            "rawId": b64(self.cred_id),
            "type": "public-key",
            "response": {
                "clientDataJSON": b64(cd),
                "authenticatorData": b64(ad),
                "signature": b64(sig),
                "userHandle": b64(b"groschen-user-1"),
            },
            "clientExtensionResults": {},
        }


@pytest.fixture
def app():
    auth._failures.clear()
    auth.time.sleep = lambda s: None
    return create_app()


@pytest.fixture
def user(app):
    c = TestClient(app, base_url=ORIGIN)
    assert c.post("/api/setup/account", json=ACCOUNT, headers=H).status_code == 200
    return c


def add_passkey(c, key: SoftKey, name="") -> dict:
    start = c.post("/api/passkeys/options", headers=H).json()
    assert start["options"]["rp"]["id"] == HOST
    assert start["options"]["authenticatorSelection"]["residentKey"] == "required"
    r = c.post(
        "/api/passkeys",
        json={"challenge_id": start["challenge_id"], "credential": key.create(start["options"]), "name": name},
        headers={**H, "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0)"},
    )
    assert r.status_code == 200, r.text
    return r.json()


def passkey_login(c, key: SoftKey, headers=H):
    start = c.post("/api/login/passkey/options", headers=headers)
    if start.status_code != 200:
        return start
    body = start.json()
    return c.post(
        "/api/login/passkey",
        json={"challenge_id": body["challenge_id"], "credential": key.get(body["options"])},
        headers=headers,
    )


def test_passkeys_need_https_and_a_name():
    assert passkeys.party_for("https://nas.example.ts.net") == passkeys.Party(HOST, ORIGIN)
    assert passkeys.party_for("https://nas.local:8443").origin == "https://nas.local:8443"
    assert passkeys.party_for("http://localhost:8420").rp_id == "localhost"
    for bad in (
        None,
        "",
        "null",
        "http://nas:8420",
        "http://192.168.1.20:8420",
        "https://192.168.1.20",
        "https://[::1]",
    ):
        assert passkeys.party_for(bad) is None, bad


def test_passkey_register_and_login(app, user):
    key = SoftKey()
    item = add_passkey(user, key)
    assert item["name"] == "iPhone" and item["rp_id"] == HOST
    assert user.get("/api/status").json()["passkeys"] is True

    user.post("/api/logout", headers=H)
    assert user.get("/api/badges").status_code == 401
    r = passkey_login(user, key)
    assert r.status_code == 200, r.text
    assert "secure" in r.headers["set-cookie"].lower()
    assert user.get("/api/badges").status_code == 200
    assert user.get("/api/sessions").json()[0]["method"] == "passkey"
    assert user.get("/api/passkeys").json()[0]["last_used_at"]
    assert [e["method"] for e in user.get("/api/logins").json()] == ["passkey"]


def test_passkey_is_refused_elsewhere(app, user):
    key = SoftKey()
    add_passkey(user, key)
    user.post("/api/logout", headers=H)
    # Opened over the bare IP: browsers wouldn't allow it, and neither does Groschen.
    r = user.post("/api/login/passkey/options", headers={"x-groschen": "1", "origin": "http://192.168.1.20:8420"})
    assert r.status_code == 400
    # Another name: the passkey was made for nas.example.ts.net only.
    other = SoftKey(rp_id="other.example.ts.net", origin="https://other.example.ts.net")
    other.cred_id = key.cred_id
    other.key = key.key
    r = passkey_login(user, other, headers={"x-groschen": "1", "origin": "https://other.example.ts.net"})
    assert r.status_code == 401
    # A key nobody registered.
    assert passkey_login(user, SoftKey()).status_code == 401


def test_challenge_works_once(app, user):
    key = SoftKey()
    add_passkey(user, key)
    user.post("/api/logout", headers=H)
    start = user.post("/api/login/passkey/options", headers=H).json()
    body = {"challenge_id": start["challenge_id"], "credential": key.get(start["options"])}
    assert user.post("/api/login/passkey", json=body, headers=H).status_code == 200
    body["credential"] = key.get(start["options"])
    assert user.post("/api/login/passkey", json=body, headers=H).status_code == 401


def test_password_login_can_be_turned_off_only_with_a_passkey(app, user):
    assert user.patch("/api/settings", json={"password_login": False}, headers=H).status_code == 400
    key = SoftKey()
    item = add_passkey(user, key, name="  Mein   iPhone ")
    assert item["name"] == "Mein iPhone"
    assert user.patch("/api/settings", json={"password_login": False}, headers=H).status_code == 200

    other = TestClient(app, base_url=ORIGIN)
    assert other.get("/api/status").json()["password_login"] is False
    r = other.post("/api/login", json={"username": "alex", "password": ACCOUNT["password"]}, headers=H)
    assert r.status_code == 403

    # The last passkey gone: the password works again, so nobody is locked out.
    assert user.delete(f"/api/passkeys/{item['id']}", headers=H).json()["password_login"] is True
    assert other.post("/api/login", json={"username": "alex", "password": ACCOUNT["password"]}, headers=H).status_code == 200


def test_rescue_variable_allows_the_password(app, user, monkeypatch):
    add_passkey(user, SoftKey())
    user.patch("/api/settings", json={"password_login": False}, headers=H)
    monkeypatch.setenv(auth.RESCUE_ENV, "1")
    other = TestClient(app, base_url=ORIGIN)
    assert other.post("/api/login", json={"username": "alex", "password": ACCOUNT["password"]}, headers=H).status_code == 200


def test_rename_and_delete_only_own_passkeys(app, user):
    item = add_passkey(user, SoftKey())
    assert user.patch(f"/api/passkeys/{item['id']}", json={"name": "Laptop"}, headers=H).status_code == 200
    assert user.get("/api/passkeys").json()[0]["name"] == "Laptop"
    assert user.patch("/api/passkeys/999", json={"name": "x"}, headers=H).status_code == 404
    assert user.delete("/api/passkeys/999", headers=H).status_code == 404
    other = TestClient(app, base_url=ORIGIN)
    assert other.get("/api/passkeys").status_code == 401
    assert other.post("/api/passkeys/options", headers=H).status_code == 401


def test_sessions_list_and_end(app, user):
    other = TestClient(app, base_url=ORIGIN)
    assert other.post("/api/login", json={"username": "alex", "password": ACCOUNT["password"]}, headers=H).status_code == 200
    listed = user.get("/api/sessions").json()
    assert len(listed) == 2 and sum(s["current"] for s in listed) == 1
    theirs = next(s for s in listed if not s["current"])
    assert user.delete(f"/api/sessions/{theirs['id']}", headers=H).status_code == 200
    assert other.get("/api/badges").status_code == 401

    assert other.post("/api/login", json={"username": "alex", "password": ACCOUNT["password"]}, headers=H).status_code == 200
    assert user.post("/api/sessions/others", headers=H).json() == {"ended": 1}
    assert other.get("/api/badges").status_code == 401
    assert user.get("/api/badges").status_code == 200


def _age_sessions(**delta):
    old = (datetime.now(timezone.utc) - timedelta(**delta)).isoformat()
    with db.session() as conn:
        conn.execute("UPDATE sessions SET last_seen = ?, created_at = ?", (old, old))


def test_idle_timeout(user):
    _age_sessions(minutes=20)
    assert user.get("/api/badges").status_code == 200  # off by default
    user.patch("/api/settings", json={"idle_minutes": 15}, headers=H)
    _age_sessions(minutes=20)
    assert user.get("/api/badges").status_code == 401


def test_shorter_session_lifetime_ends_older_logins(user):
    user.patch("/api/settings", json={"session_days": 7}, headers=H)
    r = user.post("/api/login", json={"username": "alex", "password": ACCOUNT["password"]}, headers=H)
    assert "max-age=604800" in r.headers["set-cookie"].lower()
    _age_sessions(days=8)
    assert user.get("/api/badges").status_code == 401


def test_lockout_follows_the_settings(app, user):
    user.patch("/api/settings", json={"login_max_failures": 3, "login_lock_minutes": 5}, headers=H)
    for _ in range(3):
        assert user.post("/api/login", json={"username": "alex", "password": "nope"}, headers=H).status_code == 401
    r = user.post(
        "/api/login", json={"username": "alex", "password": ACCOUNT["password"]}, headers={**H, "x-groschen-lang": "de"}
    )
    assert r.status_code == 429 and "5 Minuten" in r.json()["detail"]
    assert user.post("/api/login/passkey/options", headers=H).status_code == 429
    failed = [e for e in user.get("/api/logins").json() if not e["ok"]]
    assert len(failed) == 3 and failed[0]["username"] == "alex"
    assert user.patch("/api/settings", json={"login_max_failures": 1}, headers=H).status_code == 400


def test_old_sessions_table_gets_new_columns(tmp_path):
    with db.session() as conn:
        conn.execute("DROP TABLE sessions")
        conn.execute(
            "CREATE TABLE sessions (token_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL, created_at TEXT NOT NULL, "
            "expires_at TEXT NOT NULL)"
        )
    db.init()
    with db.session() as conn:
        cols = {r[1] for r in conn.execute("PRAGMA table_info(sessions)")}
    assert {"last_seen", "ip", "agent", "method"} <= cols


def test_restore_keeps_passkeys_and_login_settings(app, user):
    from groschen import backup

    old = backup.create("manual")["name"]
    key = SoftKey()
    add_passkey(user, key)
    user.patch("/api/settings", json={"password_login": False, "idle_minutes": 30}, headers=H)
    backup.restore(old)
    assert len(user.get("/api/passkeys").json()) == 1
    values = user.get("/api/settings").json()["values"]
    assert values["password_login"] is False and values["idle_minutes"] == 30
    user.post("/api/logout", headers=H)
    assert passkey_login(user, key).status_code == 200
