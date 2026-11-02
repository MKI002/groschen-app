"""Fingerprint login for the Android app: a key pair in the phone's secure hardware."""

import base64

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from fastapi.testclient import TestClient

from groschen import db, devices
from groschen.api import auth
from groschen.main import create_app

ACCOUNT = {"name": "Alex", "username": "alex", "password": "correct horse"}
# The app talks to the server over plain http on the home network and sends no Origin.
BASE = "http://192.168.1.20:8420"
H = {"x-groschen": "1", "user-agent": "Groschen-Android/1.0 (Pixel 9; Android 16)"}


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


class Phone:
    """What the app does with its Android Keystore key, in software."""

    def __init__(self, curve=ec.SECP256R1()):
        self.key = ec.generate_private_key(curve)
        self.key_id = None

    def public(self) -> str:
        return b64(
            self.key.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
        )

    def sign(self, label: bytes, challenge: str) -> str:
        return b64(self.key.sign(label + base64.b64decode(challenge), ec.ECDSA(hashes.SHA256())))


@pytest.fixture
def app():
    auth._failures.clear()
    auth.time.sleep = lambda s: None
    return create_app()


@pytest.fixture
def user(app):
    c = TestClient(app, base_url=BASE)
    assert c.post("/api/setup/account", json=ACCOUNT, headers=H).status_code == 200
    return c


def add_phone(c, phone: Phone, name="Pixel 9"):
    start = c.post("/api/devices/options", headers=H).json()
    r = c.post(
        "/api/devices",
        json={
            "challenge_id": start["challenge_id"],
            "public_key": phone.public(),
            "signature": phone.sign(devices.REGISTER, start["challenge"]),
            "name": name,
        },
        headers=H,
    )
    if r.status_code == 200:
        phone.key_id = r.json()["key_id"]
    return r


def phone_login(c, phone: Phone, label=devices.LOGIN):
    start = c.post("/api/login/device/options", headers=H)
    if start.status_code != 200:
        return start
    body = start.json()
    return c.post(
        "/api/login/device",
        json={
            "key_id": phone.key_id,
            "challenge_id": body["challenge_id"],
            "signature": phone.sign(label, body["challenge"]),
        },
        headers=H,
    )


def login_body(phone: Phone, start: dict) -> dict:
    return {
        "key_id": phone.key_id,
        "challenge_id": start["challenge_id"],
        "signature": phone.sign(devices.LOGIN, start["challenge"]),
    }


def test_add_a_phone_and_log_in_without_a_password(app, user):
    phone = Phone()
    r = add_phone(user, phone, name="  Alex'   Pixel ")
    assert r.status_code == 200, r.text
    assert r.json()["name"] == "Alex' Pixel"
    assert [d["name"] for d in user.get("/api/devices").json()] == ["Alex' Pixel"]

    app_client = TestClient(app, base_url=BASE)
    r = phone_login(app_client, phone)
    assert r.status_code == 200, r.text
    assert "groschen_session" in r.headers["set-cookie"]
    assert app_client.get("/api/status").json()["user"]["username"] == "alex"
    assert user.get("/api/devices").json()[0]["last_used_at"]
    newest = user.get("/api/logins").json()[0]
    assert newest["ok"] and newest["method"] == "device" and newest["username"] == "alex"
    session = next(s for s in user.get("/api/sessions").json() if not s["current"])
    assert session["method"] == "device"


def test_adding_a_phone_needs_a_login_and_a_real_signature(app, user):
    other = TestClient(app, base_url=BASE)
    assert other.post("/api/devices/options", headers=H).status_code == 401
    assert other.get("/api/devices").status_code == 401

    phone = Phone()
    start = user.post("/api/devices/options", headers=H).json()
    wrong = Phone().sign(devices.REGISTER, start["challenge"])
    body = {"challenge_id": start["challenge_id"], "public_key": phone.public(), "signature": wrong}
    assert user.post("/api/devices", json=body, headers=H).status_code == 400

    # A login signature can't stand in for the one that adds a phone.
    start = user.post("/api/devices/options", headers=H).json()
    body = {
        "challenge_id": start["challenge_id"],
        "public_key": phone.public(),
        "signature": phone.sign(devices.LOGIN, start["challenge"]),
    }
    assert user.post("/api/devices", json=body, headers=H).status_code == 400

    for bad_key in ("not base64!", b64(b"\x00" * 64)):
        start = user.post("/api/devices/options", headers=H).json()
        body = {
            "challenge_id": start["challenge_id"],
            "public_key": bad_key,
            "signature": phone.sign(devices.REGISTER, start["challenge"]),
        }
        assert user.post("/api/devices", json=body, headers=H).status_code == 400
    assert user.get("/api/devices").json() == []


def test_only_p256_keys(user):
    assert add_phone(user, Phone(ec.SECP384R1())).status_code == 400
    rsa_der = (
        rsa.generate_private_key(public_exponent=65537, key_size=2048)
        .public_key()
        .public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
    )
    assert devices._public_key(rsa_der) is None


def test_challenge_works_once_and_for_one_purpose(app, user):
    phone = Phone()
    add_phone(user, phone)
    c = TestClient(app, base_url=BASE)
    start = c.post("/api/login/device/options", headers=H).json()
    body = login_body(phone, start)
    assert c.post("/api/login/device", json=body, headers=H).status_code == 200
    assert c.post("/api/login/device", json=body, headers=H).status_code == 401
    # A signature made to add a phone is no login.
    assert phone_login(c, phone, label=devices.REGISTER).status_code == 401
    # A challenge for adding a phone can't be used to log in.
    start = user.post("/api/devices/options", headers=H).json()
    body = login_body(phone, start)
    assert c.post("/api/login/device", json=body, headers=H).status_code == 401


def test_unknown_or_foreign_key_is_refused(app, user):
    phone = Phone()
    add_phone(user, phone)
    thief = Phone()
    thief.key_id = phone.key_id
    c = TestClient(app, base_url=BASE)
    assert phone_login(c, thief).status_code == 401
    nobody = Phone()
    nobody.key_id = "no-such-key"
    assert phone_login(c, nobody).status_code == 401
    assert c.get("/api/badges").status_code == 401
    failed = [e for e in user.get("/api/logins").json() if not e["ok"]]
    assert len(failed) == 2 and all(e["method"] == "device" for e in failed)


def test_one_session_per_phone(app, user):
    phone = Phone()
    add_phone(user, phone)
    first = TestClient(app, base_url=BASE)
    second = TestClient(app, base_url=BASE)
    assert phone_login(first, phone).status_code == 200
    assert phone_login(second, phone).status_code == 200
    # The new fingerprint login replaced the phone's old one.
    assert first.get("/api/badges").status_code == 401
    assert second.get("/api/badges").status_code == 200
    assert len(user.get("/api/sessions").json()) == 2  # this browser and the phone


def test_works_with_the_password_login_off(app, user):
    phone = Phone()
    add_phone(user, phone)
    with db.session() as conn:
        conn.execute("INSERT INTO settings (key, value) VALUES ('password_login', 'false')")
    c = TestClient(app, base_url=BASE)
    assert c.post("/api/login", json={"username": "alex", "password": ACCOUNT["password"]}, headers=H).status_code == 200
    assert phone_login(c, phone).status_code == 200


def test_removing_a_phone_ends_its_login(app, user):
    phone = Phone()
    item = add_phone(user, phone).json()
    c = TestClient(app, base_url=BASE)
    assert phone_login(c, phone).status_code == 200
    assert user.delete("/api/devices/999", headers=H).status_code == 404
    assert user.delete(f"/api/devices/{item['id']}", headers=H).status_code == 200
    assert c.get("/api/badges").status_code == 401
    assert phone_login(c, phone).status_code == 401
    assert user.get("/api/devices").json() == []


def test_lockout_covers_the_phone_login(app, user):
    user.patch("/api/settings", json={"login_max_failures": 3, "login_lock_minutes": 5}, headers=H)
    phone = Phone()
    add_phone(user, phone)
    thief = Phone()
    thief.key_id = phone.key_id
    for _ in range(3):
        assert phone_login(user, thief).status_code == 401
    assert phone_login(user, phone).status_code == 429


def test_restore_keeps_the_phones(app, user):
    from groschen import backup

    old = backup.create("manual")["name"]
    phone = Phone()
    add_phone(user, phone)
    backup.restore(old)
    assert len(user.get("/api/devices").json()) == 1
    c = TestClient(app, base_url=BASE)
    assert phone_login(c, phone).status_code == 200


def test_old_sessions_table_gets_the_device_column():
    with db.session() as conn:
        conn.execute("DROP TABLE sessions")
        conn.execute(
            "CREATE TABLE sessions (token_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL, created_at TEXT NOT NULL, "
            "expires_at TEXT NOT NULL)"
        )
    db.init()
    with db.session() as conn:
        cols = {r[1] for r in conn.execute("PRAGMA table_info(sessions)")}
    assert "device_id" in cols
