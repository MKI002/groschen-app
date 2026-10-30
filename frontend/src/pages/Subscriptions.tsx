import { useEffect, useMemo, useState } from "react";
import { PaySteps } from "../components/Charts";
import { Icon } from "../components/Icons";
import { celebrate, Odometer } from "../components/Motion";
import { EVENT_LOOK, SubEventText } from "../components/Planner";
import { ORBITS, OrbitView } from "../components/Showpiece";
import { Card, ChangePill, Disclosure, Empty, ErrorNote, IconBadge, Loading, Modal, useApi, useSyncEvents, useToast } from "../components/UI";
import { catName, t, useT } from "../i18n";
import { api } from "../lib/api";
import { useApp } from "../lib/app";
import { colorVar, dateShort, eur, initial, intervalName, relDay } from "../lib/format";
import { drillPath, navigate, redirect, useSearch } from "../lib/router";
import type { Plans, SubEvent, Subscription, Subscriptions as Subs } from "../lib/types";

const GROUP_COLOR: Record<string, string> = {
  Housing: "blue", "Food & Dining": "amber", Transport: "pink", Shopping: "gray", Insurance: "forest", Subscriptions: "teal", Health: "red",
  "Leisure & Travel": "violet", Personal: "sand",
};
const subColor = (s: { group?: string | null }) => colorVar(GROUP_COLOR[s.group ?? ""]);
const EVENTS_SHOWN = 4;

// What is special about a payment right now, as one small tag: new, back after a pause, or a new price.
function StatusTag({ s }: { s: Subscription }) {
  useT();
  if (s.status === "new") return <span className="tag info">{t("subs.tag.new")}</span>;
  if (s.status === "resumed") return <span className="tag info">{t("subs.tag.back")}</span>;
  if (s.status === "ended") return <span className="tag">{t("subs.tag.ended")}</span>;
  if (s.price_change > 0) return <span className="tag warn">{t("subs.tag.up", { amount: eur(s.price_change) })}</span>;
  if (s.price_change < 0) return <span className="tag good">{t("subs.tag.down", { amount: eur(-s.price_change) })}</span>;
  return null;
}

// How often and on which day, said the short way: "monthly · on the 15th".
function rhythm(s: Subscription) {
  const day = s.interval === "weekly" || s.interval === "biweekly" || s.interval === "4-weekly" ? "" : ` · ${t("subs.onDay", { day: s.day })}`;
  return `${intervalName(s.interval)}${s.rhythm_known ? day : ""}`;
}

function SubRow({ s, i, onOpen }: { s: Subscription; i: number; onOpen: () => void }) {
  useT();
  const ended = s.status === "ended";
  return (
    <button type="button" className={`subrow stagger${ended ? " ended" : ""}`} style={{ ["--i" as string]: Math.min(i, 14), ["--c" as string]: subColor(s) }} onClick={onOpen}>
      <span className="txl-av" aria-hidden="true">
        {initial(s.name)}
      </span>
      <span className="txl-main">
        <span className="txl-name">
          <span className="txl-nm">{s.name}</span>
          <StatusTag s={s} />
        </span>
        <span className="txl-sub">{ended ? t("subs.lastOn", { date: dateShort(s.last_date) }) : rhythm(s)}</span>
      </span>
      {!ended && <span className="subrow-next">{relDay(s.next_date)}</span>}
      <span className="subrow-amt">
        <b>{s.varies ? `≈ ${eur(s.monthly_cost)}` : eur(s.amount)}</b>
        {!s.varies && s.interval !== "monthly" && <small>{t("subs.perMonthEq", { amount: eur(s.monthly_cost) })}</small>}
      </span>
      <Icon name="chevRight" size={15} className="subrow-go" />
    </button>
  );
}

// Everything about one recurring payment: its price over time, every change, pauses, and the two
// ways out (all its bookings, or "not a subscription").
function SubDetail({ s, onClose, onMark }: { s: Subscription; onClose: () => void; onMark: (state: "no" | "auto") => void }) {
  useT();
  const ended = s.status === "ended";
  const gaps = s.runs.slice(1).map((r, i) => ({ from: s.runs[i].to, to: r.from }));
  return (
    <Modal
      title={s.name}
      onClose={onClose}
      actions={
        <>
          <button
            className="btn ghost"
            onClick={() => {
              onClose();
              navigate(drillPath({ merchant: s.merchant }));
            }}
          >
            {t("subs.allPayments")}
            <Icon name="chevRight" size={14} />
          </button>
          <span className="grow" />
          {!ended && (
            <button className="btn ghost danger" onClick={() => onMark("no")}>
              <Icon name="x" size={14} />
              {t("subs.notSub")}
            </button>
          )}
        </>
      }
    >
      <div className="subhead" style={{ ["--c" as string]: subColor(s) }}>
        <span className="txl-av big" aria-hidden="true">
          {initial(s.name)}
        </span>
        <span>
          <span className="subhead-amt">
            {s.varies ? `≈ ${eur(s.monthly_cost)}` : eur(s.amount)} <small>{s.varies ? t("subs.perMonthAvg") : intervalName(s.interval)}</small>
          </span>
          <span className="muted">
            {s.category ? `${catName(s.category)} · ` : ""}
            {t("subs.since", { date: dateShort(s.since) })}
          </span>
        </span>
        <StatusTag s={s} />
      </div>
      <div className="facts">
        <span>
          <b>{eur(s.yearly_cost)}</b> {t("subs.perYearShort")}
        </span>
        <span>
          <b>{s.count}</b> {t("subs.payments", { n: s.count })}
        </span>
        {ended ? (
          <span>{t("subs.lastOn", { date: dateShort(s.last_date) })}</span>
        ) : (
          <span>
            {t("subs.nextIs")} <b>{relDay(s.next_date)}</b>
          </span>
        )}
      </div>
      <PaySteps data={s.history} color={subColor(s)} label={t("subs.history", { name: s.name })} />
      {(s.changes.length > 0 || gaps.length > 0) && (
        <ul className="plainlist">
          {s.changes
            .slice()
            .reverse()
            .map((c) => (
              <li key={c.date}>
                <span className="pl-when">{dateShort(c.date)}</span>
                <span className="pl-what">
                  {eur(c.from)} → <b>{eur(c.to)}</b>
                </span>
                <ChangePill up={c.to > c.from} good={c.to < c.from} text={eur(Math.abs(c.to - c.from))} />
              </li>
            ))}
          {gaps.map((g) => (
            <li key={g.from}>
              <span className="pl-when">{dateShort(g.from)}</span>
              <span className="pl-what">{t("subs.paused", { to: dateShort(g.to) })}</span>
              <Icon name="pause" size={14} />
            </li>
          ))}
        </ul>
      )}
      {s.confirmed && (
        <p className="muted small">
          {t("subs.yours.title")}{" "}
          <button className="linkbtn" onClick={() => onMark("auto")}>
            {t("subs.decideAgain")}
          </button>
        </p>
      )}
    </Modal>
  );
}

// Everything Groschen noticed by itself in the last year: new prices, new, stopped and returning payments.
function Changes({ events, onOpen }: { events: SubEvent[]; onOpen: (key: string) => void }) {
  useT();
  const [all, setAll] = useState(false);
  if (!events.length) return null;
  const shown = all ? events : events.slice(0, EVENTS_SHOWN);
  return (
    <Card title={t("subs.changes")} sub={t("subs.changes.sub")} className="changes">
      <ul className="feed">
        {shown.map((e, i) => {
          const [icon, tone] = EVENT_LOOK[e.kind];
          return (
            <li key={e.key} className="stagger" style={{ ["--i" as string]: i }}>
              <button type="button" className="feed-row" onClick={() => onOpen(e.sub)}>
                <IconBadge name={icon} tone={tone} size={32} />
                <span className="feed-txt">
                  <SubEventText e={e} />
                </span>
                <span className="feed-when">{relDay(e.date)}</span>
              </button>
            </li>
          );
        })}
      </ul>
      {events.length > EVENTS_SHOWN && (
        <button className="linkbtn" onClick={() => setAll(!all)}>
          {all ? t("subs.fewer") : t("subs.allChanges", { n: events.length })}
        </button>
      )}
    </Card>
  );
}

// The list view of Fixed costs: what they add up to and what comes next, what changed, the questions
// Groschen can't answer alone, and every payment as one row that opens the whole story.
export default function Subscriptions() {
  const { refresh } = useApp();
  useT();
  const toast = useToast();
  const asked = useSearch().get("sub");
  const { data, error, reload } = useApi<Subs>("/subscriptions");
  const plans = useApi<Plans>("/plans");
  const [leaving, setLeaving] = useState<Set<string>>(new Set());
  const [open, setOpen] = useState<string | null>(asked);
  useSyncEvents(reload);
  useEffect(() => setOpen(asked), [asked]);

  async function mark(key: string, state: "yes" | "no" | "auto", el?: Element | null) {
    setLeaving((s) => new Set(s).add(key));
    try {
      await api.post("/subscriptions/mark", { key, state });
      if (state === "yes") celebrate(el, 10);
      toast(state === "yes" ? t("subs.added") : state === "no" ? t("subs.gotIt") : t("subs.decidesAgain"));
    } catch (e) {
      toast((e as Error).message);
    }
    window.setTimeout(() => {
      reload();
      refresh();
      setLeaving(new Set());
    }, 320);
  }
  const close = () => {
    setOpen(null);
    if (asked) redirect("/recurring");
  };

  if (!data) return error ? <ErrorNote error={error} /> : <Loading />;
  const all = [...data.items, ...data.ended];
  const current = open ? all.find((s) => s.key === open) : undefined;
  const next = data.items
    .filter((s) => s.next_date)
    .slice()
    .sort((a, b) => a.next_date.localeCompare(b.next_date))
    .slice(0, 3);
  const p = plans.data;

  return (
    <>
      <section className="card subhero">
        <div className="hero-body">
          <div className="eyebrow">{t("subs.monthlyTitle")}</div>
          <div className="hero-v">
            <Odometer value={data.monthly} />
          </div>
          <p className="hero-sub">{t("subs.heroSub", { year: eur(data.yearly), n: data.items.length })}</p>
        </div>
        {next.length > 0 && (
          <div className="nextup">
            <div className="eyebrow">{t("subs.nextUp")}</div>
            {next.map((s, i) => (
              <button key={s.key} type="button" className="nextup-item stagger" style={{ ["--i" as string]: i, ["--c" as string]: subColor(s) }} onClick={() => setOpen(s.key)}>
                <span className="nu-when">{relDay(s.next_date)}</span>
                <span className="nu-name">{s.name}</span>
                <span className="nu-amt">{s.varies ? `≈ ${eur(s.monthly_cost)}` : eur(s.amount)}</span>
              </button>
            ))}
          </div>
        )}
      </section>

      <Changes events={data.events} onOpen={setOpen} />

      {data.suggestions.length > 0 && (
        <Card title={t("subs.ask")} sub={t("subs.ask.sub")} className="asks">
          <div className="suggest-list">
            {data.suggestions.map((s, i) => (
              <div key={s.key} className={`suggest stagger${leaving.has(s.key) ? " leaving" : ""}`} style={{ ["--i" as string]: i, ["--c" as string]: subColor(s) }}>
                <span className="txl-av" aria-hidden="true">
                  {initial(s.name)}
                </span>
                <div className="suggest-main">
                  <b>{s.name}</b>
                  <span className="muted small">
                    {s.reason === "twice" ? t("subs.twice") : s.reason === "varies" ? t("subs.varies") : rhythm(s)} · {t("subs.lastOn", { date: dateShort(s.last_date) })}
                  </span>
                </div>
                <span className="suggest-amt">{s.varies ? `≈ ${eur(s.monthly_cost)}` : eur(s.amount)}</span>
                <div className="suggest-actions">
                  <button className="btn sm primary" onClick={(e) => mark(s.key, "yes", e.currentTarget)} disabled={leaving.has(s.key)}>
                    <Icon name="check" size={15} />
                    {t("subs.yes")}
                  </button>
                  <button className="btn sm ghost" onClick={() => mark(s.key, "no")} disabled={leaving.has(s.key)}>
                    {t("subs.no")}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      <Card title={t("subs.recurring")} sub={t("subs.sub")} className="sublist">
        {data.items.length ? (
          <div className="subrows">
            {data.items.map((s, i) => (
              <SubRow key={s.key} s={s} i={i} onOpen={() => setOpen(s.key)} />
            ))}
          </div>
        ) : (
          <Empty title={t("subs.empty")} icon="repeat">
            {t("subs.empty.text")}
          </Empty>
        )}
        {data.ended.length > 0 && (
          <Disclosure label={t("subs.ended", { n: data.ended.length })} openLabel={t("subs.endedHide")}>
            <div className="subrows">
              {data.ended.map((s, i) => (
                <SubRow key={s.key} s={s} i={i} onOpen={() => setOpen(s.key)} />
              ))}
            </div>
          </Disclosure>
        )}
        {data.hidden.length > 0 && (
          <Disclosure label={t("subs.show", { n: data.hidden.length })} openLabel={t("subs.hide")}>
            <p className="muted small">{t("subs.hidden.sub")}</p>
            {data.hidden.map((h, i) => (
              <div className={`rule stagger${leaving.has(h.key) ? " leaving" : ""}`} key={h.key} style={{ ["--i" as string]: i }}>
                <b>{h.name}</b>
                <span className="muted small">
                  {eur(h.amount)} · {t("subs.lastOn", { date: dateShort(h.last_date) })}
                </span>
                <button className="btn sm ghost" onClick={() => mark(h.key, "auto")} disabled={leaving.has(h.key)}>
                  {t("subs.decideAgain")}
                </button>
              </div>
            ))}
          </Disclosure>
        )}
      </Card>

      {p && p.running > 0 && (
        <button type="button" className="plansline" onClick={() => navigate("/networth#plans")}>
          <IconBadge name="coin" tone="accent" size={32} />
          <span>
            <b>{t("subs.plans", { n: p.running, amount: eur(p.monthly) })}</b> {t("subs.plansMore")}
          </span>
          <Icon name="chevRight" size={15} />
        </button>
      )}

      {current && (
        <SubDetail
          s={current}
          onClose={close}
          onMark={(state) => {
            close();
            mark(current.key, state);
          }}
        />
      )}
    </>
  );
}

// The same payments as the list, drawn as a little solar system: one ring per rhythm,
// each payment moving toward the front as its due date comes closer.
export function SubscriptionOrbit() {
  useT();
  const { data, error, reload } = useApi<Subs>("/subscriptions");
  useSyncEvents(reload);
  // Built once per answer, so the animation isn't restarted by unrelated renders.
  const items = useMemo(
    () =>
      (data?.items ?? []).map((s) => ({
        key: s.key,
        name: s.name,
        merchant: s.merchant,
        interval: s.interval,
        next_date: s.next_date,
        amount: s.amount,
        monthly_cost: s.monthly_cost,
        color: subColor(s),
      })),
    [data],
  );
  if (!data) return error ? <ErrorNote error={error} /> : <Loading />;
  const counts = new Map<string, number>();
  for (const s of data.items) counts.set(s.interval, (counts.get(s.interval) ?? 0) + 1);
  const rings = ORBITS.filter(([k]) => counts.get(k));
  return (
    <Card title={t("orbit.title")} sub={t("orbit.sub")} className="orbit-card">
      {items.length ? (
        <>
          <OrbitView items={items} monthly={data.monthly} onPick={(i) => navigate(`/recurring?sub=${encodeURIComponent(i.key)}`)} />
          <div className="legend orbit-legend">
            {rings.map(([k], n) => (
              <span key={k}>
                <span className="orb" style={{ ["--n" as string]: n }} />
                {intervalName(k)} · {counts.get(k)}
              </span>
            ))}
          </div>
        </>
      ) : (
        <Empty title={t("subs.empty")} icon="orbit">
          {t("subs.empty.text")}
        </Empty>
      )}
    </Card>
  );
}
