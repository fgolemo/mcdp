from abc import ABCMeta, abstractmethod
from contracts import contract
from mocdp.configuration import get_conftools_nameddps
from mocdp.posets import PosetProduct
from mocdp.posets.space import NotEqual
from contracts.utils import raise_wrapped, raise_desc


__all__ = [
    'NotConnected',
    'NamedDP',
    'dp_from_ndp',
]

class NotConnected(Exception):
    pass


class NamedDP():
    """ A DP with names """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_dp(self):
        pass

    @abstractmethod
    def check_fully_connected(self):
        """ Raise NotConnected """

    def is_fully_connected(self):
        try:
            self.check_fully_connected()
        except NotConnected:
            return False
        else:
            return True

    @abstractmethod
    @contract(returns='list(str)')
    def get_fnames(self):
        pass

    @abstractmethod
    @contract(returns='list(str)')
    def get_rnames(self):
        pass

    @abstractmethod
    @contract(rname=str)
    def get_rtype(self, rname):
        pass

    @abstractmethod
    @contract(fname=str)
    def get_ftype(self, fname):
        pass

    def repr_long(self):
        return self.__repr__()

    @contract(signals='list|tuple')
    def get_ftypes(self, signals):
        # Returns the product space
        types = [self.get_ftype(s) for s in signals]
        return PosetProduct(tuple(types))

    @contract(signals='list|tuple')
    def get_rtypes(self, signals):
        # Returns the product space
        types = [self.get_rtype(s) for s in signals]
        return PosetProduct(tuple(types))


def dp_from_ndp(ndp):
    """ Unwrap """
    _, ndp = get_conftools_nameddps().instance_smarter(ndp)
    # unwrap
    return ndp.get_dp()


class NamedDPCoproduct(NamedDP):

    # @contract(ndps='tuple[>=1]($NamedDP)')
    def __init__(self, ndps):
        from mocdp.posets.types_universe import get_types_universe
        if not isinstance(ndps, tuple) or not len(ndps) >= 1:
            raise_desc(ValueError, 'Expected a nonempty tuple.', ndps=ndps)

        tu = get_types_universe()
        first = ndps[0]
        ftypes = first.get_ftypes(first.get_fnames())
        rtypes = first.get_rtypes(first.get_rnames())

        for _, ndp in enumerate(ndps):
            ftypes_i = ndp.get_ftypes(ndp.get_fnames())
            rtypes_i = ndp.get_rtypes(ndp.get_rnames())

            try:
                tu.check_equal(ftypes, ftypes_i)
            except NotEqual as e:
                msg = 'Cannot create co-product: ftypes do not match.'
                raise_wrapped(ValueError, e, msg, ftypes=ftypes, ftypes_i=ftypes_i)

            try:
                tu.check_equal(rtypes, rtypes_i)
            except NotEqual as e:
                msg = 'Cannot create co-product: rtypes do not match.'
                raise_wrapped(ValueError, e, msg, rtypes=rtypes, rtypes_i=rtypes_i)

        self.ndps = ndps

    def get_dp(self):
        options = [ndp.get_dp() for ndp in self.ndps]
        from mocdp.dp.dp_coproduct import CoProductDP
        return CoProductDP(tuple(options))

    def check_fully_connected(self):
        for ndp in self.ndps:
            ndp.check_fully_connected()

    def get_fnames(self):
        return self.ndps[0].get_fnames()

    def get_rnames(self):
        return self.ndps[0].get_rnames()

    def get_rtype(self, rname):
        return self.ndps[0].get_rtype(rname)

    def get_ftype(self, fname):
        return self.ndps[0].get_ftype(fname)


