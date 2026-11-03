package io.github.mki002.groschen.ui.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.size
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.scale
import androidx.compose.ui.graphics.vector.PathParser
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import io.github.mki002.groschen.ui.theme.Palette

// The icons of the web interface (frontend/src/components/Icons.tsx), drawn on a 24×24 grid.
internal class Part(val d: String, val fill: Boolean = false, val width: Float = 1.8f)

private fun s(d: String, width: Float = 1.8f) = Part(d, fill = false, width = width)
private fun f(d: String) = Part(d, fill = true)

private fun circle(cx: Float, cy: Float, r: Float) =
    "M${cx - r},${cy}a$r,$r 0 1,0 ${2 * r},0a$r,$r 0 1,0 ${-2 * r},0z"

private fun rrect(x: Float, y: Float, w: Float, h: Float, r: Float) =
    "M${x + r},${y}h${w - 2 * r}a$r,$r 0 0 1 $r,${r}v${h - 2 * r}a$r,$r 0 0 1 ${-r},${r}h${-(w - 2 * r)}" +
        "a$r,$r 0 0 1 ${-r},${-r}v${-(h - 2 * r)}a$r,$r 0 0 1 $r,${-r}z"

enum class Ico(internal vararg val parts: Part) {
    Home(s("M3 11l9-7 9 7M5 10v10h14V10M10 20v-6h4v6")),
    List(s(rrect(4f, 3f, 16f, 18f, 2.5f)), s("M8 8h8M8 12h8M8 16h5")),
    Pie(s("M12 3a9 9 0 1 0 9 9h-9z"), s("M15 3.5A9 9 0 0 1 20.5 9H15z")),
    Vault(
        s(rrect(3f, 4.5f, 18f, 14.5f, 2.5f)),
        s(circle(12f, 11.75f, 3.4f)),
        s("M12 6.8v1.4M12 15.3v1.4M7 11.75h1.4M15.6 11.75H17M6.5 19v1.5M17.5 19v1.5"),
    ),
    Gear(
        s(circle(12f, 12f, 3f)),
        s(
            "M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21" +
                "a2 2 0 0 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 " +
                ".3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 0 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 " +
                "2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 0 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 " +
                "1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 0 1 0 4h-.1" +
                "a1.7 1.7 0 0 0-1.5 1z",
        ),
    ),
    Eye(s("M2.5 12s3.5-6.5 9.5-6.5S21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"), s(circle(12f, 12f, 3f))),
    EyeOff(
        s("M10.6 5.6A10 10 0 0 1 12 5.5c6 0 9.5 6.5 9.5 6.5a17 17 0 0 1-2.8 3.6M6.6 6.6C4 8.3 2.5 12 2.5 12S6 18.5 12 18.5a9 9 0 0 0 4.4-1.1"),
        s("M9.9 9.9a3 3 0 0 0 4.2 4.2M4 4l16 16"),
    ),
    Search(s(circle(11f, 11f, 6.5f)), s("M20 20l-4.2-4.2")),
    X(s("M6 6l12 12M18 6L6 18")),
    Check(s("M5 12l5 5 9-10", 2f)),
    ChevRight(s("M9 6l6 6-6 6")),
    ChevDown(s("M6 9l6 6 6-6")),
    Up(s("M12 19V5M5.5 11.5L12 5l6.5 6.5")),
    Down(s("M12 5v14M5.5 12.5L12 19l6.5-6.5")),
    Download(s("M12 4v11M7 10.5l5 5 5-5M5 20h14")),
    Spark(f("M12 2l1.8 5.4L19 9l-5.2 1.6L12 16l-1.8-5.4L5 9l5.2-1.6zM19 14l.9 2.6 2.6.9-2.6.9L19 21l-.9-2.6-2.6-.9 2.6-.9z")),
    Warn(s("M12 3l10 18H2z"), s("M12 10v5M12 18h.01")),
    Repeat(s("M17 2l3 3-3 3M4 11V9a4 4 0 0 1 4-4h12M7 22l-3-3 3-3M20 13v2a4 4 0 0 1-4 4H4")),
    Ban(s(circle(12f, 12f, 9f)), s("M5.8 5.8l12.4 12.4")),
    Play(s(circle(12f, 12f, 9f)), s("M10.2 8.8l5 3.2-5 3.2z")),
    Refresh(s("M20 11a8 8 0 0 0-14.7-4.3M4 5v4h4M4 13a8 8 0 0 0 14.7 4.3M20 19v-4h-4")),
    Bank(s("M3 9l9-5 9 5M5 10v8M9.5 10v8M14.5 10v8M19 10v8M3 20h18")),
    Wallet(s("M4 7.5A2.5 2.5 0 0 1 6.5 5H18v3M4 7.5V17a2.5 2.5 0 0 0 2.5 2.5H20V8H6.5A2.5 2.5 0 0 1 4 7.5z"), f(circle(16f, 14f, 1.3f))),
    Etf(s("M4 20h16M6 16V11M10 16V7M14 16v-5M18 16V5")),
    Trend(s("M3 17l6-6 4 4 8-8M15 7h6v6")),
    Coin(s(circle(12f, 12f, 9f)), s("M14.8 9.2a3.6 3.6 0 1 0 0 5.6M8 11h5M8 13.2h5")),
    Swap(s("M5 8h13M15 5l3 3-3 3M19 16H6M9 13l-3 3 3 3")),
    Calendar(s(rrect(3.5f, 5f, 17f, 15.5f, 2.5f)), s("M3.5 10h17M8 3v4M16 3v4"), f("M7 13.5h2.5V16H7zM11 13.5h2.5V16H11z")),
    Lock(s(rrect(4f, 10f, 16f, 11f, 2.5f)), s("M8 10V7a4 4 0 0 1 8 0v3")),
    Globe(s(circle(12f, 12f, 9f)), s("M3 12h18M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3z")),
    Logout(s("M15 4h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-3M10 16l-4-4 4-4M6 12h10")),
    Pencil(s("M4 20h4L19 9a2.8 2.8 0 0 0-4-4L4 16zM13.5 6.5l4 4")),
    Tag(s("M3 12V4a1 1 0 0 1 1-1h8l9 9-9 9z"), f(circle(8f, 8f, 1.5f))),
    Clock(s(circle(12f, 12f, 9f)), s("M12 7v5l3.2 2")),
    Server(s(rrect(3.5f, 4f, 17f, 7f, 2f)), s(rrect(3.5f, 13f, 17f, 7f, 2f)), f(circle(7.5f, 7.5f, 1.1f)), f(circle(7.5f, 16.5f, 1.1f))),
    // Ridges around one centre (12, 12), so the print sits even in its circle.
    Fingerprint(
        s("M3.5 9a9 9 0 0 1 17 0"),
        s("M6 17.5V12a6 6 0 0 1 12 0v1.5"),
        s("M18 16.5c0 1.6-.3 3.1-.8 4.5"),
        s("M9 16.5V12a3 3 0 0 1 6 0v2.5c0 2.3-.4 4.4-1.2 6.4"),
        s("M12 12v3c0 2.3-.6 4.5-1.7 6.5"),
    ),
    Cloud(s("M7 18.5h10.5a4 4 0 0 0 .6-8 6 6 0 0 0-11.6 1.3A3.4 3.4 0 0 0 7 18.5z")),
}

@Composable
fun GIcon(icon: Ico, modifier: Modifier = Modifier, size: Dp = 20.dp, tint: Color = Palette.ink2) {
    val paths = remember(icon) { icon.parts.map { it to PathParser().parsePathString(it.d).toPath() } }
    Canvas(modifier.size(size)) {
        val k = this.size.minDimension / 24f
        scale(k, k, pivot = Offset.Zero) {
            for ((part, path) in paths) {
                if (part.fill) {
                    drawPath(path, tint)
                } else {
                    drawPath(path, tint, style = Stroke(width = part.width, cap = StrokeCap.Round, join = StrokeJoin.Round))
                }
            }
        }
    }
}
