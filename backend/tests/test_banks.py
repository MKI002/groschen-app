"""Banks other than ING: finding them, their CSV exports, TANs."""

# The sample files keep the banks' real line lengths.
# ruff: noqa: E501

import pytest

from groschen import demo, jobs
from groschen.bank import banks, csv_import, fints_client, sync
from groschen.jobs import UserFacingError

# Made-up accounts with correct check numbers.
SPK = demo.iban("1234567", "37050198")
VR = demo.iban("7654321", "70090500")
DKB = demo.iban("1020304050", "12030000")
DB = demo.iban("9876543", "10070000")
CB = demo.iban("1122334", "10040000")
N26 = demo.iban("100200300", "10011001")
OTHER = demo.iban("5556667", "70150000")


def _bytes(text: str, enc: str = "utf-8") -> bytes:
    return text.strip("\n").encode(enc)


# --- finding the bank -----------------------------------------------------------------


def test_a_bank_is_found_by_iban_bankleitzahl_or_name(conn):
    assert banks.search(conn, DKB)[0]["id"] == "dkb"
    assert banks.search(conn, "12030000")[0]["server"].startswith("https://banking-dkb.")
    assert banks.search(conn, "1203 0000")[0]["id"] == "dkb"
    found = banks.search(conn, "comdirect")
    # Several Bankleitzahlen: the user's own comes from the IBAN.
    assert found[0]["id"] == "comdirect" and found[0]["needs_blz"]
    assert not banks.search(conn, "DKB")[0]["needs_blz"]
    assert banks.search(conn, "Sparda")[0]["id"] == "vr"
    assert banks.search(conn, "n26")[0]["id"] == "csv-only"
    assert {b["id"] for b in banks.search(conn, "")} >= {"ing", "sparkasse", "vr", "deutsche-bank", "dkb"}


def test_bank_groups_come_from_the_fourth_digit(conn):
    vr = banks.resolve(conn, "70090500")
    assert vr["id"] == "vr" and vr["server"] == banks.ATRUVIA and vr["app"] == "VR SecureGo plus"
    assert banks.resolve(conn, "50070010")["id"] == "deutsche-bank"
    assert banks.resolve(conn, "10080000")["id"] == "commerzbank"
    # comdirect has a Commerzbank-like number but its own server.
    assert banks.resolve(conn, "20041133")["server"] == "https://fints.comdirect.de/fints"
    spk = banks.resolve(conn, "37050198")
    assert spk["id"] == "sparkasse" and spk["needs_server"]
    with pytest.raises(UserFacingError):
        banks.resolve(conn, "1234")


def test_a_sparkasse_gets_its_address_from_the_institute_list_or_by_hand(conn):
    listing = (
        "Nr.;BLZ;BIC;Institut;Ort;RZ;Organisation;PIN/TAN-Zugang URL;Version\n"
        "1;37050198;COLSDE33XXX;Sparkasse KölnBonn;Köln;FI;DSGV;https://banking-rl1.s-fints-pt-rl.de/fints30;FinTS V3.0\n"
        "2;99999999;XXXXDEXX;Bank ohne PIN/TAN;Irgendwo;;;;\n"
        "3;80020086;XXXXDEXX;Bank mit kaputter Adresse;Irgendwo;;;http://192.168.1.1/;FinTS V3.0\n"
    ).encode("cp1252")
    assert banks.import_directory(conn, listing) == {"banks": 3, "with_fints": 1}
    spk = banks.resolve(conn, "37050198")
    assert spk["name"] == "Sparkasse KölnBonn" and spk["server"].endswith("/fints30") and not spk["needs_server"]
    assert banks.search(conn, "kölnbonn")[0]["blz"] == "37050198"
    assert banks.resolve(conn, "80020086")["server"] is None
    typed = banks.resolve(conn, "80020086", "https://fints.example-bank.de/fints")
    assert typed["server"] == "https://fints.example-bank.de/fints"
    with pytest.raises(UserFacingError):
        banks.import_directory(conn, b"name;amount\nfoo;1\n")


@pytest.mark.parametrize(
    "url",
    [
        "http://fints.example.de/",
        "https://192.168.1.10/fints",
        "https://localhost/",
        "https://bank.local/x",
        "https://user:pw@fints.example.de/",
        "https://fints.example.de:8443/",
        "ftp://fints.example.de/",
    ],
)
def test_only_https_addresses_of_internet_hosts_are_accepted(url):
    with pytest.raises(UserFacingError):
        banks.check_server(url)


def test_connecting_another_bank_saves_its_server_and_allows_only_that_host(conn, demo_data, monkeypatch):
    from groschen import netguard

    allowed = set()
    monkeypatch.setattr(netguard, "allow_host", lambda h: allowed.add(h))
    monkeypatch.setattr(netguard, "disallow_host", lambda h: allowed.discard(h))
    monkeypatch.setattr(sync, "session_factory", demo.FakeBank(demo_data))
    job = jobs.run_inline("t", sync.test_connection, "12030000", "alex", demo.DEMO_PIN, "PRODUCT1")
    assert job.state == "done", job.error
    row = conn.execute("SELECT bank_name, server FROM connections").fetchone()
    assert row["bank_name"] == "DKB Deutsche Kreditbank" and "dkb" in row["server"]
    assert allowed == {"banking-dkb.s-fints-pt-dkb.de"}
    # A failed test at a bank without a saved connection takes its host off the list again.
    bad = jobs.run_inline("t", sync.test_connection, "20041111", "alex", "wrong", "PRODUCT1")
    assert bad.state == "error" and allowed == {"banking-dkb.s-fints-pt-dkb.de"}
    # A Sparkasse without a known address says what is missing.
    spk = jobs.run_inline("t", sync.test_connection, "37050198", "alex", demo.DEMO_PIN, "PRODUCT1")
    assert spk.state == "error" and "FinTS address" in spk.error


# --- TANs -----------------------------------------------------------------------------


class _Method:
    def __init__(self, name, decoupled=False, description_required="0"):
        self.name = name
        self.tan_process = "2"
        self.decoupled_max_poll_number = 60 if decoupled else None
        self.description_required = description_required


class _Medium:
    tan_medium_name = "Alex Handy"


class _Client:
    def __init__(self, methods):
        self.methods = methods
        self.current = next(iter(methods))
        self.medium = None

    def get_tan_mechanisms(self):
        return self.methods

    def get_current_tan_mechanism(self):
        return self.current

    def set_tan_mechanism(self, key):
        self.current = key

    def get_tan_media(self):
        return None, [_Medium()]

    def set_tan_medium(self, medium):
        self.medium = medium.tan_medium_name


def _session(client):
    s = fints_client.FinTSSession.__new__(fints_client.FinTSSession)
    s.client = client
    s.info = {"id": "sparkasse", "short": "Spk", "name": "Sparkasse"}
    return s


def test_app_approval_is_preferred_over_typed_tans():
    client = _Client(
        {
            "912": _Method("chipTAN optisch"),
            "921": _Method("pushTAN 2.0", decoupled=True, description_required="2"),
            "999": _Method("Einschritt"),
        }
    )
    _session(client)._prefer_app()
    assert client.current == "921" and client.medium == "Alex Handy"
    by_name = _Client({"942": _Method("mobileTAN"), "946": _Method("SecureGo plus")})
    _session(by_name)._prefer_app()
    assert by_name.current == "946"


def test_a_typed_tan_waits_for_the_web_page(monkeypatch):
    job = jobs.Job(id="t", kind="sync", interactive=True)
    seen = {}

    def answer():
        import time

        while job.tan is None:
            time.sleep(0.01)
        seen["tan"] = job.as_dict()["tan"]
        assert job.as_dict()["state"] == "waiting"
        job.give_tan("123456")

    import threading

    threading.Thread(target=answer).start()
    assert job.ask_tan({"text": "Bitte TAN eingeben", "image": None}, timeout=5) == "123456"
    assert seen["tan"]["text"] == "Bitte TAN eingeben" and job.tan is None and job.state == "running"
    # A sync at night has nobody to ask.
    assert jobs.Job(id="n", kind="sync").ask_tan({"text": "x"}) is None
    assert not job.give_tan("1")


# --- CSV exports ----------------------------------------------------------------------


def test_sparkasse_camt():
    raw = _bytes(
        f'''
"Auftragskonto";"Buchungstag";"Valutadatum";"Buchungstext";"Verwendungszweck";"Glaeubiger ID";"Mandatsreferenz";"Kundenreferenz (End-to-End)";"Sammlerreferenz";"Lastschrift Ursprungsbetrag";"Auslagenersatz Ruecklastschrift";"Beguenstigter/Zahlungspflichtiger";"Kontonummer/IBAN";"BIC (SWIFT-Code)";"Betrag";"Waehrung";"Info"
"{SPK}";"30.10.26";"30.10.26";"FOLGELASTSCHRIFT";"Abschlag Strom 10/2026";"DE98ZZZ09999999999";"M-1";"";"";"";"";"Stadtwerke Musterstadt";"{OTHER}";"XXXXDEXX";"-45,00";"EUR";"Umsatz gebucht"
"{SPK}";"29.10.26";"29.10.26";"GUTSCHR. UEBERWEISUNG";"Gehalt Oktober";"";"";"";"";"";"";"Beispiel GmbH";"{OTHER}";"XXXXDEXX";"2.500,00";"EUR";"Umsatz gebucht"
''',
        "cp1252",
    )
    p = csv_import.parse(raw)
    assert p["iban"] == SPK
    first, second = p["rows"]
    assert first["date"] == "2026-10-30" and first["amount"] == -45.0 and first["counterparty"] == "Stadtwerke Musterstadt"
    assert first["purpose"] == "Abschlag Strom 10/2026" and first["booking_text"] == "FOLGELASTSCHRIFT"
    assert first["counterparty_iban"] == OTHER and second["amount"] == 2500.0


def test_volksbank():
    raw = _bytes(
        f"""
Bezeichnung Auftragskonto;IBAN Auftragskonto;BIC Auftragskonto;Bankname Auftragskonto;Buchungstag;Valutadatum;Name Zahlungsbeteiligter;IBAN Zahlungsbeteiligter;BIC (SWIFT-Code) Zahlungsbeteiligter;Buchungstext;Verwendungszweck;Betrag;Waehrung;Saldo nach Buchung;Bemerkung;Kategorie;Steuerrelevant;Glaeubiger ID;Mandatsreferenz
Girokonto;{VR};GENODEF1XXX;Volksbank Musterstadt eG;31.10.2026;31.10.2026;Bäckerei Korn;;;Kartenzahlung;Brötchen;-4,20;EUR;1.234,56;;;;;
Girokonto;{VR};GENODEF1XXX;Volksbank Musterstadt eG;30.10.2026;30.10.2026;Beispiel GmbH;{OTHER};XXXXDEXX;Gehalt/Rente;Gehalt;2.000,00;EUR;1.238,76;;;;;
"""
    )
    p = csv_import.parse(raw)
    assert p["iban"] == VR and p["account_name"] == "Girokonto" and p["balance"] == 1234.56
    assert [r["amount"] for r in p["rows"]] == [-4.2, 2000.0]
    assert p["rows"][0]["counterparty"] == "Bäckerei Korn"


def test_dkb_new_export_skips_pending_and_names_the_other_side():
    raw = _bytes(
        f'''
"Konto";"Girokonto {DKB}"
""
"Kontostand vom 31.10.2026:";"2.345,67 €"
""
"Buchungsdatum";"Wertstellung";"Status";"Zahlungspflichtige*r";"Zahlungsempfänger*in";"Verwendungszweck";"Umsatztyp";"IBAN";"Betrag (€)";"Gläubiger-ID";"Mandatsreferenz";"Kundenreferenz"
"31.10.26";"31.10.26";"Vorgemerkt";"Alex Beispiel";"Kino Metropol";"Tickets";"Ausgang";"";"-24";"";"";""
"30.10.26";"30.10.26";"Gebucht";"Alex Beispiel";"Stadtwerke Musterstadt";"Abschlag";"Ausgang";"{OTHER}";"-45";"";"";""
"29.10.26";"29.10.26";"Gebucht";"Beispiel GmbH";"Alex Beispiel";"Gehalt";"Eingang";"{OTHER}";"2.500";"";"";""
'''
    )
    p = csv_import.parse(raw)
    assert p["iban"] == DKB and p["account_name"] == "Girokonto" and p["balance"] == 2345.67
    assert [(r["counterparty"], r["amount"]) for r in p["rows"]] == [
        ("Stadtwerke Musterstadt", -45.0),
        ("Beispiel GmbH", 2500.0),
    ]


def test_comdirect_splits_the_one_text_column():
    raw = _bytes(
        f"""
;
"Umsätze Girokonto";"Zeitraum: 30 Tage";
"Neuer Kontostand";"1.234,56 EUR";

"Buchungstag";"Wertstellung (Valuta)";"Vorgang";"Buchungstext";"Umsatz in EUR";
"offen";"--";"Lastschrift / Belastung";"Empfänger: Kino Metropol Buchungstext: Tickets";"-24,00";
"30.10.2026";"30.10.2026";"Lastschrift / Belastung";"Empfänger: Stadtwerke Musterstadt Kto/IBAN: {OTHER} BLZ/BIC: XXXXDEXX Buchungstext: Abschlag Strom Ref. 1A2B";"-45,00";
"29.10.2026";"29.10.2026";"Übertrag / Überweisung";"Auftraggeber: Beispiel GmbH Buchungstext: Gehalt Oktober Ref. 3C4D";"2.500,00";
""",
        "cp1252",
    )
    p = csv_import.parse(raw)
    assert p["balance"] == 1234.56 and p["account_name"] == "Girokonto"
    assert len(p["rows"]) == 2
    first = p["rows"][0]
    assert first["counterparty"] == "Stadtwerke Musterstadt" and first["purpose"] == "Abschlag Strom"
    assert first["booking_text"] == "Lastschrift / Belastung"
    assert p["rows"][1]["counterparty"] == "Beispiel GmbH"


def test_deutsche_bank_debit_and_credit_columns_and_closing_balance():
    raw = _bytes(
        f"""
Umsätze Girokonto;Kundennummer: 100 9876543
01.10.2026 - 31.10.2026
Buchungstag;Wert;Umsatzart;Begünstigter / Auftraggeber;Verwendungszweck;IBAN;BIC;Kundenreferenz;Mandatsreferenz ;Gläubiger ID;Fremde Gebühren;Betrag;Abweichender Empfänger;Anzahl der Aufträge;Anzahl der Schecks;Soll;Haben;Währung
30.10.2026;30.10.2026;SEPA-Lastschrift;Stadtwerke Musterstadt;Abschlag;{OTHER};XXXXDEXX;;;;;;;;;-45,00;;EUR
29.10.2026;29.10.2026;SEPA-Überweisung;Beispiel GmbH;Gehalt;{OTHER};XXXXDEXX;;;;;;;;;;2.500,00;EUR
Kontostand;31.10.2026;;;3.210,00;EUR
""",
        "cp1252",
    )
    p = csv_import.parse(raw)
    assert [r["amount"] for r in p["rows"]] == [-45.0, 2500.0]
    assert p["balance"] == 3210.0 and p["rows"][0]["booking_text"] == "SEPA-Lastschrift"


def test_commerzbank_and_n26():
    cb = csv_import.parse(
        _bytes(
            f"""
Buchungstag;Wertstellung;Umsatzart;Buchungstext;Betrag;Währung;IBAN Kontoinhaber;Kategorie
30.10.2026;30.10.2026;Lastschrift;Stadtwerke Musterstadt Abschlag Strom;-45,00;EUR;{CB};Wohnen
"""
        )
    )
    assert cb["iban"] == CB and cb["rows"][0]["purpose"] == "Stadtwerke Musterstadt Abschlag Strom"
    assert cb["rows"][0]["booking_text"] == "Lastschrift"
    n26 = csv_import.parse(
        _bytes(
            f"""
"Booking Date","Value Date","Partner Name","Partner Iban",Type,"Payment Reference","Account Name","Amount (EUR)","Original Amount","Original Currency","Exchange Rate"
2026-10-30,2026-10-30,"Stadtwerke Musterstadt",{OTHER},Direct Debit,"Abschlag","Main Account",-45.00,,,
2026-10-29,2026-10-29,"Beispiel GmbH",{OTHER},Income,"Gehalt","Main Account",2500.00,,,
"""
        )
    )
    assert [(r["date"], r["amount"]) for r in n26["rows"]] == [("2026-10-30", -45.0), ("2026-10-29", 2500.0)]
    assert n26["rows"][0]["counterparty"] == "Stadtwerke Musterstadt" and n26["account_name"] == "Main Account"


def test_amounts_in_any_format():
    assert csv_import.parse_amount("1.234,56 €") == 1234.56
    assert csv_import.parse_amount("-1,234.56") == -1234.56
    assert csv_import.parse_amount("12,30-") == -12.3
    assert csv_import.parse_amount("+2.500") == 2500.0
    assert csv_import.parse_amount("-45.00") == -45.0


def test_a_new_account_from_another_bank_keeps_its_bankleitzahl(conn, demo_data):
    raw = _bytes(
        f"""
Bezeichnung Auftragskonto;IBAN Auftragskonto;Buchungstag;Valutadatum;Name Zahlungsbeteiligter;Buchungstext;Verwendungszweck;Betrag;Waehrung;Saldo nach Buchung
Tagesgeld;{VR};30.10.2026;30.10.2026;Volksbank;Abschluss;Zinsen;3,10;EUR;5.003,10
"""
    )
    job = jobs.run_inline("import", sync.import_csv, raw, None, "export.csv")
    assert job.state == "done", job.error
    acc = conn.execute("SELECT kind, name, blz, balance FROM accounts WHERE iban = ?", (VR,)).fetchone()
    assert dict(acc) == {"kind": "savings", "name": "Tagesgeld", "blz": "70090500", "balance": 5003.1}
