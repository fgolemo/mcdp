# -*- coding: utf-8 -*-
from collections import defaultdict
from contracts.library.dummy import Any
from mocdp.comp import CompositeNamedDP, SimpleWrap
from mocdp.dp import (
    Constant, GenericUnary, Identity, Limit, Max, Min, Product, ProductN, Sum,
    SumN)
from mocdp.lang.blocks import get_missing_connections
from mocdp.posets import (BottomCompletion, R_dimensionless, Rcomp, RcompUnits,
    TopCompletion)
from mocdp.posets.rcomp_units import format_pint_unit_short
from system_cmd import CmdException, system_cmd_result
import os
import warnings


class GraphDrawingContext():
    def __init__(self, gg, parent, yourname, level=0):
        self.gg = gg
        self.parent = parent
        self.yourname = yourname
        self.level = level
        
    def newItem(self, label):
        return self.gg.newItem(label, parent=self.parent)
        
    def child_context(self, parent, yourname):
        c = GraphDrawingContext(gg=self.gg, parent=parent, yourname=yourname,
                                level=self.level + 1)
        return c

    def styleApply(self, sname, n):
        self.gg.styleApply(sname, n)

    def newLink(self, a, b, label=None):
        return self.gg.newLink(a, b, label)

    def styleAppend(self, a, b, c):
        self.gg.styleAppend(a, b, c)

    def should_I_enclose(self, ndp):
        warnings.warn('Add option here')
        if self.level == 0:
            return False

        return False
        return True
        if ndp.is_fully_connected():
            return False
        else:
            return self.yourname is not None


def gvgen_from_ndp(ndp):
    import gvgen  # @UnresolvedImport
    gg = gvgen.GvGen(options="rankdir=LR")
    cluster_functions = gg.newItem("")

    gg.styleAppend("external", "shape", "none")
    gg.styleAppend("external_cluster", "shape", "box")
    gg.styleAppend("external_cluster", "color", "red")

    gg.styleAppend("connector", "shape", "plaintext")
    gg.styleAppend("simple", "shape", "box")
    gg.styleAppend("simple", "style", "rounded")

    gg.styleAppend("constant", "shape", "plaintext")

    gg.styleAppend("unconnected_node", "shape", "plaintext")
    gg.styleAppend("unconnected_node", "fontcolor", "red")
    gg.styleAppend("unconnected_link", "color", "red")
    gg.styleAppend("unconnected_link", "fontcolor", "red")

    gg.styleAppend("container", "shape", "box")
    gg.styleAppend("container", "style", "rounded")

    gg.styleAppend("sum", "shape", "box")
    gg.styleAppend("sum", "style", "rounded")
    gg.styleAppend('sum', 'image', 'icons/sum.png')
    gg.styleAppend('sum', 'imagescale', 'true')
    gg.styleAppend('sum', 'fixedsize', 'true')

    gg.styleAppend("leq", "shape", "plaintext")
    gg.styleAppend('leq', 'image', 'icons/leq.png')
    gg.styleAppend('leq', 'imagescale', 'true')
    gg.styleAppend('leq', 'fixedsize', 'true')

    # a red dot for unconnected
    gg.styleAppend('unconnected', 'shape', 'point')
    gg.styleAppend('unconnected', 'width', '0.1')
    gg.styleAppend('unconnected', 'color', 'red')

    gg.styleAppend('splitter', 'style', 'filled')
    gg.styleAppend('splitter', 'shape', 'point')
    gg.styleAppend('splitter', 'width', '0.1')
    gg.styleAppend('splitter', 'color', 'black')
    gg.styleAppend('splitter', 'fillcolor', 'black')
    gg.styleAppend('splitter_link', 'dir', 'none')

    gg.styleAppend('limit', 'color', 'black')

    gdc = GraphDrawingContext(gg=gg, parent=None, yourname=None)
    functions, resources = create(gdc, ndp)

    for fname, n in functions.items():
        F = ndp.get_ftype(fname)
        label = fname + ' ' + format_unit(F)
        x = gg.newItem(label, parent=cluster_functions)
        gg.styleApply("external", x)

        l = gg.newLink(x, n)
        if False:
            gg.propertyAppend(l, "headport", "w")
            gg.propertyAppend(l, "tailport", "e")

    cluster_resources = gg.newItem("")
    for rname, n in resources.items():
        R = ndp.get_rtype(rname)
        label = rname + ' ' + format_unit(R)
        x = gg.newItem(label, parent=cluster_resources)
        gg.styleApply("external", x)

        l = gg.newLink(n, x)

        if False:
            gg.propertyAppend(l, "headport", "w")
            gg.propertyAppend(l, "tailport", "e")

    gg.styleApply("external_cluster", cluster_functions)
    gg.styleApply("external_cluster", cluster_resources)

    # XXX: for some reason cannot turn off the border, using "white"
#     gg.propertyAppend(cluster_functions, "shape", "plain")
#     gg.propertyAppend(cluster_functions, "color", "white")
#     gg.propertyAppend(cluster_resources, "shape", "box")
#     gg.propertyAppend(cluster_resources, "color", "red")

    return gg

def create(gdc, ndp):
    if isinstance(ndp, SimpleWrap):
        res = create_simplewrap(gdc, ndp)

    if isinstance(ndp, CompositeNamedDP):
        res = create_composite(gdc, ndp)

    functions, resources = res

    for fn in ndp.get_fnames():
        assert fn in functions
    for rn in ndp.get_rnames():
        assert rn in resources

    return res

def resize_icon(filename, imagepath, size):
    
    from cdpview.go import safe_makedirs
    res = os.path.join(imagepath, 'resized', str(size))
    safe_makedirs(res)
    resized = os.path.join(res, os.path.basename(filename))
    if not os.path.exists(resized):
        cmd = ['convert', filename, '-resize', '%s' % size, resized]
        try:
            # print('running graphviz')
            system_cmd_result(cwd='.', cmd=cmd,
                     display_stdout=False,
                     display_stderr=False,
                     raise_on_error=True)
            # print('done')
        except CmdException:
            raise
    return resized

def choose_best_icon(iconoptions, imagepath='icons'):
    for option in iconoptions:
        if option is None: continue
        imagename = os.path.join(imagepath, option) + '.png'
        if os.path.exists(imagename):
            return resize_icon(imagename, imagepath, 100)
    return None

def is_simple(ndp):
    return isinstance(ndp, SimpleWrap) and isinstance(ndp.dp,
     (Min, Max, Identity, GenericUnary, Sum, SumN, Product, ProductN))


def create_simplewrap(gdc, ndp):
    assert isinstance(ndp, SimpleWrap)
    label = str(ndp)

    sname = None  # name of style to apply, if any

    special = [
        (Sum, ''),
        (SumN, ''),
        (Product, ''),
        (ProductN, ''),
    ]
    classname = type(ndp.dp).__name__

    icon = ndp.get_icon()

    iconoptions = [gdc.yourname, icon, classname, 'default']
    best_icon = choose_best_icon(iconoptions)

    simple = (Min, Max, Identity, GenericUnary)
    only_string = isinstance(ndp.dp, simple)
    if only_string:

        label = type(ndp.dp).__name__
        if isinstance(ndp.dp, GenericUnary):
            label = ndp.dp.__repr__()

        sname = 'simple'
    else:
        for t, _ in special:
            if isinstance(ndp.dp, t):
                sname = t
                gdc.styleAppend(sname, 'image', best_icon)
                gdc.styleAppend(sname, 'imagescale', 'true')
                gdc.styleAppend(sname, 'fixedsize', 'true')
                gdc.styleAppend(sname, 'height', '1.0')
                gdc.styleAppend(sname, "shape", "none")
                label = ''
                break
        else:
            if best_icon is not None:
                if gdc.yourname is not None:
                    shortlabel = gdc.yourname
                else:
                    shortlabel = classname
                # shortlabel = '<I><B>%sa</B></I>' % shortlabel
                sname = classname
                gdc.styleAppend(sname, 'imagescale', 'true')
                gdc.styleAppend(sname, 'height', '1.0')
                gdc.styleAppend(sname, "shape", "box")
                gdc.styleAppend(sname, "style", "rounded")
                label = ("<TABLE CELLBORDER='0' BORDER='0'><TR><TD>%s</TD></TR>"
                "<TR><TD><IMG SRC='%s' SCALE='TRUE'/></TD></TR></TABLE>")
                label = label % (shortlabel, best_icon)
            else:
                # print('Image %r not found' % imagename)
                sname = None


    if isinstance(ndp.dp, Constant):
        R = ndp.dp.get_res_space()
        c = ndp.dp.c
        label = R.format(c) + ' ' + format_unit(R)
        sname = 'constant'

    if isinstance(ndp.dp, Limit):
        F = ndp.dp.get_fun_space()
        c = ndp.dp.limit
        label = F.format(c) + ' ' + format_unit(F)
        sname = 'limit'

#     if label[:2] != '<T':
#         # Only available in svg or cairo renderer
#         label = '<I>%s</I>' % label

    node = gdc.newItem(label)

    if isinstance(ndp.dp, (Sum, SumN)):
        gdc.styleApply("sum", node)

    if sname:
        gdc.styleApply(sname, node)

    functions = {}
    resources = {}
    for rname in ndp.get_rnames():
        resources[rname] = node
    for fname in ndp.get_fnames():
        functions[fname] = node

    return functions, resources

def format_unit(R):
    if R == BottomCompletion(TopCompletion(Any())):
        return '[*]'
    warnings.warn('fix bug')
    if isinstance(R, BottomCompletion):
        return '[*]'
    if R == R_dimensionless:
#         return '[R]'
        return '[]'
    elif isinstance(R, RcompUnits):
        return '[%s]' % format_pint_unit_short(R.units)
    elif isinstance(R, Rcomp):
        return '[R]'
    else:
        return '[%s]' % str(R)
            
def create_composite(gdc, ndp):  # @UnusedVariable
    assert isinstance(ndp, CompositeNamedDP)

    if gdc.should_I_enclose(ndp):
        c = gdc.newItem(gdc.yourname)
        gdc.styleApply('container', c)
        gdc = gdc.child_context(parent=c, yourname=gdc.yourname)


    names2resources = defaultdict(lambda: {})
    names2functions = defaultdict(lambda: {})

    def get_connections_to_function(name):
        assert ndp.context.is_new_function(name)
        res = []
        for c in ndp.context.connections:
            if c.dp1 == name:
                res.append(c)
        # print('Connection to %r: %r' % (name, res))
        return res

    def get_connections_to_resource(name):
        assert ndp.context.is_new_resource(name)
        res = []
        for c in ndp.context.connections:
            if c.dp2 == name:
                res.append(c)
        # print('Connection to %r: %r' % (name, res))
        return res

    # it is connected to only one
    def is_function_with_one_connection(name):
        return ndp.context.is_new_function(name) and len(get_connections_to_function(name)) == 1

    # it is connected to only one
    def is_resource_with_one_connection(name):
        return ndp.context.is_new_resource(name) and len(get_connections_to_resource(name)) == 1

    def is_function_with_no_connections(name):
        return ndp.context.is_new_function(name)  and len(get_connections_to_function(name)) == 0

    def is_resource_with_no_connections(name):
        return ndp.context.is_new_resource(name)   and len(get_connections_to_resource(name)) == 0

    def get_connections_to_dp_resource(name, rn):
        assert name in ndp.context.names
        res = []
        for c in ndp.context.connections:
            if c.dp1 == name and c.s1 == rn:
                res.append(c)
        return res

    def resource_has_more_than_one_connected(name, rn):
        res = get_connections_to_dp_resource(name, rn)
        # print(ndp.context.connections)
        # print('number connected to %s.%s: %s' % (name, rn, len(res)))
        return len(res) > 1
        
    for name, value in ndp.context.names.items():
        # do not create these edges
        if is_function_with_one_connection(name):
            # print('Skipping extra node for f %r' % name)
            continue

        if is_function_with_no_connections(name):
            # only draw the balloon
            item = gdc.newItem("%s" % name)
            gdc.styleApply('unconnected', item)
            for fn in value.get_fnames():
                names2functions[name][fn] = item
            for rn in value.get_rnames():
                names2resources[name][rn] = item
            continue

        if is_resource_with_no_connections(name):
            # only draw the balloon instead of "Identity" node
            item = gdc.newItem("%s" % name)
            gdc.styleApply('unconnected', item)
            for fn in value.get_fnames():
                names2functions[name][fn] = item
            for rn in value.get_rnames():
                names2resources[name][rn] = item
            continue

        if is_resource_with_one_connection(name):
            # print('Skipping extra node for r %r' % name)
            continue

        child = gdc.child_context(yourname=name, parent=gdc.parent)
        f, r = create(child, value)
        # print('name %s -> functions %s , resources = %s' % (name, list(f), list(r)))
        names2resources[name] = r
        names2functions[name] = f
        
        for rn in names2resources[name]:
            if resource_has_more_than_one_connected(name, rn):
                # create new splitter
                orig = names2resources[name][rn]
                split = gdc.newItem('')
                gdc.styleApply('splitter', split)
                l = gdc.newLink(orig, split)
                gdc.gg.propertyAppend(l, "constraint", "false")
                gdc.gg.propertyAppend(l, "weight", "0")

                gdc.styleApply('splitter_link', l)
                names2resources[name][rn] = split
        
    ignore_connections = set()
    for name, value in ndp.context.names.items():
        if  is_function_with_one_connection(name):
            only_one = get_connections_to_function(name)[0]
            ignore_connections.add(only_one)
            node = names2functions[only_one.dp2][only_one.s2]
            names2functions[name][only_one.s1] = node
            # XXX: not really sure
            names2resources[name][only_one.s1] = node

    for name, value in ndp.context.names.items():
        if is_resource_with_one_connection(name):
            only_one = get_connections_to_resource(name)[0]
            ignore_connections.add(only_one)
            node = names2resources[only_one.dp1][only_one.s1]
            names2resources[name][only_one.s2] = node
            # XXX: not really sure
            names2functions[name][only_one.s2] = node


    for c in ndp.context.connections:
        if c in ignore_connections:
            continue
        dpa = names2functions[c.dp2]
        n_a = dpa[c.s2]
        dpb = names2resources[c.dp1]
        n_b = dpb[c.s1]

        second_simple = is_simple(ndp.context.names[c.dp2])
        first_simple = is_simple(ndp.context.names[c.dp1])
        any_simple = second_simple or first_simple
        both_simple = second_simple and first_simple

        # TODO: make parameter
        skip = second_simple

        ua = ndp.context.names[c.dp2].get_ftype(c.s2)
        ub = ndp.context.names[c.dp1].get_rtype(c.s1)

        if skip:
            l1 = gdc.newLink(n_b, n_a , label=get_signal_label(c.s1, ub))

        else:
            box = gdc.newItem('')  # '≼')
            gdc.styleApply("leq", box)
    
            l1 = gdc.newLink(box, n_a , label=get_signal_label(c.s2, ua))
            if False:
                gdc.gg.propertyAppend(l1, "headport", "w")
    
            l2 = gdc.newLink(n_b, box, label=get_signal_label(c.s1, ub))
            if False:
                gdc.gg.propertyAppend(l2, "tailport", "e")
            
            if False:
                gdc.gg.propertyAppend(l1, 'constraint', 'false')
                gdc.gg.propertyAppend(l2, 'constraint', 'false')
    
            if both_simple:
                weight = 0
            elif any_simple:
                weight = 0.5
            else:
                weight = 1
            if any_simple:
                gdc.gg.propertyAppend(l2, 'weight', '%s' % weight)
                gdc.gg.propertyAppend(l1, 'weight', '%s' % weight)
                


    unconnected_fun, unconnected_res = get_missing_connections(ndp.context)
    for (dp, fn) in unconnected_fun:
        x = gdc.newItem('')
        gdc.styleApply("unconnected_node", x)

        n = names2functions[dp][fn]
        F = ndp.context.names[dp].get_ftype(fn)
        l = gdc.newLink(x, n, label=get_signal_label(fn, F))
        gdc.styleApply('unconnected_link', l)

    for (dp, rn) in unconnected_res:
        x = gdc.newItem('')
        gdc.styleApply("unconnected_node", x)

        n = names2resources[dp][rn]
        R = ndp.context.names[dp].get_rtype(rn)
        l = gdc.newLink(n, x, label=get_signal_label(rn, R))
        gdc.styleApply('unconnected_link', l)


    functions = {}
    resources = {}


    for rname in ndp.get_rnames():
        name = ndp.context.get_name_for_res_node(rname)
        resources[rname] = list(names2resources[name].values())[0]

    for fname in ndp.get_fnames():
        name = ndp.context.get_name_for_fun_node(fname)
        functions[fname] = list(names2functions[name].values())[0]
 
    return functions, resources

def get_signal_label(name, unit):
    # no label for automatically generated ones
    for i in range(9):
        if str(i) in name:
            name = ""
    s2 = format_unit(unit)
    if name:
        return name + ' ' + s2
    else:
        return s2


