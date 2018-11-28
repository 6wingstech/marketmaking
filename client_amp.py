import urllib
import requests
from account_functions import ampRestEndpoints
from BoundMethods import BoundInstanceMethods

class AmpClient(object):

    def __init__(self,  _user_address, _private_key=None, web3_endpoint=None, _host = "52.78.227.253", _port = "8081", _rest_protocol = "http", _ws_protocol = "ws"):
        """
        All calls return as Python Objects
        """
        self.host = str(_host) or str(HOST)
        self.port = str(_port) or str(PORT)

        self.rest_protocol = _rest_protocol + "://"
        self.rest_endpoint = self.rest_protocol + _host + ":" + self.port

        self.ws_protocol = _ws_protocol + "://"
        self.ws_endpoint = self.ws_protocol + _host + ":" + self.port + "/socket"

        self.rest_methods = ampRestEndpoints(self.rest_endpoint, _user_address)
        self.ws_subscriber = None

        self.methods = BoundInstanceMethods(self.rest_methods)

    def __getattr__(self, _attr):
        return getattr(self.methods, _attr)
