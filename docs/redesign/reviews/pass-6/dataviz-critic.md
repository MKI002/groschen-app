# Groschen: data visualisation critique

Role: data visualisation critic. I score only the lines I can judge from the charts: 1 clarity of purpose, 2 hierarchy (within charts), 4 data presentation, 6 consistency (of encodings and numbers between charts), 7 phone experience (charts on phone), 9 visual craft (of charts). Lines 3, 5 and 8 are "-". Every score names the element it rests on.

Overall: the charting is better than most self-hosted finance tools. The plain forms (the merchant/category bar lists, the monthly bar charts with an average line, the drawdown chart, the monthly-returns grid, the ETF price chart with purchase dots and average-cost line, the payday breakdown dialog) are clear and should stay. The weak points are (a) ornamental forms that look good but answer their question badly (the Orbit, the jar, the calm/wild gauge, the coin strips), (b) area fills under charts whose y-axis does not start at zero, and (c) the same idea shown with different numbers on different screens with no explanation (fixed costs 1,407 vs 1,423; volatility 15 % vs ±17 %; ETF +7.5 % vs +17.2 %; Housing 35.6 % vs 58.3 %; income 33.5k vs 42.1k).

---

## 01-overview (desk.en, desk.de, phone.en, phone.de) and 31-hidden-overview

| Line | Score | Based on |
|---|---|---|
| 1 clarity | 7 | `01-overview.desk.en`: the "Available until payday" figure is clear; the jar beside it has no label, so its question is unclear |
| 2 hierarchy | 8 | `01-overview.desk.en`: 5,170.65 € hero, then three KPI cards, then the Sankey; the order is right |
| 3 | - | |
| 4 data presentation | 6 | `01-overview.desk.en`: Sankey labels carry value and %, good; jar, payday strip and KPI mini bars cannot be read |
| 5 | - | |
| 6 consistency | 5 | `01-overview.desk.en` Sankey "Housing 35.6 %" vs `07-spending.desk.en` "Housing 58.3 %": the same category has two percentages on different bases, and neither says what it is a percentage of |
| 7 phone | 8 | `01-overview.phone.de`: the Sankey drops to one stage (Einnahmen → targets) and still fits with labels; good adaptation |
| 8 | - | |
| 9 craft | 7 | `01-overview.desk.en`: tidy Sankey; jar glow and gradient are ornament |

Findings

- **Jar graphic in the hero card** (`01-overview.desk.en`, `31-hidden-overview.desk.en`). It is about two-thirds full, which matches 5,170.65 / 7,768.05 (the free share of the balance). Nothing on the card says so, and its tick marks have no values. It repeats the number beside it at lower precision. *slows a task.* Remove it, or replace it with one labelled horizontal bar: "Balance 7,768 € = free 5,171 € + still going out 2,597 €". That is exactly the sum in `34-payday-details`. Note that the phone layout (`01-overview.phone.de`) already drops the jar and loses nothing.
- **Payday day strip** (`01-overview.desk.en`, "TODAY · 28 days to payday"). It answers "when do payments hit before payday", but every payment dot is the same size, so the 1,050 € rent looks like the 2.99 € Apple charge. Days 1–2 hold four payments (2,150 €), and they are hidden as tiny dots. *slows a task.* Better form: a projected-balance step line from today to 27 Nov (start at 7,768 €, step down on each due date, end at 5,171 €), or dots sized by amount, with the largest labelled.
- **Income and spending mini bars** (`01-overview.desk.en` KPI cards). These are ten unlabelled monthly bars with no axis or month names, and the last one is highlighted. As a trend cue they are fine, but the highlighted last bar (October) is not explained. Add a hover value and month, or a short "Oct" label under the highlighted bar. *cosmetic.*
- **Saved card** (`01-overview.desk.en`). The three-part stacked bar (invested / put aside / stays) with the values listed under it is a good form. *keep.* The 39 % ring next to it is a second encoding of a ratio that could simply be text. *cosmetic*: acceptable, but it is ornament.
- **Sankey "Where the money went"** (`01-overview.desk.en`). The value + % labels on every node are good. *keep.* Weaknesses:
  - The left stage (Salary 99.6 % → Income) is almost a single band and spends about 360 px saying "nearly all income is salary". *cosmetic.* Collapse the left stage into the node label, as the phone does.
  - The nine smaller spending categories squeeze into the bottom 25 % of the chart, where 0.5 px bands are not traceable. A sorted bar list with the three savings destinations above a separator would answer "where did it go" more precisely. The Spending page already has that list.
  - The percentages here are % of income. On Spending they are % of spending. *slows a task*: write "of income" in the subtitle.
- **Hidden mode** (`31-hidden-overview.desk.en`). Amounts blur, but the shares (8.9 %, 35.6 %), the 39 % savings rate and the chart shapes stay. That is a sensible privacy line, because shape without scale exposes no amounts. *keep.*

## 02 / 03 / 04 / 05 / 06-transactions (all variants)

| Line | Score | Based on |
|---|---|---|
| 1 | 8 | `02-transactions.desk.en`: day-grouped list with a day total on the right |
| 4 | 7 | `02-transactions.desk.en`: "297 transactions · 42,057.91 € in · 31,970.76 € out" summary line is useful but conflicts with the Overview |
| 6 | 5 | `02-transactions.desk.en` "42,057.91 € in" vs `01-overview.desk.en` Income "33,538.60 €" for the same Jan–Oct 2026 period |
| 2,3,5,7,8,9 | - | |

Findings

- **Summary totals do not match the Overview** (`02-transactions.desk.en`). In vs Income differs by about 8.5k, and Out vs Spending by about 11.5k, presumably because transfers and savings are included. *slows a task.* Label it "incl. transfers", or show the same definition as the Overview.
- **Review summary line** (`03-transactions-review.desk.en`). "8 transactions · 110,315.81 € in · 84,234.46 € out" cannot belong to 8 rows. This may be a demo artefact (see the capture notes), but if the real app does this the totals mislead. *slows a task.*
- **Inline repayment progress bar** (`03-transactions-review.desk.en`, Lena Berger "32.00 € of 64.00 € back"). It is a small, precise, labelled bar at the point of need. *keep.*
- **Day totals right-aligned in the date header** (`02-transactions.desk.en`, "-177.49 €"). *keep.*

## 07-spending (all variants), 33-period-menu, 08-spending-group-dialog

| Line | Score | Based on |
|---|---|---|
| 1 | 7 | `07-spending.desk.en`: "Spending breakdown" plus "Your year in days" each state their question |
| 2 | 7 | `07-spending.desk.en`: the two-ring donut takes as much weight as the precise bar list beside it |
| 4 | 6 | `07-spending.desk.en`: the bar list is precise; the donut outer ring is unlabelled; the heatmap legend has no thresholds |
| 6 | 7 | `07-spending.desk.en` bar colours match the Sankey colours on `01-overview.desk.en` (Housing blue, Food yellow, Transport pink) |
| 7 | 8 | `07-spending.phone.de`: the heatmap wraps into two half-years and stays readable |
| 9 | 7 | `07-spending.desk.en`: clean bars; the donut's 20+ thin outer slices are noisy |
| 3,5,8 | - | |

Findings

- **Two-ring donut (sunburst)** (`07-spending.desk.en`, `07-spending.phone.de`). The outer ring (categories within groups) has about 20 slivers with no labels and lighter shades of the same hue, so it cannot be read without hovering. The bar list to its right already gives the group shares exactly. *slows a task.* Drop the outer ring, or drop the donut and let the bar list take the full width. When "Categories" is toggled, show a grouped bar list (group header + indented category bars).
- **Category bar list** (`07-spending.desk.en`). It is sorted, carries € and %, and has a drill chevron. *keep.* Note that the bars are scaled to the largest row (Housing 58.3 % = full width) while the % column is the share of the total. That is legitimate but should stay consistent everywhere. It is consistent across Spending and the drill pages.
- **"Personal · more refunds than spending −162.37 €"** row (`07-spending.desk.en`) has an empty bar. A negative value in a share list is handled honestly with text. *keep.*
- **"Your year in days" heatmap** (`07-spending.desk.en`). The calendar heatmap is a good form for spotting rhythm and outlier days, and the three summary figures under it (185 days without spending, priciest day, average day) make it actionable. *keep.* Weaknesses:
  - The "Less ■■■■■ More" legend gives no € thresholds, so a yellow day cannot be told apart from an orange one in money. *slows a task.* Put the bin edges on the legend (for example <25 / 25–75 / 75–150 / 150–400 / >400 €).
  - The violet → pink → orange → yellow ramp changes hue as well as lightness. Pink and violet sit close in lightness, so the middle bins are hard to order (and hard for colour-vision-deficient users). Use a single-hue or perceptually ordered ramp.
  - Only Mon/Wed/Fri rows are labelled.
- **Period menu** (`33-period-menu.desk.en`). The presets (This month … All time) are a clean list with the selection marked. *keep.* That the charts behind it follow one global period is good.

## 09-drill-group, 10-drill-category (all variants)

| Line | Score | Based on |
|---|---|---|
| 1 | 9 | `09-drill-group.desk.en`: "Food & Dining · Spent 3,480.29 € · Per month" chart plus the merchant and category lists answer "how much, when, where" |
| 2 | 8 | `09-drill-group.desk.en`: the headline sits left of the monthly bars and the lists follow |
| 4 | 8 | `10-drill-category.desk.en`: monthly bars on a zero baseline with gridlines and a dashed "Average 255 €" line |
| 6 | 8 | `09-drill-group.desk.en` and `10-drill-category.desk.en`: identical layout at both drill levels |
| 7 | 7 | `09-drill-group.phone.de`: the bar chart keeps its average line; x labels every second month |
| 9 | 8 | `09-drill-group.desk.en`: restrained single-hue bars |
| 3,5,8 | - | |

Findings

- **Monthly bar chart with average line** (`09-drill-group.desk.en`, `10-drill-category.desk.en`). This is the right form, on an honest zero baseline. *keep.* The "Average 348 €" label sits on top of the Sept/Oct bars (`09-drill-group.desk.en`). *cosmetic*: move it to the left end of the line or into the margin.
- **Zero rows in Categories** (`09-drill-group.desk.en`: "Food & Dining · 0× 0.00 €", "Food delivery · 0× 0.00 €"). These are empty bars that add noise, and the same zero chips appear in the filter row. *cosmetic.* Hide 0× rows or fold them into "2 unused".
- **"↑ 35 % vs. the period before"** (`09-drill-group.desk.en`). The comparison period is not named (Mar–Dec 2025?). *slows a task*: name it.
- **The Months/Weekdays toggle** is a good secondary question on the same chart. *keep.*

## 11-recurring-list (all variants)

| Line | Score | Based on |
|---|---|---|
| 1 | 8 | `11-recurring-list.desk.en`: "Fixed costs per month 1,407.01 €" plus "Next up" |
| 4 | 6 | `11-recurring-list.desk.en` "Running" list: the bold amount is the native amount, but the sort order follows the monthly equivalent |
| 6 | 5 | `11-recurring-list.desk.en` "1,407.01 €" vs `12-recurring-calendar.desk.en` "1,423.48 € fixed costs" |
| 2,3,5,7,8,9 | - | |

Findings

- **Sort key versus displayed figure** (`11-recurring-list.desk.en`). Rundfunkbeitrag 55.08 € appears below FitX 24.99 €, and Lime 129.00 € below Spotify 11.99 €, because the list sorts by monthly equivalent while the bold figure is the per-payment amount. *slows a task.* Make "≈ x € a month" the bold right-aligned column and the payment amount the secondary text, or sort by what is bold. A thin bar per row scaled to monthly cost would show at a glance that rent is 75 % of fixed costs.
- **Price-change chips** ("+7.00 €", "+2.00 €") and the "What changed" log are an excellent use of data. *keep.*

## 12-recurring-calendar (all variants)

| Line | Score | Based on |
|---|---|---|
| 1 | 7 | `12-recurring-calendar.desk.en`: a month calendar with the "Day by day" list |
| 4 | 5 | `12-recurring-calendar.desk.en`: truncated chips "Ha… −1,050 €", "Spar… −800 €", "+1"; `12-recurring-calendar.phone.de`: day 1 shows "−2.150 €", mixing rent with savings |
| 6 | 5 | `12-recurring-calendar.desk.en` header 1,423.48 € vs list 1,407.01 €; legend mixes status (Paid/Expected) with type (Standing order/Salary) |
| 7 | 7 | `12-recurring-calendar.phone.de`: the dot + day-sum cell is a sensible compression |
| 9 | 6 | `12-recurring-calendar.desk.en`: the bottom 600 px of the left column is empty |
| 2,3,5,8 | - | |

Findings

- **The legend mixes two dimensions** (`12-recurring-calendar.desk.en`, "Paid · Expected · Standing order · Salary"). Orange means paid, but teal means standing order, and a standing order is also paid. On phone, teal standing order and green salary are close in hue. *slows a task.* Encode type by colour and status by fill (solid = paid, outline = expected) and say so.
- **Day sums mix costs and savings** (`12-recurring-calendar.phone.de`, day 1 "−2.150 €"; desk header "1,423.48 € fixed costs · 1,100.00 € saved"). On the phone the cell sum adds savings transfers to rent. *slows a task*: sum costs only, or show two numbers.
- **Two different "fixed costs" totals** (1,407.01 € on the List, 1,423.48 € on the Calendar). The first is likely a monthly average and the second the October actual, but neither says which. *slows a task.* Label them "monthly average" vs "paid in October".
- **Full-width orange progress bar** (`12-recurring-calendar.desk.en`). It shows 100 % paid, but it is unlabelled and looks like a decorative rule. *cosmetic.*

## 13-recurring-orbit (all variants)

| Line | Score | Based on |
|---|---|---|
| 1 | 3 | `13-recurring-orbit.desk.en` "Your month in orbit": the question (what is due when, and how big) is answered worse than by the List or Calendar |
| 2 | 4 | `13-recurring-orbit.desk.en`: the central "1,407 €" glow dominates; only 4 of 13 dots are labelled |
| 4 | 2 | `13-recurring-orbit.desk.en`: dot size competes with perspective scaling; the two overlapping blue dots by "Hausverwaltung Kr…" cannot be separated; dot colours are unexplained |
| 6 | 4 | `13-recurring-orbit.desk.en`: dot colours (blue, teal, pink, green) match neither the calendar legend nor the category colours |
| 7 | 2 | `13-recurring-orbit.phone.de`: the whole system collapses into a 150 px knot; the labels "HUK-Coburg", "Telekom" and "Hausverwaltung Kr…" overlap the total |
| 9 | 5 | `13-recurring-orbit.desk.en`: polished render, but stars, glow and 3D-shaded spheres are pure ornament |
| 3,5,8 | - | |

Findings

- **The Orbit view as a whole** (`13-recurring-orbit.desk.en`, `13-recurring-orbit.phone.de`). Area-encoded spheres on tilted ellipses are among the least precise encodings possible. Perspective makes front dots bigger regardless of cost, the "due" marker is only meaningful once you learn the metaphor, and amounts and dates cannot be read at all. *slows a task* (on phone it is close to *blocks a task*: you cannot pick a dot). Better forms: a **month timeline strip** (x = day 1–31, one row per rhythm, circle area or bar height = amount, labels on the largest items), or a **"what's due in the next 30 days" bar list**. If Orbit stays as a showpiece, make List the default and give Orbit hover/tap labels for every dot, plus a size legend ("● = 50 € ●● = 500 €").
- The ring legend under the chart (`every 4 weeks · 1`, `monthly · 9`, …) is good, cheap context. *keep.*

## 14-networth (all variants)

| Line | Score | Based on |
|---|---|---|
| 1 | 8 | `14-networth.desk.en`: "Today 44,931.92 €, ↑ 13,592.05 € Jan–Oct" and the line chart |
| 2 | 8 | `14-networth.desk.en`: total, then accounts, then savings plans |
| 4 | 5 | `14-networth.desk.en`: the area fill is drawn down to a 25k € axis floor, which overstates growth by about 2.5×; the total line cannot show which account drove the growth |
| 6 | 6 | `14-networth.desk.en` account share bars (17 % / 62 % / 21 %) use the same gold as the line, while the savings-plan coins use gold as well |
| 7 | 7 | `14-networth.phone.de`: the chart is legible and the axis labels are kept |
| 9 | 7 | `14-networth.desk.en`: clean line and markers; the coin rows are ornament |
| 3,5,8 | - | |

Findings

- **Truncated axis with area fill** (`14-networth.desk.en`, `14-networth.phone.de`). The y-axis starts at 25k €. A filled area implies a quantity measured from zero, so the fill makes a +45 % rise look like a ~10× rise. *slows a task* (it misleads). Either start at 0 (the rise is still clearly visible) or keep the zoomed axis and remove the area fill.
- **Missing composition** (`14-networth.desk.en`). The question after "how much" is "from where". A stacked area by account (Girokonto / Extra-Konto / Depot), or a toggle for it, would answer that directly. The account cards below carry only today's share.
- **Account cards with share bars** (`14-networth.desk.en`, "17 % / 62 % / 21 %"). These are simple and readable. *keep.* A single 100 % stacked bar across the three cards would show the split in one glance.
- **Savings-plan coin strips** (`14-networth.desk.en`, 12 gold coins per plan, labels Nov/Feb/May/Aug). Twelve identical coins only say "it ran every month". They carry no information unless a month is missed, and the month labels under 12 coins are sparse. *cosmetic.* Use hollow coins for missed months (if there are none, a single "12/12 months" text says the same), or replace the strip with a cumulative-paid sparkline.

## 15-investments (all variants), 32-hidden-investments

| Line | Score | Based on |
|---|---|---|
| 1 | 6 | `15-investments.desk.en`: the legend "Value without deposits" is unclear; the headline is 9,350.57 € but the line is a deposit-adjusted series with the same end point |
| 2 | 7 | `15-investments.desk.en`: value line on top, monthly gain/loss bars below, holdings after |
| 4 | 7 | `15-investments.desk.en`: the gain/loss bars each carry a € label and sum to +504.90 €, matching the headline; good |
| 6 | 5 | `15-investments.desk.en` holding "Vanguard +7.5 % · 474 €" vs `19-etf.desk.en` "+1,160.97 € · +17.2 %" for the same fund, with no period stated on the card |
| 7 | 7 | `15-investments.phone.de`: the bars keep only the extreme labels (+564 € / −429 €), so the rest must be estimated |
| 9 | 7 | `15-investments.desk.en`: tidy; the area fill again sits over a truncated 8k axis |
| 3,5,8 | - | |

Findings

- **"Value without deposits" line** (`15-investments.desk.en`). Most users will not know what this series is. It is apparently the market-only performance on the current value. *slows a task.* Rename it to something like "Value if you had paid nothing in since Jan", or plot value and paid-in as two lines (the "Money paid in" toggle exists, so make it on by default) so the gap is the gain.
- **Truncated axis with area fill** (`15-investments.desk.en`, 8k–10k axis). Same issue as on Net worth: drop the fill or start at 0.
- **Monthly gain/loss bars** (`15-investments.desk.en`). Diverging colour, a label on every bar, and an exact sum to the headline. This is the best chart in the app. *keep.*
- **Allocation bar + per-holding share bars** (`15-investments.desk.en`, 85 % / 15 %). The same split is drawn twice. *cosmetic*: keep the top stacked bar and drop the per-card bars, or the reverse.
- **Holding sparklines** (`15-investments.desk.en`). These have no axis or period, and their shape does not visibly match "+7.5 %". *cosmetic*: add the period.
- **Tax-free allowance bar** (`15-investments.desk.en`, "95.40 € of 1,000.00 €"). A precise, labelled progress bar. *keep.*
- **Hidden mode** (`32-hidden-investments.desk.en`). Axis labels are blurred and shapes and percentages stay. Consistent with the Overview. *keep.*

## 16-inv-forecast (all variants)

| Line | Score | Based on |
|---|---|---|
| 1 | 8 | `16-inv-forecast.desk.en` "Where it could go · 800 simulated futures, assumptions not a promise" |
| 2 | 8 | `16-inv-forecast.desk.en`: assumptions, then "In 10 years 68,412 €", then the bad/good range, then the chart |
| 4 | 6 | `16-inv-forecast.desk.en`: the lower edge of the "8 of 10 outcomes" band disappears into the grey "Paid in" area, so the downside is not visible |
| 6 | 5 | `16-inv-forecast.desk.en` "Swing 15 % a year" vs `17-inv-analysis.desk.en` "±17 % up or down in a normal year" |
| 7 | 7 | `16-inv-forecast.phone.de`: the chart is kept but small; the milestone chips work well |
| 9 | 7 | `16-inv-forecast.desk.en`: the milestone markers (10k/25k/50k) on the median line are nicely done |
| 3,5,8 | - | |

Findings

- **The fan chart hides its downside** (`16-inv-forecast.desk.en`). The band's lower bound overlaps the dark "paid in" fill and cannot be seen. Together with "1 in 12 futures ends below what you paid in", the risk the user most needs to see is the one that is invisible. *slows a task.* Draw paid-in as a line only (no fill), and give the band a distinct fill with both edges visible. Consider a second, lighter band for the 5–95 % range.
- **Bad/middle/good range bar** (`16-inv-forecast.desk.en`, 46,246 € / 68,412 € / 102,388 €, with the "paid in" tick). This is a compact and honest summary of the distribution. *keep.*
- **Volatility figure differs between screens** (15 % here vs ±17 % on Analysis). *slows a task.* Use one number, or state the different windows.

## 17-inv-analysis (all variants)

| Line | Score | Based on |
|---|---|---|
| 1 | 7 | `17-inv-analysis.desk.en`: the "Return in this period", "Ups and downs", "Drawdown" and "Monthly returns" titles state their question |
| 2 | 7 | `17-inv-analysis.desk.en`: the drawdown chart rightly gets the width |
| 4 | 6 | `17-inv-analysis.desk.en`: the drawdown and monthly grid are good; the return bars and the calm/wild gauge are not readable |
| 6 | 6 | `17-inv-analysis.desk.en`: drawdown sampled monthly (11 points), while `15-investments.desk.en` plots daily values |
| 7 | 8 | `17-inv-analysis.phone.de`: the monthly grid reflows to 6×2 cleanly |
| 9 | 7 | `17-inv-analysis.desk.en`: the diverging red/green grid is calm and well spaced |
| 3,5,8 | - | |

Findings

- **Return bars** (`17-inv-analysis.desk.en`, "+6.7 %" full width, "+6.3 %" ~93 %). Bars scaled to the larger of two numbers exaggerate a 0.4-point difference and have no scale. *cosmetic.* Show the two numbers side by side with the difference ("+0.4 pts from your timing"). That is the actual insight.
- **"Ups and downs" gauge** (`17-inv-analysis.desk.en`, gradient bar from "calm" to "wild" with a knob). It has no scale values, and the "usual for stock ETFs" bracket has no numbers, so it is a decorative restatement of ±17 %. *cosmetic.* Use a labelled number line (0 % … 30 %) with markers for "bonds ~5 %", "world ETF ~15 %" and "single stocks ~30 %".
- **Drawdown chart** (`17-inv-analysis.desk.en`). This is the right form, with the trough annotated "−12.7 % (Jun 26)" and a current badge "0.9 % below its high". *keep.* Use the same daily data as the Investments chart so the trough matches what the user sees there.
- **Monthly returns grid** (`17-inv-analysis.desk.en`). Labelled cells, diverging colour, best and worst outlined, and "5 of 10 months up". *keep.* The legend "Outlined: the best and the worst month" is drawn with a **checkbox** (`17-inv-analysis.desk.en`, `17-inv-analysis.phone.de`), which reads as a control. *cosmetic*: use an outlined swatch.

## 18-inv-payments (all variants)

| Line | Score | Based on |
|---|---|---|
| 1 | 7 | `18-inv-payments.desk.en` "Money put in · 3,600.00 € in the last 12 months" |
| 4 | 6 | `18-inv-payments.desk.en`: the month accordion lists six identical "300.00 €" rows; a gap or change would not stand out |
| 2,3,5,6,7,8,9 | - | |

Findings

- **No chart for pay-ins over time** (`18-inv-payments.desk.en`). For 27 months of pay-ins, a small monthly column chart (stacked by ETF) above the accordion would show plan changes and gaps at a glance. *cosmetic.*

## 19-etf (all variants)

| Line | Score | Based on |
|---|---|---|
| 1 | 8 | `19-etf.desk.en`: "Your value 7,910.97 €" and the price chart with purchases |
| 4 | 8 | `19-etf.desk.en`: purchase dots on the price line plus the dashed "Your average 110.71 €" line show at once whether you bought well |
| 6 | 5 | `19-etf.desk.en` "+17.2 %" vs `15-investments.desk.en` "+7.5 %" for the same fund |
| 9 | 7 | `19-etf.desk.en`: clean; the area fill under a 100–140 axis is again implicitly truncated |
| 2,3,5,7,8 | - | |

Findings

- **Price chart with purchase dots and average-cost line** (`19-etf.desk.en`). This is excellent and should stay. *keep.* The key "Dots are your purchases" sits below the card in grey footnote text. *cosmetic*: put it in the chart legend.
- **"+17.2 %" (since first purchase) vs "+7.5 %" (period) on the Investments card**. *slows a task.* Put the period next to every return figure.

## 34-payday-details (all variants)

| Line | Score | Based on |
|---|---|---|
| 1 | 9 | `34-payday-details.desk.en`: "Balance now 7,768.05 − Still going out 2,597.40 = Free to spend 5,170.65" |
| 4 | 9 | `34-payday-details.desk.en`: the visible arithmetic, then each payment with its due date and amount |
| 2,3,5,6,7,8,9 | - | |

Findings

- **The explicit subtraction** (`34-payday-details.desk.en`, `34-payday-details.phone.de`). It makes the hero number trustworthy. *keep.* It is also the best evidence that the jar and day strip on the Overview add nothing this dialog does not say better.

## Screens without charts (20–27, 30, 40–42, 05, 06, 08)

These screens contain no charts or graphics with data, so I do not score them. One note on `23-settings-depot.desk.en`: "Interest rate to compare with … Used for the Sharpe ratio". No screen I saw shows a Sharpe ratio (`17-inv-analysis.desk.en` has none), so the setting points to a number the user cannot find. *cosmetic.*

---

## Top 10

1. **Orbit view of fixed costs is the wrong form** (`13-recurring-orbit.desk.en`, `13-recurring-orbit.phone.de`): sphere area plus perspective cannot be read, most dots are unlabelled, dot colours are unexplained, and on phone it collapses into an unusable knot. Replace it with a month timeline strip (x = day, size = amount, largest labelled) or a "due next 30 days" bar list. Severity: slows a task (phone: nearly blocks).
2. **Area fills over truncated y-axes** (`14-networth.desk.en` 25k floor, `15-investments.desk.en` 8k floor, `19-etf.desk.en` 100 floor): the fill implies a zero baseline and overstates the change. Remove the fill or start at 0. Severity: slows a task (misleads).
3. **Forecast fan chart hides its downside** (`16-inv-forecast.desk.en`): the lower edge of the "8 of 10 outcomes" band disappears into the grey paid-in fill. Draw paid-in as a line and show both band edges. Severity: slows a task.
4. **The same idea with different numbers, unexplained**: fixed costs 1,407.01 vs 1,423.48 € (`11` vs `12-recurring-*.desk.en`), volatility 15 % vs ±17 % (`16` vs `17-inv-*.desk.en`), Vanguard +7.5 % vs +17.2 % (`15` vs `19`), income 33,538.60 vs 42,057.91 € (`01` vs `02`). Name the period or definition beside each figure. Severity: slows a task.
5. **Percentages without a base**: Housing is 35.6 % on the Overview Sankey (of income) and 58.3 % on Spending (of spending) (`01-overview.desk.en`, `07-spending.desk.en`). Add "of income" / "of spending". Severity: slows a task.
6. **Jar and payday strip in the Overview hero say less than the dialog** (`01-overview.desk.en`): the jar is unlabelled, and the strip shows 1,050 € rent the same size as 2.99 €. Replace them with a labelled balance → free stacked bar or a projected-balance step line to payday. Severity: slows a task.
7. **Two-ring donut on Spending** (`07-spending.desk.en`): the outer ring has about 20 unlabelled slivers and duplicates the precise bar list. Drop the outer ring or the donut and use a grouped bar list. Severity: slows a task.
8. **"Value without deposits" line on Investments is unclear** (`15-investments.desk.en`): show value and paid-in as two lines by default, so the gap is the gain, or rename the series plainly. Severity: slows a task.
9. **Calendar encodings mixed** (`12-recurring-calendar.desk.en` and `.phone.de`): the legend mixes status and type, the day-1 sum adds savings to rent ("−2.150 €"), and teal and green are nearly the same. Use colour for type and fill for status, and sum costs only. Severity: slows a task.
10. **Keep the strong charts as they are**: the monthly gain/loss bars that sum to the headline (`15-investments.desk.en`), the ETF price chart with purchase dots and average line (`19-etf.desk.en`), the drawdown chart and monthly-returns grid (`17-inv-analysis.desk.en`), the drill-down monthly bars with an average line (`09/10-drill-*.desk.en`), the sorted category/merchant bar lists, and the payday arithmetic dialog (`34-payday-details.desk.en`). Small fixes: € thresholds on the heatmap legend (`07-spending.desk.en`), an outlined swatch in place of the checkbox legend (`17-inv-analysis.desk.en`), and moving the "Average 348 €" label off the bars (`09-drill-group.desk.en`). Severity: keep / cosmetic.
