import os, os.path as p
import logzero
import logging
from logzero import logger

LOG_LEVEL = getattr(logging, os.environ.get('LOGLEVEL', 'INFO'))

logdir = p.expanduser("~/logs")
os.makedirs(logdir, exist_ok=True)
logfile = "logs.txt"

# Setup rotating logfile with 3 rotations, each with a maximum filesize of 1MB:
logzero.logfile(p.join(logdir, logfile), maxBytes=1e6, backupCount=3)
logzero.loglevel(LOG_LEVEL)
