import os

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template, util

import json
from urlopener import URLOpener
from BeautifulSoup import BeautifulSoup

import logging

class JSONHandler(json.JSONRPCHandler):
    def json_helloworld(self):
        return "Hello, World!"
    
    def json_auth(self):
        user = users.get_current_user()
        if user:
            greeting = ("Welcome, %s!" % (user.nickname()))
        else:
            greeting = ("Annonymous")

        return greeting
    
    def json_login(self, phone, pin):
        data = {
                'action': 'login',
                'bike_no': '',
                'mobile': phone,
                'pin': pin,
                }
        
        opener = URLOpener()
        response = opener.open('https://nextbike.net/de/m/home', data)
        logging.info(response.content)
        soup = BeautifulSoup(response.content)
        if soup.find('input', type='hidden', value='login') is not None:
            raise json.JSONRPCError("Bad phone number or pin", 404)
        
        result = {
             'action': 'login',
             'url': response.final_url,
             'cookies': response.cookies,
             }
        return result
    
    def json_logout(self, session):
        logging.debug("Logout user")
        opener = URLOpener()
        opener.setCookie('PHPSESSID', session)
        response = opener.open('https://nextbike.net/de/m/logout')
        logging.info(response.content)
        soup = BeautifulSoup(response.content)
        return soup.find('input', type='hidden', value='login') is not None
    
    def json_isSessionValid(self, session):
        logging.debug("Checking is session valid")
        opener = URLOpener()
        opener.setCookie('PHPSESSID', session)
        response = opener.open('https://nextbike.net/de/m/home')
        logging.info(response.content)
        soup = BeautifulSoup(response.content)
        return soup.find('input', type='hidden', value='login') is None
    
    def json_rentBike(self, cookies, bike_no):
        pass

class HelloWorldPage(webapp.RequestHandler):
    
    def get(self):
        hello = os.path.join('templates', 'helloworld.html')
        self.response.out.write(template.render(hello, {}))
        
class WelcomePage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            greeting = ("Welcome, %s! (<a href=\"%s\">sign out</a>)" %
                        (user.nickname(), users.create_logout_url("/")))
        else:
            greeting = ("<a href=\"%s\">Sign in or register</a>." %
                        users.create_login_url("/welcome.html"))

        self.response.out.write("<html><body>%s</body></html>" % greeting)

def main():
    app = webapp.WSGIApplication([
        ('/json', JSONHandler),
        ('/', HelloWorldPage),
        ('/welcome.html', WelcomePage)
        ], debug=True)
    util.run_wsgi_app(app)

if __name__ == '__main__':
    main()