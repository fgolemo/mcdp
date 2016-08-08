from mcdp_dp.primitive import PrimitiveDP
from mocdp.memoize_simple_imp import memoize_simple

__all__ = [
    'CacheDP',
]


class CacheDP(PrimitiveDP):
    
    def __init__(self, dp):
        self.dp = dp
        F = dp.F
        R = dp.R
        I = dp.I
        PrimitiveDP.__init__(self, F, R, I)

    @memoize_simple
    def solve(self, f):
        return self.dp.solve(f)

    @memoize_simple
    def evaluate(self, i):
        return self.dp.evaluate(i)
