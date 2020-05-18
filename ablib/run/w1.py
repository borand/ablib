import logging
from ablib.sensors import onewire


def start(args):
    logging.info(f'Starting 1-wire acquisition, args: {args}')
    onewire.run()
