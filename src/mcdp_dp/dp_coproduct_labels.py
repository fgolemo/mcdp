from contracts import contract
from contracts.utils import check_isinstance
from mcdp_posets import Coproduct1, Coproduct1Labels
from mocdp.exceptions import do_extra_checks

from .dp_coproduct import CoProductDP
from .primitive import PrimitiveDP
from mcdp_dp.primitive import NotFeasible


__all__ = [
    'CoProductDPLabels',
]

class CoProductDPLabels(PrimitiveDP):
    """ Wrap to allow labels for the implementations. """

    @contract(dp=CoProductDP)
    def __init__(self, dp, labels):
        check_isinstance(dp, CoProductDP)

        self.dp = dp
        self.labels = labels

        I0 = dp.get_imp_space()

        check_isinstance(I0, Coproduct1)
        M = Coproduct1Labels(I0.spaces, labels)
        
        F = dp.get_fun_space()
        R = dp.get_res_space()
        PrimitiveDP.__init__(self, F=F, R=R, I=M)

    def evaluate(self, m):
        label = m[0]
        i = self.labels.index(label)
        m0 = i, m[1]
        return self.dp.evaluate(m0)

    def get_implementations_f_r(self, f, r):
        try:
            m0s = self.dp.get_implementations_f_r(f, r)
        except NotFeasible:
            raise
        res = []
        for m0 in m0s:
            i = m0[0]
            label = self.labels[i]
            m = label, m0[1]

            res.append(m)

        if do_extra_checks():
            for imp in res:
                self.I.belongs(imp)

        return set(res)

    # For solve and solve_r, we don't care about implementations at all
    def solve(self, f):
        return self.dp.solve(f)

    def solve_r(self, r):
        return self.dp.solve_r(r)

    def __repr__(self):
        s = "^".join('%s:%s' % x for x in zip(self.labels, self.dp.dps))
        return 'CoProductDPLabels(%s)' % s

    def repr_long(self):
        s = "CoProductDPLabels %s " % self.labels.__repr__()
        s += '\n' + self.dp.repr_long()
        return s