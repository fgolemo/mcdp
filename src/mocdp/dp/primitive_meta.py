from abc import ABCMeta
from contracts.enabling import all_disabled
from contracts.utils import raise_wrapped
from mocdp.posets.space import NotBelongs

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
            if 'solve' in cls.__dict__:
                solve = cls.__dict__['solve']

                def solve2(self, f):
                    F = self.get_fun_space()
                    try:
                        F.belongs(f)
                    except NotBelongs as e:
                        msg = "Function passed to solve() is not in function space."
                        raise_wrapped(NotBelongs, e, msg,
                                      F=F, f=f, self=self)

                    try:
                        res = solve(self, f)
                        return res
                    except NotBelongs as e:
                        raise_wrapped(NotBelongs, e,
                            'Solve failed.', self=self, f=f)
                    except NotImplementedError as e:
                        raise_wrapped(NotImplementedError, e,
                            'Solve not implemented for class %s.' % name)
                    except Exception as e:
                        raise_wrapped(Exception, e,
                            'Solve failed', f=f, self=self)


                setattr(cls, 'solve', solve2)
