"""
general utility functions

LL2017
"""

import logging

def basic_logging_setup(level=logging.WARNING):
    fmt = '%(asctime)s %(levelname)s (%(module)s.%(funcName)s()): %(message)s'
    logging.basicConfig(format=fmt, level=level)