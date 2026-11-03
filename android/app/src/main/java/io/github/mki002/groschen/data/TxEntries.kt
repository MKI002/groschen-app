package io.github.mki002.groschen.data

/**
 * A booking as the list shows it. For money moved between own accounts with both sides listed,
 * the side that left an account, with the side that arrived ([other]).
 */
data class TxItem(val tx: Transaction, val other: Transaction? = null)

/** One line of a day in the transactions list. */
sealed interface TxEntry {
    data class One(val item: TxItem) : TxEntry

    /** A day's round-ups, or several moves of one payee the same way, folded into one line that opens up. */
    data class Fold(val key: String, val items: List<TxItem>, val roundup: Boolean) : TxEntry {
        val first: Transaction get() = items.first().tx
        val sum: Double get() = items.sumOf { kotlin.math.abs(it.tx.amount) }
    }
}

/**
 * A day's bookings in the order the list shows them, as in the web app: real income and spending
 * first, then the money that only moved, each move once with both of its sides, and with [fold]
 * several of the same kind (a round-up per card payment, two ETF plans) in one line. A booking
 * still to check stays in sight. [listed] holds every booking loaded, so the other side of a move
 * is found also on another day.
 */
fun dayEntries(items: List<Transaction>, listed: Map<Int, Transaction>, fold: Boolean): List<TxEntry> {
    val real = mutableListOf<TxEntry>()
    val moves = mutableListOf<TxItem>()
    for (tx in items) {
        val other = tx.move?.mirror?.let { listed[it] }
        if (other != null && tx.amount > 0) continue // shown with the side that left the other account
        if (tx.move != null) moves += TxItem(tx, other) else real += TxEntry.One(TxItem(tx))
    }
    if (!fold) return real + moves.map { TxEntry.One(it) }
    fun key(tx: Transaction) = "${tx.title}|${tx.route}"
    val groups = moves.filter { it.tx.needsReview != 1 }.groupBy { key(it.tx) }
    val shown = mutableListOf<TxEntry>()
    for (item in moves) {
        val rows = if (item.tx.needsReview == 1) null else groups[key(item.tx)]
        when {
            rows == null || rows.size < 2 -> shown += TxEntry.One(item)
            rows.first() === item -> shown += TxEntry.Fold("${item.tx.date}|${key(item.tx)}", rows, rows.all { it.tx.roundup })
        }
    }
    // The round-ups last: the smallest and the most of them.
    return real + shown.sortedBy { it is TxEntry.Fold && it.roundup }
}
