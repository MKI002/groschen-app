package io.github.mki002.groschen.ui.screens

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
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyListState
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.selection.SelectionContainer
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.CircularProgressIndicator
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
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import io.github.mki002.groschen.data.Category
import io.github.mki002.groschen.data.Transaction
import io.github.mki002.groschen.i18n.categoryName
import io.github.mki002.groschen.model.AppModel
import io.github.mki002.groschen.model.Sheet
import io.github.mki002.groschen.ui.components.ChoiceChip
import io.github.mki002.groschen.ui.components.Dot
import io.github.mki002.groschen.ui.components.EmptyNote
import io.github.mki002.groschen.ui.components.ErrorNote
import io.github.mki002.groschen.ui.components.GButton
import io.github.mki002.groschen.ui.components.GCard
import io.github.mki002.groschen.ui.components.GField
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
import io.github.mki002.groschen.ui.components.SheetBody
import io.github.mki002.groschen.ui.components.Tone
import io.github.mki002.groschen.ui.components.veilText
import io.github.mki002.groschen.ui.theme.G
import io.github.mki002.groschen.ui.theme.Palette

val TX_FILTERS = listOf("all", "review", "unc", "income")

@Composable
fun TransactionsPage(model: AppModel, list: LazyListState) {
    val s = LocalStrings.current
    val fmt = LocalFmt.current
    val days = remember(model.transactions.toList()) { model.transactions.groupBy { it.date.take(10) }.toList() }
    LazyColumn(state = list, contentPadding = PagePadding, verticalArrangement = Arrangement.spacedBy(12.dp)) {
        item {
            PageHeader(null, s.tabTransactions, sub = if (model.txTotal > 0) s.bookingCount(model.txTotal) else null)
        }
        item {
            GField(
                model.txQuery,
                model::searchTransactions,
                s.search,
                leading = Ico.Search,
                imeAction = ImeAction.Search,
                placeholder = s.searchHint,
                trailing = if (model.txQuery.isNotEmpty()) {
                    {
                        Box(
                            Modifier.size(40.dp).clickable(role = Role.Button, onClickLabel = s.clear) { model.searchTransactions("") },
                            contentAlignment = Alignment.Center,
                        ) { GIcon(Ico.X, size = 16.dp, tint = Palette.muted) }
                    }
                } else {
                    null
                },
            )
        }
        item {
            Row(Modifier.horizontalScroll(rememberScrollState()), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                for (f in TX_FILTERS) {
                    ChoiceChip(
                        s.txFilter(f),
                        model.txFilter == f,
                        { model.filterTransactions(f) },
                        count = if (f == "review") model.txReview.takeIf { it > 0 } else null,
                    )
                }
            }
        }
        model.txError?.let { item { ErrorNote(it, model::reloadTransactions) } }
        if (model.transactions.isEmpty()) {
            if (model.txLoading) {
                items(3) { Placeholder(height = 150.dp) }
            } else if (model.txError == null) {
                item {
                    EmptyNote(
                        if (model.txQuery.isNotBlank()) s.nothingFound(model.txQuery) else s.noBookings(model.txFilter),
                        icon = if (model.txFilter == "review") Ico.Check else Ico.Search,
                    )
                }
            }
            return@LazyColumn
        }
        items(days, key = { it.first }) { (day, txs) ->
            Column {
                Row(Modifier.padding(start = 4.dp, end = 4.dp, bottom = 8.dp, top = 4.dp), verticalAlignment = Alignment.CenterVertically) {
                    Text(fmt.dayHeader(day), style = G.type.bodyStrong.copy(fontSize = G.type.small.fontSize), color = Palette.ink2)
                }
                GCard(padding = PaddingValues(horizontal = 14.dp, vertical = 4.dp)) {
                    txs.forEachIndexed { i, tx ->
                        if (i > 0) Hairline()
                        TxRow(tx) { model.open(Sheet.Tx(tx)) }
                    }
                }
            }
        }
        if (model.txHasMore) {
            item {
                LaunchedEffect(model.transactions.size) { model.loadMoreTransactions() }
                Box(Modifier.fillMaxWidth().padding(16.dp), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator(Modifier.size(22.dp), color = Palette.accent, strokeWidth = 2.dp)
                }
            }
        }
    }
}

@Composable
fun TxRow(tx: Transaction, onClick: () -> Unit) {
    val s = LocalStrings.current
    val fmt = LocalFmt.current
    val color = Palette.category(tx.categoryColor)
    Row(
        Modifier.fillMaxWidth().clickable(onClick = onClick).padding(vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Initial(tx.title, if (tx.categoryId == null) Palette.muted else color)
        Spacer(Modifier.width(12.dp))
        Column(Modifier.weight(1f)) {
            Text(veilText(tx.title, fmt.hidden), style = G.type.bodyStrong, maxLines = 1, overflow = TextOverflow.Ellipsis)
            Row(verticalAlignment = Alignment.CenterVertically) {
                if (tx.needsReview == 1) {
                    Pill(s.checkThis, Tone.Accent)
                    Spacer(Modifier.width(6.dp))
                }
                Text(
                    tx.category?.let { categoryName(it, fmt.lang) } ?: s.noCategory,
                    style = G.type.small,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
            }
        }
        Spacer(Modifier.width(10.dp))
        Column(horizontalAlignment = Alignment.End) {
            Money(tx.amount, G.type.number, color = if (tx.amount > 0) Palette.good else Palette.ink, signed = true)
            val orig = tx.origAmount
            if (orig != null && tx.currency != null && tx.currency != fmt.currency) {
                Money(orig, G.type.small, currency = tx.currency, signed = true)
            }
        }
    }
}

/** One booking: what it was, where it belongs, a note. */
@Composable
fun ColumnScope.TransactionSheet(model: AppModel, tx: Transaction) {
    val s = LocalStrings.current
    val fmt = LocalFmt.current
    var picking by rememberSaveable(tx.id) { mutableStateOf(false) }
    SheetBody(Modifier.weight(1f, fill = false).verticalScrollable()) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Initial(tx.title, Palette.category(tx.categoryColor), size = 46.dp)
            Spacer(Modifier.width(14.dp))
            Column(Modifier.weight(1f)) {
                Text(veilText(tx.title, fmt.hidden), style = G.type.heading, maxLines = 2, overflow = TextOverflow.Ellipsis)
                Text(listOfNotNull(fmt.date(tx.date), tx.account).joinToString(" · "), style = G.type.small)
            }
        }
        Spacer(Modifier.height(18.dp))
        Money(tx.amount, G.type.big, color = if (tx.amount > 0) Palette.good else Palette.ink, signed = true)
        val orig = tx.origAmount
        if (orig != null && tx.currency != null && tx.currency != fmt.currency) {
            Money(orig, G.type.small, currency = tx.currency, signed = true)
        }
        Spacer(Modifier.height(18.dp))

        // Where it belongs.
        Label(s.category)
        Spacer(Modifier.height(8.dp))
        Row(
            Modifier
                .fillMaxWidth()
                .clickable(role = Role.Button) {
                    picking = !picking
                    if (picking) model.ensureCategories()
                }
                .padding(vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Dot(Palette.category(tx.categoryColor), size = 12.dp)
            Spacer(Modifier.width(12.dp))
            Column(Modifier.weight(1f)) {
                Text(tx.category?.let { categoryName(it, fmt.lang) } ?: s.noCategory, style = G.type.bodyStrong)
                tx.categoryGroup?.let { Text(categoryName(it, fmt.lang), style = G.type.small) }
            }
            Text(if (picking) s.close else s.change, style = G.type.small, color = Palette.accentInk)
        }
        if (tx.needsReview == 1 && !picking) {
            Spacer(Modifier.height(8.dp))
            GCard(padding = PaddingValues(14.dp)) {
                Text(s.sortedByItself, style = G.type.body, color = Palette.ink2)
                Spacer(Modifier.height(12.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    GButton(s.looksRight, { model.acceptGuess(tx) }, primary = true, small = true, icon = Ico.Check)
                    GButton(s.otherCategory, {
                        picking = true
                        model.ensureCategories()
                    }, small = true)
                }
            }
        }
        if (picking) {
            Spacer(Modifier.height(8.dp))
            CategoryPicker(model, tx) {
                picking = false
                model.setCategory(tx, it)
            }
        }

        // What the bank wrote.
        val details = listOfNotNull(
            tx.counterparty?.takeIf { it.isNotBlank() && it != tx.title },
            tx.purpose?.takeIf { it.isNotBlank() },
            tx.bookingText?.takeIf { it.isNotBlank() },
        ).distinct()
        if (details.isNotEmpty()) {
            Spacer(Modifier.height(20.dp))
            Label(s.fromTheBank)
            Spacer(Modifier.height(8.dp))
            SelectionContainer {
                Text(veilText(details.joinToString("\n"), fmt.hidden), style = G.type.body, color = Palette.ink2)
            }
        }

        // A note of one's own.
        Spacer(Modifier.height(20.dp))
        var note by rememberSaveable(tx.id) { mutableStateOf(tx.note.orEmpty()) }
        GField(
            note,
            { note = it.take(500) },
            s.note,
            leading = Ico.Pencil,
            imeAction = ImeAction.Done,
            onDone = { model.saveNote(tx, note) },
            singleLine = false,
        )
        if (note.trim() != tx.note.orEmpty()) {
            Spacer(Modifier.height(10.dp))
            GButton(s.saveNote, { model.saveNote(tx, note) }, small = true, icon = Ico.Check)
        }
    }
}

@Composable
private fun CategoryPicker(model: AppModel, tx: Transaction, onPick: (Category) -> Unit) {
    val s = LocalStrings.current
    val fmt = LocalFmt.current
    val state = model.categories
    val all = state.value
    if (all == null) {
        val error = state.error
        if (error != null) ErrorNote(error, model::ensureCategories) else Placeholder(height = 160.dp)
        return
    }
    var query by remember { mutableStateOf("") }
    GField(query, { query = it }, s.searchCategory, leading = Ico.Search, imeAction = ImeAction.Search)
    Spacer(Modifier.height(10.dp))
    val q = query.trim().lowercase()
    // Incoming money first among income categories, outgoing among the rest.
    val incoming = tx.amount > 0
    val shown = all
        .filter { q.isEmpty() || categoryName(it.name, fmt.lang).lowercase().contains(q) || it.name.lowercase().contains(q) }
        .sortedWith(compareBy({ (it.kind == "income") != incoming }, { -it.used }))
        .groupBy { it.group?.let { g -> categoryName(g, fmt.lang) } ?: "" }
    GCard(padding = PaddingValues(horizontal = 14.dp, vertical = 6.dp)) {
        if (shown.isEmpty()) {
            Text(s.nothingFound(query), style = G.type.small, modifier = Modifier.padding(vertical = 12.dp))
        }
        shown.entries.forEachIndexed { gi, (group, cats) ->
            if (gi > 0) Spacer(Modifier.height(6.dp))
            if (group.isNotEmpty()) {
                Label(group, Modifier.padding(top = 10.dp, bottom = 2.dp))
            }
            for (c in cats) {
                val selected = c.id == tx.categoryId
                Row(
                    Modifier.fillMaxWidth().clickable(role = Role.Button) { onPick(c) }.padding(vertical = 10.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Dot(Palette.category(c.color))
                    Spacer(Modifier.width(12.dp))
                    Text(categoryName(c.name, fmt.lang), style = G.type.body, modifier = Modifier.weight(1f))
                    if (selected) GIcon(Ico.Check, size = 16.dp, tint = Palette.accentInk)
                }
            }
        }
    }
}

/** A sheet's content scrolls once it is taller than the screen. */
@Composable
fun Modifier.verticalScrollable(): Modifier = verticalScroll(rememberScrollState())
