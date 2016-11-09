# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import indent
from mcdp_dp import LabelerDP, PrimitiveDP
from mocdp.comp.interfaces import NamedDP
from mocdp.comp.wrap import dpwrap


__all__ = [
    'LabelerNDP',
]


class LabelerNDP(NamedDP):
    """ Wrapper used to label stuff. """

    @contract(ndp=NamedDP, recursive_name='tuple,seq(str)')
    def __init__(self, ndp, recursive_name):
        if isinstance(ndp, LabelerNDP):
            # never expect a labeler inside another
            raise TypeError(ndp)
        self.ndp = ndp
        self.recursive_name = recursive_name

    def get_dp(self):
        dp0 = self.ndp.get_dp()
        assert isinstance(dp0, PrimitiveDP), self.ndp

        dp = LabelerDP(dp0, self.recursive_name)
        return dp
    
    def check_fully_connected(self):
        return self.ndp.check_fully_connected()

    def flatten(self):
        n = self.ndp.flatten()
        return LabelerNDP(n, self.recursive_name)

    def compact(self):
        n = self.ndp.compact()
        return LabelerNDP(n, self.recursive_name)

    def abstract(self):
        n0 = self.ndp.abstract()
        dp0 = n0.get_dp()
        dp = LabelerDP(dp0, self.recursive_name)
        fnames = self.get_fnames()
        rnames = self.get_rnames()
        if len(fnames) == 1:
            fnames = fnames[0]
        if len(rnames) == 1:
            rnames = rnames[0]

        return dpwrap(dp, fnames, rnames)

    def get_fnames(self):
        return self.ndp.get_fnames()

    def get_rnames(self):
        return self.ndp.get_rnames()

    def get_rtype(self, rname):
        return self.ndp.get_rtype(rname)

    def get_ftype(self, fname):
        return self.ndp.get_ftype(fname)

    def __repr__(self):
        return self.repr_long()
    def repr_long(self):
        s = "LabelerNDP({})".format(self.recursive_name)
        s += '\n' + indent(self.ndp.repr_long(), ' ')
        return s

