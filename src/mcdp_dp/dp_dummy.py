# -*- coding: utf-8 -*-
from contracts.utils import raise_desc
from mcdp_dp import PrimitiveDP
from mcdp_posets import LowerSet, SpaceProduct, UpperSet
from mocdp.exceptions import DPInternalError, mcdp_dev_warning


__all__ = [
    'Dummy',
    'Template',
]

class Template(PrimitiveDP):

    def __init__(self, F, R):
        I = SpaceProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, I=I)

    def solve(self, _f):
        minimals = self.R.get_minimal_elements()
        if not minimals: 
            msg = 'No minimal elements for poset %s' % self.R
            raise_desc(DPInternalError, msg, ndp=self)

        return self.R.Us(minimals)
    
    def solve_r(self, _r):
        maximals = self.F.get_maximal_elements()
        if not maximals:
            msg = 'No minimal elements for poset %s' % self.R
            raise_desc(DPInternalError, msg, ndp=self)

        return self.F.Ls(maximals)
    
    def evaluate(self, m):
        assert m == ()
        minimals = self.R.get_minimal_elements()
        ur = UpperSet(minimals, self.R)
        maximals = self.F.get_maximal_elements()
        lf = LowerSet(maximals, self.F)
        return lf, ur

mcdp_dev_warning('Remove Dummy name')

Dummy = Template

