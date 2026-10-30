// Money that came back for a payment: a shop's refund or someone paying back. Groschen links most of
// it by itself. Both bookings show the link, a wrong one goes with one tap (and Groschen keeps the two
// apart from then on), and money it couldn't place is linked by picking the payment.

import { useEffect, useState, type CSSProperties } from "react";
import { catName, t, useT, type Key } from "../i18n";
import { qs } from "../lib/api";
import { colorVar, dateShort, dayMonth, eur, initial } from "../lib/format";
import type { RefundCandidate, RefundInfo, Tx, TxBrief } from "../lib/types";
import { Icon } from "./Icons";
import { Spinner, useApi } from "./UI";

const vars = (v: Record<string, string | number>) => v as CSSProperties;
const isAll = (back: number, of: number) => back >= of - 0.005;

// "€29.00 of €40.00 back", or that all of it came back.
export const backText = (back: number, of: number) => (isAll(back, of) ? t("rf.all") : t("rf.part", { back: eur(back), of: eur(of) }));

// What came back of a payment, as a bar that fills up.
export function BackBar({ back, of }: { back: number; of: number }) {
  const share = of > 0 ? Math.max(0, Math.min(1, back / of)) : 0;
  return (
    <span className="rf-bar" aria-hidden="true">
      <i style={vars({ "--p": share })} />
    </span>
  );
}

// The line under a booking in lists: what came back for it, or the payment it came back for.
export function BackLine({ tx }: { tx: Tx }) {
  if (tx.refund_for)
    return (
      <span className="txl-back">
        <Icon name="rewind" size={12} />
        {t("rf.for", { merchant: tx.refund_for.merchant, date: dayMonth(tx.refund_for.date) })}
      </span>
    );
  if (!tx.refunded || tx.amount >= 0) return null;
  return (
    <span className="txl-back">
      <Icon name="rewind" size={12} />
      {backText(tx.refunded, -tx.amount)}
      {!isAll(tx.refunded, -tx.amount) && <BackBar back={tx.refunded} of={-tx.amount} />}
    </span>
  );
}

export const allBack = (tx: Tx) => !!tx.refunded && tx.amount < 0 && isAll(tx.refunded, -tx.amount);

// In a payment's dialog: what came back for it, each with a way to take it off.
export function PaymentBack({ tx, info, busy, onUnlink }: { tx: Tx; info: RefundInfo; busy: number | null; onUnlink: (r: TxBrief) => void }) {
  useT();
  const of = -tx.amount;
  return (
    <section className="rf">
      <div className="rf-head">
        <span className="rf-ic">
          <Icon name="rewind" size={15} />
        </span>
        <b>{backText(info.refunded, of)}</b>
      </div>
      <BackBar back={info.refunded} of={of} />
      <div className="rf-list">
        {info.refunds.map((r) => (
          <div key={r.id} className="rf-item">
            <span className="rf-when">{dayMonth(r.date)}</span>
            <span className="rf-who">{r.merchant}</span>
            <b className="rf-amt pos">{eur(r.amount)}</b>
            <button type="button" className="btn sm ghost rf-off" disabled={busy !== null} onClick={() => onUnlink(r)} aria-label={t("rf.notPartOf", { amount: eur(r.amount), date: dateShort(r.date) })}>
              {busy === r.id ? <Spinner /> : <Icon name="x" size={13} />}
              {t("rf.notPart")}
            </button>
          </div>
        ))}
      </div>
      {tx.category && info.left !== null && (
        <p className="rf-note">{info.left > 0.005 ? t("rf.counts", { amount: eur(info.left), cat: catName(tx.category) }) : t("rf.countsNone", { cat: catName(tx.category) })}</p>
      )}
    </section>
  );
}

// In the dialog of money that came back: the payment it belongs to, how much of it is back now, and
// the two ways out (another payment, or none).
export function MoneyBackFor({ tx, info, busy, onUnlink, onPick }: { tx: Tx; info: RefundInfo; busy: boolean; onUnlink: () => void; onPick: () => void }) {
  useT();
  const p = info.purchase;
  if (!p) return null;
  const of = -p.amount;
  const others = info.refunds.filter((r) => r.id !== tx.id).length;
  return (
    <section className="rf">
      <div className="rf-head">
        <span className="rf-ic">
          <Icon name="rewind" size={15} />
        </span>
        <b>{t("rf.backFor")}</b>
      </div>
      <div className="rf-pay" style={vars({ "--c": colorVar(tx.category_color) })}>
        <span className="txl-av" aria-hidden="true">
          {initial(p.merchant)}
        </span>
        <span className="rf-pay-main">
          <b>{p.merchant}</b>
          <small>{dateShort(p.date)}</small>
        </span>
        <b className="rf-pay-amt">{eur(p.amount)}</b>
      </div>
      <div className="rf-prog">
        <BackBar back={info.refunded} of={of} />
        <small>
          {backText(info.refunded, of)}
          {others > 0 && ` · ${t("rf.withOthers", { n: others })}`}
        </small>
      </div>
      <p className="rf-note">{tx.category ? t("rf.against", { cat: catName(tx.category) }) : t("rf.againstNone")}</p>
      <div className="rf-actions">
        <button type="button" className="btn sm" disabled={busy} onClick={onPick}>
          {t("rf.other")}
        </button>
        <button type="button" className="btn sm ghost rf-off" disabled={busy} onClick={onUnlink}>
          {busy ? <Spinner /> : <Icon name="x" size={13} />}
          {t("rf.notPart")}
        </button>
      </div>
    </section>
  );
}

// In the dialog of money that came in and isn't linked: the way to say what it came back for.
export function LinkAsk({ onPick }: { onPick: () => void }) {
  useT();
  return (
    <button type="button" className="rf-ask" onClick={onPick}>
      <span className="rf-ic">
        <Icon name="rewind" size={15} />
      </span>
      <span className="rf-ask-txt">
        <b>{t("rf.ask")}</b>
        <small>{t("rf.askSub")}</small>
      </span>
      <Icon name="chevRight" size={15} />
    </button>
  );
}

// The payments the money could have come back for, the likeliest first, with a search.
export function PaymentPicker({ tx, busy, onPick }: { tx: Tx; busy: number | null; onPick: (c: RefundCandidate) => void }) {
  useT();
  const [q, setQ] = useState("");
  const [query, setQuery] = useState("");
  useEffect(() => {
    const h = window.setTimeout(() => setQuery(q.trim()), 220);
    return () => window.clearTimeout(h);
  }, [q]);
  const { data, error, loading } = useApi<{ items: RefundCandidate[] }>(`/transactions/${tx.id}/refund/candidates${qs({ q: query })}`);
  return (
    <div className="rf-pick">
      <p className="rf-note">{t("rf.pickText")}</p>
      <label className="catpick-search">
        <Icon name="search" size={15} />
        <input autoFocus value={q} onChange={(e) => setQ(e.target.value)} placeholder={t("rf.search")} aria-label={t("rf.search")} />
        {loading && <Spinner />}
      </label>
      {error && <p className="err">{error}</p>}
      <div className="rf-cands">
        {data?.items.map((c, i) => (
          <button key={c.id} type="button" className="rf-cand" style={vars({ "--c": colorVar(c.category_color), "--i": Math.min(i, 12) })} disabled={busy !== null} onClick={() => onPick(c)}>
            <span className="txl-av" aria-hidden="true">
              {initial(c.merchant)}
            </span>
            <span className="rf-cand-main">
              <b>{c.merchant}</b>
              <small>
                {dateShort(c.date)}
                {c.category && ` · ${catName(c.category)}`}
              </small>
            </span>
            <span className="rf-cand-amt">
              {busy === c.id ? <Spinner /> : <b>{eur(c.amount)}</b>}
              {c.share ? (
                <small>{t(`rf.share${Math.min(c.share, 6)}` as Key)}</small>
              ) : (
                c.left < -c.amount - 0.005 && <small className="muted">{t("rf.leftOf", { amount: eur(c.left) })}</small>
              )}
            </span>
          </button>
        ))}
        {data && !data.items.length && <p className="rf-none">{query ? t("rf.noneQ") : t("rf.none")}</p>}
      </div>
    </div>
  );
}
