package io.github.mki002.groschen.ui.screens

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.tween
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyListState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import io.github.mki002.groschen.data.Cashflow
import io.github.mki002.groschen.data.FixedCost
import io.github.mki002.groschen.data.FixedCosts
import io.github.mki002.groschen.data.SpendGroup
import io.github.mki002.groschen.i18n.categoryName
import io.github.mki002.groschen.model.AppModel
import io.github.mki002.groschen.model.Sheet
import io.github.mki002.groschen.model.Tab
import io.github.mki002.groschen.ui.components.ChoiceChip
import io.github.mki002.groschen.ui.components.Dot
import io.github.mki002.groschen.ui.components.EmptyNote
import io.github.mki002.groschen.ui.components.ErrorNote
import io.github.mki002.groschen.ui.components.GButton
import io.github.mki002.groschen.ui.components.GCard
import io.github.mki002.groschen.ui.components.GIcon
import io.github.mki002.groschen.ui.components.Hairline
import io.github.mki002.groschen.ui.components.Ico
import io.github.mki002.groschen.ui.components.Initial
import io.github.mki002.groschen.ui.components.Label
import io.github.mki002.groschen.ui.components.LocalFmt
import io.github.mki002.groschen.ui.components.LocalStrings
import io.github.mki002.groschen.ui.components.Money
import io.github.mki002.groschen.ui.components.Pill
import io.github.mki002.groschen.ui.components.Placeholder
import io.github.mki002.groschen.ui.components.ShareBar
import io.github.mki002.groschen.ui.components.SheetBody
import io.github.mki002.groschen.ui.components.Tone
import io.github.mki002.groschen.ui.components.rememberSentence
import io.github.mki002.groschen.ui.theme.G
import io.github.mki002.groschen.ui.theme.Palette

val SPEND_PRESETS = listOf("month", "last30", "ytd", "last12")

@Composable
fun SpendingPage(model: AppModel, list: LazyListState) {
    val s = LocalStrings.current
    val state = model.spending
    val data = state.value
    LazyColumn(state = list, contentPadding = PagePadding, verticalArrangement = Arrangement.spacedBy(14.dp)) {
        item { PageHeader(data?.range?.label?.uppercase(), s.tabSpending) }
        item {
            Row(Modifier.horizontalScroll(rememberScrollState()), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                for (p in SPEND_PRESETS) ChoiceChip(s.period(p), model.spendPreset == p, { model.setSpendingPeriod(p) })
            }
        }
        if (data == null) {
            val error = state.error
            if (error != null) item { ErrorNote(error, model::loadSpending) } else item { Placeholder(height = 360.dp) }
        } else {
            state.error?.let { item { ErrorNote(it, model::loadSpending) } }
            item { SpendingCard(model, data) }
        }
        item { FixedCard(model) }
    }
}

@Composable
private fun SpendingCard(model: AppModel, c: Cashflow) {
    val s = LocalStrings.current
    val fmt = LocalFmt.current
    GCard(padding = PaddingValues(20.dp)) {
        Label(s.spent)
        Spacer(Modifier.height(8.dp))
        Money(c.spendingTotal, G.type.big.copy(fontSize = G.type.hero.fontSize * 0.82f), countUp = true)
        Spacer(Modifier.height(6.dp))
        val sentence = rememberSentence(Palette.ink, G.type.body.fontSize)
        if (c.incomeTotal > 0) {
            sentence.tpl(s.ofIncome, "amount" to c.incomeTotal)
            if (c.saved >= 0) sentence.tpl(s.leftOverSentence, "amount" to c.saved) else sentence.tpl(s.overSentence, "amount" to -c.saved)
        }
        if (c.months > 1) {
            if (c.incomeTotal > 0) sentence.text(" ")
            sentence.tpl(s.perMonthSentence, "amount" to c.avgSpending)
        }
        Text(sentence.build(), style = G.type.body, color = Palette.muted)

        val groups = c.groups.filter { it.amount > 0 }
        if (groups.isEmpty()) {
            EmptyNote(s.noSpending, icon = Ico.Pie)
            return@GCard
        }
        Spacer(Modifier.height(18.dp))
        val grow = remember(c) { Animatable(0f) }
        LaunchedEffect(c) { grow.animateTo(1f, tween(700)) }
        ShareBar(groups.map { it.amount.toFloat() to Palette.category(it.color) }, height = 12.dp, progress = grow.value)
        Spacer(Modifier.height(10.dp))
        for ((i, g) in groups.withIndex()) {
            if (i > 0) Hairline()
            GroupRow(g) { model.open(Sheet.Group(g.name)) }
        }
        if (c.transactionCount > 0) {
            Spacer(Modifier.height(6.dp))
            Text(s.fromBookings(c.transactionCount), style = G.type.small)
        }
    }
}

@Composable
private fun GroupRow(g: SpendGroup, onClick: () -> Unit) {
    val fmt = LocalFmt.current
    Row(
        Modifier.fillMaxWidth().clickable(role = Role.Button, onClick = onClick).padding(vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Dot(Palette.category(g.color), size = 10.dp)
        Spacer(Modifier.width(12.dp))
        Column(Modifier.weight(1f)) {
            Text(categoryName(g.name, fmt.lang), style = G.type.bodyStrong, maxLines = 1, overflow = TextOverflow.Ellipsis)
            Text(fmt.pct(g.share, digits = 0), style = G.type.small)
        }
        Money(g.amount, G.type.number)
        Spacer(Modifier.width(8.dp))
        GIcon(Ico.ChevRight, size = 15.dp, tint = Palette.faint)
    }
}

@Composable
private fun FixedCard(model: AppModel) {
    val s = LocalStrings.current
    val fmt = LocalFmt.current
    val state = model.fixed
    val data = state.value
    if (data == null) {
        val error = state.error
        if (error != null) ErrorNote(error, model::loadFixed) else Placeholder(height = 200.dp)
        return
    }
    GCard(onClick = { model.open(Sheet.FixedCosts) }) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(s.fixedCosts, style = G.type.heading, modifier = Modifier.weight(1f))
            GIcon(Ico.ChevRight, size = 16.dp, tint = Palette.muted)
        }
        Spacer(Modifier.height(6.dp))
        if (data.items.isEmpty()) {
            Text(s.noFixedCosts, style = G.type.body, color = Palette.muted)
            return@GCard
        }
        val sentence = rememberSentence(Palette.ink, G.type.body.fontSize)
        Text(
            sentence.tpl(s.fixedSentence, "count" to data.items.size.toString(), "amount" to data.monthly, bold = true).build(),
            style = G.type.body,
            color = Palette.muted,
        )
        Spacer(Modifier.height(10.dp))
        val next = data.items.filter { it.nextDate != null }.sortedBy { it.nextDate }.take(3)
        for ((i, f) in next.withIndex()) {
            if (i > 0) Hairline()
            FixedRow(f, showNext = true)
        }
        val changed = data.items.count { kotlin.math.abs(it.priceChange) > 0.004 }
        if (changed > 0) {
            Spacer(Modifier.height(8.dp))
            Pill(s.priceChanges(changed), Tone.Warn)
        }
    }
}

@Composable
private fun FixedRow(f: FixedCost, showNext: Boolean) {
    val s = LocalStrings.current
    val fmt = LocalFmt.current
    Row(Modifier.fillMaxWidth().padding(vertical = 11.dp), verticalAlignment = Alignment.CenterVertically) {
        Initial(f.name, Palette.category(null).takeIf { f.status != "active" } ?: Palette.accent2, size = 34.dp)
        Spacer(Modifier.width(12.dp))
        Column(Modifier.weight(1f)) {
            Text(f.name, style = G.type.bodyStrong, maxLines = 1, overflow = TextOverflow.Ellipsis)
            val sub = when {
                f.status != "active" -> s.endedOn(fmt.date(f.lastDate))
                showNext && f.nextDate != null -> "${fmt.interval(f.interval)} · ${s.next} ${fmt.relDay(f.nextDate)}"
                else -> fmt.interval(f.interval)
            }
            Text(sub, style = G.type.small, maxLines = 1, overflow = TextOverflow.Ellipsis)
        }
        Spacer(Modifier.width(10.dp))
        Column(horizontalAlignment = Alignment.End) {
            Money(f.amount, G.type.number, color = if (f.status == "active") Palette.ink else Palette.muted)
            if (kotlin.math.abs(f.priceChange) > 0.004 && f.status == "active") {
                val up = f.priceChange > 0
                Row(verticalAlignment = Alignment.CenterVertically) {
                    GIcon(if (up) Ico.Up else Ico.Down, size = 12.dp, tint = if (up) Palette.warn else Palette.good)
                    Spacer(Modifier.width(3.dp))
                    Money(kotlin.math.abs(f.priceChange), G.type.small, color = if (up) Palette.warn else Palette.good)
                }
            } else if (f.varies) {
                Text(s.varies, style = G.type.small)
            }
        }
    }
}

/** All fixed costs, the next one first. */
@Composable
fun ColumnScope.FixedCostsSheet(model: AppModel) {
    val s = LocalStrings.current
    val data: FixedCosts? = model.fixed.value
    SheetBody(Modifier.weight(1f, fill = false).verticalScrollable()) {
        Text(s.fixedCosts, style = G.type.title)
        if (data == null) {
            Spacer(Modifier.height(14.dp))
            val error = model.fixed.error
            if (error != null) ErrorNote(error, model::loadFixed) else Placeholder(height = 240.dp)
            return@SheetBody
        }
        Spacer(Modifier.height(6.dp))
        val sentence = rememberSentence(Palette.ink, G.type.body.fontSize)
        Text(
            sentence.tpl(s.fixedPerMonthYear, "month" to data.monthly, "year" to data.yearly, bold = true).build(),
            style = G.type.body,
            color = Palette.muted,
        )
        Spacer(Modifier.height(14.dp))
        if (data.items.isEmpty()) {
            EmptyNote(s.noFixedCosts, icon = Ico.Repeat)
        } else {
            GCard(padding = PaddingValues(horizontal = 14.dp, vertical = 2.dp)) {
                val sorted = data.items.sortedWith(compareBy(nullsLast<String>()) { it.nextDate })
                for ((i, f) in sorted.withIndex()) {
                    if (i > 0) Hairline()
                    FixedRow(f, showNext = true)
                }
            }
        }
        if (data.ended.isNotEmpty()) {
            Spacer(Modifier.height(18.dp))
            Label(s.ended)
            Spacer(Modifier.height(8.dp))
            GCard(padding = PaddingValues(horizontal = 14.dp, vertical = 2.dp)) {
                for ((i, f) in data.ended.take(12).withIndex()) {
                    if (i > 0) Hairline()
                    FixedRow(f, showNext = false)
                }
            }
        }
        Spacer(Modifier.height(16.dp))
        Text(s.fixedLearned, style = G.type.small)
    }
}

/** One spending group: its categories, each leading to its bookings. */
@Composable
fun ColumnScope.GroupSheet(model: AppModel, name: String) {
    val s = LocalStrings.current
    val fmt = LocalFmt.current
    val group = model.spending.value?.groups?.firstOrNull { it.name == name }
    SheetBody(Modifier.weight(1f, fill = false).verticalScrollable()) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Dot(Palette.category(group?.color), size = 12.dp)
            Spacer(Modifier.width(10.dp))
            Text(categoryName(name, fmt.lang), style = G.type.title)
        }
        if (group == null) {
            Spacer(Modifier.height(12.dp))
            Text(s.nothingHere, style = G.type.body, color = Palette.muted)
            return@SheetBody
        }
        Spacer(Modifier.height(10.dp))
        Money(group.amount, G.type.big)
        Text(
            s.shareOfSpending(fmt.pct(group.share, digits = 0), model.spending.value?.range?.label.orEmpty()),
            style = G.type.small,
        )
        Spacer(Modifier.height(16.dp))
        val max = group.categories.maxOfOrNull { it.amount }?.takeIf { it > 0 } ?: 1.0
        GCard(padding = PaddingValues(horizontal = 14.dp, vertical = 4.dp)) {
            for ((i, c) in group.categories.withIndex()) {
                if (i > 0) Hairline()
                Column(
                    Modifier
                        .fillMaxWidth()
                        .clickable(role = Role.Button) {
                            model.sheets.clear()
                            model.tab = Tab.Transactions
                            model.searchTransactions(categoryName(c.name, fmt.lang))
                        }
                        .padding(vertical = 12.dp),
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(categoryName(c.name, fmt.lang), style = G.type.bodyStrong, modifier = Modifier.weight(1f))
                        Money(c.amount, G.type.number)
                        Spacer(Modifier.width(8.dp))
                        GIcon(Ico.ChevRight, size = 14.dp, tint = Palette.faint)
                    }
                    Spacer(Modifier.height(8.dp))
                    ShareBar(
                        listOf((c.amount / max).toFloat() to Palette.category(group.color), (1 - c.amount / max).toFloat() to Palette.surface3),
                        height = 5.dp,
                    )
                }
            }
        }
        Spacer(Modifier.height(12.dp))
        Text(s.tapForBookings, style = G.type.small)
    }
}

/** What still goes out before the next salary. */
@Composable
fun ColumnScope.UpcomingSheet(model: AppModel) {
    val s = LocalStrings.current
    val fmt = LocalFmt.current
    val a = model.overview.value?.available
    SheetBody(Modifier.weight(1f, fill = false).verticalScrollable()) {
        Text(s.stillToCome, style = G.type.title)
        if (a == null) return@SheetBody
        Spacer(Modifier.height(6.dp))
        val sentence = rememberSentence(Palette.ink, G.type.body.fontSize)
        Text(
            sentence.tpl(
                if (a.payday != null) s.upcomingSentence else s.upcomingSentenceMonth,
                "amount" to a.fixedTotal,
                "date" to fmt.dayMonth(a.payday?.date ?: a.until),
                bold = true,
            ).build(),
            style = G.type.body,
            color = Palette.muted,
        )
        Spacer(Modifier.height(14.dp))
        if (a.upcoming.isEmpty()) {
            EmptyNote(s.nothingMoreToCome)
            return@SheetBody
        }
        GCard(padding = PaddingValues(horizontal = 14.dp, vertical = 2.dp)) {
            for ((i, u) in a.upcoming.withIndex()) {
                if (i > 0) Hairline()
                Row(Modifier.fillMaxWidth().padding(vertical = 12.dp), verticalAlignment = Alignment.CenterVertically) {
                    Column(Modifier.width(64.dp)) {
                        Text(fmt.dayMonth(u.date), style = G.type.bodyStrong.copy(fontSize = G.type.small.fontSize))
                        Text(fmt.relDay(u.date), style = G.type.small.copy(fontSize = G.type.label.fontSize), maxLines = 1)
                    }
                    Spacer(Modifier.width(8.dp))
                    Column(Modifier.weight(1f)) {
                        Text(u.name, style = G.type.bodyStrong, maxLines = 1, overflow = TextOverflow.Ellipsis)
                        Text(
                            listOfNotNull(u.category?.let { categoryName(it, fmt.lang) }, u.interval?.let(fmt::interval)).joinToString(" · "),
                            style = G.type.small,
                            maxLines = 1,
                        )
                    }
                    Money(u.amount, G.type.number)
                }
            }
        }
        if (a.buffer > 0) {
            Spacer(Modifier.height(12.dp))
            Text(rememberSentence(Palette.muted, G.type.small.fontSize).tpl(s.bufferNote, "amount" to a.buffer).build(), style = G.type.small)
        }
        Spacer(Modifier.height(14.dp))
        GButton(s.allFixedCosts, {
            if (model.fixed.value == null) model.loadFixed()
            model.open(Sheet.FixedCosts)
        }, small = true, trailing = Ico.ChevRight)
    }
}
