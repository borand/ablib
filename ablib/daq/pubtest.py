from ablib.util.message import Message
from redis import Redis 
from datetime import datetime
from time import sleep
r = Redis()
timestamp = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')


def pubtest(delay=0):
	m = Message()
	m.msg = {'data' : [["0",1]],'timestamp':timestamp}
	r.publish('data', m.as_json())
	print m.as_json()
	sleep(delay)
	return 

if __name__ == "__main__":
	pubtest()