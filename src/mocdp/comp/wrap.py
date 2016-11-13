# -*- coding: utf-8 -*-
from contracts import contract, raise_wrapped
from contracts.utils import indent, raise_desc, check_isinstance
from mcdp_dp import PrimitiveDP
from mcdp_dp.dp_flatten import get_it
from mcdp_posets import PosetProduct
from mocdp.exceptions import DPInternalError

from .interfaces import NamedDP


__all__ = [
    'SimpleWrap',
    'dpwrap',
]


class SimpleWrap(NamedDP):
    
    @contract(dp=PrimitiveDP)
    def __init__(self, dp, fnames, rnames, icon=None):
        assert isinstance(dp, PrimitiveDP), type(dp)
        self.dp = dp

        F = self.dp.get_fun_space()
        R = self.dp.get_res_space()

        try:
            # assume that dp has product spaces of given length

            if isinstance(rnames, list):
                if not len(set(rnames)) == len(rnames):
                    raise ValueError('Repeated rnames.')

            if isinstance(fnames, list):
                if not len(set(fnames)) == len(fnames):
                    raise ValueError('Repeated fnames.')

            if isinstance(fnames, str):
                self.F_single = True
                self.Fname = fnames
            else:

                if isinstance(F, PosetProduct):
                    if not isinstance(fnames, list) or not len(F) == len(fnames):
                        raise ValueError("F incompatible")
                    self.F_single = False
                    self.Fnames = fnames
                else:
                    if not isinstance(fnames, str):
                        msg = "F and fnames incompatible: not a string"
                        raise_desc(ValueError, msg, F=F, fnames=fnames)
                    self.F_single = True
                    self.Fname = fnames


            if isinstance(rnames, str):
                self.R_single = True
                self.Rname = rnames
            else:
                if isinstance(R, PosetProduct):
                    if not isinstance(rnames, list) or not len(R) == len(rnames):
                        raise ValueError("R incompatible")
                    self.R_single = False
                    self.Rnames = rnames
                else:
                    if not isinstance(rnames, str):
                        msg = "R and rnames incompatible: not a string"
                        raise_desc(ValueError, msg, R=R, rnames=rnames)
                    self.R_single = True
                    self.Rname = rnames
            self.icon = icon
        except Exception as e:
            msg = 'Cannot wrap primitive DP.'
            raise_wrapped(ValueError, e, msg, dp=self.dp, F=F, R=R,
                          fnames=fnames, rnames=rnames)

    def abstract(self):
        return self

    def get_icon(self):
        if self.icon is None:
            return type(self.dp).__name__
        else:
            return self.icon

    def check_fully_connected(self):
        pass  # it is


    def get_copy_with_renamed_function(self, current, updated):
        """ Returns an equivalent SimpleWrap with one function
            name replaced. """
        check_isinstance(current, str)
        check_isinstance(updated, str)
        
        if self.F_single:
            if not (self.Fname == current):
                msg = 'Invalid current function name.'
                raise_desc(ValueError, msg, ndp=self)
            fnames2 = updated
        else:
            if not (current in self.Fnames):
                msg = 'Invalid current function name.'
                raise_desc(ValueError, msg, ndp=self)
            fnames2 = list(self.Fnames)
            fnames2[fnames2.index(current)] = updated
            
        if self.R_single:
            rnames2 = self.Rname
        else:
            rnames2 = self.Rnames

        return SimpleWrap(dp=self.dp, fnames=fnames2, rnames=rnames2, icon=self.icon)
           
    def get_copy_with_renamed_resource(self, current, updated):
        """ Returns an equivalent SimpleWrap with one resource
            name replaced. """
        check_isinstance(current, str)
        check_isinstance(updated, str)
        
        if self.R_single:
            if not (self.Rname == current):
                msg = 'Invalid current resource name.'
                raise_desc(ValueError, msg, ndp=self)
            rnames2 = updated
        else:
            if not (current in self.Rnames):
                msg = 'Invalid current function name.'
                raise_desc(ValueError, msg, ndp=self)
            rnames2 = list(self.Rnames)
            rnames2[rnames2.index(current)] = updated
            
        if self.F_single:
            fnames2 = self.Fname
        else:
            fnames2 = self.Fnames

        return SimpleWrap(dp=self.dp, fnames=fnames2, rnames=rnames2, icon=self.icon)
            

            
    def get_dp(self):
        dp = self.dp

        if self.R_single:
            dp.R.label = self.Rname
        else:
            for i, rname in enumerate(self.Rnames):
                dp.R[i].label = rname

        if self.F_single:
            dp.F.label = self.Fname
        else:
            for i, rname in enumerate(self.Fnames):
                dp.F[i].label = rname

        return dp

    def get_fnames(self):
        if self.F_single:
            return [self.Fname]
        else:
            return self.Fnames

    def get_rnames(self):
        if self.R_single:
            return [self.Rname]
        else:
            return self.Rnames
    
    def rindex(self, r):
        if self.R_single:
            if not r == self.Rname:
                msg = 'Cannot find resource %r.' % r
                raise_desc(DPInternalError, msg, r=r, self=self.repr_long())

            return ()

        rnames = self.get_rnames()

        try:
            return rnames.index(r)
        except ValueError:
            msg = 'Cannot find resource %r.' % r
            raise_desc(DPInternalError, msg,
                       r=r, rnames=rnames, self=self.repr_long())


    def findex(self, f):
        if self.F_single:
            if not f == self.Fname:
                msg = 'Cannot find function %r.' % f
                raise_desc(DPInternalError, msg,
                           fnames=[self.Fname], self=self.repr_long())
            return ()
        fnames = self.get_fnames()
        try:
            return fnames.index(f)
        except ValueError:
            msg = 'Cannot find function %r.' % f
            raise_desc(DPInternalError, msg, fnames=fnames, self=self.repr_long())

    @contract(fname=str)
    def get_ftype(self, fname):
        F = self.get_dp().get_fun_space()
        i = self.findex(fname)
        return get_it(F, i, reduce_list=None)

    @contract(rname=str)
    def get_rtype(self, rname):
        R = self.get_dp().get_res_space()
        i = self.rindex(rname)
        return get_it(R, i, reduce_list=None)

    def desc(self):
        s = 'SimpleWrap'
        from mcdp_library.library import ATTR_LOAD_NAME
        if hasattr(self, ATTR_LOAD_NAME):
            s += '\n (loaded as %r)' % getattr(self, ATTR_LOAD_NAME)
        for f in self.get_fnames():
            s += '\n  provides %10s (%s) ' % (f, self.get_ftype(f))
        for r in self.get_rnames():
            s += '\n  requires %10s (%s) ' % (r, self.get_rtype(r))
            
        dp = self.get_dp()
        s += '\n %s' % type(dp)
        s += '\n' + indent(dp.repr_long(), '  | ')
        return s

    def __repr__(self):
        return self.desc()

    def repr_long(self):
        return self.desc()


@contract(dp=PrimitiveDP, returns=NamedDP, fnames='str|seq(str)', rnames='str|seq(str)')
def dpwrap(dp, fnames, rnames):
    return SimpleWrap(dp, fnames, rnames)
