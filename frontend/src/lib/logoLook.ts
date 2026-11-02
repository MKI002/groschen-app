// Reads an uploaded picture so the crop dialog can be smart about it:
// - the colour along its border, to fill the space around it when zooming out,
// - where the logo itself sits, to frame it the way the built-in logos are framed,
// - whether it is a one-coloured logo on white or see-through, to offer it the other way round:
//   the logo in white on its own colour, like the built-in brand discs.

export type RGB = [number, number, number];
export type Look = {
  edge: RGB | null; // null: the border is see-through
  plain: boolean; // the border is one colour (or see-through), so it can be extended seamlessly
  box: { x: number; y: number; w: number; h: number } | null; // the logo, as fractions of the picture
  ink: RGB | null; // the logo's one colour, when it sits on white or see-through
  palette: RGB[]; // its main colours (the background left out), for background suggestions
};

const dist = (a: RGB, b: RGB) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
export const css = (c: RGB) => `rgb(${c[0]}, ${c[1]}, ${c[2]})`;
export const hex = (c: RGB) => `#${c.map((v) => v.toString(16).padStart(2, "0")).join("")}`;
export const fromHex = (h: string): RGB => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16) || 0) as RGB;
export const near = (a: RGB | null, b: RGB | null, by = 6) => (a && b ? dist(a, b) < by : a === b);

/** Relative luminance (0 black .. 1 white), as for the built-in logos. */
export function luminance(c: RGB): number {
  const [r, g, b] = c.map((v) => {
    const x = v / 255;
    return x <= 0.03928 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

/** White on dark colours, near-black on light ones (the built-in logos' rule). */
export const glyphOn = (c: RGB): RGB => (luminance(c) > 0.45 ? [17, 18, 20] : [255, 255, 255]);

/** Up to `n` clearly different main colours, most used first, the background left out. */
function paletteOf(d: Uint8ClampedArray, edge: RGB | null, n = 3): RGB[] {
  const buckets = new Map<number, number[]>(); // 4 bits per channel -> [count, r, g, b sums]
  let total = 0;
  for (let i = 0; i < d.length; i += 4) {
    if (d[i + 3] < 200 || (edge && dist([d[i], d[i + 1], d[i + 2]], edge) < 60)) continue;
    const key = ((d[i] >> 4) << 8) | ((d[i + 1] >> 4) << 4) | (d[i + 2] >> 4);
    const b = buckets.get(key) ?? [0, 0, 0, 0];
    b[0]++;
    b[1] += d[i];
    b[2] += d[i + 1];
    b[3] += d[i + 2];
    buckets.set(key, b);
    total++;
  }
  const out: RGB[] = [];
  for (const b of [...buckets.values()].sort((x, y) => y[0] - x[0])) {
    if (b[0] < total * 0.04 || out.length >= n) break;
    const c: RGB = [Math.round(b[1] / b[0]), Math.round(b[2] / b[0]), Math.round(b[3] / b[0])];
    if (out.every((o) => dist(o, c) > 90)) out.push(c);
  }
  return out;
}

function median(list: RGB[]): RGB {
  const mid = Math.floor(list.length / 2);
  return [0, 1, 2].map((ch) => list.map((p) => p[ch]).sort((a, b) => a - b)[mid]) as RGB;
}

/** Looks at a (small) copy of the picture: RGBA pixels, w × h. */
export function analyse(d: Uint8ClampedArray, w: number, h: number): Look {
  const px = (i: number): RGB => [d[i], d[i + 1], d[i + 2]];
  const band = Math.max(1, Math.round(Math.min(w, h) * 0.03));
  const border: number[] = [];
  for (let y = 0; y < h; y++)
    for (let x = 0; x < w; x++) if (x < band || y < band || x >= w - band || y >= h - band) border.push((y * w + x) * 4);

  const solid = border.filter((i) => d[i + 3] > 200);
  const clear = solid.length < border.length / 2;
  const edge = clear ? null : median(solid.map(px));
  const plain = edge
    ? solid.filter((i) => dist(px(i), edge) < 40).length >= border.length * 0.85
    : border.filter((i) => d[i + 3] < 40).length >= border.length * 0.85;
  const palette = paletteOf(d, edge);
  if (!plain) return { edge, plain, box: null, ink: null, palette };

  // The logo is whatever differs from the background; its "core" is what clearly does
  // (soft, half-blended edges left out), which tells whether it is one colour.
  let x0 = w;
  let y0 = h;
  let x1 = -1;
  let y1 = -1;
  const core: RGB[] = [];
  for (let y = 0; y < h; y++)
    for (let x = 0; x < w; x++) {
      const i = (y * w + x) * 4;
      const a = d[i + 3];
      const off = edge ? dist(px(i), edge) : 0;
      if (a <= 50 || (edge && off <= 48)) continue;
      if (x < x0) x0 = x;
      if (x > x1) x1 = x;
      if (y < y0) y0 = y;
      if (y > y1) y1 = y;
      if (a > 220 && (!edge || off > 100)) core.push(px(i));
    }
  if (x1 < 0) return { edge, plain, box: null, ink: null, palette };
  const box = { x: x0 / w, y: y0 / h, w: (x1 + 1 - x0) / w, h: (y1 + 1 - y0) / h };

  let ink: RGB | null = null;
  const onLight = !edge || luminance(edge) > 0.7;
  if (onLight && core.length >= w * h * 0.004) {
    const m = median(core);
    const same = core.filter((p) => dist(p, m) < 70).length / core.length;
    if (same >= 0.9 && luminance(m) < 0.85 && (!edge || dist(m, edge) > 120)) ink = m;
  }
  return { edge, plain, box, ink, palette };
}

/** The logo the other way round: its shape in `glyph` colour on see-through, pixels as `d`. */
export function turnAround(d: Uint8ClampedArray, edge: RGB | null, ink: RGB, glyph: RGB): Uint8ClampedArray<ArrayBuffer> {
  const out = new Uint8ClampedArray(d.length);
  const v: RGB = edge ? [ink[0] - edge[0], ink[1] - edge[1], ink[2] - edge[2]] : [0, 0, 0];
  const vv = v[0] * v[0] + v[1] * v[1] + v[2] * v[2] || 1;
  for (let i = 0; i < d.length; i += 4) {
    let cover = d[i + 3] / 255;
    if (edge) {
      // How far each pixel is on the way from the background to the logo's colour.
      const t = ((d[i] - edge[0]) * v[0] + (d[i + 1] - edge[1]) * v[1] + (d[i + 2] - edge[2]) * v[2]) / vv;
      cover *= Math.min(1, Math.max(0, (t - 0.1) / 0.8));
    }
    out[i] = glyph[0];
    out[i + 1] = glyph[1];
    out[i + 2] = glyph[2];
    out[i + 3] = Math.round(cover * 255);
  }
  return out;
}
