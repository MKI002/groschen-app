import { useSyncExternalStore } from "react";

// Hidden amounts: one switch in the corner turns every figure that says how much money there is
// (balances, payments, values, a fund's shares) into a number seen through frosted glass, for a
// screen someone else can see. Charts keep their shapes; percentages, dates and names stay. Each
// browser keeps its own choice.
const STORE = "groschen.hidden";

function load() {
  try {
    return localStorage.getItem(STORE) === "1";
  } catch {
    return false;
  }
}

// What the figures show, and what the switch says: the switch moves at once, the figures follow
// once they have gone out of focus.
let hidden = load();
let wanted = hidden;
let timer = 0;
let blurring: Animation[] = [];
const listeners = new Set<() => void>();
const notify = () => listeners.forEach((fn) => fn());

// The stylesheet blurs amount fields while this is set.
const mark = () => document.documentElement.toggleAttribute("data-hidden", hidden);
if (typeof document !== "undefined") mark();

export const amountsHidden = () => hidden;
const hideWanted = () => wanted;

// The placeholder's digits, period and comma, drawn out of focus by the "Groschen Veil" font
// (U+E000-U+E00B). Where a font can't reach (a tooltip, a screen reader), `plain` says "•••".
const VEIL_TEST = /[-]/;
const VEIL_RUN = /[-](?:[-\s]*[-])?/g;
export const plain = (text: string) => (VEIL_TEST.test(text) ? text.replace(VEIL_RUN, "•••") : text);

function remember() {
  try {
    if (hidden) localStorage.setItem(STORE, "1");
    else localStorage.removeItem(STORE);
  } catch {
    /* storage blocked: the choice lasts until the page is reloaded */
  }
}

const still = () =>
  document.documentElement.dataset.motion === "off" || (typeof matchMedia !== "undefined" && matchMedia("(prefers-reduced-motion: reduce)").matches);

// The elements on screen that hold an amount and little else: a figure, a list amount, an axis
// label. A sentence with a sum in it just swaps the sum; blurring the whole line would flicker.
function figures(veiled: boolean): Element[] {
  const found = new Set<Element>();
  const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n = walk.nextNode(); n && found.size < 160; n = walk.nextNode()) {
    const text = n.nodeValue ?? "";
    if (text.length > 26 || !(veiled ? VEIL_TEST.test(text) : text.includes("€"))) continue;
    let el: Element | null = n.parentElement;
    if (!el || el.closest(".hide-btn")) continue;
    // An odometer as a whole (its digits roll in columns of their own); otherwise up to the
    // element that still holds only the figure.
    const odo = el.closest(".odo");
    if (odo) el = odo;
    else while (el.parentElement && el.parentElement !== document.body && (el.parentElement.textContent ?? "").trim().length <= 26) el = el.parentElement;
    const r = el.getBoundingClientRect();
    if (r.bottom < 0 || r.top > innerHeight || r.right < 0 || r.left > innerWidth || !r.width) continue;
    found.add(el);
  }
  return [...found];
}

const BLUR = "blur(.12em)";
function apply(on: boolean, settle: Element[]) {
  const blurred = blurring;
  blurring = [];
  hidden = on;
  mark();
  remember();
  watchAttributes();
  notify();
  // React has drawn the new figures by the next frame.
  requestAnimationFrame(() => {
    blurred.forEach((a) => a.cancel());
    if (!on) settle.forEach((el) => el.isConnected && el.animate([{ filter: BLUR, opacity: 0.6 }, { filter: "blur(0)", opacity: 1 }], { duration: 420, easing: "cubic-bezier(.2,.8,.2,1)" }));
    sanitize(document.body);
  });
}

export function hideAmounts(on: boolean) {
  if (on === wanted) return;
  wanted = on;
  window.clearTimeout(timer);
  blurring.forEach((a) => a.cancel());
  blurring = [];
  notify();
  if (on === hidden) return;
  if (typeof document === "undefined" || still()) return apply(on, []);
  if (!on) return apply(false, figures(true));
  // Hiding: the real figures go out of focus first, then the placeholder (already blurred) takes their place.
  blurring = figures(false).map((el) => el.animate([{ filter: "blur(0)" }, { filter: BLUR, opacity: 0.85 }], { duration: 220, easing: "cubic-bezier(.4,0,.6,1)", fill: "forwards" }));
  timer = window.setTimeout(() => apply(true, []), 200);
}

// Another tab of Groschen hiding or showing amounts does the same here.
if (typeof window !== "undefined")
  addEventListener("storage", (e) => {
    if (e.key !== STORE) return;
    window.clearTimeout(timer);
    blurring.forEach((a) => a.cancel());
    blurring = [];
    wanted = e.newValue === "1";
    if (wanted !== hidden) apply(wanted, []);
    else notify();
  });

// Tooltips and labels for screen readers are drawn by the system, not with the page's fonts:
// there the placeholder becomes "•••".
const ATTRS = ["title", "aria-label", "aria-valuetext", "alt", "placeholder"];
function sanitize(root: Element) {
  const one = (el: Element) => {
    for (const name of ATTRS) {
      const v = el.getAttribute(name);
      if (v && VEIL_TEST.test(v)) el.setAttribute(name, plain(v));
    }
    // An SVG <title> is a tooltip too.
    if (el.localName === "title" && el.parentElement)
      el.childNodes.forEach((c) => {
        if (c.nodeType === 3 && VEIL_TEST.test(c.nodeValue ?? "")) c.nodeValue = plain(c.nodeValue ?? "");
      });
  };
  one(root);
  root.querySelectorAll(`[${ATTRS.join("],[")}],title`).forEach(one);
}

let observer: MutationObserver | null = null;
function watchAttributes() {
  if (typeof MutationObserver === "undefined") return;
  if (!hidden) {
    observer?.disconnect();
    observer = null;
    return;
  }
  if (observer) return;
  observer = new MutationObserver((records) => {
    for (const r of records) {
      if (r.type === "attributes") sanitize(r.target as Element);
      else if (r.type === "childList") r.addedNodes.forEach((n) => n.nodeType === 1 && sanitize(n as Element));
      else if (r.target.parentElement?.localName === "title") sanitize(r.target.parentElement);
    }
  });
  observer.observe(document.body, { subtree: true, childList: true, characterData: true, attributes: true, attributeFilter: ATTRS });
}
if (typeof document !== "undefined" && hidden) {
  const start = () => {
    watchAttributes();
    sanitize(document.body);
  };
  if (document.body) start();
  else addEventListener("DOMContentLoaded", start);
}

// The font loads before it is first needed, so switching never shows an empty gap.
if (typeof document !== "undefined" && document.fonts)
  setTimeout(() => document.fonts.load('16px "Groschen Veil"', "").catch(() => {}), hidden ? 0 : 2500);

function subscribe(fn: () => void) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

// Components that show amounts in their own way (a number that counts up) call this to follow the switch.
export function useHidden() {
  return useSyncExternalStore(subscribe, amountsHidden, amountsHidden);
}

// The switch itself: it says what was asked for at once, while the figures still blur.
export function useHideWanted() {
  return useSyncExternalStore(subscribe, hideWanted, hideWanted);
}
