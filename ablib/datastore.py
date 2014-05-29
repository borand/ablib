import datetime

import simplejson as sjson

from logbook import Logger
from requests import get
from redis import Redis


log = Logger('datastore')

def get_last_value(serial_number):
    R = Redis()
    datavalue_json = R.get('serial_number:'+serial_number)
    if datavalue_json is not None:
        try:
            datavalue_obj = sjson.loads(datavalue_json)
            timestamp = datavalue_obj[0]
            datavalue = datavalue_obj[1]
        except Exception as e:
            log.error("Exception occured, within get_last_value function: %s" % E.message)
            return None
        
        timestamp = datetime.datetime.strptime(timestamp.split('.')[0],"%Y-%m-%d-%H:%M:%S")
        return {'serial_number' : serial_number, 'timestamp': timestamp, 'datavalue' : datavalue}
    else:
        return None

def save_last_value(serial_number, timestamp, datavalue):
    R = Redis()
    datavalue_json = sjson.dumps([timestamp.strftime('%Y-%m-%d-%H:%M:%S'), datavalue])
    R.set('serial_number:'+serial_number, datavalue_json)

def submit(data_set, timestamp='', submit_to='0.0.0.0', port=8000, threshold=0, max_interval=3600):

    if isinstance(timestamp, str):
        if timestamp.lower() == 'now':
            timestamp = datetime.datetime.now()
        else:
            try:
                timestamp = datetime.datetime.strptime(timestamp.split('.')[0],"%Y-%m-%d-%H:%M:%S") 
            except:
                timestamp = datetime.datetime.now()
    
    try:
        ret = []
        for data in data_set:
            # print data, timestamp.strftime('%Y-%m-%d-%H:%M:%S')
            # url = 'http://%s/sensordata/api/submit/datavalue/now/sn/%s/val/%s' % (submit_to, data[0], data[-1])
            print data
            serial_number = data[1]
            datavalue     = data[-1]
            

            last_submitted = get_last_value(serial_number)
            if last_submitted is not None:                
                time_since_last_submission  = timestamp - last_submitted['timestamp']
                # print (abs(datavalue - last_submitted['datavalue']), threshold
                
                if time_since_last_submission.seconds < max_interval and abs(datavalue - last_submitted['datavalue']) < threshold:
                    status_msg = '[SKIPPING], %s value less than %d sec old and below min change threshold %f' % (serial_number, max_interval, threshold)
                    #log.info(status_msg)
                    ret.append(status_msg)
                    continue
            
            url = 'http://%s:%d/sensordata/api/submit/datavalue/%s/sn/%s/val/%.3f' % (submit_to, port, timestamp.strftime('%Y-%m-%d-%H:%M:%S'), serial_number, datavalue)
            log.debug('submitting to: %s' % url)
            res = get(url)
            if res.ok:                
                log.info(res.content)
                ret.append(res.content)
                save_last_value(serial_number, timestamp, datavalue)
            else:
                log.info(res)

        return ret

    except Exception as E:
        log.error("Exception occured, within the submit function: %s" % E.message)
        log.error('q_data = %s' % str(data_set[0]))
        return E.message


# class DataStore(threading.Thread):

#     def __init__(self, interface=InterfaceTemplate(), channel='', host='127.0.0.1'):
#         threading.Thread.__init__(self)
#         self.timeout   = 1        
#         self.redis     = redis.Redis(host=host)
#         self.msg_count = 0
#         self.busy = 0;
#         if channel=='':
#             self.channel   = str(interface)
#         else:
#             self.channel   = channel

#         self.pubsub    = self.redis.pubsub()
#         self.Log       = Logger('DataStore')
#         self.Log.debug('__init__(channel=%s)' % self.channel)

#         self.pubsub.subscribe(self.channel)
#         self.start()
#         self.setName('HwRedisInterface-Thread')

#     def __del__(self):        
#         self.Log.info('__del__()')
#         self.stop()

#     def stop(self):
#         self.Log.info('stop()')
#         self.busy = False
#         self.redis.publish(self.channel,'QUIT')
#         time.sleep(1)        
#         self.Log.info('  stopped')

#     def run(self):
#         self.Log.debug('run()')
#         for item in self.pubsub.listen():
#             if item['data'] == "QUIT":
#                 self.pubsub.unsubscribe()
#                 self.Log.info("unsubscribed and finished")
#                 break
#             else:                
#                 # self.Log.debug('run() - incoming message')
#                 if not self.busy:
#                     self.process_message(item)
#         self.Log.debug('end of run()')

#     def process_message(self, item):
#         self.Log.debug('process_message(type=%s)' % item['type'])
#         to = time.time()
#         self.busy = True

#         self.msg_count = self.msg_count + 1
#         if item['type'] == 'message':
#             try:
#                 msg = sjson.loads(item['data'])
#                 self.Log.debug('    msg=%s, from=%s' % (msg['cmd'], msg['from']))
                
#                 if isinstance(msg['cmd'],list):
#                     cmd      = msg['cmd'][0]
#                     kwargs   = msg['cmd'][1]
#                     is_query = msg['cmd'][2]
#                 else:
#                     cmd      = msg['cmd']                    
#                     is_query = True
                    
#             except Exception as E:
#                 self.Log.error(E.message)
#                 return None
            
#             self.Log.debug('    is_query=%d' % is_query)
            
#             if is_query:
#                 out = self.query(cmd,**kwargs)
#                 self.redis.publish('res', sjson.dumps(out))
#                 timeout = msg['timeout']
#                 timeout = self.timeout
#                 self.redis.set(msg['from'],sjson.dumps(out))
#                 self.redis.expire(msg['from'], timeout)
#                 self.Log.debug('    query(cmd=%s) = %s' % (cmd, str(out)))
#             else:
#                 self.Log.debug('    send(cmd)')
#                 out = self.interface.send(cmd)
#             self.busy = False
#             return out
#         else:
#             self.busy = False
#             return None


if __name__ == "__main__":
    submit([['0', 0.0]])
