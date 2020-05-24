import logging
from ablib.sensors import onewire

try:
    import systemd.daemon
    systemd_loaded = True
except:
    systemd_loaded = False
    pass


def start(args):
    logging.info(f'Starting 1-wire acquisition, args: {args}')
    if systemd_loaded:
        try:
            systemd.daemon.notify('READY=1')
        except:
            pass

    onewire.run()
