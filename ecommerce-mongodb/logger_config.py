import logging
import sys

# Create a logger
logger = logging.getLogger('app')
logger.setLevel(logging.INFO)

# Create a console handler and set its level to debug
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)

# Add formatter to handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(ch)


