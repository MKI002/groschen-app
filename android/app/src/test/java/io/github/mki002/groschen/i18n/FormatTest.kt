package io.github.mki002.groschen.i18n

import java.time.LocalDate
import kotlin.test.Test
import kotlin.test.assertEquals

class FormatTest {
    private val today = LocalDate.of(2026, 11, 2)
    private fun de(hidden: Boolean = false) = Fmt(Lang.DE, "DE", "EUR", hidden) { today }
    private fun en(country: String = "DE", currency: String = "EUR") = Fmt(Lang.EN, country, currency, false) { today }

    @Test
    fun `the euro sign follows the amount, in English too`() {
        assertEquals("4.271,93\u00a0€", de().money(4271.93))
        assertEquals("4.271,93\u00a0€", en().money(4271.93))
        assertEquals("−12,50\u00a0€", de().money(-12.5))
        assertEquals("+12,50\u00a0€", de().money(12.5, signed = true))
    }

    @Test
    fun `hidden amounts keep their shape with nines`() {
        assertEquals("9.999,99\u00a0€", de(hidden = true).money(1235.34))
        assertEquals("−99,99\u00a0€", de(hidden = true).money(-12.5))
        val parts = de(hidden = true).moneyParts(1235.34)
        assertEquals("", parts.before)
        assertEquals("9.999,99", parts.number)
        assertEquals("\u00a0€", parts.after)
    }

    @Test
    fun `other home countries write their own way`() {
        assertEquals("$1,234.50", en("US", "USD").money(1234.5))
        // Austria groups thousands with a space (as Intl does on the web); the € still follows.
        val at = Fmt(Lang.EN, "AT", "EUR", false) { today }.money(1234.5)
        assertEquals("234,50\u00a0€", at.takeLast(8))
        assertEquals('1', at.first())
    }

    @Test
    fun `days close by have words`() {
        val f = de()
        assertEquals("heute", f.relDay("2026-11-02"))
        assertEquals("morgen", f.relDay("2026-11-03"))
        assertEquals("in 5 Tagen", f.relDay("2026-11-07"))
        assertEquals("Gestern", f.dayHeader("2026-11-01"))
        assertEquals("2. Nov. 2026", f.date("2026-11-02"))
        assertEquals("2 Nov 2026", en().date("2026-11-02"))
        assertEquals("Nov 2, 2026", en("US", "USD").date("2026-11-02"))
    }

    @Test
    fun `percent and spans`() {
        assertEquals("+13,7\u00a0%", de().pct(0.137, signed = true))
        assertEquals("13.7%", en("US", "USD").pct(0.137))
        assertEquals("13,7%", en().pct(0.137))
        assertEquals("4 Monaten", de().span(122))
        assertEquals("2 weeks", en().span(14))
    }
}
