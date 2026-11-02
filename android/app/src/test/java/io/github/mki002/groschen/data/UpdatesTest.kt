package io.github.mki002.groschen.data

import kotlinx.coroutines.runBlocking
import mockwebserver3.MockResponse
import mockwebserver3.MockWebServer
import okio.Buffer
import java.io.File
import java.nio.file.Files
import java.security.MessageDigest
import kotlin.test.AfterTest
import kotlin.test.BeforeTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertFalse
import kotlin.test.assertNull
import kotlin.test.assertTrue

class UpdatesTest {
    private val server = MockWebServer()
    private val dir: File = Files.createTempDirectory("updates").toFile()

    @BeforeTest
    fun start() = server.start()

    @AfterTest
    fun stop() {
        server.close()
        dir.deleteRecursively()
    }

    private fun release(tag: String, apk: String? = "groschen-${tag.removePrefix("android-v")}.apk", extra: String = "") =
        """{"tag_name":"$tag","html_url":"https://github.com/o/r/releases/tag/$tag","body":"notes",$extra
            "assets":[${apk?.let { """{"name":"$it","size":3,"browser_download_url":"https://github.com/o/r/releases/download/$tag/$it"}""" } ?: ""}]}"""

    @Test
    fun `the newest app release that is newer wins`() {
        val list = "[" + listOf(
            release("android-v1.0.7"),
            release("android-v1.0.12"),
            release("android-v1.0.13", extra = """"draft":true,"""),
            release("android-v1.0.14", extra = """"prerelease":true,"""),
            release("v2.0.0"),
            release("android-v1.0.15", apk = null),
            release("android-v1.0.9"),
        ).joinToString(",") + "]"
        val r = UpdateChecker.pick(list, currentCode = 8)!!
        assertEquals(12, r.versionCode)
        assertEquals("1.0.12", r.versionName)
        assertEquals("https://github.com/o/r/releases/download/android-v1.0.12/groschen-1.0.12.apk", r.apkUrl)
        assertNull(UpdateChecker.pick(list, currentCode = 12))
        assertNull(UpdateChecker.pick("[]", currentCode = 1))
    }

    @Test
    fun `the checksum comes from GitHub, or else from the release notes`() {
        val sha = "a".repeat(64)
        val fromGitHub = """[{"tag_name":"android-v1.0.5","assets":[{"name":"g.apk","size":3,"digest":"sha256:${sha.uppercase()}",
            "browser_download_url":"https://github.com/x"}]}]"""
        assertEquals(sha, UpdateChecker.pick(fromGitHub, 1)!!.sha256)
        val fromNotes = """[{"tag_name":"android-v1.0.5","body":"SHA-256 of the APK: `$sha`",
            "assets":[{"name":"g.apk","size":3,"browser_download_url":"https://github.com/x"}]}]"""
        assertEquals(sha, UpdateChecker.pick(fromNotes, 1)!!.sha256)
    }

    private fun checker() = UpdateChecker("o/r", "Groschen-Android/test", api = server.url("/"), allowed = { true })

    private fun sha256(bytes: ByteArray) = MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }

    @Test
    fun `asks GitHub for the repository's releases`() = runBlocking {
        server.enqueue(MockResponse.Builder().body("[" + release("android-v1.0.4") + "]").build())
        val r = checker().latest(currentCode = 3)
        assertEquals(4, r?.versionCode)
        val request = server.takeRequest()
        assertEquals("/repos/o/r/releases", request.url.encodedPath)
        assertEquals("Groschen-Android/test", request.headers["User-Agent"])
        assertNull(request.headers["Cookie"])
    }

    @Test
    fun `a download is kept only when it matches`() = runBlocking {
        val apk = byteArrayOf(1, 2, 3)
        val target = File(dir, "groschen-4.apk")
        val good = AppRelease(4, "1.0.4", server.url("/a.apk").toString(), 3, sha256(apk), "")

        server.enqueue(MockResponse.Builder().body(Buffer().write(apk)).build())
        var last = 0f
        checker().download(good, target) { last = it }
        assertTrue(target.readBytes().contentEquals(apk))
        assertEquals(1f, last)
        target.delete()

        server.enqueue(MockResponse.Builder().body(Buffer().write(apk)).build())
        val e = assertFailsWith<UpdateException> { checker().download(good.copy(sha256 = "b".repeat(64)), target) }
        assertEquals(UpdateException.Reason.BROKEN, e.reason)
        assertFalse(target.exists())
        assertTrue(dir.listFiles().isNullOrEmpty(), "no half-downloaded file is left")
    }

    @Test
    fun `only GitHub's hosts are asked, also after a redirect`() = runBlocking {
        val onlyGitHub = UpdateChecker("o/r", "test")
        val e = assertFailsWith<UpdateException> {
            onlyGitHub.download(AppRelease(4, "1.0.4", server.url("/a.apk").toString(), 3, null, ""), File(dir, "x.apk"))
        }
        assertEquals(UpdateException.Reason.BLOCKED, e.reason)
        assertEquals(0, server.requestCount)

        // GitHub's API answers with a redirect to a host that is not on the list.
        val first = server.url("/")
        val redirecting = UpdateChecker("o/r", "test", api = first, allowed = { it.port == first.port && it.host == first.host })
        server.enqueue(MockResponse.Builder().code(302).addHeader("Location", "http://127.0.0.2:${first.port}/elsewhere").build())
        val e2 = assertFailsWith<UpdateException> { redirecting.latest(1) }
        assertEquals(UpdateException.Reason.BLOCKED, e2.reason)
        assertEquals(1, server.requestCount)
    }

    @Test
    fun `no network is reported as offline`() = runBlocking {
        val url = server.url("/")
        server.close()
        val e = assertFailsWith<UpdateException> { UpdateChecker("o/r", "test", api = url, allowed = { true }).latest(1) }
        assertEquals(UpdateException.Reason.OFFLINE, e.reason)
    }
}
