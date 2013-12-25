import threading

from redis import Redis
from rq import Queue
from logbook import Logger
from docopt import docopt
from datastore import submit
import simplejson as sjson
import time
import datetime


log = Logger('daq_irq')
log.info("2013.12.22 20:23")

##########################################################################################
class IrqSubmit(threading.Thread):

    def __init__(self, channel='irq', host='192.168.1.133'):
        threading.Thread.__init__(self)        
        self.redis     = Redis(host=host)
        self.msg_count = 0
        self.busy = 0;
        self.last = []        
        self.Q = Queue(connection=Redis())
        self.last_q = self.Q.enqueue(submit,([[0,'0',0]]))
        if channel=='':
            self.channel   = str(interface)
        else:
            self.channel   = channel

        self.pubsub    = self.redis.pubsub()
        self.Log       = Logger('IrqSubmit')
        
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
            else:                
                # self.Log.debug('run() - incoming message')                
                self.process_message(item)
        self.Log.debug('end of run()')

    def process_message(self, item):
        self.Log.debug('process_message(type=%s)' % item['type'])
        #to = time.time()
        #self.busy = True

        #self.msg_count = self.msg_count + 1
        if item['type'] == 'message':            
            #msg = sjson.loads(item['data'])
            try:             
                msg = sjson.loads(item['data'])
                self.last = msg
                timestamp = datetime.datetime.strptime(msg[0].split('.')[0],"%Y-%m-%d-%H:%M:%S")
                power_W = round(3600.0/((pow(2,16)*msg[1][1] + msg[1][2])/16e6*1024))
                self.last_enqueue = self.Q.enqueue(submit, [[0,'hydro',power_W]], timestamp=timestamp)

                self.Log.debug('    msg=%s' % str(msg))
            except Exception as E:
                self.Log.error(E.message)

##########################################################################################