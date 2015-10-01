"""daq.py -

module used to listen for new data on the redis channel and submit the data to sensoredweb

Usage:
  daq.py test [--submit_to=SUBMIT_TO] [--redishost=REDISHOST]
  daq.py run  [--submit_to=SUBMIT_TO] [--redishost=REDISHOST]
  daq.py (-h | --help)

Options:
  -h, --help  
  --submit_to=SUBMIT_TO  [default: 127.0.0.1]
  --redishost=REDISHOST  [default: 127.0.0.1]

"""

from ablib.daq.datastore import submit

from celery import Celery

app = Celery('daq', broker='redis://localhost', backend='redis://localhost')

@app.task
def add(x, y):
    return x + y