from abc import ABCMeta
from contracts import all_disabled
from contracts.utils import raise_wrapped
from mcdp_posets import NotBelongs

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
            # print('disabling checks on Primitive')
            pass
        else:
            from mcdp_dp.primitive import NotSolvableNeedsApprox
            from mcdp_dp.primitive import WrongUseOfUncertain

            if 'solve' in cls.__dict__:
                solve = cls.__dict__['solve']

                def solve2(self, f):
                    F = self.get_fun_space()
                    try:
                        F.belongs(f)
                    except NotBelongs as e:
                        msg = "Function passed to solve() is not in function space."
                        raise_wrapped(NotBelongs, e, msg,
                                      F=F, f=f, dp=self.repr_long())

                    try:
                        res = solve(self, f)
                        return res
                    except NotBelongs as e:
                        raise_wrapped(NotBelongs, e,
                            'Solve failed.', self=self, f=f)
                    except NotImplementedError as e:
                        raise_wrapped(NotImplementedError, e,
                            'Solve not implemented for class %s.' % name)
                    except NotSolvableNeedsApprox:
                        raise
                    except WrongUseOfUncertain:
                        raise
                    except Exception as e:
                        raise_wrapped(Exception, e,
                            'Solve failed', f=f, self=self)

                setattr(cls, 'solve', solve2)

            if 'get_implementations_f_m' in cls.__dict__:
                get_implementations_f_r = cls.__dict__['get_implementations_f_r']

                def get_implementations_f_r2(self, f, r):
                    F = self.get_fun_space()
                    R = self.get_fun_space()
                    try:
                        F.belongs(f)
                    except NotBelongs as e:
                        msg = "Function passed to get_implementations_f_r() is not in function space."
                        raise_wrapped(NotBelongs, e, msg,
                                      F=F, f=f, dp=self.repr_long())
                    try:
                        R.belongs(r)
                    except NotBelongs as e:
                        msg = "Function passed to get_implementations_f_r() is not in R space."
                        raise_wrapped(NotBelongs, e, msg,
                                      R=R, r=r, dp=self.repr_long())

                    try:
                        res = get_implementations_f_r(self, f, r)
                    except NotBelongs as e:
                        raise_wrapped(NotBelongs, e,
                            'Solve failed.', self=self, f=f)
                    except NotImplementedError as e:
                        raise_wrapped(NotImplementedError, e,
                            'Solve not implemented for class %s.' % name)
                    except NotSolvableNeedsApprox:
                        raise
                    except WrongUseOfUncertain:
                        raise
                    except Exception as e:
                        raise_wrapped(Exception, e,
                            'Solve failed', f=f, self=self)
                        
                    M = self.get_imp_space()
                    try:
                        for m in res:
                            M.belongs(m)
                    except NotBelongs as e:
                        raise_wrapped(NotBelongs, e,
                                      'Result of get_implementations_f_r not in M.',
                                      self=self, m=m, M=M)

                    return res

                setattr(cls, 'get_implementations_f_r', get_implementations_f_r2)
