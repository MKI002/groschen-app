"""Made-up sample data for tests and for trying the web interface.

Everything here is invented: the person, the employer, the IBANs and the
amounts. It never touches the network. ``python -m groschen.demo`` fills an
empty data folder with two years of example history.
"""

import datetime as dt
import math
import random

BLZ = "50010517"
BIC = "INGDDEFFXXX"
OWNER = "Alex Beispiel"
EMPLOYER = "Nordlicht Software GmbH"

VWCE = "IE00BK5BQT80"
EMIM = "IE00BKM4GZ66"
FUNDS = {
    VWCE: {
        "name": "Vanguard FTSE All-World U.ETF Reg.Shs USD Acc. oN",
        "start": 96.0,
        "drift": 0.08,
        "vol": 0.14,
        "plan": 250.0,
    },
    EMIM: {
        "name": "iShs Core MSCI EM IMI U.ETF Registered Shares o.N.",
        "start": 27.5,
        "drift": 0.05,
        "vol": 0.17,
        "plan": 50.0,
    },
}


def iban(account_number: str, blz: str = BLZ) -> str:
    """A German IBAN with a correct check number (the account itself is made up)."""
    bban = blz + account_number.zfill(10)
    check = 98 - int(bban + "131400") % 97
    return f"DE{check:02d}{bban}"


GIRO_IBAN = iban("5401234567")
EXTRA_IBAN = iban("5409876543")
FRIEND, FRIEND_IBAN = "Lena Berger", iban("0012345678", "70150000")
DEPOT_NUMBER = "5405551212"
DEMO_PIN = "not-a-real-pin"  # what the fake bank accepts; there is no real bank behind it


def _workday(d: dt.date) -> dt.date:
    while d.weekday() >= 5:
        d += dt.timedelta(days=1)
    return d


def _months(start: dt.date, end: dt.date):
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        yield y, m
        m += 1
        if m == 13:
            y, m = y + 1, 1


def _tx(date, amount, counterparty, booking_text, purpose, counterparty_iban=None):
    return {
        "date": date.isoformat(),
        "value_date": date.isoformat(),
        "amount": round(amount, 2),
        "currency": "EUR",
        "counterparty": counterparty,
        "counterparty_iban": counterparty_iban,
        "purpose": purpose,
        "booking_text": booking_text,
    }


def _card(date, amount, merchant):
    return _tx(date, -amount, merchant, "Lastschrift", f"VISA Debitkartenumsatz vom {date:%d.%m.%Y}")


def prices(today: dt.date, months: int = 26, seed: int = 7) -> list[tuple[str, str, float]]:
    rng = random.Random(seed)
    start = today - dt.timedelta(days=months * 31)
    out = []
    for isin, f in FUNDS.items():
        p = f["start"]
        d = start
        daily_mu = f["drift"] / 252
        daily_sigma = f["vol"] / math.sqrt(252)
        while d <= today:
            if d.weekday() < 5:
                p *= math.exp(rng.gauss(daily_mu - daily_sigma**2 / 2, daily_sigma))
                out.append((isin, d.isoformat(), round(p, 2)))
            d += dt.timedelta(days=1)
    return out


def build(today: dt.date | None = None, months: int = 26, seed: int = 42) -> dict:
    today = today or dt.date.today()
    rng = random.Random(seed)
    start = (today.replace(day=1) - dt.timedelta(days=months * 30)).replace(day=1)
    price_rows = prices(today, months + 1)
    price_at = {}
    for isin, date, p in price_rows:
        price_at.setdefault(isin, {})[date] = p

    def price_on(isin, d):
        for back in range(10):
            key = (d - dt.timedelta(days=back)).isoformat()
            if key in price_at[isin]:
                return price_at[isin][key]
        return FUNDS[isin]["start"]

    giro, extra = [], []
    pieces = {isin: 0.0 for isin in FUNDS}
    paid = {isin: 0.0 for isin in FUNDS}
    groceries = ["REWE Markt GmbH", "EDEKA Center", "LIDL Dienstleistung", "ALDI SUED", "Hofladen Sonnenfeld"]
    eating = ["Vapiano Muenchen", "Starbucks Coffee", "Cafe Kranzler", "Pizzeria Da Luigi", "Kantine Nordlicht"]

    for y, m in _months(start, today):
        age = (today.year - y) * 12 + (today.month - m)  # 0 = this month

        def on(day, y=y, m=m):
            try:
                d = _workday(dt.date(y, m, day))
            except ValueError:
                d = _workday(dt.date(y, m, 28))
            return d if d <= today else None

        def add(lst, d, *args):
            if d:
                lst.append(_tx(d, *args))

        salary = 3180.0 if age > 12 else 3340.0
        add(giro, on(27), salary, EMPLOYER, "Gehalt/Rente", f"LOHN/GEHALT {m:02d}/{y}")
        add(giro, on(1), -1050.0, "Hausverwaltung Kraemer GmbH", "Dauerauftrag", "Miete Wohnung 3.OG links")
        add(
            giro,
            on(2),
            -74.0 if age > 10 else -81.0,
            "Stadtwerke Muenchen GmbH",
            "Lastschrift",
            "Abschlag Strom Vertragskonto 10000001",
        )
        add(giro, on(5), -39.95, "Telekom Deutschland GmbH", "Lastschrift", "Rechnung Festnetz/Internet")
        add(
            giro,
            on(6),
            -13.99 if age > 7 else -15.99,
            "Netflix International B.V.",
            "Lastschrift",
            "Netflix Monthly Subscription",
        )
        add(giro, on(8), -10.99 if age > 4 else -11.99, "Spotify AB", "Lastschrift", "Spotify Premium")
        # A streaming service cancelled a few months ago, one that came back after a pause, a new cloud plan.
        if 4 <= age <= 16:
            add(giro, on(12), -9.99, "Disney Plus", "Lastschrift", "Disney+ Monatsabo")
        if age <= 2 or 9 <= age <= 20:
            add(giro, on(18), -34.99, "DAZN Limited", "Lastschrift", "DAZN Abonnement")
        if age <= 2:
            add(giro, on(9), -2.99, "Apple Services", "Lastschrift", "iCloud+ 50 GB")
        add(giro, on(4), -49.0 if age > 9 else -58.0, "DB Vertrieb GmbH", "Lastschrift", "Deutschlandticket Abo")
        add(giro, on(15), -48.50, "HUK-COBURG Versicherung", "Lastschrift", "Kfz-Versicherung Vertrag 44-1234")
        if m in (1, 4, 7, 10):
            add(giro, on(15), -55.08, "Rundfunk ARD, ZDF, DRadio", "Lastschrift", "Beitragsnummer 123456789 Quartal")
        if m == 3:
            add(giro, on(10), -89.0, "Allianz Versicherungs-AG", "Lastschrift", "Haftpflichtversicherung Jahresbeitrag")
        if m == 11:
            add(giro, on(20), -129.0, "Lime Technology Inc", "Lastschrift", "Unraid license renewal")
        add(giro, on(1), -800.0, OWNER, "Ueberweisung", "Sparen", EXTRA_IBAN)
        d = on(1)
        if d:
            extra.append(_tx(d, 800.0, OWNER, "Gutschrift", "Sparen", GIRO_IBAN))
        if m in (3, 6, 9, 12):
            d = on(28)
            if d:
                extra.append(_tx(d, round(12 + (months - age) * 0.9, 2), "ING", "Abschluss", "Zinsen Extra-Konto"))

        for isin, f in FUNDS.items():
            d = on(1)
            if not d:
                continue
            giro.append(_tx(d, -f["plan"], "ING-DiBa AG", "Wertpapierkauf", f"Sparplan {isin} {f['name'][:30]}"))
            pieces[isin] += f["plan"] / price_on(isin, d)
            paid[isin] += f["plan"]

        for week in range(5):
            day = 2 + week * 6 + rng.randint(0, 3)
            d = on(min(day, 28))
            if not d:
                continue
            giro.append(_card(d, rng.uniform(18, 95), rng.choice(groceries)))
            if rng.random() < 0.6:
                giro.append(_card(d, rng.uniform(6, 38), rng.choice(eating)))
            if rng.random() < 0.35:
                giro.append(_card(d, rng.uniform(45, 75), rng.choice(["ARAL Station 1234", "Shell Deutschland"])))
            if rng.random() < 0.3:
                giro.append(_card(d, rng.uniform(4, 25), "dm-drogerie markt"))
        if rng.random() < 0.7:
            d = on(rng.randint(5, 25))
            if d:
                giro.append(
                    _tx(
                        d,
                        -round(rng.uniform(12, 140), 2),
                        "AMAZON PAYMENTS EUROPE S.C.A.",
                        "Lastschrift",
                        f"Amazon.de Bestellung 302-{rng.randint(1000000, 9999999)}",
                    )
                )
        if rng.random() < 0.5:
            d = on(rng.randint(5, 25))
            if d:
                shop = rng.choice(["Zalando SE", "Thomann GmbH", "Steam Games"])
                giro.append(
                    _tx(
                        d,
                        -round(rng.uniform(20, 120), 2),
                        "PayPal Europe S.a.r.l. et Cie S.C.A",
                        "Lastschrift",
                        f"PP.{rng.randint(1000, 9999)}.PP . {shop}, Ihr Einkauf bei {shop}",
                    )
                )
        if rng.random() < 0.4:
            d = on(rng.randint(5, 25))
            if d:
                giro.append(
                    _tx(
                        d,
                        -round(rng.choice([50, 100, 150]), 2),
                        "Bargeldauszahlung",
                        "Bargeldauszahlung",
                        "GA NR00001234 BLZ70010080 0",
                    )
                )
        if rng.random() < 0.3:
            d = on(rng.randint(5, 25))
            if d:
                giro.append(_card(d, rng.uniform(25, 40), "Friseur Haarmonie"))
        if m == 8 and age < 13:
            d = on(12)
            if d:
                giro.append(_tx(d, -612.40, "Booking.com B.V.", "Lastschrift", "Hotel Lago di Garda"))
        if m == 12:
            d = on(18)
            if d:
                giro.append(_card(d, 189.99, "MediaMarkt Muenchen"))
        if m == 5 and age < 13:
            d = on(22)
            if d:
                giro.append(_tx(d, 412.37, "Finanzamt Muenchen", "Gutschrift", "Einkommensteuer Erstattung 2025"))
        # Money that came back last month: part of an order sent back, a whole order refunded, a friend
        # paying back half of the concert tickets, and one paying back a share of dinner (linked by hand).
        if age == 1:
            pp, shop = "PayPal Europe S.a.r.l. et Cie S.C.A", "About You SE"
            add(giro, on(3), -89.90, pp, "Lastschrift", f"PP.5521.PP . {shop}, Ihr Einkauf bei {shop}")
            add(giro, on(15), 39.95, pp, "Gutschrift", f"PP.5521.PP . {shop}, Ihr Einkauf bei {shop}")
            add(giro, on(10), -34.99, "AMAZON PAYMENTS EUROPE S.C.A.", "Lastschrift", "Amazon.de Bestellung 302-4418805")
            add(giro, on(19), 34.99, "AMAZON PAYMENTS EUROPE S.C.A.", "Gutschrift", "Amazon.de Erstattung 302-4418805")
            add(giro, on(5), -64.0, FRIEND, "Ueberweisung", "Konzertkarten", FRIEND_IBAN)
            add(giro, on(12), 32.0, FRIEND, "Gutschrift", "Deine Karte", FRIEND_IBAN)
            d = on(20)
            if d:
                giro.append(_card(d, 86.40, "Pizzeria Da Luigi"))
            add(giro, on(22), 43.20, "Jonas Weber", "Gutschrift", "Pizza bei Luigi")

    # The gym charges every four weeks, always on the same weekday.
    d = _workday(start + dt.timedelta(days=10))
    while d <= today:
        giro.append(_tx(d, -24.99, "FitX Deutschland GmbH", "Lastschrift", "Mitgliedsbeitrag alle 4 Wochen"))
        d += dt.timedelta(days=28)

    giro.sort(key=lambda t: t["date"])
    extra.sort(key=lambda t: t["date"])
    holdings = []
    for isin, f in FUNDS.items():
        p = price_on(isin, today)
        holdings.append(
            {
                "isin": isin,
                "name": f["name"],
                "pieces": round(pieces[isin], 4),
                "price": p,
                "price_date": today.isoformat(),
                "value": round(pieces[isin] * p, 2),
                "acquisition_price": round(paid[isin] / pieces[isin], 4) if pieces[isin] else None,
            }
        )
    giro_balance = round(3500.0 + sum(t["amount"] for t in giro), 2)
    extra_balance = round(6000.0 + sum(t["amount"] for t in extra), 2)
    return {
        "today": today,
        "giro": giro,
        "extra": extra,
        "giro_balance": giro_balance,
        "extra_balance": extra_balance,
        "holdings": holdings,
        "prices": price_rows,
    }


def ing_csv(iban_: str, name: str, balance: float, txs: list[dict]) -> bytes:
    """The same layout as the CSV that ING banking exports ("Umsatzanzeige")."""

    def de(x: float) -> str:
        return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    lines = [
        "Umsatzanzeige;Datei erstellt am: 27.09.2026 12:00",
        "",
        f"IBAN;{iban_[:4]} {iban_[4:8]} {iban_[8:12]} {iban_[12:16]} {iban_[16:20]} {iban_[20:]}",
        f"Kontoname;{name}",
        "Bank;ING",
        f"Kunde;{OWNER}",
        "Zeitraum;01.01.2024 - 27.09.2026",
        f"Saldo;{de(balance)};EUR",
        "",
        "Sortierung;Datum absteigend",
        "",
        "In der CSV-Datei finden Sie alle bereits gebuchten Umsätze. Die vorgemerkten Umsätze werden nicht aufgenommen.",
        "",
        "Buchung;Wertstellungsdatum;Auftraggeber/Empfänger;Buchungstext;Verwendungszweck;Saldo;Währung;Betrag;Währung",
    ]
    running = balance
    for t in sorted(txs, key=lambda t: t["date"], reverse=True):
        d = dt.date.fromisoformat(t["date"]).strftime("%d.%m.%Y")
        purpose = (t["purpose"] or "").replace(";", ",")
        lines.append(
            f"{d};{d};{t['counterparty'] or ''};{t['booking_text'] or ''};{purpose};{de(running)};EUR;{de(t['amount'])};EUR"
        )
        running = round(running - t["amount"], 2)
    return ("\n".join(lines) + "\n").encode("cp1252", errors="replace")


def price_csv(rows: list[tuple[str, str, float]]) -> bytes:
    out = ["Datum;ISIN;Kurs"]
    for isin, date, p in rows:
        out.append(f"{dt.date.fromisoformat(date):%d.%m.%Y};{isin};" + f"{p:.2f}".replace(".", ","))
    return "\n".join(out).encode("utf-8")


class FakeBank:
    """Behaves like FinTSSession for tests and for the demo: serves the last 90 days."""

    def __init__(self, data: dict, needs_approval: bool = False):
        self.data = data
        self.needs_approval = needs_approval

    def __call__(self, bank_code, login, pin, product_id, state=None, on_wait=None, server=None, on_tan=None):
        from .jobs import UserFacingError

        if pin != DEMO_PIN or not product_id:
            raise UserFacingError("ING didn't accept the login or PIN. Check both and try again.")
        if self.needs_approval and on_wait:
            on_wait("Please approve the request in your banking app.")
        return _FakeSession(self.data, approved=self.needs_approval)


class _FakeSession:
    def __init__(self, data, approved: bool = False):
        self.data = data
        self.approved = approved

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def state(self) -> bytes:
        return b"fake-state"

    def accounts(self):
        return [
            {
                "kind": "checking",
                "name": "Girokonto",
                "iban": GIRO_IBAN,
                "account_number": "5401234567",
                "subaccount": None,
                "bic": BIC,
                "blz": BLZ,
                "currency": "EUR",
            },
            {
                "kind": "savings",
                "name": "Extra-Konto",
                "iban": EXTRA_IBAN,
                "account_number": "5409876543",
                "subaccount": None,
                "bic": BIC,
                "blz": BLZ,
                "currency": "EUR",
            },
            {
                "kind": "depot",
                "name": "Direkt-Depot",
                "iban": None,
                "account_number": DEPOT_NUMBER,
                "subaccount": None,
                "bic": BIC,
                "blz": BLZ,
                "currency": "EUR",
            },
        ]

    def _list(self, account):
        return self.data["giro"] if account["iban"] == GIRO_IBAN else self.data["extra"]

    def balance(self, account):
        bal = self.data["giro_balance"] if account["iban"] == GIRO_IBAN else self.data["extra_balance"]
        return bal, self.data["today"].isoformat()

    def transactions(self, account, since):
        return [t for t in self._list(account) if t["date"] >= since.isoformat()]

    def holdings(self, account):
        return self.data["holdings"]


def load(conn_factory=None, today: dt.date | None = None) -> dict:
    """Fill the database the way a real first run would: CSV history, then a bank sync."""
    from . import db, jobs, settings
    from .bank import sync

    data = build(today)
    cutoff = (data["today"] - dt.timedelta(days=89)).isoformat()
    sync.session_factory = FakeBank(data)
    job = jobs.run_inline("demo", sync.test_connection, BLZ, "demo", DEMO_PIN, "DEMO-PRODUCT-ID")
    if job.state == "error":
        raise RuntimeError(job.error)
    jobs.run_inline(
        "demo",
        sync.import_csv,
        ing_csv(GIRO_IBAN, "Girokonto", data["giro_balance"], [t for t in data["giro"] if t["date"] < cutoff]),
    )
    jobs.run_inline(
        "demo",
        sync.import_csv,
        ing_csv(EXTRA_IBAN, "Extra-Konto", data["extra_balance"], [t for t in data["extra"] if t["date"] < cutoff]),
    )
    sync.import_prices(price_csv(data["prices"]))
    job = jobs.run_inline("demo", sync.sync_all, True, True)
    if job.state == "error":
        raise RuntimeError(job.error)
    with db.session() as conn:
        settings.put(conn, "setup_complete", True)
    return job.result or {}


if __name__ == "__main__":
    import sys

    from . import db, netguard

    netguard.install()
    db.init()
    with db.session() as c:
        if c.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]:
            sys.exit("This data folder already has transactions. Use an empty folder for the demo.")
    print(load())
