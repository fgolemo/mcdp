# -*- coding: utf-8 -*-
from collections import defaultdict
from contracts import contract
from contracts.utils import raise_desc, raise_wrapped
from mcdp_dp import (Constant, Conversion, GenericUnary, Identity, InvMult2,
    InvPlus2, InvPlus2Nat, Limit, Max, MeetNDual, Min, Mux, MuxMap, Product,
    ProductN, Sum, SumN, SumNNat, WrapAMap)
from mcdp_lang.blocks import get_missing_connections
from mcdp_posets import (Any, BottomCompletion, R_dimensionless, Rcomp,
    RcompUnits, TopCompletion, format_pint_unit_short)
from mocdp import logger
from mocdp.comp import CompositeNamedDP, SimpleWrap
from mocdp.comp.context import get_name_for_fun_node, get_name_for_res_node
from mocdp.comp.interfaces import NamedDP
from mocdp.exceptions import mcdp_dev_warning
from mocdp.ndp import NamedDPCoproduct
from mcdp_dp.dp_max import JoinNDP

STYLE_GREENRED = 'greenred'
STYLE_GREENREDSYM = 'greenredsym'

COLOR_DARKGREEN = 'darkgreen'
# COLOR_DARKGREEN = 'green'
COLOR_DARKRED = 'red'

#    bidirectional
#             propertyAppend(l2, 'color', 'red')
#             propertyAppend(l2, 'arrowtail', 'dot')
#             propertyAppend(l2, 'arrowhead', 'none')
#             propertyAppend(l2, 'dir', 'both')

@contract(ndp=NamedDP)
def gvgen_from_ndp(ndp, style='default', direction='LR', images_paths=[], yourname=None):
    assert isinstance(ndp, NamedDP)
    import my_gvgen as gvgen
    # gg = gvgen.GvGen(options="rankdir=LR")
    gg = gvgen.GvGen(options="rankdir=%s" % direction)

    if len(ndp.get_fnames()) > 0:
        cluster_functions = gg.newItem("")

    from .gdc import GraphDrawingContext
    gdc = GraphDrawingContext(gg=gg, parent=None,
                              yourname=yourname, images_paths=images_paths)
    gdc.set_style(style)

    gg.styleAppend("external", "shape", "none")
    gg.styleAppend("external_cluster_functions", "shape", "plaintext")
    # gg.styleAppend("external_cluster_functions", "bgcolor", "#d0FFd0")
    gg.styleAppend("external_cluster_functions", "color", "white")
#     gg.styleAppend("external_cluster_functions", "color", "#008000")
    gg.styleAppend("external_cluster_resources", "shape", "plaintext")
    # gg.styleAppend("external_cluster_resources", "bgcolor", "#FFd0d0")
    gg.styleAppend("external_cluster_resources", "color", "white")
#     gg.styleAppend("external_cluster_functions", "color", "#008000")

    gg.styleAppend("connector", "shape", "plaintext")

    gg.styleAppend("simple", "shape", "box")
    gg.styleAppend("simple", "style", "rounded")

    # constant resource (min r. needed)
    gg.styleAppend("constant", "shape", "plaintext")
    # constant function (max f. to be implemented)
    gg.styleAppend("limit", "shape", "plaintext")

    gg.styleAppend("unconnected_node", "shape", "plaintext")
    unconnected_color = 'purple'
    gg.styleAppend("unconnected_node", "fontcolor", unconnected_color)
    gg.styleAppend("unconnected_link", "color", unconnected_color)
    gg.styleAppend("unconnected_link", "fontcolor", unconnected_color)

    gg.styleAppend("container", "shape", "box")
    gg.styleAppend("container", "style", "rounded")

    gg.styleAppend("sum", "shape", "box")
    gg.styleAppend("sum", "style", "rounded")
    gg.styleAppend('sum', 'image', gdc.get_icon(['sum']))
    gg.styleAppend('sum', 'imagescale', 'true')
    gg.styleAppend('sum', 'fixedsize', 'true')

    gg.styleAppend("leq", "shape", "plaintext")
    gg.styleAppend('leq', 'image', gdc.get_icon(['leq']))
    gg.styleAppend('leq', 'imagescale', 'true')
    gg.styleAppend('leq', 'fixedsize', 'true')

    # a red dot for unconnected
    gg.styleAppend('unconnected', 'shape', 'point')
    gg.styleAppend('unconnected', 'width', '0.1')
    gg.styleAppend('unconnected', 'color', 'red')


    gg.styleAppend('splitter', 'fillcolor', 'black')
    gg.styleAppend('splitter_link', 'dir', 'none')

    gg.styleAppend('limit', 'color', 'black')

    gg.styleAppend("coproduct_resource", "shape", "point")
    gg.styleAppend("coproduct_function", "shape", "point")
    gg.styleAppend("coproduct_link", "style", "dashed")


    functions, resources = create(gdc, ndp)

    if functions:
        nodes_functions = []
        for fname, n in functions.items():
            F = ndp.get_ftype(fname)
            label = fname + ' ' + format_unit(F)
            x = gg.newItem(label, parent=cluster_functions)
            nodes_functions.append(x)
            gg.styleApply("external", x)

            l = gg.newLink(x, n)
            if False:
                gg.propertyAppend(l, "headport", "w")
                gg.propertyAppend(l, "tailport", "e")

            gdc.decorate_arrow_function(l)
            gdc.decorate_function_name(x)

            gg.styleApply("external_cluster_functions", cluster_functions)

    if resources:
        cluster_resources = gg.newItem("")
        nodes_resources = []
        for rname, n in resources.items():
            R = ndp.get_rtype(rname)
            label = rname + ' ' + format_unit(R)
            x = gg.newItem(label, parent=cluster_resources)
            nodes_resources.append(x)
            gg.styleApply("external", x)

            l = gg.newLink(n, x)
            gdc.decorate_arrow_resource(l)
            gdc.decorate_resource_name(x)
            if False:
                gg.propertyAppend(l, "headport", "w")
                gg.propertyAppend(l, "tailport", "e")

        gg.styleApply("external_cluster_resources", cluster_resources)

    ADD_ORDER = False
    if ADD_ORDER:
        all_nodes = gdc.get_all_nodes()

        for i, n in enumerate(all_nodes):
            if i % 5 != 0:
                continue

            if functions:
                l = gdc.newLink(nodes_functions[0], n)
                gg.propertyAppend(l, "style", "invis")

            if True:
                if resources:
                    l = gdc.newLink(n, nodes_resources[0])
                    gg.propertyAppend(l, "style", "invis")

    # XXX: for some reason cannot turn off the border, using "white"
#     gg.propertyAppend(cluster_functions, "shape", "plain")
#     gg.propertyAppend(cluster_functions, "color", "white")
#     gg.propertyAppend(cluster_resources, "shape", "box")
#     gg.propertyAppend(cluster_resources, "color", "red")
#
#     if False:
#         gg.remove_identity_nodes()
#
    return gg

def create(gdc, ndp):

    if isinstance(ndp, SimpleWrap):
        res = create_simplewrap(gdc, ndp)
    elif isinstance(ndp, CompositeNamedDP):
        res = create_composite(gdc, ndp)
    elif isinstance(ndp, NamedDPCoproduct):
        res = create_coproduct(gdc, ndp)
    else:
        raise_desc(NotImplementedError, '', ndp=ndp)

    functions, resources = res

    for fn in ndp.get_fnames():
        assert fn in functions
    for rn in ndp.get_rnames():
        assert rn in resources

    return res



def is_simple(ndp):
    return isinstance(ndp, SimpleWrap) and isinstance(ndp.dp,
     (Min, Max, Identity, GenericUnary, Sum, SumN, Product, ProductN, InvPlus2, InvMult2))


def create_simplewrap(gdc, ndp):
    assert isinstance(ndp, SimpleWrap)
    from mocdp.comp.composite_templatize import OnlyTemplate

    label = str(ndp)

    sname = None  # name of style to apply, if any


    # special = we display only the image
    # simple = we display only the string
    # If special and simple, then special wins.
    # For these, we only disply the image, without the border

    # This is a list of either PrimitiveDP or Maps
    special = [
        (Sum, ''),
        (SumN, ''),
        (SumNNat, ''),
        (Product, ''),
        (ProductN, ''),
        (InvPlus2, ''),
        (InvMult2, ''),
        (InvPlus2Nat, ''),
        (Conversion, ''),
        (MeetNDual, ''),
        (JoinNDP, ''),
    ]

    def is_special_dp(dp):
        if isinstance(dp, Mux):
            coords = dp.coords
            if coords == [(), ()]:
                return True
        for t, _ in special:
            if isinstance(dp, t):
                return True

            if isinstance(dp, WrapAMap) and isinstance(dp.amap, t):
                return True
        return False

    classname = type(ndp.dp).__name__

    icon = ndp.get_icon()
    
    is_special = is_special_dp(ndp.dp)

    simple = (Min, Max, Identity, GenericUnary, WrapAMap, MeetNDual)
    only_string = not is_special and isinstance(ndp.dp, simple)


    from mcdp_library.library import ATTR_LOAD_NAME
    load_name = getattr(ndp, ATTR_LOAD_NAME, '(ATTR_LOAD_NAME unavailable)')

    iconoptions = [gdc.yourname, icon, load_name, classname, 'default']
    best_icon = gdc.get_icon(iconoptions)
#     print('best_icon: %r' % best_icon)
#     print('only_string: %r' % only_string)
#     print('is special: %r' % is_special)
    if only_string:

        label = type(ndp.dp).__name__

        if isinstance(ndp.dp, GenericUnary):
            label = ndp.dp.function.__name__

        elif isinstance(ndp.dp, WrapAMap):
            label = ndp.dp.diagram_label()

            if isinstance(ndp.dp.amap, MuxMap):
                label = 'Mux(%s)' % ndp.dp.amap.coords

        sname = 'simple'
    else:

        if is_special_dp(ndp.dp):
#             print('special')
            sname = 'style%s' % id(ndp)
            gdc.styleAppend(sname, 'image', best_icon)
            gdc.styleAppend(sname, 'imagescale', 'true')
            gdc.styleAppend(sname, 'fixedsize', 'true')
            gdc.styleAppend(sname, 'height', '1.0')
            gdc.styleAppend(sname, "shape", "none")
            label = ''
        else:
            if best_icon is not None:
                if gdc.yourname is not None:
                    if gdc.yourname[0] == '_':
                        shortlabel = ""
                    else:
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
#                 print('Image %r not found' % imagename)
                sname = None


    if isinstance(ndp.dp, Constant):
        R = ndp.dp.get_res_space()
        c = ndp.dp.c
        label = R.format(c)  # + ' ' + format_unit(R)
        sname = 'constant'

    if isinstance(ndp.dp, Limit):
        F = ndp.dp.get_fun_space()
        c = ndp.dp.limit
        label = F.format(c)  # + ' ' + format_unit(F)
        sname = 'limit'

#     if label[:2] != '<T':
#         # Only available in svg or cairo renderer
#         label = '<I>%s</I>' % label

    # an hack to think about better
    # if hasattr(ndp, '_xxx_label'):
    #    label = getattr(ndp, '_xxx_label')

    # This does not work, for some reason
#     if hasattr(ndp, 'template_parameter'):
#         print('found it')
#         label = getattr(ndp, 'template_parameter')

    node = gdc.newItem(label)

    if isinstance(ndp.dp, (Sum, SumN)):
        gdc.styleApply("sum", node)

    if isinstance(ndp, OnlyTemplate):
        gdc.gg.propertyAppend(node, 'color', 'blue')
        gdc.gg.propertyAppend(node, 'style', 'dashed')

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
    mcdp_dev_warning('fix bug')
    if isinstance(R, BottomCompletion):
        return '[*]'
    if R == R_dimensionless:
        # return '[R]'
#         return '[]'
        # TODO: make option
        return ''
    elif isinstance(R, RcompUnits):
        return '[%s]' % format_pint_unit_short(R.units)
    elif isinstance(R, Rcomp):
        return '[R]'
    elif hasattr(R, '__mcdplibrary_load_name'):
        n = getattr(R, '__mcdplibrary_load_name')
        return '[`%s]' % n
    else:
        return '[%s]' % str(R)
            
@contract(ndp=NamedDPCoproduct)
def create_coproduct(gdc0, ndp):
    
    label = gdc0.yourname if gdc0.yourname else ''
    cluster = gdc0.newItem(label)
    gdc0.gg.propertyAppend(cluster, 'style', 'dashed')

    gdc0 = gdc0.child_context(parent=cluster, yourname=None)

    functions = {}
    resources = {}

    for rname in ndp.get_rnames():
        c = gdc0.newItem(rname)
        resources[rname] = c
        gdc0.styleApply('coproduct_resource', c)

    for fname in ndp.get_fnames():
        c = gdc0.newItem(fname)
        functions[fname] = c
        gdc0.styleApply('coproduct_function', c)

    if ndp.labels is not None:
        altnames = ndp.labels
    else:
        n = len(ndp.ndps)
        altnames = ['alternative %d' % (i + 1) for i in range(n)]

    for i, ndpi in enumerate(ndp.ndps):
        
        altname = altnames[i]

        if gdc0.yourname is not None:
#             if LABELS
            header = '%s - %s' % (gdc0.yourname, altname)
        else:
            header = altname

        with gdc0.child_context_yield(parent=gdc0.parent, yourname=header) as gdci:
            funi, resi = create(gdci, ndpi)

            for fn, fni in zip(ndp.get_fnames(), ndpi.get_fnames()):
                l = gdc0.newLink(functions[fn], funi[fni])
                gdci.decorate_arrow_function(l)  # XXX?
                gdci.styleApply('coproduct_link', l)

            for rn, rni in zip(ndp.get_rnames(), ndpi.get_rnames()):
                l = gdc0.newLink(resi[rni], resources[rn])
                gdci.decorate_arrow_resource(l)  # XXX?
                gdci.styleApply('coproduct_link', l)

    return functions, resources

def create_composite(gdc0, ndp):
    try:
        return create_composite_(gdc0, ndp, SKIP_INITIAL=True)
    except Exception as e:
        logger.error(e)
        logger.error('I will try again without the SKIP_INITIAL parameter.')
        return create_composite_(gdc0, ndp, SKIP_INITIAL=False)

def create_composite_(gdc0, ndp, SKIP_INITIAL):
        
    try:
        assert isinstance(ndp, CompositeNamedDP)

        # names2functions[name][fn] = item

        names2resources = defaultdict(lambda: {})
        names2functions = defaultdict(lambda: {})

        if gdc0.should_I_enclose(ndp):
            if gdc0.yourname is None:
                container_label = ''
            else:
                container_label = gdc0.yourname
            c = gdc0.newItem(container_label)
            gdc0.styleApply('container', c)
            gdc = gdc0.child_context(parent=c, yourname=gdc0.yourname)

        else:

            gdc = gdc0
        for name, value in ndp.context.names.items():
            # do not create these edges
            if SKIP_INITIAL:
                if is_function_with_one_connection_that_is_not_a_res_one(ndp, name):
                    # print('Skipping extra node for is_function_with_one_connection %r' % name)
    #                 warnings.warn('hack')
                    continue

            if SKIP_INITIAL:
                if is_resource_with_one_connection_that_is_not_a_fun_one(ndp, name):
                    # print('skipping extra node for %r' % name)
    #                 warnings.warn('hack')
                    continue

            if False:
                # this makes the nodes appear as red dots
                if is_function_with_no_connections(ndp, name):
                    # only draw the balloon
                    item = gdc.newItem("%s" % name)
                    gdc.styleApply('unconnected', item)
                    for fn in value.get_fnames():
                        names2functions[name][fn] = item
                    for rn in value.get_rnames():
                        names2resources[name][rn] = item
                    continue

                if is_resource_with_no_connections(ndp, name):
                    # only draw the balloon instead of "Identity" node
                    item = gdc.newItem("%s" % name)
                    gdc.styleApply('unconnected', item)
                    for fn in value.get_fnames():
                        names2functions[name][fn] = item
                    for rn in value.get_rnames():
                        names2resources[name][rn] = item
                    continue

            with gdc.child_context_yield(yourname=name, parent=gdc.parent) as child:
                f, r = create(child, value)
                
            # print('name %s -> functions %s , resources = %s' % (name, list(f), list(r)))
            names2resources[name] = r
            names2functions[name] = f

            for rn in names2resources[name]:
                if resource_has_more_than_one_connected(ndp, name, rn):
                    # create new splitter
                    orig = names2resources[name][rn]
                    split = gdc.newItem('')
                    gdc.styleApply('splitter', split)
                    l = gdc.newLink(orig, split)
                    gdc.gg.propertyAppend(l, "constraint", "false")
                    gdc.gg.propertyAppend(l, "weight", "0")

                    gdc.styleApply('splitter_link', l)
                    gdc.decorate_arrow_resource(l)
                    names2resources[name][rn] = split


        ignore_connections = set()
        if SKIP_INITIAL:
            for name, value in ndp.context.names.items():
                if is_function_with_one_connection_that_is_not_a_res_one(ndp, name):
                    only_one = get_connections_to_function(ndp, name)[0]
                    ignore_connections.add(only_one)

                    if not only_one.dp2 in names2functions:
                        msg = ('Cannot find function node ref for %r' % only_one.dp2
                                         + ' while drawing one connection %s' % str(only_one))
    #                     warnings.warn('giving up')
    #                     continue
                        raise_desc(ValueError, msg, names=list(ndp.context.names),
                                   names2functions=list(names2functions))

                    node = names2functions[only_one.dp2][only_one.s2]
                    names2functions[name][only_one.s1] = node
                    # XXX: not really sure
                    names2resources[name][only_one.s1] = node

            for name, value in ndp.context.names.items():
                if is_resource_with_one_connection_that_is_not_a_fun_one(ndp, name):
                    only_one = get_connections_to_resource(ndp, name)[0]
                    ignore_connections.add(only_one)

                    if not only_one.dp1 in names2resources:
    #                     warnings.warn('giving up')
    #                     continue

                        raise ValueError('Cannot find function node ref for %r' % only_one.dp1
                                         + ' while drawing one connection %s' % str(only_one))

                    node = names2resources[only_one.dp1][only_one.s1]
                    names2resources[name][only_one.s2] = node
                    # XXX: not really sure
                    names2functions[name][only_one.s2] = node


        for c in ndp.context.connections:
            if c in ignore_connections:
                # print('ignoring connection %s' % str(c))
                continue

            dpa = names2functions[c.dp2]
            n_a = dpa[c.s2]
            dpb = names2resources[c.dp1]
            n_b = dpb[c.s1]

            skip = gdc.should_I_skip_leq(ndp.context, c)

            second_simple = is_simple(ndp.context.names[c.dp2])
            first_simple = is_simple(ndp.context.names[c.dp1])
            any_simple = second_simple or first_simple
            both_simple = second_simple and first_simple

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

                gdc.decorate_arrow_function(l1)
                gdc.decorate_arrow_resource(l2)


        unconnected_fun, unconnected_res = get_missing_connections(ndp.context)
        for (dp, fn) in unconnected_fun:
            x = gdc.newItem('')
            gdc.styleApply("unconnected_node", x)

            n = names2functions[dp][fn]
            F = ndp.context.names[dp].get_ftype(fn)
            l = gdc.newLink(x, n, label=get_signal_label(fn, F))

            gdc.decorate_arrow_function(l)  # XXX?
            gdc.styleApply('unconnected_link', l)

        for (dp, rn) in unconnected_res:
            x = gdc.newItem('')
            gdc.styleApply("unconnected_node", x)

            n = names2resources[dp][rn]
            R = ndp.context.names[dp].get_rtype(rn)
            l = gdc.newLink(n, x, label=get_signal_label(rn, R))
            gdc.decorate_arrow_resource(l)  # XXX?
            gdc.styleApply('unconnected_link', l)
    
        functions = {}
        resources = {}
    
        for rname in ndp.get_rnames():
            name = get_name_for_res_node(rname)
            resources[rname] = list(names2resources[name].values())[0]
    
        for fname in ndp.get_fnames():
            name = get_name_for_fun_node(fname)
            functions[fname] = list(names2functions[name].values())[0]

        if not (gdc is gdc0):
            gdc0.all_nodes.extend(gdc.all_nodes)

        return functions, resources
    except BaseException as e:
        msg = 'Could not draw diagram.'
        raise_wrapped(Exception, e, msg, names2functions=names2functions,
                      names2resources=names2resources, ndp=ndp)

def get_signal_label(name, unit):

    # a/b/c/signal -> ../signal
    if '/' in name:
        name = '../' + name.split('/')[-1]

    # no label for automatically generated ones
#     for i in range(9):
#         if str(i) in name:
#             name = ""
    
    if len(name) >= 1 and name[0] == '_':
        name = ''


    s2 = format_unit(unit)
    if name:
        return name + ' ' + s2
    else:
        return s2



def get_connections_to_function(ndp, name):
    assert ndp.context.is_new_function(name)
    res = []
    for c in ndp.context.connections:
        if c.dp1 == name:
            res.append(c)
    # print('Connection to %r: %r' % (name, res))
    return res

def get_connections_to_resource(ndp, name):
    assert ndp.context.is_new_resource(name)
    res = []
    for c in ndp.context.connections:
        if c.dp2 == name:
            res.append(c)
    # print('Connection to %r: %r' % (name, res))
    return res

# it is connected to only one
def is_function_with_one_connection(ndp, name):
    return (ndp.context.is_new_function(name)
            and len(get_connections_to_function(ndp, name)) == 1)

# it is connected to only one
def is_resource_with_one_connection(ndp, name):
    return (ndp.context.is_new_resource(name)
            and len(get_connections_to_resource(ndp, name)) == 1)

def is_function_with_no_connections(ndp, name):
    return (ndp.context.is_new_function(name)
            and len(get_connections_to_function(ndp, name)) == 0)

def is_resource_with_no_connections(ndp, name):
    return (ndp.context.is_new_resource(name)
            and len(get_connections_to_resource(ndp, name)) == 0)


def get_connections_to_dp_resource(ndp, name, rn):
    assert name in ndp.context.names
    res = []
    for c in ndp.context.connections:
        if c.dp1 == name and c.s1 == rn:
            res.append(c)
    return res

def resource_has_more_than_one_connected(ndp, name, rn):
    res = get_connections_to_dp_resource(ndp, name, rn)
    # print(ndp.context.connections)
    # print('number connected to %s.%s: %s' % (name, rn, len(res)))
    return len(res) > 1

def is_function_with_one_connection_that_is_not_a_res_one(ndp, name):
    if is_function_with_one_connection(ndp, name):
        other = get_connections_to_function(ndp, name)[0].dp2
        assert other != name
        if is_resource_with_one_connection(ndp, other):
            return False
        return True
    else:
        return False

def is_resource_with_one_connection_that_is_not_a_fun_one(ndp, name):
    if is_resource_with_one_connection(ndp, name):
        other = get_connections_to_resource(ndp, name)[0].dp1
        assert other != name

        if is_function_with_one_connection(ndp, other):
            return False
        return True
    else:
        return False
