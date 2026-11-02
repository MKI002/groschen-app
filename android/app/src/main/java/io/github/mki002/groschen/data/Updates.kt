package io.github.mki002.groschen.data

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.ensureActive
import kotlinx.coroutines.withContext
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.builtins.ListSerializer
import okhttp3.HttpUrl
import okhttp3.HttpUrl.Companion.toHttpUrl
import okhttp3.HttpUrl.Companion.toHttpUrlOrNull
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import java.io.File
import java.io.IOException
import java.security.MessageDigest
import java.util.concurrent.TimeUnit

/** A newer version of the app under the repository's GitHub Releases. */
data class AppRelease(
    val versionCode: Int,
    val versionName: String,
    val apkUrl: String,
    val size: Long,
    /** The APK's SHA-256 as GitHub lists it, in lower-case hex; null when GitHub gives none. */
    val sha256: String?,
    val page: String,
)

/** The update check or download didn't work; [reason] says why. */
class UpdateException(val reason: Reason, cause: Throwable? = null) : Exception(reason.name, cause) {
    enum class Reason { OFFLINE, BLOCKED, BROKEN }
}

/**
 * Looks for a newer app version under the repository's GitHub Releases and downloads it.
 *
 * It talks to GitHub only, over https: the API that lists the releases and the hosts GitHub keeps
 * release files on ([HOSTS]). Every request, each redirect included, is checked against that list
 * before it goes out. It sends no login and nothing about the user; GitHub sees the phone's IP
 * address. A download is kept only when its size and SHA-256 match what GitHub lists; that the APK
 * carries the same signature as the installed app is checked on the phone before it is installed.
 */
class UpdateChecker(
    private val repo: String,
    private val userAgent: String,
    private val api: HttpUrl = "https://api.github.com/".toHttpUrl(),
    private val allowed: (HttpUrl) -> Boolean = { it.isHttps && it.host in HOSTS },
    client: OkHttpClient? = null,
) {
    // Redirects are followed by hand, so a host off the list isn't even looked up.
    private val http = (client?.newBuilder() ?: OkHttpClient.Builder())
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .followRedirects(false)
        .followSslRedirects(false)
        .build()

    /** The newest release that is newer than [currentCode], or null. */
    suspend fun latest(currentCode: Int): AppRelease? {
        val url = api.newBuilder()
            .addPathSegments("repos/$repo/releases")
            .addQueryParameter("per_page", "20")
            .build()
        val text = fetch(url) { it.body.string() }
        return try {
            pick(text, currentCode)
        } catch (e: Exception) {
            throw UpdateException(UpdateException.Reason.BROKEN, e)
        }
    }

    /**
     * Downloads [release] into [target] and checks its size and SHA-256. On any mismatch the file
     * is deleted again. [progress] goes from 0 to 1.
     */
    suspend fun download(release: AppRelease, target: File, progress: (Float) -> Unit = {}) {
        val url = release.apkUrl.toHttpUrlOrNull() ?: throw UpdateException(UpdateException.Reason.BROKEN)
        val partial = File(target.parentFile, target.name + ".part")
        target.parentFile?.mkdirs()
        val digest = MessageDigest.getInstance("SHA-256")
        val job = currentCoroutineContext()
        var written = 0L
        try {
            fetch(url) { response ->
                val total = response.body.contentLength().takeIf { it > 0 } ?: release.size
                response.body.byteStream().use { input ->
                    partial.outputStream().use { output ->
                        val buffer = ByteArray(64 * 1024)
                        while (true) {
                            val n = input.read(buffer)
                            if (n < 0) break
                            job.ensureActive()
                            output.write(buffer, 0, n)
                            digest.update(buffer, 0, n)
                            written += n
                            if (total > 0) progress((written.toFloat() / total).coerceIn(0f, 1f))
                        }
                    }
                }
            }
            val sha = digest.digest().joinToString("") { "%02x".format(it) }
            if ((release.size > 0 && written != release.size) || (release.sha256 != null && sha != release.sha256)) {
                throw UpdateException(UpdateException.Reason.BROKEN)
            }
            if (!partial.renameTo(target)) throw UpdateException(UpdateException.Reason.BROKEN)
        } finally {
            partial.delete()
        }
    }

    private suspend fun <T> fetch(start: HttpUrl, read: (Response) -> T): T = withContext(Dispatchers.IO) {
        var url = start
        repeat(MAX_REDIRECTS + 1) {
            if (!allowed(url)) throw UpdateException(UpdateException.Reason.BLOCKED)
            val request = Request.Builder()
                .url(url)
                .header("User-Agent", userAgent)
                .header("Accept", if (url.host == api.host) "application/vnd.github+json" else "application/octet-stream")
                .build()
            val response = try {
                http.newCall(request).execute()
            } catch (e: IOException) {
                throw UpdateException(UpdateException.Reason.OFFLINE, e)
            }
            response.use {
                ensureActive()
                if (it.isRedirect) {
                    url = it.header("Location")?.let(url::resolve) ?: throw UpdateException(UpdateException.Reason.BROKEN)
                } else {
                    if (!it.isSuccessful) throw UpdateException(UpdateException.Reason.BROKEN)
                    return@withContext try {
                        read(it)
                    } catch (e: IOException) {
                        throw UpdateException(UpdateException.Reason.OFFLINE, e)
                    }
                }
            }
        }
        throw UpdateException(UpdateException.Reason.BROKEN)
    }

    @Serializable
    private data class GitHubRelease(
        @SerialName("tag_name") val tag: String = "",
        val draft: Boolean = false,
        val prerelease: Boolean = false,
        val body: String? = null,
        @SerialName("html_url") val page: String = "",
        val assets: List<GitHubAsset> = emptyList(),
    )

    @Serializable
    private data class GitHubAsset(
        val name: String = "",
        val size: Long = 0,
        val digest: String? = null,
        @SerialName("browser_download_url") val url: String = "",
    )

    companion object {
        /** GitHub's API, and where GitHub keeps release files (a download is sent on from github.com). */
        val HOSTS = setOf("api.github.com", "github.com", "objects.githubusercontent.com", "release-assets.githubusercontent.com")

        private const val MAX_REDIRECTS = 5

        // The app's releases are tagged android-v1.0.<build>; the build number is the app's version code.
        private val TAG = Regex("""^android-v(\d+\.\d+\.(\d+))$""")
        private val HEX = Regex("""^[0-9a-f]{64}$""")
        private val NOTES_SHA = Regex("""SHA-256 of the APK: `([0-9a-fA-F]{64})`""")

        /** The newest app release in GitHub's list of releases that is newer than [currentCode]. */
        fun pick(releasesJson: String, currentCode: Int): AppRelease? =
            json.decodeFromString(ListSerializer(GitHubRelease.serializer()), releasesJson)
                .asSequence()
                .filter { !it.draft && !it.prerelease }
                .mapNotNull { r ->
                    val m = TAG.matchEntire(r.tag) ?: return@mapNotNull null
                    val code = m.groupValues[2].toIntOrNull() ?: return@mapNotNull null
                    val apk = r.assets.firstOrNull { it.name.endsWith(".apk") && it.url.isNotBlank() } ?: return@mapNotNull null
                    val sha = apk.digest?.removePrefix("sha256:")?.lowercase()?.takeIf { HEX.matches(it) }
                        ?: r.body?.let { NOTES_SHA.find(it)?.groupValues?.get(1)?.lowercase() }
                    AppRelease(code, m.groupValues[1], apk.url, apk.size, sha, r.page)
                }
                .filter { it.versionCode > currentCode }
                .maxByOrNull { it.versionCode }
    }
}
