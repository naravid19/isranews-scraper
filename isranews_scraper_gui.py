# isranews_scraper_gui.py

import sys
import threading
import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QComboBox, QLineEdit, QSpinBox, QPushButton,
    QVBoxLayout, QHBoxLayout, QProgressBar, QTextEdit, QDateEdit, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal

# --- Import backend ---
from isranews_scraper import (
    category_map, EXPORT_FORMATS, scrape_category, merge_news,
    extract_full_content_and_meta, export_news, load_old_news
)

class ScraperThread(threading.Thread):
    def __init__(self, params, log_signal, progress_signal, done_signal):
        super().__init__()
        self.params = params
        self.log_signal = log_signal
        self.progress_signal = progress_signal
        self.done_signal = done_signal
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        try:
            cat_paths = self.params["cat_paths"]
            start = self.params["start"]
            end = self.params["end"]
            filter_date = self.params["filter_date"]
            fmt = self.params["fmt"]
            filename = self.params["filename"]
            max_threads = self.params["max_threads"]

            filename_with_ext = f"{filename}.{('xlsx' if fmt=='excel' else fmt)}"
            old_news = load_old_news(filename_with_ext, fmt)
            scraped_urls = {news["URL"] for news in old_news}
            news_results = []
            workers = min(max_threads, len(cat_paths))

            from concurrent.futures import ThreadPoolExecutor, as_completed

            # Scrape list
            with ThreadPoolExecutor(max_workers=workers) as executor:
                future2cat = {
                    executor.submit(scrape_category, cat_path, start, end, filter_date, scraped_urls): cat_path
                    for cat_path in cat_paths
                }
                for i, future in enumerate(as_completed(future2cat), 1):
                    if not self._is_running:
                        self.log_signal.emit("User cancelled process.")
                        return
                    news_results.extend(future.result())
                    self.progress_signal.emit(int(i / len(cat_paths) * 30))
            news_list = merge_news(old_news, news_results)

            # Scrape content (parallel)
            total = len(news_list)
            with ThreadPoolExecutor(max_workers=max_threads) as executor:
                future_to_idx = {
                    executor.submit(extract_full_content_and_meta, news['URL']): i
                    for i, news in enumerate(news_list)
                    if not news.get("เนื้อหา") or news.get("เนื้อหา") == "[ERROR]"
                }
                for idx, future in enumerate(as_completed(future_to_idx), 1):
                    if not self._is_running:
                        self.log_signal.emit("User cancelled process.")
                        return
                    i = future_to_idx[future]
                    content, categories, tags, views = future.result()
                    news_list[i]['เนื้อหา'] = content
                    news_list[i]['หมวดหมู่ข่าว'] = categories
                    news_list[i]['Tags'] = tags
                    news_list[i]['ยอดวิว'] = views
                    self.progress_signal.emit(int(30 + idx / (total if total else 1) * 65))

            export_news(news_list, filename, fmt)
            self.progress_signal.emit(100)
            self.log_signal.emit(f"\nบันทึกข่าวทั้งหมดลงไฟล์ {filename}.{fmt} แล้ว")
        except Exception as e:
            self.log_signal.emit(f"\n[ERROR] {e}")
        finally:
            self.done_signal.emit()

class MainWindow(QWidget):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    done_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Isranews News Scraper GUI")
        self.setMinimumWidth(580)
        self.setStyleSheet("""
            QWidget { background: #171B23; color: #E5E7EF; font-size:15px;}
            QLabel { font-weight: 500; }
            QLineEdit, QComboBox, QSpinBox, QDateEdit {
                background: #242735; color: #eaeaea; border-radius: 7px;
                border: 1px solid #36395a; padding: 7px 10px;
            }
            QCheckBox { color: #b0b2ba; padding: 2px 0 0 6px;}
            QPushButton {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5A67E5, stop:1 #7C5DFA);
                color: #fff; border-radius: 7px; font-weight: 600; padding: 10px 24px;
            }
            QPushButton:disabled { background: #232645; color: #999; }
            QProgressBar { height: 22px; border-radius: 7px; background: #222645; text-align: center; }
            QProgressBar::chunk {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #6E8CFB, stop:1 #A684EA);
                border-radius: 7px;
            }
        """)
        main = QVBoxLayout(self)
        form = QVBoxLayout()
        row1 = QHBoxLayout()
        row2 = QHBoxLayout()
        row3 = QHBoxLayout()
        row4 = QHBoxLayout()
        row5 = QHBoxLayout()

        self.category_label = QLabel("หมวดหมู่ข่าว")
        self.category_combo = QComboBox()
        self.category_combo.addItem("เลือกทั้งหมด (all)", "all")
        for k in category_map:
            self.category_combo.addItem(k, k)
        row1.addWidget(self.category_label)
        row1.addWidget(self.category_combo)

        self.start_label = QLabel("หน้าที่เริ่มต้น")
        self.start_spin = QSpinBox(); self.start_spin.setRange(1, 9999); self.start_spin.setValue(1)
        self.end_label = QLabel("ถึงหน้า")
        self.end_spin = QSpinBox(); self.end_spin.setRange(0, 9999); self.end_spin.setValue(1)
        row2.addWidget(self.start_label)
        row2.addWidget(self.start_spin)
        row2.addWidget(self.end_label)
        row2.addWidget(self.end_spin)

        self.date_label = QLabel("วันที่ (ใหม่กว่า)")
        self.date_checkbox = QCheckBox("ใช้ตัวกรองวันที่")
        self.date_checkbox.setChecked(False)
        self.date_edit = QDateEdit()
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setEnabled(False)
        self.date_checkbox.stateChanged.connect(self.toggle_dateedit)

        row3.addWidget(self.date_label)
        row3.addWidget(self.date_edit)
        row3.addWidget(self.date_checkbox)

        self.format_label = QLabel("Export Format")
        self.format_combo = QComboBox()
        for fmt in EXPORT_FORMATS:
            self.format_combo.addItem(fmt.upper(), fmt)
        self.filename_label = QLabel("ชื่อไฟล์")
        self.filename_edit = QLineEdit("isranews")
        row4.addWidget(self.format_label)
        row4.addWidget(self.format_combo)
        row4.addWidget(self.filename_label)
        row4.addWidget(self.filename_edit)

        self.thread_label = QLabel("จำนวน Threads")
        self.thread_spin = QSpinBox(); self.thread_spin.setRange(1, 32); self.thread_spin.setValue(8)
        row5.addWidget(self.thread_label)
        row5.addWidget(self.thread_spin)

        self.start_button = QPushButton("เริ่มดึงข่าว")
        self.start_button.clicked.connect(self.start_scrape)
        self.cancel_button = QPushButton("ยกเลิก")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_scrape)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMinimumHeight(120)
        self.log_area.setStyleSheet("QTextEdit { background: #1A1C29; color: #A0A3B1; border-radius: 7px; }")

        # Layout setup
        form.addLayout(row1)
        form.addLayout(row2)
        form.addLayout(row3)
        form.addLayout(row4)
        form.addLayout(row5)
        main.addLayout(form)
        main.addWidget(self.progress)
        main.addWidget(self.log_area)
        row_button = QHBoxLayout()
        row_button.addWidget(self.start_button)
        row_button.addWidget(self.cancel_button)
        main.addLayout(row_button)

        self.thread = None

        # Connect signals
        self.log_signal.connect(self.log)
        self.progress_signal.connect(self.set_progress)
        self.done_signal.connect(self.on_done)

    def toggle_dateedit(self, state):
        self.date_edit.setEnabled(state == Qt.CheckState.Checked.value)

    def log(self, text):
        self.log_area.append(text)
        self.log_area.ensureCursorVisible()

    def set_progress(self, value):
        self.progress.setValue(int(value))

    def set_running(self, running):
        self.start_button.setEnabled(not running)
        self.cancel_button.setEnabled(running)

    def start_scrape(self):
        self.log_area.clear()
        cat_sel = self.category_combo.currentData()
        if cat_sel == "all":
            cat_paths = list(category_map.values())
        else:
            cat_paths = [category_map[cat_sel]]
        start = self.start_spin.value()
        end = self.end_spin.value()

        # NEW: เลือกว่าจะใช้วันที่หรือไม่
        if self.date_checkbox.isChecked():
            date_val = self.date_edit.date().toString("yyyy-MM-dd")
            try:
                filter_date = datetime.datetime.strptime(date_val, "%Y-%m-%d")
            except Exception:
                filter_date = None
        else:
            filter_date = None

        fmt = self.format_combo.currentData()
        filename = self.filename_edit.text().strip() or "isranews"
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
        self.thread = ScraperThread(
            params, 
            self.log_signal, 
            self.progress_signal, 
            self.done_signal
        )
        self.thread.start()
        self.log("เริ่มดึงข่าว ...")

    def cancel_scrape(self):
        if self.thread is not None:
            self.thread.stop()
            self.set_running(False)
            self.log("[ยกเลิกแล้ว]")

    def on_done(self):
        self.set_running(False)
        QMessageBox.information(self, "เสร็จสิ้น", "ดึงข่าวและ export เสร็จสมบูรณ์!", QMessageBox.StandardButton.Ok)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
