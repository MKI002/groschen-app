import { useEffect, useState } from "react";
import { CategoryPicker } from "../components/CategoryPicker";
import { searchEgg } from "../components/Eggs";
import { FilterBar, filterQuery, useTxFilters } from "../components/Filters";
import { Icon } from "../components/Icons";
import { celebrate } from "../components/Motion";
import { LinkAsk, MoneyBackFor, PaymentBack, PaymentPicker } from "../components/Refunds";
import { TxList } from "../components/TxList";
import { Card, Empty, ErrorNote, IconBadge, Loading, Modal, Seg, Spinner, Switch, useApi, useSyncEvents, useToast } from "../components/UI";
import { api, qs } from "../lib/api";
import { t, useT, type Key } from "../i18n";
import { periodQuery, useApp } from "../lib/app";
import { dateShort, dayLabel, eur, int, monthLong, veil } from "../lib/format";
import { drillPath, navigate, useSearch } from "../lib/router";
import type { RefundCandidate, RefundInfo, Tx, TxBrief, TxPage } from "../lib/types";
import { PageHeader, periodLabel } from "./Shell";

const FILTERS: [string, Key][] = [
  ["all", "tx.all"],
  ["review", "tx.needsReview"],
  ["unc", "tx.uncategorized"],
  ["income", "cf.income"],
];
const PAGE = 200;
// Bookings Groschen recognised as not spent, and why (shown in the booking's details).
const WHY: Record<string, [string, Key]> = {
  own: ["bank", "why.own"],
  transfer: ["bank", "why.transfer"],
};
// Money in these categories is plainly earned, never money back for a payment.
const EARNED = new Set(["Salary", "Interest & dividends"]);

// What the closed dialog says, with a way to take the change back when there is one.
export type Saved = { msg: string; undo?: () => Promise<unknown> };

// After the booking dialog: close it, say what happened and fetch the page again.
export function useTxSaved(close: () => void, reload: () => void, refresh: () => void) {
  const toast = useToast();
  return (n: number, note?: Saved) => {
    close();
    const again = () => {
      reload();
      refresh();
    };
    const undo = note?.undo;
    toast(note?.msg ?? (n ? t("tx.savedMore", { n }) : t("tx.saved")), undo && { label: t("rf.undo"), run: () => void undo().then(again, (e: Error) => toast(e.message)) });
    again();
  };
}

// One booking: what the bank sent, its category (with "the same for this payee"), whether it is a
// subscription, a note, and the way to everything else from this payee. Money that came back shows
// the payment it belongs to (and a payment what came back for it); money that came in and isn't
// linked can be linked to the payment it came back for.
export function EditTx({ tx, onClose, onSaved }: { tx: Tx; onClose: () => void; onSaved: (changed: number, note?: Saved) => void }) {
  useT();
  const [cat, setCat] = useState<number | null>(tx.category_id);
  const [similar, setSimilar] = useState(true);
  const [note, setNote] = useState(tx.note ?? "");
  const [sub, setSub] = useState<"yes" | "no" | "auto">(tx.subscription ?? "auto");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [picking, setPicking] = useState(false);
  const [linking, setLinking] = useState<number | null>(null);
  const backFor = !!tx.refund_for;
  const { data: back } = useApi<RefundInfo>(backFor || (tx.refunded && tx.amount < 0) ? `/transactions/${tx.id}/refund` : null);
  const canLink = tx.amount > 0 && !backFor && !(tx.cat_source && tx.cat_source in WHY) && !EARNED.has(tx.category ?? "");

  async function unlink(refund: TxBrief) {
    const to = back?.purchase?.id;
    setLinking(refund.id);
    try {
      await api.del(`/transactions/${refund.id}/refund`);
      onSaved(0, { msg: t("rf.unlinked"), undo: to ? () => api.put(`/transactions/${refund.id}/refund`, { purchase_id: to }) : undefined });
    } catch (e) {
      setError((e as Error).message);
      setLinking(null);
    }
  }
  async function link(c: RefundCandidate) {
    setLinking(c.id);
    try {
      await api.put(`/transactions/${tx.id}/refund`, { purchase_id: c.id });
      onSaved(0, { msg: t("rf.linked", { merchant: c.merchant }) });
    } catch (e) {
      setError((e as Error).message);
      setLinking(null);
    }
  }

  async function save() {
    setBusy(true);
    try {
      const r = await api.patch<{ also_changed: number }>(`/transactions/${tx.id}`, {
        category_id: cat, note, apply_to_similar: similar, set_category: cat !== tx.category_id || tx.needs_review === 1,
      });
      if (sub !== (tx.subscription ?? "auto")) await api.post(`/transactions/${tx.id}/subscription`, { state: sub });
      onSaved(r.also_changed);
    } catch (e) {
      setError((e as Error).message);
      setBusy(false);
    }
  }
  const lines = ([tx.counterparty && tx.counterparty !== tx.merchant ? tx.counterparty : null, tx.purpose, tx.booking_text].filter(Boolean) as string[]).map(veil);

  if (picking)
    return (
      <Modal
        title={t("rf.pickTitle")}
        onClose={onClose}
        actions={
          <button className="btn ghost" onClick={() => setPicking(false)} disabled={linking !== null}>
            {t("common.back")}
          </button>
        }
      >
        <PaymentPicker tx={tx} busy={linking} onPick={link} />
        {error && <p className="err">{error}</p>}
      </Modal>
    );

  return (
    <Modal
      title={tx.merchant}
      onClose={onClose}
      actions={
        <>
          <button
            className="btn ghost"
            onClick={() => {
              onClose();
              navigate(drillPath({ merchant: tx.merchant }));
            }}
          >
            {t("tx.everything", { merchant: tx.merchant })}
            <Icon name="chevRight" size={14} />
          </button>
          <span className="grow" />
          <button className="btn primary" onClick={save} disabled={busy}>
            {busy && <Spinner />}
            {t("common.save")}
          </button>
        </>
      }
    >
      <div className="txhead">
        <span className={`txhead-amt${tx.amount > 0 ? " pos" : ""}`}>{eur(tx.amount)}</span>
        <span className="muted">
          {dayLabel(tx.date)} · {tx.account}
        </span>
        {tx.counts_for && <span className="tag">{t("tx.countsForLong", { month: monthLong(tx.counts_for) })}</span>}
      </div>
      {tx.cat_source && tx.cat_source in WHY && (
        <p className="why">
          <Icon name={WHY[tx.cat_source][0]} size={14} />
          {t(WHY[tx.cat_source][1])}
        </p>
      )}
      {backFor && back && <MoneyBackFor tx={tx} info={back} busy={linking !== null} onUnlink={() => unlink(tx)} onPick={() => setPicking(true)} />}
      {!backFor && back && back.refunds.length > 0 && <PaymentBack tx={tx} info={back} busy={linking} onUnlink={unlink} />}
      {lines.length > 0 && (
        <div className="txraw">
          {lines.map((l, i) => (
            <span key={i}>{l}</span>
          ))}
        </div>
      )}
      {canLink && <LinkAsk onPick={() => setPicking(true)} />}
      {!backFor && (
        <>
          <div className="field">
            <span className="label">{t("tx.category")}</span>
            <CategoryPicker value={cat} onPick={setCat} amount={tx.amount} />
          </div>
          <div className="setrow tight">
            <span>{t("tx.similar")}</span>
            <Switch checked={similar} onChange={setSimilar} label={t("tx.similar")} />
          </div>
          <div className="setrow tight">
            <span>{t("tx.sub")}</span>
            <Seg<"auto" | "yes" | "no">
              label={t("tx.sub")}
              value={sub}
              onChange={setSub}
              options={[
                ["auto", t("tx.sub.auto")],
                ["yes", t("tx.sub.yes")],
                ["no", t("tx.sub.no")],
              ]}
            />
          </div>
        </>
      )}
      <div className="field">
        <label htmlFor="tx-note">{t("tx.note")}</label>
        <input className="input" id="tx-note" value={note} maxLength={500} placeholder={t("tx.notePh")} onChange={(e) => setNote(e.target.value)} />
      </div>
      {error && <p className="err">{error}</p>}
    </Modal>
  );
}

export default function Transactions() {
  const { refresh, badges, period } = useApp();
  useT();
  const toast = useToast();
  const params = useSearch();
  const initialFilter = params.get("filter") ?? "all";
  const f = useTxFilters(params.get("q") ?? "");
  const [filter, setFilter] = useState(FILTERS.some(([x]) => x === initialFilter) ? initialFilter : "all");
  // A day picked in the year heatmap (or any from/to link) narrows the list until it is cleared.
  const [days, setDays] = useState<{ from: string; to: string } | null>(() => {
    const from = params.get("from"), to = params.get("to");
    return from && /^\d{4}-\d{2}-\d{2}$/.test(from) ? { from, to: to && /^\d{4}-\d{2}-\d{2}$/.test(to) ? to : from } : null;
  });
  const [limit, setLimit] = useState(PAGE);
  const [editing, setEditing] = useState<Tx | null>(null);
  const [accepted, setAccepted] = useState<Set<number>>(new Set());
  const [bulk, setBulk] = useState(false);
  const fq = filterQuery(f);
  // The list follows the shared period, except the review queue (a to-do list) and a picked day.
  const everything = filter === "review" || !!days;
  const range = everything ? { preset: "all", anchor: undefined } : periodQuery(period);
  useEffect(() => setLimit(PAGE), [fq.q, fq.account_id, fq.min, fq.max, fq.sort, fq.dir, filter, days, range.preset, range.anchor]);
  // Searching for the right words finds more than bookings.
  useEffect(() => {
    if (f.query) searchEgg(f.query, toast);
  }, [f.query, toast]);

  const { data, error, loading, reload } = useApi<TxPage>(`/transactions${qs({ ...fq, filter, limit, ...range, from: days?.from, to: days?.to })}`);
  useSyncEvents(reload);
  const saved = useTxSaved(() => setEditing(null), reload, refresh);
  const byDay = f.sort === "date";
  const after = () =>
    window.setTimeout(() => {
      reload();
      refresh();
    }, 450);

  async function accept(tx: Tx, el: Element) {
    setAccepted((s) => new Set(s).add(tx.id));
    try {
      const r = await api.post<{ also_changed: number }>(`/transactions/${tx.id}/reviewed`);
      if (data && data.review <= 1 + r.also_changed) {
        celebrate(el, 18);
        toast(t("tx.allCaughtUp"));
      } else if (r.also_changed) {
        toast(t("tx.learned", { n: r.also_changed, merchant: tx.merchant }));
      }
    } catch (e) {
      toast((e as Error).message);
    }
    after();
  }

  // "All fine": every guess on the list is taken as it is, in one go.
  const guesses = (data?.items ?? []).filter((x) => x.needs_review === 1 && x.category_id !== null && !accepted.has(x.id));
  async function acceptAll(el: Element) {
    setBulk(true);
    const ids = guesses.map((x) => x.id);
    setAccepted((s) => new Set([...s, ...ids]));
    try {
      const r = await api.post<{ accepted: number }>("/transactions/reviewed", { ids });
      celebrate(el, 24);
      toast(t("tx.acceptedAll", { n: r.accepted }));
    } catch (e) {
      toast((e as Error).message);
    }
    setBulk(false);
    after();
  }

  const quick = (
    <Seg
      label={t("tx.show")}
      value={filter}
      onChange={setFilter}
      options={FILTERS.map(([key, label]) => [
        key,
        key === "review" && badges?.review ? (
          <>
            {t(label)} <span className="n">{badges.review}</span>
          </>
        ) : (
          t(label)
        ),
      ])}
    />
  );

  return (
    <>
      <PageHeader title={t("nav.transactions")} period />
      <FilterBar f={f}>{quick}</FilterBar>
      {filter === "review" && data && (
        <div className="reviewbar">
          <IconBadge name="spark" tone="accent" size={38} />
          <span className="rb-txt">
            {guesses.length ? (
              <>
                <b>{t("tx.review.title", { n: guesses.length })}</b> {t("tx.review.text")}
              </>
            ) : (
              <b>{t("tx.review.none")}</b>
            )}
          </span>
          {guesses.length > 1 && (
            <button className="btn primary" disabled={bulk} onClick={(e) => acceptAll(e.currentTarget)}>
              {bulk ? <Spinner /> : <Icon name="check" size={15} />}
              {t("tx.acceptAll", { n: guesses.length })}
            </button>
          )}
        </div>
      )}
      {data && (
        <div className="txsum">
          {days ? (
            <button className="chip on" onClick={() => setDays(null)} aria-label={t("tx.clearDay")}>
              {days.from === days.to ? dayLabel(days.from) : `${dateShort(days.from)} – ${dateShort(days.to)}`}
              <Icon name="x" size={13} />
            </button>
          ) : (
            <span>{everything ? t("tx.allPeriods") : periodLabel(period)}</span>
          )}
          <span>{t("dd.txCount", { n: data.total })}</span>
          {data.in > 0 && <span className="pos">{t("tx.in", { amount: eur(data.in) })}</span>}
          {data.out !== 0 && <span>{t("tx.out", { amount: eur(data.out) })}</span>}
          {(f.filtered || days) && (
            <button
              className="linkbtn"
              onClick={() => {
                f.reset();
                setDays(null);
              }}
            >
              {t("dd.clearFilters")}
            </button>
          )}
          {loading && <Spinner />}
        </div>
      )}
      <ErrorNote error={error} />
      {!data && !error && <Loading />}
      {data && (
        <Card className="txcard">
          {data.items.length ? (
            <TxList items={data.items} byDay={byDay} onOpen={setEditing} accepted={accepted} onAccept={accept} fold={!f.filtered && filter === "all"} />
          ) : filter === "review" && !f.filtered ? (
            <Empty title={t("tx.review.done")} icon="check">
              {t("tx.review.doneText")}
            </Empty>
          ) : (
            <Empty title={t("tx.noMatch")} icon="search">
              {t("tx.noMatch.text")}
            </Empty>
          )}
          {data.items.length < data.total && (
            <div className="pager">
              <button className="btn sm" onClick={() => setLimit((l) => l + PAGE)} disabled={loading}>
                {t("tx.more", { left: int(data.total - data.items.length) })}
              </button>
            </div>
          )}
        </Card>
      )}
      {editing && <EditTx tx={editing} onClose={() => setEditing(null)} onSaved={saved} />}
    </>
  );
}
