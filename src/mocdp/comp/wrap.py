from contracts import contract, raise_wrapped
from mocdp.comp.interfaces import NamedDP
from mocdp.dp.primitive import PrimitiveDP
from mocdp.posets.poset_product import PosetProduct
from mocdp.posets.uppersets import UpperSet

class SimpleWrap(NamedDP):
    def __init__(self, dp, fnames, rnames):
        self.dp = dp
        self._rnames = rnames
        self._fnames = fnames

    def get_dp(self):
        return self.dp

    def get_fnames(self):
        return self._fnames

    def get_rnames(self):
        return self._rnames

    def __repr__(self):
        return 'Wrap(%s|%s|%s)' % (self._fnames, self.dp, self._rnames)

class LiftRToProduct(PrimitiveDP):
    """ Returns a new DP with ProductPoset of length 1 """

    def __init__(self, dp):
        self.dp = dp

        F0 = dp.get_fun_space()
        R0 = dp.get_res_space()

        if isinstance(R0, PosetProduct):
            raise ValueError('R already product')

        F = F0
        R = PosetProduct((R0,))
        PrimitiveDP.__init__(self, F=F, R=R)


class LiftToProduct(PrimitiveDP):
    """ Returns a new DP with ProductPoset of length 1 """
    
    def __init__(self, dp):
        self.dp = dp
        
        F0 = dp.get_fun_space()
        R0 = dp.get_res_space()

        if isinstance(F0, PosetProduct):
            raise ValueError('F already product')
        if isinstance(R0, PosetProduct):
            raise ValueError('R already product')

        F = PosetProduct((F0,))
        R = PosetProduct((R0,))
        PrimitiveDP.__init__(self, F=F, R=R)


    @contract(returns=UpperSet)
    def solve(self, func):
        '''
            Given one func point,
            Returns an UpperSet 
        '''
        raise NotImplementedError()


@contract(dp=PrimitiveDP, returns=NamedDP, fnames='seq(str)', rnames='seq(str)')
def dpwrap(dp, fnames, rnames):
    try:
        # assume that dp has product spaces of given length

        F = dp.get_fun_space()
        R = dp.get_res_space()

        if not isinstance(F, PosetProduct) or not len(F) == len(fnames):
            raise ValueError("F incompatible")

        if not isinstance(R, PosetProduct) or not len(R) == len(rnames):
            raise ValueError("R incompatible")

        return SimpleWrap(dp, fnames, rnames)

    except Exception as e:
        msg = 'Cannot wrap primitive DP.'
        raise_wrapped(ValueError, e, msg, dp=dp, fnames=fnames, rnames=rnames)

def dploop(ndp, s1, s2):
    pass


