__author__ = 'andrzej'

import unittest
import ablib.hardware.bbio as bbio
from ablib.util.message import Message
import unittest

class FooTests(unittest.TestCase):

    def testFoo(self):
        self.failUnless(True)

    def testBBIO(self):
        out = bbio.getvalues()
        self.assertIsInstance(out, dict)
        self.assertEqual(out["P8_14"],-1)

    def test_main(self):
        m = bbio.main(test=True)
        self.assertIsInstance(m, Message)
        self.assertEquals(m.msg['data'][0],-1)

def main():
    unittest.main()

if __name__ == '__main__':
    main()
