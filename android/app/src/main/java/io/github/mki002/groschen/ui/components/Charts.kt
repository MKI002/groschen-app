package io.github.mki002.groschen.ui.components

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.clipRect
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import io.github.mki002.groschen.ui.theme.Palette
import kotlin.math.max
import kotlin.math.min

/** Draws itself from left to right once, when it first shows. */
@Composable
private fun rememberReveal(key: Any?): Animatable<Float, *> {
    val reveal = remember { Animatable(0f) }
    LaunchedEffect(key) {
        reveal.snapTo(0f)
        reveal.animateTo(1f, tween(1100, easing = FastOutSlowInEasing))
    }
    return reveal
}

private fun DrawScope.linePath(values: List<Double>, lo: Double, hi: Double, top: Float, bottom: Float): Path {
    val path = Path()
    val span = (hi - lo).takeIf { it > 0 } ?: 1.0
    values.forEachIndexed { i, v ->
        val x = if (values.size == 1) 0f else size.width * i / (values.size - 1)
        val y = bottom - ((v - lo) / span).toFloat() * (bottom - top)
        if (i == 0) path.moveTo(x, y) else path.lineTo(x, y)
    }
    return path
}

/**
 * A value over time with a soft fill under it; optionally a second, dashed line (the money paid
 * in), so a rise from paying in never looks like a gain.
 */
@Composable
fun LineChart(
    values: List<Double>,
    modifier: Modifier = Modifier,
    color: Color = Palette.accent,
    second: List<Double>? = null,
    secondColor: Color = Palette.muted,
    height: Dp = 150.dp,
) {
    if (values.size < 2) return
    val reveal = rememberReveal(values.size)
    Canvas(modifier.fillMaxWidth().height(height)) {
        val all = values + (second ?: emptyList())
        val pad = (all.max() - all.min()).coerceAtLeast(1.0) * 0.08
        val lo = if (all.min() >= 0) max(0.0, all.min() - pad) else all.min() - pad
        val hi = all.max() + pad
        val top = 6.dp.toPx()
        val bottom = size.height - 2.dp.toPx()
        // Three calm guide lines.
        for (i in 0..2) {
            val y = top + (bottom - top) * i / 2f
            drawLine(Palette.line, Offset(0f, y), Offset(size.width, y), strokeWidth = 1f)
        }
        clipRect(right = size.width * reveal.value) {
            val line = linePath(values, lo, hi, top, bottom)
            val fill = Path().apply {
                addPath(line)
                lineTo(size.width, bottom)
                lineTo(0f, bottom)
                close()
            }
            drawPath(fill, Brush.verticalGradient(listOf(color.copy(alpha = 0.22f), color.copy(alpha = 0f)), top, bottom))
            if (second != null && second.size == values.size) {
                drawPath(
                    linePath(second, lo, hi, top, bottom),
                    secondColor,
                    style = Stroke(
                        width = 1.6.dp.toPx(),
                        cap = StrokeCap.Round,
                        pathEffect = PathEffect.dashPathEffect(floatArrayOf(6.dp.toPx(), 5.dp.toPx())),
                    ),
                )
            }
            drawPath(line, color, style = Stroke(width = 2.2.dp.toPx(), cap = StrokeCap.Round, join = StrokeJoin.Round))
        }
    }
}

/** A small line without axes, for a fund's last months. */
@Composable
fun Sparkline(values: List<Double>, modifier: Modifier = Modifier, color: Color = Palette.accent, height: Dp = 36.dp) {
    if (values.size < 2) return
    Canvas(modifier.fillMaxWidth().height(height)) {
        val lo = values.min()
        val hi = values.max()
        drawPath(
            linePath(values, lo, max(hi, lo + 1e-9), 2.dp.toPx(), size.height - 2.dp.toPx()),
            color,
            style = Stroke(width = 1.8.dp.toPx(), cap = StrokeCap.Round, join = StrokeJoin.Round),
        )
    }
}

/**
 * The month from the last salary to the next: one bar per day, the days gone filled, today
 * marked, and a dot on each day a fixed cost is still to come.
 */
@Composable
fun PaydayStrip(days: Int, today: Int, charges: Set<Int>, modifier: Modifier = Modifier) {
    if (days <= 0) return
    val reveal = rememberReveal(days)
    Canvas(modifier.fillMaxWidth().height(30.dp)) {
        val gap = (size.width / days * 0.22f).coerceIn(1.5f, 4.dp.toPx())
        val w = (size.width - gap * (days - 1)) / days
        val h = size.height
        for (i in 0 until days) {
            // The bars appear one after another from the left.
            val appear = ((reveal.value * days * 1.3f) - i).coerceIn(0f, 1f)
            if (appear <= 0f) continue
            val x = i * (w + gap)
            val isToday = i == today
            val barH = if (isToday) h else h * 0.72f
            val y = (h - barH) / 2
            val r = CornerRadius(min(w, barH) / 2)
            when {
                i < today -> drawRoundRect(Palette.accent2.copy(alpha = 0.55f * appear), Offset(x, y), Size(w, barH), r)
                isToday -> {
                    drawRoundRect(Palette.accent.copy(alpha = appear), Offset(x, y), Size(w, barH), r)
                }
                else -> drawRoundRect(
                    Palette.line2.copy(alpha = 0.12f * appear + 0.04f),
                    Offset(x, y),
                    Size(w, barH),
                    r,
                    style = Stroke(1.2.dp.toPx()),
                )
            }
            if (i in charges && i >= today) {
                val cr = (w * 0.38f).coerceAtMost(3.4.dp.toPx())
                drawCircle(Palette.spend.copy(alpha = appear), cr, Offset(x + w / 2, h / 2))
            }
        }
    }
}
