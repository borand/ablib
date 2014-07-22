import ablib.hardware.digitemp as dt
from submit import submit


done = False
while not done:
	out = C.query('GetData')	
	if out[0] == 0:
		try:
			data_set = [y[1:] for y in out[1]]
			submit(out[1],submit_to="192.168.1.10",port=8000, threshold=0.5)
		except:
			pass

def StartIqrSubmit(channel, host, submit_to):
    print"StartIqrSubmit(%s, %s, %s)" % (channel, host, submit_to)
    try:

        while True:
            pass
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
        channel   = 'rtweb'
        host      = get_host_ip()
        submit_to = arguments.get('--submit_to', get_host_ip())
        StartIqrSubmit(channel, host, submit_to)