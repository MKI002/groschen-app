# Judge 2: blind comparison of Groschen screens

How I compared: I computed pixel differences for each pair and zoomed into every changed area. All differences are text and order changes. Layout, colour and data are the same in both versions. There are five kinds of change:
- **Investments sub-nav order**: "Analysis, Forecast" vs "Forecast, Analysis".
- **Name of the investments payments page**: "Pay-ins" vs "Payments". In German both versions say "Einzahlungen".
- **Word for a bank line**: "transactions" vs "bookings". The nav item and page are called "Transactions".
- **Fixed-costs headline**: split ("1,423.48 € fixed costs · 1,100.00 € saved") vs total ("2,523.48 € fixed costs this month").
- **Opt-out control on Pay-ins**: "Don't count" vs "Not counted". The Settings hint also points to "Needs review" or "To review".

The improved variant is not always on the same side (A or B), so read each table on its own.

## Pair 01: Overview (desk, en)
Differences: the "Worth a look" card says "39 transactions" (B) vs "39 bookings" (A). Sidebar: B shows Analysis/Forecast/Pay-ins, A shows Forecast/Analysis/Payments.

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | same | The card and its "Check" action are the same in both |
| hierarchy | same | No change in layout or weight |
| task efficiency | same | Same actions and links |
| data presentation | same | Same figures and Sankey chart |
| navigation and naming | B | "transactions" matches the Transactions nav item it sends you to, and "Pay-ins" is more specific than "Payments" |
| consistency | B | One word for bank lines across the app, and the sub-nav matches the other screens in its version |
| phone experience | same | Desktop only |
| accessibility | same | Same contrast and sizes |
| visual craft | same | Only the line break of the card text moves |

**Winner: B.** A is not better anywhere important.

## Pair 02: Transactions, Needs review (desk, en)
Differences: the banner says "These transactions need a category" (A) vs "These bookings…" (B). Sidebar: A shows Analysis/Forecast/Pay-ins, B shows Forecast/Analysis/Payments.

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | A | The banner uses the page's own word, "Transactions", and the counter right below says "8 transactions" |
| hierarchy | same | Same |
| task efficiency | same | Same filters and list |
| data presentation | same | Same rows |
| navigation and naming | A | "Pay-ins" in the sidebar, and the banner wording matches the page title |
| consistency | A | In B, the banner says "bookings" while the counter says "transactions" |
| phone experience | same | Desktop only |
| accessibility | same | Same |
| visual craft | same | Same |

**Winner: A.** B is not better anywhere.

## Pair 03: Spending drill-down, Food & Dining (desk, en)
Differences: the KPI reads "79 transactions" (A) vs "79 bookings" (B). The sidebar differs as in pair 02.

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | same | Same header and KPI block |
| hierarchy | same | Same |
| task efficiency | same | Same |
| data presentation | A | The "79 transactions" count uses the app's term for these rows |
| navigation and naming | A | Sidebar says "Pay-ins", and the KPI term matches the Transactions nav |
| consistency | A | Same vocabulary as the Transactions screen |
| phone experience | same | Desktop only |
| accessibility | same | Same |
| visual craft | same | Same |

**Winner: A**, by a small margin. B is not better anywhere.

## Pair 04: Fixed costs, calendar (desk, en)
Differences: the headline is "1,423.48 € fixed costs · 1,100.00 € saved" (A) vs "2,523.48 € fixed costs this month" (B). The sidebar differs as in pair 02.

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | A | It separates real fixed costs from standing orders into savings (Sparen 800 + Sparpläne 300 = 1,100). B counts savings as costs |
| hierarchy | same | Same size and position |
| task efficiency | same | Same |
| data presentation | A | The split figure is more accurate. Small catch: the line below still says "2,523.48 € paid", which does not match the 1,423.48 headline at a glance |
| navigation and naming | A | Sidebar order and "Pay-ins" |
| consistency | A | The sub-nav matches the other screens of its version |
| phone experience | same | Desktop only |
| accessibility | same | Same |
| visual craft | same | Same |

**Winner: A.** B's single total reconciles directly with the "paid" line, which is a minor plus. It does not outweigh the misleading "costs" figure.

## Pair 05: Fixed costs, calendar (phone, de)
Differences: the headline is "2.523,48 € Fixkosten in diesem Monat" (A) vs "1.423,48 € Fixkosten · 1.100,00 € gespart" (B).

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | B | Saving is not shown as a cost |
| hierarchy | same | Same |
| task efficiency | same | Same |
| data presentation | B | The split figure is more honest. The same "2.523,48 € bezahlt" mismatch applies below it |
| navigation and naming | same | The tabs are the same |
| consistency | B | Matches the split headline on desktop in its version |
| phone experience | B | The headline still fits on one line at 390 px and carries more meaning |
| accessibility | same | Same |
| visual craft | same | Same |

**Winner: B.** A is not better anywhere important.

## Pair 06: Investments / Depot (desk, de)
Differences: only the sidebar order. A has Analyse, Prognose, Einzahlungen. B has Prognose, Analyse, Einzahlungen.

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | same | Same page |
| hierarchy | same | Same |
| task efficiency | same | Same |
| data presentation | same | Same |
| navigation and naming | A | Slightly better order: look at the past (Analyse) before the future (Prognose) |
| consistency | A | Matches the phone tab order and the other screens in its version |
| phone experience | same | Desktop only |
| accessibility | same | Same |
| visual craft | same | Same |

**Winner: A**, marginal. On this screen alone it is nearly a tie.

## Pair 07: Investments Pay-ins (desk, en)
Differences: the title is "Pay-ins" (A) vs "Payments" (B). The row action is "Don't count" (A) vs "Not counted" (B). The sidebar differs too.

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | A | "Pay-ins" says money put into the depot, which matches the "Money put in" card. "Payments" could mean any outgoing payment |
| hierarchy | same | Same |
| task efficiency | A | "Don't count" with an × reads as an action you can click. "Not counted" reads like a status, which is wrong because these rows are counted |
| data presentation | same | The rows and totals are the same in both. Both still label the rows "2 payments" |
| navigation and naming | A | The title, breadcrumb and highlighted sidebar item all say "Pay-ins" |
| consistency | A | The title matches "Money put in", and the sub-nav order matches the other screens |
| phone experience | same | Desktop only |
| accessibility | A | The control's label describes what clicking it does |
| visual craft | same | Same |

**Winner: A.** B is not better anywhere.

## Pair 08: Investments Pay-ins (phone, en)
Differences: the tabs are Investments·Analysis·Forecast·Pay-ins (A) vs Investments·Forecast·Analysis·Payments (B). The title and row action differ as in pair 07.

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | A | Title "Pay-ins" |
| hierarchy | same | Same |
| task efficiency | A | "Don't count" is clearly an action |
| data presentation | same | Same. A truncates the fund name one character later ("iShs C…") |
| navigation and naming | A | Tab and title wording match the desktop version |
| consistency | A | Same order and names as the desktop sidebar in its version |
| phone experience | A | The shorter tab label leaves more room in the tab strip, and the action is easy to tap |
| accessibility | A | The label describes the action |
| visual craft | same | Same |

**Winner: A.** B is not better anywhere.

## Pair 09: Settings, Categories (desk, en)
Differences: the hint says "…wait under Transactions, Needs review" (B) vs "…, To review" (A). The text reads "future transactions" (B) vs "future bookings" (A), and "collects transactions" (B) vs "collects bookings" (A). The sidebar differs too: B shows Analysis/Pay-ins.

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | B | The hint uses the real filter name, "Needs review", which is also in the toggle's own title |
| hierarchy | same | Same |
| task efficiency | B | You can find the target filter by name. A points to a "To review" filter that does not exist |
| data presentation | same | Same |
| navigation and naming | B | "Needs review" and "transactions" match the Transactions page. "Pay-ins" in the sidebar |
| consistency | B | A uses three names in one screen: "Needs review" in the title, "To review" in the hint, and "bookings" in the text |
| phone experience | same | Desktop only |
| accessibility | same | Same |
| visual craft | same | Same |

**Winner: B.** A is not better anywhere.

## Overall verdict

| Pair | Winner |
|---|---|
| 01 Overview desk | B |
| 02 Transactions review desk | A |
| 03 Drill group desk | A |
| 04 Fixed-costs calendar desk | A |
| 05 Fixed-costs calendar phone | B |
| 06 Investments desk (de) | A (marginal) |
| 07 Pay-ins desk | A |
| 08 Pay-ins phone | A |
| 09 Settings categories desk | B |

**Across the set**, one version is fully consistent. Its screens are pair 01 B, 02 A, 03 A, 04 A, 05 B, 06 A, 07 A, 08 A and 09 B:
- One word for bank lines, "transactions", matching the nav item.
- One sub-nav order, Investments → Analysis → Forecast → Pay-ins, on both desktop and phone.
- "Pay-ins" in the title, breadcrumb, sidebar and phone tab.
- A Settings hint that names the real "Needs review" filter.
- Fixed costs shown separately from savings on both desktop and phone.

The other version mixes "bookings" and "transactions" and names a non-existent "To review" filter. Moving from the Overview card, Settings or the drill-down to the Transactions page works better in the consistent version.

Two small leftovers in the better version:
- The split fixed-costs headline (1,423.48) sits above a "2,523.48 paid" line.
- Pay-ins month rows still say "2 payments".
