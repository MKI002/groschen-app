<p align="center">
  <img src="frontend/public/icon.png" width="88" alt="Groschen logo">
</p>

<h1 align="center">Groschen</h1>

<p align="center">
  <b>A private, self-hosted finance dashboard for German bank accounts.</b><br>
  Runs as one Docker container on your own server, sorts your money by itself with a small
  built-in AI model, and talks to nobody on the internet except your bank.
</p>

<p align="center">
  <a href="https://mki002.github.io/groschen-app/"><b>▶ Try the live demo</b></a><br>
  <sub>The real app in your browser, with made-up data. Nothing to install.</sub>
</p>

<p align="center">
  <a href="#install">Install</a> ·
  <a href="#try-it-with-demo-data">Try the demo</a> ·
  <a href="#whats-inside">Features</a> ·
  <a href="#privacy-and-network">Privacy</a> ·
  <a href="#development">Development</a>
</p>

![Overview: money free until payday, hints and where the money went](docs/screenshots/overview.png)

<sub>All screenshots show the built-in demo data. The person, employer and amounts are invented.</sub>

## Highlights

- **Your data stays home.** SQLite in your appdata folder, no cloud account, no analytics, no
  web fonts. A network guard inside the app blocks every host except your bank.
- **Sorts itself.** About 10,000 known shops and services from Germany, the rest of Europe and the US, plus a small multilingual model on the CPU.
  It learns from every correction, spots own transfers, refunds and savings plans on its own.
- **Knows your month.** What is free until payday, which fixed costs are still to come, and which
  subscriptions got pricier, stopped or came back.
- **Depot without the noise.** Real gain and loss without counting the money you paid in,
  zoomable charts, a projection with 800 simulated futures.
- **Everything in the browser.** Setup wizard, bank connection, backups, passkeys: no config files.
  English and German.

## Screenshots

| | |
| --- | --- |
| ![Transactions](docs/screenshots/transactions.png) | ![Spending](docs/screenshots/spending.png) |
| **Transactions** with search, filters and a one-click review queue | **Spending** by group and category, and a year in days |
| ![Fixed costs](docs/screenshots/recurring.png) | ![Investments](docs/screenshots/investments.png) |
| **Fixed costs** that notice price changes, cancellations and comebacks | **Depot** value with monthly gain and loss, pay-ins left out |

<p align="center">
  <img src="docs/screenshots/phone.png" width="300" alt="Groschen on a phone">
</p>

## Contents

- [What's inside](#whats-inside)
- [Privacy and network](#privacy-and-network)
- [Banks: what to know](#banks-what-to-know)
- [Install](#install)
- [Updates](#updates)
- [Try it with demo data](#try-it-with-demo-data)
- [Development](#development)

## What's inside

- **Setup wizard** on first start: your login, the bank connection, CSV import of older history,
  categorizer and schedule, first sync.
- **Overview**: what is free to spend until payday, with every charge still to come on a line to
  payday, a few hints worth a look, and where the money went (as a flow, a timeline or by month).
- **Transactions** (search, filters and a review queue where one click accepts a guess),
  **spending** by group and category with every day of the year, **fixed costs** (as a list, a
  calendar or an orbit), **net worth** and your own **groups** (a car, a flat you rent out).
  In English or German.
- **Fixed costs that keep themselves up to date**: Groschen notices when a subscription gets more
  expensive or cheaper, stops, starts, or comes back after a pause, and says so on the Overview.
- **Savings plans found on their own**: ETF savings plans, Kleingeld Plus and standing orders to
  the savings account show up under Net worth with every payment, no setup needed.
- **Less sorting by hand**: money moved to your own name (the Extra-Konto, a broker, an account at
  another bank) counts as moved, saved or invested, not spent; a refund cancels out the purchase it
  belongs to; payees get readable names ("VISA MCDONALDS 01234" becomes McDonald's, PayPal shows
  the shop behind it); a day's Kleingeld Plus round-ups are one line. Hints stay quiet about
  everyday shopping, and new merchant knowledge sorts existing bookings again after an update
  (never the ones you sorted).
- **Depot**: value against money paid in, with what each month (week, day) earned or lost in euros
  without counting the money paid in. Everything on the page follows the chosen period, and the
  charts zoom: drag across them, Ctrl + mouse wheel, or two fingers on a phone; the browser keeps
  the view. Behind tabs the rest: money-weighted and time-weighted return, volatility, Sharpe ratio
  against your Extra-Konto rate, drawdown, a monthly-returns heatmap, a projection with 800
  simulated futures, and a page for every ETF. Also the tax-free allowance (Sparerpauschbetrag).
- **One dark design**, calm and formal with small animations. The Animations setting (full, calm,
  off) and the system's reduced-motion switch tone it down.
- **Categorizer**: your own choices and rules first, then about 10,000 known shops and services (Germany, Europe, US), then a
  small multilingual sentence model (MiniLM, int8, about 120 MB) on the CPU. It learns from every
  correction. Uncertain guesses go to "Needs review". It uses about 300 MB of memory for a few
  seconds after a sync and then unloads.
- **Nightly backups** into the data folder and a CSV export.

## Privacy and network

- The only outgoing connections are to the FinTS servers of the banks you connected (for ING
  `fints.ing.de`), plus `www.justetf.com` once you switch on Online ETF prices. A guard inside the app refuses every other address, and
  **Settings → Export & privacy** shows a log of every connection it made.
- No update checks, analytics, web fonts or map tiles. Fonts, icons and charts are built in.
- The bank PIN is stored encrypted. The key is `secret.key` in the data folder and is never
  included in backups. The app password is stored as an Argon2 hash.
- Nothing secret lives in this repository. The image is built by GitHub from the code alone.
- Don't forward port 8420 on your router. For access from outside, use Tailscale or WireGuard.

## Banks: what to know

Groschen talks to German banks over **FinTS** (also called HBCI), read-only, and imports their
**CSV exports** for older history or for banks without FinTS. Pick your bank in the wizard or under
**Settings → Bank & import** by name, Bankleitzahl or IBAN.

| Bank | FinTS | Approve in | CSV import |
| --- | --- | --- | --- |
| ING | built in | ING App (rarely asked) | Umsatzanzeige |
| Sparkassen | Bankleitzahl plus the FinTS address, from the institute list or the Sparkasse's website | S-pushTAN | CSV-CAMT, CSV-MT940 |
| Volksbanken, Raiffeisenbanken, Sparda-, PSD-, GLS Bank | built in (Atruvia), by Bankleitzahl | VR SecureGo plus | yes |
| Deutsche Bank, norisbank | built in, by Bankleitzahl | photoTAN, BestSign | yes, with Soll and Haben columns |
| Postbank | built in, by Bankleitzahl | BestSign | yes |
| Commerzbank | built in, by Bankleitzahl | photoTAN | yes |
| comdirect | built in | photoTAN push | yes |
| DKB | built in | DKB App | old and new layout |
| Consorsbank | built in | SecurePlus | yes |
| HypoVereinsbank | built in | HVB app | generic |
| N26, Trade Republic, Revolut, C24 | no FinTS at these banks | | CSV only |

Only ING has been used with a real account so far. The others follow each bank's published FinTS
access and CSV layout; if one refuses, Settings shows what the bank said. Banks not in the table
work too: type the Bankleitzahl and the FinTS address from the bank's website.

- **FinTS product ID.** Every FinTS program needs a free product ID from the Deutsche
  Kreditwirtschaft. Search for "FinTS Produktregistrierung" (the form is on hbci-zka.de), choose
  private use and give "Groschen" as the product name. The ID arrives by email. Until then you can
  import CSV files. One ID works for every bank.
- **Institute list.** With the registration you can get the FinTS institute list, a CSV with every
  bank's FinTS address. Import it under Settings → Bank & import, and a Sparkasse is found by its
  Bankleitzahl alone. It stays on your server.
- **Approvals and TANs.** Groschen picks the bank's app approval (pushTAN, SecureGo plus, BestSign,
  photoTAN push) when the bank offers one, and waits up to three minutes for you to confirm. If a
  bank wants a typed TAN (chipTAN, smsTAN, photoTAN picture), Groschen asks for it on the page
  during a sync you start; a sync at night can't, and says so.
- **Login every 90 days.** Banks ask you to log in or confirm a request at least once every 90
  days (PSD2), otherwise FinTS access pauses. Groschen reminds you ahead of time. A sync you approve
  in the app counts by itself; after a plain login press "I logged in to my bank" in Settings.
- **History.** FinTS returns about 90 days. For older transactions, export CSV files in your online
  banking and import them in the wizard or in Settings. Duplicates are skipped. The file finds its
  account by itself (by the IBAN in the file or its name) and takes the balance from the file.
- **Depot.** Holdings and prices come over FinTS where the bank offers it. Banks only send today's
  prices, so Groschen records them at every sync. For older price history, import a file with one
  line per day: `date;ISIN;price`.

## Install

Groschen is one Docker image, `ghcr.io/mki002/groschen-app:latest`, for 64-bit Intel/AMD
servers. It needs a port and a data folder; everything else is set up in the web page.
Any Docker host works: a Linux box, a Synology or QNAP NAS, Unraid, Portainer, TrueNAS.

### Docker Compose

Save [`docker-compose.yml`](docker-compose.yml) in a new folder and run:

```bash
docker compose up -d
```

### docker run

```bash
docker run -d --name groschen --restart unless-stopped \
  -p 8420:8420 -v /path/to/groschen-data:/data \
  -e TZ=Europe/Berlin -e PUID=1000 -e PGID=1000 \
  --cap-drop=ALL --cap-add=CHOWN --cap-add=SETUID --cap-add=SETGID \
  --cap-add=DAC_READ_SEARCH --cap-add=FOWNER \
  --security-opt=no-new-privileges:true --memory=1g \
  ghcr.io/mki002/groschen-app:latest
```

Then open `http://your-server:8420` and the setup wizard takes it from there.

| Setting | What it is | Default |
| --- | --- | --- |
| Port `8420` | The web page. Don't forward it on your router; use Tailscale or WireGuard from outside. | |
| Volume `/data` | Database, the key that protects your bank PIN, and nightly backups. Back this up. | |
| `TZ` | Time zone for the sync and backup schedule. | `Europe/Berlin` |
| `PUID` / `PGID` | The user and group the app runs as. Use the owner of your data folder (`id -u`, `id -g`). | `99` / `100` |

The container starts as root only long enough to take ownership of the data folder, then runs as
`PUID:PGID`. The capability flags drop every other privilege and cap memory at 1 GB.

<details>
<summary>Unraid</summary>

1. Copy [`unraid/groschen.xml`](unraid/groschen.xml) to
   `/boot/config/plugins/dockerMan/templates-user/my-Groschen.xml`, then **Docker → Add Container**
   and pick **Groschen** as the template. Or fill in the form by hand:

   | Field | Value |
   | --- | --- |
   | Repository | `ghcr.io/mki002/groschen-app:latest` |
   | Port | container `8420`, host `8420` |
   | Path | container `/data`, host `/mnt/user/appdata/groschen` |
   | Icon URL | `http://your-server:8420/icon.png` (your server's name or IP) |
   | Extra Parameters | `--cap-drop=ALL --cap-add=CHOWN --cap-add=SETUID --cap-add=SETGID --cap-add=DAC_READ_SEARCH --cap-add=FOWNER --security-opt=no-new-privileges:true --memory=1g --cpu-shares=256` |

2. The defaults `PUID=99` and `PGID=100` are Unraid's nobody:users, so nothing else to set.
3. The app serves its own logo for the Icon URL. If the Docker tab shows a question mark because
   the container wasn't running yet, click **Edit** on Groschen and **Apply** once more.

</details>

<details>
<summary>Build the image yourself</summary>

```bash
git clone https://github.com/MKI002/groschen-app.git && cd groschen-app
docker build -t groschen:local .
```

Then use `groschen:local` instead of the image name above.

</details>

## Updates

Every change to `main` is tested and built by GitHub Actions (see [`.github/workflows/build.yml`](.github/workflows/build.yml)).
The image only gets published if the tests pass and a self-test inside the finished image loads the
model, categorizes sample texts and confirms the network guard blocks the internet.

- Back up the data folder first.
- Pull the new image and recreate the container: `docker compose pull && docker compose up -d`,
  or **Check for updates** in Unraid, Portainer or similar. The database is upgraded on start.
- Every build is also tagged with its date and commit, for example `2026.09.27-1a2b3c4`. To roll
  back, use that tag instead of `latest`.
- The app never updates itself. Base images, Python packages and GitHub Actions are pinned to
  exact versions and hashes, and change only through a reviewed pull request.

## Try it with demo data

The quickest way is the **[live demo](https://mki002.github.io/groschen-app/)**: the real web app
running in your browser on recorded sample data. Clicks work, changes are not kept, and no server
or bank is involved.

To run the whole thing yourself, Groschen ships with a made-up person, two years of invented bookings and a small depot, so you can
look around without a bank account:

```bash
mkdir demo-data
docker run --rm -v "$PWD/demo-data:/data" ghcr.io/mki002/groschen-app:latest python -m groschen.demo
docker run --rm -p 8420:8420 -v "$PWD/demo-data:/data" ghcr.io/mki002/groschen-app:latest
```

Open http://localhost:8420, create a login, and skip the bank step.

## Development

```bash
# Backend (Python 3.12)
cd backend
python -m venv .venv && . .venv/bin/activate
pip install --require-hashes --only-binary=:all: --no-deps -r requirements.txt
pip install -r requirements-dev.txt
ruff check . && ruff format --check .
python -m pytest -q
GROSCHEN_DATA=./data python -m groschen.demo   # optional: fill with demo data
GROSCHEN_DATA=./data python -m groschen        # http://127.0.0.1:8420

# Web app (Node 22), with the backend running
cd frontend
npm ci
npm run dev                                      # http://127.0.0.1:5173
npm run build                                    # writes into backend/groschen/static
npm run build:demo                               # the web demo, into dist-demo
```

`requirements.txt` is generated from `requirements.in` (the command is at the top of that file).
`overrides.txt` keeps the Hugging Face download client out of the image, since the model is
already inside it. `model.lock.json` pins the model revision and file hashes, and the build
stops if a download doesn't match. To move to a newer model revision, empty the three values;
the next build prints the new ones as a note on the run.

### Layout

```
backend/groschen/
  bank/         bank list, FinTS client, CSV import for German banks, storing transactions, sync
  categorize/   rules, merchant list, model, learning
  analytics/    cash flow, net worth, portfolio statistics, subscriptions, savings plans
  api/          HTTP endpoints
  netguard.py   allowlist for outgoing connections, and the connection log
  selftest.py   checks run inside the finished image before it's published
frontend/src/   React web app (no router or chart libraries)
unraid/         Unraid container template
docker-compose.yml  example for Docker Compose
Dockerfile      web app, packages, model and app in one image
```
