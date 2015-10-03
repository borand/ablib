"""daq.py -

module used to listen for new data on the redis channel and submit the data to sensoredweb

Usage:
  daq.py test [--submit_to=SUBMIT_TO] [--redishost=REDISHOST]
  daq.py run  [--submit_to=SUBMIT_TO] [--redishost=REDISHOST]
  daq.py (-h | --help)

Options:
  -h, --help  
  --submit_to=SUBMIT_TO  [default: 127.0.0.1]
  --redishost=REDISHOST  [default: 127.0.0.1]

"""

import threading
import datetime
import time
import simplejson as sjson

from redis import Redis
from logbook import Logger
from docopt import docopt

from redislog import handlers, logger

from datastore import submit
from ablib.util.common import get_host_ip

import time
##########################################################################################
# Define special processing functions for various sensor data
def process_hydro_power_data(data):    
    power = round(3600.0/((pow(2,16)*float(data[1]) + float(data[2]))/16.0e6*1024.0))    
    print("process_hydro_power_data({} = power = {})".format(data,power))
    if power < 120.0*100.0: # 120V @ 100A 
        return power
    else:
        return -1

def process_hydro_wh_data(data):
    print("process_hydro_wh_data({})".format(data))
    return data[2]

def process_default(data):
    print("process_default({})".format(data))
    return data[1]

def process_1wire_thermometer(data):
    print("process_default({})".format(data))
    return data[1]

ProcessingFunctions = {'hydro_power' : process_hydro_power_data,\
                       'hydro_wh'    : process_hydro_wh_data,\
                       }

##########################################################################################
class SubmitData(object):

    def __init__(self, channel='data', host='127.0.0.1', submit_to='192.168.1.12'):
        self.redis     = Redis(host=host)
        self.submit_to = submit_to
        self.msg_count = 0
        self.busy      = 0;
        self.last      = []    
        
        self.channel   = channel

        self.pubsub    = self.redis.pubsub()
        self.log       = logger.RedisLogger('daq.py:SubmitData')
        self.log.addHandler(handlers.RedisHandler.to("log", host='localhost', port=6379))
        self.log.level = 10

        self.alive             = False
        self._subscribe_thread = False
        
        self.pubsub.subscribe(self.channel)
        self.log.info("Initialized SubmitData()")
        self.start()

    def __del__(self):        
        self.log.info('__del__()')
        if self.subscribe_thread.is_alive():
            self.stop()

    def start(self):
        """Start reader thread"""
        self.log.debug("Start reader thread")        
        self.subscribe_thread    = threading.Thread(target=self.reader)
        self.subscribe_thread.setDaemon(True)
        self.subscribe_thread.start()

    def stop(self):
        """Stop reader thread only, wait for clean exit of thread"""
        self.log.debug("Stop reader thread only, wait for clean exit of thread")
        self.redis.publish(self.channel,"KILL")
        self._subscribe_thread = False
        self.subscribe_thread.join(3)

    def reader(self):
        self.log.debug('run()')
        self.alive               = True
        self._subscribe_thread   = True

        while self._subscribe_thread:

            for item in self.pubsub.listen():
                if item['data'] == "KILL":
                    self.pubsub.unsubscribe()
                    self.log.info("unsubscribed and finished")
                    return
                if item['data'] == "ERROR_TEST":
                    self.redis.publish('error', __name__ + ": ERROR_TEST")
                else:
                    if item['type'] == 'message':
                        self.last = item             
                        self.process_message(item)
                    #self.process_message(item)

        self.log.debug('end of reader() function')

    def process_message(self, item):
        self.log.debug('process_message()')
        #print(item)
        try:
            #print("   item = {0}".format(item))

            msg         = sjson.loads(item['data'])
            #print("   msg = {0}".format(msg))

            device_data = msg['MSG']['data']
            timestamp   = msg['MSG']['timestamp']            

            #print("   msg = {0}".format(msg))

            for data in device_data:
                sn                  = data[0]
                processing_function = ProcessingFunctions.get(sn,process_default)
                val                 = processing_function(data)                

                threshold   = 0
                submit_data = [[sn, val]]
                if len(sn):
                    #print("Final dataset : sn = {0}, val = {1}".format(sn, val))
                    submit.delay(submit_data,timestamp=timestamp,submit_to=self.submit_to)

        except Exception as E:
            self.log.error("process_message(): " + E.message)
            self.log.error(item)

def StartIqrSubmit(channel, host, submit_to):
    print"StartIqrSubmit(%s, %s, %s)" % (channel, host, submit_to)
    try:
        I = SubmitData(channel=channel, host=host, submit_to=submit_to);
        print("===============================================")
        while True:
            time.sleep(1)
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

    if arguments['run']:
        channel   = 'data'
        host      = arguments.get('--redishost', get_host_ip())
        submit_to = arguments.get('--submit_to', get_host_ip())
        StartIqrSubmit(channel, host, submit_to)
