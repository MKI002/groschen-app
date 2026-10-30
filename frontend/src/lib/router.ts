import { useEffect, useState } from "react";
import { flushSync } from "react-dom";
import { reducedMotion } from "../components/Motion";

// A tiny router: the server answers every path with the app, the app picks the page.

// Swap the current address without a new history entry (old links, view switches).
export function redirect(path: string) {
  history.replaceState(null, "", path);
  window.dispatchEvent(new Event("groschen:navigate"));
}
type ViewTransitionDoc = Document & { startViewTransition?: (update: () => void) => unknown };

// Page changes morph from one page to the next where the browser supports View Transitions;
// elsewhere, and with reduced motion, the page simply swaps.
export function navigate(path: string) {
  const go = () => {
    if (path !== location.pathname + location.search) history.pushState(null, "", path);
    flushSync(() => window.dispatchEvent(new Event("groschen:navigate")));
    window.scrollTo(0, 0);
  };
  const doc = document as ViewTransitionDoc;
  if (doc.startViewTransition && !reducedMotion()) doc.startViewTransition(go);
  else go();
}

export function usePath(): string {
  const [path, setPath] = useState(location.pathname);
  useEffect(() => {
    const update = () => setPath(location.pathname);
    window.addEventListener("popstate", update);
    window.addEventListener("groschen:navigate", update);
    return () => {
      window.removeEventListener("popstate", update);
      window.removeEventListener("groschen:navigate", update);
    };
  }, []);
  return path;
}

// Where a click on a chart slice or a payee leads: every transaction in that group, category or with that payee.
// Uncategorized has no category id, so it always opens as a group.
export function drillPath(target: { group: string } | { merchant: string } | { category: number | null; income?: boolean }): string {
  if ("group" in target) return `/spending/group/${encodeURIComponent(target.group)}`;
  if ("merchant" in target) return `/spending/payee/${encodeURIComponent(target.merchant)}`;
  if (target.category !== null) return `/spending/category/${target.category}`;
  return `/spending/group/Uncategorized${target.income ? "?flow=income" : ""}`;
}

export function decodePart(part: string): string {
  try {
    return decodeURIComponent(part);
  } catch {
    return part; // a hand-typed address with a stray %
  }
}

export function useSearch(): URLSearchParams {
  const [search, setSearch] = useState(location.search);
  useEffect(() => {
    const update = () => setSearch(location.search);
    window.addEventListener("popstate", update);
    window.addEventListener("groschen:navigate", update);
    return () => {
      window.removeEventListener("popstate", update);
      window.removeEventListener("groschen:navigate", update);
    };
  }, []);
  return new URLSearchParams(search);
}
