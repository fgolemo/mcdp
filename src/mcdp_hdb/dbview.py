from abc import abstractmethod, ABCMeta
import time

from contracts import contract
from contracts.utils import raise_desc, raise_wrapped

from mcdp_hdb.change_events import event_set, event_delete, event_rename
from mcdp_hdb.schema import SchemaBase, SchemaContext, SchemaBytes, SchemaString,\
    SchemaDate, SchemaHash, SchemaList
from mcdp_utils_misc.string_utils import format_list


class ViewError(Exception):
    pass

class FieldNotFound(ViewError):
    pass

class EntryNotFound(ViewError, KeyError):
    pass

class InvalidOperation(ViewError):
    pass

class ViewBase(object):
    
    __metaclass__ = ABCMeta
    
    def __init__(self, view_manager, data, schema):
        schema.validate(data)
        self._view_manager = view_manager
        self._data = data
        self._schema = schema
        self._prefix = ()
        self._who = {}
        # if not none, it will be called when an event is generated
        self._notify_callback = None
        
    @contract(s=SchemaBase)
    def _create_view_instance(self, s, data, url):
        v = self._view_manager.create_view_instance(s, data)
        v._prefix = self._prefix + (url,)
        v._who = self._who
        v._notify_callback = self._notify_callback
        return v
    
    @abstractmethod
    def child(self, key):
        ''' '''
    
    def _get_event_id(self):
        return int(time.time() * 1000000)
    
    def _get_prefix(self, append):
        if append is None:
            return self._prefix
        else:
            return self._prefix + (append,)
    
    def _notify_set(self, what, value):
        _id = self._get_event_id()
        what = self._get_prefix(what)
        event = event_set(_id=_id, who=self._who, what=what, value=value)
        self._notify(event)
        
    def _notify_delete(self, what): 
        _id = self._get_event_id()
        what = self._get_prefix(what)
        event = event_delete(_id=_id, who=self._who, what=what)
        self._notify(event)
    
    def _notify_rename(self, what, key2):
        _id = self._get_event_id()
        what = self._get_prefix(what)
        event = event_rename(_id=_id, who=self._who, what=what, key2=key2)
        self._notify(event)

    def _notify(self, event):
        if self._notify_callback is not None:
            self._notify_callback.__call__(event)
        
class ViewContext0(ViewBase): 
    
    def _get_child(self, name):
        children = self._schema.children
        if not name in children:
            msg = 'Could not find field "%s"; available: %s.' % (name, format_list(children))
            raise_desc(FieldNotFound, msg)

        child = children[name]
        return child

    def __getattr__(self, name):
        if name.startswith('_') or name == 'child':
            return object.__getattr__(self, name)
        child = self._get_child(name)
        assert name in self._data
        child_data = self._data[name]
        if is_simple_data(child):
            # just return the value
            return child_data
        else:
            return self._create_view_instance(child, child_data, name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            return object.__setattr__(self, name, value)
        child = self._get_child(name)
        child.validate(value)
        self._notify_set(name, value)
        self._data[name] = value
        
    def child(self, name):
        child = self._get_child(name)
        child_data = self._data[name]
        v = self._create_view_instance(child, child_data, name)        
        if is_simple_data(child):
            def set_callback(value):
                self._data[name] = value
            v._set_callback = set_callback
        return v
    

def is_simple_data(s):
    return isinstance(s, (SchemaString, SchemaBytes, SchemaDate))

class ViewHash0(ViewBase):

    def __contains__(self, key):
        return key in self._data
    
    def keys(self):
        return self._data.keys()
    def __iter__(self):
        return self._data.__iter__()
    
    def child(self, name):
        if not name in self._data:
            msg = 'Cannot get child "%s"; known: %s.' % (name, format_list(self.keys()))
            raise_desc(InvalidOperation, msg)
        d = self._data[name]
        prototype = self._schema.prototype    
        v = self._create_view_instance(prototype, d, name)
        if is_simple_data(prototype):
            def set_callback(value):
                self._data[name] = value
            v._set_callback = set_callback
        return v
    
    def __getitem__(self, key):
        if not key in self._data:
            msg = 'Could not find key "%s"; available keys are %s' % (key, format_list(self._data))
            raise_desc(EntryNotFound, msg)
        d = self._data[key]
        prototype = self._schema.prototype
        if is_simple_data(prototype):
            return d
        else:
            return self._create_view_instance(prototype, d, key)

    def __setitem__(self, key, value):
        prototype = self._schema.prototype
        prototype.validate(value)
        self._notify_set(key, value)
        self._data[key] = value
        
    def __delitem__(self, key):
        if not key in self._data:
            msg = ('Could not delete not existing key "%s"; known: %s.' % 
                   (key, format_list(self._data)))
            raise_desc(InvalidOperation, msg)
        del self._data[key]
        self._notify_delete(key)
        
    def rename(self, key1, key2):
        if not key1 in self._data:
            msg = ('Could not rename not existing key "%s"; known: %s.' % 
                   (key1, format_list(self._data)))
            raise_desc(InvalidOperation, msg)
        self._data[key2] = self._data.pop(key1)
        self._notify_rename(key1, key2)    

class ViewString(ViewBase):
    def child(self, i):  # @UnusedVariable
        msg = 'Cannot get child of view for basic types.'
        raise_desc(InvalidOperation, msg)
    
    def set(self, value):
        self._schema.validate(value)
        self._set_callback(value)
        
    def get(self):
        return self._data
        
class ViewList0(ViewBase): 
        
    def __len__(self):
        return self._data.__len__()
    
    def __iter__(self):
        if is_simple_data(self._schema.prototype):
            return self._data.__iter__()
        else:
            raise NotImplementedError()
    
    def __contains__(self, key):
        return key in self._data
    
    def child(self, i):
        prototype = self._schema.prototype
        try:
            d = self._data[i]
        except IndexError as e:
            msg = 'Could not use index %d' % i
            raise_wrapped(EntryNotFound, e, msg)
        return self._create_view_instance(prototype, d, i)   
    
    def __getitem__(self, i):
        prototype = self._schema.prototype
        try:
            d = self._data[i]
        except IndexError as e:
            msg = 'Could not use index %d' % i
            raise_wrapped(EntryNotFound, e, msg)
        if is_simple_data(prototype):
            return d
        else:
            return self._create_view_instance(prototype, d, i)
            
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

class ViewManager(object):
    
    @contract(schema=SchemaBase)
    def __init__(self, schema):
        self.schema = schema

        self.s2baseclass = {}

    def set_view_class(self, s, baseclass):
        self.s2baseclass[s] = baseclass

    def view(self, data, who):
        v = self.create_view_instance(self.schema, data)
        v._who = who
        return v

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
    
        if isinstance(s, SchemaString):
            return ViewString(view_manager=self, data=data, schema=s)

        
        raise NotImplementedError(type(s))

class View():
    @contract(view_manager=ViewManager)
    def __init__(self, data, view_manager):
        self.data = data
        self.view_manager = view_manager
