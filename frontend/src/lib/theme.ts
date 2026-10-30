// Groschen has one look: dark, formal, with a champagne accent (styles.css). Older versions let every
// browser pick a palette, a tint and light or dark; those choices are cleared once so nothing stale lingers.
const OLD_KEYS = ["groschen.palette", "groschen.tint", "groschen.theme"];

export function settleLook() {
  const root = document.documentElement;
  delete root.dataset.palette;
  delete root.dataset.tint;
  delete root.dataset.theme;
  try {
    for (const k of OLD_KEYS) localStorage.removeItem(k);
  } catch {
    /* storage blocked: nothing was stored either */
  }
}
