"""
Created on Sep 7, 2017

@author: Zelly
TODO: Add search function
"""
from PyQt5.QtWidgets import QGridLayout, QSystemTrayIcon, \
    qApp, QAction, QStyle, QMenu, QWidget, QScrollArea, QFrame
from PyQt5.QtCore import QEvent, Qt
import os
from imageviewer.ui.image import UiImageGroup
from imageviewer.image import IVImage
import imageviewer.settings
import pathlib
import json


# noinspection PyArgumentList,PyUnresolvedReferences
class UiMainWindow(QWidget):
    def __init__(self, app):
        QWidget.__init__(self)
        self.app = app
        self.setMinimumSize(1100, 512)  # TODO: Resizable
        self.setMaximumSize(1100, 1024)
        self.setWindowTitle('ImageViewer')
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))  # TODO: Make icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))

        # Grid Layout & Scrpll Area of Image center
        self.gridlayout = QGridLayout(self)
        self.setLayout(self.gridlayout)
        self.scrollArea = QScrollArea(self)
        self.gridlayout.addWidget(self.scrollArea)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameStyle(QFrame.NoFrame)
        self.scrollContent = QWidget(self.scrollArea)
        self.scrollLayout = QGridLayout(self.scrollContent)
        self.scrollLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollContent.setLayout(self.scrollLayout)

        self.setStyleSheet("background-color: white; border: 1px solid black;")

        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)
        hide_action = QAction("Hide", self)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(qApp.quit)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()
        self.show()
        # Show the window so we know something is happening
        #  in future a loading progress bar could be helpful
        self.load_db()
        self.load_images()

    @staticmethod
    def load_db():
        db_path = pathlib.Path(imageviewer.settings.DATABASE_PATH)
        if db_path.is_file():
            with db_path.open("r") as db_file:
                imageviewer.settings.IMAGE_DB = json.loads(db_file.read())
            if not imageviewer.settings.IMAGE_DB:
                imageviewer.settings.IMAGE_DB = []
            print("Loaded json image database")

    @staticmethod
    def save_db():
        db_path = pathlib.Path(imageviewer.settings.DATABASE_PATH)
        if imageviewer.settings.IMAGE_DB:
            with db_path.open("w") as db_file:
                db_file.write(json.dumps(imageviewer.settings.IMAGE_DB))
            print("Wrote database")

    def load_images(self):
        images_per_row = 4  # limit to 4 images per row( currently at 256/256 image frames so ~1024px+ )
        row = col = 0
        for root, _, files in os.walk(imageviewer.settings.ROOT_DIR):
            for filename in files:
                if not filename.endswith("jpg") and not filename.endswith("gif"):
                    continue  # Ignore webm files and any other garbage
                iv_image = IVImage(os.path.join(root, filename))
                if not iv_image.path:
                    # error happened
                    continue
                label = UiImageGroup(iv_image)
                self.scrollLayout.addWidget(label, row, col, 1, 1)
                col += 1
                if col % images_per_row == 0:
                    row += 1
                    col = 0
        self.scrollArea.setWidget(self.scrollContent)
        self.show()

    def on_tray_icon_activated(self, reason):
        print(reason)
        if reason == QSystemTrayIcon.Trigger:
            self.show()
            self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
            self.activateWindow()

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                event.ignore()
                self.hide()

    # Override closeEvent, to intercept the window closing event
    def closeEvent(self, event):
        self.tray_icon.hide()  # Hide the icon before closing
        self.save_db()
