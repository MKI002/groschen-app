"""Which German bank a Bankleitzahl belongs to, and where its FinTS server is.

Three sources, best first:

1. The FinTS institute list of the Deutsche Kreditwirtschaft. Everyone who registers a
   FinTS product gets it with the product ID; imported in Settings, it covers every bank
   in Germany, Sparkassen included (they each have their own server address).
2. The big banks built in below, found by name or by any of their Bankleitzahlen.
3. The bank group, which the fourth digit of a Bankleitzahl tells: Volksbanken and
   Raiffeisenbanken share one server, so do Deutsche Bank and Commerzbank branches.

Anything else can be connected by typing the server address from the bank's website.
Nothing here goes online: the list is a file in the image or one the user imports.
"""

import csv
import io
import re
from urllib.parse import urlsplit

from ..jobs import UserFacingError

ATRUVIA = "https://fints1.atruvia.de/cgi-bin/hbciservlet"
DEUTSCHE_BANK = "https://fints.deutsche-bank.de/"
COMMERZBANK = "https://fints.commerzbank.de/fints"

# label: the name in sentences ("Log in to DKB"); short: the two to four letters on its badge.
# login: which name the bank gives the login (the web page shows it in the user's language).
# app: the app that approves requests ("decoupled" approval). tested: confirmed on a real account.
KNOWN = [
    {
        "id": "ing",
        "label": "ING",
        "name": "ING-DiBa AG",
        "short": "ING",
        "blz": ["50010517"],
        "server": "https://fints.ing.de/fints/",
        "bic": "INGDDEFFXXX",
        "login": "zugangsnummer",
        "app": "ING App",
        "tested": True,
    },
    {
        "id": "sparkasse",
        "label": "Sparkasse",
        "name": "Sparkasse",
        "short": "Spk",
        "blz": [],
        "server": None,
        "login": "sparkasse",
        "app": "S-pushTAN",
        "group": "5",
    },
    {
        "id": "vr",
        "label": "Volksbank",
        "name": "Volksbank / Raiffeisenbank",
        "short": "VR",
        "aliases": ["Volksbank", "Raiffeisenbank", "VR Bank", "Sparda-Bank", "PSD Bank", "GLS Bank", "BBBank"],
        "blz": [],
        "server": ATRUVIA,
        "login": "vr",
        "app": "VR SecureGo plus",
        "group": "69",
    },
    {
        "id": "deutsche-bank",
        "label": "Deutsche Bank",
        "name": "Deutsche Bank",
        "short": "DB",
        "blz": ["10070000", "20070000", "25070070", "30070010", "37070060", "50070010", "60070070", "70070010"],
        "server": DEUTSCHE_BANK,
        "login": "deutschebank",
        "app": "Deutsche Bank photoTAN",
        "group": "7",
    },
    {
        "id": "postbank",
        "label": "Postbank",
        "name": "Postbank",
        "short": "PB",
        "blz": [
            "10010010",
            "20010020",
            "25010030",
            "36010043",
            "37010050",
            "44010046",
            "50010060",
            "54510067",
            "55010065",
            "59010066",
            "60010070",
            "66010075",
            "70010080",
            "76010085",
            "86010090",
        ],
        "server": "https://hbci.postbank.de/banking/hbci.do",
        "login": "postbank",
        "app": "Postbank BestSign",
    },
    {
        "id": "commerzbank",
        "label": "Commerzbank",
        "name": "Commerzbank",
        "short": "CB",
        "blz": ["10040000", "20040000", "30040000", "37040044", "50040000", "60040071", "70040041"],
        "server": COMMERZBANK,
        "login": "commerzbank",
        "app": "Commerzbank photoTAN",
        "group": "48",
    },
    {
        "id": "comdirect",
        "label": "comdirect",
        "name": "comdirect",
        "short": "cd",
        "blz": ["20041111", "20041133", "20041144", "20041155"],
        "server": "https://fints.comdirect.de/fints",
        "login": "zugangsnummer",
        "app": "comdirect photoTAN",
    },
    {
        "id": "dkb",
        "label": "DKB",
        "name": "DKB Deutsche Kreditbank",
        "short": "DKB",
        "blz": ["12030000"],
        "server": "https://banking-dkb.s-fints-pt-dkb.de/fints30",
        "login": "dkb",
        "app": "DKB App",
    },
    {
        "id": "consorsbank",
        "label": "Consorsbank",
        "name": "Consorsbank",
        "short": "Cons",
        "blz": ["76030080"],
        "server": "https://brokerage-hbci.consorsbank.de/hbci",
        "login": "consors",
        "app": "Consorsbank SecurePlus",
    },
    {
        "id": "hvb",
        "label": "HypoVereinsbank",
        "name": "HypoVereinsbank (UniCredit)",
        "short": "HVB",
        "blz": ["70020270", "10020890", "20030000", "30220190", "60020290"],
        "server": "https://hbci-01.hypovereinsbank.de/bank/hbci",
        "login": "generic",
        "app": "HVB Mobile Banking",
    },
    {
        "id": "norisbank",
        "label": "norisbank",
        "name": "norisbank",
        "short": "nb",
        "blz": ["10077777"],
        "server": "https://fints.norisbank.de/",
        "login": "deutschebank",
        "app": "norisbank App",
    },
]

# Banks people ask for that have no FinTS access at all: their CSV export still works.
NO_FINTS = ["N26", "Trade Republic", "Revolut", "C24", "Vivid", "bunq", "Scalable Capital", "Tomorrow"]

_BY_ID = {b["id"]: b for b in KNOWN}
_BY_BLZ = {code: b for b in KNOWN for code in b["blz"]}

IBAN_DE = re.compile(r"^DE\d{20}$")


def blz_from(text: str) -> str | None:
    """A Bankleitzahl from what the user typed: the 8 digits themselves or a German IBAN."""
    t = re.sub(r"\s+", "", text or "").upper()
    if re.fullmatch(r"\d{8}", t):
        return t
    if IBAN_DE.match(t):
        return t[4:12]
    return None


def _group(blz: str) -> dict | None:
    """The bank group a Bankleitzahl belongs to, from its fourth digit."""
    digit = blz[3]
    for b in KNOWN:
        if digit in b.get("group", ""):
            return b
    return None


def check_server(url: str) -> str:
    """A FinTS address the user typed: HTTPS to a host name on the internet, nothing else."""
    url = (url or "").strip()
    parts = urlsplit(url)
    host = (parts.hostname or "").lower()
    if (
        parts.scheme != "https"
        or not host
        or "." not in host
        or parts.username
        or parts.password
        or parts.port not in (None, 443)
        or re.fullmatch(r"[\d.]+|\[?[0-9a-f:]+\]?", host)
        or host.endswith((".local", ".lan", ".internal", ".home", ".localhost"))
    ):
        raise UserFacingError("The FinTS address must start with https:// and name the bank's server.")
    return url


def host_of(url: str) -> str:
    return (urlsplit(url).hostname or "").lower()


def _view(b: dict, blz: str | None, server: str | None, name: str | None = None, source: str = "known") -> dict:
    return {
        "id": b["id"] if b else "other",
        "name": name or (b["name"] if b else None) or "Bank",
        # A bank from the institute list is called by its own name, not its group's.
        "label": name or (b["label"] if b else None) or "Bank",
        "short": b["short"] if b else _short(name),
        "blz": blz,
        "server": server,
        "bic": b.get("bic") if b else None,
        "login": b["login"] if b else "generic",
        "app": b.get("app") if b else None,
        "tested": bool(b and b.get("tested")),
        # A bank with many Bankleitzahlen needs the user's own (it is in the IBAN).
        "needs_blz": blz is None,
        "needs_server": server is None,
        "source": source,
    }


def _short(name: str | None) -> str:
    words = [w for w in re.split(r"[\s\-/]+", name or "") if w and w[0].isalpha()]
    if not words:
        return "Bank"
    if len(words) == 1:
        return words[0][:4]
    return "".join(w[0] for w in words[:3]).upper()


def resolve(conn, blz: str, server: str | None = None) -> dict:
    """Everything Groschen knows about the bank behind a Bankleitzahl."""
    if not re.fullmatch(r"\d{8}", blz or ""):
        raise UserFacingError("A Bankleitzahl has 8 digits. It is also in your IBAN, right after DE and two digits.")
    listed = (
        conn.execute(
            "SELECT name, server FROM bank_directory WHERE blz = ? ORDER BY server IS NULL, name LIMIT 1", (blz,)
        ).fetchone()
        if conn
        else None
    )
    known = _BY_BLZ.get(blz)
    group = known or _group(blz)
    if known:
        info = _view(known, blz, known["server"])
    elif listed:
        info = _view(group, blz, listed["server"] or (group or {}).get("server"), listed["name"], "list")
    elif group:
        info = _view(group, blz, group["server"], source="group")
    else:
        info = _view(None, blz, None, source="none")
    if server:
        info["server"] = check_server(server)
        info["needs_server"] = False
    return info


def search(conn, q: str, limit: int = 8) -> list[dict]:
    """Banks matching what the user typed: a Bankleitzahl, an IBAN or part of a name."""
    q = (q or "").strip()
    if not q:
        return [_view(b, b["blz"][0] if len(b["blz"]) == 1 else None, b["server"]) for b in KNOWN]
    blz = blz_from(q)
    if blz:
        return [resolve(conn, blz)]
    needle = q.lower()
    out = []
    for b in KNOWN:
        names = [b["name"], b["short"], *b.get("aliases", [])]
        if any(needle in n.lower() for n in names):
            out.append(_view(b, b["blz"][0] if len(b["blz"]) == 1 else None, b["server"]))
    if conn is not None and len(needle) >= 3:
        rows = conn.execute(
            "SELECT blz, name, server FROM bank_directory WHERE LOWER(name) LIKE ? AND server IS NOT NULL "
            "ORDER BY name LIMIT ?",
            (f"%{needle}%", limit),
        ).fetchall()
        for r in rows:
            group = _BY_BLZ.get(r["blz"]) or _group(r["blz"])
            out.append(_view(group, r["blz"], r["server"], r["name"], "list"))
    for name in NO_FINTS:
        if needle in name.lower():
            out.append({**_view(None, None, None, name, "csv"), "id": "csv-only", "short": _short(name)})
    return out[:limit]


def by_id(bank_id: str) -> dict | None:
    return _BY_ID.get(bank_id)


# --- the institute list ---------------------------------------------------------------


def _decode(raw: bytes) -> str:
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1", errors="replace")


def _norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue"))


def parse_directory(raw: bytes) -> list[tuple[str, str, str | None]]:
    """The FinTS institute list (CSV or the CSV saved from its Excel file): BLZ, name, PIN/TAN address."""
    text = _decode(raw)
    first = text.split("\n", 1)[0]
    delim = ";" if first.count(";") >= first.count(",") else ","
    reader = csv.reader(io.StringIO(text), delimiter=delim)
    header = None
    out = []
    for cells in reader:
        names = [_norm(c) for c in cells]
        if header is None:
            if "blz" in names:
                header = names
                i_blz = names.index("blz")
                i_name = next((i for i, n in enumerate(names) if n in ("institut", "institutsname", "name")), None)
                i_url = next((i for i, n in enumerate(names) if n.startswith("pintanzugangurl") or n == "pintanurl"), None)
                if i_name is None or i_url is None:
                    header = None
                    break
            continue
        if len(cells) <= max(i_blz, i_name, i_url):
            continue
        blz = cells[i_blz].strip()
        if not re.fullmatch(r"\d{8}", blz):
            continue
        url = cells[i_url].strip()
        try:
            url = check_server(url) if url else None
        except UserFacingError:
            url = None
        out.append((blz, " ".join(cells[i_name].split())[:120], url))
    if header is None or not out:
        raise UserFacingError(
            "This isn't the FinTS institute list. It is the file with the columns BLZ, Institut and "
            "PIN/TAN-Zugang URL that came with your product registration."
        )
    return out


def import_directory(conn, raw: bytes) -> dict:
    rows = parse_directory(raw)
    conn.execute("DELETE FROM bank_directory")
    conn.executemany(
        "INSERT OR REPLACE INTO bank_directory (blz, name, server) VALUES (?, ?, ?)",
        rows,
    )
    return {"banks": len({r[0] for r in rows}), "with_fints": sum(1 for r in rows if r[2])}


def directory_size(conn) -> int:
    return conn.execute("SELECT COUNT(*) FROM bank_directory").fetchone()[0]
