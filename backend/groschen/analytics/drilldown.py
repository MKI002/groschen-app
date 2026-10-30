"""Every transaction behind one slice of the spending charts, with a small analysis on top."""

import datetime as dt
import statistics

from .. import db
from ..categorize import names
from . import common, paydays, refunds

SORTS = {"date", "amount", "merchant"}
WEEKDAYS = 7


def display_name(tx: dict) -> str:
    return names.display_name(tx)


def _load(conn, start: str, end: str) -> list[dict]:
    return db.rows(
        conn.execute(
            "SELECT t.id, t.date, t.amount, t.counterparty, t.purpose, t.booking_text, t.category_id, t.cat_source, "
            "t.confidence, t.needs_review, t.note, t.account_id, a.name AS account, a.kind AS account_kind, "
            "c.name AS category, c.grp AS category_group, c.color AS category_color "
            "FROM transactions t JOIN accounts a ON a.id = t.account_id LEFT JOIN categories c ON c.id = t.category_id "
            "WHERE a.enabled = 1 AND t.date >= ? AND t.date <= ? ORDER BY t.date DESC, t.id DESC",
            (start, end),
        )
    )


def resolve_scope(cats: dict, group: str | None, category_id: int | None, flow: str | None = None) -> dict | None:
    """What was clicked: a group of categories or one category. None if it doesn't exist."""
    if category_id is not None:
        cat = cats.get(category_id)
        if not cat:
            return None
        direction = "income" if cat.get("kind") == "income" else "spending"
        return {
            "kind": "category",
            "name": cat["name"],
            "group": cat["grp"],
            "color": cat.get("color") or "muted",
            "ids": {category_id},
            "direction": direction,
        }
    if group is None:
        return None
    ids = {cid for cid, c in cats.items() if c["grp"] == group}
    uncategorized = group == common.UNCATEGORIZED["grp"]
    if not ids and not uncategorized:
        return None
    if uncategorized:
        ids.add(None)
    kinds = {cats[c].get("kind") for c in ids if c is not None}
    first = next((cats[c] for c in sorted(i for i in ids if i is not None)), None)
    return {
        "kind": "group",
        "name": group,
        "group": group,
        "color": (first or common.UNCATEGORIZED).get("color") or "muted",
        "ids": ids,
        # Uncategorized money coming in shows on the income side of the charts, going out on the spending side.
        "direction": flow if flow in ("income", "spending") else "income" if kinds == {"income"} else "spending",
    }


def custom_scope(cats: dict, name: str, ids: list[int]) -> dict | None:
    """One of the user's own groups: any mix of categories, shown like a category group."""
    known = {i for i in ids if i in cats}
    if not known:
        return None
    kinds = {cats[c].get("kind") for c in known}
    first = cats[min(known)]
    return {
        "kind": "custom",
        "name": name,
        "group": name,
        "color": first.get("color") or "muted",
        "ids": known,
        "direction": "income" if kinds == {"income"} else "spending",
    }


def merchant_scope(history: list[dict], flow: str | None) -> dict:
    """A payee or sender: everything booked with them, whatever the category."""
    net = sum(t["amount"] for t in history)
    cats: dict = {}
    for t in history:
        cats[(t["category_group"], t["category_color"])] = cats.get((t["category_group"], t["category_color"]), 0) + 1
    (grp, color), _ = max(cats.items(), key=lambda kv: kv[1])
    return {
        "kind": "merchant",
        "name": history[0]["merchant"],
        "group": grp or common.UNCATEGORIZED["grp"],
        "color": color or "muted",
        "key": history[0]["merchant"].lower(),
        "direction": flow if flow in ("income", "spending") else "income" if net > 0 else "spending",
    }


def _in_scope(tx: dict, scope: dict, cats: dict) -> bool:
    if scope["kind"] == "merchant":
        # Refunds and payments alike, so the total is what really went to (or came from) them.
        return tx["merchant"].lower() == scope["key"]
    if tx["category_id"] not in scope["ids"]:
        return False
    # The same rule the charts use, so the list adds up to the slice that was clicked.
    flow, _ = common.classify_flow(tx, cats)
    return flow == scope["direction"]


def _all_time(history: list[dict], sign: int) -> dict:
    """Everything ever booked with one payee, month by month, whatever period is picked."""
    first, last = history[-1]["date"], history[0]["date"]
    dates = [t["counts_for"] for t in history]
    monthly = {m: 0.0 for m in common.months_between(min(dates), max(dates))}
    for t in history:
        monthly[common.month_key(t["counts_for"])] += sign * t["amount"]
    return {
        "total": round(sign * sum(t["amount"] for t in history), 2),
        "count": len(history),
        "first": first,
        "last": last,
        "monthly": [{"month": m, "amount": round(v, 2)} for m, v in monthly.items()],
    }


def _previous(start: str, end: str) -> tuple[str, str]:
    s, e = dt.date.fromisoformat(start), dt.date.fromisoformat(end)
    days = (e - s).days + 1
    pe = s - dt.timedelta(days=1)
    return (pe - dt.timedelta(days=days - 1)).isoformat(), pe.isoformat()


def build(
    conn,
    *,
    start: str,
    end: str,
    label: str,
    group: str | None = None,
    category_id: int | None = None,
    merchant: str | None = None,
    custom: dict | None = None,
    q: str = "",
    account_id: int | None = None,
    min_amount: float | None = None,
    max_amount: float | None = None,
    sub: set[int | None] | None = None,
    sort: str = "date",
    desc: bool = True,
    limit: int = 200,
    offset: int = 0,
    compare: bool = True,
    flow: str | None = None,
) -> dict | None:
    """``custom`` is one of the user's own groups: {"id", "name", "category_ids"}."""
    cats = common.categories(conn)
    # Salary paid late in a month counts for the next one, as on the cash flow page.
    moved = paydays.shifted(conn)
    history: list[dict] = []
    if merchant is not None:
        wanted = merchant.strip().lower()
        for t in _load(conn, "0001-01-01", "9999-12-31"):
            t["merchant"] = display_name(t)
            t["counts_for"] = moved.get(t["id"], t["date"])
            if t["merchant"].lower() == wanted:
                history.append(t)
        scope = merchant_scope(history, flow) if history else None
    elif custom is not None:
        scope = custom_scope(cats, custom["name"], custom["category_ids"])
    else:
        scope = resolve_scope(cats, group, category_id, flow)
    if scope is None:
        return None
    sign = -1 if scope["direction"] == "spending" else 1
    needle = q.strip().lower()

    def matches(t: dict) -> bool:
        if not _in_scope(t, scope, cats):
            return False
        if account_id and t["account_id"] != account_id:
            return False
        value = abs(t["amount"])
        if min_amount is not None and value < min_amount - 0.004:
            return False
        if max_amount is not None and value > max_amount + 0.004:
            return False
        if needle:
            hay = " ".join(
                str(x or "") for x in (t["counterparty"], t["purpose"], t["note"], t["merchant"], t["category"])
            ).lower()
            amt = f"{abs(t['amount']):.2f}"
            if needle not in hay and needle not in amt and needle not in amt.replace(".", ","):
                return False
        return True

    if merchant is None:
        # Read a month further back so salary from the last days of the month before is found.
        early = (dt.date.fromisoformat(max(start, "1900-02-01")).replace(day=1) - dt.timedelta(days=1)).replace(day=1)
        history = _load(conn, early.isoformat(), end)
        for t in history:
            t["counts_for"] = moved.get(t["id"], t["date"])
    rows = [t for t in history if start <= t["counts_for"] <= end]
    for t in rows:
        t["merchant"] = display_name(t)
        t["detail"] = names.display_detail(t)
        t["value"] = round(sign * t["amount"], 2)
    base = [t for t in rows if matches(t)]
    # Sub-category counts ignore the sub-category filter itself, so every chip keeps its number.
    by_cat: dict = {}
    for t in base:
        c = by_cat.setdefault(
            t["category_id"],
            {
                "id": t["category_id"],
                "name": t["category"] or common.UNCATEGORIZED["name"],
                "color": t["category_color"] or "muted",
                "amount": 0.0,
                "count": 0,
            },
        )
        c["amount"] += t["value"]
        c["count"] += 1
    if scope["kind"] in ("group", "custom"):
        for cid in scope["ids"]:
            if cid is not None and cid not in by_cat:
                c = cats[cid]
                by_cat[cid] = {"id": cid, "name": c["name"], "color": c.get("color") or "muted", "amount": 0.0, "count": 0}
    items = [t for t in base if sub is None or t["category_id"] in sub]

    if sort == "amount":
        items.sort(key=lambda t: (t["value"], t["date"]), reverse=desc)
    elif sort == "merchant":
        items.sort(key=lambda t: (t["merchant"].lower(), t["date"]), reverse=desc)
    elif not desc:
        items.sort(key=lambda t: (t["date"], t["id"]))

    first, _ = common.data_range(conn)
    start_eff = max(start, first) if first else start
    months = common.months_between(start_eff, end) if start_eff <= end else []
    monthly = {m: {"month": m, "amount": 0.0, "count": 0} for m in months}
    weekday = [{"day": d, "amount": 0.0, "count": 0} for d in range(WEEKDAYS)]
    merchants: dict[str, dict] = {}
    for t in items:
        key = common.month_key(t["counts_for"])
        m = monthly.setdefault(key, {"month": key, "amount": 0.0, "count": 0})
        m["amount"] += t["value"]
        m["count"] += 1
        w = weekday[dt.date.fromisoformat(t["date"]).weekday()]
        w["amount"] += t["value"]
        w["count"] += 1
        me = merchants.setdefault(t["merchant"].lower(), {"name": t["merchant"], "amount": 0.0, "count": 0})
        me["amount"] += t["value"]
        me["count"] += 1

    values = [t["value"] for t in items]
    total = round(sum(values), 2)
    n_months = 1 if common.about_a_month(start_eff, end) else max(1, len(months))
    largest = max(items, key=lambda t: t["value"], default=None)
    previous = None
    if compare and start > "1900-01-01":
        p_start, p_end = _previous(start_eff, end)
        if not first or p_end >= first:
            prev = build(
                conn,
                start=p_start,
                end=p_end,
                label="",
                group=group,
                category_id=category_id,
                merchant=merchant,
                custom=custom,
                q=q,
                account_id=account_id,
                min_amount=min_amount,
                max_amount=max_amount,
                sub=sub,
                limit=0,
                compare=False,
                flow=scope["direction"],
            )
            if prev is not None:
                summary = prev["summary"]
                previous = {"start": p_start, "end": p_end, "total": summary["total"], "count": summary["count"]}

    public = (
        "id",
        "date",
        "amount",
        "counterparty",
        "purpose",
        "booking_text",
        "category_id",
        "cat_source",
        "confidence",
        "needs_review",
        "note",
        "account",
        "category",
        "category_group",
        "category_color",
        "merchant",
    )
    page = [
        {**{k: t[k] for k in public}, "counts_for": t["counts_for"] if t["counts_for"] != t["date"] else None}
        for t in items[offset : offset + max(0, min(limit, 1000))]
    ]
    refunds.annotate(conn, page)
    return {
        "scope": {
            "kind": scope["kind"],
            "name": scope["name"],
            "group": scope["group"],
            "color": scope["color"],
            "direction": scope["direction"],
            "category_id": category_id,
            "custom_id": custom["id"] if custom else None,
        },
        "range": {"start": start, "end": end, "label": label},
        "categories": sorted(
            ({**c, "amount": round(c["amount"], 2)} for c in by_cat.values()), key=lambda c: (-c["amount"], c["name"])
        ),
        "summary": {
            "total": total,
            "count": len(items),
            "average": round(total / len(items), 2) if items else 0,
            "median": round(statistics.median(values), 2) if values else 0,
            "per_month": round(total / n_months, 2),
            "months": n_months,
            "largest": {k: largest[k] for k in ("id", "date", "merchant", "value")} if largest else None,
            "review": sum(1 for t in items if t["needs_review"]),
            "previous": previous,
        },
        "monthly": [{**m, "amount": round(m["amount"], 2)} for m in sorted(monthly.values(), key=lambda m: m["month"])],
        "weekday": [{**w, "amount": round(w["amount"], 2)} for w in weekday],
        "merchants": sorted(
            (
                {**m, "amount": round(m["amount"], 2), "share": m["amount"] / total if total else 0}
                for m in merchants.values()
            ),
            key=lambda m: -m["amount"],
        )[:8],
        "merchant_count": len(merchants),
        "all_time": _all_time(history, sign) if merchant is not None else None,
        "items": page,
        "total": len(items),
    }
