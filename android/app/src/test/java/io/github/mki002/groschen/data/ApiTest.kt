package io.github.mki002.groschen.data

import kotlinx.coroutines.asCoroutineDispatcher
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withContext
import mockwebserver3.MockResponse
import mockwebserver3.MockWebServer
import okhttp3.OkHttpClient
import java.io.FilterInputStream
import java.io.InputStream
import java.net.InetAddress
import java.net.Socket
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import javax.net.SocketFactory
import kotlin.test.AfterTest
import kotlin.test.BeforeTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertNull
import kotlin.test.assertTrue
import kotlin.test.fail

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
    fun `answers are read on the network thread, never on the caller's`() {
        // Android closes an app that reads from the network on the thread that draws the screen.
        // Here a socket refuses reads on the "screen" thread, and the answer arrives slowly, so
        // it can't be read in one go together with the headers.
        val big = (1..400).joinToString(",", "[", "]") { """{"id":$it,"name":"Category $it","group":"G"}""" }
        server.enqueue(json(big).newBuilder().throttleBody(512, 5, TimeUnit.MILLISECONDS).build())
        val client = OkHttpClient.Builder().socketFactory(NoReadsOn("screen")).build()
        val api = GroschenApi(server.url("/"), "Groschen-Android/test", { "de" }, { texts }, client)
        val screen = Executors.newSingleThreadExecutor { Thread(it, "screen") }
        try {
            val categories = runBlocking { withContext(screen.asCoroutineDispatcher()) { api.categories() } }
            assertEquals(400, categories.size)
        } finally {
            screen.shutdown()
        }
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

/** Sockets whose reads fail on one thread, like Android's rule for the screen thread. */
private class NoReadsOn(private val thread: String) : SocketFactory() {
    override fun createSocket(): Socket = object : Socket() {
        override fun getInputStream(): InputStream = object : FilterInputStream(super.getInputStream()) {
            override fun read(): Int = guard { super.read() }
            override fun read(b: ByteArray, off: Int, len: Int): Int = guard { super.read(b, off, len) }
        }
    }

    private inline fun <T> guard(read: () -> T): T {
        // Coroutines add " @coroutine#1" to the name while tests run.
        if (Thread.currentThread().name.startsWith(thread)) fail("read from the network on the $thread thread")
        return read()
    }

    override fun createSocket(host: String, port: Int): Socket = unused()
    override fun createSocket(host: String, port: Int, localHost: InetAddress, localPort: Int): Socket = unused()
    override fun createSocket(host: InetAddress, port: Int): Socket = unused()
    override fun createSocket(address: InetAddress, port: Int, localAddress: InetAddress, localPort: Int): Socket = unused()
    private fun unused(): Nothing = throw UnsupportedOperationException()
}
