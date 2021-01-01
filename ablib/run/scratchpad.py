from selenium import webdriver
import re
from time import sleep
import datetime
re_snr = re.compile('SNR Margin \(dB\)\:\s*(-{0,1}\d+\.\d+)\s*(-{0,1}\d+\.\d+)')
re_at_rate = re.compile('Attainable Rate \(Kbps\)\:\s(\d+)\s(\d+)')
re_rate = re.compile('(?:\r\n|\r|\n)Rate \(Kbps\)\:\s(\d+)\s(\d+)')

d = webdriver.Firefox()
d.implicitly_wait(3)

fid = open('teksavyy.csv','w')

try:
    while True:
        d.get('http://192.168.1.1/admin/landingpage.fwd')
        out = d.find_elements_by_class_name('stats')
        res = out[1].text
        snr_dB = re_snr.findall(res)
        attainable_rate = re_at_rate.findall(res)
        my_rate = re_rate.findall(res)
        print(f"Down: SNR {snr_dB[0][0]}, Attainable Rate: {attainable_rate[0][0]}, My Rate:  {my_rate[0][0]}")
        timestamp = datetime.datetime.now().strftime("%Y.%d.%m %H:%M:%S")
        fid.writelines(f"{timestamp}, {snr_dB[0][0]}, {attainable_rate[0][0]}, {my_rate[0][0]}\n")
        #fid.writelines(res)
        sleep(3)
except KeyboardInterrupt:
    pass
print('Closing selenium connection')
d.quit()
print('Closing file')
fid.close()
print('All done')