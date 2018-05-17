import pathlib
import os
import hashlib
from PIL import Image
import imageviewer.settings


class IVImage:
    def __init__(self, filepath):
        self.path = pathlib.Path(filepath)
        self.filename = self.path.name
        self.db_entry = None
        self.thumbnail_md5 = None
        self.image_md5 = None

        self.get_db_ifexists()

        edited_root = str(self.path).replace(imageviewer.settings.ROOT_DIR, '').replace('\\', '').replace(' ',
                                                                                                          '_').lower()
        _tmp_thumb_path = pathlib.Path(imageviewer.settings.THUMBNAIL_DIR, edited_root)
        _tmp_thumb_path = os.path.splitext(str(_tmp_thumb_path))[0] + ".jpg"
        self.thumbnail_path = pathlib.Path(_tmp_thumb_path)
        # this tmp thing seems counter productive but couldn't come up with a less hacky way

        _tmp_file_path = os.path.splitext(str(self.path))[0]
        if pathlib.Path(_tmp_file_path + ".jpg").is_file() and pathlib.Path(_tmp_file_path + ".gif").is_file():
            # if there is gif and jpeg of same file name remove the jpg
            # This sometimes happens when downloading images improperly
            os.remove(_tmp_file_path + ".jpg")
            if self.filename.endswith("jpg"):
                self.path = None
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
                print("Could not link to database, ", str(self.path))
                self.path = None
                return

    def get_db_ifexists(self):
        pf_path = str(self.path).replace("\\\\", "/").replace("\\", "/")
        self.db_entry = next((item for item in imageviewer.settings.IMAGE_DB if item["image_path"] == pf_path),
                             None)
        if self.db_entry:
            if "image_md5" in self.db_entry:
                self.image_md5 = self.db_entry["image_md5"]
            if "thumbnail_md5" in self.db_entry:
                self.thumbnail_md5 = self.db_entry["thumbnail_md5"]

    def set_db(self):
        image_path = str(self.path).replace("\\\\", "/").replace("\\", "/")
        thumb_path = str(self.thumbnail_path).replace("\\\\", "/").replace("\\", "/")
        self.db_entry = next((item for item in imageviewer.settings.IMAGE_DB if item["image_md5"] == self.image_md5),
                             None)
        if not self.db_entry:
            print("Created new image json db entry")
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
