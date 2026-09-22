"""Build the participant archive."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent
CHALLENGE = ROOT.parent
NTTP = CHALLENGE.name == "no-time-to-prime"
FILES = (
    "README.md",
    "run.py", "recover.py", "run.sh", "run.bat",
    "app/__init__.py", "app/crypto_core.py", "app/gui.py",
    "challenge/manifest.json", "challenge/module1.json", "challenge/module2.json",
    "challenge/module3.json", "challenge/final.enc.json",
) if NTTP else ("chall.py", "output.json", "README.md")

def main():
    seven_zip = shutil.which("7zz") or shutil.which("7z")
    if not seven_zip:
        raise RuntimeError("7-Zip is required.")
    match = re.search(r"^Password: `([^`\n]+)`$", (CHALLENGE / "README.md").read_text(), re.M)
    if not match:
        raise ValueError("Missing password in README.md")
    password = match.group(1)
    verify = ROOT / ("probset/tests/verify.py" if NTTP else "probset/verify.py")
    subprocess.run([sys.executable, str(verify)], check=True)
    flag_path = ROOT / ("probset/secrets/flag.txt" if NTTP else "probset/flag.txt")
    flag = flag_path.read_text().strip()
    destination = CHALLENGE / "public"
    destination.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="crypto-release-") as directory:
        temp = Path(directory)
        stage = temp / "stage"
        stage.mkdir()
        for name in FILES:
            source = ROOT / "participant" / name
            if source.is_symlink() or not source.is_file():
                raise ValueError("Missing file: " + name)
            data = source.read_bytes()
            if password.encode() in data or flag.encode() in data:
                raise ValueError("Private value in " + name)
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        archive = temp / "participant.zip"
        subprocess.run([seven_zip, "a", "-tzip", "-mem=AES256", "-mx=9",
                        "-p" + password, str(archive), *FILES],
                       cwd=stage, check=True, capture_output=True)
        with zipfile.ZipFile(archive) as z:
            assert set(z.namelist()) == set(FILES)
            assert all(i.flag_bits & 1 and i.compress_type == 99
                       for i in z.infolist() if i.file_size)
        for bad in ("", "incorrect-password"):
            result = subprocess.run([seven_zip, "t", "-p" + bad, str(archive)],
                                    input=b"", capture_output=True)
            if result.returncode == 0:
                raise ValueError("Archive accepted an invalid password")
        extracted = temp / "extracted"
        subprocess.run([seven_zip, "x", "-y", "-p" + password,
                        "-o" + str(extracted), str(archive)],
                       check=True, capture_output=True)
        for name in FILES:
            assert (extracted / name).read_bytes() == (stage / name).read_bytes()
        solver = ROOT / ("probset/solver/solve_all.py" if NTTP else "probset/solve.py")
        arguments = ["--challenge", str(extracted / "challenge"), "--json"] if NTTP else [str(extracted)]
        output = subprocess.check_output([sys.executable, str(solver), *arguments])
        recovered = json.loads(output)["flag"] if NTTP else output.decode().strip()
        assert recovered == flag
        shutil.copy2(archive, destination / "participant.zip")
    digest = hashlib.sha256((destination / "participant.zip").read_bytes()).hexdigest()
    (destination / "SHA256SUMS.txt").write_text(digest + "  participant.zip\n")
    metadata = CHALLENGE / "challenge.yml"
    text, count = re.subn(r"(?m)^flags:\n  - .*$",
                         lambda _: "flags:\n  - " + json.dumps(flag), metadata.read_text())
    if count != 1:
        raise ValueError("Expected one flags entry in challenge.yml")
    metadata.write_text(text)
    print(destination / "participant.zip")

if __name__ == "__main__":
    main()
