import { useSyncExternalStore } from "react";
import { de } from "./de";
import { en, type Key } from "./en";

// Every language Groschen ships. To add one, copy en.ts, translate the values
// and add it here. TypeScript refuses to build while a text is missing.
export const LANGUAGES = {
  de: { name: "Deutsch", locale: "de-DE", dict: de },
  en: { name: "English", locale: "en-GB", dict: en },
} satisfies Record<string, { name: string; locale: string; dict: Record<Key, string> }>;

export type Lang = keyof typeof LANGUAGES;
export type { Key };

const STORE = "groschen.lang";
export const isLang = (v: unknown): v is Lang => typeof v === "string" && v in LANGUAGES;

function detect(): Lang {
  try {
    const saved = localStorage.getItem(STORE);
    if (isLang(saved)) return saved;
  } catch {
    /* storage blocked: fall back to the browser language */
  }
  for (const l of typeof navigator !== "undefined" ? navigator.languages ?? [navigator.language] : []) {
    const short = l.slice(0, 2).toLowerCase();
    if (isLang(short)) return short;
  }
  return "de";
}

let current: Lang = detect();
const listeners = new Set<() => void>();
if (typeof document !== "undefined") document.documentElement.lang = current;

export const getLang = () => current;
export const locale = () => LANGUAGES[current].locale;

export function setLang(lang: Lang) {
  if (lang === current) return;
  current = lang;
  document.documentElement.lang = lang;
  try {
    localStorage.setItem(STORE, lang);
  } catch {
    /* ignore */
  }
  listeners.forEach((fn) => fn());
}

function subscribe(fn: () => void) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

// Plural texts come as "key.one" / "key.other"; t("key", { n }) picks the right one.
type PluralBase<K> = K extends `${infer B}.other` ? B : never;
export type TKey = Key | PluralBase<Key>;
type Vars = Record<string, string | number | null | undefined>;

export function t(key: TKey, vars?: Vars): string {
  const dict = LANGUAGES[current].dict as Record<string, string>;
  let text = dict[key];
  if (text === undefined && vars && typeof vars.n === "number") {
    const rule = new Intl.PluralRules(LANGUAGES[current].locale).select(vars.n);
    text = dict[`${key}.${rule}`] ?? dict[`${key}.other`];
  }
  if (text === undefined) text = (en as Record<string, string>)[key] ?? key;
  if (!vars) return text;
  return text.replace(/\{(\w+)\}/g, (m, name: string) => {
    const v = vars[name];
    if (v === undefined || v === null) return m;
    return typeof v === "number" && name === "n" ? v.toLocaleString(LANGUAGES[current].locale) : String(v);
  });
}

// Components call this so they re-render when the language changes.
export function useT() {
  useSyncExternalStore(subscribe, getLang, getLang);
  return t;
}

export function useLang(): Lang {
  return useSyncExternalStore(subscribe, getLang, getLang);
}

// Built-in category and group names are stored in English in the database
// (the categorizer looks them up by name). They are shown translated; names the
// user typed stay exactly as typed.
export function catName(name: string | null | undefined): string {
  if (!name) return name ?? "";
  const key = `cat.${name}` as Key;
  const dict = LANGUAGES[current].dict as Record<string, string>;
  return dict[key] ?? name;
}
