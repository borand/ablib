from __future__ import print_function
import tornado.httpserver
import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.gen

import simplejson as sj
import tornadoredis


c = tornadoredis.Client(host='192.168.1.99')
c.connect()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        #self.render("template.html", title="PubSub + WebSocket Demo")
        self.render("chart.html", title="PubSub + WebSocket Demo")

class NewMessageHandler(tornado.web.RequestHandler):
    def post(self):
        message = self.get_argument('message')
        c.publish('test_channel', message)
        self.set_header('Content-Type', 'text/plain')
        self.write('sent: %s' % (message,))


class MessageHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super(MessageHandler, self).__init__(*args, **kwargs)
        self.listen()

    @tornado.gen.engine
    def listen(self):
        self.client = tornadoredis.Client('192.168.1.99')
        self.client.connect()
        yield tornado.gen.Task(self.client.subscribe, 'irq')
        self.client.listen(self.on_message)

    def on_message(self, msg):
        if msg.kind == 'message':
            json_data = sj.loads(msg.body)            
            power_W = round(3600.0/((pow(2,16)*json_data[1][1] + json_data[1][2])/16e6*1024))            
            self.write_message(sj.dumps(power_W))
        if msg.kind == 'disconnect':
            # Do not try to reconnect, just send a message back
            # to the client and close the client connection
            self.write_message('The connection terminated '
                               'due to a Redis server error.')
            self.close()

    def on_close(self):
        if self.client.subscribed:
            self.client.unsubscribe('test_channel')
            self.client.disconnect()


application = tornado.web.Application([
    (r'/', MainHandler),
    (r'/msg', NewMessageHandler),
    (r'/track', MessageHandler),
])

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    print('Demo is runing at 0.0.0.0:8888\nQuit the demo with CONTROL-C')
    tornado.ioloop.IOLoop.instance().start()