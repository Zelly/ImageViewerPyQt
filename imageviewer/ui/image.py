from PyQt5.QtWidgets import QLabel, QApplication
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QMovie
import subprocess
from imageviewer.image import IVImage
import imageviewer.settings


# noinspection PyArgumentList
class UiImageGroup(QLabel):
    """
    :type iv_image: IVImage
    :type self.movie: QMovie
    """

    def __init__(self, iv_image):
        super().__init__()
        if not iv_image:
            return
        self.iv_image = iv_image
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("UiImageGroup { background-color: white; }")
        self.setPixmap(self.iv_image.thumbnail)
        self.movie = None

    def gif(self):
        if self.movie:
            # Movie is already created
            self.movie.start()
            return
        print("Creating movie for", str(self.iv_image.path))
        self.movie = QMovie(str(self.iv_image.path))
        if self.iv_image.image.height() > imageviewer.settings.IMAGE_HEIGHT or self.iv_image.image.width() > \
                imageviewer.settings.IMAGE_WIDTH:
            # scale the movie if it doesn't fit in the frame
            # the frame is big enough we don't need the gif at full size to see what is going on
            image2 = self.iv_image.image.scaled(imageviewer.settings.IMAGE_WIDTH, imageviewer.settings.IMAGE_HEIGHT,
                                                Qt.KeepAspectRatio)
            size = QSize()
            size.setHeight(image2.height())
            size.setWidth(image2.width())
            self.movie.setScaledSize(size)
            print("Scaled movie size")
        self.setMovie(self.movie)
        self.movie.start()

    def open_explorer(self):
        print(r'explorer /select,"' + str(self.iv_image.path) + '"')
        subprocess.Popen(r'explorer /select,"' + str(self.iv_image.path) + '"')

    def enterEvent(self, event):
        if self.iv_image.filename.endswith(".gif"):
            self.gif()
        QApplication.setOverrideCursor(Qt.PointingHandCursor)
        event.accept()

    def leaveEvent(self, event):
        if self.movie:
            self.movie.jumpToFrame(0)  # Reset gif?
            self.movie.stop()
        QApplication.restoreOverrideCursor()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.open_explorer()
            event.accept()
