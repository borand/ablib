"""pubtest.py - 

Simple module for communicating with ComPort firmware written for AVR328p.

Usage:
  pubtest.py [DELAY]
  pubtest.py (-h | --help)

Options:
  -h, --help
  DELAY              [default: 0]
"""

from ablib.util.message import Message
from docopt import docopt
from redis import Redis 
from datetime import datetime
from time import sleep
r = Redis()
timestamp = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')


def pubtest(delay=0):
	sleep(delay)
	m = Message()
	m.msg = {'data' : [["0",1]],'timestamp':timestamp}
	r.publish('data', m.as_json())
	print m.as_json()
	
	return 

if __name__ == "__main__":
	arguments = docopt(__doc__, version='Naval Fate 2.0')
	print(arguments)
	pubtest()