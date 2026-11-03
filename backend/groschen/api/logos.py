"""Logos the user picked for merchants. The built-in logos ship with the web app; only the
user's own choices (a picture, another built-in logo, or the letter) are kept here. The phone app
asks /logos/resolve which logo each merchant gets, since it has no copy of the built-in ones."""

import hashlib
import re
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field

from .. import brand_logos, db, i18n
from .deps import current_user

router = APIRouter(dependencies=[Depends(current_user)])

MAX_IMAGE = 300 * 1024  # the app shrinks pictures to 160 px first; this is only a ceiling
SLUG = re.compile(r"^[a-z0-9_.-]{1,80}$")
# A picture is stored only when its first bytes say what it is; SVG (which can carry script) never.
MAGIC = (
    (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"GIF87a", "image/gif"),
    (b"GIF89a", "image/gif"),
)


def _key(key: str) -> str:
    if not key or len(key) > 120 or not all(c.isalnum() for c in key):
        raise HTTPException(status_code=400, detail=i18n.t("Unknown merchant."))
    return key


def _name(name: str | None) -> str | None:
    name = " ".join((name or "").split())[:200]
    return name or None


def _hash(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()[:16]


def _mime(raw: bytes) -> str | None:
    for magic, mime in MAGIC:
        if raw.startswith(magic):
            return mime
    if raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        return "image/webp"
    return None


@router.get("/logos")
def list_logos():
    """Every choice, with the merchant's name and, for pictures, a fingerprint: the logo dialog
    offers pictures already given to one merchant for others ("Cineplex" for "Cineplex Musterstadt")."""
    with db.session() as conn:
        # Pictures from before fingerprints existed get theirs now, once.
        for r in conn.execute("SELECT key, image FROM vendor_logos WHERE kind = 'image' AND hash IS NULL").fetchall():
            conn.execute("UPDATE vendor_logos SET hash = ? WHERE key = ?", (_hash(r["image"] or b""), r["key"]))
        rows = conn.execute("SELECT key, kind, slug, updated_at, name, hash FROM vendor_logos").fetchall()
    return {
        r["key"]: {"kind": r["kind"], "slug": r["slug"], "v": r["updated_at"], "name": r["name"], "hash": r["hash"]}
        for r in rows
    }


class Names(BaseModel):
    names: list[Annotated[str, Field(min_length=1, max_length=200)]] = Field(max_length=500)


@router.post("/logos/resolve")
def resolve(body: Names):
    """The logo each shown merchant name gets, as the web app picks it: the user's own choice
    first (a picture, another built-in logo, or just the letter), else the built-in logo."""
    with db.session() as conn:
        own = {r["key"]: r for r in conn.execute("SELECT key, kind, slug, updated_at FROM vendor_logos")}
    out = {}
    for name in dict.fromkeys(body.names):
        key = brand_logos.logo_key(name)
        choice = own.get(key) if key else None
        if choice and choice["kind"] == "image":
            # Loaded from /logos/{key}/image?v=...; a new picture gets a new address.
            out[name] = {"kind": "image", "key": key, "v": choice["updated_at"]}
            continue
        if choice and choice["kind"] == "letter":
            out[name] = {"kind": "letter"}
            continue
        slug = choice["slug"] if choice and choice["slug"] else brand_logos.auto_slug(name)
        out[name] = (slug and brand_logos.brand(slug)) or {"kind": "letter"}
    return out


class Choice(BaseModel):
    kind: Literal["brand", "letter", "image"]
    slug: str | None = Field(default=None, max_length=80)
    # kind image: the merchant whose picture this one gets as well
    source: str | None = Field(default=None, max_length=120)
    name: str | None = Field(default=None, max_length=200)


@router.put("/logos/{key}")
def choose(key: str, body: Choice):
    key = _key(key)
    name = _name(body.name)
    if body.kind == "image":
        source = _key(body.source or "")
        with db.session() as conn:
            row = conn.execute(
                "SELECT mime, image, hash FROM vendor_logos WHERE key = ? AND kind = 'image'", (source,)
            ).fetchone()
            if not row:
                raise HTTPException(status_code=404, detail=i18n.t("Not found."))
            conn.execute(
                "INSERT OR REPLACE INTO vendor_logos (key, kind, slug, mime, image, updated_at, name, hash) "
                "VALUES (?, 'image', NULL, ?, ?, ?, ?, ?)",
                (key, row["mime"], row["image"], db.now_iso(), name, row["hash"] or _hash(row["image"] or b"")),
            )
        return {"ok": True}
    if body.kind == "brand" and not (body.slug and SLUG.match(body.slug)):
        raise HTTPException(status_code=400, detail=i18n.t("Unknown logo."))
    with db.session() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO vendor_logos (key, kind, slug, mime, image, updated_at, name, hash) "
            "VALUES (?, ?, ?, NULL, NULL, ?, ?, NULL)",
            (key, body.kind, body.slug if body.kind == "brand" else None, db.now_iso(), name),
        )
    return {"ok": True}


@router.post("/logos/{key}/image")
async def upload(key: str, file: UploadFile = File(...), name: str | None = Form(None, max_length=200)):
    key = _key(key)
    raw = await file.read(MAX_IMAGE + 1)
    if len(raw) > MAX_IMAGE:
        raise HTTPException(status_code=413, detail=i18n.t("That picture is too large."))
    mime = _mime(raw)
    if not mime:
        raise HTTPException(status_code=415, detail=i18n.t("Use a PNG, JPEG, WebP or GIF picture."))
    with db.session() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO vendor_logos (key, kind, slug, mime, image, updated_at, name, hash) "
            "VALUES (?, 'image', NULL, ?, ?, ?, ?, ?)",
            (key, mime, raw, db.now_iso(), _name(name), _hash(raw)),
        )
    return {"ok": True}


@router.get("/logos/{key}/image")
def image(key: str):
    key = _key(key)
    with db.session() as conn:
        row = conn.execute("SELECT mime, image FROM vendor_logos WHERE key = ? AND kind = 'image'", (key,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=i18n.t("Not found."))
    # The address carries the upload time (?v=), so a new picture gets a new address.
    return Response(row["image"], media_type=row["mime"], headers={"Cache-Control": "private, max-age=31536000, immutable"})


@router.delete("/logos/{key}")
def reset(key: str):
    with db.session() as conn:
        conn.execute("DELETE FROM vendor_logos WHERE key = ?", (_key(key),))
    return {"ok": True}
