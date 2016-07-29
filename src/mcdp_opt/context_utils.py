from contracts import contract
from mcdp_posets.types_universe import get_types_universe
from mocdp.comp.context import CFunction, Context


@contract(returns='list($CFunction)')
def get_compatible_unconnected_functions(R, context, unconnected_fun):
    tu = get_types_universe()
    res = []
    for dp1, fname in unconnected_fun:
        f = CFunction(dp1, fname)
        F = context.get_ftype(f)
        if tu.leq(R, F):
            res.append(f)
    return res

def clone_context(c):
    c2 = Context()
    c2.names = dict(**c.names)
    c2.connections = list(c.connections)
    c2.fnames = list(c.fnames)
    c2.rnames = list(c.rnames)
    return c2


def create_context0(
         flabels, F0s, f0s,
         rlabels, R0s, r0s):

    for fname, F0, f0 in zip(flabels, F0s, f0s):
        F0.belongs(f0)
    for rname, R0, r0 in zip(flabels, R0s, r0s):
        R0.belongs(r0)

    context = Context()

    for fname, F in zip(flabels, F0s):
        context.add_ndp_fun_node(fname, F)

    for rname, R in zip(rlabels, R0s):
        context.add_ndp_res_node(rname, R)

    return context
