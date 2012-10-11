import webapp2
from google.appengine.api import memcache
import jinja2
import time
import logging
import json
import os
import re

import dbmodels
import utils

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
    autoescape=True)


def renderString(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


class BaseHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        logging.error("Render.  Template: %s" % template)
        # pass username to template if user is logged in.
        username = self.getUsername()
        if username:
            kw['username'] = username
        self.response.write(renderString(template, **kw))

    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_json(self, dic, **kw):
        self.response.headers['Content-Type'] = 'application/json'
        self.write(json.dumps(dic))

    def getUsername(self):
        u = self.getUser()
        username = None
        if u:
            username = u.username
        return username

    def getUserSpots(self, u):
        userSpots = None
        if not u:
            u = self.getUser()
        if u:
            userSpots = dbmodels.UserSpots.by_user(u)
        return userSpots

    def getUser(self):
        u = None
        cookie_data = self.request.cookies.get('user_id')
        if cookie_data and utils.valid_secure_val(cookie_data):
            user_id = long(cookie_data.split('|')[0])
            u = dbmodels.User.by_id(user_id)
        return u


class MainPage(BaseHandler):
    def get(self):
        self.render("mainpage.html")


class NewPostPage(BaseHandler):
    def get(self):
        self.render("newpost.html")


class NewSpotPage(BaseHandler):
    def get(self):
        self.render("newspot.html")

    def post(self):
        name = self.request.get('name')
        website = self.request.get('website')
        city = self.request.get('city')
        state = self.request.get('state')

        nameError = ""
        websiteError = ""

        if not(name and valid_name(name)):
            nameError = NAME_ER
        if not(website and valid_website(website)):
            websiteError = WEBSITE_ER

        if(nameError or websiteError):
            self.render('newspot.html', name=name,
                            website=website,
                            city=city,
                            state=state,
                            nameError=nameError,
                            websiteError=websiteError)
        else:
            s = dbmodels.Spot(name=name, website=website, city=city, state=state)
            key = s.put()
            spot = dbmodels.Spot.get(key)
            user = self.getUser()
            dbmodels.UserSpots(user=user, spot=spot).put()
            self.redirect('/viewspots')


class ViewSpotPage(BaseHandler):
    def get(self):
        user = self.getUser()
        if user:
            userSpots = self.getUserSpots(user)
            self.render("viewspots.html", userSpots=userSpots)
        else:
            self.redirect('/login')


# Helper methods - may move to utils.py
NAME_ER = 'Name is not valid'
WEBSITE_ER = 'Website URL is not valid'

NAME_RE = re.compile(r"^[a-zA-Z0-9_-]{2,30}$")


def valid_name(name):
    if dbmodels.Spot.by_name(name):
        return False
    else:
        return NAME_RE.match(name)


def valid_website(website):
    if dbmodels.Spot.by_website(website):
        return False
    else:
        return True


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/newpost', NewPostPage),
    ('/newspot', NewSpotPage),
    ('/viewspots', ViewSpotPage)
], debug=True)


def main():
    app.run()

if __name__ == '__main__':
    main()
