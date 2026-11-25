# Groschen, pass 8: Data visualisation critic

Role: data visualisation critic. I score only the lines a dataviz reviewer can judge: 1 clarity of purpose, 2 hierarchy, 4 data presentation, 6 consistency, 7 phone experience (charts only), 8 accessibility (colour and legibility of charts only), 9 visual craft (charts only). Lines 3 (task efficiency) and 5 (navigation and naming) are "-" throughout. Every score names the element it rests on.

Short verdict: the core charts are good. They include the monthly bar chart with an average line on the drill pages, the ETF price chart with purchase dots and an average-cost line, the forecast fan chart, the monthly-returns heatmap and the payday breakdown. These charts are labelled, reconcile with one another (I checked the sums) and adapt well on phones. Where the app has problems, it is because a chart was chosen for its look rather than its job. The orbit, the jar, the coin rows, the payday day-strip dots and the area fills on axes that do not start at zero add mood but little information, and two of them distort. The bigger issues are about meaning rather than looks. Bars that look like percentage tracks are actually scaled to the largest row. The same number is shown with different percentage bases on different screens. Volatility is given as 15 % on one screen and 17 % on another. The in/out totals on Transactions do not match Overview's income/spending for the same period.

---

## 01-overview (desk.en, desk.de, phone.en, phone.de)

### "Available until payday" hero
- **Hero number plus "That's about 184.67 € per day"** (`01-overview.desk.en`): this is the right question, answered first. 5,170.65 / 28 = 184.67, so the figure reconciles. **keep**
- **Jar graphic** (`01-overview.desk.en`, right side of the hero): the fill is about 2/3, which matches 5,170.65 / 7,768.05 balance = 66.6 %. Nothing on screen says that, though. The jar has three tick marks with no labels and no legend. It repeats the hero number as an unlabelled level, and its glossy, high-contrast shape draws more attention than the number does. Severity: cosmetic. Suggestion: either drop it (phone already does, `01-overview.phone.de`, and loses nothing), or turn it into a labelled horizontal bar: "balance 7,768 → still going out 2,597 → free 5,171".
- **Day strip to payday** (`01-overview.desk.en`, row of 28 pills plus coin): it answers "when do payments hit before payday?", which is a good question. Elapsed days are filled and the today marker is clear. The payment dots do not encode amount, however. Nov 1 carries 2,150 € in `34-payday-details.desk.en` (rent, savings and two ETF plans), but its dot is only slightly larger than the 2.99 € Apple dot. The 2,597 € total sits only in the link text. Severity: slows a task. Suggestion: draw a stepped "remaining money" line, or size and label each dot by amount, or put small euro labels on the 3–4 largest days. The coin at the end is ornament.
- **Payday details dialog** (`34-payday-details.desk.en`): Balance − Still going out = Free to spend, followed by a dated list. This is the clearest piece of data on the overview. **keep** It should be the strip's tooltip and click target, and it is.

### Period KPI cards
- **Income and Spending mini bars** (`01-overview.desk.en`, the 10 bars to the right of each total): they have no month labels, no scale and no hover hint. The income bars are almost all the same height, so they say "stable" and nothing else. The spending bars do show the August spike, which matches the hint "August 2026 was 42 % above your average". The highlighted last bar is October, a month that is not yet complete (frozen on 30 Oct). Severity: cosmetic. Suggestion: add first and last month initials and an average tick. Mark the current month as partial with a hatched or outlined bar instead of the brightest colour, because brightest reads as "most important".
- **Saved card: stacked bar plus 39 % ring** (`01-overview.desk.en`): the segments 3,000 / 8,095 / 1,992 are drawn in correct proportion, and 13,087 / 33,538 = 39 %, so it reconciles. The ring and the stacked bar encode different things in the same card, and the ring's gold matches the "invested" segment, which suggests a link that does not exist. Severity: cosmetic. Suggestion: keep the ring and recolour it neutral, or replace it with the text "39 % of income".

### "Where the money went" Sankey
- (`01-overview.desk.en`, `01-overview.phone.de`) The question is "where did income go?". The labels carry amount plus % of income, and the ribbons add up: 20,451 spending + 13,087 saved = 33,538. Good. **keep** the labels.
- The left half of the desktop Sankey is almost all one wide Salary→Income rectangle (99.6 %). It uses about 40 % of the card width to say "almost all income is salary". Severity: cosmetic. Suggestion: drop the source column and show the sources as one line of text ("Salary 99.6 %, interest 0.3 %"), or put them in a tooltip. The phone version already does this, `01-overview.phone.de`, and reads better.
- **"Uncategorized" appears on both sides** (`01-overview.desk.en`: income source 43.20 €, outflow 510.60 €) with the same name and grey. Severity: slows a task (ambiguous click target). Suggestion: "Uncategorized income" / "Uncategorized spending".
- **Percent base differs from Spending** (`01-overview.desk.en` Housing "11,929.82 € (35.6 %)" vs `07-spending.desk.en` Housing "58.3 %"): it is the same number on two screens with two different bases (income vs spending), and neither base is stated. Severity: slows a task. Suggestion: suffix "of income" / "of spending", or show the base once in the card subtitle.
- The 9 outflow ribbons below Housing are thin and use many hues on a dark ground. They are legible because labels sit beside every node, so the colour is redundant, which is the right way round. **keep**

### Scores (01)
| # | Score | Based on |
|---|---|---|
| 1 | 8 | `01-overview.desk.en` "Available until payday" hero states its question plainly |
| 2 | 7 | `01-overview.desk.en` jar competes with the hero number |
| 3 | - | |
| 4 | 6 | `01-overview.desk.en` day-strip dots carry no amounts; mini bars have no axis |
| 5 | - | |
| 6 | 6 | `01-overview.desk.en` Sankey % of income vs `07-spending` % of spending for the same Housing figure |
| 7 | 8 | `01-overview.phone.de` drops the jar and collapses the Sankey to one source column |
| 8 | 7 | `01-overview.desk.en` Sankey nodes are labelled, so colour is not the only carrier |
| 9 | 7 | `01-overview.desk.en` coin and jar glow are ornament; the Sankey is clean |

---

## 02 / 04 transactions, 03 review, 05 edit, 06 empty

- **Summary line "42,057.91 € in / 31,970.76 € out"** (`02-transactions.desk.en`) vs Overview "Income 33,538.60 € / Spending 20,451.45 €" for the same Jan–Oct period (`01-overview.desk.en`). The gap is internal transfers. The `02-transactions.phone.de` list shows "Alex Beispiel Sparen +800,00 €" and "−800,00 €", which inflate both in and out. Two headline totals for one period that do not agree undermine trust. Severity: slows a task. Suggestion: exclude own transfers from in/out (the "That's you" setting already identifies them), or label the line "incl. transfers between own accounts".
- **Day subtotals at the right of each date header** (`02-transactions.desk.en`, e.g. "Wednesday 28 October −177.49 €"): good, cheap aggregation. **keep**
- **Category pills with group-coloured dots** (`02-transactions.desk.en`): colour equals group, matching the Spending chart. Consistent. **keep**
- **Inline repayment bar "32.00 € of 64.00 € back"** (`03-transactions-review.desk.en`, Lena Berger row): a tiny, well-placed progress bar with the numbers next to it. **keep**
- **Count mismatch** (`03-transactions-review.desk.en`): the badge and tab say "Needs review 39", but the summary says "8 transactions". If the 39 are "auto-sorted, please confirm" and the 8 are "uncategorized", the screen has to say so. Severity: slows a task.
- `05-transactions-edit` and `06-transactions-empty` contain no charts. The edit dialog's group-coloured category chips are consistent with the Spending palette. **keep**

| # | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| 02/04 | - | - | - | 7 (`02-transactions.desk.en` day subtotals) | - | 5 (`02-transactions.desk.en` in/out ≠ Overview income/spending) | 7 (`02-transactions.phone.de` amounts right-aligned, pill under name) | - | - |
| 03 | - | - | - | 7 (`03-transactions-review.desk.en` inline repayment bar) | - | 5 (`03-transactions-review.desk.en` "39" badge vs "8 transactions") | - | - | - |

---

## 07-spending (desk.en, desk.de, phone.en, phone.de), 08 group dialog, 33 period menu

### Spending breakdown: sunburst plus ranked bar list
- **Sunburst donut** (`07-spending.desk.en`): the inner ring shows groups and the outer ring shows categories. It answers "how is spending split?", but the ranked list next to it answers the same question better: exact values, sorted, readable. The outer ring has about 20 slivers under 3 % that cannot be read or told apart, several in near-identical greys and greens. The donut is mostly decorative duplication. Severity: cosmetic. Suggestion: on desktop, drop the donut and let the bar list use the full width, with categories nested under each group as indented sub-bars. Or keep one ring (groups only) as a small glyph.
- **Bar list track semantics** (`07-spending.desk.en`): Housing 58.3 % fills the whole track, and Food 17.0 % fills about 29 % of it. The bars are scaled to the largest row, but a full-width rounded grey track reads as "100 %" next to a % number. Users will read Housing as "all of it". The same pattern appears in `09-drill-group.desk.en` Top merchants (Lidl 22.3 % = full bar) and Categories (Groceries 73.4 % = full bar), and in `10-drill-category.desk.en`. Severity: slows a task (misreading). Suggestion: either scale bars to the share (0–100 %), or remove the background track so the bars read as plain relative lengths.
- **Negative row "Personal −162.37 €"** (`07-spending.desk.en`): it shows an empty track. A negative value has no visual. Suggestion: a short bar going left from a zero line, or move it under the list as a "refunds" note.
- **Zero rows** (`09-drill-group.desk.en`: "Food & Dining · 0× 0.00 €", "Food delivery · 0× 0.00 €"): these are empty rows that take up as much space as real ones. Severity: cosmetic. Suggestion: hide 0 € rows, or collapse them into "2 categories without spending".

### "Your year in days" calendar heatmap
- (`07-spending.desk.en`) This is a good question ("what are my spending rhythms, and when were my spikes?"), and the three summary numbers underneath (185 days without spending, priciest day, average spending day) give the chart its meaning. **keep** the summary line.
- **Colour scale**: violet → magenta → pink → orange → yellow. It is sequential in lightness, but it passes through the hues already used for categories (violet = Leisure & Travel, pink = Transport, orange/gold = Food). On this page, beside the category donut, a pink cell can read as "transport day". The legend's 5 bins also have no values ("Less … More"). Severity: slows a task. Suggestion: use a single-hue sequential ramp that no category uses, and give the legend bin edges (e.g. "<20 €, 20–50, 50–100, 100–250, >250 €").
- **"Nothing" vs future days** (zoom of `07-spending.desk.en` Oct–Dec): no-spend days are filled dark grey, and future days are outlined dark. The two differ only slightly in contrast. Acceptable, but the "Nov" label sits over the week of 26–30 Oct, because that column contains Sun 1 Nov. That reads as if October's last week were November. Severity: cosmetic.
- **Sat/Sun rows almost entirely grey** (`07-spending.desk.en`): an odd pattern that comes from the data, not a chart fault. Worth checking in the demo data, though, because it makes the heatmap look broken.
- **Phone** (`07-spending.phone.de`): the year wraps into two half-year blocks, which is a good adaptation. The cells are about 8 px, so the "click a day" interaction is not realistic by touch. Suggestion: on phone, make the month the tap target.
- `08-spending-group-dialog` and `33-period-menu`: no charts. The period menu offers sensible presets. **keep**

| # | Score | Based on |
|---|---|---|
| 1 | 7 | `07-spending.desk.en` "Spending breakdown … most on Housing (58 %)" subtitle states the answer |
| 2 | 6 | `07-spending.desk.en` donut and bar list compete as equal-weight twins |
| 3 | - | |
| 4 | 5 | `07-spending.desk.en` bars scaled to max on a 100 %-looking track; heatmap legend bins have no values |
| 5 | - | |
| 6 | 5 | `07-spending.desk.en` heatmap hues collide with category hues on the same page |
| 7 | 7 | `07-spending.phone.de` heatmap split into two half-years; cells too small to tap |
| 8 | 5 | `07-spending.desk.en` outer-ring slivers distinguishable only by similar hues; magenta/pink/orange bins are close for deuteranopes |
| 9 | 7 | `07-spending.desk.en` sunburst is polished but crowded with slivers |

---

## 09-drill-group and 10-drill-category

- **Monthly bar chart with dashed average** (`09-drill-group.desk.en` "Per month", `10-drill-category.desk.en`): this is the right form, with a zero baseline, a labelled y-axis and an average line that has a value. The best chart in the app for its question. **keep**
- **Average label collides with bars** (`09-drill-group.desk.en` "Average 348 €" sits on top of the Sept/Oct bars; the same happens on `09-drill-group.phone.de` "Durchschnitt 348 €"). Severity: cosmetic. Suggestion: put the label left of the plot at the y-axis, or above the line in the gap.
- **October is a partial month** (frozen 30 Oct), drawn the same as complete months. That matters little here (one day left), but the same chart early in a month would show a misleading dip. Suggestion: hatch or outline the current month.
- **"↑ 35 % vs. the period before"** (`09-drill-group.desk.en`): the comparison period is not stated (Mar–Dec 2025? Jan–Oct 2025?). The visible bars trend downward, so a red "up 35 %" next to them confuses. Severity: slows a task. Suggestion: "vs Jan–Oct 2025", in a tooltip at minimum.
- **Top merchants / Categories bar lists**: see the track-scaling issue under 07. Same finding.
- **Phone** (`09-drill-group.phone.de`, `10-drill-category.phone.de`): the bar chart keeps its axis and shows every other month label. Good. **keep**

| # | Score | Based on |
|---|---|---|
| 1 | 8 | `09-drill-group.desk.en` Spent / Per month / Top merchants answer one question each |
| 2 | 8 | `10-drill-category.desk.en` total, then trend, then contributors, then rows |
| 3 | - | |
| 4 | 7 | `09-drill-group.desk.en` bar chart with average; "35 %" comparison base unstated |
| 5 | - | |
| 6 | 6 | `09-drill-group.desk.en` merchant bars scaled to max, unlike a % bar |
| 7 | 8 | `09-drill-group.phone.de` chart keeps axis, labels thinned sensibly |
| 8 | 7 | `10-drill-category.desk.en` single-hue bars with values |
| 9 | 7 | `09-drill-group.desk.en` average label overlaps Sept/Oct bars |

---

## 11-recurring-list, 12-recurring-calendar, 13-recurring-orbit

### List
- **"1,407.01 € fixed costs on average per month" plus "Next up" stack** (`11-recurring-list.desk.en`): this answers the question clearly. **keep**
- **Sort order is invisible** (`11-recurring-list.desk.en` Running list): the order is Hausverwaltung 1,050, Stadtwerke 81, DB 58, HUK 48.50, Telekom 39.95, DAZN 34.99, FitX 24.99, Rundfunk 55.08… The list is sorted by monthly equivalent (Rundfunk ≈ 18.36 €/month), but the bold number shown is the payment amount, so 55.08 after 24.99 looks unsorted. Severity: slows a task. Suggestion: make the monthly equivalent the primary right-hand number for every row and the payment amount secondary. Adding a thin bar of each row's share of 1,407 € would make this a real cost ranking.
- **Price-change chips "+7.00 €", "+2.00 €"** (`11-recurring-list.desk.en`): compact and useful. **keep**

### Calendar
- **Month grid with chips** (`12-recurring-calendar.desk.en`): the chips truncate names ("Ha…", "Nor…") and round amounts (−1,050 €, −16 €) while the side list shows cents. That is acceptable, because the "Day by day" list is the precise channel.
- **Today is 30 Oct, so the default month is entirely in the past**: the progress bar is 100 % "paid" and "0.00 € still to come". The view answers "what happened" when the user wants "what's coming". Severity: slows a task. Suggestion: default to a rolling "next 30 days" window, or open November when fewer than N days of the month remain. The full-width all-paid progress bar carries no information in this state.
- **Phone** (`12-recurring-calendar.phone.de`): chips become coloured dots plus a day total (−2.150 €, −123 €). This is a good compression. **keep**

### Orbit
- (`13-recurring-orbit.desk.en`, `13-recurring-orbit.phone.de`) The question is "when is each fixed cost due and how big is it?". The orbit encodes due date as angle on a tilted ellipse, cadence as ring, and amount as sphere area. All three are among the hardest encodings to read: angle on a foreshortened ellipse, area of a 3D-shaded ball, and rings in perspective. Only 5 of 13 items carry labels. Hausverwaltung's two spheres overlap. The legend lists rings as "every 4 weeks · 1, monthly · 9, quarterly · 1, yearly · 2", but the description says "monthly inside", so the ring-to-cadence mapping is unclear. On phone (`13-recurring-orbit.phone.de`) the whole thing collapses into a blob around the "1.407 €" label, and spheres cover the centre text. The starfield and the glow are pure decoration. Severity: slows a task (on phone, nearly unusable). Suggestion: replace it with a horizontal "next 12 months" timeline. Put one lane per cadence, ticks at due dates, tick height = amount, and labels on the top N. Or use a bar chart of annual cost grouped by cadence. If the orbit stays as a delight view, make sure it is never the default and hide it on phone.

| # | List | Calendar | Orbit |
|---|---|---|---|
| 1 | 8 (`11-recurring-list.desk.en` 1,407 € hero) | 6 (`12-recurring-calendar.desk.en` defaults to a fully past month) | 3 (`13-recurring-orbit.desk.en` encoding needs a paragraph of explanation) |
| 2 | 7 (`11-recurring-list.desk.en` Next up beside hero) | 7 (`12-recurring-calendar.desk.en` grid plus day list) | 4 (`13-recurring-orbit.desk.en` glow centre outshines data) |
| 3 | - | - | - |
| 4 | 6 (`11-recurring-list.desk.en` sort key ≠ displayed number) | 7 (`12-recurring-calendar.desk.en` day list exact) | 2 (`13-recurring-orbit.desk.en` angle/area on ellipse, 8 of 13 unlabelled) |
| 5 | - | - | - |
| 6 | 7 | 7 (`12-recurring-calendar.desk.en` legend colours = list dots) | 4 (`13-recurring-orbit.desk.en` ring legend vs "monthly inside" text) |
| 7 | 8 (`11-recurring-list.phone.de`) | 8 (`12-recurring-calendar.phone.de` dot plus day total) | 2 (`13-recurring-orbit.phone.de` collapses to a blob) |
| 8 | - | 6 (`12-recurring-calendar.desk.en` paid vs standing-order coral/teal) | 3 (`13-recurring-orbit.desk.en` "a month" label low-contrast on glow) |
| 9 | 7 | 7 | 5 (`13-recurring-orbit.desk.en` pretty but ornamental) |

---

## 14-networth

- **Net-worth line with area fill on a 25k baseline** (`14-networth.desk.en`, `14-networth.phone.de`): the y-axis starts at 25k € but the area is filled down to it, so the shaded area triples visually against a 44 % rise (31k → 45k). An area implies magnitude from zero. Severity: slows a task (overstates growth). Suggestion: either start at 0 and keep the fill, or keep the truncated axis and drop the fill.
- **No split between "saved" and "market growth"** in the +13,592 € (`14-networth.desk.en`). That is the next question a finance user asks. Suggestion: a stacked area by account (Girokonto / Extra-Konto / Depot) or a two-line "contributions vs value" chart. The account cards' share bars (17 / 62 / 21 %) are a good start, so **keep** them. They sum to 100 % and match the balances.
- **Savings-plan coin rows** (`14-networth.desk.en`, 12 identical gold coins per plan): 12 identical marks say "paid every month", and nothing more. Their only information would be a missed or changed month, and nothing marks that. The shiny 3D coins take more attention than the "6,750.00 € since August 2024" total. Severity: cosmetic. Suggestion: use flat dots with a hollow or red state for missed months, or the text "12 of 12 months paid".

| # | Score | Based on |
|---|---|---|
| 1 | 8 | `14-networth.desk.en` "Today 44,931.92 €" plus trend |
| 2 | 7 | `14-networth.desk.en` coin rows draw the eye in the lower half |
| 3 | - | |
| 4 | 5 | `14-networth.desk.en` area fill on truncated axis; no contributions/growth split |
| 5 | - | |
| 6 | 7 | `14-networth.desk.en` account share bars sum to 100 % and match Settings balances |
| 7 | 8 | `14-networth.phone.de` chart keeps axis and labels |
| 8 | 7 | `14-networth.desk.en` single-series gold line, labelled axis |
| 9 | 6 | `14-networth.desk.en` 3D coins vs flat UI |

---

## 15-investments, 32-hidden-investments

- **Value line plus monthly gain/loss bars on a shared x-axis** (`15-investments.desk.en`): a good composition. The bars sum exactly to the +504.90 € headline (−111+497+47−259−429−261+564+427+112−82 = 505). **keep**
- **"Value without your pay-ins" is hard to interpret** (`15-investments.desk.en` legend): the line starts near 8.7k, but the start-of-period depot was about 5.8k (9,350 − 3,000 − 505). The line evidently adds all period pay-ins at the start. That construction is valid for showing market movement, but the label does not explain it, and a user will compare 8.7k with the real Jan balance. Severity: slows a task. Suggestion: rename it to "Market movement (as if all pay-ins were there from the start)", or plot an indexed performance line (Jan = 100) instead.
- **Area fill again on a truncated 8k–10k axis** (`15-investments.desk.en`): the same objection as 14.
- **Holdings 85/15 split bar plus per-ETF share bars** (`15-investments.desk.en`): clear. **keep**
- **Holding sparklines** (`15-investments.desk.en`, the small green lines in each holding card): there is no scale or period, and they are always green even though the trend is mixed. Fine as a glyph.
- **Return figures with different bases** (`15-investments.desk.en` holding "+7.5 % · 474 €" for the period vs `19-etf.desk.en` "+1,160.97 € · +17.2 %" since purchase): neither number names its base. Severity: slows a task. Suggestion: "+7.5 % this period" / "+17.2 % since first buy".
- **Tax-free allowance bar** (`15-investments.desk.en` "95.40 € of 1,000.00 €"): fine. **keep**
- **Hidden mode** (`32-hidden-investments.desk.en`): the y-axis ticks and bar labels are masked, but the chart shape and percentages stay. This is a sensible privacy trade-off. **keep**

| # | Score | Based on |
|---|---|---|
| 1 | 7 | `15-investments.desk.en` "Depot value on 30 Oct 2026" hero |
| 2 | 8 | `15-investments.desk.en` value chart over monthly bars |
| 3 | - | |
| 4 | 6 | `15-investments.desk.en` "Value without your pay-ins" construction unexplained; area on truncated axis |
| 5 | - | |
| 6 | 6 | `15-investments.desk.en` +7.5 % vs `19-etf.desk.en` +17.2 % for the same ETF, bases unstated |
| 7 | 8 | `15-investments.phone.de` gain/loss bars keep only max/min labels (+564 / −429), which is sensible |
| 8 | 6 | `15-investments.desk.en` red/green gain bars rely on hue plus sign, which is acceptable because the signed labels carry it |
| 9 | 8 | `15-investments.desk.en` clean composition |

---

## 16-inv-forecast

- **Fan chart with median, 8-of-10 band and paid-in line** (`16-inv-forecast.desk.en`): the right form for "where could this go?", with honest framing ("Assumptions, not a promise") and milestone markers on the median. **keep**
- **Bad / middle / good range bar** (`16-inv-forecast.desk.en`, 46,246 / 68,412 / 102,388 with a "paid in" tick): it summarises the fan's end-point well. **keep** The "paid in" tick sits left of the band, so its label overlaps the "Bad case" label area on phone (`16-inv-forecast.phone.de`). Cosmetic.
- **Lower band edge is invisible** (`16-inv-forecast.desk.en`): the band's lower boundary blends into the dark "paid in" fill, so the fan looks one-sided (upside only). Severity: slows a task (understates downside). Suggestion: draw the band edges as thin lines, or render "paid in" as a line only, without a fill.
- **"1 in 12 futures ends below what you paid in"**: frequency framing. Excellent. **keep**
- **Swing "15 % a year"** here vs **"±17 %"** on `17-inv-analysis.desk.en`: two volatility numbers for the same depot. See 17.

| # | Score | Based on |
|---|---|---|
| 1 | 9 | `16-inv-forecast.desk.en` "Where it could go … Assumptions, not a promise" |
| 2 | 8 | `16-inv-forecast.desk.en` 68,412 € headline, then range bar, then chart |
| 3 | - | |
| 4 | 7 | `16-inv-forecast.desk.en` lower band edge lost in paid-in fill |
| 5 | - | |
| 6 | 5 | `16-inv-forecast.desk.en` Swing 15 % vs `17-inv-analysis.desk.en` ±17 % |
| 7 | 7 | `16-inv-forecast.phone.de` assumptions in a 2×2 grid; chart pushed far below the fold |
| 8 | 7 | `16-inv-forecast.desk.en` median labelled in-line ("middle path", "paid in") |
| 9 | 8 | `16-inv-forecast.desk.en` restrained gold-on-dark fan |

---

## 17-inv-analysis

- **"Return in this period" as two progress bars** (`17-inv-analysis.desk.en`, +6.7 % and +6.3 %): progress-bar tracks imply a 0–100 % scale, but 6.7 % fills the whole track. The bars add nothing to the two numbers, and the track suggests a goal. Severity: cosmetic. Suggestion: show the two numbers side by side, or use a dot plot on a shared axis with a 0 line and a benchmark (for example the 1.75 % comparison rate from `23-settings-depot`).
- **"±17 %" calm↔wild gauge** (`17-inv-analysis.desk.en`): a rainbow-ish gradient with no ticks. The "usual for stock ETFs" band is a nice touch, but its position cannot be read as a number. Severity: cosmetic. Suggestion: add 0 / 10 / 20 / 30 % ticks.
- **Two volatility numbers** ("±17 %" here, "15 % a year" in `16-inv-forecast.desk.en`): if one is realised over Jan–Oct and the other is the long-run assumption, say so. Severity: slows a task.
- **Drawdown chart** (`17-inv-analysis.desk.en`): correct form, labelled trough "−12.7 % (Jun 26)" and current "0.9 % below its high" chip. **keep** It uses monthly points, while the Investments value chart is daily, so the depth can differ from what users see on the daily chart. Minor.
- **Monthly returns heatmap row** (`17-inv-analysis.desk.en`): a diverging green/red scale with the value printed in every cell, best and worst outlined, and "5 of 10 months up". The colour carries no information the number doesn't, which is fine here. **keep**
- **Sharpe ratio**: `23-settings-depot.desk.en` says the interest rate is "Used for the Sharpe ratio", but no Sharpe ratio appears on Analysis. Severity: cosmetic.

| # | Score | Based on |
|---|---|---|
| 1 | 7 | `17-inv-analysis.desk.en` card titles answer plain questions ("Ups and downs", "Drawdown") |
| 2 | 7 | `17-inv-analysis.desk.en` |
| 3 | - | |
| 4 | 6 | `17-inv-analysis.desk.en` return progress-bars and the tick-less gauge |
| 5 | - | |
| 6 | 5 | `17-inv-analysis.desk.en` ±17 % vs 15 % on Forecast; Sharpe promised in Settings, absent here |
| 7 | 8 | `17-inv-analysis.phone.de` heatmap wraps to 2×6 with values kept |
| 8 | 7 | `17-inv-analysis.desk.en` heatmap values printed in cells, not colour-only |
| 9 | 7 | `17-inv-analysis.desk.en` gauge gradient is decorative |

---

## 18-inv-payments

- (`18-inv-payments.desk.en`) The page is a month-by-month accordion of identical "300.00 €" rows behind "Show all 27 months". The page's question ("how much have I put in, and steadily?") is a chart question. Severity: cosmetic. Suggestion: add a cumulative paid-in step line or 27 small monthly bars above the list, so gaps or raises become visible at a glance. "3,600.00 € in the last 12 months" reconciles with 12 × 300. **keep** that number.

| # | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| 18 | 7 (`18-inv-payments.desk.en` "Money put in" plus 12-month total) | - | - | 5 (`18-inv-payments.desk.en` 27 months only as accordion rows) | - | 7 | - | - | - |

---

## 19-etf

- **Price chart with purchase dots and a "Your average 110.71 €" line** (`19-etf.desk.en`): this is the best chart in the app. It answers "did I buy well, and where am I versus cost?" in one view. **keep**
- **Area fill on a 100–140 axis**: the same truncated-axis objection, though it is milder for a price chart, where nobody reads area as amount.
- **Phone** (`19-etf.phone.de`): the "Dein Schnitt 110,71 €" label sits on the price line and a purchase dot. Severity: cosmetic. Suggestion: anchor the label at the left axis.

| # | Score | Based on |
|---|---|---|
| 1 | 9 | `19-etf.desk.en` "Your value" plus purchases-on-price chart |
| 2 | 8 | `19-etf.desk.en` |
| 3 | - | |
| 4 | 8 | `19-etf.desk.en` purchase dots and average-cost reference line |
| 5 | - | |
| 6 | 6 | `19-etf.desk.en` +17.2 % vs +7.5 % on `15-investments`, bases unstated |
| 7 | 7 | `19-etf.phone.de` average label overlaps the line |
| 8 | 7 | `19-etf.desk.en` |
| 9 | 8 | `19-etf.desk.en` |

---

## 20–28 settings, 30 connect dialog

Almost no data graphics. Only these matter for my role:
- **"Bank login needed within 90 days" bar** (`20-settings-bank.desk.en`): a full green bar means "plenty of time", and it will drain. That is clear enough together with the text. **keep**
- **Backup retention strip** (`24-settings-backup.desk.en`): segmented tiers (1/year · 1/month · 1/week · 1/day) with labelled spans and "now" at the right. This is a nice non-linear timeline that explains a retention policy better than text would. **keep** It currently shows only dashed empty slots ("No backups yet"), so the filled state was not reviewed.
- **"94 % of the last 60 days categorized without help"** (`21-settings-categories.desk.en`): a one-line metric, good. It is at odds with "Needs review 39" elsewhere, though.
- 22, 23, 25, 26, 27, 28, 30: no charts. Score "-" on every line.

| # | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| 20 | - | - | - | 7 (`20-settings-bank.desk.en` 90-day bar with number) | - | - | - | - | - |
| 24 | 8 (`24-settings-backup.desk.en` retention strip explains the policy) | - | - | 7 | - | - | - | - | 7 |

---

## 31-hidden-overview

- (`31-hidden-overview.desk.en`, `31-hidden-overview.phone.de`) The amounts are blurred, but the Sankey widths, percentages, savings ring 39 % and jar level remain. That is a coherent choice: proportions are shown, absolute amounts are hidden. **keep** Note that the jar plus the per-day figure could let someone infer scale. That is acceptable.

| # | 4 | 6 |
|---|---|---|
| 31 | 7 (`31-hidden-overview.desk.en` proportions kept, absolutes masked) | 8 (`31-hidden-overview.desk.en` same masking rule as `32-hidden-investments`) |

## 40–42 wizard and login
No data graphics. The step progress bar on `41-wizard-country.phone.de` (5 segments, 2 filled) is fine. All lines "-".

---

## Top 10

1. **The orbit view has no precise reading** (`13-recurring-orbit.desk.en`, `13-recurring-orbit.phone.de`): angle on a tilted ellipse plus 3D sphere area, 8 of 13 items unlabelled, and an unreadable blob on phone. Replace it with a "next 12 months" lane timeline (one lane per cadence, tick height = amount) or an annual-cost bar chart grouped by cadence. At minimum, never make it the default and hide it on phone. Severity: slows a task.
2. **Bar lists scaled to the largest row on a track that reads as 100 %** (`07-spending.desk.en` Housing 58.3 % = full bar; `09-drill-group.desk.en` merchants/categories; `10-drill-category.desk.en`). Scale bars to share, or remove the grey track. Severity: slows a task.
3. **Headline totals disagree across screens** (`02-transactions.desk.en` 42,057.91 in / 31,970.76 out vs `01-overview.desk.en` 33,538.60 / 20,451.45): own transfers (Sparen ±800 €) are counted on Transactions. Exclude them or label them. Severity: slows a task.
4. **Same figure, different % bases, unstated** (`01-overview.desk.en` Housing 35.6 % of income vs `07-spending.desk.en` 58.3 % of spending; `15-investments.desk.en` ETF +7.5 % vs `19-etf.desk.en` +17.2 %). Name the base every time ("of income", "this period", "since first buy"). Severity: slows a task.
5. **Two volatility numbers for one depot** (`16-inv-forecast.desk.en` "Swing 15 % a year" vs `17-inv-analysis.desk.en` "±17 %"). Reconcile them or label them realised vs assumed. Severity: slows a task.
6. **Area fills on truncated y-axes exaggerate growth** (`14-networth.desk.en` 25k baseline, `15-investments.desk.en` 8k baseline). Drop the fill or start at zero. Also split net-worth growth into contributions vs market. Severity: slows a task.
7. **The payday day-strip does not encode amounts** (`01-overview.desk.en`): the Nov 1 dot (2,150 €, per `34-payday-details.desk.en`) looks like the 2.99 € dot. Use a stepped "money left" line or amount-sized, labelled dots. The jar and coin are ornament competing with the hero number. Severity: slows a task.
8. **The heatmap palette collides with category colours and its bins have no values** (`07-spending.desk.en` "Your year in days"). Use a single-hue sequential ramp not used by any category and give the legend euro ranges. Severity: slows a task.
9. **"Value without your pay-ins" is unexplained** (`15-investments.desk.en`): it starts at about 8.7k while the real depot was about 5.8k. Rename it, or plot an indexed performance line. The forecast's lower band edge also disappears into the paid-in fill (`16-inv-forecast.desk.en`), which hides downside. Severity: slows a task.
10. **Keep the strong charts as the model for the rest**: the ETF price chart with purchase dots and average-cost line (`19-etf.desk.en`), the monthly bars with an average line (`09-drill-group.desk.en`; fix the label overlap), the forecast fan with "1 in 12 futures ends below what you paid in" (`16-inv-forecast.desk.en`), the monthly-returns heatmap with values in cells (`17-inv-analysis.desk.en`) and the payday breakdown dialog (`34-payday-details.desk.en`). **keep**
