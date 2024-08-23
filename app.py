import sys
import datetime
from PyQt5.QtCore import QUrl, Qt, QTranslator, QLocale, QLibraryInfo, QObject
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLineEdit, QPushButton, QVBoxLayout, QWidget,
    QTabWidget, QToolBar, QAction, QGraphicsDropShadowEffect, QFileDialog,
    QMessageBox, QMenuBar, QMenu, QTableWidget, QTableWidgetItem, QComboBox
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile
from PyQt5.QtGui import QColor, QIcon

class AdBlockPage(QWebEnginePage):
    def acceptNavigationRequest(self, url, _type, is_main_frame):
        if "ad" in url.toString():
            return False  # 阻止廣告頁面
        return super().acceptNavigationRequest(url, _type, is_main_frame)

class DownloadManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.downloads = []

    def add_download(self, download):
        self.downloads.append(download)
        download.downloadProgress.connect(self.update_progress)
        download.finished.connect(self.on_download_finished)

    def update_progress(self, bytes_received, bytes_total):
        progress = bytes_received / bytes_total * 100
        print(f"下載進度: {progress:.2f}%")

    def on_download_finished(self):
        print("下載完成！")

class HistoryManager:
    def __init__(self):
        self.history = []

    def add_history(self, url, title):
        self.history.append((url, title, datetime.datetime.now()))

    def get_history(self):
        return self.history

    def search_history(self, search_term):
        return [entry for entry in self.history if search_term.lower() in entry[1].lower() or search_term.lower() in entry[0].lower()]

class BookmarkManager:
    def __init__(self):
        self.bookmarks = []

    def add_bookmark(self, url, title):
        self.bookmarks.append((url, title))

    def remove_bookmark(self, url):
        self.bookmarks = [bm for bm in self.bookmarks if bm[0] != url]

    def get_bookmarks(self):
        return self.bookmarks

class PrismBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prism 瀏覽器")
        self.setGeometry(100, 100, 1200, 800)

        self.browser = QWebEngineView()
        self.browser.setPage(AdBlockPage(self.browser))
        self.browser.setUrl(QUrl("http://www.google.com"))

        self.history_manager = HistoryManager()
        self.download_manager = DownloadManager()
        self.bookmark_manager = BookmarkManager()

        self.browser.urlChanged.connect(self.update_url)
        self.browser.titleChanged.connect(self.update_title)
        self.browser.page().profile().downloadRequested.connect(self.download_manager.add_download)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        self.btn_reload = QPushButton("重新載入")
        self.btn_reload.clicked.connect(self.browser.reload)

        self.btn_back = QPushButton("返回")
        self.btn_back.clicked.connect(self.browser.back)

        self.btn_forward = QPushButton("前進")
        self.btn_forward.clicked.connect(self.browser.forward)

        self.btn_bookmark = QPushButton("加入書籤")
        self.btn_bookmark.clicked.connect(self.add_bookmark)

        self.btn_history = QPushButton("歷史記錄")
        self.btn_history.clicked.connect(self.show_history)

        self.btn_privacy = QPushButton("隱私模式")
        self.btn_privacy.clicked.connect(self.toggle_privacy_mode)

        self.search_engines = QComboBox()
        self.search_engines.addItem("Google", "https://www.google.com/search?q=")
        self.search_engines.addItem("Bing", "https://www.bing.com/search?q=")
        self.search_engines.addItem("DuckDuckGo", "https://www.duckduckgo.com/?q=")
        self.search_engines.currentIndexChanged.connect(self.change_search_engine)

        toolbar = QToolBar()
        toolbar.addWidget(self.btn_back)
        toolbar.addWidget(self.btn_forward)
        toolbar.addWidget(self.btn_reload)
        toolbar.addWidget(self.url_bar)
        toolbar.addWidget(self.search_engines)
        toolbar.addWidget(self.btn_bookmark)
        toolbar.addWidget(self.btn_history)
        toolbar.addWidget(self.btn_privacy)

        self.addToolBar(toolbar)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.browser, "新標籤頁")
        self.setCentralWidget(self.tabs)
        self.tabs.currentChanged.connect(self.on_tab_changed)

        self.apply_styles()
        self.is_privacy_mode = False
        self.current_search_engine = "https://www.google.com/search?q="

        # 菜單欄
        menubar = self.menuBar()
        file_menu = menubar.addMenu("檔案")
        history_action = QAction("歷史記錄", self)
        history_action.triggered.connect(self.show_history)
        file_menu.addAction(history_action)

        bookmarks_menu = menubar.addMenu("書籤")
        bookmarks_action = QAction("查看書籤", self)
        bookmarks_action.triggered.connect(self.show_bookmarks)
        bookmarks_menu.addAction(bookmarks_action)

        themes_menu = menubar.addMenu("主題")
        light_theme_action = QAction("亮色主題", self)
        light_theme_action.triggered.connect(lambda: self.set_theme("light"))
        dark_theme_action = QAction("暗色主題", self)
        dark_theme_action.triggered.connect(lambda: self.set_theme("dark"))
        themes_menu.addAction(light_theme_action)
        themes_menu.addAction(dark_theme_action)

    def apply_styles(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #5a5a5a;
                border-radius: 10px;
                font-size: 18px;
                background-color: #ffffff;
                color: #000000;
            }
            QPushButton {
                padding: 10px;
                font-size: 16px;
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 10px;
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.3);
            }
            QPushButton:hover {
                background-color: #005999;
            }
            QPushButton:pressed {
                background-color: #004466;
            }
            QTabWidget::pane {
                border: 1px solid #d0d0d0;
                border-radius: 10px;
                padding: 10px;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                border: 1px solid #d0d0d0;
                padding: 15px;
                border-radius: 10px;
                color: #000000;
            }
            QTabBar::tab:selected {
                background-color: #007acc;
                font-weight: bold;
                color: white;
            }
            QMenuBar {
                background-color: #ffffff;
                color: #000000;
            }
            QMenuBar::item:selected {
                background-color: #007acc;
                color: white;
            }
            QMenu {
                background-color: #f0f0f0;
                color: #000000;
            }
            QMenu::item:selected {
                background-color: #007acc;
                color: white;
            }
        """)

    def navigate_to_url(self):
        url = QUrl(self.url_bar.text())
        if url.scheme() == "":
            url.setScheme("http")
        self.browser.setUrl(url)

    def update_url(self, url):
        self.url_bar.setText(url.toString())
        self.history_manager.add_history(url.toString(), self.browser.title())

    def update_title(self, title):
        self.setWindowTitle(f"{title} - Prism 瀏覽器")

    def add_bookmark(self):
        url = self.browser.url().toString()
        title = self.browser.title()
        self.bookmark_manager.add_bookmark(url, title)
        QMessageBox.information(self, "書籤", "書籤已加入！")

    def show_history(self):
        history = self.history_manager.get_history()
        history_dialog = QTableWidget()
        history_dialog.setRowCount(len(history))
        history_dialog.setColumnCount(3)
        history_dialog.setHorizontalHeaderLabels(["網址", "標題", "時間"])

        for i, (url, title, timestamp) in enumerate(history):
            history_dialog.setItem(i, 0, QTableWidgetItem(url))
            history_dialog.setItem(i, 1, QTableWidgetItem(title))
            history_dialog.setItem(i, 2, QTableWidgetItem(timestamp.strftime("%Y-%m-%d %H:%M:%S")))

        history_dialog.setWindowTitle("歷史記錄")
        history_dialog.resize(800, 600)
        history_dialog.exec_()

    def show_bookmarks(self):
        bookmarks = self.bookmark_manager.get_bookmarks()
        bookmarks_dialog = QTableWidget()
        bookmarks_dialog.setRowCount(len(bookmarks))
        bookmarks_dialog.setColumnCount(2)
        bookmarks_dialog.setHorizontalHeaderLabels(["網址", "標題"])

        for i, (url, title) in enumerate(bookmarks):
            bookmarks_dialog.setItem(i, 0, QTableWidgetItem(url))
            bookmarks_dialog.setItem(i, 1, QTableWidgetItem(title))

        bookmarks_dialog.setWindowTitle("書籤")
        bookmarks_dialog.resize(800, 600)
        bookmarks_dialog.exec_()

    def toggle_privacy_mode(self):
        self.is_privacy_mode = not self.is_privacy_mode
        if self.is_privacy_mode:
            QMessageBox.information(self, "隱私模式", "已啟用隱私模式。")
            self.browser.page().setProfile(QWebEngineProfile("IncognitoProfile", self.browser))
        else:
            QMessageBox.information(self, "隱私模式", "已停用隱私模式。")
            self.browser.page().setProfile(QWebEngineProfile.defaultProfile())

    def change_search_engine(self):
        current_index = self.search_engines.currentIndex()
        self.current_search_engine = self.search_engines.itemData(current_index)

    def on_tab_changed(self, index):
        if index == self.tabs.count() - 1:
            self.tabs.widget(index).setPage(AdBlockPage(self.tabs.widget(index)))
            self.tabs.widget(index).setUrl(QUrl("http://www.google.com"))

    def set_theme(self, theme):
        if theme == "light":
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f0f0f0;
                }
                QLineEdit {
                    background-color: #ffffff;
                    color: #000000;
                }
                QPushButton {
                    background-color: #007acc;
                    color: white;
                }
                QTabBar::tab:selected {
                    background-color: #007acc;
                    color: white;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1e1e1e;
                }
                QLineEdit {
                    background-color: #2e2e2e;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #333333;
                    color: white;
                }
                QTabBar::tab:selected {
                    background-color: #333333;
                    color: white;
                }
            """)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = PrismBrowser()
    window.show()
    sys.exit(app.exec_())
