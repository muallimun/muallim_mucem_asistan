import sys, re, time, keyboard, pyperclip, mouse, json, os, traceback, urllib.request
import openpyxl
from openpyxl import Workbook, load_workbook

try:
    import winreg
except ImportError:
    winreg = None

from PyQt6.QtCore import Qt, QUrl, pyqtSignal, QObject, QTimer
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QPushButton, QHBoxLayout, QLabel, QSystemTrayIcon, 
                             QMenu, QDialog, QLineEdit, QMessageBox, 
                             QCheckBox, QFileDialog, QFrame, QTextEdit)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtGui import QAction, QCursor, QDesktopServices, QIcon

VERSION = "1.0.0"
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/kullanici_adiniz/repo_adiniz/main/version.json" # Burayı güncelleyeceksiniz

# --- YOL YÖNETİCİSİ ---
def get_app_data_path():
    app_data = os.path.join(os.environ['APPDATA'], 'MuallimunAsistan')
    if not os.path.exists(app_data): os.makedirs(app_data)
    return app_data

def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except Exception: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class SilentWebPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineID, sourceID): pass

# --- AYAR YÖNETİCİSİ ---
class SettingsManager:
    def __init__(self):
        self.path = os.path.join(get_app_data_path(), "asistan_ayarlar.json")
        self.defaults = {
            "hotkey": "ctrl+shift+z", 
            "excel_path": os.path.join(os.path.expanduser("~"), "Desktop", "Arapca_Kelime_Bankasi.xlsx"),
            "auto_start": False,
            "allow_empty_meaning": False
        }
        if not os.path.exists(self.path): self.save(self.defaults)

    def load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f: return json.load(f)
        except: return self.defaults

    def save(self, data):
        with open(self.path, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

# --- AYARLAR VE BİLGİ PENCERESİ ---
class SettingsDialog(QDialog):
    def __init__(self, manager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.settings = manager.load()
        self.setWindowTitle("Muallimun Asistan - Ayarlar")
        self.setFixedSize(500, 560)
        self.setWindowIcon(QIcon(resource_path("muallim.ico")))
        self.setStyleSheet("background-color: white;")
        layout = QVBoxLayout()

        # Bilgi Paneli
        info_box = QFrame()
        info_box.setStyleSheet("background-color: #f8fbff; border: 1px solid #d1e2ff; border-radius: 10px;")
        info_layout = QVBoxLayout(info_box)
        info_layout.addWidget(QLabel("🚀 <b>Evrensel Kullanım Rehberi</b>"))
        info_layout.addWidget(QLabel(f"Versiyon: {VERSION}\n"
                                   "• Sistemdeki tüm pencerelerde Arapça metinleri tanır.\n"
                                   "• Kısayol: {self.settings['hotkey'].upper()} | Fare: Orta Tekerlek"))
        
        btn_update = QPushButton("🔄 Güncelleme Kontrol Et")
        btn_update.clicked.connect(self.check_update)
        info_layout.addWidget(btn_update)
        layout.addWidget(info_box)

        # Form
        self.hotkey_input = QLineEdit(self.settings["hotkey"])
        layout.addWidget(QLabel("⌨️ <b>Kısayol Tuşu:</b>"))
        layout.addWidget(self.hotkey_input)

        self.path_input = QLineEdit(self.settings["excel_path"])
        layout.addWidget(QLabel("📁 <b>Excel Konumu:</b>"))
        p_lay = QHBoxLayout()
        p_lay.addWidget(self.path_input)
        btn_b = QPushButton("Seç"); btn_b.clicked.connect(self.browse_path)
        p_lay.addWidget(btn_b); layout.addLayout(p_lay)

        self.auto_start_cb = QCheckBox("Windows açıldığında çalıştır")
        self.auto_start_cb.setChecked(self.settings.get("auto_start", False))
        layout.addWidget(self.auto_start_cb)

        self.empty_save_cb = QCheckBox("Anlam olmadan kayda izin ver")
        self.empty_save_cb.setChecked(self.settings.get("allow_empty_meaning", False))
        layout.addWidget(self.empty_save_cb)

        btn_save = QPushButton("Ayarları Kaydet"); btn_save.clicked.connect(self.save_settings)
        btn_save.setStyleSheet("background: #10b981; color: white; font-weight: bold; padding: 10px;")
        layout.addWidget(btn_save)

        self.setLayout(layout)

    def browse_path(self):
        f, _ = QFileDialog.getSaveFileName(self, "Excel Seç", self.path_input.text(), "Excel (*.xlsx)")
        if f: self.path_input.setText(f)

    def check_update(self):
        try:
            with urllib.request.urlopen(GITHUB_VERSION_URL) as response:
                data = json.loads(response.read().decode())
                new_ver = data.get("version", VERSION)
                if new_ver != VERSION:
                    QMessageBox.information(self, "Güncelleme", f"Yeni bir sürüm mevcut: {new_ver}\nLütfen web sitemizden indirin.")
                else:
                    QMessageBox.information(self, "Güncelleme", "Uygulamanız güncel.")
        except:
            QMessageBox.warning(self, "Hata", "Güncelleme sunucusuna bağlanılamadı.")

    def save_settings(self):
        self.settings.update({"hotkey": self.hotkey_input.text().lower(), "excel_path": self.path_input.text(), 
                             "auto_start": self.auto_start_cb.isChecked(), "allow_empty_meaning": self.empty_save_cb.isChecked()})
        self.manager.save(self.settings)
        # Registry (Aynı kalacak)
        self.accept()

# --- ANA PENCERE ---
class DictionaryWindow(QMainWindow):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setFixedSize(620, 850)
        self.setWindowIcon(QIcon(resource_path("muallim.ico")))
        self.current_word = ""
        self._old_pos = None

        container = QWidget()
        container.setStyleSheet("QWidget { background: white; border: 2px solid #1e3a8a; border-radius: 15px; }")
        layout = QVBoxLayout(container)

        header = QWidget(); header.setFixedHeight(50); header.setStyleSheet("background: #1e3a8a; border-radius: 0px; border-top-left-radius: 12px; border-top-right-radius: 12px;")
        h_lay = QHBoxLayout(header)
        h_lay.addWidget(QLabel("<b style='color:white'>MUALLİMUN SÖZLÜK</b>"))
        btn_c = QPushButton("✕"); btn_c.setFixedSize(30,30); btn_c.clicked.connect(self.hide)
        h_lay.addStretch(); h_lay.addWidget(btn_c)

        self.browser = QWebEngineView()
        self.browser.setPage(SilentWebPage(self.browser))

        footer = QWidget(); footer.setFixedHeight(210); footer.setStyleSheet("background: #f8fafc;")
        f_lay = QVBoxLayout(footer)
        self.meaning_box = QTextEdit(); f_lay.addWidget(self.meaning_box)
        self.btn_save = QPushButton("Deftere Kaydet"); self.btn_save.clicked.connect(self.save_to_excel); f_lay.addWidget(self.btn_save)

        layout.addWidget(header); layout.addWidget(self.browser); layout.addWidget(footer)
        self.setCentralWidget(container)

    def search_word(self, word):
        self.current_word = word; self.meaning_box.clear()
        self.browser.setUrl(QUrl(f"https://www.almaany.com/tr/dict/ar-tr/{word}"))
        self.show_at_pos()

    def show_at_pos(self):
        pos = QCursor.pos()
        self.move(pos.x() + 20, pos.y() + 20)
        self.showNormal(); self.show(); self.activateWindow()

    def save_to_excel(self):
        f = self.settings["excel_path"]; m = self.meaning_box.toPlainText().strip()
        if not m and not self.settings.get("allow_empty_meaning", False): return
        try:
            if not os.path.exists(f):
                wb = Workbook(); ws = wb.active; ws.append(["Tarih", "Kelime", "Anlam"])
            else:
                wb = load_workbook(f); ws = wb.active
            ws.append([time.strftime("%d.%m.%Y %H:%M"), self.current_word, m or "Anlam yok"])
            wb.save(f); self.btn_save.setText("Kaydedildi ✅")
        except: QMessageBox.critical(self, "Hata", "Excel açık olabilir!")

# --- APP CONTROLLER ---
class AppController(QObject):
    search_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.manager = SettingsManager(); self.settings = self.manager.load()
        self.app = QApplication(sys.argv); self.app.setQuitOnLastWindowClosed(False)
        self.window = DictionaryWindow(self.settings)
        self.search_signal.connect(self.window.search_word)
        
        self.setup_tray()
        # Tetikleyiciler
        keyboard.add_hotkey(self.settings["hotkey"], self.trigger_search)
        mouse.on_middle_click(self.trigger_search)

    def setup_tray(self):
        self.tray = QSystemTrayIcon(QIcon(resource_path("muallim.ico")))
        menu = QMenu()
        menu.addAction("Ayarlar", lambda: SettingsDialog(self.manager, self.window).exec())
        menu.addAction("Çıkış", self.app.quit)
        self.tray.setContextMenu(menu); self.tray.show()

    def trigger_search(self):
        # Ses ikonunu önlemek için Clipboard işlemini asenkron yapıyoruz
        QTimer.singleShot(150, self.process_clipboard)

    def process_clipboard(self):
        old_clip = pyperclip.paste()
        pyperclip.copy("")
        keyboard.press_and_release('ctrl+c')
        time.sleep(0.3)
        text = pyperclip.paste().strip()
        clean = re.sub(r'[^\u0600-\u06FF]', '', text)
        if clean: self.search_signal.emit(clean)
        else: pyperclip.copy(old_clip)

    def run(self): return self.app.exec()

if __name__ == "__main__":
    controller = AppController()
    try: sys.exit(controller.run())
    except BaseException: pass