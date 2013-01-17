# model.py - Container for model objects

import hashlib

from google.appengine.ext import db
from google.appengine.api import images

THUMBNAIL_HEIGHT=45
THUMBNAIL_WIDTH=0 # Proportional to height

class Place(db.Model):
    count = db.IntegerProperty(default=0)

    time_created = db.DateTimeProperty(auto_now_add=True)
    time_updated = db.DateTimeProperty(auto_now=True, auto_now_add=True)

    @property
    def name(self):
        return self.key().name()

    def get_images(self):
        pass

class ImageFull(db.Model):
    data = db.BlobProperty(required=True)
    time_created = db.DateTimeProperty(auto_now_add=True)

class ImageThumbnail(db.Model):
    data = db.BlobProperty(required=True)
    time_created = db.DateTimeProperty(auto_now_add=True)

IMAGE_SIZE_MAP = {
    'o': ImageFull,
    't': ImageThumbnail,
}

class Image(db.Model):
    place = db.ReferenceProperty(Place, collection_name="images")
    hash = db.ByteStringProperty(required=True)

    author = db.StringProperty()
    caption = db.StringProperty()

    filename = db.StringProperty()
    image_full = db.ReferenceProperty(ImageFull, collection_name="images")
    image_thumbnail = db.ReferenceProperty(ImageThumbnail, collection_name="images")

    time_created = db.DateTimeProperty(auto_now_add=True)

    @staticmethod
    def create(place, data, **kw):
        "Create and commit the Image and the subsequent data objects"
        hash = hashlib.sha1(data).hexdigest()

        full = ImageFull.get_or_insert(hash, data=images.im_feeling_lucky(data, output_encoding=images.JPEG))
        full.put()
        
        thumb = ImageThumbnail.get_or_insert(hash, data=images.resize(full.data, THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT, output_encoding=images.JPEG))
        thumb.put()

        img = Image(place=place.key(), hash=hash, image_full=full, image_thumbnail=thumb, **kw)
        img.put()

        return img

    def get_path(self):
        return "/%s/images/o/%s.jpg" % (self.place.name, self.hash)

    def get_thumbnail_path(self):
        return "/%s/images/t/%s.jpg" % (self.place.name, self.hash)
