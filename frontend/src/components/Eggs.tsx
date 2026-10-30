// Easter eggs. Small, silly and offline: nothing here loads anything or touches your data.
// They can be switched off under Settings, Account. Which ones you found is kept
// in this browser only, like the animation setting.

import { useEffect, useState } from "react";
import { t } from "../i18n";
import { reducedMotion } from "./Motion";
import { useToast } from "./UI";

// Names and hints live in the language files as egg.<id>.name and egg.<id>.hint.
export const EGGS = [{ id: "penny" }, { id: "dagobert" }, { id: "meaning" }, { id: "lambo" }, { id: "owl" }, { id: "season" }] as const;
export type EggId = (typeof EGGS)[number]["id"];
export const eggName = (id: EggId) => t(`egg.${id}.name`);
export const eggHint = (id: EggId) => t(`egg.${id}.hint`);

const ON_KEY = "groschen.eggs";
const FOUND_KEY = "groschen.eggs.found";

export function eggsOn(): boolean {
  try {
    return localStorage.getItem(ON_KEY) !== "off";
  } catch {
    return true;
  }
}

export function setEggsOn(on: boolean) {
  try {
    if (on) localStorage.removeItem(ON_KEY);
    else localStorage.setItem(ON_KEY, "off");
  } catch {
    /* storage blocked: stays on for this visit */
  }
}

export function foundEggs(): EggId[] {
  try {
    const list = JSON.parse(localStorage.getItem(FOUND_KEY) || "[]");
    return Array.isArray(list) ? list.filter((id) => EGGS.some((e) => e.id === id)) : [];
  } catch {
    return [];
  }
}

// Returns true the first time an egg is found.
export function markFound(id: EggId): boolean {
  const found = foundEggs();
  if (found.includes(id)) return false;
  try {
    localStorage.setItem(FOUND_KEY, JSON.stringify([...found, id]));
  } catch {
    /* ignore */
  }
  window.dispatchEvent(new Event("groschen:egg"));
  return true;
}

export function resetFound() {
  try {
    localStorage.removeItem(FOUND_KEY);
  } catch {
    /* ignore */
  }
  window.dispatchEvent(new Event("groschen:egg"));
}

export function useFoundEggs() {
  const [found, setFound] = useState(foundEggs);
  useEffect(() => {
    const on = () => setFound(foundEggs());
    window.addEventListener("groschen:egg", on);
    return () => window.removeEventListener("groschen:egg", on);
  }, []);
  return found;
}

// "Easter egg 3 of 6", counted before the new one is marked found.
const nth = () => t("egg.nth", { n: foundEggs().length + 1, total: EGGS.length });

// Tell the egg layer to play something. Everything goes through one event so any page can
// trigger an egg without knowing how it's drawn.
type Play = "penny" | "rain" | "car" | "gold";
function play(what: Play) {
  window.dispatchEvent(new CustomEvent("groschen:eggplay", { detail: what }));
}

export function rain(count = 60) {
  if (reducedMotion()) return;
  window.dispatchEvent(new CustomEvent("groschen:coins", { detail: { rain: true, count } }));
}

// --- the eggs ---------------------------------------------------------------------------

// Five quick clicks on the logo, or on a page title on the phone where the sidebar is hidden.
let logoClicks: number[] = [];
function logoClicked(toast: (m: string) => void) {
  if (!eggsOn()) return;
  const now = Date.now();
  logoClicks = [...logoClicks.filter((c) => now - c < 2500), now];
  if (logoClicks.length < 5) return;
  logoClicks = [];
  const extra = foundEggs().includes("penny") ? "" : ` (${nth()})`;
  play("penny");
  window.setTimeout(() => toast(t("egg.penny.toast", { extra })), 900);
  markFound("penny");
}

function dagobert(toast: (m: string) => void) {
  const extra = foundEggs().includes("dagobert") ? "" : ` (${nth()})`;
  rain(70);
  play("gold");
  toast(t("egg.dagobert.toast", { extra }));
  markFound("dagobert");
}

// Searching the bookings for the big questions (Transactions). Each one plays once per search.
let searched: EggId | null = null;
export function searchEgg(query: string, toast: (m: string) => void) {
  const q = query.toLowerCase();
  const id: EggId | null = !eggsOn()
    ? null
    : /sinn des lebens|meaning of life|answer to (life|everything)/.test(q)
      ? "meaning"
      : /lambo|lamborghini|bugatti|traumauto|dream car/.test(q)
        ? "lambo"
        : null;
  if (id === searched) return;
  searched = id;
  if (!id) return;
  const extra = foundEggs().includes(id) ? "" : ` (${nth()})`;
  markFound(id);
  if (id === "lambo") play("car");
  else rain(42);
  toast(t(`egg.${id}.toast`, { extra }));
}

// Splash screen extras, depending on the time of year and day.
export function splashEgg(now = new Date()): { tagline?: string; kind?: "snow" | "stars" | "newyear" } {
  if (!eggsOn()) return {};
  const m = now.getMonth() + 1;
  const d = now.getDate();
  const h = now.getHours();
  if ((m === 12 && d === 31) || (m === 1 && d === 1)) {
    markFound("season");
    return { tagline: t("egg.newyear"), kind: "newyear" };
  }
  if (h < 5) {
    markFound("owl");
    return { tagline: t("egg.owl"), kind: "stars" };
  }
  if (m === 12) {
    markFound("season");
    return { tagline: t("egg.snow"), kind: "snow" };
  }
  if (m === 4 && d === 1) {
    markFound("season");
    return { tagline: t("egg.april") };
  }
  return {};
}

// --- the layer that draws them ---------------------------------------------------------

const KONAMI = ["arrowup", "arrowup", "arrowdown", "arrowdown", "arrowleft", "arrowright", "arrowleft", "arrowright", "b", "a"];
const WORD = "dagobert";

export function EggLayer() {
  const toast = useToast();
  const [shown, setShown] = useState<{ penny: number; car: number }>({ penny: 0, car: 0 });

  useEffect(() => {
    let keys: string[] = [];
    let typed = "";
    const onKey = (e: KeyboardEvent) => {
      const el = e.target as HTMLElement | null;
      if (el && (el.isContentEditable || ["INPUT", "TEXTAREA", "SELECT"].includes(el.tagName))) return;
      if (!eggsOn() || e.metaKey || e.ctrlKey || e.altKey) return;
      const k = e.key.toLowerCase();
      keys = [...keys, k].slice(-KONAMI.length);
      typed = (typed + (k.length === 1 ? k : " ")).slice(-WORD.length);
      if (keys.join() === KONAMI.join() || typed === WORD) {
        keys = [];
        typed = "";
        dagobert(toast);
      }
    };
    const onPlay = (e: Event) => {
      const what = (e as CustomEvent<Play>).detail;
      if (what === "gold") {
        document.documentElement.classList.add("egg-gold");
        window.setTimeout(() => document.documentElement.classList.remove("egg-gold"), 6000);
      }
      if (reducedMotion()) return;
      if (what === "penny" || what === "car") {
        setShown((s) => ({ ...s, [what]: Date.now() }));
        window.setTimeout(() => setShown((s) => ({ ...s, [what]: 0 })), what === "penny" ? 2400 : 2600);
      }
      if (what === "penny") {
        const logo = document.querySelector(".brand svg");
        logo?.classList.add("egg-flip");
        window.setTimeout(() => logo?.classList.remove("egg-flip"), 1000);
      }
    };
    const onClick = (e: MouseEvent) => {
      if ((e.target as Element | null)?.closest?.(".brand, .ph h1")) logoClicked(toast);
    };
    window.addEventListener("keydown", onKey);
    window.addEventListener("click", onClick);
    window.addEventListener("groschen:eggplay", onPlay);
    return () => {
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("click", onClick);
      window.removeEventListener("groschen:eggplay", onPlay);
    };
  }, [toast]);

  if (!shown.penny && !shown.car) return null;
  return (
    <div className="egg-layer" aria-hidden="true">
      {shown.penny > 0 && (
        <div className="egg-penny" key={shown.penny}>
          <span>10</span>
        </div>
      )}
      {shown.car > 0 && (
        <div className="egg-car" key={shown.car}>
          <span>🏎️</span>
          <i />
        </div>
      )}
    </div>
  );
}
