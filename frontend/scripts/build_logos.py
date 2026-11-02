"""Build src/data/logos/, the brand logos Groschen ships, from a Simple Icons release.

    npm pack simple-icons@<version> --ignore-scripts && tar xzf simple-icons-<version>.tgz
    python3 -I frontend/scripts/build_logos.py package   # from the repository root

Every icon whose licence allows it goes in; the app never fetches a logo from the internet.
Names come from two places: the vendor list (backend/groschen/categorize/vendor_list.py, with its
spellings and "only at the start" rules) and each icon's own title and aliases. An icon's own
title is used more carefully, because it was never checked against booking texts: a name of two or
more words, or one long unusual word, counts at the start of the payee; anything shorter or more
common only when it is the whole name ("Max" is a first name before it is a streaming service).
"""

import json
import pathlib
import re
import sys
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
from groschen.categorize import vendors  # noqa: E402

# Only public-domain icons: those without a licence entry are released under CC0 by Simple Icons.
# Icons under any licence of their own (even MIT or CC BY, which ask for credit) stay out.
FREE = {None, "CC0-1.0", "Unlicense"}

# Brands a bank writes differently from the logo's title. Key: icon slug.
EXTRA_LEAD = {
    "edeka": ["E CENTER", "ECENTER", "E AKTIV", "E NEUKAUF", "EDEKA"],
    "claude": ["CLAUDE AI", "CLAUDE.AI", "ANTHROPIC"],
    "googleplay": ["GOOGLE PLAY", "GOOGLEPLAY", "GOOGLE PLAY APPS"],
    "dm": ["DM DROGERIE", "DM DROGERIEMARKT", "DM FIL"],
    "deutschebahn": ["DB VERTRIEB", "DB FERNVERKEHR", "DB REGIO", "DEUTSCHE BAHN"],
    "deutschetelekom": ["TELEKOM DEUTSCHLAND", "TELEKOM"],
    "aral": ["ARAL"],
    "shell": ["SHELL"],
}
EXTRA_EXACT = {"claude": ["CLAUDE"]}
# Vendor-list names that should show a different icon than their own title would.
VENDOR_ICON = {
    "Anthropic": "claude",
    "Edeka Getränkemarkt": "edeka",
    "Edeka Xpress": "edeka",
    "Edeka Smart": "edeka",
}

# Single words that are too ordinary to stand for a brand at the start of a payee.
COMMON = set(
    """A AN AND THE OF FOR TO IN ON AT BY WITH FROM DER DIE DAS UND ODER FUER MIT VON ZU AM IM DE LA LE LES ET DU EL
    MAX TIM TOM ANNA MARIA MARTA BART JAN PETER PAUL JULES DAVID MICHAEL LEO LISA SARA EMMA LUCA MARCO PIERRE JEAN HANS
    KARL FRITZ JOHN JAMES MARY LINDA ROSE CORA AIDA OTTO HUGO FELIX OSCAR OLIVER HENRY VICTOR MILO ALEX SAM NOAH
    CLAUDE ROBERT MARTIN THOMAS DANIEL ANDREAS STEFAN MARKUS MATTHIAS CHRISTIAN SEBASTIAN FLORIAN TOBIAS JULIAN
    PATRICK SIMONE SABINE MONIKA ANDREA CLAUDIA SANDRA NICOLE MELANIE CHARLOTTE SOPHIE HANNAH GEORGE ARTHUR
    WALTER WERNER GUENTER HELMUT HEINZ GERHARD WOLFGANG JUERGEN BERND FRANZ JOSEF LORENZ VINCENT ADRIAN DAMIAN
    ALBERT ROLAND RICHARD EDWARD CHARLES WILLIAM HAROLD ARNOLD OSWALD SILVIA VIKTOR MORITZ JONAS ELIAS LUKAS
    PLUS MORE LIFE TIME WORLD NATURE SUN SUMMER SPRING FALL WINTER APPLE PEACH LEMON CHERRY GOLD SILVER
    BANK PAY PAYMENT CARD SHOP STORE MARKET CITY HOME HOUSE BOOK BOOKS ONLINE SERVICE SERVICES DIGITAL STUDIO
    CENTER CENTRE GROUP MEDIA ENERGY POWER DIRECT GLOBAL SYSTEMS NETWORK CLOUD DATA SMART OPEN FRESH SIMPLE
    GUTSCHEIN RECHNUNG ZAHLUNG UEBERWEISUNG DAUERAUFTRAG LASTSCHRIFT GUTSCHRIFT INVOICE TRANSFER SAVINGS SPARPLAN
    """.split()
)
LONG = 6  # a single word this long (and not common) is unusual enough to count at the start


CHUNKS = 48


def bucket(slug: str) -> int:
    h = 5381
    for c in slug:
        h = (h * 33 + ord(c)) % 4294967296
    return h % CHUNKS


def key(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s.casefold()) if c.isalnum())


PATH = re.compile(r"^[MmLlHhVvCcSsQqTtAaZz0-9eE.,+\s-]+$")  # SVG path commands and numbers, nothing else


def path_of(svg: str) -> str | None:
    m = re.search(r'<path d="([^"]+)"', svg)
    return m.group(1) if m and PATH.match(m.group(1)) and len(m.group(1)) < 60000 else None


def main(pkg: str) -> None:
    pkg = pathlib.Path(pkg)
    meta = json.loads((pkg / "package.json").read_text())
    data = json.loads((pkg / "data" / "simple-icons.json").read_text())
    icons, by_name, skipped = {}, {}, 0
    for icon in data:
        lic = (icon.get("license") or {}).get("type")
        svg = pkg / "icons" / f"{icon['slug']}.svg"
        if lic not in FREE or not svg.exists():
            skipped += 1
            continue
        path = path_of(svg.read_text())
        ok = re.fullmatch(r"[0-9A-Fa-f]{6}", icon["hex"]) and re.fullmatch(r"[a-z0-9_.-]{1,80}", icon["slug"])
        if not path or not ok:
            skipped += 1
            continue
        icons[icon["slug"]] = [icon["title"][:80], icon["hex"].upper(), path]
        for name in [icon["title"], *((icon.get("aliases") or {}).get("aka") or [])]:
            by_name.setdefault(key(name), icon["slug"])

    anywhere, lead, exact = {}, {}, {}

    def put(table, words, slug):
        if words and slug in icons:
            table.setdefault(" ".join(words), slug)

    # 1. The vendor list, with its own rules for where a name may stand.
    for src, dst in ((vendors.ANYWHERE, anywhere), (vendors.LEAD, lead)):
        for words, (_cat, display, _weak) in src.items():
            put(dst, words, VENDOR_ICON.get(display) or by_name.get(key(display)))
    # 2. Spellings banks use that neither list knows.
    for slug, names in EXTRA_LEAD.items():
        for n in names:
            put(lead, tuple(vendors.words(n)), slug)
    for slug, names in EXTRA_EXACT.items():
        for n in names:
            put(exact, tuple(vendors.words(n)), slug)
    # 3. Every other icon by its own title and aliases.
    for icon in data:
        slug = icon["slug"]
        if slug not in icons:
            continue
        for name in [icon["title"], *((icon.get("aliases") or {}).get("aka") or [])]:
            for w in vendors._variants(name):
                j = " ".join(w)
                if j in anywhere or j in lead:
                    continue
                if len(w) >= 2 and not all(x in COMMON or x.isdigit() for x in w):
                    put(lead, w, slug)
                elif len(w) == 1 and len(w[0]) >= LONG and w[0] not in COMMON and not w[0].isdigit():
                    put(lead, w, slug)
                else:
                    put(exact, w, slug)

    used = set(anywhere.values()) | set(lead.values()) | set(exact.values())
    out = {
        "source": f"Simple Icons {meta['version']} (https://simpleicons.org), CC0 1.0 unless noted in NOTICE",
        "chunks": CHUNKS,
        "icons": {},
        "any": dict(sorted(anywhere.items())),
        "lead": dict(sorted(lead.items())),
        "exact": dict(sorted(exact.items())),
    }
    # The drawings are split into small files by a hash of the slug, so a list loads only the few
    # files its logos are in, not all of them (lib/logos.ts computes the same hash).
    folder = ROOT / "frontend" / "src" / "data" / "logos"
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob("*.json"):
        old.unlink()
    chunks: dict[int, dict[str, str]] = {}
    for slug, (title, hexcode, path) in icons.items():
        chunks.setdefault(bucket(slug), {})[slug] = path
        out["icons"][slug] = [title, hexcode]
    for n, part in chunks.items():
        (folder / f"{n:02d}.json").write_text(json.dumps(part, separators=(",", ":")) + "\n")
    dest = folder / "index.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")) + "\n")
    (folder / "NOTICE.md").write_text(
        "# Brand logos\n\n"
        f"The brand logos in this folder come from [Simple Icons](https://simpleicons.org) {meta['version']} and are "
        "public domain ([CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)). Icons that carry a licence "
        "of their own were left out.\n\n"
        "All brand names and logos are trademarks of their respective owners. Groschen shows them only to tell "
        "you who a payment went to; this does not mean any brand endorses Groschen. Every logo can be replaced "
        "with your own picture or a letter in the app. Rebuild with frontend/scripts/build_logos.py.\n"
    )
    print(
        f"{len(icons)} icons ({skipped} left out), {len(used)} matched by name; "
        f"{len(anywhere)} anywhere, {len(lead)} lead, {len(exact)} exact; {dest.stat().st_size // 1024} KB"
    )


if __name__ == "__main__":
    main(sys.argv[1])
