import re
import sh
import socket
import redis
import subprocess
import logging
import requests
import paho.mqtt.client as mqtt

from serial.tools import list_ports

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


def get_hostname():
    return (sh.hostname().strip(), sh.hostname('-I').strip())


def find_db_server(hosts=None, db_server_port=8000):
    """
    :param hosts: - None or list of ip addresses to scan for database servers
    :param db_server_port: - default port of the db server
    :return:
    """
    if hosts is None:
        hosts = []
    logger.debug("find_db_server() start")
    full_db_server_ip = []
    api_url = []

    if len(hosts) == 0:
        hosts = ping_all()

    for ip_str in hosts:
        try:
            out = requests.get(f'http://{ip_str}:8000/ping', timeout=0.05)
            if out.ok:
                full_db_server_ip.append(ip_str)
                api_url.append(f'http://{ip_str}:{db_server_port}/api')
        except:
            pass

    return full_db_server_ip, api_url


def scan_serial_ports():
    ports = list_ports.comports()
    return [p.device for p in ports]


def find_redis_servers(hosts=None) -> list:
    if hosts is None:
        hosts = []
    logger.debug("find_redis_servers() start")

    redis_servers = []
    if len(hosts) == 0:
        hosts = ping_all()

    for host_ip in hosts:
        try:
            r = redis.Redis(host=host_ip, socket_timeout=0.1, socket_connect_timeout=0.1, )
            r.ping()
            redis_servers.append(host_ip)
        except Exception as ex:
            # logger.error(ex)
            pass

    return redis_servers


def find_mqtt_brokers(hosts=None) -> list:
    if hosts is None:
        hosts = []
    logger.debug("find_mqtt_brokers() start")

    mqtt_brokers = []
    if len(hosts) == 0:
        hosts = ping_all()

    client = mqtt.Client("Test")
    for host_ip in hosts:
        try:
            logger.debug("   attempting to reach {}".format(host_ip))
            out = client.connect(host_ip, keepalive=1)
            if out == 0:
                mqtt_brokers.append(host_ip)
        except Exception as ex:
            logger.debug(ex)

    return mqtt_brokers


def ping(ip='192.168.50.1', wait=1):
    status, result = subprocess.getstatusoutput("ping -c1 -W{} {} ".format(wait, ip))
    # return True when ping successful
    return not status, result


def ping_all():
    """
    From: https://stackoverflow.com/questions/14038606/fastest-way-to-ping-a-network-range-and-return-responsive-hosts
    :return:
    """
    status, result = subprocess.getstatusoutput('nmap -T5 -sP 192.168.50.0-255')
    pinged_ips = ['127.0.0.1']
    if status == 0:
        ip_re = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")
        pinged_ips.extend(ip_re.findall(result))
    else:
        logger.error(result)
        if "nmap: not found" in result:
            logger.error("You are missing nmap program try using: logger.error(result) to speedup ping scan")

        for ip in range(2, 255):
            ip_str = f"192.168.50.{ip}"
            out = ping(ip_str)
            if out[0]:
                pinged_ips.append(ip_str)

    return pinged_ips


if __name__ == "__main__":
    ping()
    hosts = ping_all()
    find_db_server(hosts)
    find_mqtt_brokers(hosts)
    find_redis_servers(hosts)
    scan_serial_ports()