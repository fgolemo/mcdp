from .actions import ActionAddNDP, ActionConnect
from .context_utils import get_compatible_unconnected_functions
from .optimization import Optimization
from .partial_result import get_lower_bound_ndp
from contracts import contract
from contracts.utils import raise_desc
from mcdp_lang import parse_poset
from mcdp_lang.blocks import get_missing_connections
from mcdp_posets import get_types_universe
from mcdp_posets.uppersets import UpperSet
from mocdp.comp.composite import CompositeNamedDP
from mocdp.comp.context import CResource, Connection

_ = UpperSet

class OptimizationState():
    """
        
    
    """
    @contract(opt=Optimization, lower_bounds='dict($CResource:$UpperSet)')
    def __init__(self, opt, options, context, executed, forbidden, lower_bounds, ur):
        self.opt = opt
        self.options = options

        self.context = context
        self.executed = executed
        self.forbidden = forbidden
        self.lower_bounds = lower_bounds
        self.ur = ur

        tu = get_types_universe()
        # We expect that for each unconnected resource, we have a lower bound
        unconnected_fun, unconnected_res = get_missing_connections(self.context)
        for dp, s in unconnected_res:
            r = CResource(dp,s)
            if not r in lower_bounds:
                msg = 'There is no lower bound for this resource.'
                raise_desc(ValueError, msg, r=r, lower_bounds=lower_bounds)
            r_ur = lower_bounds[r]
            R =  self.context.get_rtype(r)
            tu.check_equal(r_ur.P, R)

        # make sure we don't have extra
        for r in lower_bounds:
            assert isinstance(r, CResource), r
            R = self.context.get_rtype(r)
            assert (r.dp, r.s) in unconnected_res, (r, unconnected_res)

        # count the number

        self.num_connection_options = self._compute_connection_options()

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
        unconnected_fun, unconnected_res = get_missing_connections(self.context)

        if not unconnected_res:
            # we are done
            return True, []
        else:
            actions = self.generate_actions()

            if not actions:
#                 openR = [self.context.get_rtype(CResource(dp, s)) for dp, s in
#                          unconnected_res]
                # print('Cannot find anything to provide %r' % openR)
                pass
            return False, actions


    def get_current_ndp(self):
        return CompositeNamedDP.from_context(self.context)


    def generate_actions(self):
        """ Returns a list of actions. Actions are hashable and 
            given an OptimizationState they return another """
        actions = []

        unconnected_fun, unconnected_res = get_missing_connections(self.context)
        for dp, rname in unconnected_res:
            r = CResource(dp, rname)
            r_actions = []
            R = self.context.get_rtype(r)
            # print('need to look for somebody implementing %s' % R)
            lb = self.lower_bounds[r]
            options = self.opt.get_providers(R=R, lb=lb)
            if not options:
                print('Nobody can provide for %s %s' % (r, lb))

            for id_ndp, fname in options:
#                 def avoid(action):
#                     for a in self.executed:
#                         if isinstance(a, ActionAddNDP) and (a.id_ndp == action.id_ndp):
#                             return True
#                     return False

                action = ActionAddNDP(id_ndp, fname, r)
                # if avoid(action):
                #     continue
#
#                 def forbidden(action):
#                     return False
#
#                     for f in self.forbidden:
#                         if action.__eq__(f):
#                             return True
#                     return False
#
#                 if forbidden(action):
#                     print('pruning')
#                 else:
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

            if not r_actions:
                # this is a resource that cannot be satisfied...
                msg = ('Nobody can provide for resource %s %s and no unconnected compatible' % (r, lb))
                msg += '\n unconn: %s' % unconnected_fun
                print(msg)
                self.msg = msg
                return []

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




