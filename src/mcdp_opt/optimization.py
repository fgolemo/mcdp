# -*- coding: utf-8 -*-
import gc
import os
import shutil

from contracts import contract
from reprep import Report

from mcdp import MCDPConstants
from mcdp.exceptions import mcdp_dev_warning
from mcdp_dp import Limit
from mcdp_library import MCDPLibrary
from mcdp_opt.cachedp import CacheDP
from mcdp_opt.compare_different_resources import less_resources2
from mcdp_opt.context_utils import create_context0
from mcdp_opt.report_utils import get_optim_state_report
from mcdp_posets import Nat, NotBounded, Poset, get_types_universe, PosetProduct, UpperSet, upperset_project, express_value_in_isomorphic_space
from mcdp_report import my_gvgen
from mcdp_report.gg_utils import gg_figure
from mcdp_utils_misc import memoize_simple
from mocdp.comp.composite import CompositeNamedDP
from mocdp.comp.context import CResource, get_name_for_fun_node
from mocdp.comp.interfaces import NotConnected
from mocdp.comp.wrap import SimpleWrap, dpwrap
import networkx as nx


_ = UpperSet, CResource, Poset

__all__ = ['Optimization']


class Optimization():

    @contract(library=MCDPLibrary, initial=CompositeNamedDP)
    def __init__(self, library, options,
                 flabels, F0s, f0s,
                 rlabels, R0s, r0s, initial):

        f0s = list(f0s)
        F0s = list(F0s)
        r0s = list(r0s)
        R0s = list(R0s)

        for i, (fname, F0, f0) in enumerate(zip(flabels, F0s, f0s)):
            F0.belongs(f0)
            F = initial.get_ftype(fname)
            f0s[i] = express_value_in_isomorphic_space(F0, f0, F)
            F0s[i] = F

        for i, (rname, R0, r0) in enumerate(zip(rlabels, R0s, r0s)):
            R0.belongs(r0)
            R = initial.get_rtype(rname)
            r0s[i] = express_value_in_isomorphic_space(R0, r0, R)
            R0s[i] = R

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
                    # 
                    pass
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

        self.num_created = 0
        s0 = OptimizationState(self, options, context, executed=[], forbidden=set(),
                               lower_bounds=lower_bounds, ur=ur,
                               creation_order=self.get_next_creation())

        self.root = s0
        # open nodes
        self.states = [s0]
        self.actions = [(s0, ActionExpand())]  # tuples of state, action
        
        # connected
        self.done = []
        # impossible
        self.abandoned = []
        # expanded
        self.expanded = []

        # extra ndps not present in library
        self.additional = {}  # str -> NamedDP

        self.iteration = 0

        # for visualization
        self.G = nx.DiGraph()
        self.G_dom = nx.DiGraph()  # domination graph

    def mark_abandoned(self, s):
        self.abandoned.append(s)

    def mark_done(self, s):
        self.done.append(s)

    def mark_expanded(self, s):
        self.expanded.append(s)

    @contract(s='isinstance(OptimizationState)',
              s1='isinstance(OptimizationState)')
    def note_edge(self, s, a, s1):
        """ Note that there was a state s1 generated that
            led from s using action a """
        # print('%s --> %s' % (s.creation_order, s1.creation_order))
        self.G.add_node(s)
        self.G.add_node(s1)
        self.G.add_edge(s, s1, action=a)

    @contract(dominated='isinstance(OptimizationState)',
              dominator='isinstance(OptimizationState)')
    def note_domination_relation(self, dominated, dominator):
        """ s is-dominated-by s1 """
        self.G_dom.add_node(dominated)
        self.G_dom.add_node(dominator)
        self.G_dom.add_edge(dominated, dominator)

    def draw_tree(self, outdir):
        out_nodes = out = outdir
        if not os.path.exists(out):
            os.makedirs(out)

        fn0 = os.path.join(outdir, 'stepLAST_tree.html')
        fn = os.path.join(outdir, 'step%03d_tree.html' % self.iteration)

        r = self.get_tree_report()
        print('writing to %s   %s ' % (fn, fn0))
        r.to_html(fn)

        shutil.copy(fn, fn0)
        
        for s in self.G.nodes():
            order = s.creation_order
            fn = os.path.join(out_nodes, 'node%03d.html' % order)
            if os.path.exists(fn):
                continue
            r = get_optim_state_report(s, opt=self)
            print('writing to %r' % fn)
            r.to_html(fn)

    def get_tree_report(self):

        r = Report()
        with r.subsection('regular') as rr:
            gg = self.draw_tree_get_tree_expand()
            gg_figure(rr, 'tree', gg, do_png=True, do_dot=False, do_svg=False)

        with r.subsection('compact') as rr:
            gg = self.draw_tree_get_tree_compact()
            gg_figure(r, 'tree', gg, do_png=True, do_dot=False, do_svg=False)
        return r

    def draw_tree_get_tree_expand(self):
        def label_for_node(n):
            s = '#%s' % n.creation_order
            s += ' (%d)' % len(n.context.names)
            return s

        def label_for_edge(n1, a, n2):  # @UnusedVariable
            return a.__repr__()
        
        return self.draw_tree_get_tree(label_for_edge, label_for_node)

    def draw_tree_get_tree_compact(self):
        def label_for_node(n):
            nactions = len([() for (s, _) in self.actions if s is n])
            s = '#%s' % n.creation_order

            #             s += ' (%d)' % len(n.context.names)
            if nactions:
                s += ' (%d)' % nactions
            return s

        def label_for_edge(n1, a, n2):  # @UnusedVariable
            return a.__repr__()[:1]  # first letter

        return self.draw_tree_get_tree(label_for_edge, label_for_node)

    def draw_tree_get_tree(self, label_for_edge, label_for_node):
        gg = my_gvgen.GvGen(options="rankdir=TB")
        n2ggn = {}
        G = self.G

        open_states = [s for (s, _) in self.actions]
        def get_ggn_node(n):
            assert n in G.nodes()
            if not n in n2ggn:
                parent = None
                label = label_for_node(n)
                ggn = gg.newItem(label, parent=parent)

                n2ggn[n] = ggn
                if n in open_states:
                    color = 'blue'  # open
                elif n in self.done:
                    color = 'green'
                elif n in self.abandoned:
                    color = 'red'  # closed
                elif n in self.expanded:
                    color = 'gray'  #
                else:
                    color = 'black'

                gg.propertyAppend(ggn, 'color', color)

            return n2ggn[n]

        for n in G.nodes():
            get_ggn_node(n)

        for n1, n2 in G.edges():
            a = G.get_edge_data(n1, n2)['action']
            gn1 = get_ggn_node(n1)
            gn2 = get_ggn_node(n2)
            label = label_for_edge(n1, a, n2)
            gg.newLink(gn1, gn2, label)

        # domination is dashed
        for n1, n2 in self.G_dom.edges():
            # print('drawing dom %s -> %s' % (n1.creation_order, n2.creation_order))
            gn1 = get_ggn_node(n1)
            gn2 = get_ggn_node(n2)
            label = "D"
            l = gg.newLink(gn1, gn2, label)
            gg.propertyAppend(l, 'style', 'dashed')

        return gg
        

    def print_status(self):
        print('nactions: %3d open: %3d  done: %3d  abandoned: %3d' %
              (len(self.actions), len(self.states),
                                                        len(self.done),
                                                        len(self.abandoned)))

    def is_done(self):
        return not self.actions

    def step(self):
        gc.collect()
        self.iteration += 1
        
        if not self.actions:
            print('Done - no actions left')
            return
            
        (s0, a0) = self.choose_action()
        s0.info('Popped at iteration %d with %s' % (self.iteration, a0))
        
        new_actions = a0.__call__(self, s0)

        for (s, a) in new_actions:

            print('%s -> %s' % (a0, a))
            self.actions.append((s,a))
            
    def already_known(self, s1): 
        if ((not s1 in self.states) and
            (not s1 in self.done) and
            (not s1 in self.abandoned) and
            (not s1 in self.expanded)):
            return False
        else:
            return True

    def choose_action(self):
        # choose connect actions first
        if not self.actions: raise ValueError('no actions')
        for i, (_s, a) in enumerate(self.actions):
            from mcdp_opt.actions import ActionConnect
            if isinstance(a, ActionConnect):
                return self.actions.pop(i)  # (s, a)
        # otherwise breadth-first
        return self.actions.pop(0)

    def is_dominated_by_open(self, s1):
        for s in self.states:
            if s1 is s:
                raise ValueError('same state')
            if s1.creation_order == s.creation_order:
                raise ValueError('same id, different state?')
            if self.dominates(s, s1):
                return True, s
        return False, None

    def dominates(self, s1, s2):
        
        n1 = (40 - s1.num_connection_options, s1.num_resources_need_connecting)
        n2 = (40 - s2.num_connection_options, s2.num_resources_need_connecting)
        N = PosetProduct((Nat(), Nat()))
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
        print('Solving')

        dp = ndp.get_dp()
        # print(ndp)
        # print(dp.repr_long())

        ur = dp.solve(f)
        
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

        att = MCDPConstants.ATTR_LOAD_NAME
        a = getattr(ndp, att, None)

        # TODO: check if there is a loop
        ndp = ndp.abstract()
        if a:
            setattr(ndp, att, a)

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
        
        
    def get_next_creation(self):
        n = self.num_created
        self.num_created += 1
        return n
        
class ActionExpand():
    def __init__(self):
        pass

    @contract(returns=list)    
    def __call__(self, opt, s):
        """ Returns a list of (state, action) """
        done, actions = s.iteration()
        if done:
            opt.mark_done(s)
            return []

        s.info('Generated %d actions' % len(actions))

        if not actions:
            s.info("No actions available, placing in abandoned")
            opt.mark_abandoned(s)
            return []
                
        expanded = [(s, a) for  a in actions]
        opt.mark_expanded(s)
        return expanded
                     
