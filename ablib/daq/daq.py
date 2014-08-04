import threading
import docopt
import time
import simplejson
from logbook import Logger
from redis import Redis
from rq import Queue
from ablib.daq.datastore import submit
from ablib.util.common import get_host_ip
from ablib.util.message import Message
import datetime

__author__ = 'andrzej'


##########################################################################################
# Define special processing functions for various sensor data
def process_default(data):
    return data

ProcessingFunctions = {'default' : process_default,\
                       }

##########################################################################################
class Daq(threading.Thread):

    def __init__(self, channel='daq', host='192.168.1.10', submit_to='192.168.1.10'):
        threading.Thread.__init__(self)
        self.channel   = channel
        self.redis     = Redis(host=host)
        self.submit_to = submit_to
        self.Q         = Queue(connection=Redis())
        self.last_q    = []
        self.Log       = Logger('Daq')

        self.pubsub.subscribe(self.channel)
        self.start()
        self.setName('IrqSubmit-Thread')

    def __del__(self):
        self.Log.info('__del__()')
        self.stop()

    def stop(self):
        self.Log.info('stop()')
        self.busy = False
        self.redis.publish(self.channel,'KILL')
        time.sleep(1)
        self.Log.info('  stopped')

    def run(self):
        self.Log.debug('run()')

        for item in self.pubsub.listen():
            if item['data'] == "KILL":
                self.pubsub.unsubscribe()
                self.Log.info("unsubscribed and finished")
                break
            if item['data'] == "ERROR_TEST":
                self.redis.publish('error', __name__ + ": ERROR_TEST")
            else:
                if item['type'] == 'message':
                    self.process_message(item)
                #self.process_message(item)

        self.Log.debug('end of run()')

    def process_message(self, item):
        try:

            msg         = simplejson.loads(item['data'])
            device_data = msg['MSG']['data']
            timestamp   = msg['MSG']['timestamp']

            for data in device_data:
                sn                  = data[0]
                processing_function = ProcessingFunctions.get(sn,process_default)
                val                 = processing_function(data)
                print("Final dataset : sn = {0}, val = {1}".format(sn, val))

                threshold   = 0
                submit_data = [[sn, val]]
                self.last_enqueue = self.Q.enqueue(submit, submit_data,\
                                    timestamp=timestamp,\
                                    submit_to=self.submit_to,\
                                    threshold=threshold)

        except Exception as E:
            self.Log.error("print_message(): " + E.message)
            self.Log.error(item)

def StartIqrSubmit(channel, host, submit_to):
    print"StartIqrSubmit(%s, %s, %s)" % (channel, host, submit_to)
    try:
        I = Daq(channel=channel, host=host, submit_to=submit_to);
        print("===============================================")
        while True:
            pass
    except KeyboardInterrupt:
        pass
    I.stop()

    print "Exiting " + __name__

##########################################################################################
if __name__ == "__main__":
    arguments = docopt(__doc__, version='Naval Fate 2.0')
    print("===============================================")
    print(arguments)

    dev = arguments['--dev']

    if arguments['run']:
        channel   = 'rtweb'
        host      = get_host_ip()
        submit_to = arguments.get('--submit_to', get_host_ip())
        StartIqrSubmit(channel, host, submit_to)