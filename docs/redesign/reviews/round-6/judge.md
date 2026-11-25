# Judge 6: blind A/B comparison

I diffed every pair with PIL first, then looked closely at the regions that changed. The differences are small and local.

## Pair 01: Overview, desktop (en)
The only change is the "Saved" KPI card. A says "3,000.00 € invested · 1,991.75 € stays", which leaves out the largest (teal) segment of the bar. B adds "8,095.40 € put aside", but the text wraps onto two lines (it breaks between "put" and "aside"), the card row grows by 19 px and the chevron ends up floating.

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | same | Same layout and headings |
| hierarchy | same | KPI row reads the same |
| task efficiency | B | The full savings breakdown is readable without clicking through |
| data presentation | B | The caption covers all three bar segments and adds up to 13,087.15 €. In A the teal "put aside" segment has no label |
| navigation and naming | same | Same |
| consistency | B | The caption matches the Sankey's Invested / Put aside / Stays nodes |
| phone experience | n/a | Desktop screen |
| accessibility | B | Every colour segment has a text label, so colour is not the only cue |
| visual craft | A | Neat one-line caption. B breaks "put / aside" across lines, leaves a detached chevron and makes the cards taller with empty space in Income/Spending |

**Winner: B.** A is better only on visual tidiness of that one card.

## Pair 02: Overview, phone (de)
Same change: B adds "8.095,40 € zurückgelegt". Here it fits in the same two lines as A, so the card height does not change.

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | same | Same |
| hierarchy | same | Same |
| task efficiency | B | Full breakdown at a glance |
| data presentation | B | All three segments are labelled. A leaves out "zurückgelegt" |
| navigation and naming | same | Same |
| consistency | B | Matches the Sankey's "Zurückgelegt" node |
| phone experience | B | More information in the same space |
| accessibility | B | The teal segment gets a text label |
| visual craft | same | Both wrap to two lines cleanly |

**Winner: B.** A is not better anywhere.

## Pair 03: Transactions, desktop (en)
In B, date headers for days with a single transaction (no day total on the right), such as "TUESDAY 27 OCTOBER", "WEDNESDAY 21 OCTOBER", "FRIDAY 9 OCTOBER" and "FRIDAY 18 SEPTEMBER", are brighter, larger and less letter-spaced than the headers of multi-transaction days. The list also gets slightly taller. In A all day headers share one muted small-caps style.

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | same | Same list |
| hierarchy | A | In B, some date headers stand out at random, so the scan rhythm is uneven |
| task efficiency | A | Slightly denser, so more rows per screen |
| data presentation | A | Grouping looks uniform |
| navigation and naming | same | Same filters and tabs |
| consistency | A | One header style. B mixes two styles depending on whether a day total is shown |
| phone experience | n/a | Desktop screen |
| accessibility | same | Contrast is fine in both. B's bright headers are slightly more legible, but inconsistent |
| visual craft | A | B looks like a styling bug |

**Winner: A.** B is not better anywhere important.

## Pair 04: Transactions, phone (de)
This is the mirror of pair 03. In A, the single-transaction day headers ("DIENSTAG, 27. OKTOBER", "MITTWOCH, 21. OKTOBER", "MONTAG, 19. OKTOBER", ...) are brighter and larger than the others. In B all headers are uniform and the rows are slightly more compact.

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | same | Same |
| hierarchy | B | Uniform date headers, so amounts and merchants lead |
| task efficiency | B | Slightly more compact, so more rows per screen |
| data presentation | B | Grouping looks even |
| navigation and naming | same | Same chips and filters |
| consistency | B | One header style. A switches style for days without a total |
| phone experience | B | Tighter, cleaner list |
| accessibility | same | Comparable contrast and sizes |
| visual craft | B | A's mixed headers look accidental |

**Winner: B.** A is not better anywhere important.

## Pair 05: Settings, "Connect your bank" dialog, desktop (en)
A already shows "No bank found by that name. Type your Bankleitzahl or IBAN instead." while the search field is still empty. B shows only the helper text.

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | B | Without the contradictory error, the task is clear |
| hierarchy | B | The helper text is the only message under the field |
| task efficiency | B | No false error to read and discard |
| data presentation | same | n/a |
| navigation and naming | same | Same title and button |
| consistency | B | No error before any input, as is normal for validation |
| phone experience | n/a | Desktop screen |
| accessibility | B | No misleading status message for screen readers |
| visual craft | B | A more compact, calmer dialog |

**Winner: B.** Both enable "Done, start syncing" with no bank chosen, so this is not a difference.

## Pair 06: Setup wizard, country/bank step, phone (de)
This is the mirror of pair 05. Here B shows "Keine Bank mit diesem Namen gefunden…" under the empty "Deine Bank" field, and A does not.

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | A | No false error on the first-run screen |
| hierarchy | A | The helper text alone sits under the field |
| task efficiency | A | Nothing to misread before typing |
| data presentation | same | n/a |
| navigation and naming | same | Same buttons ("Überspringen…", "Weiter") |
| consistency | A | No validation before input |
| phone experience | A | Shorter card. B's extra error pushes the actions down |
| accessibility | A | No misleading error message |
| visual craft | A | Cleaner |

**Winner: A.** B is not better anywhere.

## Pair 07: Login, phone (de)
The only difference is the focused "Benutzername" field. A has a crisp, clearly visible gold focus ring. In B the focus border is a faint, muddy brown that is hard to tell apart from an unfocused field.

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | same | Same |
| hierarchy | A | Clear where to type first |
| task efficiency | A | The active field is obvious |
| data presentation | same | n/a |
| navigation and naming | same | Same |
| consistency | A | The gold focus matches the accent and the primary button |
| phone experience | A | The focus is visible at a glance |
| accessibility | A | A visible focus indicator. B's ring has very low contrast |
| visual craft | A | Crisper |

**Winner: A.**

## Pair 08: Login, desktop (en)
Same difference as pair 07: A has a clear gold focus ring on "Username", and B's is faint.

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | same | Same |
| hierarchy | A | The focused field stands out |
| task efficiency | A | Clear starting point |
| data presentation | same | n/a |
| navigation and naming | same | Same |
| consistency | A | The accent colour is used for focus |
| phone experience | n/a | Desktop screen |
| accessibility | A | Focus is visible. B is low contrast |
| visual craft | A | Crisper |

**Winner: A.**

## Overall verdict

| Pair | Winner |
|---|---|
| 01 Overview desk | B (complete savings breakdown; A only tidier) |
| 02 Overview phone | B |
| 03 Transactions desk | A (B has inconsistent date headers) |
| 04 Transactions phone | B (A has inconsistent date headers) |
| 05 Settings connect dialog | B (A shows an error on an empty field) |
| 06 Wizard country | A (B shows an error on an empty field) |
| 07 Login phone | A (visible focus ring) |
| 08 Login desk | A (visible focus ring) |

**Across the set: roughly a tie, and neither version holds together well.** Both have the same two defects, each on a different screen:
- **Date-header bug:** each version has inconsistent date headers on one transactions view (A on phone, B on desktop).
- **Empty-field error:** each version shows a "no bank found" error on an empty field in one place (A in the Settings dialog, B in the first-run wizard).

So moving between desktop and phone, or from onboarding to Settings, looks different in either version. What actually separates them:
- **B is better** on the core dashboard data: the savings caption is complete on both overviews.
- **A is better** on accessibility: the login focus ring is visible on both login screens.

If forced to pick, A has a very slight edge, because a visible focus indicator on the entry screen is an accessibility basic. B's savings caption is a useful completeness fix but not a blocker.
