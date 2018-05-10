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
from imageviewer.ui.image import UI_ImageLabel
import hashlib
import shutil


class Ui_MainWindow(QWidget):
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
        self.tray_icon.activated.connect(self.onTrayIconActivated)
        self.tray_icon.show()
        self.loadThumbnails()
        self.scrollArea.setWidget(self.scrollContent)
        self.show()

    def close_all_popup(self):
        for imagelabel in self.scrollContent.children():
            if imagelabel is not None and isinstance(imagelabel, UI_ImageLabel):
                if imagelabel.popup is not None:
                    imagelabel.close_popup()

    def loadThumbnails(self):
        imagesPerRow = 7
        row = col = 0
        # count = 0
        for root, _, files in os.walk(ROOT_DIR):
            # print('root = ' + root)
            for filename in files:
                if not filename.endswith("jpg"): continue  # Ignore webm files
                # if count > 7: return
                file_path = os.path.join(root, filename)
                edited_root = root.replace(ROOT_DIR, '').replace('\\', '').replace(' ', '_')
                thumbnail_name = filename.replace('\\', '_').replace(' ', '_')
                thumbnail_path = os.path.join(THUMBNAIL_DIR, (edited_root + thumbnail_name).lower())
                thumbnail_path = os.path.splitext(thumbnail_path)[0] + '.jpg'
                cleanname = os.path.splitext(file_path)[0]
                if os.path.isfile(cleanname + ".jpg") and os.path.isfile(cleanname + ".gif"):
                    os.remove(cleanname + ".jpg")
                    continue
                if not os.path.isfile(thumbnail_path):
                    self.createThumbnail(file_path, thumbnail_path)
                label = UI_ImageLabel()
                label.parent = self
                label.thumbnail_path = thumbnail_path
                label.file_path = file_path
                label.loadThumbnail()
                self.scrollLayout.addWidget(label, row, col, 1, 1)
                col += 1
                # count +=1
                if col % imagesPerRow == 0:
                    row += 1
                    col = 0

    def createThumbnail(self, imagefilename, thumbnailfilename):
        if imagefilename.endswith("jpg"):
            newpath = os.path.join(THUMBNAIL_DIR, hashlib.md5(open(imagefilename, 'rb').read()).hexdigest() + "jpg")
            shutil.copy(imagefilename, newpath)
            img = Image.open(newpath).convert("RGB")
            img_size = img.width, img.height
            img.thumbnail(img_size)
            img.save(imagefilename, "JPEG")
            print("Moved original image to %s" % newpath)
        thumbnail_size = 128, 128
        print("Loading %s" % imagefilename)
        new_thumbnail = Image.open(imagefilename).convert("RGB")
        print("Creating thumbnail ...")
        new_thumbnail.resize(thumbnail_size)
        new_thumbnail.thumbnail(thumbnail_size)
        new_thumbnail.save(thumbnailfilename, "JPEG")
        print("New thumbnail created at %s" % thumbnailfilename)

    def onTrayIconActivated(self, reason):
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
