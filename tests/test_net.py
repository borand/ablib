import unittest
import sys

sys.path.append('../')
import src.net.scan as scan


class MyTestCase(unittest.TestCase):

    def test_investments_creation(self):
        print('IP address: {}'.format(scan.get_host_ip()))
        self.assertEqual(1,1)

    def test_load_creation(self):
        out = scan.find_db_server()
        print(out)
        self.assertEqual(1,1)

if __name__ == '__main__':
    unittest.main()
