// The depot over a stretch of time: what it earned in money (not counting what was paid in), bucket
// by bucket, per ETF, and its returns. Works on the daily series the server sends: the depot's value
// on a day and all money paid in up to that day.

import { periodBounds, type Period } from "./app";

export type DayPoint = { date: string; value: number; paid_in: number };

// Month-only dates ("2026-03", from before daily values existed) count from the middle of the month.
export const timeOf = (d: string) => Date.parse(d.length === 7 ? `${d}-15` : d.slice(0, 10));

// A period's first and last index in a series sorted by date, led by the day before it: a change
// over the period is measured from there. null when no day of the series falls in the period.
export function periodSpan(days: { date: string }[], p: Period): [number, number] | null {
  const { start, end } = periodBounds(p);
  let first = -1, last = -1;
  for (let i = 0; i < days.length; i++) {
    const d = days[i].date;
    if (d < start.slice(0, d.length) || d > end.slice(0, d.length)) continue;
    if (first < 0) first = i;
    last = i;
  }
  if (first < 0) return null;
  return [Math.max(first - 1, 0), last];
}

export type Gain = { gain: number; paid: number; rate: number | null };

// What the depot earned from one day to another: the change in value minus the money paid in
// between, and that as a share of the money at work. A payment counts for the part of the time it
// was in the depot (Modified Dietz), so a big payment late in the period doesn't water the rate down.
// end: the value at the end instead of the series' own (today's value, fresher than the last day).
export function gainBetween(days: DayPoint[], i0: number, i1: number, end?: number): Gain {
  const a = days[i0], b = days[i1];
  const paid = b.paid_in - a.paid_in;
  const gain = (end ?? b.value) - a.value - paid;
  const t0 = timeOf(a.date), t1 = timeOf(b.date), span = Math.max(t1 - t0, 1);
  let base = a.value;
  for (let i = i0 + 1; i <= i1; i++) {
    const f = days[i].paid_in - days[i - 1].paid_in;
    if (f) base += f * ((t1 - timeOf(days[i].date)) / span);
  }
  return { gain, paid, rate: base > 1 ? gain / base : null };
}

export type Unit = "month" | "week" | "day";
export type Bucket = { key: string; unit: Unit; i0: number; i1: number; gain: number };

// Months for a long view, weeks for a few months, days for a few weeks.
export function unitFor(days: { date: string }[], i0: number, i1: number): Unit {
  const span = (timeOf(days[i1].date) - timeOf(days[i0].date)) / 864e5;
  return span > 110 ? "month" : span > 24 ? "week" : "day";
}

export function mondayOf(iso: string) {
  const d = new Date(`${iso.slice(0, 10)}T12:00:00`);
  d.setDate(d.getDate() - ((d.getDay() + 6) % 7));
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}
const keyOf = (date: string, unit: Unit) => (unit === "month" ? date.slice(0, 7) : unit === "week" ? mondayOf(date) : date.slice(0, 10));

// The gain of every month (week, day) from i0 to i1, each measured from the day before it starts.
export function buckets(days: DayPoint[], i0: number, i1: number, unit = unitFor(days, i0, i1)): Bucket[] {
  const out: Bucket[] = [];
  for (let i = i0 + 1; i <= i1; i++) {
    const key = keyOf(days[i].date, unit);
    const last = out[out.length - 1];
    if (last && last.key === key) last.i1 = i;
    else out.push({ key, unit, i0: i, i1: i, gain: 0 });
  }
  for (const b of out) b.gain = gainBetween(days, b.i0 - 1, b.i1).gain;
  return out;
}

// How the money in it did, day by day with payments taken out, as an index starting at 1: the
// shape of an ETF's performance without the steps its savings plan adds.
export function performance(days: DayPoint[], i0: number, i1: number): number[] {
  const out = [1];
  let idx = 1;
  for (let i = i0 + 1; i <= i1; i++) {
    const prev = days[i - 1].value;
    if (prev >= 1) idx *= (days[i].value - (days[i].paid_in - days[i - 1].paid_in)) / prev;
    out.push(idx);
  }
  return out;
}

// At most n values, evenly picked, keeping the last.
export function thin(values: number[], n = 60): number[] {
  if (values.length <= n) return values;
  const step = (values.length - 1) / (n - 1);
  return Array.from({ length: n }, (_, k) => values[Math.round(k * step)]);
}

// Money-weighted annual return: flows as [time in ms, amount], money in negative, the end value positive.
export function xirr(flows: [number, number][]): number | null {
  if (flows.length < 2 || !flows.some(([, a]) => a > 0) || !flows.some(([, a]) => a < 0)) return null;
  const t0 = flows[0][0];
  const npv = (rate: number) => flows.reduce((s, [t, a]) => s + a / Math.pow(1 + rate, (t - t0) / (365 * 864e5)), 0);
  let lo = -0.99, hi = 10, fLo = npv(lo);
  if (fLo * npv(hi) > 0) return null;
  for (let k = 0; k < 200; k++) {
    const mid = (lo + hi) / 2, f = npv(mid);
    if (Math.abs(f) < 1e-7) return mid;
    if (fLo * f < 0) hi = mid;
    else {
      lo = mid;
      fLo = f;
    }
  }
  return (lo + hi) / 2;
}

// The money-weighted return of the depot between two days, the start value counting as paid in.
export function xirrBetween(days: DayPoint[], i0: number, i1: number): number | null {
  const flows: [number, number][] = [[timeOf(days[i0].date), -days[i0].value]];
  for (let i = i0 + 1; i <= i1; i++) {
    const f = days[i].paid_in - days[i - 1].paid_in;
    if (f) flows.push([timeOf(days[i].date), -f]);
  }
  flows.push([timeOf(days[i1].date), days[i1].value]);
  return xirr(flows);
}

export type Returns = { months: number; twr: number | null; perYear: boolean; volatility: number | null; sharpe: number | null; up: number };

// The market's part of the returns over a list of months: chained into one figure (per year once
// the list covers a year), how much they swung, and the Sharpe ratio against the risk-free rate.
export function monthlyReturns(returns: { r: number }[], riskFree: number): Returns {
  const n = returns.length;
  const growth = returns.reduce((g, x) => g * (1 + x.r), 1);
  const perYear = n >= 12;
  const twr = n ? (perYear ? (growth > 0 ? Math.pow(growth, 12 / n) - 1 : null) : growth - 1) : null;
  let volatility: number | null = null;
  if (n >= 3) {
    const mean = returns.reduce((s, x) => s + x.r, 0) / n;
    volatility = Math.sqrt(returns.reduce((s, x) => s + (x.r - mean) ** 2, 0) / (n - 1)) * Math.sqrt(12);
  }
  const sharpe = perYear && twr !== null && volatility ? (twr - riskFree / 100) / volatility : null;
  return { months: n, twr, perYear, volatility, sharpe, up: returns.filter((x) => x.r > 0).length };
}
