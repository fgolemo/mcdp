from contracts.utils import raise_desc, raise_wrapped
from mocdp.comp.interfaces import NamedDP
from mocdp.posets import NotEqual
from contracts import contract

__all__ = [
    'NamedDPCoproduct',
]

class NamedDPCoproduct(NamedDP):

    # @contract(ndps='tuple[>=1]($NamedDP)')
    @contract(labels='None|(tuple,seq(str))')
    def __init__(self, ndps, labels=None):
        from mocdp.posets.types_universe import get_types_universe
        if not isinstance(ndps, tuple) or not len(ndps) >= 1:
            raise_desc(ValueError, 'Expected a nonempty tuple.', ndps=ndps)

        if labels is not None:
            if not isinstance(labels, tuple) or not len(labels) == len(ndps):
                raise_desc(ValueError, 'Need labels to be consistent',
                           ndps=ndps, labels=labels)
        self.labels = labels

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
                raise_wrapped(ValueError, e, msg,
                              ftypes=ftypes, ftypes_i=ftypes_i)

            try:
                tu.check_equal(rtypes, rtypes_i)
            except NotEqual as e:
                msg = 'Cannot create co-product: rtypes do not match.'
                raise_wrapped(ValueError, e, msg,
                              rtypes=rtypes, rtypes_i=rtypes_i)

        self.ndps = ndps

    def get_dp(self):
        options = [ndp.get_dp() for ndp in self.ndps]
        from mocdp.dp.dp_coproduct import CoProductDP
        dp = CoProductDP(tuple(options))
#         return dp
    # XXX
        if self.labels is None:
            return dp
        else:
            from mocdp.dp.dp_coproduct import CoProductDPLabels
            dp2 = CoProductDPLabels(dp, self.labels)

            assert dp2.get_fun_space() == dp.get_fun_space(), (dp, dp2)
            assert dp2.get_res_space() == dp.get_res_space(), (dp, dp2)
            return dp2

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
