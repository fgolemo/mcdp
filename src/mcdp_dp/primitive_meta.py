# -*- coding: utf-8 -*-
from abc import ABCMeta

from contracts import all_disabled
from contracts.utils import raise_wrapped
from mcdp_posets import NotBelongs
import sys
from mocdp import logger
from contracts.enabling import Switches


__all__ = [
    'PrimitiveMeta',
]


class PrimitiveMeta(ABCMeta):
    # we use __init__ rather than __new__ here because we want
    # to modify attributes of the class *after* they have been
    # created
    def __init__(cls, name, bases, dct):  # @NoSelf
        ABCMeta.__init__(cls, name, bases, dct)

        if all_disabled():
            pass
        else:
#             print('Adding checks on Primitive %s: Switches.disable_all = %s' % (name, Switches.disable_all))
            from mcdp_dp.primitive import NotSolvableNeedsApprox
            from mcdp_dp.primitive import WrongUseOfUncertain

            if 'solve' in cls.__dict__:
                solve = cls.__dict__['solve']

                def solve2(self, f):
                    if all_disabled():
                        return solve(self, f)
                    
                    F = self.get_fun_space()
                    try:
                        F.belongs(f)
                    except NotBelongs as e:
                        msg = "Function passed to solve() is not in function space."
                        raise_wrapped(NotBelongs, e, msg,
                                      F=F, f=f, dp=self.repr_long(), exc=sys.exc_info())

                    try:
                        res = solve(self, f)
                        return res
                    except NotBelongs as e:
                        raise_wrapped(NotBelongs, e,
                            'Solve failed.', self=self, f=f, exc=sys.exc_info())
                    except NotImplementedError as e:
                        raise_wrapped(NotImplementedError, e,
                            'Solve not implemented for class %s.' % name, exc=sys.exc_info())
                    except NotSolvableNeedsApprox:
                        raise
                    except WrongUseOfUncertain:
                        raise
                    except Exception as e:
                        raise_wrapped(Exception, e,
                            'Solve failed', f=f, self=self, exc=sys.exc_info())

                setattr(cls, 'solve', solve2)

            if 'get_implementations_f_m' in cls.__dict__:
                get_implementations_f_r = cls.__dict__['get_implementations_f_r']

                def get_implementations_f_r2(self, f, r):
                    if all_disabled():
                        return get_implementations_f_r(self, f, r)
                    
                    
                    F = self.get_fun_space()
                    R = self.get_fun_space()
                    try:
                        F.belongs(f)
                    except NotBelongs as e:
                        msg = "Function passed to get_implementations_f_r() is not in function space."
                        raise_wrapped(NotBelongs, e, msg,
                                      F=F, f=f, dp=self.repr_long(), exc=sys.exc_info())
                    try:
                        R.belongs(r)
                    except NotBelongs as e:
                        msg = "Function passed to get_implementations_f_r() is not in R space."
                        raise_wrapped(NotBelongs, e, msg,
                                      R=R, r=r, dp=self.repr_long(), exc=sys.exc_info())

                    try:
                        res = get_implementations_f_r(self, f, r)
                    except NotBelongs as e:
                        raise_wrapped(NotBelongs, e,
                            'Solve failed.', self=self, f=f, exc=sys.exc_info())
                    except NotImplementedError as e:
                        raise_wrapped(NotImplementedError, e,
                            'Solve not implemented for class %s.' % name)
                    except NotSolvableNeedsApprox:
                        raise
                    except WrongUseOfUncertain:
                        raise
                    except Exception as e:
                        raise_wrapped(Exception, e,
                            'Solve failed', f=f, self=self, exc=sys.exc_info())
                        
                    M = self.get_imp_space()
                    try:
                        for m in res:
                            M.belongs(m)
                    except NotBelongs as e:
                        raise_wrapped(NotBelongs, e,
                                      'Result of get_implementations_f_r not in M.',
                                      self=self, m=m, M=M, exc=sys.exc_info())

                    return res

                setattr(cls, 'get_implementations_f_r', get_implementations_f_r2)
