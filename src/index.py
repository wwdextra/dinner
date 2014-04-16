#! /usr/bin/python
# coding=utf-8

__author__ = 'Michael Fan'

import os
root = os.path.dirname(__file__)
PORT = 8888

import tornado
from tornado import web, ioloop, template
from tornado.web import authenticated as auth

import settings

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler)
        ]
        settings = {
            "template_path": Settings.TEMPLATE_PATH,
            "static_path": Settings.STATIC_PATH,
        }
        tornado.web.Application.__init__(self, handlers, **settings)


class BaseHandler(tornado.web.RequestHandler):
  def get_current_user(self):
    """Identity a user by cookie `sid` as session_id."""
    return self.get_secure_cookie("sid")


class MainHandler(BaseHandler):
  """ Project homepage. """
  def get(self):
    if not self.get_secure_cookie('sid'):
      self.set_secure_cookie('sid', 'fuck')
    if not self.get_current_user:
      self.redirect("/login")
      return
    name = tornado.escape.xhtml_escape(self.current_user)
    items = []
    self.render("index.html", title="My title", items=items)


class LoginHandler(BaseHandler):
  def get(self):
      self.render("""
        <html><body>
        <form action="/login" method="post">
          {% module xsrf_form_html() %}
          Name: <input type="text" name="name">
                <input type="submit" value="Sign in">
        </form>
        </body></html>"""
      )

  def post(self):
      self.set_secure_cookie("sid", self.get_argument("name"))
      self.redirect("/")

class AdminHandler(BaseHandler):
  @auth
  def get(self):
    self.write('admin ok')


settings = {
  "cookie_secret": "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
  "login_url": "/login",
  "xsrf_cookies": True,
  "static_path": os.path.join(os.path.dirname(__file__), "../static/"),
  "template_path": os.path.join(os.path.dirname(__file__), "../template/"),
  'debug' : True
}


application = tornado.web.Application([
  (r"/", MainHandler),
  (r"/login", LoginHandler),
  (r"/admin", AdminHandler),
], **settings)

def main():
  print 'Using static path: %s' % settings.get('static_path')
  print 'Listen port: %s' % PORT
  application.listen(PORT)
  tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
  main()
