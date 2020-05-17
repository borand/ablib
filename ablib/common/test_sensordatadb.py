import unittest
import datetime
import ablib.common.sensordatadb as sdb


class TestSensorDataDb(unittest.TestCase):

    def setUp(self) -> None:
        self.s = sdb.SensorDataDb()

    def tearDown(self) -> None:
        pass

    def test_find_all_servers(self):
        self.s.find_all_servers()
        self.assertTrue(True)

    def test_register_device_instance(self):
        self.s.register_device_instance('y')
        self.assertTrue(True)

    def test_register_gateway(self):
        self.s.register_gateway()
        self.assertTrue(True)

    def test_submit_data_to_db(self):
        self.s.submit_data_to_db([['y', 1]])
        self.assertTrue(True)

    def test_get_days_data(self):
        self.s.get_days_data('y', 2020, 5, 15)
        self.assertTrue(True)


class TestPublisher(unittest.TestCase):

    def setUp(self) -> None:
        self.p = sdb.Publisher()

    def tearDown(self) -> None:
        pass

    def test_publish_data(self):
        data = {'timestamp': datetime.datetime.now(), 'data': [['z', 0], ['q', 1], ['x', 0], ['y', 1]]}
        self.p.publish_data(data)
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
