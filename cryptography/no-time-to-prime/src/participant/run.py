#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys

def main():
    parser = argparse.ArgumentParser(description="No Time to Prime offline recovery console")
    parser.add_argument("--challenge", type=Path, default=Path(__file__).parent / "challenge")
    args = parser.parse_args()
    try:
        from PySide6.QtWidgets import QApplication
        from app.gui import RecoveryWindow
    except ImportError as exc:
        parser.exit(1, f"Missing dependency: {exc}\n")
    app = QApplication(sys.argv[:1])
    try:
        window = RecoveryWindow(args.challenge)
    except (OSError, KeyError, ValueError) as exc:
        parser.exit(1, f"Challenge tidak dapat dimuat: {exc}\n")
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
