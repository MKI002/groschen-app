# GUI improvement loop: log

Branch `redesign/loop`, started 2026-11-25. Every screenshot comes from the web demo (`npx vite --mode demo`, invented data, clock frozen on Fri 30 Oct 2026). Screenshots in the repository are WebP (quality 85) to keep the history small; the reviewers saw the original PNGs.

## Setup

- Screenshot script: Playwright, outside `frontend/` (not committed). 34 states × 2 sizes (1500×950 desktop, 390×844 phone) × 2 languages = 136 pictures per full pass. Tall pages are captured by growing the window to the page height (max 5200 px) so the fixed sidebar and the phone tab bar sit where a person sees them. Animations off (`groschen.motion=off`, reduced motion) for reproducible pictures; the demo banner is hidden.
- States beyond the routes: transaction edit dialog, review queue, search in use, empty search result (patched empty answer), new-group dialog, connect-bank dialog, period menu, hidden amounts (Overview, Depot), wizard step 1 (no user) and step 2 (no setup), login.
- Demo limits the reviewers were told about: the demo can't filter, so the review queue and search show the recorded unfiltered list.

## Round 0

### Inventory

Frequency: D = daily, W = weekly, M = monthly, R = rarely. "Candidate" marks elements that answer no clear question, or a rare question in a prime spot.

**Overview (`/`)**
| Element | Question it answers | How often |
|---|---|---|
| "Available until payday" hero, per-day figure | How much can I still spend before the salary comes? | D |
| Day strip to payday with dots for charges, "14 payments still to come" | What comes off my account before payday? | D/W |
| Tank graphic beside the hero | Same as the hero, as a fill level | — candidate (duplicate of the hero number) |
| "Worth a look" inbox (review, new subscription, unusual month) | Is there anything I should act on? | D |
| Period cards Income / Spending / Saved with mini bars and savings-rate ring | How did this period go? | M |
| "Where the money went" flow (Sankey) / Timeline | Where did the income go? | M |

**Transactions (`/transactions`)**: search (D), quick filters All / Needs review / Uncategorized / Income (D/W), Filter and sort menus (W), period picker (W), summary line count/in/out (W), day-grouped list with logo, purpose, category chip, account, amount, day total (D), edit dialog with category chips and "always for this merchant" (W), review bar with accept-all (W), "load more" (R).

**Spending (`/spending`)**: Spending/Income switch (M), "Your own group" chip (R, prime spot: candidate), breakdown sunburst + ranked bars with share (M), Groups/Categories switch (M), "Your year in days" heatmap with three stats (R/M). Drilldowns (`/spending/group|category|payee`): total vs. period before, per-month bars with average (M), top merchants (M), categories (M), filtered list (W).

**Fixed costs (`/recurring`)**: List: monthly total + "next up" three (W), "What changed" (M; answers "what got more expensive"), "Running" list with badges (M), stopped (R), savings-plans link (R). Calendar: month grid + "day by day" (W). Orbit: rings per rhythm (R; answers no question the list doesn't: candidate).

**Net worth (`/networth`)**: total with change and trend line (M), account cards with share bar (M), "Add account" (R), savings plans with coin rows (M).

**Investments (`/investments` + Forecast, Analysis, Payments)**: depot value with change and pay-ins, value chart with monthly gain/loss bars and "Money paid in" toggle (W/M), holdings cards (M), tax-free allowance bar (R/annual), justETF opt-in banner (R, but shown on every visit while off). Forecast: assumption tiles, fan chart, milestones (R). Analysis: return with and without timing, swing gauge, drawdown, monthly returns strip (M/R). Payments: pay-ins by month with "not counted" (M), price-history import (R). ETF page: tabs Overview/Analysis/Forecast/Facts, value, price chart with average price line (M).

**Settings**: 8 tabs (Bank & import, Categories, Hints & salary, Investments, Backups, Export & privacy, Security, Account & look). Monthly to rare. The 90-day bank login (every 90 days) lives here and in a banner.

**Shell**: sidebar with 5 places + depot children, sync box, eye (hide amounts), user + log out; phone: top bar (sync chip, eye, gear) and 4-tab bar (Overview, Transactions, Spending, Net worth).

**Wizard and login**: five-step first run (account, country/bank, history import, smart features, first sync); login with password/passkey.

### Research: comparable tools

Sources and notes from Actual Budget, Firefly III, Ghostfolio, Lunch Money, Monarch, Copilot Money, YNAB, MoneyMoney, Finanzguru (docs, help centres, app-store pages). Ideas, not clones:

- **Overview.** Copilot's dashboard puts "Free to spend" first, then a cumulative-spend line against an ideal pace line ("am I ahead of pace today?"), then To review, then an "Upcoming" strip of recurrings ([help](https://help.copilot.money/en/articles/6045480-dashboard-tab-overview)). Finanzguru shows "frei verfügbares Einkommen" and the bookings still expected this month. Groschen is the only one counting to *payday* rather than month end, with a per-day figure and one inbox that merges review, subscriptions and anomalies: keep.
- **Transactions.** Copilot marks unreviewed rows with a dot in every list and offers keyboard shortcuts; Monarch offers a rule *after* a category change; Lunch Money totals a multi-selection. Groschen's "use for every booking from this merchant" in the dialog is simpler than a rule builder: keep.
- **Spending.** YNAB's breakdown is a stack-ranked list by share with a separate inflow/refund section; Copilot colours category bars by pace. A sorted bar list reads values better than a sunburst; Groschen already pairs both.
- **Fixed costs.** Monarch's calendar marks paid items with checks; Lunch Money shows matched / overdue / upcoming state per row. Explicit "what changed" (price up/down, new, stopped) is rare: only Groschen and Rocket Money surface it prominently ([comparison](https://getfinny.app/blog/apps-track-subscription-price-increases-2026)). Orbit-like views are unique but not scannable; the list should stay default.
- **Net worth.** Actual shows a trend/stacked net-worth chart; Firefly has piggy banks (goals). Groschen's auto-detected savings plans are unique.
- **Investments.** Ghostfolio: one period selector for all charts, benchmark compare, invested-capital vs. value chart ([docs](https://ghostfolio-docs.pages.dev/analyzing-portfolio-performance)); Finanzfluss Copilot explains TWROR vs. price gain. Two lines (paid in vs. value, gap shaded) is the common way to keep pay-ins from looking like gains.
- **Navigation.** YNAB mobile: five bottom tabs; Copilot: Dashboard, Transactions, Accounts, Investments, Categories, Recurrings, Cash flow; Ghostfolio: Overview, Portfolio, Accounts. Monarch's Sankey falls back to bars on phones.
- **Hide amounts.** Ghostfolio's Zen mode and Monarch's share mode hide amounts; Groschen's eye in the header already does this.

### Baseline review (six reviewers, fresh context, screenshots only)

Full reviews: [`reviews/round-0/`](reviews/round-0/). Mean rubric scores per area, pulled from the reviewers' tables by a small script (each reviewer scored only the lines their role can judge, so not every cell has six votes):

| Area | Clarity | Hierarchy | Tasks | Data | Naming | Consistency | Phone | Access. | Craft | Mean |
|---|---|---|---|---|---|---|---|---|---|---|
| Overview | 7.2 | 7.7 | 8.0 | 6.2 | 6.4 | 6.5 | 7.2 | 6.0 | 7.3 | 6.9 |
| Transactions | 8.0 | 7.0 | 6.5 | 6.8 | 6.0 | 5.2 | 6.2 | 5.0 | 7.0 | 6.5 |
| Spending | 7.2 | 6.5 | 6.0 | 6.7 | 4.8 | 5.6 | 4.8 | 5.0 | 7.0 | 5.9 |
| Drilldowns | 6.0 | 8.0 | 5.0 | 5.8 | 4.8 | 5.5 | 6.0 | – | 6.5 | 5.9 |
| Fixed costs | 6.4 | 7.5 | 5.0 | 5.3 | 5.2 | 4.3 | 5.5 | 6.0 | 6.0 | 5.6 |
| Net worth | 8.3 | 8.0 | 7.0 | 6.0 | 5.7 | 6.0 | 7.0 | – | 7.0 | 6.8 |
| Depot | 7.0 | 7.0 | 7.2 | 6.6 | 5.4 | 4.7 | 6.6 | 5.0 | 7.0 | 6.4 |
| ETF page | 7.7 | 7.0 | 6.0 | 7.3 | 5.0 | 4.7 | 6.3 | 5.0 | 7.5 | 6.3 |
| Settings | 7.0 | 7.0 | 6.0 | 5.0 | 5.0 | 4.0 | 5.0 | 6.0 | 7.0 | 5.5 |
| Wizard & login | 8.0 | 8.0 | – | – | 6.5 | 6.0 | 5.0 | – | 7.0 | 6.7 |

Two findings were capture artefacts, not app problems, and were left alone: Settings said "Next sync tomorrow at 05:00" under a 06:00 schedule (and backups 02:00 vs. 03:00) because the screenshot browser ran in UTC; from round 1 on the script runs in Europe/Berlin. "No bank found by that name" before typing in the connect dialog comes from the demo having no bank list.

### Ranked backlog

Score = reviewers raising it × severity (blocks 3, slows 2, cosmetic 1) × use (daily 3, weekly/monthly 2, rare 1) ÷ effort (1 small, 2 medium, 3 large).

| # | Item | Raised by | Sev. | Use | Effort | Score |
|---|---|---|---|---|---|---|
| 1 | Phone navigation: Fixed costs only via a second "Spending" switch, Depot only via a card chevron, two stacked switches both starting "Ausgaben", depot-only tab strip | IA, first-time, daily, designer, phone (5) | 3 | 3 | 2 | 22.5 |
| 2 | Faint grey secondary text below AA (account column, percentages, dates, captions) | designer, phone (2) | 2 | 3 | 1 | 12 |
| 3 | Review queue says three different things ("sorted on its own, look right?" / "need a category from you" / "To review"), and silently switches to all periods | IA, first-time, daily (3) | 2 | 2 | 1 | 12 |
| 4 | Fixed-costs totals disagree: calendar "2,523.48 € fixed costs this month" (counts savings plans and salary) vs. list "1,407.01 € per month" | IA, first-time, dataviz, daily (4) | 2 | 2 | 1 | 16 |
| 5 | Depot naming: "Payments" means pay-ins, "Not counted" vs. "Nicht zählen", tab order differs between depot and ETF page, gains without a stated period | IA, first-time, dataviz, daily, designer (5) | 2 | 2 | 2 | 10 |
| 6 | Phone: German strips and switches clip ("Sich…", "Buchungsmor…", "Einzahlungen"); heatmap and monthly returns stop at June; wizard skip link overflows | designer, phone, dataviz, IA (4) | 2 | 1 | 1 | 8 |
| 7 | Settings on phone: 8 tabs in one sideways strip, 5 hidden | IA, designer, phone (3) | 2 | 1 | 2 | 3 |
| 8 | Transactions on desktop: ~600 px gap between name and category, chips not on a column, two date-header styles | designer, phone (2) | 2 | 3 | 2 | 6 |
| 9 | Overview hero: doesn't say what is already subtracted; no week figure; unlabelled tank | daily, dataviz, designer, first-time (4) | 2 | 3 | 2 | 12 |
| 10 | Drill pages have no visible way back | IA, phone (2) | 2 | 2 | 1 | 8 |
| 11 | Edit dialog: "always for this merchant" switch hidden below ~40 chips on phone | daily, phone (2) | 2 | 2 | 1 | 8 |
| 12 | Fixed costs "Running" sorted by raw amount across monthly/yearly; price-rise badges without context | dataviz, daily (2) | 2 | 2 | 1 | 8 |
| 13 | Orbit view unreadable (no labels, overlaps on phone) | first-time, dataviz, phone (3) | 2 | 1 | 2 | 3 |
| 14 | Depot chart "value without deposits" starts at an invented level; net-worth area on a 25k baseline | dataviz (1) | 2 | 2 | 2 | 2 |
| 15 | Period menu: "last month" needs Month then ‹ | daily (1) | 3 | 2 | 1 | 6 |

Plan: structure first (1, with 10), then the cheap cross-cutting wins (2, 3, 4, 5, 6), then the daily screens (9, 8, 11, 12), then the rest as rounds allow.

## Round 1: phone navigation and the way back

**Theme.** Backlog #1 (phone can't reach Fixed costs and Depot directly; two stacked switches both start with "Ausgaben") and #10 (drill pages have no visible way back).

**Explored.** Three options, judged by two fresh reviewers (daily phone user; information architect / newcomer) from a description plus the current phone screenshots:
- A: five tabs (Overview, Transactions, Spending, Fixed costs, Net worth), depot sub-pages in a strip.
- B: four tabs plus one section strip under the top bar that mirrors the sidebar's sub-items wherever a place has them.
- C: five tabs with Depot as a tab, Fixed costs in a strip.

Both picked **B** (one pattern for sub-pages, matches the sidebar, leaves room in the bar and in German labels). Both asked that the strip show its level so "Analyse" next to "Vermögen" can't be read as analysing all money: built as two levels ("Vermögen · Depot" on Net worth, "Depot · Prognose · Analyse · Einzahlungen" on the depot pages), with a fade where a strip scrolls.

**Built.**
- `SectionStrip` in `Shell.tsx` (phone only), driven by a small table next to `MAIN_NAV`; it replaces the "Ausgaben | Fixkosten" switch (`SpendSwitch`, removed) and the depot's phone-only tab strip. Segmented switches now only filter or change a view.
- `Tabs` gained a `nav` mode (a `<nav>` with `aria-current` instead of a tablist) and edge fades whenever a strip scrolls (also helps Settings).
- The parent page in a page's eyebrow gets a back chevron and a larger hit area (drill pages, depot pages, ETF page).
- The phone tab bar spreads its four tabs over the full width instead of leaving a fifth slot empty.

**Blind judge** (10 pairs; [`reviews/round-1/judge.md`](reviews/round-1/judge.md), key in `key.json`): the new version won 9 of 10 pairs (Spending, Fixed costs, Net worth, Depot, Analysis, drill-down phone and desktop, Investments EN, Orbit). The ETF page was a tie leaning to the old version: the depot strip stacked on top of the ETF page's own tabs gave two tab rows that both contain "Analyse" and "Prognose".

**Kept**, with one fix from the verdict: no section strip on an ETF page (it has its own tabs and the back link to the depot). Rechecked on `19-etf.phone.de`: one tab row again.

## Round 2: one name for one thing

**Theme.** Backlog #3, #4, #5: the same thing under different names, and totals that disagree.

**Built** (copy and one computed title; no new elements):
- Fixed-costs calendar title: "1,423.48 € fixed costs · 1,100.00 € saved" instead of "2,523.48 € fixed costs this month", which counted standing orders to savings and the depot as fixed costs and contradicted the list. Paid / still to come and the bar now count the fixed costs only, so the line adds up to the title. Computed from the calendar entries' `kind`, no new data.
- English: "Payments" (the depot's pay-ins page) is now "Pay-ins", its rows "2 pay-ins"; the row action "Not counted" (read as a status) is now "Don't count", matching German "Nicht zählen".
- English: "transaction" everywhere instead of a mix of "booking" and "transaction" (German already says "Umsatz" throughout). Kept "booking text" and "booking month", which are bank terms.
- Settings pointed to a filter called "To review"; it is "Needs review".
- Depot sub-pages in the order the ETF page already uses: Analysis, Forecast, Pay-ins (Analysis is the more frequent question).
- Screenshot script: the review queue now shows only the transactions that wait for a look (the demo can't filter; the patch does what the server does).

**Blind judge** (9 pairs, [`reviews/round-2/judge.md`](reviews/round-2/judge.md)): the new version won all 9; "in no pair is the losing side better anywhere important". Two leftovers it named (calendar paid line still summing savings; pay-in rows saying "payments") were fixed before committing and rechecked on `12-recurring-calendar.desk.en` and `18-inv-payments`.

**Kept.**

**Not changed, noted:** the Overview inbox says "Groschen sorted 39 transactions on its own. Do the categories look right?" while the queue can also hold transactions without any guess ("These transactions need a category from you"). Telling them apart needs a count of guesses vs. blanks the badge endpoint doesn't return: see "needs backend".

## Round 3: readable grey, nothing cut off on a phone

**Theme.** Backlog #2 (secondary text below AA) and #6 (phone: switches and the wizard footer cut off; heatmap and monthly returns open on January).

**Built.**
- `--faint` from #5E636C to #7E838C: 4.8:1 on the card surface instead of 3.0:1 (account column, percentages, dates, captions, placeholders). `--muted` unchanged, so the two greys still differ.
- Phone: a segmented switch shares the screen width and lets an option break onto two lines instead of running off the card ("15 Tage vorher", "Buchungsmonat", "Einnahmen").
- Wizard footer: the long "Überspringen, vorerst CSV-Dateien nutzen" wraps inside the card, "Weiter" stays right.
- Tried: sideways-scrolling time charts (year heatmap, monthly returns, drawdown, pay-in bars) open on the latest end, with a fade on the left.

**Blind judge** (11 pairs, [`reviews/round-3/judge.md`](reviews/round-3/judge.md)): the new version won 9 (both Settings switches, wizard, Transactions phone and desktop, Overview, Fixed costs, Investments, ETF phone), mostly for the brighter grey and nothing clipped. It lost Investments › Analysis on the phone narrowly and tied on Spending: opening at the latest end hid the outlined best and worst months that the legend refers to, and scrolled the heatmap's weekday labels out of view.

**Kept** the grey and the phone fixes. **Reverted** the open-on-the-latest-end scrolling (the losses came only from it). Better fix for later: lay the monthly returns out in rows of six on a phone instead of a sideways scroll (see backlog).

## Full pass after round 3 (six fresh reviewers, all 136 screenshots)

Reviews: [`reviews/pass-3/`](reviews/pass-3/). Mean scores (same extraction as round 0; absolute scores drift, so these are a side-effect check, not the ratchet):

| Area | Clarity | Hierarchy | Tasks | Data | Naming | Consistency | Phone | Access. | Craft | Mean |
|---|---|---|---|---|---|---|---|---|---|---|
| Overview | 7.0 | 7.7 | 8.0 | 6.5 | 6.0 | 7.0 | 7.2 | 6.0 | 7.3 | 7.0 |
| Transactions | 7.6 | 7.0 | 6.0 | 6.3 | 5.6 | 6.0 | 6.1 | – | 7.2 | 6.4 |
| Spending | 7.0 | 6.5 | 6.2 | 6.3 | 5.6 | 5.3 | 6.0 | – | 7.0 | 6.2 |
| Drilldowns | 6.4 | 8.0 | 5.0 | 5.0 | 5.0 | 5.5 | 6.6 | – | 7.0 | 5.9 |
| Fixed costs | 6.6 | 7.5 | 7.0 | 5.4 | 5.7 | 6.0 | 5.4 | 4.0 | 6.5 | 6.0 |
| Net worth | 8.0 | 7.7 | 7.0 | 6.0 | 6.0 | 6.5 | 7.5 | – | 6.5 | 7.0 |
| Depot | 7.1 | 7.3 | 7.8 | 6.6 | 5.5 | 6.7 | 6.7 | – | 7.3 | 6.8 |
| ETF page | 7.7 | – | 7.0 | 6.0 | 5.2 | 4.5 | 6.7 | – | 7.5 | 6.3 |
| Settings | 7.0 | 6.7 | 7.0 | 6.5 | 6.0 | 5.0 | 6.2 | 6.0 | 7.0 | 6.3 |
| Wizard & login | 8.5 | 7.5 | 8.0 | 7.0 | 6.5 | 7.0 | 6.3 | 5.0 | 8.0 | 7.1 |

No screen got worse in any reviewer's eyes; no reviewer raised the section strip, the new names or the brighter grey as a problem. What the pass found:

- **Capture artefacts again.** The "Income" category page (category 1, a parent with no direct bookings) showed 0.00 € and was every reviewer's #1 or #3. It was my choice of page, not a path a person takes; from round 4 the script captures Groceries. "Needs review 39" opening 8 rows is the demo's 200-row recording; the server returns all 39.
- **Real, new or still open, re-ranked:**

| # | Item | Raised by | Score |
|---|---|---|---|
| 1 | Edit dialog: the "every transaction from this merchant" switch is out of sight above Save on a phone (and on by default) | daily, first-time, phone | 18 |
| 2 | Period menu has no "last month"; "what did I pay for X last month" takes 5–7 steps | daily | 18 (blocks, daily) |
| 3 | "What comes off before payday": the itemised list behind the hero link was never captured, so reviewers looked for it in the calendar | daily | capture |
| 4 | Monthly returns and year heatmap cut at June on a phone | phone, dataviz, (designer) | 8 |
| 5 | Orbit unreadable on a phone, 4 of 13 dots labelled | designer, dataviz, phone, first-time | 8 (→ needs Markus for hiding it) |
| 6 | Transactions: two styles of day header | designer (twice) | 6 |
| 7 | Disabled gold buttons and input borders below 3:1; "no bank found" before typing | designer, phone, first-time | 6 |
| 8 | "Saved" card names invested and stays, not the largest part (put aside) | first-time | 4 |
| 9 | Sankey spends half its width on a 99.6 % single source | dataviz, designer | 4 |
| 10 | Sunburst repeats the bar list; heatmap colour scale has no order | dataviz, designer | needs Markus / later |

Plan: round 4 the daily tasks (1, 2, 3), round 5 phone charts (4), round 6 polish (6, 7, 8), then the full pass.

## Round 4: two daily tasks

**Theme.** Pass-3 backlog #1 (the "every transaction from this merchant" switch is out of sight on a phone, and on by default) and #2 ("what did I pay last month" takes 5–7 steps). Plus capture: the itemised "what comes off before payday" dialog behind the hero link (`34-payday-details`), which reviewers never saw; and the category drill-down now shows Groceries instead of an empty parent category.

**Built, first try.**
- Edit dialog: the switch moved above the category list.
- Period menu: "This month" (was "Month") and a new "Last month" right under it; "Last month" is the month preset anchored one month back, so no new API parameter.

**Blind judge A** (5 pairs, `reviews/round-4/judge-a.md`): period menu won on phone and desktop; the edit dialog won on both phones but lost narrowly on desktop, where the old position happened to sit just above Save, which the judge preferred ("read once and forgotten" at the top).

**Built, second try.** The switch lives in the dialog's sticky footer, on its own line above "Everything with …" and Save, with a hairline between; same on every screen size.

**Blind judge B** (4 pairs, `reviews/round-4/judge-b.md`, against the original): the new version won all 4 ("shows the switch and its state next to Save on every screen size, which makes it easier and safer"). Cost it named: on a phone the pinned footer covers a little more of the category list.

**Kept**: second try plus the period menu. **Not changed, needs Markus:** the switch is still on by default (a deliberate self-learning choice); two reviewers want it off by default.
