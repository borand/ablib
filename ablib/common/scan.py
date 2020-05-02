import argparse
import time
import re
import sh
import socket
import serial
import json
from time import sleep
from datetime import datetime
import logging
import requests

#
logger = logging.getLogger("net.scan")
logger.level = 10
logger.setLevel(logging.INFO)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(filename)10s:%(lineno)3d | %(name)15s | %(levelname)10s | %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def get_host_ip():
    """
    parses ifconfig system command and returns host ip
    """
    ip = '127.0.0.1'
    try:
        # Get IP by pinging google DNS server
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except:
        # Get IP by parsing ifconfig shell command
        ip_exp = re.compile(r'(?:inet*.)(\d{1,3}\.\d{1,3}.\d{1,3}.\d{1,3})', re.DOTALL)
        ip_out = ip_exp.findall(sh.ifconfig().stdout.decode('utf-8'))
        if len(ip_out) > 0:
            ix = [x.__contains__('192') for x in ip_out]
            if ix.count(True):
                ip = ip_out[ix.index(True)]
    return ip

def find_db_server(db_server_port=8000):
    logger.debug("find_db_server() start")
    valid_ip = 0
    full_db_server_ip = ''
    api_url = ''
    for x in range(2, 255):
        try:
            out = requests.get('http://192.168.50.{}:8000/ping'.format(x), timeout=0.05)
            valid_ip = x
            if out.ok:
                full_db_server_ip = "192.168.50.{}".format(valid_ip)
                api_url = 'http://{}:{}/api'.format(full_db_server_ip, db_server_port)
                break
        except:
            pass

    logger.info('Valid IP: {}'.format(valid_ip))
    return (valid_ip, full_db_server_ip, api_url)

def scan_serial_ports():
    pass
    # # self.log.debug('run()')
    # ports = serial.tools.list_ports.comports()
    # for p in ports:
    #     # self.log.debug("Attempting to open port {}".format(self.port))
    #     self.serial = serial.Serial(port, 115200)
    #     self.serial.timeout = 1
    #     time.sleep(1)
    #     self.open()
    #     self.send('idn')
    #     done = self.read('idn',1)[0]
    #     if done:
    #         # self.log.info("Found hydro sensor on port {}".format(self.serial.port))
    #         self.alive = True
    #         return
    #     else:
    #         self.close()
    #         self.serial.__del__()
    # # self.log.info("Did not find hydro sensor port :(")


if __name__ == "__main__":
    print(find_db_server())
    print(get_host_ip())
