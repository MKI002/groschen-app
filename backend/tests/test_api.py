import pytest
from fastapi.testclient import TestClient

from groschen import demo
from groschen.api import auth
from groschen.bank import sync
from groschen.main import create_app

H = {"x-groschen": "1"}
ACCOUNT = {"name": "Alex", "username": "alex", "password": "correct horse"}


@pytest.fixture
def client():
    auth._failures.clear()
    return TestClient(create_app())


@pytest.fixture
def user(client):
    assert client.post("/api/setup/account", json=ACCOUNT, headers=H).status_code == 200
    return client


def test_first_run_flow(client, run_job, demo_data, monkeypatch):
    assert client.get("/api/status").json() == {
        "version": "0.1.0",
        "has_user": False,
        "setup_complete": False,
        "language": None,
        "user": None,
        "passkeys": False,
        "password_login": True,
    }
    assert client.get("/api/cashflow").status_code == 401
    assert client.post("/api/setup/account", json=ACCOUNT, headers=H).status_code == 200
    assert client.post("/api/setup/account", json=ACCOUNT, headers=H).status_code == 409

    monkeypatch.setattr(sync, "session_factory", demo.FakeBank(demo_data))
    bad = client.post("/api/bank/test", json={"login": "123", "pin": "wrong", "product_id": "ABCDEF123"}, headers=H)
    assert bad.json()["state"] == "error" and "PIN" in bad.json()["error"]
    ok = client.post("/api/bank/test", json={"login": "123", "pin": demo.DEMO_PIN, "product_id": "ABCDEF123"}, headers=H)
    assert ok.json()["state"] == "done"
    assert {a["kind"] for a in ok.json()["result"]["accounts"]} == {"checking", "savings", "depot"}
    assert "sepa" not in str(ok.json())

    history = [t for t in demo_data["giro"] if t["date"] < "2026-06-01"]
    csv = demo.ing_csv(demo.GIRO_IBAN, "Girokonto", 0, history)
    r = client.post("/api/import/csv", files={"file": ("Umsatzanzeige.csv", csv, "text/csv")}, headers=H)
    assert r.status_code == 200, r.text

    job = client.post("/api/setup/finish", headers=H).json()
    assert job["state"] == "done", job
    assert client.post("/api/setup/complete", headers=H).json() == {"ok": True}
    assert client.get("/api/status").json()["setup_complete"] is True

    txs = client.get("/api/transactions").json()
    assert txs["total"] > 100
    conns = client.get("/api/connections").json()
    assert conns[0]["login_days_left"] == 90
    assert demo.DEMO_PIN not in str(conns) and conns[0]["login_hint"].endswith("123")


def test_a_sync_approved_in_the_bank_app_restarts_the_90_days(client, run_job, demo_data, monkeypatch, conn):
    client.post("/api/setup/account", json=ACCOUNT, headers=H)
    monkeypatch.setattr(sync, "session_factory", demo.FakeBank(demo_data))
    client.post("/api/bank/test", json={"login": "123", "pin": demo.DEMO_PIN, "product_id": "ABCDEF123"}, headers=H)
    conn.execute("UPDATE connections SET bank_login_confirmed_at = '2026-08-28T08:00:00+00:00'")
    conn.commit()
    client.post("/api/sync", headers=H)
    left = client.get("/api/connections").json()[0]["login_days_left"]
    assert left < 90  # Groschen can't see a login elsewhere: the countdown goes on

    monkeypatch.setattr(sync, "session_factory", demo.FakeBank(demo_data, needs_approval=True))
    assert client.post("/api/sync", headers=H).json()["state"] == "done"
    assert client.get("/api/connections").json()[0]["login_days_left"] == 90


def test_changes_need_the_request_header(user):
    r = user.patch("/api/settings", json={"reminder_days": 5})
    assert r.status_code == 403
    assert user.patch("/api/settings", json={"reminder_days": 5}, headers=H).status_code == 200


def test_settings_are_validated(user):
    assert user.patch("/api/settings", json={"sync_schedule": "every minute"}, headers=H).status_code == 400
    assert user.patch("/api/settings", json={"backup_keep": 0}, headers=H).status_code == 400
    assert user.patch("/api/settings", json={"review_uncertain": "yes"}, headers=H).status_code == 400
    assert user.patch("/api/settings", json={"setup_complete": True}, headers=H).json()["setup_complete"] is False


def test_login_lockout(client):
    client.post("/api/setup/account", json=ACCOUNT, headers=H)
    client.post("/api/logout", headers=H)
    auth.time.sleep = lambda s: None
    for _ in range(10):  # the default under Settings → Security
        assert client.post("/api/login", json={"username": "alex", "password": "nope"}, headers=H).status_code == 401
    r = client.post("/api/login", json={"username": "alex", "password": ACCOUNT["password"]}, headers=H)
    assert r.status_code == 429


def test_logout_ends_the_session(user):
    assert user.get("/api/badges").status_code == 200
    user.post("/api/logout", headers=H)
    assert user.get("/api/badges").status_code == 401


def test_backup_names_are_checked(user):
    name = user.post("/api/backups", headers=H).json()["name"]
    assert user.get(f"/api/backups/{name}").status_code == 200
    assert user.get("/api/backups/..%2Fsecret.key").status_code == 404
    assert user.get("/api/backups/secret.key").status_code == 404


def test_static_files_stay_inside_the_web_folder(client, data_dir):
    static = data_dir / "static"
    static.mkdir()
    (static / "index.html").write_text("<html>app</html>")
    (data_dir / "outside.txt").write_text("secret")
    assert client.get("/").text == "<html>app</html>"
    assert client.get("/transactions").text == "<html>app</html>"
    assert "secret" not in client.get("/..%2Foutside.txt").text
    assert "secret" not in client.get("/%2e%2e/outside.txt").text


def test_icon_can_be_shown_by_unraid(client, data_dir):
    static = data_dir / "static"
    static.mkdir()
    (static / "icon.png").write_bytes(b"\x89PNG")
    (static / "favicon.svg").write_text("<svg/>")
    r = client.get("/icon.png")
    assert r.status_code == 200 and r.headers["content-type"] == "image/png"
    assert r.headers["cross-origin-resource-policy"] == "cross-origin"
    assert client.get("/favicon.svg").headers["cross-origin-resource-policy"] == "same-origin"


def test_health_names_the_build(client, tmp_path, monkeypatch):
    from groschen import config, main

    assert "build" in client.get("/api/health").json()
    (tmp_path / "index.html").write_text('<script type="module" crossorigin src="/assets/index-Ab12.js"></script>')
    monkeypatch.setattr(config, "STATIC_DIR", tmp_path)
    assert main.build_id() == "/assets/index-Ab12.js"


def test_security_headers(client):
    r = client.get("/api/health")
    assert r.headers["x-frame-options"] == "DENY"
    assert "default-src 'self'" in r.headers["content-security-policy"]
    assert r.headers["cache-control"] == "no-store"


def test_racing_first_run_creates_one_account(client):
    from concurrent.futures import ThreadPoolExecutor

    def create(i):
        body = {**ACCOUNT, "username": f"user{i}"}
        return client.post("/api/setup/account", json=body, headers=H).status_code

    with ThreadPoolExecutor(10) as pool:
        codes = list(pool.map(create, range(10)))
    assert codes.count(200) == 1 and codes.count(409) == 9


def test_password_change_logs_out_other_browsers(user):
    other = TestClient(user.app)
    assert other.post("/api/login", json={"username": "alex", "password": ACCOUNT["password"]}, headers=H).status_code == 200
    body = {"current": ACCOUNT["password"], "new": "a new long password"}
    assert user.post("/api/me/password", json=body, headers=H).status_code == 200
    assert other.get("/api/badges").status_code == 401
    assert user.get("/api/badges").status_code == 200


def test_export_neutralises_spreadsheet_formulas(user, conn):
    conn.execute("INSERT INTO accounts (kind, name, manual, created_at) VALUES ('checking', 'Giro', 0, '2026-01-01')")
    conn.execute(
        "INSERT INTO transactions (account_id, date, amount, currency, counterparty, purpose, source, fingerprint, "
        "created_at) VALUES (1, '2026-08-05', -12.34, 'EUR', '=HYPERLINK(1)', '@SUM(1)', 'csv', 'fp1', '2026-08-05')"
    )
    conn.commit()
    text = user.get("/api/export/transactions.csv").text
    assert "-12,34" in text
    assert ";'=HYPERLINK" in text and ";'@SUM(1)" in text


def test_drilldown_endpoint(user, run_job):
    from groschen import demo

    demo.load()
    r = user.get("/api/drilldown", params={"group": "Food & Dining", "preset": "last12", "sort": "amount", "limit": 5})
    assert r.status_code == 200
    body = r.json()
    assert body["scope"]["name"] == "Food & Dining" and len(body["items"]) == 5
    assert user.get("/api/drilldown", params={"group": "Nope"}).status_code == 404
    assert user.get("/api/drilldown", params={"group": "Food & Dining", "sort": "id; DROP"}).status_code == 422
    assert user.get("/api/drilldown", params={"group": "Food & Dining", "sub": "x"}).status_code == 422
    assert user.get("/api/drilldown", params={"group": "Food & Dining", "min": -1}).status_code == 422


def test_new_subcategory_lands_in_its_group(user):
    r = user.post("/api/categories", json={"name": "Zeitung", "group": "Subscriptions", "kind": "expense"}, headers=H)
    assert r.status_code == 200
    cats = user.get("/api/categories").json()
    subs = [c["name"] for c in cats if c["group"] == "Subscriptions"]
    assert subs[0] == "Subscriptions" and subs[-1] == "Zeitung"
    groups = [c["group"] for c in cats]
    assert groups.index("Subscriptions") + len(subs) - 1 == len(groups) - 1 - groups[::-1].index("Subscriptions")
    dup = user.post("/api/categories", json={"name": "Zeitung", "group": "Subscriptions", "kind": "expense"}, headers=H)
    assert dup.status_code == 409


def test_payday_settings(user, run_job):
    demo.load()
    found = user.get("/api/paydays").json()
    salary = next(s for s in found["sources"] if s["usual_day"] >= 25)
    assert salary["auto"] == "next" and salary["moved"] > 0
    changed = user.patch("/api/paydays", json={"key": salary["key"], "mode": "same"}, headers=H).json()
    assert next(s for s in changed["sources"] if s["key"] == salary["key"])["moved"] == 0
    assert user.patch("/api/paydays", json={"key": salary["key"], "mode": "later"}, headers=H).status_code == 400
    assert user.patch("/api/settings", json={"payday_shift": False}, headers=H).json()["payday_shift"] is False


def test_redesign_endpoints(user, run_job):
    demo.load()
    # Transactions: amount range, date range and sort order
    all_tx = user.get("/api/transactions", params={"limit": 1000}).json()
    some = user.get("/api/transactions", params={"min": 100, "max": 500, "sort": "amount", "dir": "asc"}).json()
    amounts = [abs(t["amount"]) for t in some["items"]]
    assert amounts and all(100 <= a <= 500 for a in amounts) and amounts == sorted(amounts)
    assert some["total"] < all_tx["total"]
    day = all_tx["items"][0]["date"]
    one_day = user.get("/api/transactions", params={"from": day, "to": day}).json()
    assert one_day["total"] >= 1 and {t["date"] for t in one_day["items"]} == {day}
    assert user.get("/api/transactions", params={"sort": "id; DROP"}).status_code == 422
    assert user.get("/api/transactions", params={"from": "nope"}).status_code == 422

    # Daily spending for the year heatmap
    year = int(day[:4])
    daily = user.get("/api/daily", params={"year": year}).json()
    assert daily["year"] == year and daily["days"]
    assert all(d["date"].startswith(str(year)) for d in daily["days"])

    # A user's own group opens the same detail page as a category group
    cats = user.get("/api/categories").json()
    ids = [c["id"] for c in cats if c["group"] == "Food & Dining"][:2]
    gid = user.post("/api/groups", json={"name": "Essen", "icon": "tag", "category_ids": ids}, headers=H).json()["id"]
    body = user.get("/api/drilldown", params={"custom": gid, "preset": "all"}).json()
    assert body["scope"]["kind"] == "custom" and body["scope"]["name"] == "Essen"
    assert body["scope"]["custom_id"] == gid
    assert {t["category_id"] for t in body["items"]} <= set(ids)
    assert user.get("/api/drilldown", params={"custom": 9999}).status_code == 404

    # Every recurring payment names the payee page it opens, and that page exists.
    subs = user.get("/api/subscriptions").json()["items"]
    assert subs
    for s in subs[:5]:
        page = user.get("/api/drilldown", params={"merchant": s["merchant"], "preset": "all"})
        assert page.status_code == 200 and page.json()["scope"]["kind"] == "merchant"


def test_expensive_month_hint_follows_its_switch(user, run_job):
    demo.load()
    assert user.patch("/api/settings", json={"unusual_alerts": False}, headers=H).status_code == 200
    body = user.get("/api/cashflow", params={"preset": "all"}).json()
    assert body["insights"] == []


def test_overview_timeline(client, run_job):
    assert client.get("/api/cashflow/timeline").status_code == 401
    assert client.post("/api/setup/account", json=ACCOUNT, headers=H).status_code == 200
    user = client
    assert user.get("/api/cashflow/timeline").json() == {"months": [], "account": None, "known": False, "ahead": 0.0}
    demo.load()
    body = user.get("/api/cashflow/timeline").json()
    assert body["account"] == "Girokonto" and len(body["months"]) > 12
    assert all(a["carry_out"] == b["carry_in"] for a, b in zip(body["months"], body["months"][1:]))


def test_backup_list_pin_preview_and_restore(user):
    first = user.post("/api/backups", headers=H).json()["name"]
    second = user.post("/api/backups", headers=H).json()["name"]
    listed = user.get("/api/settings").json()["backups"]
    assert [b["name"] for b in listed] == [second, first]
    assert user.patch(f"/api/backups/{first}", json={"pinned": True}, headers=H).json()["pinned"] is True
    assert user.post(
        "/api/backups/preview", json={"backup_plan": "custom", "backup_mode": "last", "backup_keep": 1}, headers=H
    ).json() == {"remove": []}
    user.patch(f"/api/backups/{first}", json={"pinned": False}, headers=H)
    assert user.post(
        "/api/backups/preview", json={"backup_plan": "custom", "backup_mode": "last", "backup_keep": 1}, headers=H
    ).json() == {"remove": [first]}
    assert user.post("/api/backups/preview", json={"backup_mode": "nope"}, headers=H).status_code == 400
    r = user.post(f"/api/backups/{first}/restore", headers=H)
    assert r.status_code == 200 and r.json()["safety"].endswith("-safety.db")
    assert user.get("/api/badges").status_code == 200  # still logged in
    assert user.post("/api/backups/secret.key/restore", headers=H).status_code == 404
    assert user.delete(f"/api/backups/{second}", headers=H).status_code == 200
    assert user.get(f"/api/backups/{second}").status_code == 404


def test_refund_links_by_hand_and_undone(user, conn):
    from test_categorize import _account, _add

    from groschen.categorize import engine

    acc = _account(conn)
    buy = _add(conn, acc, "2026-09-01", -40.0, "Muster Mode GmbH", "Bestellung 123")
    back = _add(conn, acc, "2026-09-08", 29.0, "Muster Mode GmbH", "Retoure", "Gutschrift")
    share = _add(conn, acc, "2026-09-09", 5.0, "Sam Muster", "Anteil", "Gutschrift")
    engine.categorize(conn)
    conn.commit()
    items = {t["id"]: t for t in user.get("/api/transactions", params={"preset": "all"}).json()["items"]}
    assert items[buy]["refunded"] == 29.0 and items[back]["refund_for"]["id"] == buy
    assert user.get(f"/api/transactions/{buy}/refund").json()["left"] == 11.0
    assert [c["id"] for c in user.get(f"/api/transactions/{share}/refund/candidates").json()["items"]] == [buy]
    r = user.put(f"/api/transactions/{share}/refund", json={"purchase_id": buy}, headers=H)
    assert r.status_code == 200 and r.json()["refunded"] == 34.0
    assert user.put(f"/api/transactions/{share}/refund", json={"purchase_id": back}, headers=H).status_code == 422
    assert user.delete(f"/api/transactions/{back}/refund", headers=H).status_code == 200
    assert user.get(f"/api/transactions/{buy}/refund").json()["refunded"] == 5.0
    assert user.delete("/api/transactions/9999/refund", headers=H).status_code == 404
