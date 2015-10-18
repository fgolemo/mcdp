# -*- coding: utf-8 -*-
from collections import defaultdict
from mocdp.comp.interfaces import CompositeNamedDP
from mocdp.comp.wrap import SimpleWrap
from mocdp.dp import Constant, Identity, Limit, Max, Min, Product, Sum
from mocdp.lang.blocks import get_missing_connections
from mocdp.posets.rcomp import R_dimensionless, Rcomp, RcompUnits
from system_cmd import CmdException, system_cmd_result
import os
from mocdp.dp.dp_sum import SumN


def gvgen_from_ndp(ndp):
    import gvgen  # @UnresolvedImport
    gg = gvgen.GvGen(options="rankdir=LR")
    cluster_functions = gg.newItem("")

    gg.styleAppend("external", "shape", "none")

    gg.styleAppend("connector", "shape", "plaintext")
    gg.styleAppend("simple", "shape", "box")
    gg.styleAppend("simple", "style", "rounded")

    gg.styleAppend("constant", "shape", "plaintext")
#     gg.styleAppend("leq", "shape", "circle")

    gg.styleAppend("unconnected_node", "shape", "plaintext")
    gg.styleAppend("unconnected_node", "fontcolor", "red")
    gg.styleAppend("unconnected_link", "color", "red")
    gg.styleAppend("unconnected_link", "fontcolor", "red")

    gg.styleAppend("sum", "shape", "box")
    gg.styleAppend("sum", "style", "rounded")
    gg.styleAppend('sum', 'image', 'icons/sum.png')
    gg.styleAppend('sum', 'imagescale', 'true')
    gg.styleAppend('sum', 'fixedsize', 'true')

    gg.styleAppend("leq", "shape", "plaintext")
    gg.styleAppend('leq', 'image', 'icons/leq.png')
    gg.styleAppend('leq', 'imagescale', 'true')
    gg.styleAppend('leq', 'fixedsize', 'true')

    gg.styleAppend('splitter', 'style', 'filled')
    gg.styleAppend('splitter', 'shape', 'point')
    gg.styleAppend('splitter', 'width', '0.1')
    gg.styleAppend('splitter', 'color', 'black')
    gg.styleAppend('splitter', 'fillcolor', 'black')
    gg.styleAppend('splitter_link', 'dir', 'none')

    functions, resources = create(gg, None, ndp)


    for fname, n in functions.items():
        F = ndp.get_ftype(fname)
        label = fname + ' ' + format_unit(F)
        x = gg.newItem(label, parent=cluster_functions)
        gg.styleApply("external", x)

        l = gg.newLink(x, n)
        gg.propertyAppend(l, "headport", "w")
        gg.propertyAppend(l, "tailport", "e")

    cluster_resources = gg.newItem("")
    for rname, n in resources.items():
        R = ndp.get_rtype(rname)
        label = rname + ' ' + format_unit(R)
        x = gg.newItem(label, parent=cluster_resources)
        gg.styleApply("external", x)

        l = gg.newLink(n, x)
        gg.propertyAppend(l, "headport", "w")
        gg.propertyAppend(l, "tailport", "e")

    gg.styleApply("external", cluster_functions)
    gg.styleApply("external", cluster_resources)

    # XXX: for some reason cannot turn off the border, using "white"
    gg.propertyAppend(cluster_functions, "shape", "plain")
    gg.propertyAppend(cluster_functions, "color", "white")
    gg.propertyAppend(cluster_resources, "shape", "plain")
    gg.propertyAppend(cluster_resources, "color", "white")


    return gg

def create(gg, parent, ndp, yourname=None):
    if isinstance(ndp, SimpleWrap):
        return create_simplewrap(gg, parent, ndp, yourname=yourname)

    if isinstance(ndp, CompositeNamedDP):
        return create_composite(gg, parent, ndp, yourname=yourname)


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

def create_simplewrap(gg, parent, ndp, yourname=None):  # @UnusedVariable
    assert isinstance(ndp, SimpleWrap)
    label = str(ndp)

    sname = None  # name of style to apply, if any

    special = [
        (Sum, ''),
        (SumN, ''),
        (Product, ''),
    ]
    classname = type(ndp.dp).__name__

    icon = ndp.get_icon()

    iconoptions = [yourname, icon, classname, 'default']
    best_icon = choose_best_icon(iconoptions)

    simple = [Min, Max, Identity]
    only_string = isinstance(ndp.dp, tuple(simple))
    if only_string:
        label = type(ndp.dp).__name__
    else:
        for t, _ in special:
            if isinstance(ndp.dp, t):
                sname = t
                gg.styleAppend(sname, 'image', best_icon)
                gg.styleAppend(sname, 'imagescale', 'true')
                gg.styleAppend(sname, 'fixedsize', 'true')
                gg.styleAppend(sname, 'height', '1.0')
                gg.styleAppend(sname, "shape", "none")
                label = ''
                break
        else:
            if best_icon is not None:
                if yourname is not None:
                    shortlabel = yourname
                else:
                    shortlabel = classname
                sname = classname
                gg.styleAppend(sname, 'imagescale', 'true')
                gg.styleAppend(sname, 'height', '1.0')
                gg.styleAppend(sname, "shape", "box")
                gg.styleAppend(sname, "style", "rounded")
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


    node = gg.newItem(label)

    if isinstance(ndp.dp, (Sum, SumN)):
        gg.styleApply("sum", node)

    if sname:
        gg.styleApply(sname, node)

#     gg.styleApply("simple", cluster)
    functions = {}
    resources = {}
    for rname in ndp.get_rnames():
        resources[rname] = node  # gg.newItem(rname, cluster)
    for fname in ndp.get_fnames():
        functions[fname] = node  # gg.newItem(fname, cluster)


    return functions, resources

def format_unit(R):
    if R == R_dimensionless:
        return '[R]'
    elif isinstance(R, RcompUnits):
        return '[%s]' % R.units
    elif isinstance(R, Rcomp):
        return '[R]'
    else:
        return '[%s]' % str(R)
            
def create_composite(gg, parent, ndp, yourname=None):  # @UnusedVariable
    assert isinstance(ndp, CompositeNamedDP)
#     cluster = gg.newItem("", parent=parent)
    cluster = None

    names2resources = defaultdict(lambda: {})
    names2functions = defaultdict(lambda: {})

    def get_connections_to_function(name):
        assert name in ndp.context.newfunctions
        res = []
        for c in ndp.context.connections:
            if c.dp1 == name:
                res.append(c)
        # print('Connection to %r: %r' % (name, res))
        return res

    def get_connections_to_resource(name):
        assert name in ndp.context.newresources
        res = []
        for c in ndp.context.connections:
            if c.dp2 == name:
                res.append(c)
        # print('Connection to %r: %r' % (name, res))
        return res

    def is_solitary_function(name):
        return len(get_connections_to_function(name)) == 1

    def is_solitary_resource(name):
        return len(get_connections_to_resource(name)) == 1

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
        if name in ndp.context.newfunctions and is_solitary_function(name):
            # print('Skipping extra node for f %r' % name)
            continue

        if name in ndp.context.newresources and is_solitary_resource(name):
            # print('Skipping extra node for r %r' % name)
            continue

        f, r = create(gg, cluster, value, yourname=name)
        # print('name %s -> functions %s , resources = %s' % (name, list(f), list(r)))
        names2resources[name] = r
        names2functions[name] = f
        
        for rn in names2resources[name]:
            if resource_has_more_than_one_connected(name, rn):
                # create new splitter
                orig = names2resources[name][rn]
                split = gg.newItem('')
                gg.styleApply('splitter', split)
                l = gg.newLink(orig, split)
                gg.styleApply('splitter_link', l)
                names2resources[name][rn] = split
        
    ignore_connections = set()
    for name, value in ndp.context.names.items():
        if name in ndp.context.newfunctions and is_solitary_function(name):
            only_one = get_connections_to_function(name)[0]
            ignore_connections.add(only_one)
            node = names2functions[only_one.dp2][only_one.s2]
            names2functions[name][only_one.s1] = node
            # XXX: not really sure
            names2resources[name][only_one.s1] = node

    for name, value in ndp.context.names.items():
        if name in ndp.context.newresources and is_solitary_resource(name):
            only_one = get_connections_to_resource(name)[0]
            ignore_connections.add(only_one)
            node = names2resources[only_one.dp1][only_one.s1]
            names2resources[name][only_one.s2] = node
            # XXX: not really sure
            names2functions[name][only_one.s2] = node


    for c in ndp.context.connections:
        if c in ignore_connections:
            continue
        # print('the function is %s . %s' % (c.dp2, c.s2))
        # print('the resource is %s . %s' % (c.dp1, c.s1))
        dpa = names2functions[c.dp2]
        n_a = dpa[c.s2]
        dpb = names2resources[c.dp1]
        n_b = dpb[c.s1]

#         if n_a == n_b:
#             print('skipping')
#             continue

        box = gg.newItem('')  # '≼')
        gg.styleApply("leq", box)

        ua = ndp.context.names[c.dp2].get_ftype(c.s2)
        ub = ndp.context.names[c.dp1].get_rtype(c.s1)
        gg.newLink(box, n_a , label=get_signal_label(c.s2, ua))
        gg.newLink(n_b, box, label=get_signal_label(c.s1, ub))

    unconnected_fun, unconnected_res = get_missing_connections(ndp.context)
    for (dp, fn) in unconnected_fun:
        x = gg.newItem('')
        gg.styleApply("unconnected_node", x)

        n = names2functions[dp][fn]
        F = ndp.context.names[dp].get_ftype(fn)
        l = gg.newLink(x, n, label=get_signal_label(fn, F))
        gg.styleApply('unconnected_link', l)

    for (dp, rn) in unconnected_res:
        x = gg.newItem('')
        gg.styleApply("unconnected_node", x)

        n = names2resources[dp][rn]
        R = ndp.context.names[dp].get_rtype(rn)
        l = gg.newLink(n, x, label=get_signal_label(rn, R))
        gg.styleApply('unconnected_link', l)



    functions = {}
    resources = {}

    for rname in ndp.get_rnames():
        resources[rname] = list(names2resources[rname].values())[0]

    for fname in ndp.get_fnames():
        functions[fname] = list(names2functions[fname].values())[0]
 
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


