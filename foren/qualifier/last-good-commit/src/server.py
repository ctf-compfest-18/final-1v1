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

BANNER = (
    "\x1b[1;36m"
    + r"""
 _      _   ___ _____    ___  ___   ___  ___
| |    /_\ / __|_   _|  / __|/ _ \ / _ \|   \
| |__ / _ \\__ \ | |   | (_ | (_) | (_) | |) |
|____/_/ \_\___/ |_|    \___|\___/ \___/|___/
"""
    + "\x1b[0m\x1b[36m"
    + r"""
  ___ ___  __  __ __  __ ___ _____
 / __/ _ \|  \/  |  \/  |_ _|_   _|
| (_| (_) | |\/| | |\/| || |  | |
 \___\___/|_|  |_|_|  |_|___| |_|
"""
    + "\x1b[0m\x1b[32m"
    + r"""
        .-~~~-.
       / .---. \
      | | WAL | |    the database and its write-ahead log
       \ '---' /
        '-----'
"""
    + "\x1b[0m"
    + "\x1b[33m  [ committed: ? ]  [ overwritten: ? ]  [ warehouse: SHIP-8821 ]\x1b[0m\n"
    + "\x1b[90m  Type 'help' for the proof encoding.\x1b[0m\n\n"
)

HELP = (
    "\x1b[1;37mcommands:\x1b[0m help, submit <sha256>\n"
    "  \x1b[32mhelp\x1b[0m            show this menu\n"
    "  \x1b[32msubmit\x1b[0m SHA256    submit the recovered record proof\n"
    "\x1b[90mUse the evidence ZIP. Reconstruct the committed state that agrees with the warehouse.\x1b[0m\n"
    "\x1b[90mshipment=<id>|sku=<sku>|quantity=<integer>|approved=<0 or 1>|receipt=<lowercase hex of the recovered receipt bytes>\x1b[0m\n"
    "\x1b[90mHash these UTF-8 bytes without a final newline.\x1b[0m\n"
)


def reply(command: str) -> str:
    command = command.strip()
    if command == "help":
        return HELP
    if command.startswith("submit "):
        if command[7:] == PROOF:
            return f"\x1b[1;32m{FLAG}\x1b[0m\n\x1b[32m[ record validated ]\x1b[0m\n"
        return "\x1b[1;31mproof rejected\x1b[0m\n"
    return "\x1b[31munknown command\x1b[0m\n"


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        self.connection.settimeout(10)
        try:
            self.wfile.write(BANNER.encode() + b"> ")
            while True:
                line = self.rfile.readline(1025)
                if not line:
                    return
                if len(line) > 1024 or not line.endswith(b"\n"):
                    self.wfile.write(b"\x1b[31minvalid command line\x1b[0m\n")
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
