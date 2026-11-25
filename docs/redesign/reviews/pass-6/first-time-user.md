# Groschen: first-time user review

Role: first-time user. I have never seen this app. For each screen I ask three things: what is this, what matters most here, and what would I click next. Anything that took me more than about five seconds to work out is a finding.
Lines scored: 1 clarity of purpose, 2 hierarchy, 3 task efficiency, 5 navigation and naming, 6 consistency, 7 phone experience. I put "-" on 4 data presentation, 8 accessibility and 9 visual craft, because they fall outside this role. Where I mention them, it is only because they got in the way of understanding.

Screens checked: every `desk.en` and every `phone.de`, plus `20-settings-bank.desk.de` for German label length. I cut the 5200 px tall captures into slices to read them.

---

## Global navigation (all screens)

| Line | Score | Based on |
|---|---|---|
| 1 clarity | 8 | `01-overview.desk.en`: sidebar labels Overview / Transactions / Spending / Net worth read like a finance app straight away |
| 2 hierarchy | 6 | `01-overview.desk.en`: sidebar tree nests "Fixed costs" under Spending, and Investments (with Analysis / Forecast / Pay-ins) under Net worth, three levels deep |
| 5 navigation/naming | 5 | `15-investments.desk.en` "Investments" vs `15-investments.phone.de` tab "Depot" vs `14-networth.desk.en` card "Direkt-Depot" vs `19-etf.desk.en` second-level tabs "Analysis / Forecast" |
| 6 consistency | 6 | `01-overview.desk.en` "Worth a look" rows have no dismiss X; `01-overview.phone.de` has an X on each row |
| 7 phone | 7 | `01-overview.phone.de`: bottom bar Übersicht / Umsätze / Ausgaben / Vermögen plus secondary tabs (`07-spending.phone.de` "Ausgaben | Fixkosten") work well. The settings gear sits only in the top bar |

Findings
- **G1** `01-overview.desk.en`: the unlabeled eye icon next to the "Groschen" logo. I could not guess that it hides amounts until I saw `31-hidden-overview`. It sits where a logo action normally goes. **slows a task**. Suggestion: give it a tooltip and label ("Hide amounts"), or put it next to the period picker.
- **G2** `15-investments.desk.en` / `19-etf.desk.en`: Investments has two layers of "Analysis" and "Forecast". The sidebar Analysis/Forecast cover the whole depot, and the ETF page has its own Overview / Analysis / Forecast / Facts tabs. As a newcomer I could not tell which "Forecast" I was looking at. **slows a task**. Suggestion: rename the sidebar entries "Depot analysis" / "Depot forecast", or drop the per-ETF duplicates.
- **G3** EN naming drift for one thing: sidebar "Investments", card "Direkt-Depot", page eyebrow "DEPOT VALUE", settings tab "Investments", and the DE UI uses "Depot" everywhere (`20-settings-bank.desk.de`). **cosmetic**. Suggestion: pick one term per language ("Depot" also works in English for this audience).
- **G4** `01-overview.desk.en` sidebar: the orange dot after "Overview" and the "39" badge after "Transactions" look alike, but I cannot tell what the dot means. **cosmetic**.
- **keep** `01-overview.desk.en`: "ING connected · Synced just now" status card in the sidebar foot. It tells me at once that data is live.
- **keep** `07-spending.phone.de`, `15-investments.phone.de`: on phone, the secondary pages become a top tab strip under the section. That is clear and easy to reach with a thumb.

---

## 01 Overview (`01-overview.*`)

What is it: my money right now. Most important: "Available until payday 5,170.65 €". Next click: "Check" (39 sorted transactions) or the "14 payments still to come" link.

| Line | Score | Based on |
|---|---|---|
| 1 | 9 | `01-overview.desk.en` "AVAILABLE UNTIL PAYDAY 5,170.65 € · That's about 184.67 € per day" hero |
| 2 | 8 | `01-overview.desk.en`: hero → Worth a look → Income/Spending/Saved → flow chart, top to bottom by importance |
| 3 | 8 | `01-overview.desk.en` "Worth a look" rows each carry one action button (Check / Show) |
| 4 | - | |
| 5 | 7 | `01-overview.desk.en` Sankey labels "Put aside" vs "Stays on the account" vs "Invested" |
| 6 | 6 | `01-overview.desk.en` "Housing 35.6%" in the Sankey vs `07-spending.desk.en` "Housing 58.3%" |
| 7 | 7 | `01-overview.phone.de` "Zeig auf ein Band, um ihm zu folgen" hover instruction on a touch screen |

Findings
- **O1** `01-overview.desk.en` payday strip (row of small pills with red dots, a coin at the end): it took me well over five seconds. The red dots are payments and the coin is payday, but nothing says so. The "14 payments still to come" link underneath is the real explanation. **slows a task**. Suggestion: add a tiny legend or tooltip ("● payment due"), or make the whole strip open `34-payday-details`.
- **O2** `01-overview.desk.en` vertical "glass" gauge right of the hero: I could not tell what the fill level stands for (share of month left? share of money left?). **cosmetic**. Suggestion: label it ("62 % of salary left") or drop it.
- **O3** `01-overview.desk.en` vs `07-spending.desk.en`: Housing is 35.6 % on Overview (share of income) and 58.3 % on Spending (share of spending). Seeing two different percentages for the same category made me doubt the numbers. **slows a task**. Suggestion: say "of income" in the Sankey percentage label.
- **O4** `01-overview.phone.de` "Wohin das Geld geflossen ist": the subtitle tells phone users to point at a band ("Zeig auf ein Band"), which you can't do on a phone. **cosmetic**. Suggestion: use "Tippe auf ein Band" on touch devices.
- **O5** `01-overview.desk.en` "Worth a look" first hint "Groschen sorted 39 transactions on its own": the same 39 shows as "Needs review 39" in Transactions, but that tab then says "8 transactions" (see T2). **slows a task**.
- **keep** `01-overview.desk.en` hero sentence "That's about 184.67 € per day". It is the single most useful number in the app for a newcomer.
- **keep** `01-overview.desk.en` "Saved" card that splits invested / put aside / stays, with a savings-rate ring.

---

## 34 Payday details (`34-payday-details.*`)

| Line | Score | Based on |
|---|---|---|
| 1 | 9 | `34-payday-details.desk.en` "Balance now − Still going out (14 payments) = Free to spend" |
| 2 | 9 | `34-payday-details.desk.en`: the sum sits at the top in green, the itemized list below |
| 3 | 8 | `34-payday-details.desk.en` "All fixed costs" footer button |
| 5 | 7 | `34-payday-details.desk.en` title "Available until payday" vs row "Free to spend": two names for the same number |
| 7 | 8 | `34-payday-details.phone.de` full-height sheet, list readable |

- **keep** `34-payday-details.desk.en`: this dialog explains the hero number perfectly. It should be the first thing a new user sees when they click the hero, and the hero/strip should open it (see O1).
- **P1** `34-payday-details.desk.en` rows "Sparen" / "Sparplan …" counted as "still going out": a newcomer may not expect savings to lower "free to spend". **cosmetic**. Suggestion: sub-total "of which savings 1,100 €".

---

## 31 / 32 Hidden amounts (`31-hidden-overview.*`, `32-hidden-investments.*`)

| Line | Score | Based on |
|---|---|---|
| 1 | 7 | `31-hidden-overview.desk.en` blurred "9,999.99 €" hero with the eye icon highlighted at top left |
| 6 | 8 | `32-hidden-investments.desk.en`: chart axes, bar labels and plan chips are all blurred the same way |
| 7 | 8 | `31-hidden-overview.phone.de` active eye button in the top bar is clearly highlighted |

- **H1** `31-hidden-overview.desk.en`: the only sign that privacy mode is on is the small highlighted eye at the top left. A newcomer who turned it on by accident may think the data is broken. **slows a task**. Suggestion: add a small "Amounts hidden" pill next to the page title.
- **keep** `31-hidden-overview.desk.en`: blurred digits keep the layout identical, so screenshots stay useful.

---

## 02 / 04 / 06 Transactions list (`02-transactions.*`, `04-transactions-filtered.*`, `06-transactions-empty.*`)

What is it: every booking. Most important: the list itself. Next click: a row (to edit) or "Needs review".

| Line | Score | Based on |
|---|---|---|
| 1 | 9 | `02-transactions.desk.en` title "Transactions", search, day-grouped rows with merchant logos |
| 2 | 7 | `02-transactions.desk.en`: search, segmented filter, Filter, sort and period picker all in one row; the summary line "297 transactions 42,057.91 € in 31,970.76 € out" is small grey text |
| 3 | 8 | `04-transactions-filtered.desk.en` "Clear filters" link right in the summary line |
| 5 | 6 | `02-transactions.desk.en` segmented control "All / Needs review 39 / Uncategorized / Income" |
| 6 | 6 | `02-transactions.desk.en` summary "42,057.91 € in" vs `01-overview.desk.en` "Income 33,538.60 €" for the same period |
| 7 | 7 | `02-transactions.phone.de`: search placeholder cut off ("…Kategorie oder Betr"); filter tabs fit; amounts right-aligned and readable |

Findings
- **T1** `02-transactions.desk.en` summary "42,057.91 € in / 31,970.76 € out" vs Overview "Income 33,538.60 € / Spending 20,451.45 €" for the same Jan–Oct period. Presumably transfers between own accounts are included here, but nothing says so. I don't know which number to trust. **slows a task**. Suggestion: add "incl. transfers" or show the same figures as Overview.
- **T2** `02-transactions.desk.en` "Needs review 39" vs "Uncategorized" tabs: what is the difference? After clicking (see 03) the count changes to 8. **slows a task**. Suggestion: see R1.
- **T3** `02-transactions.desk.en` amber left bar on "Hofladen Sonnenfeld" and "Lena Berger" rows: unexplained marker. I guessed "needs attention" only after seeing screen 03. **cosmetic**. Suggestion: tooltip, or say "needs review" in the chip.
- **T4** `02-transactions.desk.en` "Lena Berger · 32.00 € of 64.00 € back" with a mini progress bar, and `02-transactions.phone.de` strikethrough "‑34,99 €" plus "Komplett zurückbekommen": a clever refund feature, but a first-timer meets it with no introduction. **cosmetic**. **keep** the strikethrough for fully refunded items. It is very readable.
- **T5** `02-transactions.desk.en` day header totals on the far right (e.g. "‑1,350.00 €" on 1 September, which mixes +800 and ‑800 transfers): it is not obvious whether this is net or out-only. **cosmetic**.
- **T6** `02-transactions.phone.de` search placeholder truncated ("Händler, Verwendungszweck, Kategorie oder Betr"). **cosmetic**. Suggestion: shorten to "Suchen…".
- **T7** `06-transactions-empty.phone.de`: about 110 px of empty space above the "Umsätze" title, so the page looks scrolled or broken (the same gap shows on `13-recurring-orbit.phone.de`). **cosmetic**.
- **keep** `06-transactions-empty.desk.en` empty state "No transactions match · Try a different search, filter or period" plus "Clear filters" link.
- **keep** `02-transactions.desk.en` merchant logos and sentence-case date headers ("WEDNESDAY 28 OCTOBER"). They make it easy to scan.

---

## 03 Needs review (`03-transactions-review.*`)

| Line | Score | Based on |
|---|---|---|
| 1 | 7 | `03-transactions-review.desk.en` banner "These transactions need a category from you." |
| 2 | 7 | `03-transactions-review.desk.en`: banner on top, list below; but no bulk action is visible |
| 3 | 5 | `03-transactions-review.desk.en`: six "Hofladen Sonnenfeld" rows, each must be opened on its own |
| 5 | 4 | `03-transactions-review.desk.en` tab "Needs review 39" selected, summary says "8 transactions" |
| 6 | 3 | `03-transactions-review.desk.en` summary "All periods · 8 transactions · 110,315.81 € in · 84,234.46 € out" while the picker still says "Jan – Oct 2026" |
| 7 | 7 | `03-transactions-review.phone.de` same list, readable, banner wraps fine |

- **R1** `03-transactions-review.desk.en`: the badge says 39, the list shows 8, and the banner says "need a category", which is what the separate "Uncategorized" tab is for. Overview's hint says the 39 are "sorted on its own, do they look right?". That is three different stories for one tab. **blocks a task** (I can't tell whether I am done reviewing). Suggestion: make the badge equal the list count; split "Check auto-sorted (31)" from "No category (8)", or merge the tabs.
- **R2** `03-transactions-review.desk.en` summary line: "110,315.81 € in / 84,234.46 € out" for 8 small transactions worth a few hundred euros. The totals clearly don't belong to the visible list, and "All periods" contradicts the "Jan – Oct 2026" picker. **slows a task**. Suggestion: total only the visible rows, and grey out or hide the period picker while it is ignored.
- **R3** `03-transactions-review.desk.en`: six rows from the same merchant, "Hofladen Sonnenfeld". The review flow should offer "Categorize all 6 from Hofladen Sonnenfeld" right on the banner. **slows a task**.

---

## 05 Edit transaction (`05-transactions-edit.*`)

| Line | Score | Based on |
|---|---|---|
| 1 | 8 | `05-transactions-edit.desk.en` header "Shell −56.30 € Wed, 28 Oct 2026 · Girokonto" with raw bank text below |
| 2 | 7 | `05-transactions-edit.desk.en`: the category chip cloud is the main body; the selected "Fuel" chip sits mid-list |
| 3 | 8 | `05-transactions-edit.desk.en` toggle "Use this category for every transaction from this merchant" on by default, next to Save |
| 5 | 7 | `05-transactions-edit.desk.en` "Housing (general)" naming for the parent category |
| 7 | 6 | `05-transactions-edit.phone.de`: the current category (Tanken, under Mobilität) is below the fold; the visible part shows only Wohnen / Essen & Trinken |

- **E1** `05-transactions-edit.phone.de`: when the sheet opens I can't see which category is currently selected, because it is below the fold. **slows a task**. Suggestion: show "Current: Tanken" under the amount, or scroll the selected chip into view.
- **E2** `05-transactions-edit.desk.en`: the dialog shows only category editing. Notes, split and "mark as refunded" (which exist given T4) are not discoverable here. "Everything with Shell ›" is the only other way out. **slows a task**. Suggestion: add a secondary row of actions (Note · Split · Refund).
- **keep** `05-transactions-edit.desk.en` "Use this category for every transaction from this merchant" toggle. It teaches the rule system without a separate rules screen.
- **keep** monospace raw bank text block. It lets me see what the bank actually sent.

---

## 07 Spending (`07-spending.*`) and 33 Period menu (`33-period-menu.*`)

What is it: where my money goes. Most important: breakdown bars with euro amounts. Next click: a group row (›).

| Line | Score | Based on |
|---|---|---|
| 1 | 8 | `07-spending.desk.en` "Spending breakdown 2,045.14 € a month on average, most on Housing (58%)" |
| 2 | 7 | `07-spending.desk.en`: donut plus bars side by side; "Your year in days" heatmap below |
| 3 | 8 | `07-spending.desk.en` chevrons on each group row lead to the drill-down |
| 5 | 5 | `07-spending.desk.en` ghost button "+ Your own group" above the card, next to the "Groups / Categories" toggle |
| 6 | 6 | `07-spending.desk.en` two segmented controls (Spending/Income at top right, Groups/Categories in the card) with the same look |
| 7 | 8 | `07-spending.phone.de`: donut, then list, then heatmap split into two half-year blocks. This works well |

- **S1** `07-spending.desk.en` "+ Your own group" vs the "Groups" toggle: "group" means two different things (the built-in category groups like Housing, and user-defined cross-category groups). I expected the button to add a row to the Groups list. **slows a task**. Suggestion: call custom ones "Projects" or "Tags", e.g. "+ New project (car, flat, trip)".
- **S2** `07-spending.desk.en` two-ring donut: the inner and outer rings are not labelled (groups vs categories?). The bar list already says everything, so the donut adds a question rather than an answer. **cosmetic**.
- **S3** `07-spending.desk.en` "Personal · more refunds than spending ‑162.37 €": a negative spending row is confusing at first glance. **cosmetic**. Suggestion: show it at the bottom as "Personal: net refund +162.37 €".
- **S4** `33-period-menu.desk.en`: the button reads "Jan – Oct 2026" while the menu calls it "Year to date". I also can't see which year "Year" means, and there is no custom range. **cosmetic**. Suggestion: the button label could say "Year to date (Jan–Oct 2026)".
- **keep** `07-spending.desk.en` "Your year in days" heatmap with its plain-language caption ("grey without spending, from violet to glowing yellow…") and the three stat callouts below.

---

## 08 New group dialog (`08-spending-group-dialog.*`)

| Line | Score | Based on |
|---|---|---|
| 1 | 8 | `08-spending-group-dialog.desk.en` intro "A custom group collects transactions across categories, for a car, a flat you rent out or a holiday…" |
| 2 | 6 | `08-spending-group-dialog.desk.en`: the category chips start right after Name/Icon with no "Pick categories" label |
| 3 | 7 | `08-spending-group-dialog.desk.en`: Cancel / Save fixed at the bottom |
| 5 | 6 | `08-spending-group-dialog.desk.en` title "New group" vs entry button "Your own group" vs settings "Custom groups" |
| 7 | 7 | `08-spending-group-dialog.phone.de` sheet scrolls, footer fixed |

- **D1** `08-spending-group-dialog.desk.en`: there is no heading or instruction above the chip cloud ("Which categories belong to it?"), and nothing shows how many are selected. **slows a task**.
- **keep** the one-sentence explanation at the top. It answered "what is this?" in under five seconds.

---

## 09 / 10 Drill-downs (`09-drill-group.*`, `10-drill-category.*`)

| Line | Score | Based on |
|---|---|---|
| 1 | 9 | `09-drill-group.desk.en` "SPENDING ‹ Food & Dining 3,480.29 €" |
| 2 | 8 | `09-drill-group.desk.en`: total + monthly bars, then Top merchants / Categories, then Transactions |
| 3 | 8 | `10-drill-category.desk.en` breadcrumb "SPENDING › FOOD & DINING", plus category filter chips above the transaction list |
| 5 | 8 | `10-drill-category.phone.de` breadcrumb "AUSGABEN › ESSEN & TRINKEN" |
| 6 | 7 | `09-drill-group.desk.en` "Food & Dining · 0×  0.00 €" and "Food delivery · 0×  0.00 €" rows shown with empty bars |
| 7 | 8 | `09-drill-group.phone.de` stacked layout, chart readable |

- **DR1** `09-drill-group.desk.en` "↑ 35 % vs. the period before": I could not tell what the period before is (Jan–Oct 2025? Mar–Dec 2025?). Also, red for "up" is clear for spending, but a tooltip with the comparison range is missing. **cosmetic**.
- **DR2** `09-drill-group.desk.en` Top merchants "8 of 9": there is no "show all" link. **cosmetic**.
- **DR3** `09-drill-group.desk.en` Categories card lists 0.00 € categories. **cosmetic**. Suggestion: hide zero rows.
- **keep** the breadcrumb plus period picker pattern on both drill levels. It is the clearest navigation in the app.

---

## 11 / 12 / 13 Fixed costs (`11-recurring-list.*`, `12-recurring-calendar.*`, `13-recurring-orbit.*`)

What is it: my recurring payments. Most important: "1,407.01 € a month" and "Next up". Next click: a row in "Running".

| Line | Score | Based on |
|---|---|---|
| 1 | 9 | `11-recurring-list.desk.en` "FIXED COSTS PER MONTH 1,407.01 € · 16,884.11 € a year, 13 recurring payments" |
| 2 | 8 | `11-recurring-list.desk.en`: hero + Next up, then What changed, then Running |
| 3 | 7 | `11-recurring-list.desk.en` "Show all 8", "Stopped (1)" expanders, savings-plan link at the bottom |
| 5 | 5 | `11-recurring-list.desk.en` section title "Running" and the view toggle "List / Calendar / Orbit" |
| 6 | 5 | `12-recurring-calendar.desk.en` "1,423.48 € fixed costs" vs `11-recurring-list.desk.en` "1,407.01 €" |
| 7 | 6 | `13-recurring-orbit.phone.de` orbit squashed to a 100 px blob with overlapping labels |

- **F1** `11-recurring-list.desk.en` "Running" list order: In 2 days, 3, 5, 16, 7, 19, 3, 15 Jan… It is actually sorted by monthly cost, but there is no sort label, so it looks random next to the "In N days" column. **slows a task**. Suggestion: add a header "by monthly cost" or a sort toggle.
- **F2** `11-recurring-list.desk.en` badges "+7.00 €", "+9.00 €", "Back", "New" next to names: "+7.00 €" could mean a price rise or a credit. **cosmetic**. Suggestion: write "↑ 7.00 €" with a tooltip ("price went up").
- **F3** `12-recurring-calendar.desk.en` header "1,423.48 € fixed costs" vs list hero "1,407.01 €": the difference between "this October's actuals" and "monthly average" is not explained. **slows a task**.
- **F4** `12-recurring-calendar.desk.en` truncated chips "Ha… ‑1,050 €", "Spar… ‑800 €", "+1" in cells that have plenty of room. The "Day by day" list on the right rescues it. **cosmetic**. The legend colors "Standing order" (teal) and "Salary" (green) are almost the same.
- **F5** `13-recurring-orbit.desk.en` "Your month in orbit": a nice visual, but most dots have no label and I needed the caption to decode it. On `13-recurring-orbit.phone.de` it is illegible. **cosmetic**. Suggestion: hide Orbit on phone, or make it the last option.
- **F6** "Running" (`11-recurring-list.desk.en`) is an unusual heading. "Active" reads better. **cosmetic**.
- **keep** `11-recurring-list.desk.en` "What changed" card ("Spotify got more expensive: 10.99 € → 11.99 €… 12.00 € more per year"). This is exactly what a newcomer wants to learn from fixed costs.
- **keep** `11-recurring-list.desk.en` footer "3 savings plans run along: 1,100.00 € a month. They live under Net worth." It explains where things are.

---

## 14 Net worth (`14-networth.*`)

| Line | Score | Based on |
|---|---|---|
| 1 | 9 | `14-networth.desk.en` "TODAY 44,931.92 € ↑ 13,592.05 €" with growth line |
| 2 | 8 | `14-networth.desk.en`: hero chart, account cards with share bars, then Savings plans |
| 3 | 7 | `14-networth.desk.en` "Add account: say a house or a car loan…" tile |
| 5 | 6 | `14-networth.desk.en`: only "Direkt-Depot" has a › chevron; Girokonto and Extra-Konto look identical but are not clickable (or are they?) |
| 6 | 6 | `14-networth.desk.en` chart starts at "Dec 25" while the picker says "Jan – Oct 2026" |
| 7 | 8 | `14-networth.phone.de` cards stack cleanly; "Läuft" badges readable |

- **N1** `14-networth.desk.en` account cards: one has a chevron and two don't, so I don't know where clicking Girokonto takes me. **slows a task**. Suggestion: make every account card open its filtered transaction list.
- **N2** `14-networth.desk.en` "↑ 13,592.05 €" here vs Overview "Saved 13,087.15 €": two similar but different "growth" figures with no explanation (market gains?). **cosmetic**.
- **keep** `14-networth.desk.en` Savings plans copy: "A plan shows up after its third payment and leaves once payments stop." Clear rules up front.

---

## 15 Investments (`15-investments.*`)

| Line | Score | Based on |
|---|---|---|
| 1 | 7 | `15-investments.desk.en` "DEPOT VALUE ON 30 OCT 2026 9,350.57 € ↑ 504.90 € · +6.7 %" |
| 2 | 7 | `15-investments.desk.en`: value chart, holdings cards, tax allowance, justETF banner |
| 3 | 7 | `15-investments.desk.en` holdings cards with › lead to ETF details |
| 5 | 5 | `15-investments.desk.en` legend "Value without deposits" on a chart whose axis runs 8k–10k € |
| 6 | 6 | `15-investments.desk.en` Vanguard card "+7.5 % · 474 €" vs `19-etf.desk.en` "+1,160.97 € · +17.2 %" for the same fund |
| 7 | 7 | `15-investments.phone.de` chart and gain/loss bars fit; pinch hint "Mit zwei Fingern vergrößern" is good |

- **I1** `15-investments.desk.en` legend "Value without deposits": I read the line as the depot value, then the legend says the deposits are taken out. I could not work out what the y-axis shows in five seconds. **slows a task**. Suggestion: "Depot value if you had paid nothing in this period" or default the "Money paid in" toggle to on.
- **I2** `15-investments.desk.en` vs `19-etf.desk.en`: the same fund shows +474 € (period) and +1,160.97 € (all time) with no "in this period" / "since purchase" label. **slows a task**.
- **I3** `15-investments.desk.en` justETF opt-in banner appears at the bottom here and at the top of `19-etf.desk.en`, which pushes the value down. **cosmetic**.
- **keep** `15-investments.desk.en` "Tax-free allowance 2026 95.40 € of 1,000.00 €" bar with "Adjust". It is valuable for a German user and needs no explanation.

---

## 16 Forecast (`16-inv-forecast.*`)

| Line | Score | Based on |
|---|---|---|
| 1 | 7 | `16-inv-forecast.desk.en` "Where it could go · 800 simulated futures… Assumptions, not a promise." |
| 2 | 7 | `16-inv-forecast.desk.en`: assumption cards first, then the result "68,412 € in 10 years" |
| 3 | 7 | `16-inv-forecast.desk.en` 1Y–30Y selector, "Adjust the numbers" link |
| 5 | 5 | `16-inv-forecast.desk.en` card "Expected return 7.4 % a year · The prices show +13.5 % a year over 2.3 years (counts 19 %), the rest is the long-run 6 %…" |
| 6 | 5 | `16-inv-forecast.desk.en` "Swing 15 % a year" vs `17-inv-analysis.desk.en` "Ups and downs ±17 %" |
| 7 | 7 | `16-inv-forecast.phone.de` assumptions in a 2×2 grid, chart below; long but complete |

- **FC1** `16-inv-forecast.desk.en` "Expected return" card text: I had to read it three times. **slows a task**. Suggestion: "7.4 % a year: a blend of your fund's recent +13.5 % and the long-term market average of 6 %".
- **FC2** `16-inv-forecast.desk.en` "Swing 15 %" vs `17-inv-analysis.desk.en` "±17 %": two names and two numbers for volatility. **slows a task**. Suggestion: one name ("Ups and downs") and explain why the numbers differ.
- **FC3** `16-inv-forecast.desk.en` Bad/Good case bar with a draggable-looking knob: it looks like a slider I should move, but it is an output. **cosmetic**.
- **FC4** The assumptions sit above the result, so a newcomer reads technical inputs before the answer. **cosmetic**. Suggestion: put "68,412 € in 10 years" first.
- **keep** "24,312 € more than the 44,100 € you'd have paid in" and "1 in 12 futures ends below what you paid in". These are plain-language risk statements.

---

## 17 Analysis (`17-inv-analysis.*`)

| Line | Score | Based on |
|---|---|---|
| 1 | 7 | `17-inv-analysis.desk.en` "Return in this period · Your money +6.7 % · The funds themselves +6.3 %" |
| 2 | 7 | `17-inv-analysis.desk.en`: return, then volatility, then drawdown, then monthly heat strip |
| 5 | 6 | `17-inv-analysis.desk.en` "Drawdown" is a jargon title, though the subtitle explains it |
| 6 | 6 | `17-inv-analysis.desk.en` checkbox "Outlined: the best and the worst month" |
| 7 | 8 | `17-inv-analysis.phone.de` monthly grid wraps into two rows of six; readable |

- **A1** `17-inv-analysis.desk.en` "☐ Outlined: the best and the worst month": it looks like a checkbox I can tick, but it is a legend. **cosmetic**. Suggestion: use an outlined swatch, not a checkbox.
- **A2** `17-inv-analysis.desk.en` "About what the funds themselves made.": a verdict line with little meaning for a newcomer. "Your timing added +0.4 %" would teach more. **cosmetic**.
- **keep** `17-inv-analysis.desk.en` drawdown chart with the lowest point labelled "‑12.7 % (Jun 26)" and the "0.9 % below its high" pill.

---

## 18 Pay-ins (`18-inv-payments.*`)

| Line | Score | Based on |
|---|---|---|
| 1 | 7 | `18-inv-payments.desk.en` "Money put in · Everything in the Investments category, plus…" |
| 2 | 7 | `18-inv-payments.desk.en` month accordion with total on the right |
| 3 | 7 | `18-inv-payments.desk.en` "× Don't count" per row |
| 5 | 6 | `18-inv-payments.desk.en` nav "Pay-ins", title "Pay-ins", card "Money put in", elsewhere "paid in" |
| 7 | 7 | `18-inv-payments.phone.de` long ISIN lines truncated ("iShs …") |

- **PI1** `18-inv-payments.desk.en` "Import price history" panel at the bottom of a page about pay-ins: misplaced. I'd look for it in Settings › Investments. **cosmetic**.

---

## 19 ETF detail (`19-etf.*`)

| Line | Score | Based on |
|---|---|---|
| 1 | 8 | `19-etf.desk.en` "Vanguard FTSE All-World · YOUR VALUE 7,910.97 € · 85 % of your depot" |
| 2 | 6 | `19-etf.desk.en`: the justETF banner sits above the value card |
| 5 | 5 | `19-etf.desk.en` tabs "Overview / Analysis / Forecast / Facts" duplicate the sidebar items (see G2) |
| 7 | 7 | `19-etf.phone.de`: the banner takes the first screen, and the value is below the fold |

- **ETF1** `19-etf.phone.de`: on phone the opt-in banner fills the first screen, so I see a privacy question before my own number. **slows a task**. Suggestion: move the banner below the chart, or make it a dismissible one-liner.
- **keep** `19-etf.desk.en` "Your average 110.71 €" dashed line and purchase dots on the price chart.

---

## 20–27 Settings (`20-settings-bank.*` … `27-settings-account.*`)

| Line | Score | Based on |
|---|---|---|
| 1 | 7 | `20-settings-bank.desk.en` tabs "Bank & import / Categories / Hints & salary / Investments / Backups / Export & privacy / Security / Account & look" |
| 2 | 7 | `20-settings-bank.desk.en` cards per topic, actions on the right |
| 3 | 6 | `20-settings-bank.desk.en` buttons "Sync now / I logged in to my bank / Change login details" |
| 5 | 5 | `22-settings-hints.desk.en` tab "Hints & salary" holds the payday logic behind the Overview hero |
| 6 | 6 | `25-settings-privacy.desk.en` sentence about backups and the bank PIN key appears under "Export" |
| 7 | 6 | `20-settings-bank.phone.de` horizontal tab strip cut mid-word ("Hinweise & Gehalt" clipped), with no scroll hint |

Findings
- **ST1** `20-settings-bank.desk.en` "I logged in to my bank" button: I had no idea why I would press this until I read the long paragraph (FinTS 90-day re-login). **slows a task**. Suggestion: show it only when the 90-day timer is under 15 days, and phrase it "I re-approved access in my ING app".
- **ST2** `22-settings-hints.desk.en` "Salary and free to spend" (salary month, "Keep aside"): these settings drive the most important number on Overview, but they sit in a tab called "Hints & salary". **slows a task**. Suggestion: a "Payday" tab, or a gear link on the Overview hero.
- **ST3** `21-settings-categories.desk.en` "Categorizer: Built-in model" selected, subtitle "(built-in model not found)", plus a green "Offline" badge. These are three contradicting signals. **slows a task**. Suggestion: show "Using spelling-based matching (model not installed)" in amber.
- **ST4** `23-settings-depot.desk.en` "Interest rate to compare with… Used for the Sharpe ratio": no Sharpe ratio appears anywhere on Analysis (`17-inv-analysis.desk.en`). **cosmetic**. Also `23-settings-depot.phone.de` shows "1.75" and "1000" without German formatting.
- **ST5** `24-settings-backup.desk.en`: "Smart Recycle" is selected, yet the Daily/Weekly/Monthly/Yearly steppers and the "How far back" slider are editable, so I could not tell whether editing them switches to Custom. The timeline asks me to "Point at a place", which phones can't do. **slows a task**. "Smart Recycle" stays in English in `24-settings-backup.phone.de`.
- **ST6** `25-settings-privacy.desk.en` "Connection log · No outgoing connections in the last 7 days" while the sidebar says "Synced just now" with ING. This looks contradictory. **slows a task**. Suggestion: "No connections except to your bank".
- **ST7** `26-settings-security.desk.en` warning "Passkeys don't work at 127.0.0.1" and no "Add passkey" button, while "Chrome on Mac · with passkey" is listed below. **cosmetic** (demo artifact, but confusing).
- **ST8** `27-settings-account.desk.en` "Country: Not chosen", although the wizard (`41-wizard-country`) asks for it. **cosmetic**.
- **ST9** `20-settings-bank.phone.de` tab strip: the tabs scroll sideways and are clipped at the edge with no fade or arrow. Eight tabs is a lot on a phone. **slows a task**. Suggestion: a settings index list on phone.
- **keep** `20-settings-bank.desk.en` "Bank login needed within 90 days" progress bar with an exact date.
- **keep** `22-settings-hints.desk.en` hint toggles with one-line explanations ("Double charges: the same amount from the same merchant within a few days").
- **keep** `21-settings-categories.desk.en` "That's you: money sent to these names stays yours". This is an unusual concept explained in one line.

---

## 30 Connect bank dialog (`30-settings-connect-dialog.*`)

| Line | Score | Based on |
|---|---|---|
| 1 | 8 | `30-settings-connect-dialog.desk.en` "Connect your bank · Bank name, Bankleitzahl or IBAN" |
| 3 | 6 | `30-settings-connect-dialog.desk.en` only button "Done, start syncing" before anything is entered |
| 5 | 6 | `30-settings-connect-dialog.desk.en` German term "Bankleitzahl" in the English UI |
| 7 | 8 | `30-settings-connect-dialog.phone.de` centered sheet, readable |

- **C1** `30-settings-connect-dialog.desk.en` "Done, start syncing" as the first and only action of a one-field step: it promises the end of a flow that hasn't started (login and TAN are still to come). **slows a task**. Suggestion: "Continue".

---

## 40 / 41 First-run wizard (`40-wizard-account.*`, `41-wizard-country.*`)

| Line | Score | Based on |
|---|---|---|
| 1 | 9 | `40-wizard-account.desk.en` "Welcome to Groschen · It takes about five minutes, and everything you enter stays on your server." |
| 2 | 8 | `40-wizard-account.desk.en` step list Welcome / Connect your bank / Import history / Smart features / First sync |
| 3 | 7 | `41-wizard-country.desk.en`: country choice explains straight away that auto sync is Germany-only |
| 5 | 6 | `41-wizard-country.desk.en` step label "Connect your bank · Over FinTS" stays even after "United Kingdom" (CSV only) is chosen |
| 7 | 5 | `40-wizard-account.phone.de`: the step names are replaced by five unlabelled progress bars; there is no Back button on desktop or phone |

- **W1** `40-wizard-account.phone.de` / `41-wizard-country.phone.de`: on phone I lose the step names, so I don't know what "5 minutes" holds, and neither size has a Back button. **slows a task**. Suggestion: "Schritt 2 von 5 · Bank verbinden" above the bars, plus a Back link.
- **W2** `41-wizard-country.phone.de`: "Überspringen, vorerst CSV-Dateien nutzen" is a centered, two-line, text-only link next to the "Weiter" button, and it is easy to miss. **cosmetic**.
- **keep** `40-wizard-account.desk.en` side note "You can change everything later under Settings. There are no config files to edit." This is very reassuring for a self-hoster.

## 42 Login (`42-login.*`)

| Line | Score | Based on |
|---|---|---|
| 1 | 9 | `42-login.desk.en` "Groschen · Welcome back", two fields, one button |
| 3 | 7 | `42-login.desk.en`: no passkey button, although Settings › Security promotes passkeys |
| 7 | 9 | `42-login.phone.de` centered card, large fields |

- **keep** language picker right on the login card.

---

## Top 10

1. **R1 – blocks a task** `03-transactions-review.desk.en`: "Needs review 39" badge vs 8 rows vs banner "need a category" vs Overview "sorted 39 on its own, do they look right?". I cannot tell when I'm done reviewing. Make the badge match the list, and separate "check auto-sorted" from "no category".
2. **R2 – slows** `03-transactions-review.desk.en`: summary "All periods · 8 transactions · 110,315.81 € in · 84,234.46 € out" doesn't match the 8 visible rows or the "Jan – Oct 2026" picker. Total only what is shown.
3. **O1 – slows** `01-overview.desk.en`: the payday pill strip (red dots, coin) needs a legend, and clicking it should open the excellent `34-payday-details` breakdown.
4. **G2 / ETF – slows** `19-etf.desk.en` tabs "Analysis / Forecast" duplicate the sidebar "Analysis / Forecast" under Investments, and EN mixes "Investments / Depot / Direkt-Depot". Settle on one name and one level.
5. **T1 / O3 – slows** `02-transactions.desk.en` "42,057.91 € in" vs `01-overview.desk.en` "Income 33,538.60 €", and Housing 35.6 % vs 58.3 % (`07-spending.desk.en`). Label what each total includes ("incl. transfers", "of income").
6. **ST2 – slows** `22-settings-hints.desk.en`: the payday/salary settings that drive the Overview hero are hidden in "Hints & salary". Link them from the hero or give them a "Payday" tab.
7. **I1 / I2 – slows** `15-investments.desk.en` "Value without deposits" legend is unclear, and fund gains differ between `15-investments` (+474 €) and `19-etf` (+1,160.97 €) without saying "this period" vs "since purchase".
8. **FC1 / FC2 – slows** `16-inv-forecast.desk.en` jargon-heavy "Expected return" card, and volatility named "Swing 15 %" here but "Ups and downs ±17 %" on `17-inv-analysis.desk.en`.
9. **F1 / F3 – slows** `11-recurring-list.desk.en` "Running" list sorted by monthly cost with no label (looks random), and `12-recurring-calendar.desk.en` 1,423.48 € vs list 1,407.01 € unexplained.
10. **W1 / ST9 – slows (phone)** `40-wizard-account.phone.de` unlabelled progress bars with no Back button, and `20-settings-bank.phone.de` 8-tab horizontal strip clipped with no scroll hint.

Must keep: the "Available until payday … about 184.67 € per day" hero, the `34-payday-details` breakdown, the "What changed" card on Fixed costs, the breadcrumbs on drill-downs, and the plain-language captions under every chart.
