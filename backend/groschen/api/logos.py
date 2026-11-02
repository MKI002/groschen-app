"""Logos the user picked for merchants. The built-in logos ship with the web app; only the
user's own choices (a picture, another built-in logo, or the letter) are kept here."""

import re
from typing import Literal

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field

from .. import db, i18n
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


def _mime(raw: bytes) -> str | None:
    for magic, mime in MAGIC:
        if raw.startswith(magic):
            return mime
    if raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        return "image/webp"
    return None


@router.get("/logos")
def list_logos():
    with db.session() as conn:
        rows = conn.execute("SELECT key, kind, slug, updated_at FROM vendor_logos").fetchall()
    return {r["key"]: {"kind": r["kind"], "slug": r["slug"], "v": r["updated_at"]} for r in rows}


class Choice(BaseModel):
    kind: Literal["brand", "letter"]
    slug: str | None = Field(default=None, max_length=80)


@router.put("/logos/{key}")
def choose(key: str, body: Choice):
    key = _key(key)
    if body.kind == "brand" and not (body.slug and SLUG.match(body.slug)):
        raise HTTPException(status_code=400, detail=i18n.t("Unknown logo."))
    with db.session() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO vendor_logos (key, kind, slug, mime, image, updated_at) VALUES (?, ?, ?, NULL, NULL, ?)",
            (key, body.kind, body.slug if body.kind == "brand" else None, db.now_iso()),
        )
    return {"ok": True}


@router.post("/logos/{key}/image")
async def upload(key: str, file: UploadFile = File(...)):
    key = _key(key)
    raw = await file.read(MAX_IMAGE + 1)
    if len(raw) > MAX_IMAGE:
        raise HTTPException(status_code=413, detail=i18n.t("That picture is too large."))
    mime = _mime(raw)
    if not mime:
        raise HTTPException(status_code=415, detail=i18n.t("Use a PNG, JPEG, WebP or GIF picture."))
    with db.session() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO vendor_logos (key, kind, slug, mime, image, updated_at) "
            "VALUES (?, 'image', NULL, ?, ?, ?)",
            (key, mime, raw, db.now_iso()),
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
