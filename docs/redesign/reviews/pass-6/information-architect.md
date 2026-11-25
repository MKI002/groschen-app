# Groschen: review from an information architect

Scope: navigation, grouping, naming (English and German), duplication, buried features, whether the phone nav and the desktop nav match. I score only lines 1 (clarity of purpose), 5 (navigation and naming), 6 (consistency) and 7 (phone experience, only for navigation reach). The other lines get "-".

## Site map as I read it from the screenshots

```
Desktop sidebar (01-overview.desk.en / .desk.de)            Phone (01-overview.phone.de, 16-inv-forecast.phone.en)
-------------------------------------------------           -----------------------------------------------------
[logo] Groschen   [eye = hide amounts]                       Header: logo · sync chip "just now" · [eye] · [gear]
Overview / Übersicht            (dot = new hints)            Bottom tab 1: Overview / Übersicht
Transactions / Umsätze  [39]                                 Bottom tab 2: Transactions / Umsätze (dot, no number)
  tabs: All · Needs review 39 · Uncategorized · Income        same pills, scroll sideways
  -> edit dialog (category picker, "Everything with X")
Spending / Ausgaben                                          Bottom tab 3: Spending / Ausgaben
  toggle Spending|Income, "+ Your own group"                   top tabs: Ausgaben | Fixkosten
  -> group drill (Spending > Food & Dining)
     -> category drill (Spending > Food & Dining > Groceries)
  Fixed costs / Fixkosten                                      (Fixkosten tab)
    views: List · Calendar · Orbit
Net worth / Vermögen                                         Bottom tab 4: Net worth / Vermögen
  Investments / Depot                                          top tabs: Vermögen | Depot
    -> ETF page (Overview·Analysis·Forecast·Facts)             in Depot the row swaps to: Depot·Analyse·Prognose·Einzahlungen
    Analysis / Analyse                                         (Vermögen tab is replaced by a "< Vermögen" back link)
    Forecast / Prognose
    Pay-ins / Einzahlungen
--- footer ---
Bank status card "ING connected · Synced just now" [sync]    sync chip in header (no bank name)
Settings / Einstellungen                                     gear icon in header
  tabs: Bank & import · Categories · Hints & salary ·          the same 8 tabs, scroll sideways (3 visible at 390 px)
        Investments · Backups · Export & privacy ·
        Security · Account & look
User "Alex" + log-out icon                                   log out only under Settings > Account & look
Outside the app: wizard (Welcome, Connect your bank, Import history, Smart features, First sync), login
```

**Phone reach: complete.** Every desktop sidebar item can be reached on the phone: 4 bottom tabs, second-level top tabs (Fixkosten, Depot, Analyse, Prognose, Einzahlungen), and the gear for Settings. The weak points: Analysis, Forecast and Pay-ins sit three taps deep (Vermögen, then Depot, then the tab), and the tab row changes its contents when you enter Depot (see 15).

---

## 01 Overview (01-overview.desk.en/.desk.de/.phone.en/.phone.de, 31-hidden-overview.*)

| line | score | based on |
|---|---|---|
| 1 clarity of purpose | 9 | 01-overview.desk.en: "Available until payday" hero answers the main question first |
| 2-4 | - | |
| 5 navigation & naming | 8 | 01-overview.desk.en: sidebar tree "Spending > Fixed costs", "Net worth > Investments > Analysis/Forecast/Pay-ins" uses plain words; "Pay-ins" is the weak one |
| 6 consistency | 6 | 01-overview.desk.en vs 34-payday-details.desk.en: the hero says "Available until payday" but the dialog's total row says "Free to spend" |
| 7 phone | 8 | 01-overview.phone.de: bottom bar "Übersicht · Umsätze · Ausgaben · Vermögen" plus gear; all destinations reachable |
| 8-9 | - | |

Findings
- `keep` 01-overview.desk.de: German nav labels "Übersicht, Umsätze, Ausgaben, Fixkosten, Vermögen, Depot, Einzahlungen" are what a German banking customer actually says. "Umsätze" and "Depot" in particular match the bank's own words.
- `keep` "Worth a look" / "Einen Blick wert" hint card, linked by name from 22-settings-hints.desk.en ("Hints appear under 'Worth a look' on the Overview"). The bridge between the two names works.
- 01-overview.desk.en + 34-payday-details.desk.en: one number has three names: "Available until payday" (hero), "Free to spend" (dialog total), "Salary and free to spend" (22-settings-hints section title). **slows a task** (people search Settings for the wrong words). Fix: pick one, e.g. "Available until payday", and use it in all three places. DE likewise: "Frei verfügbar bis zum Gehalt".
- 01-overview.phone.de: the sync chip in the header shows only "gerade eben" with a dot, with no bank name and no verb. Desktop says "ING connected · Synced just now". **cosmetic**. Fix: "ING · gerade eben" or "Abgerufen: gerade eben".
- 01-overview.desk.en: the Sankey has "Uncategorized" on both the income side (43.20 €) and the spending side (510.60 €) with the same label. **cosmetic**. Fix: "Uncategorized income" / "Uncategorized spending".
- 01-overview.desk.en: the Sankey lists 9 spending groups, but 07-spending.desk.en shows a 10th, "Personal" (−162.37 €). Not shown on the Overview, so the two group lists differ. **cosmetic**.
- 31-hidden-overview.desk.en: the privacy toggle is an unlabeled eye icon next to the logo (desktop) and in the header (phone). Nowhere does the UI name the mode "Hide amounts". **cosmetic**. Fix: add a tooltip or label "Hide amounts / Beträge verbergen".

## 02-06 Transactions (02-transactions.*, 03-transactions-review.*, 04-transactions-filtered.*, 05-transactions-edit.*, 06-transactions-empty.*)

| line | score | based on |
|---|---|---|
| 1 | 8 | 02-transactions.desk.en: search field + "All · Needs review · Uncategorized · Income" pills make the page's job clear |
| 5 | 6 | 03-transactions-review.desk.en: "Needs review 39" pill vs "8 transactions" listed; "Needs review" and "Uncategorized" overlap |
| 6 | 6 | 05-transactions-edit.desk.en "Housing (general)" vs 08-spending-group-dialog.desk.en "Housing" vs 09-drill-group.desk.en "Food & Dining 0": three names for the catch-all category |
| 7 | 8 | 06-transactions-empty.phone.de: pills "Alle · Zu prüfen 39 · Ohne Kategorie · Einnahmen", Filter and sort all reachable |
| others | - | |

Findings
- 03-transactions-review.desk.en: the badge (sidebar and pill) says 39, the review list says "8 transactions" with the banner "These transactions need a category from you". The 39 seem to be the auto-sorted ones from the Overview hint ("Groschen sorted 39 transactions on its own. Do the categories look right?"), the 8 are uncategorized. One label covers two different queues. **slows a task**. Fix: split them into "To confirm (39)" and "No category (8)". Or make the badge count exactly what the tab lists.
- 03-transactions-review.desk.en: the "Needs review" view shows "All periods" in the summary while the period button still says "Jan – Oct 2026". The two scope indicators disagree. **cosmetic**. Fix: have the period button show "All time" while this tab ignores the period.
- 02-transactions.desk.en: "Uncategorized" pill and "Needs review" content overlap (03 lists only Uncategorized rows). **cosmetic**. Fix: keep one entry point.
- `keep` 05-transactions-edit.desk.en / .phone.de: the category picker grouped under HOUSING / FOOD & DINING / TRANSPORT headers, with "+ New" inside each group, plus "Everything with Shell >". The grouping is clear and teaches the taxonomy.
- 05-transactions-edit.desk.en: the toggle "Use this category for every transaction from this merchant" creates what 21-settings-categories.desk.en calls "Learned merchants", but the dialog never uses that word. **cosmetic**. Fix: add a hint "(remembered under Settings › Categories › Learned merchants)".
- `keep` 06-transactions-empty.desk.en: "No transactions match · Try a different search, filter or period" + "Clear filters". Correct wording.
- 02-transactions.desk.en: the account column shows "Girokonto"/"Extra-Konto" in English UI as well. These are account names from the bank, so that is fine.

## 07-10 Spending + drill-downs (07-spending.*, 08-spending-group-dialog.*, 09-drill-group.*, 10-drill-category.*, 33-period-menu.*)

| line | score | based on |
|---|---|---|
| 1 | 7 | 07-spending.desk.en: "Spending breakdown" + "Your year in days" are clear, but the page also holds an "Income" toggle |
| 5 | 5 | 07-spending.desk.en: "+ Your own group" vs "Groups | Categories" toggle; "group" means two different things on one screen |
| 6 | 6 | 07-spending.desk.en "Your own group" vs 21-settings-categories.desk.en "Custom groups"/"New group" vs 08 dialog title "New group" |
| 7 | 8 | 07-spending.phone.de: top tabs "Ausgaben | Fixkosten" make the sidebar sub-item reachable |
| others | - | |

Findings
- 07-spending.desk.en: **the word "group" is overloaded.** "Groups | Categories" toggle means the built-in category groups (Housing, Food & Dining), while "+ Your own group" / 08 "New group" means a cross-category tag ("for a car, a flat you rent out or a holiday"). On the same screen a person cannot tell whether a new group joins the Housing/Food list. **slows a task**. Fix: call the custom thing a "Project"/"Tag" ("Projekt"/"Topf"), or "Collection". Keep "group" for category groups.
- 08-spending-group-dialog.desk.en: "your main budget still counts everything normally". There is no Budget anywhere in the navigation. **cosmetic, but misleading**. Fix: "your totals still count everything normally".
- 07-spending.desk.en: a page named "Spending" carries a "Spending | Income" toggle. The nav label hides that income analysis lives here, and nobody looks for income under "Ausgaben". **slows a task**. Fix: either rename the page (e.g. "Categories"/"Kategorien", or "Money in & out"), or move income to its own sub-item.
- `keep` 09-drill-group.desk.en / 10-drill-category.desk.en: breadcrumb "SPENDING > FOOD & DINING", page title = category, and the sidebar keeps "Spending" active. A clear location.
- 09-drill-group.desk.en: the Categories card lists "Food & Dining 0" (the catch-all child named the same as its parent). Elsewhere it is "Food & Dining (general)". **cosmetic**. Fix: always use "(general)" / "(allgemein)".
- 08-spending-group-dialog.desk.en: the picker drops the "(general)" suffix that 05 uses ("Housing" chip next to "Rent"), so a person may think "Housing" picks the whole group. **slows a task**. Fix: same "(general)" label here.
- 33-period-menu.desk.en / .phone.de: "This month, Last month, Last 30 days, Year to date, Year, Last 12 months, All time". "Year" / "Jahr" does not say which year, and there is no custom range. **cosmetic**. Fix: "Calendar year 2026 ‹ ›" or "2025 / 2026" entries.
- 07-spending.desk.en: "Personal · more refunds than spending" is a group that never appears in the category picker headers in 05/08, which end with Insurance / Subscriptions. **cosmetic**.

## 11-13 Fixed costs (11-recurring-list.*, 12-recurring-calendar.*, 13-recurring-orbit.*)

| line | score | based on |
|---|---|---|
| 1 | 8 | 11-recurring-list.desk.en: "Fixed costs per month 1,407.01 €" + "Next up" + "What changed" |
| 5 | 6 | 11-recurring-list.desk.en: view switch "List · Calendar · Orbit"; "Orbit" names a metaphor, not a content; "Running" section header |
| 6 | 5 | 11-recurring-list.desk.en "1,407.01 €" vs 12-recurring-calendar.desk.en "1,423.48 € fixed costs" for the same month |
| 7 | 8 | 11-recurring-list.phone.de: reached via Ausgaben > Fixkosten top tab, the view switch is kept |
| others | - | |

Findings
- 11 vs 12 desk.en: two different "fixed costs" totals (1,407.01 € monthly average vs 1,423.48 € in October) with the same label. **slows a task** (which one is my number?). Fix: label them "per month on average" and "in October 2026".
- 12-recurring-calendar.desk.en: a page titled "Fixed costs" shows salary (Nordlicht 3,340 €) and savings standing orders ("Sparen −800 €", Sparplan) in its day list. Fine for a cash calendar, but the title no longer fits. **cosmetic**. Fix: header "October at a glance: fixed costs, savings, salary". The legend already does half of this.
- 13-recurring-orbit.desk.en: "Orbit" is a cute name. Nobody would look for "Orbit" to find out what is due by frequency. **cosmetic**. Fix: "By rhythm" / "Nach Rhythmus". Keep the visual.
- 11-recurring-list.desk.en: section "Running" (DE "Laufend"). In EN this reads like "in progress". **cosmetic**. Fix: "Active" / "Aktiv".
- `keep` 11-recurring-list.desk.en: the banner "3 savings plans run along: 1,100 € a month. They live under Net worth >". A cross-link that tells people where something lives.
- `keep` 11-recurring-list.phone.de: "Was sich getan hat" with "Neu dabei / ist wieder da / kommt nicht mehr / teurer geworden". Natural German.
- 11/12/34: "standing order" (Dauerauftrag), "savings plan" (Sparplan) and "fixed cost" are three overlapping words for recurring payments. They are used carefully, but the calendar legend shows "Standing order" while Net worth shows "Savings plans" for the same 800 €. **cosmetic**.

## 14 Net worth (14-networth.*)

| line | score | based on |
|---|---|---|
| 1 | 9 | 14-networth.desk.en: "Today 44,931.92 €" + account cards + "Add account" |
| 5 | 7 | 14-networth.desk.en: "Savings plans" section here vs "Pay-ins" page under Investments. Related content in two places |
| 6 | 7 | 14-networth.desk.en account card "synced · 30 Oct" vs 20-settings-bank "last fetched"; EN mixes sync/fetch |
| 7 | 8 | 14-networth.phone.de: top tabs "Vermögen | Depot" |
| others | - | |

Findings
- 14-networth.desk.en "Savings plans" vs 18-inv-payments.desk.en "Pay-ins": both show ETF savings-plan money. One shows it as plans, the other as payments. Neither links to the other. **slows a task**. Fix: a link "See every pay-in >" from the ETF plan cards to Pay-ins, and back.
- 14-networth.desk.en: "Add account / Konto hinzufügen" means manual assets, while 20-settings-bank "Add a bank" means connecting a bank. Two adding routes in two places, but the labels tell them apart. `keep`, add a hint "Bank accounts are added in Settings".
- 14-networth.desk.en: "Direkt-Depot" card has a ">" leading to Investments. Good, but Girokonto/Extra-Konto have no destination (e.g. their transactions). **cosmetic**. Fix: link those cards to Transactions filtered by account.

## 15-19 Investments / Depot (15-investments.*, 16-inv-forecast.*, 17-inv-analysis.*, 18-inv-payments.*, 19-etf.*, 32-hidden-investments.*)

| line | score | based on |
|---|---|---|
| 1 | 8 | 15-investments.desk.en: "Depot value on 30 Oct 2026" + holdings + tax-free allowance |
| 5 | 5 | 18-inv-payments.desk.en: "Pay-ins" title vs "Money put in" card vs "paid in" vs "Money paid in" toggle (15) vs "Value without deposits" legend (15): five wordings for one idea in EN |
| 6 | 6 | 19-etf.desk.en tabs "Overview · Analysis · Forecast" repeat the names of the app-level "Overview" and Investments "Analysis/Forecast" at a different scope |
| 7 | 6 | 15-investments.phone.de: the tab row swaps from "Vermögen | Depot" to "Depot · Analyse · Prognose · Einzahlungen"; the user loses the parent tab and needs a back link |
| others | - | |

Findings
- 18-inv-payments.desk.en: the EN "Pay-ins" is an unusual word (DE "Einzahlungen" is perfect). The concept also shows up as "Money put in", "paid in", "Money paid in", "deposits". **slows a task**. Fix: EN "Contributions" everywhere (nav, title, toggle, legend "Value without contributions").
- 15-investments.desk.en: EN copy uses German-isms: "Depot value", "85% of the depot", "Reinvests" chip. An English speaker says "Portfolio value", "of your portfolio", "Accumulating". **cosmetic**. DE "Depotwert", "Thesaurierend" are correct, so `keep` those.
- 15-investments.phone.de: on the phone, entering Depot swaps the second-level tab row (Vermögen | Depot → Depot | Analyse | Prognose | Einzahlungen). The Spending tab row never does this, so the user has to relearn where they are. **slows a task**. Fix: keep the row "Vermögen | Depot" and put Analyse/Prognose/Einzahlungen as a third, segmented row. Or show all five in one scrollable row.
- 19-etf.desk.en: the ETF page has its own "Overview · Analysis · Forecast · Facts" tabs, while the sidebar still has Investments > Analysis / Forecast (depot-wide). The same words at two levels make it unclear which one you are in. **slows a task**. Fix: name the ETF tabs "Chart · Risk · Projection · Fund facts", or prefix them with "This ETF".
- 18-inv-payments.desk.en / .phone.de: "Import price history" (CSV of prices) sits at the bottom of Pay-ins. It belongs with imports in 20-settings-bank "Import files" or 23-settings-depot. **slows a task** (it is buried). Fix: move it to Settings › Investments (keep a link here).
- 15-investments.desk.en and 19-etf.desk.en: the "Get full price histories? Turn on" banner repeats on two pages, and the setting is also in 23-settings-depot. Acceptable, but once dismissed it should go away everywhere. **cosmetic**.
- 23-settings-depot.desk.en: "Interest rate to compare with · Used for the Sharpe ratio". No screen shows a Sharpe ratio (17-inv-analysis.desk.en has "Ups and downs", "Drawdown", "Monthly returns"). **cosmetic**. Fix: name where it is used, or the metric it feeds.
- `keep` 16-inv-forecast.desk.en, 17-inv-analysis.desk.en: breadcrumb "< INVESTMENTS", plain headings ("Where it could go", "Ups and downs", "Drawdown").

## 20-27, 30 Settings (20-settings-bank.* … 27-settings-account.*, 30-settings-connect-dialog.*)

| line | score | based on |
|---|---|---|
| 1 | 7 | 20-settings-bank.desk.en: 8 tabs, each with clear cards |
| 5 | 6 | 20-settings-bank.desk.en tab bar: "Hints & salary" and "Export & privacy" pair unrelated topics; 20-settings-bank.phone.de shows only 3 of 8 tabs |
| 6 | 6 | 21-settings-categories.desk.en "Custom groups" vs 07 "Your own group"; 25-settings-privacy.desk.en repeats the backup-key note from 24 |
| 7 | 6 | 20-settings-bank.phone.de: tab row cut at "Hinweise & Gehalt", the other 5 tabs are off-screen with no hint |
| others | - | |

Findings
- 27-settings-account.desk.de / .phone.de: tab "Konto & Darstellung" and card "Konto". In German "Konto" already means a bank account all over the app (Girokonto, Extra-Konto, "Konto hinzufügen", "Währung der einzelnen Konten" on the same page). **slows a task**. Fix: "Profil & Darstellung" / card "Anmeldung" or "Benutzer". EN "Account & look" has the same clash with "Add account" on 14; use "Profile & appearance".
- 20-settings-bank.phone.de: the 8 settings tabs scroll sideways, and only "Bank & Import · Kategorien · Hinweise & Geh…" are visible. Security, Backups and the profile tab are hidden. **slows a task**. Fix: on phone, show Settings as a list of 8 rows (one screen each).
- 20-settings-bank.desk.en tab grouping: "Hints & salary" combines notification switches with payday logic. "Export & privacy" combines CSV export with network log. Backups is its own tab, but export is a backup-like action. **cosmetic**. Fix: "Data" tab = Backups + Export + Import files; "Payday" tab = salary + keep aside; "Hints" stays alone (or goes into Overview's "Worth a look" ⋯ menu).
- 25-settings-privacy.desk.en: "Backups never contain the key that unlocks your bank PIN…" appears under Export (as well as in 24 Backups). Wrong place. **cosmetic**.
- 26-settings-security.desk.en vs 27-settings-account.desk.en: "Password login" lives in Security, "Change password" lives in Account. "Log out" appears in Account, in Security ("Log out all others") and in the sidebar footer. **slows a task**. Fix: move "Change password" into Security › Login.
- 21-settings-categories.desk.en: "Categorizer · Built-in model" is selected while the description says "built-in model not found", with an "Offline" badge. These labels contradict each other. **cosmetic**.
- 21-settings-categories.desk.en: "Put uncertain guesses in 'Needs review' · …wait under Transactions, Needs review". Names the real place. `keep`.
- 30-settings-connect-dialog.desk.en: the button "Add a bank" opens "Connect your bank", whose only button is "Done, start syncing" even though the field is still empty. **slows a task**. Fix: "Continue", then "Start syncing" at the end. Also "Bankleitzahl" in the EN placeholder: write "bank code (BLZ)".
- 20-settings-bank.desk.en: EN mixes "Sync now", "Sync schedule", "last fetched just now", "Synced just now". DE consistently uses "abrufen". **cosmetic**. Fix: EN "sync" everywhere.
- 24-settings-backup.desk.en: "Smart Recycle" is a product name with no meaning for a user. The description saves it. **cosmetic**. Fix: "Automatic (recommended)".
- 27-settings-account.desk.en: Country "Not chosen", although 41-wizard-country asks "Where do you live?". It may be demo data, but the two places disagree. **cosmetic**.

## 34 Payday details dialog (34-payday-details.*)

| line | score | based on |
|---|---|---|
| 1 | 9 | 34-payday-details.desk.en: Balance now − Still going out = Free to spend, then the list |
| 5 | 8 | 34-payday-details.desk.en: "All fixed costs" button links to the right page |
| 6 | 6 | 34-payday-details.desk.en: title "Available until payday" but the total row "Free to spend" (see 01) |
| others | - | |

- `keep` 34-payday-details.desk.en: the math is laid out as a statement, and "All fixed costs" is the exit.

## 40-42 Wizard and login (40-wizard-account.*, 41-wizard-country.*, 42-login.*)

| line | score | based on |
|---|---|---|
| 1 | 8 | 40-wizard-account.desk.en: 5-step rail with sub-labels ("Over FinTS, read-only", "Older transactions") |
| 5 | 7 | 41-wizard-country.desk.en: step "Connect your bank" first asks "Where do you live?"; for the UK the step's sub-label "Over FinTS" is wrong |
| 6 | 7 | 40-wizard-account.desk.en step "Welcome / Your login" vs Settings "Account & look": the same thing gets three names |
| others | - | |

- 41-wizard-country.desk.en: the country/currency choice is hidden inside "Connect your bank". For non-German users the step then says automatic sync doesn't work. **cosmetic**. Fix: make it its own step "Country & currency" before the bank step, and rename the bank step's sub-label to suit (FinTS vs CSV).
- 40-wizard-account.desk.en: step 1 is called "Welcome" but it creates the login. **cosmetic**. Fix: "Your login" as the title.
- `keep` 42-login.desk.en: the language switcher on the login card and in the wizard means a German user never meets English first.

---

## Top 10

1. **"Group" means two things** on 07-spending.desk.en: the "Groups | Categories" toggle (built-in Housing/Food…) vs "+ Your own group" / 08 "New group" (cross-category tag). Rename the custom one ("Project"/"Tag", DE "Topf"/"Projekt"). *slows a task*
2. **"Needs review 39" lists 8** on 03-transactions-review.desk.en. One label covers two queues: 39 auto-sorted ones to confirm, 8 without a category. Split them into "To confirm" and "No category", or make the badge match the list. *slows a task*
3. **"Konto" clash in German**: 27-settings-account.desk.de "Konto & Darstellung" uses the same word as Girokonto/Extra-Konto/"Konto hinzufügen" (and EN "Account" vs "Add account" on 14). Rename it "Profil". *slows a task*
4. **Settings tabs on phone are hidden**: 20-settings-bank.phone.de shows 3 of 8 tabs, and Security/Backups are off-screen. Use a list of settings sections on phone. *slows a task*
5. **Investments sub-nav changes shape on phone**: on 15-investments.phone.de the tab row swaps from "Vermögen | Depot" to "Depot · Analyse · Prognose · Einzahlungen", unlike Spending's stable row. Keep the hierarchy stable. *slows a task*
6. **EN "Pay-ins" and its 5 synonyms** (18-inv-payments.desk.en, 15-investments.desk.en: "Money put in", "paid in", "Money paid in", "deposits"). Use "Contributions" throughout. Also replace the German-isms "Depot value", "Reinvests" with "Portfolio value", "Accumulating". *slows a task*
7. **Same names at two scopes**: 19-etf.desk.en tabs "Overview · Analysis · Forecast" vs app-level Overview and Investments > Analysis/Forecast. Rename the ETF tabs. *slows a task*
8. **Spending page hides Income**: 07-spending.desk.en "Spending | Income" toggle under the nav label "Spending/Ausgaben". Rename the page or give Income its own entry. *slows a task*
9. **One number, many names, and two fixed-cost totals**: "Available until payday" / "Free to spend" / "Salary and free to spend" (01, 34, 22), and "Fixed costs" 1,407.01 € (11) vs 1,423.48 € (12) with the same label. Unify the payday name and add "on average" / "in October" to the totals. *slows a task*
10. **Things in the wrong place**: "Import price history" buried at the bottom of 18-inv-payments, "Change password" in Account instead of Security (27 vs 26), the backup-key note under Export (25), "Hints & salary" pairing (22). Move each to where its topic lives. *slows a task*

`keep` (must stay): the German labels in the sidebar/bottom bar (01-overview.desk.de), breadcrumbs on drill pages (09/10/15-19), the grouped category picker (05), the "savings plans live under Net worth >" cross-link (11), "Worth a look" named from Settings (22), and the language switcher on login/wizard (40/42).
