import { setRegion } from "../i18n";

// The home country sets how numbers, amounts and dates are written (1.234,56 € in Germany,
// $1,234.56 in the US) and the home currency every total is shown in. The words stay in the
// chosen language: an English page in Germany writes "1 Nov 2026" and "4.271,93 €".
// The browser names countries and currencies in the user's language (Intl.DisplayNames).
// Keep this list in step with backend/groschen/regions.py.

export const COUNTRIES: Record<string, { currency: string; locale: string }> = {
  DE: { currency: "EUR", locale: "de-DE" },
  AT: { currency: "EUR", locale: "de-AT" },
  CH: { currency: "CHF", locale: "de-CH" },
  LI: { currency: "CHF", locale: "de-LI" },
  LU: { currency: "EUR", locale: "fr-LU" },
  BE: { currency: "EUR", locale: "nl-BE" },
  NL: { currency: "EUR", locale: "nl-NL" },
  FR: { currency: "EUR", locale: "fr-FR" },
  IT: { currency: "EUR", locale: "it-IT" },
  ES: { currency: "EUR", locale: "es-ES" },
  PT: { currency: "EUR", locale: "pt-PT" },
  IE: { currency: "EUR", locale: "en-IE" },
  FI: { currency: "EUR", locale: "fi-FI" },
  GR: { currency: "EUR", locale: "el-GR" },
  EE: { currency: "EUR", locale: "et-EE" },
  LV: { currency: "EUR", locale: "lv-LV" },
  LT: { currency: "EUR", locale: "lt-LT" },
  SK: { currency: "EUR", locale: "sk-SK" },
  SI: { currency: "EUR", locale: "sl-SI" },
  HR: { currency: "EUR", locale: "hr-HR" },
  BG: { currency: "EUR", locale: "bg-BG" },
  MT: { currency: "EUR", locale: "en-MT" },
  CY: { currency: "EUR", locale: "el-CY" },
  DK: { currency: "DKK", locale: "da-DK" },
  SE: { currency: "SEK", locale: "sv-SE" },
  NO: { currency: "NOK", locale: "nb-NO" },
  IS: { currency: "ISK", locale: "is-IS" },
  PL: { currency: "PLN", locale: "pl-PL" },
  CZ: { currency: "CZK", locale: "cs-CZ" },
  HU: { currency: "HUF", locale: "hu-HU" },
  RO: { currency: "RON", locale: "ro-RO" },
  GB: { currency: "GBP", locale: "en-GB" },
  TR: { currency: "TRY", locale: "tr-TR" },
  IL: { currency: "ILS", locale: "he-IL" },
  US: { currency: "USD", locale: "en-US" },
  CA: { currency: "CAD", locale: "en-CA" },
  MX: { currency: "MXN", locale: "es-MX" },
  BR: { currency: "BRL", locale: "pt-BR" },
  AU: { currency: "AUD", locale: "en-AU" },
  NZ: { currency: "NZD", locale: "en-NZ" },
  JP: { currency: "JPY", locale: "ja-JP" },
  KR: { currency: "KRW", locale: "ko-KR" },
  CN: { currency: "CNY", locale: "zh-CN" },
  HK: { currency: "HKD", locale: "zh-HK" },
  SG: { currency: "SGD", locale: "en-SG" },
  MY: { currency: "MYR", locale: "ms-MY" },
  TH: { currency: "THB", locale: "th-TH" },
  ID: { currency: "IDR", locale: "id-ID" },
  PH: { currency: "PHP", locale: "en-PH" },
  IN: { currency: "INR", locale: "en-IN" },
  ZA: { currency: "ZAR", locale: "en-ZA" },
};

// Every currency Groschen can convert (the ECB's daily reference rates, plus the euro).
export const CURRENCIES = [
  "EUR", "USD", "GBP", "CHF", "JPY", "CAD", "AUD", "NZD", "SEK", "NOK", "DKK", "ISK", "PLN", "CZK", "HUF",
  "RON", "TRY", "ILS", "MXN", "BRL", "KRW", "CNY", "HKD", "SGD", "MYR", "THB", "IDR", "PHP", "INR", "ZAR",
];

const names = new Map<string, Intl.DisplayNames | null>();
function displayNames(lang: string, type: "region" | "currency") {
  const key = `${lang}|${type}`;
  if (!names.has(key)) {
    try {
      names.set(key, new Intl.DisplayNames([lang], { type }));
    } catch {
      names.set(key, null);
    }
  }
  return names.get(key) ?? null;
}
export const countryName = (code: string, lang: string) => displayNames(lang, "region")?.of(code) ?? code;
export const currencyName = (code: string, lang: string) => displayNames(lang, "currency")?.of(code) ?? code;

// The countries, sorted by their name in the user's language.
export function countryList(lang: string): [string, string][] {
  return Object.keys(COUNTRIES)
    .map((c): [string, string] => [c, countryName(c, lang)])
    .sort((a, b) => a[1].localeCompare(b[1], lang));
}

// The country the browser says the user is in ("en-US", "de-AT"), if Groschen knows it.
export function guessCountry(): string {
  const langs = typeof navigator !== "undefined" ? navigator.languages ?? [navigator.language] : [];
  for (const l of langs) {
    const region = l.split("-")[1]?.toUpperCase();
    if (region && region in COUNTRIES) return region;
  }
  const first = (langs[0] ?? "").slice(0, 2).toLowerCase();
  return first === "en" ? "GB" : "DE";
}

// Use the home country and currency from the server (status, or a change in Settings).
export function applyRegion(r: { country?: string | null; currency?: string | null } | null | undefined) {
  setRegion(r?.country ?? "", r?.currency ?? "EUR", COUNTRIES[r?.country ?? ""]?.locale ?? null);
}

// The German tax allowance on investment income (Sparerpauschbetrag) only means something in Germany.
export const germanTax = (country: string | null | undefined) => !country || country === "DE";
// Automatic bank sync (FinTS) is German; elsewhere bank files are imported.
export const fintsCountry = (country: string | null | undefined) => !country || country === "DE";
