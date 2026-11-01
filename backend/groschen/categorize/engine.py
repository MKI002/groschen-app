"""Transaction categorizer.

Order of decisions, strongest first:
1. the user's own choice (never overwritten)
2. the user's rules
3. transfers between the user's own accounts
4. merchants the user corrected before
5. money sent to the user's own name (an account elsewhere)
6. the built-in German merchant list
7. the built-in model, which compares the transaction text with example phrases
   and with every transaction the user has corrected

When the model is unsure, the transaction goes to "Needs review" instead of
getting a confident-looking wrong category. Afterwards two passes look at bookings
together: both sides of a transfer between the user's accounts, and money that came
back for an earlier payment (a shop's refund, a friend paying back), which is linked
to that payment and takes its category.
"""

import datetime as dt
import re
import threading
from dataclasses import dataclass

import numpy as np

from .. import db, settings
from . import embedder as emb
from . import names, vendors
from .seed import EXAMPLES, INVEST_WORDS, MERCHANTS, SAVE_WORDS

ISIN_RE = re.compile(r"\b[A-Z]{2}[A-Z0-9]{9}\d\b")
INVEST_RE = re.compile(INVEST_WORDS)
SAVE_RE = re.compile(SAVE_WORDS)
REFUND_DAYS = 90  # money back this long after a payment can belong to it
PART_DAYS = 60  # a part of the amount comes back sooner: a return, a friend's share
REGULAR_DAYS = 120  # a payee that sent similar amounts this often lately is paying, not paying back
SHARE_DAYS = 30  # a friend's share of a bill they didn't pay themselves comes back within this
SHARES = range(1, 7)  # money back can be a whole payment or its half, third ... sixth
# Categories of money moved rather than spent: nothing comes "back" for them.
NOT_PAYMENTS = {"Savings", "Investments", "Credit card payment"}
_COMPILED = [(re.compile(p), cat, sign) for p, cat, sign in MERCHANTS]
# Words in a name that don't tell people apart.
_NAME_FILLERS = {"DR", "PROF", "HERR", "FRAU", "DIPL", "ING", "MED", "UND", "JUN", "SEN"}
_STRIP_WORDS = {
    "GMBH",
    "AG",
    "SE",
    "KG",
    "CO",
    "OHG",
    "EK",
    "E",
    "K",
    "UG",
    "MBH",
    "SARL",
    "SA",
    "SCA",
    "BV",
    "LTD",
    "INC",
    "LLC",
    "FIL",
    "FILIALE",
    "SAGT",
    "DANKE",
    "MARKT",
    "NR",
    "DE",
    "DEU",
    "GER",
    "BERLIN",
    "MUENCHEN",
    "MÜNCHEN",
    "HAMBURG",
    "KOELN",
    "KÖLN",
    "FRANKFURT",
    "STUTTGART",
    "DUESSELDORF",
    "DÜSSELDORF",
    "ET",
    "CIE",
    "EU",
    "S",
    "A",
    "R",
    "L",
}


def transfer_category(account_kinds: set, text: str) -> str:
    """Which category money moved between the user's own accounts belongs in.

    Into or out of the depot (or a securities purchase) is investing, into or out of
    the Extra-Konto is saving, anything else is a plain own transfer.
    """
    if "depot" in account_kinds or ISIN_RE.search(text) or "WERTPAPIER" in text:
        return "Investments"
    if "savings" in account_kinds:
        return "Savings"
    return "Own transfers"


def own_transfer_category(text: str) -> str:
    """Where money sent to the user's own name went, by what the transfer says about it."""
    if ISIN_RE.search(text) or INVEST_RE.search(text):
        return "Investments"
    if SAVE_RE.search(text):
        return "Savings"
    return "Own transfers"


def name_tokens(name: str | None) -> frozenset[str]:
    """The words of a person's name, so "MUSTERMANN, MAX" and "Max Mustermann" compare equal.

    Umlauts and their spelled-out forms become plain vowels, since banks write "Müller",
    "Mueller" and "Muller" for the same person.
    """
    s = (name or "").upper().translate(str.maketrans("ÄÖÜ", "AOU"))
    s = s.replace("AE", "A").replace("OE", "O").replace("UE", "U")
    return frozenset(w for w in re.split(r"[^A-Z]+", s) if len(w) > 1 and w not in _NAME_FILLERS)


def is_own_name(counterparty: str | None, holders: list[frozenset[str]]) -> bool:
    """True when the payee is the account holder: all of their name, plus at most one more word."""
    cp = name_tokens(counterparty)
    return any(len(h) >= 2 and h <= cp and len(cp - h) <= 1 for h in holders)


@dataclass
class Guess:
    category_id: int | None
    source: str | None
    confidence: float
    needs_review: bool


def tx_text(tx: dict) -> str:
    parts = [tx.get("counterparty"), tx.get("purpose"), tx.get("booking_text")]
    text = " ".join(p.strip() for p in parts if p and p.strip())
    return re.sub(r"\s+", " ", text)[:240]


def _clean(s: str) -> str:
    s = s.upper().replace("Ä", "AE").replace("Ö", "OE").replace("Ü", "UE").replace("ß", "SS")
    s = re.sub(r"[^A-Z ]+", " ", s)
    words = [w for w in s.split() if w not in _STRIP_WORDS and len(w) > 1]
    return " ".join(words[:3])


def merchant_key(tx: dict) -> str:
    """A stable, normalized name for the merchant behind a transaction.

    Spaces don't count, so the same merchant spelled "AquaNetworks" and "Aqua Networks" by the
    bank is one merchant. Keys stored before that (with spaces) are rewritten once by
    migrate_merchant_keys.
    """
    return _spaced_key(tx).replace(" ", "")


def _spaced_key(tx: dict) -> str:
    cp = (tx.get("counterparty") or "").strip()
    purpose = (tx.get("purpose") or "").strip()
    if "PAYPAL" in cp.upper() or not cp:
        m = re.search(r"(?:Ihr Einkauf bei|Einkauf bei|purchase at)\s+([^,;]+)", purpose, re.IGNORECASE)
        if m:
            return _clean(m.group(1))
        if "PAYPAL" in cp.upper():
            return "PAYPAL " + _clean(re.sub(r"\d+", " ", purpose))[:40]
        return _clean(purpose)
    return _clean(cp)


def _norm_iban(iban: str | None) -> str:
    return (iban or "").replace(" ", "").upper()


class Categorizer:
    def __init__(self, conn):
        self.conn = conn
        cats = db.rows(conn.execute("SELECT id, name, grp, kind FROM categories"))
        self.by_name = {c["name"]: c for c in cats}
        self.by_id = {c["id"]: c for c in cats}
        self.rules = db.rows(conn.execute("SELECT field, op, value, category_id FROM rules ORDER BY id"))
        self.memory = {r["key"]: r["category_id"] for r in conn.execute("SELECT key, category_id FROM merchant_memory")}
        self.own_ibans = {
            _norm_iban(r["iban"]): r["kind"]
            for r in conn.execute("SELECT iban, kind FROM accounts WHERE iban IS NOT NULL AND iban != ''")
        }
        self.account_kinds = {r["id"]: r["kind"] for r in conn.execute("SELECT id, kind FROM accounts")}
        self.holders = [h for h in map(name_tokens, settings.get(conn, "holder_names") or []) if len(h) >= 2]
        self.mode = settings.get(conn, "categorizer")
        self.review_uncertain = bool(settings.get(conn, "review_uncertain"))

    def _cat(self, name: str) -> int | None:
        c = self.by_name.get(name)
        return c["id"] if c else None

    def _sign_ok(self, category_id: int, amount: float) -> bool:
        kind = self.by_id.get(category_id, {}).get("kind")
        if kind == "income":
            return amount > 0
        if kind == "expense":
            # Refunds land in expense categories too, so allow small positive amounts back.
            return True
        return True

    def rule_match(self, tx: dict) -> int | None:
        for r in self.rules:
            field = r["field"]
            if field == "counterparty":
                hay = tx.get("counterparty") or ""
            elif field == "purpose":
                hay = tx.get("purpose") or ""
            else:
                hay = tx_text(tx)
            hay, needle = hay.lower(), r["value"].lower().strip()
            if not needle:
                continue
            if (r["op"] == "equals" and hay.strip() == needle) or (r["op"] != "equals" and needle in hay):
                return r["category_id"]
        return None

    def quick(self, tx: dict) -> Guess | None:
        """Everything except the model. Returns None when the model should decide."""
        amount = float(tx.get("amount") or 0)
        cat = self.rule_match(tx)
        if cat:
            return Guess(cat, "rule", 1.0, False)

        upper = tx_text(tx).upper()
        cp_iban = _norm_iban(tx.get("counterparty_iban"))
        if cp_iban and cp_iban in self.own_ibans:
            kinds = {self.own_ibans[cp_iban], self.account_kinds.get(tx.get("account_id"))}
            name = transfer_category(kinds, upper)
            return Guess(self._cat(name) or self._cat("Own transfers"), "transfer", 1.0, False)

        key = merchant_key(tx)
        if key and key in self.memory and self._sign_ok(self.memory[key], amount):
            return Guess(self.memory[key], "memory", 0.95, False)

        # The ING export has no IBANs, so a transfer to the Extra-Konto (or to an account at another
        # bank) shows only the holder's own name.
        if self.holders and is_own_name(tx.get("counterparty"), self.holders):
            name = own_transfer_category(upper)
            return Guess(self._cat(name) or self._cat("Own transfers"), "own", 0.95, False)

        if ISIN_RE.search(upper) and amount < 0 and ("KAUF" in upper or "SPARPLAN" in upper or "WERTPAPIER" in upper):
            return Guess(self._cat("Investments"), "dict", 0.95, False)

        shop = names.PAYPAL_SHOP.search(tx.get("purpose") or "")
        known = vendors.match(upper, (tx.get("counterparty"), shop.group(1) if shop else None))
        if known and (amount < 0 or known[0] in ("Online shopping", "Clothing")):
            cat = self._cat(known[0])
            if cat:
                return Guess(cat, "dict", 0.9, False)

        for pattern, name, sign in _COMPILED:
            if sign == "+" and amount <= 0:
                continue
            if sign == "-" and amount >= 0 and name not in ("Online shopping", "Clothing"):
                continue
            if pattern.search(upper):
                cat = self._cat(name)
                if cat:
                    return Guess(cat, "dict", 0.9, False)
        return None

    # --- model -----------------------------------------------------------
    _cache_lock = threading.Lock()
    _example_cache: dict = {}

    def _examples(self):
        texts, cats = [], []
        for name, phrases in EXAMPLES.items():
            cid = self._cat(name)
            if cid:
                for p in phrases:
                    texts.append(p)
                    cats.append(cid)
        for r in self.conn.execute("SELECT text, category_id FROM examples ORDER BY id DESC LIMIT 3000"):
            texts.append(r["text"])
            cats.append(r["category_id"])
        return texts, np.array(cats)

    def _example_matrix(self, embedder):
        texts, cats = self._examples()
        key = (embedder.name, len(texts), hash(tuple(texts[-50:])))
        with Categorizer._cache_lock:
            cached = Categorizer._example_cache.get("m")
            if cached and cached[0] == key:
                return cached[1], cached[2]
        matrix = embedder.embed(texts)
        with Categorizer._cache_lock:
            Categorizer._example_cache["m"] = (key, matrix, cats)
        return matrix, cats

    def model_guesses(self, txs: list[dict]) -> list[Guess]:
        if not txs:
            return []
        embedder = emb.get_embedder()
        matrix, cats = self._example_matrix(embedder)
        vectors = embedder.embed([tx_text(t) or "?" for t in txs])
        sims = vectors @ matrix.T
        out = []
        for i, tx in enumerate(txs):
            amount = float(tx.get("amount") or 0)
            best: dict[int, float] = {}
            for j, cid in enumerate(cats):
                cid = int(cid)
                kind = self.by_id.get(cid, {}).get("kind")
                if kind == "income" and amount <= 0:
                    continue
                if kind == "expense" and amount > 0:
                    continue
                s = float(sims[i, j])
                if s > best.get(cid, -1.0):
                    best[cid] = s
            if not best:
                out.append(Guess(None, "model", 0.0, self.review_uncertain))
                continue
            ranked = sorted(best.items(), key=lambda kv: kv[1], reverse=True)
            top_cat, top = ranked[0]
            second = ranked[1][1] if len(ranked) > 1 else 0.0
            if top >= embedder.high and top - second >= 0.03:
                out.append(Guess(top_cat, "model", top, False))
            elif top >= embedder.low:
                out.append(Guess(top_cat, "model", top, self.review_uncertain))
            else:
                out.append(Guess(None, "model", top, self.review_uncertain))
        return out

    def classify_many(self, txs: list[dict]) -> list[Guess]:
        results: list[Guess | None] = [self.quick(t) for t in txs]
        pending = [i for i, g in enumerate(results) if g is None]
        if pending:
            if self.mode == "model":
                for i, g in zip(pending, self.model_guesses([txs[i] for i in pending])):
                    results[i] = g
            else:
                for i in pending:
                    results[i] = Guess(None, None, 0.0, self.review_uncertain)
        return results  # type: ignore[return-value]


def categorize(conn, where: str = "category_id IS NULL AND cat_source IS NULL", params: tuple = ()) -> int:
    """Categorize matching transactions (never touches ones the user set). Returns how many changed."""
    txs = db.rows(
        conn.execute(
            f"SELECT id, account_id, amount, counterparty, counterparty_iban, purpose, booking_text FROM transactions "
            f"WHERE (cat_source IS NULL OR cat_source != 'user') AND ({where})",
            params,
        )
    )
    if not txs:
        return 0
    guesses = Categorizer(conn).classify_many(txs)
    for tx, g in zip(txs, guesses):
        conn.execute(
            "UPDATE transactions SET category_id = ?, cat_source = ?, confidence = ?, needs_review = ? WHERE id = ?",
            (g.category_id, g.source or "none", round(g.confidence, 3), int(g.needs_review), tx["id"]),
        )
    link(conn)
    return len(txs)


def link(conn) -> None:
    """The passes that look at bookings together: transfers between own accounts, then refunds."""
    pair_own_transfers(conn)
    match_refunds(conn)


def pair_own_transfers(conn, max_days: int = 4) -> int:
    """Mark money moved between the user's own accounts.

    The ING CSV export has no counterparty IBAN, so a transfer from the Girokonto
    to the Extra-Konto is found by its mirror image: the same amount leaving one
    account and arriving on another within a few days. Both sides then go to
    "Savings" when one of the accounts is a savings account, else "Own transfers".
    """
    txs = db.rows(
        conn.execute(
            "SELECT t.id, t.account_id, a.kind AS account_kind, t.date, t.amount, t.cat_source, t.category_id, "
            "t.purpose, t.booking_text FROM transactions t "
            "JOIN accounts a ON a.id = t.account_id WHERE a.kind != 'depot' AND t.amount != 0 "
            "AND (t.cat_source IS NULL OR t.cat_source NOT IN ('user', 'rule')) ORDER BY t.date, t.id"
        )
    )
    cat_ids = {r["name"]: r["id"] for r in conn.execute("SELECT id, name FROM categories")}
    if "Own transfers" not in cat_ids:
        return 0
    incoming: dict[float, list[dict]] = {}
    for t in txs:
        if t["amount"] > 0:
            incoming.setdefault(round(t["amount"], 2), []).append(t)
    used: set[int] = set()
    marked = 0
    for t in txs:
        if t["amount"] >= 0 or t["id"] in used:
            continue
        text = f"{t['booking_text'] or ''} {t['purpose'] or ''}".upper()
        if "GEHALT" in text or "LOHN" in text or ISIN_RE.search(text):
            continue
        day = dt.date.fromisoformat(t["date"])
        for m in incoming.get(round(-t["amount"], 2), []):
            if m["id"] in used or m["account_id"] == t["account_id"]:
                continue
            if abs((dt.date.fromisoformat(m["date"]) - day).days) > max_days:
                continue
            name = transfer_category({t["account_kind"], m["account_kind"]}, text)
            cat_id = cat_ids.get(name) or cat_ids["Own transfers"]
            used.update((t["id"], m["id"]))
            if all(x["cat_source"] == "transfer" and x["category_id"] == cat_id for x in (t, m)):
                break
            for tid in (t["id"], m["id"]):
                conn.execute(
                    "UPDATE transactions SET category_id = ?, cat_source = 'transfer', confidence = 0.97, needs_review = 0 "
                    "WHERE id = ?",
                    (cat_id, tid),
                )
            marked += 2
            break
    return marked


def share_of(amount: float, payment: float) -> int | None:
    """How many ways the payment was split when the money is exactly one share of it (to the cent)."""
    for n in SHARES:
        if abs(amount * n - payment) <= 0.01 * n:
            return n
    return None


def _named(tx: dict) -> str:
    """The payee by name; empty when the text only names the payment service (PayPal)."""
    key = merchant_key(tx)
    return "" if key.startswith("PAYPAL") else key


def match_refunds(conn) -> int:
    """Money that came back for an earlier payment: a shop's refund or someone paying back.

    Money from a payee that was paid at least as much in the REFUND_DAYS before is linked to that
    payment, and several refunds can share one payment up to its amount. The refund takes the
    payment's category, so the two cancel out in the spending charts instead of the refund counting
    as income. The whole amount back is enough with any payee; a part of it needs the payee by name
    (not just PayPal) or by IBAN, and a payee that doesn't send similar amounts regularly. Links the
    user made stay as they are, and money the user said is no refund isn't linked again: its payee
    is then only linked when the whole amount comes back. Someone whose money the user linked by
    hand to a bill paid to someone else (their share of dinner) is learned: their money is linked by
    itself from then on when it is an even share of exactly one recent payment. Returns how many
    bookings changed.
    """
    cats = {r["id"]: (r["name"], r["kind"]) for r in conn.execute("SELECT id, name, kind FROM categories")}
    other = next((cid for cid, (name, _) in cats.items() if name == "Other income"), -1)
    expense = [cid for cid, (_, kind) in cats.items() if kind == "expense"]
    links = {r["refund_id"]: dict(r) for r in conn.execute("SELECT refund_id, purchase_id, source FROM refund_links")}
    rejected = {r[0] for r in conn.execute("SELECT refund_id FROM refund_rejects")}
    strict = {r[0] for r in conn.execute("SELECT key FROM refund_rejects WHERE key IS NOT NULL")}
    cols = (
        "t.id, t.date, t.amount, t.counterparty, t.counterparty_iban, t.purpose, t.booking_text, t.category_id, t.cat_source"
    )
    # What may have come back: everything Groschen sorted by itself (a guess, the merchant list or a
    # merchant learned before), but not what the user or a rule decided.
    sorted_as = ",".join("?" * len(expense)) or "NULL"
    back = db.rows(
        conn.execute(
            f"SELECT {cols} FROM transactions t JOIN accounts a ON a.id = t.account_id "
            "WHERE t.amount > 0 AND a.kind != 'depot' "
            "AND (t.cat_source IS NULL OR t.cat_source IN ('none', 'model', 'refund') "
            f"OR (t.cat_source IN ('dict', 'memory') AND (t.category_id = ? OR t.category_id IN ({sorted_as})))) "
            "ORDER BY t.date, t.id",
            (other, *expense),
        )
    )
    fixed = {rid: link for rid, link in links.items() if link["source"] == "user"}
    sharers = set()
    for r in db.rows(
        conn.execute(
            "SELECT r.counterparty, r.purpose, p.counterparty AS paid_to, p.purpose AS paid_for FROM refund_links l "
            "JOIN transactions r ON r.id = l.refund_id JOIN transactions p ON p.id = l.purchase_id WHERE l.source = 'user'"
        )
    ):
        who = _named(r)
        if who and who != _named({"counterparty": r["paid_to"], "purpose": r["paid_for"]}):
            sharers.add(who)
    taken: dict[int, float] = {}
    for rid, amount in conn.execute(
        f"SELECT id, amount FROM transactions WHERE id IN ({','.join('?' * len(fixed)) or 'NULL'})", tuple(fixed)
    ):
        pid = fixed[rid]["purchase_id"]
        taken[pid] = taken.get(pid, 0.0) + amount

    wanted: dict[int, int] = {}
    if back:
        oldest = (dt.date.fromisoformat(back[0]["date"]) - dt.timedelta(days=REGULAR_DAYS)).isoformat()
        # Every payment that money could have come back for, found by the payee's name and IBAN.
        index: dict[str, list[dict]] = {}
        payments: list[dict] = []
        for b in db.rows(
            conn.execute(
                f"SELECT {cols} FROM transactions t JOIN accounts a ON a.id = t.account_id "
                "WHERE t.amount < 0 AND t.date >= ? AND a.kind != 'depot' "
                "AND (t.cat_source IS NULL OR t.cat_source NOT IN ('own', 'transfer')) ORDER BY t.date DESC, t.id DESC",
                (oldest,),
            )
        ):
            name, kind = cats.get(b["category_id"], (None, "expense"))
            if name in NOT_PAYMENTS or kind == "income":
                continue
            b["named"], b["iban"] = _named(b), _norm_iban(b["counterparty_iban"])
            payments.append(b)
            for k in {merchant_key(b), _clean(b["counterparty"] or ""), b["named"], b["iban"] and "IBAN " + b["iban"]} - {
                ""
            }:
                index.setdefault(k, []).append(b)
        # Money each payee sent lately, to tell paying back from paying regularly (rent shares, pocket money).
        sent: dict[str, list[tuple[str, float]]] = {}
        for t in db.rows(conn.execute(f"SELECT {cols} FROM transactions t WHERE t.amount > 0 AND t.date >= ?", (oldest,))):
            if key := _named(t):
                sent.setdefault(key, []).append((t["date"], t["amount"]))

        for t in back:
            if t["id"] in rejected or t["id"] in fixed:
                continue
            day, amount = t["date"], t["amount"]
            since = (dt.date.fromisoformat(day) - dt.timedelta(days=REFUND_DAYS)).isoformat()
            part_since = (dt.date.fromisoformat(day) - dt.timedelta(days=PART_DAYS)).isoformat()
            named, iban = _named(t), _norm_iban(t["counterparty_iban"])
            keys = {merchant_key(t), _clean(t["counterparty"] or "")} - {""}
            early = (dt.date.fromisoformat(day) - dt.timedelta(days=REGULAR_DAYS)).isoformat()
            regular = (
                named and sum(1 for d, a in sent.get(named, []) if early <= d < day and abs(a - amount) <= amount * 0.1) >= 2
            )
            partial_ok = not regular and named not in strict
            seen: dict[int, dict] = {}
            for k in keys | {named, iban and "IBAN " + iban} - {""}:
                for b in index.get(k, []):
                    seen[b["id"]] = b
            whole = part = None
            for b in sorted(seen.values(), key=lambda b: (b["date"], b["id"]), reverse=True):
                if not since <= b["date"] <= day:
                    continue
                left = -b["amount"] - taken.get(b["id"], 0.0)
                if left < amount - 0.005:
                    continue
                if abs(-b["amount"] - amount) < 0.005 and not taken.get(b["id"]):
                    if keys & ({merchant_key(b), _clean(b["counterparty"] or "")} - {""}):
                        whole = b
                        break
                if (
                    part is None
                    and partial_ok
                    and b["date"] >= part_since
                    and ((named and named == b["named"]) or (iban and iban == b["iban"]))
                ):
                    part = b
            buy = whole or part
            if not buy and named in sharers and partial_ok:
                share_since = (dt.date.fromisoformat(day) - dt.timedelta(days=SHARE_DAYS)).isoformat()
                fits = [
                    b
                    for b in payments
                    if share_since <= b["date"] <= day
                    and -b["amount"] - taken.get(b["id"], 0.0) >= amount - 0.005
                    and share_of(amount, -b["amount"])
                ]
                if len(fits) == 1:
                    buy = fits[0]
            if buy:
                wanted[t["id"]] = buy["id"]
                taken[buy["id"]] = taken.get(buy["id"], 0.0) + amount

    now = db.now_iso()
    changed: set[int] = set()
    for rid, old in links.items():
        if old["source"] == "auto" and wanted.get(rid) != old["purchase_id"]:
            conn.execute("DELETE FROM refund_links WHERE refund_id = ?", (rid,))
            changed.add(rid)
    for rid, pid in wanted.items():
        if links.get(rid, {}).get("purchase_id") != pid:
            conn.execute(
                "INSERT INTO refund_links (refund_id, purchase_id, source, created_at) VALUES (?, ?, 'auto', ?) "
                "ON CONFLICT(refund_id) DO UPDATE SET purchase_id = excluded.purchase_id, source = 'auto'",
                (rid, pid, now),
            )
            changed.add(rid)
    # Linked money follows its payment's category; money whose payment is gone is sorted again.
    for t in back:
        pid = wanted.get(t["id"]) or (fixed.get(t["id"]) or {}).get("purchase_id")
        if pid is None:
            if t["cat_source"] == "refund":
                conn.execute(
                    "UPDATE transactions SET category_id = NULL, cat_source = NULL, needs_review = 1 WHERE id = ?",
                    (t["id"],),
                )
                changed.add(t["id"])
            continue
        cat = conn.execute("SELECT category_id FROM transactions WHERE id = ?", (pid,)).fetchone()[0]
        if t["cat_source"] != "refund" or t["category_id"] != cat:
            conn.execute(
                "UPDATE transactions SET category_id = ?, cat_source = 'refund', confidence = 0.95, needs_review = 0 "
                "WHERE id = ?",
                (cat, t["id"]),
            )
            changed.add(t["id"])
    return len(changed)


def reapply_quick(conn) -> int:
    """Re-run rules, memory and the merchant list on everything the user hasn't set. No model involved."""
    txs = db.rows(
        conn.execute(
            "SELECT id, account_id, amount, counterparty, counterparty_iban, purpose, booking_text, cat_source "
            "FROM transactions "
            "WHERE cat_source IS NULL OR cat_source != 'user'"
        )
    )
    c = Categorizer(conn)
    changed = 0
    orphans = []
    for tx in txs:
        g = c.quick(tx)
        if g is None:
            if tx["cat_source"] == "own":  # the name was taken off the list of the user's names
                orphans.append(tx["id"])
            continue
        conn.execute(
            "UPDATE transactions SET category_id = ?, cat_source = ?, confidence = ?, needs_review = 0 WHERE id = ?",
            (g.category_id, g.source, g.confidence, tx["id"]),
        )
        changed += 1
    if orphans:
        marks = ",".join("?" * len(orphans))
        conn.execute(f"UPDATE transactions SET category_id = NULL, cat_source = NULL WHERE id IN ({marks})", orphans)
        changed += categorize(conn, f"id IN ({marks})", tuple(orphans))
    else:
        link(conn)
    return changed


def learn(conn, tx: dict, category_id: int | None) -> None:
    """Remember a correction: the merchant goes into memory and the text becomes a model example."""
    if category_id is None:
        return
    key = merchant_key(tx)
    if key:
        conn.execute(
            "INSERT INTO merchant_memory (key, category_id, hits, updated_at) VALUES (?, ?, 1, ?) "
            "ON CONFLICT(key) DO UPDATE SET category_id = excluded.category_id, hits = hits + 1, "
            "updated_at = excluded.updated_at",
            (key, category_id, db.now_iso()),
        )
    text = tx_text(tx)[:160]
    if text:
        conn.execute("INSERT OR IGNORE INTO examples (text, category_id) VALUES (?, ?)", (text, category_id))


def apply_to_same_merchant(conn, tx: dict, category_id: int | None) -> int:
    """After a correction, give the same category to other transactions from that merchant."""
    return apply_to_merchant(conn, merchant_key(tx), category_id, skip_id=tx.get("id") or 0)


def apply_to_merchant(conn, key: str, category_id: int | None, skip_id: int = 0) -> int:
    if not key or not category_id:
        return 0
    # The user's own choices and rules win over what was learned from one merchant.
    others = db.rows(
        conn.execute(
            "SELECT id, amount, counterparty, purpose FROM transactions "
            "WHERE id != ? AND (cat_source IS NULL OR cat_source NOT IN ('user', 'rule'))",
            (skip_id,),
        )
    )
    # Income only fits money coming in: money sent to the same person or company stays as it is.
    kind = conn.execute("SELECT kind FROM categories WHERE id = ?", (category_id,)).fetchone()
    income = bool(kind) and kind[0] == "income"
    changed = 0
    for o in others:
        if income and o["amount"] <= 0:
            continue
        if merchant_key(o) == key:
            conn.execute(
                "UPDATE transactions SET category_id = ?, cat_source = 'memory', confidence = 0.95, needs_review = 0 "
                "WHERE id = ?",
                (category_id, o["id"]),
            )
            changed += 1
    return changed


def unspread_income(conn) -> int:
    """Money going out that picked up an income category from its merchant (before apply_to_merchant
    stopped that) is sorted again: by rules and the merchant list now, by the model on the next sync."""
    ids = [
        r[0]
        for r in conn.execute(
            "SELECT id FROM transactions WHERE cat_source = 'memory' AND amount <= 0 "
            "AND category_id IN (SELECT id FROM categories WHERE kind = 'income')"
        )
    ]
    if not ids:
        return 0
    marks = ",".join("?" * len(ids))
    conn.execute(
        f"UPDATE transactions SET category_id = NULL, cat_source = NULL, confidence = NULL, needs_review = 1 "
        f"WHERE id IN ({marks})",
        ids,
    )
    c = Categorizer(conn)
    txs = db.rows(
        conn.execute(
            "SELECT id, account_id, amount, counterparty, counterparty_iban, purpose, booking_text "
            f"FROM transactions WHERE id IN ({marks})",
            ids,
        )
    )
    for tx in txs:
        g = c.quick(tx)
        if g is not None:
            conn.execute(
                "UPDATE transactions SET category_id = ?, cat_source = ?, confidence = ?, needs_review = 0 WHERE id = ?",
                (g.category_id, g.source, g.confidence, tx["id"]),
            )
    return len(ids)


def forget(conn, key: str) -> int:
    """Drop a learned merchant and let the categorizer decide its transactions again."""
    conn.execute("DELETE FROM merchant_memory WHERE key = ?", (key,))
    ids = [
        r["id"]
        for r in db.rows(conn.execute("SELECT id, counterparty, purpose FROM transactions WHERE cat_source = 'memory'"))
        if merchant_key(r) == key
    ]
    if not ids:
        return 0
    marks = ",".join("?" * len(ids))
    conn.execute(f"UPDATE transactions SET category_id = NULL, cat_source = NULL WHERE id IN ({marks})", ids)
    return categorize(conn, f"id IN ({marks})", tuple(ids))


def migrate_merchant_keys(conn) -> None:
    """Rewrite merchant keys saved before spaces stopped counting ("AQUA NETWORKS" -> "AQUANETWORKS").

    Learned categories, subscription answers, savings destinations, refund choices, closed hints and
    payday choices all keep working. When two spellings were saved, the newest answer wins.
    """

    def fold(key: str) -> str:
        return key.replace(" ", "")

    def merge(table: str, cols: list[str], stamp: str, prefix: str = "") -> None:
        groups: dict[str, list[dict]] = {}
        for r in db.rows(conn.execute(f"SELECT key, {', '.join(cols)} FROM {table}")):
            if r["key"].startswith(prefix):
                groups.setdefault(fold(r["key"]), []).append(r)
        for new, rows in groups.items():
            if all(r["key"] == new for r in rows):
                continue
            keep = max(rows, key=lambda r: r[stamp] or "")  # the newest answer wins
            if "hits" in cols:
                keep = {**keep, "hits": sum(r["hits"] for r in rows)}
            conn.executemany(f"DELETE FROM {table} WHERE key = ?", [(r["key"],) for r in rows])
            conn.execute(
                f"INSERT INTO {table} (key, {', '.join(cols)}) VALUES ({', '.join('?' * (len(cols) + 1))})",
                (new, *(keep[c] for c in cols)),
            )

    merge("merchant_memory", ["category_id", "hits", "updated_at"], "updated_at")
    merge("subscription_marks", ["state", "updated_at"], "updated_at")
    merge("saving_dest_cp", ["dest", "created_at"], "created_at", prefix="name:")
    conn.execute("UPDATE refund_rejects SET key = REPLACE(key, ' ', '') WHERE key LIKE '% %'")
    for r in db.rows(conn.execute("SELECT key, dismissed_at FROM dismissed_alerts WHERE key LIKE '% %'")):
        if r["key"].startswith(("sub:", "price:")):
            conn.execute("DELETE FROM dismissed_alerts WHERE key = ?", (r["key"],))
            conn.execute(
                "INSERT OR IGNORE INTO dismissed_alerts (key, dismissed_at) VALUES (?, ?)",
                (fold(r["key"]), r["dismissed_at"]),
            )
    chosen = settings.get(conn, "payday_overrides")
    if isinstance(chosen, dict) and any(" " in k for k in chosen):
        settings.put(conn, "payday_overrides", {fold(k): v for k, v in chosen.items()})
