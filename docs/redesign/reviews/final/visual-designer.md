# Groschen, pass 8: visual designer review

Reviewer role: visual designer. I judge hierarchy, spacing rhythm, alignment, type scale, contrast, density, consistency between screens, and empty or wasted space. Lines 1, 3 and 5 are outside my role and are marked "-". Pixel positions are approximate and refer to the screenshot at its native size: desk is 1500 px wide, phone is 390 px wide.

## Overall impression

The visual system is mature and coherent. It uses one dark surface palette, a warm gold accent, green for money in, coral for money out, and the same category colours on every screen. The type scale is consistent: hero number around 52 px, card title 15 px semibold, uppercase tracked overlines, and a 13 px muted secondary line. Cards use a 24 px inner padding and a 20 px gap almost everywhere, and the desktop-to-phone adaptation is careful. The weaknesses repeat across screens:

1. Hero cards on desktop leave large dead areas.
2. Some views keep a stretched or under-filled grid.
3. The gold accent does too many jobs.
4. Phone has a few spacing glitches (extra top gaps, wrapping segmented controls).
5. Disabled gold buttons have low contrast.

---

## 01 Overview (desk.en, desk.de, phone.de, phone.en)

| # | Line | Score | Based on |
|---|---|---|---|
| 1 | clarity of purpose | - | |
| 2 | hierarchy | 8 | `01-overview.desk.en`: the "Available until payday" hero (5,170.65 €, about 52 px) clearly dominates. The KPI row sits one level below it, and the Sankey sits below that. |
| 3 | task efficiency | - | |
| 4 | data presentation | 6 | `01-overview.desk.en`: in the Sankey, the Salary → Income link is a flat solid block about 370 × 360 px (x 505–870, y 765–1120) that carries no information. |
| 5 | navigation and naming | - | |
| 6 | consistency | 7 | `01-overview.desk.en`: in the "Saved" KPI card the overline starts at y 493, but Income and Spending start at y 525, so the three KPI cards do not share a baseline. |
| 7 | phone experience | 8 | `01-overview.phone.de`: the Sankey drops the middle column and keeps the labels readable. |
| 8 | accessibility | 7 | `01-overview.desk.en`: the grey 12 px sub-labels on the payday strip ("Salary 27 Oct", "Fri 27 Nov") are low contrast. |
| 9 | visual craft | 8 | `01-overview.desk.en`: the glass "tank" next to the hero and the bead-style payday strip are polished. |

**Findings**

- `01-overview.desk.en`, Sankey "Where the money went": the left node (Salary, 99.6 %) and the centre node (Income) are joined by a full-height rectangle, so about 25 % of the card width is spent drawing a 1:1 pass-through. *Slows a task (reading).* Suggestion: when one source is above about 95 %, collapse the first stage, or make the left column a thin stacked bar with labels.
- `01-overview.desk.en`, KPI row (y 465–617): Income and Spending centre their content vertically, while Saved is top-aligned with a progress bar and a ring. The overlines sit at y 525 and y 493, so the row looks uneven. *Cosmetic.* Suggestion: top-align all three cards at the same overline y, and pin the sparklines and the ring to the same bottom edge.
- `01-overview.desk.en`, payday strip: the "Fri 27 Nov" end label sits at x 679, but the end coin sits at x 757, so the label does not line up under its marker. *Cosmetic.*
- `01-overview.desk.en`, "Worth a look": rows 1 and 2 have right-aligned buttons and row 3 has none, so the card's right column ends ragged and the card has about 50 px of empty space at the bottom (y 350–400). *Cosmetic.*
- `01-overview.phone.de`, "Einen Blick wert": each dismiss "×" sits alone on its own row (y 687, y 790) under the action button. That adds about 40 px per hint and floats away from the item it closes. *Cosmetic.* Suggestion: put the × at the top right of each hint row.
- **Keep:** `01-overview.desk.en`, colour semantics. The green Income dot and bars, the coral Spending dot and bars, and the gold Saved dot carry straight into the Sankey band colours. This is the strongest system decision in the app.
- **Keep:** `01-overview.desk.de`. The German strings fit without truncation, and the Saved card's sub-line wraps cleanly.

## 02 / 04 Transactions and filtered transactions (desk.en, desk.de, phone.de, phone.en)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 7 | `02-transactions.desk.en`: the merchant name (semibold, white) and the amount (bold, right) carry each row, and the date overlines group the rows well. |
| 4 | data presentation | 6 | `02-transactions.desk.en`: there is an empty gutter of about 350–450 px between the merchant text (ending around x 660) and the category pill (around x 1000). |
| 6 | consistency | 7 | `02-transactions.desk.en`: the category pills have no common left edge (Fuel starts at x 1023, "Restaurants & cafés" at x 997). |
| 7 | phone experience | 7 | `02-transactions.phone.de`: the toolbar stacks on three rows (y 126–250), and the summary line wraps with "31.970,76 € raus" alone on the next line. |
| 8 | accessibility | 6 | `02-transactions.desk.en`: the account column "Girokonto" is mid-grey on near-black, about 3:1. |
| 9 | visual craft | 7 | `02-transactions.desk.en`: brand avatars and dotted pills look good, but the pill column is ragged. |

**Findings**

- `02-transactions.desk.en`, row layout: the pills appear right-aligned to about x 1140 and then pushed by their width, so their left edges zig-zag between x 997 and x 1023. *Cosmetic.* Suggestion: give the pills a fixed left edge (left-align them in a fixed-width column) and pull that column closer to the text, for example at about 55 % of the row.
- `02-transactions.desk.en`: the "Girokonto" account label is repeated on every row in low-contrast grey. With one main account it is noise. *Cosmetic.* Suggestion: show it only when it differs from the default, or drop it to a filter.
- `02-transactions.desk.en`, day header totals (for example "-177.49 €" at y 206): these use the same grey as the overline. That is good, but the header sits only 14 px above the first row, while there are 30 px between groups. **Keep** that rhythm.
- `02-transactions.phone.de`, search placeholder: "Händler, Verwendungszweck, Kategorie oder Betr" is clipped mid-word. *Cosmetic.* Suggestion: use a shorter German placeholder, such as "Suchen …".
- `02-transactions.phone.de`, toolbar: there are three stacked rows (segments, Filter plus sort, then the summary across two lines), so about 230 px of chrome comes before the first transaction. *Slows a task.* Suggestion: put Filter and sort on the same row as the segment control as icon buttons, and shorten the summary.
- `04-transactions-filtered.desk.en`: "Clear filters" in gold next to the summary is well placed. **Keep.**
- **Keep:** `02-transactions.phone.de`, the two-line row with the pill under the merchant and the amount vertically centred. It is clean and well spaced.

## 03 Transactions, needs review (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 7 | `03-transactions-review.desk.en`: the gold "These transactions need a category from you." banner leads the page. |
| 6 | consistency | 6 | `03-transactions-review.desk.en`: the tab badge says "Needs review 39", but the list summary says "8 transactions". |
| 7 | phone experience | 8 | `03-transactions-review.phone.de`: the banner wraps to two lines and the gold left marker on each row reads well. |
| 9 | visual craft | 7 | `03-transactions-review.desk.en`: the banner is 68 px tall for a single short line. |

**Findings**

- `03-transactions-review.desk.en`, banner (y 145–212): there is one 15 px line inside a 68 px, full-width, gold-outlined box, with 1,100 px of empty space to its right. *Cosmetic.* Suggestion: add the count and a primary "Categorise next" action on the right, or reduce the banner to an inline note.
- `03-transactions-review.desk.en`, dashed "Uncategorized" pills (x 1022–1127): these are the call to action, but they are the lowest-contrast element in the row. *Slows a task.* Suggestion: make the pill gold-outlined with a "+ Category" label in this view.
- **Keep:** the gold vertical tick at the left of each row (x 297) to mark rows that need attention. It is subtle and works on both desk and phone.

## 05 Transaction edit dialog (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 8 | `05-transactions-edit.desk.en`: the amount (-56.30 €, about 34 px) with the logo, then the raw bank text in monospace, then the category chips. |
| 6 | consistency | 7 | `05-transactions-edit.phone.de`: the "Use this category for every transaction from this merchant" toggle sits below its label, while on desk it sits right-aligned. |
| 7 | phone experience | 7 | `05-transactions-edit.phone.de`: the toggle on its own row adds about 40 px. |
| 9 | visual craft | 8 | `05-transactions-edit.desk.en`: the selected chip "Fuel" filled in gold is unmistakable. |

**Findings**

- `05-transactions-edit.phone.de`: the merchant toggle drops below a two-line label. *Cosmetic.* Suggestion: keep the toggle right-aligned and let the label wrap beside it, as in `22-settings-hints.phone.de`.
- `05-transactions-edit.desk.en`, footer: "Everything with Shell ›" is a ghost link at the same visual weight as body text and sits opposite Save. **Keep** the placement, but its role as a secondary action could be clearer.
- **Keep:** the grouped chip picker with category-colour dots and "+ New" at the end of each group.

## 06 Transactions, empty result (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 7 | `06-transactions-empty.desk.en`: the "No transactions match" card with its icon is centred and calm. |
| 6 | consistency | 6 | `06-transactions-empty.phone.de`: there is a gap of about 110 px between the header and the title "Umsätze" (y 60–185) that no other phone screen has. |
| 7 | phone experience | 6 | `06-transactions-empty.phone.de`: the same unexplained top gap. |
| 9 | visual craft | 7 | `06-transactions-empty.desk.en`: the card is fine, but the page below y 380 is empty. |

**Findings**

- `06-transactions-empty.phone.de`: there is about 110 px of empty space above the page title, compared with `02-transactions.phone.de`, where the title sits at y 95. It looks like a scroll or layout bug. *Cosmetic.*
- **Keep:** the gold "Clear filters" / "Filter zurücksetzen" link in the summary row.

## 07 Spending (desk.en, phone.de) and 33 period menu (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 7 | `07-spending.desk.en`: the "Spending breakdown" donut and bar list work, but "+ Your own group" floats alone at y 104 under the title, with no relation to anything. |
| 4 | data presentation | 8 | `07-spending.desk.en`: the bar list with amount, % and chevron, plus the heatmap "Your year in days", is a strong pairing. |
| 6 | consistency | 7 | `07-spending.desk.en`: the percentage column ("58.3%" at x 1381) is lighter and smaller than the amounts, but sits only about 20 px away from them. |
| 7 | phone experience | 8 | `07-spending.phone.de`: the heatmap splits into two half-year blocks and stays legible. |
| 8 | accessibility | 6 | `07-spending.desk.en`: the heatmap encodes everything in hue (violet → pink → orange → yellow). The middle steps are close in lightness. |
| 9 | visual craft | 8 | `07-spending.desk.en`: the donut and the bar rhythm (45 px per row) are clean. |

**Findings**

- `07-spending.desk.en`, "+ Your own group" button (x 285–420, y 104): it is a dashed orphan control between the title and the first card and breaks the title-to-card rhythm used on every other page. *Cosmetic.* Suggestion: move it into the breakdown card header next to Groups/Categories, or into the list footer.
- `07-spending.desk.en`, header: two segmented controls (Spending/Income, then the period button) sit side by side with different heights (30 px and 34 px). *Cosmetic.*
- `07-spending.desk.en`, heatmap: the future days (Nov to Dec) are outlined empty squares that read almost the same as "Nothing" days (filled grey). *Cosmetic.*
- `33-period-menu.desk.en`: the dropdown surface (#17181b-ish) is barely distinguishable from the card behind it, and its shadow is weak. "Year to date" in gold with a check is clear. **Keep** the check. Raise the elevation contrast. *Cosmetic.*

## 08 New group dialog (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 7 | `08-spending-group-dialog.desk.en`: the explanation paragraph and the name and icon fields come first, and the categories scroll below. |
| 6 | consistency | 8 | `08-spending-group-dialog.desk.en`: it uses the same chip groups as `05-transactions-edit`. |
| 8 | accessibility | 5 | `08-spending-group-dialog.desk.en`: the disabled "Save" (x 933–995) has dark text on dull gold, at very low contrast. |
| 9 | visual craft | 7 | `08-spending-group-dialog.desk.en`: the icon picker field stretches to x 995 but holds only 4 icons, which leaves an empty 120 px tail. |

**Findings**

- `08-spending-group-dialog.desk.en`, Icon field: it is a full-width bordered field with four 40 px icons and empty space after them. *Cosmetic.* Suggestion: hug the content, or show more icons.
- The disabled gold primary (also on `40-wizard-account`, `42-login` and `30-settings-connect-dialog`) is muddy brown with dark text. It is unclear whether it is disabled or just dim. *Slows a task.* Suggestion: use a neutral grey disabled style, and keep gold for the enabled state only.

## 09 / 10 Drill down: group and category (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 7 | `09-drill-group.desk.en`: the hero "3,480.29 €" with the per-month bars is strong. |
| 4 | data presentation | 7 | `09-drill-group.desk.en`: the "Average 348 €" label at y 273 collides with the top of the Sept bar. |
| 6 | consistency | 8 | `10-drill-category.desk.en`: it uses the same layout as 09, and the breadcrumb "Spending › Food & Dining" is good. |
| 7 | phone experience | 7 | `09-drill-group.phone.de`: every transaction repeats "VISA Debitkartenumsatz vom 28.1…" truncated, so there are two grey lines per row. |
| 9 | visual craft | 6 | `09-drill-group.desk.en`: the "Categories" card is stretched to match "Top merchants", which leaves about 220 px empty (y 700–920). |

**Findings**

- `09-drill-group.desk.en`, the "Top merchants" / "Categories" two-column row: the Categories card has 4 rows but is stretched to the height of the 8-row Merchants card. That leaves an obvious empty block. *Cosmetic.* Suggestion: let the cards keep their natural height, or put Categories above Merchants in a single column.
- `09-drill-group.desk.en`, hero card: the left half has about 130 px of empty space under "largest 94.95 €" (y 320–450). It appears on every hero (09, 10, 14, 15, 19). *Cosmetic.* Suggestion: put a mini breakdown there, or shorten the chart height.
- `09-drill-group.desk.en`, "Average 348 €" annotation: the label text overlaps the Sept bar top at x 1330–1415. *Cosmetic.* Suggestion: place the label left of the first bar, or above the line with a dark backing.
- `10-drill-category.desk.en`: every row shows the same "Groceries" pill inside a Groceries-only view, which is redundant. *Cosmetic.* Suggestion: hide the pill when the list is scoped to one category.
- `10-drill-category.desk.en`, "Top merchants" at full width with 4 rows: the bars span about 1,125 px, so short bars look tiny and the label and number are far apart. *Cosmetic.*
- `09-drill-group.desk.en`, category filter chips: "Food & Dining 0" and "Food delivery 0" are shown as tappable chips with zero items. *Cosmetic.* Suggestion: hide them or dim them.
- **Keep:** the "↑ 35 % vs. the period before" chip in coral (up means worse for spending), which is semantically right.

## 11 Fixed costs list (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 8 | `11-recurring-list.desk.en`: hero "1,407.01 €", then "Next up", then "What changed", then "Running". The order is logical. |
| 4 | data presentation | 7 | `11-recurring-list.desk.en`: in "Running", the due-date labels are not in a column ("In 2 days" at x 1267, "15 Jan 2027" at x 1222). |
| 6 | consistency | 7 | `11-recurring-list.desk.en`: the change badges ("+7.00 €" gold, "Back" blue, "New" blue) use different colour logic than the "What changed" icons. |
| 7 | phone experience | 8 | `11-recurring-list.phone.de`: dates are dropped, and the amount plus "≈ per month" stack is tidy. |
| 9 | visual craft | 8 | `11-recurring-list.desk.en`: the "Next up" cards with category-colour left borders are nice. |

**Findings**

- `11-recurring-list.desk.en`, "Running" rows: the due label floats left of the amount and follows its width, so the label column zig-zags. Rows with "≈ 27.07 € a month" are taller, so the label also moves vertically. *Cosmetic.* Suggestion: use a fixed-width due column and a fixed amount column.
- `11-recurring-list.desk.en`, hero: the right half "Next up" is dense, while the left half has about 90 px of empty space under the subline. That is acceptable. **Keep** the split.
- `11-recurring-list.desk.en`, the dashed gold "3 savings plans run along" note at the bottom: this is a good, low-weight cross-link. **Keep.**

## 12 Fixed costs calendar (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 7 | `12-recurring-calendar.desk.en`: today (30) has a gold outline and the paid progress bar runs across the top. |
| 4 | data presentation | 5 | `12-recurring-calendar.desk.en`: the chips in the calendar cells are truncated to "Ha…", "Spar…", "Nor…", and the names are unreadable. |
| 6 | consistency | 7 | `12-recurring-calendar.phone.de`: on phone the cells use dots and a total instead of chips. That is better, and it differs from desk. |
| 7 | phone experience | 8 | `12-recurring-calendar.phone.de`: the dot and total cells are legible at 44 px. |
| 9 | visual craft | 6 | `12-recurring-calendar.desk.en`: the calendar card ends at y 805, while the "Day by day" column runs to y 1325, which leaves about 520 × 800 px of empty canvas. |

**Findings**

- `12-recurring-calendar.desk.en`, cell chips: with 100 px cells, the name and amount chips truncate names to 2 to 4 characters. *Slows a task.* Suggestion: use the phone treatment (dots plus a daily total) on desk as well, and leave names to the "Day by day" list.
- `12-recurring-calendar.desk.en`, layout: the very tall right column and the short left card create a large dead area at the lower left. *Cosmetic.* Suggestion: make "Day by day" scroll inside a card the same height as the calendar, or make the calendar sticky.

## 13 Fixed costs orbit (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 6 | `13-recurring-orbit.desk.en`: the centre "1,407 €" is clear, but the "a month" label under it is nearly invisible. |
| 4 | data presentation | 4 | `13-recurring-orbit.desk.en`: only 4 of 13 planets are labelled, and "Hausverwaltung Kr…" is truncated. |
| 7 | phone experience | 3 | `13-recurring-orbit.phone.de`: the rings are squashed to about 60 px tall, the planets overlap the centre label "1.407 €", and the labels collide. |
| 9 | visual craft | 7 | `13-recurring-orbit.desk.en`: it is atmospheric and polished as a visual. |

**Findings**

- `13-recurring-orbit.phone.de`: the orbit is unreadable at 390 px. The centre number is covered by the Hausverwaltung sphere, and "Telekom" and "Hausverwaltung Kr…" overlap. *Blocks a task* (on phone this view cannot be read). Suggestion: hide the Orbit tab on phone, or render a top-down circular orbit at full width.
- `13-recurring-orbit.phone.de`: there are 44 px of extra space above the sub-tabs (tabs at y 112, compared with y 88 on `11-recurring-list.phone.de`), so the tabs jump between views. *Cosmetic.*
- `13-recurring-orbit.desk.en`, "a month" (y 463): its contrast against the gold glow is about 1.5:1. *Cosmetic.*

## 14 Net worth (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 8 | `14-networth.desk.en`: hero "44,931.92 €" with a line chart, then account cards, then savings plans. |
| 4 | data presentation | 6 | `14-networth.desk.en`: the savings-plan coin rows (12 identical gold coins per plan) carry no information beyond "paid every month". |
| 6 | consistency | 7 | `14-networth.desk.en`: the "Add account" dashed card matches the account cards in height. Good. The chart axis starts at Dec 25 for a Jan–Oct period. |
| 7 | phone experience | 8 | `14-networth.phone.de`: the chart sits under the number at full width, and the cards stack cleanly. |
| 9 | visual craft | 7 | `14-networth.desk.en`: the hero left half is empty from y 240 to y 430. |

**Findings**

- `14-networth.desk.en`, savings-plan cards: each card spends about 40 px on 12 identical coins with month ticks. *Cosmetic.* Suggestion: show missed months as hollow coins (if that is the intent), or replace the row with a cumulative sparkline.
- `14-networth.desk.en`, account cards: the share percentages ("17%" at x 538) are 10 px and grey, the smallest text on the page. *Cosmetic.*
- `14-networth.desk.en`, hero: the same empty left column as 09, 10 and 15. *Cosmetic.*

## 15 Investments (desk.en, phone.de) and 32 hidden investments

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 8 | `15-investments.desk.en`: "9,350.57 €", the chart with monthly gain and loss bars, then Holdings. |
| 4 | data presentation | 8 | `15-investments.desk.en`: the price line plus the per-month gain and loss bars are a good combination. |
| 6 | consistency | 6 | `15-investments.desk.en`: the justETF banner sits at the bottom here and at the top in `19-etf.desk.en`. |
| 7 | phone experience | 8 | `15-investments.phone.de`: the chart and bars compress well, and the sub-tabs Depot/Analyse/Prognose/Einzahlungen are clear. |
| 9 | visual craft | 6 | `15-investments.desk.en`: Holdings has 2 cards in a 3-column grid, which leaves an empty slot (x 1070–1435, y 780–1003). |

**Findings**

- `15-investments.desk.en`, Holdings grid: two cards and an empty third column. *Cosmetic.* Suggestion: let the cards stretch to 50 % each when there are only two holdings.
- `15-investments.desk.en`, "Tax-free allowance 2026" strip: the title starts at x 303, while other cards start at x 309, and the 860 px progress bar has no end labels. *Cosmetic.*
- `15-investments.desk.en` vs `19-etf.desk.en`, the "Get full price histories?" banner: it is at the page bottom on one and directly under the tabs on the other, where it pushes the main value down 80 px. *Cosmetic.* Suggestion: put it in one consistent place (the bottom).
- `15-investments.desk.en`, holding cards: "plan 250 € per month" (gold chip) sits next to the bar and "Reinvests" sits on a third line. On phone both chips share one line. *Cosmetic.*
- `32-hidden-investments.desk.en`: the placeholders use different digit counts ("plan 999 €" compared with "plan 99 €", and "+999 €" compared with "-99 €"), which leaks order of magnitude. The chart shape and the percentages also stay visible. *Cosmetic* (a privacy concern). Suggestion: use a fixed-width placeholder.
- **Keep:** `32-hidden-investments.desk.en`, the blur treatment that keeps "€" and labels sharp. It reads as intentional, not broken.

## 16 Forecast (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 7 | `16-inv-forecast.desk.en`: there are four assumption cards first, so "68,412 €" only appears at y 400. |
| 4 | data presentation | 8 | `16-inv-forecast.desk.en`: the fan chart with the "paid in" line and milestone dots is clear. |
| 6 | consistency | 7 | `16-inv-forecast.desk.en`: the chart legend sits at the card top (y 155), about 280 px away from the chart it describes. |
| 7 | phone experience | 7 | `16-inv-forecast.phone.de`: the "eingezahlt" label at x 27 breaks the card's 35 px inner padding. |
| 9 | visual craft | 7 | `16-inv-forecast.desk.en`: the bad/good range slider is elegant, but the tiny "paid in" tick label at y 433 is crowded under the hero number. |

**Findings**

- `16-inv-forecast.desk.en`, order: the inputs (assumption cards) come before the result. For a view whose answer is the result, the hero number should lead. *Slows a task.* Suggestion: put the result and chart first, and the assumptions as a compact row under them, linked to "Adjust the numbers".
- `16-inv-forecast.desk.en`, legend: move it next to the 1Y–30Y selector, directly above the chart. *Cosmetic.*
- `16-inv-forecast.phone.de`: "eingezahlt" sits outside the content edge at x 27. *Cosmetic.*

## 17 Analysis (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 8 | `17-inv-analysis.desk.en`: four clear cards in reading order. |
| 4 | data presentation | 8 | `17-inv-analysis.desk.en`: the monthly returns tile row, with best and worst months outlined, is clear. |
| 6 | consistency | 6 | `17-inv-analysis.desk.en`: the legend "Outlined: the best and the worst month" uses a checkbox glyph (x 316, y 875), so it looks like an unchecked control. |
| 7 | phone experience | 8 | `17-inv-analysis.phone.de`: the tiles wrap into 2 × 6 cleanly. |
| 9 | visual craft | 7 | `17-inv-analysis.desk.en`: the "Ups and downs" card has an empty lower third (y 320–370). |

**Findings**

- `17-inv-analysis.desk.en`, legend checkbox: it reads as an interactive control that does nothing. *Cosmetic.* Suggestion: use a small outlined swatch instead.
- `17-inv-analysis.desk.en`, "Return in this period": "+6.7 %" has a gold bar and "+6.3 %" has a grey bar, but both are the same kind of number. The colours imply a "you" versus "other" meaning that is not explained. *Cosmetic.*
- `17-inv-analysis.desk.en`, the Drawdown x-axis starts at "Dec 25" for a Jan–Oct period (the same as `14-networth`). *Cosmetic.*

## 18 Pay-ins (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 7 | `18-inv-payments.desk.en`: the month accordion with totals is clear. |
| 4 | data presentation | 7 | `18-inv-payments.desk.en`: the expanded row amounts sit at x 1288, while the month totals sit at x 1428, which creates two amount columns. |
| 6 | consistency | 7 | `18-inv-payments.desk.en`: the "Import price history" strip at the bottom uses a different card style (a thin 56 px bar) from the other footer notes. |
| 7 | phone experience | 8 | `18-inv-payments.phone.de`: the date moves under the name and "Nicht zählen" sits on a second line. |
| 9 | visual craft | 7 | |

**Findings**

- `18-inv-payments.desk.en`: the child amounts (x 1288) do not align with the parent totals (x 1428) because "× Don't count" takes the last column. *Cosmetic.* Suggestion: move the "Don't count" action to the left of the amount, or show it on hover.

## 19 ETF detail (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 6 | `19-etf.desk.en`: the full-width justETF banner sits between the tabs and the value card and competes with the main number. |
| 4 | data presentation | 8 | `19-etf.desk.en`: the "Your average 110.71 €" dashed line and the purchase dots are an excellent detail. |
| 6 | consistency | 6 | `19-etf.phone.de`: the Depot/Analyse/Prognose/Einzahlungen sub-tabs from 15–18 disappear here and are replaced by ETF-level tabs. |
| 7 | phone experience | 7 | `19-etf.phone.de`: the "Dein Schnitt 110,71 €" label collides with a purchase dot at about x 255, y 829. |
| 9 | visual craft | 7 | `19-etf.desk.en`: there is a big empty space below the hero metadata (y 500–720) on the left. |

**Findings**

- `19-etf.desk.en`: the banner is placed above the content. *Cosmetic.* Suggestion: move it below the chart, as on `15-investments.desk.en`.
- `19-etf.phone.de`: the average-line label overlaps a dot. *Cosmetic.*

## 20–28 Settings (desk.en, desk.de, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 7 | `20-settings-bank.desk.en`: card title, then row label and description left, control right. The pattern is consistent across 21–27. |
| 6 | consistency | 6 | Mixed select styles: native `<select>` in `20-settings-bank.desk.en` ("Every day at 06:00"), `21-settings-categories.desk.en` (rule builder) and `27-settings-account.desk.en` (Country, Currency), compared with the custom dropdown "03:00 ⌄" in `24-settings-backup.desk.en`. |
| 7 | phone experience | 7 | `28-settings-list.phone.de`: a good index list. However, `20-settings-bank.phone.de` wraps "30 Tage vorher" onto two lines inside the segmented control, and `23-settings-depot.phone.de` has an extra top gap of about 40 px. |
| 8 | accessibility | 6 | `22-settings-hints.desk.en`: there are six glowing gold toggles in a column. The glow halo reduces edge definition, and "on" relies on colour alone. |
| 9 | visual craft | 7 | `24-settings-backup.desk.en`: the retention timeline is a lovely, original visual on desk. |

**Findings**

- **Native versus custom selects** (`20`, `21`, `27` compared with `24`): native selects show the OS chevron and focus styles and look foreign next to the custom pill buttons. *Cosmetic.* Suggestion: use one custom select component everywhere.
- `21-settings-categories.desk.en`, rule builder (y 663–696): the selects are 34 px tall and "+ Add rule" is 30 px tall, so the row baselines do not match. "Built-in model" is shown as selected while the description says "built-in model not found", next to a green "Offline" badge. These visual states contradict each other. *Slows a task.*
- `22-settings-hints.desk.en`: the gold accent is overloaded. Gold marks the primary button, the active nav, the warning ticks, the "Needs review" counts, toggles and links. With six gold toggles stacked, it becomes the loudest element on a low-priority page. *Cosmetic.* Suggestion: use a quieter "on" style for toggles (for example white knob on a light track) and keep gold for primary actions and attention.
- `23-settings-depot.phone.de`: the German screen shows "1.75" with a decimal point and "1000" with no grouping (on desk.en "1000" also lacks a separator, while the rest of the app formats "1,000.00 €"). The first input sits inline right and the second drops below the label, so the input positions are inconsistent within one card. *Cosmetic.*
- `23-settings-depot.desk.en`, `25-settings-privacy.desk.en`: these single short cards on a 950 px canvas leave about 60 % of the page empty. That is acceptable for settings. **Keep** the restraint, rather than padding the page out.
- `24-settings-backup.phone.de`, retention timeline: at 390 px the "1 per year" and "1 per month" labels disappear and the slots are crushed. It no longer explains anything. *Cosmetic.* Suggestion: replace it on phone with a 4-row list (Daily 7, Weekly 4, Monthly 12, Yearly 3).
- `25-settings-privacy.desk.en`: "Backups never contain the key…" appears in the Export card and again in `24-settings-backup`. *Cosmetic.*
- `26-settings-security.desk.en`, "Logged-in devices": "Log out" is plain ghost text (x 1380) and "Show" in the next row is an outlined button (x 1380–1435). These are two button styles in one list. The number inputs ("30 days", "0 min", "10 tries 15 min") have ragged right edges because the unit labels differ in width. *Cosmetic.*
- `27-settings-account.phone.de`: "Passwort ändern" sits below the label, while "Abmelden" in the next row sits inline right. *Cosmetic.*
- `20-settings-bank.phone.de`, "Anmelde-Erinnerung" segmented control: the labels wrap onto two lines ("30 Tage / vorher"). *Cosmetic.* Suggestion: use "30 T." or a select.
- **Keep:** `28-settings-list.phone.de`, an index list with a title and one-line description per section. It is very clear.
- **Keep:** `20-settings-bank.desk.de`, where the long German tab labels ("Export & Datenschutz", "Konto & Darstellung") still fit on one tab row.

## 30 Connect bank dialog (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 7 | `30-settings-connect-dialog.desk.en`: a single field, simple. |
| 8 | accessibility | 5 | `30-settings-connect-dialog.desk.en`: the disabled "Done, start syncing" has low-contrast dark text on dim gold. |
| 9 | visual craft | 7 | |

**Findings**

- `30-settings-connect-dialog.desk.en`: the only button is labelled "Done, start syncing" before anything has been entered. The dialog also has about 40 px of dead space between the hint and the divider. *Cosmetic.*

## 31 Hidden overview (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 8 | `31-hidden-overview.desk.en`: the layout is preserved, and the eye toggle is gold-highlighted in the sidebar header (x 214, y 41) and on phone (x 315, y 27). |
| 6 | consistency | 7 | `31-hidden-overview.desk.en`: all € amounts are blurred, but the percentages (8.9 %, 39 % savings rate), the sparklines and the Sankey band widths stay. |
| 9 | visual craft | 8 | `31-hidden-overview.desk.en`: the blur is soft and consistent. |

**Findings**

- **Keep:** `31-hidden-overview.desk.en`, the active-state treatment of the eye toggle (filled gold square). It is clearly "on".
- `31-hidden-overview.desk.en`: if any one amount is known, the percentages and proportions let a viewer reconstruct the others. That is visually acceptable, but worth a decision. *Cosmetic.*

## 34 Payday details dialog (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 8 | `34-payday-details.desk.en`: Balance, minus "Still going out", equals "Free to spend" in a 26 px green total. The arithmetic reads well. |
| 6 | consistency | 6 | `34-payday-details.desk.en`: "Free to spend 5,170.65 €" is green here but white in the Overview hero it explains. Elsewhere green means income. |
| 7 | phone experience | 8 | `34-payday-details.phone.de`: the "In 2 Tagen" overline above each name works better than the desk side column. |
| 9 | visual craft | 7 | `34-payday-details.desk.en`: the long "Sparplan IE00BK5BQT80 Vanguard FTSE All-World U." names wrap to 3 lines and break the 59 px row rhythm. |

**Findings**

- `34-payday-details.desk.en`: green for a balance that is not income weakens the colour semantics. *Cosmetic.* Suggestion: use white or gold, matching the hero.
- `34-payday-details.desk.en`: raw Sparplan purpose strings appear as names. *Cosmetic.* Suggestion: reuse the cleaned names shown in `14-networth` ("Vanguard FTSE All-World").

## 40 / 41 Wizard (desk.en, desk.de, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 8 | `40-wizard-account.desk.en`: the stepper on the left and the large "Welcome to Groschen" title are clear. |
| 6 | consistency | 7 | `41-wizard-country.desk.de`: the FinTS paragraph is set at 15 px, larger than the field labels (13 px), which inverts the hierarchy. |
| 7 | phone experience | 7 | `41-wizard-country.phone.de`: the skip link "Überspringen, vorerst CSV-Dateien nutzen" wraps onto two centred lines above "Weiter". |
| 8 | accessibility | 5 | `40-wizard-account.desk.en`: the disabled "Continue" has low-contrast dark text on dull gold. |
| 9 | visual craft | 8 | `40-wizard-account.desk.en`: a well-proportioned two-pane card. The phone version uses a 5-segment progress bar instead of the stepper. |

**Findings**

- `40-wizard-account.desk.en`: there is about 150 px of empty space between the password hint (y 510) and the footer divider (y 675) because the card has a fixed height. *Cosmetic.* That is acceptable for a stable layout across steps. **Keep.**
- `41-wizard-country.phone.de`, footer: the two-line skip link plus the button make a stacked, unbalanced footer. *Cosmetic.* Suggestion: use a full-width "Weiter" with a one-line text link "CSV statt Bank" under it.

## 42 Login (desk.en, phone.de)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 8 | `42-login.desk.en`: logo, "Welcome back", two fields, button. Minimal and right. |
| 8 | accessibility | 5 | `42-login.desk.en`: the disabled "Log in" (x 586–914, y 561–597) has dark grey text on muted gold, roughly 2.5:1. |
| 9 | visual craft | 8 | `42-login.phone.de`: the same card scales cleanly. |

---

## Top 10

1. **`13-recurring-orbit.phone.de`, orbit visual.** It is squashed and overlapping at 390 px: the centre "1.407 €" is covered and the labels collide. *Blocks a task.* Hide it on phone, or redraw it top-down.
2. **`12-recurring-calendar.desk.en`, calendar cell chips.** Names are truncated to "Ha…", "Spar…", "Nor…". There is also about 520 × 800 px of dead canvas under the calendar. *Slows a task.* Use the phone's dot-plus-total cells on desk, and size "Day by day" to the calendar.
3. **Disabled gold primary buttons** (`42-login.desk.en` "Log in", `40-wizard-account.desk.en` "Continue", `08-spending-group-dialog.desk.en` "Save", `30-settings-connect-dialog.desk.en`). They are muddy brown with dark text at low contrast. *Slows a task.* Use a neutral disabled style.
4. **`01-overview.desk.en`, Sankey.** The Salary → Income pass-through is a 370 × 360 px solid block that wastes a quarter of the chart. *Slows a task.* Collapse single-source stages.
5. **`02-transactions.desk.en`, row columns.** The category pills have ragged left edges (x 997 vs x 1023), there is a 350–450 px gap between the text and the pills, and the low-contrast "Girokonto" repeats on every row. *Cosmetic*, but it affects the most-used screen. Fix the column grid.
6. **The gold accent is overloaded** (`22-settings-hints.desk.en` six glowing toggles, plus nav, badges, links and CTAs). It dilutes "this needs you". *Cosmetic.* Use a quieter toggle "on" state.
7. **Desktop hero cards with dead left halves** (`09-drill-group.desk.en`, `14-networth.desk.en`, `15-investments.desk.en`, `19-etf.desk.en`), plus the stretched "Categories" card in `09-drill-group.desk.en` (about 220 px empty) and the empty third Holdings slot in `15-investments.desk.en`. *Cosmetic.* Let cards keep their natural heights and widths.
8. **Mixed control components in Settings.** Native `<select>` in `20`, `21` and `27`, a custom dropdown in `24`, ghost compared with outlined buttons in one list in `26`, and inline compared with stacked inputs in `23-settings-depot.phone.de`. *Cosmetic.* Use one select component and one row pattern.
9. **`16-inv-forecast.desk.en`, inputs before the result.** The four assumption cards push "68,412 €" to y 400, and the legend sits 280 px away from its chart. *Slows a task.* Put the result first and the assumptions under it.
10. **Phone spacing glitches.** There is an unexplained top gap on `06-transactions-empty.phone.de` (about 110 px), on `13-recurring-orbit.phone.de` and on `23-settings-depot.phone.de`. The search placeholder is clipped on `02-transactions.phone.de`, and segmented labels wrap on `20-settings-bank.phone.de`. *Cosmetic.* Standardise the header-to-title offset and shorten German labels.

**Keep (most important):** green for in, coral for out and gold for saved, carried from the KPI cards into the Sankey (`01-overview.desk.en`); the consistent card, overline and title type scale across all screens; the phone heatmap split (`07-spending.phone.de`); the ETF "Your average" line with purchase dots (`19-etf.desk.en`); the phone settings index (`28-settings-list.phone.de`); and the review tick marker on rows (`03-transactions-review.desk.en`).
