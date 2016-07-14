# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from contracts import contract
from mcdp_posets import Poset  # @UnusedImport
from mcdp_posets.utils import poset_minima


__all__ = [
    'CatalogueDP',
]


class CatalogueDP(PrimitiveDP):

    @contract(entries='seq[>=1](tuple(str, *, *))')
    def __init__(self, F, R, M, entries):
        entries = tuple(entries)
        for m, f_max, r_min in entries:
            M.belongs(m)
            F.belongs(f_max)
            R.belongs(r_min)
        self.entries = entries
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def solve(self, f):
        R = self.R
        F = self.F
        options_r = []
        for _name, f_max, r_min in self.entries:
            if F.leq(f, f_max):
                options_r.append(r_min)

        rs = poset_minima(options_r, R.leq)
        return self.R.Us(rs)

    def get_implementations_f_r(self, f, r):
        R = self.R
        F = self.F
        options_m = set()
        for name, f_max, r_min in self.entries:
            if F.leq(f, f_max) and R.leq(r_min, r):
                options_m.add(name)
        return options_m

    def __repr__(self):
        return 'CatalogueDP(%r)' % self.F


