#!/usr/bin/env python3
"""Local token validator."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import time
from threading import Lock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "participant"))
from app.crypto_core import MODULES, read_json, recover_final, validate_token

class ValidatorServer(ThreadingHTTPServer):
    daemon_threads = True
    def __init__(self, address, challenge):
        self.challenge = Path(challenge)
        self.manifest = read_json(self.challenge / "manifest.json")
        self.lock = Lock()
        self.buckets = {}
        super().__init__(address, Handler)

    def permitted(self, ip):
        now = time.monotonic()
        with self.lock:
            hits = [t for t in self.buckets.get(ip, []) if now-t < 60]
            allowed = len(hits) < 120
            if allowed:
                hits.append(now)
            self.buckets[ip] = hits
            return allowed

class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(5)

    def log_message(self, format, *args):
        # Never log submitted tokens, URLs or request bodies.
        pass

    def reply(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self.reply(200, {"status": "ok", "instance_id": self.server.manifest["instance_id"]})
        else:
            self.reply(404, {"error": "not found"})

    def do_POST(self):
        if self.path not in ("/api/validate", "/api/final"):
            return self.reply(404, {"error": "not found"})
        if not self.server.permitted(self.client_address[0]):
            return self.reply(429, {"error": "rate limit"})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 4096:
                return self.reply(413, {"error": "body size"})
            obj = json.loads(self.rfile.read(size))
            if not isinstance(obj, dict):
                raise ValueError("object required")
            if obj.get("instance_id") != self.server.manifest["instance_id"]:
                return self.reply(409, {"error": "instance mismatch"})
            if self.path == "/api/validate":
                module, token = obj.get("module"), obj.get("token")
                if not isinstance(module, str) or module not in MODULES or not isinstance(token,str):
                    raise ValueError("module/token required")
                return self.reply(200, {"valid": validate_token(self.server.manifest, module, token)})
            tokens = obj.get("tokens")
            if not isinstance(tokens,dict):
                raise ValueError("tokens required")
            _, flag = recover_final(self.server.challenge, tokens)
            return self.reply(200, {"flag": flag})
        except (ValueError, TypeError, KeyError, UnicodeError):
            return self.reply(400, {"error": "invalid request or recovery tokens"})

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--challenge", type=Path, default=ROOT / "participant/challenge")
    args = parser.parse_args()
    server = ValidatorServer(("127.0.0.1", args.port), args.challenge)
    print(f"Local validator: http://127.0.0.1:{server.server_port} (Ctrl+C to stop)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
