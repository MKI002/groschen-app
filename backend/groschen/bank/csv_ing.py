"""Reader for the CSV export of ING Germany ("Umsatzanzeige").

The file starts with a few "key;value" lines (IBAN, account name, period,
balance), then a header row that begins with "Buchung", then one row per
transaction. Older and newer exports differ slightly (for example a
"Kategorie" or "Referenz" column), so columns are looked up by name.

Files whose "key;value" lines were cut off still work: the IBAN is also in
the file name ING gives the export (Umsatzanzeige_<IBAN>_<date>.csv), and
every row carries the balance after it, so the newest row says what is on
the account.
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
    t = (text or "").strip().replace("−", "-").replace(" ", "")
    if not t:
        return 0.0
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    return round(float(t), 2)


def parse_date(text: str) -> str:
    text = (text or "").strip()
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d.%m.%y"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue
    raise ValueError(f"not a date: {text!r}")


IBAN_RE = re.compile(r"(?<![A-Z0-9])([A-Z]{2}\d{2}[A-Z0-9]{12,30})(?![A-Z0-9])")


def _valid_iban(iban: str) -> bool:
    digits = "".join(str(int(c, 36)) for c in iban[4:] + iban[:4])
    return int(digits) % 97 == 1


def parse(raw: bytes, filename: str | None = None) -> dict:
    text = _decode(raw)
    lines = text.splitlines()
    meta: dict[str, str] = {}
    header_index = None
    for i, line in enumerate(lines):
        cells = [c.strip().strip('"') for c in line.split(";")]
        if cells and cells[0] == "Buchung":
            header_index = i
            break
        if len(cells) >= 2 and cells[0]:
            meta[cells[0]] = cells[1]
    if header_index is None:
        raise UserFacingError(
            "This doesn't look like an ING CSV export. In ING banking, open the account, choose Umsätze and export as CSV."
        )

    reader = csv.reader(io.StringIO("\n".join(lines[header_index:])), delimiter=";", quotechar='"')
    header = next(reader)
    names = [h.strip() for h in header]

    def col(name: str, occurrence: int = 0) -> int | None:
        found = [i for i, h in enumerate(names) if h == name]
        return found[occurrence] if len(found) > occurrence else None

    i_date = col("Buchung")
    i_value = col("Wertstellungsdatum") if col("Wertstellungsdatum") is not None else col("Valuta")
    i_party = col("Auftraggeber/Empfänger")
    i_text = col("Buchungstext")
    i_purpose = col("Verwendungszweck")
    i_amount = col("Betrag")
    i_balance = col("Saldo")
    i_currency = None
    if i_amount is not None:
        after = [i for i, h in enumerate(names) if h == "Währung" and i > i_amount]
        i_currency = after[0] if after else None
    if i_date is None or i_amount is None:
        raise UserFacingError("The CSV file is missing the Buchung or Betrag column.")

    rows = []
    for cells in reader:
        if not cells or not any(c.strip() for c in cells):
            continue
        try:
            date = parse_date(cells[i_date])
            amount = parse_amount(cells[i_amount])
        except (ValueError, IndexError):
            continue

        def get(i, cells=cells):
            return cells[i].strip() if i is not None and i < len(cells) and cells[i].strip() else None

        after = None
        if get(i_balance):
            try:
                after = parse_amount(cells[i_balance])
            except ValueError:
                after = None
        rows.append(
            {
                "date": date,
                "value_date": parse_date(cells[i_value]) if get(i_value) else date,
                "amount": amount,
                "currency": get(i_currency) or "EUR",
                "counterparty": get(i_party),
                "counterparty_iban": None,
                "purpose": get(i_purpose),
                "booking_text": get(i_text),
                "_after": after,
            }
        )

    iban = re.sub(r"\s+", "", meta.get("IBAN", "")).upper() or None
    if not iban and filename:
        found = [m for m in IBAN_RE.findall(filename.upper()) if _valid_iban(m)]
        iban = found[0] if found else None
    balance = None
    if meta.get("Saldo"):
        try:
            balance = parse_amount(meta["Saldo"])
        except ValueError:
            balance = None
    newest = _newest(rows)
    if balance is None and newest is not None:
        balance = newest["_after"]
    for r in rows:
        r.pop("_after", None)
    return {
        "iban": iban,
        "account_name": meta.get("Kontoname"),
        "holder": (meta.get("Kunde") or "").strip() or None,
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
