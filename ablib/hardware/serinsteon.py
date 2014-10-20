'''
Created on Sep 29, 2011

@author: Andrzej
'''

import time
import re
import serial
import os
import redis

from threading import Thread,Event
from ablib.util.common import get_host_ip
from logbook import Logger

from anyjson import serialize, deserialize


PROMPT_FOUND = 1
PROMPT_NOT_FOUND = 0
PORT_OPEN = 1
PORT_CLOSED = 0
PORT_ERROR = -1
TIMEOUT = 1.0

CMDS = {0x50: ['Standard Message Received', 0, 11,],
        96  : ['GetImInfo',                 2, 9, ],
        98  : ['SendMessage',               8, 9, ],
        103 : ['Factory reset',             2, 3, ],
        109 : ['LedOn',                     2, 3, ],
        110 : ['LedOff',                    2, 3, ],        
        107 : ['SetIMConfiguration',        3, 4, ],
        115 : ['GetIMConfiguration',        2, 6, ],
        }
                #cmd1,  meaning          cmd2, meaning,  response 
STANDARD_CMDS = {
                 0x17: [ 'ON',           0,    'Level',                                 0x50],
                 0x0f: [ 'PING',         0,    'Level',                                 0x50],
                 0x19: [ 'GetStatus',    0,    'Request on-level status from a unit.',  0x50],
                 }

dining_room = [0x18, 0x1d, 0x04]
living_room = [0x09, 0x8E, 0x94]
ikea_lamp1  = [0x18, 0x98, 0xAA]
ikea_lamp2  = [0x16, 0x83, 0x87]
outdoor     = [0x14, 0xa1, 0x28]
light       = [0x20, 0x1f, 0x11]
bedroom     = [0x1D, 0xAD, 0x86]
unused_se   = [0x1B, 0x7A, 0x50]

all_devices = [dining_room, living_room, ikea_lamp1, ikea_lamp2, outdoor, light]

def dbg(obj, level, msg):
    if obj.debug >= level:
        print obj.__unicode__()+ ": " + "  "*level + msg
    else:
        pass

##########################################################################################
#

def GetDecAddress(address):
    '''
    Convert hex address to decimal vector.  If address is in decimal format the command has no effect
    '''
    return [int(h) for h in address] 

def SplitStr(s, size=2):
    return [s[i:i+size] for i in xrange(0, len(s), size)]

def str2hex(address):
    return [int(i,16) for i in address.split('.')]

def hex2str(address):
    return '%02x.%02x.%02x' % (address[0],address[1],address[2])

def hex2dec(address):
    return [int(h) for h in address] 

def str2dec(s):
    return [int(i,16) for i in SplitStr(s)]

def build_message(hex_address, flag, cmd1, cmd2):
    cmd      = [0x02, 98]
    cmd.extend(GetDecAddress(hex_address))
    cmd.append(flag)
    cmd.append(cmd1)    
    cmd.append(cmd2)
    hex_cmd = ''.join(chr(x) for x in cmd)
    return hex_cmd

def parse_flag(flag):
    bit_765 = flag >> 5
    bit_765_dict = {
     0 : 'Direct Message',
     1 : 'ACK of Direct Message',
     2 : 'Group Cleanup Direct Message',
     3 : 'ACK of Group Cleanup Direct Message',
     4 : 'Broadcast Message',
     5 : 'NAK of Direct Message',    
     6 : 'Group Broadcast Message',     
     7 : 'NAK of Group Cleanup Direct Message'
    }
    if flag & 16 == 16:
        message = 'extended message'
    else:
        message = 'standard message'

    hops_left = (flag >> 2) & 3
    max_hops = flag & 3
    return [bit_765_dict.get(bit_765), message,hops_left,max_hops] 

def parse_configuration_flags(flag):
    return [['automatic linking disabled', flag & 128 == 128],
            ['Monitor Mode enabled', flag & 64 == 64],
            ['Disables automatic LED', flag & 32 == 32],
            ]
    
def parse_buffer(buff):
    cmd = []
    unparsed = []
    for byte in buff:
        if byte == 2:
            cmd.append(byte)

#    
#
##########################################################################################
#
#

class RedisSub(Thread):

    def __init__(self, interface, channel='cmd', host='127.0.0.1'):
        Thread.__init__(self)
        self.interface = interface
        self.signature = "InsteonPLM" #"{0:s}:{1:s}".format(get_host_ip(),'')
        self.redis     = redis.Redis(host=host)
        self.channel   = self.signature #+ "-cmd"
        self.pubsub    = self.redis.pubsub()
        self.Log       = Logger('RedisSub')
        self.Log.debug('__init__(channel=%s)' % self.channel)

        self.pubsub.subscribe(self.channel)
        self.start()
        self.setName('RedisSub-Thread')

    def __del__(self):        
        self.Log.info('__del__()')
        self.stop()

    def stop(self):
        self.Log.info('stop()')
        self.redis.publish(self.channel,'unsubscribe')
        time.sleep(1)        
        self.Log.info('stopped')

    def run(self):
        self.Log.debug('run(chan={0})'.format(self.channel))
        try:
            for item in self.pubsub.listen():
                if item['data'] == "unsubscribe":
                    self.pubsub.unsubscribe()
                    self.Log.info("unsubscribed and finished")
                    break
                else:
                    cmd = item['data']
                    if isinstance(cmd,str):
                        self.Log.debug(cmd)
                        try:
                            cmd_obj = deserialize(cmd)
                            print cmd_obj
                            res = self.interface.send_standard_cmd(cmd_obj[0], cmd_obj[1], cmd_obj[2])


                        except Exception as E:
                            error_msg = {'source' : 'serinsteon:RedisSub', 'function' : 'def run(self):', 'error' : E.message}
                            self.redis.publish('error',serialize(error_msg))

                    else:
                        self.Log.debug(cmd)
        except Exception as E:
            error_msg = {'source' : 'RedisSub', 'function' : 'def run(self):', 'error' : E.message}
            self.redis.publish('error',sjson.dumps(error_msg))
                
        self.Log.debug('end of run()')

class InsteonPLM(object):
    '''
    Class used to connect to Insteon serial power line modem (PLM) 
    '''
    
    debug = 1; # Controls verbosity output
    Interface = None  

    def __init__(self, port='/dev/ttyUSB0'):
        '''
        Constructor
        '''
        if os.name == 'nt':
            port = port -1
        try:        
            self.Ser = serial.Serial(port=port, baudrate=19200, timeout=3)
            self.Ser.timeout = 1
        except:
            self.Ser = None
            print "Error occured while oppening Serial Interface"
    
    def __del__(self):        
        if self.Ser.isOpen():
            self.Ser.close()
    
    def __unicode__(self):
        if self.Ser is not None:
            name = "PLM(%s)" %  self.Ser.port
        else:
            name = "PLM(None)"
            
        return name
            
    def isOpen(self):
        return self.Ser.isOpen()
    
    def __open__(self):
        if not(self.Ser.isOpen()):            
            try:
                self.Ser.open()
                dbg(self, 2, "Port %s is now open" % str(self.Ser.port))
                return PORT_OPEN
            except serial.SerialException:
                dbg(self, 0, "SerialException Cannot open port: %s " % str(self.Ser.port))
                return PORT_ERROR
            except:
                dbg(self, 0, "OtherException Cannot open port: %s" % str(self.Ser.port))
                return PORT_ERROR
        else:
            dbg(self, 2, "Port %s is already open" % str(self.Ser.port))
            return PORT_OPEN  
    
    ############################################################################################
    #
    #
    def send(self, cmd, get_confirmation=True):
        dbg(self, 2, "def send(self, cmd=%s):" % str(cmd))
        
        if not CMDS.has_key(cmd[0]):
            dbg_msg =  "Command %d does not exist in the dictionary" % cmd[0]
            dbg(self, 3, dbg_msg)
            return False
        else:
            cmd_details = CMDS.get(cmd[0])
            dbg_msg = "Sending: " + cmd_details[0] + " : " + str(cmd)
            dbg(self, 3, dbg_msg)
        
        if not self.isOpen():
            self.__open__()
        
        cmd.insert(0,0x2)
        hex_cmd = ''.join(chr(x) for x in cmd)        
        dbg_msg = "Full command: " + str(cmd)
        dbg(self, 3, dbg_msg)
        
        self.Ser.write(hex_cmd)
        
        if get_confirmation:
            return_data = self.read_response([cmd[1]])
#            response = ''
#            
#            n = 0
#            to = time.time()
#            tn = time.time() 
#            while tn - to < TIMEOUT and n < cmd_details[2]:                
#                n = self.Ser.inWaiting()
#                tn = time.time()
#                time.sleep(0.05)
#            
#            if tn - to > TIMEOUT:
#                dbg_msg = "Command timed out while waiting for response "
#                dbg(self, 3, dbg_msg)
#            
#            
#            if n >= cmd_details[2]:
#                n = self.Ser.inWaiting()
#                dbg_msg = "%d bytes inWaiting() reading out %d" % (n, cmd_details[2])
#                dbg(self, 4, dbg_msg)
#                response += self.Ser.read(cmd_details[2])        
#                #response += self.Ser.read(n)
#                data = [ord(x) for x in response]
#                dbg_msg = "cmd succesful: = %s" % str(data) #+ str(cmd[0:2] == data[0:2] and data[-1] == 6)
#                return_data = data[2:-1]            
#            else:
#                dbg_msg = "did not recive expected number of bytes within the time out period"
#                return_data = -1            
#            dbg(self, 3, dbg_msg)
        else:
            return_data = cmd
            
        return return_data
        
    def send_standard_cmd(self, hex_address, cmd1, cmd2):
        dbg(self, 1, "send_standard_cmd(self, hex_address, cmd1, cmd2):")
        cmd      = [98, 0, 0, 0, 15, 17, 255]
        cmd[1:4] = GetDecAddress(hex_address)
        cmd[5]   = cmd1
        cmd[6]   = cmd2
        sent_cmd = self.send(cmd)
        read_res = self.read_response([0x50])                
        return [sent_cmd, read_res]
    
    def read_response(self, cmd):
        dbg(self, 2, "def read_response(self, cmd%s):" % str(cmd))
        if not CMDS.has_key(cmd[0]):
            dbg_msg =  "Command %d does not exist in the dictionary" % cmd[0]
            dbg(self, 3, dbg_msg)
            return []
        else:
            cmd_details = CMDS.get(cmd[0])
            dbg_msg = "Waiting for response to: " + cmd_details[0] + " : " + str(cmd)
            dbg(self, 3, dbg_msg)
        
        if not self.isOpen():
            self.__open__()
        
        cmd_details = CMDS.get(cmd[0])
        to = time.time()
        tn = time.time()
        response = ''
        n = 0
        while tn - to < TIMEOUT and n < cmd_details[2]:
            n = self.Ser.inWaiting()
            tn = time.time()        
        
        if tn - to > TIMEOUT:
            dbg_msg = "Timeout occured while waiting for response"
            dbg(self, 3, dbg_msg)
        
        if n >= cmd_details[2]:
            #response += self.Ser.read(cmd_details[2])        
            response += self.Ser.read(n)
            data = [ord(x) for x in response]
            dbg_msg = "cmd succesful: = %s" % str(data) #+ str(cmd[0:2] == data[0:2] and data[-1] == 6)
            return_data = data[2:]
        else:
            dbg_msg = "did not recive expected number of bytes within the time out period"
            return_data = -1            
        dbg(self, 3, dbg_msg)
        return return_data      
        
    def read(self):
        dbg(self, 2, "def read(self):")
        if self.Ser is not None:
            out = self.Ser.read(self.Ser.inWaiting())
            data = [ord(x) for x in out]
            dbg_msg = "read: %s" % str(data)
            dbg(self, 3, dbg_msg)
        else:
            dbg(self, 3, "No Serial connection")
            data = ''
        return data
    
    # Methods for specific modules
    
    def SetSwitchON(self, hex_address):
        dbg(self,1, "def SetSwitchON(self, hex_address=%s):" % str(hex_address))
        cmd         = [98, 0, 0, 0, 15, 17, 255]
        dec_address = [int(h) for h in hex_address]
        cmd[1:4]    = dec_address
        self.send(cmd)        
        return self.read_response([80])
    
    def SetSwitchOFF(self, hex_address):
        dbg(self,1, "def SetSwitchOFF(self, hex_address=%s):" % str(hex_address))
        cmd         = [98, 0, 0, 0, 15, 19, 255]
        dec_address = [int(h) for h in hex_address]
        cmd[1:4]    = dec_address        
        sent_status = self.send(cmd)
        read_status = self.read_response([80])
        return 
    
    def GetSwitchStatus(self, hex_address):
        cmd         = [98, 0, 0, 0, 15, 25, 255]
        dec_address = [int(h) for h in hex_address]
        cmd[1:4]    = dec_address        
        self.send(cmd)
        
        time.sleep(0.5)
        res = self.read()
        if res[-1] == 255:
            print "Switch is ON"
        elif res[-1] == 0:
            print "Switch is OFF"
        else:
            print "Switch status value: ", res[-1]
        return res
    
    def GetIdn(self):
        dbg(self, 1, "def GetIdn():")
        data = self.send([96])
        return data
       
        
if __name__ == '__main__':
    print "================================"
    print "PLM module test function" 
    I = InsteonPLM('/dev/ttyUSB1')
    
    #outdoor_sw = []

    
    test1 = True
    test2 = False
    test3 = True

    if test1:
        print "Test 1 - Ping"
        I.send([0x60])    
            
    if test2:
        I.send([2, 96])
        time.sleep(0.5)
        I.read()
        I.send([2, 98, 22, 131, 135, 15, 17, 255])
        time.sleep(0.5)
        I.read()
        time.sleep(0.5)
        I.send([2, 98, 22, 131, 135, 15, 19, 255])
        time.sleep(0.5)
        #CrossTheLine
        I.send([2, 98, 22, 131, 135, 15, 25, 255])
        time.sleep(0.5)
        I.read()        
        
    if test3:
        #print "Turning of lamp 1"
        I.SetSwitchON(outdoor_sw);
        time.sleep(3)
        I.SetSwitchOFF(outdoor_sw);
        
        # print "Turning of lamp 2"
        # I.SetSwitchON(light_bulb);
        # time.sleep(2)
        # I.SetSwitchOFF(light_bulb);

