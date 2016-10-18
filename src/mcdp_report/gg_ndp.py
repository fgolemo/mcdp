# -*- coding: utf-8 -*-
from collections import defaultdict
from types import NoneType

from contracts import contract
from contracts.utils import raise_desc, raise_wrapped
from mcdp_dp import (Constant, ConstantMinimals, Conversion,
    Identity, InvMult2, InvPlus2, InvPlus2Nat, JoinNDP, Limit, MeetNDualDP,
    Mux, MuxMap, ProductN, SumNDP, SumNNat, TakeFun, TakeRes,
    WrapAMap)
from mcdp_dp.dp_max import MeetNDP
from mcdp_lang.blocks import get_missing_connections
from mcdp_maps.sum_n_rcomp import SumNRcomp
from mcdp_posets import (Any, BottomCompletion, R_dimensionless, Rcomp,
    RcompUnits, TopCompletion, format_pint_unit_short)
from mocdp import logger
from mocdp.comp import CompositeNamedDP, SimpleWrap
from mocdp.comp.context import get_name_for_fun_node, get_name_for_res_node
from mocdp.comp.interfaces import NamedDP
from mocdp.exceptions import mcdp_dev_warning, DPInternalError
from mocdp.ndp import NamedDPCoproduct


STYLE_GREENRED = 'greenred'
STYLE_GREENREDSYM = 'greenredsym'

COLOR_DARKGREEN = 'darkgreen'
COLOR_DARKRED = 'red'

class PlottingInfo():

    def should_I_expand(self, ndp_name, alternative):  # @UnusedVariable
        """ ndp: a coproduct, alternative """
        return True

    @contract(ndp_name='tuple')
    def get_fname_label(self, ndp_name, fname):  # @UnusedVariable
        return None

    @contract(ndp_name='tuple')
    def get_rname_label(self, ndp_name, rname):  # @UnusedVariable
        return None


class RecursiveEdgeLabeling(PlottingInfo):

    def __init__(self, plotting_info, append_ndp_name):
        assert isinstance(append_ndp_name, str)
        self.f = plotting_info
        self.append_ndp_name = append_ndp_name

    def _name(self, ndp_name):
        assert isinstance(ndp_name, tuple), ndp_name
        ndp_name = (self.append_ndp_name,) + ndp_name
        return ndp_name

    def should_I_expand(self, ndp_name, alternative):
        return self.f.should_I_expand(self._name(ndp_name), alternative)

    @contract(ndp_name='tuple')
    def get_fname_label(self, ndp_name, fname):
        return self.f.get_fname_label(self._name(ndp_name), fname)

    @contract(ndp_name='tuple')
    def get_rname_label(self, ndp_name, rname):
        return self.f.get_rname_label(self._name(ndp_name), rname)

@contract(ndp=NamedDP, direction='str', yourname='str|None')
def gvgen_from_ndp(ndp, style='default', direction='LR', images_paths=[], yourname=None,
                   plotting_info=None):
    if plotting_info is None:
        plotting_info = PlottingInfo()

    """
    
        plotting_info(ndp_name=('name', 'sub'), fname=None, rname='r1')
        plotting_info(ndp_name=('name', 'sub'), fname='f1', rname=None)
           
    """
    assert isinstance(ndp, NamedDP)
    assert isinstance(direction, str), direction.__repr__()
    assert isinstance(yourname, (NoneType, str)), yourname.__repr__()

    import my_gvgen as gvgen
    assert direction in ['LR', 'TB']
    gg = gvgen.GvGen(options="rankdir=%s" % direction)


    # if True, create clusters for functions and resources
    do_cluster_res_fun = False

    if do_cluster_res_fun and len(ndp.get_fnames()) > 0:
        cluster_functions = gg.newItem("")
    else:
        cluster_functions = None

    if do_cluster_res_fun and len(ndp.get_rnames()) > 0:
        cluster_resources = gg.newItem("")
    else:
        cluster_resources = None


    from .gdc import GraphDrawingContext
    gdc = GraphDrawingContext(gg=gg, parent=None,
                              yourname=yourname, images_paths=images_paths)
    gdc.set_style(style)

    gg.styleAppend("external", "shape", "none")
    gg.styleAppend("external_cluster_functions", "shape", "plaintext")

    gg.styleAppend("external_cluster_functions", "color", "white")
    gg.styleAppend("external_cluster_resources", "shape", "plaintext")
    gg.styleAppend("external_cluster_resources", "color", "white")

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


    functions, resources = create(gdc, ndp, plotting_info)


    for fname, n in functions.items():
        F = ndp.get_ftype(fname)
        label = fname + ' ' + format_unit(F)
        x = gg.newItem(label, parent=cluster_functions)

        gg.styleApply("external", x)

        l_label = plotting_info.get_fname_label(ndp_name=(), fname=fname)
        if not l_label: l_label = ""

        l = gg.newLink(x, n, l_label)
        if False:
            gg.propertyAppend(l, "headport", "w")
            gg.propertyAppend(l, "tailport", "e")

        gdc.decorate_arrow_function(l)
        gdc.decorate_function_name(x)


    for rname, n in resources.items():
        R = ndp.get_rtype(rname)
        label = rname + ' ' + format_unit(R)
        x = gg.newItem(label, parent=cluster_resources)

        gg.styleApply("external", x)

        l_label = plotting_info.get_rname_label(ndp_name=(), rname=rname)
        if not l_label: l_label = ""

        l = gg.newLink(n, x, l_label)
        gdc.decorate_arrow_resource(l)
        gdc.decorate_resource_name(x)
        if False:
            gg.propertyAppend(l, "headport", "w")
            gg.propertyAppend(l, "tailport", "e")


    if cluster_functions is not None:
        gg.styleApply("external_cluster_functions", cluster_functions)

    if cluster_resources is not None:
        gg.styleApply("external_cluster_resources", cluster_resources)
#
#     ADD_ORDER = False
#     if ADD_ORDER:
#         all_nodes = gdc.get_all_nodes()
#
#         for i, n in enumerate(all_nodes):
#             if i % 5 != 0:
#                 continue
#
#             if functions:
#                 l = gdc.newLink(nodes_functions[0], n)
#                 gg.propertyAppend(l, "style", "invis")
#
#             if True:
#                 if resources:
#                     l = gdc.newLink(n, nodes_resources[0])
#                     gg.propertyAppend(l, "style", "invis")

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


def create(gdc, ndp, plotting_info):
    if isinstance(ndp, SimpleWrap):
        res = create_simplewrap(gdc, ndp, plotting_info)
    elif isinstance(ndp, CompositeNamedDP):
        res = create_composite(gdc, ndp, plotting_info)
    elif isinstance(ndp, NamedDPCoproduct):
        res = create_coproduct(gdc, ndp, plotting_info)
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
     (MeetNDP, JoinNDP, Identity, SumNDP,
      SumNRcomp, 
      ProductN, InvPlus2, InvMult2))


def create_simplewrap(gdc, ndp, plotting_info):  # @UnusedVariable
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
#         (Sum, ''),
        (SumNDP, ''),
        (SumNNat, ''),
#         (Product, ''),
        (ProductN, ''),
        (InvPlus2, ''),
        (InvMult2, ''),
        (InvPlus2Nat, ''),
        (Conversion, ''),
        (MeetNDualDP, ''),
        (JoinNDP, ''),
        (TakeFun, ''),
        (TakeRes, ''),
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

    simple = (MeetNDP, JoinNDP, Identity, WrapAMap, MeetNDualDP)
    only_string = not is_special and isinstance(ndp.dp, simple)

    from mcdp_library.library import ATTR_LOAD_NAME
    load_name = getattr(ndp, ATTR_LOAD_NAME, '(ATTR_LOAD_NAME unavailable)')

    iconoptions = [
        gdc.yourname,
        load_name,
        icon,
        classname,
        'default',
    ]
    best_icon = gdc.get_icon(iconoptions)
    #print('icon options: %s' % iconoptions)
    #print('best_icon: %r' % best_icon)
    #print('only_string: %r' % only_string)
    #print('is special: %r' % is_special)
    if is_special and 'default.png' in best_icon: # pragma: no cover
        raise_desc(DPInternalError, 'Could not find icon for special',
                   iconoptions=iconoptions, is_special=is_special, best_icon=best_icon,
                   only_string=only_string)
        
    if only_string:

        label = type(ndp.dp).__name__


        if isinstance(ndp.dp, WrapAMap):
            label = ndp.dp.diagram_label()

            if isinstance(ndp.dp.amap, MuxMap):
                label = 'Mux(%s)' % ndp.dp.amap.coords

        sname = 'simple'
    else:

        if is_special_dp(ndp.dp):
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
                    if len(gdc.yourname) >= 1 and gdc.yourname[0] == '_':
                        shortlabel = ""
                    else:
                        shortlabel = gdc.yourname
                else:
                    mcdp_dev_warning('double check this (sep 16)')
                    # shortlabel = classname
                    shortlabel = None

                # shortlabel = '<I><B>%sa</B></I>' % shortlabel
                sname = classname
                gdc.styleAppend(sname, 'imagescale', 'true')
                gdc.styleAppend(sname, 'height', '1.0')
                gdc.styleAppend(sname, "shape", "box")
                gdc.styleAppend(sname, "style", "rounded")
                label = ("<TABLE CELLBORDER='0' BORDER='0'><TR><TD>%s</TD></TR>"
                "<TR><TD><IMG SRC='%s' SCALE='TRUE'/></TD></TR></TABLE>")

                if shortlabel is None:
                    shortlabel = ''
                label = label % (shortlabel, best_icon)
            else:
                # print('Image %r not found' % imagename)
                sname = None

    def make_short_label(l, max_length=25):
        if len(l) >= max_length:
            l = l[:max_length] + '...'
        return l

    if isinstance(ndp.dp, Constant):
        R = ndp.dp.get_res_space()
        c = ndp.dp.c
        label = R.format(c)
        label = make_short_label(label)
        sname = 'constant'

    if isinstance(ndp.dp, ConstantMinimals):
        R = ndp.dp.get_res_space()
        values = ndp.dp.values
        label = "↑{" + ", ".join(R.format(c) for c in values) + "}"
        label = make_short_label(label)
        sname = 'constant'

    if isinstance(ndp.dp, Limit):
        F = ndp.dp.get_fun_space()
        c = ndp.dp.limit
        label = F.format(c)
        label = make_short_label(label)
        sname = 'limit'

    from mcdp_dp.dp_limit import LimitMaximals
    if isinstance(ndp.dp, LimitMaximals):
        F = ndp.dp.get_fun_space()
        values = ndp.dp.limit.maximals
        label = "↓{" + ", ".join(F.format(c) for c in values) + "}"
        label = make_short_label(label)
        sname = 'limit'


#     if label[:2] != '<T':
#         # Only available in svg or cairo renderer
#         label = '<I>%s</I>' % label


    node = gdc.newItem(label)

    if isinstance(ndp.dp, (SumNDP,)):
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
    from mcdp_library.library import ATTR_LOAD_NAME

    if R == BottomCompletion(TopCompletion(Any())):
        return '[*]'
    mcdp_dev_warning('fix bug')
    if isinstance(R, BottomCompletion):
        return '[*]'
    if R == R_dimensionless:
        # TODO: make option
        return ''
    elif isinstance(R, RcompUnits):
        return '[%s]' % format_pint_unit_short(R.units)
    elif isinstance(R, Rcomp):
        return '[R]'
    elif hasattr(R, ATTR_LOAD_NAME):
        n = getattr(R, ATTR_LOAD_NAME)
        return '[`%s]' % n
    else:
        return '[%s]' % str(R)
            
@contract(ndp=NamedDPCoproduct)
def create_coproduct(gdc0, ndp, plotting_info):
    
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
        
        should_I = plotting_info.should_I_expand(ndp_name=(), alternative=altname)
        if not should_I:
            # print('Not expanding alternative %s' % altname)
            continue
        else:
            # print('Expanding %r' % altname)
            pass

        if gdc0.yourname is not None:
            header = '%s - %s' % (gdc0.yourname, altname)
        else:
            header = altname

        with gdc0.child_context_yield(parent=gdc0.parent, yourname=header) as gdci:
            plotting_info2 = RecursiveEdgeLabeling(plotting_info=plotting_info,
                                                            append_ndp_name=altname)
            funi, resi = create(gdci, ndpi, plotting_info=plotting_info2)

            for fn, fni in zip(ndp.get_fnames(), ndpi.get_fnames()):

                l_label = plotting_info2.get_fname_label(ndp_name=(), fname=fni)
                l = gdc0.newLink(functions[fn], funi[fni], l_label)
                gdci.decorate_arrow_function(l)  # XXX?
                gdci.styleApply('coproduct_link', l)

            for rn, rni in zip(ndp.get_rnames(), ndpi.get_rnames()):
                l_label = plotting_info2.get_rname_label(ndp_name=(), rname=rni)
                l = gdc0.newLink(resi[rni], resources[rn], l_label)
                gdci.decorate_arrow_resource(l)  # XXX?
                gdci.styleApply('coproduct_link', l)

    return functions, resources

def create_composite(gdc0, ndp, plotting_info):
    try:
        return create_composite_(gdc0, ndp, plotting_info=plotting_info, SKIP_INITIAL=True)
    except Exception as e:
        logger.error(e)
        logger.error('I will try again without the SKIP_INITIAL parameter.')
        return create_composite_(gdc0, ndp, plotting_info=plotting_info, SKIP_INITIAL=False)

def create_composite_(gdc0, ndp, plotting_info, SKIP_INITIAL):
        
    try:
        assert isinstance(ndp, CompositeNamedDP)

        # names2functions[name][fn] = item

        names2resources = defaultdict(lambda: {})
        names2functions = defaultdict(lambda: {})

        if gdc0.should_I_enclose(ndp):
            if gdc0.yourname is None:
                container_label = ''
            else:
                if gdc0.yourname and gdc0.yourname[0] == '_':
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
                plotting_info2 = RecursiveEdgeLabeling(plotting_info, name)
                f, r = create(child, value, plotting_info=plotting_info2)
                
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
        
                l1_label = get_signal_label(c.s2, ua)

                dec = plotting_info.get_fname_label(ndp_name=(c.dp2,), fname=c.s2)
                if dec is not None:
                    l1_label = get_signal_label_namepart(c.s2) + '\n' + dec

#                 print('Creating label with %r %s' % l1_label)
                l1 = gdc.newLink(box, n_a , label=l1_label)

#                 if False:
#                     gdc.gg.propertyAppend(l1, "headport", "w")

                l2_label = get_signal_label(c.s1, ub)
                dec = plotting_info.get_rname_label(ndp_name=(c.dp1,), rname=c.s1)
                if dec is not None:
                    l2_label = get_signal_label_namepart(c.s1) + '\n' + dec
                l2 = gdc.newLink(n_b, box, label=l2_label)

#                 if False:
#                     gdc.gg.propertyAppend(l2, "tailport", "e")
#
#                 if False:
#                     gdc.gg.propertyAppend(l1, 'constraint', 'false')
#                     gdc.gg.propertyAppend(l2, 'constraint', 'false')
        
                if both_simple:
                    weight = 0
                elif any_simple:
                    weight = 0.5
                else:
                    weight = 1
                if any_simple:
                    gdc.gg.propertyAppend(l2, 'weight', '%s' % weight)
                    gdc.gg.propertyAppend(l1, 'weight', '%s' % weight)

                # gdc.gg.propertyAppend(l2, 'color', 'blue')
                # gdc.gg.propertyAppend(l1, 'color', 'blue')

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
        raise
        msg = 'Could not draw diagram.'
        raise_wrapped(Exception, e, msg, names2functions=names2functions,
                      names2resources=names2resources, ndp=ndp)


def get_signal_label_namepart(name):
    # a/b/c/signal -> ../signal
    if '/' in name:
        last = name.split('/')[-1]
        if len(last) >= 1 and last[0] == '_':
            name = ''
        else:
            name = '../' + last

    if len(name) >= 1 and name[0] == '_':
        name = ''
    return name

def get_signal_label(name, unit):
    name = get_signal_label_namepart(name)
    
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
