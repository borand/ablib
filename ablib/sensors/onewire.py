import logging
import os
import glob
import re
import datetime
import time

from pathlib import Path
from itertools import compress

from ablib.common.sensordatadb import SensorDataDb, Publisher
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

class RPiOneWire():

    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.devices_dir = '/sys/bus/w1/devices/'
        if not os.path.exists(self.devices_dir):
            self.devices_dir = BASE_DIR + '/../fixtures'
        self.db = SensorDataDb(8000, user='pi', pswd='t2yCVyjzS4fVsAN')

    def register_node(self):
        """
        :param db_server_ip: - last digit of the gateway IP
        :return: True if the gateway was registered False if DB IP was invalid or could not register the gateway
        """
        self.db.register_gateway()

    def list_devices(self):
        logger.debug('list_devices()')

        if not os.path.isdir(self.devices_dir):
            logger.info("list_devices() did not find {} dir, no devices found".format(self.devices_dir))
            return []

        dev_sn = []
        logger.debug("  Devices found:")
        for dev in glob.glob(self.devices_dir + '/*/w1_slave'):
            sn = dev.split('/')[-2]
            dev_sn.append(sn)
            logger.debug("     {}".format(sn))
        return dev_sn

    def register_all_devices(self, sn_list=[]):
        logger.debug('register_all_devices()')

        if len(sn_list) == 0:
            sn_list = self.list_devices()

        if len(sn_list) == 0:
            return
        di = self.db.get_table('deviceinstance')
        db_sn = [x['serial_number'] for x in di]

        for sn in sn_list:
            if sn not in db_sn:
                self.db.register_device_instance(sn)

    def get_sensor_data(self):
        logger.debug("get_sensor_data()")
        sensor_data = []

        for ii in glob.glob(self.devices_dir + '/*/w1_slave'):
            fid = open(ii, 'r')
            raw = fid.readlines()
            fid.close()

            if len(raw) == 2:
                if "YES" in crc.findall(raw[0]):
                    temp = t_C.findall(raw[1])
                    sn = sn_expr.findall(ii)

                    if len(temp) == 1:
                        try:
                            temp_c = float(temp[0]) / 1000
                            # out = {"sn": sn[0], "temp": temp_c}
                            sensor_data.append([sn[0], temp_c])
                            logger.debug("    {} : {}".format(sn[0], temp_c))
                        except Exception as ex:
                            logger.error(ex)

        return sensor_data

def run(pause_sec=1):

    # Save PID file
    homedir = str(Path.home())
    fn = __name__
    now = datetime.datetime.now()
    timestamp = now.strftime('%Y_%m_%d_%H%M%s')
    pid_filename = homedir + '/'  + fn.split('.')[-1] + '_PID.txt'

    # Save pid file with timestamp
    fid = open(pid_filename,'w')
    fid.writelines(timestamp)
    fid.close()

    row = RPiOneWire()
    p = Publisher(mqtt_server=['192.168.50.3'], redis_server=['127.0.0.1'])

    pid = Path(pid_filename)
    # Start loop
    while pid.exists():
        data = row.get_sensor_data()
        p.publish_data({'timestamp': datetime.datetime.now(), 'data': data})
        time.sleep(pause_sec)


    # register new devices in db
    #
    # get temperature readings
    #
    # Save to onewire.json file
    # check if db online if not scan for db
    # submit data to db
    #
    # publish data to reids
    # publish data to mqtt
    # publish state to mqtt



if __name__  == '__main__':

    ow = RPiOneWire()
    p = Publisher(mqtt_server=['192.168.50.3'], redis_server=['127.0.0.1'])

    data = ow.get_sensor_data()
    p.publish_data({'timestamp':datetime.datetime.now(), 'data':data})

