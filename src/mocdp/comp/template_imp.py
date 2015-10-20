from mocdp.comp.wrap import SimpleWrap
from mocdp.dp.primitive import PrimitiveDP
from mocdp.lang.syntax import parse_wrap, unit_expr
from mocdp.posets import PosetProduct, SpaceProduct, UpperSet

__all__ = [
    'template',
]

class Template(PrimitiveDP):
    def __init__(self, F, R):
        M = SpaceProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, M=M)
    def solve(self, _func):
        minimals = [self.R.get_bottom()]
        return UpperSet(set(minimals), self.R)
Dummy = Template

def template(functions, resources):
    
    fnames = list(functions)
    rnames = list(resources)

    get_space = lambda x: parse_wrap(unit_expr, x)[0]

    Fs = tuple(get_space(functions[x]) for x in fnames)
    Rs = tuple(get_space(resources[x]) for x in rnames)

    F = PosetProduct(Fs)
    R = PosetProduct(Rs)

    if len(fnames) == 1:
        F = F[0]
        fnames = fnames[0]
    if len(rnames) == 1:
        R = R[0]
        rnames = rnames[0]

    return SimpleWrap(Template(F, R), fnames, rnames)
