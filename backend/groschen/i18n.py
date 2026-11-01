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
    # currencies and bank files from anywhere
    "Exchange rates are turned off in Settings.": "Wechselkurse sind in den Einstellungen ausgeschaltet.",
    "Couldn't load the exchange rates. Groschen tries again tomorrow.": (
        "Die Wechselkurse konnten nicht geladen werden. Groschen versucht es morgen wieder."
    ),
    "Loading exchange rates": "Wechselkurse laden",
    "Converting": "Umrechnen",
    "Exchange rates": "Wechselkurse",
    "Pick the column with the date and the one with the amount.": "Wähle die Spalte mit dem Datum und die mit dem Betrag.",
    "Checking account": "Girokonto",
    "Groschen doesn't know that currency.": "Diese Währung kennt Groschen nicht.",
    "Amount in {currency}": "Betrag in {currency}",
    "Savings account": "Sparkonto",
    "Credit card": "Kreditkarte",
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
    "This doesn't look like a bank's CSV export. In your online banking, open the account's "
    "transactions and export them as CSV.": (
        "Das sieht nicht nach dem CSV-Export einer Bank aus. "
        "Öffne im Online-Banking die Umsätze des Kontos und exportiere sie als CSV."
    ),
    "The CSV file is missing the booking date or amount column.": (
        "In der CSV-Datei fehlt die Spalte mit dem Buchungsdatum oder dem Betrag."
    ),
    "A Bankleitzahl has 8 digits. It is also in your IBAN, right after DE and two digits.": (
        "Eine Bankleitzahl hat 8 Ziffern. Sie steht auch in deiner IBAN, direkt nach DE und zwei Ziffern."
    ),
    "The FinTS address must start with https:// and name the bank's server.": (
        "Die FinTS-Adresse muss mit https:// beginnen und den Server der Bank nennen."
    ),
    "Groschen doesn't know the FinTS address of this bank yet. Enter it under Advanced: "
    "your bank lists it on its website (search for FinTS or HBCI PIN/TAN).": (
        "Groschen kennt die FinTS-Adresse dieser Bank noch nicht. Trag sie unter „Erweitert“ ein: "
        "Deine Bank nennt sie auf ihrer Website (such nach FinTS oder HBCI PIN/TAN)."
    ),
    "This isn't the FinTS institute list. It is the file with the columns BLZ, Institut and "
    "PIN/TAN-Zugang URL that came with your product registration.": (
        "Das ist nicht die FinTS-Institutsliste. Gemeint ist die Datei mit den Spalten BLZ, Institut und "
        "PIN/TAN-Zugang URL, die du mit deiner Produktregistrierung bekommen hast."
    ),
    "Nothing is waiting for a TAN.": "Gerade wartet nichts auf eine TAN.",
    "Enter the TAN your bank asks for.": "Gib die TAN ein, nach der deine Bank fragt.",
    "{bank} didn't accept the login or PIN. Check both and try again.": (
        "{bank} hat Anmeldename oder PIN nicht akzeptiert. Prüf beides und versuch es noch einmal."
    ),
    "{bank} has locked the online access for now. Unlock it in your online banking first.": (
        "{bank} hat den Online-Zugang vorerst gesperrt. Entsperr ihn zuerst im Online-Banking."
    ),
    "{bank} refused the request. Log in to your online banking once, check that FinTS (HBCI) "
    "access is turned on there, and try again. The bank said: {text}": (
        "{bank} hat die Anfrage abgelehnt. Melde dich einmal im Online-Banking an, prüf, ob der "
        "FinTS-Zugang (HBCI) dort eingeschaltet ist, und versuch es noch einmal. Die Bank sagt: {text}"
    ),
    "Groschen couldn't reach {bank}. Check that the server has internet access and the FinTS address is right.": (
        "Groschen hat {bank} nicht erreicht. Prüf, ob der Server Internet hat und die FinTS-Adresse stimmt."
    ),
    "{bank} returned an error: {text}": "{bank} hat einen Fehler gemeldet: {text}",
    "{bank} asked for a TAN. Press Sync now in Groschen while you have your TAN device, "
    "and type the TAN when Groschen asks.": (
        "{bank} hat nach einer TAN gefragt. Drück in Groschen auf „Jetzt abrufen“, wenn du dein TAN-Gerät "
        "zur Hand hast, und gib die TAN ein, sobald Groschen fragt."
    ),
    "A FinTS product ID is needed. You get one free from the Deutsche Kreditwirtschaft.": (
        "Es wird eine FinTS-Produkt-ID gebraucht. Du bekommst sie kostenlos von der Deutschen Kreditwirtschaft."
    ),
    "The approval in your banking app timed out. Try again when you have your phone.": (
        "Die Bestätigung in deiner Banking-App ist abgelaufen. Versuch es noch einmal, wenn du dein Handy zur Hand hast."
    ),
    "Please approve the request in your banking app.": "Bitte bestätige die Anfrage in deiner Banking-App.",
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
    "Connecting to your bank": "Verbinde mit deiner Bank",
    "Fetching the last 90 days from your accounts": "Hole die letzten 90 Tage von deinen Konten",
    "Merging with your imported history": "Führe sie mit deinem importierten Verlauf zusammen",
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
    "your bank's purchase prices": "Kaufkursen deiner Bank",
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
