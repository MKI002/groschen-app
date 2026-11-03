package io.github.mki002.groschen.model

import androidx.compose.ui.graphics.ImageBitmap
import java.io.File

/** What the app keeps on the phone between starts. Nothing here is a secret. */
data class StoredSettings(
    val server: String? = null,
    val username: String = "",
    /** The fingerprint login: the key's id on the server and the phone's entry there. */
    val deviceKeyId: String? = null,
    val deviceId: Int? = null,
    /** A phone entry to clean up on the server after the fingerprint key was lost. */
    val staleDeviceId: Int? = null,
    /** "auto" follows the server's language, then the phone's. */
    val language: String = "auto",
    val hideAmounts: Boolean = false,
    /** Seconds in the background before the fingerprint is asked again. */
    val lockAfterSeconds: Int = 60,
    /** The fingerprint offer after the first password login was answered. */
    val fingerprintOffered: Boolean = false,
    /** Look for new app versions on GitHub, once a day. */
    val updateCheck: Boolean = true,
    /** When GitHub was last asked, in milliseconds since 1970. */
    val lastUpdateCheck: Long = 0,
)

enum class Biometrics { READY, NOT_ENROLLED, UNAVAILABLE }

sealed interface SignResult {
    class Signed(val signature: ByteArray) : SignResult
    data object Cancelled : SignResult

    /** The key is gone: new fingerprints were added on the phone, or the screen lock was removed. */
    data object KeyGone : SignResult
    data class Failed(val message: String) : SignResult
}

/** What the phone found in a downloaded update. */
enum class ApkCheck {
    OK,

    /** Another app, or signed with another key than the installed one. */
    NOT_OURS,

    /** Not newer than the installed version. */
    NOT_NEWER,
    UNREADABLE,
}

/** The texts on the phone's own fingerprint dialog. */
data class PromptText(val title: String, val subtitle: String)

/**
 * What the app needs from the phone. On Android: preferences, the Keystore and the system's
 * fingerprint dialog (platform/AndroidPlatform.kt).
 */
interface Platform {
    fun loadSettings(): StoredSettings
    fun saveSettings(settings: StoredSettings)

    /** The login session while the fingerprint login is off, kept encrypted with a Keystore key. */
    fun loadSession(): String?
    fun saveSession(token: String?)

    fun biometrics(): Biometrics

    /** Makes a new key pair in the phone's secure hardware (replacing an old one) and returns its public half. */
    suspend fun newDeviceKey(): ByteArray

    /** Signs with the device key after the fingerprint (or phone PIN) check. */
    suspend fun signWithDeviceKey(message: ByteArray, prompt: PromptText): SignResult
    fun dropDeviceKey()

    /** "Pixel 9", for the list of phones in the web interface. */
    val deviceName: String
    val userAgent: String
    val appVersion: String

    /** The phone's language, "de" or "en". */
    val systemLanguage: String

    fun openInBrowser(url: String)

    /** A picture the bank sends with a TAN request (photoTAN, chipTAN QR). */
    fun decodeImage(bytes: ByteArray): ImageBitmap?

    /** A picture read at a fraction of its size, so its long side is at most about twice [maxSide]. */
    fun decodeSmallImage(bytes: ByteArray, maxSide: Int): ImageBitmap?

    // --- updates from GitHub Releases -----------------------------------------------------

    /** The installed version's build number, the same as in the release's name. */
    val versionCode: Int

    /** Only the released app updates itself; a build of your own has no release to follow. */
    val updatesPossible: Boolean

    /** The GitHub repository whose releases the app follows, "owner/name". */
    val updateRepo: String

    /** Where a downloaded update is kept until it is installed. */
    fun updateFile(versionCode: Int): File

    /** Deletes downloaded updates that are installed now, or older. */
    fun dropOldUpdates()

    /** Wi-Fi or another network without a data limit: updates download by themselves. */
    fun onUnmeteredNetwork(): Boolean

    /** Is [file] this app, signed with the same key as the installed one, with the expected [versionCode]? */
    fun checkApk(file: File, versionCode: Int): ApkCheck

    /** Android lets this app install apps (the "install unknown apps" setting). */
    fun mayInstallApps(): Boolean

    /** Opens Android's setting that lets this app install apps. */
    fun askToInstallApps()

    /** Hands the APK to Android's installer; the outcome comes back through [AppModel.installResult]. */
    fun install(file: File)
}
