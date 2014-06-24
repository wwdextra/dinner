#! /usr/bin/python
# coding=utf-8
# Doc: http://www.keakon.net/2012/12/03/Tornado%E4%BD%BF%E7%94%A8%E7%BB%8F%E9%AA%8C
# SQLAlchemy: http://www.keakon.net/2012/12/03/SQLAlchemy%E4%BD%BF%E7%94%A8%E7%BB%8F%E9%AA%8C

__author__ = 'Michael Fan'

import os
root = os.path.dirname(__file__)
PORT = 8000

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import datetime
try: import simplejson as json
except ImportError: import json

import tornado
from tornado import web, ioloop, template
from tornado.web import authenticated as auth
from tornado.web import HTTPError as http_error
from sqlalchemy import func, or_, not_

import models
from models import DbSession, User, Session

from settings import *
from error import error_code, error_info
from session import gen_session_id
from utils import JsonResult


session_key = 'ssid' # Browser cookie

db = DbSession() # instantiated


settings = {
  "cookie_secret": "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
  "login_url": "/login",
  "xsrf_cookies": False,
  "static_path": os.path.join(os.path.dirname(__file__), "../static/"),
  "template_path": os.path.join(os.path.dirname(__file__), "../template/"),
  'debug': True,
  'autoreload': True,
  'serve_traceback': True,
  "gzip": True,
  "static_url_prefix": '/s/'
}

class Application(tornado.web.Application):
  def __init__(self):
    handlers = [
      (r"/", IndexHandler),
      (r"/login", LoginHandler),
      (r"/logout", LogoutHandler),
      (r"/h\/(?P<filename>\w+)", HtmlHandler),
      (r"/dinner", DinnerHandler),
      (r"/dinner/calendar", CalendarHandler),
      (r"/%20admin", AdminHandler), # it is a secret :)
    ]
    tornado.web.Application.__init__(self, handlers, **settings)


class BaseHandler(tornado.web.RequestHandler):

  def initialize(self):
    self.db = models.DbSession()
    self.user, self.session_id = None, None
    self.j = JsonResult()
    self.session_id = self.get_secure_cookie(session_key)
    # name = tornado.escape.xhtml_escape(self.current_user)
    if not self.session_id:
      _session_id = gen_session_id()
      self.set_secure_cookie(session_key, _session_id)

  def on_finish(self): self.db.close()

  def get(self): pass

  def get_current_user(self):
    # self.session_id = self.get_secure_cookie(session_key)
    if not self.session_id:
      return None
    _s = self.db.query(Session).filter(Session.session_id == self.session_id).first()
    if _s:
      return self.db.query(User).get(_s.user_id)
    else:
      return None

  # def get_user_locale(self):
  #       if "locale" not in self.current_user.prefs:
  #           # Use the Accept-Language header
  #           return None
  #       return self.current_user.prefs["locale"]


class IndexHandler(BaseHandler):
  """ Homepage """
  def get(self):
    print self.locale.name
    print '-'*80
    if self.current_user:

      q = self.db.query(User)
      items = q.all()
      self.render("index.html", title="Life", items=items)
    else:
      # Please sign in or up first
      self.render("login.html", title="Life")

  def post(self):
    email = self.get_argument("email")
    password = self.get_argument('password')
    q = db.query(User).filter(User.email==email).filter(User.password==password)


class LoginHandler(BaseHandler):
  def get(self):
    _next = self.get_argument('next', default=None)
    if self.get_current_user():
      if _next:
        self.redirect(_next)
      else:
        self.redirect('/')
      return

    self.render('login.html', title='Login')

  def post(self):
    next = self.get_argument("next", default=None)
    email = self.get_argument("email", default=None)
    password = self.get_argument('password', default=None)
    rememberme = self.get_argument('remember-me', default=None)
    expires_days = 30
    if rememberme:
      expires_days = 30^2

    # 已登录返回重定向
    if self.current_user:
      self.redirect(next if next else '/')
      return

    # 未登录返回JSON
    self.set_header("Content-Type", 'application/json; charset="utf-8"')
    # 看密码是否吻合，返回第一条记录的第一个元素
    _q = db.query(User).filter(User.email == email, User.password == password).first()
    if _q:
      _session_id = gen_session_id()
      self.set_secure_cookie(session_key, _session_id, expires_days=expires_days)
      # 密码校验通过,记录session backend
      _s = Session(user_id = _q.id,
                   session_id = _session_id,
                   # session_id = gen_session_id(),
                   data = None,
                   expire_date = datetime.datetime.now() + datetime.timedelta(days=expires_days))
      self.db.add(_s)
      self.db.commit()
    else:
      # 密码校验失败
      self.j.error(2)
      # raise tornado.web.HTTPError(403)
    self.write(self.j.json())


class LogoutHandler(BaseHandler):
  def get(self):
    # This logs the user out of this demo app, but does not log them
    # out of Google.  Since Google remembers previous authorizations,
    # returning to this app will log them back in immediately with no
    # interaction (unless they have separately logged out of Google in
    # the meantime).
    # todo: remove db.session.`session_id` value
    self.post()

  def post(self):
    self.set_header("Content-Type", 'application/json; charset="utf-8"')
    self.clear_cookie(session_key)
    _s = self.db.query(Session).filter(Session.session_id == self.session_id).first()
    if _s:
      # todo: delete it
      # db.delete(_s)
      return self.write( self.j.ok().json() )
    else:
      return self.write( self.j.error().json() )


class HtmlHandler(BaseHandler):
  """General html template"""
  def get(self, filename):
    self.render("h/%s.html" % filename, title="%s" % filename.capitalize())


class DinnerHandler(BaseHandler):
  """ Homepage """
  @auth
  def get(self):
    items = []
    self.render("dinner.html", title="Life", items=items)

  def post(self):
    email = self.get_argument("email")
    password = self.get_argument('password')
    q = db.query(User).filter(User.email==email).filter(User.password==password)

class AdminHandler(BaseHandler):
  # todo: uncomment bellow
  # @auth
  def get(self):
    self.write('admin ok')


class CalendarHandler(BaseHandler):
  """CalendarHandler"""
  def get(self):
    return self.write(self.j.error().json())

  def post(self):
    ''' Unix Bash commond `cal` displays a calendar and the date of Easter. '''
    # selected: {String} `0`=False, `1`=True
    selected = self.get_argument("selected")
    cal_id = self.get_argument('cal_id')

    return self.write( self.j.ok().json() )
            


application = Application()

def main():
  print 'Using static: %s' % settings.get('static_path')
  print 'Running at: http://localhost:%s' % PORT
  application.listen(PORT)
  tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
  main()
