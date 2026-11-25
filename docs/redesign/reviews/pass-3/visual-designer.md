# Groschen, pass 3: visual designer review

Role: visual designer. I score hierarchy, consistency and visual craft, plus data presentation, phone experience and accessibility where they are visual questions (contrast, legibility, label collisions). The other lines are "-".
Coordinates are approximate pixels on the 1500 px desktop or 390 px phone capture.

## Overall impression
This is a confident dark finance UI with one family. The gold accent is used sparingly, cards share one radius and border, the type scale has a clear top (40 to 56 px hero figures, 28 px page titles, 15 px card titles, 11 px tracked eyebrows), and amounts are bold, right-aligned and tabular. Most problems come from the parts drifting apart: four different page-header patterns, two tab styles, native and custom selects side by side, half-empty hero cards, and a few charts with labels that collide or get cut off.

---

## 01-overview (desk.en / desk.de / phone.en / phone.de)
| Line | Score | Basis |
|---|---|---|
| 2 hierarchy | 8 | `01-overview.desk.en`: the "Available until payday" hero (5,170.65 € at ~56 px) clearly dominates. The KPI row is second and the Sankey third. |
| 4 data presentation | 7 | `01-overview.desk.en`: the Sankey's Salary-to-Income band is a solid 370×360 px slab (x 500-870), which spends space on a flow of 99.6 %. |
| 6 consistency | 6 | `01-overview.desk.en`: the "Saved" KPI figure sits at y≈525 while Income and Spending sit at y≈539. |
| 7 phone | 7 | `01-overview.phone.de`: the hero, KPI stack and vertical Sankey read well, and the "Worth a look" actions wrap under the text. |
| 8 accessibility | 6 | `01-overview.phone.de`: the Sankey caption "Zeig auf ein Band…" tells a touch user to point. The muted grey sublines (e.g. "Im Schnitt 3.353,86 € pro Monat") are around 4:1. |
| 9 visual craft | 8 | `01-overview.desk.en`: the payday bead timeline and the jar are distinctive and well finished. |

Findings
- `01-overview.desk.en`, KPI row (y 465-600): in the Saved card the figure sits ~14 px higher than in its neighbours, because the card puts the figure, a stacked bar and a ring side by side. In `01-overview.desk.de` the subline "…1.991,75 € bleibt liegen" wraps to 2 lines. That card becomes the tallest (y 465-618), and the three figures land at y 525 / 557 / 557. **Cosmetic.** Top-align all three cards and pin the figure baseline, or move the savings-rate ring under the figure.
- `01-overview.desk.en`, Sankey: the Salary → Income link is drawn as a full-height filled block (x 500-870, y 745-1105), the heaviest object on the page, yet it carries no information. The left labels sit far from their nodes (Salary label at x 450, node at x 500). The small right-hand categories (Transport to Uncategorized, y 1100-1310) are spaced 37 px apart, while the large ones get 60-80 px. **Cosmetic.** Drop the middle "Income" node, or narrow the link to a thin band with low opacity, and give the canvas width to the right-hand labels.
- `01-overview.desk.en` vs `01-overview.phone.de`, "Worth a look": the phone shows dismiss "×" buttons on each hint. The desktop shows none, so the same card has different affordances. **Slows a task** (no way to dismiss a hint on desktop). Show the × on hover on desktop.
- `01-overview.desk.en`, hero card: the jar (x 808-912) and the bead timeline (y 320-345) leave a dead zone at x 600-790, y 150-280. The card could be ~40 px shorter. **Cosmetic.**
- keep: the date eyebrow "FRIDAY 30 OCTOBER" over the page title, the gold "28 days to payday" number, the "Jan – Oct 2026" section rule above the KPIs, and the green, red and gold dot code for income, spending and saved.

## 02-transactions (desk.en / desk.de / phone.en / phone.de)
| Line | Score | Basis |
|---|---|---|
| 2 hierarchy | 7 | `02-transactions.desk.en`: the merchant name and the bold amount win, and the category pill and the account are secondary. |
| 4 data presentation | 7 | `02-transactions.desk.en`: day groups have daily totals, but only on some days. |
| 6 consistency | 5 | `02-transactions.desk.en`: day headers alternate between a muted grey style ("WEDNESDAY 28 OCTOBER", which has a total) and a bright white style ("TUESDAY 27 OCTOBER", which has none). |
| 7 phone | 7 | `02-transactions.phone.de`: the two-line rows with the pill under the name work well. The search placeholder is cut off at "…oder Betr" and the summary line wraps "31.970,76 € raus" onto a second line. |
| 9 visual craft | 7 | `02-transactions.desk.en`: the logo avatars and the dotted "Uncategorized" pill are good, but the middle of each row is empty. |

Findings
- `02-transactions.desk.en`, day headers (y 206, 405, 498, 643…): two visual weights for the same element. Days with more than one row get a grey 11 px header plus a total. Days with one row get a white header and no total. Scanning down, the list looks like it has two levels of grouping. **Slows a task.** Use one header style everywhere, and show the total on single-row days too, or never show it.
- `02-transactions.desk.en`, row layout: name at x 357, category pill right-aligned so its left edge wanders (x 997 to 1023), account at x 1157, amount at x 1437. That leaves a ~500 px empty band in the middle of every row. **Cosmetic.** Left-align the pills in a fixed column (e.g. x 900) and drop or narrow the "Girokonto" column. With one bank account it repeats the same word 297 times.
- `02-transactions.desk.en`, day totals (x ~1410, 11 px grey): set lighter and smaller than the row amounts and ~2 px out of their right edge. Fine as a secondary layer, but align the right edges. **Cosmetic.**
- `02-transactions.phone.de`, search field: the placeholder "Händler, Verwendungszweck, Kategorie oder Betr" is clipped. **Cosmetic.** Shorten it on phone ("Suchen…").
- keep: the refund progress line "32.00 € of 64.00 € back" with its mini bar (`02-transactions.desk.en`, Lena Berger), green incoming amounts, and the gold left marker on rows that need review.

## 03-transactions-review (all variants)
| Line | Score | Basis |
|---|---|---|
| 2 hierarchy | 6 | `03-transactions-review.desk.en`: the gold banner "These transactions need a category from you." is the loudest element on the page, but it is a 1175×68 px box holding one 15 px sentence and no action. |
| 6 consistency | 6 | `03-transactions-review.desk.en`: here every day header is white. On 02 they mix grey and white. The summary says "All periods" while the header chip still reads "Jan – Oct 2026". |
| 7 phone | 7 | `03-transactions-review.phone.de`: clean, and the gold review markers read well. |

Findings
- `03-transactions-review.desk.en`, banner (y 145-213): a large empty bar (x 660-1460). **Cosmetic.** Make it a compact inline note, or put the primary action in it ("Categorize next").
- `03-transactions-review.desk.en`, the "All periods" text in the summary row vs the "Jan – Oct 2026" chip in the header: two scopes shown at once. **Slows a task.** Dim or relabel the period chip while the review tab ignores the period.

## 04-transactions-filtered (all variants)
| Line | Score | Basis |
|---|---|---|
| 6 consistency | 8 | `04-transactions-filtered.desk.en`: the "Clear filters" gold link sits inline in the summary row, and the search field gets a clear "×". |
Finding: keep the inline "Clear filters" pattern (`04-transactions-filtered.desk.en`, x 699, y 153).

## 05-transactions-edit (all variants)
| Line | Score | Basis |
|---|---|---|
| 2 hierarchy | 8 | `05-transactions-edit.desk.en`: the 40 px "-56.30 €" with the merchant logo leads, the raw bank text sits in a mono box, and the chips are grouped by uppercase group labels. |
| 6 consistency | 6 | `05-transactions-edit.desk.en`: chips say "Housing (general)" here but "Housing" in the group dialog (`08-spending-group-dialog.desk.en`). |
| 7 phone | 7 | `05-transactions-edit.phone.de`: works as a full-height sheet with a sticky footer, but the "apply to every transaction from this merchant" toggle is not visible above the fold. |
| 9 visual craft | 8 | `05-transactions-edit.desk.en`: the selected "Fuel" chip in solid gold is unmistakable. |

Findings
- `05-transactions-edit.desk.en`: the title "Shell" (y 52) repeats next to the logo, whose figure and date line already name the transaction. The "SUBSCRIPTIONS" group label at y 807 is cut off by the sticky toggle row with no fade. **Cosmetic.** Add a scroll fade above the sticky area.
- `05-transactions-edit.desk.en`, the "Use this category for every transaction from this merchant" toggle: the on state is a gold track with a dark knob on the right. That reads as the inverse of the usual light-knob-on-colour toggle, and it is used everywhere (`20-settings-bank.desk.en`, `22-settings-hints.desk.en`). **Cosmetic.** Use a light knob on the gold track.
- keep: the raw bank text in a mono box, group colour dots on the chips, and "+ New" as a ghost chip.

## 06-transactions-empty (all variants)
| Line | Score | Basis |
|---|---|---|
| 9 visual craft | 7 | `06-transactions-empty.desk.en`: tidy empty card with a gold search icon. On desktop, everything below y 380 is empty. |
| 7 phone | 6 | `06-transactions-empty.phone.de`: the page header starts at y 190 instead of y 95 as on `02-transactions.phone.de`. The layout jumps down ~95 px. |
Finding: `06-transactions-empty.phone.de` has a vertical offset of the whole header, so the title moves between states. **Cosmetic.** Keep the header pinned at the same y.

## 07-spending (all variants)
| Line | Score | Basis |
|---|---|---|
| 2 hierarchy | 7 | `07-spending.desk.en`: the donut plus ranked bars is a clear primary block. "Your year in days" is secondary. |
| 4 data presentation | 6 | `07-spending.desk.en`: the two-ring donut has no key for the inner ring versus the outer ring. Blue Housing takes ~60 % of both rings, so the small groups are 2-4 px slivers. The heat map ramp runs violet → pink → orange → yellow, which is hard to order. |
| 6 consistency | 5 | `07-spending.desk.en`: the header puts a lone ghost button "+ Your own group" under the title (x 285-420, y 104) and a Spending/Income switch beside the period chip. No other page has this layout. |
| 7 phone | 6 | `07-spending.phone.de`: "Ausgaben" appears three times in the first 190 px (sub-tab, title, segmented control). The heat map shows only Jan-Jun. |
| 9 visual craft | 8 | `07-spending.desk.en`: the bar list rhythm (45 px rows, thin 3 px bars) is clean. |

Findings
- `07-spending.desk.en`, "+ Your own group" (y 104): an orphan dashed button floats between the title and the first card and adds 50 px of header. **Cosmetic.** Move it into the "Spending breakdown" card header next to Groups/Categories, or into a "…" menu.
- `07-spending.desk.en`, donut (x 333-625): no key explains the inner ring versus the outer ring. **Slows a task.** Label the rings ("groups / categories") or drop to one ring, since the list to the right already carries the numbers.
- `07-spending.desk.en`, "Personal · more refunds than spending  -162.37 €": the row has an empty bar and no percent. Visually it reads as missing data. **Cosmetic.** Show a small green "net refund" tag instead of an empty track.
- `07-spending.desk.en`, heat map legend "Less ■■■■■ More" (x 1300-1435): five hues across two colour families. Lightness does not rise steadily, so pink and orange days are hard to rank. **Slows a task.** Use a single-hue lightness ramp ending in gold.
- `07-spending.phone.de`: sub-tab "Ausgaben", H1 "Ausgaben" and segment "Ausgaben" are stacked. **Cosmetic.** On phone, drop the H1 or rename the segment ("Ausgaben / Einnahmen" → "Raus / Rein").
- keep: the "most on Housing (58 %)" summary line under the card title, and right-aligned amounts with a lighter percent column.

## 08-spending-group-dialog (all variants)
| Line | Score | Basis |
|---|---|---|
| 2 hierarchy | 6 | `08-spending-group-dialog.desk.en`: there is no label above the category chips. The chip groups start right after Name/Icon, so it is unclear that the chips are the main input. |
| 6 consistency | 6 | `08-spending-group-dialog.desk.en`: chips say "Housing" here and "Housing (general)" in `05-transactions-edit.desk.en`. The icon picker row has 4 icons and ~90 px of empty field. |
| 7 phone | 7 | `08-spending-group-dialog.phone.de`: good sheet with a sticky footer. |
Finding: `08-spending-group-dialog.desk.en`, the Save button (x 933-995, y 823) is a desaturated gold with no reason given. The user does not know a category is required. **Slows a task.** Add a "Categories" label with a hint ("pick at least one") and a live count, e.g. "Save (0)".

## 09-drill-group (all variants)
| Line | Score | Basis |
|---|---|---|
| 2 hierarchy | 8 | `09-drill-group.desk.en`: the hero "3,480.29 €" with the red "↑35 %" pill and the monthly bars sit side by side, and "Top merchants" and "Categories" follow as paired cards. |
| 4 data presentation | 6 | `09-drill-group.desk.en`: the "Average 348 €" label collides with the Sept/Oct bar tops (x 1325-1415, y 273). Categories lists two 0.00 € rows. |
| 6 consistency | 6 | `09-drill-group.desk.en`: category filter chips use square dots, while the rest of the app uses round dots. The phone version puts the period chip under the title (`09-drill-group.phone.de`, y 210), but `10-drill-category.phone.de` puts it to the right of the title. |
| 9 visual craft | 7 | `09-drill-group.desk.en`: the Categories card (x 880-1460) is about half empty (y 700-925). |
Findings
- `09-drill-group.desk.en`, the average label sits inside the plot over the bars. **Cosmetic.** Put it at the left end of the dashed line, outside the bar area.
- `09-drill-group.desk.en`, Categories card: "Food & Dining · 0× 0.00 €" and "Food delivery · 0× 0.00 €" add noise and leave ~220 px of empty card height next to Top merchants. **Cosmetic.** Hide zero rows, or let the card fit its content and put the transactions list beside it.
- keep: the "8 of 9" counter and the "· 14×" counts in muted type beside merchant names.

## 10-drill-category (all variants)
| Line | Score | Basis |
|---|---|---|
| 5 navigation and naming | 5 | `10-drill-category.desk.en`: the breadcrumb "‹ INCOME" sits above the H1 "Income", so the back link names the page you are already on. In 09 it correctly reads "‹ SPENDING". |
| 9 visual craft | 6 | `10-drill-category.desk.en`: two empty states stacked ("Nothing to chart" and "No transactions match"), each with its own icon disc. |
Finding: with no data, `10-drill-category.desk.en` shows the hero "0.00 €" at full 56 px plus two empty states. **Cosmetic.** Collapse to one empty state, shrink the hero, and fix the breadcrumb to point at the parent ("‹ SPENDING").

## 11-recurring-list (all variants)
| Line | Score | Basis |
|---|---|---|
| 2 hierarchy | 8 | `11-recurring-list.desk.en`: hero "1,407.01 €", a "Next up" stack, "What changed", then "Running". |
| 4 data presentation | 7 | `11-recurring-list.desk.en`: the amount column alternates between one-line and two-line cells ("≈ 27.07 € a month"), so the row heights and the amount baselines wobble. |
| 6 consistency | 7 | `11-recurring-list.desk.en`: the change badges (amber "+7.00 €", blue "Back"/"New") match the "What changed" icons. |
| 7 phone | 7 | `11-recurring-list.phone.de`: the phone drops "In X days" from the Running rows. The Next-up row truncates "Hausverwaltung Kr…". |
| 9 visual craft | 7 | `11-recurring-list.desk.en`: the hero card's left half (x 600-930, y 240-320) is empty. |
Findings
- `11-recurring-list.desk.en`, the Running list order (In 2, 3, 5, 16, 7, 19, 3 days…) is neither by date nor obviously by amount within type. With "In N days" printed on every row, the eye expects date order. **Slows a task.** Sort by amount and say so, or sort by next due date.
- `11-recurring-list.desk.en`, the monthly-equivalent sublines appear only on FitX, Rundfunkbeitrag, Lime and Allianz. **Cosmetic.** Reserve the second line on all rows, or show the monthly equivalent in a separate muted column.
- keep: the coloured left edge on the "Next up" rows and the dashed gold "3 savings plans run along" footer card.

## 12-recurring-calendar (all variants)
| Line | Score | Basis |
|---|---|---|
| 4 data presentation | 6 | `12-recurring-calendar.desk.en`: the in-cell chips truncate names to 2-5 characters ("Ha… -1,050 €", "Nor… 3,340 €"). Teal "Standing order" and green "Salary" are nearly the same hue in the legend. |
| 6 consistency | 6 | `12-recurring-calendar.desk.en`: the header says "1,423.48 € fixed costs", but the List view hero says "1,407.01 €" for the same thing, with no explanation. |
| 7 phone | 8 | `12-recurring-calendar.phone.de`: dot clusters with day sums fit 7 columns well. |
| 9 visual craft | 6 | `12-recurring-calendar.desk.en`: the calendar card ends at y 803 while "Day by day" runs to y 1325, leaving a ~800×520 px void. |
Findings
- `12-recurring-calendar.desk.en`: unbalanced columns, with a large empty area below the calendar. **Cosmetic.** Make the day list scroll inside a card the same height as the calendar, or move the list under the calendar.
- `12-recurring-calendar.desk.en`, chips: show only the amount in the cell (as the phone does with dots), with the name on hover. **Cosmetic.**
- `12-recurring-calendar.desk.en`, legend: "Standing order" (teal) vs "Salary" (green). **Slows a task** for colour-weak users. Use a distinct hue, or an outline style for salary.
- keep: the gold-ringed "today" cell (30) and the row separators in "Day by day".

## 13-recurring-orbit (all variants)
| Line | Score | Basis |
|---|---|---|
| 4 data presentation | 4 | `13-recurring-orbit.desk.en`: 13 payments, only 4 labelled, overlapping spheres at x 950-1110, and "Hausverwaltung Kr…" truncated. |
| 7 phone | 3 | `13-recurring-orbit.phone.de`: the whole orbit is squeezed into ~260×100 px, and spheres overlap the "1.407 €" centre label. It cannot be read. |
| 8 accessibility | 4 | `13-recurring-orbit.desk.en`: the "a month" sub-label under 1,407 € is dark gold on a gold glow, about 1.5:1. |
| 9 visual craft | 6 | `13-recurring-orbit.desk.en`: the shaded 3D spheres are the only skeuomorphic object in an otherwise flat UI. |
Finding: the orbit is a novelty view that gets in the way of reading on phone. **Slows a task.** On phone, hide it or swap in a radial/ring chart with a list. On desktop, label every planet, or list them below with matching colours.

## 14-networth (all variants)
| Line | Score | Basis |
|---|---|---|
| 2 hierarchy | 8 | `14-networth.desk.en`: the 56 px "44,931.92 €" with the gold area chart is a strong hero, and the account tiles follow. |
| 6 consistency | 7 | `14-networth.desk.en`: the savings plans total "1,100.00 € a month" sits right-aligned in the card header, while on phone (`14-networth.phone.de`) it moves under the description. Fine, but note that 15-investments says "Savings plan 300.00 € per month". |
| 7 phone | 7 | `14-networth.phone.de`: long but clean. Each account card takes ~140 px, so the screen holds about 4 accounts. |
| 9 visual craft | 7 | `14-networth.desk.en`: the hero card's left column is empty from y 240 to y 430 (~340×190 px). The account-tile percentages ("17%") are ~9 px. |
Findings
- `14-networth.desk.en`: the empty area in the hero's left column under the figure. **Cosmetic.** Add a small breakdown (cash / depot) there, or shorten the card.
- `14-networth.desk.en`, the "Direkt-Depot" subline is truncated ("30 Oct 20…") because of the chevron. **Cosmetic.**
- `14-networth.desk.en`, savings plan coin rows: 12 identical gold coins per plan only work as decoration. They give no amounts and no gaps. **Cosmetic.** Keep them, but mark missed months clearly.
- keep: the dashed "Add account" tile as the last item in the grid, and the green "RUNNING" status pills.

## 15-investments (all variants)
| Line | Score | Basis |
|---|---|---|
| 2 hierarchy | 7 | `15-investments.desk.en`: hero value, price line and gain/loss bars. The gain/loss value labels (-111 €, +47 €) are 10 px red and green on dark. |
| 6 consistency | 6 | `15-investments.desk.en`: this page puts the "Get full price histories?" banner at the bottom, but `19-etf.desk.en` puts it at the top, above the hero. The legend shows only a green square for "Gain and loss", but half the bars are red. |
| 7 phone | 7 | `15-investments.phone.de`: the chart compresses well, and the holdings stack. |
| 9 visual craft | 7 | `15-investments.desk.en`: the Holdings grid places 2 cards in 3 columns, leaving x 1055-1435 empty. The hero's left column is empty from y 310 to y 650. |
Findings
- `15-investments.desk.en`, Holdings: the two cards use 2/3 of the width. **Cosmetic.** Let 2 cards share the full width (50/50).
- `15-investments.desk.en`, the "85% of the depot" / "15% of the depot" labels are ~10 px muted grey. **Cosmetic.** Raise to 12 px.
- keep: the IBM-style mono ISIN under each fund name, the allocation bar at the top of Holdings, and the gold "plan 250 € per month" pill.

## 16-inv-forecast (all variants)
| Line | Score | Basis |
|---|---|---|
| 2 hierarchy | 7 | `16-inv-forecast.desk.en`: "68,412 €" with a range slider from bad to good case is a strong focus. The four assumption cards above it have the same weight as each other and compete with it. |
| 6 consistency | 7 | `16-inv-forecast.desk.en`: the legend (top right, y 155) sits 250 px away from the chart it explains (y 400-680). |
| 7 phone | 7 | `16-inv-forecast.phone.de`: the "eingezahlt" tick label hangs outside the card padding at x 28. |
Finding: `16-inv-forecast.desk.en`, the tiny "paid in" tick label (y 433, ~9 px) collides with the range bar. **Cosmetic.** Move the legend next to the chart, and the tick label below the bar.

## 17-inv-analysis (all variants)
| Line | Score | Basis |
|---|---|---|
| 4 data presentation | 7 | `17-inv-analysis.desk.en`: the monthly-returns heat strip and the drawdown chart are clear. The "Outlined: the best and the worst month" legend uses a checkbox glyph, so it looks interactive. |
| 7 phone | 6 | `17-inv-analysis.phone.de`: the monthly returns show Jan-Jun only, and Jul-Oct are not visible (no scroll cue). |
| 9 visual craft | 8 | `17-inv-analysis.desk.en`: the calm-to-wild gradient gauge is well done, although the "calm/wild" labels are ~9 px. |
Finding: `17-inv-analysis.phone.de`, the Monatsrenditen strip cuts off after June. **Slows a task.** Wrap to two rows of 6 months.

## 18-inv-payments (all variants)
| Line | Score | Basis |
|---|---|---|
| 2 hierarchy | 8 | `18-inv-payments.desk.en`: the month accordion with the total at the right is simple and well aligned. |
| 6 consistency | 7 | `18-inv-payments.desk.en`: "Don't count" with "×" is quiet. The import strip is a plain card with its action at the far right. |
Finding: keep this page's compact rhythm (44 px rows). **Cosmetic:** on `18-inv-payments.phone.de` the "Nicht zählen" link sits on a separate line from its amount, so each pay-in takes 3 lines.

## 19-etf (all variants)
| Line | Score | Basis |
|---|---|---|
| 5 navigation and naming | 5 | `19-etf.desk.en`: the in-page tabs "Overview / Analysis / Forecast" repeat sidebar entries with the same names but a different scope (fund vs depot). |
| 6 consistency | 5 | `19-etf.desk.en`: the underline tabs here, segmented pills on Fixed costs and Spending, and underline tabs in Settings give three tab treatments for one concept. |
| 9 visual craft | 7 | `19-etf.desk.en`: the hero's left column is empty from y 500 to y 735. A footnote floats outside the card at y 765. |
Finding: `19-etf.desk.en`, the justETF banner (y 218-278) pushes the hero down on the main detail page. **Cosmetic.** Move it to the bottom as on 15, and pick one tab style (underline for page-level views, segmented for chart modes).

## 20-27 Settings (all variants)
| Line | Score | Basis |
|---|---|---|
| 2 hierarchy | 7 | `22-settings-hints.desk.en`: an even 82 px row rhythm, with label plus help text left and control right. |
| 6 consistency | 5 | Native `<select>` with the browser chevron on `20-settings-bank.desk.en` ("Every day at 06:00"), `21-settings-categories.desk.en` (the rule builder) and `27-settings-account.desk.en` (Country, Currency), next to the custom "03:00 ⌄" select on `24-settings-backup.desk.en` and the custom period chip. |
| 7 phone | 6 | `20-settings-bank.phone.de`: the 8-tab row is clipped ("Hinweise & Gehal…") with no fade or arrow. `24-settings-backup.phone.de`: the backup timeline loses its "1 pro Jahr / 1 pro Monat" labels and the slots overlap. |
| 8 accessibility | 6 | `21-settings-categories.desk.en`: the "Offline" status pill is green, the same treatment as "Connected" on `20-settings-bank.desk.en`. |
| 9 visual craft | 7 | `24-settings-backup.desk.en`: the backup slot timeline is a nice touch. |
Findings
- Settings uses mixed control styles: native selects of three different widths in one card (`27-settings-account.desk.en`: "Not chosen" 138 px, "EUR · Euro" 195 px, "English" 115 px). **Cosmetic.** Use the custom select everywhere at one fixed width.
- `23-settings-depot.desk.en`, `26-settings-security.desk.en`: the number inputs with unit suffixes ("%", "€", "days", "min") don't share a right edge, so the inputs start at x 1322-1336. **Cosmetic.** Use a fixed suffix column.
- `21-settings-categories.desk.en`: the "Offline" pill is in success green, and the "Built-in model" segment is selected while the subline says "(built-in model not found)". **Slows a task.** Make it a neutral or amber pill, and show the real active mode.
- `25-settings-privacy.desk.en`: the Export card repeats the backups note ("Backups never contain the key…"), which is copy in the wrong place. "Show log" looks disabled (grey border, grey text). **Cosmetic.**
- `26-settings-security.desk.en`, Logged-in devices: "Log out" on the Safari row is plain text while "Show" two rows below is a bordered button. **Cosmetic.**
- `24-settings-backup.desk.en`: the "Back up now" primary button uses a "+" icon. **Cosmetic.** Use a save or upload icon.
- `20-settings-bank.phone.de`, the tab strip: add an edge fade, or a select-style switcher on phone.
- keep: the "Bank login needed within 90 days" green progress bar with its explanatory paragraph, and the "This device" pill.

## 30-settings-connect-dialog (all variants)
| Line | Score | Basis |
|---|---|---|
| 2 hierarchy | 6 | `30-settings-connect-dialog.desk.en`: the error "No bank found by that name…" shows on an empty field in body grey, styled the same as the help line above it. "Done, start syncing" looks enabled even though no bank has been chosen. |
| 7 phone | 7 | `30-settings-connect-dialog.phone.de`: the dialog fits well. |
Finding: `30-settings-connect-dialog.desk.en`: the error state shows before any input, and nothing marks it as an error. **Slows a task.** Hide it until a search runs, then show it in amber or red with an icon. Disable the primary button until a bank is picked.

## 31-hidden-overview / 32-hidden-investments
| Line | Score | Basis |
|---|---|---|
| 6 consistency | 8 | `31-hidden-overview.desk.en`: every amount is blurred to a 9s mask at the same width, and the eye toggle in the sidebar header turns gold. |
| 9 visual craft | 8 | `32-hidden-investments.phone.de`: even the axis labels are masked ("9.9k €"). |
Finding: `31-hidden-overview.desk.en`: the percentages (99.6 %, 24.1 %), the savings-rate ring (39 %) and the sparkline heights stay visible, so the proportions still show. Acceptable. keep the consistent blur style.

## 33-period-menu
| Line | Score | Basis |
|---|---|---|
| 9 visual craft | 7 | `33-period-menu.desk.en`: a clean menu with the gold selected item and a check. It has no custom-range entry and no date hints next to presets ("Last 12 months" → "Nov 2025 – Oct 2026"). |
| 7 phone | 7 | `33-period-menu.phone.de`: the menu opens as an anchored popover rather than a bottom sheet. Acceptable at this size. |

## 40-41 Wizard and 42 login
| Line | Score | Basis |
|---|---|---|
| 2 hierarchy | 7 | `40-wizard-account.desk.en`: the step rail with numbered circles and a gold active ring is clear. The form leaves ~150 px empty above the footer. |
| 8 accessibility | 5 | `42-login.desk.en`: the disabled "Log in" has dark text on muted gold (x 586-914, y 562-597), about 3:1. The same applies to "Continue" on `40-wizard-account.desk.en`. |
| 7 phone | 6 | `41-wizard-country.phone.de`: the "Überspringen, vorerst CSV-Dateien nutzen" link is centred on 2 lines and sits above the "Weiter" button instead of beside it. As in 30, the bank search shows its "not found" error before any input. |
| 9 visual craft | 8 | `42-login.desk.en`: a compact centred card with the logo and a focused gold-ring input. Good. |
Finding: the disabled primary buttons only lower the gold's saturation, so they read as a dimmer gold rather than as disabled (`40-wizard-account.desk.en`, `42-login.desk.en`, `08-spending-group-dialog.desk.en`). **Slows a task.** Use a neutral grey fill for disabled buttons and keep gold for enabled ones.

---

## Cross-screen consistency notes
- **Four page-header patterns:** eyebrow date + H1 + period chip (`01-overview.desk.en`). H1 + period chip at y 50 (`02-transactions.desk.en`, `14-networth.desk.en`). H1 + segmented switch + chip + orphan button (`07-spending.desk.en`). Breadcrumb + H1 (`09-drill-group.desk.en`, `15-investments.desk.en`). The title baseline moves between y 50 and y 75 across top-level pages.
- **Three tab styles:** underline (`19-etf.desk.en`, Settings, phone sub-nav), segmented pill (`11-recurring-list.desk.en` List/Calendar/Orbit, `07-spending.desk.en`), and ghost chips (`09-drill-group.desk.en` filters).
- **Naming drift between desk and phone:** "Investments" (sidebar, `15-investments.desk.en`) vs "Depot" (`15-investments.phone.de` tab, and the sidebar in `01-overview.desk.de`) vs the Settings tab "Investments". The desk.de sidebar uses "Depot", so the inconsistency is in the English copy.

---

## Top 10
1. `13-recurring-orbit.phone.de`, orbit chart: compressed to ~260×100 px with spheres over the total. It cannot be read on phone, and on desktop only 4 of 13 payments are labelled. Slows a task. Replace with a list or ring chart on phone, and label all items on desktop.
2. `02-transactions.desk.en`, day headers: two styles (grey with a total, white without) for the same element, so the list looks like it has two levels of grouping. Slows a task. Unify.
3. `30-settings-connect-dialog.desk.en` and `41-wizard-country.phone.de`, bank search: the "No bank found" error shows on an empty field in body-grey, and the primary button looks enabled. Slows a task.
4. Disabled primary buttons (`42-login.desk.en` "Log in", `40-wizard-account.desk.en` "Continue", `08-spending-group-dialog.desk.en` "Save"): dimmed gold with dark text at about 3:1, and no reason given. Slows a task. Use a neutral disabled style and an inline hint.
5. `07-spending.desk.en`, donut and heat map: no key for the inner and outer rings, and a five-hue violet→yellow ramp that cannot be ranked by lightness. Slows a task. Use one ring and a single-hue ramp.
6. Page-header and tab inconsistency across `01-overview.desk.en`, `02-transactions.desk.en`, `07-spending.desk.en` and `19-etf.desk.en`: four header layouts and three tab styles. Cosmetic, but it is the main thing that makes the app feel less polished.
7. `12-recurring-calendar.desk.en`: an ~800×520 px void under the calendar, chip names truncated to "Ha…", and "1,423.48 €" here vs "1,407.01 €" on the list view without explanation. Slows a task.
8. `01-overview.desk.en`/`desk.de`, KPI row: the Saved figure sits 14-32 px higher than the Income and Spending figures. The Sankey's Salary→Income slab is the heaviest object on the page yet carries no information. Cosmetic.
9. Settings controls (`20-settings-bank.desk.en`, `27-settings-account.desk.en`, `21-settings-categories.desk.en`): native browser selects of three widths next to custom selects. The green "Offline" pill signals success for a degraded state. Cosmetic / slows a task.
10. Half-empty hero cards (`14-networth.desk.en`, `15-investments.desk.en`, `19-etf.desk.en`, `11-recurring-list.desk.en`): the left column holds the figure and then ~200-340 px of nothing. Holdings in `15-investments.desk.en` leaves a third of its row empty. Cosmetic. Fill the space with a breakdown or let the cards fit their content.
- keep (not ranked): the payday bead timeline and jar (`01-overview.desk.en`), the refund progress line in transaction rows (`02-transactions.desk.en`), consistent blur in privacy mode (`31-hidden-overview.desk.en`), the bank-login 90-day bar with its explanation (`20-settings-bank.desk.en`), and tabular right-aligned amounts throughout.
