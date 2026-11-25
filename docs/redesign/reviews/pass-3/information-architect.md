# Groschen: Information Architect review (pass 3)

Role: information architect. I score only **1 clarity of purpose**, **5 navigation and naming** and **6 consistency**. I put "-" for the others. Every score names the element and screenshot it is based on.

## Site map as I read it from the screenshots

```
DESKTOP SIDEBAR (all screens)              PHONE (bottom tab bar + header + sub-tab row)
-----------------------------------        ------------------------------------------------
[eye] hide amounts (icon only, by logo)     Header: logo | sync pill "gerade eben" | [eye] | [gear]
Overview  (dot = "Worth a look" items?)     Tab 1  Übersicht
Transactions (39 badge)                     Tab 2  Umsätze (dot badge, no number)
Spending                                    Tab 3  Ausgaben  -> sub-tabs: Ausgaben | Fixkosten
  └ Fixed costs  [List | Calendar | Orbit]  Tab 4  Vermögen  -> sub-tabs: Vermögen | Depot
Net worth                                          Depot     -> sub-tabs change to:
  └ Investments (DE: Depot)                          Depot | Analyse | Prognose | Einzahlungen
      ├ Analysis                                     (the "Vermögen" tab disappears, replaced by "< Vermögen")
      ├ Forecast                            Gear  -> Einstellungen (8 tabs in a horizontal scroller,
      └ Pay-ins (DE: Einzahlungen)                   3 visible at a time)
-- bottom --                                Logout: only Settings > Konto & Darstellung
ING connected / Synced just now (+ sync)
Settings
Alex  [log out icon]

Pages reached only by clicking in content (no nav entry):
  Spending > <group> drill (09)      breadcrumb "< Spending"
  Spending > <category> drill (10)   breadcrumb "< Income" (!) on a page titled "Income"
  Investments > <ETF> (19)           breadcrumb "< Investments", own tabs Overview | Analysis | Forecast | Facts
  Transaction dialog (05), New group dialog (08), Connect bank dialog (30)

Settings tabs: Bank & import | Categories | Hints & salary | Investments (DE: Depot) | Backups |
               Export & privacy | Security | Account & look (DE: Konto & Darstellung)
Global controls: period picker (top right, most pages; not on Fixed costs, Forecast, Pay-ins, ETF)
First run: 40 Wizard (Welcome, Connect your bank, Import history, Smart features, First sync) -> 42 Login
```

**Can the phone reach everything?** Yes. Every page in the desktop sidebar can be reached on the phone: Fixed costs through the Ausgaben sub-tab, Depot through the Vermögen sub-tab, and Analysis/Forecast/Pay-ins through a second sub-tab row that appears inside Depot. The costs are:
- The depth goes from 2 to 3 levels.
- The sub-tab row changes its level when you enter Depot.
- On the ETF page the sub-tab row disappears completely.
- The privacy toggle and Settings are icon-only.
- Log out is buried in the last Settings tab.

---

## 01 Overview (01-overview.desk.en / .desk.de / .phone.de / .phone.en)

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 8 | 01-overview.desk.en: "Available until payday" hero with "28 days to payday" timeline. It answers "what can I spend" at once. The "Worth a look" panel answers "what needs me". |
| 5 navigation and naming | 6 | 01-overview.desk.en sidebar: the tree (Spending > Fixed costs, Net worth > Investments > Analysis/Forecast/Pay-ins) is clear, but "Pay-ins" is not natural English. The unexplained yellow dot on "Overview" competes with the "39" badge on Transactions. |
| 6 consistency | 6 | 01-overview.desk.en: the Sankey labels "Put aside" and "Stays on the account" do not match the "Saved" card ("3,000.00 € invested · 1,991.75 € stays"), which drops the 8,095 € "Put aside" share that makes up most of the saved total. |
| 2,3,4,7,8,9 | - | |

Findings
- **01-overview.desk.en, sidebar "Pay-ins"**: not a word people use for money they paid into a portfolio. Use "Contributions" or "Deposits". The German "Einzahlungen" is correct. *slows a task.*
- **01-overview.desk.en, yellow dot on "Overview" nav item**: it has no label or legend. Next to the numeric "39" badge it reads as "unread". If it means "3 hints in Worth a look", show "3", or drop it. *cosmetic.*
- **01-overview.desk.en, "Saved" card subline vs Sankey**: the card names two of the three bar segments (invested, stays). The third, "Put aside 8,095 €", is visible in the Sankey but not named on the card. Name all three, using the same words as the Sankey. *slows a task.*
- **01-overview.desk.de, Sankey "Zurückgelegt" vs Settings "Zurücklegen" (22-settings-hints.desk.en "Keep aside")**: two different concepts share almost the same word. One is money moved to savings, the other is a cushion subtracted from "Frei verfügbar". Rename the setting "Notgroschen / Puffer" (EN "Safety cushion"). *slows a task.*
- **01-overview.phone.de, "Zeig auf ein Band, um ihm zu folgen"**: hover wording on a touch device. 16-inv-forecast.phone.de already says "tippen". Use "Tipp auf ein Band". *cosmetic.*
- **01-overview.phone.de, Sankey**: the left column (Gehalt / Zinsen & Dividenden / Ohne Kategorie) is dropped on the phone, so income sources are not visible there at all. *slows a task.*
- **keep: 01-overview.desk.en, "Worth a look" panel with direct "Check" / "Show" buttons**. It links straight into Transactions > Needs review and Fixed costs. Good cross-linking.
- **keep: 01-overview.phone.de, bottom tab bar Übersicht / Umsätze / Ausgaben / Vermögen**. The four words people use, matching the sidebar's top level one-to-one.

## 02–06 Transactions (02, 03-review, 04-filtered, 05-edit, 06-empty; all sizes)

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 8 | 02-transactions.desk.en: day-grouped list with merchant, category pill, account and amount. Obvious. |
| 5 navigation and naming | 5 | 03-transactions-review.desk.en: the "Needs review 39" tab shows a banner "These transactions need a category from you" and "8 transactions", all "Uncategorized". That makes "Needs review" and the neighbouring "Uncategorized" tab indistinguishable, and 39 ≠ 8. |
| 6 consistency | 5 | 03-transactions-review.desk.en, summary line "All periods" while the header picker says "Jan – Oct 2026". Also 02-transactions.desk.en "42,057.91 € in", while the Overview "Income" for the same period is 33,538.60 €. Same scope, different words and numbers, no explanation. |

Findings
- **03-transactions-review.desk.en, "Needs review" vs "Uncategorized" tabs**: the 01 hint says "Groschen sorted 39 transactions on its own. Do the categories look right?", so "Needs review" should mean "confirm the auto-sorted ones". The banner here instead says they "need a category from you". Pick one meaning:
  - "Needs review" = auto-categorized, waiting for a confirmation;
  - "Uncategorized" = no category.
  
  Then make the banner, the count and the badge agree. *blocks a task* (the user cannot tell which list clears the 39 badge).
- **03-transactions-review.desk.en, "All periods" next to a picker showing "Jan – Oct 2026"**: the page silently overrides the global period. Either grey out the picker with "Review ignores the period", or respect it. *slows a task.*
- **02-transactions.desk.en, "in / out" vs Overview "Income / Spending"**: the list totals include transfers, the Overview totals do not, but nothing says so. Label the list totals "money in / money out (incl. transfers)", or show the same figures. *slows a task.*
- **02-transactions.phone.de, search placeholder "Händler, Verwendungszweck, Kategorie oder Betr…"**: it is cut off. Shorten it to "Suchen…". Also, 09-drill-group.desk.en says "purpose, note or amount", while 02 says "purpose, category or amount", for the same search. *cosmetic.*
- **05-transactions-edit.desk.en, "Housing (general)" / "Insurance" (no "(general)")**: inconsistent. 08-spending-group-dialog.desk.en shows the same category as just "Housing", and 09-drill-group.desk.en lists it as "Food & Dining · 0×" with the group's own name. Always write "(general)", or call it "Other housing". *slows a task.*
- **05-transactions-edit.desk.en, "Everything with Shell >" footer link**: a good jump to a merchant view. **keep.**
- **06-transactions-empty.desk.en**: "No transactions match / Try a different search, filter or period" plus "Clear filters". Clear. **keep.**
- **keep: 02-transactions.desk.en, "Needs review" count is identical on the sidebar badge and the tab (39)**. Fix the list it leads to, not the badge.

## 07–10 Spending and drill-downs (07-spending, 08-spending-group-dialog, 09-drill-group, 10-drill-category, 33-period-menu)

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 7 | 07-spending.desk.en: "Spending breakdown" donut + ranked group list. The purpose is clear. "Your year in days" is a nice secondary view. |
| 5 navigation and naming | 4 | 10-drill-category.desk.en: breadcrumb "< INCOME" above the title "Income" (the parent is the page itself), the sidebar still highlights "Spending", and it shows 0.00 € while Overview Income is 33,538.60 €. Also 07-spending.desk.en: a "Spending / Income" toggle on a page named Spending. |
| 6 consistency | 5 | 08-spending-group-dialog.desk.en: the button is "Your own group", the dialog title is "New group", and Settings calls them "Custom groups". Meanwhile the "Groups" segmented control on 07 means something else (the category groups). |

Findings
- **10-drill-category.desk.en / .phone.de, breadcrumb "< Income" on page "Income" showing 0.00 €**: the "Income (general)" sub-category shares its name with the Income total. A user who toggles Spending → Income and clicks lands on an empty page labelled as if it were all income. Name the bucket "Other income" and make the breadcrumb point to "Spending › Income". *blocks a task.*
- **07-spending.desk.en, page "Spending" with toggle "Spending | Income"**: either rename the page "Money in & out" / "Categories", or move Income to its own nav item. On phone (07-spending.phone.de) "Ausgaben" appears three times stacked: sub-tab, H1 and toggle. *slows a task.*
- **07-spending.desk.en / 08 dialog / 21-settings-categories.desk.en, "group" means two things**:
  - the built-in category groups (the "Groups | Categories" toggle);
  - user "custom groups" (Car, Flat).
  
  Call the user ones "Projects" or "Tags" (DE "Projekte"), and use one verb on all entry points ("New project"). *slows a task.*
- **08-spending-group-dialog.desk.en, "your main budget still counts everything normally"**: "budget" appears nowhere in the navigation. Say "your spending totals". *cosmetic.*
- **07-spending.desk.en, "Personal · more refunds than spending"**: a group that does not exist in the category picker (05) or the Sankey (01). Users can't find where "Personal" comes from. *slows a task.*
- **09-drill-group.desk.en, "Categories" card lists "Food & Dining · 0×" and "Food delivery · 0×"**: zero rows add noise, and the first repeats the group name (see the "(general)" naming). Hide zero rows or fold them into "+2 unused". *cosmetic.*
- **keep: 09-drill-group.desk.en, breadcrumb "< SPENDING" + title + scoped transaction list with category chips**. This is the right drill-down pattern.
- **keep: 07-spending.phone.de, sub-tabs "Ausgaben | Fixkosten"**. This is how the phone reaches Fixed costs, and it works.
- **33-period-menu.desk.en, "Month" / "Year" options**: they don't say which month or year. The button shows "Jan – Oct 2026" rather than the chosen preset "Year to date". Show "Year to date (Jan – Oct 2026)". *cosmetic.*

## 11–13 Fixed costs (11-recurring-list, 12-recurring-calendar, 13-recurring-orbit)

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 8 | 11-recurring-list.desk.en: "Fixed costs per month 1,407.01 €" + "Next up" + "What changed". Exactly the questions people have. |
| 5 navigation and naming | 6 | 13-recurring-orbit.desk.en: "Orbit" is a whimsical view name that tells nobody what it shows. 11-recurring-list.desk.en: placing it under Spending is right, but it contains Netflix/Spotify/DAZN, which the Spending page groups as "Subscriptions". The overlap between "Fixed costs" and "Subscriptions" is not explained. |
| 6 consistency | 5 | 12-recurring-calendar.desk.en "1,423.48 € fixed costs" vs 11-recurring-list.desk.en "1,407.01 €" for the same month, and the calendar includes "Sparen", the Sparpläne and "Salary" (income) on a page called Fixed costs. |

Findings
- **12-recurring-calendar.desk.en, salary and savings in "Fixed costs"**: the legend mixes status (Paid, Expected) with type (Standing order, Salary). Either rename the calendar "Money calendar" / "Payment calendar", or keep it to fixed costs and show savings and salary as separate toggles. Explain why the total differs from the List view. *slows a task.*
- **13-recurring-orbit.desk.en, view name "Orbit"**: rename it "Rhythm" or "By frequency". *cosmetic.*
- **11-recurring-list.desk.en, footer "3 savings plans run along… They live under Net worth"**: a good cross-reference. **keep.** Note that it points to Net worth, while the investment ones also show under Investments > Pay-ins.
- **11-recurring-list.desk.en, "Running" section heading**: "Active" is the more common word. DE "Laufend" is fine. *cosmetic.*
- **11-recurring-list.phone.de**: the "In X days" next-date column from desktop is dropped on the phone, so only the frequency is left. *slows a task.*
- **keep: 11-recurring-list.desk.en "What changed" (New / is back / stopped coming / got more expensive)**. These are plain-language event names that reappear as hint toggles in 22-settings-hints, a consistent vocabulary.

## 14 Net worth (14-networth)

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 8 | 14-networth.desk.en: "Today 44,931.92 €" + trend + one card per account + "Add account". |
| 5 navigation and naming | 6 | 14-networth.desk.en: "Savings plans" lives here, but the same ETF plans drive Investments > Pay-ins and Forecast ("Savings plan 300 € a month"), so there are three homes for one concept. The "Direkt-Depot" card has a chevron (it goes to Investments), the other account cards don't, and there is no explanation. |
| 6 consistency | 6 | 14-networth.phone.de: "abgerufen" (fetched) on cards vs 14-networth.desk.en "synced". The sidebar uses "Synced just now", Settings uses "last fetched just now". |

Findings
- **14-networth.desk.en, account cards**: only Direkt-Depot is clickable. Girokonto and Extra-Konto have no destination, although a natural one exists (Transactions filtered to that account). *slows a task.*
- **14-networth.desk.en vs 20-settings-bank.desk.en, "synced" vs "fetched"**: pick one word (EN "synced", DE "abgerufen" or "synchronisiert") and use it in the sidebar, cards and Settings. *cosmetic.*
- **keep: 14-networth.phone.de, sub-tabs "Vermögen | Depot"**. This is the phone path to Investments.

## 15–19 Investments family (15-investments, 16-inv-forecast, 17-inv-analysis, 18-inv-payments, 19-etf, 32-hidden-investments)

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 7 | 15-investments.desk.en: "Depot value", chart and Holdings. Clear. 16-inv-forecast.desk.en "Where it could go… Assumptions, not a promise" is very honest. |
| 5 navigation and naming | 4 | 19-etf.desk.en: the ETF page has its own tabs "Overview | Analysis | Forecast | Facts", which collide with the sidebar's "Overview" and "Investments > Analysis / Forecast". On 19-etf.phone.de the Depot sub-tab row vanishes, so the phone user loses the sibling navigation. EN uses "depot" (a German loan word) in "Depot value", "85% of the depot" and "Reinvests". |
| 6 consistency | 4 | 16-inv-forecast.desk.en "Swing 15% a year" vs 17-inv-analysis.desk.en "Ups and downs ±17%": the same concept with two names and two values. 18-inv-payments.desk.en "Pay-ins" / "Money put in" vs 15-investments "Money paid in" toggle vs 16 "Paid in": four labels for one thing. |

Findings
- **19-etf.desk.en, tab names "Overview / Analysis / Forecast"**: they duplicate the global nav names at a different scope. Name them "Summary / Performance / Projection / Fund facts", or prefix them "This ETF". Keep the sidebar's sub-items highlighted on the "Investments" parent while on an ETF. *slows a task.*
- **19-etf.phone.de, no "Depot | Analyse | Prognose | Einzahlungen" row**: inconsistent with 15–18 on the phone, where that row is shown. Keep it, or show only the "< Depot" breadcrumb on all of them. *slows a task.*
- **15-investments.phone.de, sub-tab row switches level**: on 14 it is "Vermögen | Depot", on 15 it becomes "Depot | Analyse | Prognose | Einzahlungen" and "Vermögen" disappears. On Ausgaben (09-drill-group.phone.de) the row stays the same in a drill-down. One rule is needed. *slows a task.*
- **15-investments.desk.en, English "depot", "Reinvests"**: use "Portfolio" ("Portfolio value", "85% of your portfolio") and "Accumulating". Keep "Depot" in German. *cosmetic.*
- **16 vs 17, "Swing" vs "Ups and downs"**: one name (EN "Volatility (typical yearly swing)", DE "Schwankung" is already used on 17 and 16), and explain why the numbers differ (price history vs. period). *slows a task.*
- **18/15/16 "Pay-ins", "Money put in", "Money paid in", "Paid in"**: use one term, "Contributions", everywhere. *cosmetic.*
- **18-inv-payments.desk.en, "Import price history" at the bottom of Pay-ins**: this has nothing to do with pay-ins. It belongs in Settings > Investments next to "Online ETF prices", or on the ETF page. *slows a task* (hard to find).
- **18-inv-payments.desk.en, "Everything in the Investments category"**: there is no category called Investments in the picker (05) or Spending (07). The Sankey calls it "Invested". Name the real category. *slows a task.*
- **15-investments.desk.en vs 19-etf.desk.en**: the ETF card says "+7.5% · 474 €", the ETF page says "+1,160.97 € · +17.2%". Different scopes (period vs since purchase), unlabeled. Add "Jan – Oct" or "since first buy". *slows a task.*
- **23-settings-depot.desk.en, "Used for the Sharpe ratio"**: no Sharpe ratio appears on 17-inv-analysis.desk.en. The setting points to nothing visible. *cosmetic.*
- **keep: 15-investments.desk.en "Get full price histories?" banner → "Turn it off any time in Settings"**. It matches Settings > Investments "Online ETF prices" exactly.
- **keep: breadcrumbs "< NET WORTH", "< INVESTMENTS"** on 15–19 desktop. They are correct and consistent.

## 20–27, 30 Settings (20-bank, 21-categories, 22-hints, 23-depot, 24-backup, 25-privacy, 26-security, 27-account, 30-connect-dialog)

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 7 | 20-settings-bank.desk.en: "Bank connections" with "Bank login needed within 90 days" explained in plain words. |
| 5 navigation and naming | 5 | 20-settings-bank.phone.de: 8 tabs in a horizontal scroller with only "Bank & Import | Kategorien | Hinweise & Geh…" visible, and no overflow hint. 27-settings-account.desk.de "Konto & Darstellung": "Konto" already means bank account everywhere else (Girokonto, Extra-Konto, "Konto hinzufügen"). |
| 6 consistency | 5 | 25-settings-privacy.desk.en: "Internet access: Bank only", while the justETF toggle (23 Investments) and the ECB exchange rates (27 Account & look) that change it live in other tabs. 25 Export repeats the Backups note "Backups never contain the key…". |

Findings
- **20-settings-bank.phone.de, 8-tab scroller**: on the phone, replace it with a list (Settings home → section) or a select. Group the tabs into fewer sections:
  - Bank & import
  - Categories & groups
  - Hints & payday
  - Investments
  - Data (backups, export)
  - Privacy & security
  - Account & appearance
  
  *slows a task.*
- **27-settings-account.desk.de, "Konto & Darstellung"**: rename it "Benutzer & Darstellung" or "Profil & Darstellung". *slows a task* (users looking for bank accounts open it).
- **25-settings-privacy.desk.en, "Network and privacy"**: list every outbound switch here (justETF, ECB rates), or link to them. Right now the privacy tab can say "Bank only" while the switches that would change it live in other tabs. *slows a task.*
- **26-settings-security.desk.en "Password login" vs 27-settings-account.desk.en "Change password"**: password is split across two tabs. Put "Change password" under Security > Login. *slows a task.*
- **22-settings-hints.desk.en, "Hints & salary"**: two unrelated topics in one tab. "Salary and free to spend" (payday logic, Keep aside) is about the Overview hero. Rename the tab "Overview & payday" and put the Hints under it, or split it. *cosmetic.*
- **21-settings-categories.desk.en "Custom groups" + 07 "Your own group" + 08 "New group"**: the same feature has three names (see 07). *cosmetic.*
- **20-settings-bank.desk.en "Add a bank" → 30-settings-connect-dialog.desk.en "Connect your bank"**: fine. But the EN placeholder "Bank name, Bankleitzahl or IBAN" uses a German term. Use "bank code (BLZ)". The "No bank found…" error shows before anything is typed, and "Done, start syncing" is the only action. *slows a task.*
- **27-settings-account.desk.en, "Country: Not chosen"**, while the wizard (41-wizard-country.phone.de) asks "Wo wohnst du?" with Deutschland preselected. The two do not agree. *cosmetic.*
- **keep: 22-settings-hints.desk.en "Hints appear under 'Worth a look' on the Overview"** and **21 "Guesses… wait under Transactions, Needs review"**. Settings name the exact place in the UI where the effect shows up. This is excellent IA writing.
- **keep: 23-settings-depot.phone.de**: the tab scroller auto-scrolls to show the active tab.

## 31–32 Hide amounts (31-hidden-overview, 32-hidden-investments)

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 7 | 31-hidden-overview.phone.de: the blurred 9s make the mode obvious, and the eye icon turns gold when active. |
| 5 navigation and naming | 5 | 32-hidden-investments.desk.en: the only control is an unlabeled eye icon next to the "Groschen" wordmark, with no text, so it is easy to miss and its meaning is unclear. |
| 6 consistency | 8 | 31-hidden-overview.phone.de and 32-hidden-investments.desk.en: the same masking applies everywhere, including chart axes and hint text. |

Findings
- **32-hidden-investments.desk.en, eye icon by the logo**: add a tooltip or label "Hide amounts" (DE "Beträge verbergen"), and put the same item in Settings > Account & look so it can be found. *slows a task.*

## 40–42 First run and login

| Line | Score | Based on |
|---|---|---|
| 1 clarity of purpose | 8 | 40-wizard-account.desk.en: the 5 named steps with subtitles ("Connect your bank · Over FinTS, read-only") set expectations well. |
| 5 navigation and naming | 6 | 41-wizard-country.phone.de: on the phone, the step names are replaced by 5 unlabeled bars, so the user doesn't know what comes next. 40-wizard-account.desk.en: step 1 is called "Welcome" but actually creates the login. |
| 6 consistency | 7 | 42-login.desk.en: the same logo, language switch and button style as the wizard. |

Findings
- **40-wizard-account.desk.en, step "Welcome / Your login"**: name it "Your login" (DE "Dein Zugang"). *cosmetic.*
- **41-wizard-country.phone.de, progress bars**: add "Schritt 2 von 5 · Bank verbinden" text. *cosmetic.*
- **keep: 41-wizard-country.phone.de "Überspringen, vorerst CSV-Dateien nutzen"**. It is a clear exit, and it matches the "Import files" section in Settings > Bank & import.

---

## Top 10

1. **10-drill-category.desk.en: the "Income" category page.** Its breadcrumb "< Income" points to itself, it shows 0.00 €, and the sidebar still highlights Spending. The "Income (general)" bucket shares its name with total income. Rename it "Other income" and fix the breadcrumb to "Spending › Income". *blocks a task.*
2. **03-transactions-review.desk.en: "Needs review 39" opens an "8 transactions / need a category" list.** That is the same content as "Uncategorized". Define the two tabs separately, and make the badge, count and banner agree. *blocks a task.*
3. **19-etf.desk.en: the ETF tabs "Overview / Analysis / Forecast" reuse global nav names.** On 19-etf.phone.de the Depot sub-nav disappears. Rename the tabs ("Summary / Performance / Projection / Fund facts") and keep the sibling nav. *slows a task.*
4. **16-inv-forecast.desk.en "Swing 15%" vs 17-inv-analysis.desk.en "Ups and downs ±17%".** Same concept, two names, two numbers. "Pay-ins / Money put in / Money paid in / Paid in" is the same problem. Use one term per concept. *slows a task.*
5. **07-spending.desk.en: "Group" is overloaded, and "Spending" contains "Income".** The category groups and the user's "Your own group / New group / Custom groups" share one word. Call the user ones "Projects", and give Income a clearer home. *slows a task.*
6. **20-settings-bank.phone.de: 8 settings tabs in a hidden horizontal scroller.** About 5 tabs are invisible, and Log out sits in the last one. Use a section list on phone and merge the tabs into about 6 sections. *slows a task.*
7. **15-investments.phone.de: the phone sub-tab row changes level.** "Vermögen | Depot" becomes "Depot | Analyse | …", while the Ausgaben drill-downs keep their row. Use one rule for second-level navigation on the phone. *slows a task.*
8. **12-recurring-calendar.desk.en: the Fixed costs calendar shows 1,423.48 € and includes salary and savings, while List says 1,407.01 €.** Rename it "Payment calendar" or filter it, and explain the totals. *slows a task.*
9. **01-overview.desk.de "Zurückgelegt" (savings) vs 22-settings-hints "Zurücklegen" (cushion); 27-settings-account.desk.de "Konto & Darstellung" vs bank "Konto".** Similar German words point to different concepts. Rename the setting "Puffer" and the tab "Profil & Darstellung". *slows a task.*
10. **18-inv-payments.desk.en "Import price history" and 23-settings-depot "Sharpe ratio".** Features sit in the wrong place, or point to a metric that isn't shown. Move the import to Settings > Investments, and either show the Sharpe ratio on Analysis or drop the reference. *slows a task.*

Keep: the sidebar tree and its 1:1 match with the phone tab bar (01-overview.desk.en / .phone.de), the breadcrumbs on drill-downs (09, 15–19 desktop), the "Worth a look" deep links (01), and Settings text that names the exact UI location of an effect (21, 22).
