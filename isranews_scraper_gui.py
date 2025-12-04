# isranews_scraper_gui.py

import sys
import threading
import datetime
import asyncio
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QComboBox, QLineEdit, QSpinBox, QPushButton,
    QVBoxLayout, QHBoxLayout, QProgressBar, QTextEdit, QDateEdit, QMessageBox, QCheckBox,
    QFrame, QGridLayout
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor

# --- Import backend ---
from isranews_scraper import IsranewsScraper, CATEGORY_MAP, EXPORT_FORMATS

# --- Modern Dark Theme Stylesheet ---
STYLESHEET = """
QWidget {
    background-color: #1E1E2E;
    color: #CDD6F4;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}

QFrame#Container {
    background-color: #252537;
    border-radius: 12px;
    border: 1px solid #313244;
}

QLabel {
    color: #CDD6F4;
    font-weight: 500;
}

QLabel#Header {
    font-size: 18px;
    font-weight: bold;
    color: #89B4FA;
}

QLineEdit, QComboBox, QSpinBox, QDateEdit {
    background-color: #313244;
    color: #CDD6F4;
    border: 1px solid #45475A;
    border-radius: 6px;
    padding: 8px;
    selection-background-color: #585B70;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus {
    border: 1px solid #89B4FA;
}

QComboBox::drop-down {
    border: 0px;
}

QPushButton {
    background-color: #89B4FA;
    color: #1E1E2E;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #B4BEFE;
}

QPushButton:pressed {
    background-color: #74C7EC;
}

QPushButton:disabled {
    background-color: #45475A;
    color: #6C7086;
}

QPushButton#CancelButton {
    background-color: #F38BA8;
    color: #1E1E2E;
}

QPushButton#CancelButton:hover {
    background-color: #F5C2E7;
}

QProgressBar {
    background-color: #313244;
    border-radius: 6px;
    text-align: center;
    color: #CDD6F4;
    height: 24px;
}

QProgressBar::chunk {
    background-color: #A6E3A1;
    border-radius: 6px;
}

QTextEdit {
    background-color: #181825;
    color: #A6ADC8;
    border: 1px solid #313244;
    border-radius: 8px;
    padding: 8px;
    font-family: 'Consolas', 'Monospace';
    font-size: 12px;
}

QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #45475A;
    background-color: #313244;
}

QCheckBox::indicator:checked {
    background-color: #89B4FA;
    border-color: #89B4FA;
}
"""

class ScraperThread(threading.Thread):
    def __init__(self, params, log_signal, progress_signal, done_signal):
        super().__init__()
        self.params = params
        self.log_signal = log_signal
        self.progress_signal = progress_signal
        self.done_signal = done_signal
        self._is_running = True
        self.scraper = None
        self.loop = None

    def stop(self):
        self._is_running = False
        # To stop asyncio loop gracefully from another thread is tricky.
        # We rely on the loop checking self._is_running if we implemented checks,
        # but for now, we just let it finish or force close browser if possible.
        # Since we can't easily interrupt the async loop from here without complex logic,
        # we will rely on the user knowing that 'Cancel' might take a moment.
        pass

    def run(self):
        try:
            # Create a new event loop for this thread
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self.run_async())
            self.loop.close()
        except Exception as e:
            self.log_signal.emit(f"\n[ERROR] {e}")
        finally:
            self.done_signal.emit()

    async def run_async(self):
        try:
            cat_paths = self.params["cat_paths"]
            start = self.params["start"]
            end = self.params["end"]
            filter_date = self.params["filter_date"]
            fmt = self.params["fmt"]
            filename = self.params["filename"]
            max_threads = self.params["max_threads"]

            def progress_callback(current, total, title):
                if not self._is_running:
                    # This might raise cancellation in the loop
                    pass 
                percent = int((current / total) * 100)
                self.progress_signal.emit(percent)

            self.scraper = IsranewsScraper(max_concurrency=max_threads, headless=True)
            
            self.log_signal.emit("Starting scraper (Async)...")
            await self.scraper.run(
                cat_paths=cat_paths,
                start=start,
                end=end,
                filter_date=filter_date,
                filename=filename,
                fmt=fmt,
                progress_callback=progress_callback
            )
            
            self.progress_signal.emit(100)
            self.log_signal.emit(f"\nSUCCESS: Saved to {filename}.{fmt}")
            
        except Exception as e:
            self.log_signal.emit(f"\n[ERROR] {e}")

class MainWindow(QWidget):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    done_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Isranews Scraper Pro")
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        
        # Apply Theme
        self.setStyleSheet(STYLESHEET)
        
        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("Isranews Scraper")
        header.setObjectName("Header")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)

        # Container Frame
        container = QFrame()
        container.setObjectName("Container")
        form_layout = QGridLayout(container)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 20, 20, 20)

        # Row 1: Category
        form_layout.addWidget(QLabel("หมวดหมู่ข่าว (Category):"), 0, 0)
        self.category_combo = QComboBox()
        self.category_combo.addItem("เลือกทั้งหมด (All Categories)", "all")
        for k, v in CATEGORY_MAP.items():
            self.category_combo.addItem(k, k)
        form_layout.addWidget(self.category_combo, 0, 1, 1, 3)

        # Row 2: Page Range
        form_layout.addWidget(QLabel("หน้าเริ่มต้น (Start Page):"), 1, 0)
        self.start_spin = QSpinBox()
        self.start_spin.setRange(1, 9999)
        self.start_spin.setValue(1)
        form_layout.addWidget(self.start_spin, 1, 1)

        form_layout.addWidget(QLabel("ถึงหน้า (End Page):"), 1, 2)
        self.end_spin = QSpinBox()
        self.end_spin.setRange(0, 9999)
        self.end_spin.setValue(1)
        self.end_spin.setToolTip("0 = Until last page")
        form_layout.addWidget(self.end_spin, 1, 3)

        # Row 3: Date Filter
        self.date_checkbox = QCheckBox("กรองตามวันที่ (Filter Date)")
        self.date_checkbox.setChecked(False)
        self.date_checkbox.stateChanged.connect(self.toggle_dateedit)
        form_layout.addWidget(self.date_checkbox, 2, 0)

        self.date_edit = QDateEdit()
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setEnabled(False)
        form_layout.addWidget(self.date_edit, 2, 1)

        # Row 4: Format & Filename
        form_layout.addWidget(QLabel("รูปแบบไฟล์ (Format):"), 3, 0)
        self.format_combo = QComboBox()
        for fmt in EXPORT_FORMATS:
            self.format_combo.addItem(fmt.upper(), fmt)
        form_layout.addWidget(self.format_combo, 3, 1)

        form_layout.addWidget(QLabel("ชื่อไฟล์ (Filename):"), 3, 2)
        self.filename_edit = QLineEdit("isranews_data")
        form_layout.addWidget(self.filename_edit, 3, 3)

        # Row 5: Threads
        form_layout.addWidget(QLabel("Concurrency:"), 4, 0)
        self.thread_spin = QSpinBox()
        self.thread_spin.setRange(1, 32)
        self.thread_spin.setValue(5)
        form_layout.addWidget(self.thread_spin, 4, 1)

        main_layout.addWidget(container)

        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setFormat("%p%")
        main_layout.addWidget(self.progress)

        # Log Area
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setPlaceholderText("Logs will appear here...")
        main_layout.addWidget(self.log_area)

        # Buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("START SCRAPING")
        self.start_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_button.clicked.connect(self.start_scrape)
        
        self.cancel_button = QPushButton("CANCEL")
        self.cancel_button.setObjectName("CancelButton")
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_scrape)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        # State
        self.thread = None
        
        # Signals
        self.log_signal.connect(self.log)
        self.progress_signal.connect(self.set_progress)
        self.done_signal.connect(self.on_done)

    def toggle_dateedit(self, state):
        self.date_edit.setEnabled(state == Qt.CheckState.Checked.value)

    def log(self, text):
        self.log_area.append(text)
        self.log_area.ensureCursorVisible()

    def set_progress(self, value):
        self.progress.setValue(value)

    def set_running(self, running):
        self.start_button.setEnabled(not running)
        self.cancel_button.setEnabled(running)
        self.category_combo.setEnabled(not running)
        self.start_spin.setEnabled(not running)
        self.end_spin.setEnabled(not running)
        self.filename_edit.setEnabled(not running)

    def start_scrape(self):
        self.log_area.clear()
        
        # Gather Params
        cat_sel = self.category_combo.currentData()
        if cat_sel == "all":
            cat_paths = list(CATEGORY_MAP.values())
        else:
            cat_paths = [CATEGORY_MAP[cat_sel]]
            
        start = self.start_spin.value()
        end = self.end_spin.value()
        
        filter_date = None
        if self.date_checkbox.isChecked():
            d = self.date_edit.date()
            filter_date = datetime.datetime(d.year(), d.month(), d.day())

        fmt = self.format_combo.currentData()
        filename = self.filename_edit.text().strip() or "isranews_data"
        max_threads = self.thread_spin.value()

        params = {
            "cat_paths": cat_paths,
            "start": start,
            "end": end,
            "filter_date": filter_date,
            "fmt": fmt,
            "filename": filename,
            "max_threads": max_threads
        }

        self.set_progress(0)
        self.set_running(True)
        
        self.thread = ScraperThread(params, self.log_signal, self.progress_signal, self.done_signal)
        self.thread.start()

    def cancel_scrape(self):
        if self.thread and self.thread.is_alive():
            self.thread.stop()
            self.log("Cancelling... (might take a moment)")
            self.cancel_button.setEnabled(False)

    def on_done(self):
        self.set_running(False)
        QMessageBox.information(self, "Done", "Process Completed!", QMessageBox.StandardButton.Ok)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
