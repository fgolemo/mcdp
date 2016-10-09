from abc import ABCMeta, abstractmethod
from contracts import contract
from contracts.utils import check_isinstance, raise_desc
from mcdp_opt.context_utils import clone_context
from mcdp_posets.uppersets import upperset_product_multi, upperset_project
from mocdp.comp.context import CFunction, CResource, Connection

class Action():

    __metaclass__ = ABCMeta

    def __call__(self, opt, s):
        raise NotImplementedError(type(self))

class ActionCreate(Action):

    __metaclass__ = ABCMeta

    def __init__(self):
        # actions that will be forbidden from now on
        self.forbidden = set()

    def add_forbidden(self, a):
        check_isinstance(a, Action)
        self.forbidden.add(a)

    def __call__(self, opt, s):
        s2 = self.call(opt, s)

        s.info('Created from #%s.' % s.creation_order)
        s.info('Using action %s' % self)

        opt.note_edge(s, self, s2)

        if opt.already_known(s2):
            print('already known')
            return []

        if len(s2.ur.minimals) == 0:
            msg = 'Unfortunately this is not feasible (%s)' % s2.ur.P
            msg += '%s' % s2.lower_bounds
            s2.info(msg)
            opt.mark_abandoned(s2)
            return []

        dominated, by_what = opt.is_dominated_by_open(s2)

        if dominated:
            s2.info('Dominated by #%s' % by_what.creation_order)
            opt.mark_abandoned(s2)
            opt.note_domination_relation(dominated=s2, dominator=by_what)
            return []

        s.info('Expanded.')

        opt.mark_expanded(s)
        opt.states.append(s2)

        from mcdp_opt.optimization import ActionExpand
        return [(s2, ActionExpand())]

    @abstractmethod
    def call(self, opt, s):
        pass

class ActionConnect(ActionCreate):
    @contract(f=CFunction, r=CResource)
    def __init__(self, f, r):
        self.cfunction = f
        self.cresource = r

    def call(self, opt, c):
        context = clone_context(c.context)

        con = Connection(self.cresource.dp, self.cresource.s,
                         self.cfunction.dp, self.cfunction.s)

        context.add_connection(con)
        executed = c.executed + [self]
        # XXX
        forbidden = c.forbidden + [self]

        from mcdp_opt.partial_result import get_lower_bound_ndp
        ndp, table = get_lower_bound_ndp(context)
        (R, ur), tableres = opt.get_lower_bounds(ndp, table)
        lower_bounds = tableres

        from mcdp_opt.optimization_state import OptimizationState
        s2 = OptimizationState(opt=opt, options=c.options,
                                 context=context, executed=executed,
                                 forbidden=forbidden, lower_bounds=lower_bounds,
                                 ur=ur, creation_order=opt.get_next_creation())
        return s2


    def __repr__(self):
        return "Connect(%s:%s->%s:%s)" % (self.cresource.dp, self.cresource.s,
                                          self.cfunction.dp, self.cfunction.s)

    def __eq__(self, a):
        return isinstance(a, ActionAddNDP) and \
            (a.cfunction, a.cresource) == (self.cfunction, self.cresource)

class ActionAddNDP(ActionCreate):
    """ Instance id_ndp and connect to cresource """

    def __eq__(self, a):
        return isinstance(a, ActionAddNDP) and \
            (a.id_ndp, a.fname, a.cresource) == (self.id_ndp, self.fname, self.cresource)

    @contract(id_ndp=str, fname=str, cresource=CResource)
    def __init__(self, id_ndp, fname, cresource):
        self.id_ndp = id_ndp
        self.fname = fname
        self.cresource = cresource

    def call(self, opt, c):
        context = clone_context(c.context)

        ndp = opt.load_ndp(self.id_ndp)

        if not self.id_ndp in context.names:
            name = self.id_ndp
        else:
            name = context.new_name(prefix=self.id_ndp)
        context.add_ndp(name, ndp)

        con = Connection(self.cresource.dp, self.cresource.s, name, self.fname)
        context.add_connection(con)

        executed = c.executed + [self]
        # XXX
        forbidden = c.forbidden + [self]

        lower_bounds = dict(**c.lower_bounds)

        # get lower bounds for the new one
        lower_bounds_a = get_new_lowerbounds(context=context, name=name,
                                             lower_bounds=lower_bounds)
        for k, u in lower_bounds_a.items():
            if len(u.minimals) == 0:
                msg = 'Unfeasible: %s' % (lower_bounds_a)
                raise Exception(msg)

        print('new lowerbounds: %s' % lower_bounds_a)
        for rname in ndp.get_rnames():
            r = CResource(name, rname)
            if not r in lower_bounds_a:
                msg = 'Cannot find resource.'
                raise_desc(ValueError, msg, r=r, lower_bounds_a=lower_bounds_a)
            lower_bounds[r] = lower_bounds_a[r]

        del lower_bounds[self.cresource]

        from mcdp_opt.partial_result import get_lower_bound_ndp
        ndp, table = get_lower_bound_ndp(context)
        (_R, ur), _tableres = opt.get_lower_bounds(ndp, table)

        from mcdp_opt.optimization_state import OptimizationState
        s2 = OptimizationState(opt=opt, options=c.options,
                                 context=context, executed=executed,
                                 forbidden=forbidden, lower_bounds=lower_bounds, ur=ur,
                                 creation_order=opt.get_next_creation())

        s2.info('Parent: #%s' % c.creation_order)
        s2.info('Action: #%s' % self)
        return s2


    def __repr__(self):
        return "AddNDP(%s:%s provides %s:%s)" % (self.id_ndp, self.fname,
                                                 self.cresource.dp,
                                                 self.cresource.s)

def get_new_lowerbounds(context, name, lower_bounds):
    connections = context.connections
    ndp = context.names[name]
    fnames = ndp.get_fnames()
    
    def get_lb_for_fname(fname):
        cf = CFunction(name, fname)
        is_connected, cresource = get_connection_to_function(connections, cf)
        if is_connected:
            lb = lower_bounds[cresource]
        else:
            F = context.get_ftype(cf)
            lb = F.Us(F.get_minimal_elements())

#         print('lb for %r: %s' % (fname, lb))
        return lb

    lbs = []
    for fname in fnames:
        lb = get_lb_for_fname(fname)
        lbs.append(lb)
    
    if len(fnames) == 1:
        lbF = lbs[0]
    else:
        lbF = upperset_product_multi(tuple(lbs))

    dp = ndp.get_dp()

    ur = dp.solveU(lbF)
#     print('Solving with %s -> %s ' % (lbF, ur))

    lower_bounds_new = {}
    rnames = ndp.get_rnames()
    if len(rnames) == 1:
        cr = CResource(name, rnames[0])
        lower_bounds_new[cr] = ur
    else:
        for i, rname in enumerate(rnames):
            uri = upperset_project(ur, i)
            cr = CResource(name, rname)
            lower_bounds_new[cr] = uri

    return lower_bounds_new

    
@contract(cresource=CResource, returns='tuple(*, $CFunction|None)')
def get_connection_to_function(connections, cfunction):
    for c in connections:
        if c.dp2 == cfunction.dp and c.s2 == cfunction.s:
            return True, CResource(c.dp1, c.s1)
    return False, None

    
