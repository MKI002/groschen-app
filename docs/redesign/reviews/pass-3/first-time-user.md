# Groschen, pass 3: first-time user review

**Role:** first-time user. I have never seen the app. For each screen I ask three things: what is this, what matters most here, and what would I click next. Anything that took me more than about five seconds to work out is a finding.

**Scored lines:** 1 clarity of purpose, 2 hierarchy, 3 task efficiency, 5 navigation and naming, 7 phone experience. Lines 4, 6, 8 and 9 are `-` because they are outside my role. I score them only when a first-timer would trip over them.

**Which screenshots I looked at:** every `desk.en` and every `phone.de`. I also checked `01-overview.desk.de` and `01-overview.phone.en` for language and length. The 5200 px pages I viewed cropped as well as whole.

---

## Global navigation (applies to every screen)

**What is this?** A dark personal-finance dashboard. The desktop has a left sidebar. The phone has 4 bottom tabs plus a gear icon in the top bar.

| Line | Score | Based on |
|---|---|---|
| 5 navigation and naming | 6 | `01-overview.desk.en` sidebar tree: "Spending > Fixed costs" and "Net worth > Investments > Analysis / Forecast / Pay-ins" |
| 7 phone experience | 6 | `01-overview.phone.de` bottom bar "Übersicht / Umsätze / Ausgaben / Vermögen", plus the gear and eye icons top right |

**Findings**

- **`01-overview.desk.en`, sidebar.** Two places are nested three levels deep. Fixed costs sits under Spending, and Investments sits under Net worth. Its own children (Analysis, Forecast, Pay-ins) are also generic words that appear again as ETF tabs (`19-etf.desk.en`: "Overview / Analysis / Forecast / Facts"). A first-timer cannot tell whether "Analysis" in the sidebar means spending, the depot or the app as a whole. Severity: slows a task. Suggestion: name the items "Depot analysis" and "Depot forecast", or put a small "DEPOT" label over that sub-tree.
- **`01-overview.desk.en`, the eye icon next to the "Groschen" logo.** It has no label or tooltip text visible. I could not guess that it hides amounts until I saw `31-hidden-overview`. The same icon sits in the phone top bar (`01-overview.phone.de`). When the mode is on, the only signal is the highlighted icon. Nothing tells me why the numbers are blurred. Severity: slows a task. Suggestion: add the tooltip and aria-label "Hide amounts", and show a small "Amounts hidden" pill while the mode is on.
- **`01-overview.desk.en` vs `01-overview.desk.de`, naming.** The same item is called "Investments" in English but "Depot" in German. English pages then use "depot" anyway ("Depot value", "85% of the depot", "Direkt-Depot" on `14-networth.desk.en`). "Pay-ins" (EN) vs "Einzahlungen" (DE) has the same problem: the page heading on `18-inv-payments.desk.en` says "Money put in". Severity: slows a task. Suggestion: pick one English term ("Depot" or "Portfolio") and use it everywhere.
- **`01-overview.phone.de`, bottom bar.** Fixed costs and Settings have no bottom tab. Fixed costs appears only as a sub-tab inside "Ausgaben" (`11-recurring-list.phone.de`). Settings is only the unlabelled gear. Severity: slows a task. Suggestion: keep 4 tabs, but label the gear, or add "Mehr".
- **`01-overview.phone.en`, top-bar pill "just now" / "gerade eben".** It does not say what happened just now. The desktop says "ING connected / Synced just now". Severity: cosmetic. Suggestion: "Synced just now", or show the bank logo in the pill.
- **`keep`, `01-overview.desk.en`, sidebar footer.** The "ING connected / Synced just now" card with a refresh icon is instantly clear.
- **`keep`, `09-drill-group.desk.en` and others, breadcrumbs.** The "< SPENDING" style back-links above titles help orientation.

---

## 01 Overview (desk.en, desk.de, phone.de, phone.en)

**What is this?** My money right now. **Most important:** "Available until payday 5,170.65 €". **Next click:** "Check" on the first "Worth a look" item.

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 8 | `01-overview.desk.en` "AVAILABLE UNTIL PAYDAY 5,170.65 €" hero with "That's about 184.67 € per day" |
| 2 hierarchy | 8 | `01-overview.desk.en` hero first, then "Worth a look", then the Income/Spending/Saved row, then the Sankey |
| 3 task efficiency | 7 | `01-overview.desk.en` "Worth a look" rows with "Check" and "Show" buttons |
| 5 navigation and naming | 6 | `01-overview.desk.en` Sankey labels "Put aside" vs "Stays on the account" vs "Invested" |
| 7 phone experience | 7 | `01-overview.phone.de` stacked cards, and the Sankey that still fits at 390 px |

**Findings**

- **`01-overview.desk.en`, the timeline strip of dots/bars under "28 days to payday".** It takes more than 5 seconds to read. Bars, red dots and a coin icon appear without a legend, and only "Salary 27 Oct" and "Fri 27 Nov" are labelled. Severity: slows a task. Suggestion: give it a short caption such as "each red dot = a payment still to come".
- **`01-overview.desk.en`, the jar/glass graphic on the right of the hero.** It is decorative. I could not tell what "full" means: share of salary left, or days left. Severity: cosmetic. Suggestion: label it with a percentage ("48% of salary left") or drop it.
- **`01-overview.desk.en`, "SAVED 13,087.15 €" card.** The caption reads "3,000.00 € invested · 1,991.75 € stays". The biggest (teal) segment, which is 8,095.40 € "Put aside" in the Sankey, is not named. The numbers on the card therefore don't add up. Severity: slows a task. Suggestion: name all three parts: "3,000 invested · 8,095 put aside · 1,992 stays".
- **`01-overview.desk.en`, "Worth a look" item 1.** It reads "Groschen sorted 39 transactions on its own. Do the categories look right?", and the sidebar badge says 39. On `03-transactions-review.desk.en`, "Needs review 39" opens a banner "These transactions need a category from you" listing 8 uncategorised rows. So "review" means two different things: confirming 39 auto-sorted rows, or categorising uncategorised rows. Severity: blocks a task, because I don't know what I'm meant to finish. Suggestion: split the two jobs ("39 to confirm", "8 without category"), or make the banner text match the hint.
- **`01-overview.phone.de`, Sankey hint "Zeig auf ein Band, um ihm zu folgen".** "Point at a band" does not work on touch. Severity: cosmetic. Suggestion: on phones, say "Tippe auf ein Band".
- **`01-overview.phone.de`, "Einen Blick wert".** Items 2 and 3 have a dismiss X, but item 1 does not, and the desktop has no X at all. Severity: cosmetic.
- **`keep`, `01-overview.desk.en`, hero copy.** "Available until payday" plus a per-day figure is the clearest first-screen promise in the app.
- **`keep`, `01-overview.desk.en`, "Worth a look".** These are actionable sentences with one button each, and they read well for a newcomer.

## 02 / 04 / 06 Transactions: list, search, empty (desk.en, phone.de)

**What is this?** All bookings. **Most important:** the list. **Next click:** "Needs review 39".

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 8 | `02-transactions.desk.en` title, search, and a day-grouped list with merchant logos |
| 2 hierarchy | 7 | `02-transactions.desk.en` amount right-aligned in bold, category chip, faded "Girokonto" |
| 3 task efficiency | 7 | `02-transactions.desk.en` filter chips "All / Needs review / Uncategorized / Income" next to the search |
| 5 navigation and naming | 6 | `02-transactions.desk.en` summary line "297 transactions · 42,057.91 € in · 31,970.76 € out" |
| 7 phone experience | 6 | `02-transactions.phone.de` search placeholder cut ("…Kategorie oder Betr") and chip row cut at "Einnahmen" |

**Findings**

- **`02-transactions.desk.en`, summary line "42,057.91 € in · 31,970.76 € out".** Same period, different totals: the Overview shows Income 33,538.60 € and Spending 20,451.45 €. A newcomer will assume one of the two is wrong. Severity: slows a task. Suggestion: add "incl. transfers & savings" or a tooltip that explains the difference.
- **`02-transactions.desk.en`, the yellow left bar on "Hofladen Sonnenfeld" rows.** It is never explained. "Lena Berger" (Uncategorized, 14 Sept) has no bar, so it is not simply "uncategorised" either. Severity: slows a task. Suggestion: add a legend or tooltip ("needs your review").
- **`02-transactions.desk.en`, "Girokonto" column on every row.** With one main account this column is noise. Severity: cosmetic. Suggestion: hide it when only one account has transactions.
- **`02-transactions.desk.en`, refund lines.** Green text "Money back for Amazon, 10 Sept" and the struck-through "-34.99 €" with "All of it came back" are clever and readable. `keep`.
- **`02-transactions.phone.de`, filter chip row.** It is cut at the right edge ("Einnahmen" touches the edge). Severity: cosmetic. Suggestion: add a fade or scroll affordance.
- **`04-transactions-filtered.desk.en`.** "Clear filters" appears next to the counts. That is good, and `keep` it.
- **`06-transactions-empty.desk.en`.** "No transactions match / Try a different search, filter or period" plus "Clear filters" is a clear empty state. `keep`.
- **`06-transactions-empty.phone.de`.** A large empty gap opens above "Umsätze": the title starts about 190 px down. It looks like a layout glitch. Severity: cosmetic.

## 03 Transactions: needs review (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 6 | `03-transactions-review.desk.en` banner "These transactions need a category from you." |
| 2 hierarchy | 7 | `03-transactions-review.desk.en` gold banner above the list |
| 3 task efficiency | 5 | `03-transactions-review.desk.en` seven separate "Hofladen Sonnenfeld" rows, with no bulk action |
| 5 navigation and naming | 4 | `03-transactions-review.desk.en` tab "Needs review 39" vs "8 transactions" and "All periods" |
| 7 phone experience | 7 | `03-transactions-review.phone.de` same layout; the rows are easy to tap |

**Findings**

- **`03-transactions-review.desk.en`, count mismatch.** The tab says "Needs review 39", the list shows "8 transactions", and the summary says "All periods" while the top-right picker still shows "Jan – Oct 2026". Severity: blocks a task, because I can't tell when I'm done. Suggestion: make the badge equal the list count, and grey out the period picker when the view ignores it.
- **`03-transactions-review.desk.en`, the repeated merchant.** Seven of the eight rows are Hofladen Sonnenfeld. Nothing on screen says "categorise all from this merchant". The edit dialog has that toggle (`05`), but I'd only find it by opening a row. Severity: slows a task. Suggestion: add a row action or banner button: "Set a category for all 7 from Hofladen Sonnenfeld".
- **`03-transactions-review.desk.en`, the summary "110,315.81 € in / 84,234.46 € out" for 8 small rows.** I know the capture can't filter, but in a real filtered view this line must reflect the visible rows.

## 05 Transaction edit dialog (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 8 | `05-transactions-edit.desk.en` "Shell −56.30 €", the raw bank text, then "Category" |
| 2 hierarchy | 7 | `05-transactions-edit.desk.en` the selected chip "Fuel" highlighted gold |
| 3 task efficiency | 7 | `05-transactions-edit.desk.en` "Search categories" plus the "Use this category for every transaction from this merchant" toggle |
| 5 navigation and naming | 6 | `05-transactions-edit.desk.en` "Housing (general)" chips vs "Housing" in `08`, and "Food & Dining" as a category in `09` |
| 7 phone experience | 5 | `05-transactions-edit.phone.de` the "for every transaction from this merchant" toggle is not visible without scrolling |

**Findings**

- **`05-transactions-edit.phone.de`, the merchant-rule toggle.** It is the most powerful control in the dialog, and it is below the fold, under a long chip list. Severity: slows a task. Suggestion: pin it next to "Speichern".
- **`05-transactions-edit.desk.en`, the "SUBSCRIPTIONS" group header.** It is cut off under the sticky toggle row, so a whole group looks missing. Severity: cosmetic.
- **`05-transactions-edit.desk.en`, the "Everything with Shell >" link in the footer.** It is useful, but it sits where "Cancel" usually sits. Severity: cosmetic.

## 07 Spending (desk.en, phone.de) and 33 period menu

**What is this?** Where my money goes. **Most important:** the donut and list. **Next click:** a group row with ">".

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 7 | `07-spending.desk.en` "Spending breakdown 2,045.14 € a month on average, most on Housing (58%)" |
| 2 hierarchy | 7 | `07-spending.desk.en` donut and ranked bar list, then "Your year in days" |
| 3 task efficiency | 7 | `33-period-menu.desk.en` presets "Month / Last 30 days / Year to date / Year / Last 12 months / All time" |
| 5 navigation and naming | 5 | `07-spending.desk.en` page title "Spending" with a "Spending / Income" toggle, and the "+ Your own group" button |
| 7 phone experience | 6 | `07-spending.phone.de` heat map cut at "Jun" with no scroll hint |

**Findings**

- **`07-spending.desk.en`, the "Spending | Income" toggle on a page titled "Spending".** Switching to Income leaves me on "Spending" in the sidebar. `10-drill-category.desk.en` then shows "< INCOME / Income 0.00 €" with "0 transactions", even though the Overview says income is 33,538 €. To a newcomer that looks broken. Severity: blocks a task, because I can't find my income here. Suggestion: rename the page "Money in & out", or move Income to its own breadcrumb root. At minimum, never show 0.00 € for a period that has salary.
- **`07-spending.desk.en`, "+ Your own group" button.** It floats under the title with low contrast. I didn't know what a "group" was until the dialog explained it. Severity: slows a task. Suggestion: rename it "+ Custom group (e.g. Car)", and move it into the "Groups / Categories" toggle area.
- **`07-spending.desk.en`, "Housing 58.3%".** The Overview Sankey shows "Housing 35.6%" (share of income). Two percentages for the same thing confuse. Severity: slows a task. Suggestion: label each one: "of spending" / "of income".
- **`07-spending.desk.en`, "Personal · more refunds than spending −162.37 €".** It reads like a bug. Severity: cosmetic.
- **`07-spending.desk.en`, "Your year in days".** The heat map covers Nov–Dec too, although the period is Jan–Oct, and it has its own year arrows that ignore the period picker. That makes two time controls on one page. Severity: slows a task.
- **`33-period-menu.desk.en`.** The presets are clear. "Month" doesn't say which month, and there is no custom range. Severity: cosmetic.
- **`keep`, `07-spending.desk.en`.** Explaining the heat map in one sentence above it ("grey without spending, from violet to glowing yellow…") is exactly what a newcomer needs.

## 08 New group dialog (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 8 | `08-spending-group-dialog.desk.en` intro "A custom group collects transactions across categories, for a car, a flat…" |
| 3 task efficiency | 6 | `08-spending-group-dialog.desk.en` long chip list with no selected count |
| 5 navigation and naming | 6 | `08-spending-group-dialog.desk.en` "Housing" chip vs "Housing (general)" in `05` |
| 7 phone experience | 6 | `08-spending-group-dialog.phone.de` list cut at "Einkaufen" with no counter |

**Findings**

- **`08-spending-group-dialog.desk.en`, chips.** Nothing shows how many categories are picked. "SUBSCRIPTIONS" is cut at the bottom. Severity: slows a task. Suggestion: add "3 selected" next to Save.
- **`keep`.** The one-sentence explanation with concrete examples (car, flat, holiday).

## 09 Drill: group, Food & Dining (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 9 | `09-drill-group.desk.en` "< SPENDING / Food & Dining / SPENT 3,480.29 € ↑35% vs. the period before" |
| 2 hierarchy | 8 | `09-drill-group.desk.en` big figure, monthly bars with an "Average 348 €" line, then Top merchants and Categories |
| 3 task efficiency | 7 | `09-drill-group.desk.en` category filter chips "Groceries 43 / Restaurants & cafés 36" above the transactions |
| 5 navigation and naming | 6 | `09-drill-group.desk.en` "Food & Dining · 0×" listed as a category inside the group "Food & Dining" |
| 7 phone experience | 8 | `09-drill-group.phone.de` cards stack cleanly and the chart stays readable |

**Findings**

- **`09-drill-group.desk.en`, Categories card "Food & Dining · 0× 0.00 €" and "Food delivery · 0×".** The category has the same name as its group, and zero rows add noise. Severity: cosmetic. Suggestion: call it "(general)" as in `05`, and hide zero rows.
- **`09-drill-group.desk.en`, "Top merchants 8 of 9".** There is no visible way to see the 9th. Severity: cosmetic.
- **`keep`.** This is the best drill-down page in the app, a model for the others.

## 10 Drill: category, Income (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 4 | `10-drill-category.desk.en` "< INCOME / Income / RECEIVED 0.00 €" |
| 5 navigation and naming | 4 | `10-drill-category.desk.en` breadcrumb "INCOME" leads to a page also called "Income" |
| 7 phone experience | 7 | `10-drill-category.phone.de` empty states "Nichts darzustellen" / "Keine passenden Umsätze" fit well |

**Findings**

- **`10-drill-category.desk.en`.** Income shows 0.00 € and "Nothing in this period. Pick a different one at the top", although salary exists for Jan–Oct. Even if this is demo data, a first-timer loses trust here. The breadcrumb also repeats the title. Severity: blocks a task.
- **`keep`.** The empty-state copy itself ("Nothing to chart") is clear.

## 11 / 12 / 13 Fixed costs: List, Calendar, Orbit (desk.en, phone.de)

**What is this?** My recurring payments. **Most important:** "1,407.01 € fixed costs per month" and "Next up". **Next click:** a row in "Running".

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 8 | `11-recurring-list.desk.en` "FIXED COSTS PER MONTH 1,407.01 €" and "NEXT UP In 2 days Hausverwaltung Kraemer" |
| 2 hierarchy | 7 | `11-recurring-list.desk.en` hero, then "What changed", then "Running" |
| 3 task efficiency | 6 | `11-recurring-list.desk.en` "Running" list sorted by amount while showing "In 2 days / In 16 days / In 7 days…" |
| 5 navigation and naming | 5 | `11-recurring-list.desk.en` view switch "List / Calendar / Orbit", and section names "Running", "Stopped (1)" |
| 7 phone experience | 6 | `11-recurring-list.phone.de` "Laufend" rows drop the "In X Tagen" due date; `13-recurring-orbit.phone.de` orbit squashed and labels overlap |

**Findings**

- **`12-recurring-calendar.desk.en`, header "1,423.48 € fixed costs".** The List says 1,407.01 € per month. Two different totals for "fixed costs" one tab apart. Severity: slows a task. Suggestion: label one "this month's actual" and the other "monthly average".
- **`11-recurring-list.desk.en`, badges "+7.00 €", "+9.00 €", "+2.00 €" next to names.** It is unclear whether these are a price rise or a surcharge, and since when. "What changed" explains Spotify only. Severity: slows a task. Suggestion: write "+7.00 € since Jun" or use a tooltip.
- **`13-recurring-orbit.desk.en`, "Orbit" view.** This is a visual toy. Most planets are unlabelled, and "A payment reaches the front on the day it is due" needs reading twice. On `13-recurring-orbit.phone.de` it collapses into an overlapping blob. Severity: cosmetic, though it slows anyone who opens it. Suggestion: rename it "Rhythm" or hide it on phones.
- **`11-recurring-list.desk.en`, "3 savings plans run along: 1,100.00 € a month. They live under Net worth."** This is a great cross-link and explains the information architecture. `keep`.
- **`12-recurring-calendar.desk.en`, chips "Ha…", "Spar…", "Rundf…", "Nor…".** The truncated names are hard to read, though the "Day by day" list on the right saves it. `keep` the side list.
- **`11-recurring-list.desk.en`, "What changed".** Plain-language sentences ("Disney+ stopped coming… That saves 119.88 € a year") are excellent for newcomers. `keep`.

## 14 Net worth (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 9 | `14-networth.desk.en` "TODAY 44,931.92 € ↑13,592.05 € Jan – Oct 2026" with the line chart |
| 2 hierarchy | 8 | `14-networth.desk.en` total, then account cards, then "Savings plans" |
| 5 navigation and naming | 6 | `14-networth.desk.en` account cards with an unlabelled "17% / 62% / 21%" bar |
| 7 phone experience | 8 | `14-networth.phone.de` sub-tabs "Vermögen / Depot" make the depot easy to reach |

**Findings**

- **`14-networth.desk.en`, the percentage bars on the account cards.** They don't say "of net worth". Severity: cosmetic.
- **`14-networth.desk.en`, the "Add account" card.** "Say a house or a car loan outside your banks. You keep its value up to date." is clear. `keep`.
- **`14-networth.desk.en`, only "Direkt-Depot" has a ">" chevron.** The Girokonto and Extra-Konto cards look clickable but aren't, or don't show it. Severity: cosmetic.

## 15 / 32 Investments (desk.en, phone.de, hidden)

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 7 | `15-investments.desk.en` "DEPOT VALUE ON 30 OCT 2026 9,350.57 € ↑504.90 € · +6.7%" |
| 2 hierarchy | 7 | `15-investments.desk.en` value chart with monthly gain/loss bars, then Holdings |
| 5 navigation and naming | 5 | `15-investments.desk.en` legend "Value without deposits", and the toggle "Money paid in" |
| 7 phone experience | 7 | `15-investments.phone.de` tabs "Depot / Analyse / Prognose / Einzahlungen" |

**Findings**

- **`15-investments.desk.en`, the chart legend "Value without deposits".** Next to the depot value of 9,350 € it is unclear what is plotted. Severity: slows a task. Suggestion: write "Market growth only (deposits removed)".
- **`15-investments.desk.en`, the holding card "+7.5% · 474 €".** The ETF page `19-etf.desk.en` shows "+1,160.97 € · +17.2%" for the same fund. That is period vs since-purchase, but neither is labelled. Severity: slows a task. Suggestion: add "this period" or "since first buy".
- **`32-hidden-investments.desk.en`.** Percentages stay visible while amounts blur. That is fine. The blurred "9,999.99" placeholders are clearly fake. `keep`.

## 16 Forecast (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 8 | `16-inv-forecast.desk.en` "Where it could go: 800 simulated futures… Assumptions, not a promise." and "IN 10 YEARS 68,412 €" |
| 2 hierarchy | 8 | `16-inv-forecast.desk.en` assumptions row, then the result with a bad/good-case slider, then the chart |
| 5 navigation and naming | 6 | `16-inv-forecast.desk.en` "Expected return 7.4%… +13.5% a year over 2.3 years (counts 19%), the rest is the long-run 6%" |
| 7 phone experience | 8 | `16-inv-forecast.phone.de` 2×2 assumption cards and a horizon picker that fits |

**Findings**

- **`16-inv-forecast.desk.en`, "Expected return" explanation.** "(counts 19%)" is jargon. Severity: cosmetic. Suggestion: "weighted 19% recent / 81% long-run".
- **`keep`.** "1 in 12 futures ends below what you paid in" and the milestone chips "50,000 € in 2034" are great plain-language outputs.

## 17 Analysis (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 7 | `17-inv-analysis.desk.en` "Return in this period: Your money +6.7% / The funds themselves +6.3%" |
| 2 hierarchy | 7 | `17-inv-analysis.desk.en` return, then volatility, then drawdown, then monthly heat strip |
| 5 navigation and naming | 6 | `17-inv-analysis.desk.en` "Ups and downs ±17%" and "Drawdown" |
| 7 phone experience | 6 | `17-inv-analysis.phone.de` "Monatsrenditen" cut at "Jun" with no scroll hint |

**Findings**

- **`17-inv-analysis.desk.en`, "☐ Outlined: the best and the worst month".** It is a legend but looks like an unticked checkbox. Severity: cosmetic.
- **`23-settings-depot.desk.en`.** It says the interest rate is "used for the Sharpe ratio", but no Sharpe ratio appears on `17-inv-analysis.desk.en`. Severity: cosmetic.
- **`keep`.** "About what the funds themselves made" is a one-line verdict for a newcomer.

## 18 Pay-ins (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 7 | `18-inv-payments.desk.en` "Money put in… Not part of this depot? One click takes it out." |
| 3 task efficiency | 7 | `18-inv-payments.desk.en` the "× Don't count" per row |
| 5 navigation and naming | 5 | `18-inv-payments.desk.en` sidebar "Pay-ins", title "Pay-ins", card title "Money put in", and an "Import price history" bar at the bottom |

**Findings**

- **`18-inv-payments.desk.en`, the "Import price history" bar ("One line per day: date;ISIN;price").** It has nothing to do with pay-ins, and a newcomer would not look for it here. Severity: slows a task. Suggestion: move it to Settings > Investments or onto the ETF "Facts" tab.

## 19 ETF detail (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 8 | `19-etf.desk.en` "Vanguard FTSE All-World", ISIN chip, "YOUR VALUE 7,910.97 €", price chart with "Your average 110.71 €" |
| 5 navigation and naming | 5 | `19-etf.desk.en` tabs "Overview / Analysis / Forecast / Facts" duplicating the sidebar names |
| 7 phone experience | 7 | `19-etf.phone.de` "< DEPOT" back-link; the depot sub-tabs disappear |

**Findings**

- **`19-etf.desk.en`, the "Get full price histories?" banner.** It appears here and on `15-investments.desk.en`, above the main content, pushing the value down. Severity: cosmetic. Suggestion: show it once, or below the chart.
- **`keep`.** "Dots are your purchases" plus the average-price line make the chart easy to read.

## 20-27 Settings (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 7 | `20-settings-bank.desk.en` "Bank connections", ING card with "Sync now" |
| 2 hierarchy | 7 | `20-settings-bank.desk.en` gold "Sync now" as the primary action |
| 5 navigation and naming | 6 | `20-settings-bank.desk.en` 8 tabs "Bank & import / Categories / Hints & salary / Investments / Backups / Export & privacy / Security / Account & look" |
| 7 phone experience | 6 | `20-settings-bank.phone.de` tab strip cut at "Hinweise & Gehalt", with 5 more tabs hidden off-screen |

**Findings**

- **`20-settings-bank.desk.en`, the button "✓ I logged in to my bank".** As a first-timer I don't know why I'd press this. The explanation is a dense paragraph underneath. Severity: slows a task. Suggestion: show it only when the 90-day timer runs low, and rename it "Reset 90-day timer".
- **`20-settings-bank.desk.en`, "FinTS · login •emo".** The masked login looks like a typo. Severity: cosmetic.
- **`21-settings-categories.desk.en`, "Categorizer".** The "Built-in model" option is selected, but the text says "(built-in model not found)", and the badge "Offline" is green. That contradicts itself. Severity: slows a task.
- **`21-settings-categories.desk.en`, "That's you".** It is an odd section name for "my own accounts' owner names". Severity: cosmetic. Suggestion: "Your own names (transfers to yourself)".
- **`22-settings-hints.desk.en`, "Keep aside" (subtracted from "Available until payday").** The Overview Sankey has "Put aside" meaning savings. Two near-identical terms with different meanings. Severity: slows a task. Suggestion: rename this one "Safety cushion".
- **`24-settings-backup.desk.en`.** Smart Recycle cards, a timeline, a slider and four steppers are a lot for "back up my data". It is fine for experts. A newcomer only needs "Back up now" and "Next backup tomorrow at 03:00", which are present top right. `keep` those.
- **`25-settings-privacy.desk.en`, "Connection log: No outgoing connections in the last 7 days".** The sidebar says "Synced just now" with ING. That contradicts itself. Severity: slows a task, because it erodes trust. The "Show log" button also looks disabled.
- **`25-settings-privacy.desk.en`, "Backups never contain the key…" under Export.** This duplicates the Backups text. Severity: cosmetic.
- **`26-settings-security.desk.en`, the passkeys warning "Passkeys don't work at 127.0.0.1".** Yet "Chrome on Mac · active just now · with passkey" sits below it. That contradicts itself. Severity: cosmetic.
- **`27-settings-account.desk.en`, "Country: Not chosen".** The wizard asks for a country in step 2 (`41-wizard-country.desk.en`). Severity: cosmetic.
- **`30-settings-connect-dialog.desk.en`, the "Connect your bank" dialog.** It shows the error "No bank found by that name. Type your Bankleitzahl or IBAN instead." while the field is still empty, and "Done, start syncing" is enabled with no bank chosen. Severity: slows a task. Suggestion: show the error only after typing, and disable the button until a bank is picked.
- **`keep`, `20-settings-bank.desk.en`.** The 90-day progress bar "Bank login needed within 90 days" is a clear status.
- **`keep`, `22-settings-hints.desk.en`.** Each toggle has a one-line plain description.

## 31 Hidden overview (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 6 | `31-hidden-overview.desk.en` blurred "9,999.99 €" with only the highlighted eye icon as a signal |
| 7 phone experience | 7 | `31-hidden-overview.phone.de` the highlighted eye in the top bar |

**Findings**

- **`31-hidden-overview.desk.en`.** No text explains the blur. Severity: slows a task. Suggestion: add an "Amounts hidden · show" chip.

## 40 / 41 Wizard, 42 Login (desk.en, phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 9 | `40-wizard-account.desk.en` "Welcome to Groschen. Let's set up your dashboard. It takes about five minutes…" |
| 2 hierarchy | 8 | `40-wizard-account.desk.en` 5-step side rail "Welcome / Connect your bank / Import history / Smart features / First sync" |
| 5 navigation and naming | 7 | `41-wizard-country.desk.en` "Automatic bank sync works with German banks. Everywhere else… CSV" |
| 7 phone experience | 5 | `40-wizard-account.phone.de` only 5 unlabeled progress dashes, no step names |

**Findings**

- **`40-wizard-account.phone.de`, progress dashes.** They don't say what is coming or which step I'm on. Severity: slows a task. Suggestion: add "Schritt 1 von 5 · Anmeldung".
- **`41-wizard-country.phone.de`.** It shows the error "Keine Bank mit diesem Namen gefunden" under an empty bank field (the same bug as `30`). "Überspringen, vorerst CSV-Dateien nutzen" is a good escape hatch. `keep` that.
- **`42-login.desk.en`.** It is simple, with the language picker. The "Log in" button looks disabled (muted gold) even when it may be ready. Severity: cosmetic.
- **`keep`, `40-wizard-account.desk.en`.** "You can change everything later under Settings. There are no config files to edit."

---

## Top 10

1. **Two meanings of "review" (blocks a task).** `01-overview.desk.en` "Groschen sorted 39 transactions… look right?" and the sidebar badge 39 contradict `03-transactions-review.desk.en`, where "Needs review 39" lists 8 rows under "These transactions need a category from you". Split it into "39 to confirm" and "8 without category", with badges that match the lists.
2. **Income dead-end (blocks a task).** The `07-spending.desk.en` "Spending | Income" toggle leads to `10-drill-category.desk.en` "Income 0.00 €, 0 transactions", while the Overview shows 33,538 € income. Give Income a proper home and never show 0 when salary exists.
3. **Totals disagree across screens (slows a task).** Transactions "42,057.91 € in / 31,970.76 € out" (`02`) vs Overview 33,538.60 / 20,451.45 (`01`). Fixed costs 1,407.01 € (`11`) vs 1,423.48 € (`12`). Housing 35.6% (`01`) vs 58.3% (`07`). Label each figure's basis.
4. **Investment naming is inconsistent (slows a task).** Investments / Depot / Pay-ins / "Money put in", plus "Analysis" and "Forecast" used both in the sidebar (depot-wide, `01-overview.desk.en`) and as ETF tabs (`19-etf.desk.en`). Pick one vocabulary and prefix the depot items.
5. **"Saved" card omits its largest part (slows a task).** `01-overview.desk.en` "3,000.00 € invested · 1,991.75 € stays" leaves out the 8,095.40 € "Put aside". Name all three segments.
6. **Payday timeline strip has no legend (slows a task).** On `01-overview.desk.en`, the bars, red dots, coin icon and jar graphic under "28 days to payday" need a one-line caption.
7. **Bank-connect error shown on an empty field, and the action is enabled without a bank (slows a task).** `30-settings-connect-dialog.desk.en` and `41-wizard-country.phone.de` both do this. Show the error only after input, and disable "Done, start syncing" until a bank is picked.
8. **No bulk action for the same uncategorised merchant (slows a task).** `03-transactions-review.desk.en` has 7× Hofladen Sonnenfeld. Add "Categorise all 7", and on `05-transactions-edit.phone.de` move the "every transaction from this merchant" toggle above the fold.
9. **Unlabelled icons and modes (slows a task).** The eye icon (`01-overview.desk.en`, `01-overview.phone.de`) has no label, and hidden mode (`31-hidden-overview.desk.en`) has no text cue. The phone gear is the only way into Settings, and the phone settings tab strip hides 5 of 8 tabs (`20-settings-bank.phone.de`).
10. **Contradictory status text erodes trust (slows a task).** `25-settings-privacy.desk.en` "No outgoing connections in the last 7 days" vs "Synced just now". `21-settings-categories.desk.en` "Built-in model" selected but "(built-in model not found)". `26-settings-security.desk.en` "Passkeys don't work here" vs "with passkey". `22-settings-hints.desk.en` "Keep aside" vs the Overview's "Put aside".
