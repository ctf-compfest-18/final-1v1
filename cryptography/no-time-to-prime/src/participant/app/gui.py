"""Recovery console."""
import time
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QProgressBar, QPushButton, QScrollArea, QTextEdit,
    QVBoxLayout, QWidget)
from .crypto_core import MODULES, read_json, recover_final, validate_token

STYLE = """
QWidget { background: #0b1119; color: #dce5ee; font-family: 'Inter', 'Segoe UI', 'Arial'; font-size: 13px; }
QFrame#card, QFrame#vault { background: #121d29; border: 1px solid #293a4c; border-radius: 12px; }
QFrame#card QLabel, QFrame#vault QLabel { background: transparent; border: none; }
QLabel#eyebrow { color: #f6ad55; font-size: 11px; font-weight: bold; letter-spacing: 2px; }
QLabel#title { color: #f3f7fc; font-size: 34px; font-weight: bold; }
QLabel#muted { color: #91a4b8; }
QLabel#clock { color: #f6ad55; font-family: monospace; font-size: 38px; font-weight: bold; }
QLabel#cardtitle { color: #f3f7fc; font-size: 19px; font-weight: bold; }
QLabel#status { color: #f6ad55; font-size: 11px; font-weight: bold; }
QLineEdit { background: #080e16; border: 1px solid #33495e; border-radius: 6px; padding: 11px; font-family: monospace; }
QLineEdit:focus { border: 1px solid #5de2bd; }
QLineEdit:disabled { color: #5de2bd; border-color: #225647; }
QPushButton { background: #23364a; border: 1px solid #344e67; border-radius: 6px; padding: 10px 14px; font-weight: bold; }
QPushButton:hover { background: #304a64; }
QPushButton:disabled { color: #738599; background: #192330; border-color: #293746; }
QPushButton#primary { background: #5de2bd; color: #091610; border: none; }
QPushButton#primary:hover { background: #82f2d2; }
QPushButton#primary:disabled { background: #244a43; color: #819f98; }
QProgressBar { border: none; border-radius: 4px; background: #1b2b3c; height: 8px; }
QProgressBar::chunk { background: #5de2bd; border-radius: 4px; }
QTextEdit { background: #080e16; border: 1px solid #293a4c; border-radius: 6px; padding: 10px; font-family: monospace; color: #7de8c8; }
QScrollArea { border: none; }
"""

def label(text, name=None, wrap=False):
    widget = QLabel(text)
    if name:
        widget.setObjectName(name)
    widget.setWordWrap(wrap)
    return widget

class RecoveryWindow(QMainWindow):
    def __init__(self, challenge):
        super().__init__()
        self.challenge = Path(challenge).resolve()
        self.manifest = read_json(self.challenge / "manifest.json")
        self.tokens = {}
        self.entries, self.statuses, self.submit_buttons = {}, {}, {}
        self.started_at = None
        self.duration = self.manifest["duration_seconds"]
        self.setWindowTitle("No Time to Prime | COMPFEST Recovery Console")
        self.resize(1200, 960)
        self.setMinimumSize(1000, 720)
        self.setStyleSheet(STYLE)
        outer = QScrollArea()
        outer.setWidgetResizable(True)
        canvas = QWidget()
        layout = QVBoxLayout(canvas)
        layout.setContentsMargins(32, 28, 32, 26)
        layout.setSpacing(20)
        header = QHBoxLayout()
        title_column = QVBoxLayout()
        title_column.addWidget(label("COMPFEST  /  FINAL TIE-BREAKER", "eyebrow"))
        title_column.addWidget(label("NO TIME TO PRIME", "title"))
        title_column.addWidget(label("Emergency cryptographic recovery  •  3 modules / 1 final flag", "muted"))
        header.addLayout(title_column, 1)
        timer_column = QVBoxLayout()
        self.clock = label("20:00", "clock")
        self.clock.setAlignment(Qt.AlignmentFlag.AlignRight)
        timer_column.addWidget(self.clock)
        timer_column.addWidget(label("TIMER LOKAL • REFERENSI LATIHAN", "muted"))
        header.addLayout(timer_column)
        layout.addLayout(header)
        controls = QHBoxLayout()
        self.start_button = QPushButton("MULAI TIMER 20 MENIT")
        self.start_button.clicked.connect(self.start_timer)
        controls.addWidget(self.start_button)
        browse = QPushButton("BUKA FOLDER CHALLENGE")
        browse.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.challenge))))
        controls.addWidget(browse)
        controls.addStretch()
        self.progress_text = label("RECOVERY PROGRESS  0 / 3", "eyebrow")
        controls.addWidget(self.progress_text)
        layout.addLayout(controls)
        self.progress = QProgressBar()
        self.progress.setRange(0, 3)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        layout.addWidget(self.progress)
        cards = QGridLayout()
        cards.setSpacing(16)
        descriptions = [
            ("01", "Module 1", "Recover token 01.", "module1.json"),
            ("02", "Module 2", "Recover token 02.", "module2.json"),
            ("03", "Module 3", "Recover token 03.", "module3.json")]
        for column, (module, desc) in enumerate(zip(MODULES, descriptions)):
            number, title, body, filename = desc
            card = QFrame()
            card.setObjectName("card")
            box = QVBoxLayout(card)
            box.setContentsMargins(20, 20, 20, 20)
            box.setSpacing(13)
            box.addWidget(label("RECOVERY MODULE " + number, "eyebrow"))
            box.addWidget(label(title, "cardtitle"))
            info = label(body, "muted", True)
            info.setMinimumHeight(66)
            box.addWidget(info)
            file_button = QPushButton("OPEN " + filename)
            file_button.clicked.connect(lambda checked=False, f=filename: QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.challenge / f))))
            box.addWidget(file_button)
            entry = QLineEdit()
            entry.setPlaceholderText("Recovery token • 64 hex chars")
            entry.setMaxLength(128)
            entry.setAccessibleName(title + " recovery token")
            entry.returnPressed.connect(lambda m=module: self.submit(m))
            box.addWidget(entry)
            submit = QPushButton("SUBMIT TOKEN")
            submit.clicked.connect(lambda checked=False, m=module: self.submit(m))
            box.addWidget(submit)
            status = label("UNSOLVED  /  AWAITING RECOVERY", "status", True)
            status.setMinimumHeight(34)
            box.addWidget(status)
            self.entries[module], self.statuses[module], self.submit_buttons[module] = entry, status, submit
            cards.addWidget(card, 0, column)
            cards.setColumnStretch(column, 1)
        layout.addLayout(cards)
        vault = QFrame()
        vault.setObjectName("vault")
        vault_layout = QVBoxLayout(vault)
        vault_layout.setContentsMargins(20, 18, 20, 18)
        vault_header = QHBoxLayout()
        vault_title = QVBoxLayout()
        vault_title.addWidget(label("FINAL / MASTER-KEY RECOVERY", "eyebrow"))
        self.vault_status = label("LOCKED • Selesaikan ketiga modul untuk membuka final vault.", "muted", True)
        vault_title.addWidget(self.vault_status)
        vault_header.addLayout(vault_title, 1)
        self.unlock_button = QPushButton("RECOVER MASTER KEY")
        self.unlock_button.setObjectName("primary")
        self.unlock_button.setEnabled(False)
        self.unlock_button.clicked.connect(self.unlock)
        vault_header.addWidget(self.unlock_button)
        vault_layout.addLayout(vault_header)
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setMinimumHeight(100)
        self.output.setMaximumHeight(145)
        self.output.setPlaceholderText("[vault] Menunggu 3 recovery token yang valid ...")
        vault_layout.addWidget(self.output)
        layout.addWidget(vault)
        footer = label("OFFLINE CONSOLE  •  Token tersimpan selama sesi ini.", "muted", True)
        layout.addWidget(footer)
        layout.addStretch()
        outer.setWidget(canvas)
        self.setCentralWidget(outer)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(250)

    def start_timer(self):
        if self.started_at is None:
            self.started_at = time.monotonic()
            self.start_button.setText("TIMER BERJALAN")
            self.start_button.setEnabled(False)

    def tick(self):
        if self.started_at is None:
            return
        remaining = max(0, self.duration - int(time.monotonic() - self.started_at))
        self.clock.setText(f"{remaining//60:02d}:{remaining%60:02d}")
        if remaining == 0:
            self.clock.setStyleSheet("color: #ff737e")
            self.start_button.setText("WAKTU LOKAL HABIS")

    def submit(self, module):
        value = self.entries[module].text().strip()
        if not validate_token(self.manifest, module, value):
            self.statuses[module].setText("REJECTED  /  Token salah atau berbeda instance.")
            self.statuses[module].setStyleSheet("color: #ff737e; background: transparent")
            return
        self.tokens[module] = value.lower()
        self.entries[module].setEnabled(False)
        self.submit_buttons[module].setEnabled(False)
        self.statuses[module].setText("SOLVED  /  RECOVERY TOKEN VERIFIED")
        self.statuses[module].setStyleSheet("color: #5de2bd; background: transparent")
        count = len(self.tokens)
        self.progress.setValue(count)
        self.progress_text.setText(f"RECOVERY PROGRESS  {count} / 3")
        self.unlock_button.setEnabled(count == 3)
        if count == 3:
            self.vault_status.setText("READY • Ketiga token terverifikasi. Final vault siap dibuka.")

    def unlock(self):
        try:
            key, flag = recover_final(self.challenge, self.tokens)
        except (ValueError, KeyError, OSError) as exc:
            self.output.setPlainText("[vault] Recovery gagal: " + str(exc))
            return
        self.output.setPlainText("MASTER KEY\n" + key.hex() + "\n\n" + flag)
        self.vault_status.setText("RECOVERED • Salin flag dan submit ke scoreboard resmi.")
        self.unlock_button.setText("VAULT RECOVERED")
        self.unlock_button.setEnabled(False)
