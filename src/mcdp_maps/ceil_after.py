from mcdp_posets import Map
import numpy as np



class CeilAfter(Map):
    """ Applies a function and rounds it to int. """

    def __init__(self, f, dom, cod):
        self.f = f
        Map.__init__(self, dom, cod)

    def _call(self, x):
        if np.isinf(x):
            return self.cod.get_top()

        y = self.f(x * 1.0)
        if np.isinf(y):
            return self.cod.get_top()

        y = int(np.ceil(y))
        return y

    def __repr__(self):
        if hasattr(self.f, '__name__'):
            fn = getattr(self.f, '__name__')
            return 'ceil(%s(.))' % fn
        else:
            return 'ceil(%s(.))' % self.f




