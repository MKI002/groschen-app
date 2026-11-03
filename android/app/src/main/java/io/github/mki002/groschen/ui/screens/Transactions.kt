package io.github.mki002.groschen.ui.screens

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.expandVertically
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.shrinkVertically
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
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyListState
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.text.selection.SelectionContainer
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import io.github.mki002.groschen.data.Category
import io.github.mki002.groschen.data.Transaction
import io.github.mki002.groschen.data.TxEntry
import io.github.mki002.groschen.data.dayEntries
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
import io.github.mki002.groschen.ui.components.Label
import io.github.mki002.groschen.ui.components.LocalFmt
import io.github.mki002.groschen.ui.components.LocalStrings
import io.github.mki002.groschen.ui.components.MerchantBadge
import io.github.mki002.groschen.ui.components.Money
import io.github.mki002.groschen.ui.components.Pill
import io.github.mki002.groschen.ui.components.Placeholder
import io.github.mki002.groschen.ui.components.SheetBody
import io.github.mki002.groschen.ui.components.Tone
import io.github.mki002.groschen.ui.components.veilText
import io.github.mki002.groschen.ui.theme.G
import io.github.mki002.groschen.ui.theme.Palette
import kotlin.math.abs

val TX_FILTERS = listOf("all", "review", "unc", "income")

@Composable
fun TransactionsPage(model: AppModel, list: LazyListState) {
    val s = LocalStrings.current
    val fmt = LocalFmt.current
    // Moves between own accounts show once with both sides; without a search or filter, a day's
    // round-ups (and several moves of one payee) fold into one line that opens up.
    val fold = model.txFilter == "all" && model.txQuery.isBlank()
    val days = remember(model.transactions.toList(), fold) {
        val listed = model.transactions.associateBy { it.id }
        model.transactions
            .groupBy { it.date.take(10) }
            .map { (day, txs) -> day to dayEntries(txs, listed, fold) }
            .filter { it.second.isNotEmpty() }
    }
    val open = remember { mutableStateListOf<String>() }
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
        items(days, key = { it.first }) { (day, entries) ->
            Column {
                Row(Modifier.padding(start = 4.dp, end = 4.dp, bottom = 8.dp, top = 4.dp), verticalAlignment = Alignment.CenterVertically) {
                    Text(fmt.dayHeader(day), style = G.type.bodyStrong.copy(fontSize = G.type.small.fontSize), color = Palette.ink2)
                }
                GCard(padding = PaddingValues(horizontal = 14.dp, vertical = 4.dp)) {
                    entries.forEachIndexed { i, entry ->
                        if (i > 0) Hairline()
                        when (entry) {
                            is TxEntry.One -> TxRow(entry.item.tx, paired = entry.item.other != null) { model.open(Sheet.Tx(entry.item.tx)) }
                            is TxEntry.Fold -> {
                                val isOpen = entry.key in open
                                FoldRow(entry, isOpen) { if (isOpen) open.remove(entry.key) else open.add(entry.key) }
                                AnimatedVisibility(
                                    isOpen,
                                    enter = expandVertically() + fadeIn(),
                                    exit = shrinkVertically() + fadeOut(),
                                ) {
                                    Column {
                                        for (item in entry.items) {
                                            TxRow(item.tx, paired = item.other != null, inner = true) { model.open(Sheet.Tx(item.tx)) }
                                        }
                                    }
                                }
                            }
                        }
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

/**
 * One booking in a list. Money that only moved between own accounts is neither spent nor earned:
 * it shows in grey without a sign and says the way it went ("Girokonto → Extra-Konto"); with both
 * of its sides in one row ([paired]) it gets the two arrows instead of the payee's badge. An
 * [inner] row, one of a folded line, is smaller and leaves out what the line already says.
 */
@Composable
fun TxRow(tx: Transaction, paired: Boolean = false, inner: Boolean = false, onClick: () -> Unit) {
    val s = LocalStrings.current
    val fmt = LocalFmt.current
    val color = Palette.category(tx.categoryColor)
    val moved = tx.move != null
    val badge = if (inner) 30.dp else 38.dp
    Row(
        Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .padding(start = if (inner) 16.dp else 0.dp, top = if (inner) 8.dp else 12.dp, bottom = if (inner) 8.dp else 12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        if (paired) {
            MoveBadge(Ico.Swap, badge)
        } else {
            MerchantBadge(tx.title, if (tx.categoryId == null) Palette.muted else color, size = badge)
        }
        Spacer(Modifier.width(12.dp))
        Column(Modifier.weight(1f)) {
            Text(
                veilText(tx.title, fmt.hidden),
                style = G.type.bodyStrong,
                color = if (moved) Palette.ink2 else G.type.bodyStrong.color,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
            if (!inner || tx.needsReview == 1) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    if (tx.needsReview == 1) {
                        Pill(s.checkThis, Tone.Accent)
                        Spacer(Modifier.width(6.dp))
                    }
                    if (!inner) {
                        Text(
                            if (moved) tx.route else tx.category?.let { categoryName(it, fmt.lang) } ?: s.noCategory,
                            style = G.type.small,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis,
                        )
                    }
                }
            }
        }
        Spacer(Modifier.width(10.dp))
        Column(horizontalAlignment = Alignment.End) {
            if (moved) {
                Money(abs(tx.amount), G.type.number, color = Palette.muted)
            } else {
                Money(tx.amount, G.type.number, color = if (tx.amount > 0) Palette.good else Palette.ink, signed = true)
            }
            val orig = tx.origAmount
            if (orig != null && tx.currency != null && tx.currency != fmt.currency) {
                Money(if (moved) abs(orig) else orig, G.type.small, currency = tx.currency, signed = !moved)
            }
        }
    }
}

/** A day's round-ups (or moves of one payee) in one quiet line; a tap shows each of them. */
@Composable
private fun FoldRow(fold: TxEntry.Fold, open: Boolean, onToggle: () -> Unit) {
    val s = LocalStrings.current
    val fmt = LocalFmt.current
    val first = fold.first
    val turn by animateFloatAsState(if (open) 180f else 0f, label = "fold")
    Row(
        Modifier
            .fillMaxWidth()
            .clickable(role = Role.Button, onClickLabel = if (open) s.close else s.show) { onToggle() }
            .padding(vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        if (fold.roundup) MoveBadge(Ico.Coin) else MerchantBadge(first.title, Palette.category(first.categoryColor))
        Spacer(Modifier.width(12.dp))
        Column(Modifier.weight(1f)) {
            Text(veilText(first.title, fmt.hidden), style = G.type.bodyStrong, color = Palette.ink2, maxLines = 1, overflow = TextOverflow.Ellipsis)
            Row(verticalAlignment = Alignment.CenterVertically) {
                val n = fold.items.size
                Text(
                    "${if (fold.roundup) s.roundUps(n) else s.bookingCount(n)} · ${first.route}",
                    style = G.type.small,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                    modifier = Modifier.weight(1f, fill = false),
                )
                Spacer(Modifier.width(4.dp))
                GIcon(Ico.ChevDown, Modifier.rotate(turn), size = 14.dp, tint = Palette.muted)
            }
        }
        Spacer(Modifier.width(10.dp))
        Money(fold.sum, G.type.number, color = Palette.muted)
    }
}

/** A quiet round badge with an icon, for money that only moved. */
@Composable
private fun MoveBadge(icon: Ico, size: Dp = 38.dp) {
    Box(
        Modifier.size(size).clip(CircleShape).background(Palette.ink.copy(alpha = 0.07f)),
        contentAlignment = Alignment.Center,
    ) {
        GIcon(icon, size = size * 0.45f, tint = Palette.ink2)
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
            MerchantBadge(tx.title, Palette.category(tx.categoryColor), size = 46.dp)
            Spacer(Modifier.width(14.dp))
            Column(Modifier.weight(1f)) {
                Text(veilText(tx.title, fmt.hidden), style = G.type.heading, maxLines = 2, overflow = TextOverflow.Ellipsis)
                Text(listOfNotNull(fmt.date(tx.date), tx.account).joinToString(" · "), style = G.type.small)
            }
        }
        Spacer(Modifier.height(18.dp))
        val moved = tx.move != null
        if (moved) {
            Money(abs(tx.amount), G.type.big, color = Palette.ink2)
        } else {
            Money(tx.amount, G.type.big, color = if (tx.amount > 0) Palette.good else Palette.ink, signed = true)
        }
        val orig = tx.origAmount
        if (orig != null && tx.currency != null && tx.currency != fmt.currency) {
            Money(if (moved) abs(orig) else orig, G.type.small, currency = tx.currency, signed = !moved)
        }
        if (moved) {
            // Money moved between own accounts: the way it went, and that it counts for nothing.
            Spacer(Modifier.height(10.dp))
            Row(verticalAlignment = Alignment.CenterVertically) {
                GIcon(Ico.Swap, size = 16.dp, tint = Palette.ink2)
                Spacer(Modifier.width(8.dp))
                Text(s.movedWhy(tx.route), style = G.type.small, color = Palette.ink2)
            }
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
