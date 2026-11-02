package io.github.mki002.groschen.ui.screens

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawing
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import io.github.mki002.groschen.model.AppModel
import io.github.mki002.groschen.ui.components.GButton
import io.github.mki002.groschen.ui.components.GField
import io.github.mki002.groschen.ui.components.GIcon
import io.github.mki002.groschen.ui.components.Ico
import io.github.mki002.groschen.ui.components.IconBubble
import io.github.mki002.groschen.ui.components.LocalStrings
import io.github.mki002.groschen.ui.components.Logo
import io.github.mki002.groschen.ui.components.Tone
import io.github.mki002.groschen.ui.theme.G
import io.github.mki002.groschen.ui.theme.Palette

/** The frame of the screens before the app opens: centred, calm, the logo on top. */
@Composable
private fun AuthFrame(content: @Composable ColumnScope.() -> Unit) {
    val logoIn = remember { Animatable(0.85f) }
    LaunchedEffect(Unit) { logoIn.animateTo(1f, tween(500)) }
    Box(
        Modifier
            .fillMaxSize()
            .background(Brush.radialGradient(listOf(Palette.surface2, Palette.bg), radius = 1400f))
            .windowInsetsPadding(WindowInsets.safeDrawing)
            .imePadding(),
        contentAlignment = Alignment.Center,
    ) {
        Column(
            Modifier
                .widthIn(max = 460.dp)
                .fillMaxWidth()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 24.dp, vertical = 32.dp),
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Logo(Modifier.scale(logoIn.value), size = 44.dp)
                Spacer(Modifier.width(12.dp))
                Text("Groschen", style = G.type.title.copy(fontSize = G.type.heading.fontSize * 1.4f))
            }
            Spacer(Modifier.height(36.dp))
            content()
        }
    }
}

@Composable
private fun ErrorText(text: String?) {
    if (text == null) return
    Spacer(Modifier.height(12.dp))
    Row(verticalAlignment = Alignment.Top) {
        GIcon(Ico.Warn, size = 16.dp, tint = Palette.bad, modifier = Modifier.padding(top = 2.dp))
        Spacer(Modifier.width(8.dp))
        Text(text, style = G.type.body, color = Palette.bad)
    }
}

@Composable
private fun NoticeBox(text: String?) {
    if (text == null) return
    Row(
        Modifier
            .fillMaxWidth()
            .clip(androidx.compose.foundation.shape.RoundedCornerShape(14.dp))
            .background(Palette.infoSoft)
            .padding(14.dp),
        verticalAlignment = Alignment.Top,
    ) {
        GIcon(Ico.Lock, size = 18.dp, tint = Palette.info)
        Spacer(Modifier.width(10.dp))
        Text(text, style = G.type.body, color = Palette.ink2)
    }
    Spacer(Modifier.height(18.dp))
}

@Composable
fun ConnectScreen(model: AppModel) {
    val s = LocalStrings.current
    var address by rememberSaveable { mutableStateOf(model.settings.server.orEmpty()) }
    AuthFrame {
        Text(s.connectTitle, style = G.type.title)
        Spacer(Modifier.height(10.dp))
        Text(s.connectText, style = G.type.body, color = Palette.ink2)
        Spacer(Modifier.height(24.dp))
        GField(
            address,
            { address = it; model.formError = null },
            s.serverAddress,
            placeholder = "192.168.178.20:8420",
            keyboard = KeyboardType.Uri,
            imeAction = ImeAction.Go,
            onDone = { model.connect(address) },
            leading = Ico.Server,
        )
        ErrorText(model.formError)
        if (model.setupUrl != null) {
            Spacer(Modifier.height(12.dp))
            GButton(s.setupInBrowser, model::openSetupInBrowser, icon = Ico.Globe, modifier = Modifier.fillMaxWidth())
        }
        Spacer(Modifier.height(20.dp))
        GButton(s.connect, { model.connect(address) }, primary = true, busy = model.busy, modifier = Modifier.fillMaxWidth())
        Spacer(Modifier.height(28.dp))
        Row(verticalAlignment = Alignment.Top) {
            GIcon(Ico.Lock, size = 16.dp, tint = Palette.muted, modifier = Modifier.padding(top = 2.dp))
            Spacer(Modifier.width(10.dp))
            Text(s.connectSafety, style = G.type.small)
        }
    }
}

@Composable
fun LoginScreen(model: AppModel) {
    val s = LocalStrings.current
    var username by rememberSaveable { mutableStateOf(model.settings.username) }
    var password by rememberSaveable { mutableStateOf("") }
    AuthFrame {
        NoticeBox(model.notice)
        Text(s.loginTitle, style = G.type.title)
        Spacer(Modifier.height(8.dp))
        Row(verticalAlignment = Alignment.CenterVertically) {
            GIcon(Ico.Server, size = 15.dp, tint = Palette.muted)
            Spacer(Modifier.width(8.dp))
            Text(model.serverLabel, style = G.type.small, modifier = Modifier.weight(1f, fill = false))
            Spacer(Modifier.width(10.dp))
            Text(
                s.change,
                style = G.type.small,
                color = Palette.accentInk,
                modifier = Modifier.clickable(role = Role.Button, onClick = model::changeServer).padding(4.dp),
            )
        }
        Spacer(Modifier.height(24.dp))
        GField(username, { username = it; model.formError = null }, s.username, leading = Ico.Tag)
        Spacer(Modifier.height(12.dp))
        GField(
            password,
            { password = it; model.formError = null },
            s.password,
            password = true,
            imeAction = ImeAction.Go,
            onDone = { model.login(username, password) },
            leading = Ico.Lock,
        )
        ErrorText(model.formError)
        Spacer(Modifier.height(20.dp))
        GButton(s.login, { model.login(username, password) }, primary = true, busy = model.busy, modifier = Modifier.fillMaxWidth())
        if (model.fingerprintOn) {
            Spacer(Modifier.height(12.dp))
            GButton(s.useFingerprint, model::backToLock, icon = Ico.Fingerprint, modifier = Modifier.fillMaxWidth())
        }
        if (model.status?.passwordLogin == false && !model.fingerprintOn) {
            Spacer(Modifier.height(16.dp))
            Text(s.passwordOffHint, style = G.type.small)
        }
    }
}

@Composable
fun LockScreen(model: AppModel) {
    val s = LocalStrings.current
    // The phone's fingerprint dialog opens by itself when the app opens.
    LaunchedEffect(Unit) { model.unlock() }
    val pulse by rememberInfiniteTransition(label = "lock").animateFloat(
        initialValue = 0.94f,
        targetValue = 1.04f,
        animationSpec = infiniteRepeatable(tween(1600), RepeatMode.Reverse),
        label = "pulse",
    )
    AuthFrame {
        Column(Modifier.fillMaxWidth(), horizontalAlignment = Alignment.CenterHorizontally) {
            Spacer(Modifier.height(24.dp))
            Box(
                Modifier
                    .size(116.dp)
                    .scale(if (model.busy) pulse else 1f)
                    .clip(CircleShape)
                    .background(Palette.accentSoft)
                    .border(1.5.dp, Palette.accentLine, CircleShape)
                    .clickable(role = Role.Button, onClickLabel = s.unlockTitle, onClick = model::unlock),
                contentAlignment = Alignment.Center,
            ) {
                GIcon(Ico.Fingerprint, size = 56.dp, tint = Palette.accent)
            }
            Spacer(Modifier.height(28.dp))
            val name = model.status?.user?.name ?: model.settings.username
            Text(if (name.isNotBlank()) s.hello(name) else s.unlockTitle, style = G.type.title, textAlign = TextAlign.Center)
            Spacer(Modifier.height(8.dp))
            Text(s.unlockHint, style = G.type.body, color = Palette.ink2, textAlign = TextAlign.Center)
            ErrorText(model.formError)
            Spacer(Modifier.height(28.dp))
            GButton(s.unlock, model::unlock, primary = true, busy = model.busy, icon = Ico.Fingerprint, modifier = Modifier.fillMaxWidth())
            Spacer(Modifier.height(12.dp))
            Text(
                s.usePassword,
                style = G.type.bodyStrong,
                color = Palette.accentInk,
                modifier = Modifier.clickable(role = Role.Button, onClick = model::usePassword).padding(10.dp),
            )
        }
    }
}

/** The offer after the first password login: from now on, the fingerprint. */
@Composable
fun FingerprintOffer(model: AppModel) {
    val s = LocalStrings.current
    Column(
        Modifier.fillMaxWidth().padding(horizontal = 24.dp, vertical = 12.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center,
    ) {
        IconBubble(Ico.Fingerprint, Tone.Accent, size = 72.dp)
        Spacer(Modifier.height(20.dp))
        Text(s.offerTitle, style = G.type.heading.copy(fontSize = G.type.big.fontSize * 0.75f), textAlign = TextAlign.Center)
        Spacer(Modifier.height(10.dp))
        Text(s.offerText, style = G.type.body, color = Palette.ink2, textAlign = TextAlign.Center)
        Spacer(Modifier.height(24.dp))
        GButton(s.turnOn, model::enableFingerprint, primary = true, busy = model.busy, icon = Ico.Fingerprint, modifier = Modifier.fillMaxWidth())
        Spacer(Modifier.height(10.dp))
        GButton(s.later, model::declineFingerprint, modifier = Modifier.fillMaxWidth())
        Spacer(Modifier.height(8.dp))
    }
}
