// Zoom for charts over time. Drag across a chart to look closer at that stretch; Ctrl + mouse wheel
// (or pinching a trackpad) zooms around the pointer, two fingers do the same on a phone; a sideways
// wheel or the strip under the chart moves along; a double-click, a double tap or the button shows the
// whole period again. Each chart remembers its view in this browser, for as long as the period it
// shows stays the same.

import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState, type KeyboardEvent, type PointerEvent as ReactPointerEvent } from "react";
import { useT } from "../i18n";
import { Icon } from "./Icons";
import { reducedMotion } from "./Motion";

const STORE = "groschen.zoom";
type Saved = { scope: string; from: string; to: string };

function readAll(): Record<string, Saved> {
  try {
    const v = JSON.parse(localStorage.getItem(STORE) ?? "{}");
    return v && typeof v === "object" && !Array.isArray(v) ? v : {};
  } catch {
    return {};
  }
}
function write(id: string, v: Saved | null) {
  try {
    const all = readAll();
    if (v) all[id] = v;
    else delete all[id];
    localStorage.setItem(STORE, JSON.stringify(all));
  } catch {
    /* private window or blocked storage: the view lasts until the page is left */
  }
}

// The first index whose value is at least v, in an ascending list.
function lower<T>(list: T[], v: T) {
  let lo = 0, hi = list.length;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (list[mid] < v) lo = mid + 1;
    else hi = mid;
  }
  return lo;
}

export type Zoom = {
  // Where the view is right now, along the chart's x positions (they glide from one view to the next).
  a: number;
  b: number;
  // Where it is headed, as the first and last point inside: what the figures beside the chart describe.
  to: [number, number];
  n: number;
  max: number; // the last point's position
  minSpan: number;
  zoomed: boolean;
  // The point nearest to a position.
  near: (x: number) => number;
  // The first and last point between two positions.
  inside: (a: number, b: number) => [number, number];
  pos: (i: number) => number;
  set: (a: number, b: number, instant?: boolean) => void;
  commit: () => void;
  reset: () => void;
};

// dates: the chart's points in order (ISO days or months). positions: where each sits along the x
// axis, ascending from 0 (a day count for a chart drawn to time); the points' numbers by default.
// scope: what the chart is showing, such as the period; a view saved under another scope is not used.
// minSpan: the closest it zooms in, in positions.
export function useZoom(id: string, scope: string, dates: string[], positions?: number[], minSpan = 4): Zoom {
  const n = dates.length;
  const P = useMemo(() => positions ?? dates.map((_, i) => i), [positions, dates]);
  const max = n ? P[n - 1] : 0;
  const least = Math.min(minSpan, max);
  const near = useCallback(
    (x: number) => {
      const i = Math.min(lower(P, x), n - 1);
      return i > 0 && x - P[i - 1] < P[i] - x ? i - 1 : Math.max(i, 0);
    },
    [P, n],
  );
  const restore = useCallback((): [number, number] => {
    const s = readAll()[id];
    if (!s || s.scope !== scope || n < 3 || typeof s.from !== "string" || typeof s.to !== "string") return [0, max];
    const i0 = lower(dates, s.from), i1 = lower(dates, s.to + "\uffff") - 1;
    return i0 < n && i1 > i0 && P[i1] - P[i0] >= least ? [P[i0], P[i1]] : [0, max];
  }, [id, scope, dates, P, n, max, least]);

  const [view, setView] = useState<[number, number]>(restore);
  const now = useRef(view);
  const goal = useRef(view);
  const frame = useRef(0);
  const show = (v: [number, number]) => {
    now.current = v;
    setView(v);
  };

  // Another period (or new data): straight to its own view, no gliding across.
  const domain = `${scope}|${n}|${dates[0]}|${dates[n - 1]}|${max}`;
  useLayoutEffect(() => {
    cancelAnimationFrame(frame.current);
    goal.current = restore();
    show(goal.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [domain]);
  useEffect(() => () => cancelAnimationFrame(frame.current), []);

  const clamp = useCallback(
    (a: number, b: number): [number, number] => {
      let span = Math.min(Math.max(b - a, least), max);
      if (!isFinite(span)) span = max;
      const start = Math.min(Math.max(a, 0), max - span);
      return [start, start + span];
    },
    [least, max],
  );

  const set = useCallback(
    (a: number, b: number, instant = false) => {
      const g = clamp(a, b);
      goal.current = g;
      cancelAnimationFrame(frame.current);
      if (instant || reducedMotion()) return show(g);
      const from = now.current, t0 = performance.now();
      const tick = (t: number) => {
        const k = Math.min((t - t0) / 420, 1), e = 1 - Math.pow(1 - k, 3);
        show([from[0] + (g[0] - from[0]) * e, from[1] + (g[1] - from[1]) * e]);
        if (k < 1) frame.current = requestAnimationFrame(tick);
      };
      frame.current = requestAnimationFrame(tick);
    },
    [clamp],
  );

  // The first and last point between two positions.
  const inside = useCallback(
    (a: number, b: number): [number, number] => {
      const i0 = Math.max(Math.min(lower(P, a - 1e-6), n - 1), 0);
      return [i0, Math.max(lower(P, b + 1e-6) - 1, i0)];
    },
    [P, n],
  );
  const span = (): [number, number] => inside(goal.current[0], goal.current[1]);
  const to = n ? span() : ([0, 0] as [number, number]);
  const zoomed = n > 1 && (to[0] > 0 || to[1] < n - 1);

  const commit = useCallback(() => {
    const [i0, i1] = span();
    write(id, i0 <= 0 && i1 >= n - 1 ? null : { scope, from: dates[i0], to: dates[i1] });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, scope, dates, n, P]);

  const reset = useCallback(() => {
    set(0, max);
    write(id, null);
  }, [id, max, set]);

  const pos = useCallback((i: number) => P[Math.min(Math.max(i, 0), n - 1)] ?? 0, [P, n]);
  return { a: view[0], b: view[1], to, n, max, minSpan: least, zoomed, near, inside, pos, set, commit, reset };
}

// The pointer, wheel and keys that drive a zoom on a chart drawn in a viewBox W wide, whose plot
// runs from x = l over iw. onHover gets the position under the pointer (null when it leaves);
// onTap a click that didn't drag, with the height it was at in the viewBox.
export function useZoomGestures(zoom: Zoom, plot: { l: number; iw: number; W: number; H: number }, onHover: (x: number | null) => void, onTap?: (x: number, y: number) => void) {
  const ref = useRef<SVGSVGElement>(null);
  const live = useRef({ zoom, plot, onHover, onTap });
  live.current = { zoom, plot, onHover, onTap };
  const [sel, setSel] = useState<[number, number] | null>(null);
  const g = useRef<{
    pointers: Map<number, { x: number; y: number }>;
    start: { x: number; at: number } | null;
    selecting: boolean;
    pinch: { dist: number; view: [number, number]; at: number } | null;
    lastTap: { t: number; x: number };
    commitTimer: number;
  }>({ pointers: new Map(), start: null, selecting: false, pinch: null, lastTap: { t: 0, x: 0 }, commitTimer: 0 });

  // Screen coordinates to the viewBox, and from there to a position along the x axis.
  const local = (clientX: number, clientY = 0) => {
    const el = ref.current;
    const { plot: p } = live.current;
    if (!el) return { x: 0, y: 0 };
    const r = el.getBoundingClientRect();
    return { x: ((clientX - r.left) / (r.width || 1)) * p.W, y: ((clientY - r.top) / (r.height || 1)) * p.H };
  };
  const posAt = (clientX: number) => {
    const { zoom: z, plot: p } = live.current;
    return z.a + ((local(clientX).x - p.l) / p.iw) * (z.b - z.a);
  };
  const inside = (clientX: number) => {
    const { plot: p } = live.current;
    const x = local(clientX).x;
    return x >= p.l - 6 && x <= p.l + p.iw + 6;
  };
  const clampX = (x: number) => Math.min(Math.max(x, 0), live.current.zoom.max);
  const later = () => {
    window.clearTimeout(g.current.commitTimer);
    g.current.commitTimer = window.setTimeout(() => live.current.zoom.commit(), 350);
  };
  // Zoom by a factor around a position, which stays where it is on screen.
  const scaleAround = (center: number, factor: number, instant: boolean) => {
    const { zoom: z } = live.current;
    const [a, b] = instant ? [z.a, z.b] : [z.pos(z.to[0]), z.pos(z.to[1])];
    const next = Math.max((b - a) * factor, z.minSpan);
    const k = (center - a) / (b - a || 1);
    z.set(center - k * next, center - k * next + next, instant);
  };

  // The wheel needs a listener that may cancel scrolling (React's is passive). A plain wheel keeps
  // scrolling the page.
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const wheel = (e: WheelEvent) => {
      const { zoom: z, plot: p } = live.current;
      if (z.n < 3) return;
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault();
        const unit = e.deltaMode === 1 ? 0.05 : e.deltaMode === 2 ? 1 : 0.0025;
        scaleAround(clampX(posAt(e.clientX)), Math.exp(Math.max(Math.min(e.deltaY * unit, 0.6), -0.6)), true);
        later();
        return;
      }
      const sideways = Math.abs(e.deltaX) > Math.abs(e.deltaY) ? e.deltaX : e.shiftKey ? e.deltaY : 0;
      if (!sideways || !z.zoomed) return;
      e.preventDefault();
      const r = el.getBoundingClientRect();
      const perPx = (z.b - z.a) / ((p.iw / p.W) * r.width || 1);
      z.set(z.a + sideways * perPx, z.b + sideways * perPx, true);
      later();
    };
    el.addEventListener("wheel", wheel, { passive: false });
    return () => el.removeEventListener("wheel", wheel);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  useEffect(() => () => window.clearTimeout(g.current.commitTimer), []);

  const twoFingers = () => {
    const [p, q] = [...g.current.pointers.values()];
    return { dist: Math.hypot(p.x - q.x, p.y - q.y), mid: (p.x + q.x) / 2 };
  };

  const onPointerDown = (e: ReactPointerEvent<SVGSVGElement>) => {
    const s = g.current;
    s.pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (s.pointers.size === 2) {
      const { zoom: z } = live.current;
      const f = twoFingers();
      s.pinch = { dist: f.dist, view: [z.a, z.b], at: posAt(f.mid) };
      s.start = null;
      s.selecting = false;
      setSel(null);
      live.current.onHover(null);
      return;
    }
    if (!inside(e.clientX)) return;
    if (e.pointerType === "mouse") {
      if (e.button !== 0) return;
      s.start = { x: e.clientX, at: clampX(posAt(e.clientX)) };
      e.currentTarget.setPointerCapture?.(e.pointerId);
    } else live.current.onHover(clampX(posAt(e.clientX)));
  };

  const onPointerMove = (e: ReactPointerEvent<SVGSVGElement>) => {
    const s = g.current;
    if (s.pointers.has(e.pointerId)) s.pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (s.pinch) {
      if (s.pointers.size < 2) return;
      const { zoom: z, plot: p } = live.current;
      const { dist, mid } = twoFingers();
      const [a0, b0] = s.pinch.view;
      const span = Math.max(((b0 - a0) * s.pinch.dist) / Math.max(dist, 1), z.minSpan);
      const k = (local(mid).x - p.l) / p.iw;
      z.set(s.pinch.at - k * span, s.pinch.at - k * span + span, true);
      return;
    }
    if (s.start) {
      if (!s.selecting && Math.abs(e.clientX - s.start.x) > 4) s.selecting = true;
      if (s.selecting) {
        setSel([s.start.at, clampX(posAt(e.clientX))]);
        live.current.onHover(null);
        return;
      }
    }
    if (e.pointerType !== "mouse" && !s.pointers.has(e.pointerId)) return;
    live.current.onHover(inside(e.clientX) ? clampX(posAt(e.clientX)) : null);
  };

  const end = (e: ReactPointerEvent<SVGSVGElement>) => {
    const s = g.current;
    s.pointers.delete(e.pointerId);
    if (s.pinch) {
      if (!s.pointers.size) {
        s.pinch = null;
        live.current.zoom.commit();
      }
      return;
    }
    const { zoom: z } = live.current;
    if (s.start && s.selecting && e.type === "pointerup") {
      const x = clampX(posAt(e.clientX));
      const a = Math.min(s.start.at, x), b = Math.max(s.start.at, x);
      if (b - a >= z.minSpan * 0.75) {
        z.set(a, b);
        z.commit();
      }
    } else if (s.start && e.type === "pointerup") {
      const { y } = local(e.clientX, e.clientY);
      live.current.onTap?.(clampX(posAt(e.clientX)), y);
    }
    s.start = null;
    s.selecting = false;
    setSel(null);
    // Two taps in a row on a touch screen: the whole period again.
    if (e.type === "pointerup" && e.pointerType !== "mouse") {
      const t = performance.now();
      if (t - s.lastTap.t < 320 && Math.abs(e.clientX - s.lastTap.x) < 30) {
        if (z.zoomed) z.reset();
        s.lastTap = { t: 0, x: 0 };
      } else s.lastTap = { t, x: e.clientX };
    }
  };

  const onKeyDown = (e: KeyboardEvent<SVGSVGElement>) => {
    const { zoom: z } = live.current;
    const a = z.pos(z.to[0]), b = z.pos(z.to[1]);
    if (e.key === "+" || e.key === "=") scaleAround((a + b) / 2, 1 / 1.6, false);
    else if ((e.key === "-" || e.key === "_") && z.zoomed) scaleAround((a + b) / 2, 1.6, false);
    else if ((e.key === "ArrowLeft" || e.key === "ArrowRight") && z.zoomed) {
      const step = (b - a) * 0.25 * (e.key === "ArrowLeft" ? -1 : 1);
      z.set(a + step, b + step);
    } else if ((e.key === "Escape" || e.key === "0") && z.zoomed) z.reset();
    else return;
    e.preventDefault();
    later();
  };

  return {
    ref,
    sel,
    props: {
      onPointerDown,
      onPointerMove,
      onPointerUp: end,
      onPointerCancel: end,
      onPointerLeave: (e: ReactPointerEvent<SVGSVGElement>) => {
        // A finger lifted leaves its point showing; the mouse takes it along.
        if (e.pointerType === "mouse" && !g.current.start) live.current.onHover(null);
      },
      onDoubleClick: () => live.current.zoom.zoomed && live.current.zoom.reset(),
      onKeyDown,
      tabIndex: 0,
    },
  };
}

// The whole period as a thin line under a zoomed chart, with the part in view as a window that can
// be dragged along (or by its edges to show more or less); a click beside it moves it there.
export function ZoomStrip({ zoom, values, label }: { zoom: Zoom; values: number[]; label: string }) {
  const ref = useRef<SVGSVGElement>(null);
  const drag = useRef<{ mode: "move" | "a" | "b"; x: number; view: [number, number] } | null>(null);
  const W = 1000, H = 28;
  const { max, pos } = zoom;
  const line = useMemo(() => {
    const n = values.length;
    const step = Math.max(1, Math.floor(n / 300));
    const idx: number[] = [];
    for (let i = 0; i < n; i += step) idx.push(i);
    if (idx[idx.length - 1] !== n - 1) idx.push(n - 1);
    const lo = Math.min(...values), hi = Math.max(...values);
    const X = (i: number) => (pos(i) / (max || 1)) * W;
    const Y = (v: number) => 3 + (1 - (v - lo) / (hi - lo || 1)) * (H - 6);
    const d = idx.map((i, k) => `${k ? "L" : "M"}${X(i).toFixed(1)} ${Y(values[i]).toFixed(1)}`).join("");
    return { d, area: `${d}L${W} ${H}L0 ${H}Z` };
  }, [values, max, pos]);
  const X = (x: number) => (x / (max || 1)) * W;
  const x0 = X(zoom.a), x1 = X(zoom.b);
  const perPx = () => max / (ref.current?.getBoundingClientRect().width || 1);
  const down = (e: ReactPointerEvent<SVGSVGElement>) => {
    const r = ref.current!.getBoundingClientRect();
    const px = e.clientX - r.left, a = (x0 / W) * r.width, b = (x1 / W) * r.width;
    const mode = Math.abs(px - a) < 10 ? "a" : Math.abs(px - b) < 10 ? "b" : px > a && px < b ? "move" : null;
    if (!mode) {
      const span = zoom.b - zoom.a, c = (px / r.width) * max;
      zoom.set(c - span / 2, c + span / 2);
      zoom.commit();
      return;
    }
    drag.current = { mode, x: e.clientX, view: [zoom.a, zoom.b] };
    e.currentTarget.setPointerCapture?.(e.pointerId);
  };
  const move = (e: ReactPointerEvent<SVGSVGElement>) => {
    const d = drag.current;
    if (!d) return;
    const dx = (e.clientX - d.x) * perPx();
    const [a, b] = d.view;
    if (d.mode === "move") zoom.set(a + dx, b + dx, true);
    else if (d.mode === "a") zoom.set(Math.min(a + dx, b - zoom.minSpan), b, true);
    else zoom.set(a, Math.max(b + dx, a + zoom.minSpan), true);
  };
  const up = () => {
    if (!drag.current) return;
    drag.current = null;
    zoom.commit();
  };
  return (
    <svg
      ref={ref}
      className="zstrip"
      viewBox={`0 0 ${W} ${H}`}
      preserveAspectRatio="none"
      role="img"
      aria-label={label}
      onPointerDown={down}
      onPointerMove={move}
      onPointerUp={up}
      onPointerCancel={up}
    >
      <path d={line.area} className="zs-area" />
      <path d={line.d} className="zs-line" vectorEffect="non-scaling-stroke" />
      <rect x={0} y={0} width={Math.max(x0, 0)} height={H} className="zs-dim" />
      <rect x={x1} y={0} width={Math.max(W - x1, 0)} height={H} className="zs-dim" />
      <rect x={x0} y={0.5} width={Math.max(x1 - x0, 1)} height={H - 1} rx={3} className="zs-win" vectorEffect="non-scaling-stroke" />
    </svg>
  );
}

// Beside a chart's legend: how to zoom while it shows everything, the way back once it doesn't.
export function ZoomNote({ zoom }: { zoom: Zoom }) {
  const t = useT();
  const [touch] = useState(() => typeof matchMedia !== "undefined" && matchMedia("(pointer: coarse)").matches);
  if (zoom.n < 3 || zoom.max <= zoom.minSpan) return null;
  return zoom.zoomed ? (
    <button type="button" className="chip zoom-back" onClick={zoom.reset}>
      <Icon name="zoomOut" size={14} />
      {t("zoom.back")}
    </button>
  ) : (
    <span className="zoom-hint">
      <Icon name="zoomIn" size={14} />
      {t(touch ? "zoom.hintTouch" : "zoom.hint")}
    </span>
  );
}
