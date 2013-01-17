from django.utils import simplejson

from google.appengine.ext.webapp import RequestHandler

import logging
log = logging.getLogger(__name__)

class APIException(Exception):
    def __init__(self, msg, code=400):
        self.msg = msg
        self.code = 400

class APIHandler(RequestHandler):
    def _index(self):
        function = self.request.params.get('function')
        if not function:
            raise APIException("Missing parameter: function")

        fn = getattr(self, "api_%s" % function, None)
        if not fn:
            raise APIException("Invalid function: %s" % function)

        try:
            r = fn()
        except KeyError, e:
            log.debug(e)
            raise APIException("Function missing required parameter: %s" % e.args[0])

        return {'returned': r}

    def get(self):
        response = {'messages': [], 'status': 'ok', 'code': 200, 'returned': []}
        response_template = "%s"

        callback = self.request.params.get('callback')
        if callback:
            response_template = "%s(%%s);" % callback

        try:
            r = self._index()
        except APIException, e:
            self.response.set_status(e.code)
            r = {'messages': [e.msg], 'status': 'error', 'code': e.code}

        response.update(r)
        self.response.headers['Content-Type'] = "text/javascript; charset=utf-8"
        self.response.out.write(response_template % simplejson.dumps(response))

    def post(self):
        return self.get()

