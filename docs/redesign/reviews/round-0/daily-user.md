# Groschen – review round 0 – role: DAILY USER

Perspective: I open this app every day for my own money. I judge only what the screenshots show. Click counts start on the Overview, after login. "Click" means a tap or click, or a scroll that I have to do to reach the answer. "Dead end" means a place where I hesitate, go the wrong way, or get two answers that disagree.

## Task table

| # | Task | Steps desktop | Steps phone | Dead ends | Screenshots used |
|---|---|---|---|---|---|
| 1 | "Can I afford 200 € this week?" | **0** (hero on Overview: 5,170.65 €, "about 184.67 € per day") | **0** (hero above the fold) | 1: the hero does not say whether the "14 payments still to come · 2,597.40 €" are already subtracted. There is no "this week" figure, so I multiply 184.67 × 7 in my head. | 01-overview.desk.en, 01-overview.phone.de, 22-settings-hints.desk.en ("Keep aside … subtracted from Available until payday") |
| 2 | "What did I pay for groceries last month?" | **~6**: Spending → period menu → "Month" → step back to Sept (control not shown) → Food & Dining row → Groceries row. Or ~5 through Transactions → period → search "Groceries" → read "€ out". | **~6–7**: Ausgaben tab → period → "Monat" → back to Sept → Essen & Trinken → scroll to Kategorien → Lebensmittel | 3: (a) the period menu has no "Last month" preset. (b) The Food & Dining monthly bars have no value labels, and they show the group, not Groceries. (c) The category drill page (10-drill-category) shows a full-screen "0.00 €" empty state, and the sidebar still highlights "Spending". | 07-spending.*, 33-period-menu.*, 09-drill-group.*, 10-drill-category.*, 02-transactions.desk.en |
| 3 | "Which subscription got more expensive?" | **1–2**: Fixed costs → "What changed" names Spotify. To see all increases: "Show all 8" (+1). | **2–3**: Ausgaben tab → "Fixkosten" toggle → scroll → "Alle 8 zeigen" | 2: (a) The list shows price badges on 4 items (Stadtwerke +7.00 €, Deutsche Bahn +9.00 €, Netflix +2.00 €, Spotify +1.00 €), but "What changed" shows only Spotify in its first 4 entries. (b) The badges give no "since" date and no old price. The Overview "Worth a look" card does not mention any price increase. | 11-recurring-list.desk.en, 11-recurring-list.phone.de, 01-overview.desk.en |
| 4 | "Fix a wrongly sorted booking" | **4–5**: Transactions → find the row (scroll or search) → open → pick a chip → Save | **5–6**: Umsätze → search → row → scroll the sheet to the right group → chip → Speichern | 2: (a) The merchant-rule toggle is ON by default and sits on top of the "SUBSCRIPTIONS" chip group, so you can change every Shell booking without noticing. On phone the toggle is not visible at all. (b) The Overview says "Groschen sorted 39 bookings on its own. Do the categories look right?", but the Needs-review banner says "These bookings need a category from you". There is no "looks right / confirm" action on the rows. | 05-transactions-edit.*, 03-transactions-review.*, 01-overview.desk.en, 21-settings-categories.desk.en |
| 5 | "How is my depot doing without my own pay-ins?" | **1**: sidebar "Investments" → "+504.90 € · +6.7 %", "plus 3,000.00 € paid in", chart shows "Value without deposits" by default | **2**: Vermögen tab → Direkt-Depot card (chevron) | 3: (a) Three different figures for the same question: +6.7 % (Investments), +6.3 % "the funds themselves" (Analysis), +17.2 % / 1,160.97 € on the ETF page with no period label. (b) Payments shows "3,600.00 € in the last 12 months" while Investments says 3,000 € paid in (Jan–Oct), on different time bases. (c) EN "× Not counted" on every pay-in reads like a status, but it is the action "Nicht zählen". | 15-investments.*, 17-inv-analysis.desk.en, 18-inv-payments.desk.en/.desk.de/.phone.de, 19-etf.desk.en, 14-networth.phone.de |
| 6 | "What is coming off my account before payday?" | Total **0** (Overview: "14 payments still to come · 2,597.40 €"). List: **1** on that link (target not captured). Through Fixed costs → Calendar → next month: **3**. | Total **0**. List: **4** (Ausgaben → Fixkosten → Kalender → ›) | 2: (a) The calendar is limited to the calendar month. October shows "0.00 € still to come", and you have to page to November. It does not stop at the 27 Nov payday. (b) "Next up" shows only 3 items, and "Running" is sorted by amount, not by due date. The phone list drops the "In X days" column. | 01-overview.*, 11-recurring-list.*, 12-recurring-calendar.* |

I checked the sum: the 14 items until Fri 27 Nov (Nov 1: 1,050 + 800 + 250 + 50, then Stadtwerke, FitX, DB, Telekom, Netflix, Spotify, Apple, HUK, DAZN, Lime 129) add up to exactly 2,597.40 €. The number is right. It is just hard to see the list behind it.

---

## Per-screen review

Scores use rubric lines 1–9. My role scores **3 task efficiency, 4 data presentation, 5 navigation and naming**, and **7 phone experience** where phone tasks matter. Other lines are "-".

### 01-overview (desk.en, desk.de, phone.de, phone.en)

| Line | Score | Based on |
|---|---|---|
| 1 | - | |
| 2 | - | |
| 3 | 8 | `01-overview.desk.en`: "Available until payday" hero answers task 1 with zero clicks; "14 payments still to come · 2,597.40 €" answers the total of task 6 |
| 4 | 6 | `01-overview.desk.en`: "Where the money went" Sankey omits "Personal −162.37 €", so the right-hand categories sum to 20,613.82 € and not the 20,451.45 € on the Spending card |
| 5 | 7 | `01-overview.desk.en`: "Worth a look" wording "sorted 39 bookings on its own" does not match the target screen's banner "need a category from you" |
| 6 | - | |
| 7 | 7 | `01-overview.phone.de`: hero, payday strip and "14 Zahlungen kommen noch" all sit above the fold. The Sankey tip "Zeig auf ein Band" is a hover instruction on a touch screen. |
| 8 | - | |
| 9 | - | |

Findings
- `keep` – 01-overview.desk.en, hero "Available until payday 5,170.65 € · That's about 184.67 € per day" with "28 days to payday". This is the single most useful number for a daily user. Keep it on top.
- `slows a task` – 01-overview.desk.en, hero. The hero does not say whether the 2,597.40 € still to come are already subtracted. I only learn the meaning from 22-settings-hints ("Keep aside … subtracted from Available until payday"). Suggestion: add a one-line breakdown under the number, e.g. "7,768 € on account − 2,597 € still to come − 0 € kept aside", or a tooltip. Add "≈ 1,293 € this week" next to the per-day figure.
- `slows a task` – 01-overview.desk.en, "Where the money went" Sankey. The right side has no "Personal" band, so the outflows do not add up to the 20,451.45 € Spending card. Suggestion: show the net refunds as a small inflow on the left, or as a footnote.
- `slows a task` – 01-overview.desk.en, "Worth a look" item 1 ("Groschen sorted 39 bookings on its own. Do the categories look right?" → Check). The destination 03-transactions-review says "These bookings need a category from you". Use one story everywhere: "39 bookings Groschen wasn't sure about – confirm or change".
- `cosmetic` – 01-overview.desk.en, "Worth a look": the desktop items have no dismiss (×), but 01-overview.phone.de does. Use the same controls on both.
- `slows a task` – 01-overview.phone.de, Sankey hint "Zeig auf ein Band, um ihm zu folgen" asks you to hover, which a phone cannot do. Suggestion: "Tipp auf ein Band …".
- `keep` – 01-overview.*, "Saved 13,087.15 €" with the split bar "3,000 invested · 1,991.75 stays" and the 39 % savings rate. It answers "am I saving" at a glance.

### 02 / 03 / 04 / 06 – Transactions (list, needs review, filtered, empty; all variants)

| Line | Score | Based on |
|---|---|---|
| 3 | 6 | `02-transactions.desk.en`: no month jump or "last month" chip. Reaching September means scrolling about 4,000 px of a 297-row list. |
| 4 | 7 | `02-transactions.desk.en`: day headers with day totals, merchant logos, category pills and right-aligned amounts read well. The day total is shown only on multi-row days and includes transfers (Tue 1 Sept "−1,350.00 €" mixes +800 / −800 savings). |
| 5 | 6 | `03-transactions-review.desk.en`: the "Needs review 39" tab switches the summary to "All periods · 774 transactions" while the period button still says "Jan – Oct 2026" |
| 7 | 7 | `02-transactions.phone.de`: the filter tabs scroll sideways ("Einnahmen" cut off) and the search placeholder is truncated ("…oder Betr"). The rows themselves are excellent. |

Findings
- `keep` – 02-transactions.desk.en, Nordlicht Software row: "counts for November 2026 · LOHN/GEHALT 10/2026". This explains the salary shift right where it matters.
- `keep` – 02-transactions.phone.de bottom: refund linking ("Geld zurück für Amazon, 10. Sept." and the strike-through "Komplett zurückbekommen") and the "32.00 € of 64.00 € back" progress bar on the desktop rows. This is a great daily-use detail.
- `slows a task` – 03-transactions-review.desk.en, summary line "All periods · 774 transactions" next to the "Jan – Oct 2026" period button. Two different periods on one screen. Suggestion: grey out or relabel the period button ("All periods") while the review tab ignores it.
- `slows a task` – 03-transactions-review.desk.en, review rows. They look exactly like normal rows. There is no "✓ looks right" button, and there is no bulk "confirm all 39". Confirming a correct guess costs open → Save. Suggestion: add an inline ✓ per row and a "Confirm all shown" action.
- `slows a task` – 02-transactions.desk.en, the list has no month jump. For task 2 the user must change the period first. Suggestion: add sticky month headers with a month total, e.g. "September · −2,1xx €", or a "Last month" quick chip next to the tabs.
- `cosmetic` – 02-transactions.desk.en, day headers: days with a total are set in small, letter-spaced grey caps ("WEDNESDAY 28 OCTOBER"), days without a total in bold white caps ("TUESDAY 27 OCTOBER"). It looks like two kinds of header. Use one style.
- `slows a task` – 02-transactions.desk.en, summary "42,057.91 € in · 31,970.76 € out". This does not match the Overview's Income 33,538.60 € / Spending 20,451.45 € for the same period, because transfers and investments are included. Suggestion: label it "incl. transfers & savings", or show "spending 20,451 €" instead.
- `keep` – 04-transactions-filtered.desk.en, "Clear filters" link right in the summary line. 06-transactions-empty.desk.en has a clear empty state with "Try a different search, filter or period".
- `cosmetic` – 02-transactions.phone.de, filter tabs row: "Einnahmen" is clipped with no fade or scroll hint.

### 05-transactions-edit (desk.en, desk.de, phone.de, phone.en)

| Line | Score | Based on |
|---|---|---|
| 3 | 7 | `05-transactions-edit.desk.en`: every category is a one-tap chip grouped by parent, with search on top. Fixing a booking takes 2 clicks inside the dialog. |
| 4 | 8 | `05-transactions-edit.desk.en`: the raw bank text in a monospace box ("VISA Debitkartenumsatz vom 28.10.2026") is exactly what I need to decide |
| 5 | 6 | `05-transactions-edit.desk.en`: the sticky "Use this category for every transaction from this merchant" row covers the "SUBSCRIPTIONS" group |
| 7 | 5 | `05-transactions-edit.phone.de`: the merchant-rule toggle is not visible. Only "Alles mit Shell ›" and "Speichern" show, and the categories below "Mobilität" must be scrolled inside the sheet. |

Findings
- `blocks a task` (silent data change) – 05-transactions-edit.desk.en, toggle "Use this category for every transaction from this merchant" is **on** by default. If I fix one odd booking (e.g. an Amazon gift), all Amazon bookings move. On phone (05-transactions-edit.phone.de) I cannot even see the toggle before pressing Speichern. Suggestion: default to off for merchants with mixed categories. Show the toggle on phone, and after saving show a toast like "Also changed 12 other Shell bookings – Undo".
- `slows a task` – 05-transactions-edit.desk.en, the sticky footer row overlaps the "SUBSCRIPTIONS" header, so the subscription chips are hidden under it. Suggestion: give the toggle its own row inside the scroll area, or a fixed footer with a top border.
- `keep` – 05-transactions-edit.desk.en, "Everything with Shell ›" link. It is a quick way to check the merchant history.
- `slows a task` – 05-transactions-edit.*, the dialog has no note field and no split. "Personal" refunds (Lena Berger 32/64 €) suggest splits exist elsewhere, but you can't set them here.

### 07-spending + 33-period-menu (all variants)

| Line | Score | Based on |
|---|---|---|
| 3 | 5 | `33-period-menu.desk.en`: the menu offers Month / Last 30 days / Year to date / Year / Last 12 months / All time, with no "Last month" and no visible month stepper. That is the main dead end of task 2. |
| 4 | 8 | `07-spending.desk.en`: "Spending breakdown" ranked bars with amount and %, and an explicit "Personal · more refunds than spending −162.37 €" row |
| 5 | 5 | `07-spending.phone.de`: two stacked segmented controls "Ausgaben | Einnahmen" and "Ausgaben | Fixkosten". The word "Ausgaben" appears three times on one screen with different meanings. |
| 7 | 5 | `07-spending.phone.de`: the "Dein Jahr in Tagen" heatmap is cut off after "Jun" with no scroll hint |

Findings
- `blocks a task` – 33-period-menu.desk.en / .phone.de, period menu. There is no "Last month" (or "Previous month") entry, and it is not shown how "Month" moves to September. Suggestion: add "Last month" and show ‹ › arrows next to the period chip whenever a single month is selected.
- `slows a task` – 07-spending.phone.de, the double toggle "Ausgaben/Einnahmen" plus "Ausgaben/Fixkosten". Suggestion: make Fixkosten its own bottom-nav destination or a clearly named tab ("Fixkosten" next to "Kategorien"), and rename the first toggle "Geld raus / Geld rein".
- `keep` – 07-spending.desk.en, rows with chevrons that drill into the group. It is a clear path from total to detail.
- `slows a task` – 07-spending.desk.en, "Your year in days" heatmap. It is pretty, but squares carry no value until hover, and the month labels sit offset from the columns (coloured squares under "Nov" although today is 30 Oct). Low task value for its size. Suggestion: show monthly totals under the month labels.
- `cosmetic` – 07-spending.desk.en, the donut centre "20,451 €" is rounded, while the header line uses cents ("2,045.14 €"). Fine, but be consistent with the Overview's 20,451.45 €.

### 08-spending-group-dialog (all variants)

| Line | Score | Based on |
|---|---|---|
| 3 | 7 | `08-spending-group-dialog.desk.en`: multi-select chips per parent, name and icon. Quick. |
| 4 | - | |
| 5 | 6 | `07-spending.desk.en`: the entry point is named "+ Your own group", and the dialog title is "New group" |
| 7 | - | |

- `cosmetic` – 08-spending-group-dialog.desk.en: the "SUBSCRIPTIONS" group is cut off at the bottom edge with no scroll shadow, so it looks like the list ends at Insurance.
- `keep` – 08-spending-group-dialog.desk.en, explanation "your main budget still counts everything normally". This removes the fear of double counting.

### 09-drill-group (Food & Dining) (all variants)

| Line | Score | Based on |
|---|---|---|
| 3 | 7 | `09-drill-group.desk.en`: "Categories" card puts "Groceries · 43× 2,553.63 €" one click away, and the transaction list below has category chips with counts |
| 4 | 6 | `09-drill-group.desk.en`: the "Per month" bars have no values (I need the Sept number), and the "↑ 35 % vs. the period before" baseline is not named |
| 5 | 6 | `09-drill-group.desk.en`: no back control. Only the eyebrow "SPENDING" shows, and it is not visibly a link. |
| 7 | 6 | `09-drill-group.phone.de`: month axis labels only every other month, and the last bar (Oct) has no label |

Findings
- `slows a task` – 09-drill-group.desk.en, "Per month" chart. Suggestion: show the value on hover/tap and print the latest full month's value ("Sept 3xx €"). Make the bars clickable to filter the list below to that month. That alone would make task 2 three clicks.
- `cosmetic` – 09-drill-group.desk.en, "Categories" card lists "Food & Dining · 0× 0.00 €" and "Food delivery · 0× 0.00 €". Empty rows are noise. Hide zero rows.
- `slows a task` – 09-drill-group.desk.en, "↑ 35 % vs. the period before". Which period, Mar–Dec 2025? Name it.
- `keep` – 09-drill-group.desk.en, "Top merchants" with counts ("Lidl · 14×"). Really useful.

### 10-drill-category (Income drill) (all variants)

| Line | Score | Based on |
|---|---|---|
| 3 | 3 | `10-drill-category.desk.en`: shows "Income · RECEIVED 0.00 € · 0 bookings" while the Overview says 33,538.60 € income |
| 4 | 4 | `10-drill-category.desk.en`: big "0.00 €" hero plus two empty states |
| 5 | 4 | `10-drill-category.desk.en`: page "Income" with eyebrow "INCOME", while the sidebar still highlights "Spending" |
| 7 | 5 | `10-drill-category.phone.de`: the same empty page, now a full phone screen |

- `blocks a task` – 10-drill-category.desk.en. Landing on "Income 0.00 €" looks like data loss. If this is the "Income (general)" leaf category, say so ("Income (general) – no bookings here; your salary is under Salary") and link to the parent. Don't show a 0 hero.

### 11-recurring-list – Fixed costs list (all variants)

| Line | Score | Based on |
|---|---|---|
| 3 | 7 | `11-recurring-list.desk.en`: "What changed" answers task 3 directly ("Spotify got more expensive: 10.99 € → 11.99 € since 8 Jun 2026, 12.00 € more per year") |
| 4 | 7 | `11-recurring-list.desk.en`: "Running" shows rhythm, next date and the monthly equivalent ("≈ 18.36 € a month"). The price badges ("+7.00 €") lack a "since" and an old price. |
| 5 | 6 | `11-recurring-list.desk.en`: page "Fixed costs" lists subscriptions (Spotify, Netflix) next to rent, while the spending group is called "Subscriptions". And "Fixed costs per month 1,407.01 €" ≠ calendar's "2,523.48 € fixed costs this month". |
| 7 | 6 | `11-recurring-list.phone.de`: the "Laufend" rows drop the "in X Tagen" column, and "Hausverwaltung Kr…" is truncated in "Als Nächstes" |

Findings
- `keep` – 11-recurring-list.desk.en, "What changed" feed (New / Back / Stopped / More expensive) with the yearly effect ("12.00 € more per year"). This is the best single answer in the app.
- `slows a task` – 11-recurring-list.desk.en, "What changed" shows 4 of 8 events, and only Spotify is a price rise. Stadtwerke (+7), Deutsche Bahn (+9) and Netflix (+2) carry badges but are hidden behind "Show all 8". Suggestion: rank price rises first, or add a filter chip "Got more expensive (4)".
- `slows a task` – 11-recurring-list.desk.en, price badges "+7.00 €" have no context. Suggestion: show "+7.00 € since Mar" on hover/tap, or print "74 → 81 €" under the name.
- `slows a task` – 11-recurring-list.desk.en, "Running" is sorted by amount, so the due dates jump (in 16 days, then 7, 19, 3 …). For task 6 a sort-by-next-due toggle is needed.
- `slows a task` – 11-recurring-list.desk.en vs 12-recurring-calendar.desk.en: 1,407.01 € "per month" against 2,523.48 € "this month". The difference is the 1,100 € savings plans plus irregular items, but nothing says so. Suggestion: on the calendar, split it as "1,423 € fixed costs + 1,100 € savings plans".
- `keep` – 11-recurring-list.desk.en, footer "3 savings plans run along: 1,100.00 € a month. They live under Net worth." This is a nice cross-link.
- `cosmetic` – 11-recurring-list.desk.en, "Next up" card shows only 3 payments, and FitX "in 3 days" appears before the 5-day DB. Fine, but a "+11 more until payday ›" link would serve task 6.

### 12-recurring-calendar (all variants)

| Line | Score | Based on |
|---|---|---|
| 3 | 5 | `12-recurring-calendar.desk.en`: on 30 Oct it shows October, where everything is paid ("0.00 € still to come"). The useful month needs a click on ›. |
| 4 | 7 | `12-recurring-calendar.desk.en`: the "Day by day" side list with "monthly · paid" is clear. The cells truncate names to "Ha…", "Spar…", "Nor…". |
| 5 | 6 | `12-recurring-calendar.desk.en`: legend mixes "Paid / Expected / Standing order / Salary". Salary inside "Fixed costs" is odd. |
| 7 | 7 | `12-recurring-calendar.phone.de`: compact dot calendar with daily sums ("−2.150 €") plus the full list below works well on phone |

- `slows a task` – 12-recurring-calendar.desk.en. Suggestion: add a mode "Until payday (27 Nov)" that starts today, or auto-advance to the next month when the current one has nothing left.
- `cosmetic` – 12-recurring-calendar.desk.en, cell chips "Ha… −1,050 €". Suggestion: on desktop there is room for a short name.

### 13-recurring-orbit (all variants)

| Line | Score | Based on |
|---|---|---|
| 3 | 3 | `13-recurring-orbit.desk.en`: most dots are unlabelled and need clicking. It answers none of my tasks. |
| 4 | 3 | `13-recurring-orbit.desk.en`: size encodes cost but there is no scale, and only 4 of 13 dots carry a name |
| 5 | 5 | `13-recurring-orbit.desk.en`: "Orbit" says nothing about what the view is for |
| 7 | 3 | `13-recurring-orbit.phone.de`: the dots overlap the centre total "1.407 € im Monat" and the labels collide |

- `cosmetic` (but it costs a tab slot) – 13-recurring-orbit.*. Consider moving it to an easter egg (Settings already has "Easter eggs"), and use the tab for "Until payday".

### 14-networth (all variants)

| Line | Score | Based on |
|---|---|---|
| 3 | 7 | `14-networth.desk.en`: "TODAY 44,931.92 €" plus account cards. The Direkt-Depot card is the phone's only way into the depot. |
| 4 | 6 | `14-networth.desk.en`: the "↑ 13,592.05 €" change mixes my own savings and market gain without saying so. The chart starts at "Dec 25" although the period is Jan–Oct. |
| 5 | 6 | `14-networth.phone.de`: only the Direkt-Depot card has a chevron. Girokonto and Extra-Konto cards look the same but lead nowhere. |
| 7 | 7 | `14-networth.phone.de`: clean stacked cards. Savings plan names are truncated ("Vanguard FTSE All-W…"). |

- `slows a task` – 14-networth.phone.de, Direkt-Depot card. It is the only entry to Depot/Prognose/Analyse/Einzahlungen on phone. Suggestion: a visible "Depot ansehen ›" button, or a Depot tab inside Vermögen.
- `cosmetic` – 14-networth.desk.en, "↑ 13,592.05 €". Split it as "+11,1xx € saved, +505 € market".
- `keep` – 14-networth.desk.en, savings-plan cards with coin rows and "6,750.00 € since August 2024".

### 15-investments / 32-hidden-investments (all variants)

| Line | Score | Based on |
|---|---|---|
| 3 | 8 | `15-investments.desk.en`: answer to task 5 in the hero ("504.90 € · +6.7 %", "plus 3,000.00 € paid in"), and the chart defaults to "Value without deposits" |
| 4 | 7 | `15-investments.desk.en`: monthly gain/loss bars with values (−111 € … −82 €) sum exactly to 505 €. Good. The line labelled "Value without deposits" still ends at the full 9.35k depot value, which is confusing. |
| 5 | 5 | `15-investments.desk.en` vs `15-investments.phone.de` vs `14-networth.desk.en`: the same thing is called "Investments", "Depot" and "Direkt-Depot" |
| 7 | 7 | `15-investments.phone.de`: the tab bar "Überblick / Prognose / Analyse / Einzahlungen" is better than the desktop sidebar tree |

- `keep` – 15-investments.desk.en, hero sentence "Jan – Oct 2026, plus 3,000.00 € paid in". This is the right framing.
- `slows a task` – 15-investments.desk.en, legend "Value without deposits". Suggestion: rename it "Value if you had paid nothing in since Jan", or plot the gain line from 0.
- `slows a task` – naming. Sidebar "Investments", phone page "Depot", the net-worth card "Direkt-Depot", and Settings has an "Investments" tab. Pick one ("Depot" in DE, "Portfolio" or "Depot" in EN) and use it everywhere.

### 16-inv-forecast (all variants)

| Line | Score | Based on |
|---|---|---|
| 3 | 7 | `16-inv-forecast.desk.en`: "68,412 €" with bad and good case, and "24,312 € more than the 44,100 € you'd have paid in" |
| 4 | 8 | `16-inv-forecast.desk.en`: assumption cards ("Expected return 7.4 % a year … counts 19 %") are honest and checkable |
| 5 | 7 | `16-inv-forecast.desk.en`: "Adjust the numbers" link at the bottom is easy to miss |
| 7 | 7 | `16-inv-forecast.phone.de`: long but complete. The four assumption cards are dense. |

- `keep` – 16-inv-forecast.desk.en, "1 in 12 futures ends below what you paid in". This is the kind of plain-language risk statement users understand.

### 17-inv-analysis (all variants)

| Line | Score | Based on |
|---|---|---|
| 3 | 6 | `17-inv-analysis.desk.en`: "Your money +6.7 %" against "The funds themselves +6.3 %". These are two answers to task 5, and "About what the funds themselves made" does not tell me which to trust. |
| 4 | 7 | `17-inv-analysis.desk.en`: the "Monthly returns" heatmap in % with an outlined best and worst month is clear |
| 5 | 6 | `17-inv-analysis.desk.en`: "Ups and downs ±17 %" next to forecast "Swing 15 % a year". Same concept, two names, two numbers. |
| 7 | - | |

- `slows a task` – 17-inv-analysis.desk.en, "Return in this period". Suggestion: one sentence like "Your timing added +0.4 pts (6.7 % vs 6.3 % for the funds)".

### 18-inv-payments (all variants)

| Line | Score | Based on |
|---|---|---|
| 3 | 7 | `18-inv-payments.desk.en`: grouped by month, with expand and "Show all 27 months" |
| 4 | 6 | `18-inv-payments.desk.en`: "3,600.00 € in the last 12 months" ignores the page-wide Jan–Oct period (no period chip on this page) |
| 5 | 4 | `18-inv-payments.desk.en`: "× Not counted" on every included payment reads as a status ("this was not counted"). DE `18-inv-payments.desk.de` says "Nicht zählen" (an action). Sidebar EN "Payments" vs DE "Einzahlungen". |
| 7 | 7 | `18-inv-payments.phone.de`: readable. The ISIN text is truncated. |

- `slows a task` – 18-inv-payments.desk.en, "× Not counted". Rename it "Don't count" or "Exclude", and show a real state for excluded rows.
- `slows a task` – 18-inv-payments.desk.en, sidebar "Payments" under Investments is easily confused with fixed-cost payments. Use "Pay-ins" or "Money put in" (the card title already says that).

### 19-etf (all variants)

| Line | Score | Based on |
|---|---|---|
| 3 | 6 | `19-etf.desk.en`: "1,160.97 € · +17.2 %" is all-time while the Holdings card showed "+7.5 % · 474 €" for Jan–Oct. There is no period label here and no period chip. |
| 4 | 8 | `19-etf.desk.en`: price chart with purchase dots and the "Your average 110.71 €" line is excellent |
| 5 | 6 | `19-etf.desk.en`: the sidebar highlights "Investments" but the page has its own Overview/Analysis/Forecast tabs that duplicate the sidebar children |
| 7 | - | |

- `slows a task` – 19-etf.desk.en, "YOUR VALUE … +17.2 %". Add "since first purchase (Aug 2024)".
- `keep` – 19-etf.desk.en, purchase dots and the average-price line.

### 20–27, 30 – Settings (all variants)

Settings matter little for daily tasks. Only the points that affect them:

| Line | Score | Based on |
|---|---|---|
| 3 | 6 | `22-settings-hints.desk.en`: "Keep aside" (feeds the Overview hero) is buried under Settings › Hints & salary |
| 4 | 5 | `20-settings-bank.desk.en`: "Every day at 06:00" vs "Next sync tomorrow at 05:00". `24-settings-backup.desk.en`: "Next backup tomorrow at 02:00" vs "Time of day 03:00". |
| 5 | 5 | `21-settings-categories.desk.en`: "Built-in model" is selected while the line says "built-in model not found", with an "Offline" badge. The "Needs review" tab is called "To review" in the description. |
| 7 | 6 | `20-settings-bank.phone.de`: the settings tabs scroll sideways (only 3 of 8 visible), and the "7 Tage vorher" segment is clipped |

- `slows a task` – 22-settings-hints.desk.en, "Keep aside". It belongs next to the Overview hero as an inline edit.
- `cosmetic` – 20-settings-bank.desk.en / 24-settings-backup.desk.en, the time mismatches above. It looks like a timezone bug and erodes trust.
- `slows a task` – 21-settings-categories.desk.en, "learned from 0 corrections and 0 merchants", while the edit dialog's merchant toggle defaults on. It is unclear where my fixes go: "Learned merchants" says "Nothing learned yet". Make the link between the dialog and this list explicit.
- `cosmetic` – 25-settings-privacy.desk.en, the backup note "Backups never contain the key…" is repeated under "Export". It belongs to Backups only.
- `cosmetic` – 27-settings-account.desk.en, "Country: Not chosen", but the numbers are already formatted EN-style. Show the country that is actually in effect.
- `slows a task` – 30-settings-connect-dialog.desk.en, the error "No bank found by that name" shows while the field is empty, and "Done, start syncing" is enabled without a bank chosen.
- `keep` – 20-settings-bank.desk.en, "Bank login needed within 90 days" bar with plain-language instructions.

### 31/32 – hidden amounts (all variants)

| Line | Score | Based on |
|---|---|---|
| 3 | 8 | `31-hidden-overview.phone.de`: the eye toggle sits in the top bar, so one tap hides everything; percentages (39 %) stay readable |
| 4 | - | |
| 5 | 7 | `31-hidden-overview.phone.de`: the active state is shown by a gold eye-slash icon |
| 7 | 8 | `31-hidden-overview.phone.de` |

- `keep` – 31-hidden-overview.*, privacy toggle one tap away on both layouts.

### 40–42 – wizard and login

These are not daily screens, so I did not score them. Note: `41-wizard-country.desk.en` keeps the step subtitle "Over FinTS, read-only" while the body says that for the UK it reads CSV, which contradicts it (cosmetic). `42-login.desk.en` is clean.

### Navigation overall (all screens)
- `slows a task` – phone bottom nav (`01-overview.phone.de`): Übersicht / Umsätze / Ausgaben / Vermögen. Fixkosten (tasks 3 and 6) hides behind a second toggle inside Ausgaben, and Depot (task 5) behind a card chevron inside Vermögen. On desktop both are one sidebar click. Suggestion: a 5th tab "Fixkosten", or a clear sub-tab row like the Depot tabs.
- `slows a task` – desktop sidebar (`01-overview.desk.en`): the investment children "Forecast / Analysis / Payments" are a second-level tree. On the ETF page (`19-etf.desk.en`) the same words reappear as page tabs with a different scope (one fund). Two "Forecast"s confuse.
- `keep` – the period chip in the same top-right place on every analytic page (`07-spending.desk.en`, `09-drill-group.desk.en`, `15-investments.desk.en`).

---

## Top 10

1. **blocks a task** – `33-period-menu.desk.en/.phone.de`: there is no "Last month" entry and no visible month stepper, so "Groceries last month" needs about 6 clicks and some guessing. Add "Last month" and ‹ › arrows on the period chip.
2. **blocks a task (silent change)** – `05-transactions-edit.desk.en`: "Use this category for every transaction from this merchant" defaults to ON, is placed over the Subscriptions chips, and is invisible on `05-transactions-edit.phone.de`. Default it to off (or show "also changes N bookings – Undo") and show it on phone.
3. **blocks a task** – `10-drill-category.desk.en/.phone.de`: the Income drill shows "RECEIVED 0.00 € · 0 bookings" next to an Overview income of 33,538.60 €, and the sidebar still highlights Spending. Explain that it is the empty leaf category, or redirect to Salary.
4. **slows a task** – `01-overview.desk.en`: the "Available until payday 5,170.65 €" hero does not say whether the "2,597.40 € still to come" are already deducted, and it has no "this week" figure. Add a one-line breakdown and a weekly amount.
5. **slows a task** – `11-recurring-list.desk.en`: four price-rise badges (+7, +9, +2, +1 €), but "What changed" shows only Spotify before "Show all 8", and the badges have no date or old price. Put price rises first and give the badges context.
6. **slows a task** – `15-investments.desk.en` / `17-inv-analysis.desk.en` / `19-etf.desk.en` / `18-inv-payments.desk.en`: four gain and pay-in figures on different time bases (+6.7 %, +6.3 %, +17.2 % unlabeled, 3,600 € "last 12 months" vs 3,000 € Jan–Oct). Label every figure with its period.
7. **slows a task** – `12-recurring-calendar.desk.en` + `11-recurring-list.desk.en`: there is no "until payday" view. The calendar opens on a fully paid October, "Running" is sorted by amount, and the phone list drops "in X days". Add an "Until 27 Nov" list sorted by date (also the target of the Overview "14 payments" link).
8. **slows a task** – `07-spending.phone.de` / `11-recurring-list.phone.de` / `14-networth.phone.de`: on phone, Fixkosten and Depot hide behind a second "Ausgaben | Fixkosten" toggle and a card chevron, and the word "Ausgaben" appears three times. Give them first-level access.
9. **slows a task** – naming. "Investments" / "Depot" / "Direkt-Depot"; sidebar "Payments" (= pay-ins); EN "× Not counted" for the action "Nicht zählen" (`18-inv-payments.desk.en` vs `.desk.de`); "Needs review" vs "To review"; "Fixed costs 1,407.01 €/month" vs "2,523.48 € fixed costs this month". Unify the terms.
10. **slows a task** – `03-transactions-review.desk.en` + `01-overview.desk.en`: "sorted 39 bookings on its own – do they look right?" leads to "These bookings need a category from you", with "All periods" next to a "Jan – Oct 2026" chip and no confirm or "confirm all" action on rows. Add an inline ✓ and bulk confirm, and use one consistent message.
