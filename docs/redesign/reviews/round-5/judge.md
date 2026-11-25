# Judge 5: blind comparison

Method: I viewed all 14 pictures, compared them pixel by pixel and zoomed into the charts. **Pairs 05, 06 and 07 are byte-identical** (same MD5), so A and B match on every line. In pairs 01–04 the only change is the bottom calendar or month chart. Everything above it matches pixel for pixel. A/B orientation flips between pairs: the "wrapped full-year" version is **B in pair 01, A in pair 02, B in pair 03, B in pair 04**.

## Pair 01: Spending, phone, DE

The only difference is the heatmap "Dein Jahr in Tagen". A shows one strip that is cut off at Jun at the right card edge, with no visible scroll cue. B wraps the year into two blocks (Jan–Jun, then Jul–Dez) and draws future days (Nov/Dez) as dashed outlines.

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | B | Heading says "Dein Jahr", and only B shows the whole year |
| hierarchy | same | Card order and headings are the same |
| task efficiency | B | In B, Jul–Okt can be seen without a hidden horizontal scroll |
| data presentation | B | In A the stats "185 Tage ohne Ausgaben" / "2. Feb." cover days you cannot see. B shows them all, and its outlined future days separate "no data yet" from "no spending" |
| navigation and naming | same | The year stepper and labels are the same |
| consistency | B | Matches the desktop heatmap, which shows Jan–Dez |
| phone experience | B | No clipped content at 390 px. The page gets about 100 px taller, which is acceptable |
| accessibility | B | Nothing is hidden behind a horizontal swipe that has no cue |
| visual craft | B | A's grid ends abruptly mid-column at the card edge. B's two blocks are tidy |

**Winner: B.** A is better nowhere important (it is only about 100 px shorter).
**Most recent months:** **B**. A shows nothing after Jun on first view.

## Pair 02: Spending, phone, EN

This is the same change as pair 01 with the sides swapped: **A** is wrapped (Jan–Jun / Jul–Dec) and B is clipped at Jun.

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | A | "Your year in days" shows the whole year |
| hierarchy | same | Same as the other version |
| task efficiency | A | Jul–Oct can be read with no scrolling |
| data presentation | A | All days behind the summary stats are visible, and future days are outlined |
| navigation and naming | same | Same labels. "Sept" is an abbreviation style shared with the desktop |
| consistency | A | Matches the desktop full-year heatmap |
| phone experience | A | No clipped grid |
| accessibility | A | No hidden overflow |
| visual craft | A | Clean two-block layout, where B has a hard cut at the edge |

**Winner: A.** B is better nowhere important.
**Most recent months:** **A**.

## Pair 03: Investment analysis, phone, DE

The only difference is the "Monatsrenditen" chart. A has one row of tiles, Jan–Jun, with month labels above. Jul–Okt are cut off, even though the text says "5 von 10 Monaten im Plus". B uses a 6×2 grid with the month name inside each tile, Jul–Okt filled in, and Nov/Dez as dashed empty tiles.

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | B | The chart covers the stated range "Jan – Okt 2026" |
| hierarchy | same | Card order is the same |
| task efficiency | B | All 10 months fit in one glance |
| data presentation | B | In A, "5 von 10 im Plus" contradicts the 6 tiles shown, and 2 of the 5 positive months are visible. B shows all 10, so the count can be checked |
| navigation and naming | same | Same labels and outline legend |
| consistency | B | Matches the desktop row Jan–Dez and the Rückgang chart, which runs to Sep/Okt above it |
| phone experience | B | Nothing is clipped at 390 px |
| accessibility | A (slight) | A's month labels are grey on the dark background. In B, the small labels inside light-green tiles (Feb, Jul) have weak contrast |
| visual craft | B | The grid is balanced and the dashed future tiles are a nice touch |

**Winner: B.** The loser is better in one minor place: the month-label contrast on the light tiles. That is worth fixing in B, but it does not outweigh four missing months.
**Most recent months:** **B** (+7,9 / +5,3 / +1,3 / −0,9 visible). In A they cannot be seen.

## Pair 04: Investment analysis, phone, EN

This is the same change as pair 03, with the same orientation (A clipped at Jun, B a 6×2 grid with Jul–Oct).

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | B | The chart covers "Jan – Oct 2026" |
| hierarchy | same | Same as the other version |
| task efficiency | B | All months are visible at once |
| data presentation | B | "5 of 10 months up" matches the visible tiles only in B |
| navigation and naming | same | Same labels |
| consistency | B | Matches the desktop and the Drawdown x-axis, which runs to Sept |
| phone experience | B | No clipping |
| accessibility | A (slight) | B's in-tile labels on light-green tiles have low contrast |
| visual craft | B | Tidy grid with outlined future months |

**Winner: B.** The loser is only better on label contrast, which is minor.
**Most recent months:** **B**.

## Pair 05: ETF detail, phone, DE

The pictures are identical. Every rubric line is **same**. **Tie.**
**Most recent months:** same in both. The 1J price chart runs to about Okt and is readable.

## Pair 06: Spending, desktop, EN

The pictures are identical. Every rubric line is **same**. **Tie.**
**Most recent months:** same in both. The heatmap shows Jan–Dec in one row.

## Pair 07: Investment analysis, desktop, DE

The pictures are identical. Every rubric line is **same**. **Tie.**
**Most recent months:** same in both. The Monatsrenditen row shows Jan–Dez.

## Across pairs

Taken together, the **wrapped-chart version** (01-B, 02-A, 03-B, 04-B) works better as a set:
- On the desktop, both the heatmap and the month-returns row show the full year.
- In the wrapped version, the phone shows the same months as the desktop, so moving between devices or between Spending and Analysis gives the same picture.
- On the phone in the clipped version, both charts stop at Jun while the summaries around them ("Jan – Okt", "5 von 10", the Rückgang axis to Sep) talk about later months. That leaves the newest data, which matters most, hidden on every phone chart.
- The wrapped version also uses the same "dashed = future" treatment for empty days and empty months, which ties the two screens together.

One small inconsistency remains in the wrapped version. Phone month-tiles put labels inside the tile, while the desktop puts them above. Combined with the low contrast on light tiles, that is the one thing to polish.

## Overall verdict
- Pair 01: **B**
- Pair 02: **A**
- Pair 03: **B** (A slightly better only on month-label contrast)
- Pair 04: **B** (A slightly better only on month-label contrast)
- Pair 05: **tie** (identical)
- Pair 06: **tie** (identical)
- Pair 07: **tie** (identical)
- The recent months are easier to read in the wrapped version in every differing pair: 01-B, 02-A, 03-B, 04-B.
