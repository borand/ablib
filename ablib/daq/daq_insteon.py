 from datetime import datetime
import insteon as I

from datastore import submit


plm = I.InsteonPLM()
plm.log.level = 50

timestamp = datetime.now()
val = []
for device in I.all_devices:        
    tmp  = plm.GetSwitchStatus(device)
    if tmp is not None:
        val.append([0, hex2str(device), tmp])
print submit(val,submit_to="192.168.1.133",port=8000,timestamp='')
plm.stop()