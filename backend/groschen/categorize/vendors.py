"""Thousands of well-known shops, brands and services, and the category each one belongs to.

The list itself is in vendor_list.py. Here it is turned into a word lookup: the booking text is cut
into words once and every run of words that can start a known name is looked up in a dict, so matching stays fast
however long the list gets. A name only matches as whole words ("ICA" never matches "AMERICA").

Names written with a leading "^", and single words shorter than four letters, only count when the
payee starts with them, after card and payment-provider prefixes such as "VISA" or "SQ *". That is
how ordinary words that are also shop names ("Target", "Coop", "Boots") stay safe:
"TARGET T-1234 MINNEAPOLIS" is a shop, "Anna Schmidt, Target 2027 erreicht" is not.
"""

import re
import unicodedata

from .vendor_list import PAYMENT_SERVICES, VENDORS

# Letters German banks spell out, and letters Unicode does not split into base letter plus accent.
_FOLD = str.maketrans({"Ä": "AE", "Ö": "OE", "Ü": "UE", "ß": "SS", "Æ": "AE", "Œ": "OE", "Ø": "OE", "Ł": "L", "Đ": "D"})
_PLAIN = str.maketrans({"Ä": "A", "Ö": "O", "Ü": "U", "Ø": "O", "Æ": "AE", "Œ": "OE", "ß": "SS", "Ł": "L", "Đ": "D"})
_TOKEN = re.compile(r"[A-Z0-9]+|[&+]")
# Words in front of the shop name that only say how it was paid.
_LEAD_SKIP = {
    "VISA", "MASTERCARD", "MC", "MAESTRO", "GIROCARD", "DEBITK", "DEBITKARTE", "KARTENZAHLUNG", "KARTENUMSATZ",
    "POS", "CRV", "ACH", "CHECKCARD", "PURCHASE", "DEBIT", "CARD", "RECURRING", "PAYMENT", "PAYPAL", "PP",
    "SQ", "SQU", "SUMUP", "SUM", "UP", "ZETTLE", "IZ", "IZETTLE", "SP", "SPC", "STRIPE", "PADDLE",
    "CB", "CARTE", "PAIEMENT", "COMPRA", "PAGO", "PAGAMENTO", "BETALING", "KORTBETALNING", "KAUF", "NR",
}  # fmt: skip
MIN_ANYWHERE = 4  # a single word shorter than this only counts at the start of the payee ("KFC 1234")


def _fold(text: str, table) -> str:
    text = text.upper().translate(table)
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def words(text: str | None) -> list[str]:
    """Upper-cased words, umlauts spelled out the way German banks do (Ä -> AE), accents dropped."""
    text = (text or "").replace("'", "").replace("’", "").replace("`", "")
    return _TOKEN.findall(_fold(text, _FOLD))


def _variants(key: str) -> set[tuple[str, ...]]:
    """The ways a bank may spell a name: "Müller" as MUELLER or MULLER, "Burger King" also as BURGERKING."""
    key = key.replace("'", "").replace("’", "")
    out = {tuple(_TOKEN.findall(_fold(key, _FOLD))), tuple(_TOKEN.findall(_fold(key, _PLAIN)))}
    for w in list(out):
        if 1 < len(w) <= 3 and all(t.isalnum() and len(t) > 1 for t in w) and len("".join(w)) >= 6:
            out.add(("".join(w),))
    return {w for w in out if w}


def _build():
    anywhere: dict[tuple[str, ...], tuple[str, str, bool]] = {}
    lead: dict[tuple[str, ...], tuple[str, str, bool]] = {}
    blocks = [(category, block, False) for category, block in VENDORS.items()]
    for category, block, weak in [*blocks, ("Online shopping", PAYMENT_SERVICES, True)]:
        for line in block.splitlines():
            line = line.split("#", 1)[0]
            for entry in line.split(","):
                entry = entry.strip()
                if not entry:
                    continue
                name, _, aliases = entry.partition("=")
                name = name.strip()
                display = name.lstrip("^")
                keys = [k.strip() for k in [name, *aliases.split("/")] if k.strip()]
                if any(k.startswith("^") and words(k) == words(display) for k in keys[1:]):
                    keys[0] = "^" + display  # "TÜV = ^TUEV": the name itself only counts at the start too
                for key in keys:
                    key = key.strip()
                    if not key:
                        continue
                    only_lead = key.startswith("^")
                    for w in _variants(key.lstrip("^")):
                        short = len(w) == 1 and len(w[0]) < MIN_ANYWHERE
                        table = lead if only_lead or short else anywhere
                        table.setdefault(w, (category, display, weak))
    return anywhere, lead


ANYWHERE, LEAD = _build()
_FIRST = {}
for _w in (*ANYWHERE, *LEAD):
    _FIRST[_w[0]] = max(_FIRST.get(_w[0], 0), len(_w))


def _lead_words(name: str | None) -> list[str]:
    w = words(name)
    while w and (w[0] in _LEAD_SKIP or w[0].isdigit()):
        w = w[1:]
    return w


def _rank(size: int, hit) -> tuple[bool, int]:
    return (not hit[2], size)  # a shop beats a payment service, a longer name a shorter one


def _longest(w: list[str], table, start_only: bool = False):
    best = None
    for i in range(min(1, len(w)) if start_only else len(w)):
        n = _FIRST.get(w[i], 0)
        for size in range(min(n, len(w) - i), 0, -1):
            hit = table.get(tuple(w[i : i + size]))
            if hit:
                if not best or _rank(size, hit) > best[0]:
                    best = (_rank(size, hit), hit)
                break
    return best


def match(text: str | None, payees: tuple[str | None, ...] = ()) -> tuple[str, str] | None:
    """(category, shop name) for the best-known name in a booking, or None.

    text is the whole booking text; payees are the names a booking is from or to (the
    counterparty, the shop behind PayPal). The longest name wins, so "Uber Eats" beats "Uber"; on a
    tie the name the payee starts with wins. Payment services such as Klarna count only without a shop.
    """
    best = _longest(words(text), ANYWHERE)
    for payee in payees:
        lw = _lead_words(payee)
        for table in (LEAD, ANYWHERE):
            hit = _longest(lw, table, start_only=True)
            if hit and (not best or hit[0] >= best[0]):
                best = hit
    return best[1][:2] if best else None


def shop_name(payee: str | None) -> str | None:
    """The tidy name of a known shop when the payee starts with it ("CARREFOUR 1234 PARIS" -> Carrefour)."""
    lw = _lead_words(payee)
    for table in (LEAD, ANYWHERE):
        hit = _longest(lw, table, start_only=True)
        if hit and not hit[1][2]:
            return hit[1][1]
    return None
