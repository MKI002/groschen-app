package io.github.mki002.groschen.data

import okhttp3.HttpUrl
import okhttp3.HttpUrl.Companion.toHttpUrlOrNull

/**
 * The address of the Groschen server, as typed in the app.
 *
 * Plain http:// is only accepted for addresses in a home network or a private tunnel
 * (192.168.x.x, a server name like "nas", Tailscale's 100.x.x.x and *.ts.net). Over the
 * internet the app insists on https://, so nobody between the phone and the server can read
 * along. At home the traffic stays in the own network, and the fingerprint login never sends
 * a password at all.
 */
object ServerAddress {
    sealed interface Result {
        data class Ok(val url: HttpUrl, val encrypted: Boolean) : Result
        data class Bad(val reason: Reason) : Result
    }

    enum class Reason { EMPTY, INVALID, PUBLIC_HTTP }

    // Names that only exist inside a home network or a private tunnel.
    private val PRIVATE_SUFFIXES = listOf(
        ".local", ".lan", ".home", ".home.arpa", ".internal", ".intranet", ".localdomain",
        ".fritz.box", ".ts.net",
    )

    fun parse(input: String): Result {
        var text = input.trim().trimEnd('/')
        if (text.isEmpty()) return Result.Bad(Reason.EMPTY)
        if (!text.contains("://")) {
            val host = text.substringBefore('/').substringBefore(':').removePrefix("[")
            text = (if (isPrivateHost(host)) "http://" else "https://") + text
        }
        val url = text.toHttpUrlOrNull() ?: return Result.Bad(Reason.INVALID)
        if (url.username.isNotEmpty() || url.password.isNotEmpty() || url.query != null || url.fragment != null) {
            return Result.Bad(Reason.INVALID)
        }
        if (url.scheme == "http" && !isPrivateHost(url.host)) return Result.Bad(Reason.PUBLIC_HTTP)
        // Groschen answers at the root of its address.
        val root = url.newBuilder().encodedPath("/").build()
        return Result.Ok(root, encrypted = root.isHttps)
    }

    fun isPrivateHost(host: String): Boolean {
        val h = host.lowercase().trim('[', ']').trimEnd('.')
        if (h.isEmpty()) return false
        if (h == "localhost") return true
        ipv4(h)?.let { return privateIpv4(it) }
        if (h.contains(':')) return privateIpv6(h)
        // A plain server name without a dot ("nas", "homeserver") only resolves in the home network.
        if (!h.contains('.')) return h.all { it.isLetterOrDigit() || it == '-' }
        return PRIVATE_SUFFIXES.any { h.endsWith(it) }
    }

    private fun ipv4(h: String): IntArray? {
        val parts = h.split('.')
        if (parts.size != 4) return null
        val out = IntArray(4)
        for ((i, p) in parts.withIndex()) {
            if (p.isEmpty() || p.length > 3 || !p.all(Char::isDigit)) return null
            val n = p.toInt()
            if (n > 255) return null
            out[i] = n
        }
        return out
    }

    private fun privateIpv4(ip: IntArray): Boolean {
        val (a, b) = ip[0] to ip[1]
        return a == 10 ||
            a == 127 ||
            (a == 172 && b in 16..31) ||
            (a == 192 && b == 168) ||
            (a == 169 && b == 254) ||
            // Tailscale and other private tunnels (carrier-grade NAT range)
            (a == 100 && b in 64..127)
    }

    private fun privateIpv6(h: String): Boolean {
        if (h == "::1") return true
        val first = h.substringBefore(':').ifEmpty { return false }
        val n = first.toIntOrNull(16) ?: return false
        // fc00::/7 (unique local, also Tailscale's fd7a:...) and fe80::/10 (link local)
        return (n and 0xfe00) == 0xfc00 || (n and 0xffc0) == 0xfe80
    }
}
