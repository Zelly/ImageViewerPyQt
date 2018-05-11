from sys import exit as sys_exit
from sys import argv as sys_argv
from PyQt5.QtWidgets import QApplication


from imageviewer.ui.mainwindow import UiMainWindow

if __name__ == '__main__':
    app = QApplication(sys_argv)
    ex = UiMainWindow()
    sys_exit(app.exec_())
