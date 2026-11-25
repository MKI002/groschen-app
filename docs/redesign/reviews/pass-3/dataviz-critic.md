# Groschen, pass 3: data visualisation review

Role: data visualisation critic. I score only the rubric lines a chart critic can judge: 1 clarity of purpose, 2 hierarchy (chart vs. number), 4 data presentation, 7 phone experience (for charts), 9 visual craft (for charts). The other lines are "-". Every score names an element on a named screenshot.

Method: I looked at every desk.en and phone.de screenshot, plus desk.de for 01, and cropped the full-resolution images to read chart detail (01, 02, 07, 09). I checked the arithmetic between numbers where a chart and a label should agree.

---

## 01 Overview (01-overview.desk.en / .desk.de / .phone.de / .phone.en; 31-hidden-overview.*)

| Line | Score | Based on |
|---|---|---|
| 1 clarity | 6 | `01-overview.desk.en`: the "Available until payday" hero answers its question well. The phone-shaped "tank" gauge next to it has no label, scale or value, so nobody can tell what fraction it fills. |
| 2 hierarchy | 7 | `01-overview.desk.en`: 5,170.65 € dominates correctly. The Sankey "Where the money went" is the largest element on the page, yet its left half carries almost no information. |
| 4 data presentation | 5 | `01-overview.desk.en`: on the Sankey, Salary (99.6 %) to Income is a solid block about 370 px wide that encodes one number. The Income/Spending mini bars have no axis and no month labels. The Saved split bar has three segments but its caption names only two. |
| 7 phone | 7 | `01-overview.phone.de`: the Sankey drops the source column and gives the width to the outflows, which is a good adaptation. The payday strip still fits. |
| 9 visual craft | 6 | `01-overview.desk.en`: the glowing gold coin on the payday strip, the glossy tank and the gradient bands look polished but compete with the numbers. The mini bars have a glow on the last bar. |

### Findings
- **Sankey wastes half its width on a single source**: `01-overview.desk.en`, "Where the money went". Salary is 99.6 % of income, so the Salary→Income stage is a big green rectangle that tells you nothing. Meanwhile the 8 small outflows (Transport down to Uncategorized) are squeezed into thin, crossing ribbons whose labels stack tightly. **Slows a task.** Suggestion: when one source is above about 90 %, drop the source stage and put "Salary 99.6 % · other 0.4 %" as a caption on the Income node (the phone version already does this). Use the freed width for the outflows. For the actual question ("how was my income split?") a sorted horizontal bar list or one 100 % stacked bar reads more precisely than ribbons.
- **The same category has two different shares on two screens**: Housing is "35.6 %" on `01-overview.desk.en` (share of income) and "58.3 %" on `07-spending.desk.en` (share of spending), with the same blue and the same label. **Slows a task** (it erodes trust). Suggestion: write the denominator next to the percentage ("35.6 % of income", "58 % of spending").
- **The Sankey leaves out "Personal"**: the outflows on `01-overview.desk.en` add up to 33,700.97 €, which is 162.37 € more than Income (33,538.60 €). The gap is exactly the net-refund "Personal" group (−162.37 €) that appears on `07-spending.desk.en`. **Cosmetic**, but a careful user will notice that the sums don't match. Suggestion: show the refund as a small inflow, or add a footnote.
- **Tank gauge with no meaning**: `01-overview.desk.en`, the phone-shaped glass to the right of 5,170.65 € (about 70 % full). It has no label, no scale and no value, and it isn't clear whether it shows the share of salary left or the share of the month left. **Cosmetic / slows.** Suggestion: remove it, or turn it into a labelled bullet bar such as "5,170 € of 7,768 € left · 28 of 31 days left". Two aligned bars (money left vs. time left) would answer the real question: am I spending faster than the month is passing?
- **Payday strip (keep, with a fix)**: `01-overview.desk.en`, the day pills from Salary 27 Oct to Fri 27 Nov. The 14 upcoming payments appear as identical red dots, so 1,050 € rent looks the same as 2.99 € Apple. **Cosmetic.** Suggestion: size the dots by amount, or mark only payments above about 50 € and show amounts on hover. The concept is good and should **keep**.
- **Income/Spending mini bars carry almost no information**: `01-overview.desk.en`, the Income card sparkbars are 10 near-identical bars (salary is constant). Spending sparkbars have no month labels or average line, even though the hint next to them says "August 2026 was 42 % above your average". **Cosmetic.** Suggestion: draw a faint average tick and highlight August in the spending bars so the hint and the chart point at the same thing. For income, replace the bars with a single "+0 % vs. last month" figure.
- **Saved bar caption is incomplete**: `01-overview.desk.en`, Saved card. The bar has gold (invested), teal (put aside) and grey (stays) segments, but the caption reads only "3,000.00 € invested · 1,991.75 € stays". The largest segment, 8,095.40 € put aside, has no caption. On `01-overview.desk.de` the caption wraps to two lines ("bleibt / liegen"). **Slows a task.** Suggestion: use a three-item legend with coloured dots that matches the Sankey colours.
- **39 % savings ring duplicates the bar**: `01-overview.desk.en`, the "39 % Savings rate" ring sits next to a bar that already encodes the parts. **Cosmetic.** Keep the number; the ring is optional.
- **Overview "Income" doesn't match the Transactions "in" total**: the Overview says Income is 33,538.60 € and Spending 20,451.45 €. `02-transactions.desk.en` says "42,057.91 € in · 31,970.76 € out" for the same Jan–Oct 2026. The gap is presumably transfers and savings, but nothing explains it. **Slows a task.** Suggestion: show a one-line reconciliation on Transactions ("of which 8,519 € transfers between your accounts").
- **Hidden mode (keep)**: `31-hidden-overview.desk.en` / `.phone.de`. Amounts are blurred but percentages and chart shapes stay, so the page is still useful when someone is looking over your shoulder. **Keep.**

---

## 02–04 Transactions list (02-transactions.*, 03-transactions-review.*, 04-transactions-filtered.*)

| Line | Score | Based on |
|---|---|---|
| 1 clarity | 8 | `02-transactions.desk.en`: day-grouped list with a day subtotal on the right. |
| 4 data presentation | 6 | `03-transactions-review.desk.en`: the summary line "8 transactions · 110,315.81 € in · 84,234.46 € out" cannot be the total of the 8 rows shown, which add up to about −410 €. |
| 7 phone | 6 | `02-transactions.phone.de`: the category chip moves under the merchant name and the amount stays right-aligned (good), but the purpose text is cut ("zählt für November 2026 · LOHN..."). |
| 9 visual craft | 8 | `02-transactions.desk.en`: tabular right-aligned amounts, green only for income. |

### Findings
- **Summary totals don't belong to the filtered list**: `03-transactions-review.desk.en`, the line under the "These transactions need a category" banner. It reads "All periods · 8 transactions · 110,315.81 € in · 84,234.46 € out". The in/out totals look like all-time totals, not the 8 rows shown. The period label also switches to "All periods" while the period button still says "Jan – Oct 2026". **Slows a task.** Suggestion: compute the totals from the visible set, or hide them when a status filter is active.
- **Partial-refund progress bar (keep)**: `03-transactions-review.desk.en`, Lena Berger: "32.00 € of 64.00 € back" with a small green bar. Strikethrough on the fully refunded Amazon −34.99 € (`02-transactions.desk.en`). Both are precise and clear. **Keep.**
- **Day subtotals appear inconsistently**: `02-transactions.desk.en`. "Tuesday 27 October" (salary only) and "Wednesday 21 October" (single row) have no subtotal, while other days do. Monday 28 Sept shows "3,291.40 €" in green. **Cosmetic.** Suggestion: either always show the day total or only on days with two or more rows, and say so.

## 05 Transaction edit dialog (05-transactions-edit.*)
| Line | Score | Based on |
|---|---|---|
| 4 data presentation | 7 | `05-transactions-edit.desk.en`: the category chips carry their group colour dots (blue Housing, gold Food, pink Transport), the same as the charts. This is good colour continuity. |
| 9 visual craft | 6 | `05-transactions-edit.desk.en`: the "SUBSCRIPTIONS" header is cut off by the sticky "Use this category for every transaction" row, so its chips are hidden. |

- **Colour collision**: the Insurance chip is green (`05-transactions-edit.desk.en`), the same family as the Income/Salary green used across the Sankey and the calendar legend. **Cosmetic.** Suggestion: reserve green for money coming in.

## 06 Transactions empty (06-transactions-empty.*)
- `06-transactions-empty.desk.en`: "0 transactions · Clear filters". Clear, no chart issue. **Keep.**

---

## 07 Spending (07-spending.* , 33-period-menu.*)

| Line | Score | Based on |
|---|---|---|
| 1 clarity | 6 | `07-spending.desk.en`: the "Spending breakdown" bar list answers "where does my money go". The sunburst next to it answers the same question less precisely. |
| 2 hierarchy | 6 | `07-spending.desk.en`: the sunburst and the bar list are given equal weight, even though the list is the readable one. |
| 4 data presentation | 6 | `07-spending.desk.en`: the bar list with € and % is good. The sunburst's outer ring (sub-categories) has about 25 unlabelled slices. The "Your year in days" legend "Less ■■■■■ More" has no values. |
| 7 phone | 4 | `07-spending.phone.de`: the "Dein Jahr in Tagen" heatmap is cut off in the middle of June with no scroll cue, so July to October (the most recent and most relevant months) are invisible. |
| 9 visual craft | 6 | `07-spending.desk.en`: the heatmap palette (violet → magenta → orange → glowing yellow) is a multi-hue scale with a glow on the top bin. |

### Findings
- **Sunburst duplicates the bar list**: `07-spending.desk.en`, the "Total 20,451 €" donut. The inner ring repeats the 9 groups that the bar list already shows with exact values. The outer ring adds sub-categories, but none are labelled (about 25 slivers, many under 2 %), so you can only read them by hovering. **Slows a task.** Suggestion: drop the sunburst. Let each group row in the bar list expand into its categories (indented bars), or show a single 100 % stacked bar above the list. If you keep the ring, label the outer slices over 5 %.
- **Bar list (keep)**: `07-spending.desk.en`. Sorted, value and % aligned, bars scaled to the maximum, and "Personal · more refunds than spending −162.37 €" handled honestly with an empty bar. **Keep.**
- **Heatmap scale can't be read**: `07-spending.desk.en`, "Your year in days". The five colour bins have no thresholds, and a hue sequence of violet, magenta, orange and yellow is not perceived as ordered (magenta vs. orange is ambiguous, and it is hard for colour-blind users). **Slows a task.** Suggestion: use a single-hue sequential ramp, label the bins ("< 20 €, 20–60, 60–150, 150–400, > 400 €"), and drop the glow on the top bin. The summary line "185 days without spending · 1,233.55 € on your priciest day · 177.08 € on an average spending day" is very good and should **keep**.
- **Phone heatmap clipped and scrolled to the wrong end**: `07-spending.phone.de`. The grid stops halfway through a June cell. **Blocks a task** (you can't see recent days on the phone). Suggestion: scroll to today on load and add a fade or arrow at the edge. Better still, on the phone show the last 13 weeks only, with the year navigator for older weeks.
- **Weekend rows are entirely empty** in `07-spending.desk.en` (the Sat/Sun rows are grey all year). This is probably the demo data, but it makes the chart look broken in screenshots. **Cosmetic (capture).**
- **Period menu** (`33-period-menu.desk.en`): Month / Last 30 days / Year to date / Year / Last 12 months / All time. Clear. **Keep.**

## 08 New group dialog (08-spending-group-dialog.*)
- `08-spending-group-dialog.desk.en`: a chip picker with group colour dots, consistent with the charts. No chart issue. The SUBSCRIPTIONS section is cut off at the dialog fold, the same problem as on 05. **Cosmetic.**

## 09 Drill: group (09-drill-group.*)

| Line | Score | Based on |
|---|---|---|
| 1 clarity | 8 | `09-drill-group.desk.en`: "Food & Dining 3,480.29 €, ↑35 % vs. the period before" and a "Per month" column chart with an "Average 348 €" reference line. |
| 4 data presentation | 8 | `09-drill-group.desk.en`: the monthly bars have a zero baseline, gridlines at 200 € steps and a labelled average. The Top merchants bars show € and %. |
| 7 phone | 7 | `09-drill-group.phone.de`: the chart keeps its axis and average line. Month labels thin out to every other month, which is acceptable. |
| 9 visual craft | 8 | `09-drill-group.desk.en`: flat gold bars and no ornament. |

### Findings
- **This is the best chart in the app (keep)**: `09-drill-group.desk.en`, the "Per month" bars with the average line. Use it as the pattern for the Overview mini bars. **Keep.**
- **Zero rows add noise**: `09-drill-group.desk.en`, Categories card. "Food & Dining · 0× 0.00 €" and "Food delivery · 0× 0.00 €" each get a full row with an empty bar. **Cosmetic.** Suggestion: hide 0× rows or collapse them into "2 unused categories".
- **"↑35 %" is red with no anchor**: `09-drill-group.desk.en`. It says "vs. the period before" but doesn't say what that period is or what the amount was. **Cosmetic.** Suggestion: add a tooltip or subline, e.g. "Mar–Dec 2025: 2,578 €".

## 10 Drill: category (10-drill-category.*)
| Line | Score | Based on |
|---|---|---|
| 1 clarity | 4 | `10-drill-category.desk.en`: the "Income" drill shows "Received 0.00 €, 0 transactions, Nothing to chart" for Jan–Oct 2026, while the Overview reports 33,538.60 € income for the same period. |
| 4 data presentation | 3 | Same element: a total that contradicts another screen. |

- **Income drill reports zero**: `10-drill-category.desk.en` / `.phone.de`. Either this drill page filters on a category that doesn't hold the salary (the salary is under "Salary"), or it is broken. In both cases a page titled "Income" that says 0.00 € while the Overview says 33.5 k is a trust breaker. **Blocks a task.** Suggestion: make the Income view of Spending (`07` toggle "Income") reuse the same income definition as the Overview Sankey.
- **The empty state is well done (keep)**: "Nothing to chart · No transactions match in this period" appears instead of an empty axis. **Keep.**

---

## 11 Fixed costs: list (11-recurring-list.*)

| Line | Score | Based on |
|---|---|---|
| 1 clarity | 8 | `11-recurring-list.desk.en`: "1,407.01 € fixed costs per month · 16,884.11 € a year, 13 recurring payments" and "Next up". |
| 4 data presentation | 7 | `11-recurring-list.desk.en`: the "+7.00 €" / "+9.00 €" price-change pills and the "≈ 27.07 € a month" normalisation for 4-weekly and yearly items are precise. |
| 7 phone | 6 | `11-recurring-list.phone.de`: the "In 2 days" due column is dropped from the "Laufend" list, so on the phone you lose when each payment is due. |
| 9 visual craft | 8 | `11-recurring-list.desk.en`: a clean list with no ornament. |

- **Price changes have no history**: `11-recurring-list.desk.en`, "Stadtwerke Muenchen +7.00 €". A tiny step-line sparkline of the last 12 charges would show when it changed. **Cosmetic.**
- **Fixed costs vs. savings plans (keep)**: the footer "3 savings plans run along: 1,100.00 € a month" separates savings from costs. This is good and should **keep**.

## 12 Fixed costs: calendar (12-recurring-calendar.*)

| Line | Score | Based on |
|---|---|---|
| 1 clarity | 6 | `12-recurring-calendar.desk.en`: the header says "1,423.48 € fixed costs" while the List tab on `11` says "1,407.01 €" and the Orbit says "1,407 €". These are three views of the same thing with two numbers and no explanation (one is this month's actual, which includes the quarterly Rundfunkbeitrag; the other is a normalised monthly figure). |
| 4 data presentation | 5 | `12-recurring-calendar.desk.en`: the day chips are truncated ("Ha... −1,050 €", "Spar... −800 €", "+1") and rounded to whole euros. The progress bar under the header is 100 % filled on 30 Oct and so carries no information. |
| 7 phone | 5 | `12-recurring-calendar.phone.de`: day 1 shows a single "−2.150 €", which merges 1,050 € rent with 1,100 € of savings orders into one "cost" figure. Day 27 shows a salary dot with no amount. |
| 9 visual craft | 7 | `12-recurring-calendar.desk.en`: the legend "Paid · Expected · Standing order · Salary" is present, but the teal (standing order) and green (salary) are hard to tell apart. |

### Findings
- **Two "fixed costs per month" figures**: `11-recurring-list.desk.en` "1,407.01 €" vs. `12-recurring-calendar.desk.en` "1,423.48 €". **Slows a task.** Suggestion: label the calendar figure "This month: 1,423.48 € (incl. quarterly Rundfunkbeitrag 55.08 €)".
- **Phone day totals mix costs and savings**: `12-recurring-calendar.phone.de`, "−2.150 €" on 1 Oct. **Slows a task.** Suggestion: show costs only in the day total and mark savings with a separate teal dot.
- **Standing order vs. salary colours**: `12-recurring-calendar.desk.en` legend. Teal and mint are too close. **Cosmetic.** Suggestion: use a shape difference (an outlined dot for transfers) or a clearly different hue.
- **The "Day by day" side list is the readable version (keep)**: `12-recurring-calendar.desk.en`. **Keep.**

## 13 Fixed costs: orbit (13-recurring-orbit.*)

| Line | Score | Based on |
|---|---|---|
| 1 clarity | 3 | `13-recurring-orbit.desk.en`: "Your month in orbit". The question ("what is due when, and how much?") is answered better by the Calendar and List tabs next to it. |
| 4 data presentation | 2 | `13-recurring-orbit.desk.en`: perspective ellipses distort the angular position (due day), sphere size encodes amount with no scale, only 4 of 13 dots are labelled, and the "Hausverwaltung Kr..." label overlaps its own sphere. No value can be read without hovering. |
| 7 phone | 2 | `13-recurring-orbit.phone.de`: the whole system collapses into a cluster about 150 px wide. The labels "HUK-Coburg", "Telekom" and "Hausverwaltung Kr..." overlap the "1.407 €" centre total, so it is unusable. |
| 9 visual craft | 5 | `13-recurring-orbit.desk.en`: glossy 3D spheres, a glowing sun and a starfield. The ornament is the content. |

- **Orbit view is decoration posing as a chart**: `13-recurring-orbit.desk.en` / `.phone.de`. **Slows a task** (it is a whole tab with nothing readable). Suggestion: replace it with a "next 30 days" horizontal timeline. Put days on the x axis and one bar per payment, with height or label = amount. Add a cumulative step line that shows how much of the 1,407 € has left the account by each day, and mark today. That answers "when will the money go out?" precisely. If the orbit stays as a fun extra, move it behind the easter-egg toggle and don't make it a peer of List and Calendar.

---

## 14 Net worth (14-networth.*)

| Line | Score | Based on |
|---|---|---|
| 1 clarity | 7 | `14-networth.desk.en`: "Today 44,931.92 € ↑13,592.05 €" with a monthly line. |
| 2 hierarchy | 7 | `14-networth.desk.en`: the hero number, then the chart, then the accounts. |
| 4 data presentation | 5 | `14-networth.desk.en`: the area fill sits on a y axis that starts at 25 k €, so a 44 % rise looks like a five-fold rise. The account cards show 17 % / 62 % / 21 % as three separate bars that don't share a frame. The savings-plan coin rows are 12 identical gold coins. |
| 7 phone | 7 | `14-networth.phone.de`: the chart stays readable with 4 x-labels. |
| 9 visual craft | 6 | `14-networth.desk.en`: the "Savings plans" coin rows (glossy gold coins) are ornament. |

### Findings
- **Area chart on a truncated axis**: `14-networth.desk.en`, the net-worth line from Dec 25 (about 31 k) to Oct 26 (44.9 k), with the axis starting at 25 k. An area fill implies a zero baseline. **Slows a task** (it misreads growth). Suggestion: either start the axis at 0, or keep it truncated and remove the area fill (line only). Better still for the question "what is my wealth made of over time": use a stacked area by account (Girokonto / Extra-Konto / Depot) with a zero baseline. That would also replace the three separate share bars.
- **Account share bars**: `14-networth.desk.en`, the 17 % / 62 % / 21 % bars under each account card. **Cosmetic.** Suggestion: one shared 100 % stacked bar above the three cards.
- **Coin rows carry no information**: `14-networth.desk.en`, the 12 coins under "250.00 € a month" with Nov / Feb / May / Aug ticks. Every coin is identical (every payment arrived), so the row shows nothing until something goes wrong, and even then you would have to spot one dim coin among 12. **Cosmetic.** Suggestion: replace it with the text "27 of 27 payments on time" plus a small cumulative line for "6,750.00 € since August 2024", or show coins only when one is missing.

## 15 Investments (15-investments.*, 32-hidden-investments.*)

| Line | Score | Based on |
|---|---|---|
| 1 clarity | 6 | `15-investments.desk.en`: "Value without deposits" is the legend for the main line, but the line ends at about 9,350 €, the actual depot value. The name doesn't match what is drawn, or else the concept needs explaining. |
| 4 data presentation | 7 | `15-investments.desk.en`: the "Gain and loss per month" bars (−111, +497, +47, −259, −429, −261, +564, +427, +112, −82) are labelled and add up exactly to the +504.90 € headline. This is excellent. The main line again has an area fill on a y axis that starts at 8 k. |
| 7 phone | 7 | `15-investments.phone.de`: the bars keep only their extreme labels (+564 / −429), which is the right reduction. |
| 9 visual craft | 7 | `15-investments.desk.en`: the line and bars share an x axis and the colours have meaning (gold value, green/red gain). |

### Findings
- **Monthly gain bars (keep)**: `15-investments.desk.en`. **Keep.**
- **Unclear series name**: `15-investments.desk.en`, legend "Value without deposits". **Slows a task.** Suggestion: name it "Market value (deposits removed)" with a one-line tooltip, or plot the real value with the "Money paid in" toggle drawn as a second line (that toggle exists but is off by default).
- **The same 85/15 split is drawn three times**: `15-investments.desk.en`, the Holdings full-width split bar, plus a mini bar plus "85 % of the depot" text on each card. **Cosmetic.** Keep one of them.
- **Holding sparklines have no scale or period**: `15-investments.desk.en`, the green squiggles on the Vanguard and iShares cards. They are always green even though the Vanguard line falls in the middle of the period. **Cosmetic.** Suggestion: use a neutral colour, add an end-dot, and use the same period as the page.
- **The return for the same fund differs between screens**: `15-investments.desk.en` Vanguard card "+7.5 % · 474 €" vs. `19-etf.desk.en` "+1,160.97 € · +17.2 %". One is the period return and the other the since-purchase return, and neither is labelled. **Slows a task.** Suggestion: add "Jan–Oct 2026" or "since first buy" next to each figure.
- **Tax-free allowance bar (keep)**: `15-investments.desk.en`, "95.40 € of 1,000.00 €". A simple, exact bullet. **Keep.**
- **Hidden mode**: `32-hidden-investments.desk.en`. Y-axis ticks are blurred too ("9.9k €"), but "+6.7 %" and the bar shapes stay. Good. **Keep.**

## 16 Forecast (16-inv-forecast.*)

| Line | Score | Based on |
|---|---|---|
| 1 clarity | 8 | `16-inv-forecast.desk.en`: "In 10 years · Oct 2036 68,412 €", the Bad case 46,246 € / Good case 102,388 € range bar with a "paid in" tick, and "1 in 12 futures ends below what you paid in". This is honest uncertainty communication. |
| 4 data presentation | 8 | `16-inv-forecast.desk.en`: a fan chart with a zero baseline, a paid-in line, labelled milestones (10k / 25k / 50k) on the median path, and horizon buttons (1Y to 30Y). |
| 7 phone | 7 | `16-inv-forecast.phone.de`: the chart stays legible. The horizon buttons wrap tightly. |
| 9 visual craft | 7 | `16-inv-forecast.desk.en`: a restrained gold band. |

- **Fan chart and range bar (keep)**: `16-inv-forecast.desk.en`. **Keep.**
- **Volatility figure doesn't match Analysis**: here "Swing 15 % a year", but `17-inv-analysis.desk.en` says "±17 % up or down in a normal year". It is the same concept with two different numbers. **Slows a task.** Suggestion: use one computed value, or name the different windows.
- **The fan band edges aren't labelled**: `16-inv-forecast.desk.en`. The band ("8 of 10 outcomes") has no values at its 2036 edges, while the range bar on the left shows 46 k / 102 k. **Cosmetic.** Suggestion: put the same two numbers at the right edge of the band.

## 17 Analysis (17-inv-analysis.*)

| Line | Score | Based on |
|---|---|---|
| 1 clarity | 7 | `17-inv-analysis.desk.en`: the "Drawdown" chart with "−12.7 % (Jun 26)" and "0.9 % below its high", and the "Monthly returns" grid. |
| 4 data presentation | 5 | `17-inv-analysis.desk.en`: in "Return in this period", +6.7 % fills the whole bar and +6.3 % fills about 93 %. The bars are scaled to the maximum, which makes a 0.4-point difference look like a meaningful gap. The "Ups and downs" calm→wild gradient gauge has no ticks. |
| 7 phone | 3 | `17-inv-analysis.phone.de`: the "Monatsrenditen" grid stops at Jun. Jul to Oct (+7.9, +5.3, +1.3, −0.9) are cut off with no scroll cue. |
| 9 visual craft | 7 | `17-inv-analysis.desk.en`: the drawdown is a clean underwater area in muted red. |

### Findings
- **Return bars exaggerate a tiny difference**: `17-inv-analysis.desk.en`, "Your money +6.7 %" vs. "The funds themselves +6.3 %". **Slows a task.** Suggestion: drop the bars and show the two numbers side by side with the difference ("+0.4 pt from timing"), or put both as dots on one axis that starts at 0.
- **Gradient gauge**: `17-inv-analysis.desk.en`, "±17 %" on a blue→red calm/wild bar with a glowing knob. You can't read the band edges. **Cosmetic.** Suggestion: a labelled scale ("bonds 5 % · balanced 10 % · stock ETFs 15–20 % · single stocks 30 %+") with the marker on it.
- **Phone monthly returns clipped**: `17-inv-analysis.phone.de`. **Blocks a task** (the latest 4 months aren't visible). Suggestion: wrap into 2 rows of 6 months, or show the most recent 6 months first.
- **The "Outlined: the best and the worst month" legend looks like a checkbox**: `17-inv-analysis.desk.en`. **Cosmetic.** Suggestion: use an outlined swatch, not a checkbox.
- **Drawdown granularity**: `17-inv-analysis.desk.en`. About 11 monthly points, while the depot chart on `15` is daily, so the intra-month troughs are smoothed away. **Cosmetic.**
- **Sharpe ratio is set up but never shown**: `23-settings-depot.desk.en` says "Interest rate to compare with · used for the Sharpe ratio", but no Sharpe ratio appears on `17-inv-analysis.desk.en`. **Cosmetic.**

## 18 Pay-ins (18-inv-payments.*)
| Line | Score | Based on |
|---|---|---|
| 1 clarity | 7 | `18-inv-payments.desk.en`: "3,600.00 € in the last 12 months" with month accordions of "2 pay-ins · 300.00 €". |
| 4 data presentation | 6 | Same element: 27 months of identical 300 € rows, with no visual summary. |
- Suggestion: a small monthly column strip (27 bars) above the accordion would show gaps or raises at a glance. **Cosmetic.**

## 19 ETF detail (19-etf.*)

| Line | Score | Based on |
|---|---|---|
| 1 clarity | 8 | `19-etf.desk.en`: the price line with purchase dots and a "Your average 110.71 €" reference line answers "am I above my cost basis?". |
| 4 data presentation | 7 | `19-etf.desk.en`: the y axis has no unit (100, 110, ... 140) and the area fill sits on a 100 baseline. |
| 7 phone | 6 | `19-etf.phone.de`: the "Dein Schnitt 110,71 €" label sits on top of the price line around Jul. |
| 9 visual craft | 8 | `19-etf.desk.en`. |

- **Average-cost line and purchase dots (keep)**: `19-etf.desk.en`. **Keep.**
- Add "€" to the axis and drop the area fill on the non-zero axis. **Cosmetic.**

---

## 20–27, 30 Settings (20-settings-bank.* … 27-settings-account.*, 30-settings-connect-dialog.*)

| Line | Score | Based on |
|---|---|---|
| 4 data presentation | 7 | `24-settings-backup.desk.en`: the retention diagram (1 per year · 1 per month · 1 per week · 1 per day → now) shows the Smart Recycle policy at a glance. `20-settings-bank.desk.en`: the "Bank login needed within 90 days" bar. |

- **Backup retention diagram (keep)**: `24-settings-backup.desk.en`. It explains an abstract policy visually. **Keep.**
- **Countdown bar**: `20-settings-bank.desk.en`. The 90-days bar is full and green. Make sure it changes colour as the deadline nears (it can't be judged from these screenshots). **Cosmetic.**
- **Salary amount differs between screens**: `22-settings-hints.desk.en` says "about 3,180.00 €" for Nordlicht Software, while `02-transactions.desk.en` shows 3,340.00 € salary payments. Presumably this is an average over 27 payments, but say so. **Cosmetic.**
- 21, 23, 25, 26, 27, 30: no charts. Nothing to judge from a data-visualisation point of view.

## 40–42 Wizard and login
- `40-wizard-account.desk.en`, `41-wizard-country.desk.en`, `42-login.desk.en`: no data graphics. Nothing to judge.

---

## Things that work and must stay (keep)
1. `09-drill-group.desk.en`: the "Per month" bars with the average line.
2. `15-investments.desk.en`: the monthly gain/loss bars that add up to the headline.
3. `16-inv-forecast.desk.en`: the fan chart, the bad/good range bar with the paid-in tick, and "1 in 12 futures ends below what you paid in".
4. `07-spending.desk.en`: the sorted bar list with € and %, and the heatmap's summary sentence.
5. `19-etf.desk.en`: the average-cost line and purchase dots.
6. `03-transactions-review.desk.en`: the partial-refund micro bar.
7. `31-hidden-overview.*`: hidden mode keeps percentages and shapes.
8. `24-settings-backup.desk.en`: the retention diagram.

---

## Top 10

1. **Income drill reports 0.00 €**: `10-drill-category.desk.en`, the "Income · Received 0.00 € · Nothing to chart" page for Jan–Oct 2026 contradicts the Overview's 33,538.60 € income. **Blocks a task.** Use one income definition everywhere.
2. **Orbit view can't be read**: `13-recurring-orbit.desk.en` / `.phone.de`. Perspective rings, unscaled sphere sizes and 4 of 13 labels; on the phone it is an overlapping cluster. **Slows a task.** Replace it with a next-30-days timeline plus a cumulative outflow line, or demote it to an easter egg.
3. **Phone charts clipped with no scroll cue**: `07-spending.phone.de` (heatmap stops mid-June) and `17-inv-analysis.phone.de` (monthly returns stop at June). The most recent months are hidden. **Blocks a task.** Scroll to today, or wrap into rows.
4. **The same quantity shows different numbers on different screens**: fixed costs 1,407.01 € (`11`) vs. 1,423.48 € (`12`); volatility 15 % (`16`) vs. ±17 % (`17`); Vanguard +7.5 % (`15`) vs. +17.2 % (`19`); Income 33,538 € (`01`) vs. 42,058 € in (`02`). **Slows a task.** Label the period or definition next to every figure.
5. **Sankey spends half its width on one 99.6 % source**: `01-overview.desk.en`, "Where the money went". **Slows a task.** Drop the source stage on desktop as the phone version already does, give the room to the outflows, or use a sorted bar list.
6. **Spending sunburst duplicates the bar list and has an unlabelled outer ring**: `07-spending.desk.en`. **Slows a task.** Remove it, or make the bar list expandable into categories.
7. **Area fills on truncated y axes exaggerate change**: `14-networth.desk.en` (axis starts at 25 k), `15-investments.desk.en` (8 k), `19-etf.desk.en` (100). **Slows a task.** Use a zero baseline or a line without fill. For net worth, a stacked area by account would also replace the three share bars.
8. **Shares with unstated denominators**: Housing is 35.6 % on `01-overview.desk.en` and 58.3 % on `07-spending.desk.en`, with the same colour and label. Also, `03-transactions-review.desk.en` shows all-time in/out totals above a filtered list of 8 rows. **Slows a task.** Write "of income / of spending" and compute totals from the visible rows.
9. **Heatmap colour scale has no values and uses a multi-hue ramp with glow**: `07-spending.desk.en`, "Your year in days" ("Less ■■■■■ More"). **Slows a task.** Use a single-hue ramp with bin thresholds in €.
10. **Decoration that carries no data**: the unlabelled tank gauge (`01-overview.desk.en`), 12 identical gold coins per savings plan (`14-networth.desk.en`), and return bars that make +6.7 % vs. +6.3 % look large (`17-inv-analysis.desk.en`). **Cosmetic / slows.** Replace with labelled bullets or plain numbers (for example "money left vs. month left", "27 of 27 payments on time", "+0.4 pt from timing").
