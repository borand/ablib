import sys
from sh import whoami


my_paths = ['/ablib/ablib','/Daq328p/daq328p/hardware','/digitemPy/digitempy']
for path in my_paths:
	user = whoami()
	sys.path.append('/home/'+whoami().stdout[:-1]+'/projects' + path)