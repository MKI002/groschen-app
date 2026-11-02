package io.github.mki002.groschen.ui.screens

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import io.github.mki002.groschen.data.Connection
import io.github.mki002.groschen.data.Job
import io.github.mki002.groschen.model.AppModel
import io.github.mki002.groschen.model.Sheet
import io.github.mki002.groschen.ui.components.ChoiceChip
import io.github.mki002.groschen.ui.components.GButton
import io.github.mki002.groschen.ui.components.GCard
import io.github.mki002.groschen.ui.components.GField
import io.github.mki002.groschen.ui.components.GIcon
import io.github.mki002.groschen.ui.components.GSwitch
import io.github.mki002.groschen.ui.components.Hairline
import io.github.mki002.groschen.ui.components.Ico
import io.github.mki002.groschen.ui.components.IconBubble
import io.github.mki002.groschen.ui.components.Label
import io.github.mki002.groschen.ui.components.LocalFmt
import io.github.mki002.groschen.ui.components.LocalStrings
import io.github.mki002.groschen.ui.components.SettingRow
import io.github.mki002.groschen.ui.components.SheetBody
import io.github.mki002.groschen.ui.components.Tone
import io.github.mki002.groschen.ui.theme.G
import io.github.mki002.groschen.ui.theme.Palette

/** Which sheet shows what. */
@Composable
fun ColumnScope.SheetContent(model: AppModel, sheet: Sheet) {
    when (sheet) {
        Sheet.Settings -> SettingsSheet(model)
        Sheet.Sync -> SyncSheet(model)
        Sheet.Upcoming -> UpcomingSheet(model)
        Sheet.FixedCosts -> FixedCostsSheet(model)
        Sheet.Fingerprint -> FingerprintOffer(model)
        is Sheet.Tx -> TransactionSheet(model, sheet.tx)
        is Sheet.Holding -> HoldingSheet(model, sheet.isin)
        is Sheet.Group -> GroupSheet(model, sheet.name)
    }
}

@Composable
private fun ColumnScope.SettingsSheet(model: AppModel) {
    val s = LocalStrings.current
    var confirmServer by remember { mutableStateOf(false) }
    SheetBody(Modifier.weight(1f, fill = false).verticalScrollable()) {
        Text(s.settings, style = G.type.title)
        Spacer(Modifier.height(16.dp))

        // The server.
        Label(s.server)
        GCard(padding = PaddingValues(horizontal = 16.dp, vertical = 2.dp)) {
            SettingRow(
                model.serverLabel,
                if (model.serverEncrypted) s.encrypted else s.unencryptedLan,
                icon = if (model.serverEncrypted) Ico.Lock else Ico.Server,
            ) {
                model.status?.version?.takeIf { it.isNotBlank() }?.let { Text("v$it", style = G.type.small) }
            }
            Hairline()
            SettingRow(s.openWeb, s.openWebSub, onClick = model::openWeb, icon = Ico.Globe) {
                GIcon(Ico.ChevRight, size = 15.dp, tint = Palette.faint)
            }
        }
        Spacer(Modifier.height(18.dp))

        // Logging in.
        Label(s.login)
        GCard(padding = PaddingValues(horizontal = 16.dp, vertical = 2.dp)) {
            val name = model.status?.user?.name?.takeIf { it.isNotBlank() } ?: model.settings.username
            if (name.isNotBlank()) {
                SettingRow(s.loggedInAs(name), null, icon = Ico.Tag)
                Hairline()
            }
            SettingRow(s.fingerprintLogin, if (model.fingerprintOn) s.fingerprintOnSub else s.fingerprintOffSub, icon = Ico.Fingerprint) {
                GSwitch(model.fingerprintOn, { on -> if (on) model.enableFingerprint() else model.disableFingerprint() }, enabled = !model.busy)
            }
            if (model.fingerprintOn) {
                Hairline()
                Column(Modifier.padding(vertical = 12.dp)) {
                    Text(s.lockAfter, style = G.type.bodyStrong)
                    Spacer(Modifier.height(10.dp))
                    Row(Modifier.horizontalScroll(rememberScrollState()), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        for (sec in AppModel.LOCK_CHOICES) {
                            ChoiceChip(s.lockChoice(sec), model.settings.lockAfterSeconds == sec, { model.setLockAfter(sec) })
                        }
                    }
                }
            }
            Hairline()
            SettingRow(s.logout, null, onClick = model::logout, icon = Ico.Logout)
        }
        Spacer(Modifier.height(18.dp))

        // How the app looks.
        Label(s.display)
        GCard(padding = PaddingValues(horizontal = 16.dp, vertical = 2.dp)) {
            SettingRow(s.hideAmounts, s.hideAmountsSub, icon = Ico.EyeOff) {
                GSwitch(model.settings.hideAmounts, { model.toggleHidden() })
            }
            Hairline()
            Column(Modifier.padding(vertical = 12.dp)) {
                Text(s.language, style = G.type.bodyStrong)
                Spacer(Modifier.height(10.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    for (code in listOf("auto", "de", "en")) {
                        ChoiceChip(s.languageName(code), model.settings.language == code, { model.setLanguage(code) })
                    }
                }
            }
        }
        Spacer(Modifier.height(18.dp))

        // Another server.
        if (!confirmServer) {
            GButton(s.changeServer, { confirmServer = true }, icon = Ico.Server, modifier = Modifier.fillMaxWidth())
        } else {
            GCard {
                Text(s.changeServerConfirm, style = G.type.body, color = Palette.ink2)
                Spacer(Modifier.height(12.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    GButton(s.changeServer, model::changeServer, primary = true, small = true)
                    GButton(s.cancel, { confirmServer = false }, small = true)
                }
            }
        }
        Spacer(Modifier.height(16.dp))
        Text(s.versionLine(model.appVersion), style = G.type.small, modifier = Modifier.fillMaxWidth())
        Spacer(Modifier.height(4.dp))
        Text(s.moreInWeb, style = G.type.small)
    }
}

@Composable
private fun ColumnScope.SyncSheet(model: AppModel) {
    val s = LocalStrings.current
    val connections = model.overview.value?.connections.orEmpty()
    SheetBody(Modifier.weight(1f, fill = false).verticalScrollable()) {
        Text(s.bankSync, style = G.type.title)
        Spacer(Modifier.height(6.dp))
        Text(s.bankSyncText, style = G.type.body, color = Palette.muted)
        Spacer(Modifier.height(16.dp))
        if (connections.isNotEmpty()) {
            GCard(padding = PaddingValues(horizontal = 16.dp, vertical = 2.dp)) {
                for ((i, c) in connections.withIndex()) {
                    if (i > 0) Hairline()
                    ConnectionRow(c)
                }
            }
            Spacer(Modifier.height(16.dp))
        }
        val job = model.syncJob
        if (job != null && (model.syncing || job.state == "done")) {
            SyncProgress(model, job)
            Spacer(Modifier.height(16.dp))
        }
        model.syncError?.let {
            Row(verticalAlignment = Alignment.Top) {
                GIcon(Ico.Warn, size = 16.dp, tint = Palette.bad, modifier = Modifier.padding(top = 2.dp))
                Spacer(Modifier.width(8.dp))
                Text(it, style = G.type.body, color = Palette.bad)
            }
            Spacer(Modifier.height(14.dp))
        }
        if (connections.isEmpty()) {
            Text(s.noBankYet, style = G.type.body, color = Palette.ink2)
            Spacer(Modifier.height(12.dp))
            GButton(s.openWeb, model::openWeb, icon = Ico.Globe, modifier = Modifier.fillMaxWidth())
        } else {
            GButton(
                if (model.syncing) s.syncing else s.syncNow,
                model::startSync,
                primary = true,
                busy = model.syncing,
                enabled = !model.syncing,
                icon = Ico.Refresh,
                modifier = Modifier.fillMaxWidth(),
            )
        }
        Spacer(Modifier.height(12.dp))
        Text(s.syncNote, style = G.type.small)
    }
}

@Composable
private fun ConnectionRow(c: Connection) {
    val s = LocalStrings.current
    val fmt = LocalFmt.current
    val trouble = c.status == "error" || c.lastError != null
    Row(Modifier.fillMaxWidth().padding(vertical = 12.dp), verticalAlignment = Alignment.CenterVertically) {
        IconBubble(Ico.Bank, if (trouble) Tone.Warn else Tone.Muted, size = 36.dp)
        Spacer(Modifier.width(12.dp))
        Column(Modifier.weight(1f)) {
            Text(c.label ?: c.bankName ?: s.bank, style = G.type.bodyStrong, maxLines = 1, overflow = TextOverflow.Ellipsis)
            Text(s.lastSync(fmt.ago(c.lastSyncAt)), style = G.type.small, maxLines = 1)
            c.loginDaysLeft?.let { days ->
                Text(s.loginDaysLeft(days), style = G.type.small, color = if (days <= 7) Palette.warn else Palette.muted)
            }
            c.lastError?.let { Text(it, style = G.type.small, color = Palette.warn, maxLines = 3) }
        }
    }
}

@Composable
private fun SyncProgress(model: AppModel, job: Job) {
    val s = LocalStrings.current
    GCard(padding = PaddingValues(16.dp)) {
        if (job.message.isNotBlank()) {
            Text(job.message, style = G.type.bodyStrong)
            Spacer(Modifier.height(10.dp))
        }
        for (step in job.steps) {
            Row(Modifier.padding(vertical = 5.dp), verticalAlignment = Alignment.CenterVertically) {
                Box(Modifier.size(18.dp), contentAlignment = Alignment.Center) {
                    when (step.state) {
                        "done" -> GIcon(Ico.Check, size = 15.dp, tint = Palette.good)
                        "running", "active" -> CircularProgressIndicator(Modifier.size(13.dp), color = Palette.accent, strokeWidth = 1.6.dp)
                        "error", "failed" -> GIcon(Ico.X, size = 14.dp, tint = Palette.bad)
                        else -> Box(Modifier.size(6.dp).clip(RoundedCornerShape(3.dp)).background(Palette.faint))
                    }
                }
                Spacer(Modifier.width(10.dp))
                Text(step.label, style = G.type.body, color = if (step.state == "pending") Palette.muted else Palette.ink2)
            }
        }
        val tan = job.tan
        if (job.state == "waiting" && tan == null) {
            Spacer(Modifier.height(10.dp))
            Row(verticalAlignment = Alignment.CenterVertically) {
                GIcon(Ico.Fingerprint, size = 16.dp, tint = Palette.accentInk)
                Spacer(Modifier.width(8.dp))
                Text(s.confirmInBankApp, style = G.type.body, color = Palette.accentInk)
            }
        }
        if (tan != null) {
            Spacer(Modifier.height(12.dp))
            Hairline()
            Spacer(Modifier.height(12.dp))
            TanPrompt(model, tan.text, tan.image)
        }
    }
}

@Composable
private fun TanPrompt(model: AppModel, text: String, image: String?) {
    val s = LocalStrings.current
    var tan by remember { mutableStateOf("") }
    Text(s.tanTitle, style = G.type.heading)
    Spacer(Modifier.height(6.dp))
    Text(text.ifBlank { s.tanText }, style = G.type.body, color = Palette.ink2)
    val bitmap = remember(image) { model.tanImage(image) }
    if (bitmap != null) {
        Spacer(Modifier.height(12.dp))
        Image(
            bitmap,
            contentDescription = s.tanTitle,
            modifier = Modifier.fillMaxWidth().heightIn(max = 260.dp).clip(RoundedCornerShape(12.dp)).background(Palette.ink),
            contentScale = ContentScale.Fit,
        )
    }
    Spacer(Modifier.height(12.dp))
    GField(tan, { tan = it.trim() }, s.tanLabel, keyboard = KeyboardType.Number, imeAction = ImeAction.Send, onDone = {
        if (tan.isNotBlank()) model.answerTan(tan)
    })
    Spacer(Modifier.height(12.dp))
    Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
        GButton(s.tanSend, { model.answerTan(tan) }, primary = true, small = true, enabled = tan.isNotBlank())
        GButton(s.cancel, { model.answerTan(null) }, small = true)
    }
}
