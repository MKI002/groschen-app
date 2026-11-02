import json
import pathlib

from tests.test_api import ACCOUNT, H, client, user  # noqa: F401

PNG = b"\x89PNG\r\n\x1a\n" + b"\0" * 64
LOGOS = pathlib.Path(__file__).resolve().parents[2] / "frontend" / "src" / "data" / "logos"


def test_choices_need_a_login(client):  # noqa: F811
    assert client.get("/api/logos").status_code == 401


def test_pick_upload_and_reset_a_merchants_logo(user):  # noqa: F811
    assert user.get("/api/logos").json() == {}
    assert user.put("/api/logos/ecenterbeispiel", json={"kind": "brand", "slug": "edeka"}, headers=H).status_code == 200
    assert user.get("/api/logos").json()["ecenterbeispiel"]["slug"] == "edeka"

    r = user.post("/api/logos/musterbaustiftung/image", files={"file": ("logo.png", PNG, "image/png")}, headers=H)
    assert r.status_code == 200
    got = user.get("/api/logos/musterbaustiftung/image")
    assert got.content == PNG and got.headers["content-type"] == "image/png"
    assert "immutable" in got.headers["cache-control"]

    assert user.put("/api/logos/musterbaustiftung", json={"kind": "letter"}, headers=H).status_code == 200
    assert user.get("/api/logos/musterbaustiftung/image").status_code == 404
    assert user.delete("/api/logos/ecenterbeispiel", headers=H).status_code == 200
    assert set(user.get("/api/logos").json()) == {"musterbaustiftung"}


def test_only_real_pictures_are_stored(user):  # noqa: F811
    svg = b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'
    r = user.post("/api/logos/shell/image", files={"file": ("logo.svg", svg, "image/svg+xml")}, headers=H)
    assert r.status_code == 415
    big = b"\x89PNG\r\n\x1a\n" + b"\0" * 400_000
    assert user.post("/api/logos/shell/image", files={"file": ("x.png", big, "image/png")}, headers=H).status_code == 413
    assert user.put("/api/logos/bad key", json={"kind": "letter"}, headers=H).status_code == 400
    assert user.put("/api/logos/shell", json={"kind": "brand", "slug": "../x"}, headers=H).status_code == 400
    assert user.put("/api/logos/shell", json={"kind": "brand"}, headers=H).status_code == 400


def test_bundled_logos_are_public_domain_and_complete():
    index = json.loads((LOGOS / "index.json").read_text())
    assert len(index["icons"]) > 3000
    assert "CC0" in index["source"]
    drawn = {}
    for part in LOGOS.glob("[0-9][0-9].json"):
        drawn.update(json.loads(part.read_text()))
    assert set(drawn) == set(index["icons"])
    for table in ("any", "lead", "exact"):
        assert set(index[table].values()) <= set(index["icons"])
    # The brands from the request, and first names that must never be a brand on their own.
    assert index["lead"]["E CENTER"] == "edeka"
    assert index["any"]["SHELL"] == "shell"
    assert index["any"]["REWE"] == "rewe"
    assert index["exact"]["CLAUDE"] == "claude"
    for name in ("MAX", "CLAUDE", "MARKUS", "THOMAS"):
        assert name not in index["any"] and name not in index["lead"]
