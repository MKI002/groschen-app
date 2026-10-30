"""Server messages in the language the web page shows.

The code writes every message in English. The web page sends its language with
each request (header ``X-Groschen-Lang``), and messages are translated on the
way out. Stored English texts (a sync error saved for later, a job step) are
translated when they are shown, so switching the language also switches them.

To add a language, add it to ``LANGS`` and give it a catalogue like ``DE``.
"""

import re
from contextvars import ContextVar

LANGS = ("de", "en")
DEFAULT = "en"

_current: ContextVar[str | None] = ContextVar("groschen_lang", default=None)


def use(lang: str | None):
    """Set the language for the current request. Returns a token for ``reset``."""
    return _current.set(lang if lang in LANGS else None)


def reset(token) -> None:
    _current.reset(token)


def current() -> str:
    return _current.get() or DEFAULT


def pick(header: str | None) -> str | None:
    """The language asked for by a request header or query value, if Groschen has it."""
    if not header:
        return None
    short = header.strip()[:2].lower()
    return short if short in LANGS else None


# English template -> German template. Placeholders in braces must match.
DE = {
    # login and account
    "Please log in.": "Bitte melde dich an.",
    "An account already exists. Please log in.": "Es gibt schon ein Konto. Bitte melde dich an.",
    "Too many failed logins. Try again in {minutes} minutes.": (
        "Zu viele fehlgeschlagene Anmeldungen. Versuch es in {minutes} Minuten noch einmal."
    ),
    "Password login is turned off. Log in with a passkey.": (
        "Die Anmeldung mit Passwort ist ausgeschaltet. Melde dich mit einem Passkey an."
    ),
    "Passkeys only work when Groschen is opened over HTTPS with a name, not an IP address.": (
        "Passkeys funktionieren nur, wenn Groschen über HTTPS mit einem Namen geöffnet wird, nicht über eine IP-Adresse."
    ),
    "That passkey didn't work. Try again or use your password.": (
        "Dieser Passkey hat nicht geklappt. Versuch es noch einmal oder nimm dein Passwort."
    ),
    "The passkey couldn't be saved. Please try again.": (
        "Der Passkey konnte nicht gespeichert werden. Bitte versuch es noch einmal."
    ),
    "Add a passkey before turning off the password login.": (
        "Leg zuerst einen Passkey an, bevor du die Anmeldung mit Passwort ausschaltest."
    ),
    "Wrong username or password.": "Benutzername oder Passwort falsch.",
    "The current password isn't right.": "Das aktuelle Passwort stimmt nicht.",
    "Missing request header.": "Anfrage-Header fehlt.",
    "Not found.": "Nicht gefunden.",
    # lookups
    "Unknown job.": "Unbekannter Vorgang.",
    "Unknown connection.": "Unbekannte Verbindung.",
    "Unknown transaction.": "Unbekannter Umsatz.",
    "The month must look like 2026-09.": "Der Monat muss so aussehen: 2026-09.",
    "Unknown group.": "Unbekannte Gruppe.",
    "Unknown backup.": "Unbekannte Sicherung.",
    "This backup is damaged.": "Diese Sicherung ist beschädigt.",
    "This file is not a Groschen backup.": "Diese Datei ist keine Groschen-Sicherung.",
    "This backup is from a newer Groschen version.": "Diese Sicherung stammt aus einer neueren Groschen-Version.",
    "A bank sync is running. Try again when it has finished.": "Gerade läuft ein Abgleich. Versuch es danach noch mal.",
    "Unknown rule type.": "Unbekannte Regelart.",
    "Unknown category.": "Unbekannte Kategorie.",
    "This transaction has no merchant to remember.": "Dieser Umsatz hat keinen Händler, den Groschen sich merken könnte.",
    "Unknown flow.": "Unbekannte Richtung.",
    "Unknown sort order.": "Unbekannte Sortierung.",
    "Unknown category filter.": "Unbekannter Kategoriefilter.",
    "Nothing found for this category or payee.": "Für diese Kategorie oder diesen Empfänger wurde nichts gefunden.",
    "{group} already has a category called {name}.": "{group} hat schon eine Kategorie namens {name}.",
    "Kind must be expense, income or transfer.": "Die Art muss Ausgabe, Einnahme oder Umbuchung sein.",
    "Only accounts entered by hand can be changed here.": "Hier lassen sich nur von Hand angelegte Konten ändern.",
    "Bank accounts can be hidden, not deleted.": "Bankkonten lassen sich ausblenden, aber nicht löschen.",
    "That file is larger than 20 MB.": "Die Datei ist größer als 20 MB.",
    # bank and imports
    "That bank connection no longer exists.": "Diese Bankverbindung gibt es nicht mehr.",
    "This doesn't look like an ING CSV export. In ING banking, open the account, choose Umsätze and export as CSV.": (
        "Das sieht nicht nach einem ING-CSV-Export aus. "
        "Öffne im ING-Banking das Konto, wähle Umsätze und exportiere als CSV."
    ),
    "The CSV file is missing the Buchung or Betrag column.": "In der CSV-Datei fehlt die Spalte Buchung oder Betrag.",
    "This bank isn't supported yet. For now Groschen connects to ING.": (
        "Diese Bank wird noch nicht unterstützt. Im Moment verbindet sich Groschen mit der ING."
    ),
    "ING didn't accept the access number or PIN. Check both and try again.": (
        "Die ING hat Zugangsnummer oder PIN nicht akzeptiert. Prüf beides und versuch es noch einmal."
    ),
    "Groschen couldn't reach ING. Check that the server has internet access and try again.": (
        "Groschen hat die ING nicht erreicht. Prüf, ob der Server Internet hat, und versuch es noch einmal."
    ),
    "ING returned an error: {text}": "Die ING hat einen Fehler gemeldet: {text}",
    "A FinTS product ID is needed. You get one free from the Deutsche Kreditwirtschaft.": (
        "Es wird eine FinTS-Produkt-ID gebraucht. Du bekommst sie kostenlos von der Deutschen Kreditwirtschaft."
    ),
    "The approval in your banking app timed out. Try again when you have your phone.": (
        "Die Bestätigung in deiner Banking-App ist abgelaufen. Versuch es noch einmal, wenn du dein Handy zur Hand hast."
    ),
    "Please approve the request in your ING app.": "Bitte bestätige die Anfrage in deiner ING-App.",
    "Something went wrong: {text}": "Etwas ist schiefgelaufen: {text}",
    "Online ETF prices are turned off in Settings.": "Online-ETF-Kurse sind in den Einstellungen ausgeschaltet.",
    "ETF prices": "ETF-Kurse",
    "Loading prices for {isin}": "Lade Kurse für {isin}",
    "No ETFs yet": "Noch keine ETFs",
    "ETF not found.": "ETF nicht gefunden.",
    # job steps
    "Connecting to {bank}": "Verbinde mit {bank}",
    "Reading your accounts": "Lese deine Konten",
    "Connecting to the bank": "Verbinde mit der Bank",
    "Fetching new transactions": "Hole neue Umsätze",
    "Categorizing": "Kategorisiere",
    "Categorizing {n} transactions": "Kategorisiere {n} Umsätze",
    "Categorizing your transactions": "Kategorisiere deine Umsätze",
    "Finding subscriptions and recurring payments": "Suche Abos und wiederkehrende Zahlungen",
    # connection log
    "{bank} connection test": "{bank} Verbindungstest",
    "{bank} sync": "{bank} Abruf",
    # transactions export
    "Date": "Datum",
    "Account": "Konto",
    "Amount": "Betrag",
    "Currency": "Währung",
    "Counterparty": "Empfänger/Auftraggeber",
    "Purpose": "Verwendungszweck",
    "Booking text": "Buchungstext",
    "Group": "Gruppe",
    "Category": "Kategorie",
    "Note": "Notiz",
    # dashboard labels
    "Entered by hand": "Von Hand eingetragen",
    "{bank} · synced": "{bank} · abgerufen",
    "CSV import": "CSV-Import",
    "ING purchase prices": "ING-Kaufkursen",
    "payments into your depot": "Einzahlungen ins Depot",
    "Last 12 months": "Letzte 12 Monate",
    "Last 30 days": "Letzte 30 Tage",
    "All time": "Gesamter Zeitraum",
    "Uncategorized": "Ohne Kategorie",
    "Spelling-based matcher (built-in model not found)": ("Abgleich nach Schreibweise (eingebautes Modell nicht gefunden)"),
    "Built-in model (multilingual MiniLM, runs on the CPU)": (
        "Eingebautes Modell (mehrsprachiges MiniLM, läuft auf dem Prozessor)"
    ),
}

CATALOGUES = {"de": DE}

MONTHS = {
    "en": "January February March April May June July August September October November December".split(),
    "de": "Januar Februar März April Mai Juni Juli August September Oktober November Dezember".split(),
}


def month_name(month: int, short: bool = False) -> str:
    name = MONTHS[current()][month - 1]
    return name[:3] if short else name


def t(template: str, **values) -> str:
    """Translate an English template, then fill in the values."""
    text = CATALOGUES.get(current(), {}).get(template, template)
    return text.format(**values) if values else text


_patterns: dict[str, list[tuple[re.Pattern, str]]] = {}


def _compiled(lang: str) -> list[tuple[re.Pattern, str]]:
    if lang not in _patterns:
        out = []
        for en, target in CATALOGUES.get(lang, {}).items():
            if "{" not in en:
                continue
            regex = re.escape(en)
            regex = re.sub(r"\\\{(\w+)\\\}", lambda m: f"(?P<{m.group(1)}>.+?)", regex)
            out.append((re.compile(f"^{regex}$", re.S), target))
        _patterns[lang] = out
    return _patterns[lang]


def tr(text: str | None) -> str | None:
    """Translate a finished English message, including ones with values already filled in."""
    if not text:
        return text
    catalogue = CATALOGUES.get(current())
    if not catalogue:
        return text
    if text in catalogue:
        return catalogue[text]
    for pattern, target in _compiled(current()):
        m = pattern.match(text)
        if m:
            return target.format(**m.groupdict())
    return text


# Built-in category and group names are stored in English (the categorizer looks
# them up by name) and shown translated, like in the web page.
CATEGORY_NAMES = {
    "de": {
        "Income": "Einnahmen",
        "Salary": "Gehalt",
        "Interest & dividends": "Zinsen & Dividenden",
        "Other income": "Sonstige Einnahmen",
        "Housing": "Wohnen",
        "Rent": "Miete",
        "Energy": "Energie",
        "Internet & phone": "Internet & Telefon",
        "Broadcast fee": "Rundfunkbeitrag",
        "Home & furniture": "Haushalt & Möbel",
        "Food & Dining": "Essen & Trinken",
        "Groceries": "Lebensmittel",
        "Restaurants & cafés": "Restaurants & Cafés",
        "Food delivery": "Lieferdienste",
        "Transport": "Mobilität",
        "Fuel": "Tanken",
        "Public transport": "ÖPNV & Bahn",
        "Car costs": "Autokosten",
        "Parking": "Parken",
        "Taxi & rides": "Taxi & Fahrdienste",
        "Shopping": "Einkaufen",
        "Online shopping": "Onlineshopping",
        "Clothing": "Kleidung",
        "Electronics": "Elektronik",
        "Drugstore": "Drogerie",
        "Insurance": "Versicherungen",
        "Subscriptions": "Abos",
        "Streaming": "Streaming",
        "Software & cloud": "Software & Cloud",
        "Fitness": "Fitness",
        "Health": "Gesundheit",
        "Pharmacy": "Apotheke",
        "Doctor & health": "Arzt & Gesundheit",
        "Leisure & Travel": "Freizeit & Reisen",
        "Travel": "Reisen",
        "Hobbies": "Hobbys",
        "Entertainment": "Unterhaltung",
        "Gaming": "Gaming",
        "Personal": "Persönliches",
        "Cash withdrawal": "Bargeldabhebung",
        "Gifts & donations": "Geschenke & Spenden",
        "Education": "Bildung",
        "Bank fees": "Bankgebühren",
        "Taxes": "Steuern",
        "Saving & investing": "Sparen & Anlegen",
        "Savings": "Sparen",
        "Transfers": "Umbuchungen",
        "Own transfers": "Eigene Umbuchungen",
        "Investments": "Geldanlage",
        "Credit card payment": "Kreditkartenabrechnung",
        "Uncategorized": "Ohne Kategorie",
    }
}


def cat_name(name: str | None, lang: str | None = None) -> str | None:
    if not name:
        return name
    return CATEGORY_NAMES.get(lang or current(), {}).get(name, name)
