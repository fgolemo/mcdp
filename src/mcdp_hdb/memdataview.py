
from abc import abstractmethod, ABCMeta
from copy import deepcopy
import inspect

from contracts import contract
from contracts import describe_value
from contracts.utils import raise_desc, raise_wrapped, indent, check_isinstance

from mcdp import MCDPConstants
from mcdp import logger
from mcdp_hdb.schema import NotValid, SchemaContext, SchemaHash, SchemaList
from mcdp_shelf import ACL
from mcdp_shelf.access import acl_from_yaml
from mcdp_utils_misc import format_list, memoize_simple

from .memdataview_exceptions import InsufficientPrivileges, InvalidOperation, EntryNotFound
from .memdataview_utils import special_string_interpret
from .schema import SchemaBase, SchemaSimple



__all__ = [
    'ViewBase',
    'ViewContext0',
    'ViewHash0',
    'ViewList0',
    'ViewString', 
]

class ViewBase(object):
    '''
    
        Implementation notes:
        
        First generate the event using _notify, and only then modify the structure.
        Notify() will need access to the current state. 
    '''
    __metaclass__ = ABCMeta

         
    @abstractmethod
    @contract(key=str)
    def child(self, key):
        ''' '''
        
    @contract(name='seq(str)')
    def get_descendant(self, name):
        check_isinstance(name, (list, tuple))
        if len(name) == 0:
            return self
        elif len(name) >= 1:
            child = self.child(name[0])
            return child.get_descendant(name[1:])
        assert False, name
        
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
        self._events = None
        
    def deepcopy(self):
        ''' Will create a copy of the view and the data associated to it. '''
        data = deepcopy(self._data)
        n = type(self)(view_manager=self._view_manager, data=data, schema=self._schema)
        n._who = self._who
        n._principals = self._principals
        n._notify_callback = self._notify_callback
        n._events = self._events
        return n

    def __str__(self):
        names = [base.__name__ for base in inspect.getmro(type(self))]
        for n in list(names):
            if n.endswith('0'):
                names.remove(n)
        remove = ['ViewBase','Base','object', 'ViewMount']
        for r in remove:
            if r in names:
                names.remove(r)
        s = '%s[%s]' % ("/".join(names), self._data)
        assert not 'Mount' in s
        return s

    def set_root(self):
        ''' Give this view all permissions '''
        self.set_principals([MCDPConstants.ROOT])
        
    def set_principals(self, principals):
        self._principals = principals

    @contract(s=SchemaBase, url=str)
    def _create_view_instance(self, s, data, url):
        v = self._view_manager.create_view_instance(s, data)
        v._prefix = self._prefix + (url,)
        v._who = self._who
        v._principals = self._principals 
        v._notify_callback = self._notify_callback
        return v
    
    def check_can_read(self):
        privilege = MCDPConstants.Privileges.READ
        self.check_privilege(privilege)
    
    def check_can_write(self):
        privilege = MCDPConstants.Privileges.WRITE
        self.check_privilege(privilege)
        
    @contract(returns=ACL)
    def get_acl(self):
        ''' Returns the ACL by looking at two things:
            1) the ACL in the schema
            2) the ACL in the data, by looking for a field 
                called 'acl'
                
            (eventually will look also at parent data)
        '''
        acl_schema = self._schema.get_acl()
        rules = acl_schema.rules 
        if isinstance(self, ViewContext0) and 'acl' in self._data:
            acl_data = acl_from_yaml(self._data['acl'])
            rules = acl_data.rules + rules
        acl = ACL(rules)
        return acl
        
    def check_privilege(self, privilege):
        ''' Raises exception InsufficientPrivileges ''' 
        acl = self.get_acl()
        acl = interpret_special_rules(acl, path=self._prefix)
            
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

@contract(acl=ACL, path='seq(str)', returns=ACL)
def interpret_special_rules(acl, path):
    acl = deepcopy(acl)
    # interpret special rules 
    acl.rules = deepcopy(acl.rules)
    for r in acl.rules:
        if r.to_whom.startswith('special:'):
            rest = r.to_whom[r.to_whom.index(':')+1:]
            r.to_whom = special_string_interpret(rest, path)
    return acl

class ViewMount(ViewBase):
    ''' Types of views that support mount points '''
    
    @contract(view=ViewBase)
    def mount(self, child_name, view):
        ''' Mounts a view to be returned by this if it is ever called. '''
        self.mount_points[child_name] = view

    def mount_init(self):
        ''' initializes mount points '''
        # logger.debug('mount_init() for %s' % id(self))
        object.__setattr__(self, 'mount_points', {})
        
class ViewContext0(ViewMount):  

    def init_context(self):
#         logger.debug('init_context() for %s' % id(self))
        self.mount_init()
#         object.__setattr__(self, 'mount_points', {})
        object.__setattr__(self, 'children_already_provided', {})
        
#     def __deepcopy__(self):
#         raise Exception('cannot deepcopy')
    @contract(returns=ViewBase, name=str)
    def child(self, name):
        try:
            children_already_provided = object.__getattribute__(self, 'children_already_provided')
        except AttributeError:
            object.__setattr__(self, 'children_already_provided', {})
            self.mount_init()

            
        try:
            children_already_provided = object.__getattribute__(self, 'children_already_provided')
            mount_points = object.__getattribute__(self, 'mount_points')
        except AttributeError as e:
            msg = 'Could not get basic attrs for %s: %s' % (id(self), e)
            raise_wrapped(AttributeError, e, msg)
            
        if name in mount_points:
            return mount_points[name]
        
        if name in children_already_provided:
            c = children_already_provided[name]
            # but note that the data might have been changed
            # so we need to update it
            c._data  = self._data[name]
            return c
        
        child_schema = self._schema.get_descendant((name,))
        child_data = self._data[name]
        v = self._create_view_instance(child_schema, child_data, name)        
        if is_simple_data(child_schema):
            def set_callback(value):
                if self._data[name] == value:
                    return
                else:
                    from .memdata_events import event_leaf_set
                    event = event_leaf_set(name=self._prefix,
                                           leaf=name, value=value,
                                            **self._get_event_kwargs())
                    self._notify(event)

                    self._data[name] = value
                    
                    
            v._set_callback = set_callback
        self.children_already_provided[name] = v
        return v
    
    def __str__(self):
        names = [base.__name__ for base in inspect.getmro(type(self))]
        for n in list(names):
            if n.endswith('0'):
                names.remove(n)
        remove = ['ViewBase','Base','object', 'ViewMount']
        for r in remove:
            if r in names:
                names.remove(r)
        #myname = "/".join(names)
        myname = names[-1]
        res = []
        for k, schema_child in self._schema.children.items():
            if isinstance(schema_child, SchemaSimple):
                res.append('%s=%r' % (k, self._data[k]))
            else:
                res.append('%s=%s' % (k, self.child(k)))
                
        data_string = ", ".join(res) 
        
        return '%s[%s]' % (myname, data_string)

    def __getattr__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError as _e:
            #print _e
            pass  
        
        child = self.child(name)
        
        if is_simple_data(child._schema):
            child.check_can_read()
            return child._data
        else:
            return child 

    def __setattr__(self, leaf, value):
        if leaf.startswith('_') or leaf in ['mount_points', 'children_already_provided']:
            return object.__setattr__(self, leaf, value)
        v = self.child(leaf)
        v.check_can_write()
        
        try:
            v._schema.validate(value)
        except NotValid as e:
            msg = 'Cannot set %s = %s:' % (leaf, describe_value(value))
            raise_wrapped(NotValid, e, msg, compact=True)
            
        from .memdata_events import event_leaf_set
        from .memdata_events import event_struct_set
        from .memdata_events import event_hash_set
        from .memdata_events import  event_list_set

        if self._data[leaf] == value:
            pass
        else:
            # case of a simple data 
            if is_simple_data(v._schema):
                event = event_leaf_set(name=self._prefix,
                                       leaf=leaf, 
                                       value=value, 
                                       **self._get_event_kwargs())
            # struct
            elif isinstance(v._schema, SchemaContext):
                name = self._prefix + (leaf,)
                event = event_struct_set(name=name, value=value, **self._get_event_kwargs())
            elif isinstance(v._schema, SchemaHash):
                name = self._prefix + (leaf,)
                event = event_hash_set(name=name, value=value, **self._get_event_kwargs())
            elif isinstance(v._schema, SchemaList):
                name = self._prefix + (leaf,)
                event = event_list_set(name=name, value=value, **self._get_event_kwargs())
            else:
                raise NotImplementedError(v._schema)
            self._notify(event)
            
#             logger.debug('setting leaf %s = %s' % (leaf, value))
#             logger.debug('setting leaf schema = %s ' % (v._schema))
            self._data[leaf] = value
        
    
    

def is_simple_data(s):
    return isinstance(s, SchemaSimple)

class ViewHash0(ViewMount):
     
    def init_hash(self):
        self.mount_init()
        object.__setattr__(self, 'children_already_provided', {})
        

    @memoize_simple
    def child(self, name):
        if name in self.children_already_provided:
            return self.children_already_provided[name]
        
        if name in self.mount_points:
            return self.mount_points[name]
        
        if not name in self._data:
            msg = 'Cannot get child "%s"; known: %s.' % (name, format_list(self.keys()))
            raise_desc(InvalidOperation, msg)
            
        d = self._data[name]
        prototype = self._schema.prototype    
        v = self._create_view_instance(prototype, d, name)
        if isinstance(prototype, SchemaSimple):
            def set_callback(value):
                self._data[name] = value
            v._set_callback = set_callback
        self.children_already_provided[name] = v
        return v
    
    def __getitem__(self, key):
        if key in self.mount_points:
            return self.mount_points[key]

        if not key in self._data:
            msg = 'Could not find key "%s"; available keys are %s, mount points %s' % (key, format_list(self._data),
                                                                                       format_list(self.mount_points))
            raise_desc(EntryNotFound, msg)
        d = self._data[key]
        prototype = self._schema.prototype
        if is_simple_data(prototype):
            self.child(key).check_can_read()
            return d
        else:
            return self._create_view_instance(prototype, d, key)

    def __setitem__(self, key, value):
        from .memdata_events import event_dict_setitem
        if isinstance(value, ViewBase):
            value = value._data
        self.check_can_write()
        prototype = self._schema.prototype
        prototype.validate(value) 
        
        if key in self._data and self._data[key] == value:
            pass
        else:
            
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
        
    # Dictionary interface
    def __contains__(self, key):
        return key in self._data or key in self.mount_points
    
    def __len__(self):
        return len(self._data) + len(self.mount_points)
    
    def items(self):
        for k in self.keys():
            yield k, self.child(k)    
            
    def keys(self):
        return list(self._data.keys()) + list(self.mount_points)
    
    def values(self):
        for k in self.keys():
            yield self.child(k)
        
    def __iter__(self):
        for _ in self._data.__iter__():
            yield _
        for _ in self.mount_points.__iter__():
            yield _
class ViewString(ViewBase):
    def child(self, i):  # @UnusedVariable
        msg = 'Cannot get child of view for basic types.'
        raise_desc(InvalidOperation, msg)
    
    def set(self, value):
        self._schema.validate(value)
        self._set_callback(value)
        
    def get(self):
        return self._data

class ViewBytes(ViewBase):
    def child(self, i):  # @UnusedVariable
        msg = 'Cannot get child of view for basic types.'
        raise_desc(InvalidOperation, msg)
    
    def set(self, value):
        self._schema.validate(value)
        self._set_callback(value)
        
    def get(self):
        return self._data
    
class ViewDate(ViewBase):
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
            for _ in self._data.__iter__():
                yield _
        else:
            for i in range(len(self._data)):
                yield self.child(i)
            
    
    def __contains__(self, key):
        return key in self._data
    
    def child(self, i):
        prototype = self._schema.prototype
        try:
            d = self._data[i]
        except IndexError as e:
            msg = 'Could not use index %d' % i
            raise_wrapped(EntryNotFound, e, msg)
        return self._create_view_instance(prototype, d, str(i))   
    
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
        from .memdata_events import event_list_setitem
        event = event_list_setitem(name=self._prefix,
                                   index=i,
                                   value=value, 
                                   **self._get_event_kwargs())
        self._notify(event)
        
        self._data.__setitem__(i, value) 


        
    def insert(self, i, value):
        self._schema.prototype.validate(value) 

        from .memdata_events import event_list_insert
        event = event_list_insert(name=self._prefix,
                                   index=i,
                                   value=value, 
                                   **self._get_event_kwargs())
        self._notify(event)

        self._data.insert(i, value) 
        
    def remove(self, value):
        if not value in self._data:
            msg = 'The list does not contain %r: available %s' % (value, format_list(self._data))
            raise ValueError(msg)
        from .memdata_events import event_list_remove
        event = event_list_remove(name=self._prefix,
                                   value=value, 
                                   **self._get_event_kwargs())
        self._notify(event)
        
        self._data.remove(value)
         
    def delete(self, i):
        # todo: check i 
        if not( 0 <= i < len(self._data)):
            msg ='Invalid index %d for list of length %d.' % (i, len(self._data))
            raise ValueError(msg)
        
        from .memdata_events import event_list_delete
        event = event_list_delete(name=self._prefix,
                                   index=i, 
                                   **self._get_event_kwargs())
        self._notify(event)
        self._data.pop(i) 
        
    def append(self, value):
        self._schema.prototype.validate(value) 
#         logger.info('After appending %s, the list is %s' ( value, self._data))
        from .memdata_events import event_list_append
        event = event_list_append(name=self._prefix,
                                   value=value, 
                                   **self._get_event_kwargs())
        self._notify(event)
        self._data.append(value) 
