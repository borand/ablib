import logging
import os
import glob
import re
import time

from ablib.common.sensordatadb import SensorDataDb

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
        self.devices_dir = '/sys/bus/w1/devices/'
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

    def register_all_devices(self):
        logger.debug('register_all_devices()')
        sn_list = self.list_devices()

        if len(sn_list) == 0:
            return

        for sn in sn_list:
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

if __name__  == '__main__':

    ow = RPiOneWire()
    ow.register_node()
    ow.register_all_devices()
    while True:
        ow.submit_data_to_db()
        time.sleep(1)