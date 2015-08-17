"""hardware.py - 

Simple module for communicating with ComPort firmware written for AVR328p.

Usage:
  hardware.py test [--dev=DEV ] [--test] [--submit_to=SUBMIT_TO] [--redishost=REDISHOST]
  hardware.py run [--dev=DEV] [--local] [--submit_to=SUBMIT_TO] [--redishost=REDISHOST]
  hardware.py (-h | --help)

Options:
  -h, --help
  --dev=DEV              [default: /dev/ttyUSB0]
  --run=RUN              [default: True]
  --submit_to=SUBMIT_TO  [default: 127.0.0.1]
  --redishost=REDISHOST  [default: 127.0.0.1]

"""

import serial
import time
import re
import simplejson as sjson
import logbook
import redis

import threading
from datetime import datetime
from logbook import Logger
from docopt import docopt

from redislog import handlers, logger

# MY MODULES
from ablib.util.message import Message
from ablib.util.common import get_host_ip

##########################################################################################
# Global definitions
TIMEOUT  = 2
EXCHANGE = 'ComPort'

#l = logger.RedisLogger('ablib.hw.sermon')
#l.addHandler(handlers.RedisHandler.to("log:sermon", host='localhost', port=6379, password=''))

##########################################################################################
class ComPort(object):
    re_data        = re.compile(r'(?:<)(?P<cmd>\d+)(?:>)(.*)(?:<\/)(?P=cmd)(?:>)', re.DOTALL)
    re_next_cmd    = re.compile("(?:<)(\d+)(?:>\{\"cmd\":\")")

    redis_pub_channel = 'rtweb'
    
    def __init__(self,
                 port = '/dev/ttyUSB0',
                 packet_timeout=1,
                 baudrate=115200,       
                 bytesize=8,    
                 parity='N',    
                 stopbits=1, 
                 xonxoff=0,             
                 rtscts=0,              
                 writeTimeout=None,     
                 dsrdtr=None,
                 host='127.0.0.1',
                 run=True):
        
        self.buffer  = ''
        self.serial    = serial.Serial(port, baudrate, bytesize, parity, stopbits, packet_timeout, xonxoff, rtscts, writeTimeout, dsrdtr)
        self.signature = "{0:s}:{1:s}".format(get_host_ip(), self.serial.port)
        
        self.redis_send_key = self.signature+'-send'
        self.redis_read_key = self.signature+'-read'
        self.redis = redis.Redis(host=host)        
        self.log   = logger.RedisLogger('sermon.py:ComPort')
        self.log.addHandler(handlers.RedisHandler.to("log", host='localhost', port=6379))
        self.log.level = 1


        self.alive = False
        self._reader_alive = False

        # TODO add checking for redis presence and connection
        if self.redis.ping():
            # Register the new instance with the redis exchange
            if not self.redis.sismember(EXCHANGE,self.signature):
                self.redis.sadd(EXCHANGE,self.signature)
        else:
            pass
        
        if run:
            self._start_reader()
            self._start_listner()

    def __del__(self):
        self.log.debug("About to delete the object")
        self.close()
        time.sleep(1)
        self.log.debug("Closing serial interface")
        self.serial.close()

        if self.serial.closed:
            self.log.error("The serial connection still appears to be open")
        else:
            self.log.debug("The serial connection is closed")
        self.log.debug("Object deleted")

        if self.redis.sismember('ComPort',self.signature):
            self.redis.srem('ComPort',self.signature)
    
    # Thread control
    def _start_reader(self):
        """Start reader thread"""
        self.log.debug("Start serial port reader thread")
        self.alive           = True
        self._reader_alive   = True
        self.receiver_thread = threading.Thread(target=self.reader)
        self.receiver_thread.setDaemon(True)
        self.receiver_thread.start()

    def _stop_reader(self):
        """Stop reader thread only, wait for clean exit of thread"""
        self.log.debug("Stop reader thread only, wait for clean exit of thread")
        self._reader_alive = False
        self.receiver_thread.join()

    def _start_listner(self):
        self.log.debug("Start redis sub channel and listen for commands send via redis")
        self._redis_subscriber_alive = True
        self.redis_subscriber_thread = threading.Thread(target=self.cmd_via_redis_subscriber)
        self.redis_subscriber_thread.setDaemon(True)
        self.redis_subscriber_thread.start()

    def cmd_via_redis_subscriber(self):
        self.log.debug('cmd_via_redis_subscriber()')
        self.pubsub    = self.redis.pubsub()
        self.pubsub.subscribe("cmd")
        
        while self._redis_subscriber_alive:
            try:
                for item in self.pubsub.listen():
                    if item['data'] == "unsubscribe":
                        self.pubsub.unsubscribe()
                        self.log.info("unsubscribed and finished")
                        break
                    else:
                        cmd = item['data']
                        if isinstance(cmd,str):
                            self.log.debug(cmd)
                            self.send(item['data'])
                        else:
                            self.log.debug(cmd)
            except Exception as E:
                error_msg = {'source' : 'RedisSub', 'function' : 'def run(self):', 'error' : E.message}
                self.redis.publish('error',sjson.dumps(error_msg))
        
        self.pubsub.unsubscribe()      
        self.log.debug('end of cmd_via_redis_subscriber()')

    def stop(self):
        self.alive = False

    def join(self, transmit_only=False):
        self.transmitter_thread.join()
        if not transmit_only:
            self.receiver_thread.join()
        
    def start_thread(self):
        '''
        Open the serial serial bus to be read. This starts the listening
        thread.
        '''

        self.log.debug('start_thread()')
        self.serial.flushInput()
        self.running.set()
        self.start()
        
    def open(self):
        if not self.serial.isOpen():
            self.serial.open()
        return self.serial.isOpen()
    
    def send(self, data, CR=True):
        '''Send command to the serial port
        '''
        if len(data) == 0:               
            return
        self.log.debug("send(cmd=%s)" % data)
        # Automatically append \n by default, but allow the user to send raw characters as well
        if CR:
            if (data[-1] == "\n"):
                pass            
            else:
                data += "\n"
            
        if self.open():
            try:
                self.serial.write(data)
                serial_error = 0
            except:
                serial_error = 1
        else:
            serial_error = 2
        self.redis.set(self.redis_send_key,data)
        return serial_error
    
    def read(self, waitfor=''):
        '''
        reads the data by waiting until new comport is found in the buffer and result can be read from the redis server
        '''

        serial_data = ''
        done = False
        to = time.clock()
        while time.clock() - to < TIMEOUT and not done:
            serial_data = self.redis.get(self.redis_read_key)
            done = waitfor in self.buffer and isinstance(serial_data,str)

        if not done:
            self.log.debug("read() did not find waitfor {:s} in self.buffer".format(waitfor))

        self.redis.delete(self.redis_read_key)
        return [done, serial_data]

    def query(self,cmd, **kwargs):
        """
        sends cmd to the controller and waits until waitfor is found in the buffer.
        """
        
        waitfor = kwargs.get('waitfor','')
        tag     = kwargs.get('tag','')
        json    = kwargs.get('json',1)
        delay   = kwargs.get('delay',0.01)

        if len(waitfor) < 1:
            next_cmd_num = self.re_next_cmd.findall(self.buffer)
            if len(next_cmd_num) > 0:
                waitfor = '<{:d}>{:s}"cmd":"'.format(int(next_cmd_num[0])+1,"{")

        self.log.debug('query(cmd=%s, waitfor=%s, tag=%s,json=%d, delay=%d):' % \
            (cmd, waitfor, tag, json, delay))

        self.send(cmd)
        time.sleep(delay)        
        query_data = self.read(waitfor=waitfor)
        if query_data[0]:
            try:
                query_data[1] = sjson.loads(query_data[1])
            except:
                query_data[0] = False
        return query_data

    def close(self):
        '''
        Close the listening thread.
        '''
        self.log.debug('close() - closing the worker thread')
        self.alive = False
        self._reader_alive = False
        self._redis_subscriber_alive = False
        self.receiver_thread.join()

    def reader(self):
        '''
        Run is the function that runs in the new thread and is called by        
        '''
        
        try:
            self.log.debug('Starting the listner thread')
            Msg = Message(self.signature)

            while self.alive and self._reader_alive:
                bytes_in_waiting = self.serial.inWaiting()
                
                if bytes_in_waiting:
                    new_data = self.serial.read(bytes_in_waiting)
                    self.buffer = self.buffer + new_data                    

                crlf_index = self.buffer.find('\r\n')

                if crlf_index > -1:
                    line = self.buffer[0:crlf_index]
                    temp = self.re_data.findall(line)
                    self.log.debug('read line: ' + line)

                    if len(temp):
                        final_data = dict()
                        timestamp = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
                        final_data['timestamp'] = timestamp
                        final_data['raw']       = line
                        try:
                            final_data.update({'cmd_number' : sjson.loads(temp[0][0])})
                            final_data.update(sjson.loads(temp[0][1]))
                            self.log.debug('.....updated final_data')

                        except Exception as E:
                            final_data.update({'cmd_number' : -1})
                            error_msg = {'timestamp' : timestamp, 'from': self.signature, 'source' : 'ComPort', 'function' : 'def run() - inner', 'error' : E.message}
                            Msg.msg = error_msg
                            self.redis.publish('error',error_msg)
                            self.log.error(Msg.msg)

                        Msg.msg = final_data
                        self.redis.publish(self.redis_pub_channel, Msg.as_jsno())
                        self.log.debug('.....publish to :' + self.redis_pub_channel)
                        self.redis.set(self.redis_read_key,Msg.as_jsno())

                        self.buffer = self.buffer[crlf_index+2:]
                        self.log.debug('.....empty buffer')
                    else:
                        self.buffer = ''
                        self.send('Z')
                        self.log.debug('.....reseting command number')

        except Exception as E:
            error_msg = {'source' : 'ComPort', 'function' : 'def run() - outter', 'error' : E.message}
            self.redis.publish('error',sjson.dumps(error_msg))
            self.log.error("Exception occured, within the run function: %s" % E.message)
        
        self.log.debug('Exiting run() function')

############################################################################################

def main(**kwargs):
    try:
        while True:
            pass
    except KeyboardInterrupt:
        pass    

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Naval Fate 2.0')
    
    mainlog   = logger.RedisLogger('sermon.py:main')
    mainlog.addHandler(handlers.RedisHandler.to("log", host='localhost', port=6379))
    mainlog.level = 10

    mainlog.info("===============================================")
    mainlog.info(arguments)

    dev = arguments['--dev']

    mainlog.info("===============================================")
    mainlog.info(dev)


    test_json  = arguments['test']
    run_main   = arguments['run']
    redis_host = arguments.get('--redishost',get_host_ip())
    run_local  = arguments.get('--local',False)

    C = ComPort(dev, host=redis_host)
    C.log.level = 10

    if run_local:
        redis_host = 'localhost'
    
    if test_json:
        cmd_vector = ['idn', 'adc', 'dio', 'getwh', 'resetwh', 'peek 22', 'owrom', 'owsave 1','owload', \
                  'owsp','owdata','owwp 3 1', 'owrp 3', 'adsf']
        for cmd in cmd_vector:
            try:
                out = C.query(cmd)
                mainlog.info(out)
            except Exception as E:
                mainlog.info(E)
    
    if run_main:        
        try:
            while True:
                pass
        except KeyboardInterrupt:
            pass
    C.close()

    mainlog.info("All done")
    print("All done")
