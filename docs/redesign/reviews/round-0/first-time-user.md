# Groschen review: first-time user

Role: someone who has never seen the app. For each screen I ask three things: what is this, what matters most here, and what would I click next. Anything that took me more than about five seconds to work out is a finding. I score only lines 1 (clarity of purpose), 2 (hierarchy), 3 (task efficiency), 5 (navigation and naming) and 6 (consistency, naming only). The other lines are "-".

I looked at every desk.en and phone.de screenshot. I also opened desk.de 20 and phone.en 15 to check naming across languages. Tall pages were cropped into pieces for reading.

---

## 01 Overview (01-overview.desk.en / .desk.de / .phone.de / .phone.en)

**What is this?** It is a home dashboard. I could tell right away. **Most important?** The "Available until payday 5,170.65 €" hero. It wins, as it should. **Next click?** "Check" in "Worth a look", or the Transactions badge "39".

| Line | Score | Based on |
|---|---|---|
| 1 Clarity | 8 | 01-overview.desk.en: "Available until payday" hero with "That's about 184.67 € per day" says what the number means in plain words |
| 2 Hierarchy | 7 | 01-overview.desk.en: the hero number dominates, but the decorative jar graphic to its right takes as much space as the number and explains nothing |
| 3 Efficiency | 7 | 01-overview.desk.en: "Worth a look" rows each have one direct action button ("Check", "Show") |
| 5 Nav/naming | 6 | 01-overview.desk.en: the Sankey has "Saved", "Put aside", "Invested" and "Stays on the account", four overlapping savings words |
| 6 Consistency | 6 | 01-overview.phone.de: the hint rows have dismiss "x" buttons; 01-overview.desk.en has none |
| 4,7,8,9 | - | |

Findings
- **01-overview.desk.en, the jar graphic next to the hero.** I could not tell what the fill level means: share of salary left? Share of the month gone? It has no label. *slows a task.* Label it (for example "62 % of salary left") or remove it. On phone.de it is already gone.
- **01-overview.desk.en, "Saved 13,087.15 €" card vs the Sankey.** The card's caption reads "3,000.00 € invested · 1,991.75 € stays" and leaves out the 8,095.40 € "Put aside" from the Sankey, so the caption does not add up to the headline. "Saved", "Put aside" and "Stays on the account" all sound like the same thing to a newcomer. *slows a task.* Use one term set everywhere: Saved = Invested + Put aside + Left on account, and show all three parts in the caption.
- **01-overview.desk.en, the sidebar eye icon next to the logo.** It has no label or tooltip, so I would not guess that it hides amounts. In 31-hidden-overview.desk.en the only sign that the mode is on is that the icon turns gold. *slows a task.* Add a tooltip and an "Amounts hidden" pill while the mode is on.
- **01-overview.desk.en, the gold dot after "Overview" in the sidebar.** It is unexplained. Is it unread hints? *cosmetic.*
- **01-overview.phone.de, the Sankey caption "Zeig auf ein Band, um ihm zu folgen".** On a phone you cannot point. *cosmetic.* Use "Tipp auf ein Band" on touch devices.
- **01-overview.desk.en, the payday strip.** "Salary 27 Oct" on the left and "Fri 27 Nov" on the right are clear. The coloured dots for the 14 payments are tiny, and I only understood them after reading the gold link "14 payments still to come". *cosmetic.*
- **keep:** 01-overview.desk.en, the date eyebrow "FRIDAY 30 OCTOBER" above the title, and "Worth a look", which reads like a person talking.
- **keep:** 01-overview.desk.en, the hero sentence "That's about 184.67 € per day."

---

## 02 / 03 / 04 Transactions: list, needs review, search (02/03/04-*.desk.en / .phone.de)

**What is this?** A bank statement. It is obvious. **Most important?** The amounts on the right. **Next click?** "Needs review 39".

| Line | Score | Based on |
|---|---|---|
| 1 Clarity | 8 | 02-transactions.desk.en: the day-grouped list with logos and category pills reads like a banking app |
| 2 Hierarchy | 6 | 02-transactions.desk.en: about 600 px of empty space between the merchant name and the category pill, and the account column "Girokonto" is so faint it looks disabled |
| 3 Efficiency | 7 | 02-transactions.desk.en: search, the filter tabs, "Filter" and sort all sit in one row |
| 5 Nav/naming | 5 | 03-transactions-review.desk.en: the tabs "Needs review" and "Uncategorized" plus the banner "These bookings need a category from you". Overview says these 39 were auto-sorted and need checking, not that they need a category |
| 6 Consistency | 5 | 02-transactions.desk.en: day headers come in two styles, grey letter-spaced with a day total ("WEDNESDAY 28 OCTOBER -177.49 €") and bold white without a total ("TUESDAY 27 OCTOBER") |
| 4,7,8,9 | - | |

Findings
- **03-transactions-review.desk.en, "Needs review" vs "Uncategorized".** Overview says "Groschen sorted 39 bookings on its own. Do the categories look right?" This banner says "These bookings need a category from you." So which is it: check guesses, or fill in blanks? And how does that differ from the "Uncategorized" tab next to it? *slows a task.* Make the banner match Overview ("Groschen guessed these 39. Confirm or change"), and say in the tab tooltip that "Uncategorized" means no guess at all.
- **03-transactions-review.desk.en, the summary line "All periods · 774 transactions".** The period button top right still says "Jan – Oct 2026". Two contradicting periods on one screen. *slows a task.* Disable the period picker or change its label to "All periods" while this tab is active.
- **02-transactions.desk.en, the gold left bar on rows (Hofladen Sonnenfeld, Lena Berger).** It has no legend. I guessed it means "needs review", but some of these rows are not in review. *cosmetic.*
- **02-transactions.desk.en, day headers.** There are two visual styles for the same element: grey with a total vs white without one. *cosmetic.* Use one style and always show the total, or none.
- **02-transactions.phone.de, the filter tabs and search placeholder.** "Einnahmen" is cut off at the right edge. The placeholder "Händler, Verwendungszweck, Kategorie oder Betr…" is cut off too. *cosmetic.* Shorten it to "Suchen…".
- **04-transactions-filtered.desk.en, the "Clear filters" link.** It is good that it appears. But the active search is not repeated anywhere except inside the input. *cosmetic.*
- **keep:** 02-transactions.phone.de, the strikethrough "-34,99 €" with "Komplett zurückbekommen", and the "32.00 € of 64.00 € back" progress on 02-transactions.desk.en. Refunds are understandable at a glance.
- **keep:** 02-transactions.desk.en, the summary line "297 transactions · 42,057.91 € in · 31,970.76 € out".

## 05 Transaction edit (05-transactions-edit.desk.en / .phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 Clarity | 8 | 05-transactions-edit.desk.en: the header "Shell -56.30 €" with the raw bank text in monospace below it |
| 2 Hierarchy | 7 | 05-transactions-edit.desk.en: the selected "Fuel" pill is gold and easy to find among about 25 pills |
| 3 Efficiency | 6 | 05-transactions-edit.phone.de: the toggle "Use this category for every transaction from this merchant" is below the fold, behind about 20 pills |
| 5 Nav/naming | 7 | 05-transactions-edit.desk.en: the footer link "Everything with Shell" is a clear next step |
| 4,6,7,8,9 | - | |

Findings
- **05-transactions-edit.phone.de, the merchant-rule toggle.** It is hidden by scrolling. It is on by default and changes the behaviour for every future Shell booking. *slows a task.* Move it above the category grid, or next to "Speichern".
- **05-transactions-edit.desk.en.** Category is the only visible task. Splitting, notes and marking a refund are not discoverable from here. If they exist, I could not find them. *slows a task.*
- **keep:** 05-transactions-edit.desk.en, the category search field on top, grouped pills and the "+ New" pill inside each group.

## 06 Transactions empty (06-transactions-empty.desk.en / .phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 Clarity | 8 | 06-transactions-empty.desk.en: "No transactions match / Try a different search, filter or period." |
| 3 Efficiency | 6 | 06-transactions-empty.desk.en: no one-click "Search all periods" in the empty card |
| 9 | - | |
| 2,4,5,6,7,8 | - | |

Findings
- **06-transactions-empty.phone.de, page top.** There is an empty band of about 100 px between the header bar and "Umsätze". I saw the same gap on 13-recurring-orbit.phone.de and 23-settings-depot.phone.de, and it makes the page look broken. *cosmetic.*
- **06-transactions-empty.desk.en, the empty card.** Offer a "Search in all periods" button. *slows a task.*

---

## 07 Spending (07-spending.desk.en / .phone.de) and 33 Period menu

**What is this?** Where my money went by category. **Most important?** The breakdown list. **Next click?** A category row.

| Line | Score | Based on |
|---|---|---|
| 1 Clarity | 8 | 07-spending.desk.en: "Spending breakdown · 2,045.14 € a month on average · most on Housing (58%)" |
| 2 Hierarchy | 7 | 07-spending.desk.en: the donut and list pair is clear. "Your own group" floats alone above the card and looks like a stray tag |
| 3 Efficiency | 7 | 07-spending.desk.en: every row has a chevron to drill in |
| 5 Nav/naming | 4 | 07-spending.phone.de: two stacked segmented controls, "Ausgaben, Einnahmen" and "Ausgaben, Fixkosten", with "Ausgaben" selected in both |
| 6 Consistency | 6 | 07-spending.desk.en: "Personal · more refunds than spending -162.37 €", a negative value in a spending list with no bar |
| 4,7,8,9 | - | |

Findings
- **07-spending.phone.de, the two segmented controls.** "Ausgaben" appears twice and means two different things (spending vs income, then spending vs fixed costs). I had to stop and think about which one I was on. *slows a task.* Rename the second one ("Übersicht, Fixkosten"), or put fixed costs in the bottom nav.
- **07-spending.desk.en, "+ Your own group".** I did not know what this creates until I opened 08. *slows a task.* Rename it "+ Custom group", the name used in Settings (21-settings-categories.desk.en "Custom groups").
- **07-spending.desk.en, the "Your year in days" heatmap.** Future days (Nov–Dec) and "Nothing" days look almost the same grey. *cosmetic.*
- **33-period-menu.desk.en, the menu items "Month" and "Year".** It does not say which month or year, and there is no custom range. The button says "Jan – Oct 2026" while the menu ticks "Year to date". *slows a task.*
- **keep:** 07-spending.desk.en, the helper text under "Your year in days" explains the colour scale in one sentence.

## 08 New group dialog (08-spending-group-dialog.desk.en / .phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 Clarity | 7 | 08-spending-group-dialog.desk.en: the intro "A custom group collects bookings across categories, for a car, a flat…" |
| 2 Hierarchy | 5 | 08-spending-group-dialog.desk.en: the category pills have no "Categories" label and no hint that you can pick several |
| 5 Nav/naming | 5 | 08-spending-group-dialog.desk.en: "your main budget still counts everything normally", although no "budget" appears anywhere else in the app |
| 6 Consistency | 6 | 08-spending-group-dialog.desk.en "Housing" vs 05-transactions-edit.desk.en "Housing (general)" for the same pill |
| 3,4,7,8,9 | - | |

Findings
- **08-spending-group-dialog.desk.en, the pill area.** Add the heading "Which categories belong in it? (pick several)". *slows a task.*
- **08-spending-group-dialog.desk.en, the "Save" button.** It is dimmed with no reason given (presumably the name is empty). *cosmetic.*
- **08-spending-group-dialog.desk.en, the word "budget".** There is no budget feature anywhere else. Say "your other totals" instead. *cosmetic.*

## 09 / 10 Drill-downs (09-drill-group.desk.en / .phone.de, 10-drill-category.desk.en / .phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 Clarity | 8 | 09-drill-group.desk.en: "SPENDING / Food & Dining 3,480.29 € ↑35% vs. the period before" |
| 2 Hierarchy | 8 | 09-drill-group.desk.en: total, monthly bars, merchants, categories, transactions in a sensible top-down order |
| 5 Nav/naming | 5 | 09-drill-group.desk.en: no back button. The grey eyebrow "SPENDING" is the only way back, and it does not look clickable |
| 1 Clarity (10) | 3 | 10-drill-category.desk.en: a page titled "INCOME / Income" shows "Received 0.00 €" although Overview shows 33,538.60 € income |
| 4,6,7,8,9 | - | |

Findings
- **10-drill-category.desk.en, "Income 0.00 €".** For a newcomer this looks like a bug: Overview said 33k income. It is most likely a category called "Income" that the salary is not in (salary is "Salary"). *blocks a task* (I would think my data is broken). Hide categories that are empty in the period, or redirect to the income group. Do not repeat "Income" in both the eyebrow and the title.
- **10-drill-category.desk.en, two stacked empty states** ("Nothing to chart" plus "No transactions match"). One is enough. *cosmetic.*
- **09-drill-group.desk.en, the Categories card.** It lists "Food & Dining · 0×" and "Food delivery · 0×" with 0.00 €. That is noise. *cosmetic.*
- **09-drill-group.desk.en, the eyebrow "SPENDING".** Make it a real "‹ Spending" back link. *slows a task.*
- **keep:** 09-drill-group.desk.en, the dashed "Average 348 €" line on the monthly bars.

---

## 11 / 12 / 13 Fixed costs (11-recurring-list, 12-recurring-calendar, 13-recurring-orbit; desk.en / phone.de)

**What is this?** Subscriptions and contracts. That is clear from the "List" view. **Most important?** "1,407.01 € fixed costs per month". **Next click?** A row, or "Show all 8".

| Line | Score | Based on |
|---|---|---|
| 1 Clarity | 8 | 11-recurring-list.desk.en: hero "FIXED COSTS PER MONTH 1,407.01 €" plus a "Next up" list |
| 2 Hierarchy | 7 | 11-recurring-list.desk.en: "What changed" sits above "Running", which is good for scanning |
| 3 Efficiency | 6 | 11-recurring-list.desk.en: the "Running" list is sorted neither by amount (55.08 € comes after 24.99 €) nor by due date |
| 5 Nav/naming | 4 | 13-recurring-orbit.desk.en: the view name "Orbit" says nothing about what it shows |
| 6 Consistency | 3 | 12-recurring-calendar.desk.en "2,523.48 € fixed costs this month" vs 11-recurring-list.desk.en "1,407.01 € fixed costs per month" |
| 4,7,8,9 | - | |

Findings
- **12-recurring-calendar.desk.en, header "2,523.48 € fixed costs this month".** The List view says 1,407.01 €. The calendar also counts the savings plans (800 + 250 + 50) and even shows the salary. Two "fixed costs" totals, 1,100 € apart, are confusing. *slows a task.* Call the calendar total "All recurring this month", or split it into "Fixed costs 1,407 € + savings 1,100 €".
- **11-recurring-list.desk.en, the amber badges "+7.00 €", "+9.00 €", "+2.00 €".** Is that a price increase? A month-on-month change? It is not labelled. *cosmetic.* Use "↑ 7.00 €" with a tooltip "price went up".
- **11-recurring-list.desk.en, the "Running" sort order.** It is unclear. *slows a task.* Sort by next due date (which the "Next up" box already does) or by amount, and say which.
- **13-recurring-orbit.desk.en / .phone.de, the whole Orbit view.** It took about 20 seconds plus reading the paragraph to understand. Most dots have no label. On phone the planets overlap the "1.407 €" centre and the labels. Fun, but it answers no question the List does not answer better. *slows a task.* Make it optional or move it lower; at least label every dot.
- **11-recurring-list.phone.de, the "Laufend" rows.** The "in N days" due date is dropped on phone. *cosmetic.*
- **12-recurring-calendar.desk.en, the chips in day cells.** They are truncated to "Ha…", "Nor…", "Spar…". The side panel saves it. *cosmetic.*
- **keep:** 11-recurring-list.desk.en, the "What changed" sentences ("Disney+ stopped coming… That saves 119.88 € a year"). This is the best copy in the app.
- **keep:** 11-recurring-list.desk.en, the bottom card "3 savings plans run along: 1,100.00 € a month. They live under Net worth." It is good cross-navigation.

---

## 14 Net worth (14-networth.desk.en / .phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 Clarity | 9 | 14-networth.desk.en: "TODAY 44,931.92 € ↑13,592.05 €" plus a rising line |
| 2 Hierarchy | 8 | 14-networth.desk.en: total, then account cards, then savings plans |
| 5 Nav/naming | 6 | 14-networth.desk.en: only the "Direkt-Depot" card has a chevron. Girokonto and Extra-Konto look clickable but give no hint |
| 6 Consistency | 6 | 14-networth.desk.en: the period says "Jan – Oct 2026" but the chart starts "Dec 25" |
| 3,4,7,8,9 | - | |

Findings
- **14-networth.phone.de, bottom nav.** "Vermögen" is the only way to reach Depot, Prognose, Analyse and Einzahlungen, and it is only through the Direkt-Depot card chevron. A first-time phone user will not find investments. *slows a task.*
- **keep:** 14-networth.desk.en, the dashed "Add account" card with "Say a house or a car loan outside your banks".

## 15–19 Investments (15-investments, 16-inv-forecast, 17-inv-analysis, 18-inv-payments, 19-etf; desk.en / phone.de / phone.en)

**What is this?** My ETF depot. **Most important?** "9,350.57 €" depot value. **Next click?** A holding card.

| Line | Score | Based on |
|---|---|---|
| 1 Clarity | 7 | 15-investments.desk.en: "DEPOT VALUE ON 30 OCT 2026 9,350.57 €" is clear. The waterfall bars under the chart need the legend to understand |
| 2 Hierarchy | 7 | 16-inv-forecast.desk.en: "68,412 €" with a bad/good-case slider is a strong focal point |
| 5 Nav/naming | 4 | 15-investments.desk.en nav "Investments" vs 15-investments.phone.de "Depot" vs 14-networth "Direkt-Depot" vs 15-investments.desk.en "85% of the depot" |
| 6 Consistency | 4 | 15-investments.phone.de tabs are Überblick, Prognose, Analyse, Einzahlungen; 19-etf.phone.de tabs are Überblick, Analyse, Prognose, Fakten (different order) |
| 3,4,7,8,9 | - | |

Findings
- **18-inv-payments.desk.en, nav label "Payments".** It sounds like bills, but the page is "Money put in" (deposits). The German "Einzahlungen" is right. *slows a task.* Rename it "Deposits" or "Money put in".
- **18-inv-payments.desk.en, the row action "× Not counted".** It reads as a status ("this is not counted"), not as a button. The German "Nicht zählen" is clearer. *slows a task.* Use "Don't count".
- **16-inv-forecast.desk.en "Swing 15% a year" vs 17-inv-analysis.desk.en "Ups and downs ±17%".** These are two names and two numbers for volatility. A newcomer will ask which one is right. *slows a task.* Use one name and explain the difference (forecast assumption vs measured).
- **15-investments.desk.en "+7.5% · 474 €" on the holding card vs 19-etf.desk.en "+1,160.97 € · +17.2%" for the same ETF.** Both are probably correct (period vs since purchase), but neither says which. *slows a task.* Add "in period" or "since first buy".
- **16-inv-forecast.desk.en, the "Expected return" box.** "+13.5% a year over 2.3 years (counts 19%), the rest is the long-run 6%" is jargon. *cosmetic.*
- **17-inv-analysis.desk.en, "☐ Outlined: the best and the worst month".** It is drawn as a checkbox but is a legend. *cosmetic.*
- **17-inv-analysis.phone.de, "Monatsrenditen".** It is cut at "Jun" with no hint that it scrolls sideways. *cosmetic.*
- **15-investments.phone.de / 17-inv-analysis.phone.de, the tab bar.** "Einzahlungen" is cut at the right, and on 17 "Überblick" is cut at the left. *cosmetic.*
- **19-etf.desk.en.** The justETF opt-in banner is placed above the actual content. It is also repeated at the bottom of 15-investments.desk.en. *cosmetic.* Show it once.
- **18-inv-payments.desk.en, "Import price history".** It sits on the deposits page, where I would not look for it. *cosmetic.*
- **keep:** 16-inv-forecast.desk.en, "800 simulated futures… Assumptions, not a promise." plus the milestone chips "25,000 € in 2030". These are honest and understandable.
- **keep:** 17-inv-analysis.desk.en, "Your money +6.7% / The funds themselves +6.3% / About what the funds themselves made." This turns a hard concept into a sentence.

---

## 20–27, 30 Settings (desk.en / phone.de, plus 20 desk.de)

**What is this?** Settings with 8 tabs. **Most important?** The bank connection. **Next click?** "Sync now".

| Line | Score | Based on |
|---|---|---|
| 1 Clarity | 7 | 20-settings-bank.desk.en: the "Bank login needed within 90 days" bar with an explanation |
| 2 Hierarchy | 7 | 20-settings-bank.desk.en: the primary "Sync now" is gold. "I logged in to my bank" is a mysterious secondary button until you read the paragraph |
| 5 Nav/naming | 5 | 25-settings-privacy.desk.en: the tab "Export & privacy" has no setting for the "hide amounts" privacy mode; 21-settings-categories.desk.en: "That's you" as a section title |
| 6 Consistency | 3 | 20-settings-bank.desk.en "Every day at 06:00" vs "Next sync tomorrow at 05:00"; 24-settings-backup.desk.en "Time of day 03:00" vs "Next backup tomorrow at 02:00" |
| 3,4,7,8,9 | - | |

Findings
- **20-settings-bank.desk.en, "Sync schedule".** It is set to 06:00 but says the next sync is at 05:00. **24-settings-backup.desk.en** has the same off-by-one-hour mismatch (03:00 vs 02:00). Users will stop trusting the scheduler. *slows a task.*
- **21-settings-categories.desk.en, "Categorizer".** "Built-in model" is selected, the subtitle says "built-in model not found", and a green "Offline" badge sits beside it. These are three contradicting signals. *slows a task.* Say "Built-in model missing; using spelling matcher" in amber.
- **21-settings-categories.desk.en, "Needs review" vs "Transactions, To review".** The same feature has two names in one sentence. *cosmetic.*
- **22-settings-hints.desk.en "Keep aside" vs 01-overview "Put aside".** In German both are "Zurücklegen" / "Zurückgelegt" but they mean different things: a cushion deducted from free money vs money moved to savings. *slows a task.* Rename the setting "Safety cushion" / "Notgroschen".
- **25-settings-privacy.desk.en, "Connection log: No outgoing connections in the last 7 days".** The sidebar says "ING connected · Synced just now". That is contradictory for a privacy page. *slows a task.* Either exclude the bank in the wording ("besides your bank") or count it.
- **25-settings-privacy.desk.en, "Backups never contain the key…" under Export.** It is duplicated from 24 and misplaced. *cosmetic.*
- **26-settings-security.desk.en.** The banner says "Passkeys don't work at 127.0.0.1", yet the device list shows "Chrome on Mac · with passkey". *cosmetic*, but it confuses.
- **26-settings-security.desk.en, the "Password login" row.** It has no control, so it looks like a missing toggle. *cosmetic.*
- **23-settings-depot.desk.en, "Used for the Sharpe ratio".** There is no Sharpe ratio visible on 17-inv-analysis. **23-settings-depot.phone.de** shows "1.75" with a decimal point in German. *cosmetic.*
- **20-settings-bank.phone.de / 22-settings-hints.phone.de.** The segmented controls are clipped ("7 Tage vorhe", "Buchungsmon"), and the settings tab bar is clipped on both sides (26: "ort & Datenschutz"). *cosmetic.*
- **30-settings-connect-dialog.desk.en.** "No bank found by that name" shows before I typed anything, and the only button is "Done, start syncing" at step one. It feels like an error state. *slows a task.* Show the hint only after input, and use "Next" until the bank is found.
- **27-settings-account.desk.en, "Country: Not chosen".** This is right after a wizard that asked "Where do you live?" (41). *cosmetic.*
- **keep:** 20-settings-bank.desk.en, the toggles in "Accounts shown" with balances. 22-settings-hints.desk.en: every hint type is one plain sentence plus a toggle.
- **keep:** 24-settings-backup.desk.en, the "Smart Recycle · Recommended" vs "Custom" choice. The timeline is clear on desktop, though cramped on phone.de.

## 31 / 32 Hidden amounts (31-hidden-overview.desk.en, 32-hidden-investments.phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 Clarity | 6 | 31-hidden-overview.desk.en: the blurred 9s read as "hidden", but the only toggle state shown is the gold eye icon next to the logo |
| 5 Nav/naming | 5 | 31-hidden-overview.desk.en: there is no "Amounts hidden" label; percentages and "39%" stay visible with no explanation of what is kept |
| 2,3,4,6,7,8,9 | - | |

Findings
- **31-hidden-overview.desk.en, the eye icon.** Add a visible "Amounts hidden" chip so the user knows how to undo it. *slows a task.*
- **keep:** 32-hidden-investments.phone.de, the blur keeps layout and percentages, so the screen stays readable for screen-sharing.

## 40–42 Wizard and login (desk.en / phone.de)

| Line | Score | Based on |
|---|---|---|
| 1 Clarity | 8 | 40-wizard-account.desk.en: "Welcome to Groschen… about five minutes… stays on your server" |
| 2 Hierarchy | 8 | 40-wizard-account.desk.en: the 5-step rail with subtitles |
| 5 Nav/naming | 6 | 40-wizard-account.phone.de: only 5 unlabeled progress bars, so you cannot tell what is next; 40-wizard-account.desk.en step "Smart features · Offline, sync, reminders" is vague |
| 6 Consistency | 5 | 41-wizard-country.phone.de: "keine Zugangsschlüssel, die ablaufen", while 20-settings-bank needs a bank login every 90 days |
| 3,4,7,8,9 | - | |

Findings
- **41-wizard-country.phone.de, the footer.** "Überspringen, vorerst CSV-Dateien nu…" overflows the card, and "Weiter" sits misaligned below it. *slows a task.*
- **41-wizard-country.phone.de, "Keine Bank mit diesem Namen gefunden".** It shows on an empty field, the same as in 30. *cosmetic.*
- **41-wizard-country.phone.de, "nothing expires" promise vs the 90-day re-login in 20-settings-bank.** First-run copy should not contradict the first settings page. *slows a task.*
- **42-login.desk.en.** There is no passkey button, although Security talks about passkeys. "Log in" looks disabled until filled. *cosmetic.*
- **keep:** 40-wizard-account.desk.en, the footer "You can change everything later under Settings. There are no config files to edit." It is reassuring.

---

## Top 10

1. **10-drill-category.desk.en, "Income 0.00 €"** while Overview shows 33,538.60 € income. A newcomer will think the data is broken. Hide empty categories, or point to the Salary/income group. *blocks a task*
2. **12-recurring-calendar.desk.en vs 11-recurring-list.desk.en: two "fixed costs" totals** (2,523.48 € this month vs 1,407.01 € per month). The calendar mixes in savings plans and salary. Rename it or split it. *slows a task*
3. **03-transactions-review.desk.en, "Needs review" is defined three ways.** Overview says "check what I sorted", the banner says "need a category from you", and there is a separate "Uncategorized" tab. Pick one meaning and match the copy. *slows a task*
4. **Investments naming is a mess:** "Investments" / "Depot" / "Direkt-Depot"; "Payments" means deposits; "Not counted" is an action, not a status (15-investments.desk.en, 18-inv-payments.desk.en). *slows a task*
5. **01-overview.desk.en, the savings vocabulary.** "Saved", "Put aside", "Invested", "Stays on the account", plus "Keep aside" in 22-settings-hints. The Saved caption does not add up. Define one set of terms. *slows a task*
6. **07-spending.phone.de, two stacked toggles that both start with "Ausgaben"**, and fixed costs and investments are missing from the phone bottom nav (14-networth.phone.de). Phone users will get lost. *slows a task*
7. **Schedule times contradict their settings:** 20-settings-bank.desk.en (06:00 vs next sync 05:00) and 24-settings-backup.desk.en (03:00 vs 02:00). *slows a task*
8. **Two volatility figures with two names:** 16-inv-forecast "Swing 15%" vs 17-inv-analysis "Ups and downs ±17%". Also two gain figures for the same ETF (15 "+7.5%" vs 19 "+17.2%") with no "since when". *slows a task*
9. **13-recurring-orbit.desk.en / .phone.de.** The "Orbit" view is unlabeled, needs a paragraph of explanation, and overlaps itself on phone. Demote it or label every dot. *slows a task*
10. **Unlabeled controls a newcomer must guess at:** the sidebar eye or privacy toggle with no "Amounts hidden" state (01/31), the jar graphic in the hero (01-overview.desk.en), and the amber "+7.00 €" badges (11-recurring-list.desk.en). *slows a task*

**Keep:** the hero sentence "That's about 184.67 € per day" (01), the "What changed" sentences (11), "Your money vs the funds themselves" (17), the refund strikethrough and progress (02), and the wizard reassurance footer (40).
