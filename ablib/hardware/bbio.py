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

import docopt
import Adafruit_BBIO.GPIO as GPIO

pins = ['P8_14']

def configio():
    for pin in pins:
        GPIO.setup(pin,GPIO.IN)

def getvalues():
    val = dict()
    for pin in pins:
        val[pin] = GPIO.input(pin)
    return val


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Naval Fate 2.0')
    print("===============================================")
    print(arguments)

    dev = arguments['--dev']

    print("===============================================")
    print(dev)

    run_test  = arguments['test']
    run_main  = arguments['run']

    if run_test:
        val = getvalues()
        for key in val.keys:
            print "pin {0} = {1}".format(key,val[key])

    if run_main:
        configio()
        try:
            while True:
                val = getvalues()
                for key in val.keys:
                    print "pin {0} = {1}".format(key,val[key])
        except KeyboardInterrupt:
            pass