'''
Created on 2012-12-29

@author: borand
'''
import re
import sh
#import logging
#import sys

def get_host_ip():
    """
    parses ifconfig system command and returns host ip
    """
    ip_exp = re.compile(r'(?:eth\d.*?inet addr\:)(\d{1,3}\.\d{1,3}.\d{1,3}.\d{1,3})',re.DOTALL)
    ip_out = ip_exp.findall(sh.ifconfig().stdout)    
    if len(ip_out) > 0:        
        return  ip_out[0]
    else:
        return '127.0.0.1'
    

if __name__ == "__main__":
    print "get_host_ip: ", get_host_ip()