"""Groschen working things out by itself: own transfers, refunds, readable names and CSV files
without their header lines. All names, places and numbers here are made up."""

import pytest
from test_categorize import _account, _add, _category

from groschen import db, demo, jobs, settings
from groschen.analytics import cashflow, refunds
from groschen.bank import csv_import, sync
from groschen.categorize import engine, names

IBAN = "DE70500105171234567890"  # made up, with a valid check sum
PAYPAL = "PayPal Europe S.a.r.l. et Cie S.C.A"
HEADER = (
    "Buchung;Wertstellungsdatum;Auftraggeber/Empfänger;Buchungstext;Verwendungszweck;Referenz;Saldo;Währung;Betrag;Währung"
)
ROWS = [  # newest first, as ING exports them; the balance after each booking is in the "Saldo" column
    ("07.10.2026", "VISA SHOP MUSTERSTADT", "Lastschrift", "1.859,17", "-6,14"),
    ("06.10.2026", "Kleingeld Plus - Sparen", "Überweisung", "1.865,31", "-0,4"),
    ("06.10.2026", "VISA CAFE ROSE", "Lastschrift", "1.865,71", "-3,60"),
    ("01.10.2026", "Arbeitgeber GmbH", "Gehalt/Rente", "1.869,31", "2.000,00"),
]


def _csv(rows) -> bytes:
    lines = [HEADER] + [f"{d};{d};{cp};{bt};XXX;XXX;{saldo};EUR;{amount};EUR" for d, cp, bt, saldo, amount in rows]
    return "\r\n".join(lines).encode("cp1252")


def _source(conn, tx_id):
    return conn.execute("SELECT cat_source FROM transactions WHERE id = ?", (tx_id,)).fetchone()[0]


def _set_category(conn, tx_id, name):
    cat = conn.execute("SELECT id FROM categories WHERE name = ?", (name,)).fetchone()[0]
    conn.execute("UPDATE transactions SET category_id = ?, cat_source = 'user', needs_review = 0 WHERE id = ?", (cat, tx_id))


# --- money sent to the user's own name -------------------------------------------------


def test_transfer_to_own_name_is_moved_not_spent(conn):
    settings.put(conn, "holder_names", ["Alex Beispiel"])
    acc = _account(conn)
    plain = _add(conn, acc, "2026-09-01", -200.0, "BEISPIEL, ALEX", "Urlaubskasse", "Überweisung")
    saved = _add(conn, acc, "2026-09-02", -300.0, "Alex Beispiel", "Notgroschen", "Echtzeitüberweisung")
    invested = _add(conn, acc, "2026-09-03", -500.0, "Alex Beispiel", "Trade Republic", "Überweisung")
    back = _add(conn, acc, "2026-09-04", 150.0, "Dr. Alex Beispiel", "", "Gutschrift")
    family = _add(conn, acc, "2026-09-05", -50.0, "Kim Beispiel", "Geburtstag", "Überweisung")
    engine.categorize(conn)
    assert (_category(conn, plain), _source(conn, plain)) == ("Own transfers", "own")
    assert _category(conn, saved) == "Savings"
    assert _category(conn, invested) == "Investments"
    assert _category(conn, back) == "Own transfers"
    assert _source(conn, family) != "own"
    month = cashflow.summary(conn, "2026-09-01", "2026-09-30")
    assert month["income_total"] == 0 and month["spending_total"] == pytest.approx(50.0)


def test_names_can_be_changed_and_bookings_follow(conn):
    acc = _account(conn)
    tx = _add(conn, acc, "2026-09-01", -200.0, "Alex Beispiel", "Urlaubskasse", "Überweisung")
    engine.categorize(conn)
    assert _source(conn, tx) != "own"
    settings.update(conn, {"holder_names": ["  Alex   Beispiel ", "Alex Beispiel"]})
    assert settings.get(conn, "holder_names") == ["Alex Beispiel"]
    engine.reapply_quick(conn)
    assert _category(conn, tx) == "Own transfers"
    settings.update(conn, {"holder_names": []})
    engine.reapply_quick(conn)
    assert _source(conn, tx) != "own"
    with pytest.raises(ValueError):
        settings.update(conn, {"holder_names": "Alex Beispiel"})


def test_name_matching():
    holders = [engine.name_tokens("Jürgen Müller")]
    assert engine.is_own_name("MUELLER, JUERGEN", holders)
    assert engine.is_own_name("Jurgen Muller", holders)
    assert engine.is_own_name("Jürgen Peter Müller", holders)  # a middle name
    assert not engine.is_own_name("Anna Müller", holders)
    assert not engine.is_own_name("Müller", holders)
    assert not engine.is_own_name("Jürgen Müller Bau GmbH und Partner", holders)


def test_holder_names_come_from_the_bank_file(run_job):
    raw = demo.ing_csv(demo.GIRO_IBAN, "Girokonto", 100.0, [])
    job = jobs.run_inline("import", sync.import_csv, raw)
    assert job.state == "done", job.error
    with db.session() as conn:
        assert settings.get(conn, "holder_names") == [demo.OWNER]


# --- refunds ---------------------------------------------------------------------------


def test_refund_cancels_its_purchase(conn):
    acc = _account(conn)
    buy = _add(conn, acc, "2026-09-01", -59.90, "VISA TANKSTELLE AM RING")
    back = _add(conn, acc, "2026-09-03", 59.90, "VISA TANKSTELLE AM RING", "", "Gutschrift")
    engine.categorize(conn)
    assert _category(conn, buy) == "Fuel"
    assert (_category(conn, back), _source(conn, back)) == ("Fuel", "refund")
    month = cashflow.summary(conn, "2026-09-01", "2026-09-30")
    assert month["income_total"] == 0 and month["spending_total"] == 0


def test_refund_through_paypal_follows_the_purchase(conn):
    acc = _account(conn)
    buy = _add(conn, acc, "2026-09-10", -14.18, PAYPAL, "1234/PP.1329.PP/. Shop A, Ihr Einkauf bei Shop A")
    back = _add(conn, acc, "2026-09-14", 14.18, PAYPAL, "1240/PP.1329.PP/. Rueckzahlung", "Gutschrift")
    other = _add(conn, acc, "2026-09-15", 9.0, PAYPAL, "1241/PP.1329.PP/. Rueckzahlung", "Gutschrift")
    old = _add(conn, acc, "2026-03-01", -30.0, PAYPAL, "1200/PP.1329.PP/. Shop B, Ihr Einkauf bei Shop B")
    late = _add(conn, acc, "2026-09-15", 30.0, PAYPAL, "1242/PP.1329.PP/. Rueckzahlung", "Gutschrift")
    _set_category(conn, buy, "Clothing")
    _set_category(conn, old, "Clothing")
    engine.categorize(conn)
    assert (_category(conn, back), _source(conn, back)) == ("Clothing", "refund")
    assert _source(conn, other) != "refund"  # no purchase of that amount
    assert _source(conn, late) != "refund"  # more than three months later
    _set_category(conn, buy, "Electronics")
    engine.link(conn)
    assert _category(conn, back) == "Electronics"


def _links(conn):
    return dict(conn.execute("SELECT refund_id, purchase_id FROM refund_links").fetchall())


def test_money_back_from_a_friend_is_linked_to_what_was_sent(conn):
    acc = _account(conn)
    out = _add(conn, acc, "2026-09-01", -15.0, "Kim Beispiel", "Kino", "Echtzeitüberweisung")
    _set_category(conn, out, "Own transfers")
    back = _add(conn, acc, "2026-09-05", 15.0, "Kim Beispiel", "", "Gutschrift")
    tickets = _add(conn, acc, "2026-09-10", -40.0, "Sam Muster", "Konzertkarten", "Überweisung")
    _set_category(conn, tickets, "Entertainment")
    share = _add(conn, acc, "2026-09-20", 29.0, "Sam Muster", "Danke!", "Gutschrift")
    engine.categorize(conn)
    assert _links(conn) == {back: out, share: tickets}
    assert (_category(conn, back), _category(conn, share)) == ("Own transfers", "Entertainment")
    month = cashflow.summary(conn, "2026-09-01", "2026-09-30")
    assert month["income_total"] == 0 and month["spending_total"] == pytest.approx(11.0)


def test_money_back_for_a_payment_without_a_category_is_no_income(conn):
    acc = _account(conn)
    gift = _add(conn, acc, "2026-09-01", -64.0, "Lena Muster", "Auslage", "Überweisung")
    back = _add(conn, acc, "2026-09-03", 32.0, "Lena Muster", "Meine Hälfte", "Gutschrift")
    engine.categorize(conn)
    assert _links(conn) == {back: gift} and _category(conn, gift) is None
    month = cashflow.summary(conn, "2026-09-01", "2026-09-30")
    assert month["income_total"] == 0 and month["spending_total"] == pytest.approx(32.0)


def test_part_refunds_add_up_to_their_payment(conn):
    acc = _account(conn)
    buy = _add(conn, acc, "2026-09-01", -40.0, "Muster Mode GmbH", "Bestellung 123")
    _set_category(conn, buy, "Clothing")
    first = _add(conn, acc, "2026-09-08", 15.0, "Muster Mode GmbH", "Retoure", "Gutschrift")
    second = _add(conn, acc, "2026-09-12", 14.0, "Muster Mode GmbH", "Retoure", "Gutschrift")
    too_much = _add(conn, acc, "2026-09-15", 20.0, "Muster Mode GmbH", "Gutschrift", "Gutschrift")
    engine.categorize(conn)
    assert _links(conn) == {first: buy, second: buy}
    items = [{"id": buy}, {"id": first}, {"id": too_much}]
    refunds.annotate(conn, items)
    assert items[0]["refunded"] == 29.0 and items[1]["refund_for"]["id"] == buy and items[2]["refund_for"] is None
    assert refunds.detail(conn, first)["left"] == 11.0


def test_a_part_back_through_paypal_needs_the_shop_by_name(conn):
    acc = _account(conn)
    buy = _add(conn, acc, "2026-09-01", -30.0, PAYPAL, "1234/PP.1329.PP/. Shop A, Ihr Einkauf bei Shop A")
    _set_category(conn, buy, "Clothing")
    vague = _add(conn, acc, "2026-09-05", 10.0, PAYPAL, "1240/PP.1329.PP/. Rueckzahlung", "Gutschrift")
    named = _add(conn, acc, "2026-09-06", 5.0, PAYPAL, "1241/PP.1329.PP/. Shop A, Ihr Einkauf bei Shop A", "Gutschrift")
    engine.categorize(conn)
    assert _links(conn) == {named: buy} and _source(conn, vague) != "refund"


def test_money_that_comes_regularly_is_no_payback(conn):
    acc = _account(conn)
    paid = _add(conn, acc, "2026-08-01", -900.0, "Robin Beispiel", "Moebel", "Überweisung")
    _set_category(conn, paid, "Home & furniture")
    rent = [_add(conn, acc, f"2026-{m:02d}-03", 350.0, "Robin Beispiel", "Miete", "Gutschrift") for m in (6, 7, 8)]
    engine.categorize(conn)
    assert rent[2] not in _links(conn)


def test_a_wrong_link_is_taken_away_and_remembered(conn):
    acc = _account(conn)
    gift = _add(conn, acc, "2026-09-01", -150.0, "Kim Beispiel", "Geburtstag", "Überweisung")
    _set_category(conn, gift, "Gifts & donations")
    back = _add(conn, acc, "2026-09-20", 100.0, "Kim Beispiel", "Alles Gute", "Gutschrift")
    engine.categorize(conn)
    assert _links(conn) == {back: gift}
    refunds.unlink(conn, back)
    assert _links(conn) == {} and _source(conn, back) != "refund"
    engine.link(conn)
    assert _links(conn) == {}
    part = _add(conn, acc, "2026-09-25", 20.0, "Kim Beispiel", "", "Gutschrift")  # a part: no longer linked by itself
    lent = _add(conn, acc, "2026-10-01", -30.0, "Kim Beispiel", "Pizza", "Überweisung")
    whole = _add(conn, acc, "2026-10-02", 30.0, "Kim Beispiel", "Pizza", "Gutschrift")  # the whole amount still is
    engine.categorize(conn)
    assert _links(conn) == {whole: lent} and part not in _links(conn)


def test_linking_by_hand(conn):
    acc = _account(conn)
    dinner = _add(conn, acc, "2026-09-01", -80.0, "Trattoria Muster", "VISA")
    _set_category(conn, dinner, "Restaurants & cafés")
    share = _add(conn, acc, "2026-09-02", 40.0, "Sam Muster", "Pizza gestern", "Gutschrift")
    engine.categorize(conn)
    assert _links(conn) == {}
    assert refunds.candidates(conn, share)[0]["id"] == dinner
    refunds.link(conn, share, dinner)
    engine.link(conn)
    assert _links(conn) == {share: dinner} and _category(conn, share) == "Restaurants & cafés"
    other = _add(conn, acc, "2026-09-03", 50.0, "Alex Muster", "", "Gutschrift")
    with pytest.raises(ValueError):
        refunds.link(conn, other, dinner)  # only 40 left of it
    d = refunds.detail(conn, dinner)
    assert d["refunded"] == 40.0 and d["left"] == 40.0 and [r["id"] for r in d["refunds"]] == [share]
    _set_category(conn, dinner, "Food & Dining")
    engine.link(conn)
    assert _category(conn, share) == "Food & Dining"  # follows its payment


def test_someone_paying_back_a_share_is_learned(conn):
    acc = _account(conn)
    dinner = _add(conn, acc, "2026-08-01", -64.20, "Trattoria Muster", "VISA")
    _set_category(conn, dinner, "Restaurants & cafés")
    _add(conn, acc, "2026-08-01", -71.80, "Markt Muster", "VISA")
    first = _add(conn, acc, "2026-08-02", 32.10, "Robin Muster", "Pizza", "Gutschrift")
    engine.categorize(conn)
    assert _links(conn) == {}  # a bill paid to someone else: not linked by itself
    top = refunds.candidates(conn, first)[0]
    assert top["id"] == dinner and top["share"] == 2  # exactly half of it, so it comes first
    refunds.link(conn, first, dinner)
    bar = _add(conn, acc, "2026-09-10", -45.30, "Bar Beispiel", "VISA")
    _add(conn, acc, "2026-09-11", -23.17, "Markt Muster", "VISA")
    third = _add(conn, acc, "2026-09-12", 15.10, "Robin Muster", "Bar", "Gutschrift")
    engine.categorize(conn)
    assert _links(conn)[third] == bar  # a third of the bar: Robin is known to pay back shares now
    _add(conn, acc, "2026-09-20", -40.0, "Kino Muster", "VISA")
    _add(conn, acc, "2026-09-21", -20.0, "Imbiss Muster", "VISA")
    either = _add(conn, acc, "2026-09-22", 20.0, "Robin Muster", "", "Gutschrift")
    engine.categorize(conn)
    assert either not in _links(conn)  # half of one payment and all of another: not guessed
    refunds.unlink(conn, third)
    snack = _add(conn, acc, "2026-09-25", -9.80, "Kiosk Muster", "VISA")
    late = _add(conn, acc, "2026-09-26", 4.90, "Robin Muster", "", "Gutschrift")
    engine.categorize(conn)
    assert late not in _links(conn) and snack not in _links(conn).values()  # taken back once: asked from then on


# --- merchants and readable names ------------------------------------------------------


def test_new_merchants(conn):
    acc = _account(conn)
    cases = {
        _add(conn, acc, "2026-09-01", -12.99, "klarmobil GmbH"): "Internet & phone",
        _add(conn, acc, "2026-09-02", -56.39, "MUSTER VERSICHERUNGS AG"): "Insurance",
        _add(conn, acc, "2026-09-03", 29.45, "Dioezese Musterstadt (KdoR)", "", "Gutschrift"): "Taxes",
        _add(conn, acc, "2026-09-04", -102.0, "KFZ Beispiel", "Rechnung 123", "Echtzeitüberweisung"): "Car costs",
        _add(conn, acc, "2026-09-05", -107.2, "Klarna Bank AB (publ)", "", "Echtzeitüberweisung"): "Online shopping",
        _add(conn, acc, "2026-09-06", -3.6, "VISA DITSCH MUSTERSTADT"): "Restaurants & cafés",
        _add(conn, acc, "2026-09-07", -25.0, "VISA GOOGLE CLOUD 12AB34"): "Software & cloud",
        _add(conn, acc, "2026-09-08", -3.1, "Amazon Web Services EMEA SARL"): "Software & cloud",
        _add(conn, acc, "2026-09-09", -500.0, "Scalable Capital GmbH", "", "Überweisung"): "Investments",
        _add(conn, acc, "2026-09-10", -300.0, "HUK-COBURG", "Kfz-Versicherung", "Lastschrift"): "Insurance",
    }
    engine.categorize(conn)
    for tx_id, expected in cases.items():
        assert _category(conn, tx_id) == expected


def test_existing_install_learns_new_merchants(conn):
    acc = _account(conn)
    tx = _add(conn, acc, "2026-09-01", -12.99, "klarmobil GmbH")
    conn.execute("UPDATE transactions SET category_id = NULL, cat_source = 'model', needs_review = 1 WHERE id = ?", (tx,))
    conn.execute("UPDATE meta SET value = '1' WHERE key = 'knowledge'")
    conn.commit()
    db.init()
    assert _category(conn, tx) == "Internet & phone"


def test_readable_names():
    cases = {
        "VISA MCDONALDS 01234": "McDonald's",
        "AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND": "Amazon",
        "VISA SPC*CAFE ROSE": "Cafe Rose",
        "VISA BURGER KING 12345 ABC": "Burger King",
        "MUSTER VERSICHERUNGS AG": "Muster Versicherung",
        "VISA EDEKA MUSTERMANN 12345": "Edeka",
        "Dioezese Musterstadt (KdoR)": "Dioezese Musterstadt",
        "Becker & Söhne GmbH & Co. KG": "Becker & Söhne",
        "VISA E-CENTER MUSTERMANN": "E-Center Mustermann",
        "Kleingeld Plus - Sparen": "Kleingeld Plus",
        "ANTHROPIC* CLAUDE SUB": "Claude",
        "Netflix International B.V.": "Netflix",
    }
    for raw, name in cases.items():
        assert names.clean(raw) == name, raw
    paypal = {"counterparty": PAYPAL, "purpose": "1234/PP.1329.PP/. Spotify AB, Ihr Einkauf bei Spotify AB"}
    assert names.display_name(paypal) == "Spotify"
    assert names.display_name({"counterparty": PAYPAL, "purpose": "XXX"}) == "PayPal"
    assert names.display_name({"counterparty": "", "purpose": "XXX", "booking_text": "Wertpapierkauf"}) == "Wertpapierkauf"
    assert names.display_name({"counterparty": None, "purpose": "Zinsen", "booking_text": "Gutschrift"}) == "Zinsen"


def test_readable_second_line():
    def detail(purpose, counterparty="Muster Shop"):
        return names.display_detail({"counterparty": counterparty, "purpose": purpose})

    # The bank sync joins the lines of a card payment without spaces.
    assert detail("NR XXXX 1234 MUSTERSTADT DEKAUFUMSATZ02.10 5,80123456ARN74000000000000000000001Google Pay") == (
        "Musterstadt · Google Pay"
    )
    assert detail("NR XXXX 1234 AMSTERDAM NL KAUFUMSATZ 03.10 12,00 123456 ARN7400000000001 Apple Pay") == (
        "Amsterdam, NL · Apple Pay"
    )
    assert detail("NR XXXX 1234 SHOP.EXAMPLE US KAUFUMSATZ 04.10 20,00 123456 ARN7400000000002") == "US"
    sepa = "EREF+RE-2026-0001 MREF+M-0001 CRED+DE98ZZZ09999999999 SVWZ+Abschlag Strom 10/2026"
    assert detail(sepa, "Stadtwerke Musterstadt") == "Abschlag Strom 10/2026"
    assert detail("Muster Shop") == "" and detail("") == "" and detail("VISA Debitkartenumsatz vom 05.10.2026") == ""


# --- CSV files without their header lines ----------------------------------------------


def test_csv_without_header_lines_takes_iban_from_the_file_name_and_balance_from_the_rows():
    parsed = csv_import.parse(_csv(ROWS), f"Umsatzanzeige_{IBAN}_20261007.csv")
    assert parsed["iban"] == IBAN and parsed["balance"] == 1859.17 and parsed["holder"] is None
    assert len(parsed["rows"]) == 4
    oldest_first = csv_import.parse(_csv(ROWS[::-1]), "export.csv")
    assert oldest_first["iban"] is None and oldest_first["balance"] == 1859.17
    wrong_sum = IBAN[:-1] + "1"
    assert csv_import.parse(_csv(ROWS), f"Umsatzanzeige_{wrong_sum}_20261007.csv")["iban"] is None


def test_csv_import_finds_its_account_and_keeps_the_newer_balance(run_job):
    name = f"Umsatzanzeige_{IBAN}_20261007.csv"
    job = jobs.run_inline("import", sync.import_csv, _csv(ROWS), None, name)
    assert job.state == "done", job.error
    with db.session() as conn:
        [acc] = db.rows(conn.execute("SELECT id, kind, iban, balance, balance_date FROM accounts"))
    assert (acc["kind"], acc["iban"], acc["balance"]) == ("checking", IBAN, 1859.17)
    # An older export of the same account: its bookings join the same account, the balance stays.
    older = [("01.09.2026", "VISA SHOP MUSTERSTADT", "Lastschrift", "999,00", "-1,00")]
    job = jobs.run_inline("import", sync.import_csv, _csv(older), None, "Umsatzanzeige_older.csv")
    assert job.state == "done", job.error
    with db.session() as conn:
        accounts = db.rows(conn.execute("SELECT id, balance FROM accounts"))
        count = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    assert accounts == [{"id": acc["id"], "balance": 1859.17}] and count == 5
