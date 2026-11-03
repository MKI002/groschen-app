package io.github.mki002.groschen.data

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertIs
import kotlin.test.assertNull
import kotlin.test.assertTrue

class TxEntriesTest {
    private fun tx(id: Int, amount: Double, merchant: String, move: Move? = null, roundup: Boolean = false, review: Int = 0) =
        Transaction(id = id, date = "2026-10-29", amount = amount, merchant = merchant, move = move, roundup = roundup, needsReview = review)

    private val giroToExtra = { mirror: Int -> Move("Girokonto", "Extra-Konto", mirror) }

    // The day in the screenshot: two round-ups with both sides, a depot purchase and a shop.
    private val day = listOf(
        tx(1, 0.83, "Kleingeld Plus", giroToExtra(3), roundup = true),
        tx(2, 0.02, "Kleingeld Plus", giroToExtra(4), roundup = true),
        tx(3, -0.83, "Kleingeld Plus", giroToExtra(1), roundup = true),
        tx(4, -0.02, "Kleingeld Plus", giroToExtra(2), roundup = true),
        tx(5, -1000.0, "Wertpapierkauf", Move("Girokonto", "Depot", null)),
        tx(6, -8.73, "E-Center Fischer"),
    )
    private val listed = day.associateBy { it.id }

    @Test
    fun realBookingsFirstThenMovesAndOneLineOfRoundUps() {
        val entries = dayEntries(day, listed, fold = true)
        assertEquals(3, entries.size)
        assertEquals(6, assertIs<TxEntry.One>(entries[0]).item.tx.id)
        assertEquals(5, assertIs<TxEntry.One>(entries[1]).item.tx.id)
        val fold = assertIs<TxEntry.Fold>(entries[2])
        assertTrue(fold.roundup)
        // Each round-up once, shown on the side that left the Girokonto, with its other side.
        assertEquals(listOf(3, 4), fold.items.map { it.tx.id })
        assertEquals(listOf(1, 2), fold.items.map { it.other?.id })
        assertEquals(0.85, fold.sum, 1e-9)
        assertEquals("Girokonto → Extra-Konto", fold.first.route)
    }

    @Test
    fun withoutFoldingEachMoveIsOneRow() {
        val entries = dayEntries(day, listed, fold = false)
        assertEquals(listOf(6, 3, 4, 5), entries.map { assertIs<TxEntry.One>(it).item.tx.id })
    }

    @Test
    fun aSideWhoseOtherHalfIsNotLoadedStaysOnItsOwn() {
        val only = listOf(day[0])
        val entries = dayEntries(only, only.associateBy { it.id }, fold = true)
        val one = assertIs<TxEntry.One>(entries.single())
        assertNull(one.item.other)
    }

    @Test
    fun aBookingToCheckIsNeverFoldedAway() {
        val items = listOf(
            tx(3, -0.83, "Kleingeld Plus", Move("Girokonto", "Extra-Konto", null), roundup = true),
            tx(4, -0.02, "Kleingeld Plus", Move("Girokonto", "Extra-Konto", null), roundup = true, review = 1),
        )
        val entries = dayEntries(items, items.associateBy { it.id }, fold = true)
        assertEquals(2, entries.size)
        assertTrue(entries.all { it is TxEntry.One })
    }

    @Test
    fun theRouteNamesThePayeeWhereTheAccountIsUnknown() {
        assertEquals("Girokonto → Trade Republic", tx(9, -50.0, "Trade Republic", Move("Girokonto", null, null)).route)
        assertEquals("", tx(9, -5.0, "Rewe").route)
    }
}
