# Groschen – Phone and accessibility review (round 0)

Reviewer role: phone experience and accessibility. I score only line 7 (phone experience) and line 8 (accessibility); lines 1-6 and 9 are "-". I viewed every phone.de and phone.en screenshot (the tall ones in 1000 px slices) and desk.en/desk.de where they matter for comparison (01, 02, 05, 20).

## Measurements used throughout

These are estimated from the 390 px width. Contrast was measured with PIL: the most-contrasting anti-aliased glyph pixel against the dominant background in the crop.

| Token (where measured) | Colour on surface | Ratio | WCAG AA small text (4.5) |
|---|---|---|---|
| Primary text (nav active label, 06-transactions-empty.phone.de) | #ecedef on #0d0e11 | 16.5:1 | pass |
| Secondary grey (e.g. "Passen die Kategorien?" 01-overview.phone.de, "Ohne Kategorie" chip 02-transactions.phone.de, chart axes 14-networth.phone.de) | #8d919a on #121418 | 5.8:1 | pass |
| Inactive bottom-nav label (06-transactions-empty.phone.de "Übersicht") | #8d919a on #0d0e11 | 6.1:1 | pass |
| **Tertiary grey** (search placeholder 02-transactions.phone.de; "58,3 %" 07-spending.phone.de; "Vor 21 Tagen" 11-recurring-list.phone.de; "Sparplan 300,00 € pro Monat" and "Mit zwei Fingern vergrößern" 15-investments.phone.de; "Girokonto" account column 02-transactions.desk.en) | #5e636c on #121418 | **3.05:1** | **fail** |
| Disabled gold primary buttons ("Anmelden" 42-login.phone.de, "Weiter" 40-wizard-account.phone.de) | #141312 on #6e6145 | 3.05:1 | fail. Disabled state is exempt, but the button reads as "dimmed, maybe enabled", not clearly disabled |
| Disabled "Protokoll zeigen" (25-settings-privacy.phone.de) | #747679 on #14161b | 4.0:1 | exempt (disabled) |

Estimated sizes on the phone:
- Bottom nav bar: about 66 px tall. Each item is about 78 px wide. Labels are about 10 px.
- Header icon buttons (eye, gear): about 34 × 32 px.
- Dismiss "×" on hint cards (01-overview): about 28 × 28 px.
- Search clear "×" (04-transactions-filtered): about 26 px.
- Category chips in the edit dialog (05): about 30 px tall.
- Segmented controls: about 30-32 px tall.
- Transaction rows: about 64 px. This is good.
- Chart axis text: about 9 px.
- Calendar-cell amounts and "Nov/Feb/Mai" coin labels: about 8 px.

The platform guidance is 44 pt (Apple) or 48 dp (Material). Most secondary controls are 28-34 px.

---

## Global (applies to every phone screen)

- **Bottom nav uses only 4 of 5 slots.**
  - 06-transactions-empty.phone.de: bottom nav, icons at x≈41/118/195/271. The bar is laid out for 5 equal slots, so the right ~80 px is empty and the bar looks left-aligned and unfinished. Settings is only reachable from the 32 px gear in the top-right corner, the hardest place to reach one-handed.
  - Severity: slows a task.
  - Suggestion: either spread the 4 items across the full width, or put "Einstellungen/Settings" (or "Mehr") in the 5th slot.
- **Bottom nav badge is weaker than desktop.**
  - 02-transactions.phone.de: the "Umsätze" item shows only a small gold dot (about 6 px). 02-transactions.desk.en shows a "39" count.
  - The dot is colour-only and has no number.
  - Severity: cosmetic. Suggestion: show the count, as on desktop.
- **The bottom nav is right (keep).** All 4 nav items, from Übersicht to Vermögen, have icon plus label, the active state is a filled pill with white label (16.5:1), and inactive labels are 6:1. `keep`
- **Tertiary grey #5e636c fails contrast (3.05:1) and carries real information.**
  - Where it appears:
    - per-category percentages (07-spending.phone.de "58,3 %")
    - dates under insights (11-recurring-list.phone.de "Vor 21 Tagen")
    - the Sparplan line under the depot value (15-investments.phone.de)
    - the search placeholder (02-transactions.phone.de)
    - the account column on desktop (02-transactions.desk.en "Girokonto")
  - Severity: slows a task (low-vision, sunlight).
  - Suggestion: raise the token to about #80858e (≈4.6:1 on #121418), or reuse the #8d919a secondary.
- **Touch targets for secondary actions are 26-34 px.**
  - Examples:
    - the hint dismiss × (01-overview)
    - the search clear × (04)
    - the eye/gear header buttons
    - the segmented controls (07, 11, 15)
    - the category chips (05, 08)
    - the steppers −/+ (24)
  - Severity: slows a task.
  - Suggestion: keep the visual size, but give each a ≥44 px hit area (padding or pseudo-element), especially the × buttons that sit next to "Zeigen".
- **Hover wording on a touch device.**
  - "Zeig auf ein Band, um ihm zu folgen; Klick zeigt die Umsätze" (01-overview.phone.de, Sankey). "Point at a band… click…" (01-overview.phone.en).
  - "Zeig auf einen Platz…" (24-settings-backup.phone.de).
  - "Klick zeigt die Umsätze des Tages" (07-spending.phone.de, heatmap).
  - There is no hover on a phone.
  - Severity: cosmetic.
  - Suggestion: on touch devices use "Tippe auf…/Tap…". 15-investments.phone.de "Mit zwei Fingern vergrößern" already does this right. `keep` that one.
- **Inconsistent top spacing before page titles.**
  - The H1 sits at y≈90 on most screens. It sits at y≈117 on 23-settings-depot.phone.de and y≈115 on 13-recurring-orbit.phone.de, and at y≈204 on 06-transactions-empty.phone.de, which leaves a 130 px blank band under the header.
  - This looks like the layout reserving space for something that is missing.
  - Severity: cosmetic.
- **Horizontally scrolling tab and segmented bars have no affordance.**
  - The last item is simply cut by the card edge, with no fade or chevron:
    - "Einnahmen" filter chip (02)
    - "Einzahlungen" tab (15, 16)
    - "Sich…", "Exp…", "Konto & Darstellun…" (22-27 settings tabs)
    - "7 Tage vorhe…" (20)
    - "Buchungsmon…" (22)
  - In German it is worse because every label is longer.
  - Severity: slows a task, because settings sections are hard to find.
  - Suggestion: on the phone, replace the 8-tab settings strip with a list page (Settings → section). Elsewhere add an edge fade and scroll the active tab into view. The latter already happens in 24/26, which is good.
- **Privacy toggle in the header (keep).** 31-hidden-overview.phone.de: the eye button turns gold when amounts are hidden. Blurred 9s keep the layout and still read as "hidden". `keep`

---

## 01-overview (phone.de / phone.en; desk.en for comparison)

- **Hero order on the phone is good (keep).**
  - 01-overview.phone.de: "Frei verfügbar bis zum Gehalt" hero is first, with a 34 px number and "28 Tage bis zum Gehalt" under it.
  - The desktop "tank" graphic is dropped on the phone. That is a sensible trim. `keep`
- **Payday strip is too small to read or tap.**
  - 01-overview.phone.de: the day strip has about 30 bars at ~6 px wide, with payment dots ~6 px.
  - "Gehalt 27. Okt." and "Fr., 27. Nov." labels are about 11 px.
  - The dots look tappable but are not usable targets. Severity: cosmetic.
- **"Einen Blick wert" card targets are too small.**
  - 01-overview.phone.de: "Prüfen" and "Zeigen" buttons are about 30 px tall, and the × is 28 px, about 165 px away on the same row.
  - It is OK that the two do not collide, but both are under target size. Severity: slows a task.
- **Sankey is cramped at phone width.**
  - 01-overview.phone.de: "Wohin das Geld geflossen ist" Sankey.
    - The labels stack readably. Amount sublabels are #8d919a at about 11 px, which passes.
    - The bottom 6 categories have bands of about 2-4 px. Those bands cannot be hit by touch, so the "tap to drill" promise fails for small categories.
  - Severity: slows a task.
  - Suggestion: on the phone, make the label rows the tap targets (full row, ≥44 px).
- **EN is slightly tighter.** 01-overview.phone.en: "Stays on the account" is the longest Sankey label and fits. No overflow in either language.
- Scores:
  - 7 (phone): **7**. 01-overview.phone.de: the hero and stacked KPI cards work well, but the Sankey bands and payday dots are not touch-sized.
  - 8 (accessibility): **6**. 01-overview.phone.de: 28 px dismiss × and the hover-only Sankey instruction.

## 02 / 03 / 04 / 06 Transactions (list, needs review, search, empty)

- **List rows (keep).**
  - 02-transactions.phone.de: rows are about 64 px with logo, merchant, category chip and right-aligned bold amount. Income is green with "+" implied.
  - The day headers carry the day total. `keep`
- **Search placeholder is cut and too faint.**
  - 02-transactions.phone.de: the placeholder "Händler, Verwendungszweck, Kategorie oder Betr…" is cut mid-word, and it is the 3.05:1 tertiary grey.
  - Severity: cosmetic.
  - Suggestion: use a shorter DE placeholder such as "Suchen: Händler, Betrag…".
- **The filter chip row clips "Einnahmen".**
  - 02-transactions.phone.de: chips run "Alle / Zu prüfen 39 / Ohne Kategorie / Einnahmen", and "Einnahmen" is clipped at the card edge (see Global). Severity: slows a task.
- **The summary line wraps badly.**
  - 02-transactions.phone.de: the line "Jan – Okt 2026 · 297 Umsätze · 42.057,91 € rein / 31.970,76 € raus" breaks so that "raus" starts a new line with nothing in front. In 04 the "Filter zurücksetzen" link is squeezed after it.
  - Severity: cosmetic.
  - Suggestion: put the in/out totals on their own line, as two figures.
- **Uncategorised marker relies on colour alone.**
  - 02-transactions.phone.de, "Hofladen Sonnenfeld": the uncategorised row is flagged by a 3 px gold left bar plus a dashed "Ohne Kategorie" chip.
  - The bar is colour only. The chip text saves it. Severity: cosmetic.
- **Description lines truncate.**
  - 02-transactions.phone.de: "Beitragsnummer 123456789 Quar…" and "zählt für November 2026 · LOH…" are ellipsised at about 200 px.
  - Acceptable, because the dialog shows the full text.
- **"Needs review" callout is clear (keep).** 03-transactions-review.phone.de: the gold-outlined callout "Diese Umsätze brauchen eine Kategorie von dir." `keep`
- **Search clear button is too small.** 04-transactions-filtered.phone.de: the clear × in the search field is about 26 × 26 px. Severity: slows a task.
- **Empty state works but sits too low.**
  - 06-transactions-empty.phone.de: the empty state "Keine passenden Umsätze" has an icon, text and a gold "Filter zurücksetzen" link. Good.
  - But the whole page is pushed down about 115 px by an empty band under the header. Severity: cosmetic.
- **Sort and filter sit at the top, far from the thumb.**
  - 02-transactions.phone.de: the "Filter" and "Neueste zuerst" controls sit at y≈238. They scroll away and do not stick.
  - With 297 rows, the period, filter and sort are only reachable by scrolling back to the top. The capture also shows no "back to top" control.
  - Severity: slows a task.
  - Suggestion: use a sticky compact search/filter bar or a FAB.
- Scores:
  - 7: **7**. 02-transactions.phone.de: the row design is excellent on the phone, but the chip strip clips and the filters do not stick.
  - 8: **5**. 02-transactions.phone.de: 3.05:1 placeholder, 26 px clear button (04), and the colour-only review bar.

## 05 Transactions – edit dialog

- **The phone gets a centred desktop modal, not a sheet.**
  - 05-transactions-edit.phone.de: the dialog fills the screen with a 16 px margin. Close × at the top right is about 34 px. "Speichern" is at the bottom right, which is good for the thumb. `keep` the Save placement.
- **Category chips are below target size.** 05-transactions-edit.phone.de: chips such as "Wohnen (allgemein)", "Miete" and "+ Neu" are about 30 px tall with 6 px gaps, which invites mis-taps. Severity: slows a task.
- **The rule toggle is below the fold on the phone.**
  - 05-transactions-edit.desk.en shows the toggle "Use this category for every transaction from this merchant" above the footer.
  - On 05-transactions-edit.phone.de it is below the fold, under roughly 40 chips. Users will save without seeing it.
  - Severity: slows a task.
  - Suggestion: pin the toggle into the sticky footer on the phone, or show the "suggested/recent" categories first and collapse the full list.
- **Selected chip is clear (keep).** 05-transactions-edit.phone.de: the selected chip "Tanken" is a gold fill with dark text, distinguishable by more than colour. `keep`
- Scores:
  - 7: **6**. 05-transactions-edit.phone.de: the sticky footer with "Speichern" is good, but the chip wall and hidden toggle hurt.
  - 8: **6**. 05-transactions-edit.phone.de: 30 px chips. The selected state is strong.

## 07 Spending / 33 period menu

- **Two stacked segmented controls start with the same word.**
  - 07-spending.phone.de: "Ausgaben | Einnahmen" sits directly above "Ausgaben | Fixkosten". Two controls both start with "Ausgaben" and mean different things (type vs. page).
  - On desktop, Fixkosten is a sidebar child. On the phone it is this second toggle, so it is navigation disguised as a filter.
  - Severity: slows a task.
  - Suggestion: make it a tab row "Übersicht | Fixkosten", or move Fixkosten into the bottom nav.
- **Donut works at phone width (keep).** 07-spending.phone.de: the donut is about 300 px with the centre total "20.451 €", and the legend rows below have bars. `keep`
- **Legend percentages and a truncated label.**
  - 07-spending.phone.de: the legend percentages ("58,3 %") are the 3.05:1 tertiary grey.
  - "Persönliches · mehr Erstattungen…" is truncated, and its meaning (a negative amount) is lost. Severity: cosmetic.
- **Heatmap cells cannot be tapped.**
  - 07-spending.phone.de: the "Dein Jahr in Tagen" heatmap cells are about 9 px squares, and the grid is cut at "Jun" (it scrolls horizontally, with no affordance).
  - The legend has 5 hues from violet to yellow. They are distinguishable for most colour-vision types, but the cells cannot be tapped. Severity: slows a task.
  - Suggestion: on the phone show a month-by-month heatmap, or rely on the 3 summary lines underneath, which are good.
- **"+ Eigene Gruppe" is faint.** 07-spending.phone.de: the dashed button is low-emphasis and about 30 px tall. Severity: cosmetic.
- **Period menu (keep).**
  - 33-period-menu.phone.de: the dropdown anchors under the trigger, rows are about 37 px, and the current item is marked with a gold label plus a ✓. It does not rely on colour only. `keep`
  - Rows are slightly under 44 px.
- Scores:
  - 7: **6**. 07-spending.phone.de: two "Ausgaben" toggles and the cut heatmap.
  - 8: **6**. 07-spending.phone.de: 3.05:1 percentages and 9 px heatmap cells. 33-period-menu.phone.de has a non-colour selected state.

## 08 Spending – new group dialog

- **Long scroll with a weak Save.**
  - 08-spending-group-dialog.phone.de: the "Neue Gruppe" dialog has a 4-line explanation, then the name field, then an icon picker (icons about 32 px), then a long chip list.
  - The sticky footer holds "Abbrechen / Speichern". Disabled Speichern is the dim gold (3:1 label contrast), which looks almost enabled. Severity: cosmetic.
  - Suggestion: use a clearer disabled style (outline only), plus helper text "Name eingeben".
- **Chips:** about 30 px tall, as in 05.
- Scores:
  - 7: **6**. 08-spending-group-dialog.phone.de: the sticky footer is good, the chip wall is long.
  - 8: **6**. 08-spending-group-dialog.phone.de: the disabled Save state is ambiguous.

## 09 / 10 Drill-down (group, category)

- **No visible way back.**
  - 09-drill-group.phone.de: "AUSGABEN" above "Essen & Trinken" is an 11 px eyebrow label. Nothing shows that it is a back link, and there is no back chevron. On a phone the only way back is the browser gesture.
  - Severity: slows a task.
  - Suggestion: show "‹ Ausgaben" as a 44 px back button.
- **Hero card is clear (keep).** 09-drill-group.phone.de: "3.480,29 €" with "↑ 35 %" in a red pill. The arrow plus text means it is not colour-only. `keep`
- **Chart labels are tiny.** 09-drill-group.phone.de: the monthly bar chart axis labels ("600 €", "Jan", "Mär") are about 9 px, and "Durchschnitt 348 €" is about 9 px. Severity: cosmetic.
- **Nested list is good, but its search placeholder is cut.**
  - 09-drill-group.phone.de: the nested transaction list has its own search, filter, sort and category chips. Good for the task.
  - The placeholder "Händler, Verwendungszweck, Notiz oder Be…" is cut again.
- **Empty "Einnahmen" category leaves two empty states.**
  - 10-drill-category.phone.de: the "Einnahmen" category shows 0,00 € with two stacked empty states ("Nichts darzustellen", "Keine passenden Umsätze").
  - On the phone this is a long scroll of nothing. Severity: cosmetic.
  - Suggestion: collapse it to one empty state.
- Scores:
  - 7: **6**. 09-drill-group.phone.de: there is no back affordance.
  - 8: **6**. 09-drill-group.phone.de: 9 px chart labels.

## 11 / 12 / 13 Fixed costs (list, calendar, orbit)

- **Page layout and the "Als Nächstes" block (keep).**
  - 11-recurring-list.phone.de: the "Liste | Kalender | Orbit" switcher sits next to the "Fixkosten" title, and the "Ausgaben | Fixkosten" toggle sits under it. That is again two segmented controls at the top.
  - "Als Nächstes" rows show "In 2 Tagen Hausverwaltung Kr… 1.050,00 €". The merchant is truncated because the "In 2 Tagen" prefix takes 60 px. Severity: cosmetic.
  - The rows have a coloured left edge. Good. `keep`
- **Badges and normalised amounts (keep).**
  - 11-recurring-list.phone.de "Laufend" list: badges such as "+7,00 €", "Wieder da" and "Neu" carry text, not only colour. `keep`
  - "≈ 27,07 € im Monat" sub-amounts are #8d919a at about 11 px and readable.
- **Dates under insights are too faint.** 11-recurring-list.phone.de: the "Was sich getan hat" dates ("Vor 21 Tagen", "18. Aug. 2026") are the 3.05:1 tertiary grey.
- **German is long.** 11-recurring-list.phone.de is 2303 px tall, against 2224 px in EN. The DE insight copy wraps to 3-4 lines.
- **Calendar cells hold too much text.**
  - 12-recurring-calendar.phone.de: the month grid cells are about 42 × 54 px, which is OK for tapping. Each cell shows dots plus amounts such as "−2.150 €" at about 8 px (5.3:1).
  - At 8 px this is unreadable without zoom. Severity: cosmetic.
  - Suggestion: on the phone show only the dots, and rely on the "Tag für Tag" list below, which is excellent. `keep` the list.
- **Today marker (keep).** 12-recurring-calendar.phone.de: "30" has a gold outline and bold text. `keep`
- **Orbit is not usable on a phone.**
  - 13-recurring-orbit.phone.de, "Dein Monat im Orbit":
    - Labels overlap ("HUK-Coburg" collides with the "1.407 €" centre label).
    - "im Monat" is covered by a bubble.
    - "Hausverwaltung Kr…" is truncated.
    - Most bubbles are 10-20 px, so they cannot be tapped.
  - It carries no information the list does not. Severity: cosmetic.
  - Suggestion: hide Orbit on the phone, or make it a pure visual with no tap promise. Its description says "Klick zeigt ihre Umsätze".
- Scores:
  - 7: **6**. 11-recurring-list.phone.de works. 13-recurring-orbit.phone.de is not fit for the phone.
  - 8: **5**. 12-recurring-calendar.phone.de: 8 px cell amounts. 13-recurring-orbit.phone.de: overlapping labels and tiny targets.

## 14 Net worth

- **Chart and account cards (keep).**
  - 14-networth.phone.de: "Stand heute 44.931,92 €" with a line chart. Axis labels are about 9 px at 5.8:1.
  - The account cards have share bars. Their "17 %" labels are about 10 px. `keep` the card layout.
- **Only one card shows it is tappable.**
  - 14-networth.phone.de: only "Direkt-Depot" has a ›. Girokonto and Extra-Konto look identical but have none.
  - This is OK if they are not tappable, but the user cannot tell. Severity: cosmetic.
- **Sparplan details are too small and truncated.**
  - 14-networth.phone.de: the Sparplan cards show 12 coins about 18 px each, with month labels ("Nov", "Feb") at about 8 px.
  - Names are truncated ("Vanguard FTSE All-W…", "iShares Core MSCI EM…") because the "LÄUFT" badge takes room. Severity: cosmetic.
  - Suggestion: let the name wrap to 2 lines.
- Scores:
  - 7: **7**. 14-networth.phone.de: the cards stack well.
  - 8: **6**. 14-networth.phone.de: 8 px coin labels and truncated fund names.

## 15-19 Depot (overview, forecast, analysis, payments, ETF)

- **The tab strip clips.**
  - 15-investments.phone.de: the "Überblick / Prognose / Analyse / Einzahlungen" tab strip clips "Einzahlungen" at the right.
  - On 17-inv-analysis.phone.de the strip is scrolled so "Überblick" touches the left edge.
  - It works, but there is no affordance. Severity: cosmetic.
- **Depot chart and gestures.**
  - 15-investments.phone.de: the value chart has a profit/loss sub-chart (green/red bars). Red vs green is the only up/down cue on the bars, but the bars also sit above or below the zero line, so it is not colour-only. `keep`
  - The "Einzahlungen" toggle is about 40 × 22 px.
  - The hint "Mit zwei Fingern vergrößern" (pinch) is the right gesture language, but it is 3.05:1 grey.
- **Forecast inputs.**
  - 16-inv-forecast.phone.de: the assumption tiles (2 × 2) are readable.
  - The range bar "Schlechter Fall 46.246 € / Guter Fall 102.388 €" is clear.
  - The horizon chips "1 J … 30 J" are about 30 px tall, with 7 options in 320 px. That is tight.
  - "Auf den Graphen tippen oder ziehen" uses touch wording. Good, `keep`.
- **Monthly return grid is cut, and the best/worst marker is weak.**
  - 17-inv-analysis.phone.de: the "Monatsrenditen" grid shows only Jan-Jun. Jul-Oct are off-screen with no scroll hint. Severity: slows a task (half the data is invisible).
  - The best and worst months are marked only by a thin white outline. The legend "Umrandet: …" helps, but the outline is about 1.5 px.
  - Suggestion: wrap to 2 rows of 6 on the phone.
- **The volatility gauge has a text label (keep).** 17-inv-analysis.phone.de: the gauge "±17 %" has the label "üblich für Aktien-ETFs" and the ends "ruhig/wild". `keep`
- **Payments list.**
  - 18-inv-payments.phone.de: the "Nicht zählen" × actions are text buttons about 24 px tall, sitting right of the date. Severity: slows a task.
  - The expand chevrons (›) are about 12 px, but the whole month row is the target. OK. `keep`
- **ETF detail page.**
  - 19-etf.phone.de: the ISIN chip is monospace and readable.
  - The range buttons "1M 3M 6M 1J Max" are about 32 px tall.
  - The "Dein Schnitt 110,71 €" line label overlaps the chart line at about 9 px. Severity: cosmetic.
- **Hidden mode on the depot.** 32-hidden-investments.phone.de: the blur works on all amounts, axes included ("9k €"). Percentages stay visible, which is a sensible choice. `keep`
- Scores:
  - 7: **6**. 17-inv-analysis.phone.de: the clipped monthly grid. 15-investments.phone.de: the clipped tab strip.
  - 8: **6**. 15-investments.phone.de: 3.05:1 hints. 17-inv-analysis.phone.de: an outline-only best/worst marker.

## 20-27 Settings (all sections), 30 connect dialog

- **Settings navigation.**
  - 20-settings-bank.phone.de: 8 settings sections in one horizontally scrolling tab strip. Only 3 are visible ("Bank & Import / Kategorien / Hinweise & Gehalt").
  - 25-settings-privacy.phone.de shows "Export & Datenschutz". 26-settings-security.phone.de shows "…ort & Datenschutz | Sicherheit | Konto & Darstellun…".
  - A user cannot see that "Sicherheit" or "Konto" exist without swiping. **Severity: slows a task.**
  - Suggestion: on the phone, use a settings index list.
- **Settings opens in the hardest-to-reach corner.** Every screen, e.g. 20-settings-bank.phone.de: the gear in the top-right header is the only entry, and the gear stays highlighted while Settings is open. The bottom nav shows nothing active while in Settings.
- **Bank card.**
  - 20-settings-bank.phone.de: the actions "Jetzt abrufen", "Ich war bei der Bank angemeldet" and "Zugangsdaten ändern" stack vertically at about 30 px tall. Good stacking for the phone, small height.
  - Toggles are about 40 × 24 px. Their on-state is gold with a dark knob. The off-state (24-settings-backup.phone.de "Anzahl begrenzen", 27-settings-account.phone.de "Wechselkurse") is a grey knob on a dark track at low contrast, about 2:1 against the card. Severity: cosmetic.
  - Suggestion: give the off-track an outline.
- **"7 Tage vorher" is clipped.** 20-settings-bank.phone.de: the segmented control "30 Tage vorher | 15 Tage vorher | 7 Tage vorhe…" is clipped. On the phone use "30 / 15 / 7 Tage". Severity: cosmetic.
- **Native selects.** 20-settings-bank.phone.de: "Täglich um 06:00" and 27-settings-account.phone.de "Nicht gewählt", "EUR · Euro" are native selects. Good on a phone (OS picker). `keep`. They look different from the custom period picker (consistency), which is fine.
- **Categories section has a clipped control and a long label.**
  - 21-settings-categories.phone.de: the "Wenn Händler enthält …" rule builder selects are about 32 px. "Kategorie…" is clipped.
  - The toggle label "Unsichere Zuordnungen in „Zu prüfen" legen" wraps over 2 lines next to the toggle. Fine.
- **"Buchungsmonat" is clipped.** 22-settings-hints.phone.de: the segmented "Automatisch | Nächster Monat | Buchungsmon…" is clipped. Severity: cosmetic. The rows of 6 toggles are clean. `keep`
- **Depot settings.**
  - 23-settings-depot.phone.de: the page has the extra 27 px top gap (see Global).
  - The field "1.75 %" uses a dot decimal in the German UI. Severity: cosmetic, but confusing for German users (should be "1,75").
- **Backup.**
  - 24-settings-backup.phone.de: the stepper −/+ buttons are about 28 px.
  - The text "Zeig auf einen Platz, um die Sicherung darin zu sehen" uses hover wording.
  - The slider "Wie weit zurück" thumb is about 20 px, which is fine.
  - The radio cards "Smart Recycle / Eigene" are large targets with a radio plus a border. `keep`
- **The disabled log button has no explanation in place.** 25-settings-privacy.phone.de: "Protokoll zeigen" is disabled at 4:1. The reason is in the line above ("Keine ausgehenden Verbindungen"), not on the button. Acceptable.
- **Security uses German labels well (keep).**
  - 26-settings-security.phone.de: the numeric fields ("10 Versuche 15 Min.") are about 64 × 32 px.
  - The "Angemeldete Geräte" row has a text-only "Abmelden" action, about 60 × 24 px. Severity: slows a task.
  - The German strings wrap but do not overflow. `keep`
- **Account and display.**
  - 27-settings-account.phone.de: the animation setting "Voll / Ruhig / Aus" shows "Aus" selected, and the copy says the system "Bewegung reduzieren" setting is honoured. **Excellent accessibility detail, `keep`.**
  - "Quellcode" is plain grey text with no link affordance. Severity: cosmetic.
- **Connect dialog shows an error too early.**
  - 30-settings-connect-dialog.phone.de: in "Bank verbinden", with the field empty, the dialog already shows the error "Keine Bank mit diesem Namen gefunden. Gib stattdessen deine Bankleitzahl oder IBAN ein." The same happens in the wizard (41-wizard-country.phone.de).
  - Premature errors are a known a11y and anxiety issue. Severity: slows a task.
  - Suggestion: show it only after input.
  - The primary "Fertig, Abruf starten" is dim gold (disabled), and it is unclear why.
- Scores:
  - 7: **5**. 20-settings-bank.phone.de: the 8-tab strip hides most sections. Three segmented controls are clipped (20, 22). 23-settings-depot.phone.de has an extra top gap.
  - 8: **6**. 27-settings-account.phone.de: the reduced-motion setting is a strong plus. Against it: 24-settings-backup.phone.de has low-contrast off toggles and 28 px steppers, and 30-settings-connect-dialog.phone.de shows a premature error.

## 31 / 32 Hidden mode

- **Blur covers every amount (keep).**
  - 31-hidden-overview.phone.de: every amount, inline amounts in hint text included ("Apple, 9,99 € monatlich"), is replaced by blurred 9s.
  - The eye button shows an active gold state with a crossed-eye icon. `keep`
- **Sankey widths still leak proportions.** 31-hidden-overview.phone.de: the Sankey band widths and percentages still show proportions. That is a design choice, acceptable.
- **Blur legibility.** The blurred placeholders keep their text width. Screen readers would still read the real numbers if the blur is CSS only, which cannot be judged from a screenshot. Worth checking.
- Scores:
  - 7: **8**. 31-hidden-overview.phone.de: one tap in the header.
  - 8: **7**. 31-hidden-overview.phone.de: a clear state change, not colour-only (the icon changes).

## 40 / 41 / 42 Wizard and login

- **Account step layout.**
  - 40-wizard-account.phone.de: the fields are about 40 px tall with labels above, and the password hint is below. Good. `keep`
  - The progress bar is 5 segments of 3 px each, and the step number is not shown in text. Severity: cosmetic.
  - "Weiter" is disabled dim gold at 3:1.
- **German overflow bug in the country step.**
  - **41-wizard-country.phone.de: the skip link "Überspringen, vorerst CSV-Dateien nu…" overflows the card's right edge and is cut off.**
  - "Weiter" drops to a second line on the left. The page also becomes 854 px tall instead of 844 px, which suggests horizontal overflow.
  - The EN equivalent (41-wizard-country.phone.en, United Kingdom path) has no such link.
  - **Severity: slows a task** (the skip option is unreadable in German).
  - Suggestion: stack it as a full-width secondary button under "Weiter", with a shorter text, "Überspringen – nur CSV".
- **Long German paragraph and early error.** 41-wizard-country.phone.de: the 7-line FinTS paragraph is at 15 px in #8d919a. Readable, but long. The premature error "Keine Bank mit diesem Namen gefunden" also appears here.
- **Login.**
  - 42-login.phone.de: a gold focus ring is visible on "Benutzername". This is the only screenshot that shows a focus indicator, and it is good (about 2 px, gold on dark). `keep`
  - "Anmelden" is a 36 px full-width button. With the button disabled, its label contrast is 3:1.
  - The language select is about 30 px.
- Scores:
  - 7: **6**. 41-wizard-country.phone.de: the overflowing skip link. 40 and 42 are good.
  - 8: **6**. 42-login.phone.de: a visible focus ring. 41-wizard-country.phone.de: a premature error and a cut link.

---

## Score summary (lines 7 / 8; lines 1-6, 9: "-")

| Screen | 7 phone | 8 a11y | Anchor element |
|---|---|---|---|
| 01-overview | 7 | 6 | phone.de Sankey bands / 28 px dismiss × |
| 02-04, 06 transactions | 7 | 5 | phone.de 64 px rows / 3.05:1 placeholder, clipped chip strip |
| 05 edit dialog | 6 | 6 | phone.de 30 px chips, rule toggle below the fold |
| 07 spending, 33 period menu | 6 | 6 | phone.de double "Ausgaben" toggles, 9 px heatmap |
| 08 group dialog | 6 | 6 | phone.de disabled "Speichern" |
| 09/10 drill | 6 | 6 | phone.de missing back control |
| 11-13 fixed costs | 6 | 5 | 12 calendar 8 px amounts, 13 orbit overlap |
| 14 net worth | 7 | 6 | phone.de Sparplan coin labels / truncated names |
| 15-19 depot | 6 | 6 | 17 monthly grid cut at Jun |
| 20-27, 30 settings | 5 | 6 | 20 8-tab strip / 27 reduced-motion setting |
| 31/32 hidden | 8 | 7 | 31 eye toggle state |
| 40-42 wizard/login | 6 | 6 | 41 phone.de overflowing skip link / 42 focus ring |

## Keep list

- 02-transactions.phone.de: the 64 px transaction rows with logo, chip, and day totals in the headers.
- 06-transactions-empty.phone.de: the bottom nav with icon plus label and a filled active pill (16.5:1).
- 31-hidden-overview.phone.de: the one-tap privacy eye in the header, with an icon state change.
- 27-settings-account.phone.de: the "Animationen Voll/Ruhig/Aus" setting that honours the system "Bewegung reduzieren".
- 42-login.phone.de: the visible gold focus ring.
- 33-period-menu.phone.de: the selected item marked with ✓ plus colour.
- 12-recurring-calendar.phone.de: the "Tag für Tag" list under the calendar.
- 15-investments.phone.de and 16-inv-forecast.phone.de: the touch-specific hints ("Mit zwei Fingern vergrößern", "tippen oder ziehen").
- 05-transactions-edit.phone.de: the sticky dialog footer with "Speichern" at the bottom right.
- 11-recurring-list.phone.de: the text badges ("+7,00 €", "Wieder da", "Neu"), which do not rely on colour.

## Top 10

1. **41-wizard-country.phone.de: the skip link "Überspringen, vorerst CSV-Dateien nu…" overflows the card and is cut off.** "Weiter" also wraps and the page scrolls horizontally. Severity: slows a task. Stack it as a full-width secondary button with shorter copy.
2. **20-27 settings (e.g. 20-settings-bank.phone.de, 26-settings-security.phone.de): 8 settings sections hide in a horizontally scrolling tab strip.** Only 3 are visible, the labels are cut ("Sich…", "Konto & Darstellun…"), and the strip has no scroll affordance. Severity: slows a task. Use a settings index list on the phone.
3. **Tertiary grey #5e636c on #121418 is 3.05:1, which fails WCAG AA.** It is used for information, not decoration: 07-spending.phone.de percentages, 11-recurring-list.phone.de dates, 15-investments.phone.de Sparplan line, 02-transactions.phone.de search placeholder, and 02-transactions.desk.en "Girokonto" column. Severity: slows a task. Lift it to ≥4.5:1, about #80858e.
4. **Secondary touch targets are 26-34 px.** Examples: 01-overview.phone.de dismiss ×, 04-transactions-filtered.phone.de search clear ×, 05-transactions-edit.phone.de category chips, 24-settings-backup.phone.de steppers, and 26-settings-security.phone.de text "Abmelden". Severity: slows a task. Give each a ≥44 px hit area.
5. **06-transactions-empty.phone.de: the bottom nav uses 4 of 5 slots and leaves the right ~80 px empty.** Settings exists only as a 32 px gear in the top-right corner, out of thumb reach. Severity: slows a task. Fill the 5th slot with Settings/More, or spread the 4 items.
6. **17-inv-analysis.phone.de: the "Monatsrenditen" grid shows only Jan-Jun.** Jul-Oct are off-screen with no hint, and 07-spending.phone.de's heatmap is cut at "Jun" the same way. Severity: slows a task. Wrap to 2 × 6 on the phone.
7. **05-transactions-edit.phone.de: the "apply to every transaction from this merchant" toggle is hidden below about 40 category chips.** On 05-transactions-edit.desk.en it is visible. Severity: slows a task. Put it in the sticky footer, or show recent categories first.
8. **30-settings-connect-dialog.phone.de and 41-wizard-country.phone.de show the error "Keine Bank mit diesem Namen gefunden" before the user has typed anything.** Severity: slows a task. Validate only after input.
9. **07-spending.phone.de: two stacked segmented controls both begin with "Ausgaben".** "Ausgaben|Einnahmen" sits above "Ausgaben|Fixkosten", so navigation looks like a filter. Separately, 09-drill-group.phone.de has no back control (only an 11 px "AUSGABEN" eyebrow). Severity: slows a task.
10. **Mobile data-vis is too small or unusable by touch.** Severity: cosmetic.
    - 12-recurring-calendar.phone.de: 8 px amounts in the calendar cells.
    - 13-recurring-orbit.phone.de: overlapping labels ("HUK-Coburg" over "1.407 €") and bubbles of 10-20 px.
    - 01-overview.phone.de: Sankey bands of 2-4 px that promise "Klick zeigt die Umsätze".
    - Fix: make the legend/label rows the tap targets, drop the in-cell amounts on the phone, and replace "Zeig auf…/Klick" with "Tippe…" on touch.
