import tornado.httpserver
import tornado.ioloop
import tornado.web

import os

class MainHandler(tornado.web.RequestHandler):
    def initialize(self):
        self._examples = {}
    def get(self):
        examples = os.listdir("examples")
        self._examples = {}
        for example in examples:
            self._examples[example] = example
        with open("examples/consensus.py", 'r') as ifile:
            source = ifile.read()
        self.render("web/templates/template.html", 
                    examples=self._examples)

application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()