// Brand logos for merchants. Every logo ships with the app (src/data/logos, from Simple Icons,
// built by scripts/build_logos.py), so nothing is ever fetched from the internet. A merchant's
// own choice (an uploaded picture, another logo, or just the letter) is kept on the server.
//
// Matching follows the vendor list's rules (backend categorize/vendors.py): names are compared as
// whole words, "any" names count anywhere in the shown name, "lead" names only at its start, and
// "exact" names only when they are the whole name.

import { useSyncExternalStore } from "react";
import { api } from "./api";

type Index = {
  source: string;
  chunks: number;
  icons: Record<string, [title: string, hex: string]>;
  any: Record<string, string>;
  lead: Record<string, string>;
  exact: Record<string, string>;
};
export type Choice = { kind: "image" | "brand" | "letter"; slug?: string | null; v: string };
export type Logo =
  | { kind: "image"; src: string }
  | { kind: "brand"; slug: string; title: string; hex: string; ink: string; path: string | null; dark: boolean }
  | { kind: "letter" };

const loadIndex = () => import("../data/logos/index.json").then((m) => m.default as unknown as Index);
const CHUNKS = import.meta.glob<Record<string, string>>("../data/logos/[0-9][0-9].json", { import: "default" });

let index: Index | null = null;
let custom: Record<string, Choice> = {};
const paths: Record<string, string> = {};
const loading = new Set<number>();
const matched = new Map<string, string | null>();
const listeners = new Set<() => void>();
let version = 0;
let started = false;

function changed() {
  version++;
  for (const fn of listeners) fn();
}

function start() {
  if (started) return;
  started = true;
  loadIndex()
    .then((i) => {
      index = i;
      changed();
    })
    .catch(() => {
      /* without the index every merchant keeps its letter */
    });
  reloadChoices();
}

export function reloadChoices() {
  return api
    .get<Record<string, Choice>>("/logos")
    .then((c) => {
      custom = c && typeof c === "object" ? c : {};
      changed();
    })
    .catch(() => {
      /* the demo and older servers have no choices */
    });
}

/** Re-render when logos arrive. */
export function useLogos(): number {
  start();
  return useSyncExternalStore(
    (fn) => {
      listeners.add(fn);
      return () => listeners.delete(fn);
    },
    () => version,
  );
}

// djb2, the same hash build_logos.py uses to split the drawings into files.
function bucket(slug: string, n: number): number {
  let h = 5381;
  for (let i = 0; i < slug.length; i++) h = (h * 33 + slug.charCodeAt(i)) % 4294967296;
  return h % n;
}

function ensurePath(slug: string): string | null {
  if (slug in paths) return paths[slug];
  if (!index) return null;
  const n = bucket(slug, index.chunks);
  const load = CHUNKS[`../data/logos/${String(n).padStart(2, "0")}.json`];
  if (load && !loading.has(n)) {
    loading.add(n);
    load()
      .then((part) => {
        Object.assign(paths, part);
        changed();
      })
      .catch(() => loading.delete(n));
  }
  return null;
}

/** What a merchant's choice is stored under: case, accents, spaces and dots don't count (as the server's names.name_key). */
export function logoKey(name: string): string {
  return Array.from(name.replace(/ß/g, "ss").normalize("NFKD").toLowerCase())
    .filter((c) => /[\p{L}\p{N}]/u.test(c))
    .join("")
    .slice(0, 120);
}

const FOLD: Record<string, string> = { Ä: "AE", Ö: "OE", Ü: "UE", ß: "SS", Æ: "AE", Œ: "OE", Ø: "OE", Ł: "L", Đ: "D" };
/** Upper-cased words the way the vendor list spells them (Ä -> AE, accents dropped). */
export function words(text: string): string[] {
  const up = text
    .replace(/['’`]/g, "")
    .toUpperCase()
    .replace(/[ÄÖÜßÆŒØŁĐ]/g, (c) => FOLD[c])
    .normalize("NFKD")
    .replace(/\p{M}/gu, "");
  return up.match(/[A-Z0-9]+|[&+]/g) ?? [];
}

// Words in front of a name that only say how it was paid (vendors.py _LEAD_SKIP).
const LEAD_SKIP = new Set(
  "VISA MASTERCARD MC MAESTRO GIROCARD DEBITK DEBITKARTE KARTENZAHLUNG KARTENUMSATZ POS CRV ACH CHECKCARD PURCHASE DEBIT CARD RECURRING PAYMENT PAYPAL PP SQ SQU SUMUP SUM UP ZETTLE IZ IZETTLE SP SPC STRIPE PADDLE CB CARTE PAIEMENT COMPRA PAGO PAGAMENTO BETALING KORTBETALNING KAUF NR".split(" "),
);
// Company forms and web endings that may follow a whole name ("Netflix.com", "Spotify AB").
const TRAIL = new Set("GMBH AG KG SE CO INC LTD LLC LIMITED CORP PLC BV NV SA SAS SARL SRL SPA AB AS ASA OY APS COM DE EU IO NET ORG APP".split(" "));
const MAX_WORDS = 6;

function longest(w: string[], table: Record<string, string>, startOnly: boolean): [number, string] | null {
  let best: [number, string] | null = null;
  for (let i = 0; i < (startOnly ? Math.min(1, w.length) : w.length); i++) {
    for (let size = Math.min(MAX_WORDS, w.length - i); size > 0; size--) {
      const hit = table[w.slice(i, i + size).join(" ")];
      if (hit) {
        if (!best || size > best[0]) best = [size, hit];
        break;
      }
    }
  }
  return best;
}

/** The bundled logo for a shown merchant name, or null. */
export function autoSlug(name: string): string | null {
  if (!index) return null;
  const cached = matched.get(name);
  if (cached !== undefined) return cached;
  const all = words(name);
  let lw = all;
  while (lw.length && (LEAD_SKIP.has(lw[0]) || /^\d+$/.test(lw[0]))) lw = lw.slice(1);
  let whole = lw;
  while (whole.length > 1 && TRAIL.has(whole[whole.length - 1])) whole = whole.slice(0, -1);
  let slug: string | null = index.exact[whole.join(" ")] ?? null;
  if (!slug) {
    const anywhere = longest(all, index.any, false);
    const lead = longest(lw, index.lead, true) ?? longest(lw, index.any, true);
    const best = lead && (!anywhere || lead[0] >= anywhere[0]) ? lead : anywhere;
    slug = best ? best[1] : null;
  }
  matched.set(name, slug);
  return slug;
}

function luminance(hex: string): number {
  const [r, g, b] = [0, 2, 4].map((i) => {
    const c = parseInt(hex.slice(i, i + 2), 16) / 255;
    return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

export type Brand = Extract<Logo, { kind: "brand" }>;

export function brand(slug: string): Brand | null {
  const icon = index?.icons[slug];
  if (!icon) return null;
  const [title, hex] = icon;
  const lum = luminance(hex);
  return { kind: "brand", slug, title, hex: `#${hex}`, ink: lum > 0.45 ? "#111214" : "#FFFFFF", path: ensurePath(slug), dark: lum < 0.03 };
}

/** What a merchant shows: the user's choice first, then the bundled logo, else its letter. */
export function logoFor(name: string): Logo {
  const key = logoKey(name);
  const own = key ? custom[key] : undefined;
  if (own?.kind === "image") return { kind: "image", src: `/api/logos/${encodeURIComponent(key)}/image?v=${encodeURIComponent(own.v)}` };
  if (own?.kind === "letter") return { kind: "letter" };
  const slug = own?.kind === "brand" && own.slug ? own.slug : autoSlug(name);
  return (slug && brand(slug)) || { kind: "letter" };
}

export const hasChoice = (name: string) => logoKey(name) in custom;

/** Bundled logos whose name contains the search, best first. */
export function searchBrands(q: string, limit = 40): string[] {
  if (!index) return [];
  const needle = q.trim().toLowerCase();
  if (!needle) return [];
  const starts: string[] = [];
  const contains: string[] = [];
  for (const [slug, [title]] of Object.entries(index.icons)) {
    const t = title.toLowerCase();
    if (t.startsWith(needle)) starts.push(slug);
    else if (t.includes(needle)) contains.push(slug);
    if (starts.length >= limit) break;
  }
  return [...starts, ...contains].slice(0, limit);
}

export const brandCount = () => (index ? Object.keys(index.icons).length : 0);

export async function chooseLogo(name: string, choice: { kind: "brand"; slug: string } | { kind: "letter" } | null) {
  const key = logoKey(name);
  if (choice) await api.put(`/logos/${encodeURIComponent(key)}`, choice);
  else await api.del(`/logos/${encodeURIComponent(key)}`);
  await reloadChoices();
}

/** Stores a picture (already cut to a square by the upload dialog) for the merchant. */
export async function uploadLogoBlob(name: string, blob: Blob) {
  const form = new FormData();
  form.append("file", blob, "logo.png");
  await api.upload(`/logos/${encodeURIComponent(logoKey(name))}/image`, form);
  await reloadChoices();
}
