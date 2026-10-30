// Small motion helpers. Everything here stays still when the system asks for reduced motion.

import { useEffect, useRef, useState } from "react";
import { eur, pct } from "../lib/format";
import { plain, useHidden } from "../lib/privacy";

// "Animations" in Settings: full, calm (no ambient motion, no particles) or off. Off also follows the system setting.
export type MotionPref = "full" | "calm" | "off";
const MOTION_KEY = "groschen.motion";
export function motionPref(): MotionPref {
  try {
    const v = localStorage.getItem(MOTION_KEY);
    if (v === "calm" || v === "off") return v;
  } catch {
    /* storage blocked */
  }
  return "full";
}
export function setMotionPref(v: MotionPref) {
  try {
    if (v === "full") localStorage.removeItem(MOTION_KEY);
    else localStorage.setItem(MOTION_KEY, v);
  } catch {
    /* ignore */
  }
  applyMotionPref();
}
export function applyMotionPref() {
  if (typeof document === "undefined") return;
  const v = motionPref();
  if (v === "full") delete document.documentElement.dataset.motion;
  else document.documentElement.dataset.motion = v;
}

export const reducedMotion = () =>
  motionPref() === "off" || (typeof matchMedia !== "undefined" && matchMedia("(prefers-reduced-motion: reduce)").matches);

// How much ambient motion this device gets: 0 = none, 1 = light (fewer particles, no ambient drift), 2 = everything.
// Weak devices, data saver and the "calm" setting step down on their own.
export function motionTier(): 0 | 1 | 2 {
  if (reducedMotion()) return 0;
  const nav = navigator as Navigator & { deviceMemory?: number; connection?: { saveData?: boolean } };
  if (nav.connection?.saveData) return 0;
  if (motionPref() === "calm") return 1;
  const cores = nav.hardwareConcurrency ?? 4;
  const mem = nav.deviceMemory ?? 4;
  return cores <= 2 || mem <= 2 ? 1 : 2;
}

// A canvas that draws itself every frame while it is on screen and the tab is visible.
// It sizes itself to its box at the device's pixel ratio, and watches its own frame times:
// when frames take too long, `budget` drops so the drawing can do less work.
// `still` frames are drawn once, without motion: reduced motion, off screen, or a background tab.
export type Frame = { ctx: CanvasRenderingContext2D; w: number; h: number; t: number; dt: number; budget: number; still: boolean };
// A drawing that returns false is finished and stops asking for frames until its deps change.
export function useCanvasLoop(draw: (f: Frame) => boolean | void, deps: unknown[] = [], animate = true) {
  const ref = useRef<HTMLCanvasElement>(null);
  const drawRef = useRef(draw);
  drawRef.current = draw;
  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    let w = 0, h = 0, frame = 0, visible = true, live = false, last = performance.now(), budget = 1, slow = 0;
    const size = () => {
      const r = canvas.getBoundingClientRect();
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = r.width;
      h = r.height;
      canvas.width = Math.max(1, Math.round(w * dpr));
      canvas.height = Math.max(1, Math.round(h * dpr));
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    const once = (now: number): boolean => {
      // Hidden (display: none, say on a phone): nothing to draw until it has a size again.
      if (w < 4 || h < 4) return false;
      const still = !isFinite(now);
      const dt = still ? 0 : Math.max(0, Math.min(now - last, 64));
      if (!still) last = now;
      ctx.clearRect(0, 0, w, h);
      const more = drawRef.current({ ctx, w, h, t: still ? 0 : now, dt, budget, still }) !== false;
      // Twenty slow frames in a row (under ~45 fps) halve the work, down to a quarter.
      if (dt > 22) slow++;
      else slow = Math.max(0, slow - 1);
      if (slow > 20 && budget > 0.25) {
        budget /= 2;
        slow = 0;
      }
      return more;
    };
    const loop = (now: number) => {
      frame = once(now) ? requestAnimationFrame(loop) : 0;
    };
    const start = () => {
      cancelAnimationFrame(frame);
      last = performance.now();
      frame = 0;
      live = animate && motionTier() > 0 && visible && !document.hidden;
      if (live) frame = requestAnimationFrame(loop);
      else once(Infinity);
    };
    size();
    const ro = new ResizeObserver(() => {
      size();
      if (!frame && once(live ? performance.now() : Infinity) && live) frame = requestAnimationFrame(loop);
    });
    ro.observe(canvas);
    const io = new IntersectionObserver(([e]) => {
      visible = e.isIntersecting;
      start();
    });
    io.observe(canvas);
    const onVis = () => start();
    document.addEventListener("visibilitychange", onVis);
    start();
    return () => {
      cancelAnimationFrame(frame);
      ro.disconnect();
      io.disconnect();
      document.removeEventListener("visibilitychange", onVis);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [animate, ...deps]);
  return ref;
}

// Pointer effects for the whole app, set up once by the shell: buttons lean toward the pointer
// (magnetic), and cards light up where the pointer is. Only with a mouse or pen, never on touch.
export function usePointerEffects() {
  useEffect(() => {
    if (typeof matchMedia === "undefined" || !matchMedia("(pointer: fine)").matches) return;
    let frame = 0;
    let magnet: HTMLElement | null = null;
    let lit: HTMLElement | null = null;
    let ev: PointerEvent | null = null;
    const release = (el: HTMLElement | null) => {
      if (!el) return;
      el.style.removeProperty("--mx");
      el.style.removeProperty("--my");
    };
    const apply = () => {
      frame = 0;
      if (!ev || motionTier() === 0) return;
      const target = ev.target as Element | null;
      const m = target?.closest<HTMLElement>(".btn, .ib, .syncchip, .seg button, .chip");
      if (m !== magnet) {
        release(magnet);
        magnet = m ?? null;
      }
      if (magnet && !(magnet as HTMLButtonElement).disabled) {
        const r = magnet.getBoundingClientRect();
        const pull = magnet.classList.contains("primary") ? 0.22 : 0.12;
        magnet.style.setProperty("--mx", `${((ev.clientX - (r.left + r.width / 2)) * pull).toFixed(1)}px`);
        magnet.style.setProperty("--my", `${((ev.clientY - (r.top + r.height / 2)) * pull).toFixed(1)}px`);
      }
      const c = target?.closest<HTMLElement>(".card, .tile, .stat");
      if (c !== lit) {
        lit?.classList.remove("lit");
        lit = c ?? null;
        lit?.classList.add("lit");
      }
      if (lit) {
        const r = lit.getBoundingClientRect();
        lit.style.setProperty("--sx", `${ev.clientX - r.left}px`);
        lit.style.setProperty("--sy", `${ev.clientY - r.top}px`);
      }
    };
    const onMove = (e: PointerEvent) => {
      ev = e;
      if (!frame) frame = requestAnimationFrame(apply);
    };
    const onLeave = () => {
      release(magnet);
      magnet = null;
      lit?.classList.remove("lit");
      lit = null;
    };
    document.addEventListener("pointermove", onMove, { passive: true });
    document.documentElement.addEventListener("pointerleave", onLeave);
    return () => {
      cancelAnimationFrame(frame);
      document.removeEventListener("pointermove", onMove);
      document.documentElement.removeEventListener("pointerleave", onLeave);
      onLeave();
    };
  }, []);
}

// amount: the number is a sum of money. While amounts are hidden it rests, and when they show again
// it counts up from zero like the first time.
export function useCountUp(target: number, duration = 750, amount = false): number {
  const hidden = useHidden() && amount;
  const [value, setValue] = useState(reducedMotion() ? target : 0);
  const from = useRef(reducedMotion() ? target : 0);
  useEffect(() => {
    if (hidden) {
      from.current = 0;
      setValue(reducedMotion() ? target : 0);
      return;
    }
    if (reducedMotion() || !isFinite(target)) {
      setValue(target);
      from.current = target;
      return;
    }
    const start = performance.now();
    const origin = from.current;
    let frame = 0;
    const tick = (now: number) => {
      const t = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - t, 3);
      setValue(origin + (target - origin) * eased);
      if (t < 1) frame = requestAnimationFrame(tick);
      else from.current = target;
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [target, duration, hidden]);
  return value;
}

// Like useCountUp, but starts where it is: for values that glide from one state to the next
// (a chart zooming to another range, a number following a pointer).
export function useTween(target: number, duration = 450): number {
  const [value, setValue] = useState(target);
  const now = useRef(target);
  useEffect(() => {
    if (reducedMotion() || !isFinite(target) || !isFinite(now.current)) {
      now.current = target;
      setValue(target);
      return;
    }
    const start = performance.now();
    const origin = now.current;
    let frame = 0;
    const tick = (t: number) => {
      const k = Math.min((t - start) / duration, 1);
      const eased = 1 - Math.pow(1 - k, 3);
      now.current = origin + (target - origin) * eased;
      setValue(now.current);
      if (k < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [target, duration]);
  return value;
}

export function Money({ value, sign }: { value: number; sign?: boolean }) {
  const v = useCountUp(value, 750, true);
  return <span className="mono-num">{`${sign && value > 0 ? "+" : ""}${eur(v)}`}</span>;
}

export function Percent({ value }: { value: number | null }) {
  const v = useCountUp(value ?? 0);
  return <span className="mono-num">{value === null ? "–" : pct(v)}</span>;
}

// A big number that rolls into place like a mechanical counter: every digit is a column of 0 to 9
// that slides to its value, the other characters (€, separators, signs) stand still. Columns are
// matched from the right, so 999 → 1.000 rolls the last three and adds one. The first time it shows,
// and again when hidden amounts come back, every digit rolls up from 0; reduced motion shows the number
// straight away. Hidden, it is the blurred placeholder at once.
export function Odometer({ value, format = eur, className }: { value: number; format?: (v: number) => string; className?: string }) {
  const text = format(value);
  const digits = /\d/.test(text);
  const [shown, setShown] = useState(() => (reducedMotion() ? text : text.replace(/\d/g, "0")));
  useEffect(() => {
    if (reducedMotion() || !digits) {
      setShown(text);
      return;
    }
    setShown((s) => (/\d/.test(s) ? s : text.replace(/\d/g, "0")));
    let id = requestAnimationFrame(() => (id = requestAnimationFrame(() => setShown(text))));
    return () => cancelAnimationFrame(id);
  }, [text, digits]);
  const chars = [...(digits ? shown : text)];
  return (
    <span className={className ? `odo ${className}` : "odo"}>
      <span className="sr-only">{plain(text)}</span>
      <span className="odo-v" aria-hidden="true">
        {chars.map((c, i) => {
          const right = chars.length - i;
          return /\d/.test(c) ? (
            <span key={`d${right}`} className="odo-col" style={{ ["--d" as string]: c, ["--i" as string]: right }}>
              <span className="odo-strip">
                {DIGITS.map((d) => (
                  <span key={d}>{d}</span>
                ))}
              </span>
            </span>
          ) : (
            <span key={`c${right}${c}`} className="odo-ch">
              {c}
            </span>
          );
        })}
      </span>
    </span>
  );
}
const DIGITS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"];

// A handful of coins tumbling out of a point: Groschen's little celebration for
// finishing setup, clearing the review queue or a sync that brought something new.
let coinId = 0;
type Coin = { id: number; x: number; y: number; dx: number; dy: number; r: number; d: number; s: number; delay?: number; rain?: boolean };

export function celebrate(el?: Element | null, count = 14) {
  if (reducedMotion()) return;
  const rect = el?.getBoundingClientRect();
  const detail = { x: rect ? rect.left + rect.width / 2 : window.innerWidth / 2, y: rect ? rect.top + rect.height / 2 : window.innerHeight / 3, count };
  window.dispatchEvent(new CustomEvent("groschen:coins", { detail }));
}

export function CoinLayer() {
  const [coins, setCoins] = useState<Coin[]>([]);
  useEffect(() => {
    const onCoins = (e: Event) => {
      const { x, y, count, rain } = (e as CustomEvent<{ x: number; y: number; count: number; rain?: boolean }>).detail;
      // Rain (the Dagobert easter egg): coins fall from the top across the whole window.
      const made: Coin[] = rain
        ? Array.from({ length: Math.min(count, 80) }, () => ({
            id: ++coinId,
            x: Math.random() * window.innerWidth,
            y: -20,
            dx: (Math.random() - 0.5) * 120,
            dy: window.innerHeight + 60,
            r: (Math.random() - 0.5) * 900,
            d: 1400 + Math.random() * 900,
            s: 0.8 + Math.random() * 0.8,
            delay: Math.random() * 1400,
            rain: true,
          }))
        : Array.from({ length: Math.min(count, 40) }, () => ({
        id: ++coinId,
        x,
        y,
        dx: (Math.random() - 0.5) * 280,
        dy: -(120 + Math.random() * 170),
        r: (Math.random() - 0.5) * 720,
        d: 950 + Math.random() * 500,
        s: 0.7 + Math.random() * 0.6,
      }));
      const ids = new Set(made.map((c) => c.id));
      setCoins((c) => [...c, ...made]);
      window.setTimeout(() => setCoins((c) => c.filter((k) => !ids.has(k.id))), rain ? 3800 : 1600);
    };
    window.addEventListener("groschen:coins", onCoins);
    return () => window.removeEventListener("groschen:coins", onCoins);
  }, []);
  if (!coins.length) return null;
  return (
    <div className="coin-layer" aria-hidden="true">
      {coins.map((c) => (
        <span
          key={c.id}
          className={c.rain ? "coin rain" : "coin"}
          style={{
            left: c.x,
            top: c.y,
            ["--dx" as string]: `${c.dx}px`,
            ["--dy" as string]: `${c.dy}px`,
            ["--r" as string]: `${c.r}deg`,
            ["--s" as string]: c.s,
            animationDuration: `${c.d}ms`,
            animationDelay: c.delay ? `${c.delay}ms` : undefined,
          }}
        />
      ))}
    </div>
  );
}

// The soft colour field behind every screen: a few blurred blobs that drift very slowly
// and shift a little as the page scrolls. Pure CSS transforms, so it costs next to nothing;
// it holds still with reduced motion.
export function MeshBackdrop() {
  return (
    <div className="mesh" aria-hidden="true">
      <i className="m1" />
      <i className="m2" />
      <i className="m3" />
      <i className="m4" />
    </div>
  );
}
