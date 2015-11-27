import time

def time_poset_minima_func(f):
    def ff(elements, leq):
        class Storage:
            nleq = 0
        def leq2(a, b):
            Storage.nleq += 1
            return leq(a, b)
        t0 = time.clock()
        res = f(elements, leq2)
        delta = time.clock() - t0
        n1 = len(elements)
        n2 = len(res)
        if n1 == n2:
            if False:
                if n1 > 10:
                    print('unnecessary leq!')
                    print('poset_minima %d -> %d t = %f s nleq = %d leq = %s' %
                          (n1, n2, delta, Storage.nleq, leq))
        return res
    return ff
