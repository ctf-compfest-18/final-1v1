import hashlib
import os

import jinja2
from flask import Flask, request

FLAG_PATH = os.environ.get("FLAG_PATH", "/flag.txt")
MAX_PAYLOAD = 1000

app = Flask(__name__)

env = jinja2.Environment(autoescape=True)
env.globals.clear()

_RECORDS = {
    "flag": "flag{belum_disetal}",
}

if os.path.exists(FLAG_PATH):
    with open(FLAG_PATH) as fh:
        _RECORDS["flag"] = fh.read().strip()


def build_cert():
    digest = hashlib.sha256(_RECORDS["flag"].encode()).hexdigest()[:12]
    return "CERT-%s" % digest


def lock(payload):
    payload = payload.replace("(", "").replace(")", "")
    return "{% set config=None%}{% set self=None%}" + payload


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ad Astra — Certificate Generator</title>
<style>
  body { font-family: system-ui, sans-serif; max-width: 760px; margin: 40px auto; padding: 0 16px; color: #1c1c1c; }
  textarea { width: 100%; box-sizing: border-box; font-family: monospace; font-size: 14px; padding: 8px; }
  button { padding: 8px 16px; font-size: 15px; cursor: pointer; }
  .cert { border: 1px dashed #999; border-radius: 8px; padding: 16px; margin-top: 24px; }
  .cert h2 { margin-top: 0; }
  .err { color: #a00; }
  .note { color: #555; font-size: 14px; }
  pre { background: #f4f4f4; padding: 12px; overflow-x: auto; font-size: 13px; }
</style>
</head>
<body>
<h1>Ad Astra Certificate Generator</h1>
<p>Masukkan nama, sistem akan merender sertifikat untuk Anda.</p>
<form method="post">
  <textarea name="name" rows="4" placeholder="nama Anda">{{ last }}</textarea>
  <p><button type="submit">Generate certificate</button></p>
</form>
{result}
<details>
<summary>Lihat kode filter</summary>
<pre>{% raw %}def lock(payload):
    payload = payload.replace("(", "").replace(")", "")
    return "{% set config=None%}{% set self=None%}" + payload

# render
env.from_string(page).render(helper=build_cert, cert=build_cert()){% endraw %}</pre>
</details>
<p class="note">Semua output di-escape otomatis oleh template engine.</p>
</body>
</html>
"""

CERT = """<div class="cert">
  <h2>Certificate</h2>
  <p>name: {payload}</p>
  <p>cert: {{ cert }}</p>
</div>"""


def page(result_html, last_value=""):
    return env.from_string(PAGE.replace("{result}", result_html)).render(
        helper=build_cert,
        cert=build_cert(),
        last=last_value,
    )


@app.get("/health")
def health():
    return "ok"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return page("", "")

    payload = request.form.get("name", "")
    if len(payload) > MAX_PAYLOAD:
        return page("<div class='cert'><p class='err'>payload too long</p></div>", ""), 413

    result = CERT.replace("{payload}", lock(payload))
    try:
        return page(result, payload)
    except jinja2.TemplateError:
        return page("<div class='cert'><p class='err'>Template error.</p></div>", payload), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4007, debug=False)
