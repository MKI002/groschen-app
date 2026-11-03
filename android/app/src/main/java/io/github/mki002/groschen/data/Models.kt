package io.github.mki002.groschen.data

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.JsonObject

// What the Groschen server answers, as far as the app shows it. Fields the app doesn't need are
// left out (the JSON reader skips them), so a newer server never breaks an older app.

@Serializable
data class Health(val ok: Boolean = false, val version: String = "")

@Serializable
data class Region(val country: String = "", val currency: String = "EUR")

@Serializable
data class User(val id: Int = 0, val username: String = "", val name: String = "")

@Serializable
data class Status(
    val version: String = "",
    @SerialName("has_user") val hasUser: Boolean = false,
    @SerialName("setup_complete") val setupComplete: Boolean = false,
    val language: String? = null,
    val region: Region? = null,
    val user: User? = null,
    @SerialName("password_login") val passwordLogin: Boolean = true,
)

@Serializable
data class Challenge(
    @SerialName("challenge_id") val challengeId: String,
    val challenge: String,
)

@Serializable
data class Device(
    val id: Int,
    val name: String = "",
    @SerialName("created_at") val createdAt: String? = null,
    @SerialName("last_used_at") val lastUsedAt: String? = null,
    @SerialName("key_id") val keyId: String? = null,
)

// --- Overview ---------------------------------------------------------------------------------

@Serializable
data class Payday(
    val date: String,
    val late: Boolean = false,
    val name: String? = null,
    val amount: Double? = null,
    val last: String? = null,
)

@Serializable
data class Upcoming(
    val date: String,
    val name: String = "",
    val amount: Double = 0.0,
    val kind: String = "fixed",
    val category: String? = null,
    val interval: String? = null,
)

@Serializable
data class Available(
    @SerialName("has_account") val hasAccount: Boolean = false,
    val balance: Double? = null,
    @SerialName("balance_date") val balanceDate: String? = null,
    @SerialName("balance_age_days") val balanceAgeDays: Int? = null,
    val payday: Payday? = null,
    val since: String? = null,
    val until: String? = null,
    val days: Int? = null,
    val upcoming: List<Upcoming> = emptyList(),
    @SerialName("fixed_total") val fixedTotal: Double = 0.0,
    val buffer: Double = 0.0,
    val available: Double? = null,
    @SerialName("per_day") val perDay: Double? = null,
)

/** One hint under "Worth a look": a double charge, a big payment, a fixed cost that changed. */
@Serializable
data class Alert(
    val key: String,
    val kind: String,
    val date: String? = null,
    val name: String? = null,
    val amount: Double? = null,
    @SerialName("first_date") val firstDate: String? = null,
    val basis: String? = null,
    val usual: Double? = null,
    val category: String? = null,
    val from: Double? = null,
    val to: Double? = null,
    @SerialName("per_year") val perYear: Double? = null,
    val interval: String? = null,
    val since: String? = null,
    @SerialName("last_date") val lastDate: String? = null,
    @SerialName("monthly_cost") val monthlyCost: Double? = null,
    @SerialName("pause_days") val pauseDays: Int? = null,
)

@Serializable
data class Alerts(val items: List<Alert> = emptyList())

@Serializable
data class Badges(
    val review: Int = 0,
    @SerialName("price_changes") val priceChanges: Int = 0,
    val transactions: Int = 0,
    val alerts: Int = 0,
)

@Serializable
data class Connection(
    val id: Int,
    val label: String? = null,
    @SerialName("bank_name") val bankName: String? = null,
    val status: String? = null,
    @SerialName("last_sync_at") val lastSyncAt: String? = null,
    @SerialName("last_error") val lastError: String? = null,
    @SerialName("login_days_left") val loginDaysLeft: Int? = null,
)

// --- Money flow -------------------------------------------------------------------------------

@Serializable
data class DateRange(val start: String = "", val end: String = "", val label: String = "")

@Serializable
data class NamedAmount(val name: String, val amount: Double = 0.0)

@Serializable
data class SpendGroup(
    val name: String,
    val color: String? = null,
    val amount: Double = 0.0,
    val share: Double = 0.0,
    val categories: List<NamedAmount> = emptyList(),
)

@Serializable
data class Cashflow(
    val range: DateRange = DateRange(),
    @SerialName("income_total") val incomeTotal: Double = 0.0,
    @SerialName("spending_total") val spendingTotal: Double = 0.0,
    val saved: Double = 0.0,
    @SerialName("savings_rate") val savingsRate: Double? = null,
    val months: Int = 1,
    @SerialName("avg_spending") val avgSpending: Double = 0.0,
    val groups: List<SpendGroup> = emptyList(),
    @SerialName("transaction_count") val transactionCount: Int = 0,
)

// --- Transactions -----------------------------------------------------------------------------

@Serializable
data class Transaction(
    val id: Int,
    val date: String,
    val amount: Double,
    val currency: String? = null,
    @SerialName("orig_amount") val origAmount: Double? = null,
    val counterparty: String? = null,
    val purpose: String? = null,
    @SerialName("booking_text") val bookingText: String? = null,
    @SerialName("category_id") val categoryId: Int? = null,
    @SerialName("cat_source") val catSource: String? = null,
    val confidence: Double? = null,
    @SerialName("needs_review") val needsReview: Int = 0,
    val note: String? = null,
    val account: String? = null,
    val category: String? = null,
    @SerialName("category_group") val categoryGroup: String? = null,
    @SerialName("category_color") val categoryColor: String? = null,
    val merchant: String? = null,
    val detail: String? = null,
) {
    val title: String get() = merchant?.takeIf { it.isNotBlank() } ?: counterparty?.takeIf { it.isNotBlank() } ?: purpose.orEmpty()
}

@Serializable
data class TransactionPage(
    val items: List<Transaction> = emptyList(),
    val total: Int = 0,
    @SerialName("in") val inflow: Double = 0.0,
    @SerialName("out") val outflow: Double = 0.0,
    val review: Int = 0,
)

@Serializable
data class Category(
    val id: Int,
    val name: String,
    val group: String? = null,
    val kind: String? = null,
    val color: String? = null,
    val used: Int = 0,
)

@Serializable
data class Changed(val ok: Boolean = true, @SerialName("also_changed") val alsoChanged: Int = 0)

// --- Fixed costs ------------------------------------------------------------------------------

@Serializable
data class FixedCost(
    val key: String,
    val name: String,
    val category: String? = null,
    val group: String? = null,
    val amount: Double = 0.0,
    @SerialName("previous_amount") val previousAmount: Double? = null,
    @SerialName("price_change") val priceChange: Double = 0.0,
    val interval: String = "monthly",
    @SerialName("monthly_cost") val monthlyCost: Double = 0.0,
    @SerialName("yearly_cost") val yearlyCost: Double = 0.0,
    @SerialName("next_date") val nextDate: String? = null,
    @SerialName("last_date") val lastDate: String? = null,
    val since: String? = null,
    val status: String = "active",
    val varies: Boolean = false,
)

@Serializable
data class FixedCosts(
    val items: List<FixedCost> = emptyList(),
    val monthly: Double = 0.0,
    val yearly: Double = 0.0,
    val ended: List<FixedCost> = emptyList(),
)

// --- Net worth and depot ----------------------------------------------------------------------

@Serializable
data class Account(
    val id: Int,
    val name: String,
    val kind: String? = null,
    val balance: Double = 0.0,
    @SerialName("balance_date") val balanceDate: String? = null,
    val currency: String? = null,
    @SerialName("orig_balance") val origBalance: Double? = null,
    val counted: Int = 1,
    @SerialName("bank_name") val bankName: String? = null,
    val side: String = "asset",
    val source: String? = null,
)

@Serializable
data class MonthValue(val month: String, val value: Double = 0.0)

@Serializable
data class NetWorth(
    @SerialName("net_worth") val netWorth: Double = 0.0,
    val assets: Double = 0.0,
    val liabilities: Double = 0.0,
    @SerialName("change_this_year") val changeThisYear: Double? = null,
    val accounts: List<Account> = emptyList(),
    val series: List<MonthValue> = emptyList(),
)

@Serializable
data class Holding(
    val isin: String,
    val name: String = "",
    val pieces: Double = 0.0,
    val price: Double? = null,
    @SerialName("price_date") val priceDate: String? = null,
    val value: Double = 0.0,
    val cost: Double? = null,
    val share: Double = 0.0,
    val plan: Double? = null,
    val r1y: Double? = null,
    val ytd: Double? = null,
    val spark: List<Double> = emptyList(),
)

@Serializable
data class DayValue(
    val date: String,
    val value: Double = 0.0,
    @SerialName("paid_in") val paidIn: Double = 0.0,
)

@Serializable
data class Investments(
    val value: Double = 0.0,
    @SerialName("paid_in") val paidIn: Double = 0.0,
    val gain: Double = 0.0,
    val holdings: List<Holding> = emptyList(),
    val daily: List<DayValue> = emptyList(),
    val xirr: Double? = null,
    @SerialName("monthly_plan") val monthlyPlan: Double? = null,
    @SerialName("price_date") val priceDate: String? = null,
)

// --- Bank sync --------------------------------------------------------------------------------

@Serializable
data class JobStep(val label: String = "", val state: String = "pending")

@Serializable
data class TanRequest(val text: String = "", val image: String? = null)

@Serializable
data class Job(
    val id: String,
    val kind: String = "",
    val state: String = "running",
    val message: String = "",
    val steps: List<JobStep> = emptyList(),
    val result: JsonObject? = null,
    val error: String? = null,
    val tan: TanRequest? = null,
)

/**
 * Which logo a merchant gets, as the web app shows it: a built-in brand logo (its drawing in
 * [ink] on a disc in [hex]), a picture of the user's own ([key], changing [v] with each new
 * picture), or the letter.
 */
@Serializable
data class MerchantLogo(
    val kind: String = "letter",
    val slug: String? = null,
    val title: String? = null,
    val hex: String? = null,
    val ink: String? = null,
    val dark: Boolean = false,
    /** The drawing as SVG path data, on a 24 x 24 grid. */
    val path: String? = null,
    val key: String? = null,
    val v: String? = null,
)
