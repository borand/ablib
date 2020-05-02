import argparse
import re
import sh
import socket
import redis
import subprocess
from serial.tools import list_ports
import json
from time import sleep
from datetime import datetime
import logging
import requests
import paho.mqtt.client as mqtt

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
    ports = list_ports.comports()
    return [p.device for p in ports]

def find_redis_servers():
    logger.debug("find_redis_servers() start")
    redis_servers = []
    pinged_hosts = ping_all()
    pinged_hosts.append('127.0.0.1')
    for host_ip in pinged_hosts:
        try:
            r = redis.Redis(host=host_ip, socket_timeout=0.1, socket_connect_timeout=0.1,)
            r.ping()
            redis_servers.append(host_ip)
        except Exception as ex:
            logger.error(ex)

    return redis_servers

def find_mqtt_brokers():
    logger.debug("find_mqtt_brokers() start")
    mqtt_brokers = []
    pinged_hosts = ping_all()
    pinged_hosts.append('127.0.0.1')
    client = mqtt.Client("Test")
    for host_ip in pinged_hosts:
        try:
            out = client.connect(host_ip, keepalive=1)
            if out==0:
                mqtt_brokers.append(host_ip)
        except Exception as ex:
            logger.debug(ex)

    return mqtt_brokers

def ping(ip='192.168.50.1', wait=1):
    status, result = subprocess.getstatusoutput("ping -c1 -W{} {} ".format(wait, ip))
    # return True when ping successful
    return (not status, result)

def ping_all():
    """
    From: https://stackoverflow.com/questions/14038606/fastest-way-to-ping-a-network-range-and-return-responsive-hosts
    :return:
    """
    status, result = subprocess.getstatusoutput('nmap -T5 -sP 192.168.50.0-255')
    ip_re = re.compile("(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")
    return ip_re.findall(result)


if __name__ == "__main__":
    #print(find_db_server())
    #print(get_host_ip())
    print("Redis servers: {}".format(find_redis_servers()))
