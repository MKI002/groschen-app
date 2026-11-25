# Judge 4b: Transactions, edit sheet (Shell, -56.30 EUR)

What the pixel diff shows: in all four pairs the only change is in the bottom area of the sheet (desk y 814-866, phone y 658-827). Everything else is pixel-identical. The change is where the merchant-wide switch "Use this category for every transaction from this merchant" / "Diese Kategorie für alle Umsätze dieses Händlers verwenden" sits. Where it is visible, the switch is **on**: gold track, knob on the right.

- **Pinned switch** (pair01 B, pair02 A, pair03 A, pair04 B): the switch is in a fixed footer above Save. A full-width rule separates it from the scrolling category list, and an inset rule separates it from "Everything with Shell" and Save.
- **Inline switch** (pair01 A, pair02 B, pair03 B, pair04 A): on desktop there is no rule above the switch, so it sits right under the "SUBSCRIPTIONS"/"ABOS" heading and reads like part of that category group. On phone the switch is not in the visible sheet at all: it scrolls with the list and is below the fold, so the footer shows only "Alles mit Shell/Everything with Shell" and Save.

**The task: fix the category of this one transaction without changing the other Shell transactions.** The switch is on by default. That means Save will recategorise every Shell transaction unless the user turns the switch off. The pinned version shows this switch and its state right next to Save on every screen size, so the user sees the side effect before committing. The inline version hides the switch on phone, where a user who picks a chip and taps Save would change all Shell transactions without ever seeing the switch. On desktop it is visible, but it looks like a Subscriptions setting rather than a setting about this save. **Pinned is clearly easier and safer in every pair.** The flip side is that the user has to know to turn a pre-set switch off, and neither version says how many transactions it affects.

## pair01: phone, DE (A = inline, B = pinned)

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | B | The "für alle Umsätze dieses Händlers" switch next to Speichern says what saving will do. In A this is invisible. |
| hierarchy | B | Switch then Speichern reads as one decision. A's footer has no context for Speichern. |
| task efficiency | B | One glance to check or turn off the switch. In A you have to scroll to the end of a long chip list to find it. |
| data presentation | A | A shows more of MOBILITÄT, including the selected "Tanken" chip. In B the pinned panel hides it. |
| navigation and naming | same | Same labels: "Alles mit Shell", "Kategorie suchen". |
| consistency | B | Matches desktop, where the switch is always shown with the footer. |
| phone experience | B | The scope control stays reachable without scrolling. The cost is a shorter list viewport (about 100 px). |
| accessibility | B | A screen-reader or keyboard user meets the switch right before Save. In A it is far down the list. |
| visual craft | same | Both are tidy. B adds a clean separator, A is less crowded. |
| **Overall** | **B** | The loser is better only in list space: A keeps the selected chip in view. |

## pair02: desktop, EN (A = pinned, B = inline)

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | A | The rule above the switch makes it a property of this Save, not of the "SUBSCRIPTIONS" group. |
| hierarchy | A | A has three clear tiers (list, scope switch, actions). B's switch runs straight on from the SUBSCRIPTIONS heading. |
| task efficiency | same | The switch is visible in both. One click either way. |
| data presentation | same | Same chips, and "Fuel" is selected in both. |
| navigation and naming | same | Same text. |
| consistency | A | Same footer structure as the phone footer (pair03 A). |
| phone experience | same | n/a (desktop) |
| accessibility | A | The grouping is clearer. B's layout suggests the wrong relationship between the switch and the heading above it. |
| visual craft | A | B has the "SUBSCRIPTIONS" label stuck to the switch row with no gap, which looks like a clipping error. |
| **Overall** | **A** | Small but real. B is not better anywhere important. |

## pair03: phone, EN (A = pinned, B = inline)

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | A | "Use this category for every transaction from this merchant" (on) is shown above Save. B shows no hint that saving affects all Shell rows. |
| hierarchy | A | Scope, then commit. |
| task efficiency | A | Turning it off takes one tap. In B the user has to scroll past Shopping, Insurance and Subscriptions. |
| data presentation | B | B shows the full TRANSPORT group. A cuts it after the "Fuel" chip (still visible). |
| navigation and naming | same | Same labels. |
| consistency | A | Matches the desktop footer. |
| phone experience | A | The safety control is always in reach. B only gains list height. |
| accessibility | A | The switch comes right before Save in reading order. |
| visual craft | same | Both are clean. B is airier, A is well separated. |
| **Overall** | **A** | B is better only in how much of the list fits. |

## pair04: desktop, DE (A = inline, B = pinned)

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | B | The rule above the switch separates it from the "ABOS" group. In A the switch reads like an Abos item. |
| hierarchy | B | Clear footer tiers. |
| task efficiency | same | The switch is visible in both. |
| data presentation | same | Identical chips, and "Tanken" is selected. |
| navigation and naming | same | Same text. |
| consistency | B | Consistent with the phone footer. |
| phone experience | same | n/a |
| accessibility | B | Clearer grouping. |
| visual craft | B | A's "ABOS" heading runs into the switch row. |
| **Overall** | **B** | A is not better anywhere important. |

## Across pairs
The pinned version (01B, 02A, 03A, 04B) holds together better as a set. On every screen size and in both languages, the footer has the same three-part structure (scope switch, then "Everything with Shell", then Save), so moving between phone and desktop changes nothing about where the decision lives. The inline version behaves differently by device: on desktop it is visible but misgrouped, and on phone it is hidden below the fold. That inconsistency is risky because the switch defaults to on.

**Overall verdict:** pair01 B · pair02 A · pair03 A · pair04 B. In every pair the winner is the pinned-switch version. It is the easier and safer one for changing a single transaction, because the pre-enabled merchant-wide switch is visible next to Save. The loser is only better in list space on phone: it shows more chips, including the selected one in pair01.
