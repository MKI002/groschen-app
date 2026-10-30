// The Overview's money flow as one stream through every month: what came over from the month
// before, what came in, where it went, and what carried on into the next month. It scrolls
// sideways from the first booking to today, one month at a time, and follows the shared period.

import { useEffect, useId, useLayoutEffect, useMemo, useRef, useState, type KeyboardEvent, type PointerEvent as ReactPointerEvent, type ReactNode, type RefObject } from "react";
import { catName, t as tr, useLang } from "../i18n";
import { colorVar, eur, eur0, monthLong } from "../lib/format";
import type { SavedDest, Timeline, TimelineMonth } from "../lib/types";
import { reducedMotion } from "./Motion";
import { groupColor, groupName } from "./SavedTo";
import { useNarrow } from "./Charts";

// What a click on a band opens: an income category, a spending group, or where the savings went.
export type TimelinePick = { kind: "income"; id: number | null } | { kind: "group"; name: string } | { kind: "saved"; focus: SavedDest };

// note: which way unusual money went ("abgebucht"), shown after the name, or under it on phones.
type Flow = { key: string; name: string; amount: number; color: string; note?: string; pick?: TimelinePick };
// A flow placed on the chart: its node at (x, y) with height h, meeting the month's bar at s; its
// label has the room from slot down to slot + sh.
type Placed = Flow & { x: number; y: number; h: number; s: number; slot: number; sh: number };
type Col = { m: TimelineMonth; x: number; cin: number; cout: number; inH: number; h: number; ins: Placed[]; outs: Placed[]; bottom: number };
// scale: how tall the fullest month's bar is drawn.
type Layout = { cols: Col[]; colW: number; pad: number; W: number; H: number; L: number; cap: number; scale: number };

const NW = 12; // the month's bar and the nodes
const HEAD = 48; // room for the month names
const SLOT = 20; // the least room a label needs
// On a phone a month fills the screen: the bar sits left of the middle, income labels go above
// their nodes and spending labels take two lines, so nothing runs off the edge.
const PHONE_IN = 18, PHONE_OUT = 30;
// Where the month in focus sits across the window.
const FOCUS = (narrow: boolean) => (narrow ? 0.5 : 0.64);
const sum = (xs: { amount: number }[]) => xs.reduce((a, x) => a + x.amount, 0);
const named = (f: Flow) => (f.note ? `${f.name} (${f.note})` : f.name);
// A spending label's second line on phones.
const amountLine = (f: Flow) => (f.note ? `${f.note} · ${eur0(f.amount)}` : eur0(f.amount));
const textW = (s: string) => s.length * 6.9 + 6;

// How far down a band edge has come at a share of its width. Bands are cubic curves with both control
// points halfway across (as in the Sankey), so this inverts x(u) = 1.5u − 1.5u² + u³.
function drop(xf: number) {
  if (xf <= 0) return 0;
  if (xf >= 1) return 1;
  let lo = 0, hi = 1;
  for (let n = 0; n < 22; n++) {
    const u = (lo + hi) / 2;
    if (1.5 * u - 1.5 * u * u + u * u * u < xf) lo = u;
    else hi = u;
  }
  const u = (lo + hi) / 2;
  return 3 * u * u - 2 * u * u * u;
}

const bandD = (x0: number, a0: number, a1: number, x1: number, b0: number, b1: number) => {
  const xm = (x0 + x1) / 2;
  return `M${x0} ${a0}C${xm} ${a0} ${xm} ${b0} ${x1} ${b0}L${x1} ${b1}C${xm} ${b1} ${xm} ${a1} ${x0} ${a1}Z`;
};
const edgeD = (x0: number, a: number, x1: number, b: number) => {
  const xm = (x0 + x1) / 2;
  return `M${x0} ${a}C${xm} ${a} ${xm} ${b} ${x1} ${b}`;
};

// A month's flows as the chart shows them: the biggest income sources and spending groups, the rest
// summed up, and invested / put aside next to spending (or with income when money came back out).
function flowsOf(m: TimelineMonth): { ins: Flow[]; outs: Flow[] } {
  const inc = m.income.filter((i) => i.amount > 0);
  const ins: Flow[] = (inc.length > 3 ? inc.slice(0, 2) : inc).map((i) => ({
    key: `income:${m.month}:${i.name}`,
    name: catName(i.name),
    amount: i.amount,
    color: "var(--good)",
    pick: { kind: "income", id: i.id },
  }));
  if (inc.length > 3) ins.push({ key: `income:${m.month}:*`, name: tr("tl.moreIn"), amount: sum(inc.slice(2)), color: "var(--good)" });
  const outs: Flow[] = [];
  for (const p of m.placed) {
    const f = { name: groupName(p.key, p.amount), amount: Math.abs(p.amount), color: groupColor[p.key], pick: { kind: "saved", focus: p.focus } as TimelinePick };
    if (p.amount < 0) ins.push({ ...f, key: `back:${m.month}:${p.key}` });
    else if (p.amount > 0) outs.push({ ...f, key: `saved:${m.month}:${p.key}` });
  }
  const sp = m.spending.filter((g) => g.amount > 0);
  const many = sp.length > 5;
  for (const g of many ? sp.slice(0, 4) : sp)
    outs.push({ key: `spending:${m.month}:${g.name}`, name: catName(g.name), amount: g.amount, color: colorVar(g.color), pick: { kind: "group", name: g.name } });
  if (many) outs.push({ key: `spending:${m.month}:*`, name: tr("tl.moreOut"), amount: sum(sp.slice(4)), color: "var(--c-muted)" });
  // Money that went the other way: an income category that lost more than it got (paid back, or a
  // booking in the wrong category) leaves with the spending, and refunds larger than a group's
  // spending come in with the income. Left out, the month wouldn't add up and the money would vanish.
  for (const i of m.income)
    if (i.amount < -0.5) outs.push({ key: `out:${m.month}:${i.name}`, name: catName(i.name), note: tr("tl.paidOut"), amount: -i.amount, color: "var(--bad)", pick: { kind: "income", id: i.id } });
  for (const g of m.spending)
    if (g.amount < -0.5) ins.push({ key: `refund:${m.month}:${g.name}`, name: catName(g.name), note: tr("tl.refund"), amount: -g.amount, color: colorVar(g.color), pick: { kind: "group", name: g.name } });
  return { ins, outs };
}

function layout(months: TimelineMonth[], VW: number, narrow: boolean): Layout {
  const flows = months.map(flowsOf);
  // A large balance would squeeze every month into a thin line, so the stream is drawn at most
  // two typical incomes wide; its label keeps the real amount.
  const incomes = months.map((m) => m.income_total).filter((v) => v > 0).sort((a, b) => a - b);
  const typical = incomes.length ? incomes[Math.floor(incomes.length / 2)] : 0;
  const cap = typical > 0 ? typical * 2 : Math.max(1, ...months.map((m) => Math.max(m.carry_in, m.carry_out)));
  const dc = (v: number) => Math.min(Math.max(v, 0), cap);
  const most = Math.max(1, ...months.map((m, i) => Math.max(dc(m.carry_in) + sum(flows[i].ins), dc(m.carry_out) + sum(flows[i].outs))));
  const scale = narrow ? 130 : 150;
  const k = scale / most;
  const colW = narrow ? Math.max(VW, 300) : Math.round(Math.min(560, Math.max(380, VW / 3)));
  // The month in focus sits a little right of the middle, so more of the past is in view and
  // today doesn't leave half the chart empty. Every month can come into focus.
  const pad = Math.max(0, Math.round(FOCUS(narrow) * VW - colW / 2));
  const padR = Math.max(0, Math.round((1 - FOCUS(narrow)) * VW - colW / 2));
  const off = Math.round(colW * 0.3);
  const inSlot = (h: number) => (narrow ? Math.max(h, 4) + PHONE_IN : Math.max(h, SLOT));
  const outSlot = (h: number) => Math.max(h, narrow ? PHONE_OUT : SLOT);
  const stack = (fs: Flow[]) => fs.reduce((a, f) => a + inSlot(Math.max(f.amount * k, 1.5)) + 5, -5);
  const zone = Math.max(0, ...flows.map((f) => (f.ins.length ? stack(f.ins) : 0)));
  const L = HEAD + (zone ? zone + 16 : 8);

  const cols: Col[] = months.map((m, i) => {
    const cin = dc(m.carry_in) * k, cout = dc(m.carry_out) * k;
    const inH = sum(flows[i].ins) * k, outH = sum(flows[i].outs) * k;
    const x = pad + i * colW + Math.round(colW * (narrow ? 0.34 : 0.5) - NW / 2);
    return { m, x, cin, cout, inH, h: Math.max(inH + cin, cout + outH, 2), ins: [], outs: [], bottom: 0 };
  });
  cols.forEach((c, i) => {
    // Income: stacked above the stream, ending just above it.
    let y = L - 16 - stack(flows[i].ins);
    let s = L;
    c.ins = flows[i].ins.map((f) => {
      const h = Math.max(f.amount * k, 1.5), slot = inSlot(h);
      const o = { ...f, x: c.x - (narrow ? Math.round(colW * 0.26) : off), y: narrow ? y + PHONE_IN : y + (slot - h) / 2, h, s, slot: y, sh: slot };
      y += slot + 5;
      s += f.amount * k;
      return o;
    });
    // Spending and savings: below the stream, clear of it on its way down into the next month.
    const next = cols[i + 1];
    const x0 = c.x + NW, a1 = L + c.cout;
    const under = (x: number) => (next ? a1 + next.inH * drop((x - x0) / (next.x - x0)) : a1);
    const xo = c.x + (narrow ? Math.round(colW * 0.2) : off);
    const widest = Math.max(0, ...flows[i].outs.map((f) => (narrow ? Math.max(textW(f.name), textW(amountLine(f))) : textW(`${named(f)} ${eur0(f.amount)}`))));
    const place = (top: number) => {
      let yy = top, ss = a1;
      return flows[i].outs.map((f) => {
        const h = Math.max(f.amount * k, 1.5), slot = outSlot(h);
        const o = { ...f, x: xo, y: yy + (slot - h) / 2, h, s: ss, slot: yy, sh: slot };
        yy += slot + 5;
        ss += f.amount * k;
        return o;
      });
    };
    const top = Math.max(a1 + 10, under(xo + NW + 8 + widest) + 10);
    let outs = place(top);
    let shift = 0;
    for (const o of outs)
      for (let n = 1; n <= 10; n++) {
        const q = n / 10, d = drop(q);
        const short = under(x0 + (o.x - x0) * q) - (o.s + (o.y - o.s) * d);
        if (short > 0) shift = Math.max(shift, short / d);
      }
    if (shift) outs = place(top + shift);
    c.outs = outs;
    const last = outs[outs.length - 1];
    c.bottom = Math.max(L + c.h, last ? last.slot + last.sh : 0);
  });
  const H = Math.round(Math.max(L + 40, ...cols.map((c) => c.bottom)) + 18);
  return { cols, colW, pad, W: pad + padR + months.length * colW, H, L, cap, scale };
}

type Tip = { name: string; amount: number; color: string; sub: string };

export function FlowTimeline({ data, focus, follow, inPeriod, onSettle, onMonth, onPick }: {
  data: Timeline;
  focus: string; // the month to show in the middle (the period's month, or its last month)
  follow: boolean; // settling on another month moves the period along (month periods)
  inPeriod: (month: string) => boolean;
  onSettle: (month: string) => void;
  onMonth: (month: string) => void;
  onPick: (month: string, pick: TimelinePick) => void;
}) {
  useLang();
  const gid = `tl${useId().replace(/[^a-zA-Z0-9]/g, "")}`;
  const narrow = useNarrow();
  const scroller = useRef<HTMLDivElement>(null);
  const view = useRef(0);
  const [VW, setVW] = useState(0);
  useLayoutEffect(() => {
    const el = scroller.current;
    if (!el) return;
    const measure = () => setVW(el.clientWidth);
    measure();
    const ro = new ResizeObserver(measure);
    ro.observe(el);
    return () => ro.disconnect();
  }, []);
  const months = data.months;
  const n = months.length;
  const lay = useMemo(() => (VW ? layout(months, VW, narrow) : null), [months, VW, narrow]);
  const indexOf = (m: string) => {
    const i = months.findIndex((x) => x.month === m);
    return i >= 0 ? i : m < (months[0]?.month ?? "") ? 0 : n - 1;
  };
  const [center, setCenter] = useState(() => indexOf(focus));
  const centerRef = useRef(center);
  // The month this chart last moved the period to, so the period's change doesn't scroll it again.
  const settled = useRef<string | null>(null);
  const settleTimer = useRef(0);
  const dragging = useRef(false);

  const go = (i: number, smooth = true) => {
    const el = scroller.current;
    if (!el || !lay) return;
    const j = Math.max(0, Math.min(n - 1, i));
    el.scrollTo({ left: j * lay.colW, behavior: smooth && !reducedMotion() ? "smooth" : "auto" });
  };

  // Open on the period's month, and stay on the month in the middle when the window is resized.
  useLayoutEffect(() => {
    if (!lay || !scroller.current) return;
    scroller.current.scrollLeft = centerRef.current * lay.colW;
    view.current = scroller.current.scrollLeft;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lay]);
  // A period picked in the header (or by clicking a month) brings its month to the middle.
  useEffect(() => {
    if (settled.current === focus) return;
    settled.current = null;
    go(indexOf(focus));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [focus]);

  const mini = useRef<HTMLDivElement>(null);
  const onScroll = () => {
    const el = scroller.current;
    if (!el || !lay) return;
    view.current = el.scrollLeft;
    const c = Math.max(0, Math.min(n - 1, Math.round(el.scrollLeft / lay.colW)));
    if (c !== centerRef.current) {
      centerRef.current = c;
      setCenter(c);
    }
    moveWindow();
    window.clearTimeout(settleTimer.current);
    settleTimer.current = window.setTimeout(() => {
      if (dragging.current) return;
      const m = months[centerRef.current]?.month;
      if (follow && m && m !== focus) {
        settled.current = m;
        onSettle(m);
      }
    }, 260);
  };
  useEffect(() => () => window.clearTimeout(settleTimer.current), []);

  // Dragging with the mouse moves through the months; a quick flick goes one further.
  const drag = useRef<{ x: number; left: number; moved: boolean; v: number; lx: number; lt: number } | null>(null);
  const suppressClick = useRef(false);
  const onPointerDown = (e: ReactPointerEvent<HTMLDivElement>) => {
    if (e.pointerType !== "mouse" || e.button !== 0 || !scroller.current) return;
    drag.current = { x: e.clientX, left: scroller.current.scrollLeft, moved: false, v: 0, lx: e.clientX, lt: e.timeStamp };
  };
  const onPointerMove = (e: ReactPointerEvent<HTMLDivElement>) => {
    const d = drag.current, el = scroller.current;
    if (!d || !el) return;
    const dx = e.clientX - d.x;
    if (!d.moved && Math.abs(dx) > 5) {
      d.moved = true;
      dragging.current = true;
      el.setPointerCapture(e.pointerId);
      el.classList.add("dragging");
      setHot(null);
    }
    if (!d.moved) return;
    el.scrollLeft = d.left - dx;
    const dt = Math.max(1, e.timeStamp - d.lt);
    d.v = 0.7 * ((e.clientX - d.lx) / dt) + 0.3 * d.v;
    d.lx = e.clientX;
    d.lt = e.timeStamp;
  };
  const endDrag = () => {
    const d = drag.current, el = scroller.current;
    drag.current = null;
    if (!d?.moved || !el || !lay) return;
    suppressClick.current = true;
    window.setTimeout(() => (suppressClick.current = false), 0);
    dragging.current = false;
    el.classList.remove("dragging");
    const at = el.scrollLeft / lay.colW;
    const fling = Math.abs(d.v) > 0.35 ? -Math.sign(d.v) * 0.5 : 0;
    go(Math.round(at + fling));
  };
  const onKey = (e: KeyboardEvent) => {
    const step = { ArrowLeft: -1, ArrowRight: 1, PageUp: -3, PageDown: 3 }[e.key];
    if (step) go(centerRef.current + step);
    else if (e.key === "Home") go(0);
    else if (e.key === "End") go(n - 1);
    else return;
    e.preventDefault();
  };

  // The hover card follows the pointer without re-rendering the chart.
  const [hot, setHot] = useState<string | null>(null);
  const tipEl = useRef<HTMLDivElement>(null);
  const tipData = useRef<Tip | null>(null);
  const tips = useRef(new Map<string, Tip>());
  const wrap = useRef<HTMLDivElement>(null);
  const moveTip = (e: ReactPointerEvent) => {
    const el = tipEl.current, host = wrap.current;
    if (!el || !host) return;
    const r = host.getBoundingClientRect();
    const tw = el.offsetWidth;
    let x = e.clientX - r.left + 16;
    if (x + tw > r.width - 4) x = e.clientX - r.left - tw - 16;
    el.style.transform = `translate(${Math.round(x)}px,${Math.round(e.clientY - r.top + 16)}px)`;
  };

  // The overview strip below: every month, the window on it, and the period.
  const moveWindow = () => {
    const el = mini.current?.querySelector<HTMLElement>(".tl-win");
    if (!el || !lay || !mini.current) return;
    const mw = mini.current.clientWidth;
    const f0 = (view.current - lay.pad) / lay.colW, f1 = (view.current + VW - lay.pad) / lay.colW;
    const a = Math.max(0, f0) / n, b = Math.min(n, f1) / n;
    el.style.transform = `translateX(${(a * mw).toFixed(1)}px)`;
    el.style.width = `${Math.max(10, (b - a) * mw).toFixed(1)}px`;
  };
  useLayoutEffect(moveWindow);
  const scrub = useRef(false);
  const scrubTo = (e: ReactPointerEvent<HTMLDivElement>, settle: boolean) => {
    const host = mini.current, el = scroller.current;
    if (!host || !el || !lay) return;
    const r = host.getBoundingClientRect();
    const fi = Math.max(0, Math.min(n - 1, ((e.clientX - r.left) / r.width) * n - 0.5));
    if (settle) {
      el.classList.remove("dragging");
      dragging.current = false;
      go(Math.round(fi), false);
    } else {
      el.classList.add("dragging");
      dragging.current = true;
      el.scrollLeft = fi * lay.colW;
    }
  };

  if (!n) return null;
  const reach = Math.ceil((VW || 1200) / (lay?.colW ?? 400)) + 1;
  const lo = Math.max(0, center - reach);
  const hi = Math.min(n - 1, center + reach);
  const defs: ReactNode[] = [];
  // Gradient ids are numbered: band keys hold category names, which may contain spaces.
  const grad = (x0: number, x1: number, from: string, to: string, o0 = 0.5, o1 = 1) => {
    const id = `${gid}-${defs.length}`;
    defs.push(
      <linearGradient key={id} id={id} gradientUnits="userSpaceOnUse" x1={x0} y1={0} x2={x1} y2={0}>
        <stop offset="0" style={{ stopColor: from, stopOpacity: o0 }} />
        <stop offset="1" style={{ stopColor: to, stopOpacity: o1 }} />
      </linearGradient>,
    );
    return `url(#${id})`;
  };
  const tipFor = (key: string, tip: Tip) => {
    tips.current.set(key, tip);
    return {
      onPointerEnter: () => {
        if (!dragging.current) setHot(key);
      },
    };
  };
  const clickFor = (month: string, f: Flow) =>
    f.pick
      ? {
          "data-pick": "",
          role: "button",
          tabIndex: -1,
          "aria-label": named(f),
          onClick: () => !suppressClick.current && onPick(month, f.pick!),
        }
      : {};
  const band = (key: string, d: string, edges: [string, string], fill: string, opacity: number, delay: number, extra = {}) => {
    const on = hot === key ? " hot" : "";
    const st = { ["--d" as string]: `${delay}ms` };
    return (
      <g key={key}>
        <path className={`band${on}`} style={st} d={d} fill={fill} fillOpacity={opacity} {...extra} />
        <path className={`edge${on}`} style={st} pathLength={1} d={edges[0]} stroke={fill} />
        <path className={`edge${on}`} style={st} pathLength={1} d={edges[1]} stroke={fill} />
      </g>
    );
  };

  const body: ReactNode[] = [];
  const labels: ReactNode[] = [];
  const account = data.account ?? tr("tl.accounts");
  if (lay) {
    const { cols, L, colW, cap } = lay;
    // The period: a soft band behind its months.
    const inside = cols.map((c, i) => (inPeriod(c.m.month) ? i : -1)).filter((i) => i >= 0);
    if (inside.length) {
      const a = cols[inside[0]], b = cols[inside[inside.length - 1]];
      body.push(<rect key="period" className="tl-period" x={a.x + NW / 2 - colW / 2 + 4} y={4} width={b.x - a.x + colW - 8} height={lay.H - 8} rx={16} />);
    }
    for (let i = lo; i <= hi; i++) {
      const c = cols[i], m = c.m, mk = m.month, on = i === center;
      const prev = cols[i - 1], next = cols[i + 1];
      // What came over from the month before: from its bar, or faded in before the first month.
      if (!prev || i === lo) {
        const x0 = prev ? prev.x + NW : Math.max(2, c.x - Math.round(colW * 0.48));
        const key = prev ? `carry:${prev.m.month}` : "start";
        const fill = grad(x0, c.x, "var(--good)", "var(--good)", prev ? 0.5 : 0, 1);
        const a0 = prev ? L : L + c.inH, a1 = prev ? L + prev.cout : L + c.inH + c.cin;
        if (c.cin > 0.5) body.push(band(key, bandD(x0, a0, a1, c.x, L + c.inH, L + c.inH + c.cin), [edgeD(x0, a0, c.x, L + c.inH), edgeD(x0, a1, c.x, L + c.inH + c.cin)], fill, 0.34, 0, tipFor(key, prev ? { name: tr("tl.carry", { month: monthLong(mk) }), amount: m.carry_in, color: "var(--good)", sub: account } : { name: tr("tl.start"), amount: m.carry_in, color: "var(--good)", sub: monthLong(mk) })));
        if (!prev) labels.push(pill("start", (x0 + c.x) / 2 - 10, L + c.inH + c.cin / 2, m.carry_in, m.carry_in > cap, tr("tl.startShort")));
      }
      if (next) {
        const key = `carry:${mk}`;
        const fill = grad(c.x + NW, next.x, "var(--good)", "var(--good)", 0.5, 1);
        if (c.cout > 0.5) body.push(band(key, bandD(c.x + NW, L, L + c.cout, next.x, L + next.inH, L + next.inH + next.cin), [edgeD(c.x + NW, L, next.x, L + next.inH), edgeD(c.x + NW, L + c.cout, next.x, L + next.inH + next.cin)], fill, 0.34, 200, tipFor(key, { name: tr("tl.carry", { month: monthLong(next.m.month) }), amount: m.carry_out, color: "var(--good)", sub: account })));
        else body.push(<path key={key} className="tl-dry" d={edgeD(c.x + NW, L, next.x, L + next.inH)} />);
        const mx = (c.x + NW + next.x) / 2;
        labels.push(pill(key, mx, L + next.inH / 2 + c.cout / 2, m.carry_out, m.carry_out > cap));
      } else {
        // Today: the stream runs on a little and ends.
        const x1 = c.x + NW + Math.round(colW * 0.48);
        const key = "today";
        const fill = grad(c.x + NW, x1, "var(--good)", "var(--good)", 0.9, 0);
        if (c.cout > 0.5) body.push(band(key, `M${c.x + NW} ${L}H${x1}V${L + c.cout}H${c.x + NW}Z`, [`M${c.x + NW} ${L}H${x1}`, `M${c.x + NW} ${L + c.cout}H${x1}`], fill, 0.34, 200, tipFor(key, { name: tr("tl.now"), amount: m.carry_out, color: "var(--good)", sub: data.ahead > 0.005 ? tr("tl.ahead", { amount: eur(data.ahead) }) : account })));
        labels.push(pill(key, c.x + NW + Math.round(colW * 0.3), L + c.cout / 2, m.carry_out, m.carry_out > cap, tr("tl.today")));
      }
      // Everything that passed through the month: what it started with and took in, or what it
      // sent on and paid out, whichever is more.
      const through = Math.max(1, Math.max(0, m.carry_in) + sum(c.ins), Math.max(0, m.carry_out) + sum(c.outs));
      c.ins.forEach((f, j) => {
        const fill = grad(f.x + NW, c.x, f.color, "var(--good)");
        const tip = tipFor(f.key, { name: named(f), amount: f.amount, color: f.color, sub: monthLong(mk) });
        body.push(band(f.key, bandD(f.x + NW, f.y, f.y + f.h, c.x, f.s, f.s + f.h), [edgeD(f.x + NW, f.y, c.x, f.s), edgeD(f.x + NW, f.y + f.h, c.x, f.s + f.h)], fill, 0.22, 80 + j * 90, { ...tip, ...clickFor(mk, f) }));
        labels.push(
          <g key={`n-${f.key}`} className={`nd tl-nd${on ? " on" : ""}${hot === f.key ? " hot" : ""}`} {...tip} {...clickFor(mk, f)}>
            <rect className="node" x={f.x} y={f.y} width={NW} height={f.h} rx={2} fill={f.color} />
            {narrow ? (
              <text x={f.x} y={f.slot + 12}>
                <tspan className="tl-name">{named(f)}</tspan>
                <tspan className="tl-amt" dx={6}>{eur0(f.amount)}</tspan>
              </text>
            ) : (
              <text x={f.x - 8} y={f.slot + f.sh / 2 + 4.5} textAnchor="end">
                <tspan className="tl-name">{named(f)}</tspan>
                <tspan className="tl-amt" dx={6}>{eur0(f.amount)}</tspan>
              </text>
            )}
          </g>,
        );
      });
      c.outs.forEach((f, j) => {
        const fill = grad(c.x + NW, f.x, "var(--good)", f.color);
        const tip = tipFor(f.key, { name: named(f), amount: f.amount, color: f.color, sub: `${monthLong(mk)} · ${tr("tl.share", { p: Math.round((f.amount / through) * 100) })}` });
        body.push(band(f.key, bandD(c.x + NW, f.s, f.s + f.h, f.x, f.y, f.y + f.h), [edgeD(c.x + NW, f.s, f.x, f.y), edgeD(c.x + NW, f.s + f.h, f.x, f.y + f.h)], fill, 0.28, 380 + j * 55, { ...tip, ...clickFor(mk, f) }));
        labels.push(
          <g key={`n-${f.key}`} className={`nd tl-nd${on ? " on" : ""}${hot === f.key ? " hot" : ""}`} {...tip} {...clickFor(mk, f)}>
            <rect className="node" x={f.x} y={f.y} width={NW} height={f.h} rx={2} fill={f.color} />
            {narrow ? (
              <text x={f.x + NW + 8} y={f.slot + f.sh / 2 - 2}>
                <tspan className="tl-name">{f.name}</tspan>
                <tspan className="tl-amt" x={f.x + NW + 8} dy={14}>{amountLine(f)}</tspan>
              </text>
            ) : (
              <text x={f.x + NW + 8} y={f.slot + f.sh / 2 + 4.5}>
                <tspan className="tl-name">{named(f)}</tspan>
                <tspan className="tl-amt" dx={6}>{eur0(f.amount)}</tspan>
              </text>
            )}
          </g>,
        );
      });
      const current = i === n - 1;
      labels.push(
        <g key={`m-${mk}`} className={`tl-col${on ? " on" : ""}${inPeriod(mk) ? " in" : ""}`}>
          <rect className="node tl-bar" x={c.x} y={L} width={NW} height={c.h} rx={3} onClick={() => !suppressClick.current && onMonth(mk)} />
          <g className="tl-head" role="button" tabIndex={-1} aria-label={tr("tl.pick", { month: monthLong(mk) })} onClick={() => !suppressClick.current && onMonth(mk)}>
            <rect x={c.x + NW / 2 - 70} y={6} width={140} height={current ? 38 : 28} rx={9} />
            <text className="tl-month" x={c.x + NW / 2} y={25} textAnchor="middle">{monthLong(mk)}</text>
            {current && <text className="tl-sofar" x={c.x + NW / 2} y={39} textAnchor="middle">{tr("tl.sofar")}</text>}
          </g>
        </g>,
      );
    }
  }

  function pill(key: string, x: number, y: number, amount: number, capped: boolean, caption?: string) {
    const text = eur0(amount);
    const w = textW(text) + 12;
    return (
      <g key={`p-${key}`} className={`tl-pill${amount < 0 ? " neg" : ""}`} pointerEvents="none">
        {capped && <path className="tl-cut" d={`M${x - w / 2 - 12} ${y + 9}l6 -18M${x - w / 2 - 6} ${y + 9}l6 -18`} />}
        {caption && <text className="tl-cap" x={x} y={y - 17} textAnchor="middle">{caption}</text>}
        <rect x={x - w / 2} y={y - 10.5} width={w} height={21} rx={10.5} />
        <text x={x} y={y + 4.5} textAnchor="middle">{text}</text>
      </g>
    );
  }

  const shownTip = hot ? tips.current.get(hot) ?? null : null;
  if (shownTip) tipData.current = shownTip;
  const tf = tipData.current;

  return (
    <div className="tl" ref={wrap}>
      <div className="tl-view">
        <div
          className="tl-scroll"
          ref={scroller}
          tabIndex={0}
          role="region"
          aria-label={tr("tl.aria")}
          onScroll={onScroll}
          onKeyDown={onKey}
          onPointerDown={onPointerDown}
          onPointerMove={(e) => {
            onPointerMove(e);
            moveTip(e);
          }}
          onPointerUp={endDrag}
          onPointerCancel={endDrag}
          onPointerLeave={() => setHot(null)}
          onClickCapture={(e) => {
            if (suppressClick.current) {
              e.stopPropagation();
              e.preventDefault();
            }
          }}
        >
          {lay && (
            <div className="tl-track" style={{ width: lay.W, height: lay.H }}>
              {months.map((m, i) => (
                <i key={m.month} className="tl-snap" style={{ left: i * lay.colW }} />
              ))}
              <svg className={`chart sankey tl-chart${hot ? " has-hot" : ""}`} width={lay.W} height={lay.H} viewBox={`0 0 ${lay.W} ${lay.H}`} role="img" aria-label={tr("tl.aria")}>
                <defs>{defs}</defs>
                {body}
                {labels}
              </svg>
            </div>
          )}
        </div>
        <button type="button" className="tl-nav prev" aria-label={tr("tl.prev")} disabled={center <= 0} onClick={() => go(center - 1)}>‹</button>
        <button type="button" className="tl-nav next" aria-label={tr("tl.next")} disabled={center >= n - 1} onClick={() => go(center + 1)}>›</button>
        <div ref={tipEl} className={`flowtip${shownTip ? " on" : ""}`} aria-hidden="true">
          {tf && (
            <>
              <span className="sw" style={{ background: tf.color }} />
              <b>{tf.name}</b>
              <span className="amt">{eur(tf.amount)}</span>
              <small>{tf.sub}</small>
            </>
          )}
        </div>
      </div>
      {n > 2 && (
        <MiniMap
          months={months}
          inPeriod={inPeriod}
          refEl={mini}
          onDown={(e) => {
            scrub.current = true;
            e.currentTarget.setPointerCapture(e.pointerId);
            scrubTo(e, false);
          }}
          onMove={(e) => scrub.current && scrubTo(e, false)}
          onUp={(e) => {
            if (!scrub.current) return;
            scrub.current = false;
            scrubTo(e, true);
          }}
        />
      )}
    </div>
  );
}

// Every month in a slim strip: the balance carried from month to month, the years, the period,
// and the part shown above. Click or drag on it to travel.
function MiniMap({ months, inPeriod, refEl, onDown, onMove, onUp }: {
  months: TimelineMonth[];
  inPeriod: (m: string) => boolean;
  refEl: RefObject<HTMLDivElement | null>;
  onDown: (e: ReactPointerEvent<HTMLDivElement>) => void;
  onMove: (e: ReactPointerEvent<HTMLDivElement>) => void;
  onUp: (e: ReactPointerEvent<HTMLDivElement>) => void;
}) {
  const n = months.length;
  const vals = months.map((m) => m.carry_out);
  const lo = Math.min(0, ...vals), hi = Math.max(1, ...vals);
  const W = 1000, H = 30;
  const y = (v: number) => H - 3 - ((v - lo) / (hi - lo)) * (H - 8);
  const x = (i: number) => ((i + 0.5) / n) * W;
  const line = vals.map((v, i) => `${i ? "L" : "M"}${x(i).toFixed(1)} ${y(v).toFixed(1)}`).join("");
  const area = `${line}L${x(n - 1).toFixed(1)} ${H}L${x(0).toFixed(1)} ${H}Z`;
  const inside = months.map((m, i) => (inPeriod(m.month) ? i : -1)).filter((i) => i >= 0);
  const years = months.map((m, i) => ({ m, i })).filter(({ m, i }) => m.month.endsWith("-01") || i === 0);
  return (
    <div className="tl-mini" ref={refEl} role="slider" aria-label={tr("tl.mini")} aria-valuemin={0} aria-valuemax={n - 1} onPointerDown={onDown} onPointerMove={onMove} onPointerUp={onUp} onPointerCancel={onUp}>
      <svg viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none" aria-hidden="true">
        {inside.length > 0 && <rect className="tl-mini-period" x={(inside[0] / n) * W} y={0} width={((inside[inside.length - 1] - inside[0] + 1) / n) * W} height={H} />}
        <path className="tl-mini-area" d={area} />
        <path className="tl-mini-line" d={line} vectorEffect="non-scaling-stroke" />
        {lo < 0 && <path className="tl-mini-zero" d={`M0 ${y(0)}H${W}`} vectorEffect="non-scaling-stroke" />}
      </svg>
      <div className="tl-years" aria-hidden="true">
        {years.map(({ m, i }) => (
          <span key={m.month} style={{ left: `${(i / n) * 100}%` }}>{m.month.slice(0, 4)}</span>
        ))}
      </div>
      <div className="tl-win" />
    </div>
  );
}
