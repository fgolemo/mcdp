# -*- coding: utf-8 -*-
from collections import defaultdict
import fnmatch
import os

from contracts import contract
from mcdp import MCDPConstants, logger
import time
from contracts.utils import check_isinstance


__all__ = [
    'locate_files',
]



@contract(returns='list(str)', directory='str',
          pattern='str|list(str)', followlinks='bool')
def locate_files(directory, pattern, followlinks=True,
                 include_directories=False,
                 include_files=True,
                 normalize=True,
                 ignore_patterns=None):
    """
        pattern is either a string or a sequence of strings
        ignore_patterns = ['*.bak']
    """
    t0 = time.time()
    if ignore_patterns is None:
        ignore_patterns = MCDPConstants.locate_files_ignore_patterns 
    
    if isinstance(pattern, str):
        patterns = [pattern]
    else:
        patterns = list(pattern)
        for p in patterns:
            check_isinstance(p, str)
            
    # directories visited
    visited = set()
    # print('locate_files %r %r' % (directory, pattern))
    filenames = []
    
    def matches_pattern(x):
        return any(fnmatch.fnmatch(x, p) for p in patterns)
    
    def should_ignore_resource(x):
        return any(fnmatch.fnmatch(x, ip) for ip in ignore_patterns) 

    def accept_dirname_to_go_inside(root, d):
        if should_ignore_resource(d):
            return False
        dd = os.path.realpath(os.path.join(root, d))
        if dd in visited:
            return False
        visited.add(dd)
        return True
    
    def accept_dirname_as_match(d):
        return include_directories and \
               not should_ignore_resource(d) and \
               matches_pattern(d)
    
    def accept_filename_as_match(fn):
        return include_files and \
               not should_ignore_resource(fn) and \
               matches_pattern(fn)
    
    ntraversed = 0
    for root, dirnames, files in os.walk(directory, followlinks=followlinks):
        ntraversed += 1
        dirnames[:]  = [_ for _ in dirnames if accept_dirname_to_go_inside(root, _)]
        for f in files:
            if accept_filename_as_match(f):
                filename = os.path.join(root, f)
                filenames.append(filename)
        for d in dirnames:
            if accept_dirname_as_match(d):
                filename = os.path.join(root, d)
                filenames.append(filename)

    if normalize:
        real2norm = defaultdict(lambda: [])
        for norm in filenames:
            real = os.path.realpath(norm)
            real2norm[real].append(norm)
            # print('%s -> %s' % (real, norm))

        for k, v in real2norm.items():
            if len(v) > 1:
                msg = 'In directory:\n\t%s\n' % directory
                msg += 'I found %d paths that refer to the same file:\n'
                for n in v:
                    msg += '\t%s\n' % n
                msg += 'refer to the same file:\n\t%s\n' % k
                msg += 'I will silently eliminate redundancies.'
                logger.warning(v)

        filenames = list(real2norm.keys())

    seconds = time.time() - t0
    if seconds > 5:
        n = len(filenames)
        nuniques = len(set(filenames))
        logger.debug('%.4f s for locate_files(%s,%s): %d traversed, found %d filenames (%d uniques)' % 
              (seconds, directory, pattern, ntraversed, n, nuniques))
    return filenames
