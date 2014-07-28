"""daq_digitemp.py -

module used to acquire temperature readings with digitemp_DS2490 and submit the data to sensoredweb

Usage:
  daq_digitemp.py test
  daq_digitemp.py run
  daq_digitemp.py (-h | --help)

Options:
  -h, --help
"""

from redis import Redis
from rq import Queue
from logbook import Logger
from docopt import docopt
from ablib.daq.datastore import submit
from ablib.util.common import get_host_ip
import ablib.hardware.digitemp as dt
import datetime
from submit import submit

# TO BE DELETED
# done = False
# while not done:
# 	out = C.query('GetData')
# 	if out[0] == 0:
# 		try:
# 			data_set = [y[1:] for y in out[1]]
# 			submit(out[1],submit_to="192.168.1.10",port=8000, threshold=0.5)
# 		except:
# 			pass

def StarDigitempSubmit(channel, host='0.0.0.0', submit_to='192.168.1.10'):
    """
    :param channel:   - publish channel
    :param host:      - redis host
    :param submit_to: - server running sensoredweb
    :return:          - no ret value

    data_set = [[0, '1030B8D2010800BC', 20.1875],
     [1, '1002BDD2010800ED', 22.375],
     [2, '10F237C0010800D6', 23.5625],
     [3, '10EAB6D201080015', 22.9375],
     [4, '109A3FD30108003A', 23.9375],
     [5, '10F3F1D201080060', 22.875],
     [6, '101BBFD2010800A3', 22.75],
     [7, '109729C001080020', 24.875]]
    """

    print"StartIqrSubmit(%s, %s, %s)" % (channel, host, submit_to)
    D = dt.Digitemp()
    Q = Queue(connection=Redis())
    threshold = 0.5;
    try:
        not_done = True
        while not_done:
            timestamp = datetime.datetime.now()
            data_set     = D.GetData()
            last_enqueue = Q.enqueue(submit, data_set,\
                                    timestamp=timestamp,\
                                    submit_to=submit_to,\
                                    threshold=threshold)
            #not_done = False

    except KeyboardInterrupt:
        pass
    print "Exiting " + __name__

##########################################################################################
if __name__ == "__main__":
    arguments = docopt(__doc__, version='Naval Fate 2.0')
    print("===============================================")
    print(arguments)

    dev = arguments['--dev']

    if arguments['run']:
        channel   = 'digitemp'
        host      = get_host_ip()
        submit_to = arguments.get('--submit_to', get_host_ip())
        StarDigitempSubmit(channel, host, submit_to)