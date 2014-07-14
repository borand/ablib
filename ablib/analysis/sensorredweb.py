__author__ = 'andrzej'

hvac_output        = '101BBFD2010800A3'
office             = '10F3F1D201080060'
livingroom         = '109A3FD30108003A'
most_likely_office = '10EAB6D201080015'
outdoor            = '1030B8D2010800BC'
lab                = '1048B7D2010800EA'

#########################################################################################################################
#
#
#
#
import re
sn = '16.48.184.210.1.8.0.188'

def SerialNumberDec2Hex(sn):
    tmp = [int(x) for x in re.findall("(\d+)",sn)]

    sn = ''
    if len(tmp) == 8:
        for i in tmp:
            x = hex(i)[2:].upper()
            if len(x) == 1:
                x = '0'+x
            sn+=x
    else:
        pass
    return sn

print SerialNumberDec2Hex(sn)


df1 = p.DataFrame({"Outdoor" :get_sensordata(outdoor), "Livingroom" : get_sensordata(livingroom), "Office" : get_sensordata(office), \
                   "Lab" : get_sensordata(lab), "hvac" : get_sensordata(hvac_output)})


#########################################################################################################################
#
#
#
from requests import get, post
import simplejson as sj

old_host      = 'http://sensoredweb.herokuapp.com/sensordata/api'
old_host_auth = ()

new_host      = '192.168.1.10';
new_host_auth = ()
root_url      =  'http://{0}:8000/sensordata/api'.format(new_host)
headers       = {'content-type': 'application/json'}
print root_url

model_list = ['units', 'man', 'device', 'gateway', 'physicalsignal', 'location', 'deviceinstance']

def get_json(host, host_auth, model):
    out = get('{0}/units/.json'.format(old_host), auth=old_host_auth)
    if out.ok:
        return out.json()
    else:
        return []

def set_model_data(root_url, host_auth, model, data, headers={'content-type': 'application/json'}):
    if len(data) > 0:
        for unit in units:
            #print unit
            payload = sj.dumps(data)
            p = post('{0}/{1}/'.format(root_url,model), data=payload, auth=host_auth, headers=headers)
            print p.ok
    else:
        print('Data appears to be empty')


#########################################################################################################################
#
#
#

for model in model_list:
    data = get_json(old_host, old_host_auth, model)
    print "Model '{0}' : {1}".format(model,len(data))
    #set_model_data(root_url, host_auth, model, data)
#########################################################################################################################
#
#
#
def get_sensordata(sn, today=True):
    if today:
        temp  = get(url+sn+'/today/.json', auth=('andrzej','admin'))
    else:
        temp  = get(url+sn+'/.json', auth=('andrzej','admin'))
    if temp.ok:
        print 'Data OK'
        sensordata = np.array(temp.json())
        dates = sensordata[:,0] - 4*3600
        val   = sensordata[:,1]
        dates_row = p.to_datetime(dates,unit='s')
        ds = p.Series(val, index=dates_row)
    else:
        print temp
    return ds

T = get_sensordata('101BBFD2010800A3')