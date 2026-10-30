import socket

import pytest

from groschen import db, netguard


@pytest.fixture
def guard(monkeypatch):
    calls = []

    def fake(host, *args, **kwargs):
        calls.append(host)
        return [("ok",)]

    monkeypatch.setattr(netguard, "_original_getaddrinfo", fake)
    monkeypatch.setattr(netguard, "_last_logged", {})
    netguard.allow_host("fints.ing.de")
    return calls


def test_everything_but_the_bank_is_blocked(guard, conn):
    with pytest.raises(socket.gaierror):
        netguard._guarded_getaddrinfo("huggingface.co", 443)
    with pytest.raises(socket.gaierror):
        netguard._guarded_getaddrinfo("fints.ing.de.evil.example", 443)
    assert guard == []
    blocked = db.rows(conn.execute("SELECT host, allowed FROM netlog"))
    assert {"host": "huggingface.co", "allowed": 0} in blocked


def test_bank_and_local_addresses_pass(guard, conn):
    with netguard.purpose("ING sync"):
        netguard._guarded_getaddrinfo("fints.ing.de", 443)
    netguard._guarded_getaddrinfo("127.0.0.1", 8420)
    netguard._guarded_getaddrinfo("192.168.1.20", 80)
    assert guard == ["fints.ing.de", "127.0.0.1", "192.168.1.20"]
    log = db.rows(conn.execute("SELECT host, purpose FROM netlog"))
    assert log == [{"host": "fints.ing.de", "purpose": "ING sync"}]


def test_raw_internet_addresses_are_refused(conn):
    s = socket.socket()
    try:
        with pytest.raises(ConnectionRefusedError):
            netguard._check_address(s, ("93.184.215.14", 443))
        netguard._check_address(s, ("192.168.1.20", 8420))
        netguard._check_address(s, ("127.0.0.1", 8420))
    finally:
        s.close()


def test_addresses_of_the_bank_are_allowed(monkeypatch, conn):
    monkeypatch.setattr(netguard, "_allowed_ips", set())
    monkeypatch.setattr(netguard, "_original_getaddrinfo", lambda *a, **k: [(2, 1, 6, "", ("198.51.100.7", 443))])
    netguard.allow_host("fints.ing.de")
    netguard._guarded_getaddrinfo("fints.ing.de", 443)
    s = socket.socket()
    try:
        netguard._check_address(s, ("198.51.100.7", 443))
    finally:
        s.close()
