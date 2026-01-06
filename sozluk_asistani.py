import sys, re, time, keyboard, pyperclip, mouse, json, os, traceback, urllib.request, ssl, ctypes
import openpyxl
from openpyxl import Workbook, load_workbook

# --- DPI AYARI (Qt6 OTOMATİK YÖNETTİĞİ İÇİN MANUEL ÇAKIŞMA GİDERİLDİ) ---
from PyQt6.QtCore import Qt, QUrl, pyqtSignal, QObject, QTimer, QPoint
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QPushButton, QHBoxLayout, QLabel, QSystemTrayIcon, 
                             QMenu, QDialog, QLineEdit, QMessageBox, 
                             QCheckBox, QFileDialog, QFrame, QTextEdit, QScrollArea, QSizeGrip)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtGui import QAction, QCursor, QDesktopServices, QIcon

# --- YÖNETİCİ KONTROLÜ (UAC) ---
def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

# --- GLOBAL AYARLAR ---
VERSION = "1.0.0"
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/muallimun/muallim_mucem_asistan/refs/heads/main/version.json"

def get_app_data_path():
    path = os.path.join(os.environ['APPDATA'], 'MuallimunAsistan')
    if not os.path.exists(path): os.makedirs(path)
    return path

def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except Exception: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class SilentWebPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineID, sourceID): pass

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

# --- AYARLAR PENCERESİ VE DETAYLI REHBER ---
class SettingsDialog(QDialog):
    settings_changed = pyqtSignal()
    def __init__(self, manager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.settings = manager.load()
        self.setWindowTitle(f"Muallimun Asistan Ayarları - v{VERSION}")
        # Pencere yüksekliği scroll bar oluşmaması için 700'e çıkarıldı
        self.setFixedSize(560, 700)
        self.setStyleSheet("background-color: white;")
        self.setWindowIcon(QIcon(resource_path("muallim.ico")))
        
        layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: #f8fbff; border-radius: 12px;")
        
        info_content = QWidget()
        info_layout = QVBoxLayout(info_content)
        # Rehberdeki boşluklar daha da daraltıldı
        info_layout.setContentsMargins(15, 8, 15, 8)
        info_layout.setSpacing(5)
        
        guide_title = QLabel("🚀 Detaylı Kullanım Rehberi")
        guide_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1e3a8a;")
        
        guide_text = QLabel(
            f"<div style='color: #334155; line-height: 135%; font-family: Segoe UI; font-size: 13px;'>"
            f"<b>• Evrensel Erişim:</b> Uygulama her türlü pencerede Arapça metinleri yakalar.<br>"
            f"<b>• PDF ve Belgelerde:</b> Kelimeyi seçip <b>Mouse Orta Tekerlek</b> tıklayın.<br>"
            f"<b>• Web Sayfalarında:</b> Kelimeyi seçip <b>{self.settings['hotkey'].upper()}</b> tuşlayın.<br>"
            f"<b>• Yönetici Modu:</b> Tarayıcı çakışmalarını önlemek için yetkiyle çalışmaktadır.<br>"
            f"<b>• Akıllı Kayıt:</b> Aramalar tarihli olarak Excel dosyanıza otomatik işlenir."
            f"</div>"
        )
        guide_text.setWordWrap(True)
        
        self.btn_update = QPushButton("🔄 Güncelleme Kontrol Et")
        self.btn_update.setStyleSheet("background: #3b82f6; color: white; font-weight: bold; padding: 10px; border-radius: 6px;")
        self.btn_update.clicked.connect(lambda: self.check_update(manual=True))

        info_layout.addWidget(guide_title)
        info_layout.addWidget(guide_text)
        info_layout.addWidget(self.btn_update)
        scroll.setWidget(info_content)
        layout.addWidget(scroll)

        form_frame = QFrame()
        form_frame.setStyleSheet("background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px;")
        form_layout = QVBoxLayout(form_frame)
        form_layout.addWidget(QLabel("<b>⌨️ Global Kısayol Tuşu:</b>"))
        self.hotkey_input = QLineEdit(self.settings["hotkey"])
        self.hotkey_input.setStyleSheet("padding: 9px; border: 1px solid #cbd5e1; border-radius: 5px;")
        form_layout.addWidget(self.hotkey_input)
        
        form_layout.addWidget(QLabel("<b>📁 Excel Kayıt Dosyası Yolu:</b>"))
        p_lay = QHBoxLayout()
        self.path_input = QLineEdit(self.settings["excel_path"])
        btn_browse = QPushButton("Gözat...")
        btn_browse.clicked.connect(self.browse_path)
        p_lay.addWidget(self.path_input); p_lay.addWidget(btn_browse)
        form_layout.addLayout(p_lay)

        cb_style = "QCheckBox::indicator { width: 18px; height: 18px; } QCheckBox { color: #334155; }"
        self.auto_start_cb = QCheckBox("Windows açılışında otomatik çalıştır")
        self.auto_start_cb.setStyleSheet(cb_style); self.auto_start_cb.setChecked(self.settings.get("auto_start", False))
        self.empty_save_cb = QCheckBox("Anlam girilmeden kayda izin ver")
        self.empty_save_cb.setStyleSheet(cb_style); self.empty_save_cb.setChecked(self.settings.get("allow_empty_meaning", False))
        form_layout.addWidget(self.auto_start_cb); form_layout.addWidget(self.empty_save_cb)
        layout.addWidget(form_frame)

        btn_save = QPushButton("Ayarları Kaydet ve Uygula"); btn_save.setFixedHeight(45)
        btn_save.setStyleSheet("background: #10b981; color: white; font-weight: bold; border-radius: 8px;")
        btn_save.clicked.connect(self.save_settings); layout.addWidget(btn_save)
        
        footer = QLabel('<a href="https://arapca.muallimun.net/asistan_sozluk/" style="color: #1e3a8a; text-decoration: none; font-weight: bold;">Muallimun.Net Online Rehber</a>')
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter); footer.setOpenExternalLinks(True); layout.addWidget(footer)

    def browse_path(self):
        f, _ = QFileDialog.getSaveFileName(self, "Excel Dosyası Seç", self.path_input.text(), "Excel Dosyaları (*.xlsx)")
        if f: self.path_input.setText(f)

    def check_update(self, manual=False):
        try:
            ctx = ssl._create_unverified_context()
            req = urllib.request.Request(GITHUB_VERSION_URL + f"?t={int(time.time())}", headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx) as response:
                data = json.loads(response.read().decode('utf-8'))
                if str(data.get("version")).strip() != VERSION:
                    ans = QMessageBox.information(self, "Güncelleme", "Yeni sürüm mevcut. İndirmek ister misiniz?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    if ans == QMessageBox.StandardButton.Yes:
                        QDesktopServices.openUrl(QUrl(data.get("url") or "https://github.com/muallimun/muallim_mucem_asistan/releases"))
                elif manual:
                    QMessageBox.information(self, "Bilgi", "Uygulamanız güncel.")
        except Exception:
            if manual: QMessageBox.warning(self, "Hata", "Sunucuya bağlanılamadı.")

    def save_settings(self):
        self.settings.update({"hotkey": self.hotkey_input.text().lower().strip(), "excel_path": self.path_input.text().strip(), "auto_start": self.auto_start_cb.isChecked(), "allow_empty_meaning": self.empty_save_cb.isChecked()})
        self.manager.save(self.settings); self.settings_changed.emit(); self.accept()

# --- ANA SÖZLÜK PENCERESİ ---
class DictionaryWindow(QMainWindow):
    open_settings_signal = pyqtSignal()
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Window | Qt.WindowType.CustomizeWindowHint)
        self.setWindowTitle(f"Muallimun Sözlük v{VERSION}"); self.setMinimumSize(600, 500); self.resize(620, 720)
        self.setWindowIcon(QIcon(resource_path("muallim.ico")))
        self._old_pos = None

        container = QWidget(); container.setStyleSheet("QWidget { background: white; border: 1px solid #1e3a8a; }")
        layout = QVBoxLayout(container); layout.setContentsMargins(0, 0, 0, 0)

        self.header = QWidget(); self.header.setFixedHeight(45); self.header.setStyleSheet("background: #1e3a8a; border:none;")
        h_lay = QHBoxLayout(self.header)
        title = QLabel(f"MUALLİMUN SÖZLÜK v{VERSION}"); title.setStyleSheet("color: white; font-weight: bold; border:none;")
        
        btn_settings = QPushButton("⚙"); btn_settings.setFixedSize(30,30); btn_settings.setStyleSheet("background: #64748b; color: white; border-radius: 15px; border:none; font-size: 16px;")
        btn_settings.clicked.connect(self.open_settings_signal.emit)
        
        btn_close = QPushButton("✕"); btn_close.setFixedSize(30, 30); btn_close.setStyleSheet("background: #ef4444; color: white; border-radius: 15px; font-weight: bold; border:none;")
        btn_close.clicked.connect(self.hide)
        
        h_lay.addWidget(title); h_lay.addStretch(); h_lay.addWidget(btn_settings); h_lay.addWidget(btn_close)

        self.browser = QWebEngineView(); self.browser.setPage(SilentWebPage(self.browser))
        self.browser.loadFinished.connect(self.clean_web)

        footer = QWidget(); footer.setFixedHeight(230); footer.setStyleSheet("background: #f8fafc; border-top: 1px solid #e2e8f0; border:none;")
        f_lay = QVBoxLayout(footer)
        self.meaning_box = QTextEdit(); self.meaning_box.setPlaceholderText("Anlamı buraya yazın veya tarayıcıdan sürükleyin...")
        self.meaning_box.setStyleSheet("background: white; border: 1px solid #cbd5e1; border-radius: 6px; padding: 8px;")
        
        btn_row = QHBoxLayout()
        self.quick_cb = QCheckBox("Kelime anlamı olmadan deftere kaydet"); self.quick_cb.setStyleSheet("color: #334155;")
        self.btn_save = QPushButton("Excel'e Kaydet"); self.btn_save.setFixedHeight(35); self.btn_save.setStyleSheet("background: #f59e0b; color: white; font-weight: bold; border-radius: 6px;")
        self.btn_save.clicked.connect(self.save_to_excel); btn_row.addWidget(self.quick_cb); btn_row.addWidget(self.btn_save)
        
        f_lay.addWidget(QLabel("<b>💡 Anlam Girişi:</b>")); f_lay.addWidget(self.meaning_box); f_lay.addLayout(btn_row)

        bot_link = QHBoxLayout()
        link = QLabel('<a href="https://arapca.muallimun.net/asistan_sozluk/" style="color: #1e3a8a; text-decoration: none; font-weight: bold;">Muallimun.Net Online Rehber</a>')
        link.setOpenExternalLinks(True); bot_link.addWidget(link); bot_link.addStretch(); bot_link.addWidget(QLabel(f"v{VERSION}"))
        f_lay.addLayout(bot_link); layout.addWidget(self.header); layout.addWidget(self.browser); layout.addWidget(footer)
        self.setCentralWidget(container); self.grip = QSizeGrip(self); layout.addWidget(self.grip, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

    def clean_web(self):
        # --- REKLAM ENGELLEME VE SCROLL SORUNU DÜZELTİLDİ ---
        js = """
        var h=['header', 'footer', 'nav', '.header', '.ads', '.ad-unit', '.side-bar', '#top-nav', 'iframe', 'ins'];
        function hideAds() {
            h.forEach(s => document.querySelectorAll(s).forEach(n => n.style.display = 'none'));
        }
        hideAds(); // İlk yüklemede çalıştır
        window.scrollTo(0,0); // Sadece sayfa ilk açıldığında yukarı kaydır
        setInterval(hideAds, 3000); // 3 saniyede bir sadece reklamları gizle (Scroll yapmaz)
        """
        self.browser.page().runJavaScript(js)

    def search_word(self, word): self.current_word = word; self.meaning_box.clear(); self.browser.setUrl(QUrl(f"https://www.almaany.com/tr/dict/ar-tr/{word}")); self.showNormal(); self.show(); self.activateWindow()

    def save_to_excel(self):
        f = self.settings["excel_path"]; m = self.meaning_box.toPlainText().strip()
        if not m and not (self.settings.get("allow_empty_meaning") or self.quick_cb.isChecked()): QMessageBox.warning(self, "Hata", "Anlam girin."); return
        try:
            if os.path.exists(f):
                with open(f, "a+"): pass
            if not os.path.exists(f): wb = Workbook(); ws = wb.active; ws.append(["Tarih", "Kelime", "Anlam"])
            else: wb = load_workbook(f); ws = wb.active
            ws.append([time.strftime("%d.%m.%Y %H:%M"), getattr(self, "current_word", "---"), m or "Girilmedi"]); wb.save(f)
            self.btn_save.setText("Excel'e Kaydedildi ✅"); QTimer.singleShot(2000, lambda: self.btn_save.setText("Excel'e Kaydet")); self.meaning_box.clear()
        except PermissionError:
            QMessageBox.critical(self, "Excel Açık", "Lütfen açık olan Excel dosyasını kapatıp tekrar deneyin.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Hata: {str(e)}")

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton and self.header.underMouse(): self._old_pos = e.globalPosition().toPoint()
    def mouseMoveEvent(self, e):
        if self._old_pos is not None:
            delta = e.globalPosition().toPoint() - self._old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y()); self._old_pos = e.globalPosition().toPoint()
    def mouseReleaseEvent(self, e): self._old_pos = None

class AppController(QObject):
    search_signal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.manager = SettingsManager(); self.settings = self.manager.load()
        self.app = QApplication(sys.argv); self.app.setQuitOnLastWindowClosed(False)
        self.window = DictionaryWindow(self.settings); self.search_signal.connect(self.window.search_word)
        self.window.open_settings_signal.connect(self.open_settings)
        self.setup_tray(); self.refresh_listeners()
        QTimer.singleShot(3000, self.auto_update_check)
        self.tray.showMessage("Muallimun Asistan", "Arka planda hazır!", QSystemTrayIcon.MessageIcon.Information, 3000)

    def setup_tray(self):
        self.tray = QSystemTrayIcon(QIcon(resource_path("muallim.ico")))
        menu = QMenu(); set_act = QAction("Ayarlar", menu); set_act.triggered.connect(self.open_settings); menu.addAction(set_act); menu.addAction("Çıkış", self.shutdown); self.tray.setContextMenu(menu); self.tray.show()

    def open_settings(self): self.diag = SettingsDialog(self.manager, self.window); self.diag.settings_changed.connect(self.refresh_listeners); self.diag.exec()

    def auto_update_check(self):
        tmp_diag = SettingsDialog(self.manager, self.window); tmp_diag.check_update(manual=False)

    def refresh_listeners(self):
        self.settings = self.manager.load(); self.window.settings = self.settings
        try: keyboard.unhook_all_hotkeys()
        except: pass
        try:
            keyboard.add_hotkey(self.settings.get("hotkey", "ctrl+shift+z"), lambda: QTimer.singleShot(250, self.process), suppress=True)
            mouse.on_middle_click(lambda: QTimer.singleShot(250, self.process))
        except Exception:
            QMessageBox.warning(None, "Kısayol Çakışması", f"'{self.settings['hotkey']}' başka bir programca kullanılıyor.")

    def process(self):
        pyperclip.copy(""); keyboard.press_and_release('ctrl+c'); time.sleep(0.5)
        text = pyperclip.paste().strip()
        clean = re.sub(r'[^\u0600-\u06FF]', '', text)
        if clean: self.search_signal.emit(clean)

    def shutdown(self):
        try: keyboard.unhook_all_hotkeys()
        except: pass
        self.app.quit()

    def run(self): return self.app.exec()

# --- ANA ÇALIŞTIRMA BLOĞU ---
if __name__ == "__main__":
    if not is_admin():
        try: ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{os.path.abspath(sys.argv[0])}"', None, 1)
        except: pass
        sys.exit()

    # SINGLE INSTANCE LOCK
    kernel32 = ctypes.windll.kernel32; mutex_name = "Local\\MuallimunAsistan_Final_Deploy"
    mutex = kernel32.CreateMutexW(None, False, mutex_name)
    if kernel32.GetLastError() == 183:
        temp_app = QApplication(sys.argv)
        QMessageBox.warning(None, "Bilgi", "Muallimun Sözlük Asistanı zaten çalışıyor!")
        sys.exit()
    
    try:
        controller = AppController()
        sys.exit(controller.run())
    except Exception:
        log_file = os.path.join(get_app_data_path(), "error_log.txt")
        with open(log_file, "a", encoding="utf-8") as f: f.write(f"\n--- {time.ctime()} ---\n{traceback.format_exc()}")
        msg_app = QApplication.instance() or QApplication(sys.argv)
        QMessageBox.critical(None, "Kritik Hata", f"Hata günlüğü: {log_file}")