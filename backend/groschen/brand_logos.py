"""The built-in brand logos, matched to merchant names the way the web app does it.

The logos themselves ship with the web app (frontend/src/data/logos, built from Simple Icons by
frontend/scripts/build_logos.py). The phone app has no copy of them, so the server reads the same
files and tells it, per merchant name, which logo to draw. This mirrors autoSlug() and brand() in
frontend/src/lib/logos.ts; the two must stay in step.
"""

import functools
import json
import re
import unicodedata
from pathlib import Path

from .categorize.vendors import _LEAD_SKIP, words

_HERE = Path(__file__).resolve().parent
# In the image the files sit next to the code; in a checkout they are read from the web app.
_PLACES = (_HERE / "logodata", _HERE.parents[1] / "frontend" / "src" / "data" / "logos")
_DATA = next((p for p in _PLACES if (p / "index.json").is_file()), None)
# Company forms and web endings that may follow a whole name ("Netflix.com", "Spotify AB").
TRAIL = set("GMBH AG KG SE CO INC LTD LLC LIMITED CORP PLC BV NV SA SAS SARL SRL SPA".split())
TRAIL |= set("AB AS ASA OY APS COM DE EU IO NET ORG APP".split())
MAX_WORDS = 6


@functools.cache
def _index() -> dict | None:
    if not _DATA:
        return None
    try:
        return json.loads((_DATA / "index.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


@functools.cache
def _chunk(n: int) -> dict:
    try:
        return json.loads((_DATA / f"{n:02d}.json").read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return {}


def _bucket(slug: str, n: int) -> int:
    """djb2, as build_logos.py splits the drawings into files."""
    h = 5381
    for c in slug:
        h = (h * 33 + ord(c)) % 4294967296
    return h % n


def logo_key(name: str) -> str:
    """What a merchant's own choice is stored under (logoKey() in the web app)."""
    folded = unicodedata.normalize("NFKD", (name or "").replace("ß", "ss")).lower()
    return "".join(c for c in folded if c.isalnum())[:120]


def _longest(w: list[str], table: dict, start_only: bool) -> tuple[int, str] | None:
    best = None
    for i in range(min(1, len(w)) if start_only else len(w)):
        for size in range(min(MAX_WORDS, len(w) - i), 0, -1):
            hit = table.get(" ".join(w[i : i + size]))
            if hit:
                if not best or size > best[0]:
                    best = (size, hit)
                break
    return best


def _find(index: dict, every: list[str], lead: list[str]) -> str | None:
    whole = lead
    while len(whole) > 1 and whole[-1] in TRAIL:
        whole = whole[:-1]
    exact = index["exact"].get(" ".join(whole)) if whole else None
    if exact:
        return exact
    anywhere = _longest(every, index["any"], False)
    first = _longest(lead, index["lead"], True) or _longest(lead, index["any"], True)
    best = first if first and (not anywhere or first[0] >= anywhere[0]) else anywhere
    return best[1] if best else None


def auto_slug(name: str) -> str | None:
    """The built-in logo for a shown merchant name, or None."""
    index = _index()
    if not index:
        return None
    every = words(name)
    lead = every
    while lead and (lead[0] in _LEAD_SKIP or lead[0].isdigit()):
        lead = lead[1:]
    # "PayPal *Netflix" is Netflix, but "PayPal" (or "PayPal Europe") on its own is PayPal itself.
    return _find(index, every, lead) or (_find(index, every, every) if len(lead) < len(every) else None)


_NUMBER = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")
_ARITY = {"m": 2, "l": 2, "h": 1, "v": 1, "c": 6, "s": 4, "q": 4, "t": 2, "a": 7, "z": 0}


def spaced(d: str) -> str | None:
    """The drawing with a space between all its parts. Simple Icons writes it as tightly as SVG
    allows ("a1 1 0 01-2 2": the arc's two flags and the next number run together), which not
    every drawing library on phones reads right."""
    out: list[str] = []
    i, cmd, k = 0, "", 0
    while i < len(d):
        c = d[i]
        if c in " ,\t\r\n":
            i += 1
        elif c.lower() in _ARITY:
            out.append(c)
            cmd, k, i = c.lower(), 0, i + 1
        elif cmd == "a" and k % 7 in (3, 4) and c in "01":
            out.append(c)
            k, i = k + 1, i + 1
        else:
            m = _NUMBER.match(d, i)
            if not m:
                return None
            out.append(m.group())
            k, i = k + 1, m.end()
    return " ".join(out)


def _luminance(hex6: str) -> float:
    def channel(i: int) -> float:
        c = int(hex6[i : i + 2], 16) / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * channel(0) + 0.7152 * channel(2) + 0.0722 * channel(4)


@functools.lru_cache(maxsize=4096)
def brand(slug: str) -> dict | None:
    """A built-in logo as the app draws it: the drawing (24 x 24) in `ink` on a disc in `hex`."""
    index = _index()
    icon = index and index["icons"].get(slug)
    if not icon:
        return None
    title, hex6 = icon
    path = _chunk(_bucket(slug, index["chunks"])).get(slug)
    if not path:
        return None
    lum = _luminance(hex6)
    return {
        "kind": "brand",
        "slug": slug,
        "title": title,
        "hex": f"#{hex6}",
        "ink": "#111214" if lum > 0.45 else "#FFFFFF",
        "dark": lum < 0.03,
        "path": spaced(path) or path,
    }
