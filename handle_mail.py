import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.api import images
from google.appengine.ext import db

import model

import logging

log = logging.getLogger(__name__)

def listify(o):
    if isinstance(o, list):
        return o
    return [o]

def email_to_place(to):
    return to.split('@', 1)[0].split('"', 1)[1]

class MailHandler(InboundMailHandler):
    def _post_message(self, place_name, message):
        place = model.Place.get_or_insert(place_name)
        place.put()

        attachments = listify(message.attachments)

        for attachment in attachments:
            author = message.sender
            caption = message.subject if hasattr(message, 'subject') else ''
            filename = attachment[0]
            attachment_data = attachment[1].payload.decode(attachment[1].encoding) 
            data = images.im_feeling_lucky(attachment_data, output_encoding=images.JPEG)

            log.debug("Processing attachment: %s (size: %d -> %d)" % (attachment[0], len(attachment_data), len(data)))
            img = model.Image.create(place=place, data=db.Blob(data), author=author, filename=filename, caption=caption)
            place.count += 1

        place.put()

    def receive(self, message):
        log.info("Received message from [%s] to [%s]" % (message.sender, message.to))

        to = listify(message.to)

        for to_item in to:
            place = email_to_place(to_item)
            self._post_message(place, message)

def main():
    application = webapp.WSGIApplication([
        MailHandler.mapping(),
    ])
    
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()
