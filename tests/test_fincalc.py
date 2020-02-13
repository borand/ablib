import unittest
import sys

sys.path.append('../')
from src.fincalc import Investments, Loan, run

class MyTestCase(unittest.TestCase):
    def test_investments_creation(self):
        tfsa = Investments("tfsa", 1000,1)
        run(tfsa,12)
        tfsa.summary()
        self.assertEqual(1,1)

    def test_load_creation(self):
        tfsa = Loan("mort", 100e3,3,25)
        run(tfsa,25*12)
        tfsa.summary()
        self.assertEqual(1,1)


if __name__ == '__main__':
    unittest.main()
