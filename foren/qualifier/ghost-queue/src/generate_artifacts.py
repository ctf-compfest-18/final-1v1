from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".build/ghost-queue.zip"
files = {
    "responder/collection.log": b"2026-08-22T01:14:08Z queue cleanup completed; orphaned job Q-042 remained active\n",
}
OUT.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as archive:
    for name, data in files.items():
        archive.writestr(name, data)
print(OUT)
