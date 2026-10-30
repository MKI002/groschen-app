import { useState } from "react";
import { Icon } from "../components/Icons";
import { Card, Empty, ErrorNote, Loading, useApi, useSyncEvents } from "../components/UI";
import { locale, useT } from "../i18n";
import { qs } from "../lib/api";
import { eur, eur0, intervalName, monthLong } from "../lib/format";
import type { CalendarEntry, CalendarMonth } from "../lib/types";

// Mon..Sun in the chosen language (5 Jan 2026 was a Monday).
const weekdays = () => Array.from({ length: 7 }, (_, i) => new Date(2026, 0, 5 + i).toLocaleDateString(locale(), { weekday: "short" }));
const MAX_AHEAD = 12;

function thisMonth() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

function addMonths(ym: string, n: number) {
  const d = new Date(Number(ym.slice(0, 4)), Number(ym.slice(5, 7)) - 1 + n, 1);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

function monthsApart(a: string, b: string) {
  return (Number(b.slice(0, 4)) - Number(a.slice(0, 4))) * 12 + Number(b.slice(5, 7)) - Number(a.slice(5, 7));
}

// The grid for a month: leading blanks so the 1st lands on its weekday (weeks start on Monday).
function cells(ym: string): (string | null)[] {
  const first = new Date(Number(ym.slice(0, 4)), Number(ym.slice(5, 7)) - 1, 1);
  const days = new Date(first.getFullYear(), first.getMonth() + 1, 0).getDate();
  const lead = (first.getDay() + 6) % 7;
  const out: (string | null)[] = Array(lead).fill(null);
  for (let d = 1; d <= days; d++) out.push(`${ym}-${String(d).padStart(2, "0")}`);
  while (out.length % 7) out.push(null);
  return out;
}

const signed = (e: CalendarEntry) => (e.kind === "income" ? e.amount : -e.amount);

function Chip({ e }: { e: CalendarEntry }) {
  return (
    <span className={`calchip ${e.kind} ${e.status}`} title={`${e.name}: ${eur(signed(e))}`}>
      <span className="n">{e.name}</span>
      <span className="a">{eur0(signed(e))}</span>
    </span>
  );
}

function EntryRow({ e }: { e: CalendarEntry }) {
  const t = useT();
  const label = e.kind === "income" ? t("cal.kind.salary") : e.kind === "transfer" ? t("cal.kind.standing") : intervalName(e.interval);
  return (
    <li className={`calrow ${e.kind} ${e.status}`}>
      <span className="dot" />
      <span className="nm">
        {e.name}
        <small>
          {label}
          {` · ${e.status === "expected" ? t("cal.expected") : t("cal.paidTag")}`}
        </small>
      </span>
      <span className={`amt${e.kind === "income" ? " in" : ""}`}>{eur(signed(e))}</span>
    </li>
  );
}

// The month of fixed costs as a calendar: what was paid, what is still to come, and the salary.
// One bar on top shows how much of the month's fixed costs is already behind you.
export default function Calendar() {
  const t = useT();
  const now = thisMonth();
  const [month, setMonth] = useState(now);
  const [picked, setPicked] = useState<string | null>(null);
  const { data, error, reload } = useApi<CalendarMonth>(`/calendar${qs({ month })}`);
  useSyncEvents(reload);

  const go = (n: number) => {
    setMonth(n === 0 ? now : addMonths(month, n));
    setPicked(null);
  };
  const stepper = (
    <div className="period steps">
      <button className="ib" aria-label={t("cal.prev")} onClick={() => go(-1)}>
        <Icon name="chevRight" size={15} className="flip" />
      </button>
      <span className="period-y">{monthLong(month)}</span>
      <button className="ib" aria-label={t("cal.next")} disabled={monthsApart(now, month) >= MAX_AHEAD} onClick={() => go(1)}>
        <Icon name="chevRight" size={15} />
      </button>
      {month !== now && (
        <button className="btn sm ghost" onClick={() => go(0)}>
          {t("cal.today")}
        </button>
      )}
    </div>
  );
  if (!data || data.month !== month) return <Card right={stepper}>{error ? <ErrorNote error={error} /> : <Loading />}</Card>;

  const byDay = new Map<string, CalendarEntry[]>();
  for (const e of data.entries) byDay.set(e.date, [...(byDay.get(e.date) ?? []), e]);
  const days = [...byDay.keys()].sort();
  const shown = picked ? days.filter((d) => d === picked) : days;
  const paidShare = data.total > 0 ? Math.min(1, data.paid / data.total) : 0;

  return (
    <div className="cal-split">
      <Card
        className="calcard"
        title={t("cal.total", { amount: eur(data.total) })}
        sub={
          <span className="calbar-legend">
            <span>
              <span className="sq" style={{ background: "var(--spend)" }} />
              {t("cal.paidAmt", { amount: eur(data.paid) })}
            </span>
            <span>
              <span className="sq dashed" />
              {t("cal.toComeAmt", { amount: eur(data.expected) })}
            </span>
          </span>
        }
        right={stepper}
      >
        <div className="calbar" aria-hidden="true">
          <span style={{ ["--p" as string]: `${(paidShare * 100).toFixed(1)}%` }} />
        </div>
        <div className="cal" role="grid" aria-label={t("cal.gridLabel", { month: monthLong(month) })}>
          {weekdays().map((w) => (
            <div key={w} className="calh" role="columnheader">
              {w}
            </div>
          ))}
          {cells(month).map((iso, i) => {
            if (!iso) return <div key={`b${i}`} className="calday blank" aria-hidden="true" />;
            const list = byDay.get(iso) ?? [];
            const out = list.filter((e) => e.kind !== "income").reduce((s, e) => s + e.amount, 0);
            return (
              <button
                key={iso}
                role="gridcell"
                className={`calday${iso === data.today ? " today" : ""}${picked === iso ? " on" : ""}${list.length ? " has" : ""}${iso < data.today ? " gone" : ""}`}
                style={{ ["--i" as string]: i }}
                aria-label={`${iso}: ${list.length ? list.map((e) => e.name).join(", ") : t("cal.nothing")}`}
                aria-pressed={picked === iso}
                onClick={() => setPicked(picked === iso || !list.length ? null : iso)}
              >
                <span className="d">{Number(iso.slice(8))}</span>
                <span className="chips">
                  {list.slice(0, 3).map((e, j) => (
                    <Chip key={j} e={e} />
                  ))}
                  {list.length > 3 && <span className="more">+{list.length - 3}</span>}
                </span>
                <span className="dots" aria-hidden="true">
                  {list.slice(0, 4).map((e, j) => (
                    <i key={j} className={`${e.kind} ${e.status}`} />
                  ))}
                </span>
                {out > 0 && <span className="sum">{eur0(-out)}</span>}
              </button>
            );
          })}
        </div>
        <div className="legend cal-legend">
          <span>
            <span className="sq" style={{ background: "var(--spend)" }} />
            {t("cal.legendPaid")}
          </span>
          <span>
            <span className="sq dashed" />
            {t("cal.legendExpected")}
          </span>
          <span>
            <span className="sq" style={{ background: "var(--c-teal)" }} />
            {t("cal.legendStanding")}
          </span>
          <span>
            <span className="sq" style={{ background: "var(--good)" }} />
            {t("cal.legendSalary")}
          </span>
        </div>
      </Card>
      <Card
        className="calside"
        title={picked ? new Date(`${picked}T12:00:00`).toLocaleDateString(locale(), { weekday: "long", day: "numeric", month: "long" }) : t("cal.dayByDay")}
        right={
          picked && (
            <button className="btn sm ghost" onClick={() => setPicked(null)}>
              <Icon name="x" size={14} />
              {t("cal.wholeMonth")}
            </button>
          )
        }
      >
        {shown.length ? (
          <div className="calist">
            {shown.map((d) => (
              <div key={d} className="calist-day">
                {!picked && <div className="calist-h">{new Date(`${d}T12:00:00`).toLocaleDateString(locale(), { weekday: "short", day: "numeric", month: "short" })}</div>}
                <ul>
                  {byDay.get(d)!.map((e, j) => (
                    <EntryRow key={j} e={e} />
                  ))}
                </ul>
              </div>
            ))}
          </div>
        ) : (
          <Empty title={t("cal.empty")} icon="calendar">
            {t("cal.emptySub")}
          </Empty>
        )}
      </Card>
    </div>
  );
}
