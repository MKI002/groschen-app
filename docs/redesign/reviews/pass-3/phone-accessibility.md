# Groschen, pass 3: phone and accessibility review

Reviewer role: phone experience and accessibility. I looked at every `phone.de` screenshot in full, plus `phone.en` for 02, 11, 20 and 41, and `desk.en` for 01 and 17 as reference. Sizes are estimated from the 390 px capture width, where 1 image px is 1 CSS px. Contrast ratios were measured with PIL on the PNGs: for each element I took the most common colour in its box as the background and the most contrasting pixel as the foreground, then applied the WCAG 2.x formula.

Only lines 7 (phone experience) and 8 (accessibility) are scored. Line 6 (consistency) and line 9 (visual craft) are scored only where they affect phone use. The other lines get "-".

## Measured contrast (dark theme)

| Element (screenshot) | fg / bg | Ratio | WCAG |
|---|---|---|---|
| Secondary grey text, e.g. "Im Schnitt 3.353,86 € pro Monat" (01-overview.phone.de), row subtitles "DAZN Abonnement" (02-transactions.phone.de), "monatlich · am 1." (11-recurring-list.phone.de) | #8d919a / #121418 | 5.84 | AA pass |
| Same grey on raised card #171a1f, e.g. 20-settings-bank.phone.de help paragraph | #8d919a / #171a1f | 5.52 | AA pass |
| Tertiary grey: "SPARQUOTE" label, search placeholder, "22,3 %" shares, "Mit zwei Fingern vergrößern" | #7e838c / #121418 | 4.84 | AA pass, little margin |
| Chart axis tick "Jan" (09-drill-group.phone.de, about 9 px) | #787d84 / #121418 | 4.45 | fails AA 4.5 at a very small size |
| Inactive bottom-nav label "Umsätze" (01-overview.phone.de) | #8d919a / #0d0e11 | 6.11 | pass |
| Disabled primary buttons: "Anmelden" (42-login), "Weiter" (40-wizard-account), "Speichern" (08 dialog), "Fertig, Abruf starten" (30 dialog) | #141312 / #6e6145 | about 3.0 | below 4.5. Allowed for disabled controls, but they read as "maybe enabled" |
| Disabled "+ Regel hinzufügen" (21-settings-categories.phone.de) | #747679 / #14161b | 3.97 | low |
| Input border at rest, password field (42-login.phone.de) | #26282b / #0e1013 | 1.29 | **fails 1.4.11** (needs 3:1); the field outline is barely visible |
| Focus ring, username field (42-login.phone.de) | #544932 / #0e1013 | 2.16 | **fails 3:1**; weak focus indicator |
| Month heatmap cell "−1,9" (17-inv-analysis.phone.de) | #ecedef / #5f3534 | 8.76 | pass |

Overall, body and secondary text contrast is solid. The weak points are non-text contrast (input outlines and focus ring) and the tiny chart ticks.

## Touch-target estimates (390 px wide)

| Element | Approx. size | Verdict |
|---|---|---|
| Bottom nav items (all screens) | about 97 × 60 | good |
| Header eye and gear buttons | about 34 × 34 | below 44; acceptable but tight |
| Sync pill "gerade eben" | about 112 × 32 | ok width, short |
| Hint dismiss "×" (01-overview.phone.de "Einen Blick wert") | about 28 × 28 | too small |
| Filter chips "Alle / Zu prüfen / Ohne Kategorie / Einnahmen" (02) | about 30 px tall | below 44 |
| Category chips in edit dialog (05) and group dialog (08) | about 28–30 px tall, 6 px gaps | small and dense, easy to mis-tap |
| Stepper "−" and "+" (24-settings-backup.phone.de) | about 28 × 28 | too small |
| "× Nicht zählen" (18-inv-payments.phone.de) | about 90 × 20 text-only | too small, no button shape |
| Chip remove "×" in "Alex Beispiel ×" (21) | about 12 px glyph | too small |
| Calendar day cells (12) | about 42 × 56 | good |
| Spending year-heatmap squares (07) | about 8 × 8 | not usable as tap targets ("Klick zeigt die Umsätze des Tages") |
| Orbit planets (13) | 10–40 px, overlapping | not usable for tapping |
| List rows (02, 11) | 64–80 px tall, full width | good |

---

## 01-overview (phone.de, phone.en, desk.en)

Scores: 1 - · 2 - · 3 - · 4 - · 5 - · 6 - · **7: 8** (01-overview.phone.de: "Frei verfügbar bis zum Gehalt" hero fits the width with large numerals and a readable payday timeline) · **8: 7** (01-overview.phone.de: secondary text at 5.84:1 is fine, but the hint dismiss "×" is 28 px) · 9 -

- `keep`: 01-overview.phone.de, single-column card stack, hero first, four-item bottom nav with a clear gold active state. Good thumb reach for primary navigation.
- `keep`: 01-overview.phone.de, Sankey "Wohin das Geld geflossen ist" adapts to a vertical layout that fits 390 px; labels sit right-aligned with values. The text is about 11 px but readable (5.76:1).
- 01-overview.phone.de, "Einen Blick wert" dismiss buttons "×", about 28 × 28 px, sit on their own line below the "Zeigen" button and add about 40 px of dead space per hint. **Cosmetic, slows a task.** Make them 44 px targets and put them on the same row as the action button.
- 01-overview.phone.de, payday timeline dots, about 6 px. They are decorative on phone; the "14 Zahlungen kommen noch · 2.597,40 € ›" link is the real target (about 30 px tall). Fine.
- 01-overview.desk.en vs phone: the desktop "Worth a look" rows have no dismiss "×" while phone has one. **Cosmetic.**
- "Zeig auf ein Band, um ihm zu folgen; Klick zeigt die Umsätze" (01-overview.phone.de): this is pointer wording on a touch screen. **Cosmetic.** On phone, say "Tippe auf ein Band". The same issue appears on 07 ("Klick zeigt die Umsätze des Tages"), 11 ("Ein Klick zeigt die ganze Geschichte"), 13, 15 and 18.

## 02-transactions / 03-review / 04-filtered / 06-empty

Scores: **7: 7** (02-transactions.phone.de: rows of 64–80 px with logo, two-line text and a right-aligned amount read well, but filter chips are about 30 px tall and the search placeholder is truncated) · **8: 7** (02-transactions.phone.de: date headers and subtitles measure 5.84:1; the "Hofladen Sonnenfeld" uncategorized rows are marked by colour and also by an "Ohne Kategorie" chip, so the state is not colour-only) · 6: 6 (03-transactions-review.phone.de: the "Zu prüfen 39" badge disagrees with "8 Umsätze" in the summary line)

- 02-transactions.phone.de, search placeholder "Händler, Verwendungszweck, Kategorie oder Betr…" is cut off. The EN version "Search merchant, purpose, category or amount" just fits. **Cosmetic.** Shorten the DE text to "Suchen: Händler, Zweck, Betrag…".
- 02-transactions.phone.de, summary line "Jan – Okt 2026 · 297 Umsätze · 42.057,91 € rein / 31.970,76 € raus" wraps so that "raus" lands alone on a second line, with no separator. **Cosmetic.** Use a two-line layout with in and out together, or make it a small stat row.
- 02-transactions.phone.de, "Nordlicht Software / zählt für November 2026 · LOH…" subtitle is truncated with no way to expand it except opening the row. The same happens with "Geld zurück für About You, 3. Sept…" (02-transactions.phone.de, lower section). **Cosmetic.**
- `keep`: 02-transactions.phone.de, strikethrough "−34,99 €" with "Komplett zurückbekommen" for a fully refunded row. It is clear and does not rely on colour alone.
- 03-transactions-review.phone.de: the period button says "Jan – Okt 2026" while the summary says "Alle Zeiträume · 8 Umsätze", and the chip says "Zu prüfen 39". There are three conflicting signals about the scope. **Slows a task.** When the review view ignores the period, disable or relabel the period button. Make the badge count match the list.
- 04-transactions-filtered.phone.de: `keep` the inline "×" clear in the search field (about 28 px; could be larger) and the gold "Filter zurücksetzen" link.
- 06-transactions-empty.phone.de: about 110 px of empty space sits between the top bar and the "Umsätze" title, so the layout jumps compared with 02. The same top offset appears on 13-recurring-orbit.phone.de (about 24 px) and 23-settings-depot.phone.de (about 26 px). **Cosmetic** (layout instability). The empty state itself, "Keine passenden Umsätze" with advice, is good: `keep`.
- 02-transactions.phone.de: the "Filter" control is text plus icon with no border (contrast 6.0:1), next to a bordered "Neueste zuerst" select. The two adjacent controls have inconsistent affordances. **Cosmetic.**

## 05-transactions-edit (dialog)

Scores: **7: 6** (05-transactions-edit.phone.de: a centered modal at nearly full height instead of a bottom sheet; the category chips are about 28 px with 6 px gaps) · **8: 6** (05-transactions-edit.phone.de: chips are told apart by a 6 px coloured dot plus text, which is fine, but the selected state "Tanken" is a gold fill only, with no checkmark)

- 05-transactions-edit.phone.de, category chip grid: dense targets of about 28 px make wrong taps likely. **Slows a task.** On phone, use 36–40 px chips or a list with radio rows. Add a ✓ icon to the selected chip.
- `keep`: 05-transactions-edit.phone.de, "Speichern" sits in a sticky footer at the bottom of the screen, in good thumb reach, next to "Alles mit Shell ›".
- 05-transactions-edit.phone.de, the pencil badge on the merchant logo is about 18 px. **Cosmetic.**
- The "×" close button is about 34 px at the top-right corner, the hardest thumb zone. A swipe-down sheet would fix this. **Cosmetic.**

## 07-spending / 33-period-menu

Scores: **7: 7** (07-spending.phone.de: the donut and ranked category bars fit well, but the "Dein Jahr in Tagen" heatmap squares are about 8 px and July–December are clipped) · **8: 6** (07-spending.phone.de: the heatmap encodes values by colour only, from violet to yellow, with no text alternative per cell)

- 07-spending.phone.de, "Dein Jahr in Tagen": cells are about 8 × 8 px with 2 px gaps, and the grid shows only Jan–Jun with no visible scroll affordance. The copy says "Klick zeigt die Umsätze des Tages", which is not achievable by touch. **Slows a task.** On phone, show a per-month grid with 40 px cells, or one month at a time with arrows, the way the 12 calendar does.
- 07-spending.phone.de, "Persönliches · mehr Erstattungen…" row label is truncated. **Cosmetic.**
- `keep`: 07-spending.phone.de, the three summary lines under the heatmap ("185 Tage ohne Ausgaben", etc.) give a text alternative to the chart.
- 33-period-menu.phone.de: menu items are about 37 px tall, the current item is marked by a ✓ and gold text (not colour-only), and the menu anchors under its button. `keep`. Items could be 44 px.

## 08-spending-group-dialog

Scores: **7: 6** (08-spending-group-dialog.phone.de: about 30 category chips of about 30 px stacked in a scrolling modal) · **8: 6** (08-spending-group-dialog.phone.de: the disabled "Speichern" is gold at about 3.0:1 and looks almost enabled; the symbol picker icons are about 32 px with no labels)

- 08-spending-group-dialog.phone.de, symbol picker (car, house, plane, tag): icon-only buttons with no visible label. They need aria-labels; I cannot verify that from the screenshot. **Cosmetic.**
- 08-spending-group-dialog.phone.de, disabled "Speichern": add a hint saying why it is disabled (the name is missing). **Slows a task.**

## 09-drill-group / 10-drill-category

Scores: **7: 7** (09-drill-group.phone.de: ranked merchant and category bars with value and percent fit cleanly) · **8: 6** (09-drill-group.phone.de: bar chart axis ticks are about 9 px at 4.45:1)

- 09-drill-group.phone.de, the "Pro Monat" chart axis labels and "Durchschnitt 348 €" are about 9 px. **Cosmetic.** Use at least 11 px.
- 09-drill-group.phone.de, the category filter chips "Alle / Lebensmittel 43 / Restaurants & Cafés 36…" wrap onto three lines. They are usable, but they push the list down. **Cosmetic.**
- 10-drill-category.phone.de: the drill shows "Einnahmen · Erhalten 0,00 € · 0 Umsätze" while 01 shows 33.538,60 € income for the same period. **Blocks a task** (if this is the income drill from the overview), or else it is a confusing empty state. Check the drill target.
- `keep`: 10-drill-category.phone.de, back link "‹ EINNAHMEN" above the title gives a clear way back on phone.

## 11-recurring-list / 12-recurring-calendar / 13-recurring-orbit

Scores: **7: 7** (12-recurring-calendar.phone.de: 7-column month grid with about 42 × 56 px day cells, good for touch) · **8: 6** (12-recurring-calendar.phone.de: amounts inside cells, such as "−2.150 €", are about 8 px; payment types are told apart by coloured dots only, with a legend)

- 11-recurring-list.phone.de and phone.en: "Stadtwerke Muench…" is truncated because the "+7,00 €" badge takes the space. "Hausverwaltung Kr…" in "Als Nächstes" is truncated in both languages. **Cosmetic.** Move change badges under the name on phone.
- `keep`: 11-recurring-list.phone.de, the "≈ 10,75 € im Monat" normalisation under yearly items, and the "Neu" and "Wieder da" badges with text.
- 12-recurring-calendar.phone.de, cell dots: orange "Bezahlt" vs teal "Dauerauftrag" vs green "Gehalt" are told apart by hue only, at about 5 px. **Cosmetic (accessibility).** The "Tag für Tag" list below is a good text alternative: `keep`.
- 13-recurring-orbit.phone.de: the orbit shrinks to about 250 px wide. Planets overlap each other and the "1.407 € im Monat" centre label, and the labels "HUK-Coburg", "Telekom" and "Hausverwaltung Kr…" collide or truncate. Tapping individual planets is not realistic. **Slows a task** (the view becomes decorative). On phone, hide the Orbit option or add a list under it.
- 11/12/13 phone.de, the "Liste / Kalender / Orbit" segmented control: about 30 px tall. `keep` the pattern; enlarge the targets.

## 14-networth

Scores: **7: 8** (14-networth.phone.de: the "Stand heute 44.931,92 €" hero, line chart and account cards stack cleanly; the Sparplan coin rows fit 12 months) · **8: 7** (14-networth.phone.de: chart ticks are about 9 px; percent labels such as "17 %" are gold at 9.5:1)

- `keep`: 14-networth.phone.de, the dashed "Konto hinzufügen" card, which is a full-width touch target.
- 14-networth.phone.de, "Vanguard FTSE All-W…" and "iShares Core MSCI EM…" are truncated by the "LÄUFT" badge. **Cosmetic.**

## 15-investments / 32-hidden-investments / 19-etf

Scores: **7: 8** (15-investments.phone.de: the "Mit zwei Fingern vergrößern" hint shows the chart supports touch zoom, and the holdings cards are full-width targets) · **8: 7** (15-investments.phone.de: the "Wert ohne Einzahlungen" vs "Gewinn und Verlust" legend uses colour plus position; small text such as "85 % des Depots" is 5.24:1)

- `keep`: 15-investments.phone.de and 19-etf.phone.de, "Mit zwei Fingern vergrößern", a phone-specific gesture hint.
- 15-investments.phone.de, the sub-tab row "Depot · Analyse · Prognose · Einzahlungen" just fits in DE. Any longer string will overflow. **Cosmetic, watch.**
- 19-etf.phone.de: the page has a second tab row, "Überblick / Analyse / Prognose / Fakten", under the depot tab row, which repeats "Analyse / Prognose". On phone, it is unclear which level you are in. **Slows a task.**
- 19-etf.phone.de, the "1M 3M 6M 1J Max" range buttons are about 28 px tall. **Cosmetic.**
- 32-hidden-investments.phone.de: the blur covers values and the Y-axis ticks, and the active eye button turns gold. `keep`. Percentages stay visible, which is reasonable.

## 16-inv-forecast

Scores: **7: 7** (16-inv-forecast.phone.de: the 2 × 2 assumption cards fit; "Auf den Graphen tippen oder ziehen" uses touch wording correctly) · **8: 6** (16-inv-forecast.phone.de: the "eingezahlt" marker label sits above the range bar, detached from its tick)

- `keep`: 16-inv-forecast.phone.de, "Auf den Graphen tippen oder ziehen, um jeden Monat anzusehen", the correct touch wording. Other screens should copy it.
- 16-inv-forecast.phone.de, horizon buttons "1J 2J 3J 5J 10J 20J 30J": 7 buttons of about 34 × 30 px in one row. Tight but fine.

## 17-inv-analysis

Scores: **7: 5** (17-inv-analysis.phone.de: the "Monatsrenditen" heatmap shows Jan–Jun only; Jul–Oct are cut off at the right edge with no scroll hint, while the text says "5 von 10 Monaten im Plus") · **8: 6** (17-inv-analysis.phone.de: the legend "Umrandet: der beste und der schlechteste Monat" is drawn with an empty checkbox glyph that looks interactive)

- 17-inv-analysis.phone.de, Monatsrenditen grid: the four best months (+7,9, +5,3, +1,3, −0,9 on 17-inv-analysis.desk.en) are invisible on phone. **Slows a task.** Wrap to two rows of six or use a 4 × 3 grid on phone.
- 17-inv-analysis.phone.de, the "☐ Umrandet…" legend looks like a form checkbox. **Cosmetic.** Use an outlined swatch instead.
- `keep`: 17-inv-analysis.phone.de, month cells carry the signed number as text, not colour only (8.76:1).

## 18-inv-payments

Scores: **7: 6** (18-inv-payments.phone.de: the "× Nicht zählen" text buttons are about 20 px tall and sit next to rows) · **8: 6** (18-inv-payments.phone.de: the ISIN subtitle "Sparplan IE00BKM4GZ66 iShs …" is truncated)

- 18-inv-payments.phone.de, "× Nicht zählen": a small, borderless destructive-ish action. **Slows a task.** Give it a button shape of at least 36 px, or a swipe action.
- `keep`: 18-inv-payments.phone.de, month accordion rows of about 44 px with a chevron.

## Settings 20–27 and 30

Scores: **7: 7** (20-settings-bank.phone.de: the scrollable settings tab row "Bank & Import · Kategorien · Hinweise & Gehalt…" fades at the edges, which hints at scroll, and the toggles are large at about 40 × 24) · **8: 6** (26-settings-security.phone.de: "Abmelden" next to "Safari auf iPhone", and 27-settings-account.phone.de "Quellcode", are grey text with no button shape at 5.84:1)

- 20-settings-bank.phone.de vs phone.en: the DE action buttons "Jetzt abrufen", "Ich war bei der Bank angemeldet" and "Zugangsdaten ändern" stack on 3 rows (EN fits 2), and the DE page is 131 px taller. Fine, but `keep` an eye on German length.
- 20-settings-bank.phone.de, "Anmelde-Erinnerung" segmented control "30 Tage vorher / 15 Tage vorher / 7 Tage vorher" wraps to two lines per segment. It is readable. **Cosmetic.**
- 20-settings-bank.phone.de, "FinTS · Zugang •emo ·" shows a partly masked username that looks like a rendering error. **Cosmetic.**
- 21-settings-categories.phone.de, "Kategorisierung: Abgleich nach Schreibweise (eingebautes Modell nicht gefunden)" while "Eingebautes Modell" is selected, under an "Offline" badge. This is confusing status. **Slows a task.**
- 21-settings-categories.phone.de, rule builder "Wenn [Händler] [enthält] / [z. B. ARAL] [Kategorie…]": native selects are about 32 px tall, and there are 4 controls in a 2 × 2 grid. Usable. The disabled "Regel hinzufügen" is at 3.97:1.
- 21-settings-categories.phone.de, the "×" remove on the "Alex Beispiel" chip is about 12 px. **Slows a task.**
- 22-settings-hints.phone.de: `keep` the long toggle list. Each row has a title, an explanation and a right-aligned toggle that lines up with the title.
- 22-settings-hints.phone.de, the "Automatisch / Nächster Monat / Buchungsmonat" segmented control wraps "Nächster Monat" onto two lines. **Cosmetic.**
- 24-settings-backup.phone.de, steppers "− 7 +" etc.: the −/+ buttons are about 28 px. **Slows a task.** Use 40 px.
- 24-settings-backup.phone.de, the slot visualisation labels "1 pro Woche / 1 pro Tag" do not line up with their groups, and the monthly and yearly groups have no label on phone. **Cosmetic.**
- 25-settings-privacy.phone.de, the "Protokoll zeigen" button is disabled and grey with no explanation. It can be inferred from "Keine ausgehenden Verbindungen…". **Cosmetic.**
- 26-settings-security.phone.de: `keep` the clear explanation box "Unter 127.0.0.1 gehen keine Passkeys".
- 27-settings-account.phone.de: the "Animationen: Voll / Ruhig / Aus" control respects "Bewegung reduzieren". `keep`, good accessibility practice.
- 27-settings-account.phone.de: native `<select>` elements ("Nicht gewählt", "EUR · Euro") use browser styling, which differs from the custom "Deutsch ⌄" dropdown above them. **Cosmetic** (consistency).
- 30-settings-connect-dialog.phone.de: the error "Keine Bank mit diesem Namen gefunden…" already shows while the field is empty. **Slows a task** (it reads as a failure before input). The disabled "Fertig, Abruf starten" button is at about 3.0:1. The dialog is centered with a 34 px "×" at the top-right. `keep` the clear label "Deine Bank".

## 31-hidden-overview

Scores: **7: 8** (31-hidden-overview.phone.de: the blur keeps the layout identical, so nothing jumps) · **8: 7** (31-hidden-overview.phone.de: the eye button state is shown by a gold fill and a crossed-eye icon, so it is not colour-only)

- `keep`: 31-hidden-overview.phone.de, the hidden mode is one 34 px tap away in the header on every screen.

## 40-wizard-account / 41-wizard-country / 42-login

Scores: **7: 7** (40-wizard-account.phone.de: single column, full-width inputs of about 40 px, "Weiter" at the bottom right) · **8: 5** (42-login.phone.de: input borders at rest are 1.29:1 and the focus ring is 2.16:1, both below the 3:1 non-text minimum)

- 42-login.phone.de and 40-wizard-account.phone.de, input outlines: on #0e1013 the field edges are nearly invisible (1.29:1), so the fields read as dark blobs on the card. **Slows a task** for low-vision users. Raise the border to about #5a5e66 (roughly 3:1) and the focus ring to the full gold (#ddbb74, about 9:1), 2 px wide.
- 42-login.phone.de, disabled "Anmelden" (3.06:1, muted gold) looks like a normal but dim button. **Cosmetic.**
- 41-wizard-country.phone.de vs phone.en: the DE page overflows to 854 px (the viewport is 844). The FinTS explanation paragraph uses about 17 px light grey body text, and "Überspringen, vorerst CSV-Dateien nutzen" wraps onto two centered lines above "Weiter", so the footer stacks awkwardly. **Cosmetic.** Shorten it to "Ohne Bank weiter (CSV)" and put it on the same row as "Weiter", or make it a secondary full-width button.
- 41-wizard-country.phone.de: as on 30, "Keine Bank mit diesem Namen gefunden" shows before any input. **Slows a task.**
- `keep`: 40/41/42 phone, a language switch on every first-run screen, and a progress bar of 5 segments.

---

## Top 10

1. **17-inv-analysis.phone.de, "Monatsrenditen" grid:** only Jan–Jun are visible; Jul–Oct are clipped with no scroll hint, while the text says "5 von 10 Monaten im Plus". Fix: wrap to 2 × 6 or 4 × 3 on phone. (Slows a task.)
2. **42-login.phone.de and 40-wizard-account.phone.de, inputs:** the resting border is 1.29:1 and the focus ring 2.16:1, both below the WCAG 1.4.11 3:1 minimum. Fix: use a lighter border and a 2 px full-gold focus ring. (Slows a task, accessibility.)
3. **10-drill-category.phone.de, "Einnahmen" drill:** it shows 0,00 € and 0 Umsätze, while the overview shows 33.538,60 € income for the same period. (Blocks a task if this is the income drill.)
4. **13-recurring-orbit.phone.de, orbit:** it collapses to about 250 px, and the planets and labels overlap the centre total, so it cannot be tapped. Fix: hide it on phone or add a list. (Slows a task.)
5. **07-spending.phone.de, "Dein Jahr in Tagen":** the cells are about 8 px, colour-only, Jul–Dec are clipped, and the copy promises "Klick zeigt die Umsätze des Tages". Fix: use a month-at-a-time grid with 40 px cells. (Slows a task.)
6. **05-transactions-edit.phone.de and 08-spending-group-dialog.phone.de, category chips:** they are about 28–30 px with 6 px gaps, and the selected state is a gold fill without a checkmark. Fix: use 40 px chips or radio rows and add a ✓. (Slows a task.)
7. **Small targets across settings and lists:** 24-settings-backup.phone.de steppers (28 px), 18-inv-payments.phone.de "× Nicht zählen" (20 px text-only), 01-overview.phone.de hint "×" (28 px), the 21 chip "×" (12 px), and the 26 "Abmelden" and 27 "Quellcode" text-only buttons. Fix: aim for 44 px or at least 36 px, with visible button shapes. (Slows a task.)
8. **03-transactions-review.phone.de, scope signals:** the "Jan – Okt 2026" period button, "Alle Zeiträume · 8 Umsätze" and the "Zu prüfen 39" badge conflict. Fix: make one count and one scope. (Slows a task.)
9. **30-settings-connect-dialog.phone.de and 41-wizard-country.phone.de:** "Keine Bank mit diesem Namen gefunden" shows on an empty field. Also, the DE wizard footer "Überspringen, vorerst CSV-Dateien nutzen" wraps and pushes the page past 844 px. (Slows a task.)
10. **Pointer wording on touch screens:** "Zeig auf ein Band… Klick zeigt" (01), "Klick zeigt" (07, 11, 13, 15, 18). 16-inv-forecast.phone.de already says "tippen oder ziehen", so reuse that wording. The `keep` items to preserve are the bottom nav, the "Mit zwei Fingern vergrößern" hint (15, 19), the "Animationen: Aus" option that respects reduced motion (27), the secondary text contrast of 5.5–5.8:1 throughout, and the sticky "Speichern" footer in dialogs (05). (Cosmetic.)
