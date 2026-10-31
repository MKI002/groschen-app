"""Reader for the CSV exports of German banks.

Every bank lays its export out differently, so columns are found by their names, and
each name a bank uses is listed below: ING ("Umsatzanzeige"), Sparkasse (CSV-CAMT and
CSV-MT940), Volksbanken and Raiffeisenbanken, DKB (old and new), comdirect, Deutsche
Bank, Postbank, Commerzbank, Consorsbank, N26 and others that use the same words.
Semicolons, commas or tabs, German or English numbers, one amount column or a debit and
a credit column: all of it is found from the file itself.

Most files start with a few "key;value" lines (IBAN, account name, balance) before the
header row. Files without them still work: the IBAN is in the file name some banks give
the export (Umsatzanzeige_<IBAN>_<date>.csv), and where every row carries the balance
after it, the newest row says what is on the account.
"""

import csv
import io
import re
from datetime import datetime

from ..jobs import UserFacingError


def _decode(raw: bytes) -> str:
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1", errors="replace")


def parse_amount(text: str) -> float:
    """German (-1.234,56) or English (-1,234.56) numbers, with or without a currency or trailing minus."""
    t = (text or "").strip().replace("−", "-").replace("\u00a0", "").replace(" ", "")
    t = re.sub(r"(?i)eur|€", "", t).replace("+", "")
    if not t:
        return 0.0
    if t.endswith("-"):
        t = "-" + t[:-1]
    if "," in t and "." in t:
        t = t.replace(".", "").replace(",", ".") if t.rfind(",") > t.rfind(".") else t.replace(",", "")
    elif "," in t or re.fullmatch(r"-?\d{1,3}(\.\d{3})+", t):
        # "2.500" in a German file is two and a half thousand.
        t = t.replace(".", "").replace(",", ".")
    return round(float(t), 2)


def parse_date(text: str) -> str:
    text = (text or "").strip()
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d.%m.%y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue
    raise ValueError(f"not a date: {text!r}")


def _valid_iban(iban: str) -> bool:
    digits = "".join(str(int(c, 36)) for c in iban[4:] + iban[:4])
    return int(digits) % 97 == 1


def norm(name: str) -> str:
    """A column name without case, umlauts, spaces or punctuation: "Betrag (€)" is "betrag"."""
    t = (name or "").strip().strip('"').lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        t = t.replace(a, b)
    return re.sub(r"[^a-z0-9]", "", t)


# The names banks give each column, most specific first.
COLUMNS = {
    "date": ["buchung", "buchungstag", "buchungsdatum", "bookingdate", "datum", "date"],
    "value_date": ["wertstellungsdatum", "valutadatum", "valuta", "wertstellung", "wertstellungvaluta", "wert", "valuedate"],
    "amount": [
        "betrag",
        "betrageur",
        "betragineur",
        "betrageuro",
        "umsatzineur",
        "umsatz",
        "amounteur",
        "amount",
        "betragwaehrung",
    ],
    "debit": ["soll", "solleur", "ausgang", "belastung"],
    "credit": ["haben", "habeneur", "eingang", "gutschrift"],
    "sign": ["sollhaben", "sh"],
    "currency": ["waehrung", "wahrung", "currency"],
    "counterparty": [
        "auftraggeberempfaenger",
        "beguenstigterzahlungspflichtiger",
        "namezahlungsbeteiligter",
        "beguenstigterauftraggeber",
        "auftraggeberbeguenstigter",
        "senderempfaenger",
        "empfaengerauftraggeber",
        "zahlungsbeteiligter",
        "partnername",
        "payee",
        "gegenpartei",
        "name",
    ],
    "payer": ["zahlungspflichtiger", "zahlungspflichtigein", "auftraggeber"],
    "payee": ["zahlungsempfaengerin", "zahlungsempfaenger", "empfaenger"],
    "counterparty_iban": [
        "kontonummeriban",
        "ibanzahlungsbeteiligter",
        "ibanauftraggeberkonto",
        "ibankontonr",
        "partneriban",
        "gegenkontoiban",
        "iban",
        "kontonummer",
    ],
    "purpose": ["verwendungszweck", "paymentreference", "buchungsdetails", "beschreibung", "description", "reference"],
    "booking_text": ["buchungstext", "umsatzart", "umsatztyp", "vorgang", "buchungsart", "transaktionstyp", "type"],
    "balance": ["saldonachbuchung", "saldo", "saldoeur", "kontostand"],
    "own_iban": ["ibanauftragskonto", "auftragskonto", "ibankontoinhaber"],
    "own_name": ["bezeichnungauftragskonto", "accountname"],
    "status": ["status"],
}

# comdirect and Commerzbank put everything into one text: "Empfänger: … Kto/IBAN: … Buchungstext: …".
_PARTY_IN_TEXT = re.compile(
    r"(?:Auftraggeber|Empf(?:ä|ae)nger)\s*:\s*(.+?)(?=\s+(?:Kto/IBAN|IBAN|BLZ/BIC|Buchungstext)\s*:|$)", re.I
)
_PURPOSE_IN_TEXT = re.compile(r"Buchungstext\s*:\s*(.+?)(?=\s+Ref\.\s|$)", re.I)
_ACCOUNT_NAME = re.compile(
    r"\b(Girokonto|Extra-Konto|Tagesgeld\w*|Sparkonto|Gemeinschaftskonto|Verrechnungskonto|Kreditkarte|Visa\s?Card)\b", re.I
)
_PENDING = {"vorgemerkt", "offen", "pending", "nichtgebucht"}


def _find_header(lines: list[str]) -> tuple[int, str] | None:
    """The header row and the delimiter: the first row with a date and an amount column."""
    dates = set(COLUMNS["date"])
    amounts = set(COLUMNS["amount"]) | set(COLUMNS["debit"])
    for i, line in enumerate(lines[:60]):
        for delim in (";", ",", "\t"):
            if delim not in line:
                continue
            names = {norm(c) for c in next(csv.reader([line], delimiter=delim, quotechar='"'), [])}
            if names & dates and names & amounts:
                return i, delim
    return None


_GROUPED_IBAN = re.compile(r"(?<![A-Z0-9])[A-Z]{2}\d{2}(?: ?[A-Z0-9]{4}){3,7}(?: ?[A-Z0-9]{1,3})?(?![A-Z0-9])")


def _valid_ibans(text: str) -> list[str]:
    """IBANs in a text, written in one piece or in groups of four."""
    found = [m.replace(" ", "") for m in _GROUPED_IBAN.findall(text.upper())]
    return [m for m in found if _valid_iban(m)]


def parse(raw: bytes, filename: str | None = None) -> dict:
    text = _decode(raw)
    lines = text.splitlines()
    found = _find_header(lines)
    if found is None:
        raise UserFacingError(
            "This doesn't look like a bank's CSV export. In your online banking, open the account's "
            "transactions and export them as CSV."
        )
    header_index, delim = found
    meta: dict[str, str] = {}
    preamble = []
    for line in lines[:header_index]:
        cells = [c.strip().strip('"').strip() for c in next(csv.reader([line], delimiter=delim, quotechar='"'), [])]
        cells = [c for c in cells if c] if cells and not cells[0] else cells
        preamble.append(" ".join(cells))
        if len(cells) >= 2 and cells[0]:
            meta[norm(cells[0])] = cells[1]

    reader = csv.reader(io.StringIO("\n".join(lines[header_index:])), delimiter=delim, quotechar='"')
    names = [norm(h) for h in next(reader)]

    def col(key: str, after: int | None = None) -> int | None:
        for name in COLUMNS[key]:
            hits = [i for i, h in enumerate(names) if h == name and (after is None or i > after)]
            if hits:
                return hits[0]
        return None

    i = {key: col(key) for key in COLUMNS}
    # ING has two currency columns, one after the balance and one after the amount.
    if i["amount"] is not None and col("currency", i["amount"]) is not None:
        i["currency"] = col("currency", i["amount"])
    if i["purpose"] is None and i["booking_text"] is not None and names[i["booking_text"]] == "buchungstext":
        # One text for everything (comdirect, Commerzbank): it is the purpose; the type is elsewhere.
        i["purpose"], i["booking_text"] = i["booking_text"], None
        for name in COLUMNS["booking_text"][1:]:
            if name in names:
                i["booking_text"] = names.index(name)
                break
    if i["date"] is None or (i["amount"] is None and i["debit"] is None):
        raise UserFacingError("The CSV file is missing the booking date or amount column.")

    rows = []
    own_ibans: list[str] = []
    own_names: list[str] = []
    footer_balance = None
    for cells in reader:
        if not cells or not any(c.strip() for c in cells):
            continue

        def get(key, cells=cells):
            k = i[key]
            return cells[k].strip() if k is not None and k < len(cells) and cells[k].strip() else None

        first = norm(cells[0])
        if first.startswith(("kontostand", "saldo", "neuerkontostand")):
            # Deutsche Bank and Postbank end with "Kontostand;<date>;;;1.234,56;EUR".
            for c in reversed(cells[1:]):
                try:
                    if re.search(r"\d", c) and not re.fullmatch(r"\d{1,2}\.\d{1,2}\.\d{2,4}", c.strip()):
                        footer_balance = parse_amount(c)
                        break
                except ValueError:
                    continue
            continue
        if norm(get("status") or "") in _PENDING:
            continue
        try:
            date = parse_date(get("date") or "")
            if i["amount"] is not None and get("amount"):
                amount = parse_amount(get("amount"))
            elif get("debit"):
                amount = -abs(parse_amount(get("debit")))
            elif get("credit"):
                amount = abs(parse_amount(get("credit")))
            else:
                continue
        except ValueError:
            continue
        if (get("sign") or "").upper() == "S":
            amount = -abs(amount)

        purpose = get("purpose")
        party = get("counterparty") or (get("payee") if amount < 0 else get("payer")) or get("payee") or get("payer")
        if purpose and not party:
            m = _PARTY_IN_TEXT.search(purpose)
            if m:
                party = m.group(1).strip()
                inner = _PURPOSE_IN_TEXT.search(purpose)
                purpose = inner.group(1).strip() if inner else purpose
        try:
            after = parse_amount(get("balance")) if get("balance") else None
        except ValueError:
            after = None
        try:
            value_date = parse_date(get("value_date")) if get("value_date") else date
        except ValueError:
            value_date = date
        party_iban = re.sub(r"\s+", "", get("counterparty_iban") or "").upper()
        if get("own_iban"):
            own_ibans.extend(_valid_ibans(get("own_iban")))
        if get("own_name"):
            own_names.append(get("own_name"))
        rows.append(
            {
                "date": date,
                "value_date": value_date,
                "amount": amount,
                "currency": get("currency") or "EUR",
                "counterparty": party,
                "counterparty_iban": party_iban if _valid_ibans(party_iban) else None,
                "purpose": purpose,
                "booking_text": get("booking_text"),
                "_after": after,
            }
        )

    pre = "\n".join(preamble)
    iban = re.sub(r"\s+", "", meta.get("iban", "")).upper() or None
    if not iban:
        found_ibans = _valid_ibans(pre) or own_ibans
        iban = found_ibans[0] if found_ibans else None
    if not iban and filename:
        found_ibans = _valid_ibans(filename)
        iban = found_ibans[0] if found_ibans else None
    balance = None
    for key, value in meta.items():
        if key.startswith(("saldo", "kontostand", "neuerkontostand", "aktuellerkontostand")):
            try:
                balance = parse_amount(value)
                break
            except ValueError:
                continue
    if balance is None:
        balance = footer_balance
    newest = _newest(rows)
    if balance is None and newest is not None:
        balance = newest["_after"]
    for r in rows:
        r.pop("_after", None)
    name = meta.get("kontoname") or (own_names[0] if own_names else None)
    if not name:
        m = _ACCOUNT_NAME.search(pre)
        name = m.group(1) if m else None
    holder = meta.get("kunde") or meta.get("kontoinhaber") or meta.get("inhaber")
    return {
        "iban": iban,
        "account_name": name,
        "holder": (holder or "").strip() or None,
        "balance": balance,
        "rows": rows,
    }


def _newest(rows: list[dict]) -> dict | None:
    """The latest booking that carries the balance after it.

    ING lists the newest booking first unless the export was sorted the other way; the
    file's own order says which, since several bookings can share a day.
    """
    known = [r for r in rows if r.get("_after") is not None]
    if not known:
        return None
    newest_first = known[0]["date"] >= known[-1]["date"]
    last_day = max(r["date"] for r in known)
    same_day = [r for r in known if r["date"] == last_day]
    return same_day[0] if newest_first else same_day[-1]


def parse_prices(raw: bytes) -> list[tuple[str, str, float]]:
    """Price history file: one row per day with date, ISIN and price.

    Accepts "date;isin;price" or "date,isin,price" with an optional header,
    German or English number formats.
    """
    text = _decode(raw)
    out = []
    delim = ";" if text.count(";") >= text.count(",") / 2 else ","
    for line in text.splitlines():
        cells = [c.strip().strip('"') for c in line.split(delim)]
        if len(cells) < 3:
            continue
        try:
            date = parse_date(cells[0])
        except ValueError:
            continue
        isin = cells[1].upper()
        if not re.fullmatch(r"[A-Z]{2}[A-Z0-9]{9}\d", isin):
            continue
        try:
            price = parse_amount(cells[2]) if delim == ";" else round(float(cells[2]), 4)
        except ValueError:
            continue
        out.append((isin, date, price))
    if not out:
        raise UserFacingError(
            "No prices found. Use one line per day: date;ISIN;price, for example 26.09.2026;IE00BK5BQT80;131,40"
        )
    return out
