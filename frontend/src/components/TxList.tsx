import { Fragment, useMemo, useState } from "react";
import { catName, locale, t, useT } from "../i18n";
import { colorVar, dateShort, daysFrom, eur, money, monthLong, veil } from "../lib/format";
import type { Tx } from "../lib/types";
import { MerchantAv } from "./Logo";
import { Icon } from "./Icons";
import { allBack, BackLine } from "./Refunds";

// "Today", "Yesterday", then weekday and date; the year only when it isn't this one.
// What a booking adds to a sum in the home currency: nothing while money in another currency has no rate yet.
export const counted = (tx: Pick<Tx, "amount" | "orig_amount" | "fx_rate">) => (tx.orig_amount != null && tx.fx_rate == null ? 0 : tx.amount);

// A booking's amount in the home currency; money in another currency shows what the bank booked
// underneath (50,00 $), or only that, marked, while there's no exchange rate for it.
export function TxAmount({ tx }: { tx: Pick<Tx, "amount" | "currency" | "orig_amount" | "fx_rate"> }) {
  if (tx.orig_amount == null || !tx.currency) return <>{eur(tx.amount)}</>;
  if (tx.fx_rate == null)
    return (
      <>
        {money(tx.orig_amount, tx.currency)}
        <small className="orig">{t("fx.notCounted")}</small>
      </>
    );
  return (
    <>
      {eur(tx.amount)}
      <small className="orig">{money(tx.orig_amount, tx.currency)}</small>
    </>
  );
}

export function dayHead(iso: string) {
  const n = daysFrom(iso);
  if (n === 0) return t("day.today");
  if (n === -1) return t("day.yesterday");
  const d = new Date(`${iso}T12:00:00`);
  const thisYear = d.getFullYear() === new Date().getFullYear();
  return d.toLocaleDateString(locale(), { weekday: "long", day: "numeric", month: "long", ...(thisYear ? {} : { year: "numeric" }) });
}

// Where money that only moved went: "Girokonto → Extra-Konto", the payee where the account isn't known.
export function route(tx: Tx) {
  const mv = tx.move;
  return mv ? `${mv.from ?? tx.merchant} → ${mv.to ?? tx.merchant}` : "";
}

// A booking as the list shows it; for money moved between own accounts with both sides listed, the
// side that left an account, with the side that arrived.
type Row = { tx: Tx; other?: Tx };
// A day's round-ups, or several moves of one payee the same way, folded into one line.
type Fold = { key: string; rows: Row[]; roundup: boolean };
type Entry = Row | Fold;

// What a day's moves fold by: the same payee the same way (a round-up per card payment, two ETF plans).
const foldKey = (tx: Tx) => `${tx.merchant}|${route(tx)}`;

// A day's bookings in the order the list shows them: real income and spending first, then the money
// that only moved, each move once with both sides, and with ``fold`` several of the same kind in one line.
function dayEntries(items: Tx[], listed: Map<number, Tx>, byDay: boolean, fold: boolean): Entry[] {
  const real: Entry[] = [];
  const moves: Row[] = [];
  for (const tx of items) {
    const other = byDay && tx.move?.mirror != null ? listed.get(tx.move.mirror) : undefined;
    if (other && tx.amount > 0) continue; // shown with the side that left the other account
    if (tx.move) moves.push(other ? { tx, other } : { tx });
    else real.push({ tx });
  }
  if (!fold || !byDay) return [...real, ...moves];
  const groups = new Map<string, Row[]>();
  for (const r of moves) {
    if (r.tx.needs_review === 1) continue; // still to check: stays in sight
    const key = foldKey(r.tx);
    groups.set(key, [...(groups.get(key) ?? []), r]);
  }
  const out: Entry[] = [...real];
  for (const r of moves) {
    const rows = r.tx.needs_review === 1 ? null : groups.get(foldKey(r.tx));
    if (!rows || rows.length < 2) out.push(r);
    else if (rows[0] === r) out.push({ key: `${r.tx.date}|${foldKey(r.tx)}`, rows, roundup: rows.every((x) => x.tx.roundup) });
  }
  // The round-ups last: the smallest and the most of them.
  return out.sort((a, b) => Number("rows" in a && a.roundup) - Number("rows" in b && b.roundup));
}

// The one way a list of bookings looks, on Transactions and on every detail page: grouped by day with
// the day's sum (when sorted by date and the day has more than one), each row the merchant's logo or initial
// in the category's colour, the payee with its note or purpose, the category, the account and the
// amount. Money that came back shows on both bookings, and a payment that came back whole is struck
// through. The whole row opens the booking; the tick beside a guessed category accepts the guess
// without opening anything. Money that only moved between own accounts (savings, the depot, round-ups)
// is neither spent nor earned: it shows in grey without a sign, after the day's real bookings, both of
// its sides as one row ("Girokonto → Extra-Konto"), and isn't in the day's sum. With ``fold``, a day's
// round-ups (and several moves of one payee) are one line that opens up.
export function TxList({ items, byDay, onOpen, accepted, onAccept, showAccount = true, fold = false }: {
  items: Tx[];
  byDay: boolean;
  onOpen: (tx: Tx) => void;
  accepted?: Set<number>;
  onAccept?: (tx: Tx, el: Element) => void;
  showAccount?: boolean;
  fold?: boolean;
}) {
  useT();
  const [open, setOpen] = useState<Set<string>>(() => new Set());
  const groups = useMemo(() => {
    const out: { day: string; sum: number; real: number; items: Tx[]; entries: Entry[] }[] = [];
    for (const tx of items) {
      const last = out[out.length - 1];
      const g = byDay && last && last.day === tx.date ? last : null;
      if (g) g.items.push(tx);
      else out.push({ day: tx.date, sum: 0, real: 0, items: [tx], entries: [] });
      const cur = g ?? out[out.length - 1];
      if (!tx.move) {
        cur.sum += counted(tx);
        cur.real += 1;
      }
    }
    const listed = new Map(items.map((tx) => [tx.id, tx]));
    for (const g of out) g.entries = dayEntries(g.items, listed, byDay, fold);
    return out;
  }, [items, byDay, fold]);
  let n = 0;

  const row = ({ tx, other }: Row, inner = false) => {
    const review = tx.needs_review === 1;
    const mv = !!tx.move;
    const done = accepted?.has(tx.id);
    const color = tx.category_color ? colorVar(tx.category_color) : "var(--c-muted)";
    const guessed = review && tx.cat_source === "model";
    const extra = veil(
      [tx.note, tx.counts_for ? t("tx.countsFor", { month: monthLong(tx.counts_for) }) : null, tx.detail ?? (tx.purpose !== tx.merchant ? tx.purpose : null)]
        .filter(Boolean)
        .join(" · "),
    );
    const back = !!tx.refund_for || (!!tx.refunded && tx.amount < 0);
    return (
      <div
        key={tx.id}
        className={`txl-row${mv ? " move" : ""}${review && !done ? " review" : ""}${done ? " accepted" : ""}${inner ? " inner" : ""}`}
        style={{ ["--c" as string]: color, ["--i" as string]: Math.min(n++, 14) }}
      >
        <button
          type="button"
          className="txl-hit"
          onClick={() => onOpen(tx)}
          aria-label={t("tx.open", { merchant: tx.merchant, amount: eur(mv ? Math.abs(tx.amount) : tx.amount), date: dateShort(tx.date) })}
        />
        {other ? (
          <span className="txl-av swap" aria-hidden="true">
            <Icon name="swap" size={16} />
          </span>
        ) : (
          <MerchantAv name={tx.merchant} />
        )}
        <span className="txl-main">
          <span className="txl-name">
            <span className="txl-nm">{tx.merchant}</span>
            {!byDay && <small>{dateShort(tx.date)}</small>}
          </span>
          {(extra || back || (mv && !inner)) && (
            <span className="txl-sub">
              {mv && !inner && <span className="txl-route">{route(tx)}</span>}
              {mv && !inner && extra && " · "}
              {back && <BackLine tx={tx} />}
              {back && extra && " · "}
              {extra}
            </span>
          )}
        </span>
        <span className="txl-cat">
          {inner ? null : tx.category ? (
            <span className={`catchip${guessed && !done ? " ai" : ""}`} title={guessed && !done ? t("tx.guessedTitle") : undefined}>
              <span className="sq" />
              {catName(tx.category)}
            </span>
          ) : (
            <span className="catchip unc">{t("tx.uncategorized")}</span>
          )}
          {review && tx.category && onAccept && !done && (
            <button type="button" className="ib sm accept" title={t("tx.guessRight")} aria-label={t("tx.accept", { merchant: tx.merchant })} onClick={(e) => onAccept(tx, e.currentTarget)}>
              <Icon name="check" size={14} />
            </button>
          )}
          {done && (
            <span className="txl-ok" aria-hidden="true">
              <Icon name="check" size={14} />
            </span>
          )}
        </span>
        {showAccount && <span className="txl-acct">{mv ? null : tx.account}</span>}
        {mv ? (
          <span className="txl-amt moved">
            <TxAmount tx={{ ...tx, amount: Math.abs(tx.amount), orig_amount: tx.orig_amount == null ? null : Math.abs(tx.orig_amount) }} />
          </span>
        ) : (
          <span className={`txl-amt${tx.amount > 0 ? " pos" : ""}${allBack(tx) ? " gone" : ""}`}>
            <TxAmount tx={tx} />
          </span>
        )}
      </div>
    );
  };

  // A day's round-ups (or moves of one payee) in one quiet line; a click shows each of them.
  const foldRow = ({ key, rows, roundup }: Fold) => {
    const isOpen = open.has(key);
    const first = rows[0].tx;
    const sum = rows.reduce((s, r) => s + Math.abs(counted(r.tx)), 0);
    const toggle = () =>
      setOpen((o) => {
        const next = new Set(o);
        if (isOpen) next.delete(key);
        else next.add(key);
        return next;
      });
    const label = { n: rows.length, merchant: first.merchant, amount: eur(sum) };
    return (
      <Fragment key={`fold-${key}`}>
        <div
          className={`txl-row move fold${isOpen ? " open" : ""}`}
          style={{ ["--c" as string]: first.category_color ? colorVar(first.category_color) : "var(--c-muted)", ["--i" as string]: Math.min(n++, 14) }}
        >
          <button type="button" className="txl-hit" aria-expanded={isOpen} onClick={toggle} aria-label={t(roundup ? "tx.roundups.open" : "tx.moves.open", label)} />
          {roundup ? (
            <span className="txl-av" aria-hidden="true">
              <Icon name="coin" size={16} />
            </span>
          ) : (
            <MerchantAv name={first.merchant} />
          )}
          <span className="txl-main">
            <span className="txl-name">
              <span className="txl-nm">{first.merchant}</span>
            </span>
            <span className="txl-sub">
              {t(roundup ? "tx.roundups" : "tx.moves", { n: rows.length })}
              {" · "}
              <span className="txl-route">{route(first)}</span>
              <Icon name="chevDown" size={12} />
            </span>
          </span>
          <span className="txl-cat">
            {first.category && (
              <span className="catchip">
                <span className="sq" />
                {catName(first.category)}
              </span>
            )}
          </span>
          {showAccount && <span className="txl-acct" />}
          <span className="txl-amt moved">{eur(sum)}</span>
        </div>
        {isOpen && rows.map((r) => row(r, true))}
      </Fragment>
    );
  };

  return (
    <div className={`txl${showAccount ? "" : " noacct"}`}>
      {groups.map((g) => (
        <section key={`${g.day}-${g.items[0].id}`} className="txl-group">
          {byDay && (
            <h3 className="txl-day">
              <span>{dayHead(g.day)}</span>
              {g.real > 1 && <span className={g.sum > 0 ? "pos" : undefined}>{eur(g.sum)}</span>}
            </h3>
          )}
          {g.entries.map((e) => ("tx" in e ? row(e) : foldRow(e)))}
        </section>
      ))}
    </div>
  );
}
