# Groschen — Information Architecture review (round 0)

Role: information architect. I judge navigation, grouping and naming in English and German. I score only lines 1 (clarity of purpose), 5 (navigation and naming), 6 (consistency) and 7 (phone experience, for navigation reach only). All other lines are "-".

## Site map, as read from the screenshots

```
Desktop sidebar (01-overview.desk.en)          Phone (01-overview.phone.de)
-------------------------------------          ------------------------------------------
Overview / Übersicht                           Tab 1  Übersicht
Transactions / Umsätze  [badge 39]             Tab 2  Umsätze  [dot only, no count]
Spending / Ausgaben                            Tab 3  Ausgaben
  ├─ (toggle in page) Spending | Income          ├─ toggle Ausgaben | Einnahmen
  │    └─ drill: group (09), category (10)       ├─ 2nd toggle Ausgaben | Fixkosten   <- only way to Fixkosten
  └─ Fixed costs / Fixkosten                     └─ Fixkosten: Liste | Kalender | Orbit
       └─ List | Calendar | Orbit
Net worth / Vermögen                           Tab 4  Vermögen
  └─ Investments / Depot                         └─ (no visible entry; only via the "Direkt-Depot" card chevron)
       ├─ Forecast / Prognose                         Depot tabs: Überblick | Prognose | Analyse | Einzahlungen
       ├─ Analysis / Analyse                          └─ ETF detail (19): Überblick | Analyse | Prognose | Fakten
       ├─ Payments / Einzahlungen
       └─ ETF detail (19, not in sidebar): Overview | Analysis | Forecast | Facts
----
ING connected (sync card)                      Header pill "gerade eben" (sync)
Settings / Einstellungen                       Header gear icon
  Bank & import | Categories | Hints & salary | Investments | Backups | Export & privacy | Security | Account & look
User "Alex" + log-out icon                     (log-out only inside Settings > Konto & Darstellung)
Eye icon (hide amounts)                        Header eye icon
Global: period picker (Jan–Oct 2026) on most pages, not on Fixed costs / Forecast / Settings
First run: Wizard (40 Welcome -> 41 Connect bank/country -> Import -> Smart features -> First sync), Login (42)
```

Reach check (phone vs desktop): every desktop destination is reachable on phone, but three are hidden behind non-obvious doors: Fixed costs (second segmented control inside "Ausgaben"), Investments/Depot (a card chevron on "Vermögen"; no tab or link label), and Log out (deep inside Settings tab 8). Settings is a gear icon instead of a tab, which is fine.

Scoring legend: 1 clarity, 2 hierarchy, 3 task efficiency, 4 data presentation, 5 navigation and naming, 6 consistency, 7 phone experience, 8 accessibility, 9 visual craft.

---

## 01 Overview (desk.en, desk.de, phone.en, phone.de) + 31 hidden overview

| Line | Score | Based on |
|---|---|---|
| 1 | 8 | `01-overview.desk.en`: "Available until payday" hero and "Worth a look" card state the purpose of the page at once |
| 2–4 | - | |
| 5 | 7 | `01-overview.desk.en`: sidebar tree, where "Fixed costs" sits under Spending and Forecast/Analysis/Payments under Investments under Net worth. That is three levels in a one-person app |
| 6 | 6 | `01-overview.desk.en`: "Worth a look" says "39 bookings" while the sidebar says "Transactions" |
| 7 | 7 | `01-overview.phone.de`: tab bar "Übersicht / Umsätze / Ausgaben / Vermögen" uses short native words, but the count badge 39 becomes a bare dot |
| 8–9 | - | |

Findings
- `01-overview.desk.en`, "Worth a look" row 1: "Groschen sorted 39 bookings on its own". The English UI mixes "bookings" (a calque of *Buchungen*) with "Transactions" (sidebar, page title). In German both are "Umsätze", so there the wording is consistent. **slows a task**. Suggestion: use "transactions" everywhere in English.
- `01-overview.phone.de`, tab bar "Umsätze": the desktop badge "39" is reduced to an unlabelled dot, so on phone the user cannot tell how much review work is waiting. **cosmetic**. Show the number, as the sidebar does.
- `01-overview.desk.en`, sidebar: the "Overview" item carries a yellow dot with no explanation. It probably stands for the 3 hints, but it looks the same as the "Transactions" alert. **cosmetic**.
- `01-overview.desk.en`, Sankey targets: "Put aside", "Stays on the account" and "Invested" sit next to the "Saved" card ("3,000 invested · 1,991.75 stays"). The card leaves out "Put aside 8,095.40", so the reader cannot reconcile 13,087.15 with the sub-parts. Different words describe the same money buckets. **slows a task**.
- keep: `01-overview.desk.de` / `phone.de`, the hero label "Frei verfügbar bis zum Gehalt" and its EN counterpart "Available until payday". These are the words people use.
- keep: `31-hidden-overview.phone.de`, the eye icon in the header is the same control as the desktop eye next to the logo, and it shows an active state.

## 02–06 Transactions (list, review, filtered, edit, empty)

| Line | Score | Based on |
|---|---|---|
| 1 | 8 | `02-transactions.desk.en`: title, search and the chips "All / Needs review / Uncategorized / Income" make the job clear |
| 5 | 6 | `03-transactions-review.desk.en`: the "Needs review" chip leads to the banner "These bookings need a category from you", which mixes up review and uncategorized |
| 6 | 5 | `03-transactions-review.desk.en`: the summary line changes to "All periods · 774 transactions" while the header picker still says "Jan – Oct 2026" |
| 7 | 6 | `02-transactions.phone.de`: the chip row is cut off at "Einnahmen" and the search placeholder is cut off at "…oder Betr" |

Findings
- `03-transactions-review.desk.en` / `phone.de`, banner. The Overview calls these items auto-sorted guesses to *check* ("Do the categories look right?"). The banner says they "need a category from you" (DE: "brauchen eine Kategorie von dir"), which is the meaning of the separate "Uncategorized" chip. Two chips, one explanation. **slows a task**. Suggestion: "Groschen guessed these categories. Confirm or change them."
- `03-transactions-review.desk.en`, period. Review silently switches to "All periods", but the period picker still shows "Jan – Oct 2026". The scope shown and the scope applied differ. **slows a task**. Make the picker show "All time" while review is open, or say "(all periods)" on the chip.
- `21-settings-categories.desk.en` calls the same queue "Transactions, To review", while the chip says "Needs review". This is a third name for one place. **cosmetic**.
- `02-transactions.phone.de`, chip row. "Einnahmen" is clipped at the screen edge and nothing signals that the row scrolls. **slows a task**. Put "Filter" and the sort control on the same row, or wrap the chips.
- `05-transactions-edit.desk.en`, category picker. The parent options are named "Housing (general)" here but "Housing" in the custom-group dialog (`08-spending-group-dialog.desk.en`). **cosmetic**.
- `05-transactions-edit.desk.en`. The toggle "Use this category for every transaction from this merchant" appears straight under the "SUBSCRIPTIONS" heading, so it reads as belonging to that group. **slows a task**. Separate it from the list with a divider or put it in the footer.
- `05-transactions-edit.desk.en`, category "Broadcast fee" under Housing. An English speaker would not recognise this. "TV licence (Rundfunkbeitrag)" would be clearer. The German "Rundfunkbeitrag" is correct. **cosmetic**.
- keep: `05-transactions-edit.desk.en`, the "Everything with Shell ›" link in the dialog footer. It is a good cross-link to the merchant.
- keep: `06-transactions-empty.desk.en`, the empty state "No transactions match / Try a different search, filter or period" together with "Clear filters".
- `06-transactions-empty.phone.de`. A large empty gap pushes the page title down about 150 px. **cosmetic**.

## 07–10 Spending, group dialog, drill-downs; 33 period menu

| Line | Score | Based on |
|---|---|---|
| 1 | 7 | `07-spending.desk.en`: "Spending breakdown" and "Your year in days" are clear. The "Spending / Income" toggle on a page titled Spending blurs what the page is for |
| 5 | 4 | `07-spending.phone.de`: page title "Ausgaben", then toggle "Ausgaben \| Einnahmen", then a second toggle "Ausgaben \| Fixkosten". The same word appears three times, at three levels |
| 6 | 5 | `09-drill-group.desk.en`: "79 bookings" in the hero but "79 transactions" in the list below |
| 7 | 4 | `07-spending.phone.de`: Fixed costs is reachable on phone only through the second segmented control |

Findings
- `07-spending.phone.de`, two stacked segmented controls. "Ausgaben | Einnahmen" is a data filter, while "Ausgaben | Fixkosten" switches the page. Both start with "Ausgaben", and the second is the only door to Fixkosten on phone. **blocks a task** (finding Fixkosten on phone). Suggestion: make Fixkosten a real destination (for example a fifth tab "Fixkosten", or a link row "Fixkosten · 1.407 €/Monat ›" on Ausgaben). Keep only one toggle, Ausgaben/Einnahmen.
- `07-spending.desk.en`, "Spending | Income" toggle. Income lives inside "Spending", so a user looking for income will not find it in the sidebar. **slows a task**. Rename the nav item to "Money in & out" / "Ein- & Ausgaben", or add an "Income" entry.
- `07-spending.desk.en`, "Groups | Categories" next to "+ Your own group". "Group" means both the built-in category parents (Housing…) and user-made cross-category tags ("A custom group collects bookings across categories…", `08`). **slows a task**. Call the custom ones "Projects" / "Projekte" or "Tags".
- `08-spending-group-dialog.desk.en`, dialog copy: "You find it under Spending". Custom groups are also managed in `21-settings-categories` ("Custom groups · New group"). Two homes are acceptable, but they should cross-link.
- `10-drill-category.desk.en`. Eyebrow "INCOME" and title "Income" both say the same thing, the sidebar highlights "Spending", and the page does not say which category this is. There is also no back link. **slows a task**. Use the eyebrow as a clickable breadcrumb ("‹ Spending / Income") and show the category name.
- `09-drill-group.desk.en` / `phone.de`. The eyebrow "SPENDING" / "AUSGABEN" is the only way back up, and it does not look clickable. On phone this leaves the user with only the browser back gesture. **slows a task**.
- `09-drill-group.desk.en`, the Categories card lists "Food & Dining · 0×" (the parent's own bucket) next to its children. Seeing the parent name inside its own drill is confusing. **cosmetic**. Hide 0× rows or label it "Other / general".
- `07-spending.desk.en`, the "Personal · more refunds than spending −162.37 €" row. A negative value in a spending list is a naming problem ("Personal" says nothing about what it holds). **cosmetic**.
- `33-period-menu.desk.en`. The menu items "Month" and "Year" don't say which month or year. The trigger shows "Jan – Oct 2026" while the checked item is "Year to date", so the label and the choice use different vocabularies. **cosmetic**.
- keep: `09-drill-group.desk.en`, the structure Top merchants → Categories → Transactions with category chips. It is an excellent drill hierarchy.

## 11–13 Fixed costs (list, calendar, orbit)

| Line | Score | Based on |
|---|---|---|
| 1 | 7 | `11-recurring-list.desk.en`: "Fixed costs per month 1,407.01 €" plus "Next up". The purpose is clear |
| 5 | 5 | `13-recurring-orbit.desk.en`: the view name "Orbit" tells the user nothing |
| 6 | 4 | `12-recurring-calendar.desk.en`: "2,523.48 € fixed costs this month" vs `11`: "1,407.01 € per month". The calendar counts savings plans ("Sparen −800", "Sparplan −250") and salary as fixed costs |
| 7 | 5 | `11-recurring-list.phone.de`: the header crams "Fixkosten" + "Liste/Kalender/Orbit" + "Ausgaben/Fixkosten" into two rows |

Findings
- `12-recurring-calendar.desk.en`, header total. The calendar shows the same page title as the list but a different definition (it includes standing orders to savings and salary). Users will see two "fixed costs" figures that disagree by 1,100 €. **blocks a task** (trusting the number). Call the calendar "Payment calendar", or show the savings and salary as a separate subtotal.
- `11-recurring-list.desk.en`. The section "Running" and the body "13 recurring payments" use the words "Fixed costs", "recurring payments", "Running" and "subscriptions" (in `22` hints) for one set. Netflix and Spotify are subscriptions rather than fixed costs in everyday German ("Abos" is even a spending group in `07`). **slows a task**. Consider "Regular payments" / "Regelmäßige Zahlungen" as the nav label.
- `11-recurring-list.desk.en`, bottom card: "3 savings plans run along… They live under Net worth". This is a good cross-link. The plans actually sit on Net worth (`14`), not under Investments › Payments, so the pointer is correct. keep.
- `13-recurring-orbit.desk.en`. "Orbit" works as a playful extra, but in a three-way switch it costs the user a tap to discover what it is. **cosmetic**. A tooltip or a label like "Rhythm" would help.
- `12-recurring-calendar.desk.en`, side panel. The German user labels "Sparen" and "Sparplan IE00…" appear in the English UI. These are bank data, so that is acceptable, but the rows mix "standing order" with "monthly". **cosmetic**.
- keep: `11-recurring-list.desk.en`, "What changed" with plain sentences ("Disney+ stopped coming", "Spotify got more expensive").

## 14–19 Net worth, Investments, Forecast, Analysis, Payments, ETF

| Line | Score | Based on |
|---|---|---|
| 1 | 8 | `14-networth.desk.en`: "Today 44,931.92 €", the account cards and "Savings plans" make the purpose clear |
| 5 | 5 | `18-inv-payments.desk.en`: the nav label "Payments" means deposits into the depot (DE "Einzahlungen"), which collides with "payments" in Fixed costs and Overview |
| 6 | 5 | `19-etf.desk.en`: tab order "Overview \| Analysis \| Forecast \| Facts" vs the depot's sidebar order "Forecast, Analysis, Payments" |
| 7 | 5 | `14-networth.phone.de`: no visible way into Depot except the chevron on the "Direkt-Depot" card |

Findings
- `14-networth.phone.de`. The tab "Vermögen" lands on Net worth, which shows no "Depot" link or tab. The only entry is a small chevron on the "Direkt-Depot" card. On desktop the same page is a named sidebar item with three children. **blocks a task** (finding Prognose/Analyse on phone). Add a "Depot ›" row, or put the "Überblick / Prognose / Analyse / Einzahlungen" tab strip on Vermögen.
- `18-inv-payments.desk.en`. English "Payments" is too generic: the overview's "14 payments still to come" and "13 recurring payments" use the same word for outgoing bills. The German "Einzahlungen" is right. **slows a task**. Use "Deposits" or "Contributions" in English.
- `18-inv-payments.desk.en` vs `phone.de`, row action. English "Not counted" reads as a status, while German "Nicht zählen" reads as an action. One of the two languages is giving the wrong meaning. **slows a task**. Use "Don't count" / "Nicht zählen".
- `15-investments.desk.en`, naming split. The English nav says "Investments", but the page copy says "Depot value", "85% of the depot", "Direkt-Depot". In German "Depot" is consistent everywhere (nav, title, eyebrow). English readers say "portfolio". **cosmetic**.
- `15-investments.phone.en`, sub-tab "Overview". It reuses the name of the top-level page "Overview". **cosmetic**. Use "Summary" / "Holdings".
- `19-etf.desk.en`. The ETF tabs (Overview, Analysis, Forecast, Facts) and the depot tabs (Overview, Forecast, Analysis, Payments) put the same concepts in a different order. **cosmetic**. Use the same order.
- `15-investments.desk.en` + `19-etf.desk.en`. The "Get full price histories? Turn on" banner is repeated on both pages and again as a toggle in `23-settings-depot`. That is acceptable as an opt-in, but it should disappear everywhere once dismissed.
- `15-investments.desk.en`, "Tax-free allowance 2026 · Adjust" next to `23-settings-depot.desk.en` "Tax-free allowance 1000". Two places edit one value. That is fine if "Adjust" deep-links to the setting.
- `14-networth.desk.en`. "Savings plans" on Net worth and "Payments" (deposits) under Investments are two views of the same ETF plans, each in a different branch. **cosmetic**.
- keep: `16-inv-forecast.desk.en` / `phone.de` eyebrows ("INVESTMENTS" / "DEPOT") with the parent-child depot tab strip on phone. They are clear and consistent across languages.
- keep: German labels "Prognose", "Analyse", "Sparerpauschbetrag", "Thesaurierend". They are the right domain words.

## 20–27, 30 Settings

| Line | Score | Based on |
|---|---|---|
| 1 | 7 | `20-settings-bank.desk.en`: the Bank & import tab is clear about what it controls |
| 5 | 5 | `20-settings-bank.desk.en`: eight tabs, with odd pairs such as "Hints & salary" and "Account & look" |
| 6 | 4 | `20-settings-bank.desk.en`: "Every day at 06:00" vs "Next sync tomorrow at 05:00"; `24-settings-backup.desk.en`: "Next backup tomorrow at 02:00" vs "Time of day 03:00" |
| 7 | 4 | `20-settings-bank.phone.de`: only 3 of 8 tabs are visible ("Bank & Import, Kategorien, Hinweise & Gehalt"). `27-settings-account.phone.de` shows the strip scrolled to "& Datenschutz" (cut-off label) |

Findings
- `20-settings-bank.phone.de` / `27-settings-account.phone.de`, tab strip. Five of the eight sections are hidden off-screen, and when scrolled a label is cut to "& Datenschutz". On phone the main way to log out sits in the last, hidden tab. **slows a task**. On phone use a list of sections (one row per section, drill in) instead of tabs.
- `22-settings-hints.desk.en`, "Hints & salary". The tab combines notification rules with the payday-hero logic ("Salary and free to spend", "Keep aside"). Users will look for the payday settings near the Overview hero, not under "Hints". **slows a task**. Split it into "Hints" and "Payday", and link "Available until payday" on the Overview to it.
- `22-settings-hints.desk.en`, "Salary and free to spend". The Overview hero is "Available until payday" and the "Keep aside" description quotes "Available until payday". That is two names for the hero. **cosmetic**.
- `25-settings-privacy.desk.en`. The Export card ends with "Backups never contain the key that unlocks your bank PIN…", which repeats `24` and does not belong to Export. **cosmetic**.
- `27-settings-account.desk.en` vs `26-settings-security.desk.en`. "Change password" and "Log out" live in Account, while "Password login", "Logged-in devices" and "Log out all others" live in Security. Login matters are split across two tabs. **slows a task**. Move the password and log-out controls into Security.
- `27-settings-account.desk.en`, "Country: Not chosen", although the wizard (`41-wizard-country`) asks "Wo wohnst du?". If the wizard did set it, this is a state mismatch; if not, the label should explain what is used by default. **cosmetic**.
- `23-settings-depot.desk.en`. The tab is named "Investments" but its content is depot-specific (Sharpe rate, Sparerpauschbetrag, ETF prices). That is fine, but the "Sharpe ratio" this helps compute appears nowhere on `17-inv-analysis`, so the setting has no visible target. **cosmetic**.
- `30-settings-connect-dialog.desk.en`. "No bank found by that name" is shown before the user types anything, and the primary button "Done, start syncing" appears before any bank is chosen. The labels do not match the step the user is on. **slows a task**.
- `20-settings-bank.desk.en`. The bank verbs are mixed: "Sync now", "last fetched", "Synced just now" (sidebar), with "abrufen / Abruf" in German. German is consistent, while English mixes "sync" and "fetch". **cosmetic**.
- keep: `20-settings-bank.desk.en`, "I logged in to my bank" with the 90-day explanation. It is honest, uses plain words, and puts the action next to the problem.
- keep: `21-settings-categories.desk.en`, "That's you". It is a clear, human name for own-transfer detection.

## 40–42 Wizard and login

| Line | Score | Based on |
|---|---|---|
| 1 | 8 | `40-wizard-account.desk.en`: the step rail "Welcome / Connect your bank / Import history / Smart features / First sync" with subtitles |
| 5 | 7 | `40-wizard-account.desk.en`: step 1 is titled "Welcome" with the subtitle "Your login". The step's real job is in the subtitle |
| 6 | 6 | `41-wizard-country.phone.de`: the step labels vanish on phone (only 5 bars) |
| 7 | 5 | `41-wizard-country.phone.de`: the skip link is cut off, "Überspringen, vorerst CSV-Dateien nu…" |

Findings
- `41-wizard-country.phone.de`. The skip option is truncated and sits off-centre above the "Weiter" button. Users may not see that CSV-only is possible. **slows a task**.
- `41-wizard-country.phone.de`. The page heading "Bank verbinden" sits on a screen whose first question is "Wo wohnst du?". Country is a hidden sub-step. **cosmetic**.
- keep: `40-wizard-account.desk.en`, "You can change everything later under Settings. There are no config files to edit."
- keep: `42-login.desk.en`, a language switch on the login card.

---

## Top 10

1. **blocks a task**: `14-networth.phone.de`. Phone users have no visible way into Depot (Prognose/Analyse/Einzahlungen); the only entry is the chevron on the "Direkt-Depot" card. Add a "Depot ›" row or the depot tab strip on Vermögen.
2. **blocks a task**: `07-spending.phone.de`. Fixkosten is reachable only through a second "Ausgaben | Fixkosten" toggle stacked under "Ausgaben | Einnahmen" ("Ausgaben" appears three times). Make Fixkosten a real destination (fifth tab or a link row).
3. **blocks a task**: `12-recurring-calendar.desk.en` shows "2,523.48 € fixed costs this month", while `11-recurring-list.desk.en` shows "1,407.01 € per month". The calendar counts savings plans and salary under the same title. Rename the calendar or split out the subtotals.
4. **slows a task**: `03-transactions-review.desk.en`. "Needs review" is explained as "These bookings need a category", which is the meaning of "Uncategorized". The Overview calls it "check the categories" and Settings calls it "To review". Use one name and one meaning.
5. **slows a task**: `03-transactions-review.desk.en`. Review silently switches to "All periods" while the picker still shows "Jan – Oct 2026".
6. **slows a task**: `18-inv-payments.desk.en`. The English nav label "Payments" (deposits) collides with bill "payments" elsewhere; use "Deposits/Contributions". The row action "Not counted" (EN, a status) vs "Nicht zählen" (DE, an action) also contradict each other.
7. **slows a task**: English mixes "bookings" and "transactions" (`01-overview.desk.en` "39 bookings", `09-drill-group.desk.en` "79 bookings" next to "79 transactions"). German is consistently "Umsätze".
8. **slows a task**: `20-settings-bank.phone.de` / `27-settings-account.phone.de`. The eight-tab Settings strip hides five sections and truncates labels on phone, and log-out sits in the last hidden tab. Use a section list on phone.
9. **slows a task**: `09-drill-group` / `10-drill-category` (desk + phone). Drill pages have no visible back or breadcrumb (the eyebrow looks static). `10` duplicates "INCOME / Income" and does not name the category.
10. **slows a task**: grouping in Settings. "Hints & salary" hides the payday logic behind "Hints", and password/log-out are split between "Account & look" and "Security". Also `07-spending.desk.en` uses "Groups" for both built-in category parents and user-made "Your own group". Regroup by user task and rename custom groups (for example "Projects/Projekte").

Keep: the German vocabulary (Umsätze, Fixkosten, Vermögen, Depot, Sparerpauschbetrag, Einzahlungen); "Available until payday / Frei verfügbar bis zum Gehalt"; "What changed" sentences on Fixed costs; the Top merchants → Categories → Transactions drill; cross-links such as "Everything with Shell ›" and "3 savings plans… live under Net worth"; the phone depot tab strip once you are inside Depot.
