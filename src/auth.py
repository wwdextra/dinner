#! /usr/bin/python
# coding=utf-8

import tornado
from tornado import auth, web
from index import BaseHandler


__author__ = 'Michael Fan'


# class NativeHander(BaseHandler):
#   """Native login"""
#   pass


class GoogleHandler(tornado.web.RequestHandler, tornado.auth.GoogleMixin):
    @tornado.web.asynchronous
    def get(self):
        if self.get_argument("openid.mode", None):
            self.get_authenticated_user(self._on_auth)
            return
        self.authenticate_redirect()

    def _on_auth(self, user):
        if not user:
            self.authenticate_redirect()
            return
        # Save the user with, e.g., set_secure_cookie()

class TwitterLoginHandler(tornado.web.RequestHandler,
                          tornado.auth.TwitterMixin):
    @tornado.gen.coroutine
    def get(self):
        if self.get_argument("oauth_token", None):
            user = yield self.get_authenticated_user()
            # Save the user using e.g. set_secure_cookie()
        else:
            yield self.authorize_redirect()        


class FacebookGraphLoginHandler(LoginHandler, tornado.auth.FacebookGraphMixin):
  @tornado.gen.coroutine
  def get(self):
      if self.get_argument("code", False):
          user = yield self.get_authenticated_user(
              redirect_uri='/auth/facebookgraph/',
              client_id=self.settings["facebook_api_key"],
              client_secret=self.settings["facebook_secret"],
              code=self.get_argument("code"))
          # Save the user with e.g. set_secure_cookie
      else:
          yield self.authorize_redirect(
              redirect_uri='/auth/facebookgraph/',
              client_id=self.settings["facebook_api_key"],
              extra_params={"scope": "read_stream,offline_access"})            