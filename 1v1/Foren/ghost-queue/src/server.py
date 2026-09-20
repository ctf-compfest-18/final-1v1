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


def reply(command: str) -> str:
    command = command.strip()
    if command == "help":
        return "commands: help, ps, lsof, read-spool <spool-id>, submit <sha256>\nHash the exact document bytes, including the final newline.\n"
    if command == "ps":
        return f"PID PPID COMMAND\n{os.getpid()} {os.getppid()} ghost-filter --job Q-042\n"
    if command == "lsof":
        return f"ghost-filter {os.getpid()} {FD}r REG /tmp/print-spool-{SPOOL} (deleted)\n"
    if command == f"read-spool {SPOOL}":
        return os.pread(FD, os.fstat(FD).st_size, 0).decode()
    if command.startswith("submit "):
        return FLAG + "\n" if command[7:] == PROOF else "proof rejected\n"
    return "unknown command\n"


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        self.connection.settimeout(10)
        try:
            self.wfile.write(b"ghost-queue forensic console\n> ")
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
    with Server(("0.0.0.0", int(os.getenv("PORT", "7713"))), Handler) as server:
        server.serve_forever()
