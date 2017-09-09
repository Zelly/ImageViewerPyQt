
from PyQt5.QtWidgets import QLabel, QSizePolicy,QVBoxLayout

from PyQt5.QtCore import Qt, QByteArray, QMimeData,QUrl
from PyQt5.QtGui import QPixmap, QMovie, QDrag, QImage

class UI_ImagePopup(QLabel):
    """
    Plays the image of the parent "UI_ImageLabel" if it is a gif in a popup form
    Issues:
        1. Cannot get the "leaveEvent" event from the parent to trigger. Thus 
    making it so you have to move your mouse into the popup and then move your 
    mouse out of the popup to make the popup trigger a leave event.
        2. Currently the popup can go off screen or overlap certain important ui elements.
        3. Currently does not show still images
    """
    def __init__(self, filepath):
        super(QLabel, self).__init__()
        movie = QMovie(filepath, QByteArray(), self)
        size = movie.scaledSize()
        self.setGeometry(200, 200, size.width(), size.height())
        self.setWindowTitle("title")

        movie_screen = QLabel()
        # Make label fit the gif
        movie_screen.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        movie_screen.setAlignment(Qt.AlignCenter)

        # Create the layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(movie_screen)
        
        self.setLayout(main_layout)
        
        # center the zoomed image on the thumb
        position = self.cursor().pos()
        position.setX(position.x() +50)
        position.setY(position.y())
        self.move(position)
        
        # The following is blackmagic copy pasted from the internet
        # FramelessWindowHint may not work on some window managers on Linux
        # so I force also the flag X11BypassWindowManagerHint
        self.setWindowFlags(Qt.Popup | Qt.WindowStaysOnTopHint 
                            | Qt.FramelessWindowHint 
                            | Qt.X11BypassWindowManagerHint)
        
        movie.setCacheMode(QMovie.CacheAll)
        movie.setSpeed(100)
        movie_screen.setMovie(movie)
        movie.start()
#    def leaveEvent(self,event):
#        self.destroy()
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
        self.setContentsMargins(0,0,0,0)
        self.setStyleSheet("QLabel { background-color: black; }")
    def loadThumbnail(self):
        pixmap = QPixmap(self.thumbnail_path)
        
        self.setPixmap(pixmap)
    """ This widget displays an ImagePopup when the mouse enter its region """
    def enterEvent(self, event):
        #if True: return# skip for now
        #event.accept()
        
        if not self.file_path.endswith("gif"):
            event.accept()
        else:
            self.p = UI_ImagePopup(self.file_path)
            self.p.show()
            event.accept()
    def leaveEvent(self,event):
        print("Destroy from parent")
        self.p.destroy() #TODO: Cannot get this triggered 
    def mousePressEvent(self, e):
        if e.buttons() == Qt.LeftButton:
            url = None
            print("mouseMoveEvent")
            #data = QByteArray()
            
            print("Loading orginal image from %s" % self.file_path)
            image = QImage()
            if not image.load(self.file_path):
                print("Failed to load original image")
            else:
                url = QUrl("file:///" + self.file_path)
                print(url.isValid())
                print(url.isLocalFile())
                print("Image loaded")
            mime = QMimeData()
            #mime.setData("image/gif",image.)
            mime.setImageData(image)
            mime.setUrls([url])
            print("Setting image mimedata\n[%s]\nhasImage(%s)" % (mime.text(), str(mime.hasImage())))

            
            #mime.setText("test data")
            #print("test2")
            drag = QDrag(self)
            print("Drag created")
            drag.setMimeData(mime)
            print("Setting mimedata to drag")
            drag.setPixmap(self.pixmap())
            print("Setting pixmap to drag")
            #drag.setHotSpot(self.rect().topLeft())
            dropAction = drag.exec(Qt.CopyAction, Qt.CopyAction)

            print("Dropped %s" % str(dropAction))
            print(Qt.CopyAction,Qt.MoveAction)
            
            #e.setDropAction(Qt.MoveAction)
    #def mousePressEvent(self, event):
    #    super().mousePressEvent(event)
    #dropAction = drag.exec_(Qt.MoveAction))