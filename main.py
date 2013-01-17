#!/usr/bin/env python

import os

import wsgiref.handlers
import apihandler
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template # TODO: Clean up template code, or use a more sensible template language (frak'ing django)

import model

RESERVED_PLACES = [
    'shazow', 'russeldsa', 'andreypetrov', # Emails
    'static', 'api', # Code
]

class MainHandler(webapp.RequestHandler):

    def get(self):
        places = model.Place.all().order("-time_created")[:5]
        images = [p.images.order("-time_created")[0] for p in places]
        c = {
            'images': images,
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, c))


class PlaceLatestHandler(webapp.RequestHandler):
    def get(self, place_name):
        place = model.Place.get_by_key_name(place_name)
        if not place:
            return self.error(404)

        image = place.images.order("-time_created")[0]

        self.response.headers['Content-Type'] = "image/jpeg"
        self.response.out.write(image.data)


class PlaceHandler(webapp.RequestHandler):
    def get(self, place_name):
        place = model.Place.get_by_key_name(place_name)
        if not place:
            return self.error(404)


        c = {
            'place': place,
            'images': place.images.order("-time_created")
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/place.html')
        self.response.out.write(template.render(path, c))
        

class ImageHandler(webapp.RequestHandler):
    def get(self, place_name, size, hash):
        ImageClass = model.IMAGE_SIZE_MAP.get(size)
        if not ImageClass:
            return self.error(403)

        image = ImageClass.get_by_key_name(hash)
        if not image:
            return self.error(404)

        self.response.headers['Content-Type'] = "image/jpeg"
        self.response.out.write(image.data)
        

class InstantlyAPI(apihandler.APIHandler):
    def api_upload(self):
        # Required
        upload = self.request.POST['upload']
        place = self.request.POST['place'].lower()
        filename, data = upload.filename, upload.value

        if place in RESERVED_PLACES:
            raise apihandler.APIException("This place name is reserved, try another.", 403)

        # Optional
        author = self.request.get('author')
        caption = self.request.get('caption')

        place = model.Place.get_or_insert(place)
        place.count += 1
        place.put()

        img = model.Image.create(place=place, data=data, filename=filename, author=author, caption=caption)
        
        return

    def api_get_latest(self):
        place_name = self.request.GET['place'].lower()
        
        place = model.Place.get_by_key_name(place_name)
        if not place:
            return self.error(404)

        images = []
        for i in place.images:
            images += [{
                'hash': i.hash,
                'author': i.author,
                'caption': i.caption,
                'thumbnail_path': i.get_thumbnail_path(),
                'path': i.get_path(),
            }]

        return {'images': images}


def main():
    application = webapp.WSGIApplication([
        ('/api', InstantlyAPI),
        ('/', MainHandler),
        ('/([\w\d\-_]+)[/]?', PlaceHandler),
        ('/([\w\d\-_]+)/latest', PlaceLatestHandler),
        ('/([\w\d\-_]+)/images/(\w)/([\w\d]+)\.jpg', ImageHandler),
    ], debug=True)

    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()
