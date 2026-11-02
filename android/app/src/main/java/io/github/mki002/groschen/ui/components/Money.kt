package io.github.mki002.groschen.ui.components

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.tween
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shadow
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.unit.TextUnit
import androidx.compose.ui.unit.isSpecified
import androidx.compose.ui.unit.sp
import io.github.mki002.groschen.i18n.Fmt
import io.github.mki002.groschen.i18n.MoneyParts

/**
 * The look of a hidden figure: the placeholder 9s seen through frosted glass. The glyphs are
 * nearly transparent and a soft shadow of the text colour draws their blurred shape.
 */
fun veil(color: Color, fontSize: TextUnit, density: Float): SpanStyle {
    val px = (if (fontSize.isSpecified) fontSize.value else 15f) * density
    return SpanStyle(color = color.copy(alpha = 0.12f), shadow = Shadow(color.copy(alpha = 0.92f), Offset.Zero, px * 0.2f))
}

/** Appends an amount; while amounts are hidden its digits are veiled. */
fun AnnotatedString.Builder.appendMoney(parts: MoneyParts, hidden: Boolean, veilStyle: SpanStyle, style: SpanStyle? = null) {
    if (style != null) pushStyle(style)
    append(parts.before)
    if (hidden) withStyle(veilStyle) { append(parts.number) } else append(parts.number)
    append(parts.after)
    if (style != null) pop()
}

/** An amount in the home currency (or another), written the home country's way. */
@Composable
fun Money(
    value: Double?,
    style: TextStyle,
    modifier: Modifier = Modifier,
    color: Color = style.color,
    currency: String? = null,
    digits: Int = 2,
    signed: Boolean = false,
    countUp: Boolean = false,
) {
    val fmt = LocalFmt.current
    if (value == null) {
        Text("–", modifier, style = style, color = color)
        return
    }
    // The big figure counts up once when the page first shows (not while amounts are hidden).
    val shown = if (countUp && !fmt.hidden) {
        val anim = remember { Animatable(0f) }
        LaunchedEffect(value) {
            anim.snapTo(0f)
            anim.animateTo(1f, tween(900, easing = FastOutSlowInEasing))
        }
        value * anim.value
    } else {
        value
    }
    val density = LocalDensity.current.density
    val text = buildAnnotatedString {
        appendMoney(fmt.moneyParts(shown, currency ?: fmt.currency, digits, signed), fmt.hidden, veil(color, style.fontSize, density))
    }
    Text(text, modifier, style = style, color = color, maxLines = 1)
}

/** An amount with its sign shown (+12,00 €), for [Sentence.tpl]. */
data class Signed(val value: Double)

/** Builds a sentence with amounts in it ("Netflix is 2.00 € dearer"), each one veiled while hidden. */
class Sentence(private val fmt: Fmt, private val color: Color, fontSize: TextUnit, density: Float) {
    private val veilStyle = veil(color, fontSize, density)
    private val builder = AnnotatedString.Builder()

    fun text(s: String) = apply { builder.append(s) }
    fun bold(s: String) = apply { builder.withStyle(SpanStyle(fontWeight = FontWeight.SemiBold, color = color)) { append(s) } }
    fun money(v: Double?, signed: Boolean = false, bold: Boolean = false) = apply {
        if (v == null) {
            builder.append("–")
            return@apply
        }
        builder.appendMoney(
            fmt.moneyParts(v, signed = signed),
            fmt.hidden,
            veilStyle,
            if (bold) SpanStyle(fontWeight = FontWeight.SemiBold, color = color) else null,
        )
    }

    /**
     * Fills a text like "{name} kostet jetzt {amount}": a Double becomes an amount (veiled while
     * hidden), anything else its text. With [bold] the filled-in parts stand out.
     */
    fun tpl(template: String, vararg values: Pair<String, Any?>, bold: Boolean = false) = apply {
        val map = values.toMap()
        var at = 0
        for (m in PLACEHOLDER.findAll(template)) {
            builder.append(template.substring(at, m.range.first))
            at = m.range.last + 1
            val key = m.groupValues[1]
            if (key !in map) {
                builder.append(m.value)
                continue
            }
            when (val v = map[key]) {
                null -> builder.append("–")
                is Double -> money(v, bold = bold)
                is Signed -> money(v.value, signed = true, bold = bold)
                is Float -> money(v.toDouble(), bold = bold)
                else -> if (bold) this.bold(v.toString()) else text(v.toString())
            }
        }
        builder.append(template.substring(at))
    }

    fun build(): AnnotatedString = builder.toAnnotatedString()

    private companion object {
        val PLACEHOLDER = Regex("\\{(\\w+)\\}")
    }
}

@Composable
fun rememberSentence(color: Color, fontSize: TextUnit = 15.sp): Sentence =
    Sentence(LocalFmt.current, color, fontSize, LocalDensity.current.density)

// Bank texts carry sums and account numbers of their own ("Rechnung 4711 über 49,99 EUR"):
// hidden the same way as the figures. Dates and plain numbers stay. (As in the web interface.)
private val SUM_IN_TEXT = Regex(
    "(^|[^\\d.,])((?:\\d{1,3}(?:\\.\\d{3})+|\\d+),\\d{2})(?![.,]?\\d)|((?:EUR|USD|GBP|CHF|€|\\$|£) ?)\\d(?:[\\d.,]*\\d)?" +
        "|\\d(?:[\\d.,]*\\d)?(?= ?(?:EUR|USD|GBP|CHF|€|\\$|£))",
)
private val IBAN_IN_TEXT = Regex("\\b[A-Z]{2}\\d{2}(?: ?[A-Z0-9]{4}){3,7}(?: ?[A-Z0-9]{1,3})?\\b")

fun veilText(text: String, hidden: Boolean): String {
    if (!hidden) return text
    val nines = { s: String -> s.replace(Regex("\\d"), "9") }
    return text
        .replace(IBAN_IN_TEXT) { m -> m.value.take(2) + nines(m.value.drop(2)) }
        .replace(SUM_IN_TEXT) { m ->
            val before = m.groups[1]?.value
            val sum = m.groups[2]?.value
            val cur = m.groups[3]?.value
            if (sum != null) (before ?: "") + nines(sum) else (cur ?: "") + nines(m.value.drop((cur ?: "").length))
        }
}
