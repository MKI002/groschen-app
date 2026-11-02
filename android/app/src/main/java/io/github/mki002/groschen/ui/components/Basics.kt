package io.github.mki002.groschen.ui.components

import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.compositionLocalOf
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.ui.text.input.ImeAction
import io.github.mki002.groschen.i18n.Fmt
import io.github.mki002.groschen.i18n.Lang
import io.github.mki002.groschen.i18n.Strings
import io.github.mki002.groschen.i18n.strings
import io.github.mki002.groschen.ui.theme.G
import io.github.mki002.groschen.ui.theme.Palette

val LocalStrings = compositionLocalOf<Strings> { strings(Lang.DE) }
val LocalFmt = compositionLocalOf { Fmt(Lang.DE, "DE", "EUR", hidden = false) }

val CardShape = RoundedCornerShape(18.dp)
private val ButtonShape = RoundedCornerShape(12.dp)

/** A solid surface with a hairline edge, the building block of every page. */
@Composable
fun GCard(
    modifier: Modifier = Modifier,
    onClick: (() -> Unit)? = null,
    padding: PaddingValues = PaddingValues(18.dp),
    content: @Composable ColumnScope.() -> Unit,
) {
    Column(
        modifier
            .fillMaxWidth()
            .clip(CardShape)
            .background(Palette.surface)
            .border(1.dp, Palette.line, CardShape)
            .let { if (onClick != null) it.clickable(onClick = onClick) else it }
            .padding(padding),
        content = content,
    )
}

/** The small capital letters above a figure ("AVAILABLE UNTIL PAYDAY"). */
@Composable
fun Label(text: String, modifier: Modifier = Modifier, color: Color = Palette.muted) {
    Text(text.uppercase(), modifier = modifier, style = G.type.label, color = color, maxLines = 1, overflow = TextOverflow.Ellipsis)
}

enum class Tone(val fg: Color, val bg: Color) {
    Accent(Palette.accentInk, Palette.accentSoft),
    Good(Palette.good, Palette.goodSoft),
    Bad(Palette.bad, Palette.badSoft),
    Warn(Palette.warn, Palette.warnSoft),
    Info(Palette.info, Palette.infoSoft),
    Spend(Palette.spend, Palette.spendSoft),
    Muted(Palette.muted, Color(0x0FFFFFFF)),
}

@Composable
fun Pill(text: String, tone: Tone, modifier: Modifier = Modifier) {
    Text(
        text,
        modifier = modifier
            .clip(RoundedCornerShape(999.dp))
            .background(tone.bg)
            .padding(horizontal = 8.dp, vertical = 2.dp),
        style = G.type.small.copy(fontSize = G.type.label.fontSize),
        color = tone.fg,
        maxLines = 1,
    )
}

/** An icon on a tinted square, in front of a hint or a list row. */
@Composable
fun IconBubble(icon: Ico, tone: Tone, modifier: Modifier = Modifier, size: Dp = 40.dp) {
    Box(
        modifier
            .size(size)
            .clip(RoundedCornerShape(size * 0.3f))
            .background(tone.bg)
            .border(1.dp, tone.fg.copy(alpha = 0.16f), RoundedCornerShape(size * 0.3f)),
        contentAlignment = Alignment.Center,
    ) {
        GIcon(icon, size = size * 0.48f, tint = tone.fg)
    }
}

/** A round letter in a category's colour, in front of a booking. */
@Composable
fun Initial(text: String, color: Color, modifier: Modifier = Modifier, size: Dp = 38.dp) {
    val letter = text.firstOrNull { it.isLetter() }?.uppercaseChar()?.toString() ?: "?"
    Box(
        modifier
            .size(size)
            .clip(CircleShape)
            .background(color.copy(alpha = 0.16f))
            .border(1.dp, color.copy(alpha = 0.28f), CircleShape),
        contentAlignment = Alignment.Center,
    ) {
        Text(letter, style = G.type.bodyStrong, color = color)
    }
}

@Composable
fun GButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    primary: Boolean = false,
    icon: Ico? = null,
    enabled: Boolean = true,
    busy: Boolean = false,
    small: Boolean = false,
    trailing: Ico? = null,
) {
    val bg = if (primary) Palette.accent else Palette.surface2
    val fg = if (primary) Palette.onAccent else Palette.ink
    Row(
        modifier
            .heightIn(min = if (small) 36.dp else 50.dp)
            .clip(ButtonShape)
            .background(bg)
            .border(1.dp, if (primary) Color.Transparent else Palette.line2, ButtonShape)
            .clickable(enabled = enabled && !busy, role = Role.Button, onClick = onClick)
            .alpha(if (enabled) 1f else 0.45f)
            .padding(horizontal = if (small) 14.dp else 20.dp),
        horizontalArrangement = Arrangement.Center,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        if (busy) {
            CircularProgressIndicator(Modifier.size(18.dp), color = fg, strokeWidth = 2.dp)
            Spacer(Modifier.width(10.dp))
        } else if (icon != null) {
            GIcon(icon, size = if (small) 16.dp else 18.dp, tint = fg)
            Spacer(Modifier.width(8.dp))
        }
        Text(text, style = if (small) G.type.bodyStrong.copy(fontSize = G.type.small.fontSize) else G.type.bodyStrong, color = fg, maxLines = 1)
        if (trailing != null) {
            Spacer(Modifier.width(6.dp))
            GIcon(trailing, size = 14.dp, tint = fg.copy(alpha = 0.7f))
        }
    }
}

@Composable
fun RoundButton(icon: Ico, label: String, onClick: () -> Unit, modifier: Modifier = Modifier, tint: Color = Palette.ink2) {
    Box(
        modifier
            .size(42.dp)
            .clip(RoundedCornerShape(13.dp))
            .background(Palette.surface)
            .border(1.dp, Palette.line2, RoundedCornerShape(13.dp))
            .clickable(role = Role.Button, onClickLabel = label, onClick = onClick)
            // A button with only an icon still has a name for TalkBack.
            .semantics { contentDescription = label },
        contentAlignment = Alignment.Center,
    ) {
        GIcon(icon, size = 20.dp, tint = tint)
    }
}

/** A choice among a few, like the period of the spending page. */
@Composable
fun ChoiceChip(text: String, selected: Boolean, onClick: () -> Unit, modifier: Modifier = Modifier, count: Int? = null) {
    val shape = RoundedCornerShape(999.dp)
    Row(
        modifier
            .height(36.dp)
            .clip(shape)
            .background(if (selected) Palette.accentSoft else Palette.surface)
            .border(1.dp, if (selected) Palette.accentLine else Palette.line2, shape)
            .clickable(role = Role.Tab, onClick = onClick)
            .padding(horizontal = 14.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(text, style = G.type.bodyStrong.copy(fontSize = G.type.small.fontSize), color = if (selected) Palette.accentInk else Palette.ink2)
        if (count != null && count > 0) {
            Spacer(Modifier.width(6.dp))
            Text(
                count.toString(),
                modifier = Modifier
                    .clip(shape)
                    .background(if (selected) Palette.accent else Palette.surface3)
                    .padding(horizontal = 6.dp),
                style = G.type.label.copy(letterSpacing = G.type.label.letterSpacing * 0),
                color = if (selected) Palette.onAccent else Palette.ink2,
            )
        }
    }
}

@Composable
fun GSwitch(checked: Boolean, onChange: (Boolean) -> Unit, enabled: Boolean = true) {
    Switch(
        checked = checked,
        onCheckedChange = onChange,
        enabled = enabled,
        colors = SwitchDefaults.colors(
            checkedThumbColor = Palette.onAccent,
            checkedTrackColor = Palette.accent,
            checkedBorderColor = Palette.accent,
            uncheckedThumbColor = Palette.muted,
            uncheckedTrackColor = Palette.surface3,
            uncheckedBorderColor = Palette.line2,
        ),
    )
}

@Composable
fun GField(
    value: String,
    onChange: (String) -> Unit,
    label: String,
    modifier: Modifier = Modifier,
    password: Boolean = false,
    keyboard: KeyboardType = KeyboardType.Text,
    imeAction: ImeAction = ImeAction.Next,
    onDone: (() -> Unit)? = null,
    leading: Ico? = null,
    trailing: @Composable (() -> Unit)? = null,
    singleLine: Boolean = true,
    placeholder: String? = null,
) {
    OutlinedTextField(
        value = value,
        onValueChange = onChange,
        modifier = modifier.fillMaxWidth(),
        label = { Text(label) },
        placeholder = placeholder?.let { { Text(it, color = Palette.faint) } },
        singleLine = singleLine,
        shape = RoundedCornerShape(14.dp),
        textStyle = G.type.body,
        visualTransformation = if (password) PasswordVisualTransformation() else VisualTransformation.None,
        keyboardOptions = KeyboardOptions(
            keyboardType = if (password) KeyboardType.Password else keyboard,
            imeAction = imeAction,
            autoCorrectEnabled = false,
        ),
        keyboardActions = KeyboardActions(
            onDone = { onDone?.invoke() },
            onGo = { onDone?.invoke() },
            onSearch = { onDone?.invoke() },
            onSend = { onDone?.invoke() },
        ),
        leadingIcon = leading?.let { { GIcon(it, size = 18.dp, tint = Palette.muted) } },
        trailingIcon = trailing,
        colors = OutlinedTextFieldDefaults.colors(
            focusedBorderColor = Palette.accentLine,
            unfocusedBorderColor = Palette.line2,
            focusedContainerColor = Palette.surface,
            unfocusedContainerColor = Palette.surface,
            focusedLabelColor = Palette.accentInk,
            unfocusedLabelColor = Palette.muted,
            cursorColor = Palette.accent,
            focusedTextColor = Palette.ink,
            unfocusedTextColor = Palette.ink,
        ),
    )
}

/** A line between rows, as thin as the card edges. */
@Composable
fun Hairline(modifier: Modifier = Modifier) {
    Box(modifier.fillMaxWidth().height(1.dp).background(Palette.line))
}

/** A page's data is on its way: calm grey shapes where it will be. */
@Composable
fun Placeholder(modifier: Modifier = Modifier, height: Dp = 120.dp, shape: Shape = CardShape) {
    val pulse by rememberInfiniteTransition(label = "placeholder").animateFloat(
        initialValue = 0.45f,
        targetValue = 0.9f,
        animationSpec = infiniteRepeatable(tween(900), RepeatMode.Reverse),
        label = "pulse",
    )
    Box(
        modifier
            .fillMaxWidth()
            .height(height)
            .clip(shape)
            .alpha(pulse)
            .background(Palette.surface)
            .border(1.dp, Palette.line, shape),
    )
}

@Composable
fun ErrorNote(message: String, onRetry: (() -> Unit)?, modifier: Modifier = Modifier) {
    val s = LocalStrings.current
    GCard(modifier) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            IconBubble(Ico.Cloud, Tone.Warn, size = 36.dp)
            Spacer(Modifier.width(14.dp))
            Text(message, style = G.type.body, color = Palette.ink2, modifier = Modifier.weight(1f))
        }
        if (onRetry != null) {
            Spacer(Modifier.height(14.dp))
            GButton(s.retry, onRetry, small = true, icon = Ico.Refresh)
        }
    }
}

@Composable
fun EmptyNote(text: String, modifier: Modifier = Modifier, icon: Ico = Ico.Check) {
    Column(modifier.fillMaxWidth().padding(vertical = 28.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        IconBubble(icon, Tone.Muted, size = 44.dp)
        Spacer(Modifier.height(12.dp))
        Text(text, style = G.type.body, color = Palette.muted)
    }
}

/** A title and a short line under it, for settings rows. */
@Composable
fun RowText(title: String, sub: String?, modifier: Modifier = Modifier) {
    Column(modifier) {
        Text(title, style = G.type.bodyStrong)
        if (!sub.isNullOrEmpty()) Text(sub, style = G.type.small)
    }
}

@Composable
fun SettingRow(
    title: String,
    sub: String? = null,
    onClick: (() -> Unit)? = null,
    icon: Ico? = null,
    trailing: @Composable RowScope.() -> Unit = {},
) {
    Row(
        Modifier
            .fillMaxWidth()
            .let { if (onClick != null) it.clickable(onClick = onClick) else it }
            .padding(vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        if (icon != null) {
            GIcon(icon, size = 20.dp, tint = Palette.muted)
            Spacer(Modifier.width(14.dp))
        }
        RowText(title, sub, Modifier.weight(1f))
        Spacer(Modifier.width(12.dp))
        trailing()
    }
}

/** A thin bar split into coloured parts (shares of a whole). */
@Composable
fun ShareBar(parts: List<Pair<Float, Color>>, modifier: Modifier = Modifier, height: Dp = 8.dp, progress: Float = 1f) {
    Canvas(modifier.fillMaxWidth().height(height)) {
        val total = parts.sumOf { it.first.toDouble() }.toFloat().takeIf { it > 0f } ?: return@Canvas
        val gap = 3.dp.toPx()
        val usable = size.width - gap * (parts.count { it.first > 0f } - 1).coerceAtLeast(0)
        var x = 0f
        drawRoundRect(Palette.surface3, size = size, cornerRadius = CornerRadius(size.height / 2))
        for ((value, color) in parts) {
            if (value <= 0f) continue
            val w = (usable * value / total * progress).coerceAtLeast(2f)
            drawRoundRect(color, topLeft = Offset(x, 0f), size = Size(w, size.height), cornerRadius = CornerRadius(size.height / 2))
            x += w + gap
        }
    }
}

/** A small round mark in a colour, for a legend or a category. */
@Composable
fun Dot(color: Color, modifier: Modifier = Modifier, size: Dp = 9.dp) {
    Box(modifier.size(size).clip(RoundedCornerShape(size * 0.33f)).background(color))
}

@Composable
fun Grabber() {
    Box(Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
        Box(Modifier.width(40.dp).height(4.dp).clip(CircleShape).background(Palette.surface3))
    }
}

@Composable
fun BorderedBox(modifier: Modifier = Modifier, content: @Composable () -> Unit) {
    Box(modifier.clip(CardShape).background(Palette.sunk).border(BorderStroke(1.dp, Palette.line), CardShape).padding(14.dp)) {
        content()
    }
}
