# Groschen, pass 8: phone and accessibility review

Role: phone experience and accessibility. I score only rubric line 7 (phone experience) and line 8 (accessibility). All other lines are "-".
Method: I looked at every phone screenshot in DE and EN, and at the desktop screenshots 01-overview.desk.en, 02-transactions.desk.de, 05/07 desk where it mattered. The phone captures are 390 px wide, so 1 image px is 1 CSS px. I measured contrast with PIL by taking the most common pixel in the region as the background and the pixel that contrasts most with it as the text colour. These are upper-bound WCAG ratios, because anti-aliasing softens real glyph edges a little.

## Measurements used throughout

| Element (screenshot) | Colours | Ratio | Approx. size |
|---|---|---|---|
| Secondary grey text on cards, e.g. "Im Schnitt 2.045,14 € pro Monat" (01-overview.phone.de) | #8d919a on #121418 | 5.8:1 | ~12 px |
| Date group header "MITTWOCH, 28. OKTOBER" (02-transactions.phone.de) | #8d919a on #121418 | 5.8:1 | ~11 px caps |
| Inactive bottom-nav label "Umsätze" (01-overview.phone.de) | #8d919a on #0d0e11 | 6.1:1 | ~10-11 px |
| "Girokonto" account column (02-transactions.desk.de) | #7e838c on #121418 | 4.8:1 | 12 px |
| Chart axis labels "400 €" (10-drill-category.phone.de) | #7e828a on #131519 | 4.7:1 | ~9 px |
| Calendar cell amounts "-2.150 €" (12-recurring-calendar.phone.de) | #8a8e96 on #171a1f | 5.3:1 | **~8-9 px** |
| "Protokoll zeigen" disabled button (25-settings-privacy.phone.de) | #747679 on #14161b | 4.0:1 | 12 px |
| Disabled "Anmelden" / "Sign in" (42-login.phone.*) | #141312 on #6e6145 | 3.1:1 | 13 px |
| Disabled "Weiter" (40-wizard-account.phone.de) | #131311 on #6b5e41 | 2.9:1 | 13 px |
| Return tile "-0,9" on dark red (17-inv-analysis.phone.de) | #ecedef on #452a2b | 11:1 | 11 px |

Conclusion: the grey palette passes AA everywhere I measured. Contrast is not the weak point. The problems are **size** (8-11 px text in charts, the calendar and nav labels), **touch-target size** and **mouse wording on touch screens**.

Touch-target estimates (CSS px, from the 390 px captures):
- Bottom nav items: ~97 x 60, good.
- Sub-tabs (Ausgaben/Fixkosten, Depot/Analyse/...): ~44 tall, good.
- Header eye and gear buttons: ~34 x 32.
- Period button "Jan – Okt 2026": ~34 tall.
- Filter chips row "Alle / Zu prüfen / Ohne Kategorie / Einnahmen": **~30 tall**.
- "Filter" / sort: ~32-34.
- Insight dismiss "x": **~28 x 28**.
- "Prüfen" / "Zeigen" pills: ~28 tall.
- Category chips in the edit sheet: ~28 tall.
- Backup steppers "-"/"+": **~28 round**.
- "Nicht zählen": **~18 tall text button**.
- Back links "< EINSTELLUNGEN": **~16 tall text**.
- Heatmap day cells: **~8 x 8**.
- Orbit planets: 8-40 px and overlapping.
- Calendar day cells: ~42 x 56, good.
- Transaction rows: ~64 tall, good.

---

## 01 Overview (+ 31 hidden)

| Line | Score | Based on |
|---|---|---|
| 1-6, 9 | - | |
| 7 phone | 7 | 01-overview.phone.de: hero "Frei verfügbar bis zum Gehalt" fills the first screen and is readable. Bottom tab bar with four ~97 px items. The cards stack cleanly in one column. |
| 8 a11y | 6 | 01-overview.phone.de: insight dismiss "x" at ~28 px, payday timeline dots ~6 px, Sankey sub-labels "3.000,00 € (8,9 %)" at ~11 px |

Findings:
- **keep**: 01-overview.phone.de/en, single-column order hero → "Einen Blick wert" → KPIs → Sankey. The most important number is above the fold. The Sankey turns vertical on phone and its labels never collide.
- 01-overview.phone.de, Sankey hint "Zeig auf ein Band, um ihm zu folgen; Klick zeigt die Umsätze" (EN: "Point at a band to follow it, click to see its transactions"). This is hover and click wording on a touch screen, where there is no hover. Severity: slows a task. Suggestion: on touch devices, show "Tippe auf ein Band, um die Umsätze zu sehen".
- 01-overview.phone.de, "Einen Blick wert", dismiss "x" buttons are ~28x28 and sit alone at the right edge, far from their row. Severity: slows a task. Suggestion: give them a 44x44 hit area, or put them on the same row as "Zeigen".
- 01-overview.phone.de, payday strip: the payment dots are ~6 px and "Gehalt 27. Okt." is ~11 px grey. The dots look tappable but cannot be hit reliably. The "14 Zahlungen kommen noch" link below does the same job, so this is cosmetic. Suggestion: make the whole strip one tap target that opens 34-payday-details.
- 01-overview.phone.de vs 02 desk: on desktop the sidebar shows the badge "39", but the phone bottom nav shows only a ~6 px gold dot on "Umsätze". The dot is colour-only, has no count and is too small to read. Severity: cosmetic. Suggestion: show the count badge on phone too.
- 31-hidden-overview.phone.de: amounts are blurred correctly and the eye icon shows a highlighted active state (**keep**). However, the Sankey percentages "(35,6 %)", "39 %" Sparquote and "42 % über deinem Durchschnitt" stay visible. Anyone who knows one amount can work out the others. Severity: cosmetic (privacy). Suggestion: blur percentages as well in hidden mode, or say plainly that ratios stay visible.

## 02 / 04 Transactions, 03 Needs review, 06 empty

| Line | Score | Based on |
|---|---|---|
| 7 phone | 6 | 02-transactions.phone.de: rows ~64 px with logo, name, chip and amount are good. But the filter chips "Alle / Zu prüfen 39 / Ohne Kategorie / Einnahmen" are ~30 px tall, and the search placeholder is cut off at "...Kategorie oder Betr". |
| 8 a11y | 5 | 03-transactions-review.phone.de: "needs review" is shown only by a 3 px gold bar at the row's left edge. The count in "Zu prüfen 39" disagrees with the list's "8 Umsätze". |

Findings:
- 03-transactions-review.phone.de/en: the chip says "Zu prüfen 39" ("Needs review 39") but the list header says "Alle Zeiträume · 8 Umsätze". At the same time the period button still says "Jan – Okt 2026" while the list says "Alle Zeiträume". A screen-reader or low-vision user who relies on the counts gets two conflicting numbers and two conflicting periods. Severity: slows a task. Suggestion: make the badge count the same set the list shows, and grey out or relabel the period button while the review view ignores it.
- 02-transactions.phone.de and 03-transactions-review.phone.de: a review-needed row is marked only by a thin gold left bar (Hofladen Sonnenfeld, Jonas Weber). This is a colour/position-only signal. The "Ohne Kategorie" chip helps, but rows that have a guessed category and still need review would have no text cue. Severity: slows a task. Suggestion: add a text or icon chip such as "Prüfen" to those rows.
- 02-transactions.phone.de, search placeholder "Händler, Verwendungszweck, Kategorie oder Betr" is truncated (EN "Search merchant, purpose, category or amount" fits). Severity: cosmetic. Suggestion: on phone use "Suchen: Händler, Betrag ..." or just "Umsätze durchsuchen".
- 02-transactions.phone.de, filter segmented control: ~30 px tall, with "Einnahmen" right at the edge. It fits at 390 px but will overflow at 360 px in DE. Severity: slows a task. Suggestion: make it 40-44 px tall and horizontally scrollable.
- 02-transactions.phone.de, the period button and "Filter" sit at the top of a 5200 px page, out of thumb reach, and they do not stick. After scrolling, the user has to go back to the top to change the period. Severity: slows a task. Suggestion: a sticky compact filter bar, or a floating filter button.
- 02-transactions.phone.de, secondary lines such as "Amazon.de Bestellung 302-81035..." and "Abschlag Strom Vertragskonto 10..." are truncated. That is acceptable, because the edit sheet shows the full text (**keep** the monospace purpose block in 05).
- **keep**: 02-transactions.phone.de: day headers with day totals right-aligned, income in green and amounts tabular. 04-transactions-filtered.phone.de has a clear "x" in the search (~26 px; could be larger) and a gold "Filter zurücksetzen" link.
- 06-transactions-empty.phone.de/en: the empty state "Keine passenden Umsätze" has a helpful hint (**keep**). But the whole page header is pushed down ~110 px compared with 02, leaving a blank band under the app bar. Severity: cosmetic. Suggestion: keep the header pinned at the top in the empty state.

## 05 Transaction edit sheet

| Line | Score | Based on |
|---|---|---|
| 7 phone | 6 | 05-transactions-edit.phone.de: "Speichern" sits bottom-right within thumb reach (good). But the currently selected category "Tanken" is below the fold; only Wohnen and Essen & Trinken are visible. |
| 8 a11y | 6 | 05-transactions-edit.phone.de: category chips ~28 px tall. The close "x" is ~32 px in the top-right corner. |

Findings:
- 05-transactions-edit.phone.de: in DE the selected chip "Tanken" is scrolled out of view, while in EN (05-transactions-edit.phone.en) "Fuel" is just visible at the bottom. On opening the sheet, the user cannot see what the current category is. Severity: slows a task. Suggestion: show the current category as a line under the amount ("Kategorie: Tanken"), or scroll the selected chip into view.
- 05-transactions-edit.phone.de: chips are ~28 px tall with ~6 px gaps, which invites mis-taps. Severity: slows a task. Suggestion: chips at least 36 px tall with 8 px gaps, or a list with 44 px rows on phone.
- **keep**: 05-transactions-edit.phone.de, sticky footer with the merchant-rule toggle, "Alles mit Shell" and a large "Speichern" (~94x36) at the bottom where the thumb rests.
- 05-transactions-edit.phone.de: the sheet is a centred card with a 16 px margin rather than a bottom sheet anchored to the bottom edge. Cosmetic; it works.

## 07 Spending, 08 group dialog, 33 period menu

| Line | Score | Based on |
|---|---|---|
| 7 phone | 6 | 07-spending.phone.de: the donut and category list read well. But the "Dein Jahr in Tagen" heatmap cells are ~8 px and the card says "Klick zeigt die Umsätze des Tages". |
| 8 a11y | 5 | 07-spending.phone.de: the heatmap encodes amount only by colour (violet→yellow). The donut separates neighbouring segments only by colour. |

Findings:
- 07-spending.phone.de, heatmap: day cells are ~8x8 px with ~2 px gaps. Tapping one day is not realistic, yet the card promises a click to see the day. Severity: blocks a task (on phone). Suggestion: on phone, tap a week column or month to open a list, or show a day picker. At minimum, change the copy.
- 07-spending.phone.de: the heatmap legend "Weniger ■■■■■ Mehr" is colour-only, and the five steps violet/magenta/red/orange/yellow are close in lightness for the middle three. The summary lines below ("185 Tage ohne Ausgaben", "1.233,55 € am teuersten Tag") are a good text alternative (**keep**).
- 07-spending.phone.de, donut: the two rings with ~14 thin segments are not tappable at that size, and adjacent greys (Einkaufen, Ohne Kategorie) look alike. The list below carries everything with names, amounts and %, so this is cosmetic (**keep** the list with bars and chevrons).
- 07-spending.phone.de, the list row "Persönliches · mehr Erstattungen..." is truncated and the meaning of the negative "-162,37 €" is lost. Severity: cosmetic. Suggestion: put the explanation on a second line.
- 07-spending.phone.de: "+ Eigene Gruppe" is a dashed ghost pill ~30 px tall that reads as a placeholder. Cosmetic.
- 08-spending-group-dialog.phone.de: the symbol picker is four icon-only buttons (~40x30) with no labels. Screen-reader names are unknown and sighted users have to guess (car, house, plane, tag). Cosmetic. "Speichern" is disabled until a name is entered, but nothing says why; the placeholder "Auto" looks like a filled value. Severity: slows a task. Suggestion: make the placeholder an obvious example ("z. B. Auto") and add a hint next to the disabled button.
- 33-period-menu.phone.de: the menu items are ~37 px tall with a checkmark and gold colour for the selected item (**keep**: selection is not colour-only). The menu opens from the top-right, out of thumb reach. There is no custom date range. Cosmetic.

## 09 / 10 Drill-down (group / category)

| Line | Score | Based on |
|---|---|---|
| 7 phone | 7 | 09-drill-group.phone.de: KPI card, monthly bars with an average line, a merchant list with bars and an embedded transaction list all fit at 390 px. |
| 8 a11y | 6 | 10-drill-category.phone.de: chart axis labels ~9 px (4.7:1). Back link "< AUSGABEN > ESSEN & TRINKEN" is ~11 px caps text with ~16 px hit height. |

Findings:
- 09-drill-group.phone.de / 10-drill-category.phone.de: the breadcrumb back link is tiny caps text at the top-left. The obvious phone "back" target is therefore small and out of thumb reach, and there is no other back affordance. Severity: slows a task. Suggestion: give the breadcrumb a 44 px row and make it look like a button, or rely on a proper app-bar back arrow.
- 09-drill-group.phone.de: the month axis labels only every second month ("Jan, Mär, Mai, Jul, Sep") at ~9 px. Cosmetic.
- 10-drill-category.phone.de: the secondary line "VISA Debitkartenumsatz vom 16.1..." is the same on every row and is truncated. It adds noise and no information. Cosmetic. Suggestion: hide generic bank purpose text when the merchant is known.
- **keep**: 09-drill-group.phone.de, "↑ 35 % ggü. dem Zeitraum davor" has an arrow plus a sign plus colour, so it is not colour-only.
- 09-drill-group.phone.de, the category filter chips "Alle / Lebensmittel 43 / ..." wrap to three lines, which is good, but they are ~30 px tall. Cosmetic.

## 11 Fixed costs list, 12 calendar, 13 orbit

| Line | Score | Based on |
|---|---|---|
| 7 phone | 6 | 12-recurring-calendar.phone.de: day cells ~42x56 are tappable (good), but the amounts inside them are ~8-9 px. 13-recurring-orbit.phone.de: the orbit is squeezed into ~280x120 px with overlapping planets. |
| 8 a11y | 5 | 12-recurring-calendar.phone.de: in the legend "Dauerauftrag" and "Gehalt" are two near-identical teal/green dots. 13-recurring-orbit.phone.de: the labels overlap the planets ("im Monat" under a planet). |

Findings:
- 13-recurring-orbit.phone.de/en: the orbit view does not work at phone width. Planets overlap, so the big blue one covers "im Monat"/"a month" and two others. Labels are cut ("Hausverwaltung Kr..."). Tapping a specific payment, as "Klick zeigt ihre Umsätze" offers, is guesswork. Severity: blocks a task (on phone). Suggestion: hide "Orbit" on narrow screens, or render it as a list grouped by ring.
- 12-recurring-calendar.phone.de, legend: "Dauerauftrag" (teal) and "Gehalt" (green) differ only by a slight hue. In the calendar a teal dot on the 1st and a green dot on the 27th cannot be told apart, especially with red-green colour vision deficiency. Severity: slows a task. Suggestion: use different shapes (ring vs dot) or icons, or a clearly different hue.
- 12-recurring-calendar.phone.de, the in-cell amounts "-2.150 €", "-81 €" are ~8-9 px. That is below any comfortable reading size, even though the contrast is 5.3:1. Severity: cosmetic. Suggestion: drop the amounts on phone and keep the dots, since "Tag für Tag" below lists them anyway (**keep** that list).
- 11-recurring-list.phone.de: "Als Nächstes" rows truncate the payee ("Hausverwaltung Kr..."). "Stadtwerke Muench..." is cut because the "+7,00 €" badge takes its space. Cosmetic. Suggestion: move the change badge to the second line on phone.
- 11-recurring-list.phone.de: "> Beendet (1)" is a ~11 px gold text toggle with ~20 px height, and "Alle 8 zeigen" is text-only. Cosmetic; enlarge the hit areas.
- 11-recurring-list.phone.de: "Ein Klick zeigt die ganze Geschichte" is mouse wording again (see Top 10 #3).
- **keep**: 11-recurring-list.phone.de, rows show the rhythm in text ("monatlich · am 1.", "alle 4 Wochen ≈ 27,07 € im Monat"). The badges "Neu" and "Wieder da" use words, not just colour.
- **keep**: 13-recurring-orbit.phone.de, the ring legend "alle 4 Wochen · 1, monatlich · 9..." is textual.

## 14 Net worth

| Line | Score | Based on |
|---|---|---|
| 7 phone | 7 | 14-networth.phone.de: the "Stand heute 44.931,92 €" hero and the line chart are readable, and the account cards are clear. |
| 8 a11y | 6 | 14-networth.phone.de: savings-plan names "Vanguard FTSE All-W..." and "iShares Core MSCI EM..." are truncated, so the ETF cannot be identified. The small percentage "17 %" is ~10 px grey. |

Findings:
- 14-networth.phone.de: the savings-plan card titles truncate exactly where the ETFs differ ("Vanguard FTSE All-W...", "iShares Core MSCI EM..."). Severity: cosmetic. Suggestion: allow two lines for the title, or put the "LÄUFT" badge on its own line.
- 14-networth.phone.de: the 12 gold coins per plan (~18 px each) with month labels every third coin are decorative and fine. Missed months would be distinguishable only by colour (not shown here); check that they get an icon.
- 14-networth.phone.de: the chart x-axis starts at "Dez 25" while the period says "Jan – Okt 2026". Cosmetic.

## 15 Investments, 16 forecast, 17 analysis, 18 pay-ins, 19 ETF (+ 32 hidden)

| Line | Score | Based on |
|---|---|---|
| 7 phone | 7 | 15-investments.phone.de: the "Mit zwei Fingern vergrößern" hint shows the charts are touch-aware. 16-inv-forecast.phone.de: "Auf den Graphen tippen oder ziehen". The four sub-tabs "Depot / Analyse / Prognose / Einzahlungen" fit at 390 px. |
| 8 a11y | 6 | 15-investments.phone.de: the monthly gain/loss bars are green/red only (position above/below the axis helps). 17-inv-analysis.phone.de: the "Umrandet: der beste und der schlechteste Monat" legend uses a square that looks like an unchecked checkbox. |

Findings:
- **keep**: 15-investments.phone.de and 19-etf.phone.de, the "Mit zwei Fingern vergrößern" hint; 16-inv-forecast.phone.de, "Auf den Graphen tippen oder ziehen". This is the right touch wording. The rest of the app should copy it.
- 17-inv-analysis.phone.de: the legend swatch for "Umrandet" is a bordered empty square that reads as a checkbox control. Users will try to tap it. Severity: cosmetic. Suggestion: show a mini tile with the white outline instead.
- **keep**: 17-inv-analysis.phone.de, the monthly return tiles carry signed numbers ("-5,9", "+8,2"), not just red/green, and white text on the dark tiles measures 8.8-11:1.
- 15-investments.phone.de, the "Gewinn und Verlust pro Monat" bars are red/green, but they sit above or below zero, so the encoding is redundant. OK.
- 16-inv-forecast.phone.de: the horizon chips "1J 2J 3J 5J 10J 20J 30J" are ~28 px tall and ~36 px wide. Severity: slows a task. Suggestion: 40 px height. The "eingezahlt" tick label on the range bar is ~9 px and crowds the 68.412 € number. Cosmetic.
- 18-inv-payments.phone.de: "x Nicht zählen" is a ~18 px tall grey text button on each payment. It is easy to mis-hit and its role (exclude from depot) is unclear without the paragraph above. The paragraph says "Ein Klick nimmt es raus". Severity: slows a task. Suggestion: a proper 36-44 px button, or a swipe/overflow menu.
- 19-etf.phone.de: "Dein Schnitt 110,71 €" sits on top of the price line and the purchase dots. Cosmetic.
- 19-etf.phone.de: the range buttons "1M 3M 6M 1J Max" are ~30 px tall. Cosmetic.
- 32-hidden-investments.phone.de: amounts are blurred, including the axis labels (**keep**). The percentages "+6,7 %", "85 % des Depots" and "+7,5 %" stay visible. Cosmetic (privacy).

## 20-28 Settings, 30 connect dialog

| Line | Score | Based on |
|---|---|---|
| 7 phone | 7 | 28-settings-list.phone.de: a clean list of 8 sections with ~70 px rows and chevrons. 22-settings-hints.phone.de: toggles sit at the right of each row. |
| 8 a11y | 6 | 24-settings-backup.phone.de: steppers "-"/"+" ~28 px round, plus "Zeig auf einen Platz ... Ein Klick" hover copy. 25-settings-privacy.phone.de: "Protokoll zeigen" disabled at 4.0:1 with no reason given. |

Findings:
- **keep**: 28-settings-list.phone.de, a settings index with one-line descriptions under each title ("Passkeys, Anmeldung und Handys mit Fingerabdruck"). It is easy to scan.
- 20-28 settings phone: the only way back is the ~11 px caps "< EINSTELLUNGEN" link at the top-left, with a hit height of ~16 px. The gear in the app bar is highlighted gold while inside settings (**keep** that state). Severity: slows a task. Suggestion: a larger back row.
- 24-settings-backup.phone.de: the retention timeline says "Zeig auf einen Platz, um die Sicherung darin zu sehen. Ein Klick auf einen vollen Platz zeigt sie unten in der Liste." This is hover wording on touch, and the slots are ~14x30 px. Severity: cosmetic, since the list below works. The steppers (~28 px) are tight for thumbs. Severity: slows a task. Suggestion: 40 px stepper buttons.
- 24-settings-backup.phone.de: the "Täglich/Wöchentlich/Monatlich/Jährlich für" steppers look editable while "Smart Recycle" (not "Eigene") is selected. It is unclear whether they apply. Severity: slows a task. Suggestion: disable or hide them unless "Eigene" is chosen.
- 20-settings-bank.phone.de: the long DE help text under "Bank-Anmeldung fällig in 90 Tagen" (9 lines at 12 px) is readable, but dense on phone. The segmented "30 Tage vorher / 15 Tage vorher / 7 Tage vorher" wraps to two lines per option in DE. It still works. Cosmetic.
- 20-settings-bank.phone.de: the access line reads "FinTS · Zugang •emo". The masking looks like a typo rather than an intentional mask. Cosmetic. Suggestion: mask fully ("••••") or show the full login name.
- 21-settings-categories.phone.de: the "Offline" badge is green (positive) while the text says "eingebautes Modell nicht gefunden", and the segmented control still shows "Eingebautes Modell" selected. The state contradicts itself. Severity: slows a task. Suggestion: a warning style plus "Nur Regeln" auto-selected, or explain the fallback.
- 21-settings-categories.phone.de: the native selects "Händler / enthält / Kategorie..." are ~36 px tall, two side by side, and fit at 390. OK.
- 22-settings-hints.phone.de: the segmented "Automatisch / Nächster Monat / Buchungsmonat" has "Nächster Monat" wrapping to two lines in DE. OK. **keep**: each toggle has a title plus a description.
- 25-settings-privacy.phone.de vs .en: in EN "Export" and "Show log" sit inline at the right. In DE the buttons drop below the text because of the longer strings. Both work; good responsive behaviour (**keep**). "Protokoll zeigen" is disabled (4.0:1) with the reason only implied by "Keine ausgehenden Verbindungen". Cosmetic.
- 26-settings-security.phone.de: the number inputs (30 Tage, 0 Min., 10 Versuche, 15 Min.) are ~32 px tall and narrow. "Abmelden" next to "Safari auf iPhone" is a borderless grey text button. Severity: cosmetic. Suggestion: give destructive per-device actions a visible button shape.
- 27-settings-account.phone.de: **keep** "Animationen: Voll / Ruhig / Aus" and the note that the system "Bewegung reduzieren" setting is respected. That is a strong accessibility feature. "Land: Nicht gewählt" while dates are already German-formatted is confusing. Cosmetic.
- 27-settings-account.phone.de: "Tipp: klick ein paar Mal aufs Logo" uses mouse wording. Cosmetic.
- 30-settings-connect-dialog.phone.de: a centred modal with the input "Name der Bank, Bankleitzahl oder IBAN" (~40 px, good). "Fertig, Abruf starten" is dimmed and disabled with no hint. The close "x" is top-right. Cosmetic.

## 34 Payday details

| Line | Score | Based on |
|---|---|---|
| 7 phone | 7 | 34-payday-details.phone.de: the breakdown "Kontostand jetzt / Geht noch ab / Frei verfügbar" is at the top and the upcoming payments are listed, with "Alle Fixkosten" at the bottom within thumb reach. |
| 8 a11y | 7 | 34-payday-details.phone.de: the "Frei verfügbar 5.170,65 €" green total is 24 px and also labelled in text. The "In 2 Tagen" group labels are ~11 px grey. |

Findings:
- **keep**: 34-payday-details.phone.de, the arithmetic of the hero is laid out as three lines. This is the best explanation of a computed number in the app.
- 34-payday-details.phone.en: "Free to spend" here vs "Available until payday" on the hero (01-overview.phone.en). DE uses "Frei verfügbar" in both places. Cosmetic (EN naming).
- 34-payday-details.phone.de: the sparplan rows wrap the ISIN and fund name over two lines ("Sparplan IE00BK5BQT80 Vanguard FTSE All-World U."). Fine, but noisy. Cosmetic.

## 40/41 Wizard, 42 Login

| Line | Score | Based on |
|---|---|---|
| 7 phone | 7 | 40-wizard-account.phone.de: labelled inputs ~40 px tall with labels above, and "Weiter" bottom-right. 42-login.phone.de: the card is vertically centred, which leaves the language switch within thumb reach. |
| 8 a11y | 6 | 42-login.phone.de: the focused "Benutzername" field shows a clear gold focus ring (good), but the disabled "Anmelden" button text is at 3.1:1. 40-wizard-account.phone.de: the disabled "Weiter" is at 2.9:1. |

Findings:
- **keep**: 42-login.phone.de, a visible 2 px gold focus ring on the focused field. This is the only screenshot that shows keyboard focus, and it is clearly visible.
- 40-wizard-account.phone.de / 42-login.phone.de: the primary buttons start disabled with dark text on muted gold (2.9-3.1:1). They look like a "pressed" or "loading" state rather than a disabled one, with no hint of what is missing. Severity: slows a task. Suggestion: keep the button enabled and validate on submit with inline errors. Or, if it stays disabled, keep it legible and add "Fülle alle Felder aus".
- 41-wizard-country.phone.de: "Überspringen, vorerst CSV-Dateien nutzen" is a right-aligned text link that breaks across two lines at "CSV-/Dateien", above the "Weiter" button. Two competing actions are stacked at the right edge. Severity: cosmetic. Suggestion: a full-width secondary button "Ohne Bank weiter (CSV)".
- 41-wizard-country.phone.en: the UK variant replaces the bank search with a clear info box "Automatic bank sync works with German banks." (**keep**).
- 40-wizard-account.phone.de: the progress bar has five segments with no "Schritt 1 von 5" text. Screen-reader and low-vision users get no step count. Cosmetic.

---

## Score summary (line 7 phone / line 8 accessibility)

| Screen | 7 | 8 |
|---|---|---|
| 01 Overview / 31 hidden | 7 | 6 |
| 02/04 Transactions, 03 review, 06 empty | 6 | 5 |
| 05 Edit sheet | 6 | 6 |
| 07 Spending, 08 group, 33 menu | 6 | 5 |
| 09/10 Drill-downs | 7 | 6 |
| 11/12/13 Fixed costs | 6 | 5 |
| 14 Net worth | 7 | 6 |
| 15-19 Investments / 32 hidden | 7 | 6 |
| 20-28, 30 Settings | 7 | 6 |
| 34 Payday details | 7 | 7 |
| 40-42 Wizard / login | 7 | 6 |

Lines 1-6 and 9: "-" (outside this role).

## Top 10

1. **13-recurring-orbit.phone.de/en, orbit view**: overlapping planets, a hidden centre label and truncated names make tapping a payment impossible at 390 px. Blocks a task on phone. Hide "Orbit" on narrow screens, or render it as a ring-grouped list.
2. **07-spending.phone.de, "Dein Jahr in Tagen" heatmap**: ~8 px day cells, yet the card says "Klick zeigt die Umsätze des Tages". Blocks a task on phone. Tap a week or month instead, or provide a day list.
3. **Mouse wording on touch screens**, in 01-overview.phone.de ("Zeig auf ein Band ... Klick"), 07, 11, 13, 15 ("ein Klick zeigt alles"), 18, 24 ("Zeig auf einen Platz") and 27, while 15/16/19 correctly say "Mit zwei Fingern vergrößern" / "tippen oder ziehen". Slows a task. Use touch copy on coarse pointers.
4. **03-transactions-review.phone.de**: "Zu prüfen 39" vs "8 Umsätze", and "Jan – Okt 2026" vs "Alle Zeiträume" on the same screen. Slows a task. Make the badge count and the period consistent with the list.
5. **02/03-transactions.phone.de**: review-needed rows are marked only by a 3 px gold left bar, which is a colour/position-only signal. Slows a task. Add a text or icon marker.
6. **05-transactions-edit.phone.de**: the currently selected category ("Tanken") is below the fold in DE, and the chips are ~28 px tall. Slows a task. Show the current category under the amount and enlarge the chips.
7. **Small touch targets across phone**: filter segmented control ~30 px (02), insight dismiss "x" ~28 px (01), backup steppers ~28 px (24), horizon chips ~28 px (16), "Nicht zählen" ~18 px (18), breadcrumb back links ~16 px (09/10/20-28). Slows a task. Use a 44 px minimum hit area.
8. **12-recurring-calendar.phone.de**: "Dauerauftrag" vs "Gehalt" dots are near-identical teal/green, and the in-cell amounts are ~8-9 px. Slows a task. Use distinct shapes or hues and drop the in-cell amounts on phone.
9. **40-wizard-account.phone.de / 42-login.phone.de / 30-settings-connect-dialog.phone.de**: disabled primary buttons (2.9-3.1:1) with no hint of what is missing. Slows a task. Validate on submit, or add a reason.
10. **Truncation of identifying text in DE/EN**: the search placeholder "...Kategorie oder Betr" (02 de), the savings plans "Vanguard FTSE All-W..." / "iShares Core MSCI EM..." (14), "Stadtwerke Muench..." cut by a badge (11), "Persönliches · mehr Erstattungen..." (07). Cosmetic. Allow two lines or move badges to the second line.

Keep (most important): contrast of all grey text measured at 4.7-6.1:1 on the dark surfaces; the ~97 px bottom-nav items; the "Animationen Voll/Ruhig/Aus" setting that honours reduced motion (27); the visible gold focus ring (42); the touch-aware chart hints (15/16/19); the three-line payday breakdown (34); the text alternatives under charts (07 summary lines, 12 "Tag für Tag").
