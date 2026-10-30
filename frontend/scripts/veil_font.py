"""Builds the font Groschen writes hidden amounts in: digits seen through frosted glass.

While amounts are hidden, the app writes one fixed placeholder number in Private Use Area code
points (U+E000-U+E009 the digits 0-9, U+E00A the period, U+E00B the comma). This font draws each
of them as Figtree's tabular digit out of focus: the glyph is rasterised, blurred with a Gaussian
and cut into level sets, which are stacked as colour layers of rising opacity (COLR).

veil-c1.woff2 (COLRv1) paints the layers in the text's own colour, so a green figure blurs green.
veil-c0.woff2 (COLRv0) is the fallback for browsers without COLRv1 (Safari): the same layers in a
fixed light ink. The stylesheet picks one with @font-face src tech().

Run from the repository root:  python frontend/scripts/veil_font.py
Only needed to rebuild the fonts; needs fonttools, brotli, freetype-py, numpy, scipy, scikit-image.
Derived from Figtree (Copyright 2022 The Figtree Project Authors), SIL Open Font License 1.1,
and licensed the same way.
"""

from pathlib import Path

import numpy as np
from fontTools.colorLib.builder import buildCOLR, buildCPAL
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.freetypePen import FreeTypePen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables as ot
from fontTools.varLib.instancer import instantiateVariableFont
from scipy.ndimage import gaussian_filter
from skimage.measure import approximate_polygon, find_contours

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "node_modules/@fontsource-variable/figtree/files/figtree-latin-wght-normal.woff2"
OUT = ROOT / "src/fonts"

WEIGHT = 620  # between the body text and the bold figures
SIGMA = 0.12  # blur, in em: the digits can't be read at any size, yet still look like digits
LEVELS = 32  # opacity steps; more is smoother and larger
SCALE = 0.5  # raster pixels per font unit
TOLERANCE = 0.6  # pixels a simplified outline may stray from the exact level line
INK = (0xEC, 0xED, 0xEF)  # --ink, for the COLRv0 fallback

CHARS = {**{str(d): (0xE000 + d, f"{n}.tf") for d, n in enumerate("zero one two three four five six seven eight nine".split())}, ".": (0xE00A, "period"), ",": (0xE00B, "comma")}
NAMES = {".": "period", ",": "comma", **{str(d): f"d{d}" for d in range(10)}}


def raster(glyphs, name, adv, margin):
    """Coverage of one glyph (rows top to bottom) and where its box sits in font units."""
    bottom, top = -250 - margin, 950 + margin
    left, right = -margin, adv + margin
    w, h = int((right - left) * SCALE), int((top - bottom) * SCALE)
    pen = FreeTypePen(glyphs)
    glyphs[name].draw(pen)
    cover = pen.array(width=w, height=h, transform=(SCALE, 0, 0, SCALE, -left * SCALE, -bottom * SCALE))
    return cover, (left, bottom, h)


def outlines(intensity, level, box):
    """The level line of a blurred glyph as TrueType contours (lists of points)."""
    left, bottom, h = box
    out = []
    for c in find_contours(intensity, level, fully_connected="high", positive_orientation="high"):
        c = approximate_polygon(c, tolerance=TOLERANCE)[:-1]
        if len(c) < 3:
            continue
        pts = [(round((col + 0.5) / SCALE + left), round((h - row - 0.5) / SCALE + bottom)) for row, col in c]
        area = 0.5 * sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))
        if abs(area) < 40:  # specks
            continue
        out.append(pts)
    return out


def glyph_of(contours):
    pen = TTGlyphPen(None)
    for pts in contours:
        pen.moveTo(pts[0])
        for p in pts[1:]:
            pen.lineTo(p)
        pen.closePath()
    return pen.glyph()


def main():
    figtree = instantiateVariableFont(TTFont(SOURCE), {"wght": WEIGHT})
    glyphs, hmtx = figtree.getGlyphSet(), figtree["hmtx"]
    sigma_units = SIGMA * 1000
    margin = int(sigma_units * 3.2)

    blurred = {}
    for ch, (_, src) in CHARS.items():
        adv = hmtx[src][0]
        cover, box = raster(glyphs, src, adv, margin)
        blurred[ch] = (gaussian_filter(cover, sigma_units * SCALE, mode="constant"), box, adv)

    # One set of thresholds for every glyph, so all of them share the same opacity steps.
    peak = max(i.max() for i, _, _ in blurred.values())
    thresholds = [0.012 + (peak * 0.97 - 0.012) * k / LEVELS for k in range(LEVELS)]
    every = np.concatenate([i.ravel() for i, _, _ in blurred.values()])
    bands = []
    for k, t in enumerate(thresholds):
        hi = thresholds[k + 1] if k + 1 < LEVELS else np.inf
        inside = every[(every >= t) & (every < hi)]
        bands.append(float(inside.mean()) if inside.size else t)
    # Stacked layers: each one's own opacity, so that the pile reaches the band's mean intensity.
    alphas, below = [], 0.0
    for a in bands:
        a = min(a * 1.08, 0.97)
        alphas.append(1 - (1 - a) / (1 - below))
        below = a

    order = [".notdef"]
    glyf, metrics, cmap = {".notdef": TTGlyphPen(None).glyph()}, {".notdef": (600, 0)}, {}
    v1, v0, clips = {}, {}, {}
    for ch, (intensity, box, adv) in blurred.items():
        base = f"veil.{NAMES[ch]}"
        layers = []
        for k, t in enumerate(thresholds):
            contours = outlines(intensity, t, box)
            if not contours:
                continue
            name = f"{base}.{k:02d}"
            glyf[name] = glyph_of(contours)
            metrics[name] = (adv, 0)
            layers.append((name, k))
        # Without colour support the base glyph shows: the middle level, as one soft-edged shape.
        glyf[base] = glyf[layers[len(layers) // 3][0]]
        metrics[base] = (adv, 0)
        order += [base] + [n for n, _ in layers]
        cmap[CHARS[ch][0]] = base
        v1[base] = {
            "Format": ot.PaintFormat.PaintColrLayers,
            "Layers": [{"Format": ot.PaintFormat.PaintGlyph, "Paint": {"Format": ot.PaintFormat.PaintSolid, "PaletteIndex": 0xFFFF, "Alpha": round(alphas[k], 4)}, "Glyph": n} for n, k in layers],
        }
        v0[base] = [(n, k) for n, k in layers]
        outer = glyf[layers[0][0]]
        outer.recalcBounds(glyf)
        clips[base] = (outer.xMin, outer.yMin, outer.xMax, outer.yMax)

    palette = [[(INK[0] / 255, INK[1] / 255, INK[2] / 255, a) for a in alphas]]
    for flavor, colr in (("c1", buildCOLR(v1, version=1, clipBoxes=clips)), ("c0", buildCOLR(v0, version=0))):
        fb = FontBuilder(1000, isTTF=True)
        fb.setupGlyphOrder(order)
        fb.setupCharacterMap(cmap)
        fb.setupGlyf(glyf)
        lsb = {n: (adv, getattr(fb.font["glyf"][n], "xMin", 0)) for n, (adv, _) in metrics.items()}
        fb.setupHorizontalMetrics(lsb)
        fb.setupHorizontalHeader(ascent=950, descent=-250)
        fb.setupNameTable(
            {
                "copyright": "Copyright 2022 The Figtree Project Authors (https://github.com/erikdkennedy/figtree). Blurred digits for Groschen.",
                "familyName": "Groschen Veil",
                "styleName": "Regular",
                "uniqueFontIdentifier": f"GroschenVeil-{flavor}",
                "fullName": "Groschen Veil",
                "psName": "GroschenVeil-Regular",
                "licenseDescription": "This Font Software is licensed under the SIL Open Font License, Version 1.1.",
                "licenseInfoURL": "https://openfontlicense.org",
            }
        )
        fb.setupOS2(version=4, sTypoAscender=950, sTypoDescender=-250, sTypoLineGap=0, usWinAscent=1250, usWinDescent=550, fsSelection=0x40 | 0x80, achVendID="GRSN")
        fb.setupPost(keepGlyphNames=False)
        fb.font["COLR"] = colr
        fb.font["CPAL"] = buildCPAL(palette)
        fb.font.flavor = "woff2"
        path = OUT / f"veil-{flavor}.woff2"
        fb.font.save(path)
        print(path.relative_to(ROOT.parent), path.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
