import unittest
import sys

sys.path.append('../')
import ablib.common.sensordatadb as sdb


class TestScan(unittest.TestCase):

    def setUp(self) -> None:
        self.s = 0

    def tearDown(self) -> None:
        pass

    def test_get_host_ip(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
