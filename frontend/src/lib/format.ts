import { getLang, getRegion, locale, numLocale, t, type TKey } from "../i18n";
import { amountsHidden } from "./privacy";

// Amounts are in the home currency (Settings) unless they say otherwise, written the home
// country's way: 1.234,56 € in Germany, $1,234.56 in the US, CHF 1’234.50 in Switzerland.
const cache = new Map<string, Intl.NumberFormat>();
function fmt(currency: string, digits: number | undefined) {
  const key = `${numLocale()}|${currency}|${digits}`;
  let f = cache.get(key);
  if (!f) {
    try {
      f = new Intl.NumberFormat(numLocale(), { style: "currency", currency, maximumFractionDigits: digits });
    } catch {
      f = new Intl.NumberFormat(numLocale(), { style: "currency", currency: "EUR", maximumFractionDigits: digits });
    }
    cache.set(key, f);
  }
  return f;
}
const isAmount = (p: Intl.NumberFormatPart) => p.type === "integer" || p.type === "group" || p.type === "decimal" || p.type === "fraction";
// The € always follows the amount ("4,271.93 €"), in English too, where Intl would put it in front.
// Other currencies sit where the home country puts them ($12.50, 12,50 kr).
function moneyParts(v: number, currency: string, digits: number | undefined) {
  const parts = fmt(currency, digits).formatToParts(v);
  if (currency !== "EUR") return parts;
  const body = parts.filter((p) => p.type !== "currency" && !(p.type === "literal" && !p.value.trim()));
  return [...body, { type: "literal", value: "\u00a0" }, { type: "currency", value: "€" }] as Intl.NumberFormatPart[];
}

// The home currency and its sign, for inputs and axes ("€", "$", "CHF").
export const homeCurrency = () => getRegion().currency;
export function currencySign(currency = homeCurrency()) {
  if (currency === "EUR") return "€";
  return fmt(currency, 0).formatToParts(1).find((p) => p.type === "currency")?.value ?? currency;
}
// A number with the currency sign where it belongs: "12k €", "$12k".
export function withSign(n: string, currency = homeCurrency()) {
  if (currency === "EUR") return `${n}\u00a0€`;
  const parts = fmt(currency, 0).formatToParts(1);
  const sign = currencySign(currency);
  const before = parts.findIndex((p) => p.type === "currency") < parts.findIndex((p) => p.type === "integer");
  const gap = parts.some((p) => p.type === "literal" && !p.value.trim()) ? "\u00a0" : "";
  return before ? `${sign}${gap}${n}` : `${n}${gap}${sign}`;
}

// A real minus sign for amounts and percentages: the hyphen is hard to see and runs into the
// euro sign ("-€26.10").
const minus = (s: string) => s.replace("-", "\u2212");

// While amounts are hidden, every digit of a sum becomes a 9 (1.235,34 is 9.999,99) in the
// "Groschen Veil" font, which draws it out of focus: it looks like the figure behind frosted glass.
// The sign and the € stay where the language puts them.
const VEIL_CHAR: Record<string, string> = { ".": "\uE00A", ",": "\uE00B" };
export const veiled = (s: string) => s.replace(/[\d.,]/g, (c) => VEIL_CHAR[c] ?? String.fromCharCode(0xe000 + Number(c)));
export const nines = (s: string) => veiled(s.replace(/\d/g, "9"));
function format(v: number, currency: string, digits: number | undefined) {
  const parts = moneyParts(v, currency, digits);
  if (!amountsHidden()) return minus(parts.map((p) => p.value).join(""));
  return minus(parts.map((p) => (isAmount(p) ? nines(p.value) : p.value)).join(""));
}
// eur() and eur0() write an amount in the home currency (the euro unless Settings say otherwise).
export const eur = (v: number | null | undefined) => (v === null || v === undefined ? "–" : format(v, homeCurrency(), undefined));
export const eur0 = (v: number | null | undefined) => (v === null || v === undefined ? "–" : format(v, homeCurrency(), 0));
// An amount in its own currency: what the bank booked for money in another currency.
export const money = (v: number | null | undefined, currency: string) => (v === null || v === undefined ? "–" : format(v, currency, undefined));
// Fixed sums Groschen explains itself with (the 1,000 € tax allowance) say nothing about anyone's
// money, so they stay when amounts are hidden. Those are euros by law.
export const eurPublic = (v: number, digits?: number) => minus(moneyParts(v, "EUR", digits).map((p) => p.value).join(""));
// A sum in the home currency Groschen explains itself with ("from 300 €"): shown when amounts are hidden.
export const homePublic = (v: number, digits?: number) => minus(moneyParts(v, homeCurrency(), digits).map((p) => p.value).join(""));
export const num = (v: number, d = 2) => v.toLocaleString(numLocale(), { minimumFractionDigits: d, maximumFractionDigits: d });
// A plain number that tells how much: a fund's shares, a price on a chart's axis.
export const figure = (v: number, d = 2) => (amountsHidden() ? nines(num(v, d)) : num(v, d));

// Bank texts carry sums and account numbers of their own ("Rechnung 4711 über 49,99 EUR"): hidden
// the same way. A sum is a number with a decimal comma or next to EUR/€; dates ("05.10", "07.10.2026")
// and plain numbers stay.
// (No lookbehind: older Safari can't read it, and the whole app would fail to start.)
const SUM_IN_TEXT = /(^|[^\d.,])((?:\d{1,3}(?:\.\d{3})+|\d+),\d{2})(?![.,]?\d)|((?:EUR|USD|GBP|CHF|€|\$|£) ?)\d(?:[\d.,]*\d)?|\d(?:[\d.,]*\d)?(?= ?(?:EUR|USD|GBP|CHF|€|\$|£))/g;
const IBAN_IN_TEXT = /\b[A-Z]{2}\d{2}(?: ?[A-Z0-9]{4}){3,7}(?: ?[A-Z0-9]{1,3})?\b/g;
export function veil(text: string) {
  if (!amountsHidden()) return text;
  return text
    .replace(IBAN_IN_TEXT, (m) => `${m.slice(0, 2)}${nines(m.slice(2))}`)
    .replace(SUM_IN_TEXT, (m, before?: string, sum?: string, cur?: string) => (sum !== undefined ? `${before}${nines(sum)}` : `${cur ?? ""}${nines(m.slice((cur ?? "").length))}`));
}
export const int = (v: number) => v.toLocaleString(numLocale());
// German puts a space before the percent sign; a non-breaking one, so "15,4 %" never splits.
const pctSign = () => (getLang() === "de" ? "\u00a0%" : "%");
export const pct = (v: number | null | undefined, d = 1) =>
  v === null || v === undefined || !isFinite(v) ? "–" : minus(`${num(v * 100, d)}${pctSign()}`);
export const pctS = (v: number | null | undefined, d = 1) =>
  v === null || v === undefined || !isFinite(v) ? "–" : minus(`${v > 0 ? "+" : ""}${num(v * 100, d)}${pctSign()}`);

export const monthShort = (ym: string) =>
  new Date(`${ym.slice(0, 7)}-15T12:00:00`).toLocaleDateString(locale(), { month: "short" }).replace(".", "");
export const monthLabel = (ym: string) => `${monthShort(ym)} ${ym.slice(2, 4)}`;
export const monthLong = (ym: string) =>
  new Date(`${ym.slice(0, 7)}-15T12:00:00`).toLocaleDateString(locale(), { month: "long", year: "numeric" });

export function dayLabel(iso: string) {
  return new Date(`${iso}T12:00:00`).toLocaleDateString(locale(), { weekday: "short", day: "numeric", month: "short", year: "numeric" });
}
export function dateShort(iso: string | null | undefined) {
  if (!iso) return "–";
  return new Date(`${iso.slice(0, 10)}T12:00:00`).toLocaleDateString(locale(), { day: "numeric", month: "short", year: "numeric" });
}
// Day and month only, for lists already grouped by month.
export function dayMonth(iso: string) {
  return new Date(`${iso.slice(0, 10)}T12:00:00`).toLocaleDateString(locale(), { day: "numeric", month: "short" });
}
export function relTime(iso: string | null | undefined) {
  if (!iso) return t("time.never");
  const d = new Date(iso);
  const mins = Math.round((Date.now() - d.getTime()) / 60000);
  if (mins < 1) return t("time.justNow");
  if (mins < 60) return t("time.minAgo", { m: mins });
  const today = new Date();
  const time = d.toLocaleTimeString(locale(), { hour: "2-digit", minute: "2-digit" });
  if (d.toDateString() === today.toDateString()) return t("time.todayAt", { time });
  const y = new Date(today);
  y.setDate(today.getDate() - 1);
  if (d.toDateString() === y.toDateString()) return t("time.yesterdayAt", { time });
  return t("time.dateAt", { date: dateShort(iso), time });
}
// For times ahead, like the next scheduled sync.
export function whenNext(iso: string) {
  const d = new Date(iso);
  const mins = Math.round((d.getTime() - Date.now()) / 60000);
  if (mins < 1) return t("time.anyMoment");
  if (mins < 60) return t("time.inMin", { m: mins });
  const time = d.toLocaleTimeString(locale(), { hour: "2-digit", minute: "2-digit" });
  const today = new Date();
  if (d.toDateString() === today.toDateString()) return t("time.todayAtNext", { time });
  const tomorrow = new Date(today);
  tomorrow.setDate(today.getDate() + 1);
  if (d.toDateString() === tomorrow.toDateString()) return t("time.tomorrowAt", { time });
  return t("time.dateAtNext", { date: dateShort(iso), time });
}
export function bytes(n: number) {
  if (n < 1024 * 1024) return `${num(n / 1024, 0)} KB`;
  return `${num(n / 1024 / 1024, 1)} MB`;
}

export const colorVar = (name: string | null | undefined) => `var(--c-${name || "muted"})`;
export const initial = (s: string) => (s.replace(/[^A-Za-zÄÖÜäöü]/g, "").slice(0, 1) || "?").toUpperCase();

// Whole days from today to a date: 0 today, 1 tomorrow, -1 yesterday.
export function daysFrom(iso: string, today = new Date()) {
  const d = new Date(`${iso.slice(0, 10)}T12:00:00`);
  return Math.round((Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()) - Date.UTC(today.getFullYear(), today.getMonth(), today.getDate())) / 86400000);
}

// "today", "tomorrow", "in 3 days", "4 days ago" for dates close by, the date itself further out.
export function relDay(iso: string | null | undefined) {
  if (!iso) return "–";
  const n = daysFrom(iso);
  if (n === 0) return t("day.today");
  if (n === 1) return t("day.tomorrow");
  if (n === -1) return t("day.yesterday");
  if (n > 1 && n <= 30) return t("day.in", { n });
  if (n < -1 && n >= -30) return t("day.ago", { n: -n });
  return dateShort(iso);
}

// "monthly", "every 2 weeks", ...: how often a recurring payment comes.
export const intervalName = (interval: string) => t(`cal.kind.${interval}` as TKey);

// Banks name funds the long way ("Vanguard FTSE All-World U.ETF Reg.Shs USD Acc. oN"). The words
// before "ETF" carry the meaning; the rest is share class detail, kept for the fund's own page.
export function fundName(name: string) {
  const short = name
    .replace(/\s+(U\.?\s?ETF|UCITS\s+ETF|ETF)\b.*$/i, "")
    .replace(/^iShs\.?\s/i, "iShares ")
    .replace(/^Xtr\.?\s/i, "Xtrackers ")
    .trim();
  return short.length >= 6 ? short : name;
}
