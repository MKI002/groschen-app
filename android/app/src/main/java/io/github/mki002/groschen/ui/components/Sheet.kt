package io.github.mki002.groschen.ui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.MutableTransitionState
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.slideOutVertically
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.Orientation
import androidx.compose.foundation.gestures.draggable
import androidx.compose.foundation.gestures.rememberDraggableState
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.ime
import androidx.compose.foundation.layout.navigationBars
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.union
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.SideEffect
import androidx.compose.runtime.key
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import io.github.mki002.groschen.ui.theme.Palette
import kotlinx.coroutines.launch
import kotlin.math.roundToInt

private val SheetShape = RoundedCornerShape(topStart = 26.dp, topEnd = 26.dp)

/**
 * Sheets that slide up from the bottom, one on top of the other. Each one has a stable [keyOf],
 * so a sheet whose content changes (a booking got a new category) stays where it is.
 */
@Composable
fun <T : Any> SheetStack(
    sheets: List<T>,
    keyOf: (T) -> String,
    onDismiss: () -> Unit,
    content: @Composable ColumnScope.(T) -> Unit,
) {
    val keys = sheets.map(keyOf)
    val known = remember { HashMap<String, T>() }
    sheets.forEach { known[keyOf(it)] = it }
    val displayed = remember { mutableStateListOf<String>() }
    LaunchedEffect(keys) {
        keys.forEach { if (it !in displayed) displayed.add(it) }
    }
    for (k in displayed.toList()) {
        key(k) {
            val visible = k in keys
            val state = remember { MutableTransitionState(false) }
            SideEffect { state.targetState = visible }
            if (!visible && state.isIdle && !state.currentState) {
                LaunchedEffect(Unit) {
                    displayed.remove(k)
                    known.remove(k)
                }
            }
            val item = known[k]
            if (item != null) SheetFrame(state, onDismiss) { content(item) }
        }
    }
}

@Composable
private fun SheetFrame(state: MutableTransitionState<Boolean>, onDismiss: () -> Unit, content: @Composable ColumnScope.() -> Unit) {
    val drag = remember { Animatable(0f) }
    val scope = rememberCoroutineScope()
    val density = LocalDensity.current
    BoxWithConstraints(Modifier.fillMaxSize()) {
        val maxH = maxHeight
        AnimatedVisibility(state, enter = fadeIn(tween(220)), exit = fadeOut(tween(200))) {
            Box(
                Modifier
                    .fillMaxSize()
                    .background(Color.Black.copy(alpha = 0.6f))
                    .clickable(interactionSource = remember { MutableInteractionSource() }, indication = null, onClick = onDismiss),
            )
        }
        AnimatedVisibility(
            state,
            modifier = Modifier.align(Alignment.BottomCenter),
            enter = slideInVertically(tween(300)) { it } + fadeIn(tween(200)),
            exit = slideOutVertically(tween(220)) { it } + fadeOut(tween(200)),
        ) {
            Column(
                Modifier
                    .widthIn(max = 640.dp)
                    .fillMaxWidth()
                    .heightIn(max = maxH * 0.92f)
                    .offset { IntOffset(0, drag.value.roundToInt()) }
                    .clip(SheetShape)
                    .background(Palette.bg2)
                    .border(1.dp, Palette.line2, SheetShape)
                    // A tap inside the sheet must not reach the dimmed page behind it.
                    .clickable(interactionSource = remember { MutableInteractionSource() }, indication = null) {}
                    .windowInsetsPadding(WindowInsets.navigationBars.union(WindowInsets.ime)),
            ) {
                // Pull the handle down to close.
                Box(
                    Modifier
                        .fillMaxWidth()
                        .draggable(
                            orientation = Orientation.Vertical,
                            state = rememberDraggableState { d -> scope.launch { drag.snapTo((drag.value + d).coerceAtLeast(0f)) } },
                            onDragStopped = {
                                if (drag.value > with(density) { 110.dp.toPx() }) onDismiss()
                                scope.launch { drag.animateTo(0f) }
                            },
                        )
                        .padding(top = 10.dp, bottom = 6.dp),
                ) {
                    Grabber()
                }
                content()
            }
        }
    }
}

/** The Groschen coin: a gold ring with three rising bars. */
@Composable
fun Logo(modifier: Modifier = Modifier, size: androidx.compose.ui.unit.Dp = 34.dp) {
    Canvas(modifier.size(size)) {
        val k = this.size.minDimension / 40f
        drawCircle(Palette.accent, 18f * k, Offset(20f * k, 20f * k), style = Stroke(3f * k))
        drawCircle(Color(0xFF15171B), 13.5f * k, Offset(20f * k, 20f * k))
        val bars = listOf(Triple(12.5f, 21f, Color(0xFF8F7646)), Triple(18f, 17f, Palette.accent), Triple(23.5f, 12.5f, Color(0xFFF4E9CF)))
        for ((x, y, c) in bars) {
            drawRoundRect(c, Offset(x * k, y * k), Size(4f * k, (28f - y) * k), CornerRadius(1.5f * k))
        }
    }
}

@Composable
fun SheetBody(modifier: Modifier = Modifier, content: @Composable ColumnScope.() -> Unit) {
    Column(modifier.fillMaxWidth().padding(start = 20.dp, end = 20.dp, bottom = 20.dp), content = content)
}
