package io.github.mki002.groschen.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.Immutable
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.em
import androidx.compose.ui.unit.sp

// The one look of Groschen, the same tokens as the web interface (frontend/src/styles.css):
// dark and formal, a champagne accent, Figtree with heavy, tight big numbers, solid surfaces
// with hairline edges.
object Palette {
    val bg = Color(0xFF0A0B0D)
    val bg2 = Color(0xFF0D0E11)
    val surface = Color(0xFF121418)
    val surface2 = Color(0xFF171A1F)
    val surface3 = Color(0xFF1D2026)
    val sunk = Color(0xFF0E1013)
    val line = Color(0x11FFFFFF)
    val line2 = Color(0x1AFFFFFF)
    val ink = Color(0xFFECEDEF)
    val ink2 = Color(0xFFC9CCD2)
    val muted = Color(0xFF8D919A)
    val faint = Color(0xFF5E636C)
    val accent = Color(0xFFD6B46E)
    val accentInk = Color(0xFFE8CB8A)
    val accent2 = Color(0xFFB8934F)
    val accentSoft = Color(0x1FD6B46E)
    val accentLine = Color(0x59D6B46E)
    val onAccent = Color(0xFF17130B)
    val good = Color(0xFF57D3A2)
    val goodSoft = Color(0x1F57D3A2)
    val spend = Color(0xFFEF8E73)
    val spendSoft = Color(0x21EF8E73)
    val bad = Color(0xFFF2736B)
    val badSoft = Color(0x1FF2736B)
    val warn = Color(0xFFF1B74E)
    val warnSoft = Color(0x1FF1B74E)
    val info = Color(0xFF7FA8F5)
    val infoSoft = Color(0x1F7FA8F5)

    // Category colours, by the names the server uses.
    private val categories = mapOf(
        "blue" to Color(0xFF6E9CF2),
        "amber" to Color(0xFFE3B25A),
        "pink" to Color(0xFFE58AB0),
        "gray" to Color(0xFF9C978F),
        "forest" to Color(0xFF45A97F),
        "teal" to Color(0xFF4CC3BB),
        "red" to Color(0xFFE97C6B),
        "violet" to Color(0xFFA28CF0),
        "sand" to Color(0xFFCDB287),
        "green" to Color(0xFF5DBE7C),
        "slate" to Color(0xFF8E9BAD),
    )
    val categoryMuted = Color(0xFF4B4F57)

    fun category(name: String?): Color = categories[name] ?: categoryMuted
}

@Immutable
data class GroschenType(
    val hero: TextStyle,
    val big: TextStyle,
    val title: TextStyle,
    val heading: TextStyle,
    val body: TextStyle,
    val bodyStrong: TextStyle,
    val small: TextStyle,
    val label: TextStyle,
    val number: TextStyle,
)

val LocalType = staticCompositionLocalOf<GroschenType> { error("GroschenTheme is missing") }

object G {
    val type: GroschenType
        @Composable get() = LocalType.current
}

fun groschenType(font: FontFamily): GroschenType {
    val base = TextStyle(fontFamily = font, color = Palette.ink, fontFeatureSettings = "tnum")
    return GroschenType(
        hero = base.copy(fontSize = 46.sp, fontWeight = FontWeight.Bold, letterSpacing = (-0.035).em, lineHeight = 50.sp),
        big = base.copy(fontSize = 30.sp, fontWeight = FontWeight.Bold, letterSpacing = (-0.03).em, lineHeight = 34.sp),
        title = base.copy(fontSize = 30.sp, fontWeight = FontWeight.Bold, letterSpacing = (-0.025).em, lineHeight = 36.sp),
        heading = base.copy(fontSize = 17.sp, fontWeight = FontWeight.SemiBold, letterSpacing = (-0.01).em, lineHeight = 22.sp),
        body = base.copy(fontSize = 15.sp, fontWeight = FontWeight.Normal, lineHeight = 21.sp),
        bodyStrong = base.copy(fontSize = 15.sp, fontWeight = FontWeight.SemiBold, lineHeight = 21.sp),
        small = base.copy(fontSize = 13.sp, fontWeight = FontWeight.Normal, color = Palette.muted, lineHeight = 18.sp),
        label = base.copy(
            fontSize = 11.5.sp,
            fontWeight = FontWeight.SemiBold,
            color = Palette.muted,
            letterSpacing = 0.12.em,
            lineHeight = 15.sp,
        ),
        number = base.copy(fontSize = 15.sp, fontWeight = FontWeight.SemiBold, letterSpacing = (-0.005).em),
    )
}

@Composable
fun GroschenTheme(font: FontFamily, content: @Composable () -> Unit) {
    val type = groschenType(font)
    val colors = darkColorScheme(
        primary = Palette.accent,
        onPrimary = Palette.onAccent,
        primaryContainer = Palette.accentSoft,
        onPrimaryContainer = Palette.accentInk,
        secondary = Palette.accent2,
        onSecondary = Palette.onAccent,
        background = Palette.bg,
        onBackground = Palette.ink,
        surface = Palette.surface,
        onSurface = Palette.ink,
        surfaceVariant = Palette.surface2,
        onSurfaceVariant = Palette.muted,
        surfaceContainer = Palette.surface,
        surfaceContainerHigh = Palette.surface2,
        surfaceContainerHighest = Palette.surface3,
        surfaceContainerLow = Palette.bg2,
        surfaceContainerLowest = Palette.bg,
        outline = Palette.line2,
        outlineVariant = Palette.line,
        error = Palette.bad,
        onError = Palette.bg,
    )
    val typography = Typography(
        displayLarge = type.hero,
        headlineLarge = type.title,
        headlineMedium = type.big,
        titleLarge = type.heading,
        titleMedium = type.bodyStrong,
        bodyLarge = type.body,
        bodyMedium = type.body,
        bodySmall = type.small,
        labelLarge = type.bodyStrong,
        labelMedium = type.small,
        labelSmall = type.label,
    )
    MaterialTheme(colorScheme = colors, typography = typography) {
        CompositionLocalProvider(LocalType provides type) {
            content()
        }
    }
}
