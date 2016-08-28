# -*- coding: utf-8 -*-
from .primitive import NormalForm, NotFeasible, PrimitiveDP
from contracts import contract
from contracts.utils import check_isinstance, indent, raise_desc
from mcdp_posets import (
    Coproduct1, Coproduct1Labels, Map, NotBelongs, NotEqual, PosetProduct,
    UpperSet, UpperSets, get_types_universe, poset_minima)
from mocdp.exceptions import do_extra_checks

__all__ = [
    'CoProductDP',
    'CoProductDPLabels',
]


class CoProductDP(PrimitiveDP):
    """ Returns the co-product of 1+ dps. """

    @contract(dps='tuple,seq[>=1]($PrimitiveDP)')
    def __init__(self, dps):
        check_isinstance(dps, tuple)
        tu = get_types_universe()

        F1 = dps[0].get_fun_space()
        R1 = dps[0].get_res_space()

        for dp in dps:
            Fj = dp.get_fun_space()
            Rj = dp.get_res_space()

            try:
                tu.check_equal(F1, Fj)
                tu.check_equal(R1, Rj)
            except NotEqual:
                msg = 'Cannot form the co-product.'
                raise_desc(ValueError, msg, dps=dps)

        F = F1
        R = R1
        Ms = [dp.get_imp_space_mod_res() for dp in dps]

        self.dps = dps
        self.M = Coproduct1(tuple(Ms))
        PrimitiveDP.__init__(self, F=F, R=R, I=self.M)

    def evaluate(self, m):
        i, mi = self.M.unpack(m)
        return self.dps[i].evaluate(mi)

    def evaluate_f_m(self, f, m):
        """ Returns the resources needed
            by the particular implementation m """
        i, xi = self.M.unpack(m)
        return self.dps[i].evaluate_f_m(f, xi)

    def get_implementations_f_r(self, f, r):
        """ Returns a nonempty set of thinks in self.M.
            Might raise NotFeasible() """
        res = set()
        es = []
        ms = None
        for j, dp in enumerate(self.dps):
            try:
                ms = dp.get_implementations_f_r(f, r)
                # print('%s: dp.get_implementations_f_r(f, r) = %s ' % (j, ms))
                for m in ms:
                    Mj = dp.get_imp_space_mod_res()
                    try:
                        Mj.belongs(m)
                    except NotBelongs:
                        raise ValueError(dp)
                    res.add(self.M.pack(j, m))
            except NotFeasible as e:
                es.append(e)
        if not ms:
            # no one was feasible
            msg = 'None was feasible'
            msg += '\n\n' + '\n\n'.join(str(e) for e in es)
            raise_desc(NotFeasible, msg, f=f, r=r, self=self)

        if do_extra_checks():
            for _ in res:
                self.M.belongs(_)

        return res

    def solve(self, f):
        R = self.get_res_space()

        s = []

        for dp in self.dps:
            rs = dp.solve(f)
            s.extend(rs.minimals)

        res = R.Us(poset_minima(s, R.leq))

        return res

    def __repr__(self):
        s = "^".join('%s' % x for x in self.dps)
        return 'CoProduct(%s)' % s

    def repr_long(self):
        s = 'CoProduct  %% %s -> %s' % (self.get_fun_space(), self.get_res_space())
        for dp in self.dps:
            r1 = dp.repr_long()
            s += '\n' + indent(r1, '. ', first='^ ')
        return s
#
    def get_normal_form(self):
        """

            alpha1: U(F) x S1 -> U(R)
            beta1:  U(F) x S1 -> S1

            ...
            
            alphaN: U(F) x SN -> U(R)
            betaN:  U(R) x SN -> SN
            
            S = S1 ^ S2 ^ ... ^ SN
            
            alpha: U(F) x (S) -> U(R)
            beta : U(F) x (S) -> (S)

        """
        
        nf = [dp.get_normal_form() for dp in self.dps]
        
        Ss = [_.S for _ in nf]
        S = PosetProduct(tuple(Ss))
        print('S: %s' % S)

        F = self.get_fun_space()
        R = self.get_res_space()

        UF = UpperSets(F)
        UR = UpperSets(R)

        D = PosetProduct((UF, S))
        """
            D = U(F) x S
            alpha: U(F) x S -> U(R)
            beta : U(F) x S -> (S)
        """
        class CPAlpha(Map):
            def __init__(self, dp):
                self.dp = dp
                dom = D
                cod = UR
                Map.__init__(self, dom, cod)

            def _call(self, x):
                (uf, s) = x
                
                uris = []
                for i, si in enumerate(s):
                    uri = nf[i].alpha((uf, si))
                    uris.append(uri)

                res = set()
                for _ in uris:
                    res.update(_.minimals)
                resm = poset_minima(res, R.leq)
                r = UpperSet(resm, R)
                return r

        class CPBeta(Map):
            def __init__(self, dp):
                self.dp = dp
                dom = D
                cod = S
                Map.__init__(self, dom, cod)

            def _call(self, x):
                (uf, s) = x

                res = []
                for i, si in enumerate(s):

                    sn = nf[i].beta((uf, si))
                    res.append(sn)

                return tuple(res)

        return NormalForm(S, CPAlpha(self), CPBeta(self))



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
