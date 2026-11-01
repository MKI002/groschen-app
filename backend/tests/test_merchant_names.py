"""One merchant spelled two ways by the bank ("AquaNetworks", "Aqua Networks") is one merchant."""

from test_categorize import _account, _add

from groschen import settings
from groschen.analytics import drilldown
from groschen.categorize import engine, names

PAYPAL = "PayPal Europe S.a.r.l. et Cie S.C.A"


def test_spaces_and_case_do_not_split_a_merchant():
    a = {"counterparty": "AquaNetworks", "purpose": ""}
    b = {"counterparty": "Aqua Networks Limited", "purpose": ""}
    c = {"counterparty": PAYPAL, "purpose": "1/PP. Ihr Einkauf bei Aqua Networks Limited"}
    assert engine.merchant_key(a) == "AQUANETWORKS"
    assert engine.merchant_key(b) == engine.merchant_key(c) == "AQUANETWORKSLIMITED"
    assert names.name_key("AquaNetworks") == names.name_key("Aqua Networks") == names.name_key("AQUA-NETWORKS")
    assert names.name_key("Café Müller") == names.name_key("cafe muller")
    assert names.name_key("Rewe") != names.name_key("Rossmann")


def test_merchant_page_counts_every_spelling(conn):
    acc = _account(conn)
    for date in ("2026-06-29", "2026-07-28", "2026-08-27"):
        _add(conn, acc, date, -9.99, "Aqua Networks")
    for date in ("2026-09-29", "2026-10-27"):
        _add(conn, acc, date, -5.51, "AquaNetworks")
    engine.categorize(conn)
    for asked in ("AquaNetworks", "Aqua Networks"):
        page = drilldown.build(conn, start="2026-01-01", end="2026-12-31", label="2026", merchant=asked)
        assert len(page["items"]) == 5
        assert page["summary"]["total"] == round(3 * 9.99 + 2 * 5.51, 2)
        assert page["scope"]["name"] == "AquaNetworks"  # the latest spelling
        assert [m["name"] for m in page["merchants"]] == ["AquaNetworks"]


def test_saved_keys_with_spaces_are_carried_over(conn):
    acc = _account(conn)
    tx = _add(conn, acc, "2026-09-01", -9.99, "Aqua Networks")
    _add(conn, acc, "2026-10-01", -9.99, "AquaNetworks")
    gaming = conn.execute("SELECT id FROM categories WHERE name = 'Gaming'").fetchone()[0]
    streaming = conn.execute("SELECT id FROM categories WHERE name = 'Streaming'").fetchone()[0]
    conn.executemany(
        "INSERT INTO merchant_memory (key, category_id, hits, updated_at) VALUES (?, ?, ?, ?)",
        [("AQUA NETWORKS", gaming, 2, "2026-09-02"), ("AQUANETWORKS", streaming, 1, "2026-10-02")],
    )
    conn.execute("INSERT INTO subscription_marks (key, state, updated_at) VALUES ('AQUA NETWORKS', 'yes', '2026-09-02')")
    conn.execute("INSERT INTO saving_dest_cp (key, dest, created_at) VALUES ('name:MAX SPAR', 'etf', '2026-09-02')")
    conn.execute("INSERT INTO refund_rejects (refund_id, key, created_at) VALUES (?, 'AQUA NETWORKS', '2026-09-02')", (tx,))
    conn.execute("INSERT INTO dismissed_alerts (key, dismissed_at) VALUES ('sub:new:AQUA NETWORKS', '2026-09-02')")
    conn.execute("INSERT INTO dismissed_alerts (key, dismissed_at) VALUES ('dup:1:2', '2026-09-02')")
    settings.put(conn, "payday_overrides", {"ACME GMBH LOHN": "next"})

    engine.migrate_merchant_keys(conn)

    memory = [tuple(r) for r in conn.execute("SELECT key, category_id, hits FROM merchant_memory")]
    assert memory == [("AQUANETWORKS", streaming, 3)]  # the newer answer, hits added up
    assert [tuple(r) for r in conn.execute("SELECT key, state FROM subscription_marks")] == [("AQUANETWORKS", "yes")]
    assert [r[0] for r in conn.execute("SELECT key FROM saving_dest_cp")] == ["name:MAXSPAR"]
    assert [r[0] for r in conn.execute("SELECT key FROM refund_rejects")] == ["AQUANETWORKS"]
    assert {r[0] for r in conn.execute("SELECT key FROM dismissed_alerts")} == {"sub:new:AQUANETWORKS", "dup:1:2"}
    assert settings.get(conn, "payday_overrides") == {"ACMEGMBHLOHN": "next"}

    engine.migrate_merchant_keys(conn)  # running twice changes nothing
    assert [tuple(r) for r in conn.execute("SELECT key, category_id, hits FROM merchant_memory")] == memory
