package io.github.mki002.groschen

import android.app.Application
import android.util.Log
import androidx.lifecycle.DefaultLifecycleObserver
import androidx.lifecycle.LifecycleOwner
import androidx.lifecycle.ProcessLifecycleOwner
import io.github.mki002.groschen.model.AppModel
import io.github.mki002.groschen.platform.AndroidPlatform
import kotlinx.coroutines.CoroutineExceptionHandler
import kotlinx.coroutines.MainScope
import kotlinx.coroutines.plus

/** Holds the app's state for as long as Android keeps the app alive, across screen rotations. */
class GroschenApplication : Application() {
    lateinit var platform: AndroidPlatform
        private set
    lateinit var model: AppModel
        private set

    override fun onCreate() {
        super.onCreate()
        platform = AndroidPlatform(this)
        // A mistake in the app shows a short note instead of closing the app.
        val mistakes = CoroutineExceptionHandler { _, e ->
            Log.e("Groschen", "Unexpected error", e)
            if (::model.isInitialized) model.show(model.s.unexpected)
        }
        model = AppModel(platform, MainScope() + mistakes)
        model.start()
        // Back from the background after a while: the fingerprint is asked again.
        ProcessLifecycleOwner.get().lifecycle.addObserver(
            object : DefaultLifecycleObserver {
                override fun onStart(owner: LifecycleOwner) = model.onForeground()

                override fun onStop(owner: LifecycleOwner) = model.onBackground()
            },
        )
    }
}
