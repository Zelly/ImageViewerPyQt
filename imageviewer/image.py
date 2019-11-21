import os
import hashlib
from PIL import Image
import imageviewer.settings
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from pathlib import Path


class IVImageWorker(QObject):
    sig_done = pyqtSignal()

    def __init__(self, image_list: list):
        super().__init__()
        if not image_list:
            return
        self.images = image_list

    @pyqtSlot()
    def load_images(self):
        for filepath in self.images:
            iv_image = IVImage(filepath)
            if iv_image.path:
                # error happened
                imageviewer.settings.IMAGES.append(iv_image)
                # qApp.processEvents()
        self.sig_done.emit()


class IVImage:
    def __init__(self, filepath):
        self.path = Path(filepath).resolve()
        if not self.path:
            print(f"imageviewer.image.IVImage Error resolving {str(filepath)} as file path")
            return
        self.filename = self.path.name
        self.db_entry = None
        self.thumbnail_md5 = None
        self.image_md5 = None
        self.get_db_if_exists()
        edited_root = str(self.path).replace(str(imageviewer.settings.ROOT_DIR), '').replace("\\", "_").replace(" ",
                                                                                                                "_").lower()
        self.thumbnail_path = Path(imageviewer.settings.THUMBNAIL_DIR, edited_root).with_suffix(".jpg").resolve()
        if not self.thumbnail_path:
            print(
                f"imageviewer.image.IVImage Error resolving {str(imageviewer.settings.THUMBNAIL_DIR)} + {str(edited_root)} as thumbnail path")
            return
        if self.path.with_suffix(".jpg").is_file() and self.path.with_suffix(".gif").is_file():
            print("JPG and GIF exist, deleting jpg...")
            # if there is gif and jpeg of same file name remove the jpg
            # This sometimes happens when downloading images improperly
            self.path.with_suffix(".jpg").unlink()
            if self.path.suffix == ".jpg":
                self.path = None
                print(f"imageviewer.image.IVImage duplicate JPG exiting creation")
                return
        """
        # Unecessary memory usage
        self.image = QImage(str(self.path))
        if not self.image:
            print("QImage failed to load: ", str(self.path))
            self.path = None
            return
        # not 100% sure but I originally converted old jpg's to a standard jpg with pillow
        # I am unsure if this is required anymore(was trying to debug why an image wasn't displaying before)

        self.thumbnail = QPixmap(str(self.thumbnail_path))
        if not self.thumbnail:
            print("QPixmap for thumbnail did not load", str(self.thumbnail_path))
            self.path = None
            return"""
        if not self.thumbnail_path.is_file():
            self.create_thumbnail()
        if not self.image_md5:
            self.image_md5 = hashlib.md5(open(str(self.path), 'rb').read()).hexdigest()
        if not self.thumbnail_md5:
            self.thumbnail_md5 = hashlib.md5(open(str(self.thumbnail_path), 'rb').read()).hexdigest()

        if not self.db_entry:
            self.set_db()
            if not self.db_entry:
                print(f"Could not link to database, {str(self.path)}")
                self.path = None
                return

    def get_db_if_exists(self):
        self.db_entry = next((item for item in imageviewer.settings.IMAGE_DB if item["image_path"] == str(self.path)),
                             None)
        # print(str(imageviewer.settings.IMAGE_DB))
        if self.db_entry:
            if "image_md5" in self.db_entry:
                self.image_md5 = self.db_entry["image_md5"]
            if "thumbnail_md5" in self.db_entry:
                self.thumbnail_md5 = self.db_entry["thumbnail_md5"]

    def set_db(self):
        image_path = str(self.path)
        thumb_path = str(self.thumbnail_path)
        self.db_entry = next((item for item in imageviewer.settings.IMAGE_DB if item["image_md5"] == self.image_md5),
                             None)
        if not self.db_entry:
            print("Created new image json db entry", image_path)
            new_entry = {
                "image_md5": self.image_md5,
                "thumbnail_md5": self.thumbnail_md5,
                "image_path": image_path,
                "thumbnail_path": thumb_path,
                "tags": [],
            }
            imageviewer.settings.IMAGE_DB.append(new_entry)
            self.db_entry = next(
                (item for item in imageviewer.settings.IMAGE_DB if item["image_md5"] == self.image_md5),
                None)

    def create_thumbnail(self):
        thumbnail_size = 96, 96
        new_thumbnail = Image.open(str(self.path)).convert("RGB")
        new_thumbnail.resize(thumbnail_size)
        new_thumbnail.thumbnail(thumbnail_size)
        new_thumbnail.save(str(self.thumbnail_path), "JPEG")
        print("New thumbnail created at ", str(self.thumbnail_path))
