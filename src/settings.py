#! /usr/bin/python
# coding=utf-8

import os
dirname = os.path.dirname(__file__)

STATIC_PATH = os.path.join(dirname, 'static')
TEMPLATE_PATH = os.path.join(dirname, 'templates')

settings = {
  "cookie_secret": "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
  "login_url": "/login",
  "xsrf_cookies": True,
}

SITE_NAME = 'Dinner'
SITE_LOGO = ''


try:
  from .. import pro_settings
  print "Using PRODUCTION settings..."
except ValueError:
  print "Using DEV settings..."