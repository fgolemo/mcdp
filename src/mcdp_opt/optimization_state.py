from .actions import ActionAddNDP, ActionConnect
from .context_utils import get_compatible_unconnected_functions
from .optimization import Optimization
from .partial_result import get_lower_bound_ndp
from contracts import contract
from contracts.utils import raise_desc
from mcdp_lang import parse_poset
from mcdp_lang.blocks import get_missing_connections
from mcdp_posets import get_types_universe
from mcdp_posets.uppersets import UpperSet, UpperSets
from mocdp.comp.composite import CompositeNamedDP
from mocdp.comp.context import CResource, Connection
from mocdp.memoize_simple_imp import memoize_simple
from mocdp.exceptions import do_extra_checks

_ = UpperSet

class OptimizationState():
    """
        
    
    """
    @contract(opt=Optimization, lower_bounds='dict($CResource:$UpperSet)',
              creation_order=int, forbidden='set')
    def __init__(self, opt, options, context, executed, forbidden, lower_bounds, ur,
                 creation_order):

        print('CREATED %s' % creation_order)
        self.opt = opt
        self.options = options

        self.context = context
        self.executed = executed
        self.forbidden = forbidden
        self.lower_bounds = lower_bounds
        self.ur = ur

        if do_extra_checks():
            tu = get_types_universe()
            # We expect that for each unconnected resource, we have a lower bound
            _unconnected_fun, unconnected_res = get_missing_connections(self.context)
            for dp, s in unconnected_res:
                r = CResource(dp, s)
                if not r in lower_bounds:
                    msg = 'There is no lower bound for this resource.'
                    raise_desc(ValueError, msg, r=r, lower_bounds=lower_bounds)
                r_ur = lower_bounds[r]
                R = self.context.get_rtype(r)
                tu.check_equal(r_ur.P, R)

            # make sure we don't have extra
            for r in lower_bounds:
                assert isinstance(r, CResource), r
                R = self.context.get_rtype(r)
                assert (r.dp, r.s) in unconnected_res, (r, unconnected_res)

        self.num_connection_options = self._compute_connection_options()

        self.hash = self._compute_hash()

        self._msg = ""

        for r, lb in lower_bounds.items():
            R = self.context.get_rtype(r)
            self.info('lb %s >= %s' % (r, lb), quiet=True)

        self.num_resources_need_connecting = self.compute_num_resources_need_connecting()
        self.creation_order = creation_order

    def compute_num_resources_need_connecting(self):
        n = 0
        for r, lb in self.lower_bounds.items():
            R = self.context.get_rtype(r)
            UR = UpperSets(R)
            if not UR.equal(lb, UR.get_bottom()):
                n += 1
        return n


    def get_info(self):
        return self._msg

    def info(self, msg, quiet=False):
        """ Writes a message for this node. """
        if not quiet:
            print('#%s: %s' % (self.creation_order, msg))
        self._msg += msg
        self._msg += "\n"

    def _compute_hash(self):
        names = frozenset(self.context.names)
        connections = frozenset(self.context.connections)
        attrs = (names, connections)
        return attrs.__hash__()

    def __hash__(self):
        return self.hash
        
    def _compute_connection_options(self):
        unconnected_fun, unconnected_res = get_missing_connections(self.context)
        n = 0
        usd = parse_poset('USD')
        for (dp, s) in unconnected_res:
            r = CResource(dp, s)
            R = self.context.get_rtype(r)
            foptions = get_compatible_unconnected_functions(R, self.context, unconnected_fun)
            ok = []
            for f in foptions:
                if R == usd and would_introduce_cycle(self.context, r=r, f=f):
                    print('skipping %r - %r because it adds a cycle' % (r, f))
                    continue
                ok.append(f)
                unconnected_fun.remove((f.dp, f.s))
            if ok:
                n += 1
        return n

    @contract(returns='tuple($CompositeNamedDP, dict(*:str))')
    def get_lower_bound_ndp(self):
        ndp2, table = get_lower_bound_ndp(self.context)
        return ndp2, table

    def __eq__(self, other):
        c1 = self.context
        c2 = other.context
        return set(c2.names) == set(c1.names) and set(c2.connections) == set(c1.connections)

    def iteration(self):
        _, unconnected_res = get_missing_connections(self.context)

        if not unconnected_res:
            # we are done
            return True, []
        else:
            actions = self.generate_actions()
            return False, actions

    @memoize_simple
    def get_current_ndp(self):
        return CompositeNamedDP.from_context(self.context)

    def generate_actions(self):
        """ Returns a list of actions. Actions are hashable and 
            given an OptimizationState they return another """
        self.info('generating actions')

        unconnected_fun, unconnected_res = get_missing_connections(self.context)
        unconnected = [CResource(*u) for u in unconnected_res]

        r2actions = {}  # list of list
        for r in unconnected:
            r_actions = []
            R = self.context.get_rtype(r)
            # print('need to look for somebody implementing %s' % R)
            lb = self.lower_bounds[r]
            options = self.opt.get_providers(R=R, lb=lb)
            if not options:
                # self.info('No new providers can provide for %s %s' % (r, lb))
                pass
            else:
                for id_ndp, fname in options:
                    action = ActionAddNDP(id_ndp, fname, r)
                    r_actions.append(action)

            # connecting one available resource
            foptions = get_compatible_unconnected_functions(R, self.context, unconnected_fun)
            usd = parse_poset('USD')
            for f in foptions:
                if R == usd and would_introduce_cycle(self.context, r=r, f=f):
                    print('skipping %r - %r because it adds a cycle' % (r, f))
                    continue
                
                action = ActionConnect(r=r, f=f)
                r_actions.append(action)

            r2actions[r] = r_actions

        # all the actions above should be mutually exclusive.
        # e.g. if actions = {a1, a2, a3}
        # then if we apply a1 to s to obtain a1(s),
        # we commit to never use a1 again if we

        # If there are no options
        for r, r_actions in r2actions.items():
            lb = self.lower_bounds[r]
            if not r_actions:
                # this is a resource that cannot be satisfied...
                msg = ('Nobody can provide for resource %s %s and no unconnected compatible' % (r, lb))
                msg += '\n unconn: %s' % unconnected_fun
                self.info(msg)
                return []

        # If one option is obligated, go for it.
        # Give precedence to actions that close an edge
        for r, r_actions in r2actions.items():

            if len(r_actions) == 1:

                action = r_actions[0]

                if isinstance(action, ActionConnect):
                    # If there is only one available we do that first
                    self.info('There is only one action available for %s' % (r.__str__()))
                    return r_actions

        for r, r_actions in r2actions.items():

            if len(r_actions) == 1:
                # If there is only one available we do that first
                self.info('There is only one action available for %s' % (r.__str__()))
                return r_actions

        # concatenate all
        actions = []
        for r_actions in r2actions.values():
            actions.extend(r_actions)
        return actions

def would_introduce_cycle(context, f, r):
    if f.dp == r.dp:
        return True
    from mocdp.comp.connection import get_connection_multigraph
    from networkx.algorithms.cycles import simple_cycles

    connections1 = list(context.connections)
    con = Connection(r.dp, r.s, f.dp, f.s)
    connections2 = connections1 + [con]
    
    G1 = get_connection_multigraph(connections1)
    G2 = get_connection_multigraph(connections2)
    cycles1 = list(simple_cycles(G1))
    cycles2 = list(simple_cycles(G2))
    c1 = len(cycles1)
    c2 = len(cycles2)
#     if c1 != c2:
#         print G2.edges()
#         print('c1: %s' % cycles1)
#         print('c2: %s' % cycles2)

    return c1 != c2




