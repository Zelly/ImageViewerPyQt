"""
Created on Sep 7, 2017

@author: Zelly
TODO: Add search function
"""
from PyQt5.QtWidgets import QGridLayout, QSystemTrayIcon, \
    qApp, QAction, QStyle, QMenu, QWidget, QScrollArea, QFrame
from PyQt5.QtCore import QEvent, Qt
from PIL import Image
import os
from imageviewer.constant.config import ROOT_DIR, THUMBNAIL_DIR
from imageviewer.ui.image import UiImageLabel
import hashlib
import shutil


class UiMainWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setMinimumSize(1024, 512)  # TODO: Resizable
        self.setMaximumSize(1024, 800)
        self.setWindowTitle('ImageViewer')
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))  # TODO: Make icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))

        # Grid Layout & Scrpll Area of Image center
        self.gridlayout = QGridLayout(self)
        self.setLayout(self.gridlayout)
        self.scrollArea = QScrollArea(self)
        self.gridlayout.addWidget(self.scrollArea)
        # self.gridlayout.setContentsMargins(0, 0, 0, 0)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameStyle(QFrame.NoFrame)
        self.scrollContent = QWidget(self.scrollArea)
        self.scrollLayout = QGridLayout(self.scrollContent)
        self.scrollLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollContent.setLayout(self.scrollLayout)
        # self.scrollContent.setContentsMargins(0, 0, 0, 0)
        # self.setContentsMargins(0,0,0,0)

        self.setStyleSheet("background-color: white; border: 1px solid black;")

        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)  # TODO: Remove icon on exit this way
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
        self.load_thumbnails()
        self.scrollArea.setWidget(self.scrollContent)
        self.show()

    def close_all_popup(self):
        for imagelabel in self.scrollContent.children():
            if imagelabel is not None and isinstance(imagelabel, UiImageLabel):
                if imagelabel.popup is not None:
                    imagelabel.close_popup()

    def load_thumbnails(self):
        images_per_row = 7
        row = col = 0
        # count = 0
        for root, _, files in os.walk(ROOT_DIR):
            # print('root = ' + root)
            for filename in files:
                if not filename.endswith("jpg"):
                    continue  # Ignore webm files
                # if count > 7: return
                file_path = os.path.join(root, filename)
                edited_root = root.replace(ROOT_DIR, '').replace('\\', '').replace(' ', '_')
                thumbnail_name = filename.replace('\\', '_').replace(' ', '_')
                thumbnail_path = os.path.join(THUMBNAIL_DIR, (edited_root + thumbnail_name).lower())
                thumbnail_path = os.path.splitext(thumbnail_path)[0] + '.jpg'
                clean_name = os.path.splitext(file_path)[0]
                if os.path.isfile(clean_name + ".jpg") and os.path.isfile(clean_name + ".gif"):
                    os.remove(clean_name + ".jpg")
                    continue
                if not os.path.isfile(thumbnail_path):
                    self.create_thumbnail(file_path, thumbnail_path)
                label = UiImageLabel()
                label.parent = self
                label.thumbnail_path = thumbnail_path
                label.file_path = file_path
                label.load_thumbnail()
                self.scrollLayout.addWidget(label, row, col, 1, 1)
                col += 1
                # count +=1
                if col % images_per_row == 0:
                    row += 1
                    col = 0

    def create_thumbnail(self, image_filename, thumbnail_filename):
        if image_filename.endswith("jpg"):
            new_path = os.path.join(THUMBNAIL_DIR, hashlib.md5(open(image_filename, 'rb').read()).hexdigest() + "jpg")
            shutil.copy(image_filename, new_path)
            img = Image.open(new_path).convert("RGB")
            img_size = img.width, img.height
            img.thumbnail(img_size)
            img.save(image_filename, "JPEG")
            print("Moved original image to %s" % new_path)
        thumbnail_size = 128, 128
        print("Loading %s" % image_filename)
        new_thumbnail = Image.open(image_filename).convert("RGB")
        print("Creating thumbnail ...")
        new_thumbnail.resize(thumbnail_size)
        new_thumbnail.thumbnail(thumbnail_size)
        new_thumbnail.save(thumbnail_filename, "JPEG")
        print("New thumbnail created at %s" % thumbnail_filename)

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
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
