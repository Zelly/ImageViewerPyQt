from sys import exit as sys_exit
from sys import argv as sys_argv
from PyQt5.QtWidgets import QApplication
from imageviewer.ui.mainwindow import UiMainWindow

"""
todo: add threading for the thumbnail creation :(
todo: load only a limited amount of images at a time currently at 1gb ram just by loaidng the thumbnails :P
todo: Tag editing/searching/viewing
todo: better method of accessing the image to drag to discord... since discord is a bitch
todo: add a better style :(, seriously am terrible at that stuff..
"""

if __name__ == '__main__':
    app = QApplication(sys_argv)
    ex = UiMainWindow(app)
    sys_exit(app.exec_())
