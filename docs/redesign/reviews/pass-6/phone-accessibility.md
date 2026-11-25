# Groschen: phone and accessibility review

Role: phone and accessibility. I looked at every `phone.de` and `phone.en` screenshot. I compared them side by side, at 1x and enlarged. I also checked desktop where it mattered: `01-overview.desk.de` and `02-transactions.desk.de`. The scores cover only line 3 (task efficiency on a phone), line 6 (consistency between languages and sizes), line 7 (phone experience) and line 8 (accessibility). The other lines are "-".

## How I measured

- **Sizes.** The phone captures are 390 CSS px wide at 1x, so 1 image px is 1 CSS px. Every touch-target size below was read straight from the image.
- **Contrast.** I computed WCAG ratios with PIL from the most common background pixel and the darkest or brightest stroke pixel. Values for anti-aliased small text are best-case.
  - Card surface is about #121418, page background about #0A0B0D.
  - Secondary grey text is about #7A7F88 on the card, which gives **4.3-4.7:1**. Example: `15-investments.phone.de` "Sparplan 300,00 € pro Monat" is 4.58:1. Chart axis labels such as "10k €" measure 4.26:1.
  - Inactive tab and nav labels are about #8D919A on #0D0E11, which gives **6.1:1**. That is fine.
  - Muted ghost buttons and disabled-looking buttons are about #747679 on #14161B, which gives **3.97:1**. This fails AA for normal text. Examples: `25-settings-privacy.phone.de` "Protokoll zeigen" and `21-settings-categories.phone.de` "Regel hinzufügen".
  - The dimmed gold primary button has dark text on #6E6145, which gives **2.9-3.1:1**. Examples: `42-login.phone.*` "Anmelden"/"Log in", `40-wizard-account.phone.*` "Weiter"/"Continue", `30-settings-connect-dialog.phone.*`, `08-spending-group-dialog.phone.*`.
  - Bright gold text and accents on the dark surface are 8.8-12.9:1.
- **Type sizes.** Body text is about 14-15 px. Secondary text is about 12-13 px. Several data labels are only about 8-10 px: chart axes, calendar amounts, bottom-nav labels, savings-plan month labels and chips. Uppercase section labels are about 11 px with wide letter spacing.
- **Fixed bars.** The bottom tab bar is 4 × ~97 px wide and ~65 px tall, which is good. The top bar has a 33 × 33 px privacy (eye) button and a 33 × 33 px gear button.

---

## 01 Overview and 31 Hidden overview (`01-overview.phone.de/en`, `31-hidden-overview.phone.de/en`)

| Line | Score | Based on |
|---|---|---|
| 1-2, 4-5, 9 | - | |
| 3 task efficiency | 7 | `01-overview.phone.de`: the hero and the "14 Zahlungen kommen noch · 2.597,40 €" link sit above the fold. The hints card's "Prüfen"/"Zeigen" pills are 30 px tall. |
| 6 consistency | 7 | `01-overview.phone.en` vs `.de`: the layout is the same in both languages. The hint text wraps the same way. |
| 7 phone experience | 7 | `01-overview.phone.de`: the bottom tab bar (65 px, 4 equal items, active pill) is good. The hint dismiss "×" buttons are only ~28 × 28 px. The period picker sits top-right, out of thumb reach. |
| 8 accessibility | 6 | `01-overview.phone.de`: the Sankey hint "Zeig auf ein Band, um ihm zu folgen" is an instruction you can't follow on touch. The Sankey value labels are ~10 px. Sankey category labels in `31-hidden-overview.phone.de` such as "Abos" and "Versicherungen" are ~12 px, with ~10 px values. |

Findings
- **Hint dismiss × too small.** `01-overview.phone.de`, the dismiss "×" on "Neu dabei: Apple" and "August 2026 lag 42 %…": the buttons are ~28 px. The two × buttons stack close together, so you can mis-tap. Severity: slows a task. Suggestion: 44 × 44 px hit area, or swipe to dismiss.
- **Hover wording on touch.** `01-overview.phone.de/en`, the Sankey subtitle "Zeig auf ein Band… Klick zeigt die Umsätze" / "Point at a band… click…": this is hover-and-click wording on a touch screen. Severity: cosmetic. Suggestion: use "Tippe auf ein Band" on touch, as the forecast screen already does with "Auf den Graphen tippen".
- **Payday timeline too fine.** `01-overview.phone.de`, the payday tick strip (~28 ticks in ~300 px): each tick is ~6 px wide, so single days can't be tapped. Payment dots are colour-only. Severity: cosmetic, because the "14 Zahlungen kommen noch" link gives the same data as text. Keep the link.
- **Keep: blurred amounts in hidden mode.** `31-hidden-overview.phone.de`: the blurred 9s keep the layout stable, and the active eye button gets a gold fill, so the mode is visible.
- **Keep: tab bar.** The bottom tab bar has icon plus label, the active state has a filled pill, and the Umsätze badge dot is there.
- **Desktop/phone parity.** `02-transactions.desk.de` shows the review count "39" in the sidebar badge. On phone, the bottom-nav "Umsätze" item shows only an unlabelled dot, and a screen reader can't speak a dot. Severity: cosmetic. Suggestion: show the number, or give the dot an aria-label "39 zu prüfen".

## 02 / 04 Transactions, 03 Needs review, 06 Empty (`02-…`, `03-…`, `04-…`, `06-transactions-empty.phone.*`)

| Line | Score | Based on |
|---|---|---|
| 3 | 7 | `02-transactions.phone.de`: the search, the filter segment "Alle / Zu prüfen 39 / Ohne Kategorie / Einnahmen" and the sort fit in one screen. Rows are ~60 px tall and the whole row is a target. |
| 6 | 6 | `06-transactions-empty.phone.de` vs `.en`: the page title sits ~110 px lower than on `02`, and DE and EN are offset differently (300 vs 325 px), so the layout jumps between states. |
| 7 | 7 | `02-transactions.phone.de`: list rows, logos and right-aligned amounts read well at 390 px. The capture runs to 5200 px with no paging or "load more" visible. |
| 8 | 6 | `02-transactions.phone.de`: the search placeholder is clipped mid-word ("…Kategorie oder Betr"). The "needs review" state is marked only by a thin gold left bar (`03-transactions-review.phone.de`, Hofladen rows) plus a dashed "Ohne Kategorie" chip. |

Findings
- **Search placeholder clipped (DE).** `02-transactions.phone.de` and `03-…phone.de`: the placeholder "Händler, Verwendungszweck, Kategorie oder Betr" is cut mid-word. The EN text "Search merchant, purpose, category or amount" fits. Severity: cosmetic. Suggestion: "Suchen: Händler, Zweck, Betrag…" or simply "Umsätze durchsuchen".
- **Summary line wraps.** `02-transactions.phone.de/en`: in the summary "Jan – Okt 2026 · 297 Umsätze · 42.057,91 € rein / 31.970,76 € raus", the "raus" figure wraps alone onto a second line, which breaks the in/out pair. Severity: cosmetic. Suggestion: put in and out together on line 2.
- **Review marker hard to see.** `03-transactions-review.phone.de`: the gold left bar is 3 px wide, and its meaning is not explained in the row. Severity: cosmetic. Keep it, but add the text or icon "zu prüfen" for colour-blind users and screen readers.
- **Clear-search × too small.** `06-transactions-empty.phone.de`: the clear "×" inside the search field is ~26 px. Severity: cosmetic.
- **Keep: empty state.** `06-…phone.*` has a clear empty state with a "Filter zurücksetzen" / "Clear filters" link right next to the count.
- **Keep: filter segment wording.** "Zu prüfen 39" keeps the count readable inside the segment in both languages.

## 05 Transaction edit (`05-transactions-edit.phone.*`)

| Line | Score | Based on |
|---|---|---|
| 3 | 7 | `05-transactions-edit.phone.de`: the category chips are ~33 px tall and one tap each. "Speichern" sits bottom-right in the thumb zone. |
| 6 | 6 | `05-…phone.en` shows the current category "Fuel" highlighted just above the footer. In `.de` the current category "Tanken" (MOBILITÄT) sits below the visible area, so the user cannot see what is selected. |
| 7 | 7 | `05-…phone.de`: the modal uses the full height and the footer stays fixed. The close "×" is 33 px and sits top-right, out of reach. |
| 8 | 6 | `05-…phone.de`: the "+ Neu" chips have a dashed outline and low-contrast text. The toggle "Diese Kategorie für alle Umsätze…" has its label above it instead of in the same row, which makes the pairing less obvious. |

Findings
- **Selected category hidden.** `05-transactions-edit.phone.de`: the chosen category is not visible when the sheet opens. Severity: slows a task. Suggestion: scroll the selected chip into view, or show "Aktuell: Tanken" under the search field.
- **Not a bottom sheet.** `05-…phone.*`: the dialog is a top-anchored modal. Suggestion: a bottom sheet with a drag handle would put the close action within thumb reach too. Severity: cosmetic.
- **Keep: Save placement.** Primary "Speichern"/"Save" is bottom-right, with the secondary "Alles mit Shell ›" link on the left.

## 07 Spending, 08 New-group dialog, 33 Period menu (`07-spending.phone.*`, `08-…`, `33-period-menu.phone.*`)

| Line | Score | Based on |
|---|---|---|
| 3 | 6 | `07-spending.phone.de`: you can't tap donut segments (slivers ~4-8 px); the list below with "›" rows (~45 px) is the usable path. |
| 6 | 7 | `07-…phone.de/en`: the layout is the same in both languages. "Persönliches · mehr Erstattungen…" and "Personal · more refunds than spe…" are both truncated. |
| 7 | 5 | `07-spending.phone.de`, "Dein Jahr in Tagen": the heatmap cells are ~8 × 8 px, yet the copy says "Klick zeigt die Umsätze des Tages". |
| 8 | 5 | `07-…phone.de`: the heatmap uses colour only (violet → yellow), and its month and day labels are ~10 px. The disabled "›" year arrow is barely visible. In `33-period-menu.phone.de`, the menu items are ~37 px and the checked item uses both gold and a ✓, which is good. |

Findings
- **Heatmap days too small to tap.** `07-spending.phone.de/en`, the day heatmap: ~8 px squares can't be tapped reliably on touch, so the promised "click a day" doesn't work on a phone. Severity: blocks a task on phone. Suggestion: on phone, show one month at a time with ~40 px cells (like `12-recurring-calendar`), or allow tap-and-drag with a magnifier tooltip.
- **Truncated row label.** `07-spending.phone.de`, the row "Persönliches · mehr Erstattungen…": the important qualifier is cut off. Severity: cosmetic. Suggestion: move the qualifier to a second line.
- **Keep: menu tap targets.** `33-period-menu.phone.*`: the menu items are big enough, and the open picker gets a gold outline. Note that the menu covers the chart title, so "Aufteilung der Ausg…" is clipped. That's acceptable for a popover.
- **Dimmed Save.** `08-spending-group-dialog.phone.de`: "Speichern" is dimmed at ~3:1, and the placeholder "Auto" in the name field looks like an entered value. Severity: cosmetic. Suggestion: an explicit disabled style with a hint ("Name eingeben"), and a lighter placeholder.
- **Small icon picker.** `08-…phone.*`: the four icon buttons are ~40 × 30 px. Severity: cosmetic.

## 09 Drill group, 10 Drill category (`09-drill-group.phone.*`, `10-drill-category.phone.*`)

| Line | Score | Based on |
|---|---|---|
| 3 | 7 | `09-drill-group.phone.de`: the "Top-Händler" rows have "›" and are ~45 px tall. |
| 6 | 5 | `09-drill-group.phone.de` vs `.en`: the long DE title "Essen & Trinken" pushes the period picker onto its own row. EN "Food & Dining" keeps it inline. The DE page is ~70 px taller and the picker moves left. |
| 7 | 6 | `10-drill-category.phone.de`: the breadcrumb "‹ AUSGABEN › ESSEN & TRINKEN" is ~11 px caps with ~18 px hit height, and it is the only "back" control besides the browser. |
| 8 | 6 | `09-…phone.de`: the bar-chart axis labels "600 €", "Jan" and "Mär" are ~9 px at ~4.3:1. The "Durchschnitt 348 €" label sits on top of the bars. |

Findings
- **Breadcrumb back target too small.** `10-drill-category.phone.de`, breadcrumb back: the target is too small for a primary back action. Severity: slows a task. Suggestion: a 44 px back button in the header, or make the whole breadcrumb row the target.
- **Picker position jumps (DE).** `09-drill-group.phone.de`: the period picker changes position depending on title length. Severity: cosmetic. Suggestion: always put the picker on its own row on phone, or always below the title.

## 11 Recurring list, 12 Calendar, 13 Orbit (`11-…`, `12-…`, `13-recurring-orbit.phone.*`)

| Line | Score | Based on |
|---|---|---|
| 3 | 7 | `11-recurring-list.phone.de`: "Als Nächstes" shows the next 3 payments first, and the "Laufend" rows are ~62 px. |
| 6 | 5 | `13-recurring-orbit.phone.de/en`: the sub-tab bar and title sit ~36 px lower than on `11`/`12`, so the layout jumps when you switch Liste → Orbit. |
| 7 | 6 | `12-recurring-calendar.phone.de`: the day cells are ~40 × 55 px, which is good. The segmented control "Liste / Kalender / Orbit" is only ~26 px tall. `13-…phone.de`: the orbit drawing is ~150 px tall in a ~600 px card, the planets overlap, and the labels collide ("im Monat" sits under a planet). |
| 8 | 5 | `12-…phone.de`: the cell amounts "-2.150 €" are ~8 px. The dots are distinguished only by colour (Bezahlt orange, Dauerauftrag teal, Gehalt green). `13-…phone.de`: the planets are the only targets, they overlap, and they are ~12-30 px. |

Findings
- **Orbit unusable on phone.** `13-recurring-orbit.phone.*`: the orbit is too small and its targets overlap, yet the copy says "Klick zeigt ihre Umsätze". Severity: blocks a task on phone. Suggestion: scale the orbit to the card width, or replace it on phone with the list grouped by rhythm.
- **Tiny calendar amounts.** `12-recurring-calendar.phone.de`: the in-cell amounts are ~8 px. Severity: cosmetic. Suggestion: drop the amounts from the cells on phone, since "Tag für Tag" below already lists them, or use 10-11 px.
- **Truncated names.** `11-recurring-list.phone.de`: "Hausverwaltung Kr…" and "Stadtwerke Muench…" are truncated because the "+7,00 €" badge takes width. Severity: cosmetic. Suggestion: move the change badge under the name.
- **Keep: calendar month.** `12-…phone.*` has a large today ring (gold outline on 30) and good month navigation.

## 14 Net worth (`14-networth.phone.*`)

| Line | Score | Based on |
|---|---|---|
| 6 | 6 | `14-networth.phone.de`: "Vanguard FTSE All-W…" and "iShares Core MSCI EM…" are cut by the "LÄUFT" badge. EN "Vanguard FTSE All-…" is cut even shorter by "RUNNING". |
| 7 | 7 | `14-networth.phone.de`: the savings-plan cards stack cleanly, and the "Konto hinzufügen" dashed card is a large target. |
| 8 | 5 | `14-networth.phone.de`: the coin-row month labels "Nov / Feb / Mai / Aug" are ~8 px grey. The 12 coins are identical, so you can't tell paid from missed without colour. |

Findings
- **Fund names truncated.** `14-networth.phone.*`: the fund name is the key identifier. Severity: cosmetic. Suggestion: put the status badge under the name, or allow two lines.
- **Plan dots carry no state.** `14-networth.phone.*`, coin row: if a missed month were ever shown only by colour or opacity, colour-blind users would miss it. Suggestion: use a hollow dot or a dash for missed months.

## 15 Investments, 32 Hidden investments (`15-investments.phone.*`, `32-hidden-investments.phone.*`)

| Line | Score | Based on |
|---|---|---|
| 3 | 7 | `15-investments.phone.de`: the depot value and its change are above the fold, and the holdings cards are whole-card targets with "›". |
| 6 | 5 | `15-investments.phone.en`: the holding chips "plan 50 € per month" + "Reinvests" wrap differently in the two cards, so "Reinvests" drops to its own line in the EM IMI card. DE says "Sparplan 250 € pro Monat" while EN says lower-case "plan 250 € per month". The justETF banner puts "Turn on" top-right in EN but "Einschalten" below the text in DE. |
| 7 | 7 | `15-…phone.de`: the chart includes the hint "Mit zwei Fingern vergrößern" for pinch-zoom, which is good for touch. The four sub-tabs "Depot / Analyse / Prognose / Einzahlungen" just fit at 390 px. |
| 8 | 6 | `15-…phone.de`: the chart axis labels are ~9 px at 4.26:1. The monthly gain/loss bars are red/green only, with a "+564 € / -429 €" scale. The "Einzahlungen" toggle is ~30 px tall. |

Findings
- **Chips wrap unevenly.** `15-investments.phone.en`: the chip row wrapping differs between the two holding cards. Severity: cosmetic. Suggestion: fix the chip order, keep the share bar on its own line, and keep the chips on one line.
- **Gain/loss bars colour-only.** `15-investments.phone.de`, gain/loss bars: position above or below zero helps, but give the axis a real 0 line label. Severity: cosmetic.
- **Keep: chart affordances.** The "Pinch with two fingers to zoom" hint and the "Money paid in" toggle with an inline label.

## 16 Forecast (`16-inv-forecast.phone.*`)

| Line | Score | Based on |
|---|---|---|
| 6 | 6 | `16-inv-forecast.phone.de`: the legend wraps "Eingezahlt" onto a second line. The EN legend fits on one line. |
| 7 | 6 | `16-…phone.de`: the horizon chips "1J … 30J" are ~27 px tall × ~35 px wide. The "eingezahlt" caption sits at the far left above the range bar and overlaps the start tick. |
| 8 | 5 | `16-…phone.de`: the in-chart "eingezahlt"/"paid in" label is ~7 px and drawn over the line. The four assumption tiles use ~12 px grey text at ~4.5:1. |

Findings
- **Small horizon chips.** `16-inv-forecast.phone.*`: these chips are a primary control. Severity: slows a task. Suggestion: 40 px tall segments spread across the full width.
- **Unreadable chart label.** `16-…phone.*`: the "paid in" label in the chart can't be read. Suggestion: use a legend swatch only, or 11 px text outside the plot. Severity: cosmetic.
- **Keep: touch wording.** "Auf den Graphen tippen oder ziehen" / "Tap or drag on the chart" is correct touch wording. Reuse it on the other charts.

## 17 Analysis (`17-inv-analysis.phone.*`)

| Line | Score | Based on |
|---|---|---|
| 7 | 7 | `17-inv-analysis.phone.de`: the month-return tiles are ~43 × 41 px, which are good targets. |
| 8 | 6 | `17-…phone.de`: the drawdown chart's y-axis label "-15 %" collides with the x-axis label "Dez 25". "ruhig"/"wild" are ~9 px at 4.8:1. "Umrandet: der beste und der schlechteste Monat" is drawn as an empty checkbox, which looks like a control but is only a legend. |

Findings
- **Legend looks like a checkbox.** `17-inv-analysis.phone.*`: a non-interactive checkbox glyph confuses touch and screen-reader users. Severity: cosmetic. Suggestion: use an outlined-square swatch that doesn't look like a form control.
- **Keep: values on the tiles.** The monthly tiles print signed values ("+8,2", "-5,9"), so red/green is never the only cue.

## 18 Pay-ins (`18-inv-payments.phone.*`)

| Line | Score | Based on |
|---|---|---|
| 7 | 6 | `18-inv-payments.phone.de`: the month rows are ~44 px. The per-item action "× Nicht zählen" is a ~20 px-high text button at the bottom-right of each row. |
| 8 | 6 | `18-…phone.de`: the purpose text "Sparplan IE00BKM4GZ66 iShs …" is truncated. "Kursverlauf importieren" is a bare text link with an icon. |

Findings
- **"Nicht zählen" target too small.** `18-inv-payments.phone.*`: this is a destructive-ish action with a small target and no confirmation visible. Severity: slows a task. Suggestion: ≥ 36 px tall, or put it behind row swipe or a row menu.

## 19 ETF detail (`19-etf.phone.*`)

| Line | Score | Based on |
|---|---|---|
| 6 | 6 | `19-etf.phone.de` vs `.en`: the justETF banner places its button differently, as on 15. |
| 7 | 7 | `19-…phone.de`: the range segment "1M 3M 6M 1J Max" is ~30 px tall. |
| 8 | 6 | `19-…phone.de`: the "Dein Schnitt 110,71 €" label sits on top of the price line and purchase dots. The "Thesaurierend" badge is ~10 px. |

## 20-27 Settings (`20-settings-bank` … `27-settings-account.phone.*`)

| Line | Score | Based on |
|---|---|---|
| 3 | 5 | `20-settings-bank.phone.de`: the settings sub-tab strip has 9 tabs and scrolls sideways, and only ~2.5 tabs are visible ("Bank & Import / Kategorien / Hinweise & Geha…"). There is no overview list. |
| 6 | 5 | The DE and EN layouts differ. `20-settings-bank.phone.de` stacks the 3 action buttons in 3 rows, EN uses 2. `21-settings-categories.phone.de` puts "Neu durchlaufen" under the text, EN puts "Run again" on the right. `24-settings-backup.phone.de` stacks "Jetzt sichern", EN puts it inline. On `23-settings-depot.phone.en` the title sits ~30 px lower than on DE. |
| 7 | 6 | Toggles are ~40 × 24 px with a large row target, which is good. Steppers "− 7 +" in `24-settings-backup.phone.de` are ~29 px. The segmented controls "Voll / Ruhig / Aus" in `27-settings-account.phone.de` are ~30 px tall. |
| 8 | 5 | `25-settings-privacy.phone.de`: the "Protokoll zeigen" button is #747679 on #14161B (3.97:1). `21-settings-categories.phone.de`: "Regel hinzufügen" is also 3.97:1. `24-settings-backup.phone.de`: the retention timeline's dashed outline slots are barely visible. Its copy "Zeig auf einen Platz" relies on hover. |

Findings
- **Sub-tab strip hard to scan.** `20-settings-bank.phone.de/en`, the sub-tab strip: nine sections behind a horizontal scroller, with faded edge glyphs ("Sic", "Ex", and a stray "I" at the right edge of `20-…phone.en`). This makes sections like Sicherheit or Konto hard to find. Severity: slows a task. Suggestion: on phone, make Settings a vertical list of sections (iOS style) that drills into each page.
- **Ghost buttons fail contrast.** `25-settings-privacy.phone.de` "Protokoll zeigen" and `21-…phone.de` "Regel hinzufügen" read as disabled but are presumably active, and both fail AA. Severity: slows a task. Suggestion: use the normal outline-button style (white text, ~12:1).
- **Long DE labels wrap.** `22-settings-hints.phone.de`: the segment "Automatisch / Nächster Monat / Buchungsmonat" forces "Nächster Monat" onto two lines. `20-settings-bank.phone.de`: "30 Tage vorher" wraps in all three segments, in EN too. Severity: cosmetic. Suggestion: use a stacked radio list on phone, or the short labels "30 T. / 15 T. / 7 T.".
- **Hover-only backup timeline.** `24-settings-backup.phone.*`: "Zeig auf einen Platz…" / "Point at a place…" depends on hover. Severity: cosmetic.
- **Inconsistent "Abmelden" style.** `26-settings-security.phone.de`: the per-device "Abmelden" for "Safari auf iPhone" is plain text with no border, while "Anzeigen" next to it has a border. Severity: cosmetic.
- **"Quellcode" looks like plain text.** `27-settings-account.phone.de`: "Quellcode" is a plain grey word with no link affordance.
- **Keep: toggle rows.** `22-settings-hints.phone.*`: the toggle rows have a bold title, a grey explanation and a right-aligned switch. The on-state is gold with a dark knob, the off-state a light knob on a dark track (11.5:1 knob vs surface). Both are clear.
- **Keep: animation setting.** `27-settings-account.phone.*`: "Animationen: Voll / Ruhig / Aus", with copy saying the system reduce-motion setting is honoured, which is good accessibility.
- **Keep: number inputs.** `26-settings-security.phone.*`: the number inputs have units right next to them ("Versuche", "Min.").

## 30 Connect bank dialog (`30-settings-connect-dialog.phone.*`)

| Line | Score | Based on |
|---|---|---|
| 7 | 7 | `30-…phone.de`: the field is 40 px tall and full width. The primary button sits bottom-right. |
| 8 | 5 | `30-…phone.de`: the dimmed "Fertig, Abruf starten" measures 3.06:1. A disabled control is exempt from AA, but nothing says why it is disabled. |

## 34 Payday details (`34-payday-details.phone.*`)

| Line | Score | Based on |
|---|---|---|
| 7 | 8 | `34-payday-details.phone.de`: there is a clear summary first: Kontostand jetzt − Geht noch ab = Frei verfügbar 5.170,65 € in large green. Then a list, and a footer button "Alle Fixkosten". Long names wrap to two lines instead of truncating. |
| 8 | 7 | `34-…phone.de`: the amounts are right-aligned and the text is 13-15 px. The close "×" is 33 px, top-right. |

- **Keep:** this is the best phone screen. Use the same pattern (summary, then list, then one footer action) for other details.

## 40-42 Wizard and login (`40-wizard-account`, `41-wizard-country`, `42-login.phone.*`)

| Line | Score | Based on |
|---|---|---|
| 6 | 5 | `41-wizard-country.phone.de` vs `.en`: DE (Deutschland) shows a long FinTS paragraph plus a bank field and a two-line link "Überspringen, vorerst CSV-Dateien nutzen". This is real content, but the stacked link-above-button footer looks unbalanced. |
| 7 | 7 | `40-wizard-account.phone.*`: the inputs are 40 px tall and full width, and "Weiter" is bottom-right. `42-login.phone.*`: the inputs and the "Anmelden" button are full width. |
| 8 | 6 | `42-login.phone.de`: the focused "Benutzername" input has a visible gold focus ring. The dimmed "Anmelden"/"Weiter" buttons are 2.9-3.1:1. The wizard step indicator (5 bars) has no text such as "Schritt 1 von 5". |

Findings
- **Focus ring.** `42-login.phone.*` is the only screen where a focus state is captured. It is clearly visible: keep it, and make sure every control uses the same ring.
- **No step text in the wizard.** `40-wizard-account.phone.*`, step bars: a screen reader user gets no step count. Severity: cosmetic. Suggestion: add "Schritt 1 von 5" text or an aria-label.
- **Unbalanced footer (DE).** `41-wizard-country.phone.de`: "Überspringen, vorerst CSV-Dateien nutzen" wraps centred above "Weiter". Severity: cosmetic. Suggestion: give it full width under the primary button, or use the shorter "Erstmal mit CSV-Dateien".
- **Disabled buttons give no reason.** `40/41/42 phone`: disabled primary buttons look the same as faded enabled ones. Severity: slows a task. Suggestion: keep them full-strength and show inline validation on tap, or add a hint ("Alle Felder ausfüllen").

---

## Top 10

1. **Charts on phone ask you to tap tiny targets or to hover** (blocks a task on phone).
   - `07-spending.phone.de` has ~8 px day squares, with the copy "Klick zeigt die Umsätze des Tages".
   - `13-recurring-orbit.phone.de` has overlapping 12-30 px planets in a ~150 px orbit, with the copy "Klick zeigt ihre Umsätze".
   - Fix: give the phone a month view or list fallback with ≥ 40 px targets.
2. **Settings sub-navigation is a 9-tab horizontal scroller** (`20-settings-bank.phone.de/en`). Only ~2.5 tabs are visible, with clipped glyphs ("Hinweise & Geha…", a stray "I"). This slows finding Sicherheit, Sicherungen and Konto. Fix: a vertical section list on phone.
3. **Many controls are under ~32 px tall** (slows a task).
   - Hint dismiss "×" ~28 px (`01-overview.phone.de`).
   - Horizon chips 27 px (`16-inv-forecast.phone.de`).
   - Liste/Kalender/Orbit segment 26 px (`11-recurring-list.phone.de`).
   - Backup steppers 29 px (`24-settings-backup.phone.de`).
   - "× Nicht zählen" ~20 px (`18-inv-payments.phone.de`).
   - Breadcrumb back ~18 px (`10-drill-category.phone.de`).
   - Fix: raise all of these to 44 px hit areas.
4. **Ghost and secondary buttons fail AA at 3.97:1** (slows a task). "Protokoll zeigen" (`25-settings-privacy.phone.de`) and "Regel hinzufügen" (`21-settings-categories.phone.de`) look disabled. Fix: use the standard outline-button colours.
5. **The edit sheet hides the current category** (slows a task). In `05-transactions-edit.phone.de` the selected "Tanken" is below the fold, while the EN capture shows "Fuel". Fix: auto-scroll to the selection, or show "Aktuell: …".
6. **Chart text is too small and collides** (cosmetic, but it adds up).
   - Axis and caption labels are 7-10 px at ~4.3:1: `15-investments.phone.de` axes, `16-inv-forecast.phone.de` "eingezahlt" drawn over the line, `12-recurring-calendar.phone.de` cell amounts ~8 px.
   - `17-inv-analysis.phone.de` has "-15 %" on top of "Dez 25".
   - `19-etf.phone.de` has "Dein Schnitt" over the line.
   - Fix: at least 11 px, and labels outside the plot.
7. **DE and EN layouts differ for the same screen** (cosmetic, consistency).
   - `09-drill-group.phone.de` moves the period picker onto its own row.
   - `20-settings-bank.phone.de` stacks the buttons in 3 rows (EN 2).
   - `21-settings-categories`, `24-settings-backup`, `15-investments` and `19-etf` move action buttons from inline to below in DE.
   - `06-transactions-empty`, `13-recurring-orbit` and `23-settings-depot` shift the page title down by 30-110 px.
   - Fix: one fixed phone layout per component (action always below the text) that does not depend on string length.
8. **German strings run long and get cut or wrap.**
   - Search placeholder cut at "…oder Betr" (`02-transactions.phone.de`).
   - "Nächster Monat" wraps in a segment (`22-settings-hints.phone.de`).
   - "Persönliches · mehr Erstattungen…" truncated (`07-spending.phone.de`).
   - Fund names cut by status badges (`14-networth.phone.de` "Vanguard FTSE All-W…"; EN is cut even shorter).
   - Fix: shorter strings, and badges placed under the names.
9. **Some state is shown by colour only, or by a bare dot.**
   - Needs-review is a 3 px gold bar (`03-transactions-review.phone.de`).
   - Calendar dot types (`12-recurring-calendar.phone.de`).
   - Heatmap intensity (`07-spending.phone.de`).
   - Bottom-nav review badge is a dot without a count, while desktop shows "39" (`01-overview.phone.de` vs `02-transactions.desk.de`).
   - The wizard step bars have no text (`40-wizard-account.phone.de`).
   - Fix: add text, icons or aria-labels.
10. **Keep these.**
    - The bottom tab bar: 4 × 97 × 65 px, icon plus label, active pill (all phone screens).
    - The payday sheet pattern: summary, list, footer action (`34-payday-details.phone.de`).
    - The visible gold focus ring (`42-login.phone.de`).
    - The animation setting that honours reduce-motion (`27-settings-account.phone.de`).
    - The touch-aware chart copy "Tap or drag" and "Pinch with two fingers to zoom" (`16-inv-forecast.phone.en`, `15-investments.phone.en`). Apply it to the Sankey, the backup timeline, the heatmap and the orbit, which still say "point"/"click".
    - The secondary grey text holds at about 4.5:1 almost everywhere. Don't dim it further.
