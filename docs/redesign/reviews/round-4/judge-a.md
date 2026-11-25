# Judge 4: blind comparison

Folder: /tmp/claude-0/judge4/ (5 pairs, 10 pictures, all viewed).

What differs, as seen in the pictures:
- Edit dialog (pairs 1-3): the only change is where the switch "Use this category for every transaction from this merchant" sits. It is **on** by default in every picture.
  - Phone, A: the switch is at the top, between the bank text and "Category", so you see it without scrolling.
  - Phone, B: the switch is not on the first screen. It is presumably at the end of the category list. Because of that, B shows more categories without scrolling (the selected "Fuel"/"Tanken" chip and the whole Transport group).
  - Desk, A: the switch is pinned at the bottom of the dialog, just above "Save". It covers the top of the Subscriptions group.
  - Desk, B: the switch is at the top, above "Category".
- Period menu (pairs 4-5): the only change is how the month option is worded.
  - Phone, A: one item, "Monat".
  - Phone, B: two items, "Dieser Monat" and "Letzter Monat".
  - Desk, A: two items, "This month" and "Last month".
  - Desk, B: one item, "Month".
  - All other items match: Last 30 days, Year to date (checked), Year, Last 12 months, All time.

## Pair 1: transaction edit, phone, German

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | A | The merchant-wide switch is visible up front ("Diese Kategorie für alle Umsätze dieses Händlers verwenden"), so you can tell what Speichern will affect. |
| hierarchy | B | "Kategorie", the main field, comes straight after the bank text, and the selected "Tanken" chip is above the fold. |
| task efficiency | A | Switch is visible and can be turned off before saving. In B it is off-screen yet on, so a plain Save probably recategorises every Shell transaction. |
| data presentation | B | The current category ("Tanken", highlighted) is visible without scrolling. In A it is hidden below "MOBILITÄT". |
| navigation and naming | same | Same labels everywhere: Kategorie, + Neu, "Alles mit Shell", Speichern. |
| consistency | same | Chips, group headers and footer are identical. |
| phone experience | A | On a small screen, an action that changes many transactions should not be hidden below the fold. |
| accessibility | A | The switch and its label are visible together near the top. In B, screen-reader and keyboard users meet it last or not at all. |
| visual craft | B | Slightly tidier: the label and switch on two lines in A look loose. |
| **Overall** | **A** | Keeping the bulk-change switch visible matters more than saving one scroll. B's real advantage is that the selected chip is visible straight away. |

Task "fix the category of this one transaction without changing others": **A is easier.** You see the switch is on and turn it off before Speichern. In B you have to know to scroll to the end, or you risk changing all Shell transactions.

## Pair 2: transaction edit, desktop, English

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | A | The switch sits next to Save, so the scope of the save ("every transaction from this merchant") is right where you confirm it. |
| hierarchy | A | Reads in order: what it is (bank text) → choose a category → decide the scope → Save. B puts the scope question before you have chosen anything. |
| task efficiency | A | The last thing you see before Save is the switch, which is on by default. In B you read it once at the top and can forget it after scrolling through the chips. |
| data presentation | B | B shows the whole Subscriptions header and chips area. A's pinned switch overlaps the "SUBSCRIPTIONS" group. |
| navigation and naming | same | Identical wording. |
| consistency | B | B matches the other version's phone order (switch at top). A's pinned bar is a pattern used only here. |
| phone experience | same | n/a (desktop). |
| accessibility | same | The switch has the same size and label. Either placement is reachable on desktop. |
| visual craft | B | A's pinned switch cuts the Subscriptions section in half, which looks cramped. B's layout is cleaner. |
| **Overall** | **A (narrow)** | Putting the scope switch next to Save protects the one-transaction task best. B is cleaner and doesn't hide the Subscriptions group. |

Task "fix one transaction without changing others": **A is a bit easier.** The switch is next to Save, so you are reminded at the moment you commit. B also works, because the switch is visible at the top without scrolling.

## Pair 3: transaction edit, phone, English

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | A | The scope switch is visible above Category. |
| hierarchy | B | Category comes first, and the Transport group with "Fuel" selected is fully shown. |
| task efficiency | A | You can turn off the default-on bulk switch without hunting for it. In B it is below the fold. |
| data presentation | B | B shows more categories above the fold, including all of Transport. |
| navigation and naming | same | Identical labels. |
| consistency | same | Same components. |
| phone experience | A | On a phone, a hidden setting that is on by default and affects many rows is a trap. |
| accessibility | A | A visible label with the switch, early in the reading order. |
| visual craft | B | Slightly less crowded at the top. |
| **Overall** | **A** | Same verdict as pair 1. |

Task "fix one transaction without changing others": **A is easier**, for the same reason as pair 1.

## Pair 4: period menu, phone, German

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | B | "Dieser Monat" and "Letzter Monat" say exactly which period you get. A bare "Monat" doesn't say which month. |
| hierarchy | same | Same menu position and same check on "Seit Jahresbeginn". |
| task efficiency | B | Last month is one tap. With "Monat" you pick it and then presumably step back a month. |
| data presentation | same | The chart and total underneath are unchanged. |
| navigation and naming | B | Specific, self-explanatory labels. |
| consistency | same | Both menus are internally consistent. Note that across viewports each version is mixed (see the verdict). |
| phone experience | B | One less step on a small screen. The menu is still well clear of the bottom bar. |
| accessibility | B | Screen-reader users understand the labels without context. |
| visual craft | same | One extra row, still tidy. |
| **Overall** | **B** | A's only advantage is a shorter menu, which doesn't matter much. |

Task "see what I paid last month": **B is easier** (one tap on "Letzter Monat").

## Pair 5: period menu, desktop, English

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | A | "This month" and "Last month" are unambiguous. "Month" is not. |
| hierarchy | same | Identical placement. |
| task efficiency | A | Last month is one click. |
| data presentation | B | B's shorter menu covers less of the breakdown: the Transport amount 1,549.22 € stays visible. |
| navigation and naming | A | Clearer labels. |
| consistency | same | Each version is internally fine. |
| phone experience | same | n/a. |
| accessibility | A | Labels can be understood on their own. |
| visual craft | same | Equivalent. |
| **Overall** | **A** | B's only advantage is covering one less row of data. |

Task "see what I paid last month": **A is easier** (one click on "Last month").

## Across pairs

Neither version is consistent as a set. Each one has the better design on one viewport and the worse one on the other:
- **Version A:** the switch is visible on phone and next to Save on desktop (good on both). The period menu has explicit months on desktop but only "Monat" on phone.
- **Version B:** the switch is at the top on desktop but hidden below the fold on phone. The period menu has explicit months on phone but only "Month" on desktop.

Version A works slightly better as a whole, because its edit dialog is safe on every viewport. The edit dialog is where a wrong save does damage across many transactions. Even so, neither version gives the same experience on phone and desktop.

The ideal combination:
- Edit dialog: the switch always visible, preferably next to Save. Consider making it off by default.
- Period menu: "This month" and "Last month" on every viewport.

## Short overall verdict
- Pair 1 (edit, phone de): **A**
- Pair 2 (edit, desk en): **A (narrow)**
- Pair 3 (edit, phone en): **A**
- Pair 4 (period, phone de): **B**
- Pair 5 (period, desk en): **A**
- Whole set: A is slightly ahead, but both versions treat phone and desktop differently.
