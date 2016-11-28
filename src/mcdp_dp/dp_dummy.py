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
            msg = 'No maximal elements for poset %s' % self.R
            raise_desc(DPInternalError, msg, ndp=self)

        return self.F.Ls(maximals)
    
    def evaluate(self, m):
        assert m == ()
        minimals = self.R.get_minimal_elements()
        ur = UpperSet(minimals, self.R)
        maximals = self.F.get_maximal_elements()
        lf = LowerSet(maximals, self.F)
        return lf, ur
    
    def repr_h_map(self):
        try:
            bot = self.R.get_bottom()
            return "f ⟼ {%s}" % self.R.format(bot)
        except:
            els = self.R.get_minimal_elements()
            con = ", ".join( self.R.format(_) for _ in els)
            return "f ⟼ {%s}" % con
        
    def repr_hd_map(self):
        try:
            top = self.F.get_top()
            return "r ⟼ {%s}" % self.R.format(top)
        except:
            els = self.F.get_maximal_elements()
            con = ", ".join( self.F.format(_) for _ in els)
            return "r ⟼ {%s}" % con
        

mcdp_dev_warning('Remove Dummy name')

Dummy = Template

