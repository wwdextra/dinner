#! /usr/bin/python
# coding=utf-8

from multimethods import multimethod as mm
try: import simplejson as json
except ImportError: import json
from error import error_code


class JsonResult(object):
  """Http JSON helper"""

  def __init__(self, message='', data=list(), ec=0):
    self.ec = ec # system error code, 0=no error, 9999=unknown error, others defined in error.py
    self.message = message
    self.data = data

  def json(self):
    # dumps chinese characters
    return json.dumps(self, default=lambda o: o.__dict__, ensure_ascii=False, indent=2)

  def dict(self):
    return self.__dict__

  @mm(list(), str)
  def ok(self, data, message):
    """As jQuery chain function call"""
    self.ec = 0
    self.data = data
    self.message = message
    return self

  @mm(str)
  def ok(self, message):
    self.ec = 0
    self.data = []
    self.message = message
    return self

  @mm()
  def ok(self):
    self.ec = 0
    self.data = []
    self.message = error_code.get(str(0), '')
    return self

  @mm()
  def error(self):
    self.ec = 1
    self.message = error_code.get(str(1), '')
    return self

  @mm(int)
  def error(self, ec):
    self.ec = ec
    self.message = error_code.get(str(ec), '')
    return self

  @mm(str)
  def error(self, message):
    self.message = message
    self.ec = error_info.get(message, 9999)
    return self

  @mm(int, str)
  def error(self, ec, message):
    self.message = message
    self.ec = error_info.get(message, 9999)
    return self