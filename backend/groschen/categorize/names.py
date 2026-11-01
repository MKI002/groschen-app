"""Readable names for the merchants behind bank bookings.

Banks pass on what a card terminal or the payee's bank wrote: "VISA MCDONALDS 01234",
"AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND", "PayPal Europe S.a.r.l. et Cie S.C.A".
Groschen shows "McDonald's", "Amazon" and the shop behind PayPal instead. The bank's own text
stays on the booking and is shown in its details; only the name in lists changes.
"""

import re
import unicodedata

# Well-known names, matched against the payee as the bank sends it (upper-cased). First match wins.
BRANDS: list[tuple[re.Pattern, str]] = [
    (re.compile(p), name)
    for p, name in [
        (r"KLEINGELD.?PLUS", "Kleingeld Plus"),
        (r"\bAMAZON WEB SERVICES\b|\bAWS EMEA\b", "AWS"),
        (r"\bAMAZON PRIME\b|\bPRIME VIDEO\b", "Amazon Prime"),
        (r"\bAUDIBLE\b", "Audible"),
        (r"\bAMAZON\b|\bAMZN\b|\bAMZ\s?\*", "Amazon"),
        (r"\bANTHROPIC\b|\bCLAUDE\.AI\b", "Claude"),
        (r"\bOPENAI\b|\bCHATGPT\b", "ChatGPT"),
        (r"\bGOOGLE ?CLOUD\b", "Google Cloud"),
        (r"\bGOOGLE PLAY\b", "Google Play"),
        (r"\bGOOGLE ONE\b|\bGOOGLE STORAGE\b", "Google One"),
        (r"\bYOUTUBE\b", "YouTube"),
        (r"\bGOOGLE\b", "Google"),
        (r"\bAPPLE\.COM\b|\bAPPLE SERVICES\b|\bITUNES\b", "Apple"),
        (r"\bMICROSOFT\b|\bMSFT\b", "Microsoft"),
        (r"\bNETFLIX\b", "Netflix"),
        (r"\bSPOTIFY\b", "Spotify"),
        (r"\bDISNEY\s?(\+|PLUS\b)|\bDISNEYPLUS\b", "Disney+"),
        (r"\bDAZN\b", "DAZN"),
        (r"\bPAYPAL\b", "PayPal"),
        (r"\bKLARNA\b", "Klarna"),
        (r"\bEBAY\b", "eBay"),
        (r"\bZALANDO\b", "Zalando"),
        (r"\bIKEA\b", "IKEA"),
        (r"\bMEDIA ?MARKT\b", "MediaMarkt"),
        (r"\bH ?& ?M\b|\bH\+M\b|\bHENNES\b", "H&M"),
        (r"\bREWE\b", "Rewe"),
        (r"\bEDEKA\b", "Edeka"),
        (r"\bALDI ?S(UE|Ü)D\b", "Aldi Süd"),
        (r"\bALDI ?NORD\b", "Aldi Nord"),
        (r"\bALDI\b", "Aldi"),
        (r"\bLIDL\b", "Lidl"),
        (r"\bKAUFLAND\b", "Kaufland"),
        (r"\bNETTO\b", "Netto"),
        (r"\bPENNY\b", "Penny"),
        (r"\bDM[- ]?(DROGERIE|MARKT|FIL)", "dm"),
        (r"\bROSSMANN\b", "Rossmann"),
        (r"\bMC ?DONALD'?S\b", "McDonald's"),
        (r"\bBURGER ?KING\b", "Burger King"),
        (r"\bSTARBUCKS\b", "Starbucks"),
        (r"\bDITSCH\b", "Ditsch"),
        (r"\bLIEFERANDO\b", "Lieferando"),
        (r"\bUBER ?EATS\b", "Uber Eats"),
        (r"\bARAL\b", "Aral"),
        (r"\bSHELL\b", "Shell"),
        (r"\bESSO\b", "Esso"),
        (r"\bAVIA\b", "Avia"),
        (r"\bHEM\b", "HEM"),
        (r"\bJET\b", "Jet"),
        (r"\bTOTAL ?ENERGIES\b|\bTOTAL TANK", "TotalEnergies"),
        (r"\bDB VERTRIEB\b|\bDEUTSCHE BAHN\b|\bDB FERNVERKEHR\b|\bBAHN\.DE\b", "Deutsche Bahn"),
        (r"\bFLIXBUS\b|\bFLIXTRAIN\b", "Flix"),
        (r"\bTELEKOM\b", "Telekom"),
        (r"\bVODAFONE\b", "Vodafone"),
        (r"\bTELEFONICA\b", "O2"),
        (r"\bKLARMOBIL\b", "klarmobil"),
        (r"\bCONGSTAR\b", "congstar"),
        (r"\bBEITRAGSSERVICE\b|\bRUNDFUNK", "Rundfunkbeitrag"),
        (r"\bFINANZAMT\b", "Finanzamt"),
        (r"\bFAMILIENKASSE\b", "Familienkasse"),
        (r"\bHUK[- ]?COBURG\b", "HUK-Coburg"),
        (r"\bALLIANZ\b", "Allianz"),
    ]
]

# Card networks in front of the shop name.
CARD_PREFIX = re.compile(r"^(VISA|MASTERCARD|MAESTRO|GIROCARD|DEBITK?\.?)\s+", re.IGNORECASE)
# Payment providers that put their own short name in front of the shop: "SUMUP *CAFE ROSE".
PROCESSORS = {"SUMUP", "SQ", "SQU", "IZ", "IZETTLE", "ZETTLE", "SPC", "PADDLE", "PADDLENET", "FS", "STRIPE", "PP", "SP"}
# Legal forms and branch words that say nothing about who it is (compared without dots).
LEGAL = {
    "GMBH", "MBH", "GGMBH", "AG", "SE", "KG", "KGAA", "OHG", "GBR", "EK", "EKFR", "EV", "UG", "SARL", "SCA", "SA",
    "RL", "ET", "CIE", "BV", "NV", "LTD", "LIMITED", "INC", "LLC", "CORP", "PLC", "AB", "PUBL", "APS", "OY", "SAS",
    "SPA", "SRL", "CO", "NIEDERLASSUNG", "ZWEIGNIEDERLASSUNG", "DEUTSCHLAND", "DEUTSCHL", "GERMANY",
}  # fmt: skip
# Short words that stay in capitals when an all-caps name is tidied up.
ACRONYMS = {
    "KFZ", "ING", "OBI", "ATU", "HEM", "AXA", "HUK", "ADAC", "IKEA", "DEVK", "AOK", "IKK", "DAK", "BKK", "TK", "BMW",
    "VW", "DB", "DHL", "DPD", "GLS", "UPS", "KFC", "TUI", "UCI", "OMV", "RWE", "EON", "ARD", "ZDF", "DRK", "USA", "UK",
    "EU", "SB", "GEZ", "LVM", "VHV", "HDI", "WGV", "BVG", "MVG", "HVV", "RMV", "VGN", "MVV",
}  # fmt: skip
# Booking texts that only say how money moved; for these the purpose tells more.
PLAIN_TEXTS = {
    "überweisung", "ueberweisung", "echtzeitüberweisung", "echtzeitueberweisung", "lastschrift", "basislastschrift",
    "gutschrift", "dauerauftrag", "gehalt/rente", "lohn/gehalt", "retoure", "rücküberweisung", "sepa-überweisung",
}  # fmt: skip
PAYPAL_SHOP = re.compile(r"(?:Ihr Einkauf bei|Einkauf bei|purchase at)\s+([^,;]+)", re.IGNORECASE)
# ING card payments: "NR XXXX 1234 MUSTERSTADT DE KAUFUMSATZ 02.10 5,80 121357 ARN7400000… Google Pay".
# The bank sync joins the text's lines without spaces, so every space here is optional.
CARD_TEXT = re.compile(r"^NR\s?[X\d]{4}\s?\d{4}\s+(?P<where>.*?)\s?KAUFUMSATZ", re.IGNORECASE | re.DOTALL)
WALLET = re.compile(r"(GOOGLE|APPLE|SAMSUNG|GARMIN|FITBIT)\s?PAY\b", re.IGNORECASE)  # glued to the id before it
# References that only the bank needs: SEPA field tags with their value, card network and long ids.
SEPA_TAG = re.compile(r"\b(?:EREF|MREF|CRED|KREF|PURP|ABWA|ABWE|IBAN|BIC|DEBT|COAM|OAMT|SQTP)\+\S*", re.IGNORECASE)
NOISE = re.compile(r"\bARN\d{6,}|\b(?=[A-Z]*\d)[A-Z0-9]{16,}\b|\bSVWZ\+", re.IGNORECASE)
# "VISA Debitkartenumsatz vom 05.10.2026": only says it was paid by card, on the day the list shows anyway.
CARD_ONLY = re.compile(r"^(?:VISA\s+)?(?:Debit)?karten(?:umsatz|zahlung)(?:\s+vom\s+[\d.]+)?$", re.IGNORECASE)


def _tidy_caps(word: str) -> str:
    if word.upper() in ACRONYMS or "&" in word or any(c.isdigit() for c in word) or not any(c.isalpha() for c in word):
        return word
    return "-".join(p[:1].upper() + p[1:].lower() for p in word.split("-"))


def clean(raw: str | None) -> str:
    """A readable name for a payee as the bank sends it. Empty in, empty out."""
    text = " ".join((raw or "").split())
    if not text:
        return ""
    upper = text.upper()
    for pattern, name in BRANDS:
        if pattern.search(upper):
            return name
    card = bool(CARD_PREFIX.match(text)) and not re.match(r"\S+\s+(KARTEN)?ABRECHNUNG\b", upper)
    s = CARD_PREFIX.sub("", text) if card else text
    s = re.sub(r"\([^)]*\)", " ", s)  # (KdoR), (publ), (haftungsbeschränkt)
    if "*" in s:
        left, right = (p.strip() for p in s.split("*", 1))
        tag = re.sub(r"[^A-Z]", "", left.upper())
        s = right if (tag in PROCESSORS and right) or not left else left
    if "," in s:
        head, tail = s.split(",", 1)
        if re.search(r"NIEDERLASSUNG|ZWEIGNL|FILIALE|BRANCH|\d", tail.upper()):
            s = head
    caps = not any(c.islower() for c in s)
    words = s.split()
    kept: list[str] = []
    for w in words:
        bare = re.sub(r"[.,;:]", "", w).upper()
        digits = sum(c.isdigit() for c in w)
        # A store number ends the name: what follows is a branch or place code ("12345 ABC").
        if kept and digits and (card or digits >= 4 or (len(w) >= 5 and any(c.isalpha() for c in w))):
            break
        if kept and bare in LEGAL:
            continue
        w = re.sub(r"-(AG|GMBH|KG|SE)$", "", w.strip(",;:"), flags=re.IGNORECASE)
        if kept and re.fullmatch(r"VERSICHERUNGS?", w.upper()):
            w = "Versicherung"
        kept.append(w)
    while len(kept) > 1 and len(re.sub(r"\W", "", kept[-1])) <= 1:
        kept.pop()  # "& C", a cut-off "& Co"
    s = " ".join(kept).strip(" -,.;:/&")
    if not s:
        return text
    if caps:
        s = " ".join(_tidy_caps(w) for w in s.split())
    return s


def _card_detail(match: re.Match, text: str) -> str:
    """Where and how a card payment was made: "Musterstadt · Google Pay", "US" for a shop abroad."""
    where = " ".join(match.group("where").split())
    place, country = where, ""
    m = re.match(r"^(.*?)\s*\b([A-Z]{2})$", where)
    if m:
        place, country = m.group(1), m.group(2)
    # Online shops put their web address or phone number where the town goes: the name says it already.
    if re.search(r"\d{4,}|\.|WWW|HTTP", place, re.IGNORECASE) or len(place) < 2:
        place = ""
    town = " ".join(_tidy_caps(w) for w in place.split()) if place.isupper() else place
    abroad = country if country and country != "DE" else ""
    wallet = WALLET.search(text)
    parts = [", ".join(p for p in (town, abroad) if p), f"{wallet.group(1).title()} Pay" if wallet else ""]
    return " · ".join(p for p in parts if p)


def display_detail(tx: dict) -> str:
    """The second line in lists: the purpose without what only the bank needs. Empty when it adds nothing.

    The full bank text stays in the booking's details.
    """
    purpose = " ".join((tx.get("purpose") or "").split())
    if not purpose:
        return ""
    card = CARD_TEXT.match(purpose)
    if card:
        return _card_detail(card, purpose)
    text = NOISE.sub(" ", SEPA_TAG.sub(" ", purpose))
    text = " ".join(text.split()).strip(" ,;:/-.")
    name = display_name(tx).lower()
    if not text or CARD_ONLY.match(text) or text.lower() == name or text.lower() in (tx.get("counterparty") or "").lower():
        return ""
    return text[:120]


def display_name(tx: dict) -> str:
    """The name lists show for a booking: the cleaned payee, the shop behind PayPal, or what was booked."""
    cp = (tx.get("counterparty") or "").strip()
    purpose = (tx.get("purpose") or "").strip()
    if cp and "PAYPAL" in cp.upper():
        m = PAYPAL_SHOP.search(purpose)
        shop = clean(m.group(1)) if m else ""
        return shop or "PayPal"
    if cp:
        return clean(cp)
    booking = (tx.get("booking_text") or "").strip()
    if booking and booking.lower() not in PLAIN_TEXTS:
        return booking[:60]
    return (purpose or booking or "Unknown")[:60]


def name_key(name: str) -> str:
    """What two shown names must share to be one merchant: case, accents, spaces and dots don't count.

    Banks write the same payee as "AquaNetworks" one month and "Aqua Networks" the next.
    """
    folded = unicodedata.normalize("NFKD", (name or "").casefold())
    return "".join(c for c in folded if c.isalnum())
