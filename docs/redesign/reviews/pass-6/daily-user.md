# Groschen review: DAILY USER

Role: I use Groschen every day for my own money. I scored only the lines I can judge from task walk-throughs: **3 task efficiency, 4 data presentation, 5 navigation and naming**, plus **7 phone experience** where the phone run of a task showed something the desktop run did not. Every other line is "-".

The step counts start on the screen the app opens on (Overview). One step is one click or tap, or one scroll that is needed to reach the answer. Reading is not a step.

## Task table

| # | Task | Steps desktop | Steps phone | Dead ends | Screenshots used |
|---|------|---------------|-------------|-----------|------------------|
| 1 | "Can I afford 200 € this week?" | **0** to get an answer (hero 5,170.65 €, "about 184.67 € per day"). **1** to check what was subtracted ("14 payments still to come" opens the breakdown) | **0** / **1** (same layout, hero at top) | None. The app answers per day, not per week, so I do the sum myself (7 × 184.67). Nowhere does it say whether the 28-day bar counts as spent days. | 01-overview.desk.en, 01-overview.phone.de, 34-payday-details.desk.en, 34-payday-details.phone.de, 22-settings-hints.desk.en ("Keep aside") |
| 2 | "What did I pay for groceries last month?" | **5**: Spending → period menu → "Last month" → Food & Dining → Groceries, then read "Spent". Shortcut in **3** (Spending → Food & Dining → Groceries), but the Sept bar has no value label, so it only works if hover shows one | **5**: Ausgaben → period → "Letzter Monat" → Essen & Trinken → Lebensmittel. The 3-step shortcut fails on phone: no hover, and the x-axis skips "Okt" and every other month | 1. The bars on 10-drill-category have no amounts. 2. "Top merchants" and "+30 % vs. the period before" are for the whole period, which is easy to misread as monthly. 3. The Food & Dining page lists "Food & Dining 0×" and "Food delivery 0×" rows at 0.00 € (noise). | 07-spending.*, 33-period-menu.desk.en, 33-period-menu.phone.de, 09-drill-group.*, 10-drill-category.* |
| 3 | "Which subscription got more expensive?" | **1** (sidebar "Fixed costs", "What changed" shows Spotify). **2** to see every change ("Show all 8"), because the list badges also show Stadtwerke +7 €, Deutsche Bahn +9 € and Netflix +2 €, and those are hidden in the 4-row preview | **3**: Ausgaben → Fixkosten tab → "Alle 8 zeigen" (plus about 2 scrolls) | 1. Overview "Worth a look" shows "New: Apple" and the August hint, but no price increase, even though "Price changes" is switched on in Settings → Hints. 2. On phone, Fixed costs is not in the bottom bar: it hides as a top tab under "Ausgaben". 3. The "+7.00 €" badges give no date or "per month", so I have to cross-check with "What changed". | 01-overview.desk.en, 11-recurring-list.desk.en, 11-recurring-list.phone.de, 22-settings-hints.desk.en |
| 4 | "Fix a wrongly sorted booking" | **5**: Transactions → search or scroll → click row → pick chip → Save | **6**: Umsätze → scroll → tap row → **scroll inside the dialog** (the current category "Tanken" is below the fold) → pick → Speichern | 1. Overview "Check" ("Groschen sorted 39 transactions on its own. Do the categories look right?") opens "Needs review", which says "These transactions need a category from you" and shows **8** uncategorized rows. So I check uncategorized bookings, not the 39 auto-sorted ones the link promised. 2. "Use this category for every transaction from this merchant" is **on by default**, which is risky for Amazon or PayPal style merchants. 3. There is no visible bulk action for 6 identical "Hofladen Sonnenfeld" rows. | 01-overview.desk.en, 03-transactions-review.*, 02-transactions.*, 05-transactions-edit.desk.en, 05-transactions-edit.phone.de |
| 5 | "How is my depot doing without my own pay-ins?" | **1**: sidebar "Investments" → hero "↑ 504.90 € · +6.7 %" plus "plus 3,000.00 € paid in" | **2**: Vermögen → Depot tab | 1. Net worth shows "↑ 13,592.05 €" with pay-ins mixed in, and the Direkt-Depot card shows only its value. 2. The chart legend "Value without deposits" sits on a line that ends at the full 9,350 € depot value, so the label reads the wrong way round. 3. Analysis: "Your money +6.7 % … with your payments" against "The funds themselves +6.3 %". Which one is "without my pay-ins"? 4. The ETF detail page shows "+1,160.97 € · +17.2 %" (all time, no label) in the same pill style as the period figure "+7.5 % · 474 €" on Investments. | 14-networth.*, 15-investments.*, 17-inv-analysis.*, 19-etf.* |
| 6 | "What is coming off my account before payday?" | **1**: Overview "14 payments still to come · 2,597.40 €" → dialog (10 of 14 visible, scroll for the rest) | **1** + 2 scrolls inside the dialog | 1. Fixed costs → Calendar opens on October with "0.00 € still to come" because all of October is paid, so it looks as if nothing is coming. Payday is 27 Nov, so I need the next-month arrow. 2. Fixed costs "Next up" shows only 3 items. 3. The dialog rows say "In 2 days" with no weekday or date. | 01-overview.*, 34-payday-details.*, 11-recurring-list.desk.en, 12-recurring-calendar.* |

**Bottom line:** tasks 1, 5 and 6 work well: one click or none on both sizes. Tasks 2 and 4 are where daily use slows down: unlabelled bars, period scope, the misrouted "Check" link and a dialog that hides the current category on phone. Task 3 works, but the Overview stays quiet about price rises.

---

## 01 Overview (desk.en, desk.de, phone.de, phone.en) + 31 hidden variant

| Line | Score | Based on |
|---|---|---|
| 1 clarity | - | |
| 2 hierarchy | - | |
| 3 task efficiency | 9 | 01-overview.desk.en: "Available until payday" hero, "5,170.65 €" and "That's about 184.67 € per day" answer task 1 with zero clicks; the "14 payments still to come · 2,597.40 €" link answers task 6 in one click |
| 4 data presentation | 7 | 01-overview.desk.en: the payday timeline dots carry no amounts or dates. The glass/fill graphic next to the hero repeats the number without scale. The Sankey labels are clear and give € and %. |
| 5 navigation & naming | 6 | 01-overview.desk.en: "Worth a look" item "Groschen sorted 39 transactions on its own… Check" leads to a list of 8 "need a category from you" (03). The hint says "Travel" while the category everywhere else is "Leisure & Travel". |
| 6 consistency | - | |
| 7 phone | 8 | 01-overview.phone.de: the hero and the "14 Zahlungen kommen noch" link sit above the fold. The Sankey subtitle "Zeig auf ein Band, um ihm zu folgen" asks for hover on a touch device. |
| 8 accessibility | - | |
| 9 visual craft | - | |

Findings
- **keep** - 01-overview.desk.en, "Available until payday" hero plus per-day figure: answers the main daily question with no click. Do not move it.
- 01-overview.desk.en, "Worth a look" → "Check": the promise ("sorted 39 … do the categories look right?") does not match the target (03: "need a category from you", 8 rows). **slows a task**. Either open a list of the auto-sorted bookings, or change the text to "8 bookings still need a category".
- 01-overview.desk.en, "Worth a look": no "Spotify got more expensive" item, although price changes are detected (11) and switched on (22). **slows a task**. Price rises should outrank "August was 42 % above average".
- 01-overview.desk.en, payday dot strip: the red dots are not labelled. **cosmetic**. Add a tooltip or tap state with the payment name and amount, or drop the dots in favour of the link.
- 01-overview.desk.en, hero: there is no "this week" view. Day-level budgeting is fine, but "184.67 € per day" invites ×7 arithmetic. **cosmetic**. Optionally add "≈ 1,292 € per week".
- 01-overview.phone.de, Sankey subtitle "Zeig auf ein Band": hover wording on a phone. **cosmetic**. Use "Tipp auf ein Band".
- 31-hidden-overview.desk.en: the percentages, savings-rate ring and Sankey band widths stay visible in privacy mode. Not a daily-task issue, noted only.

## 34 Available until payday dialog (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 3 | 9 | 34-payday-details.desk.en: "Balance now − Still going out = Free to spend" in three rows, then the itemised list. That is exactly task 6. |
| 4 | 7 | 34-payday-details.desk.en: rows say "In 2 days" / "In 3 days" with no date. Sparplan rows use the long ISIN names "Sparplan IE00BK5BQT80 Vanguard FTSE All-World U." instead of the short "Vanguard FTSE All-World" used on Investments. |
| 5 | 7 | 34-payday-details.desk.en: the title "Available until payday" and the total row "Free to spend" are two names for one number. "All fixed costs" is a good exit. |
| 7 | 7 | 34-payday-details.phone.de: only 6 of 14 rows fit, and the summary does not stay fixed while scrolling. |

Findings
- **keep** - 34-payday-details.desk.en, the three-line sum: makes the hero number trustworthy.
- 34-payday-details.desk.en, "In 2 days" rows: add the weekday and date ("Sun 1 Nov"). **slows a task**: before payday I want to know whether something hits before or after a specific day.
- 34-payday-details.desk.en, "Sparplan IE00…" rows: use the fund short names from 15-investments. **cosmetic**.
- 34-payday-details.desk.en: sign style differs from 11-recurring-list "Next up", which shows the same Hausverwaltung payment as "1,050.00 €" without a minus. **cosmetic**.

## 02 / 04 / 06 Transactions list, filtered, empty (all variants)

| Line | Score | Based on |
|---|---|---|
| 3 | 7 | 02-transactions.desk.en: the search accepts "merchant, purpose, category or amount", and the segment "All / Needs review / Uncategorized / Income" is one click. There are no month subtotals, so task 2 is not doable here without a filter. |
| 4 | 7 | 02-transactions.desk.en: day headers carry day totals ("-177.49 €"), but single-booking days have none (inconsistent). The refund line "32.00 € of 64.00 € back" with a progress bar is excellent. |
| 5 | 7 | 02-transactions.desk.en: "Needs review 39" and "Uncategorized" are two tabs whose difference is not explained. The sidebar badge "39" also points here. |
| 7 | 7 | 02-transactions.phone.de: the search placeholder is cut ("…Kategorie oder Betr"), and the summary line "42.057,91 € rein / 31.970,76 € raus" wraps onto 2 lines. 06-transactions-empty.phone.de: about 110 px of empty space above the title. |

Findings
- **keep** - 02-transactions.desk.en, refund tracking "39.95 € of 89.90 € back" on the About You row and "Komplett zurückbekommen" with a struck-through amount (02-transactions.phone.de): very useful daily.
- **keep** - 02-transactions.desk.en, the salary note "counts for November 2026": explains why the salary does not count in October.
- 02-transactions.desk.en, "Needs review 39" vs "Uncategorized": rename or merge. **slows a task** (task 4: I did not know which tab to use).
- 02-transactions.desk.en: day totals are missing on single-booking days. **cosmetic**.
- 02-transactions.phone.de, search placeholder truncated. **cosmetic**. Shorten to "Suchen…".
- 06-transactions-empty.phone.de, blank band above "Umsätze". **cosmetic** (the same gap shows in 13-recurring-orbit.phone.de).
- **keep** - 06-transactions-empty.desk.en, "No transactions match" with "Clear filters" next to the count.

## 03 Transactions, Needs review (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 3 | 5 | 03-transactions-review.desk.en: 6 × "Hofladen Sonnenfeld" rows, each needing its own dialog. There is no inline category picker and no "apply to all". |
| 4 | 4 | 03-transactions-review.desk.en: the summary line "All periods · 8 transactions · 110,315.81 € in · 84,234.46 € out". The in/out totals cannot belong to 8 small bookings, and "All periods" contradicts the "Jan – Oct 2026" picker on the same screen. |
| 5 | 5 | 03-transactions-review.desk.en: the tab says "Needs review 39", the banner says "need a category", and the list has 8 rows. Three numbers and two names for one queue. |
| 7 | 7 | 03-transactions-review.phone.de: the gold edge marker and the "Ohne Kategorie" chip read well on phone. |

Findings
- 03-transactions-review.desk.en, the summary totals over "All periods": **blocks a task** for trust. A daily user cannot tell what these sums are. Show the totals of the listed rows only, and keep the period in sync with the picker.
- 03-transactions-review.desk.en, repeated merchant: add "Set Hofladen Sonnenfeld for all 6". **slows a task**.

## 05 Edit transaction dialog (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 3 | 7 | 05-transactions-edit.desk.en: the category chips are grouped and searchable, the current "Fuel" is highlighted, and saving is one click. |
| 4 | - | |
| 5 | 6 | 05-transactions-edit.desk.en: chips read "Housing (general)", "Food & Dining (general)", while 08-spending-group-dialog uses "Housing", "Food & Dining" for the same thing. "Everything with Shell ›" in the footer is ambiguous: filter or rule? |
| 7 | 5 | 05-transactions-edit.phone.de: the current category ("Tanken", under MOBILITÄT) is below the fold. On opening I cannot see what is set now, and must scroll the chip list to find it. |

Findings
- 05-transactions-edit.desk.en, toggle "Use this category for every transaction from this merchant" is **on** by default. **slows a task** (a wrong mass re-sort is hard to undo). Default it to off, or show "affects 13 other bookings" next to it.
- 05-transactions-edit.phone.de: show the current category as a line under the amount ("Kategorie: Tanken ›"), and open the picker on tap. **slows a task**.
- **keep** - 05-transactions-edit.desk.en, the raw bank text box (monospace): it is how I verify a booking.

## 07 Spending + 33 period menu (all variants)

| Line | Score | Based on |
|---|---|---|
| 3 | 7 | 33-period-menu.desk.en: "Last month" is a preset, which is good for task 2. There is no free month picker (for example "August"), so older months need a custom route. |
| 4 | 7 | 07-spending.desk.en: the ranked bars with € and % beat the donut. The donut repeats the list and its outer ring is unlabelled. "Personal · more refunds than spending −162.37 €" is honest. "Your year in days" heatmap: nice, but it does not answer any daily task. |
| 5 | 6 | 07-spending.desk.en: "Your own group" button vs the "Groups" toggle (built-in groups). Two meanings of "group" on one screen. The header toggle "Spending / Income" sits beside the page title "Spending". |
| 7 | 7 | 07-spending.phone.de: the top tabs "Ausgaben / Fixkosten" are the only way to reach fixed costs on phone. The donut takes a full screen before the list. |

Findings
- **keep** - 07-spending.desk.en, the ranked bar list with chevrons into each group.
- 33-period-menu.desk.en: add a month picker (or ‹ › month stepping next to the period button). **slows a task**: "groceries in August" is 5+ steps away.
- 07-spending.desk.en, "Your own group": rename to "Custom group" (as 21-settings-categories already does), or "Own tag", to separate it from the "Groups" toggle. **cosmetic**.
- 07-spending.phone.de, donut above the list: on phone put the list first, or shrink the donut. **slows a task** (2 extra scrolls).

## 08 New group dialog (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 5 | 6 | 08-spending-group-dialog.desk.en: the title "New group", while the page button says "Your own group" and Settings says "Custom groups". Three names for one thing. |
| 3,4,7 | - | Not part of my tasks. |

## 09 Group drill: Food & Dining (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 3 | 6 | 09-drill-group.desk.en: the per-month bars give the shape but no values, so reading "last month" needs hover or a period change. |
| 4 | 6 | 09-drill-group.desk.en: the "Categories" card lists "Food & Dining · 0× 0.00 €" and "Food delivery · 0× 0.00 €", and the chip row repeats "Food & Dining 0", "Food delivery 0". "↑ 35 % vs. the period before" does not say which period. |
| 5 | 8 | 09-drill-group.desk.en: the breadcrumb "‹ SPENDING" and the in-page transaction list with category chips are clear. |
| 7 | 6 | 09-drill-group.phone.de: the x-axis labels only "Jan, Mär, Mai, Jul, Sep", so the last month (Okt) has no label. |

Findings
- 09-drill-group.desk.en: label the bars with values, or at least the last two months. **slows a task** (task 2).
- 09-drill-group.desk.en: hide categories with 0 transactions. **cosmetic**.
- 09-drill-group.desk.en: "vs. the period before" → "vs. Jan – Oct 2025". **cosmetic**.

## 10 Category drill: Groceries (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 3 | 6 | 10-drill-category.desk.en: the Sept bar sits at about 215 € with no number. This is the screen where task 2 should end, and it cannot without a period change. |
| 4 | 7 | 10-drill-category.desk.en: "2,553.63 €, 255.36 € a month on average, 43 transactions, largest 94.95 €" is a good summary. Top merchants with counts ("Lidl · 14×") is useful. |
| 5 | 8 | 10-drill-category.desk.en: the breadcrumb "SPENDING › FOOD & DINING". |
| 7 | 6 | 10-drill-category.phone.de: same unlabelled bars and skipped month labels. "Mit zwei Fingern" zoom is not offered here. |

Findings
- 10-drill-category.desk.en, bar chart: let a click on a bar filter the page to that month, with amount on top. **slows a task**. This would make task 2 three steps on both sizes.
- **keep** - 10-drill-category.desk.en, the "Average 255 €" dashed line.

## 11 Fixed costs, List (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 3 | 8 | 11-recurring-list.desk.en: "What changed" gives task 3 in one click from the sidebar: "Spotify got more expensive: 10.99 € → 11.99 € since 8 Jun 2026, 12.00 € more per year". |
| 4 | 7 | 11-recurring-list.desk.en: "≈ 27.07 € a month" for 4-weekly and yearly items is excellent. The badges "+7.00 €", "+9.00 €", "+2.00 €" have no date and no "/month". The "Running" list order (by monthly cost?) is not stated, so "In 16 days" sits above "In 7 days". |
| 5 | 7 | 11-recurring-list.desk.en: the page title is "Fixed costs" but it includes subscriptions and Netflix/Spotify. Fine for me, but "What changed" talks about "subscriptions". |
| 7 | 6 | 11-recurring-list.phone.de: the "In X days" column is dropped from "Laufend", the name "Hausverwaltung Kr…" is truncated in "Als Nächstes", and reaching it at all takes Ausgaben → Fixkosten. |

Findings
- **keep** - 11-recurring-list.desk.en, "What changed" feed with old → new price and yearly impact. Best "daily user" feature in the app.
- 11-recurring-list.desk.en, price badges: make them sortable or a filter ("Got more expensive (4)"), and add the date in a tooltip. **slows a task**: "Show all 8" is needed to match badges to changes.
- 11-recurring-list.desk.en vs 12-recurring-calendar.desk.en: "Fixed costs per month 1,407.01 €" vs "1,423.48 € fixed costs" for October. **slows a task** (trust). Explain the difference (a variable month vs the average).
- 11-recurring-list.desk.en, the "3 savings plans run along: 1,100.00 € a month. They live under Net worth." banner: **keep**. It explains why Sparen is missing here.

## 12 Fixed costs, Calendar (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 3 | 5 | 12-recurring-calendar.desk.en: opens on the calendar month, with "0.00 € still to come" on 30 Oct. For "before payday" it shows nothing until I click › to November. |
| 4 | 7 | 12-recurring-calendar.desk.en: the "Day by day" side list with "paid" status is good. The chip text is truncated ("Ha… −1,050 €", "Spar… −800 €") and day 1 hides one item as "+1". |
| 5 | 7 | 12-recurring-calendar.desk.en: the legend "Standing order" (teal) and "Salary" (green) look almost the same. |
| 7 | 7 | 12-recurring-calendar.phone.de: dots plus day totals fit well at 390 px. |

Findings
- 12-recurring-calendar.desk.en: open on the pay cycle (27 Oct – 27 Nov), or after the 20th default to the next month. **slows a task** (task 6 dead end).

## 13 Fixed costs, Orbit (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 3 | 3 | 13-recurring-orbit.desk.en: only 4 of 13 dots are labelled, and no amounts are shown. None of my six tasks can be answered here. |
| 4 | 3 | 13-recurring-orbit.phone.de: the dots and labels overlap ("Hausverwaltung Kr…" over other dots), and the centre "1.407 €" is overlapped by a dot. |
| 5 | 5 | 13-recurring-orbit.desk.en: "Orbit" as a tab name says nothing about what I would find there. |

Findings
- 13-recurring-orbit.*: keep it as a fun extra, but it must not sit as an equal third tab beside List/Calendar. **cosmetic**.

## 14 Net worth (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 3 | 7 | 14-networth.desk.en: account cards show balance and share, and Direkt-Depot has a › into Investments. |
| 4 | 6 | 14-networth.desk.en: "↑ 13,592.05 € Jan – Oct 2026" mixes savings, pay-ins and market gain with no split. The chart starts "Dec 25" while the period says Jan – Oct. |
| 5 | 6 | 14-networth.phone.de: the sub-tab is called "Depot", while desktop English calls the same page "Investments" and the hero calls it "Depot value". |
| 7 | 7 | 14-networth.phone.de: the top tabs "Vermögen / Depot" are clear. |

Findings
- 14-networth.desk.en: split the delta into "saved +X · market +504.90 €". **slows a task** (task 5 dead end).
- **keep** - 14-networth.desk.en, the savings plan cards with the coin row per month: payment gaps are easy to see.

## 15 Investments / Depot (desk.en, phone.de) + 32 hidden

| Line | Score | Based on |
|---|---|---|
| 3 | 9 | 15-investments.desk.en: the hero "↑ 504.90 € · +6.7 %" and "Jan – Oct 2026, plus 3,000.00 € paid in" answer task 5 in one click. |
| 4 | 6 | 15-investments.desk.en: the legend "Value without deposits" is drawn on a line in the 8.5–9.6 k € range ending at the full depot value, which reads as "deposits removed" but is not. The monthly gain/loss bars with € labels are very good. |
| 5 | 7 | 15-investments.desk.en: the toggle "Money paid in", the sidebar "Pay-ins" and the hero "paid in" are consistent. The hero label "DEPOT VALUE" against the page title "Investments" is a mix. |
| 7 | 8 | 15-investments.phone.de: hero and gain above the fold, plus the "Mit zwei Fingern vergrößern" hint. |

Findings
- **keep** - 15-investments.desk.en, the hero gain stated with the pay-in amount beside it.
- 15-investments.desk.en, legend "Value without deposits": rename to "Value (pay-ins hidden)" or "Value, gain only". **slows a task** (I doubted the hero number because of it).
- 15-investments.desk.en, holding pill "+7.5 % · 474 €" vs 19-etf.desk.en "+1,160.97 € · +17.2 %" for the same fund: add the scope ("this period" / "since first buy") to both. **slows a task**.

## 16 Forecast (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 4 | 7 | 16-inv-forecast.desk.en: "Bad case 46,246 € / Good case 102,388 €" and "1 in 12 futures ends below what you paid in" are clear. The "Swing 15 % a year" card contradicts 17-inv-analysis.desk.en "±17 % up or down in a normal year". |
| 5 | 7 | 16-inv-forecast.desk.en: the breadcrumb "‹ INVESTMENTS". |
| 3,7 | - | Not part of my tasks. |

Findings
- 16-inv-forecast.desk.en vs 17-inv-analysis.desk.en: volatility is 15 % on one screen and ±17 % on the other. **cosmetic** (trust).

## 17 Analysis (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 4 | 7 | 17-inv-analysis.desk.en: the monthly returns heat strip with numbers is good. The Drawdown callout "−12.7 % (Jun 26)" is clear. |
| 5 | 5 | 17-inv-analysis.desk.en: "Your money … with your payments +6.7 %" vs "The funds themselves … no matter when you paid in +6.3 %". Neither label says "without your pay-ins", which is exactly how I phrase task 5. |

## 18 Pay-ins (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 3 | 7 | 18-inv-payments.desk.en: one-click "Don't count" per row and months collapsed. |
| 4 | 6 | 18-inv-payments.desk.en: "3,600.00 € in the last 12 months" sits next to Investments' "3,000.00 € paid in" (Jan – Oct). The different windows are not explained. |
| 7 | 7 | 18-inv-payments.phone.de: the Sparplan names are truncated ("iShs …") but "Nicht zählen" stays reachable. |

## 19 ETF detail (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 4 | 7 | 19-etf.desk.en: the "Your average 110.71 €" line and purchase dots are excellent. The "+17.2 %" has no time scope. |
| 5 | 7 | 19-etf.desk.en: the tabs "Overview / Analysis / Forecast / Facts" repeat the sidebar sub-items one level deeper. This is understandable, but each has two meanings (depot vs fund). |
| 7 | 7 | 19-etf.phone.de: the "Dein Schnitt 110,71 €" label collides with the price line. |

## 20–27, 30 Settings (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 3 | 7 | 22-settings-hints.desk.en: "Keep aside" lets me hold back a cushion from "Available until payday". Useful for task 1, but it is buried in a tab called "Hints & salary". |
| 5 | 6 | 21-settings-categories.desk.en: "Categorizer: Built-in model" selected with the text "built-in model not found", plus a green "Offline" badge. Contradictory. 23-settings-depot.desk.en: the Settings tab "Investments" shares its name with the main page. 20-settings-bank.phone.de: the tab row is cut ("Hinweise & Gehalt" at the edge) with no scroll cue. |
| 7 | 6 | 20-settings-bank.phone.de: 8 tabs in a horizontal strip, only 2.5 visible. |

Findings
- 22-settings-hints.desk.en, "Keep aside": surface it from the payday dialog (34) as "Keep 0 € aside ›". **cosmetic**.
- 21-settings-categories.desk.en, "built-in model not found" under a selected "Built-in model": **cosmetic**, but it undermines trust in auto-sorting (task 4).
- **keep** - 21-settings-categories.desk.en, "That's you": transfers to your own name count as saved, not spent. This is what makes "Free to spend" sane.
- 27-settings-account.desk.en, "Country: Not chosen" while all formats are already localised. **cosmetic**.
- 30-settings-connect-dialog.desk.en: the only button, "Done, start syncing", is active before a bank is chosen. **cosmetic**.

## 40–42 Wizard and login

Not part of daily use. 42-login.phone.de: the language switch on the login card is handy. No scores.

---

## Cross-screen naming notes
- Fixed costs: sidebar "Fixed costs" (desk) vs only a top tab under "Ausgaben" (phone). The bottom bar has 4 items and none is fixed costs (01-overview.phone.de).
- Depot: "Investments" (sidebar desk.en), "Depot" (phone.de tabs, desk.de sidebar), "DEPOT VALUE" (15 hero), "Direkt-Depot" (14 card), "Investments" (Settings tab).
- Review queue: "Worth a look → Check" (39 sorted), "Needs review 39" (tab), "need a category from you" (banner), 8 rows (list).
- Groups: "Your own group", "New group", "Custom groups", plus the "Groups" toggle for built-in groups.
- Category chips: "Housing (general)" in the edit dialog vs "Housing" in the group dialog.

---

## Top 10

1. **03-transactions-review.desk.en** summary line "All periods · 8 transactions · 110,315.81 € in · 84,234.46 € out": the totals cannot belong to the 8 rows listed, and "All periods" contradicts the "Jan – Oct 2026" picker. **blocks a task** (I cannot trust the numbers). Show the sum of the listed rows and the active period.
2. **01-overview.desk.en "Worth a look → Check"** promises a review of 39 auto-sorted bookings but opens 8 uncategorized ones (03). The badge, tab, banner and list show 39 / 39 / "need a category" / 8. **slows a task** (task 4). Align the wording and the count, or add a real "auto-sorted, please confirm" list.
3. **10-drill-category.desk.en / .phone.de** monthly bars have no values, and a click on a bar does not filter by month. Task 2 takes 5 steps instead of 3. **slows a task**. Label the bars, and make a bar click set the period.
4. **05-transactions-edit.desk.en** "Use this category for every transaction from this merchant" is on by default. **slows a task**: risk of silent mass re-sorting. Default it to off, or show how many bookings it changes.
5. **05-transactions-edit.phone.de** the current category is below the fold of the dialog, so I cannot see what is set without scrolling the chip wall. **slows a task**. Show "Kategorie: Tanken ›" under the amount.
6. **12-recurring-calendar.desk.en** opens on October with "0.00 € still to come" while 14 payments (2,597.40 €) are due before payday. A dead end for task 6. **slows a task**. Open on the pay cycle, or on the next month.
7. **15-investments.desk.en** legend "Value without deposits" on a line ending at the full depot value; **17-inv-analysis.desk.en** "Your money / The funds themselves" never says "without pay-ins". **slows a task** (task 5 doubt). Rename both to plain words.
8. **01-overview.desk.en "Worth a look"** does not show the detected price rises (Spotify, Netflix, Deutsche Bahn, Stadtwerke in 11-recurring-list.desk.en) although "Price changes" is on in 22. **slows a task** (task 3). Prioritise price-rise hints.
9. **11-recurring-list.desk.en "1,407.01 €"** vs **12-recurring-calendar.desk.en "1,423.48 €"** fixed costs, and **16-inv-forecast "Swing 15 %"** vs **17-inv-analysis "±17 %"**: the same idea gets different numbers across screens. **slows a task** (trust). Explain them or unify them.
10. **keep**: **01-overview.desk.en "Available until payday" hero + 34-payday-details "Balance now − Still going out = Free to spend"**, and **11-recurring-list.desk.en "What changed"** (old → new price and yearly impact). Tasks 1, 3 and 6 take 1 click or none because of these. Do not bury them.
