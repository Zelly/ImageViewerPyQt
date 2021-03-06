"""
Created on Sep 7, 2017

@author: Zelly
TODO: Add search function
"""
from PyQt5.QtWidgets import QGridLayout, QSystemTrayIcon, \
    qApp, QAction, QStyle, QMenu, QWidget, QScrollArea, QFrame
from PyQt5.QtCore import QEvent, Qt, QThread, pyqtSlot
import os
from imageviewer.ui.image import UiImageGroup
from imageviewer.image import IVImageWorker
import imageviewer.settings
import json
import time


# noinspection PyArgumentList,PyUnresolvedReferences
class UiMainWindow(QWidget):
    def __init__(self, app):
        QWidget.__init__(self)
        ms_start = int(round(time.time() * 1000))
        self.app = app
        self.setMinimumSize(1024, 512)  # TODO: Resizable
        self.setMaximumSize(1024, 768)
        self.setWindowTitle('ImageViewer')
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))  # TODO: Make icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))

        # Grid Layout & Scroll Area of Image center
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
        self.__threads = None
        self.__workers_done = 0
        self.__numthreads = os.cpu_count()

        # Show the window so we know something is happening
        #  in future a loading progress bar could be helpful
        ms_load_db_start = int(round(time.time() * 1000))
        self.load_db()
        ms_load_db_end = int(round(time.time() * 1000))
        self.load_images()
        ms_load_images_end = int(round(time.time() * 1000))
        # self.add_images()
        ms_end = int(round(time.time() * 1000))
        print("Time it took to load main window: ", ms_load_db_start - ms_start)
        print("time it took to load json db: ", ms_load_db_end - ms_load_db_start)
        print("time it took to load images: ", ms_load_images_end - ms_load_db_end)
        print("time it took to add images: ", ms_end - ms_load_images_end)
        print("time it took to load program: ", ms_end - ms_start)

    @staticmethod
    def load_db():
        db_path = imageviewer.settings.DATABASE_PATH
        if db_path.is_file():
            with db_path.open("r") as db_file:
                imageviewer.settings.IMAGE_DB = json.loads(db_file.read())
            if not imageviewer.settings.IMAGE_DB:
                imageviewer.settings.IMAGE_DB = []
            print("Loaded json image database")

    @staticmethod
    def save_db():
        db_path = imageviewer.settings.DATABASE_PATH
        if imageviewer.settings.IMAGE_DB:
            with db_path.open("w") as db_file:
                db_file.write(json.dumps(imageviewer.settings.IMAGE_DB))
            print("Wrote database")

    @staticmethod
    def dir_image_list(threadcount):
        filelist = []
        for root, _, files in os.walk(imageviewer.settings.ROOT_DIR):
            for filename in files:
                if not filename.endswith("jpg") and not filename.endswith("gif"):
                    continue  # Ignore webm files and any other garbage
                filelist.append(os.path.join(root, filename))
        return [filelist[i::threadcount] for i in range(threadcount)]

    def load_images(self):
        ilist = self.dir_image_list(self.__numthreads)
        self.__threads = []
        for x in range(self.__numthreads):
            worker = IVImageWorker(ilist[x])
            thread = QThread()
            worker.moveToThread(thread)
            self.__threads.append((thread, worker))
            worker.sig_done.connect(self.worker_done)
            thread.started.connect(worker.load_images)
            thread.start()

    @pyqtSlot()
    def worker_done(self):
        self.__workers_done += 1
        if self.__workers_done == self.__numthreads:
            print("Done threading")
            self.add_images()

    def add_images(self):
        images_per_row = 4  # limit to 4 images per row( currently at 256/256 image frames so ~1024px+ )
        row = col = 0
        print("Total images ito load: ", len(imageviewer.settings.IMAGES))
        for iv_image in imageviewer.settings.IMAGES:
            label = UiImageGroup(iv_image)
            self.scrollLayout.addWidget(label, row, col, 1, 1)
            col += 1
            if col % images_per_row == 0:
                row += 1
                col = 0
        self.scrollArea.setWidget(self.scrollContent)

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
