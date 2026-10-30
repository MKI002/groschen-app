"""The web app: JSON API under /api and the built web interface for everything else."""

import re

from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import FileResponse, JSONResponse, Response

from . import config, i18n
from .api import auth, bank, data, manage

UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
CSRF_HEADER = "x-groschen"

SECURITY_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; "
        "font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; "
        "frame-ancestors 'none'"
    ),
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-origin",
}


def build_id() -> str:
    """The web interface's own script name, which changes with every build.

    A tab that stayed open through a container update still runs the old interface; it compares
    this with its own script to notice and offer a reload.
    """
    try:
        html = (config.STATIC_DIR / "index.html").read_text(encoding="utf-8")
    except OSError:
        return ""
    match = re.search(r'<script[^>]*\bsrc="(/assets/[^"]+\.js)"', html)
    return match.group(1) if match else ""


def create_app() -> FastAPI:
    app = FastAPI(title="Groschen", version=config.VERSION, docs_url=None, redoc_url=None, openapi_url=None)

    @app.exception_handler(HTTPException)
    async def translated_errors(request: Request, exc: HTTPException):
        if isinstance(exc.detail, str):
            exc = HTTPException(status_code=exc.status_code, detail=i18n.tr(exc.detail), headers=exc.headers)
        return await http_exception_handler(request, exc)

    @app.middleware("http")
    async def language(request: Request, call_next):
        # Messages follow the language the web page shows. Downloads opened as links
        # can't send headers, so they pass it as ?lang= instead.
        token = i18n.use(i18n.pick(request.headers.get("x-groschen-lang") or request.query_params.get("lang")))
        try:
            return await call_next(request)
        finally:
            i18n.reset(token)

    @app.middleware("http")
    async def guard(request: Request, call_next):
        # Other apps on the same server count as the "same site" for cookies, so a
        # SameSite cookie alone doesn't stop them from posting to Groschen. Every change
        # must carry a header that a plain cross-site form or image request can't set.
        if request.method in UNSAFE_METHODS and request.url.path.startswith("/api/"):
            if request.headers.get(CSRF_HEADER) != "1":
                return JSONResponse({"detail": i18n.t("Missing request header.")}, status_code=403)
        response = await call_next(request)
        for name, value in SECURITY_HEADERS.items():
            response.headers.setdefault(name, value)
        if request.url.path.startswith("/api/"):
            response.headers.setdefault("Cache-Control", "no-store")
        return response

    build = build_id()

    @app.get("/api/health")
    def health():
        return {"ok": True, "version": config.VERSION, "build": build}

    for module in (auth, bank, data, manage):
        app.include_router(module.router, prefix="/api")

    @app.api_route("/api/{rest:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], include_in_schema=False)
    def api_not_found(rest: str):
        return JSONResponse({"detail": i18n.t("Not found.")}, status_code=404)

    static_root = config.STATIC_DIR.resolve()

    @app.get("/{path:path}", include_in_schema=False)
    def web(path: str):
        index = static_root / "index.html"
        if path:
            target = (static_root / path).resolve()
            if target.is_relative_to(static_root) and target.is_file():
                headers = {"Cache-Control": "public, max-age=31536000, immutable"} if path.startswith("assets/") else {}
                if path == "icon.png":
                    # The logo for Docker dashboards such as Unraid's, which show a preview from their own
                    # address, which is another origin, so this one public file may be embedded.
                    headers["Cross-Origin-Resource-Policy"] = "cross-origin"
                return FileResponse(target, headers=headers)
        if index.is_file():
            return FileResponse(index, headers={"Cache-Control": "no-cache"})
        return Response(
            "The web interface isn't built. Run the frontend build first.", status_code=503, media_type="text/plain"
        )

    return app


app = create_app()
