import logging
from logging.handlers import RotatingFileHandler
from logging import handlers
import sys

from colorama import init
from termcolor import colored


log = logging.getLogger('')
log.setLevel(logging.DEBUG)
format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(format)
log.addHandler(ch)

fh = handlers.RotatingFileHandler('./log.log', maxBytes=(1048576*5), backupCount=7)
fh.setFormatter(format)
log.addHandler(fh)

logging.basicConfig(filename='example.log',level=logging.DEBUG)
logging.debug(colored('This message should go to the log file',"red"))
logging.info('So should this')
logging.warning('And this, too')
