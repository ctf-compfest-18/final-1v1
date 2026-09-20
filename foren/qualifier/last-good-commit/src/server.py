#!/usr/bin/env python3
import hashlib
import os
import socket
import socketserver
import threading

FLAG = "COMPFEST18{d71529044cf35667edab9718f4e66256a9293bbed9724a3a7a43844c69eb353c}"
import json
from pathlib import Path

PROOF = json.loads(Path(__file__).with_name("answer.json").read_text())["proof"]


def reply(command: str) -> str:
    command = command.strip()
    if command == "help":
        return "commands: help, submit <sha256>\nUse the evidence ZIP. Hash UTF-8 bytes without a final newline:\nshipment=<id>|sku=<sku>|quantity=<integer>|approved=<0 or 1>|receipt=<lowercase hex of the recovered receipt bytes>\n"
    if command.startswith("submit "):
        return FLAG + "\n" if command[7:] == PROOF else "proof rejected\n"
    return "unknown command\n"


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        self.connection.settimeout(10)
        try:
            self.wfile.write(b"last-good-commit forensic console\n> ")
            while True:
                line = self.rfile.readline(1025)
                if not line:
                    return
                if len(line) > 1024 or not line.endswith(b"\n"):
                    self.wfile.write(b"invalid command line\n")
                    return
                self.wfile.write(reply(line.decode("utf-8", errors="replace").strip()).encode() + b"> ")
        except OSError:
            return


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True
    slots = threading.BoundedSemaphore(32)

    def process_request(self, request, client_address):
        if not self.slots.acquire(blocking=False):
            self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except Exception:
            self.slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self.slots.release()


if __name__ == "__main__":
    with Server(("0.0.0.0", int(os.getenv("PORT", "7749"))), Handler) as server:
        server.serve_forever()
