# GUI improvement loop: report

Branch `redesign/loop`, 25 Nov 2026. Eight rounds on the web GUI (`frontend/`), each judged blind against the version before it. Full log: [LOG.md](LOG.md). All screenshots come from the demo (invented data, clock frozen on Fri 30 Oct 2026).

**In one paragraph.** The phone now reaches every page the sidebar does, through one section strip under the top bar. Settings on a phone opens on a list of its sections. One thing has one name: fixed costs are kept apart from savings, Pay-ins, transaction, Needs review. Secondary grey text passes contrast. Nothing on a phone is cut off or hidden behind a sideways scroll: switches, the wizard footer, the year heatmap and the monthly returns all fit. Two daily tasks got shorter: "Last month" is in the period menu, and the merchant switch sits next to Save. The identity is unchanged: dark, champagne accent, Figtree, big tight numbers. There are no new dependencies, no new requests and no new endpoints. Every old address still works.

## Scores: round 0 vs. final pass

Six fresh reviewers each time, given only screenshots, a rubric and a role. The numbers are mean scores per area, pulled from the reviewers' tables. Each reviewer scored only the lines their role covers. Absolute scores drift between reviewer sets, so the blind A/B judges decided each change, not these numbers.

| Area | Round 0 | After round 3 | After round 6 | Final |
|---|---|---|---|---|
| Overview | 6.9 | 7.0 | 7.2 | **7.5** |
| Transactions | 6.5 | 6.4 | 6.5 | **6.8** |
| Spending | 5.9 | 6.2 | 6.7 | **6.7** |
| Drill-downs | 5.9 | 5.9 | 7.1 | **7.1** |
| Fixed costs | 5.6 | 6.0 | 5.8 | **6.7** |
| Net worth | 6.8 | 7.0 | 6.8 | **7.1** |
| Depot | 6.4 | 6.8 | 6.7 | **7.0** |
| ETF page | 6.3 | 6.3 | 6.6 | **7.0** |
| Settings | 5.5 | 6.3 | 6.1 | **6.7** |
| Wizard & login | 6.7 | 7.1 | 7.0 | **7.0** |

Final pass per rubric line:

| Area | Clarity | Hierarchy | Tasks | Data | Naming | Consistency | Phone | Access. | Craft |
|---|---|---|---|---|---|---|---|---|---|
| Overview | 8.0 | 7.8 | 8.5 | 6.3 | 7.0 | 6.5 | 7.9 | 7.0 | 7.7 |
| Transactions | 8.0 | 7.3 | 7.0 | 6.8 | 5.6 | 6.3 | 6.8 | 6.0 | 7.2 |
| Spending | 7.4 | 6.8 | 6.5 | 6.7 | 5.8 | 6.5 | 7.1 | 5.3 | 7.3 |
| Drill-downs | 8.3 | 7.7 | 6.0 | 6.7 | 7.0 | 6.7 | 7.2 | 7.0 | 6.5 |
| Fixed costs | 8.0 | 7.2 | 7.5 | 5.8 | 5.5 | 6.5 | 6.4 | – | 7.0 |
| Net worth | 8.3 | 7.7 | – | 6.0 | 6.5 | 7.0 | 7.3 | 7.0 | 6.5 |
| Depot | 7.2 | 7.5 | 8.0 | 6.9 | 5.6 | 6.0 | 7.5 | 6.7 | 7.1 |
| ETF page | 8.0 | 7.0 | 8.0 | 7.0 | 6.0 | 6.0 | 7.0 | 7.0 | 7.5 |
| Settings | 7.7 | 7.0 | 5.0 | – | 5.7 | 6.0 | 7.5 | 5.5 | 7.0 |
| Wizard & login | 7.5 | 8.0 | 8.0 | – | 6.0 | 7.0 | 6.5 | 5.0 | 8.0 |

Daily tasks (daily-user reviewer, steps on desktop / phone):

| Task | Round 0 | Final |
|---|---|---|
| Can I afford 200 € this week? | 0 / 0 | 0 / 0 |
| What did I pay for groceries last month? | ~6 / 6–7 | 5 / 5 |
| Which subscription got more expensive? | 1–2 / 2–3 | 1–2 / 2 |
| Fix a wrongly sorted transaction | 4–5 / 5–6 (switch not visible on phone) | 4 / 4 |
| Depot without my own pay-ins | 1 / 2 | 1 / 2 |
| What comes off before payday? | 1 / 4 (list via Fixed costs) | 1 / 1 |

Reviews: [round 0](reviews/round-0/), [after round 3](reviews/pass-3/), [after round 6](reviews/pass-6/), [final](reviews/final/).

## Before and after, every screen

Each screen comes in four pictures: `desk.en`, `desk.de`, `phone.en`, `phone.de`. "Before" is [`round-0/`](round-0/) and "after" is [`final/`](final/). The table links the desktop English and phone German versions. Two screens are new in the final set: `28-settings-list` (the phone Settings list) and `34-payday-details` (never captured in round 0). For `10-drill-category`, round 0 captured the parent category "Income", which has no transactions of its own. The final set captures Groceries.

| Screen | Before | After | What changed |
|---|---|---|---|
| 01 Overview | [desk](round-0/01-overview.desk.en.webp) · [phone](round-0/01-overview.phone.de.webp) | [desk](final/01-overview.desk.en.webp) · [phone](final/01-overview.phone.de.webp) | grey text, Saved card names all its parts |
| 02 Transactions | [desk](round-0/02-transactions.desk.en.webp) · [phone](round-0/02-transactions.phone.de.webp) | [desk](final/02-transactions.desk.en.webp) · [phone](final/02-transactions.phone.de.webp) | one day-header style, grey text |
| 03 Needs review | [desk](round-0/03-transactions-review.desk.en.webp) · [phone](round-0/03-transactions-review.phone.de.webp) | [desk](final/03-transactions-review.desk.en.webp) · [phone](final/03-transactions-review.phone.de.webp) | name "Needs review" everywhere |
| 04 Search | [desk](round-0/04-transactions-filtered.desk.en.webp) · [phone](round-0/04-transactions-filtered.phone.de.webp) | [desk](final/04-transactions-filtered.desk.en.webp) · [phone](final/04-transactions-filtered.phone.de.webp) | grey text |
| 05 Edit dialog | [desk](round-0/05-transactions-edit.desk.en.webp) · [phone](round-0/05-transactions-edit.phone.de.webp) | [desk](final/05-transactions-edit.desk.en.webp) · [phone](final/05-transactions-edit.phone.de.webp) | merchant switch in the footer above Save |
| 06 Empty result | [desk](round-0/06-transactions-empty.desk.en.webp) · [phone](round-0/06-transactions-empty.phone.de.webp) | [desk](final/06-transactions-empty.desk.en.webp) · [phone](final/06-transactions-empty.phone.de.webp) | — |
| 07 Spending | [desk](round-0/07-spending.desk.en.webp) · [phone](round-0/07-spending.phone.de.webp) | [desk](final/07-spending.desk.en.webp) · [phone](final/07-spending.phone.de.webp) | phone: section strip, year heatmap folds in two |
| 08 New group | [desk](round-0/08-spending-group-dialog.desk.en.webp) · [phone](round-0/08-spending-group-dialog.phone.de.webp) | [desk](final/08-spending-group-dialog.desk.en.webp) · [phone](final/08-spending-group-dialog.phone.de.webp) | input borders |
| 09 Group drill-down | [desk](round-0/09-drill-group.desk.en.webp) · [phone](round-0/09-drill-group.phone.de.webp) | [desk](final/09-drill-group.desk.en.webp) · [phone](final/09-drill-group.phone.de.webp) | back chevron on the parent |
| 10 Category drill-down | [desk](round-0/10-drill-category.desk.en.webp) · [phone](round-0/10-drill-category.phone.de.webp) | [desk](final/10-drill-category.desk.en.webp) · [phone](final/10-drill-category.phone.de.webp) | back chevron (capture: Groceries) |
| 11 Fixed costs list | [desk](round-0/11-recurring-list.desk.en.webp) · [phone](round-0/11-recurring-list.phone.de.webp) | [desk](final/11-recurring-list.desk.en.webp) · [phone](final/11-recurring-list.phone.de.webp) | "on average per month"; phone strip |
| 12 Calendar | [desk](round-0/12-recurring-calendar.desk.en.webp) · [phone](round-0/12-recurring-calendar.phone.de.webp) | [desk](final/12-recurring-calendar.desk.en.webp) · [phone](final/12-recurring-calendar.phone.de.webp) | fixed costs and savings named apart |
| 13 Orbit | [desk](round-0/13-recurring-orbit.desk.en.webp) · [phone](round-0/13-recurring-orbit.phone.de.webp) | [desk](final/13-recurring-orbit.desk.en.webp) · [phone](final/13-recurring-orbit.phone.de.webp) | phone strip (orbit itself: needs Markus) |
| 14 Net worth | [desk](round-0/14-networth.desk.en.webp) · [phone](round-0/14-networth.phone.de.webp) | [desk](final/14-networth.desk.en.webp) · [phone](final/14-networth.phone.de.webp) | phone strip Net worth · Investments |
| 15 Investments | [desk](round-0/15-investments.desk.en.webp) · [phone](round-0/15-investments.phone.de.webp) | [desk](final/15-investments.desk.en.webp) · [phone](final/15-investments.phone.de.webp) | strip replaces in-page tabs; legend says pay-ins |
| 16 Forecast | [desk](round-0/16-inv-forecast.desk.en.webp) · [phone](round-0/16-inv-forecast.phone.de.webp) | [desk](final/16-inv-forecast.desk.en.webp) · [phone](final/16-inv-forecast.phone.de.webp) | order Analysis, Forecast, Pay-ins |
| 17 Analysis | [desk](round-0/17-inv-analysis.desk.en.webp) · [phone](round-0/17-inv-analysis.phone.de.webp) | [desk](final/17-inv-analysis.desk.en.webp) · [phone](final/17-inv-analysis.phone.de.webp) | phone: monthly returns in rows of six |
| 18 Pay-ins | [desk](round-0/18-inv-payments.desk.en.webp) · [phone](round-0/18-inv-payments.phone.de.webp) | [desk](final/18-inv-payments.desk.en.webp) · [phone](final/18-inv-payments.phone.de.webp) | "Pay-ins", "Don't count" |
| 19 ETF page | [desk](round-0/19-etf.desk.en.webp) · [phone](round-0/19-etf.phone.de.webp) | [desk](final/19-etf.desk.en.webp) · [phone](final/19-etf.phone.de.webp) | back chevron; phone monthly returns fold |
| 20–27 Settings tabs | [bank desk](round-0/20-settings-bank.desk.en.webp) · [bank phone](round-0/20-settings-bank.phone.de.webp) | [bank desk](final/20-settings-bank.desk.en.webp) · [security phone](final/26-settings-security.phone.de.webp) | phone: titled section with "‹ Settings", no tab strip; switches fit |
| 28 Settings list (new) | — | [phone](final/28-settings-list.phone.de.webp) | phone opens on a list of sections |
| 30 Connect bank | [desk](round-0/30-settings-connect-dialog.desk.en.webp) · [phone](round-0/30-settings-connect-dialog.phone.de.webp) | [desk](final/30-settings-connect-dialog.desk.en.webp) · [phone](final/30-settings-connect-dialog.phone.de.webp) | no "No bank found" before typing |
| 31/32 Hidden amounts | [desk](round-0/31-hidden-overview.desk.en.webp) · [phone](round-0/32-hidden-investments.phone.de.webp) | [desk](final/31-hidden-overview.desk.en.webp) · [phone](final/32-hidden-investments.phone.de.webp) | — |
| 33 Period menu | [desk](round-0/33-period-menu.desk.en.webp) · [phone](round-0/33-period-menu.phone.de.webp) | [desk](final/33-period-menu.desk.en.webp) · [phone](final/33-period-menu.phone.de.webp) | This month / Last month |
| 34 Payday details (new capture) | — | [desk](final/34-payday-details.desk.en.webp) · [phone](final/34-payday-details.phone.de.webp) | unchanged, now reviewed |
| 40–42 Wizard, login | [wizard phone](round-0/41-wizard-country.phone.de.webp) · [login](round-0/42-login.desk.en.webp) | [wizard phone](final/41-wizard-country.phone.de.webp) · [login](final/42-login.desk.en.webp) | footer wraps; visible focus border |

## Accepted changes

| Round | What | Why (evidence) | Commit |
|---|---|---|---|
| 1 | Phone: one section strip under the top bar for sub-pages (Spending · Fixed costs; Net worth · Investments; Investments · Analysis · Forecast · Pay-ins). It replaces the "Ausgaben \| Fixkosten" switch and the depot's own strip. Parent page in the eyebrow gets a back chevron. Tab bar spreads over the full width. | 5 of 6 reviewers couldn't reach Fixed costs or the depot pages on a phone; won 9 of 10 blind pairs | 44a5069 |
| 2 | One name for one thing. The calendar title splits fixed costs from savings ("1,423.48 € fixed costs · 1,100.00 € saved"). EN "Pay-ins", "Don't count" and "transaction" everywhere. "Needs review". Depot order Analysis, Forecast, Pay-ins. | 4–5 reviewers each; won 9/9 | a420252 |
| 3 | `--faint` grey from 3.0:1 to 4.8:1. Phone segmented switches share the width and wrap. The wizard footer wraps. | AA failures, clipped German labels; won 9 of 11 | 7b6bddb |
| 4 | Edit dialog: the "every transaction from this merchant" switch moves into the sticky footer above Save. The period menu gets "This month" / "Last month". | out of sight on a phone; "last month" took 5–7 steps; won 4/4 and 2/2 | adabfa8 |
| 5 | Phone: the year heatmap and monthly returns fold into two halves (Jan–Jun, Jul–Dec) instead of scrolling sideways. | stopped at June on a phone; won 4/4 | 31c4aeb |
| 6 | One day-header style; the Saved card names every part ("… invested · … put aside · … stays"); stronger input borders and a champagne focus border; no "No bank found" before typing. | designer, phone, first-time; won 8/8 | f9fbe54 |
| 7 | "Fixed costs, on average per month"; depot legend "Value without your pay-ins". | list and calendar totals looked contradictory; won 3/3 | 2c8368c |
| 8 | Phone Settings opens on a list of the 8 sections with one line each. A section has its own title and "‹ Settings". | 2.5 of 8 tabs visible; won 5/5 | dff6b4d |
| — | Security fixes from CodeQL on the touched file: an unknown `#hash` can only resolve to a known section, and the export link is one of two fixed addresses. | CodeQL "DOM text reinterpreted as HTML" (high) | ce88b10, bc01120 |

## Tried and reverted

- **Round 1: a depot strip on the ETF page.** It stacked with the ETF page's own tabs, giving two rows that both contain Analysis and Forecast. It lost on that page, so the strip is off for `/investments/etf/…`.
- **Round 3: sideways charts opening at the latest month.** It hid the outlined best and worst months that the legend refers to, and scrolled the weekday labels away. Lost on Analysis and tied on Spending. Round 5's folding replaced it.
- **Round 4, first try: the merchant switch above the category list.** It lost on desktop, where the old spot happened to sit next to Save. The second try (footer) won 4/4.
- **Round 7: the share base "(58 % of spending)".** It lost on both sizes because the card already says it. (The Android app says it this way; see below.)
- **Round 7: the month in the calendar title.** It lost on both sizes because the stepper beside it names the month, and on a phone the title wrapped.
- **Round 7: EN "Ups and downs" renamed to "Swing".** It lost; the old name matches the card's own explanation. The two swing figures (15 % assumed for the forecast, ±17 % measured) stay apart.

## Needs backend

- **Needs review count.** The badge (39) counts guesses to confirm and transactions with no category together. The Overview says "sorted on its own, do they look right?" and the queue says "need a category from you". To word each correctly, the badge endpoint should return guesses and blanks separately. Raised by IA, first-time and daily user in every pass.
- **Income vs. "in" on Transactions.** The Overview's income (33,538.60 €) leaves out moves between your own accounts, but the Transactions summary line (42,057.91 € in) includes them. The list endpoint could return in/out without own transfers, or both.
- **Gain on a holding vs. the ETF page.** One fund shows +7.5 % / 474 € on Investments (this period) and +17.2 % / 1,160.97 € on its own page (since the first buy). The holdings endpoint doesn't say which period its figure covers. A `since` field would let both pages label the figure.
- **Sharpe ratio.** The depot settings mention it, but no screen shows it under that name. It is only the sentence "for every 1 % it swings …".
- **Categorizer status.** The demo shows a green "Offline" badge next to "built-in model not found". The status endpoint should say whether the model is loaded, so the badge can be honest. This may be a demo artefact.

## Needs Markus

Removals, identity changes and close calls I did not make on my own:

1. **Merchant switch on by default.** Two reviewers in every pass call "use for every transaction from this merchant" a risk when it is on by default. It is a deliberate self-learning choice, so I only moved it next to Save. Turning it off by default is your call.
2. **Orbit view.** All three visual reviewers (designer, data-vis, phone) call it unreadable and untappable on a phone in every pass. Options: hide it below 820 px, or drop it (it answers nothing the list and calendar don't). Removal, so yours.
3. **The sunburst on Spending.** It repeats the sorted bar list beside it, and its outer ring is about 20 unlabelled slivers. Options: drop the outer ring, or drop the sunburst.
4. **The tank/jar on the Overview hero.** An unlabelled duplicate of the hero number. Removal.
5. **"Group" means two things.** Built-in groups (Housing, Food & Dining) and your own cross-category groups. A rename of the custom one (Project / Topf) changes a known name.
6. **"Konto & Darstellung" / "Account & look".** It clashes with bank accounts (Girokonto, "Add account"). The suggestion is "Profil" / "Profile & look".
7. **"Zurücklegen" (Hints & salary) vs. "zurückgelegt" (Overview flow).** Same word, different meaning.
8. **Area fills over axes that don't start at zero.** Net worth starts at 25k, the depot at 8k. Dropping the fill or starting at zero changes the look of the two biggest charts.
9. **The gold accent on every switch.** On Hints & salary, six glowing switches are the loudest thing on the page. A quieter "on" style would be an identity refinement.
10. **Disabled primary buttons (~3:1).** Login, wizard and dialogs dim the gold button. A neutral disabled style, or validating on submit, changes how the primary button behaves.

## What now differs from the Android app

The Android app (`android/`, not touched) has four screens: Overview, Transactions, Spending, Wealth. Differences from the web after this branch:

- Phone navigation: the web phone has the section strip (Spending · Fixed costs, Net worth · Investments, depot sub-pages) and a Settings list. Android has neither the fixed-costs pages nor the depot sub-pages.
- Words (EN): the web says "transaction" and "Pay-ins"; Android still says "booking" ("Groschen sorted {n} bookings on its own", "1 booking").
- Period: the web's menu has "This month" / "Last month"; Android's spending chips have no "Last month".
- Spending share: Android says "58 % of spending · period"; on the web that wording lost the blind test (round 7) and the web keeps "(58 %)".
- Fixed costs: the web says "on average per month" and splits fixed costs from savings in the calendar. Android shows "Fixed costs" without the average note.
- Charts that fold on a phone (year heatmap, monthly returns) don't exist on Android.

## Routes

No route was added, removed or renamed. `frontend/scripts/record-demo.cjs` and the README need no change for routes.

- The order of depot sub-pages in the sidebar is now Analysis, Forecast, Pay-ins (same paths: `/investments/analysis`, `/investments/forecast`, `/investments/payments`).
- On a phone, `/settings` without a hash now shows the section list. With a hash (`#bank` … `#account`, plus the old `#groups`, `#salary`, `#investments`, `#network`, `#look`) it opens that section as before. On desktop `/settings` still opens `#bank`.
- The "Ausgaben | Fixkosten" switch (`SpendSwitch`) is gone. `/recurring` and its `?view=` addresses are unchanged.
- The screenshot script added two states: `28-settings-list` (`/settings` on a phone) and `34-payday-details` (the hero's "payments still to come" dialog).

## Stopping

The loop ran its 8 rounds. The final pass still names problems above cosmetic, but every remaining top item falls into one of four kinds:
- a removal or identity change (needs Markus: Orbit, sunburst, tank, switch default, area fills, accent);
- a backend change (Needs review count, income totals, gain periods);
- a rename of a known name (Group, Konto);
- something the round 7 judge rejected.

The branch is not merged.
