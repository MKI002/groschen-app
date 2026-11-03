import json
import pathlib

from tests.test_api import ACCOUNT, H, client, user  # noqa: F401

PNG = b"\x89PNG\r\n\x1a\n" + b"\0" * 64
LOGOS = pathlib.Path(__file__).resolve().parents[2] / "frontend" / "src" / "data" / "logos"


def test_choices_need_a_login(client):  # noqa: F811
    assert client.get("/api/logos").status_code == 401


def test_pick_upload_and_reset_a_merchants_logo(user):  # noqa: F811
    assert user.get("/api/logos").json() == {}
    assert user.put("/api/logos/ecenterfischer", json={"kind": "brand", "slug": "edeka"}, headers=H).status_code == 200
    assert user.get("/api/logos").json()["ecenterfischer"]["slug"] == "edeka"

    r = user.post("/api/logos/maxboeglstiftung/image", files={"file": ("logo.png", PNG, "image/png")}, headers=H)
    assert r.status_code == 200
    got = user.get("/api/logos/maxboeglstiftung/image")
    assert got.content == PNG and got.headers["content-type"] == "image/png"
    assert "immutable" in got.headers["cache-control"]

    assert user.put("/api/logos/maxboeglstiftung", json={"kind": "letter"}, headers=H).status_code == 200
    assert user.get("/api/logos/maxboeglstiftung/image").status_code == 404
    assert user.delete("/api/logos/ecenterfischer", headers=H).status_code == 200
    assert set(user.get("/api/logos").json()) == {"maxboeglstiftung"}


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


def test_the_page_may_load_pictures_only_from_google_images(client):  # noqa: F811
    # A logo dragged in from Google Images is loaded by the browser; the server fetches nothing,
    # and the page may still only talk to Groschen itself.
    csp = dict(p.strip().split(" ", 1) for p in client.get("/api/health").headers["content-security-policy"].split(";"))
    assert csp["connect-src"] == "'self'"
    outside = [s for s in csp["img-src"].split() if s.startswith("https://")]
    assert outside and all(s.endswith((".gstatic.com", ".googleusercontent.com")) and "*" not in s for s in outside)


def test_the_phone_app_learns_which_logo_each_merchant_gets(user):  # noqa: F811
    assert user.put("/api/logos/ecenterfischer", json={"kind": "letter"}, headers=H).status_code == 200
    assert user.put("/api/logos/meinbacker", json={"kind": "brand", "slug": "edeka"}, headers=H).status_code == 200
    picture = {"file": ("l.png", PNG, "image/png")}
    assert user.post("/api/logos/tamroneurope/image", files=picture, headers=H).status_code == 200
    names = ["PayPal", "PAYPAL *NETFLIX", "Netflix.com", "E-Center Fischer", "Mein Bäcker", "TAMRON Europe"]
    names.append("Schreinerei Huber")
    got = user.post("/api/logos/resolve", json={"names": names}, headers=H).json()
    assert {n: got[n].get("slug") or got[n]["kind"] for n in names} == {
        "PayPal": "paypal",
        "PAYPAL *NETFLIX": "netflix",
        "Netflix.com": "netflix",
        "E-Center Fischer": "letter",  # the user's own choice beats the built-in Edeka logo
        "Mein Bäcker": "edeka",
        "TAMRON Europe": "image",
        "Schreinerei Huber": "letter",
    }
    netflix = got["Netflix.com"]
    assert netflix["hex"].startswith("#") and netflix["ink"] in ("#FFFFFF", "#111214") and netflix["path"][0] in "Mm"
    assert got["TAMRON Europe"]["key"] == "tamroneurope" and got["TAMRON Europe"]["v"]
    assert user.post("/api/logos/resolve", json={"names": ["x" * 201]}, headers=H).status_code == 422


def test_server_matching_follows_the_web_app():
    from groschen import brand_logos

    # The same names as the web app's matcher (frontend/src/lib/logos.ts autoSlug).
    expect = {
        "PayPal": "paypal",
        "PayPal Europe": "paypal",
        "PayPal *Spotify AB": "spotify",
        "Visa": "visa",
        "Klarna": "klarna",
        "VISA REWE MARKT": "rewe",
        "E-Center Fischer": "edeka",
        "Amazon": None,
        "Max Bögl": None,
        "Shell Station 123": "shell",
    }
    assert {n: brand_logos.auto_slug(n) for n in expect} == expect
    assert brand_logos.logo_key("Mein Bäcker GmbH") == "meinbackergmbh"


def test_drawings_reach_the_phone_with_every_part_spaced():
    from groschen import brand_logos

    # An arc's two flags may run into the next number in SVG; spelled out, any phone reads it.
    assert brand_logos.spaced("M5.398 0a1 1 0 01-2.5.5zm1,2l-1-1") == "M 5.398 0 a 1 1 0 0 1 -2.5 .5 z m 1 2 l -1 -1"
    assert brand_logos.spaced("M1 1 x") is None
