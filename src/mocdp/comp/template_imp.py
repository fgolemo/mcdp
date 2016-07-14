from mcdp_dp import PrimitiveDP
from mcdp_posets import SpaceProduct, UpperSet
from mocdp.exceptions import mcdp_dev_warning

__all__ = [
    'Dummy',
    'Template',
]


class Template(PrimitiveDP):
    def __init__(self, F, R):
        M = SpaceProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, M=M)
    def solve(self, _func):
        minimals = [self.R.get_bottom()]
        return UpperSet(set(minimals), self.R)

mcdp_dev_warning('Remove Dummy name')

Dummy = Template
