# Judge 8: blind comparison

Two designs run through pairs 01–05:
- **"List + back" design**: 01-B, 02-A, 03-A, 04-B, 05-B. Settings opens on a list of 8 sections with subtitles and chevrons. Each section page has a "< SETTINGS / EINSTELLUNGEN" back link and the section name as the page title.
- **"Tabs" design**: 01-A, 02-B, 03-B, 04-A, 05-A. Settings opens straight into "Bank & import" under a horizontally scrolling tab strip. Section pages keep the "Settings" title and show the tab strip scrolled to the active tab.

Below the header, the section content looks the same in both designs. **Pair 06 (desktop Bank & import): A and B are pixel-identical (same md5).**

## Pair 01: landing, phone, DE (A = tabs, B = list)

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | B | The list shows that Einstellungen holds 8 areas. A drops you into Bankverbindungen without saying so. |
| hierarchy | B | One level of 8 rows, each with a title and subtitle. A stacks a title, tabs, 2 large cards, nested buttons and a 90-day text block. |
| task efficiency | A | In A, "Jetzt abrufen" (sync now) and the account toggles need 0 taps. Reaching any other section is about as fast in either design. |
| data presentation | B | B's subtitles ("Passkeys, Anmeldung und Handys mit Fingerabdruck") say what each section contains. A shows only 2.5 tab labels. |
| navigation and naming | B | All 8 sections are visible at once. In A, "Hinweise & Gehalt" is cut off at the right edge and 5 sections are hidden. |
| consistency | A | A's tabs match the desktop tab bar in pair 06. |
| phone experience | B | B fits in one screen (862 px). A is a 1767 px scroll with buttons that wrap onto 3 rows. |
| accessibility | B | B has large full-width tap rows. A relies on a horizontal-scroll tab strip that is hard to discover and cuts labels. |
| visual craft | B | B is calm and evenly spaced. A is dense, and in German its long help paragraph and wrapped buttons look crowded. |

**Winner: B.** The loser (A) is better in one important way: the most common action, sync now, is one tap closer.

## Pair 02: landing, phone, EN (A = list, B = tabs)

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | A | The list of 8 sections with subtitles explains what Settings is. |
| hierarchy | A | The list is flat. B nests cards inside cards on first view. |
| task efficiency | B | B shows Sync now and "I logged in to my bank" right away. |
| data presentation | A | A's subtitles ("Figures for the Investments page") help the reader. B's tab strip shows only 3 names. |
| navigation and naming | A | Every section is named and in view. In B, the 4th tab is clipped, so 5 of 8 sections are hidden. |
| consistency | B | B matches the desktop tabs. |
| phone experience | A | A fits on one screen (844 px). B is 1636 px long. |
| accessibility | A | A has large tap targets and no horizontal scroll to discover. |
| visual craft | A | A is cleaner. B is fine in English, with fewer wraps than in German. |

**Winner: A.** The loser (B) gives quicker access to sync and stays closer to desktop.

## Pair 03: Security section, phone, DE (A = back link, B = tabs)

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | A | A's page title is "Sicherheit". B's title is the generic "Einstellungen", and the section name is only an underlined tab. |
| hierarchy | A | In A, the back link, the title and then the cards read top-down. |
| task efficiency | B | In B, you can move to the neighbouring "Konto & Darstellung" or "Export & Datenschutz" in one tap. A needs back plus a choice. |
| data presentation | same | The Passkeys, Handys, Anmeldung and Angemeldete Geräte cards are identical. |
| navigation and naming | A | A has a clear back link to the overview. B's neighbouring tabs are clipped ("ort & Datenschutz", "Konto & Darstellu"). |
| consistency | B | B uses the same tab model as desktop. |
| phone experience | A | A uses the standard drill-in pattern for phones, with no clipped strip. |
| accessibility | A | A's back link is a predictable target. B's clipped tab labels are hard to read and to discover. |
| visual craft | A | B's clipped words at both edges look unfinished. |

**Winner: A.** The loser (B) is faster for moving sideways between sections.

## Pair 04: Backups section, phone, EN (A = tabs, B = back link)

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | B | B's page title is "Backups". |
| hierarchy | B | In B, the title and back link come first and then the content, about 30 px higher. A has the page title "Settings", a tab and a card all saying Backups. |
| task efficiency | A | A gives one-tap access to Investments and Export & privacy. |
| data presentation | same | The Smart Recycle picker, timeline, steppers and backup list are identical. |
| navigation and naming | B | B has a clear path back to all sections. A's strip shows a stray clipped "y" and needs horizontal scrolling. |
| consistency | A | A matches the desktop tabs. |
| phone experience | B | B's content starts higher and has no horizontal scroller. |
| accessibility | B | B has no clipped labels. |
| visual craft | B | B is cleaner at the top. Both say "Click a filled one", which is desktop wording on a phone. |

**Winner: B.** The loser (A) is better for moving sideways between sections.

## Pair 05: Categories section, phone, DE (A = tabs, B = back link)

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | B | B's page title is "Kategorien". |
| hierarchy | B | B has a single clear header. |
| task efficiency | A | In A, "Bank & Import" and "Hinweise & Gehalt" are one tap away. |
| data presentation | same | The Automatisch zuordnen, Regeln, Gelernte Händler and Eigene Gruppen cards are identical. |
| navigation and naming | B | B has an explicit back link. A's "Hinweise & Gehalt" is cut off and 5 sections are hidden off-screen. |
| consistency | A | A matches desktop. |
| phone experience | B | B is about 48 px shorter and has no horizontal scroll. |
| accessibility | B | B has no clipped labels. |
| visual craft | B | B's header is cleaner. |

**Winner: B.** The loser (A) is better for moving sideways between sections.

## Pair 06: Bank & import, desktop, EN

Every rubric line is **same**, because the two images are pixel-identical. The page has a left sidebar, a full tab bar with all 8 sections visible and the Bank & import content. **Result: tie.**

## Across pairs

The "list + back" design (01-B, 02-A, 03-A, 04-B, 05-B) works better together on a phone:
- Opening Settings shows a short map of every area.
- Each section page is titled with its own name.
- A back link always returns to the map.
- The flow is predictable: list, then section, then back.

The "tabs" design (01-A, 02-B, 03-B, 04-A, 05-A) keeps one model on phone and desktop and allows one-tap moves to neighbouring sections. On a 390 px screen, though, the strip hides 5 of 8 sections and clips labels at both edges. It also turns the landing into a long Bank & import page. The cost of "list + back" is one extra tap to move between sections, and that it differs from the desktop tabs. That trade-off is acceptable on a phone. Desktop is unaffected in this set (pair 06 is identical).

## Overall verdict

- Pair 01: **B**
- Pair 02: **A**
- Pair 03: **A**
- Pair 04: **B**
- Pair 05: **B**
- Pair 06: **tie** (identical images)
- As a set: the list + back design is better.
