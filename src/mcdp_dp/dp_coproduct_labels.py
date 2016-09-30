from contracts import contract
from contracts.utils import check_isinstance
from mcdp_posets import Coproduct1, Coproduct1Labels
from mocdp.exceptions import do_extra_checks

from .dp_coproduct import CoProductDP
from .primitive import PrimitiveDP


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

        M0 = dp.get_imp_space_mod_res()

        assert isinstance(M0, Coproduct1), M0
        M = Coproduct1Labels(M0.spaces, labels)
        
        F = dp.get_fun_space()
        R = dp.get_res_space()
        PrimitiveDP.__init__(self, F=F, R=R, I=M)

    def evaluate(self, m):
        label = m[0]
        i = self.labels.index(label)
        m0 = i, m[1]
        return self.dp.evaluate(m0)
        
    def evaluate_f_m(self, f, m):
        """ Returns the resources needed
            by the particular implementation m """
        label = m[0]
        i = self.labels.index(label)
        m0 = i, m[1]
        return self.dp.evaluate_f_m(f, m0)

    def get_implementations_f_r(self, f, r):
        """ Returns a nonempty set of thinks in self.M.
            Might raise NotFeasible() """
        m0s = self.dp.get_implementations_f_r(f, r)
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

    def solve(self, f):
        return self.dp.solve(f)

    def __repr__(self):
        s = "^".join('%s:%s' % x for x in zip(self.labels, self.dp.dps))
        return 'CoProductDPLabels(%s)' % s

    def repr_long(self):
        s = "CoProductDPLabels %s " % self.labels.__repr__()
        s += '\n' + self.dp.repr_long()
        return s