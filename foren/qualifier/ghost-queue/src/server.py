#!/usr/bin/env python3
import hashlib
import os
import socket
import socketserver
import threading

FLAG = "COMPFEST18{8074f0dba10bfa1a26934d0eb00bba4b162471c33e262b8b708eb2d8114af7d9}"
DOC = b"BG-PRINT-2026\njob=Q-042\noperator=archive-bot\nstatus=processed\n"
import tempfile
import secrets

DOC += b"receipt=" + secrets.token_hex(24).encode() + b"\n"
DOCUMENT = tempfile.TemporaryFile()
DOCUMENT.write(DOC)
DOCUMENT.flush()
FD = DOCUMENT.fileno()
SPOOL = secrets.token_hex(12)
PROOF = hashlib.sha256(DOC).hexdigest()

BANNER = (
    "\x1b[1;35m"
    + r"""
   ____ _   _  ___  ____ _____    ___  _   _ _____ _   _ _____
  / ___| | | |/ _ \/ ___|_   _|  / _ \| | | | ____| | | | ____|
 | |  _| |_| | | | \___ \ | |   | | | | | | |  _| | | | |  _|
 | |_| |  _  | |_| |___) || |   | |_| | |_| | |___| |_| | |___|
  \____|_| |_|\___/|____/ |_|    \__\_\\___/|_____|\___/|_____|
"""
    + "\x1b[0m\x1b[36m"
    + r"""
        .-.
       (o o)    a removed directory entry is not a removed file
       /|_|\    filter : ghost-filter --job Q-042
      /  |  \   evidence: collection.log (2026-08-22T01:14:08Z)
       `---'
"""
    + "\x1b[0m"
    + "\x1b[33m  [ queue empty ]  [ one orphaned document ]  [ console ready ]\x1b[0m\n"
    + "\x1b[90m  Type 'help' for the console commands.\x1b[0m\n\n"
)

HELP = (
    "\x1b[1;37mcommands:\x1b[0m help, ps, lsof, read-spool <spool-id>, submit <sha256>\n"
    "  \x1b[32mhelp\x1b[0m            show this menu\n"
    "  \x1b[32mps\x1b[0m              show the filter process\n"
    "  \x1b[32mlsof\x1b[0m            show its open deleted spool descriptor\n"
    "  \x1b[32mread-spool\x1b[0m ID    read the spool by the id shown in lsof\n"
    "  \x1b[32msubmit\x1b[0m SHA256    submit the SHA-256 of the recovered document\n"
    "\x1b[90mThe digest covers the exact returned bytes, including the final newline.\x1b[0m\n"
)


def reply(command: str) -> str:
    command = command.strip()
    if command == "help":
        return HELP
    if command == "ps":
        return "\x1b[1;37mPID   PPID  COMMAND\x1b[0m\n" + f"{os.getpid()} {os.getppid()} ghost-filter --job Q-042\n"
    if command == "lsof":
        return f"\x1b[36mghost-filter {os.getpid()} {FD}r REG /tmp/print-spool-{SPOOL} (deleted)\x1b[0m\n"
    if command == f"read-spool {SPOOL}":
        return os.pread(FD, os.fstat(FD).st_size, 0).decode()
    if command.startswith("submit "):
        if command[7:] == PROOF:
            return f"\x1b[1;32m{FLAG}\x1b[0m\n\x1b[32m[ case closed ]\x1b[0m\n"
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
    with Server(("0.0.0.0", int(os.getenv("PORT", "7713"))), Handler) as server:
        server.serve_forever()
