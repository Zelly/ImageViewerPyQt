from PyQt5.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QStyle, QGridLayout, QDesktopWidget
from PyQt5.QtCore import Qt, QByteArray, QMimeData, QUrl
from PyQt5.QtGui import QPixmap, QMovie, QDrag, QImage
from time import time

current_milli_time = lambda: int(round(time() * 1000))


class UI_ImagePopup(QLabel):
    """
    Plays the image of the parent "UI_ImageLabel" if it is a gif in a popup form
    Issues:
        2. Currently the popup can go off screen or overlap certain important ui elements.
        3. Currently does not show still images
    """

    def __init__(self, filepath):
        super(QLabel, self).__init__()
        self.setWindowTitle('ImagePreview')
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))  # TODO: Make icon
        self.setStyleSheet("QLabel {background-color: white;}")
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.X11BypassWindowManagerHint | Qt.WindowStaysOnTopHint)
        self.file = filepath
        self.parent = self
        self.sizeObject = QDesktopWidget().screenGeometry(-1)
        # print(" Screen size : "  + str(self.sizeObject.height()) + "x"  + str(self.sizeObject.width()))
        if self.file.endswith("gif"):
            self.gifview()
        else:
            self.imageview()
            # movie_screen.setPixmap(QPixmap(filepath))

    def imageview(self):
        pix = QPixmap(self.file)
        gridlayout = QGridLayout()
        image_holder = QLabel()
        # center the zoomed image on the thumb
        position = self.cursor().pos()
        width_space = self.sizeObject.width() - position.x()
        x = position.x()
        w = width_space - 100
        print(width_space, w)
        if width_space <= (self.sizeObject.width() / 2):
            # Position to right
            w = width_space - 100
            x = position.x() + 100
        image_holder.setPixmap(pix.scaled(200, 200, Qt.KeepAspectRatio))
        # image_holder.setPixmap(pix)
        gridlayout.addWidget(image_holder, 0, 1)
        self.setLayout(gridlayout)
        position.setX(x + 128)
        position.setY(position.y())
        self.move(position)

        # TODO: Need the image to show up ~160 px away from cursor if more room on right then show on right vice versa

    def gifview(self):
        movie_screen = QLabel()
        print("Creating movie %s" % self.file)
        movie = QMovie(self.file, QByteArray(), self)
        size = movie.scaledSize()
        self.setGeometry(200, 200, size.width(), size.height())
        # Make label fit the gif
        movie_screen.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        movie_screen.setAlignment(Qt.AlignCenter)
        # Create the layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(movie_screen)
        self.setLayout(main_layout)

        # center the zoomed image on the thumb
        position = self.cursor().pos()
        position.setX(position.x() + 50)
        position.setY(position.y())
        self.move(position)
        # The following is blackmagic copy pasted from the internet
        # FramelessWindowHint may not work on some window managers on Linux
        # so I force also the flag X11BypassWindowManagerHint
        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.X11BypassWindowManagerHint)

        movie.setCacheMode(QMovie.CacheAll)
        movie.setSpeed(100)
        movie_screen.setMovie(movie)
        movie.start()

    def enterEvent(self, e):
        self.close()


class UI_ImageLabel(QLabel):
    """
        Displays a thumbnail and saves the thumbnail and original image 
    paths for refernence in other objects.
    TODO: Add the ability to drag and drop the thumbnail to discord, only works with explorer atm
    """

    def __init__(self):
        QLabel.__init__(self)
        self.thumbnail_path = ""
        self.file_path = ""
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("QLabel { background-color: white; }")
        self.dragging = False
        self.timedelay = current_milli_time()
        self.popup = None

    def loadThumbnail(self):
        pixmap = QPixmap(self.thumbnail_path)

        self.setPixmap(pixmap)

    """ This widget displays an ImagePopup when the mouse enter its region """

    def enterEvent(self, event):
        if not self.dragging and current_milli_time() >= self.timedelay:
            self.parent.close_all_popup()
            self.timedelay = current_milli_time() + 250
            self.popup = UI_ImagePopup(self.file_path)
            self.popup.parent = self
            self.popup.show()
        event.accept()

    def close_popup(self):
        if self.popup is not None:
            self.popup.close()
            self.popup = None

    def leaveEvent(self, event):
        if self.popup:
            print("Destroy from parent")
            self.parent.close_all_popup()

    def mousePressEvent(self, e):
        if e.buttons() == Qt.LeftButton:
            self.dragging = True
            if self.popup:
                self.popup.close()
            url = None
            print("mouseMoveEvent")

            print("Loading orginal image from %s" % self.file_path)
            image = QImage()
            if not image.load(self.file_path):
                print("Failed to load original image")
            else:
                url = QUrl.fromLocalFile(self.file_path)
                print(url.isValid())
                print(url.isLocalFile())
                print("Image loaded")

            mime = QMimeData()
            mime.setUrls([url])
            # mime.setImageData(image)

            print("Setting image mimedata\n[%s]\nhasImage(%s)" % (mime.text(), str(mime.hasImage())))

            # mime.setText("test data")
            # print("test2")
            drag = QDrag(self)
            print("Drag created")
            drag.setMimeData(mime)
            print("Setting mimedata to drag")
            drag.setPixmap(self.pixmap())
            print("Setting pixmap to drag")
            # drag.setHotSpot(self.rect().topLeft())
            dropAction = drag.exec(Qt.CopyAction, Qt.CopyAction)
            print("Dropped %s" % str(dropAction))
            self.dragging = False
            e.accept()
