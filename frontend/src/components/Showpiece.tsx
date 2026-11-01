// The animated centrepieces: money flowing through the Sankey, the payday tank and the
// orbit of recurring payments. All drawn on canvas with useCanvasLoop, so they pause off
// screen and in background tabs, do less on slow devices and hold still with reduced motion.

import { useMemo, useRef, useState } from "react";
import { t } from "../i18n";
import { currencySign, dateShort, eur, eur0, intervalName } from "../lib/format";
import { motionTier, useCanvasLoop } from "./Motion";

// --- colour helpers ------------------------------------------------------------------------

// Canvas can't read CSS variables, so a colour like var(--good) is resolved through a hidden probe.
export function resolveColor(css: string): [number, number, number] {
  if (typeof document === "undefined") return [128, 128, 128];
  const probe = document.createElement("span");
  probe.style.color = css;
  probe.style.display = "none";
  document.body.appendChild(probe);
  const m = getComputedStyle(probe).color.match(/[\d.]+/g) ?? ["128", "128", "128"];
  probe.remove();
  return [Number(m[0]), Number(m[1]), Number(m[2])];
}

export const rgba = ([r, g, b]: [number, number, number], a: number) => `rgba(${r},${g},${b},${a.toFixed(3)})`;

function roundRect(ctx: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

// A small seeded random so the same data always draws the same particles.
function seeded(seed: number) {
  let s = seed | 0;
  return () => {
    s = (s + 0x6d2b79f5) | 0;
    let x = Math.imul(s ^ (s >>> 15), 1 | s);
    x = (x + Math.imul(x ^ (x >>> 7), 61 | x)) ^ x;
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
  };
}

// --- money flowing through the Sankey ---------------------------------------------------------

// from/to: the colour where a band starts and where it ends; nw: the width of the node it runs into;
// delay: when the band starts pouring in (ms), so its comets only appear once it is there.
export type Band = { key: string; x0: number; a0: number; a1: number; x1: number; b0: number; b1: number; from: string; to: string; share: number; nw: number; delay: number };

type Rgb = [number, number, number];

const bez = (p0: number, p1: number, p2: number, p3: number, u: number) => {
  const v = 1 - u;
  return v * v * v * p0 + 3 * v * v * u * p1 + 3 * v * u * u * p2 + u * u * u * p3;
};
const mix = (a: Rgb, b: Rgb, u: number): Rgb => [a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u];
const clamp01 = (x: number) => Math.min(1, Math.max(0, x));

function bandPath(ctx: CanvasRenderingContext2D, b: Band, k: number) {
  const xm = ((b.x0 + b.x1) / 2) * k;
  ctx.beginPath();
  ctx.moveTo(b.x0 * k, b.a0 * k);
  ctx.bezierCurveTo(xm, b.a0 * k, xm, b.b0 * k, b.x1 * k, b.b0 * k);
  ctx.lineTo(b.x1 * k, b.b1 * k);
  ctx.bezierCurveTo(xm, b.b1 * k, xm, b.a1 * k, b.x0 * k, b.a1 * k);
  ctx.closePath();
}

// A comet, drawn once per colour and then reused: a soft glowing head with a small bright core, and a
// tail that thins to a point and fades to nothing, so it reads as light rather than as a little pill.
// The head sits at (hx, H / 2); the sprite is drawn along the band's direction.
const COMET = { L: 38, H: 14, hx: 31, hr: 1.6 };
// Colour steps per band, from where it starts to where it ends.
const STEPS = 6;
function cometSprite(c: Rgb, scale: number) {
  const { L, H, hx, hr } = COMET;
  const cv = document.createElement("canvas");
  cv.width = Math.ceil(L * scale);
  cv.height = Math.ceil(H * scale);
  const x = cv.getContext("2d")!;
  x.scale(scale, scale);
  const cy = H / 2;
  const tail = x.createLinearGradient(0, 0, hx, 0);
  tail.addColorStop(0, rgba(c, 0));
  tail.addColorStop(0.6, rgba(c, 0.16));
  tail.addColorStop(1, rgba(c, 0.7));
  x.beginPath();
  x.moveTo(0, cy);
  x.quadraticCurveTo(hx * 0.55, cy - hr * 0.35, hx, cy - hr);
  x.lineTo(hx, cy + hr);
  x.quadraticCurveTo(hx * 0.55, cy + hr * 0.35, 0, cy);
  x.closePath();
  x.fillStyle = tail;
  x.fill();
  const glow = x.createRadialGradient(hx, cy, 0, hx, cy, 6);
  glow.addColorStop(0, rgba(c, 0.5));
  glow.addColorStop(0.4, rgba(c, 0.18));
  glow.addColorStop(1, rgba(c, 0));
  x.fillStyle = glow;
  x.beginPath();
  x.arc(hx, cy, 6, 0, Math.PI * 2);
  x.fill();
  x.fillStyle = rgba(mix(c, [255, 255, 255], 0.6), 1);
  x.beginPath();
  x.arc(hx, cy, hr * 0.85, 0, Math.PI * 2);
  x.fill();
  return cv;
}

// Money flowing through the Sankey. Small comets travel along each band, more of them where
// more money flows, and take on the colour of where they are heading. A few are spinning coins.
// Where they arrive, the node lights up with a small ripple, so the busiest categories glow most.
// Every few seconds a soft wave of light runs across all bands; the band under the pointer gets a
// quicker one, its comets speed up and brighten while the others dim. Each comet moves on from
// where it is by the time that passed, so a change of speed never makes the comets jump.
// The "calm" setting and slow devices keep the comets only; "off" and reduced motion draw nothing.
export function FlowParticles({ bands, W, hot }: { bands: Band[]; W: number; hot: string | null }) {
  const tier = motionTier();
  const parts = useMemo(() => {
    const rand = seeded(bands.length * 97 + 13);
    const out: { band: number; u0: number; lane: number; v: number; r: number; coin: boolean; spin: number }[] = [];
    bands.forEach((b, i) => {
      // A share is 0..1 of the chart; anything outside (or not a number) must not flood the canvas.
      const n = Math.round(Math.max(3, Math.sqrt(Math.min(1, Math.max(0, b.share || 0))) * 70));
      for (let k = 0; k < n; k++) out.push({ band: i, u0: rand(), lane: (rand() - 0.5) * 0.84, v: 0.00007 + rand() * 0.00006, r: 0.9 + rand() * 1.3, coin: rand() < 0.045, spin: rand() * 6.28 });
    });
    return out;
  }, [bands]);
  // Many bands share their colours (the timeline has hundreds), so each colour is looked up once
  // and each pair of colours gets one set of comet sprites.
  const colors = useMemo(() => {
    const known = new Map<string, Rgb>();
    const rc = (c: string) => known.get(c) ?? known.set(c, resolveColor(c)).get(c)!;
    return bands.map((b) => [rc(b.from), rc(b.to)] as [Rgb, Rgb]);
  }, [bands]);
  const pairOf = useMemo(() => {
    const idx = new Map<string, number>();
    return bands.map((b) => idx.get(`${b.from}|${b.to}`) ?? idx.set(`${b.from}|${b.to}`, idx.size).get(`${b.from}|${b.to}`)!);
  }, [bands]);
  const font = useMemo(() => (typeof document === "undefined" ? "sans-serif" : getComputedStyle(document.body).fontFamily), []);
  // One character fits on a coin: "€", "$", "£"; a longer sign ("CHF") leaves it plain.
  const coinSign = useMemo(() => (currencySign().length === 1 ? currencySign() : ""), []);
  // Where every comet is, each band's current speed, brightness and node glow (easing toward
  // their targets instead of switching), and the ripples still spreading.
  type State = { parts: typeof parts; u: Float64Array; speed: Float64Array; lit: Float64Array; glow: Float64Array; ripples: { j: number; y: number; t0: number }[]; born: number };
  const flow = useRef<State | null>(null);
  const sprites = useRef<{ colors: typeof colors; scale: number; list: HTMLCanvasElement[][] } | null>(null);
  if (flow.current?.parts !== parts) {
    const n = bands.length;
    flow.current = {
      parts,
      u: Float64Array.from(parts, (p) => p.u0),
      speed: new Float64Array(n).fill(1),
      lit: new Float64Array(n).fill(1),
      glow: new Float64Array(n),
      ripples: [],
      born: flow.current?.born ?? 0,
    };
  }
  const ref = useCanvasLoop(
    ({ ctx, w, t: now, dt, budget, still }) => {
      if (still || tier === 0) return false;
      const f = flow.current!;
      if (!f.born) f.born = now;
      const age = now - f.born;
      // Streaks fade in band by band once each band has poured in.
      const intro = clamp01((age - 600) / 900);
      const shown = bands.map((b) => clamp01((age - b.delay - 650) / 600));
      const k = w / W;
      const rich = tier === 2 && budget >= 0.5;
      // The canvas is scaled to the screen's pixel ratio; comets are drawn with their own transform.
      const D = ctx.getTransform().a;
      const scale = Math.min(3, Math.ceil(D * 1.5));
      let sp = sprites.current;
      if (!sp || sp.colors !== colors || sp.scale !== scale) {
        const firsts: [Rgb, Rgb][] = [];
        pairOf.forEach((p, j) => (firsts[p] ??= colors[j]));
        sp = sprites.current = { colors, scale, list: firsts.map(([c0, c1]) => Array.from({ length: STEPS }, (_, s) => cometSprite(mix(c0, c1, (s + 0.5) / STEPS), scale))) };
      }
      const ease = 1 - Math.exp(-dt / 160);
      const cool = Math.exp(-dt / 420);
      bands.forEach((b, j) => {
        f.speed[j] += ((hot === b.key ? 2 : 1) - f.speed[j]) * ease;
        f.lit[j] += ((hot === null || hot === b.key ? 1 : 0) - f.lit[j]) * ease;
        f.glow[j] *= cool;
      });
      ctx.globalCompositeOperation = "lighter";

      // Waves of light: one across everything every 7 seconds, a quicker one along the hot band.
      const sweep = (j: number, X: number, half: number, alpha: number) => {
        const b = bands[j];
        if (X - half > b.x1 * k || X + half < b.x0 * k || alpha < 0.005) return;
        const c = mix(colors[j][0], colors[j][1], clamp01((X / k - b.x0) / (b.x1 - b.x0)));
        const g = ctx.createLinearGradient(X - half, 0, X + half, 0);
        g.addColorStop(0, rgba(c, 0));
        g.addColorStop(0.5, rgba(c, alpha));
        g.addColorStop(1, rgba(c, 0));
        bandPath(ctx, b, k);
        ctx.fillStyle = g;
        ctx.fill();
        // ...and runs along the band's edges like light on a rail.
        const e = ctx.createLinearGradient(X - half, 0, X + half, 0);
        e.addColorStop(0, rgba(c, 0));
        e.addColorStop(0.5, rgba(c, Math.min(0.9, alpha * 3.5)));
        e.addColorStop(1, rgba(c, 0));
        const xm = ((b.x0 + b.x1) / 2) * k;
        ctx.beginPath();
        ctx.moveTo(b.x0 * k, b.a0 * k);
        ctx.bezierCurveTo(xm, b.a0 * k, xm, b.b0 * k, b.x1 * k, b.b0 * k);
        ctx.moveTo(b.x0 * k, b.a1 * k);
        ctx.bezierCurveTo(xm, b.a1 * k, xm, b.b1 * k, b.x1 * k, b.b1 * k);
        ctx.strokeStyle = e;
        ctx.lineWidth = 1.6;
        ctx.stroke();
      };
      if (rich && intro === 1 && bands.length) {
        const ph = (age - 1500) % 7000;
        if (ph >= 0 && ph < 2600) {
          const p = ph / 2600;
          const e = p < 0.5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2;
          let lo = Infinity, hi = -Infinity;
          for (const b of bands) {
            lo = Math.min(lo, b.x0);
            hi = Math.max(hi, b.x1);
          }
          const X = (lo - 160 + (hi - lo + 320) * e) * k;
          bands.forEach((_, j) => sweep(j, X, 130 * k, 0.22 * f.lit[j]));
        }
        const hj = hot ? bands.findIndex((b) => b.key === hot) : -1;
        if (hj >= 0) {
          const b = bands[hj];
          const p = (now % 1400) / 1400;
          sweep(hj, (b.x0 - 60 + (b.x1 - b.x0 + 120) * p) * k, 80 * k, 0.24);
        }
      }

      // The comets.
      const keep = budget * (tier === 1 ? 0.45 : 1);
      const peak = 0.9;
      const coins: { x: number; y: number; c: Rgb; a: number; spin: number }[] = [];
      for (let i = 0; i < parts.length; i++) {
        const p = parts[i];
        const j = p.band;
        const next = f.u[i] + dt * p.v * f.speed[j];
        if (next >= 1) {
          f.glow[j] = Math.min(1, f.glow[j] + 0.2);
          if (rich && f.ripples.length < 36 && bands[j].key.startsWith("spending:") && (i * 0.382) % 1 < 0.5) f.ripples.push({ j, y: p.lane, t0: now });
        }
        const u = (f.u[i] = next % 1);
        if ((i * 0.618) % 1 > keep) continue;
        const b = bands[j];
        const a = (0.15 + (peak - 0.15) * f.lit[j]) * Math.sin(Math.PI * u) * shown[j];
        if (a < 0.01) continue;
        const xm = (b.x0 + b.x1) / 2;
        const at = (uu: number) => {
          const x = bez(b.x0, xm, xm, b.x1, uu);
          const top = bez(b.a0, b.a0, b.b0, b.b0, uu);
          const bot = bez(b.a1, b.a1, b.b1, b.b1, uu);
          return [x * k, (top + (bot - top) * (0.5 + p.lane)) * k];
        };
        const [x1, y1] = at(u);
        if (p.coin && rich && Math.min(b.a1 - b.a0, b.b1 - b.b0) * k > 11) {
          coins.push({ x: x1, y: y1, c: mix(colors[j][0], colors[j][1], u), a, spin: p.spin });
          continue;
        }
        // Point the comet where the band is heading; a faster band stretches its tail.
        const [xa, ya] = at(u + 0.005);
        const len = Math.hypot(xa - x1, ya - y1) || 1;
        const cos = (xa - x1) / len, sin = (ya - y1) / len;
        const sy = p.r / 1.5, sx = sy * (1 + 0.5 * (f.speed[j] - 1));
        ctx.globalAlpha = Math.min(1, a);
        ctx.setTransform(D * cos * sx, D * sin * sx, -D * sin * sy, D * cos * sy, D * x1, D * y1);
        ctx.drawImage(sp.list[pairOf[j]][Math.min(STEPS - 1, Math.floor(u * STEPS))], -COMET.hx, -COMET.H / 2, COMET.L, COMET.H);
      }
      ctx.setTransform(D, 0, 0, D, 0, 0);
      ctx.globalAlpha = 1;

      // Nodes light up where money arrives, with a ripple now and then.
      bands.forEach((b, j) => {
        const g = f.glow[j] * shown[j] * (0.35 + 0.65 * f.lit[j]);
        if (g < 0.02) return;
        const x = b.x1 * k, y = b.b0 * k, hgt = Math.max((b.b1 - b.b0) * k, 1.5), nw = b.nw * k;
        ctx.fillStyle = rgba(colors[j][1], g * 0.16);
        roundRect(ctx, x - 3, y - 3, nw + 6, hgt + 6, 5);
        ctx.fill();
        ctx.fillStyle = rgba([255, 255, 255], g * 0.22);
        roundRect(ctx, x, y, nw, hgt, 2);
        ctx.fill();
      });
      if (f.ripples.length) {
        f.ripples = f.ripples.filter((r) => now - r.t0 < 750);
        ctx.lineWidth = 1.2;
        for (const r of f.ripples) {
          const b = bands[r.j];
          if (!b) continue;
          const q = (now - r.t0) / 750;
          const rad = 2 + 11 * (1 - Math.pow(1 - q, 3));
          ctx.strokeStyle = rgba(colors[r.j][1], 0.55 * (1 - q) * intro * (0.3 + 0.7 * f.lit[r.j]));
          ctx.beginPath();
          ctx.arc(b.x1 * k, (b.b0 + (b.b1 - b.b0) * (0.5 + r.y)) * k, rad, 0, Math.PI * 2);
          ctx.stroke();
        }
      }

      // Coins spin as they travel; drawn normally so the € (or the home currency's sign) stays readable.
      ctx.globalCompositeOperation = "source-over";
      if (coins.length) {
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.font = `700 7.5px ${font}`;
        for (const c of coins) {
          const s = Math.cos(now * 0.0035 + c.spin);
          ctx.save();
          ctx.translate(c.x, c.y);
          ctx.scale(Math.max(0.15, Math.abs(s)), 1);
          ctx.beginPath();
          ctx.arc(0, 0, 4.8, 0, Math.PI * 2);
          ctx.fillStyle = rgba(c.c, Math.min(1, c.a * 1.1));
          ctx.fill();
          if (Math.abs(s) > 0.5) {
            ctx.fillStyle = rgba([8, 10, 12], c.a * 0.9);
            ctx.fillText(coinSign, 0, 0.5);
          }
          ctx.restore();
        }
      }
      ctx.setTransform(D, 0, 0, D, 0, 0);
    },
    // The pointer is read on every frame, so hovering doesn't restart the loop.
    [parts, colors, pairOf, W, tier, font],
  );
  return <canvas ref={ref} className="overlay-canvas" aria-hidden="true" />;
}

// --- the payday tank --------------------------------------------------------------------------

// What's left until payday as a level gauge: it fills up when the page opens, the surface
// moves gently, and it turns amber and then red as it runs low. Flat colours, no glass effects.
export function LiquidTank({ level, label }: { level: number; label: string }) {
  const lv = Math.max(0, Math.min(1, level));
  const tone = lv > 0.35 ? "good" : lv > 0.12 ? "warn" : "bad";
  const born = useRef(0);
  const colors = useMemo(() => ({ liquid: resolveColor(`var(--${tone})`), line: resolveColor("var(--line-2)"), ink: resolveColor("var(--muted)") }), [tone]);
  const bubbles = useMemo(() => {
    const rand = seeded(42);
    return Array.from({ length: 9 }, () => ({ x: 0.12 + rand() * 0.76, v: 0.012 + rand() * 0.02, o: rand(), r: 1 + rand() * 2.2 }));
  }, []);
  const ref = useCanvasLoop(
    ({ ctx, w, h, t: now, still }) => {
      if (!born.current) born.current = now;
      const p = still ? 1 : Math.min(1, (now - born.current) / 1500);
      const fill = lv * (1 - Math.pow(1 - p, 3));
      const x = 8, y = 6, tw = w - 16, th = h - 12, r = Math.min(22, tw / 3);
      const surface = y + th - fill * th;
      const amp = still ? 0 : 3.2 * (0.35 + 0.65 * (1 - p * 0.5));
      ctx.save();
      roundRect(ctx, x, y, tw, th, r);
      ctx.clip();
      // the surface as a line (open) or as the body of liquid under it (closed)
      const wave = (phase: number, a: number, speed: number, body = true) => {
        ctx.beginPath();
        if (body) ctx.moveTo(x, y + th);
        for (let px = 0; px <= tw; px += 4) {
          const yy = surface + Math.sin(px * 0.05 + now * speed + phase) * a + Math.sin(px * 0.021 - now * speed * 0.6) * a * 0.6;
          if (!body && px === 0) ctx.moveTo(x + px, yy);
          else ctx.lineTo(x + px, yy);
        }
        if (body) {
          ctx.lineTo(x + tw, y + th);
          ctx.closePath();
        }
      };
      wave(1.7, amp, 0.0017);
      ctx.fillStyle = rgba(colors.liquid, 0.2);
      ctx.fill();
      wave(0, amp * 0.8, 0.0024);
      const g = ctx.createLinearGradient(0, surface, 0, y + th);
      g.addColorStop(0, rgba(colors.liquid, 0.5));
      g.addColorStop(1, rgba(colors.liquid, 0.12));
      ctx.fillStyle = g;
      ctx.fill();
      // a bright rim where the liquid meets the air
      if (fill > 0.01) {
        wave(0, amp * 0.8, 0.0024, false);
        ctx.strokeStyle = rgba(colors.liquid, 0.95);
        ctx.lineWidth = 2;
        ctx.stroke();
      }
      // bubbles rising through the liquid
      if (!still && fill > 0.04) {
        for (const b of bubbles) {
          const k = (b.o + now * b.v * 0.001) % 1;
          const by = y + th - k * (y + th - surface);
          ctx.beginPath();
          ctx.arc(x + b.x * tw + Math.sin(now * 0.002 + b.o * 9) * 2, by, b.r, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(255,255,255,${(0.35 * (1 - k)).toFixed(3)})`;
          ctx.fill();
        }
      }
      ctx.restore();
      // scale marks
      ctx.strokeStyle = rgba(colors.ink, 0.35);
      ctx.lineWidth = 1;
      for (const m of [0.25, 0.5, 0.75]) {
        const my = y + th - m * th;
        ctx.beginPath();
        ctx.moveTo(x + tw - 10, my);
        ctx.lineTo(x + tw - 3, my);
        ctx.stroke();
      }
      roundRect(ctx, x, y, tw, th, r);
      ctx.strokeStyle = rgba(colors.line, 1);
      ctx.lineWidth = 1.5;
      ctx.stroke();
      return true;
    },
    [lv, colors],
  );
  return <canvas ref={ref} className="tank" role="img" aria-label={label} />;
}

// --- the orbit of recurring payments ---------------------------------------------------------------

export type OrbitItem = { key: string; name: string; interval: string; next_date: string; amount: number; monthly_cost: number; color: string };

// Every rhythm Groschen knows, with the days one round of its orbit takes. Only the rhythms that
// occur get a ring; they spread out evenly between the sun and the edge.
export const ORBITS: [string, number][] = [
  ["weekly", 7],
  ["biweekly", 14],
  ["4-weekly", 28],
  ["monthly", 30.44],
  ["bimonthly", 60.88],
  ["quarterly", 91.31],
  ["half-yearly", 182.62],
  ["yearly", 365.25],
];

function ringsFor(items: OrbitItem[]): [string, number, number][] {
  const used = ORBITS.filter(([k]) => items.some((i) => i.interval === k));
  const list = used.length ? used : [ORBITS[3]];
  return list.map(([k, days], i) => [k, list.length === 1 ? 0.55 : 0.3 + (0.51 * i) / (list.length - 1), days]);
}

type Placed = { item: OrbitItem; x: number; y: number; r: number; depth: number };

// Every recurring payment circles the month on the ring of its interval. It travels toward
// the front as its next payment gets closer and reaches the marker on the day it is due.
// Moving the pointer tilts the whole system a little.
export function OrbitView({ items, monthly, onPick }: { items: OrbitItem[]; monthly: number; onPick: (item: OrbitItem) => void }) {
  const tier = motionTier();
  const tilt = useRef({ x: 0, y: 0, tx: 0, ty: 0 });
  const placed = useRef<Placed[]>([]);
  const [hover, setHover] = useState<Placed | null>(null);
  const hoverKey = hover?.item.key ?? null;
  const colors = useMemo(
    () => ({
      items: items.map((i) => resolveColor(i.color)),
      accent: resolveColor("var(--accent)"),
      line: resolveColor("var(--muted)"),
      ink: resolveColor("var(--ink)"),
      surface: resolveColor("var(--surface)"),
    }),
    [items],
  );
  const today = useMemo(() => {
    const d = new Date();
    return Date.UTC(d.getFullYear(), d.getMonth(), d.getDate());
  }, []);
  const stars = useMemo(() => {
    const rand = seeded(7);
    return Array.from({ length: 60 }, () => ({ x: rand(), y: rand(), r: rand() * 1.2 + 0.3, p: rand() * 6 }));
  }, []);
  const top = useMemo(() => new Set([...items].sort((a, b) => b.monthly_cost - a.monthly_cost).slice(0, 5).map((i) => i.key)), [items]);
  const rings = useMemo(() => ringsFor(items), [items]);

  const ref = useCanvasLoop(
    ({ ctx, w, h, t: now, dt, still }) => {
      const tl = tilt.current;
      const ease = still ? 1 : Math.min(1, dt / 220);
      tl.x += (tl.tx - tl.x) * ease;
      tl.y += (tl.ty - tl.y) * ease;
      const sway = still || tier < 2 ? 0 : Math.sin(now / 9000) * 0.05;
      const yaw = sway + tl.x * 0.18;
      const squash = 0.36 + tl.y * 0.08;
      const cx = w / 2, cy = h / 2 + 6;
      const R = Math.min(w / 2 - 20, (h / 2 - 26) / squash);
      // stars
      for (const s of stars) {
        const tw = still ? 0.5 : 0.5 + 0.5 * Math.sin(now / 1400 + s.p);
        ctx.fillStyle = rgba(colors.line, 0.12 + 0.18 * tw);
        ctx.beginPath();
        ctx.arc(s.x * w, s.y * h, s.r, 0, Math.PI * 2);
        ctx.fill();
      }
      const ring = (f: number, front: boolean) => {
        ctx.beginPath();
        ctx.ellipse(cx, cy, R * f, R * f * squash, 0, front ? 0 : Math.PI, front ? Math.PI : Math.PI * 2);
        ctx.strokeStyle = rgba(colors.line, front ? 0.45 : 0.2);
        ctx.lineWidth = front ? 1.3 : 1;
        ctx.setLineDash(front ? [] : [3, 5]);
        ctx.stroke();
        ctx.setLineDash([]);
      };
      // where each payment is right now
      const list: Placed[] = items.map((it) => {
        const ringDef = rings.find(([k]) => k === it.interval) ?? rings[0];
        const next = Date.parse(`${it.next_date}T00:00:00Z`);
        const until = Math.max(0, (next - today) / 86400000);
        const theta = Math.PI / 2 - 2 * Math.PI * Math.min(1, until / ringDef[2]) + yaw;
        const rr = R * ringDef[1];
        const depth = Math.sin(theta);
        const size = Math.max(4.5, Math.min(20, 4 + Math.sqrt(it.monthly_cost) * 1.5)) * (0.78 + 0.22 * (depth + 1));
        return { item: it, x: cx + rr * Math.cos(theta), y: cy + rr * squash * depth, r: size, depth };
      });
      placed.current = list;
      for (const [, f] of rings) ring(f, false);
      const planet = (p: Placed, idx: number) => {
        const c = colors.items[idx];
        const hot = hoverKey === p.item.key;
        const dim = hoverKey && !hot ? 0.45 : 1;
        if (hot) {
          const glow = ctx.createRadialGradient(p.x, p.y, p.r * 0.5, p.x, p.y, p.r * 2.6);
          glow.addColorStop(0, rgba(c, 0.45));
          glow.addColorStop(1, rgba(c, 0));
          ctx.fillStyle = glow;
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.r * 2.6, 0, Math.PI * 2);
          ctx.fill();
        }
        const g = ctx.createRadialGradient(p.x - p.r * 0.35, p.y - p.r * 0.4, p.r * 0.1, p.x, p.y, p.r);
        g.addColorStop(0, `rgba(255,255,255,${0.85 * dim})`);
        g.addColorStop(0.25, rgba(c, dim));
        g.addColorStop(1, rgba(c.map((v) => v * 0.55) as [number, number, number], dim));
        ctx.fillStyle = g;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r * (hot ? 1.15 : 1), 0, Math.PI * 2);
        ctx.fill();
      };
      // Names for the biggest payments (and the one under the pointer), front ones first,
      // skipping any that would overlap a name already placed.
      const labels = () => {
        const taken: [number, number, number, number][] = [];
        const wanted = list.filter((p) => hoverKey === p.item.key || top.has(p.item.key));
        wanted.sort((a, b) => Number(hoverKey === b.item.key) - Number(hoverKey === a.item.key) || b.depth - a.depth);
        for (const p of wanted) {
          const hot = hoverKey === p.item.key;
          const text = p.item.name.length > 18 ? `${p.item.name.slice(0, 17)}…` : p.item.name;
          ctx.font = `${hot ? 600 : 500} 11.5px Figtree Variable, system-ui, sans-serif`;
          const box: [number, number, number, number] = [p.x + p.r + 5, p.y - 8, ctx.measureText(text).width, 16];
          if (!hot && taken.some((t) => box[0] < t[0] + t[2] && t[0] < box[0] + box[2] && box[1] < t[1] + t[3] && t[1] < box[1] + box[3])) continue;
          taken.push(box);
          // A soft plate under the name keeps it readable where it crosses another payment.
          roundRect(ctx, box[0] - 4, box[1] - 1, box[2] + 8, box[3] + 2, 6);
          ctx.fillStyle = rgba(colors.surface, hot ? 0.92 : 0.72);
          ctx.fill();
          ctx.textAlign = "left";
          ctx.fillStyle = rgba(colors.ink, hot ? 1 : 0.75);
          ctx.fillText(text, box[0], p.y + 4);
        }
      };
      const order = list.map((p, i) => [p, i] as const).sort((a, b) => a[0].depth - b[0].depth);
      for (const [p, i] of order) if (p.depth < 0) planet(p, i);
      // the month in the middle
      const pulse = still ? 1 : 1 + Math.sin(now / 900) * 0.04;
      const sun = ctx.createRadialGradient(cx, cy, 2, cx, cy, 46 * pulse);
      sun.addColorStop(0, rgba(colors.accent, 0.95));
      sun.addColorStop(0.35, rgba(colors.accent, 0.55));
      sun.addColorStop(1, rgba(colors.accent, 0));
      ctx.fillStyle = sun;
      ctx.beginPath();
      ctx.arc(cx, cy, 46 * pulse, 0, Math.PI * 2);
      ctx.fill();
      for (const [, f] of rings) ring(f, true);
      for (const [p, i] of order) if (p.depth >= 0) planet(p, i);
      labels();
      // the "due" marker at the front
      const my = cy + R * rings[rings.length - 1][1] * squash + 14;
      ctx.fillStyle = rgba(colors.accent, 0.9);
      ctx.beginPath();
      ctx.moveTo(cx, my - 8);
      ctx.lineTo(cx - 5, my);
      ctx.lineTo(cx + 5, my);
      ctx.closePath();
      ctx.fill();
      ctx.font = "600 11px Figtree Variable, system-ui, sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(t("orbit.due"), cx, my + 13);
    },
    [items, colors, hoverKey, today, tier, rings],
  );

  const find = (e: React.PointerEvent<HTMLCanvasElement>) => {
    const r = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - r.left, y = e.clientY - r.top;
    let best: Placed | null = null;
    for (const p of placed.current) {
      const d = Math.hypot(p.x - x, p.y - y);
      if (d <= p.r + 6 && (!best || p.depth > best.depth)) best = p;
    }
    return { best, x, y, r };
  };

  return (
    <div className="orbit">
      <canvas
        ref={ref}
        role="img"
        aria-label={t("orbit.label", { n: items.length, amount: eur(monthly) })}
        className={hover ? "picking" : undefined}
        onPointerMove={(e) => {
          const { best, x, y, r } = find(e);
          tilt.current.tx = (x / r.width - 0.5) * 2;
          tilt.current.ty = (y / r.height - 0.5) * 2;
          if ((best?.item.key ?? null) !== hoverKey) setHover(best);
        }}
        onPointerLeave={() => {
          tilt.current.tx = 0;
          tilt.current.ty = 0;
          setHover(null);
        }}
        onClick={(e) => {
          const { best } = find(e as unknown as React.PointerEvent<HTMLCanvasElement>);
          if (best) onPick(best.item);
        }}
      />
      <div className="orbit-center" aria-hidden="true">
        <b>{eur0(monthly)}</b>
        <small>{t("orbit.perMonth")}</small>
      </div>
      {hover && (
        <div className="orbit-tip" style={{ left: hover.x, top: hover.y - hover.r - 10 }}>
          <b>{hover.item.name}</b>
          <span>
            {eur(hover.item.amount)} · {intervalName(hover.item.interval)}
          </span>
          <small>{t("orbit.next", { date: dateShort(hover.item.next_date) })}</small>
        </div>
      )}
    </div>
  );
}
