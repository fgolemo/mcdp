from contracts import contract
from contracts.utils import raise_desc, raise_wrapped

from mcdp_hdb.schema import SchemaBase, SchemaContext, SchemaBytes, SchemaString,\
    SchemaDate, SchemaHash, SchemaList
from mcdp_utils_misc.string_utils import format_list
from mcdp.logs import logger


class ViewError(Exception):
    pass

class FieldNotFound(ViewError):
    pass

class EntryNotFound(ViewError, KeyError):
    pass

class InvalidOperation(ViewError):
    pass


class ViewContext0(object):
    @contract(data=dict, schema=SchemaContext)
    def __init__(self, view_manager, data, schema):
        schema.validate(data)
        self._view_manager = view_manager
        self._data = data
        self._schema = schema

    def _get_child(self, name):
        children = self._schema.children
        if not name in children:
            msg = 'Could not find field "%s"; available: %s.' % (name, format_list(children))
            raise_desc(FieldNotFound, msg)

        child = children[name]
        return child

    def __getattr__(self, name):
        if name.startswith('_'):
            return object.__getattr__(self, name)
        child = self._get_child(name)
        assert name in self._data
        child_data = self._data[name]
        if is_simple_data(child):
            # just return the value
            return child_data
        else:
            return self._view_manager.create_view_instance(child, child_data)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            return object.__setattr__(self, name, value)
        child = self._get_child(name)
        child.validate(value)
        self._data[name] = value

def is_simple_data(s):
    return isinstance(s, (SchemaString, SchemaBytes, SchemaDate))

class ViewHash0(object):
    @contract(data=dict, schema=SchemaHash)
    def __init__(self, view_manager, data, schema):
        schema.validate(data)
        self._view_manager = view_manager
        self._data = data
        self._schema = schema

    def __contains__(self, key):
        return key in self._data
    
    def __getitem__(self, key):
        logger.info('get with %r' % key)
        if not key in self._data:
            msg = 'Could not find key "%s"; available keys are %s' % (key, format_list(self._data))
            raise_desc(EntryNotFound, msg)
        d = self._data[key]
        prototype = self._schema.prototype
        if is_simple_data(prototype):
            return d
        else:
            return self._view_manager.create_view_instance(prototype, d)

    def __setitem__(self, key, value):
        prototype = self._schema.prototype
        prototype.validate(value)
        self._data[key] = value
        
    def __delitem__(self, key):
        if not key in self._data:
            msg = 'Could not delete not existing key "%s"; known: %s.' % (key, format_list(self._data))
            raise_desc(InvalidOperation, msg)
        del self._data[key]
            

class ViewList0(object):
    @contract(data=list, schema=SchemaList)
    def __init__(self, view_manager, data, schema):
        schema.validate(data)
        self._view_manager = view_manager
        self._data = data
        self._schema = schema
        
    def __len__(self):
        return self._data.__len__()
    
    def __iter__(self):
        if is_simple_data(self._schema.prototype):
            return self._data.__iter__()
        else:
            raise NotImplementedError()
    
    def __contains__(self, key):
        return key in self._data
    
    def __getitem__(self, i):
        try:
            return self._data[i]
        except IndexError as e:
            msg = 'Could not use index %d' % i
            raise_wrapped(EntryNotFound, e, msg)

    def __setitem__(self, i, value):
        prototype = self._schema.prototype
        prototype.validate(value)
        self._data.__setitem__(i, value)
#         
#     def __delitem__(self, key):
#         if not key in self._data:
#             msg = 'Could not delete not existing key "%s"; known: %s.' % (key, format_list(self._data))
#             raise_desc(InvalidOperation, msg)
#         del self._data[key]
#             

class ViewManager():
    @contract(schema=SchemaBase)
    def __init__(self, schema):
        self.schema = schema

        self.s2baseclass = {}

    def set_view_class(self, s, baseclass):
        self.s2baseclass[s] = baseclass

    def view(self, data):
        return self.create_view_instance(self.schema, data)

    @contract(s=SchemaBase)
    def create_view_instance(self, s, data):
        s.validate(data)
        if s in self.s2baseclass:
            class Base(self.s2baseclass[s]):
                pass
        else:
            class Base(object):
                pass

        if isinstance(s, SchemaContext):
            class ViewContext(Base, ViewContext0): pass
            return ViewContext(view_manager=self, data=data, schema=s)

        if isinstance(s, SchemaHash):
            class ViewHash(Base, ViewHash0): pass
            return ViewHash(view_manager=self, data=data, schema=s)
        
        if isinstance(s, SchemaList):
            class ViewList(Base, ViewList0): pass
            return ViewList(view_manager=self, data=data, schema=s)
        

        raise NotImplementedError(type(s))

class View():
    @contract(view_manager=ViewManager)
    def __init__(self, data, view_manager):
        self.data = data
        self.view_manager = view_manager
