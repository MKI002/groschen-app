from groschen import db
from groschen.bank import store
from groschen.categorize import engine


def _account(conn, name="Girokonto", iban="DE00500105170000000001", kind="checking"):
    return store.upsert_account(
        conn, None, {"kind": kind, "name": name, "iban": iban, "account_number": iban[-10:], "blz": "50010517"}
    )


def _add(conn, account_id, date, amount, counterparty, purpose="", booking_text="Lastschrift", cp_iban=None):
    ids = store.insert_transactions(
        conn,
        account_id,
        [
            {
                "date": date,
                "amount": amount,
                "counterparty": counterparty,
                "purpose": purpose,
                "booking_text": booking_text,
                "counterparty_iban": cp_iban,
            }
        ],
        "csv",
    )
    return ids[0]


def _category(conn, tx_id):
    return conn.execute(
        "SELECT c.name FROM transactions t LEFT JOIN categories c ON c.id = t.category_id WHERE t.id = ?", (tx_id,)
    ).fetchone()[0]


def test_known_merchants(conn):
    acc = _account(conn)
    cases = {
        _add(conn, acc, "2026-09-01", -54.20, "REWE SAGT DANKE. 44667788"): "Groceries",
        _add(conn, acc, "2026-09-02", -15.99, "Netflix International B.V."): "Streaming",
        _add(conn, acc, "2026-09-03", -63.10, "ARAL Station 1234"): "Fuel",
        _add(conn, acc, "2026-09-04", 3340.0, "Arbeitgeber GmbH", "LOHN/GEHALT 09/2026", "Gehalt/Rente"): "Salary",
        _add(
            conn, acc, "2026-09-05", -250.0, "ING-DiBa AG", "Sparplan IE00BK5BQT80 Vanguard", "Wertpapierkauf"
        ): "Investments",
    }
    engine.categorize(conn)
    for tx_id, expected in cases.items():
        assert _category(conn, tx_id) == expected


def test_refund_is_not_salary(conn):
    acc = _account(conn)
    tx = _add(conn, acc, "2026-09-01", 20.0, "REWE Markt GmbH", "Erstattung Pfand")
    engine.categorize(conn)
    assert _category(conn, tx) != "Salary"


def test_own_transfers_are_paired_without_iban(conn):
    giro = _account(conn)
    extra = _account(conn, "Extra-Konto", "DE00500105170000000002", "savings")
    out = _add(conn, giro, "2026-09-01", -800.0, "Alex Beispiel", "Sparen", "Ueberweisung")
    into = _add(conn, extra, "2026-09-02", 800.0, "Alex Beispiel", "Sparen", "Gutschrift")
    engine.categorize(conn)
    assert _category(conn, out) == "Savings"
    assert _category(conn, into) == "Savings"


def test_transfer_between_checking_accounts_stays_own_transfer(conn):
    giro = _account(conn)
    other = _account(conn, "Zweites Girokonto", "DE00500105170000000003")
    out = _add(conn, giro, "2026-09-01", -120.0, "Alex Beispiel", "Umbuchung", "Ueberweisung")
    into = _add(conn, other, "2026-09-01", 120.0, "Alex Beispiel", "Umbuchung", "Gutschrift")
    engine.categorize(conn)
    assert _category(conn, out) == "Own transfers"
    assert _category(conn, into) == "Own transfers"


def test_kleingeld_plus_is_saving(conn):
    giro = _account(conn)
    extra = _account(conn, "Extra-Konto", "DE00500105170000000002", "savings")
    alone = _add(conn, giro, "2026-09-01", -3.42, "ING", "Kleingeld Plus - Sparen", "Ueberweisung")
    out = _add(conn, giro, "2026-09-02", -1.87, "ING", "Kleingeld Plus - Sparen", "Ueberweisung")
    into = _add(conn, extra, "2026-09-02", 1.87, "ING", "Kleingeld Plus - Sparen", "Gutschrift")
    invest = _add(conn, giro, "2026-09-03", -2.10, "ING", "Kleingeld-Plus Investieren ETF", "Ueberweisung")
    engine.categorize(conn)
    assert _category(conn, alone) == "Savings"
    assert _category(conn, out) == "Savings"
    assert _category(conn, into) == "Savings"
    assert _category(conn, invest) == "Investments"


def test_interest_on_savings_is_still_income(conn):
    extra = _account(conn, "Extra-Konto", "DE00500105170000000002", "savings")
    tx = _add(conn, extra, "2026-09-30", 4.12, "", "Zinsen Tagesgeld", "Abschluss")
    engine.categorize(conn)
    assert _category(conn, tx) == "Interest & dividends"


def test_transfer_by_iban_uses_destination_account(conn):
    giro = _account(conn)
    _account(conn, "Extra-Konto", "DE00500105170000000002", "savings")
    _account(conn, "Depot", "DE00500105170000000009", "depot")
    save = _add(conn, giro, "2026-09-01", -50.0, "Alex Beispiel", "Umbuchung", cp_iban="DE00500105170000000002")
    inv = _add(conn, giro, "2026-09-01", -60.0, "Alex Beispiel", "Umbuchung", cp_iban="DE00500105170000000009")
    engine.categorize(conn)
    assert _category(conn, save) == "Savings"
    assert _category(conn, inv) == "Investments"


def test_existing_install_gets_savings_category(conn):
    from groschen.categorize import seed

    conn.execute("DELETE FROM categories WHERE name = 'Savings'")
    conn.execute("UPDATE categories SET grp = 'Transfers', color = 'slate' WHERE name = 'Investments'")
    giro = _account(conn)
    tx = _add(conn, giro, "2026-09-01", -3.42, "ING", "Kleingeld Plus - Sparen", "Ueberweisung")
    conn.commit()
    db.init()
    assert _category(conn, tx) == "Savings"
    cats = {r[0]: r[1] for r in conn.execute("SELECT name, grp FROM categories")}
    assert cats["Savings"] == cats["Investments"] == "Saving & investing"
    assert not seed.upgrade_categories(conn)


def test_correction_is_learned_and_never_overwritten(conn):
    acc = _account(conn)
    first = _add(conn, acc, "2026-08-01", -31.0, "Friseur Haarmonie", "Kartenzahlung")
    engine.categorize(conn)
    hobbies = conn.execute("SELECT id FROM categories WHERE name = 'Hobbies'").fetchone()[0]
    conn.execute("UPDATE transactions SET category_id = ?, cat_source = 'user' WHERE id = ?", (hobbies, first))
    tx = db.one(conn.execute("SELECT * FROM transactions WHERE id = ?", (first,)))
    engine.learn(conn, tx, hobbies)
    second = _add(conn, acc, "2026-09-01", -29.0, "Friseur Haarmonie", "Kartenzahlung")
    engine.categorize(conn, "1 = 1")
    assert _category(conn, second) == "Hobbies"
    assert conn.execute("SELECT cat_source FROM transactions WHERE id = ?", (first,)).fetchone()[0] == "user"


def test_rules_win(conn):
    acc = _account(conn)
    tx = _add(conn, acc, "2026-09-01", -54.20, "REWE Markt GmbH", "Betriebsfeier")
    gifts = conn.execute("SELECT id FROM categories WHERE name = 'Gifts & donations'").fetchone()[0]
    conn.execute(
        "INSERT INTO rules (field, op, value, category_id, created_at) VALUES ('purpose', 'contains', "
        "'betriebsfeier', ?, '')",
        (gifts,),
    )
    engine.categorize(conn)
    assert _category(conn, tx) == "Gifts & donations"


def test_unknown_text_goes_to_review(conn):
    acc = _account(conn)
    tx = _add(conn, acc, "2026-09-01", -17.0, "XQZ 99 Handelsges", "Ref 88123")
    engine.categorize(conn)
    assert conn.execute("SELECT needs_review FROM transactions WHERE id = ?", (tx,)).fetchone()[0] == 1


def test_merchant_key_reads_paypal_purpose():
    tx = {
        "counterparty": "PayPal Europe S.a.r.l. et Cie S.C.A",
        "purpose": "PP.1234.PP . Zalando SE, Ihr Einkauf bei Zalando SE",
    }
    assert engine.merchant_key(tx) == engine.merchant_key({"counterparty": "Zalando SE", "purpose": ""})


def test_groups_have_a_general_category(conn):
    rows = conn.execute("SELECT name, grp, kind FROM categories WHERE name = grp").fetchall()
    general = {r["name"]: r["kind"] for r in rows}
    assert general["Subscriptions"] == "expense"
    assert general["Income"] == "income"
    assert "Transfers" not in general and "Saving & investing" not in general
    first = conn.execute("SELECT name FROM categories WHERE grp = 'Subscriptions' ORDER BY sort LIMIT 1").fetchone()[0]
    assert first == "Subscriptions"


def test_existing_install_gets_general_categories(conn):
    conn.execute("DELETE FROM categories WHERE name = grp AND name != 'Insurance'")
    conn.commit()
    db.init()
    names = [r[0] for r in conn.execute("SELECT name FROM categories WHERE grp = 'Subscriptions' ORDER BY sort")]
    assert names == ["Subscriptions", "Streaming", "Software & cloud", "Fitness"]
    assert conn.execute("SELECT COUNT(*) FROM categories WHERE name = 'Insurance'").fetchone()[0] == 1
