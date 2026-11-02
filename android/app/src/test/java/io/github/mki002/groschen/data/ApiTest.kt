package io.github.mki002.groschen.data

import kotlinx.coroutines.runBlocking
import mockwebserver3.MockResponse
import mockwebserver3.MockWebServer
import kotlin.test.AfterTest
import kotlin.test.BeforeTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertNull
import kotlin.test.assertTrue

class ApiTest {
    private val server = MockWebServer()
    private val texts = object : GroschenApi.ApiTexts {
        override val unreachable = "unreachable"
        override val checkFields = "check"
        override fun failed(status: Int) = "failed $status"
    }

    @BeforeTest
    fun start() = server.start()

    @AfterTest
    fun stop() = server.close()

    private fun api() = GroschenApi(server.url("/"), "Groschen-Android/test", { "de" }, { texts })

    private fun json(body: String, code: Int = 200, vararg headers: Pair<String, String>) =
        MockResponse.Builder().code(code).body(body).addHeader("Content-Type", "application/json").apply {
            headers.forEach { (k, v) -> addHeader(k, v) }
        }.build()

    @Test
    fun `login keeps the session and sends it along`() = runBlocking {
        server.enqueue(json("""{"ok":true}""", 200, "Set-Cookie" to "groschen_session=abc123; HttpOnly; Path=/; SameSite=Lax"))
        server.enqueue(json("""{"has_user":true,"setup_complete":true,"user":{"id":1,"username":"alex","name":"Alex"}}"""))
        val api = api()
        api.login("alex", "secret")
        assertEquals("abc123", api.token)
        val status = api.status()
        assertEquals("Alex", status.user?.name)

        val login = server.takeRequest()
        assertEquals("POST", login.method)
        assertEquals("/api/login", login.url.encodedPath)
        assertEquals("1", login.headers["X-Groschen"])
        assertEquals("de", login.headers["X-Groschen-Lang"])
        assertTrue(login.body!!.utf8().contains("\"username\":\"alex\""))
        val next = server.takeRequest()
        assertEquals("groschen_session=abc123", next.headers["Cookie"])
        assertNull(next.headers["X-Groschen"])
    }

    @Test
    fun `an ended login is reported once`() = runBlocking {
        server.enqueue(json("""{"detail":"Not logged in."}""", 401))
        val api = api()
        api.token = "old"
        var ended = 0
        api.onLoggedOut = { ended++ }
        val e = assertFailsWith<ApiException> { api.available() }
        assertEquals(401, e.status)
        assertEquals("Not logged in.", e.message)
        assertEquals(1, ended)
        assertNull(api.token)
    }

    @Test
    fun `server messages and unknown fields`() = runBlocking {
        server.enqueue(json("""{"detail":[{"loc":["body","tan"],"msg":"too long"}]}""", 422))
        server.enqueue(json("""{"challenge_id":"c1","challenge":"AAEC","extra":"ignored"}"""))
        val api = api()
        assertEquals("check", assertFailsWith<ApiException> { api.answerTan("j1", "123") }.message)
        assertEquals("c1", api.deviceLoginChallenge().challengeId)
    }

    @Test
    fun `no server means unreachable`() = runBlocking {
        val api = api()
        server.close()
        val e = assertFailsWith<ApiException> { api.health() }
        assertEquals(0, e.status)
        assertEquals("unreachable", e.message)
    }
}
