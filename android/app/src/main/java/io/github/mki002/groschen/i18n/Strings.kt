package io.github.mki002.groschen.i18n

import io.github.mki002.groschen.data.GroschenApi
import io.github.mki002.groschen.data.ServerAddress

// Every text of the app, in German and English. Placeholders in {braces} are filled by
// Sentence.tpl, so amounts inside a sentence can be hidden like every other figure.

fun strings(lang: Lang): Strings = if (lang == Lang.DE) De else En

interface Strings : GroschenApi.ApiTexts {
    // Pages and bars
    val tabOverview: String
    val tabTransactions: String
    val tabSpending: String
    val tabWealth: String
    val settings: String
    val showAmounts: String
    val hideAmounts: String
    val syncing: String
    val retry: String

    // Days and times
    val today: String
    val yesterday: String
    val tomorrow: String
    fun inDays(n: Int): String
    fun daysAgo(n: Int): String
    val never: String
    val justNow: String
    fun minutesAgo(n: Int): String
    fun todayAt(time: String): String
    fun yesterdayAt(time: String): String
    fun interval(name: String?): String
    fun spanDays(n: Int): String
    fun spanWeeks(n: Int): String
    fun spanMonths(n: Int): String
    fun spanYears(n: Int): String

    // Connect, log in, unlock
    val connectTitle: String
    val connectText: String
    val serverAddress: String
    val setupInBrowser: String
    val connect: String
    val connectSafety: String
    val loginTitle: String
    val change: String
    val username: String
    val password: String
    val login: String
    val useFingerprint: String
    val passwordOffHint: String
    val unlockTitle: String
    val unlockSubtitle: String
    fun hello(name: String): String
    val unlockHint: String
    val unlock: String
    val usePassword: String
    val offerTitle: String
    val offerText: String
    val turnOn: String
    val later: String
    fun addressError(reason: ServerAddress.Reason): String
    val notGroschen: String
    val setupFirst: String
    fun unreachableHost(host: String): String
    val fillBoth: String
    val fingerprintUnavailable: String
    val fingerprintChanged: String
    val phoneRemoved: String
    val fingerprintNotEnrolled: String
    val setupTitle: String
    val setupSubtitle: String
    val fingerprintIsOn: String
    val fingerprintFailed: String
    val fingerprintIsOff: String
    val fingerprintOffLogin: String
    val sessionEnded: String

    // Little confirmations
    val hintHidden: String
    val unexpected: String
    fun categorySavedSimilar(n: Int): String
    val categorySaved: String
    fun acceptedSimilar(n: Int): String
    val accepted: String
    val noteSaved: String
    val syncDone: String

    // Overview
    val availableUntilPayday: String
    val availableUntilMonthEnd: String
    val noCheckingAccount: String
    val openWeb: String
    val perDay: String
    val overspent: String
    fun daysToPayday(n: Int): String
    fun daysToMonthEnd(n: Int): String
    val salary: String
    fun paymentsToCome(n: Int): String
    val nothingMoreToCome: String
    fun balanceFrom(date: String): String
    val bufferNote: String
    val worthALook: String
    val allCalm: String
    fun reviewHint(n: Int): String
    val reviewHintMore: String
    val check: String
    val show: String
    val hideHint: String
    fun monthSoFar(month: String): String
    val spent: String
    val leftOver: String
    val overIncome: String
    val income: String

    // Hints (the same wording as the web interface)
    val hintDup: String
    val hintDupMore: String
    val hintPrice: String
    val hintPriceMore: String
    val hintCheaper: String
    val hintCheaperMore: String
    val hintBig: String
    val hintBigOn: String
    val hintNew: String
    val hintUsual: String
    val hintUsualCat: String
    val thisCategory: String
    val hintSubNew: String
    val hintSubNewMore: String
    val hintSubEnded: String
    val hintSubEndedMore: String
    val hintSubResumed: String
    val hintSubResumedMore: String

    // Transactions
    fun bookingCount(n: Int): String
    val search: String
    val searchHint: String
    val clear: String
    fun txFilter(filter: String): String
    fun nothingFound(query: String): String
    fun noBookings(filter: String): String
    val checkThis: String
    val noCategory: String
    val category: String
    val close: String
    val sortedByItself: String
    val looksRight: String
    val otherCategory: String
    val fromTheBank: String
    val note: String
    val saveNote: String
    val searchCategory: String

    // Spending and fixed costs
    fun period(preset: String): String
    val ofIncome: String
    val leftOverSentence: String
    val overSentence: String
    val perMonthSentence: String
    val noSpending: String
    fun fromBookings(n: Int): String
    val fixedCosts: String
    val noFixedCosts: String
    val fixedSentence: String
    fun priceChanges(n: Int): String
    fun endedOn(date: String): String
    val next: String
    val varies: String
    val fixedPerMonthYear: String
    val ended: String
    val fixedLearned: String
    val nothingHere: String
    fun shareOfSpending(pct: String, period: String): String
    val tapForBookings: String
    val stillToCome: String
    val upcomingSentence: String
    val upcomingSentenceMonth: String
    val allFixedCosts: String

    // Wealth
    val netWorth: String
    val changeThisYear: String
    val now: String
    val assetsDebts: String
    val depot: String
    val paidInSentence: String
    val gainSentence: String
    val lossSentence: String
    fun perYearReturn(pct: String): String
    val viewGain: String
    val viewValue: String
    val paidIn: String
    val planSentence: String
    val accounts: String
    val notCounted: String
    fun piecesAt(pieces: String): String
    val priceLastYear: String
    val gain: String
    val loss: String
    val oneYear: String
    val thisYear: String
    val shareOfDepot: String
    val savingsPlan: String

    // Settings and bank sync
    val server: String
    val encrypted: String
    val unencryptedLan: String
    val openWebSub: String
    fun loggedInAs(name: String): String
    val fingerprintLogin: String
    val fingerprintOnSub: String
    val fingerprintOffSub: String
    val lockAfter: String
    fun lockChoice(seconds: Int): String
    val logout: String
    val display: String
    val hideAmountsSub: String
    val language: String
    fun languageName(code: String): String
    val changeServer: String
    val changeServerConfirm: String
    val cancel: String
    fun versionLine(version: String): String
    val moreInWeb: String
    val bankSync: String
    val bankSyncText: String
    val noBankYet: String
    val syncNow: String
    val syncNote: String
    val bank: String
    fun lastSync(ago: String): String
    fun loginDaysLeft(n: Int): String
    val confirmInBankApp: String
    val tanTitle: String
    val tanText: String
    val tanLabel: String
    val tanSend: String
}

private fun plural(n: Int, one: String, other: String) = (if (n == 1) one else other).replace("{n}", n.toString())

object De : Strings {
    override val unreachable = "Der Server ist gerade nicht erreichbar."
    override val checkFields = "Bitte prüfe die Eingaben."
    override fun failed(status: Int) = "Der Server meldet einen Fehler ($status)."

    override val tabOverview = "Übersicht"
    override val tabTransactions = "Umsätze"
    override val tabSpending = "Ausgaben"
    override val tabWealth = "Vermögen"
    override val settings = "Einstellungen"
    override val showAmounts = "Beträge zeigen"
    override val hideAmounts = "Beträge verbergen"
    override val syncing = "Ruft ab …"
    override val retry = "Nochmal versuchen"

    override val today = "heute"
    override val yesterday = "gestern"
    override val tomorrow = "morgen"
    override fun inDays(n: Int) = "in $n Tagen"
    override fun daysAgo(n: Int) = "vor $n Tagen"
    override val never = "noch nie"
    override val justNow = "gerade eben"
    override fun minutesAgo(n: Int) = "vor $n Min."
    override fun todayAt(time: String) = "heute, $time"
    override fun yesterdayAt(time: String) = "gestern, $time"
    override fun interval(name: String?) = when (name) {
        "weekly" -> "wöchentlich"
        "biweekly" -> "alle 2 Wochen"
        "4-weekly" -> "alle 4 Wochen"
        "monthly" -> "monatlich"
        "bimonthly" -> "alle 2 Monate"
        "quarterly" -> "vierteljährlich"
        "half-yearly" -> "halbjährlich"
        "yearly" -> "jährlich"
        else -> "regelmäßig"
    }
    override fun spanDays(n: Int) = plural(n, "1 Tag", "{n} Tagen")
    override fun spanWeeks(n: Int) = plural(n, "1 Woche", "{n} Wochen")
    override fun spanMonths(n: Int) = plural(n, "1 Monat", "{n} Monaten")
    override fun spanYears(n: Int) = plural(n, "1 Jahr", "{n} Jahren")

    override val connectTitle = "Mit deinem Groschen verbinden"
    override val connectText =
        "Gib die Adresse ein, unter der Groschen läuft, zum Beispiel die IP deines Servers mit dem Port 8420."
    override val serverAddress = "Server-Adresse"
    override val setupInBrowser = "Einrichtung im Browser abschließen"
    override val connect = "Verbinden"
    override val connectSafety =
        "Zu Hause reicht die Adresse deines Servers im Heimnetz. Von unterwegs geht es über Tailscale, WireGuard " +
            "oder eine https://-Adresse."
    override val loginTitle = "Anmelden"
    override val change = "Ändern"
    override val username = "Benutzername"
    override val password = "Passwort"
    override val login = "Anmelden"
    override val useFingerprint = "Mit Fingerabdruck"
    override val passwordOffHint =
        "Die Anmeldung mit Passwort ist auf dem Server ausgeschaltet. Schalte sie in der Weboberfläche unter " +
            "Einstellungen › Sicherheit kurz ein, um dieses Handy hinzuzufügen."
    override val unlockTitle = "Groschen entsperren"
    override val unlockSubtitle = "Mit Fingerabdruck oder Displaysperre"
    override fun hello(name: String) = "Hallo, $name"
    override val unlockHint = "Leg den Finger auf, um Groschen zu öffnen."
    override val unlock = "Entsperren"
    override val usePassword = "Mit Passwort anmelden"
    override val offerTitle = "Ab jetzt mit dem Fingerabdruck?"
    override val offerText =
        "Dann öffnet sich Groschen mit deinem Finger, ganz ohne Passwort. Der Schlüssel dafür bleibt im " +
            "Sicherheitschip dieses Handys und verlässt es nie."
    override val turnOn = "Einschalten"
    override val later = "Später"
    override fun addressError(reason: ServerAddress.Reason) = when (reason) {
        ServerAddress.Reason.EMPTY -> "Bitte gib die Adresse deines Groschen-Servers ein."
        ServerAddress.Reason.INVALID -> "Das sieht nicht nach einer Adresse aus. Beispiel: 192.168.178.20:8420"
        ServerAddress.Reason.PUBLIC_HTTP ->
            "Diese Adresse liegt im Internet, dafür braucht die App https://. Zu Hause nimm die Adresse im " +
                "Heimnetz, etwa 192.168.178.20:8420."
    }
    override val notGroschen = "Unter dieser Adresse antwortet kein Groschen."
    override val setupFirst = "Groschen ist noch nicht eingerichtet. Schließ die Einrichtung im Browser ab und verbinde dich dann."
    override fun unreachableHost(host: String) = "$host ist nicht erreichbar. Ist das Handy im selben Netz oder im VPN?"
    override val fillBoth = "Bitte Benutzername und Passwort eingeben."
    override val fingerprintUnavailable = "Auf diesem Handy ist gerade kein Fingerabdruck verfügbar."
    override val fingerprintChanged =
        "Die Fingerabdrücke auf dem Handy haben sich geändert. Melde dich einmal mit dem Passwort an und schalte " +
            "den Fingerabdruck wieder ein."
    override val phoneRemoved = "Dieses Handy wurde in Groschen entfernt. Melde dich mit dem Passwort an."
    override val fingerprintNotEnrolled = "Richte zuerst in den Einstellungen des Handys einen Fingerabdruck ein."
    override val setupTitle = "Fingerabdruck einrichten"
    override val setupSubtitle = "Bestätige, damit Groschen dieses Handy kennt"
    override val fingerprintIsOn = "Fingerabdruck ist an."
    override val fingerprintFailed = "Der Fingerabdruck ließ sich nicht einrichten."
    override val fingerprintIsOff = "Fingerabdruck ist aus."
    override val fingerprintOffLogin = "Fingerabdruck ist aus. Melde dich mit dem Passwort an."
    override val sessionEnded = "Die Anmeldung ist abgelaufen. Bitte melde dich neu an."

    override val hintHidden = "Hinweis ausgeblendet."
    override val unexpected = "Da ist etwas schiefgelaufen. Versuch es gleich noch einmal."
    override fun categorySavedSimilar(n: Int) = plural(n, "Gespeichert, auch für 1 ähnliche Buchung.", "Gespeichert, auch für {n} ähnliche Buchungen.")
    override val categorySaved = "Kategorie gespeichert."
    override fun acceptedSimilar(n: Int) = plural(n, "Bestätigt, auch 1 ähnliche Buchung.", "Bestätigt, auch {n} ähnliche Buchungen.")
    override val accepted = "Bestätigt."
    override val noteSaved = "Notiz gespeichert."
    override val syncDone = "Abruf fertig."

    override val availableUntilPayday = "Frei verfügbar bis zum Gehalt"
    override val availableUntilMonthEnd = "Frei verfügbar bis Monatsende"
    override val noCheckingAccount = "Noch kein Girokonto. Verbinde deine Bank oder importiere eine CSV-Datei in der Weboberfläche."
    override val openWeb = "Weboberfläche öffnen"
    override val perDay = "Das sind etwa {amount} pro Tag."
    override val overspent = "Die Fixkosten bis zum Gehalt sind höher als der Kontostand."
    override fun daysToPayday(n: Int) = plural(n, "Tag bis zum Gehalt", "Tage bis zum Gehalt")
    override fun daysToMonthEnd(n: Int) = plural(n, "Tag bis Monatsende", "Tage bis Monatsende")
    override val salary = "Gehalt"
    override fun paymentsToCome(n: Int) = plural(n, "1 Zahlung kommt noch", "{n} Zahlungen kommen noch")
    override val nothingMoreToCome = "Bis dahin keine Fixkosten mehr"
    override fun balanceFrom(date: String) = "Kontostand vom $date. Ein Abruf holt den neuen."
    override val bufferNote = "{amount} sind als Puffer zurückgelegt."
    override val worthALook = "Einen Blick wert"
    override val allCalm = "Alles ruhig. Nichts Ungewöhnliches gefunden."
    override fun reviewHint(n: Int) = plural(n, "1 Buchung hat Groschen selbst einsortiert", "{n} Buchungen hat Groschen selbst einsortiert")
    override val reviewHintMore = ". Ein kurzer Blick, ob es passt?"
    override val check = "Ansehen"
    override val show = "Zeigen"
    override val hideHint = "Hinweis ausblenden"
    override fun monthSoFar(month: String) = "$month bisher"
    override val spent = "Ausgegeben"
    override val leftOver = "Übrig"
    override val overIncome = "Mehr als eingenommen"
    override val income = "Eingenommen"

    override val hintDup = "{name} hat {amount} doppelt abgebucht"
    override val hintDupMore = " ({first} und {second}). War das ein Versehen, fordere eine Buchung zurück."
    override val hintPrice = "{name} ist teurer geworden"
    override val hintPriceMore = ": {from} → {to} seit {date}, {year} mehr pro Jahr."
    override val hintCheaper = "{name} ist günstiger geworden"
    override val hintCheaperMore = ": {from} → {to} seit {date}, {year} weniger pro Jahr."
    override val hintBig = "{amount} an {name}"
    override val hintBigOn = " am {date}. "
    override val hintNew = "Die erste Zahlung an diesen Händler."
    override val hintUsual = "Sonst etwa {amount} hier."
    override val hintUsualCat = "Sonst etwa {amount} für {category}."
    override val thisCategory = "diese Kategorie"
    override val hintSubNew = "Neu dabei: {name}"
    override val hintSubNewMore = ", {amount} {interval} seit {date}."
    override val hintSubEnded = "{name} kommt nicht mehr"
    override val hintSubEndedMore = ": zuletzt {amount} am {date}. Das spart {year} im Jahr."
    override val hintSubResumed = "{name} ist wieder da"
    override val hintSubResumedMore = " nach {pause} Pause: {amount} {interval}."

    override fun bookingCount(n: Int) = plural(n, "1 Buchung", "{n} Buchungen")
    override val search = "Suchen"
    override val searchHint = "Händler, Text oder Betrag"
    override val clear = "Leeren"
    override fun txFilter(filter: String) = when (filter) {
        "review" -> "Prüfen"
        "unc" -> "Ohne Kategorie"
        "income" -> "Eingänge"
        else -> "Alle"
    }
    override fun nothingFound(query: String) = "Nichts gefunden für „$query“."
    override fun noBookings(filter: String) = if (filter == "review") "Alles geprüft. Nichts wartet auf dich." else "Keine Buchungen."
    override val checkThis = "prüfen"
    override val noCategory = "Ohne Kategorie"
    override val category = "Kategorie"
    override val close = "Schließen"
    override val sortedByItself = "Groschen hat diese Buchung selbst einsortiert. Passt das?"
    override val looksRight = "Passt"
    override val otherCategory = "Andere Kategorie"
    override val fromTheBank = "Von der Bank"
    override val note = "Notiz"
    override val saveNote = "Notiz speichern"
    override val searchCategory = "Kategorie suchen"

    override fun period(preset: String) = when (preset) {
        "month" -> "Dieser Monat"
        "last30" -> "30 Tage"
        "ytd" -> "Dieses Jahr"
        "last12" -> "12 Monate"
        else -> "Alles"
    }
    override val ofIncome = "von {amount} Einnahmen"
    override val leftOverSentence = ", {amount} übrig."
    override val overSentence = ", {amount} mehr als eingenommen."
    override val perMonthSentence = "Im Schnitt {amount} pro Monat."
    override val noSpending = "Keine Ausgaben in diesem Zeitraum."
    override fun fromBookings(n: Int) = plural(n, "Aus 1 Buchung.", "Aus {n} Buchungen.")
    override val fixedCosts = "Fixkosten"
    override val noFixedCosts = "Noch keine Fixkosten erkannt. Groschen lernt sie von selbst, sobald sie sich wiederholen."
    override val fixedSentence = "{count} Fixkosten, zusammen {amount} im Monat."
    override fun priceChanges(n: Int) = plural(n, "1 Preisänderung", "{n} Preisänderungen")
    override fun endedOn(date: String) = "Beendet, zuletzt $date"
    override val next = "nächste"
    override val varies = "schwankt"
    override val fixedPerMonthYear = "{month} im Monat, {year} im Jahr."
    override val ended = "Beendet"
    override val fixedLearned =
        "Groschen erkennt Fixkosten selbst an ihrem Rhythmus. Ändern oder ausblenden kannst du sie in der Weboberfläche."
    override val nothingHere = "Hier gibt es gerade nichts zu sehen."
    override fun shareOfSpending(pct: String, period: String) = "$pct der Ausgaben · $period"
    override val tapForBookings = "Tipp auf eine Kategorie, um ihre Buchungen zu sehen."
    override val stillToCome = "Kommt noch"
    override val upcomingSentence = "Bis zum Gehalt am {date} gehen noch {amount} ab."
    override val upcomingSentenceMonth = "Bis Monatsende ({date}) gehen noch {amount} ab."
    override val allFixedCosts = "Alle Fixkosten"

    override val netWorth = "Vermögen"
    override val changeThisYear = "{amount} seit Jahresbeginn"
    override val now = "jetzt"
    override val assetsDebts = "{assets} Guthaben, {debts} Schulden"
    override val depot = "Depot"
    override val paidInSentence = "{amount} eingezahlt"
    override val gainSentence = "{amount} Gewinn"
    override val lossSentence = "{amount} Verlust"
    override fun perYearReturn(pct: String) = "$pct Rendite pro Jahr"
    override val viewGain = "Gewinn"
    override val viewValue = "Wert"
    override val paidIn = "Eingezahlt"
    override val planSentence = "Sparplan: {amount} im Monat"
    override val accounts = "Konten"
    override val notCounted = "nicht mitgezählt"
    override fun piecesAt(pieces: String) = "$pieces Stück zu"
    override val priceLastYear = "Kurs im letzten Jahr"
    override val gain = "Gewinn"
    override val loss = "Verlust"
    override val oneYear = "1 Jahr"
    override val thisYear = "Dieses Jahr"
    override val shareOfDepot = "Anteil am Depot"
    override val savingsPlan = "Sparplan"

    override val server = "Server"
    override val encrypted = "Verschlüsselt (HTTPS)"
    override val unencryptedLan = "Heimnetz oder VPN, HTTPS nicht nötig"
    override val openWebSub = "Bank, Kategorien, Backups und alles Weitere"
    override fun loggedInAs(name: String) = "Angemeldet als $name"
    override val fingerprintLogin = "Mit Fingerabdruck anmelden"
    override val fingerprintOnSub = "Groschen öffnet sich mit deinem Finger"
    override val fingerprintOffSub = "Anmeldung mit Passwort"
    override val lockAfter = "Wieder sperren nach"
    override fun lockChoice(seconds: Int) = when (seconds) {
        0 -> "Sofort"
        else -> "${seconds / 60} Min."
    }
    override val logout = "Abmelden"
    override val display = "Anzeige"
    override val hideAmountsSub = "Beträge unscharf zeigen, etwa unterwegs"
    override val language = "Sprache"
    override fun languageName(code: String) = when (code) {
        "de" -> "Deutsch"
        "en" -> "English"
        else -> "Automatisch"
    }
    override val changeServer = "Anderen Server verbinden"
    override val changeServerConfirm =
        "Die App vergisst diesen Server, die Anmeldung und den Fingerabdruck. Deine Daten bleiben auf dem Server."
    override val cancel = "Abbrechen"
    override fun versionLine(version: String) = "Groschen für Android $version"
    override val moreInWeb = "Alles Weitere stellst du in der Weboberfläche ein."
    override val bankSync = "Bankabruf"
    override val bankSyncText = "Groschen holt neue Umsätze jeden Tag von selbst. Hier geht es sofort."
    override val noBankYet = "Noch keine Bank verbunden. Das richtest du in der Weboberfläche ein."
    override val syncNow = "Jetzt abrufen"
    override val syncNote = "Nur lesend: Groschen kann bei deiner Bank nichts überweisen."
    override val bank = "Bank"
    override fun lastSync(ago: String) = "Zuletzt abgerufen: $ago"
    override fun loginDaysLeft(n: Int) = plural(n, "In 1 Tag bei der Bank neu bestätigen", "In {n} Tagen bei der Bank neu bestätigen")
    override val confirmInBankApp = "Bitte in der App deiner Bank bestätigen."
    override val tanTitle = "TAN eingeben"
    override val tanText = "Deine Bank fragt nach einer TAN."
    override val tanLabel = "TAN"
    override val tanSend = "Senden"
}

object En : Strings {
    override val unreachable = "The server can't be reached right now."
    override val checkFields = "Please check what you typed."
    override fun failed(status: Int) = "The server reported an error ($status)."

    override val tabOverview = "Overview"
    override val tabTransactions = "Transactions"
    override val tabSpending = "Spending"
    override val tabWealth = "Wealth"
    override val settings = "Settings"
    override val showAmounts = "Show amounts"
    override val hideAmounts = "Hide amounts"
    override val syncing = "Syncing …"
    override val retry = "Try again"

    override val today = "today"
    override val yesterday = "yesterday"
    override val tomorrow = "tomorrow"
    override fun inDays(n: Int) = "in $n days"
    override fun daysAgo(n: Int) = "$n days ago"
    override val never = "never"
    override val justNow = "just now"
    override fun minutesAgo(n: Int) = "$n min ago"
    override fun todayAt(time: String) = "today, $time"
    override fun yesterdayAt(time: String) = "yesterday, $time"
    override fun interval(name: String?) = when (name) {
        "weekly" -> "weekly"
        "biweekly" -> "every 2 weeks"
        "4-weekly" -> "every 4 weeks"
        "monthly" -> "monthly"
        "bimonthly" -> "every 2 months"
        "quarterly" -> "quarterly"
        "half-yearly" -> "twice a year"
        "yearly" -> "yearly"
        else -> "regularly"
    }
    override fun spanDays(n: Int) = plural(n, "1 day", "{n} days")
    override fun spanWeeks(n: Int) = plural(n, "1 week", "{n} weeks")
    override fun spanMonths(n: Int) = plural(n, "1 month", "{n} months")
    override fun spanYears(n: Int) = plural(n, "1 year", "{n} years")

    override val connectTitle = "Connect to your Groschen"
    override val connectText = "Type the address Groschen runs at, for example your server's IP with port 8420."
    override val serverAddress = "Server address"
    override val setupInBrowser = "Finish the setup in the browser"
    override val connect = "Connect"
    override val connectSafety =
        "At home, your server's address in your home network is enough. On the go, connect over Tailscale, " +
            "WireGuard or an https:// address."
    override val loginTitle = "Log in"
    override val change = "Change"
    override val username = "Username"
    override val password = "Password"
    override val login = "Log in"
    override val useFingerprint = "Use fingerprint"
    override val passwordOffHint =
        "Password login is turned off on the server. Turn it on for a moment in the web interface under " +
            "Settings › Security to add this phone."
    override val unlockTitle = "Unlock Groschen"
    override val unlockSubtitle = "With your fingerprint or screen lock"
    override fun hello(name: String) = "Hello, $name"
    override val unlockHint = "Touch the sensor to open Groschen."
    override val unlock = "Unlock"
    override val usePassword = "Log in with password"
    override val offerTitle = "Use your fingerprint from now on?"
    override val offerText =
        "Groschen then opens with your finger, no password needed. The key for it stays in this phone's security " +
            "chip and never leaves it."
    override val turnOn = "Turn on"
    override val later = "Later"
    override fun addressError(reason: ServerAddress.Reason) = when (reason) {
        ServerAddress.Reason.EMPTY -> "Please type the address of your Groschen server."
        ServerAddress.Reason.INVALID -> "That doesn't look like an address. Example: 192.168.178.20:8420"
        ServerAddress.Reason.PUBLIC_HTTP ->
            "This address is on the internet, so the app needs https:// for it. At home, use the address in your " +
                "home network, like 192.168.178.20:8420."
    }
    override val notGroschen = "No Groschen answers at this address."
    override val setupFirst = "Groschen isn't set up yet. Finish the setup in the browser, then connect."
    override fun unreachableHost(host: String) = "$host can't be reached. Is the phone on the same network or the VPN?"
    override val fillBoth = "Please type your username and password."
    override val fingerprintUnavailable = "No fingerprint is available on this phone right now."
    override val fingerprintChanged =
        "The fingerprints on this phone changed. Log in once with your password and turn the fingerprint back on."
    override val phoneRemoved = "This phone was removed in Groschen. Please log in with your password."
    override val fingerprintNotEnrolled = "Set up a fingerprint in the phone's settings first."
    override val setupTitle = "Set up fingerprint"
    override val setupSubtitle = "Confirm so Groschen knows this phone"
    override val fingerprintIsOn = "Fingerprint is on."
    override val fingerprintFailed = "The fingerprint couldn't be set up."
    override val fingerprintIsOff = "Fingerprint is off."
    override val fingerprintOffLogin = "Fingerprint is off. Please log in with your password."
    override val sessionEnded = "Your login has expired. Please log in again."

    override val hintHidden = "Hint hidden."
    override val unexpected = "Something went wrong. Please try again in a moment."
    override fun categorySavedSimilar(n: Int) = plural(n, "Saved, for 1 similar booking too.", "Saved, for {n} similar bookings too.")
    override val categorySaved = "Category saved."
    override fun acceptedSimilar(n: Int) = plural(n, "Confirmed, 1 similar booking too.", "Confirmed, {n} similar bookings too.")
    override val accepted = "Confirmed."
    override val noteSaved = "Note saved."
    override val syncDone = "Sync finished."

    override val availableUntilPayday = "Free to spend until payday"
    override val availableUntilMonthEnd = "Free to spend until month end"
    override val noCheckingAccount = "No current account yet. Connect your bank or import a CSV file in the web interface."
    override val openWeb = "Open web interface"
    override val perDay = "That's about {amount} a day."
    override val overspent = "The fixed costs until payday are more than the balance."
    override fun daysToPayday(n: Int) = plural(n, "day until payday", "days until payday")
    override fun daysToMonthEnd(n: Int) = plural(n, "day until month end", "days until month end")
    override val salary = "Salary"
    override fun paymentsToCome(n: Int) = plural(n, "1 payment still to come", "{n} payments still to come")
    override val nothingMoreToCome = "No more fixed costs until then"
    override fun balanceFrom(date: String) = "Balance from $date. A sync fetches the new one."
    override val bufferNote = "{amount} is kept aside as a buffer."
    override val worthALook = "Worth a look"
    override val allCalm = "All calm. Nothing unusual found."
    override fun reviewHint(n: Int) = plural(n, "Groschen sorted 1 booking on its own", "Groschen sorted {n} bookings on its own")
    override val reviewHintMore = ". A quick look whether it fits?"
    override val check = "Check"
    override val show = "Show"
    override val hideHint = "Dismiss this hint"
    override fun monthSoFar(month: String) = "$month so far"
    override val spent = "Spent"
    override val leftOver = "Left over"
    override val overIncome = "More than came in"
    override val income = "Came in"

    override val hintDup = "{name} charged {amount} twice"
    override val hintDupMore = " ({first} and {second}). If it was a mistake, ask for one back."
    override val hintPrice = "{name} got more expensive"
    override val hintPriceMore = ": {from} → {to} since {date}, {year} more per year."
    override val hintCheaper = "{name} got cheaper"
    override val hintCheaperMore = ": {from} → {to} since {date}, {year} less per year."
    override val hintBig = "{amount} to {name}"
    override val hintBigOn = " on {date}. "
    override val hintNew = "The first payment to this merchant."
    override val hintUsual = "Usually about {amount} here."
    override val hintUsualCat = "Usually about {amount} for {category}."
    override val thisCategory = "this category"
    override val hintSubNew = "New: {name}"
    override val hintSubNewMore = ", {amount} {interval} since {date}."
    override val hintSubEnded = "{name} stopped coming"
    override val hintSubEndedMore = ": last {amount} on {date}. That saves {year} a year."
    override val hintSubResumed = "{name} is back"
    override val hintSubResumedMore = " after a pause of {pause}: {amount} {interval}."

    override fun bookingCount(n: Int) = plural(n, "1 booking", "{n} bookings")
    override val search = "Search"
    override val searchHint = "Merchant, text or amount"
    override val clear = "Clear"
    override fun txFilter(filter: String) = when (filter) {
        "review" -> "To check"
        "unc" -> "No category"
        "income" -> "Incoming"
        else -> "All"
    }
    override fun nothingFound(query: String) = "Nothing found for “$query”."
    override fun noBookings(filter: String) = if (filter == "review") "All checked. Nothing is waiting for you." else "No bookings."
    override val checkThis = "check"
    override val noCategory = "No category"
    override val category = "Category"
    override val close = "Close"
    override val sortedByItself = "Groschen sorted this booking on its own. Does it fit?"
    override val looksRight = "Fits"
    override val otherCategory = "Other category"
    override val fromTheBank = "From the bank"
    override val note = "Note"
    override val saveNote = "Save note"
    override val searchCategory = "Search categories"

    override fun period(preset: String) = when (preset) {
        "month" -> "This month"
        "last30" -> "30 days"
        "ytd" -> "This year"
        "last12" -> "12 months"
        else -> "All time"
    }
    override val ofIncome = "of {amount} income"
    override val leftOverSentence = ", {amount} left over."
    override val overSentence = ", {amount} more than came in."
    override val perMonthSentence = "On average {amount} a month."
    override val noSpending = "No spending in this period."
    override fun fromBookings(n: Int) = plural(n, "From 1 booking.", "From {n} bookings.")
    override val fixedCosts = "Fixed costs"
    override val noFixedCosts = "No fixed costs found yet. Groschen learns them on its own once they repeat."
    override val fixedSentence = "{count} fixed costs, {amount} a month together."
    override fun priceChanges(n: Int) = plural(n, "1 price change", "{n} price changes")
    override fun endedOn(date: String) = "Ended, last on $date"
    override val next = "next"
    override val varies = "varies"
    override val fixedPerMonthYear = "{month} a month, {year} a year."
    override val ended = "Ended"
    override val fixedLearned = "Groschen finds fixed costs by their rhythm. Change or hide them in the web interface."
    override val nothingHere = "Nothing to see here right now."
    override fun shareOfSpending(pct: String, period: String) = "$pct of spending · $period"
    override val tapForBookings = "Tap a category to see its bookings."
    override val stillToCome = "Still to come"
    override val upcomingSentence = "Until payday on {date}, {amount} still goes out."
    override val upcomingSentenceMonth = "Until month end ({date}), {amount} still goes out."
    override val allFixedCosts = "All fixed costs"

    override val netWorth = "Net worth"
    override val changeThisYear = "{amount} since January"
    override val now = "now"
    override val assetsDebts = "{assets} assets, {debts} debts"
    override val depot = "Investments"
    override val paidInSentence = "{amount} paid in"
    override val gainSentence = "{amount} gain"
    override val lossSentence = "{amount} loss"
    override fun perYearReturn(pct: String) = "$pct return a year"
    override val viewGain = "Gain"
    override val viewValue = "Value"
    override val paidIn = "Paid in"
    override val planSentence = "Savings plan: {amount} a month"
    override val accounts = "Accounts"
    override val notCounted = "not counted"
    override fun piecesAt(pieces: String) = "$pieces units at"
    override val priceLastYear = "Price over the last year"
    override val gain = "Gain"
    override val loss = "Loss"
    override val oneYear = "1 year"
    override val thisYear = "This year"
    override val shareOfDepot = "Share of investments"
    override val savingsPlan = "Savings plan"

    override val server = "Server"
    override val encrypted = "Encrypted (HTTPS)"
    override val unencryptedLan = "Home network or VPN, no HTTPS needed"
    override val openWebSub = "Bank, categories, backups and everything else"
    override fun loggedInAs(name: String) = "Logged in as $name"
    override val fingerprintLogin = "Log in with fingerprint"
    override val fingerprintOnSub = "Groschen opens with your finger"
    override val fingerprintOffSub = "Log in with password"
    override val lockAfter = "Lock again after"
    override fun lockChoice(seconds: Int) = when (seconds) {
        0 -> "Right away"
        else -> "${seconds / 60} min"
    }
    override val logout = "Log out"
    override val display = "Display"
    override val hideAmountsSub = "Show amounts blurred, for example when out"
    override val language = "Language"
    override fun languageName(code: String) = when (code) {
        "de" -> "Deutsch"
        "en" -> "English"
        else -> "Automatic"
    }
    override val changeServer = "Connect another server"
    override val changeServerConfirm =
        "The app forgets this server, the login and the fingerprint. Your data stays on the server."
    override val cancel = "Cancel"
    override fun versionLine(version: String) = "Groschen for Android $version"
    override val moreInWeb = "Everything else is set in the web interface."
    override val bankSync = "Bank sync"
    override val bankSyncText = "Groschen fetches new bookings every day on its own. Here it happens right away."
    override val noBankYet = "No bank connected yet. You set that up in the web interface."
    override val syncNow = "Sync now"
    override val syncNote = "Read-only: Groschen can't move any money at your bank."
    override val bank = "Bank"
    override fun lastSync(ago: String) = "Last synced: $ago"
    override fun loginDaysLeft(n: Int) = plural(n, "Confirm at your bank again in 1 day", "Confirm at your bank again in {n} days")
    override val confirmInBankApp = "Please confirm in your bank's app."
    override val tanTitle = "Enter TAN"
    override val tanText = "Your bank asks for a TAN."
    override val tanLabel = "TAN"
    override val tanSend = "Send"
}
