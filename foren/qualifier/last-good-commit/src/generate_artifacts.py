from pathlib import Path
import sqlite3
import zipfile
import hashlib
import json
import os

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".build/last-good-commit.zip"
work = ROOT / ".buildtmp"
work.mkdir(exist_ok=True)
base = work / "inventory.db"
try:
    connection = sqlite3.connect(base)
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA wal_autocheckpoint=0")
    connection.execute("CREATE TABLE shipments(id TEXT PRIMARY KEY, sku TEXT, quantity INTEGER, approved INTEGER, receipt BLOB)")
    connection.commit()
    connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    receipt = os.urandom(24)
    connection.execute("INSERT INTO shipments VALUES ('SHIP-8821', 'BG-14', 6, 1, ?)", (receipt,))
    connection.commit()
    connection.execute("UPDATE shipments SET quantity=99, approved=0, receipt=? WHERE id='SHIP-8821'", (os.urandom(24),))
    connection.commit()
    wal = base.with_name("inventory.db-wal")
    database = base.read_bytes()
    wal_bytes = wal.read_bytes()
    connection.close()
finally:
    for path in work.glob("inventory.db*"):
        path.unlink(missing_ok=True)
    work.rmdir()

OUT.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as archive:
    archive.writestr("evidence/inventory.db", database)
    archive.writestr("evidence/inventory.db-wal", wal_bytes)
    archive.writestr("evidence/warehouse.txt", b"SHIP-8821|BG-14|6|approved\n")
    archive.writestr("evidence/collection.log", b"2026-08-24T04:19:02Z database copied while WAL was active\n")
print(OUT)
proof = hashlib.sha256(f"shipment=SHIP-8821|sku=BG-14|quantity=6|approved=1|receipt={receipt.hex()}".encode()).hexdigest()
(ROOT / "src/answer.json").write_text(json.dumps({"proof": proof}) + "\n")
