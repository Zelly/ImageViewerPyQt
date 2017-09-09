from sys import exit as sys_exit
from sys import argv as sys_argv
from PyQt5.QtWidgets import QApplication


from imageviewer.ui.mainwindow import Ui_MainWindow

if __name__ == '__main__':
    app = QApplication(sys_argv)
    ex = Ui_MainWindow()
    sys_exit(app.exec_())