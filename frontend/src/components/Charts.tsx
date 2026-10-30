// Charts drawn as plain SVG, ported from the prototype. No chart library, nothing loaded from the web.

import { useEffect, useId, useLayoutEffect, useMemo, useRef, useState, type KeyboardEvent, type PointerEvent as ReactPointerEvent, type ReactNode, type RefObject } from "react";
import { locale, t as tr } from "../i18n";
import { mondayOf, timeOf } from "../lib/depot";
import { dateShort, dayMonth, eur, eur0, figure, monthLabel, monthShort, num, pct, nines, pctS } from "../lib/format";
import { amountsHidden } from "../lib/privacy";
import { reducedMotion, useCountUp, useTween } from "./Motion";
import { FlowParticles, type Band } from "./Showpiece";
import { useZoomGestures, ZoomNote, ZoomStrip, type Zoom } from "./Zoom";

function niceStep(range: number, target = 5) {
  const raw = range / target;
  const mag = Math.pow(10, Math.floor(Math.log10(raw || 1)));
  const n = raw / mag;
  return (n <= 1 ? 1 : n <= 2 ? 2 : n <= 2.5 ? 2.5 : n <= 5 ? 5 : 10) * mag;
}

export function niceScale(min: number, max: number, target = 5) {
  if (min === max) max = min + 1;
  const step = niceStep(max - min, target);
  const lo = Math.floor(min / step) * step;
  const hi = Math.ceil(max / step) * step;
  const ticks: number[] = [];
  for (let v = lo; v <= hi + step / 2; v += step) ticks.push(Math.round(v * 100) / 100);
  return { lo, hi, ticks };
}

// d: decimals of the thousands, for an axis whose steps are finer than 100 €.
export const kEur = (v: number, d = 1) => {
  if (v === 0) return "0";
  const shown = Math.abs(v) >= 1000 ? `${num(v / 1000, Math.abs(v) % 1000 === 0 ? 0 : Math.abs(v) % 100 === 0 ? 1 : d)}k` : num(v, 0);
  const n = amountsHidden() ? nines(shown) : shown;
  return `${n} €`;
};

export function every(n: number, max = 12) {
  return Math.max(1, Math.ceil(n / max));
}

// Chart parts that open the transactions behind them: clickable, and reachable by keyboard.
function pickProps(fn: (() => void) | undefined, label: string, focusable = true) {
  if (!fn) return {};
  // A second shape for the same thing (a Sankey band next to its node) only takes the click.
  if (!focusable) return { "data-pick": "", onClick: fn };
  return {
    role: "button",
    tabIndex: 0,
    "aria-label": label,
    "data-pick": "",
    onClick: fn,
    onKeyDown: (e: KeyboardEvent) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        fn();
      }
    },
  };
}

// --- Sankey --------------------------------------------------------------------

// key is the untranslated name a click reports back; name is what the chart shows.
// fixed marks the Saved / From savings bands, which have no transactions to open.
// onClick replaces onPick for bands that open something of their own (where the savings went).
type Flow = { name: string; amount: number; color: string; key?: string; fixed?: boolean; onClick?: () => void };

export function useNarrow(query = "(max-width: 640px)") {
  const [narrow, setNarrow] = useState(() => typeof matchMedia !== "undefined" && matchMedia(query).matches);
  useEffect(() => {
    const mq = matchMedia(query);
    const on = () => setNarrow(mq.matches);
    mq.addEventListener("change", on);
    return () => mq.removeEventListener("change", on);
  }, [query]);
  return narrow;
}

// Phones get a narrower drawing with larger text instead of a chart to scroll sideways.
const chartClass = (narrow: boolean) => (narrow ? "chart sm" : "chart");
const chartStyle = (narrow: boolean) => (narrow ? undefined : { minWidth: 560 });

// Elsewhere a chart draws at the width it is shown at, so a wide window gets a wider chart with
// text at its normal size instead of a blown-up picture. Before the first measurement it assumes 940.
export function useChartWidth<T extends Element>(off = false, min = 560): [RefObject<T | null>, number] {
  const ref = useRef<T>(null);
  const [w, setW] = useState(0);
  useLayoutEffect(() => {
    const el = ref.current;
    if (!el || off) return;
    // A wrapper's layout width ignores an entrance animation's scale; an <svg> has no such
    // property everywhere, so it is measured on screen.
    const measure = () => setW(Math.round(el instanceof HTMLElement ? el.clientWidth : el.getBoundingClientRect().width));
    measure();
    const ro = new ResizeObserver(measure);
    ro.observe(el);
    return () => ro.disconnect();
  }, [off]);
  return [ref, Math.max(w || 940, min)];
}
// Wider charts also get a little taller, at most 30 %.
export const grow = (W: number) => Math.min(Math.max(W / 940, 1), 1.3);
// About one axis label per 64 pixels.
export const labelsFor = (iw: number) => Math.max(6, Math.floor(iw / 64));

// savedTo splits the saved amount into where it went; without it there is one "Saved" band.
// Destinations money came out of (sold ETFs, taken from savings) join the income side.
export function Sankey({ income, spending, saved, savedTo, onPick }: {
  income: Flow[]; spending: Flow[]; saved: number; savedTo?: Flow[]; onPick?: (side: "income" | "spending", name: string) => void;
}) {
  const [hot, setHot] = useState<string | null>(null);
  const gid = `fl${useId().replace(/[^a-zA-Z0-9]/g, "")}`;
  const pick = (side: "income" | "spending", f: Flow, focusable = true) => ({
    onPointerEnter: () => setHot(`${side}:${f.name}`),
    ...(f.onClick
      ? pickProps(f.onClick, f.name, focusable)
      : onPick && !f.fixed ? pickProps(() => onPick(side, f.key ?? f.name), tr("chart.showTx", { name: f.name }), focusable) : {}),
  });
  const left = income.filter((i) => i.amount > 0);
  const right = spending.filter((g) => g.amount > 0).sort((a, b) => b.amount - a.amount);
  if (savedTo) {
    right.unshift(...savedTo.filter((s) => s.amount > 0));
    left.push(...savedTo.filter((s) => s.amount < 0).map((s) => ({ ...s, amount: -s.amount })));
  } else if (saved > 0) right.unshift({ name: tr("cf.saved"), amount: saved, color: "var(--good)", fixed: true });
  else if (saved < 0) left.push({ name: tr("chart.fromSavings"), amount: -saved, color: "var(--warn)", fixed: true });
  const total = Math.max(left.reduce((a, x) => a + x.amount, 0), 1);
  // On a phone the income column is left out, so income flows straight into savings
  // and spending and the labels stay readable without scrolling sideways.
  const narrow = useNarrow();
  const [box, wide] = useChartWidth<HTMLDivElement>(narrow, 640);
  // The label columns keep their width; the bands stretch with the chart.
  const W = narrow ? 360 : wide, top = 46, nodeW = narrow ? 10 : 12, xL = 190, xR = narrow ? 168 : W - 204;
  const xM = narrow ? 2 : Math.round((xL + xR) / 2), midH = narrow ? 300 : Math.round(300 * grow(W));
  const k = midH / total;
  let y = top;
  const R = right.map((r) => {
    const h = Math.max(r.amount * k, 1.5);
    const o = { ...r, h, y };
    y += Math.max(h, 30) + 7;
    return o;
  });
  let yl = top;
  const L = left.map((l) => {
    const h = Math.max(l.amount * k, 1.5);
    const o = { ...l, h, y: yl };
    yl += Math.max(h, 34) + 8;
    return o;
  });
  const H = Math.max(y, yl, top + midH) + 14;
  const xmOf = (x0: number, x1: number) => (x0 + x1) / 2;
  const band = (x0: number, a0: number, a1: number, x1: number, b0: number, b1: number) => {
    const xm = xmOf(x0, x1);
    return `M${x0} ${a0}C${xm} ${a0} ${xm} ${b0} ${x1} ${b0}L${x1} ${b1}C${xm} ${b1} ${xm} ${a1} ${x0} ${a1}Z`;
  };
  const edge = (x0: number, a: number, x1: number, b: number) => {
    const xm = xmOf(x0, x1);
    return `M${x0} ${a}C${xm} ${a} ${xm} ${b} ${x1} ${b}`;
  };
  // Every band shades from where its money comes from to where it goes, with fine lit edges.
  // The bands pour in from left to right when the chart appears (styles.css).
  const defs: ReactNode[] = [];
  const drawBand = (key: string, i: number, delay: number, x0: number, a0: number, a1: number, x1: number, b0: number, b1: number, from: string, to: string, f: Flow, side: "income" | "spending") => {
    const id = `${gid}-${i}`;
    defs.push(
      <linearGradient key={id} id={id} gradientUnits="userSpaceOnUse" x1={x0} y1={0} x2={x1} y2={0}>
        <stop offset="0" style={{ stopColor: from, stopOpacity: 0.5 }} />
        <stop offset="1" style={{ stopColor: to }} />
      </linearGradient>,
    );
    const on = hot === key ? " hot" : "";
    const d = { ["--d" as string]: `${delay}ms` };
    return (
      <g key={key}>
        <path className={`band${on}`} style={d} d={band(x0, a0, a1, x1, b0, b1)} fill={`url(#${id})`} fillOpacity={side === "income" ? 0.22 : 0.28} {...pick(side, f, false)} />
        <path className={`edge${on}`} style={d} pathLength={1} d={edge(x0, a0, x1, b0)} stroke={`url(#${id})`} />
        <path className={`edge${on}`} style={d} pathLength={1} d={edge(x0, a1, x1, b1)} stroke={`url(#${id})`} />
      </g>
    );
  };
  // The geometry of every band, for the particles that flow along them.
  const geo: Band[] = [];
  const info = new Map<string, Flow>();
  let off = top;
  const leftBands = narrow ? [] : L.map((l, i) => {
    const key = `income:${l.name}`;
    info.set(key, l);
    const delay = 80 + i * 90;
    geo.push({ key, x0: xL + nodeW, a0: l.y, a1: l.y + l.h, x1: xM, b0: off, b1: off + l.h, from: l.color, to: "var(--good)", share: l.amount / total, nw: nodeW, delay });
    const el = drawBand(key, i, delay, xL + nodeW, l.y, l.y + l.h, xM, off, off + l.h, l.color, "var(--good)", l, "income");
    off += l.h;
    return el;
  });
  off = top;
  const rightBands = R.map((r, i) => {
    const key = `spending:${r.name}`;
    info.set(key, r);
    const delay = (narrow ? 80 : 420) + i * 55;
    geo.push({ key, x0: xM + nodeW, a0: off, a1: off + r.h, x1: xR, b0: r.y, b1: r.y + r.h, from: "var(--good)", to: r.color, share: r.amount / total, nw: nodeW, delay });
    const el = drawBand(key, L.length + i, delay, xM + nodeW, off, off + r.h, xR, r.y, r.y + r.h, "var(--good)", r.color, r, "spending");
    off += r.h;
    return el;
  });
  const geoKey = geo.map((g) => `${g.key}:${g.a0.toFixed(1)}:${g.b0.toFixed(1)}:${g.a1.toFixed(1)}:${g.to}`).join("|");
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const bands = useMemo(() => geo, [geoKey, W]);
  // A small card follows the pointer with the band's amount and share; it is moved directly,
  // so following the pointer never re-renders the chart.
  const tip = useRef<HTMLDivElement>(null);
  const shown = useRef<Flow | null>(null);
  const hotFlow = hot ? info.get(hot) ?? null : null;
  if (hotFlow) shown.current = hotFlow;
  const moveTip = (e: ReactPointerEvent) => {
    const el = tip.current, host = box.current;
    if (!el || !host) return;
    const r = host.getBoundingClientRect();
    const tw = el.offsetWidth;
    let x = e.clientX - r.left + 16;
    if (x + tw > r.width - 4) x = e.clientX - r.left - tw - 16;
    el.style.transform = `translate(${Math.round(x)}px,${Math.round(e.clientY - r.top + 16)}px)`;
  };
  const tf = shown.current;
  return (
    <div className="flowwrap" ref={box} style={narrow ? undefined : { minWidth: 640 }}>
    <svg className={`chart sankey${hot ? " has-hot" : ""}`} viewBox={`0 0 ${W} ${H}`} width="100%" role="img" aria-label={tr("chart.sankey")} onPointerMove={moveTip} onPointerLeave={() => setHot(null)}>
      <defs>{defs}</defs>
      {leftBands}
      {rightBands}
      {!narrow && L.map((l) => {
        const ty = l.y + Math.max(l.h / 2 - 6, 10);
        return (
          <g key={`l-${l.name}`} className={`nd${hot === `income:${l.name}` ? " hot" : ""}`} {...pick("income", l)}>
            <rect className="node" x={xL} y={l.y} width={nodeW} height={l.h} rx={2} fill={l.color} />
            <text className="lbl" x={xL - 10} y={ty} textAnchor="end">{l.name}</text>
            <text x={xL - 10} y={ty + 17} textAnchor="end"><FlowAmount value={l.amount} total={total} /></text>
          </g>
        );
      })}
      <rect className="node" x={xM} y={top} width={nodeW} height={midH} rx={2} fill="var(--good)" />
      <text className="lbl" x={narrow ? xM : xM + nodeW / 2} y={top - 24} textAnchor={narrow ? "start" : "middle"}>{tr("cf.income")}</text>
      <text x={narrow ? xM : xM + nodeW / 2} y={top - 9} textAnchor={narrow ? "start" : "middle"}><FlowAmount value={total} /></text>
      {R.map((r) => {
        const ty = r.y + Math.max(r.h / 2 - 6, 10);
        return (
          <g key={`r-${r.name}`} className={`nd${hot === `spending:${r.name}` ? " hot" : ""}`} {...pick("spending", r)}>
            <rect className="node" x={xR} y={r.y} width={nodeW} height={r.h} rx={2} fill={r.color} />
            <text className="lbl" x={xR + nodeW + 10} y={ty}>{r.name}</text>
            <text x={xR + nodeW + 10} y={ty + 17}><FlowAmount value={r.amount} total={total} /></text>
          </g>
        );
      })}
    </svg>
    <FlowParticles bands={bands} W={W} hot={hot} />
    <div ref={tip} className={`flowtip${hotFlow ? " on" : ""}`} aria-hidden="true">
      {tf && (
        <>
          <span className="sw" style={{ background: tf.color }} />
          <b>{tf.name}</b>
          <span className="amt">{eur(tf.amount)}</span>
          <small>{tr("chart.flowShare", { p: pct(tf.amount / total) })}</small>
        </>
      )}
    </div>
    </div>
  );
}

// An amount in the chart that counts up when it first appears, with its share of income.
function FlowAmount({ value, total }: { value: number; total?: number }) {
  const v = useCountUp(value, 1100, true);
  return <>{total ? `${eur(v)} (${pct(value / total)})` : eur(v)}</>;
}

// --- sunburst -------------------------------------------------------------------------

// Groups on the inner ring, their categories on the outer ring. Clicking a group zooms into it:
// its arc sweeps round to the full circle and the outer ring shows only its categories.
export type SunGroup = { key: string; name: string; color: string; amount: number; children: { id: number | null; key: string; name: string; color: string; amount: number }[] };
type Arc = [number, number];
type Layout = Record<string, Arc>;

const TAU = Math.PI * 2;
const easeOut = (x: number) => 1 - Math.pow(1 - x, 3);

function layoutFor(groups: SunGroup[], zoom: string | null): Layout {
  const out: Layout = {};
  const shown = groups.filter((g) => g.amount > 0);
  const total = shown.reduce((a, g) => a + g.amount, 0) || 1;
  let a = 0;
  for (const g of shown) {
    const span = zoom === null ? (g.amount / total) * TAU : zoom === g.key ? TAU : 0;
    // A zoomed-out group collapses where the zoomed one starts, so it folds away instead of jumping.
    const start = zoom === null || zoom === g.key ? a : zoom && shown.findIndex((x) => x.key === zoom) > shown.indexOf(g) ? 0 : TAU;
    out[`g:${g.key}`] = [start, start + span];
    const kids = g.children.filter((c) => c.amount > 0);
    const kt = kids.reduce((x, c) => x + c.amount, 0) || 1;
    let b = start;
    for (const c of kids) {
      const cs = (c.amount / kt) * span;
      out[`c:${g.key}:${c.key}`] = [b, b + cs];
      b += cs;
    }
    if (zoom === null || zoom === g.key) a += span;
  }
  return out;
}

function arcPath(cx: number, cy: number, r0: number, r1: number, [a0, a1]: Arc, pad: number) {
  let s = a0 + pad / 2, e = a1 - pad / 2;
  if (e - s <= 0.0005) return "";
  if (e - s >= TAU - 0.0005) {
    // A full ring: two half arcs, since one arc can't start and end at the same point.
    s = 0;
    e = TAU - 0.0001;
  }
  const p = (r: number, a: number) => `${(cx + r * Math.sin(a)).toFixed(2)} ${(cy - r * Math.cos(a)).toFixed(2)}`;
  const large = e - s > Math.PI ? 1 : 0;
  return `M${p(r1, s)}A${r1} ${r1} 0 ${large} 1 ${p(r1, e)}L${p(r0, e)}A${r0} ${r0} 0 ${large} 0 ${p(r0, s)}Z`;
}

export function Sunburst({ groups, zoom, onZoom, onPickGroup, onPickCategory, label, shown, zoomable = true }: {
  zoomable?: boolean;
  groups: SunGroup[];
  zoom: string | null;
  onZoom: (key: string | null) => void;
  onPickGroup: (key: string) => void;
  onPickCategory: (group: string, id: number | null) => void;
  label: string;
  shown: number;
}) {
  const target = useMemo(() => layoutFor(groups, zoom), [groups, zoom]);
  const [cur, setCur] = useState<Layout>(() => (reducedMotion() ? target : Object.fromEntries(Object.entries(target).map(([k, [a]]) => [k, [a, a] as Arc]))));
  const from = useRef<Layout>(cur);
  useEffect(() => {
    if (reducedMotion()) {
      setCur(target);
      from.current = target;
      return;
    }
    const start = performance.now();
    const origin = from.current;
    let frame = 0;
    const step = (now: number) => {
      const k = easeOut(Math.min(1, (now - start) / 700));
      const next: Layout = {};
      for (const [key, [a1, b1]] of Object.entries(target)) {
        const [a0, b0] = origin[key] ?? [a1, a1];
        next[key] = [a0 + (a1 - a0) * k, b0 + (b1 - b0) * k];
      }
      setCur(next);
      from.current = next;
      if (k < 1) frame = requestAnimationFrame(step);
    };
    frame = requestAnimationFrame(step);
    return () => cancelAnimationFrame(frame);
  }, [target]);

  const cx = 160, cy = 160;
  const zg = zoom ? groups.find((g) => g.key === zoom) : null;
  return (
    <svg className="chart sunburst" viewBox="0 0 320 320" width="320" style={{ maxWidth: "100%" }} role="img" aria-label={tr("sp.breakdown")}>
      <circle cx={cx} cy={cy} r={86} fill="none" stroke="var(--sunk)" strokeWidth={42} />
      {groups.filter((g) => g.amount > 0).map((g) => {
        const arc = cur[`g:${g.key}`];
        if (!arc) return null;
        const d = arcPath(cx, cy, 64, 108, arc, groups.length > 1 && !zoom ? 0.014 : 0);
        return (
          d && (
            <g key={g.key}>
              <path
                className="sb-arc"
                d={d}
                fill={g.color}
                {...pickProps(() => (zoom || !zoomable ? onPickGroup(g.key) : onZoom(g.key)), zoom || !zoomable ? tr("chart.showTx", { name: g.name }) : tr("sb.zoom", { name: g.name }))}
              >
                <title>{`${g.name} ${eur(g.amount)} · ${zoom || !zoomable ? tr("chart.clickForTx") : tr("sb.clickZoom")}`}</title>
              </path>
              {g.children.filter((c) => c.amount > 0).map((c, j) => {
                const ca = cur[`c:${g.key}:${c.key}`];
                const cd = ca && arcPath(cx, cy, 112, 146, ca, 0.012);
                return (
                  cd && (
                    <path key={c.key} className="sb-arc outer" d={cd} fill={c.color} fillOpacity={0.85 - (j % 4) * 0.14} {...pickProps(() => onPickCategory(g.key, c.id), tr("chart.showTx", { name: c.name }))}>
                      <title>{`${c.name} ${eur(c.amount)} · ${tr("chart.clickForTx")}`}</title>
                    </path>
                  )
                );
              })}
            </g>
          )
        );
      })}
      {zg ? (
        <g className="sb-center" {...pickProps(() => onZoom(null), tr("sb.back"))}>
          <circle cx={cx} cy={cy} r={58} fill="transparent" />
          <text x={cx} y={cy - 16} textAnchor="middle" style={{ fontSize: 12 }}>{`‹ ${tr("sb.all")}`}</text>
          <text x={cx} y={cy + 6} textAnchor="middle" style={{ fill: "var(--ink)", fontSize: 13, fontWeight: 600 }}>{zg.name.length > 16 ? `${zg.name.slice(0, 15)}…` : zg.name}</text>
          <text x={cx} y={cy + 28} textAnchor="middle" style={{ fill: "var(--ink)", fontSize: 19, fontWeight: 700 }}>{eur0(zg.amount)}</text>
        </g>
      ) : (
        <g pointerEvents="none">
          <text x={cx} y={cy - 6} textAnchor="middle" style={{ fontSize: 13 }}>{label}</text>
          <text x={cx} y={cy + 20} textAnchor="middle" style={{ fill: "var(--ink)", fontSize: 24, fontWeight: 700 }}>{eur0(shown)}</text>
        </g>
      )}
    </svg>
  );
}

// --- a year of days ---------------------------------------------------------------------

// Every day of a year as a small square, hotter the more was spent: grey without spending, then
// from indigo to a glowing yellow for the priciest days. Days still to come are outlined. The squares ripple in diagonally when the year changes.
export type DayAmount = { date: string; amount: number; count: number };

export function YearHeatmap({ year, days, onPick }: { year: number; days: DayAmount[]; onPick: (date: string) => void }) {
  const [tip, setTip] = useState<{ x: number; y: number; d: string; v: DayAmount | undefined } | null>(null);
  const wrap = useRef<HTMLDivElement>(null);
  const byDate = useMemo(() => new Map(days.map((d) => [d.date, d])), [days]);
  const levels = useMemo(() => {
    const vals = days.map((d) => d.amount).filter((v) => v > 0).sort((a, b) => a - b);
    const q = (f: number) => vals[Math.min(vals.length - 1, Math.floor(f * vals.length))] ?? 0;
    return [q(0.25), q(0.5), q(0.75), q(0.93)];
  }, [days]);
  const jan1 = new Date(year, 0, 1);
  const lead = (jan1.getDay() + 6) % 7;
  const n = (Date.UTC(year + 1, 0, 1) - Date.UTC(year, 0, 1)) / 86400000;
  const today = new Date();
  const todayIso = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;
  const cols = Math.ceil((n + lead) / 7);
  // The squares grow with the room there is, up to a point; beyond that the year sits centred.
  const [box, W] = useChartWidth<HTMLDivElement>(false, 640);
  const left = 34, top = 20, stepX = Math.min((W - left - 4) / cols, 32), cell = stepX * 0.8;
  const ox = Math.max(0, (W - left - cols * stepX - 4) / 2) + left, H = top + 7 * stepX + 2;
  const iso = (i: number) => {
    const d = new Date(year, 0, 1 + i);
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  };
  const monthCols: [number, string][] = [];
  const rects = [];
  for (let i = 0; i < n; i++) {
    const pos = i + lead, col = Math.floor(pos / 7), row = pos % 7;
    const d = iso(i);
    if (d.endsWith("-01")) monthCols.push([col, monthShort(d.slice(0, 7))]);
    const v = byDate.get(d);
    const future = d > todayIso;
    const lvl = !v || v.amount <= 0 ? 0 : v.amount <= levels[0] ? 1 : v.amount <= levels[1] ? 2 : v.amount <= levels[2] ? 3 : v.amount <= levels[3] ? 4 : 5;
    rects.push(
      <rect
        key={d}
        className={`yh-cell l${lvl}${future ? " future" : ""}`}
        style={{ ["--d" as string]: col + row }}
        x={ox + col * stepX}
        y={top + row * stepX}
        width={cell}
        height={cell}
        rx={cell / 4}
        onPointerEnter={(e) => {
          // Measured against the wrapper, which sits outside the scrolling box, so the tip is never cut off.
          const c = e.currentTarget.getBoundingClientRect();
          const w = wrap.current?.getBoundingClientRect();
          if (w) setTip({ x: c.left + c.width / 2 - w.left, y: c.top - w.top, d, v });
        }}
        onClick={() => !future && v && onPick(d)}
      />,
    );
  }
  const wd = (i: number) => new Date(2024, 0, 1 + i).toLocaleDateString(locale(), { weekday: "short" }).replace(".", "");
  return (
    <div className="yh" ref={wrap} onPointerLeave={() => setTip(null)}>
      <div className="scroll" ref={box} onScroll={() => setTip(null)}>
      <svg key={year} className="chart" viewBox={`0 0 ${W} ${H}`} width="100%" style={{ minWidth: 640 }} role="img" aria-label={tr("yh.label", { year })}>
        {monthCols.map(([c, m]) => (
          <text key={m} x={ox + c * stepX} y={12}>{m}</text>
        ))}
        {[0, 2, 4].map((r) => (
          <text key={r} x={ox - 6} y={top + r * stepX + cell / 2 + 4} textAnchor="end">{wd(r)}</text>
        ))}
        {rects}
      </svg>
      </div>
      {tip && (
        <div className="yh-tip" style={{ left: tip.x, top: tip.y }}>
          <b>{new Date(`${tip.d}T12:00:00`).toLocaleDateString(locale(), { weekday: "short", day: "numeric", month: "long" })}</b>
          <span>{tip.v ? tr("yh.spent", { amount: eur(tip.v.amount), n: tip.v.count }) : tip.d > todayIso ? tr("yh.future") : tr("yh.nothing")}</span>
        </div>
      )}
    </div>
  );
}

// --- line (net worth) ------------------------------------------------------------

export function LineChart({ data, color = "var(--accent)", label }: { data: { month: string; value: number }[]; color?: string; label: string }) {
  const narrow = useNarrow();
  const [box, wide] = useChartWidth<SVGSVGElement>(narrow);
  const W = narrow ? 480 : wide, H = narrow ? 300 : Math.round(300 * grow(W)), l = 64, r = 26, t = 18, b = 34;
  const vals = data.map((d) => d.value);
  const mn = Math.min(...vals), mx = Math.max(...vals);
  const { lo, hi, ticks } = niceScale(mn > 0 ? mn * 0.9 : mn, mx, 5);
  const ih = H - t - b, iw = W - l - r, n = data.length;
  const X = (i: number) => l + (n > 1 ? i * (iw / (n - 1)) : iw / 2);
  const Y = (v: number) => t + ih - ((v - lo) / (hi - lo)) * ih;
  const pts = data.map((d, i) => `${X(i)},${Y(d.value)}`).join(" ");
  const skip = every(n, narrow ? 5 : labelsFor(iw));
  return (
    <svg ref={box} className={chartClass(narrow)} viewBox={`0 0 ${W} ${H}`} width="100%" style={chartStyle(narrow)} role="img" aria-label={label}>
      <defs>
        <linearGradient id="nwg" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor={color} stopOpacity=".22" />
          <stop offset="1" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      {ticks.map((v) => (
        <g key={v}>
          <line x1={l} x2={W - r} y1={Y(v)} y2={Y(v)} stroke="var(--line)" strokeDasharray={v > lo ? "3 4" : undefined} />
          <text x={l - 8} y={Y(v) + 4} textAnchor="end">{kEur(v)}</text>
        </g>
      ))}
      {n > 1 && <polygon className="area" points={`${X(0)},${Y(lo)} ${pts} ${X(n - 1)},${Y(lo)}`} fill="url(#nwg)" />}
      <polyline className="draw" pathLength={1} points={pts} fill="none" stroke={color} strokeWidth={2.5} strokeLinejoin="round" />
      {data.map((d, i) => {
        const last = i === n - 1;
        return (
          <g key={d.month}>
            {(n <= 24 || last) && (
              <circle className="pt" style={{ ["--i" as string]: i }} cx={X(i)} cy={Y(d.value)} r={last ? 5.5 : 3.5} fill={last ? color : "var(--surface)"} stroke={color} strokeWidth={2}>
                <title>{`${monthLabel(d.month)} ${eur(d.value)}`}</title>
              </circle>
            )}
            {i % skip === 0 && <text x={X(i)} y={H - 12} textAnchor="middle">{monthLabel(d.month)}</text>}
          </g>
        );
      })}
    </svg>
  );
}

// --- drawdown ----------------------------------------------------------------------

export function DrawdownChart({ data, worst }: { data: { month: string; dd: number }[]; worst: { month: string; dd: number } }) {
  const narrow = useNarrow();
  const [box, wide] = useChartWidth<SVGSVGElement>(narrow);
  const W = narrow ? 480 : wide, H = narrow ? 220 : Math.round(160 * grow(W)), l = 64, r = 26, t = 10, b = 28, n = data.length;
  const low = Math.min(-0.05, ...data.map((d) => d.dd));
  const step = niceStep(-low, 3);
  const min = -Math.ceil(-low / step) * step;
  const ih = H - t - b, iw = W - l - r;
  const X = (i: number) => l + (n > 1 ? i * (iw / (n - 1)) : 0);
  const Y = (v: number) => t + (v / min) * ih;
  const ticks: number[] = [];
  for (let v = 0; v >= min - 1e-9; v -= step) ticks.push(v);
  const pts = data.map((d, i) => `${X(i)},${Y(d.dd)}`).join(" ");
  const wi = data.findIndex((d) => d.month === worst.month);
  const skip = every(n, narrow ? 5 : 10);
  return (
    <svg ref={box} className={chartClass(narrow)} viewBox={`0 0 ${W} ${H}`} width="100%" style={chartStyle(narrow)} role="img" aria-label={tr("chart.drawdown")}>
      {ticks.map((v) => (
        <g key={v}>
          <line x1={l} x2={W - r} y1={Y(v)} y2={Y(v)} stroke="var(--line)" strokeDasharray={v ? "3 4" : undefined} />
          <text x={l - 8} y={Y(v) + 4} textAnchor="end">{v ? pct(v, 0) : "0"}</text>
        </g>
      ))}
      <polygon className="area" points={`${X(0)},${Y(0)} ${pts} ${X(n - 1)},${Y(0)}`} fill="var(--bad)" fillOpacity={0.18} />
      <polyline className="draw" pathLength={1} points={pts} fill="none" stroke="var(--bad)" strokeWidth={1.8} />
      {wi >= 0 && worst.dd < 0 && (
        <g>
          <circle className="pt" style={{ ["--i" as string]: 30 }} cx={X(wi)} cy={Y(worst.dd)} r={4} fill="var(--bad)" />
          <text className="lbl" x={X(wi) + (wi > n * 0.75 ? -8 : 8)} y={Y(worst.dd) + 4} textAnchor={wi > n * 0.75 ? "end" : "start"}>
            {`${pctS(worst.dd)} (${monthLabel(worst.month)})`}
          </text>
        </g>
      )}
      {data.map((d, i) => i % skip === 0 && <text key={d.month} x={X(i)} y={H - 8} textAnchor="middle">{monthLabel(d.month)}</text>)}
    </svg>
  );
}

// --- monthly returns heatmap ---------------------------------------------------------

// `mark`: months to outline, such as the best and the worst one.
export function Heatmap({ returns, mark = [] }: { returns: { month: string; r: number }[]; mark?: string[] }) {
  const byYear = new Map<number, Map<number, number>>();
  for (const x of returns) {
    const y = Number(x.month.slice(0, 4)), m = Number(x.month.slice(5, 7));
    if (!byYear.has(y)) byYear.set(y, new Map());
    byYear.get(y)!.set(m, x.r);
  }
  const years = [...byYear.keys()].sort();
  // Columns share the width up to a point; beyond that the table sits centred.
  const [box, W] = useChartWidth<SVGSVGElement>(false, 600);
  const ch = 36, t = 24, cw = Math.min((W - 52) / 12, 110), l = Math.max(48, (W - 12 * cw - 4) / 2), H = t + years.length * ch + 4;
  const names = Array.from({ length: 12 }, (_, i) => monthShort(`2000-${String(i + 1).padStart(2, "0")}`));
  return (
    <svg ref={box} className="chart" viewBox={`0 0 ${W} ${H}`} width="100%" style={{ minWidth: 600 }} role="img" aria-label={tr("chart.heatmap")}>
      {names.map((m, i) => <text key={m} x={l + i * cw + cw / 2} y={14} textAnchor="middle">{m}</text>)}
      {years.map((y, yi) => (
        <g key={y}>
          <text x={l - 10} y={t + yi * ch + ch / 2 + 4} textAnchor="end">{y}</text>
          {names.map((m, mi) => {
            const x = l + mi * cw + 2, yy = t + yi * ch + 2, w = cw - 4, h = ch - 4;
            const r = byYear.get(y)!.get(mi + 1);
            if (r === undefined) return <rect key={m} x={x} y={yy} width={w} height={h} rx={6} fill="none" stroke="var(--line)" strokeDasharray="3 3" />;
            const a = Math.min(Math.abs(r) / 0.07, 1) * 0.85 + 0.12;
            return (
              <g key={m}>
                <rect className="hm" style={{ ["--i" as string]: yi * 12 + mi }} x={x} y={yy} width={w} height={h} rx={6} fill={r >= 0 ? "var(--good)" : "var(--bad)"} fillOpacity={a.toFixed(2)}>
                  <title>{`${m} ${y}: ${pctS(r)}`}</title>
                </rect>
                <text className="cell" x={x + w / 2} y={yy + h / 2 + 4} textAnchor="middle" style={{ fill: a > 0.55 ? "#fff" : "var(--ink)" }}>
                  {`${r > 0 ? "+" : r < 0 ? "\u2212" : ""}${num(Math.abs(r) * 100, 1)}`}
                </text>
                {mark.includes(`${y}-${String(mi + 1).padStart(2, "0")}`) && (
                  <rect className="hm-mark" x={x - 1.5} y={yy - 1.5} width={w + 3} height={h + 3} rx={7.5} fill="none" stroke="var(--ink)" strokeWidth={1.6} />
                )}
              </g>
            );
          })}
        </g>
      ))}
    </svg>
  );
}

// --- projection fan ----------------------------------------------------------------------

// below: the share of simulated futures that end the year under what was paid in by then.
export type ProjectionPoint = { m: number; p10: number; p50: number; p90: number; paid: number; below: number };
export type Projection = ProjectionPoint[];
export type Milestone = { m: number; value: number };

// The forecast as one calm picture: the range 8 in 10 futures stay in, the middle path through it,
// and the money you paid in as a filled area underneath, so the gap between the two is the growth.
// `span` is how many months are in view (it glides when the range changes), `at` the month the
// cursor stands on. Moving over the chart looks at any month, a click or tap keeps it there.
export function ForecastChart({ data, span, at, first, milestones, onHover, onPin }: {
  data: Projection;
  span: number;
  at: number;
  first: string;
  milestones: Milestone[];
  onHover: (m: number | null) => void;
  onPin: (m: number) => void;
}) {
  const narrow = useNarrow();
  const [box, wide] = useChartWidth<HTMLDivElement>(narrow, 320);
  const clip = useId();
  const W = narrow ? 480 : wide, H = narrow ? 300 : Math.round(300 * grow(W)), l = 64, r = 18, t = 26, b = 34;
  const ih = H - t - b, iw = W - l - r;
  const n = Math.min(data.length - 1, Math.ceil(span - 1e-6));
  const shown = data.slice(0, n + 1);
  const top = Math.max(1, ...shown.map((d) => d.p90)) * 1.06;
  const step = niceStep(top, narrow ? 4 : 5);
  const ticks: number[] = [];
  for (let v = 0; v <= top; v += step) ticks.push(v);
  const X = (m: number) => l + (m / Math.max(span, 1e-6)) * iw, Y = (v: number) => t + ih - (v / top) * ih;
  const line = (f: (d: ProjectionPoint) => number) => shown.map((d) => `${X(d.m).toFixed(1)},${Y(f(d)).toFixed(1)}`).join(" ");
  const up = line((d) => d.p90);
  const dn = [...shown].reverse().map((d) => `${X(d.m).toFixed(1)},${Y(d.p10).toFixed(1)}`).join(" ");
  const base = `${X(n).toFixed(1)},${Y(0)} ${X(0)},${Y(0)}`;
  const y0 = Number(first.slice(0, 4)), m0 = Number(first.slice(5, 7)) - 1;
  const ym = (m: number) => {
    const k = m0 + m;
    return `${y0 + Math.floor(k / 12)}-${String((k % 12) + 1).padStart(2, "0")}`;
  };
  // Axis: months for up to two years in view, whole years (every 1, 2, 5 or 10) beyond.
  const axis = useMemo(() => {
    const out: { m: number; text: string }[] = [];
    const room = narrow ? 5 : labelsFor(iw);
    if (span <= 24.5) {
      const every = [1, 2, 3, 6].find((e) => span / e <= room) ?? 6;
      for (let m = 1; m <= n; m++) if ((m0 + m) % every === 0) out.push({ m, text: monthLabel(ym(m)) });
    } else {
      const every = [1, 2, 5, 10].find((e) => span / 12 / e <= room) ?? 10;
      for (let m = 1; m <= n; m++) if ((m0 + m) % 12 === 0 && (y0 + (m0 + m) / 12) % every === 0) out.push({ m, text: String(y0 + (m0 + m) / 12) });
    }
    return out.filter((a) => X(a.m) < W - r - 16);
  }, [span, n, W, first]);
  const pick = (e: { clientX: number; currentTarget: SVGSVGElement }) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * W;
    return Math.max(0, Math.min(n, Math.round(((x - l) / iw) * span)));
  };
  const key = (e: KeyboardEvent<SVGSVGElement>) => {
    const d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
    if (!d) return;
    e.preventDefault();
    onPin(Math.max(0, Math.min(n, at + d * (e.shiftKey ? 12 : 1))));
  };
  const c = shown[Math.min(at, n)];
  const end = shown[n];
  // Direct labels at the right end, only where they don't run into each other.
  const midY = Y(end.p50), paidY = Y(end.paid);
  const apart = Math.abs(midY - paidY) > 16;
  // A milestone flag near the right end already names the middle path's height there.
  const crowded = milestones.some((s) => s.m <= n && X(s.m) > W - r - 110);
  return (
    <div className="flowwrap fcchart" ref={box}>
      <svg
        className={chartClass(narrow)}
        viewBox={`0 0 ${W} ${H}`}
        width="100%"
        role="img"
        tabIndex={0}
        aria-label={tr("chart.fc")}
        onPointerMove={(e) => onHover(pick(e))}
        onPointerDown={(e) => e.pointerType !== "mouse" && onHover(pick(e))}
        onPointerLeave={() => onHover(null)}
        onClick={(e) => onPin(pick(e))}
        onKeyDown={key}
      >
        <defs>
          <clipPath id={clip}>
            <rect x={l} y={0} width={iw} height={H} />
          </clipPath>
          <linearGradient id={`${clip}g`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="var(--accent)" stopOpacity=".26" />
            <stop offset="1" stopColor="var(--accent)" stopOpacity=".08" />
          </linearGradient>
        </defs>
        {ticks.map((v) => (
          <g key={v}>
            <line x1={l} x2={W - r} y1={Y(v)} y2={Y(v)} stroke="var(--line)" strokeDasharray={v ? "3 4" : undefined} />
            <text x={l - 8} y={Y(v) + 4} textAnchor="end">{kEur(v)}</text>
          </g>
        ))}
        <g clipPath={`url(#${clip})`}>
          <polygon points={`${up} ${dn}`} fill={`url(#${clip}g)`} />
          <polygon points={`${line((d) => d.paid)} ${base}`} fill="var(--muted)" fillOpacity={0.14} />
          <polyline points={line((d) => d.paid)} fill="none" stroke="var(--muted)" strokeWidth={1.5} />
          <polyline className="draw" pathLength={1} points={line((d) => d.p50)} fill="none" stroke="var(--accent)" strokeWidth={2.6} strokeLinejoin="round" />
        </g>
        {milestones.filter((s) => s.m <= n).map((s) => (
          <g key={s.value} className="fc-ms" onClick={(e) => (e.stopPropagation(), onPin(s.m))}>
            <circle cx={X(s.m)} cy={Y(s.value)} r={4.5} fill="var(--surface)" stroke="var(--accent)" strokeWidth={2} />
            <text x={X(s.m)} y={Y(s.value) - 10} textAnchor="middle">{kEur(s.value)}</text>
          </g>
        ))}
        {X(n) > W - r - 2 && (
          <g className="fc-endlbl">
            {!crowded && <text x={W - r - 4} y={midY - 8} textAnchor="end">{tr("fc.chart.middle")}</text>}
            {apart && <text x={W - r - 4} y={paidY < midY ? paidY - 8 : paidY + 16} textAnchor="end">{tr("fc.chart.paid")}</text>}
          </g>
        )}
        {axis.map((a) => <text key={a.m} x={X(a.m)} y={H - 12} textAnchor="middle">{a.text}</text>)}
        {c && (
          <g className="fc-cursor" pointerEvents="none">
            <line x1={X(c.m)} x2={X(c.m)} y1={t - 6} y2={t + ih} stroke="var(--ink)" strokeOpacity={0.35} />
            <circle cx={X(c.m)} cy={Y(c.p90)} r={3} fill="var(--surface)" stroke="var(--accent)" strokeWidth={1.5} />
            <circle cx={X(c.m)} cy={Y(c.p10)} r={3} fill="var(--surface)" stroke="var(--accent)" strokeWidth={1.5} />
            <circle cx={X(c.m)} cy={Y(c.paid)} r={3.5} fill="var(--muted)" stroke="var(--surface)" strokeWidth={1.5} />
            <circle cx={X(c.m)} cy={Y(c.p50)} r={6} fill="var(--accent)" stroke="var(--surface)" strokeWidth={2.5} />
            <text x={Math.min(Math.max(X(c.m), l + 24), W - r - 24)} y={t - 12} textAnchor="middle" className="fc-when-lbl">{c.m ? monthLabel(ym(c.m)) : tr("fc.today")}</text>
          </g>
        )}
      </svg>
    </div>
  );
}

// Monte Carlo on the client: log-normal monthly returns, 800 paths, seeded so the chart doesn't jump.
// One point per month, so the chart can be looked at month by month.
// raise grows the monthly payment once a year (a savings plan that keeps being raised).
// paidIn is money already paid in before today, so "below what you paid" counts it too.
export function project(start: number, monthly: number, years: number, ret: number, vol: number, raise = 0, paidIn = start): Projection {
  let seed = 7;
  const rand = () => {
    seed |= 0;
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  const paths = 800, months = years * 12, mu = Math.log(1 + ret) / 12 - (vol * vol) / 24, sd = vol / Math.sqrt(12);
  const vals = Array.from({ length: months + 1 }, () => new Float64Array(paths));
  const pay = (m: number) => monthly * Math.pow(1 + raise, Math.floor((m - 1) / 12));
  const paid = [paidIn];
  for (let m = 1; m <= months; m++) paid.push(paid[m - 1] + pay(m));
  for (let p = 0; p < paths; p++) {
    let v = start;
    vals[0][p] = v;
    for (let m = 1; m <= months; m++) {
      const z = Math.sqrt(-2 * Math.log(rand() || 1e-9)) * Math.cos(2 * Math.PI * rand());
      v = (v + pay(m)) * Math.exp(mu + sd * z);
      vals[m][p] = v;
    }
  }
  const q = (a: Float64Array, f: number) => a[Math.floor(f * (paths - 1))];
  const out = vals.map((a, m) => {
    a.sort();
    // How many futures end below what was paid in by then: the first sorted value at or above it.
    let lo = 0, hi = paths;
    while (lo < hi) {
      const mid = (lo + hi) >> 1;
      if (a[mid] < paid[m]) lo = mid + 1;
      else hi = mid;
    }
    return { m, p10: q(a, 0.1), p50: q(a, 0.5), p90: q(a, 0.9), paid: paid[m], below: m ? lo / paths : 0 };
  });
  // Month-to-month wobble in the percentiles is sampling noise, not a forecast: smooth it over five months.
  const smooth = (k: "p10" | "p50" | "p90") => {
    const raw = out.map((d) => d[k]);
    for (let m = 1; m < raw.length; m++) {
      const w = Math.min(2, m, raw.length - 1 - m);
      let sum = 0;
      for (let j = m - w; j <= m + w; j++) sum += raw[j];
      out[m][k] = sum / (2 * w + 1);
    }
  };
  smooth("p10");
  smooth("p50");
  smooth("p90");
  return out;
}

// Round sums the middle path passes on its way: the first month it gets there.
export function milestones(data: Projection, start: number): Milestone[] {
  const out: Milestone[] = [];
  for (const value of [10_000, 25_000, 50_000, 100_000, 250_000, 500_000, 1_000_000]) {
    if (value <= start * 1.05) continue;
    const hit = data.find((d) => d.p50 >= value);
    if (hit) out.push({ m: hit.m, value });
  }
  return out.slice(0, 4);
}

// --- one series of bars with its average (drilldown page) ---------------------------

export function AmountBars({ data, color, label, avgLabel }: {
  data: { key: string; label: string; value: number; title: string }[]; color: string; label: string; avgLabel?: string;
}) {
  const narrow = useNarrow();
  const [box, wide] = useChartWidth<SVGSVGElement>(narrow);
  const W = narrow ? 480 : wide, H = narrow ? 240 : Math.round(240 * grow(W)), l = 60, r = 16, t = 18, b = 34;
  const max = Math.max(1, ...data.map((d) => d.value));
  const { hi, ticks } = niceScale(0, max, 4);
  const ih = H - t - b, iw = W - l - r, step = iw / Math.max(data.length, 1);
  const Y = (v: number) => t + ih - (Math.max(v, 0) / hi) * ih;
  const skip = every(data.length, narrow ? 6 : labelsFor(iw));
  const avg = data.length ? data.reduce((a, d) => a + d.value, 0) / data.length : 0;
  return (
    <svg ref={box} className={chartClass(narrow)} viewBox={`0 0 ${W} ${H}`} width="100%" style={chartStyle(narrow)} role="img" aria-label={label}>
      {ticks.map((v) => (
        <g key={v}>
          <line x1={l} x2={W - r} y1={Y(v)} y2={Y(v)} stroke="var(--line)" strokeDasharray={v ? "3 4" : undefined} />
          <text x={l - 8} y={Y(v) + 4} textAnchor="end">{kEur(v)}</text>
        </g>
      ))}
      {data.map((d, i) => {
        const cx = l + step * i + step / 2, bw = Math.min(34, step * 0.62);
        return (
          <g key={d.key}>
            <rect className="bar" style={{ ["--i" as string]: i }} x={cx - bw / 2} y={Y(d.value)} width={bw} height={t + ih - Y(d.value)} rx={4} fill={color}>
              <title>{d.title}</title>
            </rect>
            {i % skip === 0 && <text x={cx} y={H - 12} textAnchor="middle">{d.label}</text>}
          </g>
        );
      })}
      {avg > 0 && data.length > 1 && (
        <g className="fade">
          <line x1={l} x2={W - r} y1={Y(avg)} y2={Y(avg)} stroke="var(--ink)" strokeOpacity={0.55} strokeDasharray="6 5" strokeWidth={1.4} />
          <text className="lbl" x={W - r} y={Y(avg) - 6} textAnchor="end">{`${avgLabel ?? tr("chart.average")} ${eur0(avg)}`}</text>
        </g>
      )}
    </svg>
  );
}

// --- one ETF's price over time -------------------------------------------------------------

export type PricePoint = { d: string; p: number };

// Labels along a time axis for the points from i0 to i1, spanning `days` days: years, months, weeks or
// days, whichever fits, thinned by a rule that holds while zooming, so they don't jump about.
export const axisUnit = (days: number, monthly: boolean) => (days > 1100 ? "year" : days > 80 || monthly ? "month" : days > 20 ? "week" : "day");
export function axisMarks(dates: string[], i0: number, i1: number, days: number, room: number): { i: number; text: string }[] {
  const unit = axisUnit(days, dates[0]?.length === 7);
  const found: { i: number; k: number; text: string }[] = [];
  for (let i = Math.max(i0, 1); i <= i1; i++) {
    const d = dates[i], p = dates[i - 1];
    if (unit === "year" && d.slice(0, 4) !== p.slice(0, 4)) found.push({ i, k: Number(d.slice(0, 4)), text: d.slice(0, 4) });
    else if (unit === "month" && d.slice(0, 7) !== p.slice(0, 7)) found.push({ i, k: Number(d.slice(0, 4)) * 12 + Number(d.slice(5, 7)), text: monthLabel(d) });
    else if (unit === "week" && mondayOf(d) !== mondayOf(p)) found.push({ i, k: Math.round(timeOf(mondayOf(d)) / (7 * 864e5)), text: dayMonth(d) });
    else if (unit === "day") found.push({ i, k: i, text: dayMonth(d) });
  }
  const step = every(found.length, room);
  return found.filter((m) => m.k % step === 0).map(({ i, text }) => ({ i, text }));
}

// The price line with the days you bought marked on it, your average buy price as a dashed line,
// and a crosshair that shows the price of any day under the pointer. It zooms (components/Zoom.tsx):
// the zoom's positions are days since the first point, so the line keeps its time scale.
export function PriceChart({ data, buys = [], avg = null, label, zoom }: { data: PricePoint[]; buys?: { date: string; amount: number }[]; avg?: number | null; label: string; zoom: Zoom }) {
  const narrow = useNarrow();
  const [box, wide] = useChartWidth<HTMLDivElement>(narrow);
  const [hover, setHover] = useState<number | null>(null);
  const W = narrow ? 480 : wide, H = narrow ? 300 : Math.round(300 * grow(W)), l = 64, r = 20, top = 18, bottom = 34, n = data.length;
  const ih = H - top - bottom, iw = W - l - r;
  const { a, b } = zoom;
  const [w0, w1] = zoom.to;
  // The price axis fits what is in view (and your average price while the whole range shows).
  const scale = useMemo(() => {
    let mn = Infinity, mx = -Infinity;
    for (let i = w0; i <= w1 && i < n; i++) {
      mn = Math.min(mn, data[i].p);
      mx = Math.max(mx, data[i].p);
    }
    if (avg && avg > 0 && !zoom.zoomed) {
      mn = Math.min(mn, avg);
      mx = Math.max(mx, avg);
    }
    if (!isFinite(mn)) [mn, mx] = [0, 1];
    const room = (mx - mn) * 0.07 || mx * 0.02 || 1;
    return niceScale(Math.max(mn - room, 0), mx + room * 0.5, 5);
  }, [data, n, w0, w1, avg, zoom.zoomed]);
  const lo = useTween(scale.lo, 420), hi = useTween(scale.hi, 420);
  const X = (x: number) => l + ((x - a) / (b - a || 1)) * iw;
  const Y = (v: number) => top + ih - ((v - lo) / (hi - lo || 1)) * ih;
  const P = zoom.pos;
  const d0 = n ? Date.parse(data[0].d) : 0;
  const at = (iso: string) => (Date.parse(iso) - d0) / 864e5;
  const i0 = Math.max(0, zoom.near(a) - 1), i1 = Math.min(n - 1, zoom.near(b) + 1);
  let pts = "";
  for (let i = i0; i <= i1; i++) pts += `${i > i0 ? "L" : "M"}${X(P(i)).toFixed(1)} ${Y(data[i].p).toFixed(1)}`;
  const floor = top + ih;
  const dates = useMemo(() => data.map((p) => p.d), [data]);
  const axis = axisMarks(dates, zoom.near(a), zoom.near(b), b - a, narrow ? 5 : labelsFor(iw)).filter((m) => X(P(m.i)) >= l + 10 && X(P(m.i)) <= W - r - 14);
  const marks = buys.filter((x) => n && x.date >= data[w0].d && x.date <= data[w1].d);
  const maxBuy = Math.max(1, ...marks.map((x) => x.amount));
  const g = useZoomGestures(zoom, { l, iw, W, H }, (x) => setHover(x === null ? null : zoom.near(x)));
  const hv = hover !== null && hover < n ? data[hover] : null;
  const first = n ? data[w0].p : 0;
  const up = n > 1 && data[w1].p >= first;
  const color = up ? "var(--accent)" : "var(--bad)";
  const sel = g.sel ? zoom.inside(Math.min(...g.sel), Math.max(...g.sel)) : null;
  const edge = (x: number) => (x < W * 0.16 ? " edge-l" : x > W * 0.84 ? " edge-r" : "");
  const uid = useId().replace(/:/g, "");
  return (
    <div className="pricechart" ref={box} style={chartStyle(narrow)}>
      <div className="flowwrap">
        <svg ref={g.ref} className={`${chartClass(narrow)} zchart`} viewBox={`0 0 ${W} ${H}`} width="100%" role="img" aria-label={`${label}. ${tr("zoom.aria")}`} {...g.props}>
          <defs>
            <linearGradient id={`${uid}g`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stopColor={color} stopOpacity=".22" />
              <stop offset="1" stopColor={color} stopOpacity="0" />
            </linearGradient>
            <clipPath id={`${uid}c`}>
              <rect x={l} y={0} width={iw} height={H} />
            </clipPath>
          </defs>
          {scale.ticks.map((v) =>
            Y(v) < top - 2 || Y(v) > floor + 2 ? null : (
              <g key={v}>
                <line x1={l} x2={W - r} y1={Y(v)} y2={Y(v)} stroke="var(--line)" strokeDasharray={v > scale.lo ? "3 4" : undefined} />
                <text x={l - 8} y={Y(v) + 4} textAnchor="end">{figure(v, v < 10 ? 2 : 0)}</text>
              </g>
            ),
          )}
          <g clipPath={`url(#${uid}c)`}>
            {sel && <rect className="zsel" x={X(P(sel[0]))} y={top} width={Math.max(X(P(sel[1])) - X(P(sel[0])), 1)} height={ih} />}
            {n > 1 && <path className="area" d={`${pts}L${X(P(i1)).toFixed(1)} ${floor}L${X(P(i0)).toFixed(1)} ${floor}Z`} fill={`url(#${uid}g)`} />}
            {avg && avg > 0 && (
              <line className="fade" x1={l} x2={W - r} y1={Y(avg)} y2={Y(avg)} stroke="var(--accent)" strokeWidth={1.4} strokeDasharray="6 4" />
            )}
            <path className="draw" pathLength={1} d={pts} fill="none" stroke={color} strokeWidth={2} strokeLinejoin="round" />
            {marks.map((x, i) => {
              const p = data[zoom.near(at(x.date))];
              return <circle key={`${x.date}-${i}`} className="pt buy" style={{ ["--i" as string]: Math.min(i, 40) }} cx={X(at(x.date))} cy={Y(p.p)} r={2.5 + 2.5 * Math.sqrt(x.amount / maxBuy)} fill="var(--accent)" stroke="var(--surface)" strokeWidth={1.2} />;
            })}
          </g>
          {hv && hover !== null && (
            <g pointerEvents="none">
              <line x1={X(P(hover))} x2={X(P(hover))} y1={top} y2={floor} stroke="var(--faint)" strokeDasharray="3 3" />
              <circle cx={X(P(hover))} cy={Y(hv.p)} r={5} fill={color} stroke="var(--surface)" strokeWidth={2} />
            </g>
          )}
          {avg && avg > 0 && Y(avg) > top + 8 && Y(avg) < floor - 4 && (
            <text className="lbl fade" x={W - r - 4} y={Y(avg) - 6} textAnchor="end" style={{ fill: "var(--accent-ink)" }}>{tr("fund.avgLine", { price: eur(avg) })}</text>
          )}
          {axis.map((m) => <text key={m.i} x={X(P(m.i))} y={H - 12} textAnchor="middle">{m.text}</text>)}
        </svg>
        {hv && hover !== null && !sel && (
          <div className={`yh-tip${edge(X(P(hover)))}`} style={{ left: `${(X(P(hover)) / W) * 100}%`, top: `${(Y(hv.p) / H) * 100}%` }}>
            <b>{new Date(`${hv.d}T12:00:00`).toLocaleDateString(locale(), { day: "numeric", month: "short", year: "numeric" })}</b>
            <span>{eur(hv.p)} · {pctS(hv.p / first - 1)}</span>
          </div>
        )}
        {sel && sel[1] > sel[0] && (
          <div className={`yh-tip${edge((X(P(sel[0])) + X(P(sel[1]))) / 2)}`} style={{ left: `${((X(P(sel[0])) + X(P(sel[1]))) / 2 / W) * 100}%`, top: `${(top / H) * 100}%` }}>
            <b className={data[sel[1]].p >= data[sel[0]].p ? "pos" : "neg"}>{pctS(data[sel[1]].p / data[sel[0]].p - 1)}</b>
            <small>{`${dayMonth(data[sel[0]].d)} – ${dayMonth(data[sel[1]].d)}`}</small>
          </div>
        )}
      </div>
      {zoom.zoomed && <ZoomStrip zoom={zoom} values={data.map((p) => p.p)} label={tr("zoom.strip")} />}
      <div className="chart-foot end">
        <ZoomNote zoom={zoom} />
      </div>
    </div>
  );
}

// A tiny trend line for a table row.
export function Sparkline({ values, width = 96, height = 28 }: { values: number[]; width?: number; height?: number }) {
  if (values.length < 3) return null;
  const mn = Math.min(...values), mx = Math.max(...values);
  const X = (i: number) => 1 + (i / (values.length - 1)) * (width - 2);
  const Y = (v: number) => 2 + (height - 4) - ((v - mn) / (mx - mn || 1)) * (height - 4);
  const up = values[values.length - 1] >= values[0];
  return (
    <svg className="spark" width={width} height={height} viewBox={`0 0 ${width} ${height}`} aria-hidden="true">
      <polyline points={values.map((v, i) => `${X(i).toFixed(1)},${Y(v).toFixed(1)}`).join(" ")} fill="none" stroke={up ? "var(--good)" : "var(--bad)"} strokeWidth={1.6} strokeLinejoin="round" />
    </svg>
  );
}

// A handful of slim bars beside a number: how it went over the period, nothing to read.
// The last bar is the most recent step and the only one at full strength.
export function MiniBars({ values, color, label }: { values: number[]; color: string; label?: string }) {
  if (values.length < 3) return null;
  const list = values.slice(-14);
  const mx = Math.max(...list.map((v) => Math.abs(v)), 1);
  return (
    <span className="minibars" title={label} aria-hidden="true" style={{ ["--c" as string]: color }}>
      {list.map((v, i) => (
        <span key={i} style={{ ["--h" as string]: `${Math.max(6, (Math.abs(v) / mx) * 100).toFixed(1)}%`, ["--i" as string]: i }} />
      ))}
    </span>
  );
}

// Every charge of a recurring payment as a dot at its amount, joined by steps: a price change is a
// visible step, a pause a gap in the dots. The amount of each price level is written once beside it.
export function PaySteps({ data, color, label }: { data: { date: string; amount: number }[]; color: string; label: string }) {
  const [box, wide] = useChartWidth<SVGSVGElement>(false, 320);
  if (data.length < 2) return null;
  const W = wide, H = 132, l = 12, r = 64, t = 18, b = 24;
  const t0 = Date.parse(data[0].date), t1 = Date.parse(data[data.length - 1].date);
  const lo = Math.min(...data.map((d) => d.amount)), hi = Math.max(...data.map((d) => d.amount));
  const pad = (hi - lo) * 0.35 || hi * 0.2 || 1;
  const X = (d: string) => l + ((Date.parse(d) - t0) / Math.max(t1 - t0, 1)) * (W - l - r);
  const Y = (v: number) => t + (1 - (v - (lo - pad)) / (hi - lo + 2 * pad)) * (H - t - b);
  let path = `M${X(data[0].date).toFixed(1)},${Y(data[0].amount).toFixed(1)}`;
  for (let i = 1; i < data.length; i++) path += `H${X(data[i].date).toFixed(1)}V${Y(data[i].amount).toFixed(1)}`;
  // One label per price level, at the right end of where it held.
  const levels: { amount: number; at: number }[] = [];
  data.forEach((d, i) => {
    if (i === 0 || Math.abs(d.amount - data[i - 1].amount) > 0.004) levels.push({ amount: d.amount, at: i });
  });
  const ends = levels.map((_, k) => (k + 1 < levels.length ? levels[k + 1].at - 1 : data.length - 1));
  const year = (d: string) => new Date(`${d}T12:00:00`).toLocaleDateString(locale(), { month: "short", year: "numeric" });
  return (
    <svg ref={box} className="chart paysteps" viewBox={`0 0 ${W} ${H}`} width="100%" role="img" aria-label={label}>
      <path className="draw" d={path} fill="none" stroke={color} strokeWidth={2} strokeLinejoin="round" pathLength={1} />
      {data.map((d, i) => (
        <circle key={d.date + i} className="pop" style={{ ["--i" as string]: i }} cx={X(d.date)} cy={Y(d.amount)} r={3.4} fill="var(--surface)" stroke={color} strokeWidth={1.8}>
          <title>{`${dateShort(d.date)}: ${eur(d.amount)}`}</title>
        </circle>
      ))}
      {levels.map((lv, k) => {
        const last = k === levels.length - 1;
        const x = last ? W - r + 8 : X(data[ends[k]].date);
        return (
          <text key={lv.at} className={last ? "lbl strong" : "lbl"} x={x} y={Y(lv.amount) + (last ? 4 : -9)} textAnchor={last ? "start" : "end"}>
            {eur(lv.amount)}
          </text>
        );
      })}
      <text x={l} y={H - 6}>{year(data[0].date)}</text>
      <text x={W - r} y={H - 6} textAnchor="end">{year(data[data.length - 1].date)}</text>
    </svg>
  );
}
