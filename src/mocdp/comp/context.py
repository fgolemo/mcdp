# -*- coding: utf-8 -*-
from collections import namedtuple

from contracts import contract
from contracts.utils import check_isinstance, raise_desc

from mcdp import logger
from mcdp.exceptions import DPInternalError, DPSemanticError, mcdp_dev_warning
from mcdp_dp import FunctionNode, PrimitiveDP, ResourceNode
from mcdp_posets import FinitePoset, NotBounded, Poset, Space, PosetProductWithLabels
from mcdp_posets import express_value_in_isomorphic_space
from mocdp.comp.interfaces import NamedDP
from mocdp.comp.template_for_nameddp import TemplateForNamedDP
from mocdp.comp.wrap import dpwrap
from mcdp_utils_misc import format_list


_ = logger

__all__ = [
    'Connection',
    'Context',
]

CFunction = namedtuple('CFunction', 'dp s')
CResource = namedtuple('CResource', 'dp s')
Connection0 = namedtuple('Connection', 'dp1 s1 dp2 s2')


class Connection(Connection0):
    def __repr__(self):
        return ("Constraint(%s.%s <= %s.%s)" %
                (self.dp1, self.s1, self.dp2, self.s2))

    @contract(nodes='set(str)|seq(str)')
    def involves_any_of_these_nodes(self, nodes):
        """ Returns true if any of the two nodes is in the iterable nodes."""
        return self.dp1 in nodes or self.dp2 in nodes



class ValueWithUnits(object):
    """ "unit" should have been "space" """
    @contract(unit=Space)
    def __init__(self, value, unit):
        unit.belongs(value)
        self.value = value
        self.unit = unit

    def __repr__(self):
        return 'ValueWithUnits(%r, %r)' % (self.value, self.unit)
    
    def cast_value(self, P):
        """ Returns the value cast in the space P (larger than
            the current space). """ 
        return express_value_in_isomorphic_space(self.unit, self.value, P)

UncertainConstant = namedtuple('UncertainConstant', 'space lower upper')

def get_name_for_fun_node(fname):
    check_isinstance(fname, str) # also more conditions
    return '_fun_%s' % fname

def get_name_for_res_node(rname):
    check_isinstance(rname, str) # also more conditions
    return '_res_%s' % rname

@contract(returns='tuple(bool, str|None)')
def is_fun_node_name(name):
    if '_fun_' in name:
        fname = name[len('_fun_'):]
        return True, fname
    return False, None

@contract(returns='tuple(bool, str|None)')
def is_res_node_name(name):
    if '_res_' in name:
        fname = name[len('_res_'):]
        return True, fname
    return False, None

def check_good_name_for_regular_node(name):
    """ Raises an exception ValueError if this is not a good name for a node
        e.g. starts with _res_ or _fun_ """
    if is_fun_node_name(name)[0]:
        msg = 'Looks like a reserved name for functions.'
        raise ValueError(msg)
    if is_res_node_name(name)[0]:
        msg = 'Looks like a reserved name for resources.'
        raise ValueError(msg)
    
def check_good_name_for_function(fname):
    check_good_name_for_regular_node(fname)

def check_good_name_for_resource(rname):
    check_good_name_for_regular_node(rname)

class NoSuchMCDPType(Exception):
    pass



class Context(object):

    def __init__(self):
        self.names = {}  # name -> ndp
        self.connections = []

        self.fnames = []
        self.rnames = []

        self.var2resource = {}  # str -> Resource
        self.var2function = {}  # str -> Function
        self.var2model = {}  # str -> NamedDP
        self.constants = {}  # str -> ValueWithUnits
        self.uncertain_constants = {} # str -> UncertainUniuts
        self.variables = set() # set of strings for variables
        # already explicitly set. It is assumed each will have
        # an NDP of the same name

        self.ifun_init()
        self.ires_init()
        
        self.load_ndp_hooks = []
        self.load_posets_hooks = []
        self.load_primitivedp_hooks = []
        self.load_template_hooks = []
        self.load_library_hooks = []
        
        # xxx this is probably not well thought out
        # for example, are we propagating this to children? (no)
        self.warnings = []
        
#         #
#         self.suggested_rname = None
#         self.suggested_fname = None

    def __repr__(self):
        s = 'Context:'
        s += '\n' + '  names: %s' % list(self.names)
        s += '\n' + '  connections: %s' % self.connections
        s += '\n' + '  var2resource: %s' % self.var2resource
        s += '\n' + '  var2function: %s' % self.var2function
        s += '\n' + '  var2model: %s' % self.var2model
        s += '\n' + '  constants: %s' % self.constants

        return s
 
    def child(self):
        """ A child context preserves the value of the constants
            and the model types. """
        c = Context()
        c.load_ndp_hooks = list(self.load_ndp_hooks)
        c.load_posets_hooks = list(self.load_posets_hooks)
        c.load_primitivedp_hooks = list(self.load_primitivedp_hooks)
        c.load_template_hooks = list(self.load_template_hooks)
        c.load_library_hooks = list(self.load_library_hooks)
        c.var2resource = {}  # XXX?
        c.var2function = {}  # XXX?
        c.var2model.update(self.var2model)
        c.constants.update(self.constants)
        # we give a reference to ours 
        # c.warnings = self.warnings
        # we do not preserve this
        # use_rname = None

        return c

    def load_ndp(self, load_arg, context=None):
        assert context is None or context is self
        return self._load_hooks(load_arg, self.load_ndp_hooks, NamedDP)

    def load_primitivedp(self, load_arg, context=None):
        assert context is None or context is self
        return self._load_hooks(load_arg, self.load_primitivedp_hooks, PrimitiveDP)

    def load_poset(self, load_arg, context=None):
        assert context is None or context is self
        return self._load_hooks(load_arg, self.load_posets_hooks, Poset)

    def load_template(self, load_arg, context=None):
        assert context is None or context is self
        return self._load_hooks(load_arg, self.load_template_hooks, TemplateForNamedDP)

    def load_library(self, load_arg, context=None):
        assert context is None or context is self
        check_isinstance(load_arg, str)
        from mcdp_library import MCDPLibrary
        return self._load_hooks(load_arg, self.load_library_hooks, MCDPLibrary)

    def _load_hooks(self, load_arg, hooks, expected):
        errors = []
        if not hooks:
            msg = 'Could not load %r because no loading hooks provided.' % load_arg
            raise_desc(DPSemanticError, msg)
        for hook in hooks:
            try:
                try:
                    res = hook(load_arg, context=self)
                    if not isinstance(res, expected):
                        msg = 'The hook did not return the expected type.'
                        raise_desc(DPSemanticError, msg, res=res, expected=expected)
                    return res
                except TypeError:
                    msg = 'Could not use hook %r' % hook
                    logger.error(msg)
                    raise
            except DPSemanticError as e:
                if len(hooks) == 1:
                    raise
                else:
                    errors.append(e)

        s = "\n\n".join(map(str, errors))
        msg = 'Could not load %r: \n%s' % (load_arg, s)
        raise DPSemanticError(msg)

    @contract(s='str', dp='str', returns=CFunction)
    def make_function(self, dp, s):
        assert isinstance(dp, str)
        if not dp in self.names:
            msg = 'Unknown design problem %r.' % dp
            raise DPSemanticError(msg)

        ndp = self.names[dp]

        if not s in ndp.get_fnames():
            msg = 'Unknown function %r for design problem %r.' % (s, dp)
            msg += ' Known functions: %s.' % format_list(ndp.get_fnames())
            raise DPSemanticError(msg)

        return CFunction(dp, s)

    @contract(s='str', dp='str', returns=CResource)
    def make_resource(self, dp, s):
        if not isinstance(dp, str):
            raise DPInternalError((dp, s))
        if not dp in self.names:
            msg = 'Unknown design problem %r.' % dp
            raise DPSemanticError(msg)

        ndp = self.names[dp]

        if not s in ndp.get_rnames():
            msg = 'Unknown resource %r for design problem %r.' % (s, dp)
            msg += ' Known functions: %s.' % format_list(ndp.get_rnames())
            raise DPSemanticError(msg)

        return CResource(dp, s)

    # TODO: move away
    def _check_good_name(self, name):
        forbidden = ['(', ']', ')', ' ']
        for f in forbidden:
            if f in name:
                raise ValueError(name)

    @contract(name=str)
    def set_var2resource(self, name, value):
        self._check_good_name(name)
        if name in self.var2resource:
            raise ValueError(name)

        self.var2resource[name] = value

    @contract(name=str)
    def set_var2function(self, name, value):
        self._check_good_name(name)
        if name in self.var2function:
            raise ValueError(name)

        self.var2function[name] = value
        
    @contract(name=str)
    def set_var2model(self, name, value):
        # from mocdp.comp.interfaces import NamedDP
        assert isinstance(value, NamedDP)
        self._check_good_name(name)
        if name in self.var2model:
            raise ValueError(name)
        self.var2model[name] = value

    def get_var2model(self, name):
        if not name in self.var2model:
            msg = 'I cannot find the MCDP type %r.' % name
            msg += '\n Known types: %s' % list(self.var2model)
            msg += '\n Known constants: %s' % list(self.constants)
            msg += '\n Known resources: %s' % list(self.var2resource)
            raise NoSuchMCDPType(msg)
        return self.var2model[name]

    @contract(name=str)
    def set_constant(self, name, value):
        self._check_good_name(name)
        self._check_good_constant_name(name)

        self.constants[name] = value
        
    @contract(name=str, uc=UncertainConstant)
    def set_uncertain_constant(self, name, uc):
        self._check_good_name(name)
        self._check_good_constant_name(name)
        self.uncertain_constants[name] = uc
        
    def _check_good_constant_name(self, name):
        if name in self.var2resource:
            raise ValueError(name)
        if name in self.var2function:
            raise ValueError(name)
        if name in self.constants:
            raise ValueError(name)
        if name in self.uncertain_constants:
            raise ValueError(name)
        
    def info(self, s):
        # print(s)
        pass

    def add_ndp(self, name, ndp):
        self.info('Adding name %r = %r' % (name, ndp))
        if name in self.names:
            # where?
            msg = 'Repeated identifier'
            raise_desc(DPInternalError, msg, name=name)        
        self.names[name] = ndp

    @contract(returns=str)
    def add_ndp_fun_node(self, fname, F):
        """ Returns the name of the node (something like _fun_****) """
        if '-' in fname:
            raise ValueError(fname)
        ndp = dpwrap(FunctionNode(F, fname), fname, fname)
        name = get_name_for_fun_node(fname)
        # print('Adding new function %r as %r.' % (str(name), fname))
        self.add_ndp(name, ndp)
        self.fnames.append(fname)
        return name

    def is_new_function(self, name):
        assert name in self.names
        return '_fun_' in name

    def is_new_resource(self, name):
        assert name in self.names
        return '_res_' in name

    @contract(returns=str)
    def add_ndp_res_node(self, rname, R):
        """ returns the name of the node """
        if '-' in rname:
            raise ValueError(rname)
        ndp = dpwrap(ResourceNode(R, rname), rname, rname)
        name = get_name_for_res_node(rname)
        # self.info('Adding new resource %r as %r ' % (str(name), rname))
        self.add_ndp(name, ndp)
        self.rnames.append(rname)
        return name


    def iterate_new_functions(self):
        for fname in self.fnames:
            name = get_name_for_fun_node(fname)
            ndp = self.names[name]
            yield fname, name, ndp

    def iterate_new_resources(self):
        for rname in self.rnames:
            name = get_name_for_res_node(rname)
            ndp = self.names[name]
            yield rname, name, ndp

    def get_ndp_res(self, rname):
        name = get_name_for_res_node(rname)
        if not name in self.names:
            raise ValueError('Resource name %r (%r) not found in %s.' %
                             (rname, name, list(self.names)))
        return self.names[name]

    def get_ndp_fun(self, fname):
        name = get_name_for_fun_node(fname)
        if not name in self.names:
            raise ValueError('Function name %r (%r) not found in %s.' %
                             (fname, name, list(self.names)))
        return self.names[name]

    @contract(c=Connection)
    def add_connection(self, c):
        self.info('Adding connection %r' % str(c))
        if not c.dp1 in self.names:
            raise_desc(DPSemanticError, 'Invalid connection: %r not found.' % c.dp1,
                       names=self.names, c=c)

        if not c.dp2 in self.names:
            raise_desc(DPSemanticError, 'Invalid connection: %r not found.' % c.dp2,
                       names=self.names, c=c)

        mcdp_dev_warning('redo this check')


        if self.is_new_function(c.dp2):
            msg = "Cannot add connection to new function %r." % c.dp2
            raise_desc(DPSemanticError, msg, c=c)

        if self.is_new_resource(c.dp1):
            msg = "Cannot add connection to new resource %r." % c.dp1
            raise_desc(DPSemanticError, msg, c=c)

        # Find if there is already a connection to c.dp2,c.s2
        # for c0 in self.connections:
        #    if c0.dp2 == c.dp2 and c0.s2 == c.s2:
        #        msg = 'There is already a connection to function %r of %r.' % (c.s2, c.dp2)
        #        raise_desc(DPSemanticError, msg)

        ndp1 = self.names[c.dp1]
        ndp2 = self.names[c.dp2]

        rnames = ndp1.get_rnames()
        if not c.s1 in rnames:
            msg = "Resource %r does not exist (known: %s)" % (c.s1, format_list(rnames))
            raise_desc(DPSemanticError, msg, known=rnames)

        fnames = ndp2.get_fnames()
        if not c.s2 in fnames:
            msg = "Function %r does not exist (known: %s)" % (c.s2,format_list(fnames))
            raise_desc(DPSemanticError, msg, known=fnames)


        R1 = ndp1.get_rtype(c.s1)
        F2 = ndp2.get_ftype(c.s2)
        # print('connecting R1 %s to R2 %s' % (R1, F2))
        if not (R1 == F2):
            msg = 'Connection between different spaces.'
            raise_desc(DPSemanticError, msg, c=c,
                       F2=F2, R1=R1, ndp1=ndp1,
                       ndp2=ndp2)

        self.connections.append(c)

    def new_name(self, prefix):
        for i in range(1, 1000):
            cand = prefix + '%d' % i
            if not cand in self.names:
                return cand
        assert False, 'cannot find name? %r' % cand

    def _fun_name_exists(self, fname):
        for ndp in self.names.values():
            if fname in ndp.get_fnames():
                return True
        return False

    def _res_name_exists(self, rname):
        for ndp in self.names.values():
            if rname in ndp.get_rnames():
                return True
        return False

    def new_fun_name(self, prefix):
        if not self._fun_name_exists(prefix):
            return prefix
        for i in range(1, 1000):
            cand = prefix + '%d' % i
            if not self._fun_name_exists(cand):
                return cand
        assert False, 'cannot find name? %r' % cand

    def new_res_name(self, prefix):
        if not self._res_name_exists(prefix):
            return prefix
        for i in range(2, 10000):
            cand = prefix + '%d' % i
            if not self._res_name_exists(cand):
                return cand
        assert False, 'cannot find name? %r' % cand

    @contract(a=CResource)
    def get_rtype(self, a):
        """ Gets the type of a resource, raises DPSemanticError if not present. """
        check_isinstance(a, CResource)
        if not a.dp in self.names:
            msg = "Cannot find design problem %r." % str(a)
            raise DPSemanticError(msg)
        ndp = self.names[a.dp]
        if not a.s in ndp.get_rnames():
            msg = "Design problem %r does not have resource %r." % (a.dp, a.s)
            raise_desc(DPSemanticError, msg, rnames=ndp.get_rnames())
        return ndp.get_rtype(a.s)

    @contract(a=CFunction)
    def get_ftype(self, a):
        """ Gets the type of a function, raises DPSemanticError if not present. """
        check_isinstance(a, CFunction)
        if not a.dp in self.names:
            msg = "Cannot find design problem %r." % str(a)
            raise DPSemanticError(msg)
        dp = self.names[a.dp]
        if not a.s in dp.get_fnames():
            msg = "Design problem %r does not have function %r." % (a.dp, a.s)
            raise_desc(DPSemanticError, msg, fnames=dp.get_fnames())
        return dp.get_ftype(a.s)

    def ires_init(self):
        self.indexed_res = {}

    def ifun_init(self):
        self.indexed_fun =  {}
    
    def ifun_finish(self):
        """ Searches for all the automatically created DPs and closes them
            by adding 0 constants. """
        from mcdp_lang.helpers import get_valuewithunits_as_resource
        from mcdp_lang.helpers import get_constant_minimals_as_resources

        def connectedfun(ndp_name, s):
            assert ndp_name in self.names
            assert s in self.names[ndp_name].get_fnames()
            for c in self.connections:
                if c.dp2 == ndp_name and c.s2 == s:
                    return True
            return False
            
        for which, created in self.indexed_fun.items():
            ndp = self.names[created]
            for fname in ndp.get_fnames():
                connected = connectedfun(created, fname)
                if not connected:
                    F = ndp.get_ftype(fname)
                    if not self._can_ignore_unconnected(F):
                        msg = 'Missing value %r for %r.' % (fname, which)
                        raise_desc(DPSemanticError, msg)
                    else:
                        msg = 'Using default value for unconnected resource %s %s' % (created, fname)
                        # logger.warn(msg)

                    try:
                        zero = F.get_bottom()
                        vu = ValueWithUnits(value=zero, unit=F)
                        res = get_valuewithunits_as_resource(vu, self)
                    except NotBounded:
                        minimals = F.get_minimal_elements()
                        res = get_constant_minimals_as_resources(F, minimals, self)
                    c = Connection(dp1=res.dp, s1=res.s, dp2=created, s2=fname)
                    self.add_connection(c)

    def ires_finish(self):
        """ Searches for all the automatically created DPs and closes them
            by adding 0 constants. """
        from mcdp_lang.helpers import get_valuewithunits_as_function
        from mcdp_lang.helpers import get_constant_maximals_as_function

        def connectedres(ndp_name, s):
            assert ndp_name in self.names
            assert s in self.names[ndp_name].get_rnames()
            for c in self.connections:
                if c.dp1 == ndp_name and c.s1 == s:
                    return True
            return False

        for which, created in self.indexed_res.items():
            ndp = self.names[created]
            for rname in ndp.get_rnames():
                connected = connectedres(created, rname)
                R = ndp.get_rtype(rname)
                if not connected:
                    if not self._can_ignore_unconnected(R):
                        msg = 'Missing value %r for %r.' % (rname, which)
                        raise_desc(DPSemanticError, msg)
                    else:
                        msg = 'Using default value for unconnected function %s %s' % (created, rname)
                        # logger.warn(msg)
                    try:
                        top = R.get_top()
                        vu = ValueWithUnits(value=top, unit=R)
                        res = get_valuewithunits_as_function(vu, self)
                    except NotBounded:
                        maximals = R.get_maximal_elements()
                        res = get_constant_maximals_as_function(R, maximals, self)
                    c = Connection(dp2=res.dp, s2=res.s, dp1=created, s1=rname)
                    self.add_connection(c)

    def _can_ignore_unconnected(self, P):
        if isinstance(P, FinitePoset) and len(P.elements) == 1:
            return True
        else:
            return False

    @contract(cr=CResource, index=int, returns=CResource)
    def ires_get_index(self, cr, index):
        from mcdp_dp.dp_flatten import TakeRes
        from mocdp.comp.wrap import SimpleWrap

        if not cr in self.indexed_res:
            R = self.get_rtype(cr)
            n = len(R.subs)

            # todo: use labels
            if isinstance(R, PosetProductWithLabels):
                rnames = list(R.labels)
            else:
                rnames = ['_r%d' % i for i in range(n)]
            coords = list(range(n))
            dp = TakeRes(R, coords)
            ndp_out = '_muxed'
            ndp = SimpleWrap(dp, fnames=ndp_out, rnames=rnames)
            ndp_name = self.new_name('_indexing')

            self.add_ndp(ndp_name, ndp)
            c = Connection(dp2=ndp_name, s2=ndp_out, dp1=cr.dp, s1=cr.s)
            self.add_connection(c)

            self.indexed_res[cr] = ndp_name

        ndp_name = self.indexed_res[cr]

        ndp = self.names[ndp_name]
        rnames = ndp.get_rnames()
        n = len(rnames)
        s = rnames[index]
        if not (0 <= index < n):
            msg = 'Out of bounds.'
            raise_desc(DPSemanticError, msg, index=index, R=R)

        res = self.make_resource(ndp_name, s)
        return res

    @contract(cf=CFunction, index=int, returns=CFunction)
    def ifun_get_index(self, cf, index):
        from mcdp_dp.dp_flatten import TakeFun
        from mocdp.comp.wrap import SimpleWrap

        if not cf in self.indexed_fun:
            F = self.get_ftype(cf)
            n = len(F.subs)

            # todo: use labels
            if isinstance(F, PosetProductWithLabels):
                fnames = list(F.labels)
            else:
                fnames = ['_f%d' % i for i in range(n)]
            coords = list(range(n))
            dp = TakeFun(F, coords)
            ndp_out = '_muxed'
            ndp = SimpleWrap(dp, fnames=fnames, rnames=ndp_out)
            ndp_name = self.new_name('_indexing')

            self.add_ndp(ndp_name, ndp)
            c = Connection(dp1=ndp_name, s1=ndp_out, dp2=cf.dp, s2=cf.s)
            self.add_connection(c)

            self.indexed_fun[cf] = ndp_name

        ndp_name = self.indexed_fun[cf]

        ndp = self.names[ndp_name]
        fnames = ndp.get_fnames()
        n = len(fnames)
        s = fnames[index]
        if not (0 <= index < n):
            msg = 'Out of bounds.'
            raise_desc(DPSemanticError, msg, index=index, F=F)

        res = self.make_function(ndp_name, s)
        return res
     
ModelBuildingContext = Context

