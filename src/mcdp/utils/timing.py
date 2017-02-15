from contextlib import contextmanager
import time

__all__ = [
    'timeit', 
    'timeit_wall',
]

@contextmanager
def timeit(desc, minimum=None):
    from mcdp import logger
    t0 = time.clock()
    yield
    t1 = time.clock()
    delta = t1 - t0
    if minimum is not None:
        if delta < minimum:
            return
    logger.debug('timeit %s: %.2f s (>= %s)' % (desc, delta, minimum))


@contextmanager
def timeit_wall(desc, minimum=None):
    from mcdp import logger
    t0 = time.time()
    yield
    t1 = time.time()
    delta = t1 - t0
    if minimum is not None:
        if delta < minimum:
            return
    logger.debug('timeit(wall) %s: %.2f s (>= %s)' % (desc, delta, minimum))