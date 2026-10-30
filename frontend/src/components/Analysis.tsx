// The analysis tabs of the depot and of one ETF. Each figure is drawn as what it means: bars on
// one scale, a marker between calm and wild, the price inside its range of the year, with one
// sentence in plain words. The charts below the cards carry the rest.

import type { CSSProperties } from "react";
import { useT, type Key } from "../i18n";
import { dateShort, eur, monthLabel, num, pct, pctS } from "../lib/format";
import { Card } from "./UI";

const at = (p: number) => `${Math.max(0, Math.min(100, p)).toFixed(2)}%`;
const vars = (v: Record<string, string | number>) => v as CSSProperties;
const known = (x: number | null | undefined): x is number => x !== null && x !== undefined && isFinite(x);

// Your money against the fund(s) themselves, each as a bar on one shared scale. The gap between
// the two comes from when the money went in, so the sentence says which way that went.
// title and youSub replace the heading and the line under "you" (for a period instead of per year).
export function ReturnCard({ you, funds, since, one = false, title, youSub }: {
  you: number | null | undefined;
  funds: number | null | undefined;
  since: string | null;
  one?: boolean;
  title?: string;
  youSub?: string;
}) {
  const t = useT();
  const shown = [you, funds].filter(known);
  if (!shown.length) return null;
  const lo = Math.min(0, ...shown);
  const hi = Math.max(0, ...shown, lo + 0.01);
  const x = (v: number) => ((v - lo) / (hi - lo)) * 100;
  const row = (label: string, sub: string, value: number | null | undefined, cls: string, i: number) =>
    known(value) && (
      <div className="an-row">
        <span className="an-lbl">
          <b>{label}</b>
          <small>{sub}</small>
        </span>
        <b className={`an-val ${value >= 0 ? "pos" : "neg"}`}>{pctS(value)}</b>
        <span className="an-track">
          {lo < 0 && <i className="an-zero" style={{ left: at(x(0)) }} />}
          <span className={`an-bar ${cls}${value < 0 ? " back" : ""}`} style={vars({ left: at(x(Math.min(0, value))), width: at(x(Math.max(0, value)) - x(Math.min(0, value))), "--i": i })} />
        </span>
      </div>
    );
  const gap = known(you) && known(funds) ? you - funds : null;
  const say: Key | null =
    gap === null ? null : gap > 0.01 ? (one ? "an.ret.ahead1" : "an.ret.ahead") : gap < -0.01 ? (one ? "an.ret.behind1" : "an.ret.behind") : one ? "an.ret.same1" : "an.ret.same";
  return (
    <Card title={title ?? t("an.ret")} className="an-card">
      <div className="an-rows">
        {row(t("an.ret.you"), youSub ?? (since ? t("an.ret.youSince", { month: since }) : t("an.ret.youSub")), you, "you", 0)}
        {row(t(one ? "an.ret.fund" : "an.ret.funds"), t("an.ret.fundsSub"), funds, "funds", 1)}
      </div>
      {say && <p className="an-say">{t(say)}</p>}
    </Card>
  );
}

const WILD = 0.4; // the end of the scale: 40 % a year is about as wild as funds get
const USUAL: [number, number] = [0.12, 0.2]; // where broad stock ETFs usually are

// How much it swings, as a marker between calm and wild next to where stock ETFs usually are;
// the Sharpe ratio in words: what each bit of swing brought on top of the Extra-Konto.
// note: what time it covers, under the heading.
export function SwingCard({ volatility, sharpe, note }: { volatility: number | null; sharpe: number | null; note?: string }) {
  const t = useT();
  if (!known(volatility)) return null;
  const x = (v: number) => (Math.min(Math.max(v, 0), WILD) / WILD) * 100;
  return (
    <Card title={t("an.swing")} sub={note} className="an-card">
      <p className="an-big">
        <b>±{pct(volatility, 0)}</b>
        <span>{t("an.swing.say")}</span>
      </p>
      <div>
        <div className="an-scale" role="img" aria-label={t("an.swing.aria", { p: pct(volatility, 1) })}>
          <span className="an-usual" style={{ left: at(x(USUAL[0])), width: at(x(USUAL[1]) - x(USUAL[0])) }}>
            <small>{t("an.swing.usual")}</small>
          </span>
          <span className="an-mark" style={{ left: at(x(volatility)) }} />
        </div>
        <div className="an-ends">
          <small>{t("an.swing.calm")}</small>
          <small>{t("an.swing.wild")}</small>
        </div>
      </div>
      {known(sharpe) && <p className="an-say">{sharpe > 0 ? t("an.sharpe.pos", { n: num(sharpe, 2) }) : t("an.sharpe.neg")}</p>}
    </Card>
  );
}

// How far below its last high, or that it is at one.
export function HighTag({ dd, title }: { dd: number | null; title?: string }) {
  const t = useT();
  if (!known(dd)) return null;
  return dd > -0.0005 ? (
    <span className="tag good" title={title}>
      {t("inv.newHigh")}
    </span>
  ) : (
    <span className="tag warn" title={title}>
      {t("an.below", { p: pct(-dd, 1) })}
    </span>
  );
}

// How many months went up, as a split bar for a card's header.
export function MonthsUp({ up, all }: { up: number; all: number }) {
  const t = useT();
  if (!all) return null;
  return (
    <span className="an-up">
      <small>{t("an.up", { up, all })}</small>
      <span className="an-split" aria-hidden="true">
        <span style={{ width: at((up / all) * 100) }} />
      </span>
    </span>
  );
}

// The best and the worst month of a list of monthly returns, to outline in the heatmap.
export function extremes(returns: { month: string; r: number }[]) {
  if (!returns.length) return [];
  const best = returns.reduce((a, b) => (b.r > a.r ? b : a));
  const worst = returns.reduce((a, b) => (b.r < a.r ? b : a));
  return best.month === worst.month ? [best.month] : [best.month, worst.month];
}

// One ETF's price inside its range of the last twelve months, with its 200-day average and how far
// it is from its record high.
export function RangeCard({ low, high, price, avg200, dd, ath, athDate }: {
  low: number | null;
  high: number | null;
  price: number | null;
  avg200: number | null;
  dd: number;
  ath: number;
  athDate: string;
}) {
  const t = useT();
  if (!known(low) || !known(high) || !known(price) || !(high > low)) return null;
  const x = (v: number) => ((Math.min(Math.max(v, low), high) - low) / (high - low)) * 100;
  const where = x(price);
  const word = where >= 85 ? "an.range.top" : where >= 60 ? "an.range.upper" : where > 40 ? "an.range.middle" : where > 15 ? "an.range.lower" : "an.range.bottom";
  const vsAvg = avg200 ? price / avg200 - 1 : null;
  return (
    <Card title={t("an.range")} className="an-card">
      <p className="an-word">{t(word)}</p>
      <div>
        <div className="an-range" role="img" aria-label={t("an.range.aria", { low: eur(low), high: eur(high), price: eur(price) })}>
          <span className="an-fill" style={{ width: at(where) }} />
          {known(avg200) && (
            <span className={`an-tick${x(avg200) < 18 ? " edge-l" : x(avg200) > 82 ? " edge-r" : ""}`} style={{ left: at(x(avg200)) }}>
              <small>{t("an.avg200")}</small>
            </span>
          )}
          <span className="an-mark" style={{ left: at(where) }} />
        </div>
        <div className="an-ends">
          <small>{t("an.range.low", { price: eur(low) })}</small>
          <small>{t("an.range.high", { price: eur(high) })}</small>
        </div>
      </div>
      <div className="hstack an-tags">
        <HighTag dd={dd} title={t("fund.ath", { price: eur(ath), date: dateShort(athDate) })} />
        {known(vsAvg) && <span className={`tag ${vsAvg >= 0 ? "good" : "warn"}`}>{t(vsAvg >= 0 ? "an.avg.above" : "an.avg.below", { p: pct(Math.abs(vsAvg), 1) })}</span>}
      </div>
    </Card>
  );
}

// Every twelve months in a row since the start as one small bar each: how often they ended higher,
// and the best and the worst of them at the ends.
export function RollingCard({ rolling, up }: { rolling: { month: string; r: number }[]; up: number | null }) {
  const t = useT();
  if (!rolling.length || !known(up)) return null;
  const top = Math.max(0, ...rolling.map((x) => x.r));
  const bottom = Math.min(0, ...rolling.map((x) => x.r));
  const span = top - bottom || 1;
  const best = rolling.reduce((a, b) => (b.r > a.r ? b : a));
  const worst = rolling.reduce((a, b) => (b.r < a.r ? b : a));
  const from = (ym: string) => {
    const [y, m] = ym.split("-").map(Number);
    const s = y * 12 + m - 13;
    return `${Math.floor(s / 12)}-${String((s % 12) + 1).padStart(2, "0")}`;
  };
  return (
    <Card title={t("an.roll")} className="an-card">
      <p className="an-big">
        <b>{pct(up, 0)}</b>
        <span>{t("an.roll.say", { n: rolling.length })}</span>
      </p>
      <div className="an-push">
        <div className="an-strip" style={vars({ "--zero": top / span })} role="img" aria-label={t("an.roll.aria", { up: pct(up, 0), n: rolling.length })}>
          {rolling.map((x, i) => (
            <span key={x.month} className={x.r >= 0 ? "up" : "down"} style={vars({ "--h": Math.abs(x.r) / span, "--i": i })} title={`${monthLabel(from(x.month))} – ${monthLabel(x.month)}: ${pctS(x.r)}`} />
          ))}
        </div>
        <div className="an-ends">
          <small title={`${monthLabel(from(worst.month))} – ${monthLabel(worst.month)}`}>{t("an.roll.worst", { p: pctS(worst.r, 0) })}</small>
          <small title={`${monthLabel(from(best.month))} – ${monthLabel(best.month)}`}>{t("an.roll.best", { p: pctS(best.r, 0) })}</small>
        </div>
      </div>
    </Card>
  );
}

// The price change over the usual periods as columns from one zero line; three years and longer
// per year.
export function PeriodBars({ periods }: { periods: { key: string; r: number; annual: boolean }[] }) {
  const t = useT();
  if (!periods.length) return null;
  const top = Math.max(0, ...periods.map((p) => p.r));
  const bottom = Math.min(0, ...periods.map((p) => p.r));
  const span = top - bottom || 1;
  return (
    <div className="scroll">
      <div className="an-cols" style={vars({ "--n": periods.length, "--zero": top / span })}>
        {periods.map((p, i) => (
          <div key={p.key} className="an-col">
            <div className="an-col-plot">
              <span className={`an-col-bar ${p.r >= 0 ? "up" : "down"}`} style={vars({ "--h": Math.abs(p.r) / span, "--i": i })} />
              <b className={`an-col-v ${p.r >= 0 ? "up pos" : "down neg"}`} style={vars({ "--h": Math.abs(p.r) / span, "--i": i })}>
                {pctS(p.r)}
              </b>
            </div>
            <small>
              {t(`fund.p.${p.key}` as Key)}
              {p.annual && <i>{t("fund.pa")}</i>}
            </small>
          </div>
        ))}
      </div>
    </div>
  );
}
