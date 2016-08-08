from contracts import contract
from mcdp_dp.dp_limit import Limit
from mcdp_library import MCDPLibrary
from mcdp_library.library import ATTR_LOAD_NAME
from mcdp_opt.compare_different_resources import less_resources2
from mcdp_opt.context_utils import create_context0
from mcdp_posets import NotBounded, Poset, get_types_universe
from mcdp_posets.uppersets import UpperSet, upperset_project
from mcdp_report import my_gvgen
from mcdp_report.gg_utils import gg_figure
from mocdp.comp.composite import CompositeNamedDP
from mocdp.comp.context import CResource, get_name_for_fun_node
from mocdp.comp.interfaces import NotConnected
from mocdp.comp.wrap import dpwrap, SimpleWrap
from mocdp.exceptions import mcdp_dev_warning
from mocdp.memoize_simple_imp import memoize_simple
from reprep import Report
import networkx as nx
import os
from mcdp_opt.cachedp import CacheDP
import gc

_ = UpperSet, CResource, Poset

__all__ = ['Optimization']


class Optimization():

    @contract(library=MCDPLibrary, initial=CompositeNamedDP)
    def __init__(self, library, options,
                 flabels, F0s, f0s,
                 rlabels, R0s, r0s, initial):

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
        
        context = create_context0(flabels, F0s, f0s, rlabels, R0s, r0s, initial=initial)

        from mcdp_opt.optimization_state import OptimizationState

        unconnected = []
        for o in options:
            ndp = library.load_ndp(o)
            try:
                ndp.check_fully_connected()
            except NotConnected as e:
                if o.lower() == "raspberrypi2":
                    print e
                unconnected.append(o)


        for u in unconnected:
            options.remove(u)

        print('Removing the unusable options %s' % sorted(unconnected))
        print('Remaining with %s' % sorted(options))

        lower_bounds = {}
        for fname, F0, f0 in zip(flabels, F0s, f0s):
            r = CResource(get_name_for_fun_node(fname), fname)
            lower_bounds[r] = F0.U(f0)
        from mcdp_opt.partial_result import get_lower_bound_ndp
        ndp, table = get_lower_bound_ndp(context)
        (_R, ur), _tableres = self.get_lower_bounds(ndp, table)
        s0 = OptimizationState(self, options, context, executed=[], forbidden=[],
                               lower_bounds=lower_bounds, ur=ur)
        s0.creation_order = 0
        self.num_created = 1

        self.root = s0
        self.states = [s0]
        # connected
        self.done = []
        # impossible
        self.abandoned = []

        # extra ndps not present in library
        self.additional = {}  # str -> NamedDP

        self.iteration = 0

        # for visualization
        self.G = nx.DiGraph()

    @contract(s='isinstance(OptimizationState)',
              s1='isinstance(OptimizationState)')
    def note_edge(self, s, a, s1):
        """ Note that there was a state s1 generated that
            led from s using action a """
        self.G.add_node(s)
        self.G.add_node(s1)
        self.G.add_edge(s, s1, action=a)

    def draw_tree(self, outdir):
#         out_nodes = os.path.join(outdir, 'nodes')
#         out_steps = os.path.join(outdir, 'steps')
#         out = os.path.join(out_steps, 'step%03d' % self.iteration)

        out_nodes = out_steps = out = outdir
#         for d in [out_nodes, out_steps]:
#             if os.path.exists(d):
#                 shutil.rmtree(d)

        if not os.path.exists(out):
            os.makedirs(out)

        fn = os.path.join(outdir, 'step%03d_tree.html' % self.iteration)
        gg = self.draw_tree_get_tree()
        r = Report()
        gg_figure(r, 'tree', gg, do_png=True, do_dot=False, do_svg=False)
        print('writing to %r' % fn)
        r.to_html(fn)
        
        for s in self.G.nodes():
            order = s.creation_order
            fn = os.path.join(out_nodes, 'node%03d.html' % order)
            if os.path.exists(fn):
                continue
            r = Report()

            from mcdp_opt_tests.test_basic import plot_ndp
            plot_ndp(r, 'current', s.get_current_ndp(), self.library)

            r.text('msg', s.get_info())

            print('writing to %r' % fn)
            r.to_html(fn)


    def draw_tree_get_tree(self):
        gg = my_gvgen.GvGen(options="rankdir=TB")
        n2ggn = {}
        G = self.G
        def label_for_node(n):
            s = '#%s' % n.creation_order
            s += ' (%d)' % len(n.context.names)
            return s
        def label_for_edge(n1, a, n2):  # @UnusedVariable
            return a.__repr__()
        def get_ggn_node(n):
            assert n in G.nodes()
            if not n in n2ggn:
#                 preds = G.predecessors(n)
#                 if preds:
#                     parent = preds[0]
#                     parent = get_ggn_node(parent)
#                 else:
                parent = None
                label = label_for_node(n)
                ggn = gg.newItem(label, parent=parent)

                n2ggn[n] = ggn

            return n2ggn[n]

        for n in G.nodes():
            get_ggn_node(n)

        for n1, n2 in G.edges():
            a = G.get_edge_data(n1, n2)['action']
            gn1 = get_ggn_node(n1)
            gn2 = get_ggn_node(n2)
            label = label_for_edge(n1, a, n2)
            gg.newLink(gn1, gn2, label)
        return gg
        

    def print_status(self):
        print('open: %3d  done: %3d  abandoned: %3d' % (len(self.states),
                                                        len(self.done),
                                                        len(self.abandoned)))

    def step(self):
        self.iteration += 1

        s = self.states.pop(0)
        s.info('Popped at iteration %d' % self.iteration)

        done, actions = s.iteration()

        s.info('Generated %d actions' % len(actions))


        if done:
            self.done.append(s)
            assert s in self.done
        else:
            if not actions:
                s.info("No actions available, placing in abandoned")
                self.abandoned.append(s)
                assert s in self.abandoned
            else:
                for i, a in enumerate(actions):
                    gc.collect()
                    s1 = a(self, s)
                    s1.info('created using %s' % a)
                    s1.creation_order = self.num_created
                    self.num_created += 1

                    self.note_edge(s, a, s1)

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
                            s1.info(msg)
                            self.abandoned.append(s1)
                        else:
                            dominated, by_what = self.is_dominated_by_open(s1)
                            if dominated:
                                s1.info('Dominated by %s' % by_what)
                                self.abandoned.append(s1)
                            else:
                                self.states.append(s1)
                    else:
                        s1.info('I was a double')

                s.info('Expanded.')

    def is_dominated_by_open(self, s1):
        for a in self.states:
            if self.dominates(a, s1):
                return True, s1.ur
        return False, None


    def dominates(self, s1, s2):
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
        options = []
        # check that if it is a bottom
        if len(lb.minimals) == 1:
            try:
                bot = R.get_bottom()
            except NotBounded:
                pass
            else:
                if R.equal(bot, list(lb.minimals)[0]):
                    # we can provide an "unused" box
                    dp = Limit(R, bot)
                    ndp = dpwrap(dp, 'limit', [])
                    
                    def sanitize(s):
                        import re
                        s = re.sub('[^0-9a-zA-Z]+', '_', s)
                        return s
                        
                    newname = sanitize('limit_%s' % R)
                    options.append((newname, 'limit'))
                    self.additional[newname] = ndp

        type_options = self.get_providers_for_type(R)
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

    @memoize_simple
    def load_ndp(self, id_ndp):
        if id_ndp in self.additional:
            return self.additional[id_ndp]

        ndp = self.library.load_ndp(id_ndp)

        a = getattr(ndp, ATTR_LOAD_NAME, None)

        # TODO: check if there is a loop
        ndp = ndp.abstract()
        if a:
            setattr(ndp, ATTR_LOAD_NAME, a)

        assert isinstance(ndp, SimpleWrap)

        dp0 = ndp.dp
        dp_cached = CacheDP(dp0)
        ndp.dp = dp_cached

        return ndp

    @memoize_simple
    def load_dp(self, id_ndp):
        ndp = self.load_ndp(id_ndp)
        dp0 = ndp.get_dp()
        # dp = CacheDP(dp0)
        return dp0
        
        
        

