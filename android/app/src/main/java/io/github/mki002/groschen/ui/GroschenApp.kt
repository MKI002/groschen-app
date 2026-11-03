package io.github.mki002.groschen.ui

import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.Crossfade
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.slideOutVertically
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBars
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBars
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.lazy.LazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Text
import androidx.compose.material3.pulltorefresh.PullToRefreshBox
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import io.github.mki002.groschen.model.AppModel
import io.github.mki002.groschen.model.Sheet
import io.github.mki002.groschen.model.Stage
import io.github.mki002.groschen.model.Tab
import io.github.mki002.groschen.ui.components.GIcon
import io.github.mki002.groschen.ui.components.Hairline
import io.github.mki002.groschen.ui.components.Ico
import io.github.mki002.groschen.ui.components.LocalFmt
import io.github.mki002.groschen.ui.components.LocalLogos
import io.github.mki002.groschen.ui.components.LocalStrings
import io.github.mki002.groschen.ui.components.Logo
import io.github.mki002.groschen.ui.components.RoundButton
import io.github.mki002.groschen.ui.components.SheetStack
import io.github.mki002.groschen.ui.screens.ConnectScreen
import io.github.mki002.groschen.ui.screens.LockScreen
import io.github.mki002.groschen.ui.screens.LoginScreen
import io.github.mki002.groschen.ui.screens.OverviewPage
import io.github.mki002.groschen.ui.screens.SheetContent
import io.github.mki002.groschen.ui.screens.SpendingPage
import io.github.mki002.groschen.ui.screens.TransactionsPage
import io.github.mki002.groschen.ui.screens.WealthPage
import io.github.mki002.groschen.ui.theme.G
import io.github.mki002.groschen.ui.theme.GroschenTheme
import io.github.mki002.groschen.ui.theme.Palette
import kotlinx.coroutines.delay

@Composable
fun GroschenApp(model: AppModel, font: FontFamily) {
    GroschenTheme(font) {
        CompositionLocalProvider(LocalStrings provides model.s, LocalFmt provides model.fmt, LocalLogos provides model.logos) {
            Box(Modifier.fillMaxSize().background(Palette.bg)) {
                Crossfade(model.stage, animationSpec = tween(280), label = "stage") { stage ->
                    when (stage) {
                        Stage.Starting -> Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { Logo(size = 64.dp) }
                        Stage.Connect -> ConnectScreen(model)
                        Stage.Login -> LoginScreen(model)
                        Stage.Locked -> LockScreen(model)
                        Stage.Main -> MainScreen(model)
                    }
                }
                ToastHost(model, Modifier.align(Alignment.BottomCenter))
            }
        }
    }
}

@Composable
private fun MainScreen(model: AppModel) {
    val lists = remember { Tab.entries.associateWith { LazyListState() } }
    Box(Modifier.fillMaxSize()) {
        Column(Modifier.fillMaxSize()) {
            TopBar(model)
            Box(Modifier.weight(1f)) {
                AnimatedContent(
                    model.tab,
                    transitionSpec = { fadeIn(tween(220)) togetherWith fadeOut(tween(120)) },
                    label = "tab",
                ) { tab ->
                    LaunchedEffect(tab) { model.ensure(tab) }
                    Page(model, tab, lists.getValue(tab))
                }
            }
            BottomBar(model)
        }
        SheetStack(model.sheets.toList(), keyOf = { it.key }, onDismiss = { model.close() }) { sheet ->
            SheetContent(model, sheet)
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun Page(model: AppModel, tab: Tab, list: LazyListState) {
    val refreshing = when (tab) {
        Tab.Overview -> model.overview.loading && model.overview.value != null
        Tab.Transactions -> model.txLoading && model.transactions.isNotEmpty()
        Tab.Spending -> model.spending.loading && model.spending.value != null
        Tab.Wealth -> model.wealth.loading && model.wealth.value != null
    }
    PullToRefreshBox(isRefreshing = refreshing, onRefresh = { model.refresh(tab) }, modifier = Modifier.fillMaxSize()) {
        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.TopCenter) {
            Box(Modifier.widthIn(max = 720.dp)) {
                when (tab) {
                    Tab.Overview -> OverviewPage(model, list)
                    Tab.Transactions -> TransactionsPage(model, list)
                    Tab.Spending -> SpendingPage(model, list)
                    Tab.Wealth -> WealthPage(model, list)
                }
            }
        }
    }
}

@Composable
private fun TopBar(model: AppModel) {
    val s = LocalStrings.current
    Column(Modifier.background(Palette.bg).windowInsetsPadding(WindowInsets.statusBars)) {
        Row(
            Modifier.fillMaxWidth().padding(start = 16.dp, end = 12.dp, top = 10.dp, bottom = 10.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Logo(size = 30.dp)
            Spacer(Modifier.width(10.dp))
            Text("Groschen", style = G.type.heading.copy(fontSize = G.type.heading.fontSize * 1.12f))
            Spacer(Modifier.weight(1f))
            SyncChip(model)
            Spacer(Modifier.width(8.dp))
            RoundButton(
                if (model.settings.hideAmounts) Ico.EyeOff else Ico.Eye,
                if (model.settings.hideAmounts) s.showAmounts else s.hideAmounts,
                onClick = model::toggleHidden,
                tint = if (model.settings.hideAmounts) Palette.accentInk else Palette.ink2,
            )
            Spacer(Modifier.width(8.dp))
            RoundButton(Ico.Gear, s.settings, onClick = { model.open(Sheet.Settings) })
        }
        Hairline()
    }
}

@Composable
private fun SyncChip(model: AppModel) {
    val s = LocalStrings.current
    val fmt = LocalFmt.current
    val connections = model.overview.value?.connections.orEmpty()
    if (connections.isEmpty() && !model.syncing) return
    val latest = connections.mapNotNull { it.lastSyncAt }.maxOrNull()
    val trouble = connections.any { it.status == "error" || it.lastError != null }
    val shape = RoundedCornerShape(999.dp)
    Row(
        Modifier
            .height(42.dp)
            .clip(shape)
            .background(Palette.surface)
            .border(1.dp, Palette.line2, shape)
            .clickable(role = Role.Button, onClick = { model.open(Sheet.Sync) })
            .padding(horizontal = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        if (model.syncing) {
            CircularProgressIndicator(Modifier.size(12.dp), color = Palette.accent, strokeWidth = 1.6.dp)
        } else {
            Box(Modifier.size(8.dp).clip(CircleShape).background(if (trouble) Palette.warn else Palette.good))
        }
        Spacer(Modifier.width(8.dp))
        Text(if (model.syncing) s.syncing else fmt.ago(latest), style = G.type.small, color = Palette.ink2, maxLines = 1)
    }
}

@Composable
private fun BottomBar(model: AppModel) {
    val s = LocalStrings.current
    val review = (model.overview.value?.badges?.review ?: 0) > 0
    Column(Modifier.background(Palette.bg2)) {
        Hairline()
        Row(
            Modifier.fillMaxWidth().windowInsetsPadding(WindowInsets.navigationBars).padding(vertical = 8.dp),
            horizontalArrangement = Arrangement.SpaceEvenly,
        ) {
            NavItem(s.tabOverview, Ico.Home, model.tab == Tab.Overview, false, Modifier.weight(1f)) { model.tab = Tab.Overview }
            NavItem(s.tabTransactions, Ico.List, model.tab == Tab.Transactions, review, Modifier.weight(1f)) { model.tab = Tab.Transactions }
            NavItem(s.tabSpending, Ico.Pie, model.tab == Tab.Spending, false, Modifier.weight(1f)) { model.tab = Tab.Spending }
            NavItem(s.tabWealth, Ico.Vault, model.tab == Tab.Wealth, false, Modifier.weight(1f)) { model.tab = Tab.Wealth }
        }
    }
}

@Composable
private fun NavItem(label: String, icon: Ico, selected: Boolean, dot: Boolean, modifier: Modifier, onClick: () -> Unit) {
    Column(
        modifier.clickable(role = Role.Tab, onClick = onClick).padding(vertical = 2.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Box(
            Modifier
                .width(58.dp)
                .height(32.dp)
                .clip(RoundedCornerShape(999.dp))
                .background(if (selected) Palette.accentSoft else Palette.bg2),
            contentAlignment = Alignment.Center,
        ) {
            GIcon(icon, size = 22.dp, tint = if (selected) Palette.accentInk else Palette.muted)
            if (dot) {
                Box(
                    Modifier
                        .offset(x = 10.dp, y = (-8).dp)
                        .size(8.dp)
                        .clip(CircleShape)
                        .background(Palette.accent),
                )
            }
        }
        Spacer(Modifier.height(4.dp))
        Text(label, style = G.type.small.copy(fontSize = G.type.label.fontSize), color = if (selected) Palette.ink else Palette.muted, maxLines = 1)
    }
}

@Composable
private fun ToastHost(model: AppModel, modifier: Modifier) {
    val toast = model.toast
    val shown = remember { mutableToast() }
    LaunchedEffect(toast) {
        if (toast != null) {
            shown.value = toast.text
            delay(3200)
            shown.value = null
        }
    }
    AnimatedVisibility(
        shown.value != null,
        modifier = modifier.windowInsetsPadding(WindowInsets.navigationBars).padding(bottom = 86.dp, start = 16.dp, end = 16.dp),
        enter = slideInVertically(tween(260)) { it / 2 } + fadeIn(tween(200)),
        exit = slideOutVertically(tween(200)) { it / 2 } + fadeOut(tween(160)),
    ) {
        Text(
            shown.value ?: "",
            modifier = Modifier
                .clip(RoundedCornerShape(14.dp))
                .background(Palette.surface3)
                .border(1.dp, Palette.line2, RoundedCornerShape(14.dp))
                .padding(horizontal = 16.dp, vertical = 12.dp),
            style = G.type.body,
        )
    }
}

private fun mutableToast() = androidx.compose.runtime.mutableStateOf<String?>(null)
