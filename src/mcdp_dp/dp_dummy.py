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

    def solve(self, _func):
        minimals = self.R.get_minimal_elements()
        # print('solving %s' % _func.__repr__())
        # print('solving minimals %s' % minimals.__repr__())
        if not minimals: # pragma: no cover
            msg = 'No minimal elements for poset %s' % self.R
            raise_desc(DPInternalError, msg, ndp=self)

        return UpperSet(set(minimals), self.R)
    
    def evaluate(self, m):
        assert m == ()
        minimals = self.R.get_minimal_elements()
        ur = UpperSet(minimals, self.R)
        maximals = self.F.get_maximal_elements()
        lf = LowerSet(maximals, self.F)
        return lf, ur

mcdp_dev_warning('Remove Dummy name')

Dummy = Template

