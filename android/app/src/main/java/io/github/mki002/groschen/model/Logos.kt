package io.github.mki002.groschen.model

import androidx.compose.runtime.mutableStateMapOf
import androidx.compose.ui.graphics.ImageBitmap
import io.github.mki002.groschen.data.GroschenApi
import io.github.mki002.groschen.data.MerchantLogo
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlinx.coroutines.Job as Task

/**
 * The merchants' logos, the same as in the web app: a built-in brand logo, a picture of the
 * user's own, or the letter. The server knows the built-in logos and what was picked on the
 * web, so it says which one each name gets. Names shown together are asked for in one go; the
 * answers and pictures are kept while the app runs, and a refresh asks again for changes.
 *
 * Everything here runs on the main thread; the network is read on OkHttp's threads and the
 * pictures are decoded in the background.
 */
class Logos(
    private val scope: CoroutineScope,
    private val api: () -> GroschenApi?,
    private val decode: (ByteArray) -> ImageBitmap?,
    private val warn: (String) -> Unit = {},
) {
    private val known = mutableStateMapOf<String, MerchantLogo>()
    private val pictures = mutableStateMapOf<String, ImageBitmap>()
    private val pending = LinkedHashSet<String>()
    private val asked = HashSet<String>()
    private val loading = HashSet<String>()

    /** Names whose request failed (offline, or a server from before the logos); asked again on refresh. */
    private val failed = LinkedHashSet<String>()
    private var asking: Task? = null

    /** Raised by [clear], so answers to an older login are dropped. */
    private var round = 0

    /** The logo for [name]; null until the server has answered (the letter shows meanwhile). */
    fun of(name: String): MerchantLogo? = known[name]

    /** Asks for [name]'s logo, together with the other names that appear on screen now. */
    fun want(name: String) {
        if (name.isBlank() || name.length > MAX_NAME || name in known || !asked.add(name)) return
        pending += name
        ask()
    }

    /** Asks again for every name shown so far: a logo may have been changed on the web. */
    fun refresh() {
        pending += known.keys
        pending += failed
        asked += failed
        failed.clear()
        ask()
    }

    fun clear() {
        round++
        asking?.cancel()
        asking = null
        known.clear()
        pictures.clear()
        pending.clear()
        asked.clear()
        loading.clear()
        failed.clear()
    }

    /** A user's own picture, once loaded. */
    fun picture(logo: MerchantLogo): ImageBitmap? = pictureId(logo)?.let { pictures[it] }

    fun wantPicture(logo: MerchantLogo) {
        val key = logo.key ?: return
        val id = pictureId(logo) ?: return
        if (id in pictures || !loading.add(id)) return
        val api = api()
        if (api == null) {
            loading.remove(id)
            return
        }
        val mine = round
        scope.launch {
            try {
                val bytes = api.logoImage(key, logo.v.orEmpty())
                val image = withContext(Dispatchers.Default) { decode(bytes) }
                if (image != null && mine == round) pictures[id] = image
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                // Offline or gone: the letter stays.
                warn("Logo picture $key: ${e.message ?: e::class.simpleName}")
            } finally {
                if (mine == round) loading.remove(id)
            }
        }
    }

    private fun pictureId(logo: MerchantLogo): String? = logo.key?.let { "$it?${logo.v.orEmpty()}" }

    private fun ask() {
        if (asking != null || pending.isEmpty()) return
        val mine = round
        asking = scope.launch {
            try {
                delay(BATCH_WAIT_MS) // the other rows on screen come in the same request
                while (pending.isNotEmpty() && mine == round) {
                    val api = api() ?: break
                    val names = pending.take(BATCH)
                    pending.removeAll(names.toSet())
                    val got = try {
                        api.logos(names)
                    } catch (e: CancellationException) {
                        throw e
                    } catch (e: Exception) {
                        // Asked again when the page is refreshed (or a row comes back into view).
                        warn("Logos for ${names.size} names: ${e.message ?: e::class.simpleName}")
                        asked.removeAll(names.toSet())
                        failed += names
                        break
                    }
                    if (mine != round) break
                    for (name in names) {
                        known[name] = got[name] ?: MerchantLogo()
                        failed.remove(name)
                    }
                }
            } finally {
                if (mine == round) asking = null
            }
        }
    }

    private companion object {
        const val MAX_NAME = 200
        const val BATCH = 200
        const val BATCH_WAIT_MS = 60L
    }
}
