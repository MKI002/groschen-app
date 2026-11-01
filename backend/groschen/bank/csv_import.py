"""Reader for the CSV exports of banks, in Germany and anywhere else.

Every bank lays its export out differently, so columns are found by their names, and
each name a bank uses is listed below: ING ("Umsatzanzeige"), Sparkasse (CSV-CAMT and
CSV-MT940), Volksbanken and Raiffeisenbanken, DKB (old and new), comdirect, Deutsche
Bank, Postbank, Commerzbank, Consorsbank, N26, and the English, French, Dutch, Spanish and
Italian words other banks use (Chase, Bank of America, Revolut, Wise, Monzo, ING in the
Netherlands, ...). Semicolons, commas or tabs, 1.234,56 or 1,234.56, day or month first
in dates, one amount column or a debit and a credit column: all of it is found from the
file itself. The currency comes from a currency column, the amount column's name
("Amount (USD)") or the amounts themselves ("$12.50"), else it is the account's own.

Most German files start with a few "key;value" lines (IBAN, account name, balance) before
the header row. Files without them still work: the IBAN is in the file name some banks give
the export (Umsatzanzeige_<IBAN>_<date>.csv), and where every row carries the balance
after it, the newest row says what is on the account.

A file Groschen can't read alone (no header, or names it doesn't know) raises NeedsMapping
with its first rows: the web page asks once which column is which, and the answer is kept
for the next file with the same header.
"""

import csv
import hashlib
import io
import re
from collections import Counter
from datetime import datetime

from .. import regions
from ..jobs import UserFacingError

NOT_A_BANK_FILE = (
    "This doesn't look like a bank's CSV export. In your online banking, open the account's "
    "transactions and export them as CSV."
)


class NeedsMapping(UserFacingError):
    """The file has rows, but which column is the date and which the amount isn't clear."""

    def __init__(self, preview: dict):
        super().__init__(NOT_A_BANK_FILE)
        self.preview = preview


def _decode(raw: bytes) -> str:
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1", errors="replace")


# Everything around the number: currency codes and signs (EUR, $, kr, R$, zł, ...).
_CURRENCY_TEXT = re.compile(r"[^\d.,'’+\-()]")


def parse_amount(text: str, decimal: str | None = None) -> float:
    """1.234,56 or 1,234.56 or 1'234.56, with or without a currency, a trailing minus or (brackets).

    ``decimal`` is the file's decimal mark when known (see _decimal_mark); "2,500" then can't be misread.
    """
    t = (text or "").strip().replace("−", "-").replace("\u00a0", "").replace("\u202f", "").replace(" ", "")
    if t and not re.search(r"\d", t):
        if re.search(r"[A-Za-z]{4}", t):  # a word, not a currency: not an amount
            raise ValueError(f"not an amount: {text!r}")
        return 0.0
    t = _CURRENCY_TEXT.sub("", t)
    negative = t.startswith("(") and t.endswith(")")
    t = t.strip("()").replace("+", "").replace("'", "").replace("’", "")
    if not t:
        return 0.0
    if t.endswith("-"):
        t = "-" + t[:-1]
    if decimal == ",":
        t = t.replace(".", "").replace(",", ".")
    elif decimal == ".":
        t = t.replace(",", "")
    elif "," in t and "." in t:
        t = t.replace(".", "").replace(",", ".") if t.rfind(",") > t.rfind(".") else t.replace(",", "")
    elif "," in t or re.fullmatch(r"-?\d{1,3}(\.\d{3})+", t):
        # "2.500" in a German file is two and a half thousand.
        t = t.replace(".", "").replace(",", ".")
    value = round(float(t), 2)
    return -abs(value) if negative else value


def _decimal_mark(cells: list[str]) -> str | None:
    """ "," or "." when the file's amounts say so: 12,50 and 1.234,56 or 12.50 and 1,234.56."""
    comma = dot = 0
    for c in cells:
        t = _CURRENCY_TEXT.sub("", (c or "").replace(" ", "").replace("\u00a0", "")).strip("()+-")
        if re.search(r"\d,\d{1,2}$", t):
            comma += 1
        elif re.search(r"\d\.\d{1,2}$", t):
            dot += 1
    if comma > dot:
        return ","
    if dot > comma:
        return "."
    return None


_ISO = re.compile(r"^(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})")
_NUMERIC = re.compile(r"^(\d{1,2})([./-])(\d{1,2})\2(\d{2}|\d{4})$")
_WORDY = ("%d %b %Y", "%d %B %Y", "%d %b %y", "%d-%b-%Y", "%d-%b-%y", "%b %d, %Y", "%B %d, %Y", "%b %d %Y")


def parse_date(text: str, month_first: bool = False) -> str:
    """A booking date. ``month_first`` reads 03/04/2026 as 4 March (the US way), not 3 April."""
    text = (text or "").strip().strip('"')
    if re.fullmatch(r"\d{8}", text):  # 20261030 (ING in the Netherlands)
        return datetime.strptime(text, "%Y%m%d").date().isoformat()
    m = _ISO.match(text)
    if m:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3))).date().isoformat()
    m = _NUMERIC.match(text.split(" ")[0])
    if m:
        a, sep, b, year = int(m.group(1)), m.group(2), int(m.group(3)), int(m.group(4))
        if year < 100:
            year += 2000
        # Dots are always day first (31.12.2026); slashes and dashes follow the file.
        if month_first and sep != "." and a <= 12:
            a, b = b, a
        if b > 12 and a <= 12:
            a, b = b, a
        return datetime(year, b, a).date().isoformat()
    for fmt in _WORDY:
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue
    raise ValueError(f"not a date: {text!r}")


def month_first_in(values: list[str], default: bool = False) -> bool:
    """Whether a file writes the month first: 12/31/2026 says so, 31/12/2026 says not; else the country's way."""
    day_first = month = False
    for v in values:
        m = _NUMERIC.match((v or "").strip().split(" ")[0])
        if not m or m.group(2) == ".":
            continue
        a, b = int(m.group(1)), int(m.group(3))
        day_first |= a > 12
        month |= b > 12
    if day_first != month:
        return month
    return default


def _valid_iban(iban: str) -> bool:
    digits = "".join(str(int(c, 36)) for c in iban[4:] + iban[:4])
    return int(digits) % 97 == 1


def norm(name: str) -> str:
    """A column name without case, umlauts, spaces or punctuation: "Betrag (€)" is "betrag"."""
    t = (name or "").strip().strip('"').lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        t = t.replace(a, b)
    return re.sub(r"[^a-z0-9]", "", t)


# The names banks give each column, most specific first. German, then English, French, Dutch,
# Spanish and Italian. A name may carry a currency ("Betrag (EUR)", "Amount (USD)").
COLUMNS = {
    "date": [
        "buchung",
        "buchungstag",
        "buchungsdatum",
        "bookingdate",
        "datum",
        "transactiondate",
        "completeddate",
        "date",
        "postingdate",
        "posteddate",
        "postdate",
        "starteddate",
        "dateoperation",
        "datedoperation",
        "boekingsdatum",
        "transactiedatum",
        "fechaoperacion",
        "fecha",
        "dataoperazione",
        "data",
        "bokforingsdag",
        "bokforingsdatum",
    ],
    "value_date": [
        "wertstellungsdatum",
        "valutadatum",
        "valuta",
        "wertstellung",
        "wertstellungvaluta",
        "wert",
        "valuedate",
        "datevaleur",
        "rentedatum",
        "fechavalor",
        "datavaluta",
    ],
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
        "transactionamount",
        "montant",
        "bedrag",
        "importe",
        "importo",
        "belopp",
        "beloeb",
        "kwota",
    ],
    "debit": [
        "soll",
        "solleur",
        "ausgang",
        "belastung",
        "debit",
        "debitamount",
        "moneyout",
        "paidout",
        "withdrawals",
        "withdrawal",
        "outflow",
        "cargo",
        "addebiti",
    ],
    "credit": [
        "haben",
        "habeneur",
        "eingang",
        "gutschrift",
        "credit",
        "creditamount",
        "moneyin",
        "paidin",
        "deposits",
        "deposit",
        "inflow",
        "abono",
        "accrediti",
    ],
    "sign": ["sollhaben", "sh", "afbij", "debitcredit", "creditdebitindicator", "drcr"],
    "currency": ["waehrung", "wahrung", "currency", "currencycode", "devise", "moneda"],
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
        "merchant",
        "merchantname",
        "counterparty",
        "counterpartyname",
        "naamomschrijving",
        "naam",
        "beneficiaire",
        "beneficiary",
        "recipient",
    ],
    "payer": ["zahlungspflichtiger", "zahlungspflichtigein", "auftraggeber", "payer", "sender"],
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
        "tegenrekening",
        "counterpartyiban",
    ],
    "purpose": [
        "verwendungszweck",
        "paymentreference",
        "buchungsdetails",
        "beschreibung",
        "description",
        "reference",
        "memo",
        "libelle",
        "libelleoperation",
        "mededelingen",
        "omschrijving",
        "concepto",
        "descripcion",
        "descrizione",
        "causale",
        "notesandtags",
        "narrative",
        "transactiondetails",
    ],
    "booking_text": [
        "buchungstext",
        "umsatzart",
        "umsatztyp",
        "vorgang",
        "buchungsart",
        "transactiontype",
        "transaktionstyp",
        "type",
        "mutatiesoort",
        "typeoperation",
    ],
    "balance": [
        "saldonachbuchung",
        "saldo",
        "saldoeur",
        "kontostand",
        "balance",
        "runningbalance",
        "runningbal",
        "balanceafter",
        "solde",
    ],
    "own_iban": ["ibanauftragskonto", "auftragskonto", "ibankontoinhaber"],
    "own_name": ["bezeichnungauftragskonto", "accountname"],
    "status": ["status", "state"],
}
GERMAN_DATES = {"buchung", "buchungstag", "buchungsdatum", "datum"}
# Columns the web page lets the user pick when a file can't be read alone.
MAPPABLE = ("date", "amount", "debit", "credit", "counterparty", "purpose", "currency", "balance")

# comdirect and Commerzbank put everything into one text: "Empfänger: … Kto/IBAN: … Buchungstext: …".
_PARTY_IN_TEXT = re.compile(
    r"(?:Auftraggeber|Empf(?:ä|ae)nger)\s*:\s*(.+?)(?=\s+(?:Kto/IBAN|IBAN|BLZ/BIC|Buchungstext)\s*:|$)", re.I
)
_PURPOSE_IN_TEXT = re.compile(r"Buchungstext\s*:\s*(.+?)(?=\s+Ref\.\s|$)", re.I)
_ACCOUNT_NAME = re.compile(
    r"\b(Girokonto|Extra-Konto|Tagesgeld\w*|Sparkonto|Gemeinschaftskonto|Verrechnungskonto|Kreditkarte|Visa\s?Card)\b", re.I
)
_PENDING = {"vorgemerkt", "offen", "pending", "nichtgebucht", "reverted", "declined", "failed", "cancelled", "canceled"}
# "S" (Soll), "Af" (Dutch), "D"/"DR"/"Debit": money going out.
_DEBIT_SIGNS = {"s", "af", "d", "dr", "debit", "dbit"}


def _bare(name: str) -> tuple[str, str | None]:
    """A column name without the currency it carries: "amountusd" is ("amount", "USD")."""
    code = name[-3:].upper()
    if len(name) > 4 and code in regions.CURRENCIES:
        return name[:-3], code
    return name, None


def _match(names: list[str], key: str, after: int | None = None) -> tuple[int, str | None] | None:
    """The column for ``key``, by its most specific name first: (index, currency in its name)."""
    bare = [_bare(n) for n in names]
    for wanted in COLUMNS[key]:
        for i, h in enumerate(names):
            if h == wanted and (after is None or i > after):
                return i, None
        for i, (h, code) in enumerate(bare):
            if code and h == wanted and (after is None or i > after):
                return i, code
    return None


def _cells(line: str, delim: str) -> list[str]:
    return next(csv.reader([line], delimiter=delim, quotechar='"'), [])


def _find_header(lines: list[str]) -> tuple[int, str] | None:
    """The header row and the delimiter: the first row with a date and an amount column."""
    for i, line in enumerate(lines[:60]):
        for delim in (";", ",", "\t"):
            if delim not in line:
                continue
            names = [norm(c) for c in _cells(line, delim)]
            if _match(names, "date") and (_match(names, "amount") or _match(names, "debit")):
                return i, delim
    return None


_GROUPED_IBAN = re.compile(r"(?<![A-Z0-9])[A-Z]{2}\d{2}(?: ?[A-Z0-9]{4}){3,7}(?: ?[A-Z0-9]{1,3})?(?![A-Z0-9])")


def _valid_ibans(text: str) -> list[str]:
    """IBANs in a text, written in one piece or in groups of four."""
    found = [m.replace(" ", "") for m in _GROUPED_IBAN.findall(text.upper())]
    return [m for m in found if _valid_iban(m)]


def _guess_layout(lines: list[str]) -> tuple[str, int] | None:
    """For a file without known column names: the delimiter, and the row naming the columns (-1 for none).

    Rows start after that one; rows of another width (a title, a total) are skipped later.
    """
    body = [(n, line) for n, line in enumerate(lines[:40]) if line.strip()]
    best = None
    for delim in (";", ",", "\t", "|"):
        counts = Counter(len(_cells(line, delim)) for _, line in body)
        width, times = counts.most_common(1)[0] if counts else (0, 0)
        if width >= 2 and (best is None or times > best[1] or (times == best[1] and width > best[2])):
            best = (delim, times, width)
    if not best or best[1] < max(2, len(body) // 2):
        return None
    delim, _, width = best
    n, line = next((n, line) for n, line in body if len(_cells(line, delim)) == width)
    # A first row without digits names the columns.
    if not any(re.search(r"\d", c) for c in _cells(line, delim)):
        return delim, n
    return delim, n - 1


def signature(header: list[str] | None, delim: str, width: int) -> str:
    """What makes a bank's file recognisable: its column names, or for files without, the delimiter and width."""
    key = "|".join(norm(h) for h in header) if header else f"{width} columns"
    return hashlib.sha256(f"{delim}|{key}".encode()).hexdigest()[:32]


def preview(raw: bytes) -> dict:
    """The first rows of a file Groschen can't read alone, for the web page's "which column is which" step."""
    lines = _decode(raw).splitlines()
    layout = _guess_layout(lines)
    if not layout:
        raise UserFacingError(NOT_A_BANK_FILE)
    delim, header_index = layout
    body = [_cells(line, delim) for line in lines[header_index + 1 :] if line.strip()]
    width = Counter(len(r) for r in body).most_common(1)[0][0]
    header = _cells(lines[header_index], delim) if header_index >= 0 else None
    return {
        "delimiter": delim,
        "header_row": header_index,
        "columns": [c.strip() for c in header] if header else [],
        "sample": [[c.strip() for c in r] for r in body if len(r) == width][:5],
        "width": width,
        "signature": signature(header, delim, width),
    }


DOLLARS = {"USD", "CAD", "AUD", "NZD", "SGD", "HKD", "MXN"}


def _currency_of(text: str | None, default: str) -> str | None:
    """A currency named in a cell: a code (USD), or a sign ($, €, £, ...)."""
    t = (text or "").strip()
    m = re.search(r"\b([A-Z]{3})\b", t.upper())
    if m and m.group(1) in regions.CURRENCIES:
        return m.group(1)
    for sign, code in regions.SYMBOLS.items():
        if sign in t:
            return code
    if "$" in t:
        # "$" alone: the home dollar when the home currency is one, else the US dollar.
        return default if default in DOLLARS else "USD"
    return None


def parse(
    raw: bytes,
    filename: str | None = None,
    *,
    default_currency: str = "EUR",
    month_first: bool = False,
    mapping: dict | None = None,
) -> dict:
    """Read a bank's CSV export.

    ``default_currency`` is the account's (or the home) currency for files that don't name one;
    ``month_first`` how ambiguous dates are read when the file itself doesn't tell (the home country's way);
    ``mapping`` the columns the user picked for this kind of file (see NeedsMapping).
    """
    text = _decode(raw)
    lines = text.splitlines()
    header_currency = None
    german = False
    if mapping:
        delim = mapping.get("delimiter") or ","
        header_index = int(mapping.get("header_row", -1))
        names = [norm(c) for c in _cells(lines[header_index], delim)] if header_index >= 0 else []
        i = {key: None for key in COLUMNS}
        for key in MAPPABLE:
            v = mapping.get(key)
            if isinstance(v, int) and v >= 0:
                i[key] = v
    else:
        found = _find_header(lines)
        if found is None:
            raise NeedsMapping(preview(raw))
        header_index, delim = found
    meta: dict[str, str] = {}
    preamble = []
    for line in lines[: max(header_index, 0)]:
        cells = [c.strip().strip('"').strip() for c in _cells(line, delim)]
        cells = [c for c in cells if c] if cells and not cells[0] else cells
        preamble.append(" ".join(cells))
        if len(cells) >= 2 and cells[0]:
            meta[norm(cells[0])] = cells[1]

    reader = csv.reader(io.StringIO("\n".join(lines[header_index + 1 :])), delimiter=delim, quotechar='"')

    if not mapping:
        names = [norm(h) for h in _cells(lines[header_index], delim)]

        def col(key: str, after: int | None = None) -> int | None:
            hit = _match(names, key, after)
            return hit[0] if hit else None

        i = {key: col(key) for key in COLUMNS}
        german = names[i["date"]] in GERMAN_DATES if i["date"] is not None else False
        for key in ("amount", "debit", "credit", "balance"):
            hit = _match(names, key)
            if hit and hit[1] and key in ("amount", "debit", "credit"):
                header_currency = hit[1]
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
            raise NeedsMapping(preview(raw))
    elif i["date"] is None or (i["amount"] is None and i["debit"] is None and i["credit"] is None):
        raise UserFacingError("Pick the column with the date and the one with the amount.")
    # No name column at all (Chase, Bank of America, most banks outside Germany): the description is the payee.
    party_from_text = i["counterparty"] is None and i["payer"] is None and i["payee"] is None

    all_rows = [cells for cells in reader if cells and any(c.strip() for c in cells)]

    def cell(cells: list[str], key: str) -> str | None:
        k = i[key]
        return cells[k].strip() if k is not None and k < len(cells) and cells[k].strip() else None

    # Dollars from a US bank write the month first, wherever the user lives; the dates themselves decide when they can.
    named = Counter(_currency_of(cell(c, "currency"), default_currency) for c in all_rows if cell(c, "currency"))
    file_currency = (
        header_currency or (named.most_common(1)[0][0] if named else None) or (mapping or {}).get("currency_code")
    )
    month_first = month_first_in([cell(c, "date") or "" for c in all_rows], month_first or file_currency == "USD")
    decimal = _decimal_mark([cell(c, k) or "" for c in all_rows for k in ("amount", "debit", "credit", "balance")])

    rows = []
    own_ibans: list[str] = []
    own_names: list[str] = []
    footer_balance = None
    for cells in all_rows:

        def get(key, cells=cells):
            return cell(cells, key)

        first = norm(cells[0])
        if first.startswith(("kontostand", "saldo", "neuerkontostand")):
            # Deutsche Bank and Postbank end with "Kontostand;<date>;;;1.234,56;EUR".
            for c in reversed(cells[1:]):
                try:
                    if re.search(r"\d", c) and not re.fullmatch(r"\d{1,2}\.\d{1,2}\.\d{2,4}", c.strip()):
                        footer_balance = parse_amount(c, decimal)
                        break
                except ValueError:
                    continue
            continue
        if norm(get("status") or "") in _PENDING:
            continue
        try:
            date = parse_date(get("date") or "", month_first)
            if i["amount"] is not None and get("amount"):
                amount = parse_amount(get("amount"), decimal)
            elif get("debit") and parse_amount(get("debit"), decimal):
                amount = -abs(parse_amount(get("debit"), decimal))
            elif get("credit"):
                amount = abs(parse_amount(get("credit"), decimal))
            else:
                continue
        except ValueError:
            continue
        if norm(get("sign") or "") in _DEBIT_SIGNS:
            amount = -abs(amount)

        purpose = get("purpose")
        party = get("counterparty") or (get("payee") if amount < 0 else get("payer")) or get("payee") or get("payer")
        if purpose and not party:
            m = _PARTY_IN_TEXT.search(purpose)
            if m:
                party = m.group(1).strip()
                inner = _PURPOSE_IN_TEXT.search(purpose)
                purpose = inner.group(1).strip() if inner else purpose
            elif party_from_text:
                party = " ".join(purpose.split())[:80]
        try:
            after = parse_amount(get("balance"), decimal) if get("balance") else None
        except ValueError:
            after = None
        try:
            value_date = parse_date(get("value_date"), month_first) if get("value_date") else date
        except ValueError:
            value_date = date
        party_iban = re.sub(r"\s+", "", get("counterparty_iban") or "").upper()
        if get("own_iban"):
            own_ibans.extend(_valid_ibans(get("own_iban")))
        if get("own_name"):
            own_names.append(get("own_name"))
        currency = (
            _currency_of(get("currency"), default_currency)
            or header_currency
            or _currency_of(get("amount") or get("debit") or get("credit"), default_currency)
            or (mapping or {}).get("currency_code")
            or default_currency
        )
        rows.append(
            {
                "date": date,
                "value_date": value_date,
                "amount": amount,
                "currency": currency,
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
    currencies = Counter(r["currency"] for r in rows)
    return {
        "iban": iban,
        "account_name": name,
        "holder": (holder or "").strip() or None,
        "balance": balance,
        "currency": currencies.most_common(1)[0][0] if currencies else default_currency,
        # A German bank's export: one without an IBAN still belongs to the user's only account of its kind.
        "german": german,
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
