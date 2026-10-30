"""Numbers for the dashboard pages."""

import datetime as dt
import json
import re
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from .. import db, settings
from ..analytics import (
    alerts,
    cashflow,
    common,
    drilldown,
    fund,
    networth,
    paydays,
    plans,
    portfolio,
    recurring,
    refunds,
    savings,
    upcoming,
)
from ..analytics.drilldown import display_name
from ..categorize import engine, names
from .deps import current_user

router = APIRouter(dependencies=[Depends(current_user)])


def _range(preset: str | None, anchor: str | None):
    return common.resolve_range(preset, anchor)


@router.get("/cashflow")
def get_cashflow(preset: str | None = None, anchor: str | None = None):
    start, end, label = _range(preset, anchor)
    with db.session() as conn:
        return cashflow.summary(conn, start, end, label, split=True)


@router.get("/cashflow/timeline")
def get_cashflow_timeline():
    """Every month's money flow, linked by what carried over on the everyday account (Overview timeline)."""
    with db.session() as conn:
        return cashflow.timeline(conn)


class SavingDest(BaseModel):
    # None goes back to what Groschen found by itself.
    dest: Literal["plan", "etf", "savings", "other", "stays"] | None
    learn: bool = True


@router.put("/savings/{tx_id}")
def set_saving_dest(tx_id: int, body: SavingDest):
    """Say where a saved amount really went (Overview), or go back to Groschen's own guess."""
    with db.session() as conn:
        try:
            savings.set_dest(conn, tx_id, body.dest, body.learn)
        except KeyError:
            raise HTTPException(status_code=404, detail="Unknown transaction.") from None
    return {"ok": True, "dest": body.dest}


@router.get("/daily")
def get_daily(year: int | None = Query(None, ge=1900, le=2999)):
    """Spending per day of one calendar year (the current one by default)."""
    y = year or dt.date.today().year
    with db.session() as conn:
        return {"year": y, **cashflow.daily(conn, f"{y}-01-01", f"{y}-12-31")}


@router.get("/transactions")
def get_transactions(
    q: str = "",
    filter: str = "all",
    account_id: int | None = None,
    category_id: int | None = None,
    preset: str | None = None,
    anchor: str | None = None,
    min_amount: float | None = Query(None, alias="min", ge=0),
    max_amount: float | None = Query(None, alias="max", ge=0),
    date_from: dt.date | None = Query(None, alias="from"),
    date_to: dt.date | None = Query(None, alias="to"),
    sort: str = "date",
    dir: str = "desc",
    limit: int = 300,
    offset: int = 0,
):
    if sort not in ("date", "amount", "merchant") or dir not in ("asc", "desc"):
        raise HTTPException(status_code=422, detail="Unknown sort order.")
    start, end, label = _range(preset or "all", anchor)
    if date_from:
        start = max(start, date_from.isoformat())
    if date_to:
        end = min(end, date_to.isoformat())
    where = ["t.date >= ?", "t.date <= ?"]
    params: list = [start, end]
    if min_amount is not None:
        where.append("ABS(t.amount) >= ?")
        params.append(min_amount - 0.004)
    if max_amount is not None:
        where.append("ABS(t.amount) <= ?")
        params.append(max_amount + 0.004)
    if q.strip():
        like = f"%{q.strip().lower()}%"
        where.append(
            "(LOWER(COALESCE(t.counterparty,'')) LIKE ? OR LOWER(COALESCE(t.purpose,'')) LIKE ? "
            "OR LOWER(COALESCE(c.name,'')) LIKE ? OR REPLACE(printf('%.2f', ABS(t.amount)), '.', ',') LIKE ? "
            "OR printf('%.2f', ABS(t.amount)) LIKE ?)"
        )
        params += [like, like, like, like, like]
    if filter == "review":
        where.append("t.needs_review = 1")
    elif filter == "unc":
        where.append("t.category_id IS NULL")
    elif filter == "income":
        where.append("t.amount > 0")
    if account_id:
        where.append("t.account_id = ?")
        params.append(account_id)
    if category_id:
        where.append("t.category_id = ?")
        params.append(category_id)
    clause = " AND ".join(where)
    base = (
        f"FROM transactions t JOIN accounts a ON a.id = t.account_id LEFT JOIN categories c ON c.id = t.category_id "
        f"WHERE a.enabled = 1 AND {clause}"
    )
    way = "DESC" if dir == "desc" else "ASC"
    order = {
        "date": f"t.date {way}, t.id {way}",
        "amount": f"ABS(t.amount) {way}, t.date DESC",
        "merchant": f"LOWER(COALESCE(NULLIF(TRIM(t.counterparty), ''), t.purpose, '')) {way}, t.date DESC",
    }[sort]
    with db.session() as conn:
        items = db.rows(
            conn.execute(
                f"SELECT t.id, t.date, t.amount, t.counterparty, t.purpose, t.booking_text, t.category_id, t.cat_source, "
                f"t.confidence, t.needs_review, t.note, a.name AS account, c.name AS category, c.grp AS category_group, "
                f"c.color AS category_color {base} ORDER BY {order} LIMIT ? OFFSET ?",
                (*params, min(limit, 1000), offset),
            )
        )
        total, inflow, outflow, review = conn.execute(
            f"SELECT COUNT(*), COALESCE(SUM(CASE WHEN t.amount > 0 THEN t.amount END), 0), "
            f"COALESCE(SUM(CASE WHEN t.amount < 0 THEN -t.amount END), 0), COALESCE(SUM(t.needs_review), 0) {base}",
            params,
        ).fetchone()
        moved = paydays.shifted(conn)
        sub_marks = recurring.marks(conn)
        refunds.annotate(conn, items)
    for it in items:
        it["merchant"] = display_name(it)
        it["detail"] = names.display_detail(it)
        it["counts_for"] = moved.get(it["id"])
        it["subscription"] = sub_marks.get(engine.merchant_key(it))
        # Kleingeld Plus rounds up every card payment: the list folds a day's round-ups into one line.
        it["roundup"] = it["merchant"] == "Kleingeld Plus" and abs(it["amount"]) < 5
    return {
        "items": items,
        "total": total,
        "in": round(inflow, 2),
        "out": round(outflow, 2),
        "review": review,
        "range": {"start": start, "end": end, "label": label},
    }


@router.get("/drilldown")
def get_drilldown(
    group: str | None = None,
    category_id: int | None = None,
    merchant: str | None = Query(None, max_length=200),
    custom: int | None = None,
    preset: str | None = None,
    anchor: str | None = None,
    q: str = "",
    account_id: int | None = None,
    min_amount: float | None = Query(None, alias="min", ge=0),
    max_amount: float | None = Query(None, alias="max", ge=0),
    sub: str = "",
    flow: str | None = None,
    sort: str = "date",
    dir: str = "desc",
    limit: int = Query(200, ge=0),
    offset: int = Query(0, ge=0),
):
    """All transactions behind one slice of the charts (a group or a category), or with one payee."""
    if flow not in (None, "income", "spending"):
        raise HTTPException(status_code=422, detail="Unknown flow.")
    if sort not in drilldown.SORTS or dir not in ("asc", "desc"):
        raise HTTPException(status_code=422, detail="Unknown sort order.")
    try:
        picked = {None if s == "none" else int(s) for s in sub.split(",") if s} if sub else None
    except ValueError:
        raise HTTPException(status_code=422, detail="Unknown category filter.") from None
    start, end, label = _range(preset, anchor)
    with db.session() as conn:
        own = None
        if custom is not None:
            own = db.one(conn.execute("SELECT id, name, category_ids FROM groups WHERE id = ?", (custom,)))
            if not own:
                raise HTTPException(status_code=404, detail="Unknown group.")
            own["category_ids"] = json.loads(own["category_ids"] or "[]")
        out = drilldown.build(
            conn,
            start=start,
            end=end,
            label=label,
            group=group,
            category_id=category_id,
            merchant=merchant,
            custom=own,
            q=q[:200],
            account_id=account_id,
            min_amount=min_amount,
            max_amount=max_amount,
            sub=picked,
            sort=sort,
            desc=dir == "desc",
            limit=limit,
            offset=offset,
            flow=flow,
        )
    if out is None:
        raise HTTPException(status_code=404, detail="Nothing found for this category or payee.")
    return out


class TxUpdate(BaseModel):
    category_id: int | None = None
    note: str | None = None
    apply_to_similar: bool = True
    set_category: bool = True


@router.patch("/transactions/{tx_id}")
def update_transaction(tx_id: int, body: TxUpdate):
    with db.session() as conn:
        tx = db.one(
            conn.execute(
                "SELECT id, amount, counterparty, counterparty_iban, purpose, booking_text FROM transactions WHERE id = ?",
                (tx_id,),
            )
        )
        if not tx:
            raise HTTPException(status_code=404, detail="Unknown transaction.")
        changed = 0
        if body.set_category:
            conn.execute(
                "UPDATE transactions SET category_id = ?, cat_source = 'user', confidence = 1, needs_review = 0 "
                "WHERE id = ?",
                (body.category_id, tx_id),
            )
            engine.learn(conn, tx, body.category_id)
            if body.apply_to_similar and body.category_id:
                changed = engine.apply_to_same_merchant(conn, tx, body.category_id)
            engine.link(conn)  # money that came back for this payment follows its new category
        if body.note is not None:
            conn.execute("UPDATE transactions SET note = ? WHERE id = ?", (body.note.strip()[:500] or None, tx_id))
    return {"ok": True, "also_changed": changed}


@router.get("/transactions/{tx_id}/refund")
def get_refund(tx_id: int):
    """Both sides of a booking's refund links, for its details: the payment it came back for, or what came back."""
    with db.session() as conn:
        try:
            return refunds.detail(conn, tx_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="Unknown transaction.") from None


@router.get("/transactions/{tx_id}/refund/candidates")
def get_refund_candidates(tx_id: int, q: str = Query("", max_length=100)):
    """Payments this money could have come back for, likeliest first."""
    with db.session() as conn:
        try:
            return {"items": refunds.candidates(conn, tx_id, q)}
        except KeyError:
            raise HTTPException(status_code=404, detail="Unknown transaction.") from None


class RefundLink(BaseModel):
    purchase_id: int


@router.put("/transactions/{tx_id}/refund")
def link_refund(tx_id: int, body: RefundLink):
    """This money came back for that payment (linked by hand)."""
    with db.session() as conn:
        try:
            refunds.link(conn, tx_id, body.purchase_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="Unknown transaction.") from None
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e)) from None
        return refunds.detail(conn, tx_id)


@router.delete("/transactions/{tx_id}/refund")
def unlink_refund(tx_id: int):
    """This money is no refund: take the link away, and Groschen remembers."""
    with db.session() as conn:
        try:
            refunds.unlink(conn, tx_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="Unknown transaction.") from None
    return {"ok": True}


@router.post("/transactions/{tx_id}/reviewed")
def mark_reviewed(tx_id: int):
    """Accept the guess as it is."""
    with db.session() as conn:
        tx = db.one(
            conn.execute(
                "SELECT id, amount, counterparty, counterparty_iban, purpose, booking_text, category_id "
                "FROM transactions WHERE id = ?",
                (tx_id,),
            )
        )
        if not tx:
            raise HTTPException(status_code=404, detail="Unknown transaction.")
        conn.execute("UPDATE transactions SET needs_review = 0, cat_source = 'user' WHERE id = ?", (tx_id,))
        engine.learn(conn, tx, tx["category_id"])
        # Confirming a guess teaches the merchant too, so its other bookings stop asking.
        changed = engine.apply_to_same_merchant(conn, tx, tx["category_id"]) if tx["category_id"] else 0
    return {"ok": True, "also_changed": changed}


class ReviewedMany(BaseModel):
    ids: list[int] = Field(min_length=1, max_length=500)


@router.post("/transactions/reviewed")
def mark_many_reviewed(body: ReviewedMany):
    """Accept several guesses at once ("All fine" on the review list)."""
    accepted = 0
    with db.session() as conn:
        for tx_id in dict.fromkeys(body.ids):
            tx = db.one(
                conn.execute(
                    "SELECT id, amount, counterparty, counterparty_iban, purpose, booking_text, category_id "
                    "FROM transactions WHERE id = ? AND needs_review = 1",
                    (tx_id,),
                )
            )
            if not tx:
                continue
            conn.execute("UPDATE transactions SET needs_review = 0, cat_source = 'user' WHERE id = ?", (tx_id,))
            engine.learn(conn, tx, tx["category_id"])
            if tx["category_id"]:
                engine.apply_to_same_merchant(conn, tx, tx["category_id"])
            accepted += 1
    return {"ok": True, "accepted": accepted}


@router.get("/networth")
def get_networth():
    with db.session() as conn:
        return networth.overview(conn)


@router.get("/investments")
def get_investments():
    with db.session() as conn:
        out = portfolio.overview(conn)
        extras = fund.holding_extras(conn, out["holdings"])
        for h in out["holdings"]:
            h.update(extras.get(h["isin"], {}))
        out["forecast"] = fund.portfolio_forecast(conn, out["holdings"])
        out["investing"] = fund.investing(portfolio.contributions(conn), [], dt.date.today())
        # The "Paid in" tile names the same monthly amount the forecast uses.
        if out["investing"]:
            out["monthly_plan"] = out["investing"]["per_month"] or None
        out["online_prices"] = bool(settings.get(conn, "online_prices"))
        return out


@router.get("/investments/payments")
def get_investment_payments():
    """What Groschen counts as money put into investments, newest first, with the ones taken out."""
    with db.session() as conn:
        return {"payments": list(reversed(portfolio.payments(conn)))}


class InvestCounted(BaseModel):
    counted: bool


@router.put("/investments/payments/{tx_id}")
def set_investment_payment(tx_id: int, body: InvestCounted):
    """Take one payment out of the Investments page (not an investment in this depot) or put it back."""
    with db.session() as conn:
        if not db.one(conn.execute("SELECT id FROM transactions WHERE id = ?", (tx_id,))):
            raise HTTPException(status_code=404, detail="Unknown transaction.")
        portfolio.set_counted(conn, tx_id, body.counted)
    return {"ok": True, "counted": body.counted}


@router.get("/investments/{isin}")
def get_fund(isin: str):
    isin = isin.strip().upper()
    if not fund.ISIN_RE.match(isin):
        raise HTTPException(status_code=404, detail="ETF not found.")
    with db.session() as conn:
        out = fund.detail(conn, isin)
    if out is None:
        raise HTTPException(status_code=404, detail="ETF not found.")
    return out


@router.get("/subscriptions")
def get_subscriptions():
    with db.session() as conn:
        found = recurring.overview(conn)
    subs = found["items"]
    monthly = round(sum(s["monthly_cost"] for s in subs), 2)
    return {
        "items": subs,
        "monthly": monthly,
        "yearly": round(sum(s["yearly_cost"] for s in subs), 2),
        "price_changes": [s for s in subs if s["price_change"] > 0],
        "suggestions": found["suggestions"],
        "hidden": found["hidden"],
        "ended": found["ended"],
        "events": found["events"],
    }


@router.get("/plans")
def get_plans():
    """Savings plans Groschen found by itself: ETF plans, Kleingeld Plus, standing orders to savings."""
    with db.session() as conn:
        return plans.find(conn)


@router.get("/available")
def get_available():
    with db.session() as conn:
        return upcoming.available(conn)


@router.get("/calendar")
def get_calendar(month: str | None = None):
    today = dt.date.today()
    if month is None:
        month = today.strftime("%Y-%m")
    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", month):
        raise HTTPException(status_code=422, detail="The month must look like 2026-09.")
    with db.session() as conn:
        return upcoming.month_calendar(conn, month, today)


@router.get("/alerts")
def get_alerts():
    with db.session() as conn:
        return {"items": alerts.find(conn)}


class AlertKey(BaseModel):
    key: str = Field(min_length=1, max_length=200)


@router.post("/alerts/dismiss")
def dismiss_alert(body: AlertKey):
    with db.session() as conn:
        alerts.dismiss(conn, body.key)
    return {"ok": True}


@router.delete("/alerts/dismissed")
def restore_alerts():
    with db.session() as conn:
        return {"restored": alerts.restore_all(conn)}


class SubscriptionMark(BaseModel):
    key: str = Field(min_length=1, max_length=120)
    state: Literal["yes", "no", "auto"]


@router.post("/subscriptions/mark")
def mark_subscription(body: SubscriptionMark):
    """Remember whether a merchant is a subscription ('auto' lets Groschen decide again)."""
    with db.session() as conn:
        recurring.set_mark(conn, body.key, body.state)
    return {"ok": True}


class TxSubscription(BaseModel):
    state: Literal["yes", "no", "auto"]


@router.post("/transactions/{tx_id}/subscription")
def mark_transaction_subscription(tx_id: int, body: TxSubscription):
    """Mark the merchant behind a transaction as a subscription, or as not one."""
    with db.session() as conn:
        tx = db.one(conn.execute("SELECT counterparty, purpose FROM transactions WHERE id = ?", (tx_id,)))
        if not tx:
            raise HTTPException(status_code=404, detail="Unknown transaction.")
        key = engine.merchant_key(tx)
        if not key:
            raise HTTPException(status_code=400, detail="This transaction has no merchant to remember.")
        recurring.set_mark(conn, key, body.state)
    return {"ok": True, "key": key}


@router.get("/badges")
def badges():
    with db.session() as conn:
        review = conn.execute("SELECT COUNT(*) FROM transactions WHERE needs_review = 1").fetchone()[0]
        subs_up = sum(1 for s in recurring.detect(conn) if s["price_change"] > 0)
        count = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
        reminder_days = int(settings.get(conn, "reminder_days") or 15)
        hints = len(alerts.find(conn))
    return {
        "review": review,
        "price_changes": subs_up,
        "transactions": count,
        "reminder_days": reminder_days,
        "alerts": hints,
    }
