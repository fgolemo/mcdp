# -*- coding: utf-8 -*-
from contextlib import contextmanager
import time
import sys

from mcdp.logs import logger_performance

__all__ = [
    'timeit', 
    'timeit_wall',
]

@contextmanager
def timeit(desc, minimum=None, logger=None):
    logger = logger or logger_performance
#     logger.debug(f'timeit {desc} ...')
    
    # time.clock() is deprecated in Python 3.3 and removed in Python 3.8
    # Use process_time() in Python 3, clock() in Python 2
    if sys.version_info[0] >= 3:
        t0 = time.process_time()
    else:
        t0 = time.clock()
        
    yield
    
    if sys.version_info[0] >= 3:
        t1 = time.process_time()
    else:
        t1 = time.clock()
        
    delta = t1 - t0
    if minimum is not None:
        if delta < minimum:
            return
    logger.debug(f'timeit result: {delta:.2f} s (>= {minimum}) for {desc}')

@contextmanager
def timeit_wall(desc, minimum=None, logger=None):
    logger = logger or logger_performance
    logger.debug(f'timeit {desc} ...')
    t0 = time.time()
    yield
    t1 = time.time()
    delta = t1 - t0
    if minimum is not None:
        if delta < minimum:
            return
    logger.debug(f'timeit result: {delta:.2f} s (>= {minimum})')
    