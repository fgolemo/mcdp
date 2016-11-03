# -*- coding: utf-8 -*-
from .parts import CDPLanguage
from contracts.utils import indent
from mocdp.comp import NotConnected

CDP = CDPLanguage

def get_missing_connections(context):
    connected_fun = set()  # contains (name, f)
    connected_res = set()  # contains (name, f)
    for c in context.connections:
        connected_fun.add((c.dp2, c.s2))
        connected_res.add((c.dp1, c.s1))

    available_fun = set()
    available_res = set()
    # look for the open connections
    for n, ndp in context.names.items():

        if not context.is_new_function(n):
            for fn in ndp.get_fnames():
                available_fun.add((n, fn))

        if not context.is_new_resource(n):
            for rn in ndp.get_rnames():
                available_res.add((n, rn))

    unconnected_fun = available_fun - connected_fun
    unconnected_res = available_res - connected_res

    return unconnected_fun, unconnected_res


def check_missing_connections(context):
    """ Checks that all resources and functions are connected. """

    def xsorted(x):
        return sorted(x)
    
    unconnected_fun, unconnected_res = get_missing_connections(context)

    s = ""
    if unconnected_fun:
        s += "There are some unconnected functions:"
        
        
        
        for n, fn in xsorted(unconnected_fun):
            s += '\n- function %r of dp %r' % (fn, n)
            if False:
                msg = 'One way to fix this is to add an explicit function:\n'
                fn2 = 'f'
                fix = "provides %s [unit]" % fn2
                if context.is_new_resource(n):
                    ref = n
                else:
                    ref = '%s.%s' % (n, fn)
                fix += '\n' + "%s >= %s" % (ref, fn2)
                msg += indent(fix, '    ')
                s += '\n' + indent(msg, 'help: ')

    if unconnected_res:
        s += "\nThere are some unconnected resources:"
        for n, rn in xsorted(unconnected_res):
            s += '\n- resource %s of dp %r' % (rn, n)
            if False:
                msg = 'One way to fix this is to add an explicit resource:\n'
                rn2 = 'r'
                fix = "requires %s [unit]" % rn2
                if context.is_new_function(n):
                    ref = n
                else:
                    ref = '%s.%s' % (n, rn)
                # todo: omit '.' if n is
                fix += '\n' + "%s >= %s" % (rn2, ref)
                msg += indent(fix, '    ')
                s += '\n' + indent(msg, 'help: ')

    if s:
        raise NotConnected(s)
    
