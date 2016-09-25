from abc import abstractmethod

from mcdp_posets import Map
from mcdp_posets import Rcomp
from mcdp_posets import RcompUnits
import numpy as np


__all__ = ['CeilMap', 'FloorMap', 'SquareMap', 'SqrtMap']


class GenericFloatOperation(Map):
    """ 
        Applies a function to a float and rounds it to the next integer,
        maintaining the float representation. 
        
        Can be used for Rcomp or Rcompunits.
    """

    def __init__(self, dom, name):
        assert isinstance(dom, (Rcomp, RcompUnits))
        Map.__init__(self, dom, dom)
        self.name = name

    def _call(self, x):
        if np.isinf(x):
            return self.cod.get_top()

        y = self.op(x)
        if np.isinf(y):
            return self.cod.get_top()

        return y
    
    def diagram_label(self):
        return self.name

    @abstractmethod
    def op(self, x):
        pass
    
    def __repr__(self):
        return '%s(%s->%s)' % (self.name, self.dom, self.cod)
    
    
class CeilMap(GenericFloatOperation):
    """ 
        Applies a function to a float and rounds it to the next integer,
        maintaining the float representation. 
        
        Can be used for Rcomp or Rcompunits.
    """

    def __init__(self, dom):
        GenericFloatOperation.__init__(self, dom, 'ceil')

    def op(self, x):
        return np.ceil(x)
    

class FloorMap(GenericFloatOperation):

    def __init__(self, dom):
        GenericFloatOperation.__init__(self, dom, 'floor')

    def op(self, x):
        return np.floor(x)
    
class SquareMap(GenericFloatOperation):

    def __init__(self, dom):
        GenericFloatOperation.__init__(self, dom, 'square')

    def op(self, x):
        return x * x

class SqrtMap(GenericFloatOperation):

    def __init__(self, dom):
        GenericFloatOperation.__init__(self, dom, 'sqrt')

    def op(self, x):
        return np.sqrt(x)
