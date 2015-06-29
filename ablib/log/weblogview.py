"""weblogview.py -

Main webserver for weblogview

Usage:
  weblogview.py [--port=PORT] [--host=HOST]

Options:
  --port=PORT  [default: 8888]

"""

from __future__ import print_function
import uuid
import tornado.httpserver
import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.gen
import logging
import tornadoredis
import os
import logbook

from docopt import docopt
from redis import Redis

##########################################################################################
#
#
redis_host_ip = '127.0.0.1'
host_ip       = '127.0.0.1'
redis_pubsub_channel = ('log:sermon', 'error')

R = Redis()

class ConsoleHandler(tornado.web.RequestHandler):
    def get(self):        
        self.render("weblogview.html", title="Web Log View", host_ip=host_ip, page_title='Web Log View')

class NewMessageHandler(tornado.web.RequestHandler):
    def post(self):
        message = self.get_argument('message')
        R.publish(redis_pubsub_channel, message)
        self.set_header('Content-Type', 'text/plain')
        self.write('sent: %s' % (message,))

class MessageHandler(tornado.websocket.WebSocketHandler):

    channel = 'comport'

    def __init__(self, *args, **kwargs):
        super(MessageHandler, self).__init__(*args, **kwargs)

    def check_origin(self, origin):
        return True

    def open(self, chan):
        print("MessageHandler.open {0}".format(chan))
        self.sub_channel = chan
        self.listen()

    @tornado.gen.engine
    def listen(self):
        self.client = tornadoredis.Client(redis_host_ip)
        self.client.connect()
        yield tornado.gen.Task(self.client.subscribe, self.sub_channel)
        self.client.listen(self.on_message)

    def on_message(self, msg):        
        #log.debug(type(msg))
        if isinstance(msg,unicode):
            log.debug(msg)
        else:
            if msg.kind == 'message':
                #log.debug(str(simplejson.loads(msg.body)))
                self.write_message(str(msg.body))
            if msg.kind == 'disconnect':
                # Do not try to reconnect, just send a message back
                # to the client and close the client connection
                self.write_message('The connection terminated '
                                   'due to a Redis server error.')
                self.close()

    def on_close(self):
        if self.client.subscribed:
            self.client.unsubscribe(redis_pubsub_channel)
            self.client.disconnect()

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
                (r'/', ConsoleHandler),                
                (r'/msg', NewMessageHandler),
                (r'/websocket/(?P<chan>.*)', MessageHandler),                
                ]
        
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=True,
            xsrf_cookies=False,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == '__main__':
    print("=== Web Log View ===")
    arguments = docopt(__doc__, version='Naval Fate 2.0')
    print(arguments)
    port = int(arguments['--port'])
    app = Application()
    app.listen(port)
    print('Web Log View is running at %s:%d\nQuit the demo with CONTROL-C' % (host_ip, port))
    tornado.ioloop.IOLoop.instance().start()