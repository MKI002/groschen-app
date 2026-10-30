from groschen.bank import store


def test_identical_rows_get_distinct_fingerprints():
    tx = {"date": "2026-09-01", "amount": -2.5, "counterparty": "Kiosk", "purpose": "Kaffee"}
    a, b = store.fingerprints(1, [tx, dict(tx)])
    assert a != b
    assert store.fingerprints(1, [tx]) == [a]


def test_reimport_adds_nothing(conn):
    acc = store.upsert_account(conn, None, {"kind": "checking", "iban": "DE001", "account_number": "1"})
    rows = [{"date": "2026-09-01", "amount": -2.5, "counterparty": "Kiosk", "purpose": "Kaffee"}] * 2
    assert len(store.insert_transactions(conn, acc, rows, "csv")) == 2
    assert store.insert_transactions(conn, acc, rows, "csv") == []


def test_csv_rows_after_first_bank_sync_are_skipped(conn):
    acc = store.upsert_account(conn, None, {"kind": "checking", "iban": "DE001", "account_number": "1"})
    store.insert_transactions(
        conn, acc, [{"date": "2026-07-01", "amount": -9.99, "counterparty": "Spotify AB", "purpose": "Premium"}], "fints"
    )
    rows = [
        {"date": "2026-06-01", "amount": -9.99, "counterparty": "Spotify AB", "purpose": "Spotify Premium"},
        {"date": "2026-07-01", "amount": -9.99, "counterparty": "SPOTIFY AB", "purpose": "Spotify P."},
        {"date": "2026-08-01", "amount": -9.99, "counterparty": "Spotify AB", "purpose": "Premium"},
    ]
    keep, skipped = store.filter_csv_overlap(conn, acc, rows)
    assert [r["date"] for r in keep] == ["2026-06-01"]
    assert skipped == 2


def test_bank_rows_already_imported_from_csv_are_skipped(conn):
    acc = store.upsert_account(conn, None, {"kind": "checking", "iban": "DE001", "account_number": "1"})
    csv = [
        {"date": "2026-09-01", "amount": -2.5, "counterparty": "Kiosk am Markt", "purpose": "Kaffee"},
        {"date": "2026-09-02", "amount": -54.99, "counterparty": "VISA REWE SAGT DANKE", "purpose": "Karte 1234"},
        {"date": "2026-09-03", "amount": 2500.0, "counterparty": "Arbeitgeber GmbH", "purpose": "Gehalt September"},
        {"date": "2026-09-04", "amount": -3.2, "counterparty": None, "purpose": "Kontofuehrung"},
    ]
    store.insert_transactions(conn, acc, csv, "csv")
    bank = [
        # The same bookings, worded the way the bank sends them.
        {"date": "2026-09-01", "amount": -2.5, "counterparty": "KIOSK AM MARKT", "purpose": "SVWZ+Kaffee EREF+1"},
        {"date": "2026-09-01", "amount": -2.5, "counterparty": "KIOSK AM MARKT", "purpose": "SVWZ+Kaffee EREF+2"},
        {"date": "2026-09-02", "amount": -54.99, "counterparty": "REWE Markt GmbH", "purpose": "Kartenzahlung"},
        {"date": "2026-09-03", "amount": 2500.0, "counterparty": "ARBEITGEBER GMBH", "purpose": "Lohn/Gehalt 09"},
        {"date": "2026-09-04", "amount": -3.2, "counterparty": "ING", "purpose": "Entgelt"},
        # Genuinely new ones.
        {"date": "2026-09-05", "amount": -12.0, "counterparty": "Kino", "purpose": "Tickets"},
    ]
    new = store.insert_transactions(conn, acc, bank, "fints")
    assert len(new) == 2  # the second coffee and the cinema
    assert store.insert_transactions(conn, acc, bank, "fints") == []
    total = conn.execute("SELECT COUNT(*) FROM transactions WHERE account_id = ?", (acc,)).fetchone()[0]
    assert total == 6


def test_bank_spelling_without_umlauts_still_matches(conn):
    acc = store.upsert_account(conn, None, {"kind": "checking", "iban": "DE001", "account_number": "1"})
    csv = [{"date": "2026-09-01", "amount": -5.0, "counterparty": "Bäckerei Müller"}]
    store.insert_transactions(conn, acc, csv, "csv")
    bank = [
        {"date": "2026-09-01", "amount": -5.0, "counterparty": "BAECKEREI MUELLER"},
        {"date": "2026-09-01", "amount": -5.0, "counterparty": "Parkhaus"},
    ]
    assert len(store.insert_transactions(conn, acc, bank, "fints")) == 1  # only the car park is new


def test_unclear_matches_keep_the_bank_row(conn):
    # Two bank rows could stand for the one CSV row and neither name fits: keeping both risks a
    # duplicate, dropping one could hide a real payment, so both stay.
    acc = store.upsert_account(conn, None, {"kind": "checking", "iban": "DE001", "account_number": "1"})
    store.insert_transactions(conn, acc, [{"date": "2026-09-01", "amount": -5.0, "counterparty": "Kiosk"}], "csv")
    bank = [
        {"date": "2026-09-01", "amount": -5.0, "counterparty": "Parkhaus"},
        {"date": "2026-09-01", "amount": -5.0, "counterparty": "Tankstelle"},
    ]
    assert len(store.insert_transactions(conn, acc, bank, "fints")) == 2
