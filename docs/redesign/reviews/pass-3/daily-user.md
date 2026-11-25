# Groschen review, pass 3: daily user

Role: I open this app every day to look after my own money. I judged only the screenshots in `pass-3/`. I looked at every `desk.en` and `phone.de` file, plus `desk.de` for overview and settings. Scores cover the lines this role can judge: **3 task efficiency, 4 data presentation, 5 navigation and naming, 7 phone experience**. Everything else is "-".

Step counting: one step is one click or tap, or one scroll needed to reach the answer. "?" means the screenshots do not show the next screen, so the count is my best reading of what the controls show.

## Task table

| # | Task | Steps desktop | Steps phone | Dead ends | Screenshots used |
|---|------|---------------|-------------|-----------|------------------|
| 1 | "Can I afford 200 € this week?" | **0**. The landing hero answers it: 5,170.65 € left, about 184.67 € a day, 28 days to payday | **0**. Same hero, above the fold | None. One small gap: there is no week figure, so I do the 184.67 × 7 sum in my head | 01-overview.desk.en, 01-overview.phone.de, 22-settings-hints.desk.en ("Keep aside") |
| 2 | "What did I pay for groceries last month?" | **5-6?** Spending → period picker → "Month" → step back to September (control not shown) → Food & Dining → read Groceries in the "Categories" card. Or Spending → Groups/Categories toggle → Categories | **6-7?** Ausgaben tab → period picker → "Monat" → back to Sept (?) → Essen & Trinken → scroll to "Kategorien" | 3. (a) The period menu has no "Last month" option. (b) The Food & Dining "Per month" bars have no values and show the group, not Groceries. (c) The category drill screenshot (10) shows a broken Income drill with 0.00 €, so I cannot confirm that tapping Groceries works | 07-spending, 33-period-menu, 09-drill-group, 10-drill-category (all desk.en + phone.de) |
| 3 | "Which subscription got more expensive?" | **1**. Sidebar "Fixed costs" → "What changed" shows Spotify 10.99 → 11.99. **+1 ("Show all 8")** to see Netflix, Stadtwerke and Deutsche Bahn | **2-3**. Ausgaben → Fixkosten → scroll to "Was sich getan hat" | 2. (a) Spending → "Subscriptions 729.57 €" shows no change information. (b) "What changed" shows only 4 of 8, but the list has 4 "+x €" badges, so Netflix +2.00 is visible only as a badge with no old price or date | 11-recurring-list.desk.en/.phone.de, 07-spending.desk.en |
| 4 | "Fix a wrongly sorted booking" | **5**. Transactions → search → click row → pick a category chip → Save | **6-7**. Umsätze → search → tap row → scroll the chip list → pick → Speichern (the merchant-rule switch is never seen) | 2. (a) "Needs review 39" opens a list of 8 uncategorised rows, but the overview says 39 were *auto-sorted* and should be checked, so the 39 cannot be found. (b) The "every transaction from this merchant" switch is ON by default and sits below the fold on the phone, so a one-off fix silently becomes a rule | 02/03/05-transactions*, 01-overview.desk.en |
| 5 | "How is my depot doing without my own pay-ins?" | **1**. Sidebar "Investments": "504.90 € · +6.7%", "plus 3,000.00 € paid in", chart "Value without deposits" | **2**. Vermögen → Depot tab | 2. (a) The Net worth "Direkt-Depot" card shows only 9,350.57 € with no gain. (b) The ETF detail shows +17.2% with no period while the holding card shows +7.5% for Jan–Oct, so I have two answers for the same fund | 14-networth, 15-investments, 17-inv-analysis, 19-etf (desk.en + phone.de) |
| 6 | "What is coming off my account before payday?" | **1 to see the total** (hero: "14 payments still to come · 2,597.40 €"). For the names: **3-4**. Fixed costs → Calendar → next month (or follow the hero link, destination not captured). "Next up" lists only 3 | **3-5**. Ausgaben → Fixkosten → Kalender → next month → scroll "Tag für Tag" | 3. (a) "Next up" stops at 3 items. (b) The October calendar says "0.00 € still to come", which is true for the month and wrong for my question. (c) The calendar is bound to calendar months and does not mark payday (27 Nov), so I have to work out the window myself. The 14 dots on the hero timeline have no labels | 01-overview.desk.en/.phone.de, 11-recurring-list, 12-recurring-calendar (desk.en + phone.de) |

**Summary:** the "now" questions (1, 5) are excellent at 0-2 steps. The "look back by month" question (2) is the weakest because of missing period presets and an unlabelled monthly chart. The "fix" flow (4) has a risky default. "Before payday" (6) gives the total in one glance, but the itemised list needs a calendar that thinks in calendar months instead of pay periods.

---

## 01-overview (desk.en, desk.de, phone.de, phone.en)

| Line | Score | Based on |
|---|---|---|
| 3 task efficiency | 9 | 01-overview.desk.en: the "Available until payday" hero (5,170.65 €, "about 184.67 € per day", "28 days to payday") answers task 1 with zero clicks |
| 4 data presentation | 7 | 01-overview.desk.en: the payday timeline's 14 red dots have no labels or amounts. The sankey shows "Uncategorized" on both the income side (43.20 €) and the spending side (510.60 €) |
| 5 navigation/naming | 7 | 01-overview.desk.en: the "Worth a look" item "Groschen sorted 39 transactions… Check" leads to a "Needs review" list of 8 (03) |
| 7 phone | 7 | 01-overview.phone.de: the hero fits above the fold. The "Wohin das Geld geflossen ist" sankey drops the income sources (Gehalt, Zinsen) and says "Zeig auf ein Band", a hover instruction on a touch screen |
| 1,2,6,8,9 | - | |

Findings
- **keep**. 01-overview.desk.en, "Available until payday" hero plus "That's about 184.67 € per day". This is the best daily-use element in the app. It checks out against the numbers: Girokonto 7,768.05 − 2,597.40 to come = 5,170.65.
- **keep**. 01-overview.desk.en, "14 payments still to come · 2,597.40 €" link: the total for task 6 in one glance.
- slows a task. 01-overview.desk.en, the timeline dots have no labels. Suggestion: on hover or tap show the payee and amount, or list the next 3-5 under the bar.
- slows a task. 01-overview.desk.en "Income 33,538.60 € / Spending 20,451.45 €" against 02-transactions.desk.en "42,057.91 € in / 31,970.76 € out" for the same Jan–Oct 2026. The two out figures differ by about 11.5k (transfers and savings) and nothing explains why. Suggestion: name the transactions header "money moved in/out incl. transfers", or show the spending figure there too.
- cosmetic. 01-overview.phone.de, sankey hint "Zeig auf ein Band…": on touch it should say "Tipp auf ein Band…".
- **keep**. 01-overview.desk.en, "Worth a look" with the Apple "Show" and "August 42 % above average": useful hints that can be dismissed (the phone has an ×).

## 02 / 04 / 06-transactions (all variants)

| Line | Score | Based on |
|---|---|---|
| 3 | 7 | 02-transactions.desk.en: search, the All / Needs review / Uncategorized / Income tabs and the sort control sit in one row. Day groups carry day totals |
| 4 | 7 | 02-transactions.desk.en: the "counts for November 2026" note on the Nordlicht salary row and the "39.95 € of 89.90 € back" refund progress on About You are excellent. The account column "Girokonto" is repeated on every row and wastes width |
| 5 | 7 | 02-transactions.desk.en: "Needs review 39" next to "Uncategorized". The difference between them is unclear (see 03) |
| 7 | 6 | 02-transactions.phone.de: the account is dropped, which is fine. The search placeholder is cut off ("…oder Betr"). 06-transactions-empty.phone.de: the whole header is pushed about 180 px down, leaving an empty band at the top |

Findings
- **keep**. 02-transactions.desk.en, the salary row note "counts for November 2026 · LOHN/GEHALT 10/2026": it explains why the payday maths works.
- **keep**. 02-transactions.phone.de, "Komplett zurückbekommen" with the struck-through −34,99 € on Amazon: refunds are clear at a glance.
- cosmetic (bug). 06-transactions-empty.phone.de, the page title "Umsätze" starts at about y=190 instead of y=80 like the other phone pages.
- cosmetic. 02-transactions.phone.de, the search placeholder is cut off. Suggestion: shorten it to "Suchen…".
- slows a task. 02-transactions.desk.en, the 1 Sept "Alex Beispiel" transfer appears twice (−800 Girokonto, +800 Extra-Konto) with the category "Savings", inflating the in/out header. Suggestion: show internal transfers as one paired row.

## 03-transactions-review (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 3 | 4 | 03-transactions-review.desk.en: the "Needs review 39" tab opens 8 rows. The 31 auto-sorted ones the overview asked me to check are not visible |
| 4 | 3 | 03-transactions-review.desk.en: the summary "All periods · 8 transactions · 110,315.81 € in · 84,234.46 € out" cannot be the sum of these 8 rows. The period chip still says "Jan – Oct 2026" while the summary says "All periods" |
| 5 | 4 | 03-transactions-review.desk.en: the banner "These transactions need a category from you" conflicts with 01-overview "Groschen sorted 39 transactions on its own. Do the categories look right?" One name is used for two different queues |
| 7 | 6 | 03-transactions-review.phone.de: the same problems. The tab strip and banner take about 330 px before the first row |

Findings
- **blocks a task** (task 4). 03-transactions-review.desk.en, badge 39 vs 8 rows, and the totals belong to another set. Suggestion: split the tabs into "Check guesses (31)" and "No category (8)", or make the badge count what the list shows. Make the in/out line reflect the visible rows.
- slows a task. 03-transactions-review.desk.en, "All periods" against the header picker "Jan – Oct 2026". Suggestion: dim the period picker, or say "ignores period".
- **keep**. 03-transactions-review.desk.en, the yellow left-edge marker on rows that need attention, which also appears in the normal list (Hofladen in 02).

## 05-transactions-edit (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 3 | 6 | 05-transactions-edit.desk.en: chips grouped by area with the current "Fuel" highlighted, plus a search. Picking one is fast. The "Subscriptions" section is cut off under the merchant switch |
| 4 | 8 | 05-transactions-edit.desk.en: the raw bank text block (monospace "VISA Debitkartenumsatz vom 28.10.2026") helps me judge the booking |
| 5 | 7 | 05-transactions-edit.desk.en: "Everything with Shell >" is a good jump |
| 7 | 4 | 05-transactions-edit.phone.de: "Use this category for every transaction from this merchant" is not visible at all above "Alles mit Shell / Speichern" |

Findings
- **blocks a task** (task 4, data safety). 05-transactions-edit.desk.en, the merchant switch is ON by default. On 05-transactions-edit.phone.de it is below the fold. Fixing one Amazon gift booking would recategorise every Amazon order without the user seeing it. Suggestion: default it to OFF, or pin it next to Save with the count ("apply to 23 Shell bookings").
- slows a task. 05-transactions-edit.desk.en, the "SUBSCRIPTIONS" header shows with no chips, hidden by the sticky switch. Suggestion: give the list a bottom padding equal to the sticky area.
- **keep**. 05-transactions-edit.desk.en, the chip grid with coloured group dots and "+ New" per group.

## 07-spending + 33-period-menu (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 3 | 5 | 33-period-menu.desk.en: the options are "Month, Last 30 days, Year to date, Year, Last 12 months, All time". There is no "Last month" and no "Since payday". Task 2 needs extra steps with a control that is not shown |
| 4 | 7 | 07-spending.desk.en: the "Spending breakdown" bars with amount and % are clear. "Personal · more refunds than spending −162.37 €" is honest. The "Your year in days" heatmap is pretty but slow to read |
| 5 | 6 | 07-spending.desk.en: a "Spending / Income" toggle on a page called "Spending". "Your own group" is a vague button label |
| 7 | 6 | 07-spending.phone.de: the "Dein Jahr in Tagen" heatmap is cut off after June, with no visible scroll cue |

Findings
- slows a task (task 2). 33-period-menu.desk.en. Suggestion: add "Last month" and "This pay period (27 Oct – 27 Nov)". Show ‹ › month arrows right in the chip once "Month" is chosen.
- **keep**. 07-spending.desk.en, the Groups / Categories toggle. With a month chosen, Categories answers "groceries last month" without the drill-down.
- cosmetic. 07-spending.phone.de, the heatmap is cut at "Jun". Suggestion: on phone show the last 3 months, or make the grid fit the width.
- cosmetic. 07-spending.desk.en, "Your own group" → "New custom group".

## 08-spending-group-dialog (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 3 | 7 | 08-spending-group-dialog.desk.en: name, icon and chip picking all on one sheet |
| 4 | - | |
| 5 | 7 | 08-spending-group-dialog.desk.en: the explainer "your main budget still counts everything normally" removes the worry about double counting |
| 7 | 6 | 08-spending-group-dialog.phone.de: you can't see how many chips are chosen while scrolling |

- cosmetic. 08 desk.en: the dialog is "New group" here but the page button says "Your own group" and Settings says "Custom groups". Pick one name.

## 09-drill-group (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 3 | 6 | 09-drill-group.desk.en: the Categories card gives "Groceries · 43× 2,553.63 €" for the period. With "Months" bars you cannot get September Groceries without changing the period |
| 4 | 6 | 09-drill-group.desk.en: the "Per month" bars have no values (only an "Average 348 €" line). "Food & Dining · 0×" and "Food delivery · 0×" rows at 0.00 € are noise. "↑ 35% vs. the period before" is a red pill with no reference period |
| 5 | 8 | 09-drill-group.desk.en: the "< SPENDING" breadcrumb and filter chips with counts (Groceries 43) |
| 7 | 7 | 09-drill-group.phone.de: compact. The bar axis labels skip months (Jan, Mär, Mai…) |

Findings
- slows a task (task 2). 09-drill-group.desk.en "Per month". Suggestion: put the value on each bar, or stack the bars by category. Clicking a bar should set the period to that month.
- cosmetic. 09-drill-group.desk.en: hide 0× categories, or fold them into "+2 unused".
- cosmetic. 09-drill-group.desk.en: say which period "↑35%" compares with (Jan–Oct 2025?).
- **keep**. 09-drill-group.desk.en, "Top merchants · 8 of 9" with counts (Lidl · 14×).

## 10-drill-category (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 3 | 2 | 10-drill-category.desk.en: the "Income" drill shows "RECEIVED 0.00 €, 0 transactions" for Jan–Oct 2026 |
| 4 | 2 | Same element. It contradicts 01-overview "Income 33,538.60 €" and the 3,340 € salary rows in 02 |
| 5 | 3 | 10-drill-category.desk.en: the breadcrumb "< INCOME" sits above the title "Income" (the parent equals itself), and the sidebar highlights "Spending" |
| 7 | 4 | 10-drill-category.phone.de: the same 0,00 €, plus two empty states stacked |

Findings
- **blocks a task**. 10-drill-category.desk.en, an Income drill showing 0.00 € while income exists. If this is the screen a category drill opens (Groceries in task 2), I cannot trust it. Suggestion: fix the income filter. An empty result should say *why* (e.g. "Salary is counted under 'Salary', pick it").
- slows a task. 10-drill-category.desk.en, the breadcrumb loop and the sidebar staying on "Spending". Suggestion: "< Spending · Income" or a separate "Income" nav item.

## 11 / 12 / 13 fixed costs (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 3 | 8 | 11-recurring-list.desk.en: "What changed" answers task 3 straight away ("Spotify got more expensive: 10.99 € → 11.99 € since 8 Jun 2026, 12.00 € more per year") |
| 4 | 7 | 11-recurring-list.desk.en: the "+2.00 €" badges on Netflix, Stadtwerke and Deutsche Bahn give no old→new and no date. "Fixed costs per month 1,407.01 €" vs 12-recurring-calendar.desk.en "1,423.48 € fixed costs" for October: two figures on one page family |
| 5 | 6 | 11-recurring-list.desk.en: one thing has four names: "Fixed costs" (nav), "recurring payments" (subtitle), "Running" (section), "Subscriptions" (spending group). "Orbit" says nothing about what the view does |
| 7 | 6 | 11-recurring-list.phone.de: the "Laufend" list drops the "In N days" due column the desktop has. 13-recurring-orbit.phone.de: the planets overlap and cannot be read |

Findings
- **keep**. 11-recurring-list.desk.en, the "What changed" feed (new / back / stopped / pricier), with money per year.
- slows a task (task 3). 11-recurring-list.desk.en, "What changed" shows 4 of 8 and Netflix +2.00 € is not among them. Suggestion: sort price increases first, or show every row that has a "+x €" badge.
- slows a task (task 6). 12-recurring-calendar.desk.en, the header "0.00 € still to come" for October, with payday 27 Nov unmarked. Suggestion: add a "Until payday" range (30 Oct – 27 Nov) that matches the overview's "14 payments · 2,597.40 €", and mark the payday cell.
- slows a task (task 6). 11-recurring-list.desk.en, "Next up" shows only 3 items. Suggestion: "Next up until payday (14) · 2,597.40 €" with an expand option.
- slows a task. 11-recurring-list.phone.de, the next-due date is missing. Suggestion: put "in 2 Tagen" under the amount.
- cosmetic. 13-recurring-orbit.desk.en, only 4 of 13 dots are labelled. Pretty, but no use for a daily task. Hide it on phone, or label it on tap.
- **keep**. 12-recurring-calendar.desk.en, the "Day by day" side list with "paid / standing order" status.
- **keep**. 11-recurring-list.desk.en, "≈ 27.07 € a month" under 4-weekly and yearly items.

## 14-networth (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 3 | 7 | 14-networth.desk.en: the account cards are clickable, but only "Direkt-Depot" has a ">" chevron |
| 4 | 7 | 14-networth.desk.en: "↑ 13,592.05 € Jan – Oct 2026" while the chart starts at "Dec 25". The Direkt-Depot card shows no gain, so for task 5 I have to go one level deeper |
| 5 | 6 | 14-networth.phone.de: the sub-tabs "Vermögen | Depot", while the desktop EN sidebar says "Investments" and the hero says "Depot value". The same thing has three names |
| 7 | 8 | 14-networth.phone.de: clean stacked cards. The savings-plan coin rows read well |

- **keep**. 14-networth.desk.en, "Savings plans" with coin dots per month and "6,750.00 € since August 2024".
- cosmetic. 14-networth.desk.en: add "+504.90 € market gain" to the Direkt-Depot card so task 5 can be answered here.

## 15-investments + 32-hidden-investments (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 3 | 9 | 15-investments.desk.en: the hero "504.90 € · +6.7%" plus "plus 3,000.00 € paid in" answers task 5 in 1 click |
| 4 | 8 | 15-investments.desk.en: the "Value without deposits" line, monthly gain/loss bars with € labels (they add up to about 505 €) and the "Money paid in" toggle. The holding cards "+7.5% · 474 €" and "+2.7% · 31 €" also sum to 505 € |
| 5 | 6 | 15-investments.desk.en: "paid in", "deposits", "Money paid in", and in 18 "Pay-ins" and "Money put in": five names for one idea. DE uses "Einzahlungen" throughout, which is better |
| 7 | 7 | 15-investments.phone.de: the gain/loss bars keep only the "+564 €/−429 €" axis labels and lose the per-month values |

- **keep**. 15-investments.desk.en, the "Value without deposits" chart with the toggle. This is the right default for task 5.
- cosmetic. 15-investments.desk.en, pick one English term ("Pay-ins") everywhere.

## 16-inv-forecast, 17-inv-analysis, 18-inv-payments, 19-etf (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 3 | 7 | 18-inv-payments.desk.en: "Don't count" per pay-in is a one-click fix |
| 4 | 5 | 17-inv-analysis.phone.de "Schwankung ±17 %" vs 16-inv-forecast.phone.de "Schwankung 15 % pro Jahr": the same label with different numbers. 19-etf.desk.en "1,160.97 € · +17.2%" (no period stated) vs 15-investments "+7.5% · 474 €" for the same Vanguard fund |
| 5 | 7 | 19-etf.desk.en: the "< INVESTMENTS" breadcrumb plus Overview / Analysis / Forecast / Facts tabs, which repeat the sidebar's Analysis / Forecast at fund level. That is clear enough |
| 7 | 7 | 16-inv-forecast.phone.de: the long assumption cards push the result (68.412 €) below the first screen |

Findings
- slows a task (task 5). 19-etf.desk.en, "+17.2%" with no time frame, while the page around it is filtered "Jan – Oct 2026". Suggestion: label it "since first purchase", or follow the period picker.
- slows a task. 17-inv-analysis.desk.en "Ups and downs ±17%" vs 16-inv-forecast.desk.en "Swing 15% a year". Suggestion: explain the gap ("this period" vs "long-run"), or show one number.
- cosmetic. 17-inv-analysis.desk.en, the "Your money +6.7%" bar is full width. The bar scale means nothing, so drop the bars.
- **keep**. 18-inv-payments.desk.en, the month accordion with "2 pay-ins · 300.00 €" and "Don't count".
- **keep**. 16-inv-forecast.desk.en, "1 in 12 futures ends below what you paid in": honest wording that a daily user can understand.

## Settings 20-27, 30 (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 3 | 7 | 20-settings-bank.desk.en: "Sync now" and "I logged in to my bank" are first-level buttons |
| 4 | 6 | 22-settings-hints.desk.en: "Nordlicht Software… about 3,180.00 €" vs the 3,340.00 € salary rows in 02. 21-settings-categories.desk.en: "Built-in model" is selected while the subtitle says "(built-in model not found)" and the badge says "Offline" |
| 5 | 7 | 20-settings-bank.desk.en: 8 tabs with clear names. "Hints & salary" is the only place to set "Keep aside" for the payday hero, which is hard to guess |
| 7 | 6 | 20-settings-bank.phone.de: the tab row is cut off at "Hinweise & Gehalt", with no scroll cue |

Findings
- slows a task. 22-settings-hints.desk.en, "Keep aside" shapes the overview hero but lives under "Hints & salary". Suggestion: add a small "Adjust" link on the 01 hero.
- cosmetic. 21-settings-categories.desk.en, the model state contradicts itself. Suggestion: grey out "Built-in model" with "not installed".
- cosmetic. 25-settings-privacy.desk.en, the "Backups never contain the key…" note is repeated under Export.
- cosmetic. 30-settings-connect-dialog.desk.en, "No bank found by that name" shows before anything is typed, and "Done, start syncing" is active with an empty field.
- **keep**. 20-settings-bank.desk.en, the "Bank login needed within 90 days" bar with a plain explanation.

## 31/32 hidden mode, 40-42 wizard/login

| Line | Score | Based on |
|---|---|---|
| 3 | 8 | 31-hidden-overview.desk.en: the eye toggle at the top of the sidebar and phone header. One click |
| 4 | 7 | 31-hidden-overview.desk.en: the amounts are blurred, but the percentages (39 % savings rate, "8.9%" etc.) and the sankey proportions still show. That is acceptable, but worth knowing |
| 5 | - | |
| 7 | 8 | 42-login.phone.de: a simple, centred form with a language switch |

- **keep**. 31-hidden-overview.phone.de, the eye button in the header is always reachable.

---

## Top 10

1. **blocks a task**. `10-drill-category.desk.en/.phone.de`, the Income drill shows **0.00 € / 0 transactions** while 01-overview reports 33,538.60 € income. The breadcrumb "< INCOME" loops onto itself and the sidebar stays on "Spending". A daily user stops trusting the category drill-downs, and task 2 depends on them.
2. **blocks a task**. `05-transactions-edit.desk.en/.phone.de`, "Use this category for every transaction from this merchant" is **ON by default** and **not visible on the phone** above "Speichern". A one-off fix silently rewrites every booking from that merchant. Default it to off, or show it next to Save with a count.
3. **blocks a task**. `03-transactions-review.desk.en`, the "Needs review 39" badge opens 8 rows. The banner ("need a category") contradicts the overview ("sorted 39 on its own, do they look right?"), and the "110,315.81 € in / 84,234.46 € out" summary does not belong to these rows. Split the queue into "Check guesses" and "No category".
4. **slows a task**. `33-period-menu.desk.en/.phone.de`, there is no "Last month" and no "This pay period" preset, so "groceries last month" takes 5-7 steps. Add both, and put ‹ › month arrows in the chip.
5. **slows a task**. `12-recurring-calendar.desk.en` + `11-recurring-list.desk.en`, "before payday" has no matching view. The calendar says "0.00 € still to come" for October, "Next up" lists only 3, and payday 27 Nov is not marked. Add an "Until payday" range that equals the hero's "14 payments · 2,597.40 €".
6. **slows a task**. `09-drill-group.desk.en`, the "Per month" bars have no values and show the group, not its categories, and clicking a bar does not set the month. Label the bars and let a click filter to that month.
7. **slows a task**. `19-etf.desk.en` "+17.2% · 1,160.97 €" (no period) vs `15-investments.desk.en` "+7.5% · 474 €" for the same fund. `17-inv-analysis` "±17 %" vs `16-inv-forecast` "Swing 15 %" use the same label for different numbers. Label the time frames.
8. **slows a task**. Naming drift: Fixed costs / recurring payments / Running / Subscriptions (11, 07), and Pay-ins / paid in / deposits / Money paid in / Money put in (15, 18). Investments / Depot / Direkt-Depot are also used across 14/15 and the DE nav. Pick one term per concept.
9. **slows a task**. `01-overview.desk.en` "Spending 20,451.45 €" vs `02-transactions.desk.en` "31,970.76 € out" for the same period, with no explanation. Mark transfers and savings in the transactions header, or show both.
10. **keep**. `01-overview.desk.en` "Available until payday 5,170.65 € · about 184.67 € per day" (task 1 in 0 steps), `15-investments.desk.en` "504.90 € · +6.7% … plus 3,000.00 € paid in" with "Value without deposits" (task 5 in 1 step), and `11-recurring-list.desk.en` "What changed" (task 3 in 1 step). These three are why the app works day to day. Don't dilute them.
