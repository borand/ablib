from datastore import submit
from redisbridge import Client


C = Client(host='192.168.1.133',channel='dt')
C.timeout = 30;

done = False
while not done:
	out = C.query('GetData')
	submit(out[1],submit_to="192.168.1.133",port=8000)