#!/usr/bin/env python3
"""Test the recovery console and local validator."""
import argparse
import json
import os
from pathlib import Path
import sys
from threading import Thread
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "participant"))
sys.path.insert(0, str(ROOT / "probset/server"))
from app.crypto_core import read_json
from validator import ValidatorServer

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--screenshot", type=Path, help="Unsolved GUI PNG, contains no recovered secrets")
    parser.add_argument("--skip-gui", action="store_true")
    args = parser.parse_args()
    challenge = ROOT / "participant/challenge"
    secret = read_json(ROOT / "probset/secrets/instance.json")
    manifest = read_json(challenge / "manifest.json")
    server = ValidatorServer(("127.0.0.1",0),challenge)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}"
    def post(path, data):
        req = Request(url+path, data=json.dumps(data).encode(), headers={"Content-Type":"application/json"})
        try:
            with urlopen(req, timeout=5) as response:
                return response.status, json.load(response)
        except HTTPError as exc:
            return exc.code, json.load(exc)
    try:
        with urlopen(url+"/health", timeout=5) as response:
            assert json.load(response)["instance_id"] == manifest["instance_id"]
        base = {"instance_id": manifest["instance_id"]}
        for m, token in secret["tokens"].items():
            assert post("/api/validate",dict(base,module=m,token=token)) == (200,{"valid":True})
            assert post("/api/validate",dict(base,module=m,token="00"*32)) == (200,{"valid":False})
        assert post("/api/final",dict(base,tokens=secret["tokens"])) == (200,{"flag":secret["flag"]})
        assert post("/api/final",dict(base,tokens={}))[0] == 400
        assert post("/api/validate",dict(base,module=[],token="00"*32))[0] == 400
        assert post("/api/final",{"instance_id":"wrong", "tokens":secret["tokens"]})[0] == 409
        assert post("/api/final",[])[0] == 400
        with server.lock:
            server.buckets["127.0.0.1"] = [__import__("time").monotonic()] * 120
        assert post("/api/final",dict(base,tokens=secret["tokens"]))[0] == 429
        print("HTTP: health, valid/invalid tokens, final, malformed input, instance mismatch, rate limit PASS")
    finally:
        server.shutdown(); server.server_close(); thread.join()
    if not args.skip_gui:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PySide6.QtWidgets import QApplication
        from PySide6.QtTest import QTest
        from PySide6.QtCore import Qt
        from app.gui import RecoveryWindow
        app = QApplication([])
        window = RecoveryWindow(challenge)
        window.show(); app.processEvents()
        assert window.progress.value() == 0 and not window.unlock_button.isEnabled()
        if args.screenshot:
            assert window.grab().save(str(args.screenshot))
        window.entries["module1"].setText("00"*32)
        QTest.mouseClick(window.submit_buttons["module1"], Qt.MouseButton.LeftButton)
        assert window.progress.value() == 0
        assert "REJECTED" in window.statuses["module1"].text()
        QTest.mouseClick(window.start_button, Qt.MouseButton.LeftButton)
        assert window.started_at is not None
        for i, (m, token) in enumerate(secret["tokens"].items(),1):
            window.entries[m].setText(token.upper())
            QTest.mouseClick(window.submit_buttons[m], Qt.MouseButton.LeftButton)
            assert window.progress.value() == i
            assert not window.entries[m].isEnabled()
            assert window.unlock_button.isEnabled() == (i == 3)
        QTest.mouseClick(window.unlock_button, Qt.MouseButton.LeftButton)
        assert secret["flag"] in window.output.toPlainText()
        assert secret["master_key"] in window.output.toPlainText()
        assert not window.unlock_button.isEnabled()
        window.started_at -= 1300
        window.tick()
        assert window.clock.text() == "00:00"
        window.close()
        print("Qt GUI: 0/3, wrong token, 1/3..3/3, unlock, final flag, timer expiry PASS")

if __name__ == "__main__":
    main()
