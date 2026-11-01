# Groschen: one image with the web app, the Python backend and the categorizer model.
# Base images are pinned by version and digest; Dependabot proposes updates.

# --- 1. Web app ------------------------------------------------------------------------
FROM node:22.23.3-trixie-slim@sha256:28d03803f09ba76560e273af33beb7eda4ed68fa0698bc9bd15e9a6e35693923 AS web
WORKDIR /src/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --ignore-scripts --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

# --- 2. Python packages, installed only from wheels with checked hashes -----------------
FROM python:3.12.15-slim-trixie@sha256:a0f57064cbdcd6285fa45f51237ab0b35ea8ebaed06a1f5973e89e19dfb86704 AS deps
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
COPY backend/requirements.txt /tmp/requirements.txt
# pip is removed afterwards: nothing installs packages inside the running container.
RUN python -m venv /opt/venv \
 && /opt/venv/bin/pip install --require-hashes --only-binary=:all: --no-deps -r /tmp/requirements.txt \
 && /opt/venv/bin/python -m pip uninstall -y pip \
 && rm -rf /opt/venv/bin/pip* \
 && chmod -R a-w /opt/venv

# --- 3. App code, compiled ahead so nothing is written next to it at runtime ----------------
FROM python:3.12.15-slim-trixie@sha256:a0f57064cbdcd6285fa45f51237ab0b35ea8ebaed06a1f5973e89e19dfb86704 AS app
COPY backend/groschen /app/groschen
COPY --from=web /src/backend/groschen/static /app/groschen/static
RUN python -m compileall -q /app/groschen \
 && chmod -R a-w /app

# --- 4. Categorizer model, downloaded here once so the app never has to ----------------
FROM python:3.12.15-slim-trixie@sha256:a0f57064cbdcd6285fa45f51237ab0b35ea8ebaed06a1f5973e89e19dfb86704 AS model
COPY backend/model.lock.json /src/model.lock.json
COPY backend/scripts/fetch_model.py /src/scripts/fetch_model.py
RUN python /src/scripts/fetch_model.py /model

# --- 5. The image that runs on your server ------------------------------------------------
FROM python:3.12.15-slim-trixie@sha256:a0f57064cbdcd6285fa45f51237ab0b35ea8ebaed06a1f5973e89e19dfb86704 AS runtime

# Debian security fixes (OpenSSL and friends) often land before a new base image is
# published. Installing them here means every build ships them; the build workflow never
# caches this stage, so a rebuild always picks up the latest ones.
RUN apt-get update \
 && apt-get upgrade -y --no-install-recommends \
 && rm -rf /var/lib/apt/lists/*

LABEL org.opencontainers.image.title="Groschen" \
      org.opencontainers.image.description="Self-hosted finance dashboard for ING Germany" \
      org.opencontainers.image.source="https://github.com/MKI002/groschen-app"

ENV PATH=/opt/venv/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GROSCHEN_DATA=/data \
    GROSCHEN_PORT=8420 \
    GROSCHEN_MODEL=/app/model \
    TZ=Europe/Berlin \
    PUID=99 \
    PGID=100

COPY --from=deps /opt/venv /opt/venv
COPY --from=model /model /app/model
COPY --from=app /app/groschen /app/groschen

WORKDIR /app
VOLUME /data
EXPOSE 8420

HEALTHCHECK --interval=60s --timeout=5s --start-period=30s --retries=3 \
  CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:%s/api/health' % os.environ.get('GROSCHEN_PORT', '8420'), timeout=4)"]

# Starts as root only to take ownership of /data, then switches to PUID/PGID for good.
CMD ["python", "-m", "groschen"]
