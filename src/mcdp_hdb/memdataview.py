from abc import abstractmethod, ABCMeta
from copy import deepcopy

from contracts import contract
from contracts.utils import raise_desc, raise_wrapped, indent

from mcdp import MCDPConstants
from mcdp.logs import logger
from mcdp_utils_misc import format_list

from .memdataview_exceptions import InsufficientPrivileges, FieldNotFound,\
    InvalidOperation, EntryNotFound
from .memdataview_utils import special_string_interpret
from .schema import SchemaBase, SchemaBytes, SchemaString,\
    SchemaDate


__all__ = [
    'ViewBase',
    'ViewContext0',
    'ViewHash0',
    'ViewList0',
    'ViewString',
#     'ViewBytes',
#     'ViewDate',
]

class ViewBase(object):
    
    __metaclass__ = ABCMeta
    
    @contract(view_manager='isinstance(ViewManager)')
    def __init__(self, view_manager, data, schema):
        schema.validate(data)
        self._view_manager = view_manager
        self._data = data
        self._schema = schema
        self._prefix = ()
        self._who = None
        self._principals = []
        # if not none, it will be called when an event is generated
        self._notify_callback = None
        
    @contract(s=SchemaBase)
    def _create_view_instance(self, s, data, url):
        v = self._view_manager.create_view_instance(s, data)
        v._prefix = self._prefix + (url,)
        v._who = self._who
        v._principals = self._principals 
        v._notify_callback = self._notify_callback
        return v
    
    @abstractmethod
    def child(self, key):
        ''' '''
    def check_can_read(self):
        privilege = MCDPConstants.Privileges.READ
        self.check_privilege(privilege)
    
    def check_can_write(self):
        privilege = MCDPConstants.Privileges.WRITE
        self.check_privilege(privilege)
        
    def check_privilege(self, privilege):
        ''' Raises exception InsufficientPrivileges ''' 
        acl = self._schema.get_acl()
        # interpret special rules 
        acl.rules = deepcopy(acl.rules)
        for r in acl.rules:
            if r.to_whom.startswith('special:'):
                rest = r.to_whom[r.to_whom.index(':')+1:]
                r.to_whom = special_string_interpret(rest, self._prefix)
    
        principals = self._principals
        ok = acl.allowed_(privilege, principals)
        if not ok:
            msg = 'Cannot have privilege %r for principals %s.' % (privilege, principals)
            msg += '\n' + indent(acl, ' > ')
            raise_desc(InsufficientPrivileges, msg)
            
        if False:
            msg = 'Permission %s granted to %s' % (privilege, principals)
            msg += '\n' + indent(acl, ' > ')
            logger.debug(msg)
            
    def _get_event_id(self):
        from time import gmtime, strftime, time
        ms = int(time() * 1000) % 1000
        d = strftime("%Y-%m-%d:%H:%M:%S:", gmtime()) + '%03d' % ms
        return d        
    
    def _get_prefix(self, append):
        if append is None:
            return self._prefix
        else:
            return self._prefix + (append,)

    def _get_event_kwargs(self):
        _id = self._get_event_id()
        who= self._who
        return dict(_id=_id, who=who)
     
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
            # check access
            v = self._create_view_instance(child, child_data, name)
            v.check_can_read()
            # just return the value
            return child_data
        else:
            return self._create_view_instance(child, child_data, name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            return object.__setattr__(self, name, value)
        child = self._get_child(name)
        child.validate(value)
        v = self._create_view_instance(child, self._data[name], name)
        v.check_can_write()
            
        from .memdata_events import event_leaf_set

        event = event_leaf_set(parent=self._prefix,
                               name=name, 
                               value=value, 
                               **self._get_event_kwargs())
        self._notify(event)

        self._data[name] = value
        
    def child(self, name):
        child = self._get_child(name)
        child_data = self._data[name]
        v = self._create_view_instance(child, child_data, name)        
        if is_simple_data(child):
            def set_callback(value):
                self._data[name] = value
                
                from .memdata_events import event_leaf_set
                event = event_leaf_set(parent=self._prefix,
                                       name=name, value=value,
                                        **self._get_event_kwargs())
                self._notify(event)
                
            v._set_callback = set_callback
        return v
    

def is_simple_data(s):
    return isinstance(s, (SchemaString, SchemaBytes, SchemaDate))

class ViewHash0(ViewBase):

    def __contains__(self, key):
        return key in self._data
    
    def keys(self):
        return self._data.keys()
    
    def values(self):
        return self._data.values()
    
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
            self.child(d).check_can_read()
            return d
        else:
            return self._create_view_instance(prototype, d, key)

    def __setitem__(self, key, value):
        from .memdata_events import event_dict_setitem
        
        self.check_can_write()
        prototype = self._schema.prototype
        prototype.validate(value) 
        
        
        event = event_dict_setitem(name=self._prefix,
                                   key=key, 
                                   value=value, 
                                   **self._get_event_kwargs())
        self._notify(event)


        self._data[key] = value
        
    def __delitem__(self, key):
        from .memdata_events import event_dict_delitem
        
        self.check_can_write()
        if not key in self._data:
            msg = ('Could not delete not existing key "%s"; known: %s.' % 
                   (key, format_list(self._data)))
            raise_desc(InvalidOperation, msg)
        
        event = event_dict_delitem(name=self._prefix,
                                   key=key, 
                                   **self._get_event_kwargs())
        self._notify(event)

        del self._data[key]
        
    def rename(self, key1, key2):
        from .memdata_events import event_dict_rename
        self.check_can_write()
        if not key1 in self._data:
            msg = ('Could not rename not existing key "%s"; known: %s.' % 
                   (key1, format_list(self._data)))
            raise_desc(InvalidOperation, msg)
        
        event = event_dict_rename(name=self._prefix,
                                   key=key1, key2=key2,
                                   **self._get_event_kwargs())
        self._notify(event)

        self._data[key2] = self._data.pop(key1)
        
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

        from .memdata_events import event_list_setitem
        event = event_list_setitem(name=self._prefix,
                                   index=i,
                                   value=value, 
                                   **self._get_event_kwargs())
        self._notify(event)
        

        
    def insert(self, i, value):
        self._schema.prototype.validate(value) 
        self._data.insert(i, value) 

        from .memdata_events import event_list_insert
        event = event_list_insert(name=self._prefix,
                                   index=i,
                                   value=value, 
                                   **self._get_event_kwargs())
        self._notify(event)
        
        
    def delete(self, i):
        # todo: check i 
        if not( 0 <= i < len(self._data)):
            msg ='Invalid index %d for list of length %d.' % (i, len(self._data))
            raise ValueError(msg)
        self._data.pop(i) 
        
        from .memdata_events import event_list_delete
        event = event_list_delete(name=self._prefix,
                                   index=i, 
                                   **self._get_event_kwargs())
        self._notify(event)
        
    def append(self, value):
        self._schema.prototype.validate(value) 
        self._data.append(value) 
          
        from .memdata_events import event_list_append
        event = event_list_append(name=self._prefix,
                                   value=value, 
                                   **self._get_event_kwargs())
        self._notify(event)
