'''
Created on 06-03-2012

@author: zwierzak
'''

import Cookie
from google.appengine.api import urlfetch

from urlparse import urljoin
from urllib import urlencode

import logging

class URLOpener:
    def __init__(self):
        self.cookies = {}
    
    def open(self, url, data = None):
        logging.info('Fetching URL: "%s"' % url)
        if data is None:
            method = urlfetch.GET
        else:
            method = urlfetch.POST
            data = urlencode(data)
        
        while True:
            response = urlfetch.fetch(url=url, 
                payload=data,
                method=method,
                headers=self._getHeaders(self.cookies),
                allow_truncated=False,
                follow_redirects=False,
                deadline=10
                )
            data = None # Next request will be a get, so no need to send the data again. 
            method = urlfetch.GET
            cookies = Cookie.SimpleCookie()
            cookies.load(response.headers.get('set-cookie', '')) # Load the cookies from the response
            
            for cookie in cookies.values():
                key = cookie.key
                value = cookie.value
                self.setCookie(key, value)
            
            if response.status_code in (300, 301, 302):
                url = urljoin(url, response.headers.get('location'))
            else:
                response.final_url = url
                response.cookies = self.cookies
                break
        
        return response
    
    def setCookie(self, key, value):
        self.cookies[key] = value
        
    def setCookies(self, jar):
        self.cookies.update(jar)
    
    def _getHeaders(self, cookie):
        headers = {
            'User-Agent' : 'Mozilla/5.0 (Linux; U; Android 2.3; en-gb) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
            'Cookie' : self._makeCookieHeader(cookie),
        }
        return headers
    
    def _makeCookieHeader(self, cookie = {}):
        cookieHeader = []
        for ckey, cvalue in cookie.items():
            cookieHeader.append( "%s=%s" % (ckey, cvalue) )
        return "; ".join(cookieHeader)