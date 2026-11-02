package io.github.mki002.groschen.model

import androidx.compose.ui.graphics.ImageBitmap

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
)

enum class Biometrics { READY, NOT_ENROLLED, UNAVAILABLE }

sealed interface SignResult {
    class Signed(val signature: ByteArray) : SignResult
    data object Cancelled : SignResult

    /** The key is gone: new fingerprints were added on the phone, or the screen lock was removed. */
    data object KeyGone : SignResult
    data class Failed(val message: String) : SignResult
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
}
