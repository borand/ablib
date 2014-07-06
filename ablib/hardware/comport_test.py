import comport


C = comport.Comport('/dev/ttyUSB0')
C.start_thread()
out = C.query('idn')