import socket
import logging
import requests
import datetime
import json
import paho.mqtt.client as mqtt
import redis

try:
    import numpy as np
    import pandas as pd

    have_np = True
except ImportError:
    have_np = False

from requests.auth import HTTPBasicAuth
from ablib.common import scan

# # Create a custom logger
# logger = logging.getLogger(__name__)
#
# # Create handlers
# c_handler = logging.StreamHandler()
# c_handler.setLevel(logging.INFO)
#
# # Create formatters and add it to handlers
# c_format = logging.Formatter(
#     '%(asctime)-8s| %(filename)-20s %(funcName)-20s |%(lineno)4d | %(levelname)9s | %(message)s', "%Y.%m.%d %H:%M")
# c_handler.setFormatter(c_format)
#
# # Add handlers to the logger
# # logger.addHandler(c_handler)
# logger.setLevel(logging.INFO)


class SensorDataDb:

    def __init__(self, port=8000, user='andrzej', pswd='admin'):
        self.ip = []
        self.port = port
        self.api_url = []
        self.user = user
        self.pswd = pswd

        self.find_all_servers()

    def find_all_servers(self):
        (ip_str, api_url) = scan.find_db_server(db_server_port=self.port)
        self.ip = ip_str
        self.api_url = api_url

    def is_db_server_online(self):

        if len(self.api_url) == 0:
            logging.error(
                "is_db_server_online()  :  Do not have a valid api_url, running find_db_server(), then try the function again")
            self.find_all_servers()

        db_server_online = [False] * len(self.ip)
        for server_ix, server_ip in enumerate(self.ip):
            try:
                pong_url = f'http://{server_ip}:{self.port}/ping'
                pong = requests.get(pong_url)
                if not pong.ok:
                    logging.warning("is_db_server_online()  :  Did not receive PONG")
                else:
                    # logging.debug("is_db_server_online()  :  got PONG from {} : {}".format(pong_url, pong.text))
                    db_server_online[server_ix] = True

            except Exception as ex:
                logging.error("is_db_server_online()  : {}".format(ex))

        return db_server_online

    def fetch_url(self, url_cmd, as_json=True):

        if not any(self.is_db_server_online()):
            logging.error("No database servers are online")
            pass
        num_of_servers = len(self.ip)

        error_flag = [False] * num_of_servers
        error_msg = [None] * num_of_servers
        api_raw = [None] * num_of_servers

        for ix, server_url in enumerate(self.api_url):
            try:
                if not url_cmd[0] == '/':
                    url_cmd = '/' + url_cmd

                api_out = requests.get(server_url + url_cmd)
                error_flag[ix] = api_out.status_code

                if api_out.ok:
                    if as_json:
                        api_raw[ix] = api_out.json()
                    else:
                        api_raw[ix] = api_out.text
                else:
                    logging.error(f"   request error: {api_raw[ix]}")
                    error_msg[ix] = api_raw

            except ConnectionError as e:
                logging.error(f"   Connection error: {e}")
                error_msg[ix] = e

        return api_raw, error_flag, error_msg

    def get_table(self, table_name, field=None):

        tables, status_codes, err_msg = self.fetch_url(table_name)
        if len(tables) == 0:
            return

        for ix, t in enumerate(tables):
            if status_codes[ix] == 200:
                if field is not None:
                    tables[ix] = [f[field] for f in t]
                else:
                    pass

        return tables

    def register_device_instance(self, sn):
        logging.debug("register_device_instance({})".format(sn))
        api_data = {
            "device": 1,
            "accept_from_gateway_only": False,
            "update_rate": "1.000",
            "update_threshold": "0.250",
            "active": True,
            "private": False,
            "serial_number": sn,
            "user": 1,
            "gateway": 1,
            "location": None,
            "physical_signal": 1
        }
        registered_serial_numbers = self.get_table('deviceinstance', 'serial_number')

        for ix, db in enumerate(self.api_url):
            if sn not in registered_serial_numbers[ix]:
                api_out = requests.post('{}/deviceinstance/?format=api'.format(self.api_url[ix]),
                                        json=api_data,
                                        auth=HTTPBasicAuth(self.user, self.pswd))
                if api_out.ok:
                    logging.debug(f"SN: {sn} REGISTERED in {self.api_url[ix]}")
                else:
                    logging.debug("  api_out = {}".format(api_out))
            else:
                logging.debug(f"SN: {sn} already exists in {self.api_url[ix]}")

    def update_table(self, url, table, data):
        logging.debug("update_table({}, {})".format(table, data))

        r = requests.post('{}/{}/?format=api'.format(url, table),
                          json=data,
                          auth=HTTPBasicAuth(self.user, self.pswd))

        if r.status_code == 200 or r.status_code == 201:
            logging.info(f"Registered the gateway {url}, status code {r.status_code}")
        else:
            logging.error("update_table() : status code {}".format(r.status_code))
        return r

    def register_gateway(self):
        """

        """

        # TODO This function is just wrong
        try:
            gateway_ip = scan.get_host_ip()
            gateways = self.get_table('gateway', 'address')
            if len(gateways) == 0:
                return

            for ix, gateway_in_db in enumerate(gateways):
                if gateway_ip not in gateway_in_db:
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
                    self.update_table(self.api_url[ix], 'gateway', gateway_data)

        except Exception as err:
            logging.error("Exception: {0}".format(err))

    def submit_data_to_db(self, data_list, timestamp=None):
        logging.debug("submit_data_to_db()")

        if timestamp is None:
            timestamp = datetime.datetime.now()

        # API format
        # (?P < datestamp > \d{4}\-\d{1, 2}\-\d{1, 2}-\d{1, 2}:\d{1, 2}:\d{1, 2}\.* \d{0, 6})
        timestamp_str = timestamp.strftime("%Y-%m-%d-%H:%M:%S")

        for db_url in self.api_url:
            for sd in data_list:

                try:
                    sn = sd[0]
                    val = sd[1]

                    url = f'{db_url}/sub/{timestamp_str}/sn/{sn}/val/{val}'
                    api_out = requests.get(url)
                    if api_out.ok:
                        logging.debug(api_out.json())
                    else:
                        logging.warning("api_out code: {} api_out text: {}".format(api_out.status_code, api_out.text))

                except Exception as ex:
                    logging.error(ex)

    def get_days_data(self, sn, yy, mo, dd, days=1, db_ix=0):
        logging.debug(f"get_days_data({sn}, {yy}, {mo}, {dd})")
        t = datetime.date(yy, mo, dd)
        t = t + datetime.timedelta(days=days)
        yy2 = t.year
        mo2 = t.month
        dd2 = t.day

        if not self.is_db_server_online():
            return

        data_url = f'{self.api_url[db_ix]}/data/sn/{sn}/from/{yy}-{mo}-{dd}/to/{yy2}-{mo2}-{dd2}'
        logging.debug(f"   full api url: {data_url}")

        api_out = {"status": 0}
        try:
            api_raw = requests.get(data_url)
            if api_raw.ok:
                api_out = api_raw.json()
            else:
                logging.error(f"   request error: {api_raw}")
        except ConnectionError as e:
            logging.error(f"   Connection error: {e}")

        return api_out


class Publisher:

    def __init__(self, mqtt_server=None, redis_server=None):

        if redis_server is None:
            self.redis_server_list = scan.find_redis_servers(redis_server)
        else:
            self.redis_server_list = redis_server

        if mqtt_server is None:
            self.mqtt_server_list = scan.find_mqtt_brokers(mqtt_server)
        else:
            self.mqtt_server_list = mqtt_server

        self.db = SensorDataDb()

        self.mqqt_topic = 'sensors/data'
        self.redis_channel = 'sensors/data'

        # Keep a local copy of serial number
        self._gateway = scan.get_host_ip() + ' ' + socket.gethostname()

        self._api_urls_of_db = self.db.api_url
        self._serial_numbers_in_db = []
        self._serial_numbers_in_db_last_updated = []

        self._update_serial_number()
        logging.info(f"Publiser(@{self._gateway})")
        logging.info(f"   sendor db: {self.db.ip}")
        logging.info(f"        mqtt: {self.mqtt_server_list}")
        logging.info(f"       redis: {self.redis_server_list}")

    def __repr__(self):
        return f"Publiser(@{self._gateway})"

    def __str__(self):
        return self.__repr__()

    def _update_serial_number(self):
        self._api_urls_of_db = self.db.api_url
        self._serial_numbers_in_db = self.db.get_table('deviceinstance', 'serial_number')
        self._serial_numbers_in_db_last_updated = datetime.datetime.now()

    def publish_data(self, dataset):
        """
        Submits data to database and publishes results to all pub/sub channels

        :param dataset: dictionary of readings containing serial number, value pairs.
        :return:
        """
        timestamp = dataset["timestamp"]

        if len(dataset.keys()) == 0:
            logging.info("No data to publish")
            return

        logging.info(f"Publishing {dataset} @ {timestamp}")

        for entry in dataset["data"]:
            sn = entry[0]
            self.db.register_device_instance(sn)

        self.db.submit_data_to_db(dataset["data"], timestamp)

        # Publish data to redis server
        for redis_server in self.redis_server_list:
            try:
                r = redis.Redis(redis_server)
                for entry in dataset["data"]:
                    r.set(f'{entry[0]}', f'{entry[1]}')
                logging.info(f"  published to redis")
            except Exception as e:
                logging.error(e)

        # Publish data to MQTT broker
        for mqtt_server in self.mqtt_server_list:
            try:
                client = mqtt.Client("Test")
                client.connect(mqtt_server, keepalive=60)

                for entry in dataset["data"]:
                    client.publish(f'{self.mqqt_topic}/{entry[0]}', json.dumps({'val': entry[1]}))
                    out = client.publish(f'{self.mqqt_topic}', json.dumps(entry))
                    logging.debug(f"Published {entry} to mqtt: {out.is_published()}")
                logging.info(f"  published to mqtt topick {self.mqqt_topic}")

            except Exception as e:
                logging.error(e)


def json_to_np(json_data, sec=False, resample=False):
    if not have_np:
        logging.error(f"This function requires NumPy and Pandas installed")
    else:
        sensordata = np.array(json_data['data'])
        dates = sensordata[:, 0] - 5 * 3600
        data = sensordata[:, 1]

        if sec:
            dates_row = dates - dates[0]
        else:
            dates_row = np.array(dates).astype('datetime64[s]')

        df = pd.DataFrame(data={'time': dates_row, 'data': data}, index=dates_row)

        if resample:
            df = df.resample('1S').ffill()
        api_out = df
    return api_out


if __name__ == '__main__':

    p = Publisher()
    data = {'timestamp': datetime.datetime.now(), 'data': [['z', 0], ['q', 1], ['x', 0], ['y', 1]]}
    p.publish_data(data)
