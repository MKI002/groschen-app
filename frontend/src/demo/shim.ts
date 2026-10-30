// The web demo: Groschen without a server. Every request the app makes is answered from
// answers recorded once from the built-in demo data (an invented person, see backend
// groschen/demo.py). Changes are accepted but not kept, and nothing leaves the browser.

import { t } from "../i18n";

// The day the answers were recorded. The demo's clock stands on it, so "today", the payday
// countdown and the chosen period all match the recorded data.
const RECORDED = new Date("2026-10-30T12:00:00Z").getTime();

type Answers = Record<string, unknown>;

function freezeClock() {
  const Real = Date;
  const offset = RECORDED - Real.now();
  class DemoDate extends Real {
    constructor(...args: unknown[]) {
      if (args.length === 0) super(Real.now() + offset);
      else super(...(args as [string]));
    }
    static now() {
      return Real.now() + offset;
    }
  }
  window.Date = DemoDate as DateConstructor;
}

// The recorded answer for a request: the exact one, else the same page with other options,
// else the same page in the other language.
function lookup(answers: Answers, lang: string, path: string): unknown {
  const exact = `${lang} ${path}`;
  if (exact in answers) return answers[exact];
  const bare = path.split("?")[0];
  const wanted = new URLSearchParams(path.split("?")[1] ?? "");
  let best: string | null = null;
  let bestScore = -1;
  for (const key of Object.keys(answers)) {
    const [l, p] = key.split(" ", 2);
    if (p.split("?")[0] !== bare) continue;
    const have = new URLSearchParams(p.split("?")[1] ?? "");
    let score = l === lang ? 100 : 0;
    for (const [k, v] of wanted) if (have.get(k) === v) score += 2;
    for (const k of wanted.keys()) if (have.has(k)) score += 1;
    if (score > bestScore) [best, bestScore] = [key, score];
  }
  return best ? answers[best] : undefined;
}

const job = { id: "demo", kind: "sync", state: "done", message: "", steps: [], result: {}, error: null };

function answer(answers: Answers, method: string, path: string, lang: string): [number, unknown] {
  if (method === "GET") {
    if (path.startsWith("/jobs/")) return [200, job];
    if (path === "/health") return [200, { ok: true, version: "demo" }];
    const found = lookup(answers, lang, path);
    return found === undefined ? [404, { detail: "Not part of the demo." }] : [200, found];
  }
  // Writes: accepted, never kept. Jobs finish at once.
  if (path.startsWith("/sync") || path.startsWith("/setup/finish") || path.startsWith("/categorize/rerun")) return [200, job];
  return [200, { ok: true }];
}

function banner() {
  const el = document.createElement("a");
  el.href = "https://github.com/MKI002/groschen-app";
  el.target = "_blank";
  el.rel = "noopener";
  el.textContent = t("demo.banner");
  el.setAttribute(
    "style",
    "position:fixed;left:50%;bottom:14px;transform:translateX(-50%);z-index:9999;padding:7px 14px;border-radius:999px;" +
      "background:rgba(20,21,24,.92);border:1px solid rgba(255,255,255,.12);color:#d9b45a;font:500 12.5px Figtree Variable,sans-serif;" +
      "text-decoration:none;white-space:nowrap;box-shadow:0 6px 24px rgba(0,0,0,.4)",
  );
  document.body.appendChild(el);
}

export async function install() {
  const answers = (await import("./data.json")).default as Answers;
  freezeClock();
  const realFetch = window.fetch.bind(window);
  window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = new URL(typeof input === "string" ? input : input instanceof URL ? input.href : input.url, location.href);
    if (url.origin !== location.origin || !url.pathname.includes("/api/")) return realFetch(input, init);
    const path = url.pathname.slice(url.pathname.indexOf("/api/") + 4) + url.search;
    const headers = new Headers(init?.headers);
    const lang = headers.get("X-Groschen-Lang") ?? "en";
    const [status, body] = answer(answers, (init?.method ?? "GET").toUpperCase(), path, lang);
    await new Promise((r) => setTimeout(r, 60));
    return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
  };
  banner();
}
