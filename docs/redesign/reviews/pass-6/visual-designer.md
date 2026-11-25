# Groschen: visual designer review (pass-final)

Role: visual designer. I score hierarchy, data presentation (visual encoding only), consistency, phone experience, accessibility (contrast and size only) and visual craft. I put "-" for clarity of purpose, task efficiency and navigation/naming, except where a naming problem shows up visually. Coordinates are in screenshot pixels (desk = 1500 px wide, phone = 390 px wide).

Overall: this is a polished, coherent dark UI. The type scale is consistent: one tabular display numeral for each hero, 11 px tracked caps for eyebrows, 14/12 px for row text. The card system, the gold accent and the category colour dots are applied with discipline across about 30 screens. The weaknesses repeat across screens: (a) the desktop hero cards put a large number on the left and leave the area below it empty; (b) two-column card rows are forced to equal height, which leaves empty card bottoms; (c) muted grey secondary text and disabled gold buttons sit at or below comfortable contrast; (d) a few phone layouts (orbit, backups timeline, the stray top gap) were not designed for the narrow width but squeezed into it.

---

## 01 Overview (desk.en, desk.de, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 8 | `01-overview.desk.en`: the "Available until payday" hero at 5,170.65 € (about 52 px) clearly outranks the 3 KPI cards (about 30 px) and the Sankey labels |
| 4 | data presentation | 6 | `01-overview.desk.en`: in the "Where the money went" Sankey, the Salary → Income link is a 370 × 360 px solid block (x 510-865) that carries no information |
| 6 | consistency | 7 | `01-overview.desk.en`: the "SAVED" card eyebrow sits at y 494, while INCOME and SPENDING sit at y 525 |
| 7 | phone | 7 | `01-overview.phone.de`: hero, hints and KPI cards stack well; the Sankey drops its left side and stays legible |
| 8 | accessibility | 6 | `01-overview.desk.en`: payday timeline dots (about 8 px, red on dark brown) and the grey sub-labels under Sankey nodes |
| 9 | visual craft | 8 | `01-overview.desk.en`: the glass "tank" fill gauge, the timeline coin and the KPI sparkbars feel crafted |

Findings
- `01-overview.desk.en`, Sankey: the left half of the chart (x 500-870, y 765-1120) is one flat green slab, because 99.6 % of income is salary. It spends about 40 % of the chart width on a single link. Suggestion: collapse the source column into a small label ("Income 33,538.60 €, 99.6 % salary") and give the width to the outflow side, or shorten the link to about 120 px. Severity: cosmetic.
- `01-overview.desk.en`, the 3 KPI cards: SAVED is laid out differently from INCOME and SPENDING. Its eyebrow is 30 px higher, it uses a 3-segment bar where the others use sparkbars, and it has a donut and a chevron. Its 2-line caption also wraps awkwardly ("8,095.40 € put / aside · 1,991.75 € stays"). Suggestion: align all three eyebrows to the same baseline and let the caption be one line ("3,000 invested · 8,095 aside · 1,992 stays"). Severity: cosmetic.
- `01-overview.desk.en`, "Worth a look" card: the bottom 60 px of the card (y 345-400) is empty because the card is stretched to the hero's height. The third hint also has no action button while the other two do, so the right column ends ragged. Severity: cosmetic.
- `01-overview.desk.en`, the "JAN – OCT 2026" section divider at y 438 repeats the period picker 360 px above it. **keep** as an anchor, but consider dimming it further.
- `01-overview.phone.de`, the hint list: the first hint has no dismiss "×", the second and third do. The buttons "Prüfen"/"Zeigen" sit on their own row under the text, while the "×" floats on the far right of that same row. Severity: cosmetic.
- `01-overview.phone.de`, Sankey caption: "Zeig auf ein Band, um ihm zu folgen" is a hover instruction shown on a touch device. Severity: cosmetic.
- **keep** `01-overview.desk.en`: the hero composition (eyebrow, large numeral, one-line daily rate, timeline, gauge) is the strongest screen in the app.

## 02 / 04 Transactions list (desk.en, phone.de; 04 is identical by capture note)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 7 | `02-transactions.desk.en`: day headers in 11 px caps with a muted day total, merchant names at 14 px semibold, amounts bold on the right |
| 4 | data presentation | 6 | `02-transactions.desk.en`: dead zone between merchant (ends about x 500) and category chip (starts about x 1000) |
| 6 | consistency | 7 | `02-transactions.desk.en`: category chips are right-aligned, so their left edges vary between x 997 and x 1023 |
| 7 | phone | 8 | `02-transactions.phone.de`: chip under the name, amount right, purpose truncated with an ellipsis: a good adaptation |
| 8 | accessibility | 6 | `02-transactions.desk.en`: the "Girokonto" account column at x 1157 is about #6b6b6b on #141414 |
| 9 | visual craft | 8 | `02-transactions.desk.en`: brand logos, avatar letters and the green income amount (3,340.00 €) are clean |

Findings
- `02-transactions.desk.en`, row layout: at 1500 px each row has about 500 px of empty space between the purpose text and the chip. The chip column is right-aligned, so chips of different widths start at different x positions and the column reads ragged (compare "Fuel" at x 1023 with "Restaurants & cafés" at x 997). Suggestion: left-align chips in a fixed column at about x 900, or move the account into the purpose line and pull the chip left. Severity: cosmetic.
- `02-transactions.desk.en`, day totals: totals appear only on multi-transaction days (e.g. "-177.49 €" on 28 Oct) and are missing on single-transaction days (27 Oct, 21 Oct). This is defensible, but the right column then switches between showing a total and showing nothing. Severity: cosmetic.
- `02-transactions.phone.de`, toolbar: the search placeholder is cut off ("…Kategorie oder Betr"), and the summary line wraps so that "31.970,76 € raus" sits alone on a second line. Suggestion: shorten the placeholder to "Suchen…" and put in/out on their own line. Severity: cosmetic.
- **keep** `02-transactions.desk.en`: the 3-px gold left bar on uncategorized rows (Hofladen Sonnenfeld, y 594) is a quiet, effective marker for rows that need attention.
- **keep** `02-transactions.desk.en`, bottom (Lena Berger, About You): the inline "32.00 € of 64.00 € back" mini progress bar is elegant.

## 03 Transactions, needs review (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 6 | `03-transactions-review.desk.en`: the 68 px gold-bordered banner "These transactions need a category from you." outweighs the list |
| 4 | data presentation | 5 | `03-transactions-review.desk.en`: the summary "All periods · 8 transactions · 110,315.81 € in" contradicts the picker "Jan – Oct 2026" and the "Needs review 39" badge |
| 6 | consistency | 5 | the same: badge 39 vs 8 rows, picker period vs "All periods" |
| 7 | phone | 7 | `03-transactions-review.phone.de`: same list pattern, readable |
| 9 | visual craft | 7 | `03-transactions-review.desk.en`: the banner is a full-width strip with one sentence and 800 px of empty space |

Findings
- `03-transactions-review.desk.en`, banner (y 145-212): a heavy gold-bordered card holding one sentence and no action. Suggestion: either give it a primary action ("Review one by one") or reduce it to a single muted line. Severity: cosmetic.
- `03-transactions-review.desk.en`, summary line (y 241) vs the period chip (y 50) vs the tab badge "39": three different scopes are visible at once. Even allowing for the capture note, the screen shows contradictory numbers. Severity: slows a task.

## 05 Transaction edit dialog (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 8 | `05-transactions-edit.desk.en`: amount "-56.30 €" at about 34 px next to the logo, raw bank text in a mono block, then the category picker |
| 6 | consistency | 6 | `05-transactions-edit.desk.en`: chips read "Housing (general)" here but "Housing" in `08-spending-group-dialog.desk.en` |
| 7 | phone | 7 | `05-transactions-edit.phone.de`: the sheet uses the full height; the toggle drops below its label |
| 9 | visual craft | 8 | `05-transactions-edit.desk.en`: the selected chip "Fuel" fills with gold; the sticky footer with toggle and Save is tidy |

Findings
- `05-transactions-edit.desk.en`, the "(general)" chips are bold while sibling chips are regular, which adds a third weight to the chip set. Severity: cosmetic.
- `05-transactions-edit.desk.en`, selected "Fuel" chip: the pink category dot disappears into the gold fill. Suggestion: keep the dot or show a check mark. Severity: cosmetic.
- **keep** the monospace raw-purpose block (y 165-245): it clearly separates bank data from the UI.

## 06 Transactions empty (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 8 | `06-transactions-empty.desk.en`: icon, heading "No transactions match" and hint text, with the gold "Clear filters" link in the summary line |
| 6 | consistency | 6 | `06-transactions-empty.phone.de`: a 130 px blank band between the app bar and the "Umsätze" title (y 55-185) that no other phone screen has at that size |
| 7 | phone | 5 | the same gap |
| 9 | visual craft | 7 | `06-transactions-empty.desk.en`: the empty card is centred but sits in 570 px of empty page |

Findings
- `06-transactions-empty.phone.de`: the page title is pushed down about 130 px. Smaller versions of the same gap appear on `13-recurring-orbit.phone.de` (y 55-95) and `23-settings-depot.phone.de` (y 55-95), which suggests leftover scroll or min-height logic. Severity: cosmetic, but it looks broken.
- **keep** the gold "Clear filters" link placed next to the "0 transactions" count.

## 07 Spending (desk.en, phone.de) and 33 period menu

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 7 | `07-spending.desk.en`: the "Total 20,451 €" donut centre and the ranked bar list read well; the "+ Your own group" ghost button at y 104 floats with no anchor |
| 4 | data presentation | 7 | `07-spending.desk.en`: two-ring donut plus a ranked bar list; the heatmap "Your year in days" uses a violet→yellow ramp |
| 6 | consistency | 7 | `07-spending.desk.en`: the "Personal · more refunds than spending" row has no bar and no %, which breaks the column rhythm |
| 7 | phone | 7 | `07-spending.phone.de`: the donut fills the width; the heatmap splits into two half-years, but cells shrink to about 8 px |
| 8 | accessibility | 5 | `07-spending.desk.en`: the heatmap legend "Less ■■■■■ More" is 8 px squares; violet, magenta and orange cells are hard to tell apart on dark grey |
| 9 | visual craft | 8 | `07-spending.desk.en`: the donut and bar colours match the category dots used everywhere else |

Findings
- `07-spending.desk.en`, the outer donut ring: about 20 thin slivers in the 9-12 o'clock region add noise without being readable. Suggestion: merge slices under 2 % into "Other" in the outer ring. Severity: cosmetic.
- `07-spending.desk.en`, "+ Your own group" (x 285-420, y 104): an orphaned dashed pill between the title and the card. It belongs in the "Spending breakdown" card header next to Groups/Categories. Severity: cosmetic.
- `07-spending.phone.de`, the year heatmap: cells about 8 px with 2 px gaps are too small to tap, although the caption says "Klick zeigt die Umsätze des Tages". Severity: slows a task.
- `33-period-menu.desk.en`: the dropdown is clean, the selected "Year to date" is gold with a check, and it overlaps the list neatly. **keep**. `33-period-menu.phone.de` is also fine.

## 08 New group dialog (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 6 | `08-spending-group-dialog.desk.en`: there is no "Categories" label above the chip groups; "HOUSING" follows straight after Name/Icon |
| 6 | consistency | 6 | `08-spending-group-dialog.desk.en`: the icon picker box stretches to x 995 but holds only 4 icons, leaving 90 px of empty box |
| 7 | phone | 7 | `08-spending-group-dialog.phone.de`: the icon row shrinks to fit, which is better than desktop |
| 9 | visual craft | 7 | `08-spending-group-dialog.desk.en`: the disabled "Save" is muted gold with dark text and gives no reason |

## 09 Drill group "Food & Dining" (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 8 | `09-drill-group.desk.en`: hero "3,480.29 €" with a delta chip, a monthly bar chart, then the merchants/categories cards |
| 4 | data presentation | 6 | `09-drill-group.desk.en`: the "Average 348 €" label overlaps the Sept bar (x 1300-1415, y 273) |
| 6 | consistency | 6 | `09-drill-group.desk.en`: filter chips in the Transactions card use square dots ("Groceries 43") while every other chip uses round dots |
| 7 | phone | 7 | `09-drill-group.phone.de`: the chart keeps every other month label; filter chips wrap to 3 rows |
| 9 | visual craft | 7 | `09-drill-group.desk.en`: the "Categories" card bottom is empty (y 700-925) because it matches the merchants card height |

Findings
- `09-drill-group.desk.en`, the hero left column: below "largest 94.95 €" (y 310) there are 140 px of empty card. This is the same pattern as 10, 14, 15 and 19. Suggestion: give the left column 35 % width, or put 2-3 mini stats in the space. Severity: cosmetic.
- `09-drill-group.desk.en`, Categories: the "Food & Dining · 0× · 0.00 €" and "Food delivery · 0×" rows add clutter. Hide zero rows or dim them. Severity: cosmetic.
- `09-drill-group.desk.en`, the bar chart: all bars are the same gold, so the period's peak and the current month don't stand out. Optional: highlight the current month. Severity: cosmetic.

## 10 Drill category "Groceries" (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 8 | `10-drill-category.desk.en`: a breadcrumb "SPENDING › FOOD & DINING" over the "Groceries" title |
| 4 | data presentation | 6 | `10-drill-category.desk.en`: the "Top merchants" bars stretch over 1,125 px for 4 rows; Lidl's bar is 100 % wide but its label says 30.3 % |
| 6 | consistency | 7 | `10-drill-category.desk.en`: every row repeats the "Groceries" chip, which adds nothing inside a Groceries drill |
| 7 | phone | 7 | `10-drill-category.phone.de`: works; purpose text truncated "vom 28.1…" |
| 9 | visual craft | 7 | the same |

Findings
- Bars scaled to the maximum while labelled with percentage shares (`10-drill-category.desk.en` Lidl 30.3 % = full bar; `09-drill-group.desk.en` Lidl 22.3 % = full bar; `07-spending.desk.en` Housing 58.3 % = full bar). Readers will take bar length as the share. Suggestion: scale bars to the share, or drop the % next to them. Severity: slows a task.
- `10-drill-category.desk.en`: hide the category chip column when the list is already filtered to one category. Severity: cosmetic.

## 11 Fixed costs, list (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 8 | `11-recurring-list.desk.en`: hero "1,407.01 €" plus the "NEXT UP" mini list, then "What changed", then "Running" |
| 4 | data presentation | 6 | `11-recurring-list.desk.en`: "Running" is sorted by amount, so the due column reads "In 2, 3, 5, 16, 7, 19, 3 days…" in apparent random order |
| 6 | consistency | 6 | `11-recurring-list.desk.en`: the due label is not a fixed column; it starts at x 1268 ("In 2 days") or x 1222 ("15 Jan 2027") depending on amount width |
| 7 | phone | 7 | `11-recurring-list.phone.de`: due dates are dropped entirely from "Laufend", and long names truncate ("Stadtwerke Muench…") because of the "+7,00 €" badge |
| 9 | visual craft | 8 | `11-recurring-list.desk.en`: the change badges (+7.00 € amber, "Back"/"New" blue) and "What changed" icons are well judged |

Findings
- `11-recurring-list.desk.en`, the hero: the left half (x 313-930, y 235-320) is empty below the subtitle. Severity: cosmetic.
- `11-recurring-list.desk.en`, "NEXT UP" rows: the merchant starts at x 1078 after a 60 px gap from "In 2 days", which leaves a hole. Severity: cosmetic.
- `11-recurring-list.desk.en`, Running: put the due date in a fixed-width right-aligned column before the amount, so rows that have a "≈ 27.07 € a month" sub-line don't shift the amount up. Severity: cosmetic.
- **keep** `11-recurring-list.desk.en`, "What changed" (y 345-690): concise sentences with one bold lead each and right-aligned dates. This is a model pattern.

## 12 Fixed costs, calendar (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 7 | `12-recurring-calendar.desk.en`: "Day by day" (right) is visually heavier than the calendar it explains |
| 4 | data presentation | 5 | `12-recurring-calendar.desk.en`: calendar chips truncate to "Ha… -1,050 €", "Spar… -800 €", "Nor… 3,340 €" |
| 6 | consistency | 5 | `12-recurring-calendar.desk.en`: header "1,423.48 € fixed costs" vs `11-recurring-list.desk.en` hero "1,407.01 €"; also "Standing order" teal vs "Salary" green are nearly the same hue |
| 7 | phone | 8 | `12-recurring-calendar.phone.de`: dots plus day totals instead of truncated chips is a better design than desktop |
| 9 | visual craft | 6 | `12-recurring-calendar.desk.en`: the calendar card ends at y 803 while "Day by day" runs to y 1325, leaving 520 px of empty space under the calendar |

Findings
- `12-recurring-calendar.desk.en`: use the phone treatment (coloured dots plus a day total) on desktop as well, or widen the cells. Truncated two-letter merchant names are unreadable. Severity: slows a task.
- `12-recurring-calendar.desk.en`, legend: "Standing order" (#3cc) and "Salary" (#3c9) are too close in hue. Severity: cosmetic (accessibility).
- **keep** the gold-outlined "today" cell (30).

## 13 Fixed costs, orbit (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 5 | `13-recurring-orbit.desk.en`: only 4 of 13 bodies are labelled; the "a month" label under 1,407 € is near-invisible |
| 4 | data presentation | 4 | `13-recurring-orbit.desk.en`: overlapping spheres at x 950-1045 (Hausverwaltung, plus one unlabelled) |
| 7 | phone | 3 | `13-recurring-orbit.phone.de`: the whole orbit is squeezed into about 80 px of height (y 440-520); labels collide with "1.407 €" |
| 9 | visual craft | 7 | `13-recurring-orbit.desk.en`: attractive as decoration, starfield included |

Findings
- `13-recurring-orbit.phone.de`: unusable at 390 px. Suggestion: hide the Orbit tab on phone, or render it top-down (circular) instead of as a flattened ellipse. Severity: blocks a task (on this view).
- `13-recurring-orbit.desk.en`: label every body on hover only, and label at least the top 5 permanently. Severity: cosmetic.

## 14 Net worth (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 6 | `14-networth.desk.en`: the savings plan amounts "250.00 €", "800.00 €" (about 28 px) are as large as the account balances "7,768.05 €", which flattens the second level |
| 4 | data presentation | 6 | `14-networth.desk.en`: the line chart y-axis starts at 25k €, which exaggerates growth; the x-axis starts "Dec 25" for a Jan–Oct period |
| 6 | consistency | 7 | `14-networth.desk.en`: only "Direkt-Depot" has a chevron (x 1135); the other account cards look clickable but aren't marked |
| 7 | phone | 6 | `14-networth.phone.de`: three 140 px account cards, each holding one number, plus three tall plan cards make this a 2,078 px page |
| 8 | accessibility | 5 | `14-networth.desk.en`: share labels "17%", "62%", "21%" at about 10 px grey |
| 9 | visual craft | 7 | `14-networth.desk.en`: the 12 identical gold coins per plan are decorative but carry no information when every payment arrived |

Findings
- `14-networth.desk.en`, the hero: the left 330 px below the delta chip (y 240-440) is empty. Severity: cosmetic.
- `14-networth.phone.de`: make the account cards compact rows (name left, balance right, thin bar), and do the same for plan cards. Severity: slows a task (scrolling).
- **keep** the dashed "Add account" tile as the 4th card. It is a well-placed affordance.

## 15 Investments (desk.en, phone.de) and 32 hidden

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 7 | `15-investments.desk.en`: hero "9,350.57 €", then the value chart plus a gain/loss strip |
| 4 | data presentation | 7 | `15-investments.desk.en`: the monthly gain/loss bars under the value line, labelled "+497 €"/"-429 €", work well |
| 6 | consistency | 6 | `15-investments.desk.en`: page "Investments" vs card "DEPOT VALUE" vs phone tab "Depot"; the justETF banner also repeats on `19-etf.desk.en` |
| 7 | phone | 8 | `15-investments.phone.de`: the chart keeps both layers; legend and toggles stack cleanly |
| 9 | visual craft | 7 | `15-investments.desk.en`: the Holdings row fills only 2 of 3 columns (empty x 1055-1435, y 780-1005) and the hero left column is empty from y 310 to y 650 |

Findings
- `15-investments.desk.en`, Holdings: with 2 ETFs, make each card 50 % wide or add a "+ add" placeholder like Net worth does. Severity: cosmetic.
- `32-hidden-investments.phone.de` / `31-hidden-overview.desk.en`: the blur is consistent, axis labels are blurred too, and percentages stay visible. **keep**. The privacy mode is well executed.

## 16 Forecast (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 7 | `16-inv-forecast.desk.en`: "68,412 €" with a bad/good range slider, then the chart |
| 4 | data presentation | 7 | `16-inv-forecast.desk.en`: a fan chart with milestones (10k, 25k, 50k) marked on the path |
| 6 | consistency | 6 | `16-inv-forecast.desk.en`: the legend (top right, y 155) is 250 px away from the chart it explains (y 400+) |
| 7 | phone | 7 | `16-inv-forecast.phone.de`: the "eingezahlt" marker label at x 27 sits outside the card's 35 px content edge |
| 9 | visual craft | 7 | `16-inv-forecast.desk.en`: the tiny "paid in" tick label at (313, 433) is hard to read |

## 17 Analysis (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 7 | `17-inv-analysis.desk.en`: "+6.7%" vs "+6.3%" green numerals on the right |
| 4 | data presentation | 6 | `17-inv-analysis.desk.en`: the two return bars (+6.7 % full, +6.3 % at 92 %) encode almost nothing; the "-15%" axis label collides with "Dec 25" (x 350, y 640) |
| 6 | consistency | 5 | `17-inv-analysis.desk.en`: "Outlined: the best and the worst month" is drawn as an unchecked checkbox (x 316, y 875), but it is a legend |
| 7 | phone | 8 | `17-inv-analysis.phone.de`: the monthly returns grid wraps to 6×2 nicely |
| 9 | visual craft | 8 | `17-inv-analysis.desk.en`: the drawdown area chart and the calm→wild gradient gauge are elegant |

## 18 Pay-ins (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 7 | `18-inv-payments.desk.en`: month rows bold, child rows indented |
| 6 | consistency | 6 | `18-inv-payments.desk.en`: child amounts are right-aligned at x 1290 and month totals at x 1428, giving two amount columns |
| 7 | phone | 8 | `18-inv-payments.phone.de`: the date moves under the row and the "Nicht zählen" action is clear |
| 9 | visual craft | 7 | `18-inv-payments.desk.en`: the expanded chevron (x 321, y 231) sits 3 px off the collapsed chevrons' axis |

## 19 ETF detail (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 6 | `19-etf.desk.en`: the ISIN pill "IE00BK5BQT80" (bold mono, bordered) is louder than the fund's full name beside it |
| 4 | data presentation | 8 | `19-etf.desk.en`: purchase dots on the price line and the dashed "Your average 110.71 €" line |
| 7 | phone | 6 | `19-etf.phone.de`: "Dein Schnitt 110,71 €" is printed over the price line at y 828 |
| 9 | visual craft | 7 | `19-etf.desk.en`: the hero left column is empty from y 500 to y 735 |

Findings
- `19-etf.phone.de` / `15-investments.phone.de`: there are two levels of "Analyse / Prognose" tabs (depot level and ETF level) with identical names. This shows visually as a repeated tab bar. Severity: slows a task.

## 20-27 Settings (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 7 | `20-settings-bank.desk.en`: section card, then setting title, description and control at right: consistent across tabs |
| 6 | consistency | 5 | native `<select>` with OS chevrons (`20-settings-bank.desk.en` "Every day at 06:00", `21-settings-categories.desk.en` rule builder, `27-settings-account.desk.en` Country/Currency) vs custom dropdown (`24-settings-backup.desk.en` "03:00"); text-only "Log out" vs bordered "Show" in `26-settings-security.desk.en` |
| 7 | phone | 6 | `20-settings-bank.phone.de`: 8 tabs scroll horizontally, cut off at "Hinweise & Gehalt" with no fade or arrow; in `27-settings-account.phone.de`, "Passwort ändern" goes below its label while "Abmelden" stays right |
| 8 | accessibility | 5 | `23-settings-depot.desk.en`: the "off" toggle (light knob on #2a2a2a, x 1415) is barely visible; `25-settings-privacy.desk.en`: the disabled "Show log" button |
| 9 | visual craft | 7 | `24-settings-backup.desk.en`: the retention timeline with dashed slots is a nice idea; long descriptions run to 1,100 px line length (`20-settings-bank.desk.en`, y 371) |

Findings
- `20-settings-bank.desk.en`: a card nested in a card (ING card inside "Bank connections"), with a full-width 1,090 px green progress bar. Cap description width at about 680 px. Severity: cosmetic.
- `21-settings-categories.desk.en`: the "Offline" badge is green (which reads as good) next to "built-in model not found", while the "Built-in model" segment is shown as selected. These are contradictory visual states. Severity: slows a task.
- `23-settings-depot.phone.de`: "Vergleichszins" has its input inline on the right while "Sparerpauschbetrag" has it below, inside the same card. The German UI also shows "1.75" with a decimal point and "1000" with no separator, where elsewhere it uses "1.000,00". Severity: cosmetic.
- `24-settings-backup.phone.de`: the retention strip collapses into overlapping dashed slots, labels "1 pro Jahr/Monat" are lost, and the 4 stepper cards stack into 360 px. Suggestion: a 2×2 grid and a simplified strip. Severity: cosmetic.
- `25-settings-privacy.desk.en`: "Backups never contain the key…" repeats under Export (y 294) and is off-topic there. Severity: cosmetic.
- `26-settings-security.desk.en`: the "Password login" row has no control on the right, which makes the column look like something is missing. Severity: cosmetic.
- **keep** `22-settings-hints.desk.en`: a well-ordered toggle list with consistent row height (82 px) and right-aligned toggles.

## 30 Connect bank dialog (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 6 | `30-settings-connect-dialog.desk.en`: the scrim is too light; the toggles and green bar behind it compete with the dialog |
| 9 | visual craft | 6 | `30-settings-connect-dialog.desk.en`: the only button, "Done, start syncing", is shown (muted) before any bank is chosen |

## 34 Payday details (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 8 | `34-payday-details.desk.en`: Balance, Going out and Free to spend form a clean sum block |
| 6 | consistency | 6 | `34-payday-details.desk.en`: "Free to spend 5,170.65 €" is green here but white in the Overview hero; raw "Sparplan IE00BK5BQT80 Vanguard FTSE All-World U." is used instead of the clean name from Holdings |
| 7 | phone | 8 | `34-payday-details.phone.de`: the due label sits above the name and wraps well |

## 40-42 Wizard and login (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 8 | `40-wizard-account.desk.en`: the stepper rail and the "Welcome to Groschen" heading are clear |
| 7 | phone | 7 | `41-wizard-country.phone.de`: the body paragraph (about 15 px grey) is larger than the field labels, and the skip link wraps to 2 centred lines above "Weiter" |
| 8 | accessibility | 4 | `42-login.desk.en`: the disabled "Log in" button has dark text on muted olive-gold (about 2.3:1); `40-wizard-account.desk.en` "Continue" is the same |
| 9 | visual craft | 7 | `40-wizard-account.desk.en`: 150 px of empty space between the password hint and the footer divider |

---

## Top 10

1. **`13-recurring-orbit.phone.de` – the Orbit view collapses to an 80 px strip with colliding labels.** Severity: blocks a task. Hide the view on phone or redesign it as a circular top-down layout.
2. **`12-recurring-calendar.desk.en` – calendar chips truncate to "Ha… -1,050 €", the card leaves 520 px empty, and its total (1,423.48 €) disagrees with the list hero (1,407.01 €).** Severity: slows a task. Use the phone's dot plus day-total treatment on desktop too, and make the totals the same.
3. **Bars scaled to the maximum but labelled with shares (`07-spending.desk.en` Housing 58 % = full bar, `10-drill-category.desk.en` Lidl 30.3 % = full bar).** Severity: slows a task. Scale bars to the share.
4. **The desktop hero pattern leaves 150-350 px of empty left column (`14-networth.desk.en`, `15-investments.desk.en`, `19-etf.desk.en`, `09-drill-group.desk.en`, `11-recurring-list.desk.en`).** Severity: cosmetic. Use a narrower hero column, or fill the space with 2-3 secondary stats.
5. **`03-transactions-review.desk.en` – contradictory scopes are visible at once ("Needs review 39" vs 8 rows; picker "Jan – Oct 2026" vs "All periods"), plus a heavy banner with no action.** Severity: slows a task.
6. **Low-contrast disabled primary buttons and grey metadata (`42-login.desk.en` "Log in", `40-wizard-account.desk.en` "Continue", `02-transactions.desk.en` "Girokonto" column, `23-settings-depot.desk.en` off-toggle).** Severity: slows a task. Raise the disabled text to at least 4.5:1 or show the reason, and lighten the secondary greys by about 15 %.
7. **Mixed control styles in Settings: native selects with OS chevrons (`20-settings-bank.desk.en`, `21-settings-categories.desk.en`, `27-settings-account.desk.en`) vs custom dropdowns (`24-settings-backup.desk.en`); text-only vs bordered buttons (`26-settings-security.desk.en`).** Severity: cosmetic. Use one custom select component and one secondary button style.
8. **`02-transactions.desk.en` – about 500 px of dead space per row, and right-aligned chips start at different x positions.** Severity: cosmetic. Use a fixed, left-aligned chip column, or a narrower max-width for the list.
9. **Phone layout glitches: a stray top gap (`06-transactions-empty.phone.de`, 130 px), a label drawn over the chart line (`19-etf.phone.de` "Dein Schnitt"), a truncated tab bar with no scroll hint (`20-settings-bank.phone.de`), and an unlabelled backup strip (`24-settings-backup.phone.de`).** Severity: cosmetic.
10. **`21-settings-categories.desk.en` – a green "Offline" badge and a selected "Built-in model" segment next to "built-in model not found".** Severity: slows a task. Use an amber/neutral badge and show the actual active mode.

Keep: the Overview hero composition (`01-overview.desk.en`), the "What changed" list (`11-recurring-list.desk.en`), the gold uncategorized-row marker and the inline refund progress (`02-transactions.desk.en`), the phone calendar adaptation (`12-recurring-calendar.phone.de`), the privacy blur (`31-hidden-overview.desk.en`, `32-hidden-investments.phone.de`), the drawdown and monthly-returns visuals (`17-inv-analysis.desk.en`), and the "Add account" dashed tile (`14-networth.desk.en`).
