package io.github.mki002.groschen.data

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertIs
import kotlin.test.assertTrue

class ServerAddressTest {
    private fun ok(input: String): ServerAddress.Result.Ok = assertIs(ServerAddress.parse(input))
    private fun bad(input: String): ServerAddress.Reason = assertIs<ServerAddress.Result.Bad>(ServerAddress.parse(input)).reason

    @Test
    fun `a home network address gets plain http`() {
        val r = ok("192.168.178.209:8420")
        assertEquals("http://192.168.178.209:8420/", r.url.toString())
        assertFalse(r.encrypted)
    }

    @Test
    fun `server names and tunnels count as private`() {
        assertEquals("http://nas:8420/", ok("nas:8420").url.toString())
        assertEquals("http://100.101.102.103:8420/", ok("100.101.102.103:8420").url.toString())
        assertEquals("http://nas.tail1234.ts.net:8420/", ok("nas.tail1234.ts.net:8420").url.toString())
        assertEquals("http://nas.fritz.box/", ok("http://nas.fritz.box/").url.toString())
        assertEquals("http://[fd7a:115c:a1e0::1]:8420/", ok("http://[fd7a:115c:a1e0::1]:8420").url.toString())
    }

    @Test
    fun `addresses on the internet need https`() {
        val r = ok("groschen.example.com")
        assertEquals("https://groschen.example.com/", r.url.toString())
        assertTrue(r.encrypted)
        assertEquals(ServerAddress.Reason.PUBLIC_HTTP, bad("http://groschen.example.com"))
        assertEquals(ServerAddress.Reason.PUBLIC_HTTP, bad("http://8.8.8.8:8420"))
        // Look-alikes of private names stay public.
        assertEquals(ServerAddress.Reason.PUBLIC_HTTP, bad("http://192.168.1.1.example.com"))
        assertEquals(ServerAddress.Reason.PUBLIC_HTTP, bad("http://evil-ts.net"))
    }

    @Test
    fun `paths are dropped and junk refused`() {
        assertEquals("http://nas:8420/", ok("http://nas:8420/settings/").url.toString())
        assertEquals(ServerAddress.Reason.EMPTY, bad("   "))
        assertEquals(ServerAddress.Reason.INVALID, bad("not an address"))
        assertEquals(ServerAddress.Reason.INVALID, bad("http://user:pw@nas:8420"))
        assertEquals(ServerAddress.Reason.INVALID, bad("ftp://nas"))
    }
}
