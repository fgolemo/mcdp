# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from contracts import contract
from mcdp_posets import LowerSet, Poset, UpperSet, poset_maxima, poset_minima
from mocdp.exceptions import do_extra_checks

_ = Poset

__all__ = [
    'CatalogueDP',
]


class CatalogueDP(PrimitiveDP):

    @contract(entries='seq[>=1](tuple(str, *, *))')
    def __init__(self, F, R, I, entries):
        entries = tuple(entries)
        if do_extra_checks():
            for m, f_max, r_min in entries:
                I.belongs(m)
                F.belongs(f_max)
                R.belongs(r_min)
        self.entries = entries
        PrimitiveDP.__init__(self, F=F, R=R, I=I)

    def solve(self, f):
        R = self.R
        F = self.F
        options_r = []
        for _name, f_max, r_min in self.entries:
            if F.leq(f, f_max):
                options_r.append(r_min)

        rs = poset_minima(options_r, R.leq)
        return self.R.Us(rs)

    def evaluate(self, i):
        if do_extra_checks():
            self.I.belongs(i)
        options_r = []
        options_f = []

        for name, f_max, r_min in self.entries:
            if name != i:
                continue

            options_f.append(f_max)
            options_r.append(r_min)

        rs = poset_minima(options_r, self.R.leq)
        fs = poset_maxima(options_f, self.F.leq)
        ur = UpperSet(rs, self.R)
        lf = LowerSet(fs, self.F)
        return lf, ur

    def get_implementations_f_r(self, f, r):
        R = self.R
        F = self.F
        options_m = set()
        for name, f_max, r_min in self.entries:
            if F.leq(f, f_max) and R.leq(r_min, r):
                options_m.add(name)

        return options_m

    def __repr__(self):
        return 'CatalogueDP(%r|%r)' % (self.F, self.R)



