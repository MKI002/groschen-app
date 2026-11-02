package io.github.mki002.groschen.model

import androidx.compose.runtime.derivedStateOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import io.github.mki002.groschen.data.Alert
import io.github.mki002.groschen.data.ApiException
import io.github.mki002.groschen.data.Available
import io.github.mki002.groschen.data.Badges
import io.github.mki002.groschen.data.Cashflow
import io.github.mki002.groschen.data.Category
import io.github.mki002.groschen.data.Connection
import io.github.mki002.groschen.data.FixedCosts
import io.github.mki002.groschen.data.GroschenApi
import io.github.mki002.groschen.data.Investments
import io.github.mki002.groschen.data.Job
import io.github.mki002.groschen.data.NetWorth
import io.github.mki002.groschen.data.ServerAddress
import io.github.mki002.groschen.data.Status
import io.github.mki002.groschen.data.Transaction
import io.github.mki002.groschen.i18n.Fmt
import io.github.mki002.groschen.i18n.Lang
import io.github.mki002.groschen.i18n.Strings
import io.github.mki002.groschen.i18n.strings
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import okhttp3.HttpUrl.Companion.toHttpUrl
import java.util.Base64
import kotlinx.coroutines.Job as Task

enum class Stage { Starting, Connect, Login, Locked, Main }

enum class Tab { Overview, Transactions, Spending, Wealth }

/** What lies on top of the pages: a sheet from the bottom of the screen. */
sealed interface Sheet {
    data object Settings : Sheet
    data object Sync : Sheet
    data object Upcoming : Sheet
    data object FixedCosts : Sheet
    data object Fingerprint : Sheet
    data class Tx(val tx: Transaction) : Sheet
    data class Holding(val isin: String) : Sheet
    data class Group(val name: String) : Sheet

    /** Stays the same while the sheet's content changes. */
    val key: String
        get() = when (this) {
            Settings -> "settings"
            Sync -> "sync"
            Upcoming -> "upcoming"
            FixedCosts -> "fixed"
            Fingerprint -> "fingerprint"
            is Tx -> "tx:${tx.id}"
            is Holding -> "holding:$isin"
            is Group -> "group:$name"
        }
}

/** Data for one page: what came, what went wrong, whether it is loading. */
class Loadable<T> {
    var value by mutableStateOf<T?>(null)
    var error by mutableStateOf<String?>(null)
    var loading by mutableStateOf(false)
}

data class Toast(val text: String, val id: Long = System.nanoTime())

data class OverviewData(
    val available: Available,
    val alerts: List<Alert>,
    val badges: Badges,
    val month: Cashflow?,
    val connections: List<Connection>,
)

data class WealthData(val netWorth: NetWorth, val investments: Investments?)

/**
 * Everything the app knows and does, without Android in it: which screen shows, the login,
 * the pages' data. The screens read it and call it; the phone's parts come in through [Platform].
 */
class AppModel(
    private val platform: Platform,
    private val scope: CoroutineScope,
    private val clock: () -> Long = System::currentTimeMillis,
) {
    var settings by mutableStateOf(platform.loadSettings())
        private set
    var stage by mutableStateOf(Stage.Starting)
        private set
    var status by mutableStateOf<Status?>(null)
        private set
    var tab by mutableStateOf(Tab.Overview)
    val sheets = mutableStateListOf<Sheet>()
    var toast by mutableStateOf<Toast?>(null)
        private set
    var busy by mutableStateOf(false)
        private set

    /** The problem with what was just typed on the connect or login screen. */
    var formError by mutableStateOf<String?>(null)

    /** A note on the login screen, like "this phone was removed in Groschen". */
    var notice by mutableStateOf<String?>(null)

    /** Groschen is reachable but not set up yet: the web address to finish the setup in. */
    var setupUrl by mutableStateOf<String?>(null)
        private set

    val lang: Lang by derivedStateOf {
        val code = settings.language.takeIf { it != "auto" } ?: status?.language ?: platform.systemLanguage
        if (code == "de") Lang.DE else Lang.EN
    }
    val s: Strings by derivedStateOf { strings(lang) }
    val fmt: Fmt by derivedStateOf {
        Fmt(lang, status?.region?.country.orEmpty(), status?.region?.currency ?: "EUR", settings.hideAmounts)
    }
    val fingerprintOn: Boolean get() = settings.deviceKeyId != null
    val serverLabel: String get() = settings.server?.trimEnd('/')?.removePrefix("http://")?.removePrefix("https://").orEmpty()
    val serverEncrypted: Boolean get() = settings.server?.startsWith("https://") == true

    private var api: GroschenApi? = null
    private var backgroundSince: Long? = null

    // --- start, connect, log in ---------------------------------------------------------------

    fun start() {
        val server = settings.server
        if (server == null) {
            stage = Stage.Connect
            return
        }
        val api = makeApi(server).also { this.api = it }
        if (settings.deviceKeyId != null) {
            stage = Stage.Locked
            scope.launch { runCatching { status = api.status() } }
            return
        }
        val token = platform.loadSession()
        if (token == null) {
            stage = Stage.Login
            scope.launch { runCatching { status = api.status() } }
            return
        }
        api.token = token
        scope.launch {
            try {
                val st = api.status()
                status = st
                if (st.user != null) enterMain() else {
                    platform.saveSession(null)
                    stage = Stage.Login
                }
            } catch (e: ApiException) {
                // Offline: show the app anyway; each page says the server can't be reached.
                if (e.status == 0) enterMain() else stage = Stage.Login
            } catch (e: Exception) {
                enterMain()
            }
        }
    }

    fun connect(input: String) {
        if (busy) return
        setupUrl = null
        when (val r = ServerAddress.parse(input)) {
            is ServerAddress.Result.Bad -> formError = s.addressError(r.reason)
            is ServerAddress.Result.Ok -> scope.launch {
                busy = true
                formError = null
                val url = r.url.toString()
                val candidate = makeApi(url)
                try {
                    val health = try {
                        candidate.health()
                    } catch (e: ApiException) {
                        throw e
                    } catch (e: Exception) {
                        null
                    }
                    if (health?.ok != true) {
                        formError = s.notGroschen
                        return@launch
                    }
                    val st = candidate.status()
                    status = st
                    if (!st.hasUser || !st.setupComplete) {
                        setupUrl = url
                        formError = s.setupFirst
                        return@launch
                    }
                    api = candidate
                    update { copy(server = url) }
                    notice = null
                    stage = Stage.Login
                } catch (e: ApiException) {
                    formError = if (e.status == 0) s.unreachableHost(r.url.host) else e.message
                } catch (e: CancellationException) {
                    throw e
                } catch (e: Exception) {
                    formError = s.notGroschen
                } finally {
                    busy = false
                }
            }
        }
    }

    fun login(username: String, password: String) {
        val api = api ?: return
        if (busy) return
        if (username.isBlank() || password.isEmpty()) {
            formError = s.fillBoth
            return
        }
        scope.launch {
            busy = true
            formError = null
            try {
                api.login(username.trim(), password)
                update { copy(username = username.trim()) }
                // A fingerprint key that stopped working: take its entry off the server.
                settings.staleDeviceId?.let { id ->
                    runCatching { api.removeDevice(id) }
                    update { copy(staleDeviceId = null) }
                }
                if (!fingerprintOn) platform.saveSession(api.token)
                status = api.status()
                notice = null
                enterMain()
                if (!fingerprintOn && !settings.fingerprintOffered && platform.biometrics() == Biometrics.READY) {
                    sheets.add(Sheet.Fingerprint)
                }
            } catch (e: ApiException) {
                formError = e.message
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                formError = s.unexpected
            } finally {
                busy = false
            }
        }
    }

    /** Log in with the fingerprint: sign the server's challenge with the key in the phone's chip. */
    fun unlock() {
        val api = api ?: return
        val keyId = settings.deviceKeyId ?: return
        if (busy) return
        scope.launch {
            busy = true
            formError = null
            try {
                if (platform.biometrics() != Biometrics.READY) {
                    loseKey(s.fingerprintUnavailable)
                    return@launch
                }
                val challenge = api.deviceLoginChallenge()
                val message = LOGIN_LABEL + Base64.getDecoder().decode(challenge.challenge)
                when (val r = platform.signWithDeviceKey(message, PromptText(s.unlockTitle, s.unlockSubtitle))) {
                    is SignResult.Signed -> {
                        api.deviceLogin(keyId, challenge.challengeId, Base64.getEncoder().encodeToString(r.signature))
                        status = api.status()
                        notice = null
                        enterMain()
                    }
                    SignResult.Cancelled -> Unit
                    SignResult.KeyGone -> loseKey(s.fingerprintChanged)
                    is SignResult.Failed -> formError = r.message
                }
            } catch (e: ApiException) {
                if (e.status == 401) loseKey(s.phoneRemoved) else formError = e.message
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                formError = s.unexpected
            } finally {
                busy = false
            }
        }
    }

    fun usePassword() {
        formError = null
        stage = Stage.Login
    }

    fun backToLock() {
        formError = null
        if (fingerprintOn) stage = Stage.Locked
    }

    private fun loseKey(message: String) {
        platform.dropDeviceKey()
        update { copy(deviceKeyId = null, staleDeviceId = deviceId ?: staleDeviceId, deviceId = null) }
        notice = message
        stage = Stage.Login
    }

    private fun enterMain() {
        stage = Stage.Main
        refreshAll()
    }

    // --- fingerprint --------------------------------------------------------------------------

    fun enableFingerprint() {
        val api = api ?: return
        if (busy) return
        when (platform.biometrics()) {
            Biometrics.READY -> Unit
            Biometrics.NOT_ENROLLED -> return show(s.fingerprintNotEnrolled)
            Biometrics.UNAVAILABLE -> return show(s.fingerprintUnavailable)
        }
        scope.launch {
            busy = true
            try {
                val publicKey = platform.newDeviceKey()
                val challenge = api.deviceChallenge()
                val message = REGISTER_LABEL + Base64.getDecoder().decode(challenge.challenge)
                when (val r = platform.signWithDeviceKey(message, PromptText(s.setupTitle, s.setupSubtitle))) {
                    is SignResult.Signed -> {
                        val device = api.addDevice(
                            challenge.challengeId,
                            Base64.getEncoder().encodeToString(publicKey),
                            Base64.getEncoder().encodeToString(r.signature),
                            platform.deviceName,
                        )
                        update { copy(deviceKeyId = device.keyId, deviceId = device.id, fingerprintOffered = true) }
                        // From now on the login lives in memory only and the fingerprint opens the app.
                        platform.saveSession(null)
                        sheets.remove(Sheet.Fingerprint)
                        show(s.fingerprintIsOn)
                    }
                    SignResult.Cancelled -> platform.dropDeviceKey()
                    SignResult.KeyGone -> {
                        platform.dropDeviceKey()
                        show(s.fingerprintFailed)
                    }
                    is SignResult.Failed -> {
                        platform.dropDeviceKey()
                        show(r.message)
                    }
                }
            } catch (e: ApiException) {
                platform.dropDeviceKey()
                show(e.message ?: s.fingerprintFailed)
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                platform.dropDeviceKey()
                show(s.fingerprintFailed)
            } finally {
                busy = false
            }
        }
    }

    fun declineFingerprint() {
        update { copy(fingerprintOffered = true) }
        sheets.remove(Sheet.Fingerprint)
    }

    fun disableFingerprint() {
        val api = api ?: return
        scope.launch {
            settings.deviceId?.let { id -> runCatching { api.removeDevice(id) } }
            platform.dropDeviceKey()
            update { copy(deviceKeyId = null, deviceId = null) }
            // Removing the phone also ended the login it made with the fingerprint.
            val stillIn = runCatching { api.status().user != null }.getOrDefault(false)
            if (stillIn) {
                platform.saveSession(api.token)
                show(s.fingerprintIsOff)
            } else {
                api.token = null
                sheets.clear()
                clearData()
                notice = s.fingerprintOffLogin
                stage = Stage.Login
            }
        }
    }

    fun setLockAfter(seconds: Int) = update { copy(lockAfterSeconds = seconds) }

    // --- leaving ------------------------------------------------------------------------------

    fun onBackground() {
        backgroundSince = clock()
    }

    fun onForeground() {
        val since = backgroundSince ?: return
        backgroundSince = null
        if (stage == Stage.Main && fingerprintOn && clock() - since >= settings.lockAfterSeconds * 1000L) lock()
    }

    fun lock() {
        api?.token = null
        sheets.clear()
        clearData()
        stage = if (fingerprintOn) Stage.Locked else Stage.Login
    }

    fun logout() {
        val api = api ?: return
        scope.launch {
            api.logout()
            platform.saveSession(null)
            sheets.clear()
            clearData()
            tab = Tab.Overview
            stage = if (fingerprintOn) Stage.Locked else Stage.Login
        }
    }

    /** Forget this server: the fingerprint key, the login and the address. */
    fun changeServer() {
        val api = api
        scope.launch {
            if (api != null) {
                settings.deviceId?.let { id -> runCatching { api.removeDevice(id) } }
                api.logout()
            }
            platform.dropDeviceKey()
            platform.saveSession(null)
            update { StoredSettings(language = language, hideAmounts = hideAmounts, lockAfterSeconds = lockAfterSeconds) }
            this@AppModel.api = null
            status = null
            sheets.clear()
            clearData()
            tab = Tab.Overview
            formError = null
            stage = Stage.Connect
        }
    }

    private fun onLoggedOut() {
        scope.launch {
            if (stage != Stage.Main) return@launch
            sheets.clear()
            clearData()
            platform.saveSession(null)
            notice = s.sessionEnded
            stage = if (fingerprintOn) Stage.Locked else Stage.Login
        }
    }

    // --- small things -------------------------------------------------------------------------

    fun toggleHidden() = update { copy(hideAmounts = !hideAmounts) }

    fun setLanguage(code: String) = update { copy(language = code) }

    fun show(text: String) {
        toast = Toast(text)
    }

    fun open(sheet: Sheet) {
        if (sheets.lastOrNull() != sheet) sheets.add(sheet)
    }

    fun close(sheet: Sheet? = null) {
        if (sheet == null) sheets.removeLastOrNull() else sheets.remove(sheet)
    }

    /** The phone's back gesture: the top sheet first, then back to the Overview. */
    fun back(): Boolean {
        if (sheets.isNotEmpty()) {
            sheets.removeAt(sheets.lastIndex)
            return true
        }
        if (stage == Stage.Main && tab != Tab.Overview) {
            tab = Tab.Overview
            return true
        }
        if (stage == Stage.Login && fingerprintOn) {
            stage = Stage.Locked
            return true
        }
        return false
    }

    fun openWeb() {
        settings.server?.let(platform::openInBrowser)
    }

    fun openSetupInBrowser() {
        setupUrl?.let(platform::openInBrowser)
    }

    val appVersion: String get() = platform.appVersion

    /** The picture of a TAN request: a data URL ("data:image/png;base64,...") or plain base64. */
    fun tanImage(data: String?): androidx.compose.ui.graphics.ImageBitmap? {
        if (data.isNullOrBlank()) return null
        val b64 = data.substringAfter("base64,", data)
        val bytes = runCatching { Base64.getMimeDecoder().decode(b64) }.getOrNull() ?: return null
        return platform.decodeImage(bytes)
    }

    // --- pages --------------------------------------------------------------------------------

    val overview = Loadable<OverviewData>()
    val spending = Loadable<Cashflow>()
    val fixed = Loadable<FixedCosts>()
    val wealth = Loadable<WealthData>()
    val categories = Loadable<List<Category>>()
    var spendPreset by mutableStateOf("month")
        private set

    fun refreshAll() {
        loadOverview()
        if (transactions.isNotEmpty() || txLoaded) reloadTransactions()
        if (spending.value != null) loadSpending()
        if (fixed.value != null) loadFixed()
        if (wealth.value != null) loadWealth()
    }

    fun refresh(tab: Tab) {
        when (tab) {
            Tab.Overview -> loadOverview()
            Tab.Transactions -> reloadTransactions()
            Tab.Spending -> {
                loadSpending()
                loadFixed()
            }
            Tab.Wealth -> loadWealth()
        }
    }

    /** A page shown for the first time loads its data. */
    fun ensure(tab: Tab) {
        when (tab) {
            Tab.Overview -> if (overview.value == null && !overview.loading) loadOverview()
            Tab.Transactions -> if (!txLoaded && !txLoading) reloadTransactions()
            Tab.Spending -> {
                if (spending.value == null && !spending.loading) loadSpending()
                if (fixed.value == null && !fixed.loading) loadFixed()
            }
            Tab.Wealth -> if (wealth.value == null && !wealth.loading) loadWealth()
        }
    }

    fun loadOverview() = load(overview) { api ->
        coroutineScope {
            val available = async { api.available() }
            val alerts = async { api.alerts().items }
            val badges = async { api.badges() }
            val month = async { runCatching { api.cashflow("month") }.getOrNull() }
            val connections = async { runCatching { api.connections() }.getOrDefault(emptyList()) }
            OverviewData(available.await(), alerts.await(), badges.await(), month.await(), connections.await())
        }
    }

    fun setSpendingPeriod(preset: String) {
        if (preset == spendPreset) return
        spendPreset = preset
        loadSpending()
    }

    fun loadSpending() = load(spending) { it.cashflow(spendPreset) }
    fun loadFixed() = load(fixed) { it.fixedCosts() }

    fun loadWealth() = load(wealth) { api ->
        coroutineScope {
            val nw = async { api.netWorth() }
            val inv = async { runCatching { api.investments() }.getOrNull() }
            WealthData(nw.await(), inv.await()?.takeIf { it.holdings.isNotEmpty() || it.value > 0 })
        }
    }

    fun dismissAlert(alert: Alert) {
        val api = api ?: return
        scope.launch {
            try {
                api.dismissAlert(alert.key)
                overview.value = overview.value?.let { it.copy(alerts = it.alerts - alert) }
                show(s.hintHidden)
            } catch (e: ApiException) {
                show(e.message ?: s.unexpected)
            }
        }
    }

    // --- transactions -------------------------------------------------------------------------

    val transactions = mutableStateListOf<Transaction>()
    var txQuery by mutableStateOf("")
        private set
    var txFilter by mutableStateOf("all")
        private set
    var txTotal by mutableStateOf(0)
        private set
    var txReview by mutableStateOf(0)
        private set
    var txLoading by mutableStateOf(false)
        private set
    var txError by mutableStateOf<String?>(null)
        private set
    private var txLoaded = false
    private var txTask: Task? = null

    val txHasMore: Boolean get() = transactions.size < txTotal

    fun searchTransactions(query: String) {
        txQuery = query
        txTask?.cancel()
        txTask = scope.launch {
            delay(300)
            fetchTransactions(reset = true)
        }
    }

    fun filterTransactions(filter: String) {
        if (filter == txFilter) return
        txFilter = filter
        reloadTransactions()
    }

    /** From the Overview's hint: the bookings Groschen sorted on its own and wants a look at. */
    fun reviewTransactions() {
        txFilter = "review"
        txQuery = ""
        tab = Tab.Transactions
        reloadTransactions()
    }

    fun reloadTransactions() {
        txTask?.cancel()
        txTask = scope.launch { fetchTransactions(reset = true) }
    }

    fun loadMoreTransactions() {
        if (txLoading || !txHasMore) return
        txTask = scope.launch { fetchTransactions(reset = false) }
    }

    private suspend fun fetchTransactions(reset: Boolean) {
        val api = api ?: return
        txLoading = true
        txError = null
        try {
            val page = api.transactions(txQuery.trim(), txFilter, if (reset) 0 else transactions.size)
            if (reset) transactions.clear()
            transactions.addAll(page.items)
            txTotal = page.total
            txReview = page.review
            txLoaded = true
        } catch (e: CancellationException) {
            throw e
        } catch (e: ApiException) {
            txError = e.message
        } catch (e: Exception) {
            txError = s.unexpected
        } finally {
            txLoading = false
        }
    }

    fun ensureCategories() {
        if (categories.value == null && !categories.loading) load(categories) { it.categories() }
    }

    fun setCategory(tx: Transaction, category: Category) {
        val api = api ?: return
        scope.launch {
            try {
                val r = api.setCategory(tx.id, category.id, similar = true)
                replace(
                    tx.copy(
                        categoryId = category.id,
                        category = category.name,
                        categoryGroup = category.group,
                        categoryColor = category.color,
                        needsReview = 0,
                        catSource = "user",
                    ),
                )
                show(if (r.alsoChanged > 0) s.categorySavedSimilar(r.alsoChanged) else s.categorySaved)
                afterChange()
            } catch (e: ApiException) {
                show(e.message ?: s.unexpected)
            }
        }
    }

    fun acceptGuess(tx: Transaction) {
        val api = api ?: return
        scope.launch {
            try {
                val r = api.markReviewed(tx.id)
                replace(tx.copy(needsReview = 0, catSource = "user"))
                show(if (r.alsoChanged > 0) s.acceptedSimilar(r.alsoChanged) else s.accepted)
                afterChange()
            } catch (e: ApiException) {
                show(e.message ?: s.unexpected)
            }
        }
    }

    fun saveNote(tx: Transaction, note: String) {
        val api = api ?: return
        scope.launch {
            try {
                api.setNote(tx.id, note)
                replace(tx.copy(note = note.trim().ifEmpty { null }))
                show(s.noteSaved)
            } catch (e: ApiException) {
                show(e.message ?: s.unexpected)
            }
        }
    }

    private fun replace(tx: Transaction) {
        val i = transactions.indexOfFirst { it.id == tx.id }
        if (i >= 0) transactions[i] = tx
        val top = sheets.indexOfLast { it is Sheet.Tx && it.tx.id == tx.id }
        if (top >= 0) sheets[top] = Sheet.Tx(tx)
    }

    // A changed category moves money between groups and may sort similar bookings too.
    private fun afterChange() {
        reloadTransactions()
        loadOverview()
        if (spending.value != null) loadSpending()
    }

    // --- bank sync ----------------------------------------------------------------------------

    var syncJob by mutableStateOf<Job?>(null)
        private set
    var syncError by mutableStateOf<String?>(null)
        private set
    private var syncTask: Task? = null
    val syncing: Boolean get() = syncJob?.state.let { it == "running" || it == "waiting" }

    fun startSync() {
        val api = api ?: return
        if (syncing) return
        syncTask?.cancel()
        syncError = null
        syncTask = scope.launch {
            try {
                var job = api.sync()
                syncJob = job
                while (job.state == "running" || job.state == "waiting") {
                    delay(1000)
                    job = api.job(job.id)
                    syncJob = job
                }
                if (job.state == "done") {
                    show(s.syncDone)
                    refreshAll()
                } else {
                    syncError = job.error ?: job.message.ifEmpty { s.unexpected }
                }
            } catch (e: CancellationException) {
                throw e
            } catch (e: ApiException) {
                syncError = e.message
            } catch (e: Exception) {
                syncError = s.unexpected
            }
        }
    }

    fun answerTan(tan: String?) {
        val api = api ?: return
        val job = syncJob ?: return
        scope.launch {
            try {
                api.answerTan(job.id, tan?.trim()?.ifEmpty { null })
            } catch (e: ApiException) {
                syncError = e.message
            }
        }
    }

    // --- plumbing -----------------------------------------------------------------------------

    private fun clearData() {
        overview.value = null
        spending.value = null
        fixed.value = null
        wealth.value = null
        categories.value = null
        transactions.clear()
        txLoaded = false
        txTotal = 0
        syncJob = null
        syncError = null
    }

    private fun <T> load(target: Loadable<T>, block: suspend (GroschenApi) -> T) {
        val api = api ?: return
        target.loading = true
        target.error = null
        scope.launch {
            try {
                target.value = block(api)
            } catch (e: CancellationException) {
                throw e
            } catch (e: ApiException) {
                target.error = e.message
            } catch (e: Exception) {
                target.error = s.unexpected
            } finally {
                target.loading = false
            }
        }
    }

    private fun update(change: StoredSettings.() -> StoredSettings) {
        settings = settings.change()
        platform.saveSettings(settings)
    }

    private fun makeApi(url: String) = GroschenApi(
        base = url.toHttpUrl(),
        userAgent = platform.userAgent,
        language = { lang.code },
        texts = { s },
    ).also { it.onLoggedOut = ::onLoggedOut }

    companion object {
        // What the phone signs, so a login signature can't be replayed to add a phone and back.
        // Must match backend/groschen/devices.py.
        val LOGIN_LABEL = "groschen-device-login:".toByteArray()
        val REGISTER_LABEL = "groschen-device-register:".toByteArray()

        val LOCK_CHOICES = listOf(0, 60, 300, 900)
    }
}
