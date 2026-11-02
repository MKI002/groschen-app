package io.github.mki002.groschen.platform

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.graphics.BitmapFactory
import android.hardware.biometrics.BiometricManager
import android.hardware.biometrics.BiometricManager.Authenticators
import android.hardware.biometrics.BiometricPrompt
import android.os.Build
import android.os.CancellationSignal
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyPermanentlyInvalidatedException
import android.security.keystore.KeyProperties
import android.security.keystore.StrongBoxUnavailableException
import android.util.Base64
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.asImageBitmap
import androidx.core.content.edit
import androidx.core.net.toUri
import io.github.mki002.groschen.BuildConfig
import io.github.mki002.groschen.model.Biometrics
import io.github.mki002.groschen.model.Platform
import io.github.mki002.groschen.model.PromptText
import io.github.mki002.groschen.model.SignResult
import io.github.mki002.groschen.model.StoredSettings
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.withContext
import java.security.GeneralSecurityException
import java.security.KeyPairGenerator
import java.security.KeyStore
import java.security.PrivateKey
import java.security.Signature
import java.security.UnrecoverableKeyException
import java.security.spec.ECGenParameterSpec
import java.util.Locale
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec
import kotlin.coroutines.resume

/**
 * The phone's parts for the app: settings in the app's private storage, the login session
 * encrypted with a key in the Android Keystore, and the fingerprint login.
 *
 * The fingerprint login uses a key pair made inside the phone's secure hardware. Its private half
 * can't be read out, not even by the app, and every use needs the fingerprint (or the phone's
 * PIN): the system's own dialog unlocks the key for exactly one signature. New fingerprints on
 * the phone make the key invalid, so someone who adds their finger can't get in.
 */
class AndroidPlatform(private val app: Context) : Platform {
    private val prefs = app.getSharedPreferences("groschen", Context.MODE_PRIVATE)

    /** The screen the fingerprint dialog shows over. */
    @Volatile
    var activity: Activity? = null

    // --- settings -----------------------------------------------------------------------------

    override fun loadSettings() = StoredSettings(
        server = prefs.getString(SERVER, null),
        username = prefs.getString(USERNAME, null).orEmpty(),
        deviceKeyId = prefs.getString(KEY_ID, null),
        deviceId = prefs.getInt(DEVICE_ID, -1).takeIf { it >= 0 },
        staleDeviceId = prefs.getInt(STALE_DEVICE_ID, -1).takeIf { it >= 0 },
        language = prefs.getString(LANGUAGE, null) ?: "auto",
        hideAmounts = prefs.getBoolean(HIDE, false),
        lockAfterSeconds = prefs.getInt(LOCK_AFTER, 60),
        fingerprintOffered = prefs.getBoolean(OFFERED, false),
    )

    override fun saveSettings(settings: StoredSettings) = prefs.edit {
        putString(SERVER, settings.server)
        putString(USERNAME, settings.username)
        putString(KEY_ID, settings.deviceKeyId)
        putInt(DEVICE_ID, settings.deviceId ?: -1)
        putInt(STALE_DEVICE_ID, settings.staleDeviceId ?: -1)
        putString(LANGUAGE, settings.language)
        putBoolean(HIDE, settings.hideAmounts)
        putInt(LOCK_AFTER, settings.lockAfterSeconds)
        putBoolean(OFFERED, settings.fingerprintOffered)
    }

    // --- the login session, encrypted ---------------------------------------------------------

    private fun keyStore(): KeyStore = KeyStore.getInstance(KEYSTORE).apply { load(null) }

    private fun sessionKey(): SecretKey {
        (keyStore().getKey(SESSION_KEY, null) as? SecretKey)?.let { return it }
        val generator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, KEYSTORE)
        generator.init(
            KeyGenParameterSpec.Builder(SESSION_KEY, KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setKeySize(256)
                .build(),
        )
        return generator.generateKey()
    }

    override fun loadSession(): String? {
        val stored = prefs.getString(SESSION, null) ?: return null
        return try {
            val bytes = Base64.decode(stored, Base64.NO_WRAP)
            val cipher = Cipher.getInstance(AES_GCM)
            cipher.init(Cipher.DECRYPT_MODE, sessionKey(), GCMParameterSpec(128, bytes, 0, IV_SIZE))
            String(cipher.doFinal(bytes, IV_SIZE, bytes.size - IV_SIZE), Charsets.UTF_8)
        } catch (e: Exception) {
            // The key is gone (the app's data was moved or the key store reset): log in again.
            prefs.edit { remove(SESSION) }
            null
        }
    }

    override fun saveSession(token: String?) {
        if (token == null) {
            prefs.edit { remove(SESSION) }
            return
        }
        try {
            val cipher = Cipher.getInstance(AES_GCM)
            cipher.init(Cipher.ENCRYPT_MODE, sessionKey())
            val sealed = cipher.iv + cipher.doFinal(token.toByteArray(Charsets.UTF_8))
            prefs.edit { putString(SESSION, Base64.encodeToString(sealed, Base64.NO_WRAP)) }
        } catch (e: GeneralSecurityException) {
            // Without a working key store the login just isn't kept.
            prefs.edit { remove(SESSION) }
        }
    }

    // --- fingerprint --------------------------------------------------------------------------

    override fun biometrics(): Biometrics {
        val manager = app.getSystemService(BiometricManager::class.java) ?: return Biometrics.UNAVAILABLE
        return when (manager.canAuthenticate(AUTHENTICATORS)) {
            BiometricManager.BIOMETRIC_SUCCESS -> Biometrics.READY
            BiometricManager.BIOMETRIC_ERROR_NONE_ENROLLED -> Biometrics.NOT_ENROLLED
            else -> Biometrics.UNAVAILABLE
        }
    }

    override suspend fun newDeviceKey(): ByteArray = withContext(Dispatchers.Default) {
        dropDeviceKey()
        fun spec(strongBox: Boolean) = KeyGenParameterSpec.Builder(DEVICE_KEY, KeyProperties.PURPOSE_SIGN)
            .setAlgorithmParameterSpec(ECGenParameterSpec("secp256r1"))
            .setDigests(KeyProperties.DIGEST_SHA256)
            .setUserAuthenticationRequired(true)
            // Every single use needs the fingerprint or the phone's PIN, not just a recent unlock.
            .setUserAuthenticationParameters(0, KeyProperties.AUTH_BIOMETRIC_STRONG or KeyProperties.AUTH_DEVICE_CREDENTIAL)
            .setInvalidatedByBiometricEnrollment(true)
            .setIsStrongBoxBacked(strongBox)
            .build()
        val generator = KeyPairGenerator.getInstance(KeyProperties.KEY_ALGORITHM_EC, KEYSTORE)
        val pair = try {
            generator.initialize(spec(strongBox = true))
            generator.generateKeyPair()
        } catch (e: StrongBoxUnavailableException) {
            // No separate security chip: the phone's trusted environment keeps the key instead.
            generator.initialize(spec(strongBox = false))
            generator.generateKeyPair()
        }
        // X.509 SubjectPublicKeyInfo, the form the server stores.
        pair.public.encoded
    }

    override suspend fun signWithDeviceKey(message: ByteArray, prompt: PromptText): SignResult {
        val signature = try {
            val key = keyStore().getKey(DEVICE_KEY, null) as? PrivateKey ?: return SignResult.KeyGone
            Signature.getInstance("SHA256withECDSA").apply { initSign(key) }
        } catch (e: KeyPermanentlyInvalidatedException) {
            dropDeviceKey()
            return SignResult.KeyGone
        } catch (e: UnrecoverableKeyException) {
            dropDeviceKey()
            return SignResult.KeyGone
        } catch (e: GeneralSecurityException) {
            return SignResult.Failed(e.message ?: e.javaClass.simpleName)
        }
        val screen = activity ?: return SignResult.Cancelled
        return withContext(Dispatchers.Main) {
            suspendCancellableCoroutine { cont ->
                val cancel = CancellationSignal()
                cont.invokeOnCancellation { cancel.cancel() }
                val dialog = BiometricPrompt.Builder(screen)
                    .setTitle(prompt.title)
                    .setSubtitle(prompt.subtitle)
                    .setAllowedAuthenticators(AUTHENTICATORS)
                    .setConfirmationRequired(false)
                    .build()
                val callback = object : BiometricPrompt.AuthenticationCallback() {
                    override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                        val signed = try {
                            val unlocked = result.cryptoObject?.signature ?: signature
                            unlocked.update(message)
                            SignResult.Signed(unlocked.sign())
                        } catch (e: GeneralSecurityException) {
                            SignResult.Failed(e.message ?: e.javaClass.simpleName)
                        }
                        if (cont.isActive) cont.resume(signed)
                    }

                    override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                        val r = when (errorCode) {
                            BiometricPrompt.BIOMETRIC_ERROR_USER_CANCELED,
                            BiometricPrompt.BIOMETRIC_ERROR_CANCELED,
                            -> SignResult.Cancelled
                            else -> SignResult.Failed(errString.toString())
                        }
                        if (cont.isActive) cont.resume(r)
                    }
                    // A finger that isn't recognised: the dialog stays open for another try.
                }
                dialog.authenticate(BiometricPrompt.CryptoObject(signature), cancel, screen.mainExecutor, callback)
            }
        }
    }

    override fun dropDeviceKey() {
        runCatching { keyStore().deleteEntry(DEVICE_KEY) }
    }

    // --- about the phone ----------------------------------------------------------------------

    override val deviceName: String
        get() {
            val maker = Build.MANUFACTURER.replaceFirstChar { it.titlecase(Locale.ROOT) }
            val model = Build.MODEL.orEmpty()
            return if (model.startsWith(Build.MANUFACTURER, ignoreCase = true)) model else "$maker $model".trim()
        }

    override val userAgent: String
        get() = "Groschen-Android/${BuildConfig.VERSION_NAME} (Android ${Build.VERSION.RELEASE})"

    override val appVersion: String
        get() = BuildConfig.VERSION_NAME

    override val systemLanguage: String
        get() = if (Locale.getDefault().language == "de") "de" else "en"

    override fun openInBrowser(url: String) {
        val intent = Intent(Intent.ACTION_VIEW, url.toUri()).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        runCatching { (activity ?: app).startActivity(intent) }
    }

    override fun decodeImage(bytes: ByteArray): ImageBitmap? =
        BitmapFactory.decodeByteArray(bytes, 0, bytes.size)?.asImageBitmap()

    private companion object {
        const val KEYSTORE = "AndroidKeyStore"
        const val DEVICE_KEY = "groschen-device-login"
        const val SESSION_KEY = "groschen-session"
        const val AES_GCM = "AES/GCM/NoPadding"
        const val IV_SIZE = 12
        const val AUTHENTICATORS = Authenticators.BIOMETRIC_STRONG or Authenticators.DEVICE_CREDENTIAL

        const val SERVER = "server"
        const val USERNAME = "username"
        const val KEY_ID = "device_key_id"
        const val DEVICE_ID = "device_id"
        const val STALE_DEVICE_ID = "stale_device_id"
        const val LANGUAGE = "language"
        const val HIDE = "hide_amounts"
        const val LOCK_AFTER = "lock_after_seconds"
        const val OFFERED = "fingerprint_offered"
        const val SESSION = "session"
    }
}
