# Groschen, pass 8: DAILY USER review

Role: I use this every day for my own money. I judge from the screenshots only. My scores cover **3 task efficiency, 4 data presentation and 5 navigation and naming**. I also score 1 (clarity of purpose) and 7 (phone experience) where a task depends on them. Every other line is "-".

Step counting: one step is one click or tap that changes the screen or opens a menu or dialog. Reading or scrolling on the same screen counts 0. The starting point is the Overview after login.

## Task table

| # | Task | Steps desktop | Steps phone | Dead ends | Screenshots used |
|---|------|---------------|-------------|-----------|------------------|
| 1 | "Can I afford 200 € this week?" | **0**: the hero reads 5,170.65 € and about 184.67 € per day. Optional 1 more step opens the breakdown. | **0**: same hero, above the fold | None. One gap: there is no "per week" or "by Friday" figure, so I multiply 184.67 × 7 in my head. | 01-overview.desk.en, 01-overview.phone.de, 34-payday-details.* |
| 2 | "What did I pay for groceries last month?" | **5**: Spending, then the period chip, then "Last month", then Food & Dining, then Groceries. The Categories toggle can replace Food & Dining. | **5**: Ausgaben, then the period chip, then "Letzter Monat", then Essen & Trinken, then Lebensmittel | (a) If I skip the period change, the Groceries page shows Jan–Oct and the "Sept" bar has **no value label**. I can only estimate about 215 €. (b) The Overview Sankey stops at the group level (Food & Dining) and never shows Groceries. (c) Food & Dining lists two dead rows, "Food & Dining 0× 0.00 €" and "Food delivery 0× 0.00 €". | 07-spending.*, 33-period-menu.*, 09-drill-group.*, 10-drill-category.* |
| 3 | "Which subscription got more expensive?" | **1**: Fixed costs, where "What changed" shows "Spotify got more expensive". **2** to see every price rise (+ "Show all 8"). | **2**: Ausgaben, then the Fixkosten tab | (a) "Subscriptions" in the Spending breakdown sounds like the right place, but it shows only spend. (b) "Worth a look" on the Overview shows "New: Apple" but no price rise. (c) The Running list has four price badges (+7, +9, +2, +1 €), while "What changed" only shows Spotify above the fold. Netflix +2 € and Deutsche Bahn +9 € are hidden behind "Show all 8". | 01-overview.*, 07-spending.*, 11-recurring-list.desk.en, 11-recurring-list.phone.de |
| 4 | "Fix a wrongly sorted booking" | **4**: Transactions, then the row, then the category chip, then Save. Add 1 step to search when the booking is old. | **4** plus scrolling or typing in "Kategorie suchen", because the current category is below the fold | (a) The "Needs review 39" badge leads to "8 transactions" titled "need a category from you". The 39 auto-sorted bookings that the Overview asks me to "Check" are not visible as such. (b) "Use this category for every transaction from this merchant" is **on by default**. Fixing a single wrong booking (for example one Amazon order) silently recategorises the whole merchant. | 02-transactions.*, 03-transactions-review.*, 05-transactions-edit.*, 01-overview.desk.en "Worth a look" |
| 5 | "How is my depot doing without my own pay-ins?" | **1**: Investments in the sidebar. The hero reads "↑ 504.90 € · +6.7%" and "plus 3,000.00 € paid in". **2** with Analysis for "The funds themselves +6.3%". | **2**: Vermögen, then the Depot sub-tab. **3** with Analyse. | (a) There are three different "gain" numbers for the same money: +6.7 % (hero), +6.3 % (Analysis) and, on the ETF page, "+1,160.97 € · +17.2%" against "+7.5% · 474 €" on the holding card. None of them says which time base it uses. (b) "Value without your pay-ins" (legend) ends near 9.4k, about the same as the real 9,350.57 €, so I can't tell what the line subtracts. | 15-investments.*, 17-inv-analysis.*, 19-etf.desk.en, 14-networth.* |
| 6 | "What is coming off my account before payday?" | **1**: the link "14 payments still to come · 2,597.40 €" in the hero opens the list | **1**: same link, then scroll | (a) Fixed costs, Calendar opens on October with "0.00 € still to come", so my natural second guess shows nothing. (b) Fixed costs "Next up" shows only 3 items and leaves out the savings transfers (Sparen 800 €, plans 300 €), which do leave the account. (c) The dialog rows say only "In 2 days" with no weekday or date. | 01-overview.*, 34-payday-details.desk.en, 34-payday-details.phone.de, 11-recurring-list.*, 12-recurring-calendar.* |

**Summary:** tasks 1, 3, 5 and 6 are fast (0–2 steps). Task 2 is the slowest, at 5 steps and one number I can only estimate. Task 4 is quick, but a risky default and a confusing "39 vs 8" count get in the way.

---

## 01 Overview (desk.en, desk.de, phone.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 9 | 01-overview.desk.en: the "Available until payday 5,170.65 €" hero answers the daily question first |
| 2 hierarchy | - | |
| 3 task efficiency | 9 | 01-overview.desk.en: the "14 payments still to come · 2,597.40 € >" link answers task 6 in one click; the hero answers task 1 at 0 clicks |
| 4 data presentation | 7 | 01-overview.desk.en: "That's about 184.67 € per day" is good. The 28-cell payday strip has unlabeled red dots: I can't tell which day holds which payment without opening the dialog. The Sankey ends at group level. |
| 5 navigation and naming | 7 | 01-overview.desk.en: "Worth a look" with Check/Show is clear. "Groschen sorted 39 transactions … Check" leads to a list that says 8 (see 03). |
| 6 consistency | - | |
| 7 phone experience | 8 | 01-overview.phone.de: hero, "14 Zahlungen kommen noch" link and hints all fit above the bottom bar; the dismiss "×" buttons have their own row |
| 8 accessibility | - | |
| 9 visual craft | - | |

Findings
- **keep**: 01-overview.desk.en / phone.de, the "Available until payday" hero with the per-day figure. It answers "can I afford it" at 0 steps.
- **keep**: 01-overview.desk.en, the "14 payments still to come · 2,597.40 €" link right under the strip. It is the fastest route to task 6.
- 01-overview.desk.en, payday strip. The dots mark payment days but carry no amount or name. Severity: slows a task. Suggestion: show a tooltip or tap label (name and amount) on each dot, and label the dates under the strip at least weekly.
- 01-overview.desk.en, hero. There is no "this week" figure. For "can I afford 200 € this week" I multiply in my head. Severity: cosmetic. Suggestion: a secondary line such as "≈ 1,290 € per week" or "until Sunday: …".
- 01-overview.desk.en, "Worth a look". The price-change hints (Spotify, Netflix, DB) that Fixed costs knows about do not appear here. Only "New: Apple" shows. Severity: slows a task (task 3). Suggestion: give price rises the same priority as new subscriptions.
- 01-overview.desk.en, "Where the money went" Sankey. The bands stop at group level (Food & Dining), so Groceries can't be read here. Severity: cosmetic, because the click-through exists.

## 34 Payday details dialog (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 3 task efficiency | 9 | 34-payday-details.desk.en: Balance now, then Still going out, then Free to spend, then an itemised list, all in one dialog |
| 4 data presentation | 7 | 34-payday-details.desk.en: the rows read "In 2 days" / "In 3 days" with no date or weekday; long Sparplan names wrap to two lines ("Sparplan IE00BK5BQT80 Vanguard FTSE All-World U.") |
| 5 navigation and naming | 8 | 34-payday-details.desk.en: the "All fixed costs" button jumps on correctly |
| 7 phone experience | 7 | 34-payday-details.phone.de: about 6 of 14 rows show before scrolling; the "In 2 Tagen" label sits above the name, which works on a narrow screen |

Findings
- **keep**: 34-payday-details.desk.en, the three-line sum (Balance now − Still going out = Free to spend). The arithmetic is transparent.
- **keep**: the dialog includes standing orders (Sparen 800 €, Sparplan) because they leave the account. This is correct for "before payday".
- 34-payday-details.desk.en, rows. "In 2 days" with no absolute date. On a Friday I want to know whether it lands on Sunday or Monday. Severity: slows a task. Suggestion: "Sun 1 Nov · in 2 days".
- 34-payday-details.desk.en, rows. The ISIN-laden plan names ("Sparplan IE00BKM4GZ66 iShs Core MSCI EM IMI U.ET") are bank strings. The holding cards elsewhere use "iShares Core MSCI EM IMI". Severity: cosmetic. Suggestion: reuse the clean fund name.
- 34-payday-details.*, there is no group subtotal (fixed costs versus savings transfers). Severity: cosmetic.

## 02 / 04 / 06 Transactions: list, filtered and empty (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 3 task efficiency | 8 | 02-transactions.desk.en: search covers "merchant, purpose, category or amount"; the summary line "297 transactions · 42,057.91 € in · 31,970.76 € out" turns any search into a total |
| 4 data presentation | 7 | 02-transactions.desk.en: day headers carry day totals (−177.49 €), refund links read "Money back for About You, 3 Sept", and strike-through amounts mark a full refund. Day totals are missing on income-only days (Tuesday 27 October), and some multi-row days have none either. |
| 5 navigation and naming | 6 | 02-transactions.desk.en: the tabs are "All / Needs review 39 / Uncategorized / Income". The difference between "Needs review" and "Uncategorized" is unclear (see 03). |
| 7 phone experience | 7 | 02-transactions.phone.de: the search placeholder is cut off ("…Kategorie oder Betr"), and "31.970,76 € raus" wraps to its own line. The rows are clean, with the category pill under the name. |

Findings
- **keep**: 02-transactions.desk.en, the summary line with in/out totals. Searching "Lidl" or a category gives an instant monthly total. This is a second route for task 2.
- **keep**: 02-transactions.desk.en, the refund chain ("32.00 € of 64.00 € back" with a progress bar). It is very readable.
- **keep**: 06-transactions-empty.desk.en, "No transactions match" with "Clear filters" next to the count.
- 02-transactions.phone.de, search placeholder. It is cut off at "Betr". Severity: cosmetic. Suggestion: shorten it to "Suchen…" on phone.
- 02-transactions.desk.en, the account column ("Girokonto") repeats on every row although nearly all rows are Girokonto. Severity: cosmetic. Suggestion: show it only when it differs from the main account.
- 04-transactions-filtered.desk.en, the "Supermarkt" search. The Groceries category name is English in the UI while the bank text is German, so it is unclear whether "Supermarkt" or "Groceries" matches. Severity: cosmetic.

## 03 Transactions: Needs review (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 3 task efficiency | 6 | 03-transactions-review.desk.en: 7 of the 8 rows are uncategorized, 6 of them the same merchant "Hofladen Sonnenfeld"; there is no bulk "set all Hofladen rows" from this list |
| 4 data presentation | 6 | 03-transactions-review.desk.en: the tab badge says "Needs review 39", the list says "8 transactions", and the summary says "All periods" while the period chip still says "Jan – Oct 2026" |
| 5 navigation and naming | 5 | 03-transactions-review.desk.en: the banner "These transactions need a category from you" describes "Uncategorized", yet the tab is "Needs review"; the 39 auto-sorted bookings the Overview asks me to check are not identifiable |
| 7 phone experience | 7 | 03-transactions-review.phone.de: the banner and rows fit well; the "Zu prüfen 39" chip is readable |

Findings
- 03-transactions-review.desk.en, the "Needs review 39" badge against the "8 transactions" list. The count does not match what I see. I can't tell whether 31 are hidden, done or elsewhere. Severity: slows a task (task 4). Suggestion: make the badge equal the list count. Alternatively, split the list into "Needs a category (8)" and "Sorted by Groschen, please confirm (31)" with a "Looks right" button per row.
- 03-transactions-review.desk.en, the period line "All periods" while the header picker shows "Jan – Oct 2026". The two disagree. Severity: cosmetic. Suggestion: grey out the picker or say "Needs review ignores the period".
- 03-transactions-review.desk.en, the six "Hofladen Sonnenfeld" rows. Severity: slows a task. Suggestion: group them by merchant ("Hofladen Sonnenfeld · 6 bookings · Set category").

## 05 Edit transaction (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 3 task efficiency | 7 | 05-transactions-edit.desk.en: the category chips are grouped and the current one (Fuel) is highlighted; "Search categories" sits at the top; Save is a single button |
| 4 data presentation | 8 | 05-transactions-edit.desk.en: the raw bank text appears in monospace ("VISA Debitkartenumsatz vom 28.10.2026"), useful for judging what the booking really is |
| 5 navigation and naming | 6 | 05-transactions-edit.desk.en: "Use this category for every transaction from this merchant" is switched on by default; "Everything with Shell >" is a clear exit |
| 7 phone experience | 6 | 05-transactions-edit.phone.de: the current category "Tanken" (Mobilität) is below the fold, so the highlighted state isn't visible when the dialog opens; the toggle label wraps over two lines and pushes the toggle under it |

Findings
- 05-transactions-edit.desk.en / phone.de, the merchant-wide toggle is ON by default. A daily "this one booking is wrong" fix (an Amazon gift or a one-off at a supermarket) changes every past and future booking from that merchant. Severity: blocks a task. The task as meant, fixing one booking, needs an extra un-toggle the user may not notice. Suggestion: default to OFF, or set it ON only when the merchant has more than one uncategorized booking. After saving, offer "Also apply to 5 other Shell bookings?".
- 05-transactions-edit.phone.de, current category off-screen. Severity: slows a task. Suggestion: pin a "Now: Tanken" chip next to the search field, or scroll to the selected group on open.
- **keep**: 05-transactions-edit.desk.en, the grouped chips with "+ New" per group, and the raw bank memo block.

## 07 / 33 Spending and the period menu (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 8 | 07-spending.desk.en: "Spending breakdown · 2,045.14 € a month on average · most on Housing (58%)" |
| 3 task efficiency | 6 | 33-period-menu.desk.en: "Last month" sits two clicks away inside the date chip; the default is Year to date, so every monthly question costs 2 extra clicks |
| 4 data presentation | 7 | 07-spending.desk.en: the list gives amount, % and bar per group. The "Personal · more refunds than spending −162.37 €" row is honest but odd in a spending list. "Your year in days" is pretty, but its colours can't be read as amounts. |
| 5 navigation and naming | 6 | 07-spending.desk.en: "Subscriptions" (a spending group, 729.57 €) and "Fixed costs" (a sub-page) overlap, and price changes live only under Fixed costs; the chip "Jan – Oct 2026" maps to the menu item "Year to date", which uses different words for the same thing |
| 7 phone experience | 7 | 07-spending.phone.de: the "Ausgaben | Fixkosten" tabs at the top are clear; the year heat-map wraps to two half-years and stays readable |

Findings
- 33-period-menu.desk.en, there is no month stepper. Going from "Last month" to "the month before" needs the menu again. Severity: slows a task. Suggestion: add ‹ › arrows next to the period chip when a month is selected, as the 12-recurring-calendar header already does.
- 33-period-menu.desk.en, label mismatch: the chip says "Jan – Oct 2026" and the ticked item says "Year to date". Severity: cosmetic. Suggestion: the chip could read "Year to date · Jan – Oct".
- 07-spending.desk.en, "Subscriptions" row. Clicking it is where I first looked for "which subscription got more expensive". Severity: slows a task (task 3). Suggestion: on the Subscriptions drill page, show the price-change badges from Fixed costs, or link "Price changes →".
- **keep**: 07-spending.desk.en, the "Groups / Categories" toggle. It lets me reach Groceries without the group step.

## 08 New group dialog (desk.en)

| Line | Score | Based on |
|---|---|---|
| 5 navigation and naming | 7 | 08-spending-group-dialog.desk.en: the intro says what a custom group is for ("for a car, a flat you rent out or a holiday") |

Finding: not part of my daily tasks. The category list repeats the edit dialog's chips, which is consistent. **keep**.

## 09 / 10 Drill-down: group and category (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 3 task efficiency | 6 | 10-drill-category.desk.en: Groceries shows "2,553.63 €" for Jan–Oct; the per-month answer requires the period menu again or estimating a bar |
| 4 data presentation | 6 | 10-drill-category.desk.en: the "Per month" bars have no value labels (only the axis and "Average 255 €"); 09-drill-group.desk.en lists "Food & Dining 0× 0.00 €" and "Food delivery 0× 0.00 €" |
| 5 navigation and naming | 8 | 10-drill-category.desk.en: the breadcrumb "Spending > Food & Dining" plus title "Groceries" makes it clear where I am |
| 7 phone experience | 6 | 10-drill-category.phone.de: the bar chart x-axis shows only "Jan, Mär, Mai, Jul, Sep", so October's bar has no label at all |

Findings
- 10-drill-category.desk.en / phone.de, unlabeled monthly bars. "What did I pay last month" is right there as a bar but can't be read. Severity: blocks a task when the user does not think to change the period first. Suggestion: print the value on or above each bar, or show the latest full month as a stat ("September: 214.80 €") next to "Spent".
- 09-drill-group.desk.en, rows with zero values. "Food & Dining 0×" and "Food delivery 0×" add noise. Severity: cosmetic. Suggestion: hide categories with 0 bookings in the period.
- 10-drill-category.phone.de, the axis skips every other month and the last bar is unlabelled. Severity: slows a task. Suggestion: label every bar with a 3-letter month, or at least the first and last.
- **keep**: 10-drill-category.desk.en, the "Top merchants" list (Lidl 14× 774.72 €, 30.3 %), the "↑ 30% vs. the period before" chip and "largest 94.95 €". These are the useful supporting facts.

## 11 / 12 / 13 Fixed costs: list, calendar and orbit (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 8 | 11-recurring-list.desk.en: "Fixed costs, on average per month 1,407.01 €" with "Next up" beside it |
| 3 task efficiency | 8 | 11-recurring-list.desk.en: the "What changed" card puts "Spotify got more expensive: 10.99 € → 11.99 € since 8 Jun 2026, 12.00 € more per year" at the top (task 3 in 1 click) |
| 4 data presentation | 7 | 11-recurring-list.desk.en: the badges "+7.00 €", "+9.00 €", "+2.00 €", "+1.00 €" in Running give no date or old price; the Running list is sorted by amount, so the "In 2 days / In 16 days / In 7 days" column jumps; 12-recurring-calendar.desk.en shows "1,423.48 € fixed costs" against 1,407.01 € on List |
| 5 navigation and naming | 6 | 12-recurring-calendar.desk.en: the calendar opens on October with "0.00 € still to come", so the useful month is one click away; 13-recurring-orbit.desk.en "Your month in orbit" names only 4 of 13 dots |
| 7 phone experience | 7 | 11-recurring-list.phone.de: Fixkosten is reached via the Ausgaben tab and then the "Fixkosten" sub-tab; the badges fit next to the names; "Stadtwerke Muench…" is truncated by the badge |

Findings
- **keep**: 11-recurring-list.desk.en, the "What changed" card. It is plain-language and dated, with a yearly effect ("12.00 € more per year"). It is the best answer to task 3 in the app.
- 11-recurring-list.desk.en, "What changed" shows 4 of 8. Netflix (+2 €) and Deutsche Bahn (+9 €) price rises are behind "Show all 8", while "New: Apple 2.99 €" takes a slot. Severity: slows a task. Suggestion: rank price rises above "new" and "back", or add a filter chip "Price changes (4)".
- 11-recurring-list.desk.en, the "+7.00 €" badges. They have no "since" date. Severity: cosmetic. Suggestion: add a tooltip or tap label "since Aug: 74 → 81 €".
- 12-recurring-calendar.desk.en / phone.de, the calendar opens on the current month even when everything is paid ("0.00 € still to come"). For "before payday" I need November, and it shows the whole month, not the cut at the 27th. Severity: slows a task (task 6, a dead end on the second route). Suggestion: after the last expected payment of the month, open on next month and draw a "Payday 27 Nov" marker.
- 12-recurring-calendar.desk.en, two totals (1,423.48 € this month against 1,407.01 € average) without a word on the difference. Severity: cosmetic. Suggestion: label them "this October" and "average".
- 11-recurring-list.desk.en, "Next up" shows 3 items, without the 800 € savings transfer that the payday dialog counts. The two "upcoming" lists disagree. Severity: slows a task. Suggestion: link "Next up" to the same 14-item list, or add "+ 1,100 € savings plans".
- 13-recurring-orbit.desk.en / phone, no daily task uses it. Most dots are unlabeled, and amounts are not shown. Severity: cosmetic. Suggestion: keep it as the third tab but never as a default.
- **keep**: 11-recurring-list.desk.en, the savings-plan footer "3 savings plans run along: 1,100.00 € a month. They live under Net worth." It explains why they are not counted here.

## 14 Net worth (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 4 data presentation | 7 | 14-networth.desk.en: "44,931.92 € ↑ 13,592.05 €" mixes savings and market gains in one number; the account cards have share bars (17 / 62 / 21 %) |
| 5 navigation and naming | 7 | 14-networth.phone.de: the sub-tabs are "Vermögen | Depot"; on the Depot screen (15-investments.phone.de) the tabs change to "Depot | Analyse | Prognose | Einzahlungen" and the "Vermögen" tab is gone, leaving only the "‹ Vermögen" crumb |
| 7 phone experience | 7 | 14-networth.phone.de: the account cards stack well; the long savings-plan cards ("Vanguard FTSE All-W…") are truncated |

Findings
- 14-networth.phone.de against 15-investments.phone.de, the sub-tab row changes its content between sibling screens. Severity: slows a task (getting back). Suggestion: one stable row, "Vermögen | Depot | Analyse | Prognose | Einzahlungen", scrollable.
- **keep**: 14-networth.desk.en, the "Savings plans" cards with coin rows and "since August 2024" totals.

## 15 / 16 / 17 / 18 / 19 Investments, Forecast, Analysis, Pay-ins, ETF (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 8 | 15-investments.desk.en: "Depot value on 30 Oct 2026 · 9,350.57 € · ↑ 504.90 € · +6.7% · Jan – Oct 2026, plus 3,000.00 € paid in" |
| 3 task efficiency | 8 | 15-investments.desk.en: task 5 answers in 1 click from the sidebar ("Investments"); 17-inv-analysis.desk.en gives "The funds themselves +6.3%" |
| 4 data presentation | 5 | 19-etf.desk.en "↑ 1,160.97 € · +17.2%" against 15-investments.desk.en holding card "+7.5% · 474 €" for the same Vanguard fund, neither saying "since purchase" or "this period"; the 15-investments legend "Value without your pay-ins" line ends near the actual value; 17-inv-analysis.desk.en "About what the funds themselves made." is a vague one-liner |
| 5 navigation and naming | 6 | desktop sidebar "Investments", phone tab "Depot" and page title "Depot", the same thing under two names; "Pay-ins" (18) against "Money paid in" toggle (15) against "Paid in" legend (16) |
| 7 phone experience | 7 | 15-investments.phone.de: the hero, chart and holdings stack well; "Mit zwei Fingern vergrößern" is a correct phone hint; the monthly bars below the chart have only "+564 €" and "−429 €" axis labels |

Findings
- 19-etf.desk.en against 15-investments.desk.en, the gain figures for the same fund disagree (+17.2 % / 1,160.97 € against +7.5 % / 474 €) with no time base. Severity: slows a task (task 5). I stop trusting the numbers. Suggestion: suffix every gain chip with its base ("since first buy" or "Jan – Oct").
- 15-investments.desk.en, the legend "Value without your pay-ins". It is unclear what is subtracted, since the line ends at about the depot value. Severity: slows a task. Suggestion: rename it "Value if you had paid nothing in since Jan", or plot "pay-ins" as a second line and the gap as the gain.
- 17-inv-analysis.desk.en, "Your money +6.7% · with your payments" against "The funds themselves +6.3% · no matter when you paid in". This is the right concept. The footnote "About what the funds themselves made." should say what it means ("Your timing added +0.4 points"). Severity: cosmetic.
- Naming: "Investments" (desk nav) against "Depot" (phone tab and title). Severity: cosmetic. Suggestion: use one term; "Depot" fits the German audience and works in English too.
- **keep**: 15-investments.desk.en, the monthly gain/loss bars with values (+497 €, −429 €). They are the clearest "without pay-ins" view in the app.
- **keep**: 18-inv-payments.desk.en, pay-ins by month with a "Don't count" action per row and "3,600.00 € in the last 12 months".
- **keep**: 16-inv-forecast.desk.en, "24,312 € more than the 44,100 € you'd have paid in" and "1 in 12 futures ends below what you paid in". It is honest and concrete.

## 20–28 Settings (desk.en, viewed 21, 22)

| Line | Score | Based on |
|---|---|---|
| 5 navigation and naming | 6 | 21-settings-categories.desk.en: "Categorizer" has "Built-in model" selected while the line beneath says "(built-in model not found)" and a badge says "Offline"; 22-settings-hints.desk.en "Hints & salary" is an odd pairing for a tab |

Findings
- 21-settings-categories.desk.en, the categorizer state contradicts itself. Severity: cosmetic for daily use.
- **keep**: 22-settings-hints.desk.en, "Keep aside: subtracted from Available until payday". It is the right knob for task 1, but nothing on the Overview hero points to it. Suggestion: a small "Adjust" link on the hero.
- **keep**: 22-settings-hints.desk.en, "Count end-of-month salary for the next month", shown in the list as "counts for November 2026" (02-transactions.desk.en). This is very good for payday logic.

## 31 / 32 Hidden mode, 40–42 Wizard and login

Not part of my daily tasks. Not scored.

---

## Top 10

1. **05-transactions-edit.desk.en / phone.de**: "Use this category for every transaction from this merchant" is ON by default. Fixing one wrong booking recategorises the whole merchant. Default it to OFF, or ask after saving. *(blocks a task)*
2. **10-drill-category.desk.en / phone.de**: the "Per month" bars carry no values, so "groceries last month" can't be read without 2 extra clicks in the period menu, and the phone axis leaves October unlabeled. Label the bars or add a "last full month" stat. *(blocks a task)*
3. **03-transactions-review.desk.en**: "Needs review 39" opens "8 transactions … need a category from you". The 39 auto-sorted bookings the Overview asks me to "Check" can't be found. Make the counts match and split "needs category" from "please confirm". *(slows a task)*
4. **19-etf.desk.en against 15-investments.desk.en**: the same fund shows +17.2 % / 1,160.97 € and +7.5 % / 474 €, with no time base on either. Label every gain chip with its base. *(slows a task)*
5. **12-recurring-calendar.desk.en / phone.de**: the calendar opens on a fully paid October ("0.00 € still to come"). For "before payday", open on the next due month and mark payday (27 Nov). *(slows a task)*
6. **11-recurring-list.desk.en**: "What changed" shows only Spotify among 4 price rises. Netflix +2 € and DB +9 € hide behind "Show all 8", and the Overview's "Worth a look" shows no price rise at all. Rank price changes first. *(slows a task)*
7. **33-period-menu.desk.en**: there is no ‹ › month stepper, and the default is Year to date, so every monthly question costs 2 clicks and month-to-month comparison costs 2 more. Add arrows beside the period chip. *(slows a task)*
8. **01-overview.desk.en / 34-payday-details.desk.en**: the payday strip dots have no labels and the dialog rows say only "In 2 days". Add the weekday and date ("Sun 1 Nov"). Keep the hero and the "14 payments still to come" link exactly as they are. *(slows a task / keep)*
9. **Naming across 15-investments.desk.en / 15-investments.phone.de / 14-networth.phone.de / 07-spending.desk.en**: "Investments" against "Depot", a sub-tab row that changes between Vermögen and Depot, and the "Subscriptions" group against "Fixed costs" with price changes only on the latter. Unify the terms and the tab row. *(slows a task)*
10. **11-recurring-list.desk.en "Next up" against 34-payday-details.desk.en**: 3 upcoming items against 14, because the savings transfers are left out. Two "what's coming" answers disagree. Link Next up to the payday list or add "+ 1,100 € savings plans". *(slows a task)*
