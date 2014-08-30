"""bbio.py -

Simple module for communicating with ComPort firmware written for AVR328p.

Usage:
  bbio.py test
  bbio.py run
  bbio.py (-h | --help)

Options:
  -h, --help
"""

__author__ = 'andrzej'

from docopt import docopt
from ablib.util.message import Message
from redis import Redis
from time import sleep

try:
    import Adafruit_BBIO.GPIO as GPIO
    LIVE = 1;
except:
    LIVE = 0;

pins = ['P8_14']

def configio():
    if LIVE:
        for pin in pins:
            GPIO.setup(pin,GPIO.IN)

def getvalues():
    val = dict()
    for pin in pins:
        if LIVE:
            val[pin] = GPIO.input(pin)
        else:
            val[pin] = -1;
    return val

def main(test=False):
    M = Message()
    R = Redis()
    configio()
    try:
        while True:
            val = getvalues()
            for key in val.keys():
                msg = {'sn' : key, 'data' : [val[key]]}
                M.msg = msg;
                R.publish('rtweb', M.as_json())
                print "pin {0} = {1}".format(key,val[key])
                if test:
                    return M
                else:
                    sleep(1)

    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Naval Fate 2.0')
    print("===============================================")
    print(arguments)
    print("===============================================")
    
    run_test  = arguments['test']
    run_main  = arguments['run']

    if run_test:
        val = getvalues()
        for key in val.keys:
            print "pin {0} = {1}".format(key,val[key])

    if run_main:
        main()
