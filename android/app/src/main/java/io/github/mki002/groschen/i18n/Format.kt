package io.github.mki002.groschen.i18n

import java.text.DecimalFormat
import java.text.DecimalFormatSymbols
import java.text.NumberFormat
import java.time.Duration
import java.time.Instant
import java.time.LocalDate
import java.time.OffsetDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.time.temporal.ChronoUnit
import java.util.Currency
import java.util.Locale
import kotlin.math.abs

enum class Lang(val code: String) { DE("de"), EN("en") }

/** An amount split where the number starts and ends, so hidden amounts can blur just the digits. */
data class MoneyParts(val before: String, val number: String, val after: String) {
    override fun toString() = before + number + after
}

/**
 * How amounts, numbers and dates are written: the home country's way (Settings on the server),
 * words in the app's language. Like the web interface, the € always follows the amount
 * ("4.271,93 €"), in English too, and a real minus sign is used.
 *
 * While amounts are hidden, every digit of a sum becomes a 9 (1.235,34 € shows as 9.999,99 €),
 * drawn out of focus on screen.
 */
class Fmt(
    val lang: Lang,
    val country: String,
    val currency: String,
    val hidden: Boolean,
    private val today: () -> LocalDate = { LocalDate.now() },
) {
    val numberLocale: Locale = COUNTRIES[country]?.second?.let(Locale::forLanguageTag)
        ?: if (lang == Lang.DE) Locale.GERMANY else Locale.UK
    private val dateLocale: Locale = if (country.isNotEmpty()) Locale.forLanguageTag("${lang.code}-$country") else {
        if (lang == Lang.DE) Locale.GERMANY else Locale.UK
    }
    private val us = country == "US" && lang == Lang.EN

    fun moneyParts(value: Double, currency: String = this.currency, digits: Int = 2, signed: Boolean = false): MoneyParts {
        val text = if (currency == "EUR") {
            val f = DecimalFormat.getNumberInstance(numberLocale) as DecimalFormat
            f.minimumFractionDigits = digits
            f.maximumFractionDigits = digits
            f.format(value) + " €"
        } else {
            val f = NumberFormat.getCurrencyInstance(numberLocale)
            runCatching { f.currency = Currency.getInstance(currency) }
            f.minimumFractionDigits = digits.coerceAtMost(f.maximumFractionDigits)
            f.maximumFractionDigits = digits.coerceAtMost(f.maximumFractionDigits)
            f.format(value)
        }
        var s = text.replace('-', '−')
        if (signed && value > 0.0049) s = "+$s"
        val first = s.indexOfFirst(Char::isDigit)
        val last = s.indexOfLast(Char::isDigit)
        if (first < 0) return MoneyParts(s, "", "")
        var number = s.substring(first, last + 1)
        if (hidden) number = number.map { if (it.isDigit()) '9' else it }.joinToString("")
        return MoneyParts(s.substring(0, first), number, s.substring(last + 1))
    }

    fun money(value: Double?, currency: String = this.currency, digits: Int = 2, signed: Boolean = false): String =
        if (value == null) "–" else moneyParts(value, currency, digits, signed).toString()

    /** A sum Groschen explains itself with, not the user's money: stays visible while amounts are hidden. */
    fun moneyPublic(value: Double, digits: Int = 0): String =
        Fmt(lang, country, currency, hidden = false, today).money(value, digits = digits)

    fun number(value: Double, digits: Int = 2): String {
        val f = NumberFormat.getNumberInstance(numberLocale)
        f.minimumFractionDigits = digits
        f.maximumFractionDigits = digits
        return f.format(value).replace('-', '−')
    }

    fun pct(value: Double?, digits: Int = 1, signed: Boolean = false): String {
        if (value == null || value.isNaN() || value.isInfinite()) return "–"
        val n = number(value * 100, digits)
        val sign = if (signed && value > 0) "+" else ""
        return sign + n + if (lang == Lang.DE) " %" else "%"
    }

    // --- dates --------------------------------------------------------------------------------

    private fun pattern(de: String, en: String, enUs: String = en) =
        DateTimeFormatter.ofPattern(if (lang == Lang.DE) de else if (us) enUs else en, dateLocale)

    private fun parse(iso: String?): LocalDate? = iso?.takeIf { it.length >= 10 }?.let {
        runCatching { LocalDate.parse(it.substring(0, 10)) }.getOrNull()
    }

    fun date(iso: String?): String = parse(iso)?.format(pattern("d. MMM yyyy", "d MMM yyyy", "MMM d, yyyy")) ?: "–"

    fun dayMonth(iso: String?): String = parse(iso)?.format(pattern("d. MMM", "d MMM", "MMM d")) ?: "–"

    fun dayHeader(iso: String?): String {
        val d = parse(iso) ?: return "–"
        return when (ChronoUnit.DAYS.between(today(), d)) {
            0L -> strings(lang).today
            -1L -> strings(lang).yesterday
            else -> d.format(pattern("EEEE, d. MMMM", "EEEE d MMMM", "EEEE, MMMM d"))
        }.replaceFirstChar { it.titlecase(dateLocale) }
    }

    fun weekdayToday(): String =
        today().format(pattern("EEEE, d. MMMM", "EEEE d MMMM", "EEEE, MMMM d")).uppercase(dateLocale)

    fun monthName(iso: String?): String = parse(iso)?.format(pattern("LLLL", "LLLL")) ?: ""

    /** "heute", "morgen", "in 3 Tagen" for days close by, the date further out. */
    fun relDay(iso: String?): String {
        val d = parse(iso) ?: return "–"
        val s = strings(lang)
        return when (val n = ChronoUnit.DAYS.between(today(), d)) {
            0L -> s.today
            1L -> s.tomorrow
            -1L -> s.yesterday
            in 2L..30L -> s.inDays(n.toInt())
            in -30L..-2L -> s.daysAgo((-n).toInt())
            else -> date(iso)
        }
    }

    fun daysUntil(iso: String?): Int? = parse(iso)?.let { ChronoUnit.DAYS.between(today(), it).toInt() }

    /** How long ago something happened: "gerade eben", "vor 5 Min.", "gestern, 18:02". */
    fun ago(isoInstant: String?, now: Instant = Instant.now()): String {
        val s = strings(lang)
        val at = isoInstant?.let { runCatching { OffsetDateTime.parse(it).toInstant() }.getOrNull() } ?: return s.never
        val mins = Duration.between(at, now).toMinutes()
        if (mins < 1) return s.justNow
        if (mins < 60) return s.minutesAgo(mins.toInt())
        val local = at.atZone(ZoneId.systemDefault())
        val time = local.format(DateTimeFormatter.ofPattern(if (us) "h:mm a" else "HH:mm", dateLocale))
        val days = ChronoUnit.DAYS.between(local.toLocalDate(), today())
        return when (days) {
            0L -> s.todayAt(time)
            1L -> s.yesterdayAt(time)
            else -> "${date(local.toLocalDate().toString())}, $time"
        }
    }

    /** "monatlich", "alle 2 Wochen", ... */
    fun interval(name: String?): String = strings(lang).interval(name)

    /** A stretch of days the way people say it: "4 Monaten" (for "nach 4 Monaten Pause"). */
    fun span(days: Int): String {
        val s = strings(lang)
        return when {
            days < 14 -> s.spanDays(days)
            days < 60 -> s.spanWeeks((days / 7.0).let(Math::round).toInt())
            days < 730 -> s.spanMonths((days / 30.44).let(Math::round).toInt())
            else -> s.spanYears((days / 365.25).let(Math::round).toInt())
        }
    }

    fun decimalSeparator(): Char = DecimalFormatSymbols.getInstance(numberLocale).decimalSeparator

    companion object {
        /** Home country → (home currency, how numbers are written). Kept in step with the server's list. */
        val COUNTRIES: Map<String, Pair<String, String>> = mapOf(
            "DE" to ("EUR" to "de-DE"), "AT" to ("EUR" to "de-AT"), "CH" to ("CHF" to "de-CH"),
            "LI" to ("CHF" to "de-LI"), "LU" to ("EUR" to "fr-LU"), "BE" to ("EUR" to "nl-BE"),
            "NL" to ("EUR" to "nl-NL"), "FR" to ("EUR" to "fr-FR"), "IT" to ("EUR" to "it-IT"),
            "ES" to ("EUR" to "es-ES"), "PT" to ("EUR" to "pt-PT"), "IE" to ("EUR" to "en-IE"),
            "FI" to ("EUR" to "fi-FI"), "GR" to ("EUR" to "el-GR"), "EE" to ("EUR" to "et-EE"),
            "LV" to ("EUR" to "lv-LV"), "LT" to ("EUR" to "lt-LT"), "SK" to ("EUR" to "sk-SK"),
            "SI" to ("EUR" to "sl-SI"), "HR" to ("EUR" to "hr-HR"), "BG" to ("EUR" to "bg-BG"),
            "MT" to ("EUR" to "en-MT"), "CY" to ("EUR" to "el-CY"), "DK" to ("DKK" to "da-DK"),
            "SE" to ("SEK" to "sv-SE"), "NO" to ("NOK" to "nb-NO"), "IS" to ("ISK" to "is-IS"),
            "PL" to ("PLN" to "pl-PL"), "CZ" to ("CZK" to "cs-CZ"), "HU" to ("HUF" to "hu-HU"),
            "RO" to ("RON" to "ro-RO"), "GB" to ("GBP" to "en-GB"), "TR" to ("TRY" to "tr-TR"),
            "IL" to ("ILS" to "he-IL"), "US" to ("USD" to "en-US"), "CA" to ("CAD" to "en-CA"),
            "MX" to ("MXN" to "es-MX"), "BR" to ("BRL" to "pt-BR"), "AU" to ("AUD" to "en-AU"),
            "NZ" to ("NZD" to "en-NZ"), "JP" to ("JPY" to "ja-JP"), "KR" to ("KRW" to "ko-KR"),
            "CN" to ("CNY" to "zh-CN"), "HK" to ("HKD" to "zh-HK"), "SG" to ("SGD" to "en-SG"),
            "MY" to ("MYR" to "ms-MY"), "TH" to ("THB" to "th-TH"), "ID" to ("IDR" to "id-ID"),
            "PH" to ("PHP" to "en-PH"), "IN" to ("INR" to "en-IN"), "ZA" to ("ZAR" to "en-ZA"),
        )
    }
}

/** Whole money: is it zero once rounded to cents? */
fun Double.isZeroMoney() = abs(this) < 0.005
