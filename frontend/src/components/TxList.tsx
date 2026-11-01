import { Fragment, useMemo, useState } from "react";
import { catName, locale, t, useT } from "../i18n";
import { colorVar, dateShort, daysFrom, eur, initial, money, monthLong, veil } from "../lib/format";
import type { Tx } from "../lib/types";
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

type Entry = { tx: Tx } | { day: string; roundups: Tx[] };

// The one way a list of bookings looks, on Transactions and on every detail page: grouped by day with
// the day's sum (when sorted by date and the day has more than one), each row a softly tinted initial
// in the category's colour, the payee with its note or purpose, the category, the account and the
// amount. Money that came back shows on both bookings, and a payment that came back whole is struck
// through. The whole row opens the booking; the tick beside a guessed category accepts the guess
// without opening anything. With ``fold``, a day's Kleingeld Plus round-ups are one line that opens up.
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
    const out: { day: string; sum: number; items: Tx[]; entries: Entry[] }[] = [];
    for (const tx of items) {
      const last = out[out.length - 1];
      if (byDay && last && last.day === tx.date) {
        last.items.push(tx);
        last.sum += counted(tx);
      } else out.push({ day: tx.date, sum: counted(tx), items: [tx], entries: [] });
    }
    for (const g of out) {
      const roundups = fold && byDay ? g.items.filter((tx) => tx.roundup && tx.needs_review !== 1) : [];
      const folded = roundups.length > 1 ? new Set(roundups) : null;
      for (const tx of g.items) {
        if (!folded?.has(tx)) g.entries.push({ tx });
        else if (tx === roundups[0]) g.entries.push({ day: g.day, roundups });
      }
    }
    return out;
  }, [items, byDay, fold]);
  let n = 0;

  const row = (tx: Tx, inner = false) => {
    const review = tx.needs_review === 1;
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
        className={`txl-row${review && !done ? " review" : ""}${done ? " accepted" : ""}${inner ? " inner" : ""}`}
        style={{ ["--c" as string]: color, ["--i" as string]: Math.min(n++, 14) }}
      >
        <button type="button" className="txl-hit" onClick={() => onOpen(tx)} aria-label={t("tx.open", { merchant: tx.merchant, amount: eur(tx.amount), date: dateShort(tx.date) })} />
        <span className="txl-av" aria-hidden="true">
          {initial(tx.merchant)}
        </span>
        <span className="txl-main">
          <span className="txl-name">
            <span className="txl-nm">{tx.merchant}</span>
            {!byDay && <small>{dateShort(tx.date)}</small>}
          </span>
          {(extra || back) && (
            <span className="txl-sub">
              {back && <BackLine tx={tx} />}
              {back && extra && " · "}
              {extra}
            </span>
          )}
        </span>
        <span className="txl-cat">
          {tx.category ? (
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
        {showAccount && <span className="txl-acct">{tx.account}</span>}
        <span className={`txl-amt${tx.amount > 0 ? " pos" : ""}${allBack(tx) ? " gone" : ""}`}>
          <TxAmount tx={tx} />
        </span>
      </div>
    );
  };

  // A day's round-ups in one quiet line; a click shows each of them.
  const roundupRow = (day: string, list: Tx[]) => {
    const isOpen = open.has(day);
    const first = list[0];
    const sum = list.reduce((s, tx) => s + counted(tx), 0);
    const toggle = () =>
      setOpen((o) => {
        const next = new Set(o);
        if (isOpen) next.delete(day);
        else next.add(day);
        return next;
      });
    return (
      <Fragment key={`fold-${day}`}>
        <div
          className={`txl-row fold${isOpen ? " open" : ""}`}
          style={{ ["--c" as string]: first.category_color ? colorVar(first.category_color) : "var(--c-muted)", ["--i" as string]: Math.min(n++, 14) }}
        >
          <button type="button" className="txl-hit" aria-expanded={isOpen} onClick={toggle} aria-label={t("tx.roundups.open", { n: list.length, amount: eur(sum) })} />
          <span className="txl-av" aria-hidden="true">
            <Icon name="coin" size={16} />
          </span>
          <span className="txl-main">
            <span className="txl-name">
              <span className="txl-nm">{first.merchant}</span>
            </span>
            <span className="txl-sub">
              {t("tx.roundups", { n: list.length })}
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
          {showAccount && <span className="txl-acct">{first.account}</span>}
          <span className="txl-amt">{eur(sum)}</span>
        </div>
        {isOpen && list.map((tx) => row(tx, true))}
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
              {g.items.length > 1 && <span className={g.sum > 0 ? "pos" : undefined}>{eur(g.sum)}</span>}
            </h3>
          )}
          {g.entries.map((e) => ("tx" in e ? row(e.tx) : roundupRow(e.day, e.roundups)))}
        </section>
      ))}
    </div>
  );
}
