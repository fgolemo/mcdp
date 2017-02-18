# -*- coding: utf-8 -*-
import os

from contracts import contract
from mcdp import MCDPConstants

from .safe_pickling import safe_pickle_dump, safe_pickle_load


__all__ = ['memo_disk_cache2']

@contract(cache_file='str')
def memo_disk_cache2(cache_file, data, f):
    """ 
        
        
    """
    from mcdp import logger

    dirname = os.path.dirname(cache_file)
    cachedir = os.path.join(dirname)
    if not os.path.exists(cachedir):
        try:
            os.makedirs(cachedir)
        except:
            if os.path.exists(cachedir):
                pass
            else:
                raise

    if os.path.exists(cache_file):
        # logger.info('Reading from cache %r.' % cache_file)
        try:
            res = safe_pickle_load(cache_file)
            if data != res['data']:
                logger.info('Stale cache, recomputing.')
            else:
                return res['result']
        except Exception as e:
            logger.error(e)

    result = f()

    if MCDPConstants.log_cache_writes:
        logger.info('Writing to cache %s.' % cache_file)
    res = dict(data=data, result=result)
    
    safe_pickle_dump(res, cache_file)
    

    return result
