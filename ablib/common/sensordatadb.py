import socket
import logging
import requests
import re
import datetime
import json


from requests.auth import HTTPBasicAuth
import paho.mqtt.client as mqtt

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

    def __init__(self, port=8000, user='andrzej', pswd='admin'):
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
            logger.error("Exception: {0}".format(err))

    def submit_data_to_db(self, sensor_data, timestamp=None):
        logger.debug("submit_data_to_db()")

        if not self.is_db_server_online():
            logger.debug("submit_data_to_db() - DB server seems to be offline")
            return

        if timestamp is None:
            timestamp = datetime.datetime.now()

        # API format
        # (?P < datestamp > \d{4}\-\d{1, 2}\-\d{1, 2}-\d{1, 2}:\d{1, 2}:\d{1, 2}\.* \d{0, 6})
        timestamp_str = timestamp.strftime("%Y-%m-%d-%H:%M:%S")

        for sd in sensor_data:

            try:
                serial_number = sd[0]
                sensor_value = sd[1]

                url = '{0}api/sub/{1}/sn/{2}/val/{3}'.format(self.api_url, timestamp_str, serial_number, sensor_value)
                api_out = requests.get(url)
                if api_out.ok:
                    logger.debug(api_out.json())
                else:
                    logger.warning("api_out code: {} api_out text: {}".format(api_out.status_code, api_out.text))

            except Exception as ex:
                logger.error(ex)


class Publisher():

    def __init__(self, mqtt_server=[], redis_server=[]):
        self.db = SensorDataDb()
        self.reids_list = scan.find_redis_servers(redis_server)
        self.mqtt_list = scan.find_mqtt_brokers(mqtt_server)
        self.mqqt_topick  = 'sensors/data'
        self.redis_channel = 'sensors/data'

        # Keep a local copy of serial number
        self._gateway = scan.get_host_ip() + ' ' + socket.gethostname()
        self._serial_numbers_in_db = []
        self._serial_numbers_in_db_last_updated = []

        self._update_serial_number()

    def _update_serial_number(self):

        if self.db.is_db_server_online():
            device_instance = self.db.get_table('deviceinstance')
            self._serial_numbers_in_db = [x['serial_number'] for x in device_instance]
            self._serial_numbers_in_db_last_updated = datetime.datetime.now()
        else:
            logger.info("Cannot query database, the database is not online and not responding to ping")

    def publish_data(self, data={}):
        """
        Submits data to database and publishes results to all pub/sub channels

        :param data: dictionary of readings containing serial number, value pairs.
        :return:
        """

        if len(data.keys()) == 0:
            logger.info("No data to publish")
            return

        timestamp = data["timestamp"]

        for entry in data["data"]:
            sn  = entry[0]
            if sn not in self._serial_numbers_in_db:
                self.db.register_device_instance(sn)
                self._update_serial_number()

        self.db.submit_data_to_db(data["data"], timestamp)

        if len(self.reids_list) != 0:
            pass


        if len(self.mqtt_list) != 0:
            client = mqtt.Client("Test")
            client.connect(self.mqtt_list[0], keepalive=1)

            for entry in data["data"]:
                client.publish(self.mqqt_topick, json.dumps(entry))








if __name__  == '__main__':

    # db = SensorDataDb(8000)
    # db.is_db_server_online()
    # db.get_table("gateway")
    # db.register_gateway()
    # db.register_device_instance("0")
    sensor_data = [["0", 1]]
    ts = datetime.datetime.now()
    # db.submit_data_to_db(sensor_data)
    p = Publisher(mqtt_server=['192.168.50.3'], redis_server=['127.0.0.1'])
    p.publish_data({'timestamp': ts, 'data': [['0', 1]]})