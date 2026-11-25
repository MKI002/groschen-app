# Groschen, pass 8: Information Architect review

Role: navigation, grouping and naming (EN and DE), clarity of purpose, consistency. I only score rubric lines 1 (clarity of purpose), 5 (navigation and naming), 6 (consistency) and, where it concerns reaching things, 7 (phone experience). Other lines are "-".

## Site map (as the screenshots show it)

```
DESKTOP SIDEBAR (01-overview.desk.en / .desk.de)
Groschen [eye = hide amounts]
├─ Overview / Übersicht                      (dot badge)
│    ├─ dialog: Available until payday / Frei verfügbar bis zum Gehalt (34)
│    │     └─ button "All fixed costs" -> Fixed costs
│    ├─ "Worth a look" hints -> Check (Transactions: Needs review), Show (Fixed costs)
│    └─ Sankey "Where the money went": Flow | Timeline, a click -> transactions
├─ Transactions / Umsätze  [39]
│    ├─ chips: All | Needs review 39 | Uncategorized | Income
│    │        (Alle | Zu prüfen | Ohne Kategorie | Einnahmen)
│    ├─ Filter, sort, period
│    └─ dialog: edit transaction (05) -> "Everything with Shell"
├─ Spending / Ausgaben
│    ├─ toggle Spending | Income (Ausgaben | Einnahmen)   <- the only home of "Income"
│    ├─ "+ Your own group" -> dialog "New group" (08)
│    ├─ breakdown Groups | Categories
│    │    └─ Group drill (09)  "< SPENDING"  Food & Dining
│    │         └─ Category drill (10) "< SPENDING > FOOD & DINING"  Groceries
│    └─ "Your year in days"
│    └─ Fixed costs / Fixkosten   (List | Calendar | Orbit)  (11-13)
├─ Net worth / Vermögen  (14)
│    ├─ accounts, Add account, Savings plans
│    └─ Investments / Depot  (15)   "< NET WORTH"
│         ├─ ETF detail (19): Overview | Analysis | Forecast | Facts
│         ├─ Analysis / Analyse (17)
│         ├─ Forecast / Prognose (16)
│         └─ Pay-ins / Einzahlungen (18)  (+ "Import price history")
├─ [footer] ING connected · Synced just now  [sync]
├─ Settings / Einstellungen  (tabs, 20-27)
│    Bank & import | Categories | Hints & salary | Investments(Depot) |
│    Backups | Export & privacy | Security | Account & look
└─ Alex  [log out]

PHONE (390 px)
Top bar: logo · sync chip "just now"/"gerade eben" · eye · gear(-> Settings list, 28)
Bottom tabs: Overview | Transactions | Spending | Net worth
             (Übersicht | Umsätze | Ausgaben | Vermögen)
Second-level tab strips:
  Spending tab  -> [Spending | Fixed costs]                         (07, 11)
  Net worth tab -> [Net worth | Investments]                        (14)
  Investments   -> [Investments | Analysis | Forecast | Pay-ins]    (15-18)  <- Net worth drops out of the strip, only "< NET WORTH" back link
  ETF detail    -> no strip, inner tabs Overview|Analysis|Forecast|Facts (19)
Settings (gear) -> list of 8 sections with subtitles (28) -> sub page "< EINSTELLUNGEN"
Log out: only Settings > Account & look (27)
FIRST RUN: Wizard 1 Welcome · 2 Connect your bank · 3 Import history · 4 Smart features · 5 First sync (phone: unnamed 5-segment bar). Login.
```

Reach check (phone vs desktop sidebar): every sidebar destination is reachable on the phone (Overview, Transactions, Spending, Fixed costs, Net worth, Investments, Analysis, Forecast, Pay-ins, Settings, log out, hide amounts, sync status). The differences: Fixed costs and the four depot pages are one level deeper (bottom tab -> strip); log-out moves into Settings > Account; the sync chip loses the bank name ("just now" without "ING"); the manual "sync now" button seen in the desktop footer is not visible in the phone top bar (only in Settings > Bank & import).

---

## 01 Overview (desk.en, desk.de, phone.en, phone.de) + 31 hidden

| Line | Score | Basis |
|---|---|---|
| 1 clarity | 8 | 01-overview.desk.en: "Available until payday" hero says what the page is for in one line |
| 5 naming | 7 | 01-overview.desk.en Sankey labels "Put aside" / "Stays on the account" / "Invested" are plain words; but "Uncategorized" appears as an income source (left) and an expense (right) in the same Sankey |
| 6 consistency | 6 | 01-overview.desk.en "Available until payday" hero vs 34-payday-details "Free to spend" row: same 5,170.65 € under two names |
| 7 phone | 8 | 01-overview.phone.de bottom bar "Übersicht · Umsätze · Ausgaben · Vermögen" + gear: four plain tabs, nothing missing |
| 2,3,4,8,9 | - | |

Findings
- `keep` 01-overview.desk.en sidebar: the tree Spending > Fixed costs, Net worth > Investments > Analysis/Forecast/Pay-ins matches how a person thinks (money out vs money owned). Keep the hierarchy.
- `keep` 01-overview.desk.de: German nav words are the words a German user uses: "Umsätze", "Ausgaben", "Fixkosten", "Vermögen", "Depot". Better than the EN set.
- 01-overview.desk.en Sankey: "Uncategorized 43.20 €" on the income side and "Uncategorized 510.60 €" on the spending side. Same word, two meanings in one chart. Slows a task. Suggest "Other income" on the left or "Uncategorized income".
- 01-overview.desk.en "Saved" card: "put aside" here, "Keep aside" in 22-settings-hints (a cushion subtracted from the hero). In DE "zurückgelegt" (Sankey) vs "Zurücklegen" (setting). Two different concepts with the same verb. Slows a task. Rename the setting to "Safety cushion" / "Notgroschen" (fits the brand).
- 01-overview.phone.de top bar chip "gerade eben" (phone.en "just now"): a time without a subject. Desktop says "ING connected · Synced just now". Cosmetic. Suggest "ING · gerade eben" or an icon that reads as sync.
- 31-hidden-overview.phone.de: eye icon turns gold and crossed when hidden: state is visible in the nav chrome. `keep`.

## 02-04, 06 Transactions (list, needs review, filtered, empty)

| Line | Score | Basis |
|---|---|---|
| 1 clarity | 7 | 02-transactions.desk.en header "Jan – Oct 2026 · 297 transactions · in / out" summary |
| 5 naming | 5 | 03-transactions-review.desk.en chip "Needs review 39" opens a list headed "These transactions need a category from you" with 8 rows, all "Uncategorized": the chip, its count, the banner and the "Uncategorized" chip next to it describe three different sets |
| 6 consistency | 6 | 03-transactions-review.desk.en meta line "All periods" while the period button still reads "Jan – Oct 2026" |
| 7 phone | 7 | 03-transactions-review.phone.de chip row "Alle · Zu prüfen 39 · Ohne Kategorie · Einnahmen" fits; filter and sort drop to a second row |
| others | - | |

Findings
- 03-transactions-review.desk.en / .phone.de: "Needs review" (= uncertain guesses, per 21-settings-categories "Put uncertain guesses in Needs review") vs the banner "These transactions need a category from you" (= uncategorized). Badge 39 in the sidebar, 8 rows here. Slows a task (the person cannot tell whether 39 or 8 things are waiting). Suggest: banner "Groschen guessed these. Confirm or change", and keep "Uncategorized" as its own chip; make the sidebar badge count the same set as the chip.
- 03-transactions-review.desk.en: "All periods" overrides the visible "Jan – Oct 2026" period control without saying so on the control. Slows a task. Grey out or relabel the period button ("All periods") while the review chip is on.
- 02-transactions.desk.en: "Income" chip in Transactions and "Income" toggle in 07-spending: income has no nav entry of its own, and lives in two unrelated places. Slows a task. Either add "Income" to the sidebar under Spending, or rename the Spending page "Money in & out"/"Ein- & Ausgaben".
- 06-transactions-empty.phone.de: the page title "Umsätze" sits ~170 px below the top bar with empty space above. Cosmetic (looks like scroll state). Same in 23-settings-depot.phone.de.
- `keep` 06-transactions-empty.desk.en "No transactions match · Try a different search, filter or period" + "Clear filters" next to the count. Clear recovery.
- 04-transactions-filtered.desk.en "Clear filters" next to the result count: `keep`.

## 05 Transaction edit dialog

| Line | Score | Basis |
|---|---|---|
| 1 clarity | 8 | 05-transactions-edit.desk.en "Category" section with grouped chips, "Use this category for every transaction from this merchant" |
| 5 naming | 6 | 05-transactions-edit.desk.en chip "Housing (general)" vs 08-spending-group-dialog chip "Housing" vs 09-drill-group category row "Food & Dining · 0×": the catch-all category has three names |
| 6 consistency | 6 | same as above |
| 7 phone | 7 | 05-transactions-edit.phone.de: full-height sheet, Save at the bottom |
| others | - | |

Findings
- 05-transactions-edit.desk.en "Housing (general)" / 08 "Housing" / 09 "Food & Dining 0×": the group's own catch-all category shares the group's name. In 09 the "Categories" card lists "Food & Dining" inside "Food & Dining". Slows a task. Use "(general)" / "(allgemein)" everywhere, or "Other food".
- 05-transactions-edit.desk.en "Broadcast fee": EN speakers will not recognise this; in DE "Rundfunkbeitrag" is perfect. Cosmetic. Suggest "TV licence (Rundfunkbeitrag)".
- 05-transactions-edit.desk.en footer "Everything with Shell >" is a good cross-link to the merchant view. `keep`.

## 07 Spending, 08 New group dialog, 33 period menu

| Line | Score | Basis |
|---|---|---|
| 1 clarity | 7 | 07-spending.desk.en "Spending breakdown · 2,045.14 € a month on average, most on Housing (58%)" |
| 5 naming | 6 | 07-spending.desk.en "+ Your own group" button vs 08 dialog title "New group" vs 21-settings-categories card "Custom groups": three names for one thing |
| 6 consistency | 6 | 07-spending.phone.de: "Ausgaben" appears three times stacked (sub-tab, page title, segmented "Ausgaben | Einnahmen") |
| 7 phone | 7 | 07-spending.phone.de sub-tab strip "Ausgaben | Fixkosten" mirrors the sidebar nesting |
| others | - | |

Findings
- 07-spending.phone.de: sub-tab "Ausgaben", title "Ausgaben", toggle "Ausgaben | Einnahmen". When the toggle is on Einnahmen the title and tab still say Ausgaben. Slows a task. Move Income out of the toggle (see above) or let the title follow the toggle.
- 07-spending.desk.en "+ Your own group" / 08 "New group" / 21 "Custom groups" / DE "Eigene Gruppe" / "Neue Gruppe" / "Eigene Gruppen". Cosmetic. Pick "Custom group" / "Eigene Gruppe" everywhere.
- 08-spending-group-dialog.desk.en text "your main budget still counts everything normally": there is no "budget" anywhere in the navigation. Slows understanding. Say "Spending totals still count everything".
- 07-spending.desk.en "Personal · more refunds than spending  -162.37 €": a group called "Personal" that never appears in the edit dialog's group list (05). Cosmetic, but the user cannot find where "Personal" comes from.
- 33-period-menu.desk.en: "This month, Last month, Last 30 days, Year to date, Year, Last 12 months, All time". "Year" is ambiguous next to "Year to date". The app is built around payday, but there is no "Since payday / This pay period" preset. Slows a task. Add "This pay period" and rename "Year" to "Last calendar year" / "Ganzes Jahr …".
- `keep` 33-period-menu.phone.de: German presets read naturally ("Seit Jahresbeginn", "Gesamter Zeitraum").

## 09 Group drill, 10 Category drill

| Line | Score | Basis |
|---|---|---|
| 1 clarity | 8 | 09-drill-group.desk.en: Spent, per month chart, Top merchants, Categories, Transactions in one column |
| 5 naming | 8 | 10-drill-category.desk.en breadcrumb "< SPENDING > FOOD & DINING" + title "Groceries" |
| 6 consistency | 6 | 09-drill-group.desk.en search placeholder "Search merchant, purpose, note or amount" vs 02 "Search merchant, purpose, category or amount"; 09 "Top merchants · 8 of 9" vs 10 no count |
| 7 phone | 7 | 10-drill-category.phone.de: breadcrumb "< AUSGABEN > ESSEN & TRINKEN" kept, sub-tab strip stays |
| others | - | |

Findings
- `keep` 10-drill-category.desk.en breadcrumb with both parents: the only deep page with a full trail. Use the same pattern on 15-19 (they show only one parent).
- 09-drill-group.desk.en "Categories" card lists zero rows "Food & Dining 0×", "Food delivery 0×", and the filter chips repeat them with 0. Cosmetic. Hide zero categories or grey them.

## 11-13 Fixed costs (List, Calendar, Orbit) + 34 payday dialog

| Line | Score | Basis |
|---|---|---|
| 1 clarity | 7 | 11-recurring-list.desk.en "Fixed costs, on average per month 1,407.01 €" + "Next up" |
| 5 naming | 5 | 13-recurring-orbit.desk.en view switch "List | Calendar | Orbit": "Orbit" names a metaphor, not a task; 12-recurring-calendar.desk.en header "1,423.48 € fixed costs · 1,100.00 € saved" vs 11 "1,407.01 €" fixed costs |
| 6 consistency | 5 | 12-recurring-calendar.desk.en: calendar under "Fixed costs" shows salary and savings standing orders, while 11-recurring-list.desk.en banner says "3 savings plans … They live under Net worth" |
| 7 phone | 7 | 12-recurring-calendar.phone.de: List/Calendar/Orbit fits beside the title |
| others | - | |

Findings
- 11 vs 12 (desk.en): two "fixed costs" totals (1,407.01 € average vs 1,423.48 € this month) without saying which is which. Slows a task. Label the calendar figure "October: 1,423.48 € paid".
- 12-recurring-calendar.desk.en and 34-payday-details.desk.en: savings transfers ("Sparen", two "Sparplan" rows) and salary appear inside "Fixed costs", and 34's button "All fixed costs" leads there, but 11-recurring-list.desk.en says savings plans live under Net worth. The boundary between "fixed costs" and "savings plans" moves from screen to screen. Slows a task. Either call the section "Recurring" / "Regelmäßiges" (covers costs, savings and salary), or keep savings out of the calendar.
- 13-recurring-orbit.desk.en "Orbit" / "Dein Monat im Orbit": playful but tells nothing. Cosmetic. "Rhythm" / "Rhythmus" would say what the view groups by.
- 11-recurring-list.desk.en section "Running" (DE "Laufend"): unusual EN; "Active" reads better. Cosmetic.
- `keep` 11-recurring-list.desk.en "What changed · Noticed by Groschen itself" and the cross-link banner to Net worth: good wayfinding.
- `keep` 34-payday-details.desk.en: Balance now − Still going out = Free to spend; the dialog explains the hero. Rename the hero or the row so both say the same.

## 14 Net worth

| Line | Score | Basis |
|---|---|---|
| 1 clarity | 8 | 14-networth.desk.en "Today 44,931.92 €" + three account cards |
| 5 naming | 7 | 14-networth.desk.en "Add account · Say a house or a car loan outside your banks" is clear; "Direkt-Depot" card is the only card with a chevron (it links to Investments), unexplained |
| 6 consistency | 7 | 14-networth.desk.en "Savings plans" here vs 15-investments "Savings plan 300.00 € per month" vs 16 "Savings plan 300 € a month" (consistent) |
| 7 phone | 6 | 14-networth.phone.en strip "Net worth | Investments", but on 15-investments.phone.en the strip becomes "Investments | Analysis | Forecast | Pay-ins" and Net worth vanishes |
| others | - | |

Findings
- 14-networth.phone.en -> 15-investments.phone.en: the second-level strip changes its members when you tap "Investments"; the tab you came from disappears and only the small "< NET WORTH" link remains. Slows a task. Keep one strip: "Net worth | Depot | Analysis | Forecast | Pay-ins" (scrollable) or nest Analysis/Forecast/Pay-ins as a third-level strip below an unchanged first strip.
- 14-networth.desk.en Extra-Konto appears both as an account card and as a "Savings plan" card ("Standing order to savings"). Cosmetic; acceptable, but the plan card could say "into Extra-Konto".

## 15 Investments, 16 Forecast, 17 Analysis, 18 Pay-ins, 19 ETF detail, 32 hidden

| Line | Score | Basis |
|---|---|---|
| 1 clarity | 7 | 15-investments.desk.en "Depot value on 30 Oct 2026" hero |
| 5 naming | 5 | 15-investments.desk.en: EN page "Investments", hero "Depot value", category "Investments" (18 "Everything in the Investments category"), Settings tab "Investments": one word for a page, a category and a settings tab; DE splits them cleanly (Depot / Geldanlage) |
| 6 consistency | 6 | 19-etf.desk.en inner tabs "Overview | Analysis | Forecast | Facts" repeat the depot-level sidebar items Analysis/Forecast at a different scope |
| 7 phone | 6 | 15-investments.phone.en strip "Investments | Analysis | Forecast | Pay-ins": all reachable, but see strip finding |
| others | - | |

Findings
- 15-investments.desk.en / 18-inv-payments.desk.en / 23-settings-depot.desk.en: "Investments" is a page, a spending category ("Everything in the Investments category") and a settings tab. The hero already says "Depot value". Slows a task. EN: call the page "Portfolio" (or "Depot", as the hero does); keep "Investments" only as the category.
- 18-inv-payments.desk.en "Pay-ins": not an everyday EN word (DE "Einzahlungen" is fine). Cosmetic. "Contributions" or "Money paid in" (the card title already says "Money put in").
- 18-inv-payments.desk.en footer "Import price history" sits on the Pay-ins page; price history is not about pay-ins. Buried. Slows a task. Move it to Settings > Investments next to "Online ETF prices" (23) or to the Investments page's price-history banner.
- 16-inv-forecast.desk.en and 17-inv-analysis.desk.en: breadcrumb shows only "< INVESTMENTS", never "NET WORTH > INVESTMENTS" as 10 does. Cosmetic.
- 19-etf.desk.en tabs "Analysis / Forecast": same labels as the depot-level pages, one level down. The sidebar keeps "Investments" highlighted, so the user cannot tell whether "Analysis" here is the fund or the depot. Cosmetic. Suggest "Fund analysis", or a heading "This fund" above the tabs.
- 15-investments.desk.en and 19-etf.desk.en both show the same "Get full price histories? Turn on" banner, and 23-settings-depot has the toggle as "Online ETF prices". Three names (full price histories / online ETF prices / Kursverläufe). Cosmetic.
- `keep` 15-investments.phone.de "Sparerpauschbetrag 2026" with "Anpassen" that goes to settings: the German legal term is the right word; EN "Tax-free allowance" plus the DE term in 23 is a good bridge.
- 32-hidden-investments.desk.en: privacy mode keeps labels, percentages, structure: nav unaffected. `keep`.

## 20-28, 30 Settings

| Line | Score | Basis |
|---|---|---|
| 1 clarity | 7 | 28-settings-list.phone.en: every section has a one-line subtitle ("Passkeys, login and phones with fingerprint") |
| 5 naming | 6 | 20-settings-bank.desk.en tabs: "Hints & salary" joins two unrelated things; 27-settings-account.desk.de "Konto & Darstellung" uses "Konto", the same word as Girokonto/Extra-Konto |
| 6 consistency | 6 | 25-settings-privacy.desk.en "Export" card carries the line "Backups never contain the key that unlocks your bank PIN" (a Backups fact, repeated from 24) |
| 7 phone | 8 | 28-settings-list.phone.de: list -> sub page with "< EINSTELLUNGEN", better than eight tabs |
| others | - | |

Findings
- 20-settings-bank.desk.en tab bar has 8 tabs without subtitles; the phone list (28) has subtitles that explain each one. Slows a task on desktop. Use the phone's list as a left rail on desktop, or add the subtitles as tooltips.
- 22-settings-hints.desk.en "Hints & salary": salary/payday rules ("Count end-of-month salary for the next month", "Keep aside") drive the Overview hero; they are buried behind "Hints". Slows a task. Rename "Overview & payday" / "Übersicht & Zahltag", or split "Payday" into its own tab.
- 22-settings-hints.desk.en "Hints" vs Overview card "Worth a look" (DE "Hinweise" vs "Einen Blick wert"): the settings text bridges it ("Hints appear under 'Worth a look'"), which is good, but one name would be better. Cosmetic.
- 27-settings-account.desk.de "Konto & Darstellung" / "Konto": collides with bank accounts. Slows a task. "Profil & Darstellung" / "Benutzerkonto".
- 24-settings-backup.phone.de "Smart Recycle" stays English in DE and the option opposite is "Eigene". Cosmetic. "Automatisch ausdünnen" or keep the name but add DE subtitle (already present).
- 25-settings-privacy.desk.en: backup sentence under Export. Cosmetic; move to Backups only.
- 21-settings-categories.desk.en "That's you" (DE "Das bist du"): names under a card about categorising, controlling own-transfer detection. Clear text, odd heading. Cosmetic. "Your own names".
- 21-settings-categories.desk.en: "Custom groups" can be created here and from Spending; "Edit categories" lives here only. Fine, but Spending could link "Edit categories". Cosmetic.
- 30-settings-connect-dialog.desk.en: "Add a bank" button opens "Connect your bank" with primary "Done, start syncing" before anything is entered. Cosmetic naming; "Continue" until the bank is found.
- Log-out appears on desktop twice (sidebar footer icon and 27 Account) and on phone only in 27. Acceptable. `keep` 27 phone placement.

## 40-42 Wizard and login

| Line | Score | Basis |
|---|---|---|
| 1 clarity | 8 | 40-wizard-account.desk.en step list "1 Welcome · 2 Connect your bank · 3 Import history · 4 Smart features · 5 First sync" |
| 5 naming | 6 | 40-wizard-account.desk.en step 1 "Welcome / Your login" names a greeting, not the task; step 4 "Smart features" is vague |
| 6 consistency | 7 | 41-wizard-country.desk.en "Connect your bank" step asks "Where do you live?" first; same label as 30 dialog "Connect your bank" |
| 7 phone | 6 | 40-wizard-account.phone.de: five unlabelled bar segments, the step names from desktop are gone |
| others | - | |

Findings
- 40-wizard-account.phone.de: progress bar without step names. Slows a task slightly (user cannot see what comes next). Add "Schritt 1 von 5 · Zugang".
- 40-wizard-account.desk.en: rename step 1 "Your login", step 4 "Automatic help" or name its content ("Offline, sync, reminders" is the real list).
- `keep` 42-login.desk.en / .phone.de: language switch on the login card.

---

## Top 10

1. **03-transactions-review.desk.en / .phone.de**: "Needs review 39" (uncertain guesses), the banner "need a category from you", 8 rows that are all "Uncategorized" and a separate "Uncategorized" chip describe three different sets. Badge and list don't agree. *Slows a task.* Make chip, badge and banner describe one set; keep Uncategorized separate.
2. **15-investments.desk.en / 18-inv-payments / 23-settings-depot (EN)**: "Investments" is a page, a category and a settings tab at once. *Slows a task.* Call the page "Portfolio"/"Depot" (the hero already says "Depot value"), keep "Investments" for the category.
3. **14-networth.phone.en -> 15-investments.phone.en**: the phone second-level strip changes members ("Net worth | Investments" becomes "Investments | Analysis | Forecast | Pay-ins"); Net worth drops out. *Slows a task.* One stable strip, or a third level under it.
4. **12-recurring-calendar.desk.en, 34-payday-details.desk.en vs 11-recurring-list.desk.en**: savings standing orders and salary appear in "Fixed costs" and its button "All fixed costs", while the same page says savings plans "live under Net worth"; two different fixed-cost totals (1,407.01 vs 1,423.48 €). *Slows a task.* Rename the section "Recurring"/"Regelmäßiges", or keep savings out, and label which total is which.
5. **07-spending.desk.en / .phone.de + 02-transactions chip "Income"**: Income has no nav home; it hides in a toggle on a page titled "Spending"/"Ausgaben" (title and sub-tab don't follow the toggle). *Slows a task.* Add Income to nav or rename the page "In & out".
6. **22-settings-hints.desk.en**: payday/salary rules that drive the Overview hero are buried under "Hints & salary"; "Keep aside" (setting) vs "Put aside" (Sankey) / DE "Zurücklegen" vs "zurückgelegt" mean different things. *Slows a task.* Tab "Overview & payday"; rename the cushion "Safety cushion"/"Notgroschen".
7. **18-inv-payments.desk.en**: "Import price history" lives on the Pay-ins page; "Pay-ins" is not everyday English. *Slows a task.* Move import to Settings > Investments next to "Online ETF prices"; rename "Contributions".
8. **20-settings-bank.desk.en**: 8 desktop settings tabs without the explanations the phone list (28-settings-list.phone.en) has; "Konto & Darstellung" (27, DE) collides with bank accounts. *Slows a task.* Reuse the phone list with subtitles on desktop; rename "Profil & Darstellung".
9. **05-transactions-edit.desk.en / 08 / 09-drill-group.desk.en**: the catch-all category is "Housing (general)", "Housing" and "Food & Dining 0×" depending on screen, so a group lists a category with its own name. *Slows a task.* Always "(general)"/"(allgemein)".
10. **33-period-menu.desk.en**: no "This pay period" preset in a payday-centred app, and "Year" next to "Year to date" is ambiguous; 03 silently switches to "All periods" while the button still says "Jan – Oct 2026". *Slows a task.* Add pay-period preset, rename "Year", reflect overrides on the period button.

Keep: the desktop sidebar tree and its German labels (01-overview.desk.de), full breadcrumbs on 10-drill-category, the phone settings list with subtitles (28), the four plain bottom tabs (01-overview.phone.de), and the cross-link banners ("They live under Net worth", "All fixed costs", "Everything with Shell").
