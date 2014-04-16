#! /usr/bin/python
# coding=utf-8

from tornado import web, ioloop
import tornado

class MainHandler(tornado.web.RequestHandler):
  def get(self):
    self.write("Hello, world")


class TestHander(web.RequestHandler):
  def get(self):
    self.write('fuck')

application = tornado.web.Application([
  (r"/", MainHandler),
  (r"/fuck", TestHander),
])

if __name__ == "__main__":
  application.listen(8888)
  tornado.ioloop.IOLoop.instance().start()