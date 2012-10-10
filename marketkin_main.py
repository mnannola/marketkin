import webapp2
from google.appengine.ext import db
from google.appengine.api import memcache
import jinja2
import time
import logging
import json
import os

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
    autoescape=True)


def renderString(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


class BaseHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        logging.error("Render.  Template: %s" % template)
        self.response.write(renderString(template, **kw))

    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_json(self, dic, **kw):
        self.response.headers['Content-Type'] = 'application/json'
        self.write(json.dumps(dic))


class MainPage(BaseHandler):
    def get(self):
        self.write("Hello My New Project!")


class PostPage(BaseHandler):
    def get(self):
        self.write("Not implemented Yet")


app = webapp2.WSGIApplication([
    ('/', MainPage)
], debug=True)


def main():
    app.run()

if __name__ == '__main__':
    main()
