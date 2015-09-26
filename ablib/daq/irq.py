import time
from daemon import runner
from daq_irq import IrqSubmit
from time import sleep

class App():
    def __init__(self):
        self.stdin_path   = '/dev/null'
        self.stdout_path  = '/dev/tty'
        self.stderr_path  = '/dev/tty'
        self.pidfile_path = '/tmp/irq.pid'
        self.pidfile_timeout = 5
        self.I = IrqSubmit(channel="data")
    
    def run(self):        
        while True:            
           sleep(10)


app = App()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()