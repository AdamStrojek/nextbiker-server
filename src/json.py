"""
JSON-RPC module, written to be used with GAE.

tyrion-mx @ chat.freenode.net
"""
## You can use simplejson, that is bundled with django, instead of jsonparser.
# from django.utils import simplejson as parser
import jsonparser as parser

## for simplejson uncomment this:
# JSONParseError = ValueError
JSONParseError = parser.JSONDecodeException


class JSONRPCError(Exception):
    """
    A JSONRPCError is an exception that can be sent over the wire, thus can be
    encoded as a json-rpc error response. You should subclass it to implement
    your json-rpc errors, or use it directly.
    """

    def __init__(self, message, code=0, httpStatus=500):
        self.message = message
        self.code = code
        self.httpStatus = httpStatus

from google.appengine.ext import webapp

class JSONRPCHandler(webapp.RequestHandler):
    
    def post(self):
        """
        @ivar data: a plain json-rpc request.

        This method will parse the request, execute the requested method if
        present, and return the encoded response.
        Methods should be implemented by subclassing this class and adding one
        or more methods with the suffix json_ (so the request can access only
        secure flagged code). If your method raises an
        Exception it will not be caught, unless it is an instance of
        JSONRPCError. JSONRPCError exceptions will be caught and encoded as an
        error response.

        @returns: an ecoded, ready to be sent, json-rpc response.
        """
        id = 0
        try:
            methodName, params, id = self._decodeRequest(self.request.body)
            try:
                method = getattr(self, 'json_%s' % methodName)
            except AttributeError:
                status = 500
                raise JSONRPCError('Procedure Not Found', httpStatus=status)

            result = method(**params)
            error = None
            httpStatus = 200
        except JSONRPCError, e:
            result = None
            error = {'name': e.__class__.__name__,
                     'message': e.message,
                     'code': e.code}
            httpStatus = e.httpStatus
        
        self.response.headers['Content-Type'] = 'application/json'
        self.response.set_status(httpStatus)
        self.response.out.write(self._encodeResponse(result, error, id))
        
    def _decodeRequest(self, data):
        try:
            data = parser.loads(data)
            for var in ('method', 'params', 'id'):
                yield data[var]
        except JSONParseError:
            raise JSONRPCError('Parse Error', httpStatus=500)
        except KeyError:
            raise JSONRPCError('Bad Call', httpStatus=500)

    def _encodeResponse(self, result, error, id):
        response = {'result': result, 'error': error, 'id': id}
        return parser.dumps(response)
