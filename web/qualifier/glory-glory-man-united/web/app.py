import json
import os
import re
import threading
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

from flask import Flask, abort, make_response, redirect, request

BASE_DIR = Path(__file__).resolve().parent
INDEX_HTML = (BASE_DIR / "templates" / "index.html").read_text(encoding="utf-8")
PREVIEW_HTML = (BASE_DIR / "templates" / "preview.html").read_text(encoding="utf-8")

FLAG = os.environ.get("FLAG", "COMPFEST18{gl0ry_gl0ry_dummy_flag}")
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "dev-admin-token")
BOT_URL = os.environ.get("BOT_URL", "http://bot:3000").rstrip("/")
REPORT_COOLDOWN = int(os.environ.get("REPORT_COOLDOWN_SECONDS", "60"))

CSP = (
    "default-src 'none'; "
    "img-src http: https: data:; "
    "font-src http: https:; "
    "style-src 'self' 'unsafe-inline' http: https:; "
    "script-src 'none'; "
    "connect-src 'none'; "
    "base-uri 'none'; "
    "frame-ancestors 'none'; "
    "form-action 'self'"
)

app = Flask(__name__)
lock = threading.Lock()
themes = {}       
last_report = {}  


def esc(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def sanitize_theme(css):
    return re.sub(r"</style", "", css, flags=re.IGNORECASE)


@app.after_request
def set_headers(resp):
    resp.headers["Content-Security-Policy"] = CSP
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    return resp


@app.get("/")
def index():
    msg = request.args.get("msg", "")
    return make_response(INDEX_HTML.replace("__MSG__", esc(msg)))


@app.post("/create")
def create():
    css = sanitize_theme(request.form.get("css", ""))
    tid = uuid.uuid4().hex
    with lock:
        themes[tid] = css
    return redirect(f"/preview/{tid}")


@app.get("/preview/<tid>")
def preview(tid):
    with lock:
        css = themes.get(tid)
    if css is None:
        abort(404)
    is_admin = request.cookies.get("admin-token", "") == ADMIN_TOKEN
    flag_value = FLAG if is_admin else "red_herring_login_first"
    html = (PREVIEW_HTML
            .replace("__THEME_ID_SHORT__", tid[:8])
            .replace("__THEME_ID__", tid)
            .replace("__FLAG__", esc(flag_value))
            .replace("__USER_CSS__", css))
    return make_response(html)


@app.post("/report")
def report():
    tid = (request.form.get("theme_id") or "").strip()
    if not re.fullmatch(r"[0-9a-f]{32}", tid):
        return redirect("/?msg=invalid+theme+id")
    with lock:
        exists = tid in themes
    if not exists:
        return redirect("/?msg=theme+not+found")
    ip = (request.headers.get("x-forwarded-for", request.remote_addr or "?")).split(",")[0].strip()
    now = time.time()
    with lock:
        last = last_report.get(ip, 0.0)
        if now - last < REPORT_COOLDOWN:
            wait = int(REPORT_COOLDOWN - (now - last))
            return redirect(f"/?msg=cooldown+try+again+in+{wait}s")
        last_report[ip] = now
    body = json.dumps({"path": f"/preview/{tid}"}).encode()
    req = urllib.request.Request(
        BOT_URL + "/visit",
        data=body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=5):
            pass
    except (urllib.error.URLError, OSError):
        with lock:
            last_report.pop(ip, None)
        return redirect("/?msg=admin+bot+offline")
    return redirect(f"/?msg=reported+{tid[:8]}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, threaded=True)
