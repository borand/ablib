from ablib.util.message import Message
from redis import Redis 
from datetime import datetime
r = Redis()
timestamp = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')

m = Message()
m.msg = {'data' : [["0",1]],'timestamp':timestamp}

r.publish('data', m.as_json())