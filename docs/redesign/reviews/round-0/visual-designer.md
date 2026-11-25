# Groschen – Visual designer review (round 0)

Role: visual designer. I score hierarchy (2), data presentation (4), consistency (6), phone experience (7), accessibility/contrast (8) and visual craft (9). Lines 1, 3 and 5 are left to other roles ("-").
Pixel positions are approximate, in screenshot coordinates.

## Overall impression

The look is a cohesive dark "gold on graphite" system: one card radius (~16 px), one hairline border, one gold accent, a clear display numeral style for hero amounts (~52 px), uppercase letter-spaced eyebrows (~11 px) and a solid 24 px card gutter. The hero amounts on Overview, Net worth, Investments, Fixed costs and the drill-downs all use the same recipe, which works well. Most weaknesses are repeated patterns, not one-offs:
- **Hero cards with a dead left column.** On many pages the hero is a big number on the left, with 150–350 px of empty card below it next to a tall chart.
- **Wide rows with nothing in the middle.** On desktop the transaction rows have ~600 px of empty space between merchant and category, and the columns are not fixed widths.
- **Grey secondary text that is too faint.** Account name, percentages, ISINs, "a month" and similar text is often below WCAG AA contrast.
- **Two different navigation models.** Desktop uses a sidebar tree. Phone uses stacked segmented controls and scrolling tab strips, and those strips clip their labels.
- **Small inconsistencies everywhere.** Date-header styles, Save-button states, tab orders, button styles and dialog title sizes all vary.

---

## 01-overview (desk.en, desk.de, phone.de, phone.en)

| # | Line | Score | Based on |
|---|---|---|---|
| 1 | clarity | - | |
| 2 | hierarchy | 8 | `01-overview.desk.en`: the "Available until payday" hero at 5,170.65 € dominates correctly. The KPI row and "Where the money went" step down cleanly. |
| 3 | task efficiency | - | |
| 4 | data presentation | 6 | `01-overview.desk.en`: in the Sankey, the Salary node (x 500) and Income node (x 870) both span the full height and are joined by a ~370 × 360 px solid block that only says "99.6 % of income is salary". |
| 5 | naming | - | |
| 6 | consistency | 6 | `01-overview.desk.en`: in the KPI row, the "SAVED" eyebrow sits at y 493 while "INCOME"/"SPENDING" sit at y 507, and its amount is ~14 px higher too. `01-overview.phone.de`: the "Einen Blick wert" hints have an × dismiss button, but desk.en shows none. |
| 7 | phone | 7 | `01-overview.phone.de`: the hero, the hints and the KPI cards stack well. The Sankey sensibly drops the left nodes. The × buttons sit on their own row at x 340, which adds ~40 px per hint. |
| 8 | accessibility | 6 | `01-overview.desk.en`: "Salary 27 Oct" / "Fri 27 Nov" under the payday track and "SAVINGS RATE" are ~#6b6f78 on #15171b, below AA for 12 px text. |
| 9 | craft | 7 | `01-overview.desk.en`: the coin/payday track and the gold palette are refined. The unlabeled "glass jar" (x 810–910, y 175–340) is decorative and reads as a phone or battery. |

Findings
- `01-overview.desk.en`, **Sankey middle block**: the Salary and Income nodes are both ~360 px tall and joined by one solid ribbon. This wastes the visual centre of the page on a near-100 % flow. — *slows a task*. Suggestion: drop the source column when one source is above ~90 %. Alternatively, shrink it to a thin ribbon and give the width to the right-hand labels.
- `01-overview.desk.en`, **Sankey card bottom**: there is ~50 px of padding under "Uncategorized 510.60 €", and on the left labels the Salary label floats mid-height at x 450. — *cosmetic*.
- `01-overview.desk.en` / `.desk.de`, **KPI row misalignment**: the SAVED card's contents start ~14 px higher than INCOME/SPENDING because of the two-line bar + caption. — *cosmetic*. Suggestion: top-align the eyebrows and amounts across all three cards, and put the stacked bar below the amount at the same y as the sparkline bottoms.
- `01-overview.desk.en`, **"Available until payday" jar**: it has no label, no scale and no legend. Its fill level does not visibly relate to anything. — *cosmetic*. Suggestion: label it (e.g. "61 % left") or remove it and let the 28-day track carry the story.
- `01-overview.desk.en`, **"Worth a look" card**: the 3rd item (August 42 % above average) has no action button while the other two do, so the right-hand column ends ragged. There is also ~50 px of empty card below. — *cosmetic*.
- `01-overview.desk.en`, **sidebar**: there is ~830 px of empty sidebar between "Payments" (y 400) and the ING status (y 1255). This is acceptable on a tall capture, but it shows that the sidebar has no secondary content. — *cosmetic*.
- **keep**: the hero recipe (eyebrow → 52 px numeral → one-line explanation), the payday coin track with paid/unpaid dots, the KPI sparklines tinted per metric, and the date eyebrow "FRIDAY 30 OCTOBER".

## 02 / 03 / 04 transactions (list, needs review, filtered)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 7 | `02-transactions.desk.en`: merchant names (15 px, semibold) and amounts (right, bold) read first, which is correct. Day totals right-aligned in the header row are good. |
| 4 | data presentation | 6 | `02-transactions.desk.en`: the category chip column's left edges wander from x 997 to x 1030 depending on chip width, and the "Girokonto" column is almost invisible. |
| 6 | consistency | 5 | `02-transactions.desk.en`: date headers use two styles. "WEDNESDAY 28 OCTOBER" is grey and letter-spaced (days with a total), while "TUESDAY 27 OCTOBER" / "WEDNESDAY 21 OCTOBER" are white and bold (days without a total). |
| 7 | phone | 7 | `02-transactions.phone.de`: the two-line rows (name / purpose / chip) are well built, and the amounts are right-aligned and tabular. The filter tab strip clips "Einnahmen" at x 368. The summary line wraps "31.970,76 € raus" onto a lonely second line. |
| 8 | accessibility | 5 | `02-transactions.desk.en`: the account column "Girokonto" at x 1157 is ~#4a4d55 on #15171b (~2.3:1). Purpose lines are ~#7d8189 at 12 px. |
| 9 | craft | 7 | `02-transactions.desk.en`: real merchant logos plus letter avatars, the refund progress bar ("32.00 € of 64.00 € back") and the struck-through fully refunded amount (`phone.de`, Amazon 10 Sept) are high quality. |

Findings
- `02-transactions.desk.en`, **row layout**: ~600 px of empty space sits between the merchant (ends ~x 600) and the category chip (x 1000+). The eye has to jump across a void to connect a row's name, category and amount. — *slows a task*. Suggestion: on desktop, use fixed columns (merchant 40 %, category 20 % left-aligned, account 15 %, amount right). Alternatively, cap the list at ~1000 px so that rows are not stretched across 1170 px.
- `02-transactions.desk.en`, **category chips not on a grid**: chips are right-anchored, so short chips ("Fuel") start further right than long ones ("Restaurants & cafés"). — *cosmetic*. Suggestion: left-align the chips in a fixed-width column.
- `02-transactions.desk.en`, **two date-header styles** (see consistency score). The header looks bolder exactly when there is *no* daily total, which reverses the visual weight. — *cosmetic*. Suggestion: use one style; leave the total blank when there is none.
- `02-transactions.desk.en`, **"Girokonto" column**: it repeats on every row with too little contrast to read, yet it is still noise. — *cosmetic*. Suggestion: hide it when only one account is shown, or raise it to secondary-text grey.
- `03-transactions-review.desk.en`, **review banner** "These bookings need a category from you.": a full-width 68 px gold-bordered card holds one short sentence. It is legible and well placed, but it is heavy for its content. — *cosmetic*. Suggestion: use an inline note row, or add the count and a "Start reviewing" action so that the card earns its size.
- `03-transactions-review.desk.en`, **uncategorized row marker**: the 3 px gold left bar on "Hofladen Sonnenfeld" (x 297) plus the dashed "Uncategorized" chip is a clear and subtle signal. — **keep**.
- `04-transactions-filtered.desk.en`, **"Clear filters"** is gold text inline with the summary stats, which is good placement. The search field's × button is a boxed 28 px icon, while other inline buttons are plain. — *cosmetic*.
- `02-transactions.phone.de`, **search placeholder** "Händler, Verwendungszweck, Kategorie oder Betr" is cut mid-word. — *cosmetic*. Suggestion: use a shorter placeholder on phone ("Suchen …").

## 05-transactions-edit (dialog)

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 8 | `05-transactions-edit.desk.en`: logo + "-56.30 €" in 34 px, then the mono raw bank text, then the category chips. The order and weight are right. |
| 6 | consistency | 6 | `05-transactions-edit.desk.en`: the "Save" button is bright gold here but a muted/disabled gold in `08-spending-group-dialog.desk.en` and `30-settings-connect-dialog.desk.en`. |
| 7 | phone | 7 | `05-transactions-edit.phone.de`: a full-height sheet with sticky footer works. The chip rows fit. The edit-pencil badge on the logo is a nice touch. |
| 9 | craft | 7 | `05-transactions-edit.desk.en`: the "SUBSCRIPTIONS" group label (y 807) is orphaned directly above the sticky "Use this category for every transaction" row, so the list appears to end in an empty heading. |

Findings
- `05-transactions-edit.desk.en`, **sticky toggle row overlapping the list**: the last visible section heading "SUBSCRIPTIONS" has no chips, and the toggle row has no top shadow or divider separating it from the scroll area. — *cosmetic*. Suggestion: add a fade/shadow at the scroll edge, or move the toggle above the chip list.
- `05-transactions-edit.desk.en`, **"(general)" chips** are bold while siblings are regular. This is a good, quiet hierarchy cue. The selected chip ("Fuel", gold fill, dark text) is unmistakable. — **keep**.
- `05-transactions-edit.desk.en`, **"+ New" chips** are dashed and low-contrast (~#6b6f78) and sit at the end of each group. They read as placeholders, which is fine. — **keep**.

## 06-transactions-empty

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 7 | `06-transactions-empty.desk.en`: the centered icon, the bold "No transactions match" and the one-line hint are a good empty state. |
| 7 | phone | 5 | `06-transactions-empty.phone.de`: there is a ~110 px empty band between the top bar (y 55) and the title "Umsätze" (y 205), unlike every other phone screen, where the title sits at y ~90. |
| 9 | craft | 7 | `06-transactions-empty.desk.en`: the empty card is 195 px tall on an otherwise empty 950 px page. It is acceptable, if a bit lonely. |

Findings
- `06-transactions-empty.phone.de`, **top gap** above the page title (also seen, smaller, in `13-recurring-orbit.phone.de` and `23-settings-depot.phone.de`). It looks like a layout or scroll-restoration bug. — *cosmetic*.
- **keep**: the empty-state component (round tinted icon + title + hint) is reused consistently on 06, 10 and others.

## 07-spending, 33-period-menu

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 7 | `07-spending.desk.en`: the "Spending breakdown" card with the donut and ranked bars is clear. The page has no hero number at page level; the 2,045.14 €/month figure is 14 px. |
| 4 | data presentation | 6 | `07-spending.desk.en`: the donut has two rings with ~25 outer slivers, most of them under 3°, and it repeats exactly what the bar list on the right already shows better. |
| 6 | consistency | 5 | `07-spending.desk.en` puts the Spending/Income toggle top-right next to the period picker, while `07-spending.phone.de` stacks three segmented controls (Ausgaben/Einnahmen, Ausgaben/Fixkosten, Gruppen/Kategorien). |
| 7 | phone | 5 | `07-spending.phone.de`: the "Dein Jahr in Tagen" heatmap is cut off at June (x 755) with no scroll affordance. Two stacked "Ausgaben" segments are confusing. |
| 8 | accessibility | 5 | `07-spending.desk.en`: the percentage column "58.3 %", "17.0 %" etc. at x 1380 is ~#5d6068 on #15171b. The heatmap relies on a violet→yellow hue ramp with dark-violet cells close to the grey "no spend" cells. |
| 9 | craft | 7 | `07-spending.desk.en`: the bar list, with thin coloured progress lines under each row, is elegant. The heatmap is attractive. |

Findings
- `07-spending.desk.en`, **double-ring donut**: the outer ring of tiny category slivers adds noise. The 600 px-wide bar list already ranks groups. — *cosmetic*. Suggestion: use a single ring of groups (9 slices max), or replace the donut with a single stacked bar and give the bar list the full width.
- `07-spending.desk.en`, **dead space under the donut**: the left half of the card (x 309–660, y 570–620) is empty while the list runs to y 615, which is minor. Below the heatmap there is ~60 px of empty card. — *cosmetic*.
- `07-spending.desk.en`, **"Personal · more refunds than spending −162.37 €"** has an empty bar and no percentage, which breaks the row rhythm. — *cosmetic*. Suggestion: show a small "refund" tag in the % column instead of leaving it blank.
- `07-spending.phone.de`, **three stacked toggles**: two of them carry the label "Ausgaben", and the second one ("Ausgaben | Fixkosten") is really navigation. — *slows a task*. Suggestion: put Fixkosten in the bottom nav or a page-level tab, and keep one Spending/Income toggle.
- `07-spending.phone.de`, **heatmap clipped**: only Jan–Jun are visible. — *slows a task*. Suggestion: on phone, transpose the heatmap (weeks as rows) or show the last 6 months, ending at today.
- `33-period-menu.desk.en` / `.phone.de`: a clean menu, the selected item is gold with a check, and the width matches the trigger. — **keep**. The "Your own group" ghost button (y 104) is visually weaker than the eyebrow text around it and floats between title and card. — *cosmetic*.

## 08-spending-group-dialog

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 7 | `08-spending-group-dialog.desk.en`: Name + Icon on one row, then the category chips. The chips lack a "Categories" label, so the list starts with "HOUSING" directly. |
| 6 | consistency | 6 | `08-spending-group-dialog.desk.en`: this dialog's "Save" is muted gold (disabled?) while `05` has bright gold. Its chips are unselected-only with no "(general)" bolding, unlike `05`. |
| 9 | craft | 7 | `08-spending-group-dialog.desk.en`: the icon picker row has a lot of empty track to the right (x 930–995). Otherwise it is tidy. |

Findings
- `08-spending-group-dialog.desk.en`, **missing section label** above the chip list ("Categories in this group"). — *cosmetic*.
- `08-spending-group-dialog.desk.en`, **disabled Save** has no visible reason (the name is empty, but no hint says so). — *cosmetic*.

## 09-drill-group, 10-drill-category

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 8 | `09-drill-group.desk.en`: "SPENDING" eyebrow → "Food & Dining" → 3,480.29 € hero → monthly bars. Clear. |
| 4 | data presentation | 6 | `09-drill-group.desk.en`: every merchant row, category row and filter chip is the same yellow, so the "Categories" card loses its colour coding. The "Average 348 €" label overlaps the Sept bar (x 1330, y 273). |
| 6 | consistency | 6 | `10-drill-category.desk.en`: the eyebrow "INCOME" repeats the title "Income". On other drill pages the eyebrow is the parent ("SPENDING"). |
| 7 | phone | 7 | `09-drill-group.phone.de`: the cards stack correctly and the bar chart scales down. The filter chip row wraps onto 3 lines. |
| 9 | craft | 6 | `09-drill-group.desk.en`: the "Categories" card (x 880–1460) is ~60 % empty below "Food delivery" (y 700–920) because it is height-matched to "Top merchants". |

Findings
- `09-drill-group.desk.en`, **half-empty Categories card**: ~220 px of empty card. — *cosmetic*. Suggestion: let the cards size to content, or put Categories above Top merchants in one column and widen the merchant bars.
- `09-drill-group.desk.en`, **zero rows** "Food & Dining · 0× 0.00 €" and "Food delivery · 0× 0.00 €" get full rows and bars. — *cosmetic*. Suggestion: collapse zero categories into "2 more with no spending".
- `09-drill-group.desk.en`, **hero left column**: under "largest 94.95 €" (y 310) the left half of the hero is empty down to y 450. — *cosmetic*.
- `10-drill-category.desk.en`, **two empty states stacked** with different icons (sparkle vs magnifier) and different copy ("Nothing to chart" / "No transactions match"). — *cosmetic*. Suggestion: show one empty state for the whole page.
- **keep**: the "↑ 35 % vs. the period before" red pill, the dashed average line, and the Months/Weekdays toggle.

## 11-recurring-list, 12-recurring-calendar, 13-recurring-orbit

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 8 | `11-recurring-list.desk.en`: the 1,407.01 € hero + "Next up" with coloured left rails, then "What changed", then "Running". The order is good. |
| 4 | data presentation | 6 | `12-recurring-calendar.desk.en`: calendar chips truncate to "Ha… −1,050 €", "Nor… 3,340 €", "Rundf… −55 €". The 2,523.48 € "fixed costs this month" disagrees visually with the 1,407.01 € hero on the List tab. |
| 6 | consistency | 6 | `11-recurring-list.desk.en`: in "Running", the "In N days" text right-aligns to the amount, so it jumps from x 1268 (Hausverwaltung) to x 1243 (FitX, two-line amount) to x 1221 ("15 Jan 2027"). |
| 7 | phone | 6 | `11-recurring-list.phone.de`: the "Laufend" rows drop the due date entirely. Two segmented controls (Liste/Kalender/Orbit + Ausgaben/Fixkosten) stack beside the title. In `13-recurring-orbit.phone.de` the orbit labels overlap the centre total. |
| 8 | accessibility | 6 | `13-recurring-orbit.desk.en`: "a month" under 1,407 € is ~#5a5d66 on a gold glow, which is unreadable. In `12-recurring-calendar.desk.en` the legend colours "Standing order" (teal) and "Salary" (green) are nearly identical. |
| 9 | craft | 7 | `11-recurring-list.desk.en`: the "+7.00 €" price-change pills and the "New"/"Back" tags are nicely restrained. The dashed gold "3 savings plans run along" footer card is a good tertiary style. |

Findings
- `11-recurring-list.desk.en`, **"Next up" rows**: ~60 px gap between "In 2 days" (x 972) and the payee (x 1078), and ~110 px of dead space in the hero's left column under "16,884.11 € a year". — *cosmetic*.
- `11-recurring-list.desk.en`, **ragged "In N days" column** (see consistency). — *cosmetic*. Suggestion: give the due column a fixed right edge independent of the amount, and put "≈ 27.07 € a month" in its own sub-line under a fixed-width amount column.
- `12-recurring-calendar.desk.en`, **~520 px of empty space** under the calendar (x 285–1080, y 805–1325), because the "Day by day" column is much taller. — *cosmetic*. Suggestion: make "Day by day" scroll inside a card of calendar height, or move it below the calendar.
- `12-recurring-calendar.desk.en`, **truncated chips**: day cells are 100 px wide but chips show 2–4 letters of the payee. — *slows a task*. Suggestion: show the amount only plus a logo/initial dot, as the phone version already does with dots (`12-recurring-calendar.phone.de`).
- `13-recurring-orbit.desk.en`, **orbit**: decorative. Only 4 of 13 planets are labeled, the yearly ring is hard to tell from the quarterly one, and ~350 px of card is empty around it. — *cosmetic*. It is fine as an "alternate view", but it should not count as the information view.
- `13-recurring-orbit.phone.de`, **overlapping planets and labels** ("Telekom", "Hausverwaltung Kr…") on top of "1.407 € im Monat". — *cosmetic*.
- **keep**: "What changed" rows with typed icons (new / back / stopped / pricier) and right-aligned relative dates; the today cell's gold outline in the calendar; the calendar's paid/expected legend.

## 14-networth

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 8 | `14-networth.desk.en`: the 44,931.92 € hero with the green delta pill and a line chart; account cards; savings plans. Clear tiers. |
| 4 | data presentation | 6 | `14-networth.desk.en`: the three savings-plan cards show identical 12-coin strips whether the plan is 50 € or 800 €, so the coins carry no information. |
| 6 | consistency | 7 | `14-networth.desk.en`: the account cards match the hero style. The "Add account" dashed card matches the dashed "savings plans" card in `11`. |
| 7 | phone | 8 | `14-networth.phone.de`: the chart sits inside the hero, and the cards and plans stack cleanly. |
| 9 | craft | 7 | `14-networth.desk.en`: the hero's left column is empty from y 240 to y 420 (~340 × 180 px). |

Findings
- `14-networth.desk.en`, **coin strips**: they are pretty but uniform. — *cosmetic*. Suggestion: scale coin size or fill by amount, or show missed months as hollow coins so that the strip means something.
- `14-networth.desk.en`, **"RUNNING" status pills**: three identical green caps pills compete with the amounts. — *cosmetic*. Suggestion: show a status only when it is not "running".
- `14-networth.desk.en`, **account cards**: the "17 % / 62 % / 21 %" share bars are a good small-multiple. — **keep**.

## 15-investments, 32-hidden-investments, 16/17/18 sub-pages, 19-etf

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 7 | `15-investments.desk.en`: the 9,350.57 € hero is strong. The combined price chart + monthly gain/loss bars below it is dense but well layered. |
| 4 | data presentation | 7 | `17-inv-analysis.desk.en`: the drawdown chart with its minimum labelled "−12.7 % (Jun 26)" and the monthly-returns heat-row with outlined best/worst are excellent. |
| 6 | consistency | 5 | `19-etf.desk.en`: the ETF tabs read "Overview / Analysis / Forecast / Facts", but the sidebar order is "Forecast / Analysis / Payments". The ETF page uses underline tabs where Investments uses the sidebar. The eyebrow is "INVESTMENTS" in en and "DEPOT"/"VERMÖGEN" in de. |
| 7 | phone | 6 | `15-investments.phone.de`: the tab strip "Überblick / Prognose / Analyse / Einzahlungen" clips "Einzahlungen" at x 375. In `17-inv-analysis.phone.de` the monthly-returns row is cut at June. In `19-etf.phone.de` the label "Dein Schnitt 110,71 €" overlaps the price line. |
| 8 | accessibility | 5 | `15-investments.desk.en`: the ISIN "IE00BK5BQT80" (mono, ~#4f525a), "85 % of the depot" and "Savings plan 300.00 € per month" (y 300) are all below AA. |
| 9 | craft | 7 | `15-investments.desk.en`: the Holdings grid leaves an empty third slot (x 1060–1435, y 780–1000) next to the 2 ETF cards. The hero's left column is empty from y 310 to y 640. |

Findings
- `15-investments.desk.en`, **Holdings empty slot**: 2 cards in a 3-column grid. — *cosmetic*. Suggestion: with fewer than 3 holdings, use 2 equal columns.
- `15-investments.desk.en`, **hero dead space**: ~330 px of empty left column under the hero text, while the chart column runs to y 630. — *cosmetic*. Suggestion: put the tax-free-allowance meter and the holdings split bar into that column.
- `15-investments.desk.en`, **"Get full price histories?" banner**: placed last, with long single-line copy (~1060 px measure). It is the same component as the top banner on `19-etf.desk.en`, but placed differently. — *cosmetic*.
- `16-inv-forecast.desk.en`, **range slider**: the "Bad case – Good case" bar has a draggable-looking gold knob, but it is a display. The "paid in" label (x 329, y 433) floats above a tick and reads like a field label for 68,412 €. — *cosmetic*. Suggestion: draw it as a non-interactive range bar (no knob shadow) and label the tick inline.
- `16-inv-forecast.desk.en`, **legend placement**: "Middle outcome / 8 of 10 outcomes / Paid in" sits top-right of the card, 250 px above the chart it explains. — *cosmetic*.
- `17-inv-analysis.desk.en`, **"Outlined: the best and the worst month"**: it is drawn as an empty checkbox, so it looks like a control. — *cosmetic*. Suggestion: use an outlined swatch instead of a checkbox.
- `17-inv-analysis.desk.en`, **"Return in this period" bars**: +6.7 % fills 100 % and +6.3 % fills ~93 %, so the bars exaggerate a tiny difference with no scale. — *cosmetic*.
- `18-inv-payments.desk.en`: the month accordion rows with "2 payments" and the amount are clean. "× Not counted" reads as a state, not as the action "Don't count" (the DE "Nicht zählen" is an action). — *cosmetic*. The page has ~210 px of empty space below. **keep** the accordion rhythm (44 px rows, hairline dividers).
- `19-etf.desk.en`, **price axis "140 / 130 / …"** has no unit, while every other chart has "€". The footnote "Up to 30 Oct 2026 … Dots are your purchases." sits outside the card at y 765. — *cosmetic*.
- `32-hidden-investments.desk.en`: the blur treatment is consistent. Charts, bar heights and percentages stay visible, which is intended but leaks proportions. **keep** the active-state gold eye button at the top of the sidebar (x 215, y 40).

## 20–27 settings, 30-settings-connect-dialog

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 7 | `20-settings-bank.desk.en`: card title → row title (14 px semibold) → helper (12 px grey) → right-aligned control. A consistent and readable settings pattern. |
| 6 | consistency | 5 | `20-settings-bank.desk.en` "Every day at 06:00" and `21-settings-categories.desk.en` "merchant/contains/Category…" are native `<select>`s with browser chevrons, while `24-settings-backup.desk.en` "03:00" is a custom dropdown. `26-settings-security.desk.en` mixes text-only "Log out", outlined "Show" and outlined-with-icon "Log out all others" buttons. |
| 7 | phone | 5 | `22-settings-hints.phone.de`: the settings tab strip is scrolled so that "Bank & Import" is hidden and "Sicl…" is clipped. The "Automatisch / Nächster Monat / Buchungsmor…" segmented control is clipped. `20-settings-bank.phone.de` "7 Tage vorhe…" is clipped. |
| 8 | accessibility | 6 | `25-settings-privacy.desk.en`: the "Show log" button is so dim that it looks disabled. In `21-settings-categories.desk.en`, "Offline" is shown as a green success pill. |
| 9 | craft | 7 | `24-settings-backup.desk.en`: the Smart Recycle radio cards and stepper tiles are well made. The retention timeline (y 410–580) is sparse, and its labels "3 years" / "1 per month" collide at x 425–470. |

Findings
- `20-settings-bank.desk.en`, **contradictory schedule**: the select says "Every day at 06:00" while the helper text says "Next sync tomorrow at 05:00". Likewise, `24-settings-backup.desk.en` shows "Next backup tomorrow at 02:00" next to a "Time of day 03:00" control. Visually, these read as bugs. — *slows a task*.
- `20/21/27 settings`, **native selects**: they have a different height (32 px vs 36 px inputs), a browser chevron and different padding. — *cosmetic*. Suggestion: use the custom dropdown from Backups ("03:00") everywhere.
- `21-settings-categories.desk.en`, **"Built-in model" selected while the helper says "(built-in model not found)"**, and "Offline" is shown in success green. — *slows a task*. Suggestion: grey out the unavailable option and use a neutral or warning pill.
- `23-settings-depot.phone.de`, **"1.75"** uses an English decimal point in German UI, and "1000" has no thousands separator. On phone, the first row puts its field inline and the second row stacks it. — *cosmetic*.
- `25-settings-privacy.desk.en`, **misplaced note**: "Backups never contain the key that unlocks your bank PIN" appears under *Export*, duplicated from Backups. The page is ~60 % empty below. — *cosmetic*.
- `26-settings-security.desk.en`, **"Password login" row** has no control on the right, which breaks the row pattern (title left / control right). — *cosmetic*. Suggestion: add an "Always on" tag.
- `26-settings-security.desk.en`, **three button styles** for the same weight of action (see consistency). — *cosmetic*.
- `27-settings-account.phone.de`: "Passwort ändern" stacks below its label, while "Abmelden" sits inline on the right. — *cosmetic*.
- `24-settings-backup.phone.de`, **retention timeline**: the slot labels collapse to only "1 pro Woche / 1 pro Tag", and the boxes become 6 px slivers. — *cosmetic*. Suggestion: on phone, show it as a list of 4 rows ("Daily · 7", "Weekly · 4" …) instead of a timeline.
- `30-settings-connect-dialog.desk.en`, **error shown before input**: "No bank found by that name…" appears under an empty field in the same grey as the hint, and "Done, start syncing" is the only (disabled-looking) action. The title is ~22 px, larger than the other dialogs' ~20 px. — *slows a task*.
- **keep**: the settings tab bar (underline, gold active), the stepper tiles in Backups, the "Recommended" tag on Smart Recycle, the "This device" green tag in Security, and the 90-day bank-login progress bar in `20-settings-bank.desk.en`.

## 31-hidden-overview

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 8 | `31-hidden-overview.desk.en`: the blurred 9s keep the exact type sizes, so the layout does not shift. |
| 6 | consistency | 8 | `31-hidden-overview.phone.de`: every amount, including inline amounts in hint text ("Reisen (999,99 €)"), is masked the same way. |
| 9 | craft | 8 | `31-hidden-overview.desk.en`: the gold-filled eye toggle at x 215, y 40 clearly signals the mode. |

Findings
- `31-hidden-overview.desk.en`: percentages ("39 %", "(35.6 %)"), the Sankey band widths and the jar fill stay visible. This is acceptable for over-the-shoulder privacy and is **keep** as the intended behaviour, but consider masking the savings-rate ring too.

## 40-wizard-account, 41-wizard-country, 42-login

| # | Line | Score | Based on |
|---|---|---|---|
| 2 | hierarchy | 8 | `40-wizard-account.desk.en`: the step rail, the 28 px "Welcome to Groschen" and the 2 × 2 field grid are clear. |
| 6 | consistency | 7 | `40-wizard-account.desk.en` and `42-login.desk.en`: the primary buttons are muted gold (disabled until valid) without a reason shown. `41-wizard-country.desk.en` "Continue" is bright. The state logic is consistent, but the disabled state looks like a colour variant, not like "disabled". |
| 7 | phone | 5 | `41-wizard-country.phone.de`: the skip link "Überspringen, vorerst CSV-Dateien nu…" overflows the card's right edge, and "Weiter" is pushed onto its own line, left-centred at x 125–197. |
| 9 | craft | 7 | `41-wizard-country.desk.de`: the FinTS explainer paragraph is 16 px grey, *larger* than the 13 px field labels and the 14 px body text, which inverts the type scale. `40-wizard-account.desk.en` has ~160 px of empty body under the fields. |

Findings
- `41-wizard-country.phone.de`, **footer overflow**: the skip link is clipped at x ~385, and the primary button is misaligned. — *blocks a task* if the skip link is the intended path for non-FinTS users on phone; otherwise *slows a task*. Suggestion: stack a full-width primary button with the skip link below it as a centred text link.
- `41-wizard-country.desk.de`, **type-scale inversion** of the explainer paragraph. — *cosmetic*. Suggestion: use 14 px secondary text in a bordered note box, as in the en "Automatic bank sync works with German banks." box.
- `41-wizard-country.desk.de`, **premature error** "Keine Bank mit diesem Namen gefunden" under an empty field (same issue as `30`). — *slows a task*.
- `42-login.desk.en`: a compact, centred card with a focused username field (gold ring) and the language switcher below it. It is good. The muted "Log in" button looks disabled even when it is just the resting state. — *cosmetic*. **keep** the overall login card.
- **keep**: the desktop wizard step rail with check/number circles and sub-labels, and the phone version's 5-segment progress bar.

---

## Top 10

1. **Desktop transaction rows have no column grid**: ~600 px of empty space between merchant and category, chips not left-aligned, and a nearly invisible "Girokonto" column (`02-transactions.desk.en`, also `03`, `04`, `09`). *slows a task*. Fix: fixed columns or a capped list width.
2. **Phone tab strips and segmented controls clip their labels** with no scroll cue: "Einzahlungen" (`15-investments.phone.de`), "Sicl…" / "Buchungsmor…" (`22-settings-hints.phone.de`), "7 Tage vorhe…" (`20-settings-bank.phone.de`), "Einnahmen" (`02-transactions.phone.de`). *slows a task*.
3. **Wizard footer overflows on phone**: the skip link is clipped and "Weiter" is misaligned (`41-wizard-country.phone.de`). *blocks/slows a task* during first run.
4. **Navigation model differs by device**: three stacked segmented controls with a duplicated "Ausgaben" (`07-spending.phone.de`), Fixkosten as a toggle (`11-recurring-list.phone.de`), ETF tab order "Analysis/Forecast" vs sidebar "Forecast/Analysis" (`19-etf.desk.en`), and "Investments" vs "Depot" eyebrows. *slows a task*.
5. **Contradictory adjacent values**: "Every day at 06:00" next to "Next sync tomorrow at 05:00" (`20-settings-bank.desk.en`), "03:00" next to "Next backup tomorrow at 02:00" (`24-settings-backup.desk.en`), and "Built-in model" selected next to "built-in model not found" (`21-settings-categories.desk.en`). *slows a task*.
6. **Heatmaps cut off at June on phone** (`07-spending.phone.de` "Dein Jahr in Tagen", `17-inv-analysis.phone.de` monthly returns), so recent months are invisible. *slows a task*.
7. **Low-contrast secondary text** below AA across screens: the account column, percentage column, ISINs, "a month", and payday-track captions (`02-transactions.desk.en`, `07-spending.desk.en`, `15-investments.desk.en`, `13-recurring-orbit.desk.en`). *slows a task*.
8. **Dead space in hero/split layouts**: an empty left column in the heroes (`14-networth.desk.en`, `15-investments.desk.en`, `09-drill-group.desk.en`), ~520 px empty under the calendar (`12-recurring-calendar.desk.en`), a half-empty Categories card (`09-drill-group.desk.en`), and an empty third Holdings slot (`15-investments.desk.en`). *cosmetic*.
9. **Sankey wastes its centre**: the Salary→Income block is ~370 × 360 px of solid colour for a 99.6 % flow, and the unlabeled jar sits in the hero (`01-overview.desk.en`). *slows a task*.
10. **Component inconsistencies**: two date-header styles in the transaction list (`02-transactions.desk.en`), the SAVED KPI card misaligned by ~14 px (`01-overview.desk.en`), native vs custom selects (`20`, `21`, `24` settings), three button styles in `26-settings-security.desk.en`, and bright vs muted Save buttons across dialogs (`05`, `08`, `30`). *cosmetic*.
