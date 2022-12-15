"""Top-level package for Text justifier."""

import logging



# *** DEFINITIONS ***
__author__ = """Alastair Irvine"""
__email__ = 'alastair@plug.org.au'
__version__ = '0.9.0'

root_logger = None  # logging.Logger
params = {}


# *** FUNCTIONS ***
def init_logging(loglevel: int) -> logging.Logger:
    global root_logger

    root_logger = logging.getLogger()
    logging.basicConfig(level=loglevel)

    return root_logger
