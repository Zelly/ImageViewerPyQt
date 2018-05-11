from PyQt5.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QStyle, QGridLayout, QDesktopWidget, QApplication
from PyQt5.QtCore import Qt, QByteArray, QMimeData, QUrl, QPoint, QTime, QBuffer, QIODevice
from PyQt5.QtGui import QPixmap, QMovie, QDrag, QImage
from time import time


def current_milliseconds():
    return int(round(time()*1000))


class UiImagePopup(QLabel):
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
        #print(width_space, w)
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


class UiImageLabel(QLabel):
    """
        Displays a thumbnail and saves the thumbnail and original image 
    paths for refernence in other objects.
    TODO: Add the ability to drag and drop the thumbnail to discord, only works with explorer atm
    """

    def __init__(self):
        QLabel.__init__(self)
        self.setText("This is a test")
        self.thumbnail_path = ""
        self.file_path = ""
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("QLabel { background-color: white; }")
        self.dragging = False
        self.timedelay = current_milliseconds()
        self.popup = None
        self.mouse_down = False  # has a left-click happened yet?
        self.mouse_posn = QPoint()  # if so, this was where...
        self.mouse_time = QTime()  # ...and this was when.

    def load_thumbnail(self):
        pixmap = QPixmap(self.thumbnail_path)

        self.setPixmap(pixmap)

    """ This widget displays an ImagePopup when the mouse enter its region """

    def enterEvent(self, event):
        if not self.dragging and current_milliseconds() >= self.timedelay:
            self.parent.close_all_popup()
            self.timedelay = current_milliseconds() + 250
            self.popup = UiImagePopup(self.file_path)
            self.popup.parent = self
            self.popup.show()
        event.accept()

    def close_popup(self):
        if self.popup is not None:
            self.popup.close()
            self.popup = None

    def leaveEvent(self, event):
        if self.popup:
            #print("Destroy from parent")
            self.parent.close_all_popup()

    def do_drag(self, actions):
        # Create the QDrag object
        dragster = QDrag(self)
        # Make a scaled pixmap of our widget to put under the cursor.
        thumb = self.grab().scaledToHeight(50)
        dragster.setPixmap(thumb)
        dragster.setHotSpot(QPoint(thumb.width()/2, thumb.height()/2))
        # Create some data to be dragged and load it in the dragster.
        md = QMimeData()
        image = QImage()
        if not image.load(self.file_path):
            print("do_drag: Failed to load original image")
        else:
            url = QUrl.fromLocalFile(self.file_path)
            print("do_drag: Image loaded, isValid()", url.isValid(), " isLocalFile()", url.isLocalFile())
        md.setImageData(image)
        md.setUrls([url])
        print("Dragable formats:", md.formats())
        dragster.setMimeData(md)
        # Initiate the drag, which really is a form of modal dialog.
        # Result is supposed to be the action performed at the drop.
        act = dragster.exec_(actions)
        defact = dragster.defaultAction()
        # Display the results of the drag.
        targ = dragster.target()  # s.b. the widget that received the drop
        src = dragster.source()  # s.b. this very widget
        print('Dragable: exec returns', int(act), 'default', int(defact), 'target', type(targ), 'source', type(src))
        return

    def mouseMoveEvent(self, event):
        if self.mouse_down:
            # Mouse left-clicked and is now moving. Is this the start of a
            # drag? Note time since the click and approximate distance moved
            # since the click and test against the app's standard.
            t = self.mouse_time.elapsed()
            d = (event.pos() - self.mouse_posn).manhattanLength()
            if t >= QApplication.startDragTime() or d >= QApplication.startDragDistance():
                # Yes, a proper drag is indicated. Commence dragging.
                self.do_drag(Qt.CopyAction)
                event.accept()
                return
        # Move does not (yet) constitute a drag, ignore it.
        event.ignore()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_down = True  # we are left-clicked-upon
            self.mouse_posn = event.pos()  # here and...
            self.mouse_time.start()  # ...now
        event.ignore()
        super().mousePressEvent(event)  # pass it on up
        """
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
            drop_action = drag.exec(Qt.CopyAction, Qt.CopyAction)
            print("Dropped %s" % str(drop_action))
            self.dragging = False
            e.accept()

            QImage image;
        QByteArray ba;
        QBuffer buffer(&ba);
        buffer.open(QIODevice::WriteOnly);
        image.save(&buffer, "PNG"); // writes image into ba in PNG format

        ba = QByteArray()
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, "PNG")
        buffer.close()
        md.setData("image/png", ba)"""
