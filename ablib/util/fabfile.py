from fabric.api import run, env, local
import psutil
import sh

__author__ = 'andrzej'
env.hosts = ['localhost']

ROOT_DIR = '~'

PROCESS_OF_INTEREST = ['comport.py', 'rtweb.py', 'daq_irq.py', 'manage.py', '/venv/bin/rqworker', 'daq_digitemp.py']

def get_python_process_list():
    plist = []
    print "======================================================="
    print "= get_python_process_list()"
    print "="
    process_list = psutil.process_iter()
    for x in process_list:

        if len(x.cmdline) > 0 and 'venv/bin/python' in x.cmdline[0]:
            if any([p in x.cmdline[1] for p in PROCESS_OF_INTEREST]):
                print "{0} : {1}".format(x.pid, x.cmdline[1])
                plist.append(x)
    print "======================================================="
    return plist

def kill():
    process_list = get_python_process_list()
    for p in process_list:
        p.kill()

if __name__ == '__main__':
    get_python_process_list()


def host_type():
    run('uname -s')

def restart():
    kill()
    start()
    ps()

def rtweb():
    venv = ROOT_DIR + '/venv/bin/python'
    cmd  = '~/projects/realtime/rtweb/rtweb.py'
    full_cmd = '{0} {1} > /dev/null &'.format(venv,cmd)
    local(full_cmd)

def sensorweb():
    venv = ROOT_DIR + '/venv/bin/python'
    cmd  = ROOT_DIR + '/projects/sensoredweb/manage.py runserver 0.0.0.0:8000'
    full_cmd = 'nohup {0} {1} > /dev/null &'.format(venv,cmd)
    #full_cmd = 'nohup {0} {1} > sensoredweb.log &'.format(venv,cmd)
    #print
    full_cmd = '~/projects/sensoredweb/venv/bin/python ~/projects/sensoredweb/manage.py runserver 0.0.0.0:8000 > /dev/null &'

    local(full_cmd)

def comport():
    venv = ROOT_DIR + '/venv/bin/python'
    cmd = ROOT_DIR + '/projects/ablib/ablib/hardware/comport.py run --redishost 127.0.0.1'
    full_cmd = 'nohup {0} {1} > /dev/null &'.format(venv,cmd)
    #print full_cmd
    local(full_cmd)

def daq():
    venv = ROOT_DIR + '/venv/bin/python'
    cmd = ROOT_DIR + '/projects/ablib/ablib/daq/daq_irq.py'
    full_cmd = 'nohup {0} {1} run --redishost localhsot > /dev/null &'.format(venv,cmd)
    #print full_cmd
    local(full_cmd)

    venv = ''
    cmd = ROOT_DIR + '/venv/bin/rqworker'
    full_cmd = 'nohup {0} {1} > /dev/null &'.format(venv,cmd)
    #print full_cmd
    local(full_cmd)

def digitemp():
    venv = ROOT_DIR + '/venv/bin/python'
    cmd = ROOT_DIR + '/projects/ablib/ablib/daq/daq_digitemp.py'
    full_cmd = 'nohup {0} {1} > /dev/null &'.format(venv,cmd)
    local(full_cmd)

def start():
    sensorweb()
    comport()
    rtweb()
    daq()
    digitemp()


def ps():
    get_python_process_list()
