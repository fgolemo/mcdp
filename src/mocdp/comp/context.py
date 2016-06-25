# -*- coding: utf-8 -*-
from collections import namedtuple
from contracts import contract
from contracts.utils import indent, raise_desc
from mcdp_posets import Space
from mcdp_posets.poset import Poset
from mocdp.comp.interfaces import NamedDP
from mocdp.comp.wrap import dpwrap
from mcdp_dp.dp_identity import Identity
from mcdp_dp.primitive import PrimitiveDP
from mocdp.exceptions import DPInternalError, DPSemanticError, mcdp_dev_warning
from mocdp.comp.template_for_nameddp import TemplateForNamedDP

__all__ = [
    'Connection',
    'Context',
]

Connection0 = namedtuple('Connection', 'dp1 s1 dp2 s2')
class Connection(Connection0):
    def __repr__(self):
        return ("Constraint(%s.%s <= %s.%s)" %
                (self.dp1, self.s1, self.dp2, self.s2))

#         return ("Constraint(dp1,s1 %s, %s <= dp2,s2 %s, %s)" %
#                 (self.dp1, self.s1, self.dp2, self.s2))

    def involves_any_of_these_nodes(self, nodes):
        """ Returns true if any of the two nodes is in the iterable nodes."""
        return self.dp1 in nodes or self.dp2 in nodes


class CFunction():
    @contract(dp=str, s=str)
    def __init__(self, dp, s):
        self.dp = dp
        self.s = s

    def __repr__(self):
        return 'CFunction(%s.%s)' % (self.dp, self.s)

class CResource():
    @contract(dp=str, s=str)
    def __init__(self, dp, s):
        self.dp = dp
        self.s = s

    def __repr__(self):
        return 'CResource(%s.%s)' % (self.dp, self.s)


class ValueWithUnits():
    """ "unit" should have been "space" """
    @contract(unit=Space)
    def __init__(self, value, unit):
        unit.belongs(value)
        self.value = value
        self.unit = unit

    def __repr__(self):
        return 'ValueWithUnits(%r, %r)' % (self.value, self.unit)

def get_name_for_fun_node(name):
    return '_fun_%s' % name

def get_name_for_res_node(name):
    return '_res_%s' % name


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


class NoSuchMCDPType(Exception):
    pass



class Context():

    def __init__(self):
        self.names = {}  # name -> ndp
        self.connections = []

        self.fnames = []
        self.rnames = []

        self.var2resource = {}  # str -> Resource
        self.var2function = {}  # str -> Function
        self.var2model = {}  # str -> NamedDP
        self.constants = {}  # str -> ValueWithUnits

        self.load_ndp_hooks = []
        self.load_posets_hooks = []
        self.load_primitivedp_hooks = []
        self.load_template_hooks = []

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
        c.var2resource = {}  # XXX?
        c.var2function = {}  # XXX?
        c.var2model.update(self.var2model)
        c.constants.update(self.constants)
        return c

    def load_ndp(self, load_arg):
        return self._load_hooks(load_arg, self.load_ndp_hooks, NamedDP)

    def load_primitivedp(self, load_arg):
        return self._load_hooks(load_arg, self.load_primitivedp_hooks, PrimitiveDP)

    def load_poset(self, load_arg):
        return self._load_hooks(load_arg, self.load_posets_hooks, Poset)

    def load_template(self, load_arg):
        return self._load_hooks(load_arg, self.load_template_hooks, TemplateForNamedDP)

    def _load_hooks(self, load_arg, hooks, expected):
        errors = []
        for hook in hooks:
            try:
                res = hook(load_arg)
                if not isinstance(res, expected):
                    msg = 'The hook did not return the expected type.'
                    raise_desc(DPSemanticError, msg, res=res, expected=expected)
                return res
            except DPSemanticError as e:
                errors.append(str(e))
        msg = 'Could not load: \n%s' % "\n\n".join(errors)
        raise DPSemanticError(msg)


    @contract(s='str', dp='str', returns=CFunction)
    def make_function(self, dp, s):
        assert isinstance(dp, str)
        if not dp in self.names:
            msg = 'Unknown dp (%r.%r)' % (dp, s)
            raise DPSemanticError(msg)
        return CFunction(dp, s)

    @contract(s='str', dp='str', returns=CResource)
    def make_resource(self, dp, s):
        if not isinstance(dp, str):
            raise DPInternalError((dp, s))
        if not dp in self.names:
            msg = 'Unknown dp (%r.%r)' % (dp, s)
            raise DPSemanticError(msg)

        ndp = self.names[dp]

        if not s in ndp.get_rnames():
            msg = 'Unknown resource %r.' % (s)
            msg += '\nThe design problem %r evaluates to:' % dp
            msg += '\n' + indent(ndp.repr_long(), '  ')
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
        if name in self.var2resource:
            raise ValueError(name)

        self.constants[name] = value

    def info(self, s):
        # print(s)
        pass

    def add_ndp(self, name, ndp):
        self.info('Adding name %r = %r' % (name, ndp))
        if name in self.names:
            # where?
            raise DPSemanticError('Repeated identifier %r.' % name)
        self.names[name] = ndp

    @contract(returns=str)
    def add_ndp_fun_node(self, fname, F):
        ndp = dpwrap(Identity(F), fname, fname)
        name = get_name_for_fun_node(fname)
        self.info('Adding new function %r as %r.' % (str(name), fname))
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
        ndp = dpwrap(Identity(R), rname, rname)
        name = get_name_for_res_node(rname)
        self.info('Adding new resource %r as %r ' % (str(name), rname))
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
            msg = "Resource %r does not exist (known: %s)" % (c.s1, ", ".join(rnames))
            raise_desc(DPSemanticError, msg, known=rnames)

        fnames = ndp2.get_fnames()
        if not c.s2 in fnames:
            msg = "Function %r does not exist (known: %s)" % (c.s2, ", ".join(fnames))
            raise_desc(DPSemanticError, msg, known=rnames)


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
        for i in range(1, 1000):
            cand = prefix + '%d' % i
            if not self._fun_name_exists(cand):
                return cand
        assert False, 'cannot find name? %r' % cand

    def new_res_name(self, prefix):
        for i in range(1, 10000):
            cand = prefix + '%d' % i
            if not self._res_name_exists(cand):
                return cand
        assert False, 'cannot find name? %r' % cand

    @contract(a=CResource)
    def get_rtype(self, a):
        """ Gets the type of a resource, raises DPSemanticError if not present. """
        if not a.dp in self.names:
            msg = "Cannot find design problem %r." % str(a)
            raise DPSemanticError(msg)
        dp = self.names[a.dp]
        if not a.s in dp.get_rnames():
            msg = "Design problem %r does not have resource %r." % (a.dp, a.s)
            raise_desc(DPSemanticError, msg, ndp=dp.repr_long())
        return dp.get_rtype(a.s)

    @contract(a=CFunction)
    def get_ftype(self, a):
        """ Gets the type of a function, raises DPSemanticError if not present. """
        if not a.dp in self.names:
            msg = "Cannot find design problem %r." % str(a)
            raise DPSemanticError(msg)
        dp = self.names[a.dp]
        if not a.s in dp.get_fnames():
            msg = "Design problem %r does not have function %r." % (a.dp, a.s)
            raise_desc(DPSemanticError, msg, ndp=dp.repr_long())
        return dp.get_ftype(a.s)

