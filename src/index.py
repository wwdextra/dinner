#! /usr/bin/python
# coding=utf-8

__author__ = 'Michael Fan'

import os
root = os.path.dirname(__file__)
PORT = 9000

import tornado
from tornado import web, ioloop, template
from tornado.web import authenticated as auth
from sqlalchemy.orm import sessionmaker

from sqlalchemy import func, or_, not_

import models
from models import DbSession, User

import settings

# instantiated
# session = DbSession()

settings = {
  "cookie_secret": "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
  "login_url": "/login",
  "xsrf_cookies": True,
  "static_path": os.path.join(os.path.dirname(__file__), "../static/"),
  "template_path": os.path.join(os.path.dirname(__file__), "../template/"),
  'debug': True,
  "gzip": True,
  "static_url_prefix": '/s/',
  # "log_function": None
}

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
          (r"/", IndexHandler),
          (r"/login", LoginHandler),
          (r"/admin", AdminHandler),
        ]
        tornado.web.Application.__init__(self, handlers, **settings)


class BaseHandler(tornado.web.RequestHandler):

  def initialize(self):
    # instantiated, this `db` is a `Session` class
    self.db = models.DbSession()

  def on_finish(self):
    self.db.close()

  def get(self):
    self.user = "fuck"

  def get_current_user(self):
    """Identity a user by cookie `sid` as session_id."""
    return self.get_secure_cookie("sid")


class IndexHandler(BaseHandler):
  """ Project homepage. """
  def get(self):
    if not self.get_secure_cookie('sid'):
      self.set_secure_cookie('sid', 'fuck')
    if not self.get_current_user:
      self.redirect( settings.get('login_url') )
      return
    name = tornado.escape.xhtml_escape(self.current_user)

    q = self.db.query(User)

    # print query
    # for user in query: # 遍历时查询
    #   print user.name
    # print query.all() # 返回的是一个类似列表的对象
    # print query.first().name
    items = q.all()
    # items = []
    # TODO: site name in settings.py
    self.render("index.html", title="Life", items=items)


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


application = Application()

def main():
  print 'Using static path: %s' % settings.get('static_path')
  print 'Listen port: %s' % PORT
  application.listen(PORT)
  tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
  main()
