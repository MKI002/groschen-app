package io.github.mki002.groschen.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.unit.dp
import io.github.mki002.groschen.data.Alert
import io.github.mki002.groschen.data.Available
import io.github.mki002.groschen.data.Cashflow
import io.github.mki002.groschen.i18n.categoryName
import io.github.mki002.groschen.model.AppModel
import io.github.mki002.groschen.model.OverviewData
import io.github.mki002.groschen.model.Sheet
import io.github.mki002.groschen.model.Tab
import io.github.mki002.groschen.ui.components.Dot
import io.github.mki002.groschen.ui.components.ErrorNote
import io.github.mki002.groschen.ui.components.GButton
import io.github.mki002.groschen.ui.components.GCard
import io.github.mki002.groschen.ui.components.GIcon
import io.github.mki002.groschen.ui.components.Hairline
import io.github.mki002.groschen.ui.components.Ico
import io.github.mki002.groschen.ui.components.IconBubble
import io.github.mki002.groschen.ui.components.Label
import io.github.mki002.groschen.ui.components.LocalFmt
import io.github.mki002.groschen.ui.components.LocalStrings
import io.github.mki002.groschen.ui.components.Money
import io.github.mki002.groschen.ui.components.PaydayStrip
import io.github.mki002.groschen.ui.components.Pill
import io.github.mki002.groschen.ui.components.Placeholder
import io.github.mki002.groschen.ui.components.ShareBar
import io.github.mki002.groschen.ui.components.Tone
import io.github.mki002.groschen.ui.components.rememberSentence
import io.github.mki002.groschen.ui.theme.G
import io.github.mki002.groschen.ui.theme.Palette
import java.time.LocalDate
import java.time.temporal.ChronoUnit

@Composable
fun PageHeader(overline: String?, title: String, sub: String? = null, trailing: @Composable () -> Unit = {}) {
    Row(Modifier.fillMaxWidth().padding(top = 14.dp, bottom = 4.dp), verticalAlignment = Alignment.Bottom) {
        Column(Modifier.weight(1f)) {
            if (overline != null) {
                Label(overline)
                Spacer(Modifier.height(6.dp))
            }
            Text(title, style = G.type.title)
            if (sub != null) Text(sub, style = G.type.small)
        }
        trailing()
    }
}

val PagePadding = PaddingValues(start = 16.dp, end = 16.dp, top = 4.dp, bottom = 28.dp)

@Composable
fun OverviewPage(model: AppModel, list: LazyListState) {
    val s = LocalStrings.current
    val fmt = LocalFmt.current
    val state = model.overview
    val data = state.value
    val update = model.appUpdate.cardRelease
    LazyColumn(state = list, contentPadding = PagePadding, verticalArrangement = Arrangement.spacedBy(14.dp)) {
        item { PageHeader(fmt.weekdayToday(), s.tabOverview) }
        if (update != null) item(key = "update") { UpdateCard(model) }
        if (data == null) {
            val error = state.error
            if (error != null) {
                item { ErrorNote(error, model::loadOverview) }
            } else {
                item { Placeholder(height = 300.dp) }
                item { Placeholder(height = 180.dp) }
            }
            return@LazyColumn
        }
        state.error?.let { item { ErrorNote(it, model::loadOverview) } }
        item { HeroCard(model, data.available) }
        item { HintsCard(model, data) }
        data.month?.takeIf { it.incomeTotal > 0 || it.spendingTotal > 0 }?.let { item { MonthCard(model, it) } }
    }
}

@Composable
private fun HeroCard(model: AppModel, a: Available) {
    val s = LocalStrings.current
    val fmt = LocalFmt.current
    GCard(padding = PaddingValues(22.dp)) {
        if (!a.hasAccount) {
            Label(s.availableUntilPayday)
            Spacer(Modifier.height(12.dp))
            Text(s.noCheckingAccount, style = G.type.body, color = Palette.ink2)
            Spacer(Modifier.height(14.dp))
            GButton(s.openWeb, model::openWeb, small = true, icon = Ico.Globe)
            return@GCard
        }
        val free = a.available ?: 0.0
        Label(if (a.payday != null) s.availableUntilPayday else s.availableUntilMonthEnd)
        Spacer(Modifier.height(10.dp))
        Money(free, G.type.hero, color = if (free < 0) Palette.bad else Palette.ink, countUp = true)
        Spacer(Modifier.height(6.dp))
        if (free > 0 && a.perDay != null) {
            val sentence = rememberSentence(Palette.ink, G.type.bodyStrong.fontSize)
            Text(sentence.tpl(s.perDay, "amount" to a.perDay).build(), style = G.type.bodyStrong, color = Palette.ink2)
        } else if (free < 0) {
            Text(s.overspent, style = G.type.body, color = Palette.ink2)
        }

        // The month to payday as a strip of days.
        val since = a.since?.let { runCatching { LocalDate.parse(it.take(10)) }.getOrNull() }
        val until = a.until?.let { runCatching { LocalDate.parse(it.take(10)) }.getOrNull() }
        if (since != null && until != null) {
            val today = LocalDate.now()
            val total = ChronoUnit.DAYS.between(since, until).toInt().coerceAtLeast(1)
            val todayIndex = ChronoUnit.DAYS.between(since, today).toInt().coerceIn(0, total - 1)
            val charges = a.upcoming.mapNotNull { u ->
                runCatching { ChronoUnit.DAYS.between(since, LocalDate.parse(u.date)).toInt() }.getOrNull()
            }.map { it.coerceIn(todayIndex, total - 1) }.toSet()
            Spacer(Modifier.height(22.dp))
            Row(verticalAlignment = Alignment.Bottom) {
                Label(s.today, color = Palette.ink2)
                Text("  ·  ", style = G.type.small, color = Palette.faint)
                Text(
                    (a.days ?: 0).toString(),
                    style = G.type.big.copy(fontSize = G.type.big.fontSize * 0.9f),
                    color = Palette.accentInk,
                )
                Spacer(Modifier.width(8.dp))
                Text(
                    if (a.payday != null) s.daysToPayday(a.days ?: 0) else s.daysToMonthEnd(a.days ?: 0),
                    style = G.type.body,
                    color = Palette.ink2,
                    modifier = Modifier.padding(bottom = 3.dp),
                )
            }
            Spacer(Modifier.height(12.dp))
            Row(verticalAlignment = Alignment.CenterVertically) {
                PaydayStrip(total, todayIndex, charges, Modifier.weight(1f))
                Spacer(Modifier.width(10.dp))
                Box(
                    Modifier
                        .size(34.dp)
                        .clip(CircleShape)
                        .background(Brush.linearGradient(listOf(Palette.accentInk, Palette.accent2)))
                        .border(1.dp, Palette.accentLine, CircleShape),
                    contentAlignment = Alignment.Center,
                ) {
                    GIcon(Ico.Coin, size = 20.dp, tint = Palette.onAccent)
                }
            }
            Spacer(Modifier.height(8.dp))
            Row {
                val payday = a.payday
                Text(
                    if (payday?.last != null) "${s.salary} ${fmt.dayMonth(payday.last)}" else fmt.dayMonth(a.since),
                    style = G.type.small,
                )
                Spacer(Modifier.weight(1f))
                Text(fmt.dayMonth(payday?.date ?: a.until), style = G.type.small)
                Spacer(Modifier.width(44.dp))
            }
        }

        Spacer(Modifier.height(16.dp))
        Hairline()
        Spacer(Modifier.height(14.dp))
        if (a.upcoming.isNotEmpty()) {
            val sentence = rememberSentence(Palette.accentInk, G.type.bodyStrong.fontSize)
            Row(
                Modifier.fillMaxWidth().clickable(role = Role.Button) { model.open(Sheet.Upcoming) }.padding(vertical = 4.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    sentence.text(s.paymentsToCome(a.upcoming.size)).text(" · ").money(a.fixedTotal).build(),
                    style = G.type.bodyStrong,
                    color = Palette.accentInk,
                    modifier = Modifier.weight(1f),
                )
                GIcon(Ico.ChevRight, size = 16.dp, tint = Palette.accentInk)
            }
        } else {
            Text(s.nothingMoreToCome, style = G.type.small)
        }
        if ((a.balanceAgeDays ?: 0) >= 2) {
            Spacer(Modifier.height(10.dp))
            Row(verticalAlignment = Alignment.CenterVertically) {
                GIcon(Ico.Clock, size = 15.dp, tint = Palette.warn)
                Spacer(Modifier.width(8.dp))
                Text(s.balanceFrom(fmt.date(a.balanceDate)), style = G.type.small, color = Palette.warn)
            }
        }
        if (a.buffer > 0) {
            Spacer(Modifier.height(8.dp))
            val sentence = rememberSentence(Palette.muted, G.type.small.fontSize)
            Text(sentence.tpl(s.bufferNote, "amount" to a.buffer).build(), style = G.type.small)
        }
    }
}

@Composable
private fun HintsCard(model: AppModel, data: OverviewData) {
    val s = LocalStrings.current
    val review = data.badges.review
    val count = data.alerts.size + if (review > 0) 1 else 0
    GCard {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(s.worthALook, style = G.type.heading, modifier = Modifier.weight(1f))
            if (count > 0) Pill(count.toString(), Tone.Accent)
        }
        if (count == 0) {
            Spacer(Modifier.height(14.dp))
            Row(verticalAlignment = Alignment.CenterVertically) {
                IconBubble(Ico.Check, Tone.Good, size = 36.dp)
                Spacer(Modifier.width(14.dp))
                Text(s.allCalm, style = G.type.body, color = Palette.ink2)
            }
            return@GCard
        }
        if (review > 0) {
            val sentence = rememberSentence(Palette.ink)
            HintRow(
                icon = Ico.List,
                tone = Tone.Accent,
                text = { Text(sentence.bold(s.reviewHint(review)).text(s.reviewHintMore).build(), style = G.type.body, color = Palette.muted) },
                action = s.check,
                onAction = model::reviewTransactions,
                onDismiss = null,
            )
        }
        for (alert in data.alerts) {
            val (icon, tone) = alertLook(alert.kind)
            HintRow(
                icon = icon,
                tone = tone,
                text = { AlertText(alert) },
                action = s.show,
                onAction = {
                    when (alert.kind) {
                        "duplicate", "unusual" -> {
                            model.tab = Tab.Transactions
                            model.searchTransactions(alert.name.orEmpty())
                        }
                        else -> {
                            if (model.fixed.value == null) model.loadFixed()
                            model.open(Sheet.FixedCosts)
                        }
                    }
                },
                onDismiss = { model.dismissAlert(alert) },
            )
        }
    }
}

private fun alertLook(kind: String): Pair<Ico, Tone> = when (kind) {
    "duplicate" -> Ico.Repeat to Tone.Bad
    "unusual" -> Ico.Warn to Tone.Warn
    "price_up" -> Ico.Up to Tone.Warn
    "price_down" -> Ico.Down to Tone.Good
    "sub_new" -> Ico.Spark to Tone.Info
    "sub_ended" -> Ico.Ban to Tone.Muted
    "sub_resumed" -> Ico.Play to Tone.Info
    else -> Ico.Spark to Tone.Info
}

@Composable
private fun AlertText(a: Alert) {
    val s = LocalStrings.current
    val fmt = LocalFmt.current
    val t = rememberSentence(Palette.ink)
    val name = a.name.orEmpty()
    when (a.kind) {
        "duplicate" -> t.tpl(s.hintDup, "name" to name, "amount" to a.amount, bold = true)
            .tpl(s.hintDupMore, "first" to fmt.date(a.firstDate), "second" to fmt.date(a.date))
        "unusual" -> {
            t.tpl(s.hintBig, "amount" to a.amount, "name" to name, bold = true).tpl(s.hintBigOn, "date" to fmt.date(a.date))
            when (a.basis) {
                "new" -> t.text(s.hintNew)
                "merchant" -> t.tpl(s.hintUsual, "amount" to a.usual)
                else -> t.tpl(
                    s.hintUsualCat,
                    "amount" to a.usual,
                    "category" to (a.category?.let { categoryName(it, fmt.lang) } ?: s.thisCategory),
                )
            }
        }
        "price_up", "price_down" -> {
            val up = a.kind == "price_up"
            t.tpl(if (up) s.hintPrice else s.hintCheaper, "name" to name, bold = true)
                .tpl(
                    if (up) s.hintPriceMore else s.hintCheaperMore,
                    "from" to a.from,
                    "to" to a.to,
                    "date" to fmt.date(a.date),
                    "year" to kotlin.math.abs(a.perYear ?: 0.0),
                )
        }
        "sub_new" -> t.tpl(s.hintSubNew, "name" to name, bold = true).tpl(
            s.hintSubNewMore,
            "amount" to a.amount,
            "interval" to fmt.interval(a.interval),
            "date" to fmt.date(a.since ?: a.date),
        )
        "sub_ended" -> t.tpl(s.hintSubEnded, "name" to name, bold = true).tpl(
            s.hintSubEndedMore,
            "amount" to a.amount,
            "date" to fmt.date(a.lastDate ?: a.date),
            "year" to (a.monthlyCost ?: 0.0) * 12,
        )
        else -> t.tpl(s.hintSubResumed, "name" to name, bold = true).tpl(
            s.hintSubResumedMore,
            "pause" to fmt.span(a.pauseDays ?: 0),
            "amount" to a.amount,
            "interval" to fmt.interval(a.interval),
        )
    }
    Text(t.build(), style = G.type.body, color = Palette.muted)
}

@Composable
private fun HintRow(
    icon: Ico,
    tone: Tone,
    text: @Composable () -> Unit,
    action: String,
    onAction: () -> Unit,
    onDismiss: (() -> Unit)?,
) {
    val s = LocalStrings.current
    Spacer(Modifier.height(16.dp))
    Row(verticalAlignment = Alignment.Top) {
        IconBubble(icon, tone, size = 38.dp)
        Spacer(Modifier.width(14.dp))
        Column(Modifier.weight(1f)) {
            text()
            Spacer(Modifier.height(10.dp))
            GButton(action, onAction, small = true, trailing = Ico.ChevRight)
        }
        if (onDismiss != null) {
            Spacer(Modifier.width(6.dp))
            Box(
                Modifier
                    .size(32.dp)
                    .clip(CircleShape)
                    .clickable(role = Role.Button, onClickLabel = s.hideHint, onClick = onDismiss),
                contentAlignment = Alignment.Center,
            ) {
                GIcon(Ico.X, size = 15.dp, tint = Palette.faint)
            }
        }
    }
}

@Composable
private fun MonthCard(model: AppModel, c: Cashflow) {
    val s = LocalStrings.current
    val fmt = LocalFmt.current
    GCard(onClick = { model.tab = Tab.Spending }) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Label(s.monthSoFar(fmt.monthName(c.range.start)), Modifier.weight(1f))
            GIcon(Ico.ChevRight, size = 16.dp, tint = Palette.muted)
        }
        Spacer(Modifier.height(14.dp))
        val saved = c.saved.coerceAtLeast(0.0)
        ShareBar(listOf(c.spendingTotal.toFloat() to Palette.spend, saved.toFloat() to Palette.good), height = 10.dp)
        Spacer(Modifier.height(14.dp))
        LegendRow(Palette.spend, s.spent, c.spendingTotal)
        if (c.saved >= 0) LegendRow(Palette.good, s.leftOver, c.saved) else LegendRow(Palette.bad, s.overIncome, -c.saved)
        LegendRow(Palette.faint, s.income, c.incomeTotal, muted = true)
    }
}

@Composable
private fun LegendRow(color: androidx.compose.ui.graphics.Color, label: String, value: Double, muted: Boolean = false) {
    Row(Modifier.fillMaxWidth().padding(vertical = 4.dp), verticalAlignment = Alignment.CenterVertically) {
        Dot(color)
        Spacer(Modifier.width(10.dp))
        Text(label, style = G.type.body, color = if (muted) Palette.muted else Palette.ink2, modifier = Modifier.weight(1f))
        Money(value, G.type.number, color = if (muted) Palette.muted else Palette.ink)
    }
}
