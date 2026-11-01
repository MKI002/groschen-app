import time

import pytest

from groschen.categorize import engine, vendors
from groschen.categorize.vendor_list import PAYMENT_SERVICES, VENDORS
from tests.test_categorize import _account, _add, _category


def _match(payee, purpose=""):
    hit = vendors.match(f"{payee} {purpose}", (payee,))
    return hit[0] if hit else None


@pytest.mark.parametrize(
    "payee, purpose, expected",
    [
        # Germany, Austria, Switzerland
        ("REWE Markt GmbH", "", "Groceries"),
        ("VISA HOFER DANKT 1234", "", "Groceries"),
        ("MUELLER DROGERIE 123", "", "Drugstore"),
        ("MULLER DROGERIE", "", "Drugstore"),
        ("Migros Zuerich", "", "Groceries"),
        ("DB Vertrieb GmbH", "Fahrkarte", "Public transport"),
        ("Stadtwerke Muenchen", "Abschlag Strom", "Energy"),
        ("Techniker Krankenkasse", "", "Insurance"),
        # France, Benelux, Italy, Spain, Portugal
        ("CARREFOUR MARKET PARIS 15", "", "Groceries"),
        ("CB INTERMARCHE 12/10", "", "Groceries"),
        ("VISA ALBERT HEIJN 1234 AMSTERDAM", "", "Groceries"),
        ("NS GROEP IZ NS REIZIGERS", "", "Public transport"),
        ("ESSELUNGA MILANO", "", "Groceries"),
        ("MERCADONA VALENCIA", "", "Groceries"),
        ("PINGO DOCE LISBOA", "", "Groceries"),
        ("Trenitalia", "Biglietto", "Public transport"),
        ("SNCF CONNECT", "", "Public transport"),
        # Nordics, Poland, UK and Ireland
        ("ICA NARA HOGDALEN", "", "Groceries"),
        ("REMA 1000 OSLO", "", "Groceries"),
        ("BIEDRONKA 1234 WARSZAWA", "", "Groceries"),
        ("TESCO STORES 1234", "", "Groceries"),
        ("TfL Travel Ch", "", "Public transport"),
        ("BOOTS 1234 LONDON", "", "Drugstore"),
        # United States
        ("WM SUPERCENTER #1234", "", "Groceries"),
        ("TARGET T-1234 MINNEAPOLIS MN", "", "Shopping"),
        ("CVS/PHARMACY #1234", "", "Pharmacy"),
        ("CHEVRON 0091234", "", "Fuel"),
        ("SQ *BLUE BOTTLE COFFEE", "", "Restaurants & cafés"),
        ("TST* JOES DINER", "", "Restaurants & cafés"),
        ("DD *DOORDASH MCDONALDS", "", "Food delivery"),
        ("GEICO *AUTO", "", "Insurance"),
        ("AT&T*BILL PAYMENT", "", "Internet & phone"),
        ("IRS USATAXPYMT", "", "Taxes"),
        # The longer name wins
        ("UBER *EATS", "", "Food delivery"),
        ("UBER *TRIP", "", "Taxi & rides"),
        ("AMAZON PRIME*1234", "", "Streaming"),
        ("AMZN Mktp DE", "", "Online shopping"),
        # Written together or with an apostrophe
        ("BURGERKING 123", "", "Restaurants & cafés"),
        ("MCDONALD'S 0815", "", "Restaurants & cafés"),
    ],
)
def test_known_vendors(payee, purpose, expected):
    assert _match(payee, purpose) == expected


def test_shop_beats_payment_service():
    assert _match("Klarna Bank AB", "Zalando SE Bestellung 1234") == "Clothing"
    assert _match("Klarna Bank AB", "Bestellung 1234") == "Online shopping"


@pytest.mark.parametrize(
    "payee, purpose",
    [
        ("Max Mustermann", "Danke fürs Essen"),
        ("John Smith", "Thanks for dinner"),
        ("Marta Rossi", "Regalo compleanno"),
        ("Bart de Vries", "Terugbetaling"),
        ("Douglas Adams", "Buch"),
        ("Tim Becker", "Konzertkarten zurück"),
        ("Jules Martin", "Remboursement"),
        ("Leclerc Jean", "Virement"),
        ("Max Next", "Rückzahlung"),
        ("Anna Schmidt", "Geburtstag"),
        ("VR Bank Nord eG", "Darlehen"),
        ("Dott. Mario Bianchi", "Fattura 12"),
        ("Dupont SAS", "Facture 2026-10"),
        ("United Domains", "Rechnung"),
    ],
)
def test_no_false_positives(payee, purpose):
    assert _match(payee, purpose) is None


def test_short_names_count_only_at_the_start():
    assert _match("KFC 1234 BERLIN") == "Restaurants & cafés"
    assert _match("BP 1234 HAMBURG") == "Fuel"
    assert _match("Max Mustermann", "Ich war bei KFC und BP") is None
    assert _match("Anna Schmidt", "Target 2027 erreicht") is None
    # Whole words only: ICA is no part of AMERICA, BP no part of BPX.
    assert _match("AMERICAN BOOKSTORE") is None
    assert _match("BPX 1234") is None


# Words that must never be a vendor on their own: everyday words and first names across Europe and the US.
COMMON = """
A AN AND THE OF FOR TO IN ON AT BY WITH FROM DER DIE DAS UND ODER FUER MIT VON ZU AM IM DE LA LE LES ET DU EL LOS Y IL DI
DA E O EN OCH OG I PA VAN HET EEN TOTAL NEW ONE BEST BIG STAR SUPER BANK PAY PAYMENT CARD SHOP STORE MARKET CITY HOME HOUSE
BOOK BOOKS
MAX TIM TOM ANNA MARIA MARTA BART JAN PETER PAUL JULES SANDRO DOUGLAS CECIL ELISA CASPER TITUS ROGER ROGERS DAVID MICHAEL
LEO LISA SARA EMMA LUCA MARCO PIERRE JEAN HANS KARL FRITZ JOHN JAMES MARY LINDA ROSE CORA AIDA BRUNA ENEA GAIA ODA
PLUS MORE LIFE TIME WORLD NATURE SUN SUMMER SPRING FALL WINTER APPLE PEACH LEMON CHERRY ROSE GOLD SILVER
GUTSCHEIN RECHNUNG ZAHLUNG UEBERWEISUNG DAUERAUFTRAG LASTSCHRIFT GUTSCHRIFT FACTURE FATTURA FACTURA REKENING INVOICE
BUCHER WOLLE FOTO MODE PRESSING PENSION SEMESTER PORTO MESSE HORT TASCA TAXE SIZE WISH KOMFORT CHECK DEPOT
""".split()


def test_common_words_are_never_vendors_on_their_own():
    single = {k[0] for k in (*vendors.ANYWHERE, *vendors.LEAD) if len(k) == 1}
    assert not single & set(COMMON)


def test_short_words_only_match_at_the_start():
    assert all(len(k) > 1 or len(k[0]) >= vendors.MIN_ANYWHERE for k in vendors.ANYWHERE)


def test_list_is_huge_and_parses():
    assert len(vendors.ANYWHERE) + len(vendors.LEAD) > 8000
    for block in [*VENDORS.values(), PAYMENT_SERVICES]:
        for line in block.splitlines():
            for entry in line.split("#", 1)[0].split(","):
                assert entry.count("=") <= 1, entry


def test_vendor_categories_exist(conn):
    names = {r[0] for r in conn.execute("SELECT name FROM categories")}
    assert set(VENDORS) <= names


def test_matching_is_fast():
    text = "VISA CARREFOUR MARKET 1234 PARIS FR KAUFUMSATZ 02.10 5,80 121357 ARN74000000 Google Pay"
    start = time.perf_counter()
    for _ in range(5000):
        vendors.match(text, ("VISA CARREFOUR MARKET 1234 PARIS",))
    assert time.perf_counter() - start < 1.0


def test_engine_sorts_by_vendor_list(conn):
    acc = _account(conn)
    cases = {
        _add(conn, acc, "2026-09-01", -42.10, "CARREFOUR MARKET PARIS"): "Groceries",
        _add(
            conn,
            acc,
            "2026-09-02",
            -15.99,
            "PayPal Europe S.a.r.l. et Cie S.C.A",
            "PP.1234.PP . Deezer, Ihr Einkauf bei Deezer",
        ): "Streaming",
        _add(conn, acc, "2026-09-03", -60.00, "Klarna Bank AB", "Zalando SE 1234"): "Clothing",
        _add(conn, acc, "2026-09-04", -9.80, "SQ *BLUE BOTTLE COFFEE"): "Restaurants & cafés",
        # An employer that is also a shop pays a salary, not a refund.
        _add(conn, acc, "2026-09-05", 3100.0, "Deutsche Telekom AG", "LOHN/GEHALT 09/2026", "Gehalt/Rente"): "Salary",
    }
    engine.categorize(conn)
    for tx_id, expected in cases.items():
        assert _category(conn, tx_id) == expected
