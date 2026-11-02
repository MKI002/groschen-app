# Groschen for Android

A native Android app (Kotlin, Jetpack Compose) for your own Groschen server. It is not a web page
in a frame: every screen is drawn by the app, in the same dark look and with the Figtree font as
the web interface. It talks to your server's API and nothing else.

- **Overview:** what is free until payday, the payments still to come, the hints worth a look
  and the month so far.
- **Transactions:** search, filters (to check, no category, incoming), the booking's details,
  change the category (similar bookings follow), confirm Groschen's own guesses, notes.
- **Spending:** by group and category for this month, 30 days, this year or 12 months, and the
  fixed costs with price changes.
- **Wealth:** net worth over time, accounts, and the depot with the gain shown without your
  pay-ins.
- **Bank sync** with TAN entry, **hidden amounts** (blurred 9s, like on the web), German and
  English.
- **Fingerprint login:** log in once with your password, then the fingerprint (or the phone's
  PIN) opens the app.

Settings, the bank connection, backups and everything else stay in the web interface; the app
opens it in the browser when needed. Android 11 or newer.

## Install

1. On your phone, open the [latest Android release](https://github.com/MKI002/groschen-app/releases?q=android&expanded=true)
   and tap `groschen-….apk`.
2. Allow your browser to install apps when Android asks, then tap **Install**.
3. Open Groschen and type your server's address, for example `192.168.178.20:8420`.

**Updates:** install a newer APK over the old one; your login and settings stay. To be told
about new versions, add this repository to [Obtainium](https://github.com/ImranR98/Obtainium)
(it picks the APK from the releases by itself).

## The server address and plain http

Groschen usually runs at home as plain `http://` on an address like `192.168.178.20:8420`.
The app accepts plain `http://` only for addresses that can't be on the open internet:

- home network addresses (`192.168.x.x`, `10.x.x.x`, `172.16–31.x.x`), names without a dot
  (`nas`, `homeserver`) and names ending in `.local`, `.lan`, `.home.arpa`, `.fritz.box`
- Tailscale (`100.64–127.x.x` and `*.ts.net`) and other private tunnels

Every other address needs `https://`, so nothing crosses the internet unencrypted. On the go,
use Tailscale or WireGuard rather than forwarding port 8420 on your router. With the
fingerprint login, no password is sent over the network at all after the first login.

## Fingerprint login

After the first login with your password, the app offers to use the fingerprint from then on.

- The app makes a key pair inside the phone's secure hardware. The private key can't be read
  out, not even by the app, and every single use needs your fingerprint or the phone's PIN.
- The server only stores the public key. To log in, it sends a one-time challenge, the phone
  signs it after the fingerprint, and the server checks the signature. A challenge works once,
  for two minutes.
- When someone adds a new fingerprint to the phone, the key stops working, and the app asks for
  the password once more.
- The app locks again after a while in the background (right away, 1, 5 or 15 minutes; Settings
  in the app).
- Every phone shows up in the web interface under **Settings → Security → Phones with fingerprint** with its
  last use. Removing it there logs it out at once. It also works when password login is turned
  off on the server.

## Build it yourself

You need the Android SDK (Android Studio brings it) and JDK 17 or newer.

```bash
cd android
./gradlew testDebugUnitTest      # unit tests
./gradlew assembleDebug          # app/build/outputs/apk/debug/app-debug.apk
```

A debug build installs next to the released app (it has its own id, `….groschen.debug`).

## Releases on GitHub

Every pull request that changes the app is built, unit-tested and its libraries are checked for
known vulnerabilities ([`.github/workflows/android.yml`](../.github/workflows/android.yml)).
Each change on `main` is then published as a signed APK under Releases.

Android only installs an update when it is signed with the same key as the installed app. That
key lives in two repository secrets and never in the code:

1. Make the key once, anywhere Docker runs (the command asks for a password twice; choose a
   long one and keep it in your password manager):

   ```bash
   docker run --rm -it -v "$PWD:/out" eclipse-temurin:21-jre \
     keytool -genkeypair -keystore /out/groschen-release.p12 -storetype PKCS12 \
     -alias groschen -keyalg RSA -keysize 4096 -validity 10000 -dname "CN=Groschen"
   base64 -w0 groschen-release.p12 > groschen-release.txt
   ```

2. On GitHub, open the repository's **Settings → Secrets and variables → Actions → New
   repository secret** and add:
   - `ANDROID_KEYSTORE`: the whole content of `groschen-release.txt`
   - `ANDROID_KEYSTORE_PASSWORD`: the password from step 1

3. Under **Actions → Android app → Run workflow**, start a run on `main`. A few minutes later
   the first APK is under Releases.

4. Keep `groschen-release.p12` safe (for example next to the password) and delete
   `groschen-release.txt`. Without the key, a new APK can't be installed over the old one.

Without the secrets, the app is still built and tested; the run then says the key is missing.
