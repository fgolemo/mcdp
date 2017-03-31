    - [Allow, Everyone, discover]
from contracts import contract
from contracts.utils import raise_desc

from mcdp_hdb.schema import SchemaBase, SchemaContext, SchemaBytes, SchemaString,\
    SchemaDate, SchemaHash
from mcdp_utils_misc.string_utils import format_list


class ViewError(Exception):
    pass

class FieldNotFound(ViewError):
    pass

class EntryNotFound(ViewError):
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
        simple = isinstance(child, (SchemaString, SchemaBytes, SchemaDate))
        assert name in self._data
        child_data = self._data[name]

        if simple:
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

class ViewHash0(object):
    @contract(data=dict, schema=SchemaHash)
    def __init__(self, view_manager, data, schema):
        schema.validate(data)
        self._view_manager = view_manager
        self._data = data
        self._schema = schema

    def __getitem__(self, key):
        if not key in self._data:
            msg = 'Could not find key "%s"; available keys are %s' % (key, format_list(self._data))
            raise_desc(EntryNotFound, msg)
        d = self._data[key]

        prototype = self._schema.prototype
        simple = isinstance(prototype, (SchemaString, SchemaBytes, SchemaDate))

        if simple:
            return d
        else:
            return self._view_manager.create_view_instance(prototype, d)


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

        raise NotImplementedError(type(s))

class View():
    @contract(view_manager=ViewManager)
    def __init__(self, data, view_manager):
        self.data = data
        self.view_manager = view_manager
