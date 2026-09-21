"""Generate and verify a new instance."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if __name__ == "__main__":
    subprocess.run([sys.executable, str(HERE/"generate.py"), *sys.argv[1:]], check=True)
    subprocess.run([sys.executable, str(HERE/"verify.py")], check=True)
