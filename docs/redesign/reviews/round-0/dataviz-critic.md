# Groschen: data visualisation review (round 0)

Role: data visualisation critic. I scored only the lines I can judge from a data-presentation point of view: 1 clarity of purpose, 4 data presentation, 7 phone experience (for the charts only), 9 visual craft (for the charts only). Everything else is "-". Screens without charts (05, 06, 20, 22-27, 30, 40-42) have no chart findings. I looked at them briefly and do not score them.

Severity scale: `blocks a task` / `slows a task` / `cosmetic` / `keep`.

---

## 01-overview (desk.en, desk.de, phone.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 7 | 01-overview.desk.en: the "Available until payday" hero answers one clear question. The tank gauge beside it answers none. |
| 2 hierarchy | - | |
| 3 task efficiency | - | |
| 4 data presentation | 6 | 01-overview.desk.en: the "Where the money went" Sankey is well labelled (value plus %), but the left half is a near-empty Salary→Income block. The KPI mini bars have no axis or labels. |
| 5 navigation | - | |
| 6 consistency | - | |
| 7 phone | 7 | 01-overview.phone.de: the Sankey drops its source column, which is the right choice, and the labels stay legible. The tank gauge is dropped. |
| 8 accessibility | - | |
| 9 visual craft | 7 | 01-overview.desk.en: the payday strip and the KPI cards are tidy, but the glowing tank and the glowing coin are ornament. |

Findings
- **01-overview.desk.en, tank/battery gauge to the right of "5,170.65 €"**: the fill is about 70 % but has no label, no scale and no reference. Is it the share of the month's money left? The share of days left? Nobody can tell. It repeats the hero number less precisely. Severity: `slows a task`. Suggestion: remove it, or replace it with one labelled bullet bar such as "5,170 € left of 7,768 € at salary · 28 of 31 days to go", so that money left can be compared with time left (the "on track?" question).
- **01-overview.desk.en, payday day-strip ("TODAY · 28 days to payday", dots per payment)**: a good form. A 31-cell timeline with dots for payments answers "what hits my account before payday". However, the dots carry no amount, so the 1,050 € rent and the 2.99 € Apple payment look the same. Severity: `cosmetic`. Suggestion: scale dot size, or add a tick height, by amount. Show the amount on hover/tap. `keep` the strip itself.
- **01-overview.desk.en, Sankey left half**: Salary is 99.6 % of income, so about 360 px of width shows one flat green slab going into "Income". The two tiny sources (95.40 € and 43.20 €) are hairlines that cannot be read. Severity: `cosmetic`. Suggestion: collapse the source side into the "Income 33,538.60 €" node label, listing the small sources as text under it (the phone layout already does this), and give the width to the outflows.
- **01-overview.desk.en, Sankey right side**: the outflows add up to 33,700.97 €, but income is 33,538.60 €. The −162.37 € "Personal" net refund from the Spending page is missing, so the bands do not balance without explanation. Severity: `cosmetic`. Suggestion: show "Personal −162 € (refunds)" as a small inflow, or add a footnote.
- **01-overview.desk.en, Sankey ordering**: savings sit at the top (Invested, Put aside, Stays) and spending sits below, sorted by size. This is clear and well labelled with € and %. `keep`.
- **01-overview.desk.en, INCOME / SPENDING mini bars**: there are 10 bars with no month labels and no baseline value. The highlighted last bar is October, which is a month still in progress. The income bars are all the same height, so they say nothing. Severity: `cosmetic`. Suggestion: keep the spending sparkbar but label the first and last month, and mark the current month as partial (hatched). Drop the income sparkbar, or show it only when income varies.
- **01-overview.desk.en, SAVED tri-colour bar + "39 %" ring**: the bar has three segments (invested / put aside / stays), but the caption names only two ("3,000.00 € invested · 1,991.75 € stays"), so the teal segment, the largest, is unexplained here. The ring repeats the same 39 % a second time. Severity: `slows a task`. Suggestion: add "8,095 € put aside" to the caption (or a tiny legend), and replace the ring with plain text "39 % savings rate".
- **01-overview.phone.de, Sankey hint "Zeig auf ein Band, um ihm zu folgen"**: hover wording on a touch device. Severity: `cosmetic`.

## 02 / 03 / 04 transactions (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 | - | |
| 4 data presentation | 6 | 03-transactions-review.desk.en: day subtotals, the strike-through of refunded amounts and the "32.00 € of 64.00 € back" mini bar. |
| 9 | 7 | 02-transactions.desk.en: amount column is right-aligned with tabular figures. |

Findings
- **03-transactions-review.desk.en, "Thursday 10 September" subtotal −160.53 €**: this total includes the Amazon −34.99 € row, even though that row is struck through as "All of it came back". The row and the day total disagree. Severity: `slows a task`. Suggestion: exclude fully refunded amounts from the day total, or show the total as "−125.54 € (−160.53 € before refunds)".
- **03-transactions-review.desk.en, "32.00 € of 64.00 € back" inline progress bar (Lena Berger, 7 Sept)**: a good small form for a partial refund, with the number stated and the bar as support. `keep`.
- **02-transactions.desk.en, header "42,057.91 € in · 31,970.76 € out"**: the period is the same as Overview (Jan–Oct), where income is 33,538.60 € and spending 20,451.45 €. The difference (transfers to your own accounts and savings) is not explained, so the two screens appear to contradict each other. Severity: `slows a task`. Suggestion: label the transaction totals "all money movements" and add a tooltip that reconciles them to Overview ("incl. 9,095 € own transfers / savings").
- **02-transactions.desk.en, day subtotal right-aligned above the rows**: works and is right-aligned with the amounts. `keep`.

## 07-spending (desk.en, desk.de, phone.en, phone.de) and 33-period-menu

| Line | Score | Based on |
|---|---|---|
| 1 | 7 | 07-spending.desk.en: "Spending breakdown" plus "most on Housing (58 %)" states the answer. |
| 4 data presentation | 6 | 07-spending.desk.en: the bar list is excellent, but the two-ring sunburst duplicates it and adds unreadable sub-slices. The "Your year in days" heatmap uses a hue ramp. |
| 7 phone | 5 | 07-spending.phone.de: the heatmap is cut after June and shows no scroll hint. The donut takes the full width before any number. |
| 9 | 7 | 07-spending.desk.en: clean bar list, with a calm palette that matches the Sankey colours. |

Findings
- **07-spending.desk.en, ranked bar list (Housing 11,929.82 € 58.3 % … Uncategorized)**: the right form. It is sorted, has exact values and shares, colours that match the Sankey, and handles the negative "Personal · more refunds than spending" honestly. `keep`.
- **07-spending.desk.en, two-ring sunburst "Total 20,451 €"**: the inner ring repeats the bar list exactly. The outer ring (sub-categories) has no labels, uses shades of the parent hue, and its slivers under 2 % cannot be told apart. It answers no question the list does not answer better. Severity: `slows a task` on phone (07-spending.phone.de, where it pushes the list down by about 350 px), otherwise `cosmetic`. Suggestion: drop the donut. Let each bar row expand into its sub-categories (nested bars), or show the sub-categories as a stacked segment inside each bar.
- **07-spending.desk.en, legend percentages ("58.3 %", "17.0 %")**: very low-contrast grey, about 2:1 by eye. Severity: `cosmetic`. Suggestion: raise them to the secondary text colour.
- **07-spending.desk.en, "Your year in days" calendar heatmap**: the ramp runs violet → magenta → orange → yellow. That is a multi-hue ramp in which magenta and orange do not read as clearly ordered. A legend of five steps with no € thresholds ("Less ■■■■■ More") makes amounts impossible to recover. Severity: `slows a task`. Suggestion: use a single-hue sequential ramp (light to dark of one hue) and print the € bin edges in the legend (e.g. "<20 €, 20–50, 50–100, 100–250, >250 €"). Keep the three summary stats below it (`keep`: "185 days without spending · 1,233.55 € on your priciest day · 177.08 € on an average spending day").
- **07-spending.desk.en, heatmap Sat/Sun rows almost entirely grey**: bank booking dates push weekend card payments to Monday. The chart therefore shows when the bank booked, not when you spent, and "185 days without spending" inflates. Severity: `slows a task` (the conclusion is misleading). Suggestion: use the card transaction date when the bank provides it, or add the caption "by booking date".
- **07-spending.desk.en, heatmap future cells (Nov–Dec)**: drawn as dashed outlines, which is good, but they sit close to "Nothing" grey. `cosmetic`.
- **07-spending.phone.de, heatmap**: cropped at June with no fade or scroll affordance, so July–October (the most recent data) is invisible. Severity: `slows a task`. Suggestion: on phone, show the last 13 weeks or a month-by-month mini calendar, or rotate the grid (weeks as rows, scrolling vertically). At minimum, start the scroll at today.
- **33-period-menu.desk.en**: the period options (Month, Last 30 days, Year to date, Year, Last 12 months, All time) are clear. The selected period is echoed in each chart subtitle. `keep`.

## 08-spending-group-dialog
No chart. Category chips reuse the chart colour per group (blue = Housing, amber = Food), so the colour coding stays consistent across screens. `keep`. Scores: all "-".

## 09-drill-group (Food & Dining) (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 | 8 | 09-drill-group.desk.en: "Spent 3,480.29 € · +35 % vs. the period before · per month" bar chart. |
| 4 data presentation | 8 | 09-drill-group.desk.en: monthly bar chart with zero baseline, gridlines and an "Average 348 €" reference line. Merchant bars are ranked. |
| 7 phone | 8 | 09-drill-group.phone.de: the chart scales down, the axis labels thin out, and the average label stays readable. |
| 9 | 7 | 09-drill-group.desk.en: the "Average 348 €" label collides with the Sept bar top. |

Findings
- **09-drill-group.desk.en, "Per month" bar chart**: a textbook form for "is this month unusual?". It has a zero baseline, a dashed average and month labels. `keep`. Small issue: the "Average 348 €" label sits on top of the Sept/Oct bars. Severity: `cosmetic`. Move it to the left end or above the plot area.
- **09-drill-group.desk.en, "+35 % vs. the period before"**: the reference period is not named (Mar–Dec 2025? Jan–Oct 2025?). A year-to-date comparison is ambiguous. Severity: `slows a task`. Suggestion: write "vs. Jan–Oct 2025 (2,578 €)".
- **09-drill-group.desk.en, Top merchants bars**: each bar is scaled to the largest merchant (Lidl fills the track), while the % beside it is the share of the total. Two different encodings sit on one row. It is acceptable, but Lidl's full bar reads as "100 %" next to "22.3 %". Severity: `cosmetic`. Suggestion: scale the bars to share of total, or drop the % and keep counts.
- **09-drill-group.desk.en, Categories card**: "Food & Dining · 0× 0.00 €" and "Food delivery · 0× 0.00 €" are shown with empty bars. They are noise. Severity: `cosmetic`. Suggestion: hide zero rows, or fold them into a "+2 unused" line.

## 10-drill-category (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 | 4 | 10-drill-category.desk.en: the page is titled "Income" and shows "Received 0.00 €", while Overview says income is 33,538.60 € for the same period. |
| 4 | 5 | 10-drill-category.desk.en: the "Nothing to chart" empty state is fine as a form, but contradicts the data. |

Findings
- **10-drill-category.desk.en, "Income · Received 0.00 € · 0 bookings"**: a category named "Income" is empty because salary is booked under "Salary". The user sees two incomes that disagree. Severity: `slows a task`. Suggestion: name the empty category something else, or make the "Income" drill aggregate the whole income group. Also, the sidebar highlights "Spending" while the page is Income.
- **10-drill-category.desk.en, empty state "Nothing to chart"**: clean, with a clear message. `keep`.

## 11-recurring-list (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 | 8 | 11-recurring-list.desk.en: "Fixed costs per month 1,407.01 €" with "Next up" beside it. |
| 4 | 6 | 11-recurring-list.desk.en: the "Running" list is sorted by raw amount across different rhythms. |
| 7 | 7 | 11-recurring-list.phone.de: the list drops "In N days" but keeps the monthly equivalents. |
| 9 | - | |

Findings
- **11-recurring-list.desk.en, "Running" sort order**: rows are sorted by the raw payment amount. Lime Technology (129 €/year ≈ 10.75 €/month) ranks above Netflix (15.99 €/month), and Rundfunkbeitrag (55.08 €/quarter ≈ 18.36 €) sits above Telekom-level items. So the ranking does not answer "what costs me most per month". Severity: `slows a task`. Suggestion: sort by monthly equivalent, show that figure as the primary number, and give the per-payment amount secondary.
- **11-recurring-list.desk.en, price-change badges "+7.00 €", "+9.00 €" and the "What changed" timeline**: answers "what got more expensive" directly, with old → new values. `keep`.
- **11-recurring-list.desk.en, missing overview chart**: 13 recurring items worth 1,407 € a month, with no visual share. Suggestion: one horizontal 100 % stacked bar under the hero ("Rent 75 % · Energy 6 % · …"), or bars in the list rows like on Spending. Severity: `cosmetic`.

## 12-recurring-calendar (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 | 6 | 12-recurring-calendar.desk.en: "2,523.48 € fixed costs this month" conflicts with "1,407.01 € per month" on the List tab. |
| 4 | 6 | 12-recurring-calendar.desk.en: names in the month-grid chips are truncated to "Ha…", "Nor…", "Rundf…". |
| 7 | 8 | 12-recurring-calendar.phone.de: dots plus day totals per cell, which reads better than desktop. |
| 9 | 7 | 12-recurring-calendar.desk.en: the paid/expected/standing order/salary legend is clear. |

Findings
- **12-recurring-calendar.desk.en, header "2,523.48 € fixed costs this month"** vs **11-recurring-list.desk.en "1,407.01 €"**: the calendar adds standing orders and savings plans (800 + 250 + 50 €), and it also lists the salary. These are the same words with two numbers. Severity: `slows a task`. Suggestion: split the header into "1,423 € fixed costs + 1,100 € savings plans", or exclude savings from "fixed costs".
- **12-recurring-calendar.desk.en, progress bar under the header (fully salmon)**: a "paid vs still to come" bar is a good form, but at the end of the month it is simply full. `keep`, but colour it by type (fixed vs savings) so it carries information.
- **12-recurring-calendar.desk.en, chips "Ha… −1,050 €", "Spar… −800 €", "+1"**: names truncated to 2–5 letters cannot be identified. The 1 Oct cell overflows into "+1". Severity: `slows a task` (readers must use the side list). Suggestion: on desktop, adopt the phone pattern (dots plus one day total in the cell) and let the "Day by day" list carry the names. Or make the cells taller and allow two-line chips.
- **12-recurring-calendar.desk.en, salary shown in a fixed-costs calendar (27 Oct, Nordlicht 3,340 €)**: useful context, but it inflates the visual weight of a non-cost. `cosmetic`.
- **12-recurring-calendar.phone.de, cell dots + "−2.150 €" day totals**: a compact form with precise values. `keep`.

## 13-recurring-orbit (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 | 3 | 13-recurring-orbit.desk.en: "Your month in orbit" needs a 2-line instruction to decode, and still does not answer "when and how much". |
| 4 | 2 | 13-recurring-orbit.desk.en: 3D-tilted ellipses, unlabeled spheres, size encodes cost without a scale, and position encodes the due date without day marks. |
| 7 | 2 | 13-recurring-orbit.phone.de: spheres overlap the "1.407 € im Monat" centre label and each other. Labels are cut ("Hausverwaltung Kr…"). |
| 9 | 4 | 13-recurring-orbit.desk.en: glowing sun, glossy spheres and starfield particles: decoration that competes with the data. |

Findings
- **13-recurring-orbit.desk.en, whole chart**: the encoding is angle = days until due (front = due), ring = rhythm, and sphere area = amount. Perspective foreshortening distorts both angle and size. Only 4 of 13 items are labelled, there are no amounts, there are no day ticks, and spheres overlap near the front (Hausverwaltung covered by another sphere). Precise reading is impossible. Severity: `slows a task`. Suggestion: replace it with a "next 30 days" horizontal timeline (days on x, one row per rhythm or a single lane, bar or dot size by € with labels). Or remove the tab: List + Calendar already answer every question. If kept as a delight view, make it flat (no tilt), label every body with name and €, and add day ticks.
- **13-recurring-orbit.desk.en, legend "every 4 weeks · 1, monthly · 9, quarterly · 1, yearly · 2"**: ellipse icons do not show which ring is which. Severity: `cosmetic`.
- **13-recurring-orbit.phone.de**: unusable at 390 px. The centre total is overlapped by the HUK sphere. Severity: `slows a task`. Suggestion: hide the Orbit tab on phone.

## 14-networth (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 | 8 | 14-networth.desk.en: "Today 44,931.92 €, ↑13,592.05 € Jan–Oct 2026" plus the trend line. |
| 4 | 6 | 14-networth.desk.en: the area fill sits on a truncated 25k € baseline. The 12-coin strips encode nothing. |
| 7 | 8 | 14-networth.phone.de: the line chart scales well with thinned axis labels. |
| 9 | 7 | 14-networth.desk.en: clean line with markers. The coins are ornament. |

Findings
- **14-networth.desk.en, net-worth area chart (y-axis 25k–45k €)**: a filled area implies quantity from the baseline. With the baseline at 25k, the growth from 31k to 45k looks like roughly 3.5× rather than +44 %. Severity: `slows a task` (it exaggerates). Suggestion: either remove the area fill (a plain line is fine on a truncated axis) or start the y-axis at 0. Better still, make it a stacked area per account (Girokonto / Extra-Konto / Depot), which answers "where did the growth come from"; the account cards already have the shares.
- **14-networth.desk.en, starting point "Dec 25"**: the period is Jan–Oct, but the line begins at Dec 25 (the opening balance). This is sensible, but unlabelled. `cosmetic`: label the first point "start 31,340 €".
- **14-networth.desk.en, account cards with share bars "17 % / 62 % / 21 %"**: a simple part-to-whole form with exact %. `keep`.
- **14-networth.desk.en, savings-plan coin strips (12 identical gold coins, labels Nov/Feb/May/Aug)**: every coin is identical, so the strip carries no information. Its only possible message is "a payment was missed", which never appears. The gloss is ornament. Severity: `cosmetic`. Suggestion: replace it with text ("12 of 12 paid on time") and show coins only when one is missing (hollow coin = missed).

## 15-investments (desk.en, phone.de) and 32-hidden-investments

| Line | Score | Based on |
|---|---|---|
| 1 | 6 | 15-investments.desk.en: "Value without deposits" line is hard to interpret. |
| 4 | 6 | 15-investments.desk.en: the monthly gain/loss bars are labelled and good. The holding sparklines have no scale. The return % differs from the ETF page. |
| 7 | 7 | 15-investments.phone.de: the chart and the gain/loss bars fit, and the "+564 € / −429 €" axis extremes are a nice touch. |
| 9 | 7 | 15-investments.desk.en: the gold line on dark is legible. The gradient area is decorative but quiet. |

Findings
- **15-investments.desk.en, "Value without deposits" line (8k–10k €)**: the line ends at today's real depot value (9,350 €), but it starts at about 8.85k in January, when the depot actually held about 6.3k. The reader assumes the depot started at 8.85k. The concept (value minus deposits made since then) is not explained on the chart. Severity: `slows a task`. Suggestion: plot two lines, "depot value" and "money paid in" (cumulative step), with the gap between them shaded as gain/loss. That is the standard investment chart and is self-explanatory. The "Money paid in" toggle hints at it; make it the default.
- **15-investments.desk.en, "Gain and loss per month" bars (−111 € … +564 €)**: a diverging bar chart, labelled per bar, with red/green and zero-centred. It answers "which months hurt". `keep`. The red/green pairing needs a secondary cue for colour-blind users: the signs on the labels already provide it, so keep the signs.
- **15-investments.desk.en, holding-card sparklines (Vanguard, iShares)**: the y-range is unknown and differs per card, so the two cannot be compared and the wiggles mean nothing on their own. Severity: `cosmetic`. Suggestion: drop them or put both on a shared % scale.
- **15-investments.desk.en, holdings 85/15 bar**: a good part-to-whole form. `keep`.
- **15-investments.desk.en, "Tax-free allowance 2026 · 95.40 € of 1,000.00 €" bar**: the right form (bullet/progress) with exact numbers. `keep`.
- **15-investments.desk.en "Vanguard +7.5 % · 474 €"** vs **19-etf.desk.en "+17.2 % · 1,160.97 €"** vs **19-etf.desk.en "Price +11.2 %"**: three different returns for one fund on adjacent screens (period return, since-purchase return and 1-year price change), none labelled with its basis. Severity: `slows a task`. Suggestion: always suffix the basis: "+7.5 % Jan–Oct", "+17.2 % since first buy", "price +11.2 % 1Y".
- **32-hidden-investments.phone.de**: amounts are blurred, but the chart shapes, % and digit counts remain ("9.999,99 €" vs "99,99 €"), so magnitudes leak to someone looking over a shoulder. The same happens on 31-hidden-overview.desk.en, where the Sankey keeps exact % ("35.6 %") and the band widths. Severity: `cosmetic` (it is a privacy screen, not a vault). Suggestion: use a fixed-width placeholder ("•••• €") regardless of real length. Keep the % (they are relative and acceptable).

## 16-inv-forecast (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 | 8 | 16-inv-forecast.desk.en: "In 10 years 68,412 €", bad/good case, and "1 in 12 futures ends below what you paid in". This is a very clear statement of uncertainty. |
| 4 | 6 | 16-inv-forecast.desk.en: the fan chart's lower edge is not visible. The band reads as filled to zero. |
| 7 | 7 | 16-inv-forecast.phone.de: everything stacks. The chart gets small (about 150 px tall) but stays legible. |
| 9 | 7 | 16-inv-forecast.desk.en: milestone dots "10k €, 25k €, 50k €" on the middle path are nice. |

Findings
- **16-inv-forecast.desk.en, outcome band ("8 of 10 outcomes")**: only the top edge (102k) is visible. The bottom edge (≈46k) disappears into the dark "Paid in" area, so the band looks like it runs from 0 to the top. The central message of a forecast, its spread, is therefore lost. Severity: `slows a task`. Suggestion: draw the 10th–90th percentile as a distinct translucent band between two thin lines, and keep "paid in" as a single dashed line, not a filled area.
- **16-inv-forecast.desk.en, range slider "Bad case 46,246 € · ● · Good case 102,388 €" with a "paid in" tick**: a good one-dimensional summary of the distribution, with the paid-in reference. `keep`.
- **16-inv-forecast.desk.en "Swing 15 % a year"** vs **17-inv-analysis.desk.en "±17 % up or down in a normal year"**: the same concept appears on two screens with two values. Severity: `slows a task` (it undermines trust). Suggestion: use one measure and one name, or state the windows ("15 % over 2.3 years of prices", "17 % in Jan–Oct").
- **16-inv-forecast.desk.en, milestone chips "100,000 € in 2040"**: this milestone lies outside the 10Y chart. That is fine, but the chip looks like it should be on the chart. `cosmetic`.

## 17-inv-analysis (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 | 7 | 17-inv-analysis.desk.en: the four cards each answer one question (return, volatility, drawdown, monthly returns). |
| 4 | 6 | 17-inv-analysis.desk.en: drawdown is good. The monthly-returns heatmap is a weak form for 10 values and conflicts with the € bars. The return bars are decorative. |
| 7 | 4 | 17-inv-analysis.phone.de: the monthly-returns row is cut after June, so July–October are invisible. |
| 9 | 7 | 17-inv-analysis.desk.en: the drawdown area with its annotated low point "−12.7 % (Jun 26)" is crisp. |

Findings
- **17-inv-analysis.desk.en, "Drawdown" chart**: the right chart for "how bad did it get", with an annotated minimum and a current-state badge ("0.9 % below its high"). `keep`. Note that it is built from monthly points, while 15-investments shows daily prices, so the intra-month lows are smoothed away. `cosmetic`.
- **17-inv-analysis.desk.en, "Monthly returns" heatmap (−1.9, +8.2, …)**: ten cells in a single row are a bar chart drawn badly: colour intensity replaces length, and the numbers carry everything. 15-investments already shows the same months as diverging € bars. Worse, the values do not line up: Feb is +8.2 % here but +497 € on a ~8.5k depot ≈ +5.8 % there, and Jul is +7.9 % vs +564 € ≈ +6.5 %. Severity: `slows a task`. Suggestion: show monthly returns as diverging % bars (one chart, toggle €/%), and add a one-line explanation of why the market return differs from the depot's € change. Keep the heatmap form only for multi-year views (years × months), where it shines.
- **17-inv-analysis.phone.de, monthly returns row**: shows Jan–Jun only, with no scroll hint. The most recent four months are hidden. Severity: `slows a task`. Suggestion: wrap into 2 rows of 6, or use vertical diverging bars.
- **17-inv-analysis.desk.en, "Outlined: the best and the worst month" checkbox**: it looks like an unchecked control, yet the outlines are already shown. It is a legend dressed as an input. Severity: `cosmetic`. Suggestion: render it as a legend swatch (outlined square).
- **17-inv-analysis.desk.en, "Return in this period" bars (+6.7 % full gold bar, +6.3 % grey bar)**: the bars have no scale. A full bar suggests "100 %/max", and they add nothing to two numbers that are already printed. Severity: `cosmetic`. Suggestion: drop the bars and show "+6.7 % your money vs +6.3 % the funds → your timing added +0.4 pts".
- **17-inv-analysis.desk.en, volatility gauge (calm → wild, "usual for stock ETFs" band)**: good. It gives a reference range so that ±17 % has meaning. `keep`. The gradient blue → gold → red is decoration but harmless.
- **17-inv-analysis.desk.en, "5 of 10 months up" split bar**: simple and precise. `keep`.

## 18-inv-payments (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 | 7 | 18-inv-payments.desk.en: "Money put in · 3,600.00 € in the last 12 months". |
| 4 | 6 | 18-inv-payments.desk.en: a month accordion of identical 300.00 € rows, with no visual of 27 months of contributions. |
| 7 | 8 | 18-inv-payments.phone.de: the accordion fits well. |
| 9 | - | |

Findings
- **18-inv-payments.desk.en, month list "October 2026 … May 2026 · 300.00 €" with "Show all 27 months"**: a constant series is listed row by row, and any irregularity (a skipped month, an extra buy) would be hidden behind "Show all". Severity: `cosmetic`. Suggestion: add a compact monthly bar strip or cumulative step line of paid-in over the 27 months above the list, so gaps and changes pop out. Keep the list for exclusion ("Not counted") actions.
- **18-inv-payments.desk.en "× Not counted"** vs **18-inv-payments.phone.de "× Nicht zählen"**: EN reads as a status, DE as an action. This matters for data trust (is the payment excluded or not?). Severity: `slows a task`. Suggestion: EN "Don't count".
- **18-inv-payments.desk.en, header "in the last 12 months"**: this screen has no period picker, unlike its siblings (Jan–Oct). `cosmetic`.

## 19-etf (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 | 8 | 19-etf.desk.en: "Your value 7,910.97 €" plus a price chart with "Your average 110.71 €". |
| 4 | 7 | 19-etf.desk.en: the purchase dots and the average-cost reference line are excellent. The unexplained 100–140 y-range and the competing returns cost points. |
| 7 | 8 | 19-etf.phone.de: the chart keeps the purchase dots and the average line. "Dein Schnitt" collides with a dot. |
| 9 | 8 | 19-etf.desk.en: restrained styling. |

Findings
- **19-etf.desk.en, price chart with purchase dots + "Your average 110.71 €" dashed line**: answers "am I above my buy-in, and did I buy high or low" in one glance. `keep`. This is the best chart in the app.
- **19-etf.desk.en, three returns (+17.2 %, +11.2 %, and +7.5 % on 15-investments)**: see the 15-investments finding. Label the basis of each. `slows a task`.
- **19-etf.desk.en, y-axis "100–140" with no unit**: it is a price per unit in €, but this is not stated, unlike every other axis, which carries €. `cosmetic`. Suggestion: "100 €".
- **19-etf.phone.de, "Dein Schnitt 110,71 €" label**: overlaps a purchase dot and the line. `cosmetic`.

## 31-hidden-overview (desk.en, phone.de)
| Line | Score | Based on |
|---|---|---|
| 4 | 7 | 31-hidden-overview.desk.en: the charts keep their shapes and %, which leaves the screen still useful while private. |

- **31-hidden-overview.desk.en, blurred values keep their digit count ("99,999.99 €" vs "999.99 €")**: leaks orders of magnitude. `cosmetic`. Suggestion: use a fixed-width mask.
- **31-hidden-overview.desk.en, Sankey and sparkbars still shown**: relative shapes stay. This is a sensible choice for privacy-in-public use. `keep`.

## Screens without charts
05-transactions-edit, 06-transactions-empty, 20–27 settings, 30-settings-connect-dialog, 40–42 wizard/login: no data graphics to judge. One data note: **21-settings-categories.desk.en "94 % of the last 60 days categorized without help"** is shown as plain text. A small progress bar would make it scannable alongside "39 need review", but text is acceptable. `cosmetic`. Scores: "-".

---

## Top 10

1. **13-recurring-orbit.desk.en / phone.de, the whole Orbit chart.** A 3D-tilted "solar system" with unlabeled glossy spheres, size encoding with no scale, and angle encoding with no day ticks. Values cannot be read. On phone the spheres overlap the total. Replace it with a flat "next 30 days" timeline with labelled amounts, or remove the tab (List and Calendar already cover it). `slows a task`.
2. **15-investments.desk.en, "Value without deposits" line.** It ends at the real value but starts at a fictional ~8.85k, so readers misjudge where the depot started. Use the standard pair "depot value" + "money paid in" (cumulative step) with the gap shaded as gain. `slows a task`.
3. **Return numbers disagree with no stated basis.** 15-investments.desk.en "Vanguard +7.5 %", 19-etf.desk.en "+17.2 %" and "Price +11.2 %". Also 16-inv-forecast "Swing 15 %" vs 17-inv-analysis "±17 %". 17-inv-analysis monthly returns (Feb +8.2 %) do not match 15-investments € bars (Feb +497 € ≈ 5.8 %). Label every % with its period and basis, and reconcile or explain. `slows a task`.
4. **12-recurring-calendar.desk.en "2,523.48 € fixed costs this month" vs 11-recurring-list.desk.en "1,407.01 € per month".** These are the same words with two numbers (the calendar includes 1,100 € of savings plans). Split the header into fixed costs + savings plans. `slows a task`.
5. **16-inv-forecast.desk.en, the outcome band's lower edge is invisible** (it merges with the filled "paid in" area), so the forecast's spread, its core message, is lost. Draw the band between two visible lines and make "paid in" a dashed line. `slows a task`.
6. **07-spending.phone.de heatmap and 17-inv-analysis.phone.de monthly-returns row are cut off** (after June) with no scroll cue, which hides the most recent four months on phone. Wrap them into rows, or start scrolled to today. `slows a task`.
7. **14-networth.desk.en, area fill on a 25k € baseline.** This exaggerates growth about threefold. Drop the fill or start at 0. Better: a stacked area by account, which shows where the growth came from. `slows a task`.
8. **07-spending.desk.en "Your year in days" heatmap.** The multi-hue violet→magenta→orange→yellow ramp is not ordered, and the legend has no € bins. Weekend rows are empty because of booking dates, which inflates "185 days without spending". Use a single-hue ramp with € thresholds and the transaction date, or caption it. `slows a task`.
9. **11-recurring-list.desk.en "Running" sorted by raw amount across monthly, quarterly and yearly rhythms** (Lime 129 €/yr above Netflix 15.99 €/mo). Sort by monthly equivalent and make that figure primary. `slows a task`.
10. **Decoration that repeats or replaces data.** 01-overview.desk.en has an unlabeled tank gauge and a "39 %" ring that repeats the text. 07-spending.desk.en has a two-ring sunburst that duplicates the bar list (outer ring unlabeled). 14-networth.desk.en has 12 identical coins per savings plan. 17-inv-analysis.desk.en has full-width return bars with no scale. Remove these, or turn each into a labelled bullet bar or plain text. `cosmetic`, but this is the single biggest lever on visual credibility.

Keep (the strongest data presentation in the app): the ranked bar list on 07-spending, the monthly bars with average line on 09-drill-group, the price chart with purchase dots and average-cost line on 19-etf, the drawdown chart on 17-inv-analysis, the diverging monthly gain/loss bars on 15-investments, the bad/good-case slider with "1 in 12 futures ends below what you paid in" on 16-inv-forecast, and the labelled Sankey outflows on 01-overview.
