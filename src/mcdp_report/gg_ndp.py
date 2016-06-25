# -*- coding: utf-8 -*-

from collections import defaultdict
from contextlib import contextmanager
from contracts import contract
from contracts.utils import raise_desc, raise_wrapped
from mcdp_dp import (Constant, Conversion, GenericUnary, Identity, InvMult2,
    InvPlus2, InvPlus2Nat, Limit, Max, MeetNDual, Min, Mux, MuxMap, Product,
    ProductN, Sum, SumN, SumNNat, WrapAMap)
from mcdp_lang.blocks import get_missing_connections
from mcdp_library.utils import dir_from_package_name
from mcdp_posets import (Any, BottomCompletion, R_dimensionless, Rcomp,
    RcompUnits, TopCompletion, format_pint_unit_short)
from mcdp_report.utils import safe_makedirs
from mocdp.comp import CompositeNamedDP, SimpleWrap
from mocdp.comp.context import get_name_for_fun_node, get_name_for_res_node
from mocdp.comp.interfaces import NamedDP
from mocdp.exceptions import mcdp_dev_warning
from mocdp.ndp import NamedDPCoproduct
from system_cmd import CmdException, system_cmd_result
from tempfile import mkdtemp
import os


STYLE_GREENRED = 'greenred'
STYLE_GREENREDSYM = 'greenredsym'

COLOR_DARKGREEN = 'darkgreen'
# COLOR_DARKGREEN = 'green'
COLOR_DARKRED = 'red'

class GraphDrawingContext():
    def __init__(self, gg, parent, yourname, level=0, tmppath=None, style='default'):
        self.gg = gg
        self.parent = parent
        self.yourname = yourname
        self.level = level
        
        if tmppath is None:
            tmppath = mkdtemp(suffix="dp-icons")
            mcdp_dev_warning('need to share icons')
            # print('created tmp directory %r' % tmppath)
        self.tmppath = tmppath

        self.all_nodes = []

        self.set_style(style)

    def get_all_nodes(self):
        return self.all_nodes

    def newItem(self, label):
        n = self.gg.newItem(label, parent=self.parent)
        self.all_nodes.append(n)
        return n
        
    def child_context(self, parent, yourname):
        c = GraphDrawingContext(gg=self.gg, parent=parent, yourname=yourname,
                                level=self.level + 1, tmppath=self.tmppath, style=self.style)
        return c

    @contextmanager
    def child_context_yield(self, parent, yourname):
        c = self.child_context(parent, yourname)
        yield c
        self.all_nodes.extend(c.all_nodes)


    def styleApply(self, sname, n):
        self.gg.styleApply(sname, n)

    def newLink(self, a, b, label=None):
        return self.gg.newLink(a, b, label)

    def styleAppend(self, a, b, c):
        self.gg.styleAppend(a, b, c)

    def set_style(self, style):
        self.style = style
        if style == 'default':
            self.policy_enclose = 'always_except_first'
            self.policy_skip = 'never'
        elif style == 'clean':
            self.policy_enclose = 'only_if_unconnected'
            self.policy_skip = 'if_second_simple'
        elif style in [STYLE_GREENRED, STYLE_GREENREDSYM]:
            self.policy_enclose = 'always_except_first'
            self.policy_skip = 'never'

        else: 
            raise ValueError(style)
        
        if style in [STYLE_GREENRED, STYLE_GREENREDSYM]:
            self.gg.styleAppend('splitter', 'style', 'filled')
            self.gg.styleAppend('splitter', 'shape', 'point')
            self.gg.styleAppend('splitter', 'width', '0.1')
            self.gg.styleAppend('splitter', 'color', 'red')
        else:
            self.gg.styleAppend('splitter', 'style', 'filled')
            self.gg.styleAppend('splitter', 'shape', 'point')
            self.gg.styleAppend('splitter', 'width', '0.1')
            self.gg.styleAppend('splitter', 'color', 'black')

    def should_I_enclose(self, ndp):
        if hasattr(ndp, '_hack_force_enclose'):
            return True

        if self.level == 0:
            return False

        if self.policy_enclose == 'always_except_first':
            return True
        elif self.policy_enclose == 'only_if_unconnected':
            unconnected = not ndp.is_fully_connected() 
            if unconnected:
                return True
            else:
                return self.yourname is not None
        else:
            raise ValueError(self.policy_enclose)

    def should_I_skip_leq(self, context, c):
        if self.policy_skip == 'never':
            return False
        elif self.policy_skip == 'if_second_simple':
            second_simple = is_simple(context.names[c.dp2])
            # first_simple = is_simple(context.names[c.dp1])
            # any_simple = second_simple or first_simple
            # both_simple = second_simple and first_simple

            mcdp_dev_warning('Add options here')
            skip = second_simple
            return skip
        else:
            assert False, self.policy_skip

    def get_temp_path(self):
        return self.tmppath

    def get_imagepath(self):
        base = dir_from_package_name('mcdp_report')
        imagepath = os.path.join(base, 'icons')
        if not os.path.exists(imagepath):
            raise ValueError('Icons path does not exist: %r' % imagepath)
        return imagepath

    def get_icon(self, options):
        tmppath = self.get_temp_path()
        # imagepath = self.get_imagepath()
        imagepaths = ['.', self.get_imagepath()]
        best = choose_best_icon(options, imagepaths, tmppath)
        return best

    def decorate_arrow_function(self, l1):
        propertyAppend = self.gg.propertyAppend
        if self.style == STYLE_GREENRED:

            propertyAppend(l1, 'color', COLOR_DARKGREEN)
            propertyAppend(l1, 'arrowhead', 'normal')
            propertyAppend(l1, 'arrowtail', 'none')
            propertyAppend(l1, 'dir', 'both')

        if self.style == STYLE_GREENREDSYM:
            propertyAppend(l1, 'color', 'darkgreen')
            propertyAppend(l1, 'arrowhead', 'dot')
            propertyAppend(l1, 'arrowtail', 'none')
            propertyAppend(l1, 'dir', 'both')


    def decorate_arrow_resource(self, l2, split=False):
        propertyAppend = self.gg.propertyAppend

        if self.style == STYLE_GREENRED:
            propertyAppend(l2, 'color', COLOR_DARKRED)
            propertyAppend(l2, 'arrowtail', 'inv')
            propertyAppend(l2, 'arrowhead', 'none')
            propertyAppend(l2, 'dir', 'both')

        if self.style == STYLE_GREENREDSYM:
            propertyAppend(l2, 'color', COLOR_DARKRED)
            propertyAppend(l2, 'arrowtail', 'dot')
            propertyAppend(l2, 'arrowhead', 'none')
            propertyAppend(l2, 'dir', 'both')


    def decorate_resource_name(self, n):
        propertyAppend = self.gg.propertyAppend

        if self.style in  [STYLE_GREENRED, STYLE_GREENREDSYM]:
            propertyAppend(n, 'fontcolor', COLOR_DARKRED)

    def decorate_function_name(self, n):
        propertyAppend = self.gg.propertyAppend
        if self.style in  [STYLE_GREENRED, STYLE_GREENREDSYM]:
            propertyAppend(n, 'fontcolor', COLOR_DARKGREEN)


#    bidirectional
#             propertyAppend(l2, 'color', 'red')
#             propertyAppend(l2, 'arrowtail', 'dot')
#             propertyAppend(l2, 'arrowhead', 'none')
#             propertyAppend(l2, 'dir', 'both')

@contract(ndp=NamedDP)
def gvgen_from_ndp(ndp, style='default', direction='LR'):
    assert isinstance(ndp, NamedDP)
    import my_gvgen as gvgen
    # gg = gvgen.GvGen(options="rankdir=LR")
    gg = gvgen.GvGen(options="rankdir=%s" % direction)

    if len(ndp.get_fnames()) > 0:
        cluster_functions = gg.newItem("")

    gdc = GraphDrawingContext(gg=gg, parent=None, yourname=None)
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

    if False:
        gg.remove_identity_nodes()
             
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

def resize_icon(filename, tmppath, size):

    res = os.path.join(tmppath, 'resized', str(size))

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

def choose_best_icon(iconoptions, imagepaths, tmppath):
    # logger.debug('Looking for %s.' % (str(iconoptions)))
    for option in iconoptions:
        if option is None:
            continue
        for imagepath in imagepaths:
            imagename = os.path.join(imagepath, option) + '.png'
            if os.path.exists(imagename):
                return resize_icon(imagename, tmppath, 100)
    # logger.debug('Could not find PNG icon for %s.' % (str(iconoptions)))
    return None

def is_simple(ndp):
    return isinstance(ndp, SimpleWrap) and isinstance(ndp.dp,
     (Min, Max, Identity, GenericUnary, Sum, SumN, Product, ProductN, InvPlus2, InvMult2))


def create_simplewrap(gdc, ndp):
    assert isinstance(ndp, SimpleWrap)
    from mocdp.comp.composite_templatize import OnlyTemplate

    label = str(ndp)

    sname = None  # name of style to apply, if any

    # For these, we only disply the image, without the border
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
    ]

    classname = type(ndp.dp).__name__

    icon = ndp.get_icon()
    



    simple = (Min, Max, Identity, GenericUnary, WrapAMap)
    only_string = isinstance(ndp.dp, simple)

    if isinstance(ndp.dp, MeetNDual):
        icon = 'split2'
        only_string = False

    iconoptions = [gdc.yourname, icon, classname, 'default']
    best_icon = gdc.get_icon(iconoptions)

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

        def is_special_dp(dp):
            if isinstance(dp, Mux):
                coords = dp.coords
                if coords == [(), ()]:
                    return True
            for t, _ in special:
                if isinstance(dp, t):
                    return True
            return False

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
    if hasattr(ndp, '_xxx_label'):
        label = getattr(ndp, '_xxx_label')

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
    
#     cluster = gdc0.newItem('mycluster-%s' % gdc0.yourname)
#     gdc0 = gdc0.child_context(parent=cluster, yourname=None)

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
        print e
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
                    print('Skipping extra node for is_function_with_one_connection %r' % name)
    #                 warnings.warn('hack')
                    continue

            if SKIP_INITIAL:
                if is_resource_with_one_connection_that_is_not_a_fun_one(ndp, name):
                    print('skipping extra node for %r' % name)
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
    # no label for automatically generated ones
    for i in range(9):
        if str(i) in name:
            name = ""
    
    if '_' in name:
        name = ''

    # a/b/c/signal -> ../signal
    if '/' in name:
        name = '../' + name.split('/')[-1]

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
