package io.github.mki002.groschen.ui.screens

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.width
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.unit.dp
import io.github.mki002.groschen.data.AppRelease
import io.github.mki002.groschen.model.AppModel
import io.github.mki002.groschen.model.AppUpdate
import io.github.mki002.groschen.ui.components.GButton
import io.github.mki002.groschen.ui.components.GCard
import io.github.mki002.groschen.ui.components.GSwitch
import io.github.mki002.groschen.ui.components.Hairline
import io.github.mki002.groschen.ui.components.Ico
import io.github.mki002.groschen.ui.components.IconBubble
import io.github.mki002.groschen.ui.components.Label
import io.github.mki002.groschen.ui.components.LocalStrings
import io.github.mki002.groschen.ui.components.SettingRow
import io.github.mki002.groschen.ui.components.Tone
import io.github.mki002.groschen.ui.theme.G
import io.github.mki002.groschen.ui.theme.Palette

/** The version an update card is about, if the Overview shows one. */
val AppUpdate.cardRelease: AppRelease?
    get() = when (this) {
        is AppUpdate.Found -> release
        is AppUpdate.Downloading -> release
        is AppUpdate.Ready -> release
        is AppUpdate.Installing -> release
        is AppUpdate.Failed -> release
        else -> null
    }

/** A new version on GitHub, on top of the Overview: what it is and the one thing to do next. */
@Composable
fun UpdateCard(model: AppModel) {
    val s = LocalStrings.current
    val update = model.appUpdate
    val release = update.cardRelease ?: return
    GCard {
        Row(verticalAlignment = Alignment.CenterVertically) {
            IconBubble(Ico.Download, if (update is AppUpdate.Failed) Tone.Warn else Tone.Accent, size = 36.dp)
            Spacer(Modifier.width(14.dp))
            Column(Modifier.weight(1f)) {
                Text(s.updateFound(release.versionName), style = G.type.bodyStrong)
                Text(
                    when (update) {
                        is AppUpdate.Found -> s.updateOnMobileData
                        is AppUpdate.Downloading -> s.updateDownloading
                        is AppUpdate.Ready -> s.updateReady
                        is AppUpdate.Installing -> s.updateInstalling
                        is AppUpdate.Failed -> update.message
                        else -> ""
                    },
                    style = G.type.small,
                )
            }
        }
        if (update is AppUpdate.Downloading) {
            Spacer(Modifier.height(14.dp))
            ProgressLine(update.progress)
        }
        if (update !is AppUpdate.Downloading && update !is AppUpdate.Installing) {
            Spacer(Modifier.height(14.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                when (update) {
                    is AppUpdate.Ready -> GButton(s.updateInstall, model::installUpdate, primary = true, small = true, icon = Ico.Download)
                    else -> GButton(s.updateDownload, model::downloadUpdate, primary = true, small = true, icon = Ico.Download)
                }
                GButton(s.onGitHub, model::openReleasePage, small = true, icon = Ico.Globe)
            }
        }
    }
}

@Composable
private fun ProgressLine(progress: Float) {
    val shown by animateFloatAsState(progress.coerceIn(0f, 1f), label = "download")
    Canvas(Modifier.fillMaxWidth().height(6.dp)) {
        val radius = CornerRadius(size.height / 2)
        drawRoundRect(Palette.surface3, size = size, cornerRadius = radius)
        drawRoundRect(Palette.accent, size = Size(size.width * shown, size.height), cornerRadius = radius)
    }
}

/** The updates part of the app's settings. */
@Composable
fun UpdateSettings(model: AppModel) {
    val s = LocalStrings.current
    Label(s.updates)
    GCard(padding = PaddingValues(horizontal = 16.dp, vertical = 2.dp)) {
        if (!model.updatesPossible) {
            SettingRow(s.versionLine(model.appVersion), s.updatesOwnBuild, icon = Ico.Download)
            return@GCard
        }
        SettingRow(s.updateCheck, s.updateCheckSub, icon = Ico.Download) {
            GSwitch(model.settings.updateCheck, model::setUpdateCheck)
        }
        Hairline()
        val update = model.appUpdate
        val status = when (update) {
            AppUpdate.Checking -> s.updateChecking
            AppUpdate.UpToDate -> s.upToDate
            is AppUpdate.Failed -> update.message
            else -> update.cardRelease?.let { s.updateFound(it.versionName) }
        }
        SettingRow(s.versionLine(model.appVersion), status) {
            when (update) {
                is AppUpdate.Ready -> GButton(s.updateInstall, model::installUpdate, primary = true, small = true)
                is AppUpdate.Found -> GButton(s.updateDownload, model::downloadUpdate, primary = true, small = true)
                is AppUpdate.Downloading, is AppUpdate.Installing -> GButton(s.checkNow, {}, small = true, busy = true, enabled = false)
                else -> GButton(s.checkNow, { model.checkForUpdate() }, small = true, busy = update == AppUpdate.Checking)
            }
        }
    }
}
