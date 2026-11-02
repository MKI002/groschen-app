package io.github.mki002.groschen.ui.screens

import androidx.compose.foundation.clickable
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
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import io.github.mki002.groschen.data.Account
import io.github.mki002.groschen.data.Holding
import io.github.mki002.groschen.data.Investments
import io.github.mki002.groschen.data.NetWorth
import io.github.mki002.groschen.model.AppModel
import io.github.mki002.groschen.model.Sheet
import io.github.mki002.groschen.ui.components.ChoiceChip
import io.github.mki002.groschen.ui.components.Dot
import io.github.mki002.groschen.ui.components.ErrorNote
import io.github.mki002.groschen.ui.components.GCard
import io.github.mki002.groschen.ui.components.GIcon
import io.github.mki002.groschen.ui.components.Hairline
import io.github.mki002.groschen.ui.components.Ico
import io.github.mki002.groschen.ui.components.IconBubble
import io.github.mki002.groschen.ui.components.Label
import io.github.mki002.groschen.ui.components.LineChart
import io.github.mki002.groschen.ui.components.LocalFmt
import io.github.mki002.groschen.ui.components.LocalStrings
import io.github.mki002.groschen.ui.components.Money
import io.github.mki002.groschen.ui.components.Placeholder
import io.github.mki002.groschen.ui.components.ShareBar
import io.github.mki002.groschen.ui.components.SheetBody
import io.github.mki002.groschen.ui.components.Signed
import io.github.mki002.groschen.ui.components.Sparkline
import io.github.mki002.groschen.ui.components.Tone
import io.github.mki002.groschen.ui.components.rememberSentence
import io.github.mki002.groschen.ui.theme.G
import io.github.mki002.groschen.ui.theme.Palette

@Composable
fun WealthPage(model: AppModel, list: LazyListState) {
    val s = LocalStrings.current
    val state = model.wealth
    val data = state.value
    LazyColumn(state = list, contentPadding = PagePadding, verticalArrangement = Arrangement.spacedBy(14.dp)) {
        item { PageHeader(null, s.tabWealth) }
        if (data == null) {
            val error = state.error
            if (error != null) {
                item { ErrorNote(error, model::loadWealth) }
            } else {
                item { Placeholder(height = 280.dp) }
                item { Placeholder(height = 220.dp) }
            }
            return@LazyColumn
        }
        state.error?.let { item { ErrorNote(it, model::loadWealth) } }
        item { NetWorthCard(data.netWorth) }
        data.investments?.let { inv -> item { DepotCard(model, inv) } }
        item { AccountsCard(data.netWorth.accounts) }
    }
}

@Composable
private fun NetWorthCard(n: NetWorth) {
    val s = LocalStrings.current
    GCard(padding = PaddingValues(20.dp)) {
        Label(s.netWorth)
        Spacer(Modifier.height(8.dp))
        Money(n.netWorth, G.type.hero, countUp = true)
        n.changeThisYear?.let { change ->
            Spacer(Modifier.height(4.dp))
            val sentence = rememberSentence(if (change >= 0) Palette.good else Palette.bad, G.type.bodyStrong.fontSize)
            Text(
                sentence.tpl(s.changeThisYear, "amount" to Signed(change)).build(),
                style = G.type.bodyStrong,
                color = if (change >= 0) Palette.good else Palette.bad,
            )
        }
        val values = n.series.map { it.value }
        if (values.size >= 2) {
            Spacer(Modifier.height(16.dp))
            LineChart(values, height = 130.dp)
            Spacer(Modifier.height(6.dp))
            val fmt = LocalFmt.current
            Row {
                Text(fmt.monthName(n.series.first().month + "-01") + " " + n.series.first().month.take(4), style = G.type.small)
                Spacer(Modifier.weight(1f))
                Text(s.now, style = G.type.small)
            }
        }
        if (n.liabilities > 0) {
            Spacer(Modifier.height(14.dp))
            ShareBar(listOf(n.assets.toFloat() to Palette.good, n.liabilities.toFloat() to Palette.bad), height = 8.dp)
            Spacer(Modifier.height(10.dp))
            val t = rememberSentence(Palette.ink, G.type.small.fontSize)
            Text(t.tpl(s.assetsDebts, "assets" to n.assets, "debts" to n.liabilities).build(), style = G.type.small)
        }
    }
}

/** Keeps a long daily series light enough to draw on a phone. */
private fun <T> thin(list: List<T>, max: Int = 220): List<T> {
    if (list.size <= max) return list
    val step = list.size.toDouble() / max
    return (0 until max).map { list[(it * step).toInt()] } + list.last()
}

@Composable
private fun DepotCard(model: AppModel, inv: Investments) {
    val s = LocalStrings.current
    val fmt = LocalFmt.current
    // Paying in is not a gain: the chart shows the gain by default; the value only beside the pay-ins.
    var view by rememberSaveable { mutableStateOf("gain") }
    GCard(padding = PaddingValues(20.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            IconBubble(Ico.Etf, Tone.Accent, size = 34.dp)
            Spacer(Modifier.width(12.dp))
            Text(s.depot, style = G.type.heading, modifier = Modifier.weight(1f))
            inv.priceDate?.let { Text(fmt.dayMonth(it), style = G.type.small) }
        }
        Spacer(Modifier.height(14.dp))
        Money(inv.value, G.type.big)
        val t = rememberSentence(Palette.ink, G.type.body.fontSize)
        t.tpl(s.paidInSentence, "amount" to inv.paidIn)
        if (inv.paidIn > 0) {
            t.text(" · ")
            t.tpl(if (inv.gain >= 0) s.gainSentence else s.lossSentence, "amount" to kotlin.math.abs(inv.gain), bold = true)
        }
        Text(t.build(), style = G.type.body, color = Palette.muted)
        inv.xirr?.let {
            Spacer(Modifier.height(2.dp))
            Text(s.perYearReturn(fmt.pct(it, signed = true)), style = G.type.small)
        }

        val daily = remember(inv) { thin(inv.daily) }
        if (daily.size >= 2) {
            Spacer(Modifier.height(16.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                ChoiceChip(s.viewGain, view == "gain", { view = "gain" })
                ChoiceChip(s.viewValue, view == "value", { view = "value" })
            }
            Spacer(Modifier.height(12.dp))
            if (view == "gain") {
                val gains = daily.map { it.value - it.paidIn }
                LineChart(gains, color = if (gains.last() >= 0) Palette.good else Palette.bad, height = 140.dp)
            } else {
                LineChart(daily.map { it.value }, second = daily.map { it.paidIn }, height = 140.dp)
                Spacer(Modifier.height(8.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Dot(Palette.accent, size = 8.dp)
                    Spacer(Modifier.width(6.dp))
                    Text(s.viewValue, style = G.type.small)
                    Spacer(Modifier.width(14.dp))
                    Dot(Palette.muted, size = 8.dp)
                    Spacer(Modifier.width(6.dp))
                    Text(s.paidIn, style = G.type.small)
                }
            }
            Spacer(Modifier.height(6.dp))
            Row {
                Text(fmt.dayMonth(daily.first().date) + " " + daily.first().date.take(4), style = G.type.small)
                Spacer(Modifier.weight(1f))
                Text(s.now, style = G.type.small)
            }
        }

        if (inv.holdings.isNotEmpty()) {
            Spacer(Modifier.height(16.dp))
            Hairline()
            for ((i, h) in inv.holdings.sortedByDescending { it.value }.withIndex()) {
                if (i > 0) Hairline()
                HoldingRow(h) { model.open(Sheet.Holding(h.isin)) }
            }
        }
        inv.monthlyPlan?.takeIf { it > 0 }?.let {
            Spacer(Modifier.height(10.dp))
            Row(verticalAlignment = Alignment.CenterVertically) {
                GIcon(Ico.Repeat, size = 14.dp, tint = Palette.muted)
                Spacer(Modifier.width(8.dp))
                Text(rememberSentence(Palette.ink2, G.type.small.fontSize).tpl(s.planSentence, "amount" to it).build(), style = G.type.small)
            }
        }
    }
}

@Composable
private fun HoldingRow(h: Holding, onClick: () -> Unit) {
    val fmt = LocalFmt.current
    Row(
        Modifier.fillMaxWidth().clickable(role = Role.Button, onClick = onClick).padding(vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column(Modifier.weight(1f)) {
            Text(fundName(h.name.ifBlank { h.isin }), style = G.type.bodyStrong, maxLines = 1, overflow = TextOverflow.Ellipsis)
            Text(fmt.pct(h.share, digits = 0) + " · " + h.isin, style = G.type.small, maxLines = 1)
        }
        Spacer(Modifier.width(10.dp))
        Sparkline(h.spark, Modifier.width(56.dp), color = trendColor(h.r1y), height = 26.dp)
        Spacer(Modifier.width(12.dp))
        Money(h.value, G.type.number)
    }
}

private fun trendColor(r: Double?) = when {
    r == null -> Palette.muted
    r >= 0 -> Palette.good
    else -> Palette.bad
}

/** "iShs Core MSCI World U.ETF Reg.Shs USD Acc. oN" → "iShares Core MSCI World", as on the web. */
fun fundName(name: String): String {
    val short = name
        .replace(Regex("\\s+(U\\.?\\s?ETF|UCITS\\s+ETF|ETF)\\b.*$", RegexOption.IGNORE_CASE), "")
        .replace(Regex("^iShs\\.?\\s", RegexOption.IGNORE_CASE), "iShares ")
        .replace(Regex("^Xtr\\.?\\s", RegexOption.IGNORE_CASE), "Xtrackers ")
        .trim()
    return if (short.length >= 6) short else name
}

@Composable
private fun AccountsCard(accounts: List<Account>) {
    val s = LocalStrings.current
    if (accounts.isEmpty()) return
    GCard(padding = PaddingValues(horizontal = 18.dp, vertical = 14.dp)) {
        Text(s.accounts, style = G.type.heading)
        Spacer(Modifier.height(4.dp))
        for ((i, a) in accounts.sortedWith(compareBy({ it.side != "asset" }, { -it.balance })).withIndex()) {
            if (i > 0) Hairline()
            AccountRow(a)
        }
    }
}

@Composable
private fun AccountRow(a: Account) {
    val s = LocalStrings.current
    val fmt = LocalFmt.current
    val counted = a.counted == 1
    val icon = when (a.kind) {
        "depot" -> Ico.Etf
        "savings" -> Ico.Vault
        "checking" -> Ico.Bank
        else -> Ico.Wallet
    }
    Row(Modifier.fillMaxWidth().padding(vertical = 12.dp), verticalAlignment = Alignment.CenterVertically) {
        IconBubble(icon, if (a.side == "asset") Tone.Muted else Tone.Bad, size = 36.dp)
        Spacer(Modifier.width(12.dp))
        Column(Modifier.weight(1f)) {
            Text(a.name, style = G.type.bodyStrong, color = if (counted) Palette.ink else Palette.muted, maxLines = 1, overflow = TextOverflow.Ellipsis)
            val sub = buildList {
                (a.source ?: a.bankName)?.let { add(it) }
                if (!counted) add(s.notCounted)
                if (a.balanceDate != null && (fmt.daysUntil(a.balanceDate) ?: 0) < -2) add(fmt.dayMonth(a.balanceDate))
            }.joinToString(" · ")
            if (sub.isNotEmpty()) Text(sub, style = G.type.small, maxLines = 1, overflow = TextOverflow.Ellipsis)
        }
        Spacer(Modifier.width(10.dp))
        Column(horizontalAlignment = Alignment.End) {
            Money(
                if (a.side == "asset") a.balance else -kotlin.math.abs(a.balance),
                G.type.number,
                color = if (!counted) Palette.muted else if (a.side == "asset") Palette.ink else Palette.bad,
            )
            val orig = a.origBalance
            if (orig != null && a.currency != null && a.currency != fmt.currency) Money(orig, G.type.small, currency = a.currency)
        }
    }
}

/** One fund: what it is worth, what was paid for it, how it went. */
@Composable
fun ColumnScope.HoldingSheet(model: AppModel, isin: String) {
    val s = LocalStrings.current
    val fmt = LocalFmt.current
    val h = model.wealth.value?.investments?.holdings?.firstOrNull { it.isin == isin }
    SheetBody(Modifier.weight(1f, fill = false).verticalScrollable()) {
        if (h == null) {
            Text(s.nothingHere, style = G.type.body, color = Palette.muted)
            return@SheetBody
        }
        Text(fundName(h.name.ifBlank { h.isin }), style = G.type.heading.copy(fontSize = G.type.big.fontSize * 0.72f))
        Text(h.isin, style = G.type.small)
        Spacer(Modifier.height(16.dp))
        Money(h.value, G.type.big)
        val t = rememberSentence(Palette.ink, G.type.body.fontSize)
        t.text(s.piecesAt(fmt.number(h.pieces, if (h.pieces % 1.0 == 0.0) 0 else 3)))
        h.price?.let { t.text(" ").money(it) }
        h.priceDate?.let { t.text(" · " + fmt.dayMonth(it)) }
        Text(t.build(), style = G.type.body, color = Palette.muted)
        if (h.spark.size >= 2) {
            Spacer(Modifier.height(16.dp))
            LineChart(h.spark, color = trendColor(h.r1y), height = 120.dp)
            Spacer(Modifier.height(4.dp))
            Text(s.priceLastYear, style = G.type.small)
        }
        Spacer(Modifier.height(16.dp))
        GCard(padding = PaddingValues(horizontal = 16.dp, vertical = 4.dp)) {
            h.cost?.let { cost ->
                FactRow(s.paidIn) { Money(cost, G.type.number) }
                Hairline()
                val gain = h.value - cost
                FactRow(if (gain >= 0) s.gain else s.loss) {
                    Money(gain, G.type.number, color = if (gain >= 0) Palette.good else Palette.bad, signed = true)
                }
                Hairline()
            }
            h.r1y?.let {
                FactRow(s.oneYear) { Text(fmt.pct(it, signed = true), style = G.type.number, color = trendColor(it)) }
                Hairline()
            }
            h.ytd?.let {
                FactRow(s.thisYear) { Text(fmt.pct(it, signed = true), style = G.type.number, color = trendColor(it)) }
                Hairline()
            }
            FactRow(s.shareOfDepot) { Text(fmt.pct(h.share, digits = 0), style = G.type.number) }
            h.plan?.takeIf { it > 0 }?.let {
                Hairline()
                FactRow(s.savingsPlan) { Money(it, G.type.number) }
            }
        }
    }
}

@Composable
private fun FactRow(label: String, value: @Composable () -> Unit) {
    Row(Modifier.fillMaxWidth().padding(vertical = 12.dp), verticalAlignment = Alignment.CenterVertically) {
        Text(label, style = G.type.body, color = Palette.ink2, modifier = Modifier.weight(1f))
        value()
    }
}
