from contracts import contract
from contracts.utils import raise_desc, raise_wrapped, indent
from mcdp_dp import CoProductDPLabels
from mcdp_posets import NotEqual
from mocdp import ATTRIBUTE_NDP_RECURSIVE_NAME, ATTR_LOAD_NAME
from mocdp.comp.interfaces import NamedDP
from mocdp.comp.wrap import SimpleWrap


__all__ = [
    'NamedDPCoproduct',
]

class NamedDPCoproduct(NamedDP):

    # @contract(ndps='tuple[>=1]($NamedDP)')
    @contract(labels='None|(tuple,seq(str))')
    def __init__(self, ndps, labels=None):
        from mcdp_posets.types_universe import get_types_universe
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

        for i, ndp in enumerate(ndps):
            ftypes_i = ndp.get_ftypes(ndp.get_fnames())
            rtypes_i = ndp.get_rtypes(ndp.get_rnames())
            name = 'model #%d' % i if not self.labels else self.labels[i].__repr__()
            try:
                tu.check_equal(ftypes, ftypes_i)
            except NotEqual as e:
                msg = 'Cannot create co-product: ftypes of %s do not match the first.' % name
                raise_wrapped(ValueError, e, msg,
                              ftypes=ftypes, ftypes_i=ftypes_i)

            try:
                tu.check_equal(rtypes, rtypes_i)
            except NotEqual as e:
                msg = 'Cannot create co-product: rtypes of %s not match the first.' % name
                raise_wrapped(ValueError, e, msg,
                              rtypes=rtypes, rtypes_i=rtypes_i)

        self.ndps = ndps

    def abstract(self):
        dp = self.get_dp()
        fnames = self.get_fnames()
        rnames = self.get_rnames()
        if len(fnames) == 1:
            fnames = fnames[0]
        if len(rnames) == 1:
            rnames = rnames[0]
        return SimpleWrap(dp, fnames=fnames, rnames=rnames)
        
    def get_dp(self):
        options = [ndp.get_dp() for ndp in self.ndps]
        from mcdp_dp.dp_coproduct import CoProductDP
        dp = CoProductDP(tuple(options))

        if self.labels is None:
            res = dp
        else:
            
            dp2 = CoProductDPLabels(dp, self.labels)

            assert dp2.get_fun_space() == dp.get_fun_space(), (dp, dp2)
            assert dp2.get_res_space() == dp.get_res_space(), (dp, dp2)
            res = dp2

        if hasattr(self, ATTRIBUTE_NDP_RECURSIVE_NAME):
            x = getattr(self, ATTRIBUTE_NDP_RECURSIVE_NAME)
            setattr(res, ATTRIBUTE_NDP_RECURSIVE_NAME, x)

        return res

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

    def __repr__(self):
        s = 'NamedDPCoproduct'

        if hasattr(self, ATTR_LOAD_NAME):
            s += '\n (loaded as %r)' % getattr(self, ATTR_LOAD_NAME)

        if hasattr(self, ATTRIBUTE_NDP_RECURSIVE_NAME):
            s += '\n (labeled as %s)' % getattr(self, ATTRIBUTE_NDP_RECURSIVE_NAME).__str__()

        for f in self.get_fnames():
            s += '\n provides %s  [%s]' % (f, self.get_ftype(f))
        for r in self.get_rnames():
            s += '\n requires %s  [%s]' % (r, self.get_rtype(r))

        for label, ndp in zip(self.labels, self.ndps):
            prefix = '- %s: ' % label
            prefix2 = ' ' * len(prefix)
            s += '\n' + indent(ndp, prefix2, prefix)
        return s
    
