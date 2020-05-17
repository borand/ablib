import unittest
import sys

sys.path.append('../')
import ablib.common.scan as scan


class TestScan(unittest.TestCase):

    def test_get_host_ip(self):
        scan.get_host_ip()
        self.assertTrue(True)

    def test_find_db_server(self):
        scan.find_db_server()
        self.assertTrue(True)

    def test_find_redis_servers(self):
        scan.find_redis_servers()
        self.assertTrue(True)

    def test_find_mqtt_brokers(self):
        scan.find_mqtt_brokers()
        self.assertTrue(True)

    def test_scan_serial_ports(self):
        scan.scan_serial_ports()
        self.assertTrue(True)

    def test_ping(self):
        scan.ping()
        self.assertTrue(True)

    def test_ping_all(self):
        scan.ping_all()
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
