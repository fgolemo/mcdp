# -*- coding: utf-8 -*-
import time
import sys

def time_poset_minima_func(f):
    def ff(elements, leq):
        class Storage:
            nleq = 0
        def leq2(a, b):
            Storage.nleq += 1
            return leq(a, b)
        
        # time.clock() is deprecated in Python 3.3 and removed in Python 3.8
        # Use process_time() in Python 3, clock() in Python 2
        if sys.version_info[0] >= 3:
            t0 = time.process_time()
        else:
            t0 = time.clock()
            
        res = f(elements, leq2)
        
        if sys.version_info[0] >= 3:
            delta = time.process_time() - t0
        else:
            delta = time.clock() - t0
            
        n1 = len(elements)
        n2 = len(res)
        if n1 == n2:
            if False: # pragma: no cover
                if n1 > 10:
                    print('unnecessary leq!')
                    print(f'poset_minima {n1} -> {n2} t = {delta} s nleq = {Storage.nleq} leq = {leq}')
        return res
    return ff
