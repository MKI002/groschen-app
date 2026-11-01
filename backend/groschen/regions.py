"""Countries Groschen knows: the money people there use and how they write dates.

The home country is picked once (first run or Settings). It sets the home currency, which
every total is shown in, and how a bank file's dates are read when the file itself can't
tell (03/04/2026 is 4 March in most of the world and 3 April in the US).

Names aren't kept here: the browser names countries and currencies in the user's language.
"""

# Country -> (currency, writes the month first in dates).
COUNTRIES: dict[str, tuple[str, bool]] = {
    "DE": ("EUR", False),
    "AT": ("EUR", False),
    "CH": ("CHF", False),
    "LI": ("CHF", False),
    "LU": ("EUR", False),
    "BE": ("EUR", False),
    "NL": ("EUR", False),
    "FR": ("EUR", False),
    "IT": ("EUR", False),
    "ES": ("EUR", False),
    "PT": ("EUR", False),
    "IE": ("EUR", False),
    "FI": ("EUR", False),
    "GR": ("EUR", False),
    "EE": ("EUR", False),
    "LV": ("EUR", False),
    "LT": ("EUR", False),
    "SK": ("EUR", False),
    "SI": ("EUR", False),
    "HR": ("EUR", False),
    "BG": ("EUR", False),
    "MT": ("EUR", False),
    "CY": ("EUR", False),
    "DK": ("DKK", False),
    "SE": ("SEK", False),
    "NO": ("NOK", False),
    "IS": ("ISK", False),
    "PL": ("PLN", False),
    "CZ": ("CZK", False),
    "HU": ("HUF", False),
    "RO": ("RON", False),
    "GB": ("GBP", False),
    "TR": ("TRY", False),
    "IL": ("ILS", False),
    "US": ("USD", True),
    "CA": ("CAD", False),
    "MX": ("MXN", False),
    "BR": ("BRL", False),
    "AU": ("AUD", False),
    "NZ": ("NZD", False),
    "JP": ("JPY", False),
    "KR": ("KRW", False),
    "CN": ("CNY", False),
    "HK": ("HKD", False),
    "SG": ("SGD", False),
    "MY": ("MYR", False),
    "TH": ("THB", False),
    "ID": ("IDR", False),
    "PH": ("PHP", True),
    "IN": ("INR", False),
    "ZA": ("ZAR", False),
}

# Every currency the European Central Bank publishes a daily rate for, plus the euro itself.
# Groschen converts between any two of them.
CURRENCIES = (
    "EUR",
    "USD",
    "GBP",
    "CHF",
    "JPY",
    "CAD",
    "AUD",
    "NZD",
    "SEK",
    "NOK",
    "DKK",
    "ISK",
    "PLN",
    "CZK",
    "HUF",
    "RON",
    "TRY",
    "ILS",
    "MXN",
    "BRL",
    "KRW",
    "CNY",
    "HKD",
    "SGD",
    "MYR",
    "THB",
    "IDR",
    "PHP",
    "INR",
    "ZAR",
)

# Symbols a bank file may put next to an amount instead of a code. "$" alone is the US dollar
# unless the home currency is another dollar.
SYMBOLS = {
    "R$": "BRL",
    "€": "EUR",
    "£": "GBP",
    "¥": "JPY",
    "₹": "INR",
    "₺": "TRY",
    "₪": "ILS",
    "₩": "KRW",
    "zł": "PLN",
    "Kč": "CZK",
}


def currency_of(country: str | None) -> str | None:
    entry = COUNTRIES.get((country or "").upper())
    return entry[0] if entry else None


def month_first(country: str | None) -> bool:
    entry = COUNTRIES.get((country or "").upper())
    return bool(entry and entry[1])


# Countries that write 1,234.56 (a decimal point). The others write 1.234,56 or 1 234,56.
DECIMAL_DOT = {
    "US",
    "GB",
    "IE",
    "MT",
    "CH",
    "LI",
    "CA",
    "MX",
    "AU",
    "NZ",
    "JP",
    "KR",
    "CN",
    "HK",
    "SG",
    "MY",
    "TH",
    "PH",
    "IN",
    "IL",
}


def decimal_dot(country: str | None) -> bool:
    return (country or "").upper() in DECIMAL_DOT
