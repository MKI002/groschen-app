package io.github.mki002.groschen.platform

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.pm.PackageInstaller
import android.os.Build
import io.github.mki002.groschen.GroschenApplication

/**
 * Hears from Android's installer how an update went. When Android wants the user to confirm the
 * update first, it hands over its own confirmation screen, which is shown right away.
 */
class UpdateReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val app = context.applicationContext as GroschenApplication
        when (val status = intent.getIntExtra(PackageInstaller.EXTRA_STATUS, PackageInstaller.STATUS_FAILURE)) {
            PackageInstaller.STATUS_PENDING_USER_ACTION -> {
                val confirm = if (Build.VERSION.SDK_INT >= 33) {
                    intent.getParcelableExtra(Intent.EXTRA_INTENT, Intent::class.java)
                } else {
                    @Suppress("DEPRECATION")
                    intent.getParcelableExtra(Intent.EXTRA_INTENT)
                }
                val shown = confirm != null && runCatching {
                    (app.platform.activity ?: context).startActivity(confirm.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
                }.isSuccess
                if (!shown) app.model.installResult(success = false, cancelled = false)
            }
            PackageInstaller.STATUS_SUCCESS -> app.model.installResult(success = true, cancelled = false)
            else -> app.model.installResult(success = false, cancelled = status == PackageInstaller.STATUS_FAILURE_ABORTED)
        }
    }
}
