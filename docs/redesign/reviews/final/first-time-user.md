# Groschen: first-time user review (pass 8)

Role: someone opening Groschen for the first time. For each screen I answer three questions: what is this, what matters most here, and what would I click next. Anything that took me more than about five seconds to work out is a finding. I scored only lines 1 (clarity of purpose), 2 (hierarchy), 5 (navigation and naming) and, where I could judge it from a first-timer's view, 3 (task efficiency) and 7 (phone experience). All other lines are "-".

Severity scale: `blocks a task` / `slows a task` / `cosmetic`. Things that work and should stay are marked `keep`.

---

## Global navigation (seen on every screen)

- **What is it:** a left sidebar on desktop (Overview, Transactions, Spending > Fixed costs, Net worth > Investments > Analysis / Forecast / Pay-ins, then Settings at the bottom). On phone it is a 4-tab bottom bar (Übersicht, Umsätze, Ausgaben, Vermögen) plus tabs inside each section.
- **Findings**
  - `01-overview.desk.en`, sidebar: the tree goes three levels deep (Net worth > Investments > Analysis). I could not tell whether "Analysis" and "Forecast" are about my whole money or only the ETFs until I opened them. Severity: slows a task. Suggestion: rename them "Depot analysis" / "Depot forecast", or show them only as tabs on the Investments page.
  - `01-overview.desk.en` vs `01-overview.desk.de`, sidebar: the English UI says "Investments" while German says "Depot". The English screens then mix both words: "Direkt-Depot" card (`14-networth.desk.en`), "DEPOT VALUE ON 30 OCT" and "85% of the depot" (`15-investments.desk.en`). A newcomer reads these as two different things. Severity: slows a task. Suggestion: pick "Portfolio" or "Depot" in English and use that one word everywhere.
  - `01-overview.desk.en`, "Pay-ins" in the sidebar: the name means nothing to me without context. I guessed income. Severity: slows a task. Suggestion: "Money paid in" (the page's own heading) or "Contributions".
  - `01-overview.phone.de`, bottom bar: "Fixkosten" is not a bottom tab. It is only a tab inside Ausgaben (`11-recurring-list.phone.de`). That is findable, but only after you think to look under Ausgaben. Severity: cosmetic. `keep` the top sub-tabs on phone ("Ausgaben | Fixkosten", "Depot | Analyse | Prognose | Einzahlungen"). They make the hierarchy obvious.
  - `01-overview.desk.en`, the small eye icon next to the logo: I could not tell what it does until I saw `31-hidden-overview`. Severity: cosmetic. Suggestion: add a tooltip or label, "Hide amounts".
  - `01-overview.desk.en`, the "ING connected / Synced just now" card in the sidebar footer: `keep`. It is reassuring and clear.
  - `01-overview.desk.en`, the orange dot next to "Overview" in the sidebar: it is not explained. The phone has the same dot on the Umsätze tab. Severity: cosmetic.

---

## 01 Overview (`01-overview.desk.en`, `.desk.de`, `.phone.de`, `.phone.en`)

- **What is this?** A home dashboard. Within 2 seconds the big "AVAILABLE UNTIL PAYDAY 5,170.65 €" tells me the answer to "how much can I spend".
- **Most important:** the payday hero. **Next click:** "Worth a look > Check", or "14 payments still to come".

| Line | Score | Based on |
|---|---|---|
| 1 Clarity of purpose | 9 | `01-overview.desk.en`: "Available until payday" hero with "That's about 184.67 € per day" |
| 2 Hierarchy | 8 | `01-overview.desk.en`: hero, then "Worth a look", then the Income/Spending/Saved row, then the Sankey, in clear descending order |
| 3 Task efficiency | 8 | `01-overview.desk.en`: "Check" / "Show" buttons inside "Worth a look" |
| 4 | - | |
| 5 Navigation and naming | 7 | `01-overview.desk.en`: "Worth a look", "Put aside" vs "Stays on the account" in the Sankey |
| 6 | - | |
| 7 Phone experience | 8 | `01-overview.phone.de`: the cards stack well, and the Sankey is readable at 390 px |
| 8, 9 | - | |

**Findings**
- `01-overview.desk.en`, "Available until payday" hero: `keep`. It is the clearest first-screen answer in the app.
- `01-overview.desk.en`, the glass/jar graphic on the right of the hero: I spent time wondering whether it shows a percentage. It has no label or scale. Severity: cosmetic. Suggestion: label it (for example "62% of salary left") or drop it.
- `01-overview.desk.en`, the payday bead track (the row of dots between "TODAY" and the € coin): I could not decode the red/pink dots versus the grey beads without hovering. Severity: cosmetic. Suggestion: a one-line legend ("dot = a payment due").
- `01-overview.desk.en`, the Saved card: "3,000.00 € invested · 8,095.40 € put aside · 1,991.75 € stays" is a three-part split crammed into two lines next to a tiny ">" chevron. Severity: cosmetic.
- `01-overview.desk.en`, "Worth a look" first hint: "Groschen sorted 39 transactions on its own. Do the categories look right?" This contradicts the screen it leads to (see 03): there the banner says the transactions "need a category from you" and only 8 rows show. Severity: slows a task.
- `01-overview.desk.en`, the "Where the money went" Sankey: `keep`. The labels and percentages are readable, and "Point at a band… click to see its transactions" tells me what to do next.

---

## 02 Transactions, 03 Needs review, 04 Filtered, 06 Empty

Files: `02-transactions.*`, `03-transactions-review.*`, `04-transactions-filtered.*`, `06-transactions-empty.*`

- **What is this?** The bank statement list. That was obvious immediately.
- **Most important:** the search bar and the filter chips ("All / Needs review 39 / Uncategorized / Income"). **Next click:** "Needs review".

| Line | Score | Based on |
|---|---|---|
| 1 | 9 | `02-transactions.desk.en`: "Transactions" title, rows grouped by day with daily totals |
| 2 | 8 | `02-transactions.desk.en`: summary line "297 transactions 42,057.91 € in 31,970.76 € out" sits above the list |
| 3 | 7 | `02-transactions.desk.en`: the "Filter" and "Newest first" controls are separated from the chip group |
| 5 | 5 | `03-transactions-review.desk.en`: "Needs review 39" vs "8 transactions"; "Needs review" vs "Uncategorized" chips |
| 7 | 7 | `02-transactions.phone.de`: the chip row fits, but the search placeholder "Händler, Verwendungszweck, Kategorie oder Betr…" is cut off |

**Findings**
- `03-transactions-review.desk.en`, the "Needs review 39" chip vs "8 transactions" in the summary line: the badge says 39, the list shows 8. The capture note says the demo cannot filter, so the row count may be a demo artefact. Even so, a newcomer is left asking what the 39 actually counts. Severity: slows a task.
- `03-transactions-review.desk.en`, the chips "Needs review" and "Uncategorized" side by side: I could not tell the difference. Is review "uncertain guess" and Uncategorized "no guess"? Only Settings > Categories ("Put uncertain guesses in 'Needs review'") explains it. Severity: slows a task. Suggestion: a tooltip, or one line in the banner such as "Groschen wasn't sure about these. Confirm or change."
- `03-transactions-review.desk.en`, the banner "These transactions need a category from you.": `keep` the idea. It turns a filter into a task. It should also say what to do: "Click a row to pick one".
- `03-transactions-review.desk.en`, the summary text "All periods": the period picker in the top right still says "Jan – Oct 2026". Two contradicting period labels on the same screen. Severity: slows a task.
- `02-transactions.desk.en`, the yellow left bar on the "Hofladen Sonnenfeld" row: it is unexplained on the All view. I only understood it means "needs review" after seeing 03. Severity: cosmetic.
- `02-transactions.desk.en`, the account column "Girokonto" in the English UI: it is the bank's own account name, which is fine. Still, on first look I took it for an untranslated label. Severity: cosmetic.
- `02-transactions.phone.de` (lower part), the green "Geld zurück für About You" lines and the struck-through "-34,99 €" Amazon amount: refunds linked to purchases are clever. The strike-through was the one thing I had to think about ("Komplett zurückbekommen" explains it). `keep`.
- `04-transactions-filtered.desk.en`, the "Clear filters" link next to the summary: `keep`. It is easy to find.
- `06-transactions-empty.desk.en`, "No transactions match / Try a different search, filter or period": `keep`. It is clear.
- `06-transactions-empty.phone.de`, the large empty gap between the top bar and the "Umsätze" title (the title starts around y≈200): it looks like a layout glitch. Severity: cosmetic.

---

## 05 Transaction edit dialog (`05-transactions-edit.desk.en`, `.phone.de`)

- **What is this?** Detail and category picker for one transaction. Clear.
- **Most important:** the category chips. **Next click:** pick a chip, then "Save".

| Line | Score | Based on |
|---|---|---|
| 1 | 8 | `05-transactions-edit.desk.en`: merchant logo, amount, raw bank text, then "Category" |
| 2 | 7 | `05-transactions-edit.desk.en`: the selected "Fuel" chip stands out; the list is long and scrolls |
| 3 | 7 | `05-transactions-edit.desk.en`: "Search categories" field on top |
| 5 | 6 | `05-transactions-edit.desk.en`: "Housing (general)" / "Food & Dining (general)" chips; "Everything with Shell >" |
| 7 | 7 | `05-transactions-edit.phone.de`: the toggle sits on its own line under a 2-line label, and "Save" stays reachable |

**Findings**
- `05-transactions-edit.desk.en`, the "Use this category for every transaction from this merchant" toggle: it is already on by default. A first-timer may not notice they are creating a rule. Severity: slows a task, because I would not expect fixing one row to change history. Suggestion: show it off by default, or say "and N past transactions".
- `05-transactions-edit.desk.en`, the "Everything with Shell >" link in the footer next to "Save": it reads like a second primary action, and it is unclear whether it saves first. Severity: cosmetic.
- `05-transactions-edit.desk.en`, the "+ New" chip at the end of each group: `keep`. Creating a category exactly where you need it is good.

---

## 07 Spending, 33 Period menu (`07-spending.*`, `33-period-menu.*`)

- **What is this?** Where my money goes by category. The donut plus bars make it clear.
- **Most important:** "Spending breakdown". **Next click:** a group row (">").

| Line | Score | Based on |
|---|---|---|
| 1 | 8 | `07-spending.desk.en`: "Spending breakdown 2,045.14 € a month on average, most on Housing (58%)" |
| 2 | 8 | `07-spending.desk.en`: donut and ranked bars, then "Your year in days" below |
| 3 | 7 | `33-period-menu.desk.en`: period presets, with no custom range |
| 5 | 5 | `07-spending.desk.en`: "Spending / Income" toggle on a page titled "Spending"; "Your own group" ghost button |
| 7 | 8 | `07-spending.phone.de`: the donut, bars and calendar heat-map split into two half-year blocks, which works |

**Findings**
- `07-spending.desk.en`, the "Spending | Income" segmented control in the header: on a page titled "Spending", switching to "Income" makes the title wrong. Severity: slows a task (how do I see my income?). Suggestion: rename the page "Money in & out", or make the title follow the toggle.
- `07-spending.desk.en`, the "+ Your own group" ghost button under the title: it is unclear what a "group" is here. The dialog that opens is titled "New group" (`08`), and Settings says "Custom groups". That is three names for one feature. Severity: slows a task. Suggestion: "+ Custom group" everywhere.
- `07-spending.desk.en`, the "Groups | Categories" toggle: `keep`. It is clear once you see it.
- `07-spending.desk.en`, the "Personal · more refunds than spending -162.37 €" row: a negative spending row needs a second read. The explanation is right there, though. `keep` the inline explanation.
- `07-spending.desk.en`, "Your year in days" heat-map with its explanation line "grey without spending, from violet to glowing yellow…": `keep`. It is self-explaining.
- `33-period-menu.desk.en`, the menu items "Year" and "Year to date": "Year" does not say which year (this one? the last full one?). There is also no custom range. Severity: slows a task. Suggestion: "2026 (full year)", "2025", "Custom…".

---

## 08 New group dialog (`08-spending-group-dialog.desk.en`, `.phone.de`)

| Line | Score | Based on |
|---|---|---|
| 1 | 7 | `08-spending-group-dialog.desk.en`: intro text "A custom group collects transactions across categories, for a car…" |
| 2 | 6 | `08-spending-group-dialog.desk.en`: the Name/Icon row is small compared with the very long list of category chips |
| 5 | 5 | `08-spending-group-dialog.desk.en`: "your main budget still counts everything normally" |
| 7 | 7 | `08-spending-group-dialog.phone.de`: fits, and the Cancel/Save footer is sticky |

**Findings**
- `08-spending-group-dialog.desk.en`, the intro sentence "your main budget still counts everything normally": nowhere else in the app is there a "budget". A newcomer will look for one. Severity: slows a task. Suggestion: "your normal totals still count everything".
- `08-spending-group-dialog.desk.en`, the chips: no chip looks selected, and nothing says "pick the categories that belong to this group". Severity: slows a task. Suggestion: add a label "Categories in this group" above the chips.

---

## 09 Drill into a group, 10 drill into a category (`09-drill-group.*`, `10-drill-category.*`)

- **What is this?** A detail page for "Food & Dining", then for "Groceries". The breadcrumb "SPENDING > FOOD & DINING" makes my position obvious.
- **Next click:** a merchant or a sub-category.

| Line | Score | Based on |
|---|---|---|
| 1 | 9 | `09-drill-group.desk.en`: "SPENT 3,480.29 €", "↑35% vs. the period before", the monthly bars with an average line |
| 2 | 8 | `09-drill-group.desk.en`: KPI and chart, then Top merchants / Categories, then Transactions |
| 5 | 6 | `09-drill-group.desk.en`: a "Food & Dining · 0×" sub-category inside the "Food & Dining" group |
| 7 | 8 | `10-drill-category.phone.de`: the breadcrumb wraps fine, and the chart stays readable |

**Findings**
- `10-drill-category.desk.en`, the breadcrumb "SPENDING > FOOD & DINING" with the back chevron: `keep`.
- `09-drill-group.desk.en`, the Categories card row "Food & Dining · 0× 0.00 €": the group has a child category with the same name. In the edit dialog the same thing is called "Food & Dining (general)". Severity: slows a task. Suggestion: always show "(general)" and hide rows that are 0×.
- `09-drill-group.desk.en`, the Top merchants card "8 of 9": there is no visible way to see the 9th. Severity: cosmetic. Suggestion: a "Show all" link.
- `09-drill-group.desk.en`, the red "↑ 35%" pill: `keep`. Colouring it red for spending up is the right signal.

---

## 11 Fixed costs list, 12 Calendar, 13 Orbit (`11-*`, `12-*`, `13-*`)

- **What is this?** My recurring payments. The "FIXED COSTS, ON AVERAGE PER MONTH 1,407.01 €" hero plus "NEXT UP" make it clear in 3 seconds.
- **Next click:** a row in "Running", or the List / Calendar / Orbit switch.

| Line | Score | Based on |
|---|---|---|
| 1 | 9 | `11-recurring-list.desk.en`: hero and "Next up" panel |
| 2 | 8 | `11-recurring-list.desk.en`: hero, "What changed", "Running", then the savings-plan footer |
| 3 | 7 | `11-recurring-list.desk.en`: each row shows rhythm, next date and amount |
| 5 | 5 | `11-recurring-list.desk.en`: "Orbit" tab, "Running" heading, "+7.00 €" badges; `12-recurring-calendar.desk.en` "1,423.48 € fixed costs" vs 1,407.01 € |
| 7 | 6 | `13-recurring-orbit.phone.de`: the orbit is shrunk to about 120 px tall with overlapping labels |

**Findings**
- `11-recurring-list.desk.en`, the "What changed" card ("New: Apple", "DAZN is back", "Disney+ stopped coming", "Spotify got more expensive"): `keep`. It is excellent, plain-language change tracking.
- `11-recurring-list.desk.en`, the amber "+7.00 €" / "+9.00 €" pills next to Stadtwerke and Deutsche Bahn: I had to guess these mean a price increase. Severity: cosmetic. Suggestion: "+7.00 € since Jun" or a tooltip.
- `11-recurring-list.desk.en`, the section title "Running": it is ambiguous (running costs? currently active?). Severity: cosmetic. Suggestion: "Active".
- `11-recurring-list.desk.en`, the "List | Calendar | Orbit" switch: "Orbit" tells a newcomer nothing. Severity: slows a task (I would never click it on purpose). Suggestion: "By rhythm" or "Orbit (by frequency)".
- `12-recurring-calendar.desk.en`, the header "1,423.48 € fixed costs · 1,100.00 € saved": the list view says 1,407.01 € a month. Seeing two different "fixed costs" numbers one click apart makes me distrust both, even though one is this month's actual and the other is the average. Severity: slows a task. Suggestion: "October: 1,423.48 € paid (avg 1,407.01 €)".
- `12-recurring-calendar.desk.en`, the legend "Paid" in orange/red: paid items are drawn in the same alarm colour the app uses for losses. Severity: cosmetic.
- `12-recurring-calendar.desk.en`, the "Day by day" side panel: `keep`. It makes the truncated cell labels ("Ha… -1,050 €") readable.
- `12-recurring-calendar.phone.de`, the calendar dots with totals under each day: `keep`. It is a good phone adaptation.
- `13-recurring-orbit.desk.en`, the "Your month in orbit" explainer: it needs a full read ("A payment reaches the front on the day it is due"), and most planets carry no label. I could not answer "what's due next" from this view in 5 seconds. Severity: slows a task. Suggestion: label all planets, or treat Orbit as a fun extra rather than a main view.
- `13-recurring-orbit.phone.de`, the orbit graphic: the planets overlap the "1.407 €" centre text and the labels collide ("Hausverwaltung Kr…"). Severity: cosmetic (List works).

---

## 14 Net worth (`14-networth.*`)

- **What is this?** Total wealth: "TODAY 44,931.92 €" with a rising line. Clear.
- **Next click:** an account card, or "Add account".

| Line | Score | Based on |
|---|---|---|
| 1 | 9 | `14-networth.desk.en`: "TODAY 44,931.92 €  ↑13,592.05 € Jan – Oct 2026" with the chart |
| 2 | 8 | `14-networth.desk.en`: hero, account cards, savings plans |
| 5 | 6 | `14-networth.desk.en`: only "Direkt-Depot" has a ">" chevron; the other two cards look clickable but have none |
| 7 | 8 | `14-networth.phone.de`: the cards stack cleanly |

**Findings**
- `14-networth.desk.en`, the account cards: only the "Direkt-Depot" card has a chevron. Is that card the way into "Investments"? Nothing else on the page says so. Severity: slows a task. Suggestion: a visible "Open investments" link, or the same affordance on all cards.
- `14-networth.desk.en`, the "Add account" dashed card ("Say a house or a car loan outside your banks"): `keep`. It is clear and inviting.
- `14-networth.desk.en`, the "Savings plans" explainer "A plan shows up after its third payment and leaves once payments stop": `keep`. It answers "why isn't my new plan here?" up front.

---

## 15 Investments / Depot (`15-investments.*`), 32 hidden variant

- **What is this?** The ETF portfolio. "DEPOT VALUE ON 30 OCT 2026 9,350.57 €" is clear once you know "depot" = portfolio.
- **Next click:** a holding card.

| Line | Score | Based on |
|---|---|---|
| 1 | 7 | `15-investments.desk.en`: "DEPOT VALUE" hero; the chart legend "Value without your pay-ins" took me several reads |
| 2 | 8 | `15-investments.desk.en`: hero and chart, holdings, tax allowance, then the opt-in banner |
| 5 | 5 | `15-investments.desk.en`: "Investments" title vs "depot" wording; `15-investments.phone.de` title "Depot" |
| 7 | 8 | `15-investments.phone.de`: the chart and waterfall bars fit, and the "Mit zwei Fingern vergrößern" hint is adapted for touch |

**Findings**
- `15-investments.desk.en`, the chart legend "Value without your pay-ins" plus the toggle "Money paid in": I could not tell what the gold line shows (9k is not my 9,350 €). Severity: slows a task. Suggestion: "Performance only (excluding deposits)", with a default toggle state that shows the actual value.
- `15-investments.desk.en`, the hero sub-line "↑504.90 € · +6.7%" vs the holding card "↑ +7.5% · 474 €" (Vanguard) vs the ETF page "+1,160.97 € · +17.2%" (`19-etf.desk.en`): three return figures for nearly the same money, each on a different basis (period vs all time). None says which. Severity: slows a task. Suggestion: suffix each with "this period" or "since purchase".
- `15-investments.desk.en`, the "Tax-free allowance 2026 95.40 € of 1,000.00 € — Adjust" card: `keep`. It is useful and clearly named for a German user.
- `15-investments.desk.en`, the bottom banner "Get full price histories? … Turn on": `keep`. It is honest opt-in copy.
- `32-hidden-investments.desk.en`, the chart axes and waterfall labels show "9.9k €" / "+999 €": hidden mode keeps the layout intact. The percentages (+6.7%) stay visible. I note this only so it can be kept intentionally.

---

## 16 Forecast (`16-inv-forecast.*`)

- **What is this?** A Monte-Carlo projection of the ETF plan. "IN 10 YEARS · OCT 2036 68,412 €" and "Assumptions, not a promise" are clear.

| Line | Score | Based on |
|---|---|---|
| 1 | 8 | `16-inv-forecast.desk.en`: "Where it could go — 800 simulated futures… Assumptions, not a promise." |
| 2 | 7 | `16-inv-forecast.desk.en`: the four assumption tiles sit above the result, so the answer comes second |
| 5 | 6 | `16-inv-forecast.desk.en`: tile "Plan raise — Stays the same", "Swing 15% a year" |
| 7 | 7 | `16-inv-forecast.phone.de`: the tiles go 2×2, and the long text in "Erwartete Rendite" makes that tile very tall |

**Findings**
- `16-inv-forecast.desk.en`, the "Bad case / Good case" slider with the "paid in" tick: `keep`. It is an intuitive range display.
- `16-inv-forecast.desk.en`, the "Swing 15% a year" tile vs the "Ups and downs ±17%" card on `17-inv-analysis.desk.en`: two names and two numbers for volatility. Severity: slows a task. Suggestion: one term ("Volatility" / "Schwankung") and a note on why they differ.
- `16-inv-forecast.desk.en`, the "Plan raise" tile: it is unclear whether this is an input. "Adjust the numbers" sits far away at the bottom left. Severity: cosmetic. Suggestion: move "Adjust" next to the tiles.

---

## 17 Analysis (`17-inv-analysis.*`)

| Line | Score | Based on |
|---|---|---|
| 1 | 7 | `17-inv-analysis.desk.en`: "Return in this period — Your money +6.7% / The funds themselves +6.3%" |
| 2 | 7 | `17-inv-analysis.desk.en`: four equal cards with no lead result |
| 5 | 6 | `17-inv-analysis.desk.en`: "Ups and downs", "Drawdown"; settings mention a "Sharpe ratio" that does not appear here |
| 7 | 8 | `17-inv-analysis.phone.de`: the month grid wraps into 6×2 |

**Findings**
- `17-inv-analysis.desk.en`, the "Your money vs The funds themselves" comparison with the plain sentence "About what the funds themselves made.": `keep`. It is the best jargon-free performance explanation I have seen.
- `17-inv-analysis.desk.en`, the "Outlined: the best and the worst month" line under Monthly returns: it is drawn with a checkbox, so it looks like a control. Severity: cosmetic. Suggestion: a legend swatch, not a checkbox.
- `23-settings-depot.desk.en` "Interest rate to compare with — Used for the Sharpe ratio" vs `17-inv-analysis.desk.en`: no Sharpe ratio is shown on Analysis, so the setting points to nothing. Severity: slows a task.

---

## 18 Pay-ins (`18-inv-payments.*`)

| Line | Score | Based on |
|---|---|---|
| 1 | 6 | `18-inv-payments.desk.en`: the title "Pay-ins" is vague; the heading "Money put in" explains it |
| 2 | 7 | `18-inv-payments.desk.en`: month accordion with totals, and "3,600.00 € in the last 12 months" on the right |
| 5 | 5 | `18-inv-payments.desk.en`: "Pay-ins" / "Money put in" / "Don't count"; the "Import price history" strip on the same page |
| 7 | 8 | `18-inv-payments.phone.de`: the rows stack, and "Nicht zählen" stays reachable |

**Findings**
- `18-inv-payments.desk.en`, the bottom strip "One line per day: date;ISIN;price … Import price history": price import is a different task from deposits. A newcomer would never look for it here. Severity: slows a task. Suggestion: move it to Settings > Investments or to the ETF "Facts" tab.
- `18-inv-payments.desk.en`, the "× Don't count" per row: `keep`. Clear, and reversible-sounding.

---

## 19 ETF detail (`19-etf.*`)

| Line | Score | Based on |
|---|---|---|
| 1 | 8 | `19-etf.desk.en`: "Vanguard FTSE All-World", ISIN chip, "YOUR VALUE 7,910.97 €" |
| 2 | 7 | `19-etf.desk.en`: the opt-in banner sits above the main value and pushes it down |
| 5 | 6 | `19-etf.desk.en`: tabs "Overview / Analysis / Forecast / Facts" repeat the depot-level names |
| 7 | 8 | `19-etf.phone.de`: the chart and "Dein Schnitt" line are readable |

**Findings**
- `19-etf.desk.en`, the tabs "Analysis" and "Forecast": the same names sit in the sidebar for the whole depot. I wasn't sure whether clicking one would leave the ETF. Severity: cosmetic.
- `19-etf.desk.en`, the "Get full price histories?" banner: it also appears on `15-investments.desk.en`. Above the hero it competes with the value. Severity: cosmetic. Suggestion: put it below the chart.
- `19-etf.desk.en`, the "Your average 110.71 €" dashed line with purchase dots: `keep`. It is very understandable.

---

## 20–28 Settings (`20-settings-bank` … `28-settings-list`)

- **What is this?** Settings with 8 tabs on desktop and a list of 8 rows with subtitles on phone.
- **Next click:** Bank & import.

| Line | Score | Based on |
|---|---|---|
| 1 | 8 | `28-settings-list.phone.de`: each entry has a one-line description ("Passwort, Land, Währung, Sprache und Animationen") |
| 2 | 7 | `20-settings-bank.desk.en`: the "Sync now" primary button stands out; the long 90-day explanation is dense |
| 5 | 6 | `20-settings-bank.desk.en` tab row: "Hints & salary", "Investments", "Account & look" |
| 7 | 8 | `28-settings-list.phone.de`: the list-then-detail pattern with a "‹ EINSTELLUNGEN" back link |

**Findings**
- `28-settings-list.phone.de`, the list with descriptions: `keep`. The desktop tab row (`20-settings-bank.desk.en`) has no descriptions, so "Hints & salary" is a guess there. Severity: cosmetic. Suggestion: tooltips on the tabs, or a left sub-nav with subtitles on desktop.
- `20-settings-bank.desk.en`, the "I logged in to my bank" button and "Bank login needed within 90 days": I had to read the 2-line paragraph twice to understand why I must press a button after logging in elsewhere. Severity: slows a task. The explanation exists, which helps. Suggestion: rename the button to "I just logged in at ING (reset 90 days)".
- `21-settings-categories.desk.en`, the "Categorizer" row: "Built-in model" is selected, yet the subtitle says "Spelling-based matcher (built-in model not found)", and a green "Offline" badge sits top-right. Selected option, status text and badge all disagree. Severity: slows a task. Suggestion: when the model is missing, disable that option and show an amber "Model missing" state.
- `21-settings-categories.desk.en`, the section "That's you": the heading is cryptic until you read the line below it. Severity: cosmetic. Suggestion: "Your own accounts / names".
- `22-settings-hints.desk.en`, the "Hints appear under 'Worth a look' on the Overview." line: `keep`. Cross-linking a setting to where it appears is excellent.
- `22-settings-hints.desk.en`, the section "Salary and free to spend": the Overview calls this "Available until payday", and the payday dialog calls it "Free to spend". Severity: cosmetic. Suggestion: one name.
- `23-settings-depot.desk.en`, tab "Investments" (EN) vs "Depot" (DE): see the global naming finding.
- `23-settings-depot.phone.de` (and `06`, `13` phone): an empty band between the top bar and the "‹ EINSTELLUNGEN" back link. Severity: cosmetic.
- `24-settings-backup.desk.en`, the "Smart Recycle (Recommended)" option: `keep` the recommended preset. The name "Smart Recycle" means nothing to a newcomer, but the sentence below it explains it.
- `24-settings-backup.phone.de`, the backup timeline: the "1 pro Jahr / 1 pro Monat" segment labels are missing, and the boxes are squeezed. Severity: cosmetic.
- `25-settings-privacy.desk.en`, the "Backups never contain the key…" sentence under Export: this belongs on the Backups tab, and here it confuses. Severity: cosmetic.
- `26-settings-security.desk.en`, the "Password login — Always on until you add a passkey" row: it has no control on the right, which looks broken next to rows that do. Severity: cosmetic. Suggestion: a disabled toggle, or an "Always on" pill.
- `27-settings-account.desk.en`, the "Country: Not chosen" dropdown: the wizard asks for the country (`41-wizard-country`), yet the account settings show none. A newcomer will wonder whether setup failed. Severity: slows a task.
- `27-settings-account.desk.en`, the "Easter eggs" toggle with the hint: harmless and charming. `keep`.

---

## 30 Connect bank dialog (`30-settings-connect-dialog.*`)

| Line | Score | Based on |
|---|---|---|
| 1 | 8 | `30-settings-connect-dialog.desk.en`: "Connect your bank — Your bank: Bank name, Bankleitzahl or IBAN" |
| 3 | 5 | `30-settings-connect-dialog.desk.en`: primary button "Done, start syncing" with an empty field |
| 5 | 5 | `30-settings-connect-dialog.desk.en`: "Done" before any step was done |

**Findings**
- `30-settings-connect-dialog.desk.en`, the primary button "Done, start syncing": it is offered (and looks enabled) before I have typed a bank or entered credentials. I would not know whether more steps follow. Severity: slows a task. Suggestion: "Continue" until the last step, and disable it while the field is empty.
- `30-settings-connect-dialog.desk.en`, the helper text "Typing your IBAN finds the exact bank.": `keep`.

---

## 31 Hidden amounts (`31-hidden-overview.*`, `32-hidden-investments.*`)

| Line | Score | Based on |
|---|---|---|
| 1 | 6 | `31-hidden-overview.desk.en`: the only cue that the mode is on is the highlighted eye icon next to the logo |
| 7 | 8 | `31-hidden-overview.phone.de`: the eye button in the top bar is highlighted, and the layout is unchanged |

**Findings**
- `31-hidden-overview.desk.en`, the blurred "9,999.99 €" values: `keep`. The layout stays the same, so you can share your screen safely.
- `31-hidden-overview.desk.en`, the eye icon at the top left: a first-timer who activated it by accident sees blurred numbers everywhere and needs to find a 20 px icon to undo it. Severity: slows a task. Suggestion: a small "Amounts hidden · Show" pill near the page title while the mode is active.

---

## 34 Payday details (`34-payday-details.*`)

| Line | Score | Based on |
|---|---|---|
| 1 | 9 | `34-payday-details.desk.en`: "Balance now 7,768.05 € − Still going out −2,597.40 € = Free to spend 5,170.65 €" |
| 2 | 9 | `34-payday-details.desk.en`: the equation on top, the itemised list below |
| 5 | 7 | `34-payday-details.desk.en`: title "Available until payday" vs result row "Free to spend" |
| 7 | 8 | `34-payday-details.phone.de`: the full-height sheet, with the "Alle Fixkosten" footer button |

**Findings**
- `34-payday-details.desk.en`, the three-line equation: `keep`. It is exactly how to explain a derived number to a newcomer.
- `34-payday-details.desk.en`, the "Sparen −800.00 €" and "Sparplan … −250.00 €" items under "Still going out": savings are counted as outgoing here. That is sensible, but the footer button says "All fixed costs", which suggests these are fixed costs. Severity: cosmetic.

---

## 40–42 First-run wizard and login (`40-wizard-account.*`, `41-wizard-country.*`, `42-login.*`)

| Line | Score | Based on |
|---|---|---|
| 1 | 7 | `40-wizard-account.desk.en`: "Welcome to Groschen — Let's set up your dashboard…" never says what Groschen does |
| 2 | 8 | `40-wizard-account.desk.en`: the 5-step sidebar with subtitles |
| 3 | 8 | `40-wizard-account.desk.en`: four fields and Continue |
| 5 | 6 | `41-wizard-country.desk.en`: step "Connect your bank — Over FinTS" while the body says sync only works for German banks |
| 7 | 6 | `40-wizard-account.phone.de`: a progress bar of 5 unlabeled segments; `41-wizard-country.phone.de` has two stacked actions |

**Findings**
- `40-wizard-account.desk.en`, the step list "Welcome / Connect your bank / Import history / Smart features / First sync" with subtitles: `keep`. I know how long this takes ("about five minutes") and what comes next.
- `40-wizard-account.desk.en`, the welcome copy: it does not say in one line what I get (for example "See what you can spend until payday, where your money goes, and your net worth"). Severity: cosmetic.
- `40-wizard-account.desk.en`, the "Your name" + "Username" fields: having two identity fields with no explanation of the difference made me hesitate. Severity: cosmetic.
- `41-wizard-country.desk.en`, the "Where do you live? United Kingdom" field and the step label "Connect your bank — Over FinTS, read-only": for a non-German user the step promises a bank connection it cannot deliver. The info box says so, but the left step label stays unchanged. Severity: slows a task. Suggestion: relabel the step to "Bank files (CSV)" when the country is not Germany.
- `41-wizard-country.phone.de`, the footer "Überspringen, vorerst CSV-Dateien nutzen" above "Weiter": the skip link is wider and more prominent than the dim primary button, and both sit stacked on the right. Severity: slows a task. Suggestion: put skip left-aligned as a text link and "Weiter" to the right.
- `40-wizard-account.phone.de`, the 5-segment progress bar: it has no step names, so the phone user loses the "what's next" the desktop has. Severity: cosmetic. Suggestion: "Schritt 1 von 5 · Anmeldung".
- `42-login.desk.en`, the "Welcome back" card with Username/Password and the language picker: `keep`. It is minimal and clear. Passkeys are not offered on this screen even though Settings promotes them. Severity: cosmetic.

---

## Top 10

1. **One concept, many names (naming).** EN uses "Investments", "Depot", "Direkt-Depot" and "depot value" for the same thing (`01-overview.desk.en` sidebar, `14-networth.desk.en`, `15-investments.desk.en`). "Custom group", "Your own group" and "New group" are one feature (`07-spending.desk.en`, `08-…dialog.desk.en`, `21-settings-categories.desk.en`). "Available until payday" is also "Free to spend" and "Salary and free to spend" (`34`, `22`). Pick one term per concept. *Slows a task.*
2. **Needs review is confusing** (`03-transactions-review.desk.en`). The badge says 39 and the list says 8. The Overview hint says "Do the categories look right?" while the banner says "need a category from you". The "Needs review" and "Uncategorized" chips cannot be told apart. *Slows a task.*
3. **Three different return figures on the depot** (`15-investments.desk.en` +6.7% / 504.90 €, holding card +7.5% / 474 €, `19-etf.desk.en` +17.2% / 1,160.97 €), with no basis stated. Add "this period" or "since purchase". *Slows a task.*
4. **Categorizer status contradicts itself** (`21-settings-categories.desk.en`). "Built-in model" is selected, the subtitle says "built-in model not found", and a green "Offline" badge is shown. *Slows a task.*
5. **Two different "fixed costs" totals one click apart** (`11-recurring-list.desk.en` 1,407.01 € vs `12-recurring-calendar.desk.en` 1,423.48 €). Label one as the monthly average and the other as this month's actual. *Slows a task.*
6. **"Spending / Income" toggle on a page titled "Spending"** (`07-spending.desk.en`). After switching, the title is wrong, and income has no named home in the navigation. *Slows a task.*
7. **The investment chart legend "Value without your pay-ins"** (`15-investments.desk.en`) can't be decoded in 5 seconds. Default to the real value and say "excluding deposits" plainly. *Slows a task.*
8. **Opaque labels: "Orbit", "Pay-ins", "Running", "That's you"** (`11-recurring-list.desk.en` view switch, `01-overview.desk.en` sidebar, `11` section head, `21` section). Use self-describing names. *Slows a task.*
9. **Wizard mismatch for non-German users and a weak phone footer** (`41-wizard-country.desk.en` step "Connect your bank — Over FinTS" for the UK; `41-wizard-country.phone.de` skip link outranks "Weiter"). Country is then "Not chosen" in `27-settings-account.desk.en`. *Slows a task.*
10. **Premature "Done, start syncing"** in the connect dialog (`30-settings-connect-dialog.desk.en`) before anything is entered, and the merchant-rule toggle already on in the edit dialog (`05-transactions-edit.desk.en`). Both are actions a newcomer takes without understanding the consequence. *Slows a task.*

**Keep (strongest first-time-user wins):** the "Available until payday" hero and its equation dialog (`01`, `34`); the plain-language "What changed" card on fixed costs (`11`); "Your money vs The funds themselves" (`17`); the phone sub-tabs and the settings list with descriptions (`11-…phone.de`, `28-settings-list.phone.de`); the breadcrumbs on drill pages (`09`, `10`); and the "Hints appear under 'Worth a look'" cross-reference (`22`).
