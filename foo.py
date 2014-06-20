import time
import datetime
today=int(time.strftime("%w"))
print today
anyday=datetime.datetime(2012,04,23).strftime("%w")
print anyday


import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)


class MainHandler(tornado.web.RequestHandler):
    def get(self, name, age):
        self.write("Hello,"+name+". I guess your age is "+age+" .")


def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/(?P<name>[^\/]+)/(?P<age>[^\/]+)", MainHandler),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
