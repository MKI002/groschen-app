package io.github.mki002.groschen.data

import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.serialization.KSerializer
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonNull
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.jsonPrimitive
import kotlinx.serialization.json.put
import kotlinx.serialization.serializer
import okhttp3.Call
import okhttp3.Callback
import okhttp3.HttpUrl
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.Response
import java.io.IOException
import java.util.concurrent.TimeUnit
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

/** The server said no (status 400-599), or couldn't be reached at all (status 0). */
class ApiException(val status: Int, message: String) : Exception(message)

val json = Json {
    ignoreUnknownKeys = true
    coerceInputValues = true
    explicitNulls = false
}

/**
 * Talks to one Groschen server, the same JSON API the web interface uses.
 *
 * The login is the server's session cookie. The app keeps it itself (in memory, or encrypted
 * on the phone when the fingerprint login is off) and sends it with every request. Changes carry
 * the `X-Groschen` header the server asks for, and answers come in the app's language.
 */
class GroschenApi(
    val base: HttpUrl,
    private val userAgent: String,
    private val language: () -> String,
    private val texts: () -> ApiTexts,
    client: OkHttpClient? = null,
) {
    /** Messages for failures that don't come from the server. */
    interface ApiTexts {
        val unreachable: String
        val checkFields: String
        fun failed(status: Int): String
    }

    private val http = client ?: OkHttpClient.Builder()
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .callTimeout(60, TimeUnit.SECONDS)
        // The app talks to this one server only; a redirect elsewhere is not followed.
        .followRedirects(false)
        .followSslRedirects(false)
        .build()

    @Volatile
    var token: String? = null

    /** Called when the server says the login has ended (401 outside the login calls). */
    var onLoggedOut: (() -> Unit)? = null

    // --- login --------------------------------------------------------------------------------

    suspend fun health(): Health = get("health")
    suspend fun status(): Status = get("status")

    suspend fun login(username: String, password: String) {
        send<JsonObject>("POST", "login", buildJsonObject {
            put("username", username)
            put("password", password)
        })
    }

    suspend fun logout() {
        runCatching { send<JsonObject>("POST", "logout", JsonObject(emptyMap())) }
        token = null
    }

    suspend fun deviceLoginChallenge(): Challenge = send("POST", "login/device/options", JsonObject(emptyMap()))

    suspend fun deviceLogin(keyId: String, challengeId: String, signature: String) {
        send<JsonObject>("POST", "login/device", buildJsonObject {
            put("key_id", keyId)
            put("challenge_id", challengeId)
            put("signature", signature)
        })
    }

    suspend fun deviceChallenge(): Challenge = send("POST", "devices/options", JsonObject(emptyMap()))

    suspend fun addDevice(challengeId: String, publicKey: String, signature: String, name: String): Device =
        send("POST", "devices", buildJsonObject {
            put("challenge_id", challengeId)
            put("public_key", publicKey)
            put("signature", signature)
            put("name", name)
        })

    suspend fun removeDevice(id: Int) {
        send<JsonObject>("DELETE", "devices/$id")
    }

    // --- pages --------------------------------------------------------------------------------

    suspend fun available(): Available = get("available")
    suspend fun alerts(): Alerts = get("alerts")
    suspend fun badges(): Badges = get("badges")
    suspend fun connections(): List<Connection> = get("connections")
    suspend fun cashflow(preset: String): Cashflow = get("cashflow", mapOf("preset" to preset))
    suspend fun categories(): List<Category> = get("categories")
    suspend fun fixedCosts(): FixedCosts = get("subscriptions")
    suspend fun netWorth(): NetWorth = get("networth")
    suspend fun investments(): Investments = get("investments")

    suspend fun transactions(query: String, filter: String, offset: Int, limit: Int = 80): TransactionPage =
        get(
            "transactions",
            mapOf("q" to query, "filter" to filter, "offset" to offset.toString(), "limit" to limit.toString()),
        )

    suspend fun setCategory(id: Int, categoryId: Int?, similar: Boolean): Changed =
        send("PATCH", "transactions/$id", buildJsonObject {
            put("category_id", categoryId?.let { JsonPrimitive(it) } ?: JsonNull)
            put("apply_to_similar", similar)
        })

    suspend fun setNote(id: Int, note: String) {
        send<JsonObject>("PATCH", "transactions/$id", buildJsonObject {
            put("note", note)
            put("set_category", false)
        })
    }

    suspend fun markReviewed(id: Int): Changed = send("POST", "transactions/$id/reviewed", JsonObject(emptyMap()))

    suspend fun dismissAlert(key: String) {
        send<JsonObject>("POST", "alerts/dismiss", buildJsonObject { put("key", key) })
    }

    // --- bank sync ----------------------------------------------------------------------------

    suspend fun sync(): Job = send("POST", "sync", JsonObject(emptyMap()))
    suspend fun job(id: String): Job = get("jobs/$id")

    suspend fun answerTan(jobId: String, tan: String?) {
        send<JsonObject>("POST", "jobs/$jobId/tan", buildJsonObject { put("tan", tan?.let { JsonPrimitive(it) } ?: JsonNull) })
    }

    // --- plumbing -----------------------------------------------------------------------------

    private suspend inline fun <reified T> get(path: String, query: Map<String, String> = emptyMap()): T =
        decode(serializer(), call("GET", path, null, query))

    private suspend inline fun <reified T> send(method: String, path: String, body: JsonElement? = null): T =
        decode(serializer(), call(method, path, body, emptyMap()))

    private fun <T> decode(serializer: KSerializer<T>, text: String): T =
        json.decodeFromString(serializer, text.ifBlank { "{}" })

    private suspend fun call(method: String, path: String, body: JsonElement?, query: Map<String, String>): String {
        val url = base.newBuilder().addPathSegment("api").addPathSegments(path).apply {
            query.forEach { (k, v) -> if (v.isNotEmpty()) addQueryParameter(k, v) }
        }.build()
        val request = Request.Builder()
            .url(url)
            .header("User-Agent", userAgent)
            .header("Accept", "application/json")
            .header("X-Groschen-Lang", language())
            .apply {
                token?.let { header("Cookie", "$SESSION_COOKIE=$it") }
                if (method == "GET") {
                    get()
                } else {
                    header("X-Groschen", "1")
                    method(method, (body ?: JsonObject(emptyMap())).toString().toRequestBody(JSON))
                }
            }
            .build()
        val response = try {
            http.newCall(request).await()
        } catch (e: IOException) {
            throw ApiException(0, texts().unreachable)
        }
        return response.use { r ->
            cookieFrom(r)
            val text = r.body.string()
            if (r.isSuccessful) return@use text
            if (r.code == 401 && !path.startsWith("login")) {
                token = null
                onLoggedOut?.invoke()
            }
            throw ApiException(r.code, messageFrom(text) ?: texts().failed(r.code))
        }
    }

    // The session the server hands out at login, or takes back at logout.
    private fun cookieFrom(r: Response) {
        for (line in r.headers("Set-Cookie")) {
            val pair = line.substringBefore(';')
            if (pair.substringBefore('=').trim() != SESSION_COOKIE) continue
            val value = pair.substringAfter('=').trim().trim('"')
            token = value.ifEmpty { null }
        }
    }

    private fun messageFrom(text: String): String? = runCatching {
        when (val detail = (json.parseToJsonElement(text) as? JsonObject)?.get("detail")) {
            is JsonPrimitive -> detail.jsonPrimitive.content
            is JsonArray -> texts().checkFields
            else -> null
        }
    }.getOrNull()

    companion object {
        const val SESSION_COOKIE = "groschen_session"
        private val JSON = "application/json".toMediaType()
    }
}

private suspend fun Call.await(): Response = suspendCancellableCoroutine { cont ->
    cont.invokeOnCancellation { cancel() }
    enqueue(object : Callback {
        override fun onFailure(call: Call, e: IOException) {
            if (cont.isActive) cont.resumeWithException(e)
        }

        override fun onResponse(call: Call, response: Response) {
            if (cont.isActive) cont.resume(response) else response.close()
        }
    })
}
