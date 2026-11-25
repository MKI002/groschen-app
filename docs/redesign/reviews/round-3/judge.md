# Judge 3: blind A/B comparison

How I checked: I diffed every pair pixel by pixel, then zoomed into and measured each region that differed. Many differences are small, so most rows below are "same". One recurring difference is the muted secondary text and icons. One version draws them in #7E838C (about 4.8 to 5.1:1 on the dark surfaces). The other draws them in #5E636C (about 3.0 to 3.2:1, which fails WCAG AA for body text). Which letter has the brighter colour changes from pair to pair. The table below lists it per pair.

| Pair | Brighter muted text (#7E838C) |
|---|---|
| 03 wizard | A |
| 04 transactions (phone) | B |
| 05 spending | A |
| 07 transactions (desk) | B |
| 08 overview | A |
| 09 fixed costs | A |
| 10 investments | B |
| 11 ETF | A |
| 01, 02, 06 | not affected |

---

## Pair 01: Settings, Hints and Salary (phone, de)

Only difference: the 3-option segmented control "Automatisch / Nächster Monat / Buchungsmonat" (salary timing). In A it is a single line, and the third option is cut off at the card edge ("Buchungsmor"). In B the labels wrap ("Nächster / Monat") and all three fit.

| Rubric | Pick | Reason |
|---|---|---|
| Clarity of purpose | B | B shows all three options; in A the third option's label is truncated |
| Hierarchy | same | Identical card and heading structure |
| Task efficiency | B | In B "Buchungsmonat" can be seen and tapped without scrolling sideways |
| Data presentation | same | No data shown differently |
| Navigation and naming | B | B shows the option names in full |
| Consistency | same | Both match the rest of the settings page |
| Phone experience | B | A's control overflows the 390 px card |
| Accessibility | B | B has taller targets (about 48 px) and no hidden option |
| Visual craft | B | A's clipped text looks broken; B's two-line labels are a little uneven but clean |

**Overall: B.** A is not better anywhere important. Its only advantage is that the labels stay on one line.

## Pair 02: Settings, Bank and Import (phone, de)

Only difference: the "Anmelde-Erinnerung" control "30 Tage vorher / 15 Tage vorher / 7 Tage vorher". In A it is a single line, and "7 Tage vorhe" is cut off at the edge. In B the labels wrap and all three fit.

| Rubric | Pick | Reason |
|---|---|---|
| Clarity of purpose | B | In B all reminder options are readable |
| Hierarchy | same | No change |
| Task efficiency | B | In B the "7 Tage vorher" option is fully visible and tappable |
| Data presentation | same | No change |
| Navigation and naming | B | A truncates the label |
| Consistency | B | Same wrap-to-fit treatment as Pair 01 B, so the settings controls behave alike |
| Phone experience | B | A's control overflows the card |
| Accessibility | B | B has bigger targets and no clipped label |
| Visual craft | B | A's cut-off text looks broken |

**Overall: B.** A is not better anywhere important.

## Pair 03: Onboarding wizard, "Bank verbinden" (phone, de)

Two differences:
- **Footer.** In A, "Überspringen, vorerst CSV-Dateien nutzen" wraps onto two lines to the right, and "Weiter" sits right-aligned below it. In B the skip link is one line that runs off the right edge of the card ("...CSV-Dateien nu"), and "Weiter" is left-aligned on its own line.
- **Bank field placeholder.** A uses the brighter colour (#7E838C, 5.0:1). B uses the dimmer one (#5E636C, 3.2:1).

| Rubric | Pick | Reason |
|---|---|---|
| Clarity of purpose | A | A shows the whole skip option; B's is cut off |
| Hierarchy | A | In A the primary "Weiter" stays bottom-right, where a wizard's next step belongs; B's left-aligned "Weiter" reads as secondary |
| Task efficiency | A | A shows both choices completely |
| Data presentation | same | n/a |
| Navigation and naming | A | B truncates the skip link's name |
| Consistency | A | A's button placement matches common wizard convention |
| Phone experience | A | B overflows horizontally at 390 px |
| Accessibility | A | A's placeholder is readable (5.0:1 vs 3.2:1) and A has no clipped text |
| Visual craft | A | B's footer looks broken |

**Overall: A.** B is not better anywhere.

## Pair 04: Transactions list (phone, de)

Two differences:
- **Filter chip bar.** In A the chips are larger, and "Einnahmen" runs to the right edge of the bar. In B the chips are smaller (about 32 px tall, versus about 36 px in A), and all four fit with room to spare. B's list sits about 3 px higher.
- **Search placeholder.** B uses the brighter colour (#7E838C). A uses the dim one (#5E636C).

| Rubric | Pick | Reason |
|---|---|---|
| Clarity of purpose | same | Same list and summary |
| Hierarchy | same | Same structure |
| Task efficiency | B | B shows all four filters (Alle / Zu prüfen / Ohne Kategorie / Einnahmen) inside the bar; in A the last one is flush with the edge |
| Data presentation | same | Rows are identical |
| Navigation and naming | same | Same labels |
| Consistency | B | B's muted text matches the brighter colour elsewhere in B-type screens |
| Phone experience | A | A's chips are larger touch targets; B's are tighter |
| Accessibility | B | B's search placeholder is 4.8:1 vs A's 3.0:1; A's only plus is slightly larger chips |
| Visual craft | B | B's chip bar fits comfortably; A's looks crammed against the edge |

**Overall: B (narrowly).** A's larger filter chips are a real but small advantage on touch.

## Pair 05: Spending (phone, de)

Three differences:
- **Controls.** The Ausgaben/Einnahmen and Gruppen/Kategorien toggles and the date picker are larger in B.
- **Percentage column.** A's "58,3 %" column uses the brighter colour; B's is dim.
- **"Dein Jahr in Tagen" heatmap.** In A it is scrolled to the recent end (Jun to Nov), with no weekday labels and a sliver of a cut-off column at the left edge. In B it starts at Jan, has weekday labels (Mo / Mi / Fr), and is cut off at the right edge in June.

| Rubric | Pick | Reason |
|---|---|---|
| Clarity of purpose | same | Same content |
| Hierarchy | same | Same order |
| Task efficiency | A | A's heatmap opens on the most recent months, the period you most likely want to tap into |
| Data presentation | B | B's weekday labels make the grid readable; A's has none and a clipped first column. A's recency is the counterpoint |
| Navigation and naming | same | Same labels |
| Consistency | same | Both are internally consistent |
| Phone experience | B | B's toggles and date picker are bigger touch targets |
| Accessibility | A | A's percentages are 4.8:1 vs 3.0:1 in B; B's larger targets partly offset this |
| Visual craft | same | Each heatmap is clipped on one side |

**Overall: tie, leaning B.** A is better in important ways: its heatmap shows recent months and its percentages have better contrast.

## Pair 06: Investment analysis (phone, de)

Only meaningful difference: the "Monatsrenditen" grid.
- **A** shows Jan to Jun with a "2026" row label. The best month (Feb +8,2) and worst month (Mai −5,9) are outlined, which matches the legend below ("Umrandet: der beste und der schlechteste Monat"). Nothing hints that more months exist: Jul to Okt are hidden to the right.
- **B** is scrolled to Jul to Dez. Jun fades out at the left, which hints that the grid scrolls. It has no year label. No outlined cell is visible, even though the legend refers to outlines. It shows two empty Nov/Dez placeholder cells.

| Rubric | Pick | Reason |
|---|---|---|
| Clarity of purpose | A | In A the legend's outlined best and worst months are on screen; in B the legend points at nothing visible |
| Hierarchy | same | Same cards |
| Task efficiency | B | B opens on the most recent months |
| Data presentation | A | A has the year row label and the outlined extremes; B spends space on empty future months |
| Navigation and naming | same | Same |
| Consistency | A | A's grid agrees with its own legend |
| Phone experience | B | B's left fade shows the grid scrolls; A gives no hint that four months are hidden |
| Accessibility | same | Same colours |
| Visual craft | same | Both tidy; B's fade is nice, A's outlines are clear |

**Overall: A (narrowly).** B is better in one important way: it shows recent months and makes the scroll discoverable.

## Pair 07: Transactions (desktop, en)

Only difference: the muted text and icon colour. It affects sidebar icons, sub-nav tree lines, the search icon and placeholder, the account column ("Girokonto"), and the chevrons. B uses #7E838C (about 4.8:1). A uses #5E636C (about 3.0:1).

| Rubric | Pick | Reason |
|---|---|---|
| Clarity of purpose | same | Identical layout |
| Hierarchy | same | Muted remains muted in both |
| Task efficiency | B | In B the account column and search hint can be read at a glance |
| Data presentation | B | B's "Girokonto" account column is legible; A's is barely visible |
| Navigation and naming | B | B's sidebar icons are clearer |
| Consistency | same | Each version is uniform on this page |
| Phone experience | same | n/a |
| Accessibility | B | B is 4.8:1 vs A's 3.0:1 for secondary text |
| Visual craft | same | A is a touch quieter, B more legible |

**Overall: B.** A is not better anywhere important.

## Pair 08: Overview (desktop, en)

Only difference: the same muted colour. It affects sidebar icons, the "JAN – OCT 2026" section label, "SAVINGS RATE", the settings and logout icons, and the chevrons. Here A is the brighter one (#7E838C) and B the dim one.

| Rubric | Pick | Reason |
|---|---|---|
| Clarity of purpose | same | Identical |
| Hierarchy | same | Same |
| Task efficiency | same | Same |
| Data presentation | A | A's "SAVINGS RATE" and period label are readable |
| Navigation and naming | A | A's sidebar icons are clearer |
| Consistency | same | Uniform within each |
| Phone experience | same | n/a |
| Accessibility | A | A is 4.8 to 5:1 vs B's 3.0 to 3.2:1 |
| Visual craft | same | Barely visible difference |

**Overall: A.** B is not better anywhere important.

## Pair 09: Fixed costs list (desktop, en)

Only difference: the same muted colour. It affects sidebar icons, the dates in "What changed" ("21 days ago", "18 Aug 2026"…), the row chevrons, and the settings and logout icons. A is brighter.

| Rubric | Pick | Reason |
|---|---|---|
| Clarity of purpose | same | Identical |
| Hierarchy | same | Same |
| Task efficiency | A | A's row chevrons, which mark rows as clickable, are easier to see |
| Data presentation | A | A's change dates are legible |
| Navigation and naming | A | A's sidebar icons are clearer |
| Consistency | same | Uniform within each |
| Phone experience | same | n/a |
| Accessibility | A | Higher contrast for secondary text |
| Visual craft | same | Negligible |

**Overall: A.** B is not better anywhere.

## Pair 10: Investments (desktop, en)

Only difference: the same muted colour. It affects "Savings plan 300.00 € per month", the "Drag across a stretch…" zoom hint and the legend, the ISINs, "85% of the depot", and the sidebar icons. B is brighter.

| Rubric | Pick | Reason |
|---|---|---|
| Clarity of purpose | same | Identical |
| Hierarchy | same | Same |
| Task efficiency | B | B's zoom hint is readable, so the zoom feature can be discovered |
| Data presentation | B | B's ISINs, savings-plan line and depot share are legible |
| Navigation and naming | B | B's sidebar icons are clearer |
| Consistency | same | Uniform within each |
| Phone experience | same | n/a |
| Accessibility | B | B is about 4.8:1 vs A's 3.0:1 |
| Visual craft | same | Negligible |

**Overall: B.** A is not better anywhere.

## Pair 11: ETF detail (phone, en)

Two differences:
- **Range selector (1M / 3M / 6M / 1Y / Max).** In A it sits inline next to "PRICE +11,2 %". In B it has its own row with larger buttons. This makes B 28 px taller.
- **Muted text.** A's muted text is brighter: "60.971 units at…", "Monthly, around day 1 · 250 €", and "Pinch with two fingers to zoom".

| Rubric | Pick | Reason |
|---|---|---|
| Clarity of purpose | same | Same content |
| Hierarchy | A | In A the range control reads as part of the price chart header; B's detached row is looser |
| Task efficiency | B | B's range buttons are easier to hit |
| Data presentation | A | A's units, average and monthly plan line are legible |
| Navigation and naming | same | Same labels |
| Consistency | same | Both coherent |
| Phone experience | B | B has bigger range-button targets |
| Accessibility | A | A's secondary text is 4.8:1 vs B's 3.0:1, and it holds important numbers here |
| Visual craft | A | A's chart header is more compact and tidy |

**Overall: A (narrowly).** B is better in one important way: larger range buttons for touch.

---

## Overall verdict

| Pair | Winner |
|---|---|
| 01 Settings, Hints and Salary | **B**: segmented control fits instead of clipping "Buchungsmonat" |
| 02 Settings, Bank and Import | **B**: reminder options fit instead of clipping "7 Tage vorher" |
| 03 Wizard, country/bank | **A**: B's skip link runs off the card, its "Weiter" is misplaced, and its placeholder is dim |
| 04 Transactions (phone) | **B**, narrowly: filter chips fit and the search placeholder is brighter; A has larger chips |
| 05 Spending (phone) | **Tie, leaning B**: B has weekday labels and bigger toggles; A has the recent heatmap and brighter percentages |
| 06 Investment analysis (phone) | **A**, narrowly: outlines match the legend; B shows recent months and has a scroll fade |
| 07 Transactions (desk) | **B**: brighter secondary text |
| 08 Overview (desk) | **A**: brighter secondary text |
| 09 Fixed costs (desk) | **A**: brighter secondary text |
| 10 Investments (desk) | **B**: brighter secondary text |
| 11 ETF (phone) | **A**, narrowly: brighter secondary text and a compact header; B has bigger range buttons |

**Across pairs.** Neither the "A" set nor the "B" set works better as a whole. Each label mixes the stronger and weaker treatments.

- **Muted text.** The A set has #7E838C on Overview, Fixed costs, ETF, Spending and the Wizard, and #5E636C on Transactions and Investments. The B set is the mirror image. Moving Overview → Transactions → Investments in either set, the sidebar icons and secondary text visibly change brightness from page to page. This is the most noticeable consistency break when switching between screens.
- **Segmented controls on phone.** B consistently wraps labels to fit (pairs 01, 02), and its controls are larger (05, 11). A tends to clip (01, 02); in pair 03 it is B that clips.
- **Scrollable grids.** Each label also mixes recency-first and start-of-year views: the heatmap in pair 05 and the month grid in pair 06.

The best combined version would take:
- the brighter muted colour everywhere
- B's wrap-to-fit segmented controls
- A's wizard footer
- recent-month grids that keep the year label, the outlines and the scroll fade
