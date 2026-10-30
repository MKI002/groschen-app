// The depot's value day by day with the money paid in as a dashed step line, and under it, on the
// same time axis, what each month (or week, or day) earned or lost in euros: the change in value
// minus what was paid in. Zooms like components/Zoom.tsx describes; both axes follow what is in view,
// and a click on a month's bar looks at that month.
// Money paid in is left out of the line unless the switch under the chart turns it on: a deposit
// would show as a jump that looks like gain. Off, every point is the value as if the money in the
// depot at the end of the view had been in it all along, so the line moves only with prices.

import { useEffect, useId, useMemo, useState } from "react";
import { locale, t as tr, useT } from "../i18n";
import { buckets, gainBetween, timeOf, type Bucket, type DayPoint } from "../lib/depot";
import { dayMonth, eur, monthLabel, monthLong, monthShort, pctS } from "../lib/format";
import { axisMarks, axisUnit, every, grow, kEur, labelsFor, niceScale, useChartWidth, useNarrow } from "./Charts";
import { useTween } from "./Motion";
import { useZoomGestures, ZoomNote, ZoomStrip, type Zoom } from "./Zoom";

const PAID = "groschen.invPaid";
function usePaidShown(): [boolean, () => void] {
  const [on, setOn] = useState(() => {
    try {
      return localStorage.getItem(PAID) === "1";
    } catch {
      return false;
    }
  });
  const flip = () => {
    setOn(!on);
    try {
      if (on) localStorage.removeItem(PAID);
      else localStorage.setItem(PAID, "1");
    } catch {
      /* storage blocked: the choice lasts until the page is left */
    }
  };
  return [on, flip];
}

const signedEur = (v: number) => `${v > 0 ? "+" : ""}${eur(v)}`;
const signedShort = (v: number) => (v ? `${v > 0 ? "+" : "−"}${kEur(Math.abs(v))}` : kEur(0));
const longDay = (iso: string) =>
  new Date(`${iso.slice(0, 10)}T12:00:00`).toLocaleDateString(locale(), iso.length === 7 ? { month: "long", year: "numeric" } : { weekday: "short", day: "numeric", month: "short", year: "numeric" });

// What a bar stands for, in the tooltip.
function bucketName(b: Bucket) {
  if (b.unit === "month") return monthLong(b.key);
  if (b.unit === "week") return tr("depot.week", { date: dayMonth(b.key) });
  return tr("depot.day");
}

// A number for each bar that counts up from one bar to the next, so labels can be thinned the same
// way however far the chart is zoomed.
function barOrdinal(b: Bucket) {
  if (b.unit === "month") return Number(b.key.slice(0, 4)) * 12 + Number(b.key.slice(5, 7));
  return Math.round(timeOf(b.key) / ((b.unit === "week" ? 7 : 1) * 864e5));
}

export function DepotChart({ days, zoom }: { days: DayPoint[]; zoom: Zoom }) {
  const t = useT();
  const id = useId().replace(/:/g, "");
  const narrow = useNarrow();
  const [wrap, wide] = useChartWidth<HTMLDivElement>(narrow);
  const [hover, setHover] = useState<number | null>(null);
  const [withPaid, flipPaid] = usePaidShown();
  const n = days.length;

  const W = narrow ? 480 : wide, l = 64, r = 22, top = 14, gap = narrow ? 24 : 14, bottom = 28;
  const mainH = narrow ? 250 : Math.round(262 * grow(W));
  const labels = !narrow;
  const pad = labels ? 17 : 6;
  const laneH = (narrow ? 74 : 72) + 2 * pad;
  const H = top + mainH + gap + laneH + bottom;
  const iw = W - l - r;
  const laneTop = top + mainH + gap, barTop = laneTop + pad, barH = laneH - 2 * pad;

  const { a, b } = zoom;
  const [w0, w1] = zoom.to;
  const vals = useMemo(() => (withPaid ? days.map((d) => d.value) : days.map((d) => d.value + days[w1].paid_in - d.paid_in)), [days, w1, withPaid]);
  const X = (i: number) => l + ((i - a) / (b - a || 1)) * iw;

  // Value axis: what is in view, from zero when that is close anyway. The paid-in line joins in while
  // it is close by; far below, it would squeeze the value's own ups and downs into a thin band.
  const scale = useMemo(() => {
    let lo = Infinity, hi = -Infinity, plo = Infinity, phi = -Infinity;
    for (let i = w0; i <= w1; i++) {
      lo = Math.min(lo, vals[i]);
      hi = Math.max(hi, vals[i]);
      plo = Math.min(plo, days[i].paid_in);
      phi = Math.max(phi, days[i].paid_in);
    }
    if (!isFinite(lo)) [lo, hi] = [0, 1];
    if (withPaid && isFinite(plo) && Math.max(hi, phi) - Math.min(lo, plo) <= Math.max(hi - lo, hi * 0.02) * 2.5) [lo, hi] = [Math.min(lo, plo), Math.max(hi, phi)];
    if (lo > 0 && lo < (hi - lo) * 0.6) lo = 0;
    const room = (hi - lo) * 0.08 || Math.abs(hi) * 0.02 || 1;
    return niceScale(lo === 0 ? 0 : lo - room, hi + room * 0.4, narrow ? 4 : 5);
  }, [days, vals, w0, w1, narrow, withPaid]);
  const ylo = useTween(scale.lo, 420), yhi = useTween(scale.hi, 420);
  const Y = (v: number) => top + mainH - ((v - ylo) / (yhi - ylo || 1)) * mainH;

  // Bars for the window the figures describe, drawn wherever the view is while it glides.
  const bars = useMemo(() => (w1 > w0 ? buckets(days, w0, w1) : []), [days, w0, w1]);
  const most = useTween(Math.max(0, ...bars.map((x) => x.gain)), 420);
  const least = useTween(Math.max(0, ...bars.map((x) => -x.gain)), 420);
  const total = most + least || 1;
  const zeroY = barTop + barH * (most / total);
  const BY = (g: number) => zeroY - (g / total) * barH;

  // Only the points in view (and one either side) are drawn.
  const i0 = Math.max(0, Math.floor(a) - 1), i1 = Math.min(n - 1, Math.ceil(b) + 1);
  let line = "", paid = "";
  for (let i = i0; i <= i1; i++) {
    const x = X(i).toFixed(1);
    line += `${i > i0 ? "L" : "M"}${x} ${Y(vals[i]).toFixed(1)}`;
    if (withPaid) paid += i > i0 ? `L${x} ${Y(days[i - 1].paid_in).toFixed(1)}L${x} ${Y(days[i].paid_in).toFixed(1)}` : `M${x} ${Y(days[i].paid_in).toFixed(1)}`;
  }
  const floor = top + mainH;
  const area = n > 1 ? `${line}L${X(i1).toFixed(1)} ${floor}L${X(i0).toFixed(1)} ${floor}Z` : "";
  // The time axis: under bars of its own unit (months under monthly bars) each bar is labelled in its
  // middle; otherwise the labels mark where months (weeks, days, years) start.
  const dates = useMemo(() => days.map((d) => d.date), [days]);
  const ia = Math.max(0, Math.round(a)), ib = Math.min(n - 1, Math.round(b));
  const spanDays = (timeOf(dates[ib]) - timeOf(dates[ia])) / 864e5;
  const room = narrow ? 4 : labelsFor(iw);
  const centred = bars.length > 0 && bars[0].unit === axisUnit(spanDays, dates[0]?.length === 7);
  const sameYear = bars.length > 0 && bars[0].key.slice(0, 4) === bars[bars.length - 1].key.slice(0, 4);
  const step = every(bars.length, room);
  const marks = (
    centred
      ? bars.filter((x) => barOrdinal(x) % step === 0).map((x) => ({ key: x.key, x: (X(x.i0 - 1) + X(x.i1)) / 2, text: x.unit === "month" ? (sameYear ? monthShort(x.key) : monthLabel(x.key)) : dayMonth(x.key) }))
      : axisMarks(dates, Math.floor(a), Math.ceil(b), spanDays, room).map((m) => ({ key: String(m.i), x: X(m.i), text: m.text }))
  ).filter((m) => m.x >= l + 8 && m.x <= W - r - 8);

  const bucketAt = (i: number) => bars.find((x) => i >= x.i0 && i <= x.i1) ?? null;
  const hb = hover !== null ? bucketAt(hover) : null;

  const g = useZoomGestures(
    zoom,
    { l, iw, W, H },
    (x) => setHover(x === null ? null : Math.min(Math.max(Math.round(x), 0), n - 1)),
    (x, y) => {
      // A click on the bars looks at that month (week); on the line it does nothing.
      if (y < laneTop) return;
      const bk = bucketAt(Math.round(x));
      if (bk && bk.i1 - (bk.i0 - 1) >= zoom.minSpan) {
        zoom.set(bk.i0 - 1, bk.i1);
        zoom.commit();
      }
    },
  );

  // A tap elsewhere puts away a point a finger left showing.
  useEffect(() => {
    if (hover === null) return;
    const away = (e: PointerEvent) => {
      if (!(e.target instanceof Node) || !g.ref.current?.contains(e.target)) setHover(null);
    };
    document.addEventListener("pointerdown", away);
    return () => document.removeEventListener("pointerdown", away);
  }, [hover, g.ref]);

  const h = hover !== null ? days[hover] : null;
  // A stretch being dragged across: the points a zoom to it will show.
  const sel = g.sel ? zoom.inside(Math.min(...g.sel), Math.max(...g.sel)) : null;
  const selGain = sel && sel[1] > sel[0] ? gainBetween(days, sel[0], sel[1]) : null;
  const edge = (x: number) => (x < W * 0.16 ? " edge-l" : x > W * 0.84 ? " edge-r" : "");
  const lastIn = b >= n - 1.001;

  return (
    <div className="depotchart" ref={wrap} style={narrow ? undefined : { minWidth: 560 }}>
      <div className="flowwrap">
        <svg ref={g.ref} className={`${narrow ? "chart sm" : "chart"} zchart`} viewBox={`0 0 ${W} ${H}`} width="100%" role="img" aria-label={`${t("chart.value")}. ${t("zoom.aria")}`} {...g.props}>
          <defs>
            <linearGradient id={`${id}g`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stopColor="var(--accent)" stopOpacity=".24" />
              <stop offset="1" stopColor="var(--accent)" stopOpacity="0" />
            </linearGradient>
            <clipPath id={`${id}c`}>
              <rect x={l} y={0} width={iw} height={H} />
            </clipPath>
            <clipPath id={`${id}m`}>
              <rect x={l} y={0} width={iw} height={floor + 1} />
            </clipPath>
          </defs>
          {scale.ticks.map((v) =>
            Y(v) < top - 2 || Y(v) > floor + 2 ? null : (
              <g key={v}>
                <line x1={l} x2={W - r} y1={Y(v)} y2={Y(v)} stroke="var(--line)" strokeDasharray={v > scale.lo ? "3 4" : undefined} />
                <text x={l - 8} y={Y(v) + 4} textAnchor="end">
                  {kEur(v, 2)}
                </text>
              </g>
            ),
          )}
          <g clipPath={`url(#${id}c)`}>
            {sel && <rect className="zsel" x={X(sel[0])} y={top} width={Math.max(X(sel[1]) - X(sel[0]), 1)} height={laneTop + laneH - top} />}
            <g clipPath={`url(#${id}m)`}>
              {area && <path className="area" d={area} fill={`url(#${id}g)`} />}
              {paid && <path className="fade" d={paid} fill="none" stroke="var(--muted)" strokeWidth={1.5} strokeDasharray="5 4" />}
              <path className="draw" pathLength={1} d={line} fill="none" stroke="var(--accent)" strokeWidth={b - a > 160 ? 1.8 : 2.3} strokeLinejoin="round" />
            </g>
            <line className="zero" x1={l} x2={W - r} y1={zeroY} y2={zeroY} />
            {bars.map((x, k) => {
              const xa = X(x.i0 - 1), xb = X(x.i1), w = xb - xa, inset = Math.min(3, w * 0.18);
              const y = BY(Math.max(x.gain, 0)), height = Math.max(Math.abs(BY(x.gain) - zeroY), x.gain ? 1 : 0);
              const text = signedShort(x.gain);
              const fits = labels && Math.abs(x.gain) >= 0.5 && bars.length <= 24 && w - 2 * inset >= text.length * 6.4 + 6;
              return (
                <g key={x.key} className={hb && hb !== x ? "gb dim" : "gb"}>
                  <rect
                    className={`gbar${x.gain < 0 ? " neg" : ""}`}
                    style={{ ["--i" as string]: Math.min(k, 30) }}
                    x={xa + inset}
                    y={y}
                    width={Math.max(w - 2 * inset, 1)}
                    height={height}
                    rx={Math.min(3, (w - 2 * inset) / 3)}
                  />
                  {fits && (
                    <text className={`glbl ${x.gain < 0 ? "neg" : "pos"}`} x={(xa + xb) / 2} y={x.gain < 0 ? y + height + 13 : y - 5} textAnchor="middle">
                      {text}
                    </text>
                  )}
                </g>
              );
            })}
          </g>
          {lastIn && n > 0 && <circle className="pt" style={{ ["--i" as string]: 30 }} cx={X(n - 1)} cy={Y(vals[n - 1])} r={4.5} fill="var(--accent)" />}
          {h && hover !== null && (
            <g pointerEvents="none">
              <line x1={X(hover)} x2={X(hover)} y1={top} y2={laneTop + laneH} stroke="var(--faint)" strokeDasharray="3 3" />
              <circle cx={X(hover)} cy={Y(vals[hover])} r={5} fill="var(--accent)" stroke="var(--surface)" strokeWidth={2} />
            </g>
          )}
          {!labels && bars.length > 0 && (
            <>
              {most > 0.5 && (
                <text x={l - 8} y={barTop + 9} textAnchor="end">
                  {signedShort(most)}
                </text>
              )}
              {least > 0.5 && (
                <text x={l - 8} y={barTop + barH + 2} textAnchor="end">
                  {signedShort(-least)}
                </text>
              )}
            </>
          )}
          {marks.map((m) => (
            <text key={m.key} x={m.x} y={H - 9} textAnchor="middle">
              {m.text}
            </text>
          ))}
        </svg>
        {h && hover !== null && !sel && (
          <div className={`yh-tip${edge(X(hover))}`} style={{ left: `${(X(hover) / W) * 100}%`, top: `${(Y(vals[hover]) / H) * 100}%` }}>
            <b>{longDay(h.date)}</b>
            {withPaid ? (
              <span>
                {eur(h.value)} <small>· {t("depot.paidIn", { amount: eur(h.paid_in) })}</small>
              </span>
            ) : (
              hover > w0 && <span>{t("depot.since", { date: dayMonth(days[w0].date), amount: signedEur(gainBetween(days, w0, hover).gain) })}</span>
            )}
            {hb && <span className={hb.gain < 0 ? "neg" : "pos"}>{`${bucketName(hb)}: ${signedEur(hb.gain)}`}</span>}
          </div>
        )}
        {sel && selGain && (
          <div className={`yh-tip${edge((X(sel[0]) + X(sel[1])) / 2)}`} style={{ left: `${((X(sel[0]) + X(sel[1])) / 2 / W) * 100}%`, top: `${(top / H) * 100}%` }}>
            <b className={selGain.gain < 0 ? "neg" : "pos"}>
              {signedEur(selGain.gain)}
              {selGain.rate !== null ? ` · ${pctS(selGain.rate)}` : ""}
            </b>
            <small>{`${dayMonth(days[sel[0]].date)} – ${dayMonth(days[sel[1]].date)}`}</small>
          </div>
        )}
      </div>
      {zoom.zoomed && <ZoomStrip zoom={zoom} values={vals} label={t("zoom.strip")} />}
      <div className="chart-foot">
        <div className="legend">
          <span>
            <span className="sq" style={{ background: "var(--accent)" }} />
            {t(withPaid ? "inv.valueShort" : "depot.valueMarket")}
          </span>
          {withPaid && (
            <span>
              <span className="sq dash" style={{ background: "var(--muted)" }} />
              {t("inv.paidIn")}
            </span>
          )}
          <span>
            <span className="sq split" />
            {t(bars[0]?.unit === "week" ? "depot.bars.week" : bars[0]?.unit === "day" ? "depot.bars.day" : "depot.bars.month")}
          </span>
        </div>
        <span className="foot-r">
          <button type="button" className={`paid-toggle${withPaid ? " on" : ""}`} aria-pressed={withPaid} onClick={flipPaid} title={t(withPaid ? "depot.paidOff" : "depot.paidOn")}>
            <span className="mini-sw" aria-hidden="true" />
            {t("depot.paidToggle")}
          </button>
          <ZoomNote zoom={zoom} />
        </span>
      </div>
    </div>
  );
}
