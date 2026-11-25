# Judge 7: blind comparison

Method: I diffed each A/B pair with PIL. Every pair differs in a single line of text (in pair 06 the change also moves everything below it by 18 px). Everything else is pixel-identical. "same" means the rubric line is not touched by the change.

## Pair 01: Spending, desk, EN
Difference: the summary line under "Spending breakdown" reads "most on Housing (58%)" in A and "(58% of spending)" in B.

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | same | Card title "Spending breakdown" already sets the context |
| hierarchy | same | Same weight and position |
| task efficiency | A | "(58%)" reads faster. "of spending" is implied by the card and repeated by the 58.3% in the Housing row |
| data presentation | same | Same figure |
| navigation and naming | same | No naming change |
| consistency | A | The rows below show bare percentages. A matches them |
| phone experience | same | n/a (desk) |
| accessibility | B | Slightly more self-explanatory for screen-reader or out-of-context reading |
| visual craft | A | Shorter subtitle, less visual noise |

**Overall: A (slight).** B is better only in being a little more explicit, which matters little here.

## Pair 02: Spending, phone, DE
Difference: "das meiste für Wohnen (58 % der Ausgaben)" in A vs "(58 %)" in B.

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | same | Card "Aufteilung der Ausgaben" frames it |
| hierarchy | same | Same |
| task efficiency | B | Shorter line on a narrow screen |
| data presentation | same | Same value |
| navigation and naming | same | None |
| consistency | B | Matches the bare % in the rows below |
| phone experience | B | Less text on a phone line, though neither wraps |
| accessibility | A | Slightly more explicit |
| visual craft | B | Tighter |

**Overall: B (slight).** This is the same edit as pair 01 with the letters reversed. A's extra words are not important.

## Pair 03: Fixed costs list, desk, EN
Difference: the KPI label reads "FIXED COSTS PER MONTH" in A and "FIXED COSTS, ON AVERAGE PER MONTH" in B.

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | B | Says that 1,407.01 € is an average. The calendar shows 1,423.48 € for October, so without "on average" the two numbers look contradictory |
| hierarchy | same | Same eyebrow style |
| task efficiency | same | Negligible |
| data presentation | B | Says how the figure is computed (annual 16,884.11 / 12) |
| navigation and naming | same | — |
| consistency | B | Squares this number with the month total in the Calendar view |
| phone experience | same | n/a |
| accessibility | B | Unambiguous label |
| visual craft | A | Slightly shorter, cleaner eyebrow. Minor |

**Overall: B.** A is better only in brevity.

## Pair 04: Fixed costs list, phone, DE
Difference: "FIXKOSTEN IM SCHNITT PRO MONAT" in A vs "FIXKOSTEN PRO MONAT" in B.

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | A | "im Schnitt" says this is an average, not this month's total |
| hierarchy | same | Same |
| task efficiency | same | — |
| data presentation | A | Says how the figure is computed |
| navigation and naming | same | — |
| consistency | A | Consistent with the calendar's month figure (1.423,48 €) |
| phone experience | same | Both fit on one line |
| accessibility | A | Less ambiguous |
| visual craft | B | Marginally shorter |

**Overall: A.** This is the same edit as pair 03 with the letters reversed.

## Pair 05: Fixed costs calendar, desk, EN
Difference: the card headline reads "1,423.48 € fixed costs in October 2026 · 1,100.00 € saved" in A and "1,423.48 € fixed costs · 1,100.00 € saved" in B.

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | same | The month picker "October 2026" sits in the same row, so both are clear |
| hierarchy | B | The headline no longer competes with the month picker beside it |
| task efficiency | B | Faster to scan |
| data presentation | same | Same numbers |
| navigation and naming | same | — |
| consistency | same | — |
| phone experience | same | n/a |
| accessibility | A | The headline stands alone for a screen reader without the picker |
| visual craft | B | Removes "October 2026" from the headline, which A shows twice on one row |

**Overall: B (slight).** A is better only for out-of-context reading.

## Pair 06: Fixed costs calendar, phone, DE
Difference: "1.423,48 € Fixkosten im Oktober 2026 · 1.100,00 € gespart" in A, which wraps to two lines, vs "1.423,48 € Fixkosten · 1.100,00 € gespart" in B, which fits on one. A is 18 px taller.

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | same | The month picker sits right under the headline in both |
| hierarchy | B | A one-line headline, and the month is said once (the picker) instead of twice |
| task efficiency | B | Calendar starts higher on screen |
| data presentation | same | Same |
| navigation and naming | same | — |
| consistency | same | — |
| phone experience | B | No awkward wrap ("Oktober / 2026 · …") and 18 px less scrolling |
| accessibility | A | The headline is self-contained |
| visual craft | B | Clean single line. A's wrap breaks the date apart |

**Overall: B.** A is not better anywhere important.

## Pair 07: Investments, desk, EN
Difference: the chart legend reads "Value without deposits" in A and "Value without your pay-ins" in B.

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | same | Both convey the meaning |
| hierarchy | same | — |
| task efficiency | same | — |
| data presentation | same | Same chart |
| navigation and naming | B | Uses the term from the sidebar's "Pay-ins" page |
| consistency | B | A introduces a fourth term ("deposits") next to "paid in", "Money paid in" and "Pay-ins". B cuts the vocabulary down |
| phone experience | same | n/a |
| accessibility | same | — |
| visual craft | same | Slightly longer, still fits |

**Overall: B (slight).** A's "deposits" is a little more standard finance wording, but that is not important here.

## Pair 08: Investment analysis, desk, EN
Difference: the card title reads "Swing" in A and "Ups and downs" in B. The card shows "±17% up or down in a normal year".

| Rubric | Pick | Reason |
|---|---|---|
| clarity of purpose | B | "Ups and downs" says what the volatility card measures. "Swing" is vaguer |
| hierarchy | same | — |
| task efficiency | same | — |
| data presentation | same | — |
| navigation and naming | B | Plain-language title that matches "up or down" in the body |
| consistency | B | Echoes the card's own explanation, and the plain tone of the "Drawdown" and "Monthly returns" subtitles |
| phone experience | same | n/a |
| accessibility | B | More descriptive heading |
| visual craft | A | Shorter, punchier title. Minor |

**Overall: B.**

## Across pairs
- The letters do not map to one consistent editing approach. The "explicit" wording ("of spending", "on average") is in B for the EN pairs (01, 03) but in A for the DE pairs (02, 04). So if each letter is one build, both builds have EN and DE copy that do not match. In one, the Spending subtitle is explicit in EN and terse in DE; in the other, the fixed-cost average label is explicit in DE and not in EN. Neither set is fully coherent across locales.
- On moving between screens, the decisive item is the fixed-costs pair List -> Calendar. The list's average (1,407.01) and the calendar's October total (1,423.48) agree only if the list says it is an average (B in EN, A in DE). On the calendar, the shorter headline (B in both locales) works better because the month picker already gives the month.
- In the Investments set, the B versions (pairs 07, 08) use plainer wording that matches the nav. "pay-ins" ties to the Pay-ins page. Here B is the more coherent set.
- On balance, the B set works slightly better as a whole: it wins 5 of 8 pairs, including both calendar screens and both investment screens. Its weak point is the DE fixed-costs list label, which drops "im Schnitt".

## Overall verdict
- Pair 01 (Spending desk EN): A, slight
- Pair 02 (Spending phone DE): B, slight
- Pair 03 (Fixed costs list desk EN): B
- Pair 04 (Fixed costs list phone DE): A
- Pair 05 (Calendar desk EN): B, slight
- Pair 06 (Calendar phone DE): B
- Pair 07 (Investments desk EN): B, slight
- Pair 08 (Analysis desk EN): B
