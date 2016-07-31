from contracts import contract
from contracts.utils import raise_wrapped
from mcdp_library import MCDPLibrary
from mcdp_opt.context_utils import create_context0
from mcdp_posets import Poset, get_types_universe
from mcdp_posets.uppersets import UpperSet, upperset_project
from mcdp_web.utils.memoize_simple_imp import memoize_simple
from mocdp.comp.context import CResource, get_name_for_fun_node
from mocdp.comp.interfaces import NotConnected
from mocdp.exceptions import mcdp_dev_warning
from mcdp_library.library import ATTR_LOAD_NAME
from mcdp_opt.compare_different_resources import CompareDifferentResources, \
    less_resources2
_ = UpperSet, CResource, Poset

__all__ = ['Optimization']

class Optimization():

    @contract(library=MCDPLibrary)
    def __init__(self, library, options,
                 flabels, F0s, f0s,
                 rlabels, R0s, r0s):

        for _fname, F0, f0 in zip(flabels, F0s, f0s):
            F0.belongs(f0)
        for _rname, R0, r0 in zip(flabels, R0s, r0s):
            R0.belongs(r0)

        self.library = library
        self.options = options
        self.flabels = flabels
        self.rlabels = rlabels
        self.F0s = F0s
        self.R0s = R0s
        self.r0s = r0s
        self.f0s = f0s
        
        context = create_context0(flabels, F0s, f0s, rlabels, R0s, r0s)

        from mcdp_opt.optimization_state import OptimizationState

        for o in options:
            ndp = library.load_ndp(o)
            try:
                ndp.check_fully_connected()
            except NotConnected as e:
                msg = 'The base option %r is not connected.' % o
                raise_wrapped(ValueError, e, msg, id_ndp=o, compact=True)

        lower_bounds = {}
        for fname, F0, f0 in zip(flabels, F0s, f0s):
            r = CResource(get_name_for_fun_node(fname), fname)
            lower_bounds[r] = F0.U(f0)
        from mcdp_opt.partial_result import get_lower_bound_ndp
        ndp, table = get_lower_bound_ndp(context)
        (_R, ur), _tableres = self.get_lower_bounds(ndp, table)
        s0 = OptimizationState(self, options, context, executed=[], forbidden=[],
                               lower_bounds=lower_bounds, ur=ur)

        self.states = [s0]
        # connected
        self.done = []
        # impossible
        self.abandoned = []

    @memoize_simple
    def load_ndp(self, id_ndp):
        ndp = self.library.load_ndp(id_ndp)

        a = getattr(ndp, ATTR_LOAD_NAME, None)

        # TODO: check if there is a loop
        ndp = ndp.abstract()
        if a:
            setattr(ndp, ATTR_LOAD_NAME, a)
        return ndp

    @memoize_simple
    def load_dp(self, id_ndp):
        ndp = self.load_ndp(id_ndp)
        dp = ndp.get_dp()
        return dp

    def print_status(self):
        print('open: %3d  done: %3d  abandoned: %3d' % (len(self.states),
                                                        len(self.done),
                                                        len(self.abandoned)))

    def step(self):
        # self.print_status()
        # if policy ...
        s = self.states.pop(0)

        done, actions = s.iteration()

        if done:
            self.done.append(s)
            assert s in self.done
        else:
            if not actions:
                # setattr(s, 'msg', 'No actions possible')
                if not hasattr(s, 'msg'):
                    s.msg = "No actions available."
                self.abandoned.append(s)
                assert s in self.abandoned
            else:
                for i, a in enumerate(actions):
                    s1 = a(self, s)
                    # mark the rest as forbidden
                    rest = [a2 for i2, a2 in enumerate(actions) if i2 != i]
                    s1.forbidden.extend(rest)

                    if ((not s1 in self.states) and
                        (not s1 in self.done) and
                        (not s1 in self.abandoned)):

                        ur = s1.ur

                        if len(ur.minimals) == 0:
                            msg = 'Unfortunately this is not feasible (%s)' % s1.ur.P
                            msg += '%s' % s1.lower_bounds
                            s1.msg = msg
                            print msg
                            self.abandoned.append(s1)
                        else:
                            dominated, by_what = self.is_dominated_by_open(s1)
                            if dominated:
                                msg = 'Dominated by %s' % by_what
                                s1.msg = msg
                                self.abandoned.append(s1)
                            else:
                                self.states.append(s1)

    def is_dominated_by_open(self, s1):
        for a in self.states:
            if self.dominates(a, s1):
                return True, s1.ur
        return False, None


    def dominates(self ,s1, s2):
        from mcdp_posets.nat import Nat
        from mcdp_posets.poset_product import PosetProduct
        
        n1 = (40 - s1.num_connection_options,)
        n2 = (40 - s2.num_connection_options,)
        N = PosetProduct((Nat(),))
        # create a joint one
        from mcdp_opt_tests.test_basic import add_extra
        l1b = add_extra(s1.ur, N, n1)
        l2b = add_extra(s2.ur, N, n2)
        # cdr = CompareDifferentResources()
        return less_resources2(l1b, l2b)

    def does_provider_provide(self, id_ndp, fname, R, lb):
        assert lb.P == R
        assert isinstance(lb, UpperSet)
        ndp = self.load_ndp(id_ndp)
        dp = self.load_dp(id_ndp)
        fnames = ndp.get_fnames()
        assert fname in fnames
        
        def get_minimal():
            """ Returns a set of minimal elements """
            others = list(fnames)
            others.remove(fname)
            Fothers = ndp.get_ftypes(others)
            fs = set()
            for m in lb.minimals:
                for otherm in Fothers.get_minimal_elements():
                    def get(i):
                        if i == fnames.index(fname):
                            return m
                        else:
                            return otherm[others.index(fnames[i])]
                        
                    f = [get(i) for i in range(len(fnames))]
                    
                    if len(fnames) == 1:
                        f = f[0]
                    else:
                        f = tuple(f)
                    fs.add(f) 
            return fs
        
        F = dp.get_fun_space()
        fs = get_minimal()
        for f in fs:
            F.belongs(f)
            ur = dp.solve(f)
            if ur.minimals:
                print('Yes %s:%s provides at least %s' % (id_ndp, fname, lb))
                print('  f = %s ' % F.format(f))
                print(' ur = %s ' % ur)
                return True
        return False

    def get_providers(self, R, lb):
        """ 
            Returns a list of (name, fname) that implements R, with lb
            being a lower bound. 
        """
        type_options = self.get_providers_for_type(R)
        options = []
        for id_ndp, fname in type_options:
            if self.does_provider_provide(id_ndp, fname, R, lb):
                options.append((id_ndp, fname))

        print('Options for %s >= %s: %r' % (R, lb, options))
        return options
    
    @memoize_simple
    def get_providers_for_type(self, R):
        options = []
        tu = get_types_universe()
        for id_ndp in self.options:
            ndp = self.load_ndp(id_ndp)
            fnames = ndp.get_fnames()
            ftypes = ndp.get_ftypes(fnames)
            for fname, F in zip(fnames, ftypes):
                if tu.leq(R, F):
                    options.append((id_ndp, fname))
                    mcdp_dev_warning("assume that it is symmetric")
                    break
        return options

    @contract(returns='tuple(tuple($Poset, $UpperSet), dict($CResource: $UpperSet))')
    def get_lower_bounds(self, ndp, table):
        rnames = ndp.get_rnames()
        for cresource, rname in table.items():
            assert rname in rnames
            assert cresource.dp in ndp.context.names
            assert cresource.s in ndp.context.names[cresource.dp].get_rnames()
        
        f = self.f0s
        if len(self.flabels) == 1:
            f = f[0]
        dp = ndp.get_dp()

        ur = dp.solve(f)
        
        if len(rnames) == 1:
            # needs to do the same above for resources
            raise NotImplementedError()
        
        tableres = {}
        for cresource, rname in table.items():
            i = rnames.index(rname)
            # print('ur: %s i = %s' % (ur, i))
            uri = upperset_project(ur, i)
            tableres[cresource] = uri
        R = ur.P
        return (R, ur), tableres
        
        
        
        

