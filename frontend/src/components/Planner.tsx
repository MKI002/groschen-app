import { useEffect, useMemo, useState, type ReactNode } from "react";
import { catName, locale, useT, type TKey } from "../i18n";
import { api } from "../lib/api";
import { useApp } from "../lib/app";
import { dateShort, dayMonth, daysFrom, eur, intervalName, monthLong, relDay } from "../lib/format";
import { navigate } from "../lib/router";
import type { Alert, Available, Insight, PlannedCharge, SettingsValues, SubEvent } from "../lib/types";
import { Icon } from "./Icons";
import { Odometer } from "./Motion";
import { LiquidTank } from "./Showpiece";
import { Card, IconBadge, Modal, useApi, useSyncEvents, useToast, type Tone } from "./UI";

const weekday = (iso: string) => new Date(`${iso}T12:00:00`).toLocaleDateString(locale(), { weekday: "short", day: "numeric", month: "short" });

// --- free until payday ----------------------------------------------------------------------------

type HasAccount = Extract<Available, { has_account: true }>;

// What is left of the Girokonto once every fixed cost before the next salary is paid: one big number,
// the salary month as a chain of days with every charge on it, and the tank that shows how full it still is.
// The list and the sum behind the number are one click away.
export function PaydayHero() {
  const t = useT();
  const { data, reload } = useApi<Available>("/available");
  const [open, setOpen] = useState(false);
  useSyncEvents(reload);
  if (!data) return <section className="card hero wait" aria-hidden="true" />;
  if (!data.has_account) return null;
  const d = data;
  const short = d.available < 0;
  const level = d.balance > 0 ? Math.max(0, d.available) / d.balance : 0;
  return (
    <section className="card hero">
      <div className="hero-body">
        <div className="eyebrow">{d.payday ? t("avail.title") : t("avail.titleMonth")}</div>
        <div className={`hero-v${short ? " neg" : ""}`}>
          <Odometer value={d.available} />
        </div>
        <p className="hero-sub">
          {short ? <b className="neg">{t("avail.short", { amount: eur(-d.available) })}</b> : <b>{t("avail.perDay", { amount: eur(d.per_day) })}</b>}
        </p>
        <Runway d={d} onOpen={() => setOpen(true)} />
        {d.balance_age_days > 7 && <p className="hero-note">{t("avail.stale", { n: d.balance_age_days })}</p>}
      </div>
      <LiquidTank level={level} label={t("avail.tankLabel", { p: Math.round(level * 100) })} />
      {open && <PaydayDetails d={d} onClose={() => setOpen(false)} />}
    </section>
  );
}

// The salary month as a chain of days, from the last salary on the left to payday on the right.
// Days gone by are filled, today glows and the days still to come are open, so how far the month
// has run shows from across the room. Every charge still to come sits on its day, bigger the more
// it costs; a click on one (or the line under the chain) lists them all.
function Runway({ d, onOpen }: { d: HasAccount; onOpen: () => void }) {
  const t = useT();
  const total = Math.max(1, -daysFrom(d.since, new Date(`${d.until}T12:00:00`)));
  const now = Math.min(total - 1, Math.max(0, -daysFrom(d.since)));
  const marks = useMemo(() => {
    const byDay = new Map<number, PlannedCharge[]>();
    // A charge a few days late is still to come: it sits on today.
    for (const u of d.upcoming) {
      const i = Math.min(total - 1, Math.max(now, now + daysFrom(u.date)));
      byDay.set(i, [...(byDay.get(i) ?? []), u]);
    }
    const max = Math.max(1, ...[...byDay.values()].map((l) => l.reduce((a, u) => a + u.amount, 0)));
    return new Map(
      [...byDay.entries()].map(([i, list]) => {
        const sum = list.reduce((a, u) => a + u.amount, 0);
        return [i, { list, sum, size: 5 + 6 * Math.sqrt(sum / max), transfer: list.every((u) => u.kind === "transfer") }];
      }),
    );
  }, [d.upcoming, total, now]);
  const left = d.days;
  const at = (now + 0.5) / total;
  return (
    <div className="runway">
      <div className={`rw-now${at > 0.62 ? " end" : ""}`} style={{ ["--x" as string]: `${(at * 100).toFixed(2)}%` }}>
        <span className="rw-today-l">{t("day.today")}</span>
        {d.payday?.late ? (
          <span>{t("avail.due")}</span>
        ) : (
          <>
            <b>{left}</b>
            <span>{t(d.payday ? "avail.left" : "avail.leftMonth", { n: left })}</span>
          </>
        )}
      </div>
      <div className="rw-chain">
        <div className={`rw-days${total > 40 ? " dense" : ""}`} style={{ ["--n" as string]: total }}>
          {Array.from({ length: total }, (_, i) => {
            const m = marks.get(i);
            const when = i < now ? "past" : i === now ? "today" : "next";
            return (
              <span
                key={i}
                className={`rw-d ${when}`}
                style={{ ["--i" as string]: i, ["--a" as string]: when === "past" ? (0.34 + 0.46 * (i / Math.max(1, now))).toFixed(2) : undefined }}
              >
                {m && (
                  <button
                    type="button"
                    className={`rw-mark${m.transfer ? " transfer" : ""}${i / total > 0.8 ? " end" : i / total < 0.15 ? " start" : ""}`}
                    style={{ ["--s" as string]: `${m.size.toFixed(1)}px` }}
                    data-tip={`${m.list.map((u) => u.name).join(", ")} · ${eur(-m.sum)} · ${relDay(m.list[0].date)}`}
                    aria-label={`${relDay(m.list[0].date)}: ${m.list.map((u) => `${u.name} ${eur(u.amount)}`).join(", ")}`}
                    onClick={onOpen}
                  />
                )}
              </span>
            );
          })}
        </div>
        <span className="rw-pay" aria-hidden="true">
          <Icon name="coin" size={16} />
        </span>
      </div>
      <div className="rw-legend">
        <span>{d.payday ? t("avail.salaryOn", { date: dayMonth(d.since) }) : dayMonth(d.since)}</span>
        <button type="button" className="linkbtn rw-open" onClick={onOpen}>
          {d.upcoming.length ? t("avail.charges", { n: d.upcoming.length, amount: eur(d.fixed_total) }) : t("avail.noCharges")}
          <Icon name="chevRight" size={13} />
        </button>
        <span>{d.payday ? weekday(d.until) : t("avail.monthEnd")}</span>
      </div>
    </div>
  );
}

// The sum behind the big number, and every charge still to come.
function PaydayDetails({ d, onClose }: { d: HasAccount; onClose: () => void }) {
  const t = useT();
  return (
    <Modal
      title={d.payday ? t("avail.title") : t("avail.titleMonth")}
      onClose={onClose}
      actions={
        <button
          className="btn"
          onClick={() => {
            onClose();
            navigate("/recurring?view=calendar");
          }}
        >
          <Icon name="calendar" size={15} />
          {t("avail.calendar")}
        </button>
      }
    >
      <div className="paysum">
        <div className="sum-row">
          <span>{d.balance_age_days > 2 ? t("avail.balanceOn", { date: dateShort(d.balance_date) }) : t("avail.balanceNow")}</span>
          <b>{eur(d.balance)}</b>
        </div>
        <div className="sum-row">
          <span>{t("avail.goingOut", { n: d.upcoming.length })}</span>
          <b>{eur(-d.fixed_total)}</b>
        </div>
        {d.buffer > 0 && (
          <div className="sum-row">
            <span>{t("avail.keptAside")}</span>
            <b>{eur(-d.buffer)}</b>
          </div>
        )}
        <div className="sum-row total">
          <span>{t("avail.free")}</span>
          <b className={d.available < 0 ? "neg" : "pos"}>{eur(d.available)}</b>
        </div>
      </div>
      {d.upcoming.length > 0 && (
        <ul className="plainlist">
          {d.upcoming.map((u, i) => (
            <li key={`${u.date}-${u.name}-${i}`} className="stagger" style={{ ["--i" as string]: i }}>
              <span className="pl-when">{relDay(u.date)}</span>
              <span className="pl-what">
                <b>{u.name}</b>
                <small>{u.kind === "transfer" ? t("avail.standing") : intervalName(u.interval)}</small>
              </span>
              <span className="pl-amt">{eur(-u.amount)}</span>
            </li>
          ))}
        </ul>
      )}
      {!!d.buffer && <p className="muted small">{t("avail.bufferNote")}</p>}
    </Modal>
  );
}

// --- worth a look -----------------------------------------------------------------------------------

// "Nach 4 Monaten Pause": a pause in days, said the way people say it.
function spanText(t: ReturnType<typeof useT>, days: number) {
  if (days < 14) return t("span.days", { n: days });
  if (days < 60) return t("span.weeks", { n: Math.round(days / 7) });
  if (days < 730) return t("span.months", { n: Math.round(days / 30.44) });
  return t("span.years", { n: Math.round(days / 365.25) });
}

// What changed with a recurring payment, in one sentence: the Overview hints and the Fixed costs page
// say it the same way.
export function SubEventText({ e }: { e: SubEvent }) {
  const t = useT();
  switch (e.kind) {
    case "price_up":
    case "price_down":
      return (
        <>
          <b>{t(e.kind === "price_up" ? "hint.price" : "hint.cheaper", { name: e.name })}</b>
          {t(e.kind === "price_up" ? "hint.priceMore" : "hint.cheaperMore", {
            from: eur(e.from),
            to: eur(e.to),
            date: dateShort(e.date),
            year: eur(Math.abs(e.per_year ?? 0)),
          })}
        </>
      );
    case "new":
      return (
        <>
          <b>{t("hint.subNew", { name: e.name })}</b>
          {t("hint.subNewMore", { amount: eur(e.amount), interval: intervalName(e.interval), date: dateShort(e.since ?? e.date) })}
        </>
      );
    case "ended":
      return (
        <>
          <b>{t("hint.subEnded", { name: e.name })}</b>
          {t("hint.subEndedMore", { amount: eur(e.amount), date: dateShort(e.last_date ?? e.date), year: eur(e.monthly_cost * 12) })}
        </>
      );
    default:
      return (
        <>
          <b>{t("hint.subResumed", { name: e.name })}</b>
          {t("hint.subResumedMore", { pause: spanText(t, e.pause_days ?? 0), amount: eur(e.amount), interval: intervalName(e.interval) })}
        </>
      );
  }
}

const AS_EVENT: Record<string, SubEvent["kind"]> = { price_up: "price_up", price_down: "price_down", sub_new: "new", sub_ended: "ended", sub_resumed: "resumed" };

function AlertText({ a }: { a: Alert }) {
  const t = useT();
  if (a.kind === "duplicate") {
    return (
      <>
        <b>{t("hint.dup", { name: a.name, amount: eur(a.amount) })}</b>
        {t("hint.dupMore", { first: dateShort(a.first_date), second: dateShort(a.date) })}
      </>
    );
  }
  if (a.kind === "unusual") {
    const why =
      a.basis === "new"
        ? t("hint.new")
        : a.basis === "merchant"
          ? t("hint.usual", { amount: eur(a.usual) })
          : t("hint.usualCat", { amount: eur(a.usual), category: a.category ? catName(a.category) : t("hint.thisCat") });
    return (
      <>
        <b>{t("hint.big", { amount: eur(a.amount), name: a.name })}</b>
        {t("hint.bigOn", { date: dateShort(a.date) })}
        {why}
      </>
    );
  }
  return <SubEventText e={{ ...a, kind: AS_EVENT[a.kind] }} />;
}

// The symbol and colour for each kind of change, on the Overview and the Fixed costs page alike.
export const EVENT_LOOK: Record<SubEvent["kind"], [string, Tone]> = {
  price_up: ["up", "warn"],
  price_down: ["down", "good"],
  new: ["spark", "info"],
  ended: ["ban", "muted"],
  resumed: ["play", "info"],
};

const ALERT_LOOK: Record<Alert["kind"], [string, Tone]> = {
  duplicate: ["repeat", "bad"],
  price_up: EVENT_LOOK.price_up,
  price_down: EVENT_LOOK.price_down,
  sub_new: EVENT_LOOK.new,
  sub_ended: EVENT_LOOK.ended,
  sub_resumed: EVENT_LOOK.resumed,
  unusual: ["warn", "warn"],
};

// The setting behind each kind of hint, for "Don't show again".
type HintSetting = "alert_duplicates" | "alert_price_up" | "alert_subscriptions" | "alert_unusual" | "unusual_alerts";
const ALERT_SETTING: Record<Alert["kind"], HintSetting> = {
  duplicate: "alert_duplicates",
  price_up: "alert_price_up",
  price_down: "alert_price_up",
  sub_new: "alert_subscriptions",
  sub_ended: "alert_subscriptions",
  sub_resumed: "alert_subscriptions",
  unusual: "alert_unusual",
};

// Close (hides this one hint for good) and "Don't show again" (turns this kind off).
// Both can be undone under Settings, Hints.
function HintClose({ hintKey, setting, onGone }: { hintKey: string; setting: HintSetting; onGone: () => void }) {
  const t = useT();
  const toast = useToast();
  const { refresh } = useApp();
  const changed = () => {
    refresh();
    window.dispatchEvent(new Event("groschen:hints"));
  };
  // Hide this one; the note that follows offers to stop this kind of hint altogether.
  async function dismiss() {
    try {
      await api.post("/alerts/dismiss", { key: hintKey });
      onGone();
      changed();
      toast(t("hint.closed"), {
        label: t("hint.never"),
        run: async () => {
          try {
            await api.patch("/settings", { [setting]: false } satisfies Partial<SettingsValues>);
            changed();
            toast(t("hint.kindOff"));
          } catch (e) {
            toast((e as Error).message);
          }
        },
      });
    } catch (e) {
      toast((e as Error).message);
    }
  }
  return (
    <button className="ib sm hint-close" aria-label={t("hint.dismiss")} title={t("hint.dismissShort")} onClick={dismiss}>
      <Icon name="x" size={14} />
    </button>
  );
}

type Item = { key: string; icon: string; tone: Tone; text: ReactNode; open?: () => void; openLabel?: TKey; close?: HintSetting };

// Everything on the Overview that asks for a moment: bookings Groschen sorted on its own, double
// charges, subscriptions that changed, came, stopped or came back, unusual amounts and an expensive
// month. One list, newest first; when there is nothing, one calm line says so.
// The inbox shows this many hints; the rest wait behind "n more" so the Overview stays calm.
const INBOX_SHOWN = 4;

export function Inbox({ review, insights }: { review: number; insights: Insight[] }) {
  const t = useT();
  const { data, setData, reload } = useApi<{ items: Alert[] }>("/alerts");
  const [gone, setGone] = useState<string[]>([]);
  const [leaving, setLeaving] = useState<string | null>(null);
  const [all, setAll] = useState(false);
  useSyncEvents(reload);
  useEffect(() => {
    window.addEventListener("groschen:hints", reload);
    return () => window.removeEventListener("groschen:hints", reload);
  }, [reload]);
  if (!data) return null;

  const items: Item[] = [];
  if (review > 0) {
    items.push({
      key: "review",
      icon: "list",
      tone: "accent",
      text: (
        <>
          <b>{t("inbox.review", { n: review })}</b> {t("inbox.review.more")}
        </>
      ),
      open: () => navigate("/transactions?filter=review"),
      openLabel: "inbox.review.go",
    });
  }
  for (const a of data.items) {
    const [icon, tone] = ALERT_LOOK[a.kind];
    const sub = a.kind !== "duplicate" && a.kind !== "unusual" ? a.sub : null;
    items.push({
      key: a.key,
      icon,
      tone,
      text: <AlertText a={a} />,
      open: sub ? () => navigate(`/recurring?sub=${encodeURIComponent(sub)}`) : () => navigate(`/transactions?q=${encodeURIComponent(a.name.slice(0, 24))}`),
      close: ALERT_SETTING[a.kind],
    });
  }
  for (const ins of insights) {
    items.push({
      key: ins.key,
      icon: "trend",
      tone: "warn",
      text: (
        <>
          <b>{t("cf.highMonth", { month: monthLong(ins.month), p: ins.percent })}</b>
          {ins.driver ? t("cf.mostly", { driver: catName(ins.driver), amount: eur(ins.driver_amount) }) : "."}
        </>
      ),
      close: "unusual_alerts",
    });
  }
  const shown = items.filter((i) => !gone.includes(i.key));

  if (!shown.length) {
    return (
      <div className="allgood" role="status">
        <IconBadge name="check" tone="good" size={30} />
        <span>
          <b>{t("inbox.calm")}</b> {t("inbox.calm.more")}
        </span>
      </div>
    );
  }

  const remove = (key: string) => {
    setLeaving(key);
    window.setTimeout(() => {
      setGone((g) => [...g, key]);
      setData({ items: data.items.filter((x) => x.key !== key) });
      setLeaving(null);
    }, 260);
  };

  const visible = all ? shown : shown.slice(0, INBOX_SHOWN);
  const more = shown.length - visible.length;

  return (
    <Card className="inbox" title={t("hint.title")} right={<span className="count">{shown.length}</span>}>
      <ul className="inbox-list">
        {visible.map((it, i) => (
          <li key={it.key} className={`inbox-item${leaving === it.key ? " out" : ""}`} style={{ ["--i" as string]: i }}>
            <IconBadge name={it.icon} tone={it.tone} />
            <span className="ii-txt">{it.text}</span>
            <span className="ii-acts">
              {it.close && <HintClose hintKey={it.key} setting={it.close} onGone={() => remove(it.key)} />}
              {it.open && (
                <button className="btn sm" onClick={it.open}>
                  {t(it.openLabel ?? "hint.show")}
                  <Icon name="chevRight" size={13} />
                </button>
              )}
            </span>
          </li>
        ))}
      </ul>
      {more > 0 && (
        <button type="button" className="inbox-more" onClick={() => setAll(true)}>
          {t("inbox.more", { n: more })}
          <Icon name="chevDown" size={13} />
        </button>
      )}
    </Card>
  );
}
