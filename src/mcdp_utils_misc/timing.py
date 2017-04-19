# -*- coding: utf-8 -*-
from contextlib import contextmanager
import time

from mcdp.logs import logger_performance

__all__ = [
    'timeit', 
    'timeit_wall',
]

@contextmanager
def timeit(desc, minimum=None, logger=None):
    logger = logger or logger_performance
#     logger.debug('timeit %s ...' % desc)
    t0 = time.clock()
    yield
    t1 = time.clock()
    delta = t1 - t0
    if minimum is not None:
        if delta < minimum:
            return
    logger.debug('timeit result: %.2f s (>= %s) for %s' % (delta, minimum, desc))

@contextmanager
def timeit_wall(desc, minimum=None, logger=None):
    logger = logger or logger_performance
    logger.debug('timeit %s ...' % desc)
    t0 = time.time()
    yield
    t1 = time.time()
    delta = t1 - t0
    if minimum is not None:
        if delta < minimum:
            return
    logger.debug('timeit result: %.2f s (>= %s)' % (delta, minimum))
    