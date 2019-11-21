from sys import exit as sys_exit
from sys import argv as sys_argv
from PyQt5.QtWidgets import QApplication
from imageviewer.ui.mainwindow import UiMainWindow


def main():
    app = QApplication(sys_argv)
    ex = UiMainWindow(app)
    sys_exit(app.exec_())


if __name__ == '__main__':
    main()
