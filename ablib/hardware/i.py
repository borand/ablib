import time
import re
import serial
import os
import redis

from threading import Thread,Event
from ablib.util.common import get_host_ip
from logbook import Logger

from anyjson import serialize, deserialize

def build_sd_message(addr, flag, cmd1, cmd2=0):
    cmd = [0x02, 0x62]
    if isinstance(addr, str):
        addr = str2hex(addr)
    addr = hex2dec(addr)
    cmd.extend(addr)
    cmd.append(flag)
    cmd.append(cmd1)    
    cmd.append(cmd2)    
    return cmd

def build_ex_message(addr, flag, cmd1, cmd2, data=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]):
    '''
    Sample cmd:
    02 62 [address] 3F 09 [group] 00 00 00 00 00 00 00 00 00 00 00 00 00 [checksum]
    '''
    cmd = [0x02, 0x62]
    if isinstance(addr, str):
        addr = str2hex(addr)
    cmd.extend(addr)
    cmd.append(flag)
    cmd.append(cmd1)    
    cmd.append(cmd2)
    cmd.extend(data)
    sum_of_cmd1_d13 = sum(cmd[6:-1])    
    checksum = (~(sum_of_cmd1_d13) + 1) & 255    
    cmd.append(checksum)    
    return cmd

###########################################################################################################
# Conversion functions
#
def hex2str(address):
    return '%02x.%02x.%02x' % (address[0],address[1],address[2])

def cmd2str(cmd):
    return ''.join(chr(x) for x in cmd)

def split_str(s, size=2):
    return [s[i:i+size] for i in xrange(0, len(s), size)]

def str2hex(address):
    return [int(i,16) for i in address.split('.')]

def hex2str(address):
    return '%02x.%02x.%02x' % (address[0],address[1],address[2])

def hex2dec(address):
    return [int(h) for h in address] 

def str2dec(s):
    return [int(i,16) for i in SplitStr(s)]
###########################################################################################################
# Command Parsers

def do_nothing(cmd):
    return {'raw' : cmd}

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
    return [flag, [bit_765, bit_765_dict.get(bit_765)], message,hops_left, max_hops] 

def parse_get_im_info(cmd):
    cmd_info = cmd_dict.get(cmd[1], None)
    if cmd_info is None:
        cmd_str = ''
    else:
        cmd_str = cmd_info[0]
        
    return {'raw' : cmd,
            'cmd' : [cmd[1], cmd_str],
            'success': cmd[-1] == 6,
            'response': {
            'id':  [cmd[2:5], hex2str(cmd[2:5])],            
            'devcat' : cmd[5], 'subcat' : cmd[6], 'firmware' : cmd[7]}
            }

def parse_response(cmd):
    return {'to': [cmd[2:5], hex2str(cmd[2:5])], 'from': [cmd[5:8], hex2str(cmd[5:8])],
            'flag': parse_flag(cmd[8]),'cmd1': [cmd[9], sd_commands.get(cmd[9],cmd[9])],'cmd2': cmd[10], 'raw' : cmd} 

def parse_std_cmd(cmd):
    # split byte buffer into meaningful dictionary
    return {'to': [cmd[2:5], hex2str(cmd[2:5])], 'flag': parse_flag(cmd[5]),
            'cmd1': sd_commands.get(cmd[6], cmd[6]), 'cmd2': cmd[7], 'success': cmd[8] == 6, 'raw' : cmd}

def parse_x10_cmd(cmd):
    raw_x10  = cmd[2]
    x10_flag = cmd[3]
    x10_code = x10_code_dict.get(raw_x10 >> 4,'Z')
    return [x10_code, x10_flag & 15]

def parse(buf, process=True):
    parsed   = []
    unparsed = [];
    buf.reverse()
    while len(buf) > 0:
        x = buf.pop()
        if x == 2 and len(buf) > 1:            
            cmd_num = buf.pop()
            cmd_meta = cmd_dict.get(cmd_num, 0)
            if cmd_meta != 0:
                data_length = cmd_meta[2] - 2 # by now we have popped 0x02 and cmd byte                
                data = buf[-1*data_length:]
                data.extend([cmd_num, 0x02])
                buf[-1*data_length:] = []
                data.reverse()
                if process:
                    processing_func = cmd_meta[-1]
                    parsed.append([cmd_num, cmd_meta[0], processing_func(data)])
                else:
                    parsed.append(data)
            else:
                unparsed.append(cmd_num)
        else:
            unparsed.append(x)
    return [parsed, unparsed]

###########################################################################################################
devices = {
'19.74.73' : 'Serial PLM',
'18.1d.04' : 'dining_room',
'09.8E.94' : 'living_room',
'18.98.AA' : 'livingroom_dimmer',
'16.83.87' : 'livingroom_lamp_sw',
'14.a1.28' :'20.1f.11' 'outdoor',
'20.1f.11' : 'light',
'1D.AD.86' : 'bedroom',
'1B.7A.50' : 'unused_se',
}

###########################################################################################################
# http://www.insteon.com/pdf/insteon_developers_guide_20070816a.pdf pg 223
cmd_dict = {
0x50 : ['sd msg received',                0, 11, 0, parse_response],
0x51 : ['ed msg received',                0, 25, 0, do_nothing],
0x52 : ['x10 received',                   0, 4,  0, parse_x10_cmd] ,
0x53 : ['all-linking completed',          0, 10, 0, do_nothing],
0x54 : ['button event report',            0, 3,  0, do_nothing],
0x55 : ['user reset detected',            0, 2,  0, do_nothing],
0x56 : ['link cleanup failure report',    0, 3,  0, do_nothing],
0x57 : ['all-link record response',       0, 10, 0, do_nothing],
0x58 : ['all-link cleanup status report', 0, 3,  0, do_nothing],   
# Commands Sent from the Host to an IM 
0x60 : ['get im info',            2, 9,  0,  parse_get_im_info],
0x61 : ['send all link command',  5, 6,  0,  do_nothing],
0x62 : ['std message',            8, 9,  0,  parse_std_cmd],
0x63 : ['x10 message',            4, 5,  0,  do_nothing],
0x64 : ['start all-linking',      4, 5,  0,  do_nothing],
0x65 : ['cancel all-linking',     2, 3,  0,  do_nothing],
0x66 : ['set host dev cat',       5, 6,  0,  do_nothing],
0x67 : ['reset im',               2, 3,  0,  do_nothing],
0x68 : ['set ack msg byte',       3, 4,  0,  do_nothing],
0x69 : ['get 1st all-link record',2, 3,  0,  do_nothing],
0x6d : ['led on',                 2, 3,  0,  do_nothing],
0x6d : ['led off',                2, 3,  0,  do_nothing],
0x73 : ['get im configuration',   2, 6,  0,  do_nothing],
}

# http://www.madreporite.com/insteon/insteon.html
sd_commands = {
0x0d: ['get_engine_version'],
0x0f: ['ping'],
0x10: ['id_request'],
0x11: ['light_on'],
0x12: ['light_on_fast'],
0x13: ['light_off'],
0x14: ['light_off'],
0x15: ['light_brighten_1_step'],
0x16: ['light_dim_1_step'],
0x17: ['light_start_manual_change'],
0x18: ['light_stop_manual_change'],
0x19: ['light_status_request'],
0x1f: ['get_operating_flags'],
0x2e: ['light_on_at_ramp_rate'],
0x2f: ['light_off_at_ramp_rate'],
}

x10_code_dict = {
0x6 : 'A',
0xE : 'B',
0x2 : 'C',
0xA : 'D',
0x1 : 'E',
0x9 : 'F',
0x5 : 'G',
0xD : 'H',
0x7 : 'I',
0xF : 'J',
0x3 : '11',
0xB : 'L',
0x0 : 'M',
0x8 : 'N',
0x4 : 'O',
0xC : 'P',
}

###########################################################################################################
# LOW LEVEN FUNCTIONS
#

def dbg(obj, level, msg):
    if obj.debug >= level:
        print obj.__unicode__()+ ": " + "  "*level + msg
    else:
        pass

###########################################################################################################
# Insteon Class
#
class InsteonPLM(object):
    '''
    Class used to connect to Insteon serial power line modem (PLM) 
    '''
    
    debug = 1; # Controls verbosity output
    Interface = None  

    def __init__(self, port='/dev/ttyUSB0'):
        '''        
        '''
        if os.name == 'nt':
            port = port -1
        try:        
            self.uart = serial.Serial(port=port, baudrate=19200, timeout=3)
            self.uart.timeout = 1
        except:
            self.uart = None
            print "Error occured while oppening serial Interface"
    
    def __del__(self):        
        if self.is_open():
            self.uart.close()
    
    def __unicode__(self):
        if self.uart is not None:
            name = "PLM(%s)" %  self.uart.port
        else:
            name = "PLM(None)"
            
        return name
            
    def is_open(self):
        return self.uart.isOpen()
    
    def __open__(self):
        if not(self.uart.isOpen()):            
            try:
                self.uart.open()
                dbg(self, 2, "Port %s is now open" % str(self.uart.port))
                return PORT_OPEN
            except uartial.uartialException:
                dbg(self, 0, "uartialException Cannot open port: %s " % str(self.uart.port))
                return PORT_ERROR
            except:
                dbg(self, 0, "OtherException Cannot open port: %s" % str(self.uart.port))
                return PORT_ERROR
        else:
            dbg(self, 2, "Port %s is already open" % str(self.uart.port))
            return PORT_OPEN
        
    def read(self):
        dbg(self, 2, "def read(self):")
        if self.uart is not None:
            data = self.uart.read(self.uart.inWaiting())
            dbg_msg = "read: %s" % str(data)
            dbg(self, 3, dbg_msg)
        else:
            dbg(self, 3, "No uartial connection")
            data = ''
        return data

    def send(self, cmd):
        if not isinstance(cmd, list):
            raise TypeError("cmd must be a list" )
        
        if len(cmd) < 2:
            raise ValueError("every insteon command must be at least 2 bytes long")
        
        if cmd[0] != 2:
            raise ValueError("All insteon commands must start with 0x02 (2 dec)")
        
        cmd_meta = cmd_dict.get(cmd[1], 0)
        if isinstance(cmd_meta, int) and cmd_meta == 0:
            raise ValueError("Command 0x{0:x} ({0}) was not found in command dictionary".format(cmd[1]))
        
        cmd_length = cmd_meta[1]
        
        if len(cmd) != cmd_length:
            raise ValueError('Command 0x{0:x} ({0}) - "{1}", must be {2} bytes'.format(cmd[1], cmd_meta[0], cmd_length))
            
        if self.is_open():
            out = self.uart.write(cmd)
        else:
            print "Serial port is not open"
            out = 0
        
        if out != cmd_length:
            print "Warning serial port sent {0} bytes while {1} were expected".format(out, cmd_length)
            
        return out

    def query(self, cmd, expected_response_length=None):
        # read data which could have arrived
        leftover_buffer = self.read()
        
        if not cmd_dict.has_key(cmd[1]):
            print "Command not found"
            return [None, leftover_buffer]
            
        cmd_details = cmd_dict.get(cmd[1])
        if expected_response_length is None:
            expected_response_length = cmd_details[2]
        
        # TODO this is bit of a hack and will not work for extended commands
        if cmd[1] == 0x62:
            expected_response_length += 11
        
        # print "Sending {0}, expecting response length of {1}".format(cmd_details[0], expected_response_length)    
        bytes_sent = self.send(cmd)
        
        timeout = 1
        to = time.time()
        tn = to
        response = ''
        n = 0
        
        while tn - to < timeout and n < expected_response_length:
            n  = self.uart.inWaiting()
            tn = time.time()
            
        if n >= expected_response_length:
            #response += self.Ser.read(cmd_details[2])        
            response += self.read()
            data = [ord(x) for x in response]
            dbg_msg = "cmd succesful: = {0}".format(data)
            return_data = data
        else:
            dbg_msg = "did not recive expected number of bytes within the time out period"
            return_data = self.read()
            
        return [return_data, leftover_buffer]


    def send_sd_cmd(self, *args):
        cmd    = build_sd_message(args[0], 15, args[1], args[2])
        res    = self.query(cmd)
        parsed = parse(res[0])[0]        
        ack_received = parsed[1][2]['flag'][1][0] == 1
        if ack_received:
            return [parsed[1][2]['cmd2'], parsed]
        else:
            return None

###########################################################################################################
# HIGH LEVEL FUNCTIONS
#

    def GetLightLevel(self, addr):
        out = self.send_sd_cmd(addr, 25, 0)
        return round(float(out[0])/2.55)

    def SetLightLevel(self, addr, level):
        if level < 0 or level > 100:
            raise ValueError("Light level must be between 0-100%")
        level = int(round(255*float(level)/100.0))
        out = self.send_sd_cmd(addr, 17, level)    
        return round(float(out[0])/2.55)

    def SetSwOff(self, addr):    
        out = self.send_sd_cmd(addr, 19, 0)
        return out

    def SetSwOn(self, addr):    
        out = self.send_sd_cmd(addr, 17, 255)
        return out

###########################################################################################################
# HIGH LEVEL FUNCTIONS
#
class InsteonSub(Thread):

    def __init__(self, plm, channel='insteon', host='127.0.0.1'):
        Thread.__init__(self)
        self.plm       = plm        
        self.redis     = redis.Redis(host=host)
        self.channel   = channel
        self.pubsub    = self.redis.pubsub()
        self.Log       = Logger('InsteonSub')
        self.Log.debug('__init__(channel=%s)' % self.channel)

        self.pubsub.subscribe(self.channel)
        self.start()
        self.setName('InsteonSub-Thread')

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
                            res = self.plm.send_sd_cmd(cmd_obj[0], cmd_obj[1], cmd_obj[2])
                            self.redis.publish(self.channel+"_res", serialize(res))

                        except Exception as E:
                            error_msg = {'source' : 'serinsteon:RedisSub', 'function' : 'def run(self):', 'error' : E.message}
                            self.redis.publish('error',serialize(error_msg))

                    else:
                        self.Log.debug(cmd)
        except Exception as E:
            error_msg = {'source' : 'InsteonSub', 'function' : 'def run(self):', 'error' : E.message}
            self.redis.publish('error',serialize(error_msg))
                
        self.Log.debug('end of run()')

def main(test=False):
    plm = InsteonPLM('/dev/ttyUSB1')
    plmsub = InsteonSub(plm)
    plmsub.log.level = 50

    try:
        while True:
            pass
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    print "================================"
    main()