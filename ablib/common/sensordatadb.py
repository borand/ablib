import socket
import logging
import requests
import re
import time
from requests.auth import HTTPBasicAuth

from ablib.common import scan

# Create a custom logger
logger = logging.getLogger(__name__)

# Create handlers
c_handler = logging.StreamHandler()
c_handler.setLevel(logging.DEBUG)

# Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.setLevel(logging.DEBUG)

crc = re.compile(r"crc=\w{2} (\w+)")
t_C = re.compile(r"t=(-*\d+)")
sn_expr = re.compile(r'/(\w{2}-\w*)/w1_slave')

class SensorDataDb():

    def __init__(self, port, user='andrzej', pswd='admin'):
        (ip_num, ip_str, api_url) = scan.find_db_server(db_server_port=port)
        self.ip = ip_str
        self.port = port
        self.api_url = api_url
        self.user = user
        self.pswd = pswd

    def is_db_server_online(self):

        db_server_online = False
        if len(self.api_url) == 0:
            logger.error("is_db_server_online()  :  Do not have a valid api_url, try running find_db_server() first")

        try:
            pong_url = 'http://{}:{}/ping'.format(self.ip, self.port)
            pong = requests.get(pong_url)
            if not pong.ok:
                logger.warning("is_db_server_online()  :  Did not receive PONG")
            else:
                # logger.debug("is_db_server_online()  :  got PONG from {} : {}".format(pong_url, pong.text))
                db_server_online = True

        except Exception as ex:
            logger.error("is_db_server_online()  : {}".format(ex))

        return db_server_online

    def get_table(self, table_name, field=''):

        table = []
        if not self.is_db_server_online():
            return table

        api_out = requests.get('{}/{}.json'.format(self.api_url, table_name))

        if api_out.status_code == 404:
            logger.warning(" did not find tablename {}".format(table_name))
        if api_out.status_code == 200:
            table = api_out.json()
            if len(field) > 0:
                # "get_table({},{}) - requested field dows not exist in the table schema".format(table_name, field))
                assert(field in table[0])
                return  [d[field] for d in table]

        return table

    def register_device_instance(self, sn):
        logger.debug("register_device_instance({})".format(sn))
        api_data = {
            "device": 1,
            "accept_from_gateway_only": False,
            "update_rate": "1.000",
            "update_threshold": "0.250",
            "active": False,
            "private": False,
            "serial_number": sn,
            "user": 2,
            "gateway": 1,
            "location": None,
            "physical_signal": 1
        }

        if not self.is_db_server_online():
            return

        try:
            full_api_url = '{}/deviceinstance.json'.format(self.api_url)
            api_out = requests.get(full_api_url)
            # logger.debug("api_out = {}".format(api_out.status_code))
        except Exception as ex:
            logger.error("Cound not register device: {}")
            return

        registered_serial_numbers = [d['serial_number'] for d in api_out.json()]

        if not sn in registered_serial_numbers:
            api_out = requests.post('{}/deviceinstance/?format=api'.format(self.api_url),
                                    json=api_data,
                                    auth=HTTPBasicAuth(self.user, self.pswd))
            print(api_out.text)
            if api_out.ok:
                logger.debug("SN: {} REGISTERED".format(sn))
            else:
                logger.debug("  api_out = {}".format(api_out))
        else:
            logger.debug("SN: {} already exists in DB".format(sn))

    def update_table(self, table, data):
        logger.debug("update_table({}, {})".format(table, data))

        r = requests.post('{}/{}/?format=api'.format(self.api_url, table),
                          json=data,
                          auth=HTTPBasicAuth(self.user, self.pswd))
        if r.status_code == 200:
            logger.info("Registered the gateway")
        else:
            logger.error("update_table() : status code {}".format(r.status_code))
        return r

    def register_gateway(self):
        """
        :param db_server_ip: - last digit of the gateway IP
        :return: True if the gateway was registered False if DB IP was invalid or could not register the gateway
        """

        if not self.is_db_server_online():
            return

        try:
            gateway_ip =scan.get_host_ip()
            gateways = self.get_table("gateway")
            if gateway_ip in [g['address'] for g in gateways]:
                logger.info("register_gateway() : gateway {} already registered in {}".format(gateway_ip, self.ip))
                return

            if not self.gateway_registered:
                gateway_data = {
                    "id": 2,
                    "name": socket.gethostname(),
                    "address": gateway_ip,
                    "port": 8888,
                    "protocol": "rest",
                    "url": "http://{}".format(gateway_ip),
                    "mac_address": "none",
                    "active": True,
                    "process_name": "",
                    "process_pid": 0,
                    "description": ""
                }

                r = self.update_table('gateway',gateway_data)
                if r.ok:
                    logger.info("Registered the gateway")

        except Exception as err:
            print("Exception: {0}".format(err))

    def submit_data_to_db(self, sensor_data):
        logger.debug("submit_data_to_db()")

        if not self.is_db_server_online():
            logger.debug("submit_data_to_db() - DB server seems to be offline")
            return

        for sd in sensor_data:
            serial_number = sd[0]
            sensor_value = sd[1]

            url = '{0}api/sub/now/sn/{1}/val/{2}'.format(self.api_url, serial_number, sensor_value)
            try:
                api_out = requests.get(url)
                if api_out.ok:
                    logger.debug(api_out.json())
                else:
                    logger.warning("api_out code: {} api_out text: {}".format(api_out.status_code, api_out.text))

            except Exception as ex:
                logger.error(ex)

if __name__  == '__main__':

    db = SensorDataDb(8000)
    db.is_db_server_online()
    db.get_table("gateway")
    db.register_gateway()
    db.register_device_instance("0")
    sensor_data = [["0", 1]]
    db.submit_data_to_db(sensor_data)