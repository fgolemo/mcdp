from collections import OrderedDict
from copy import deepcopy

from contracts import contract
from contracts.utils import check_isinstance, indent, raise_wrapped

from mcdp.logs import logger
from mcdp_utils_misc import format_list
from mcdp_utils_misc import yaml_dump

from .memdataview import ViewBase
from .memdataview_exceptions import InvalidOperation


class DataEvents(object):
    # For simple values: int, string, float, date
    leaf_set = 'leaf_set' # leaf_set <name> <leaf> <value> 
    struct_set = 'struct_set' # struct_set <name> <struct-value>
    increment = 'increment' # increment <name> <value>
    list_append = 'list_append' # list_append <name>[a list] <value>
    list_delete = 'list_delete' # list_delete <name>[a list] <index> # by index
    list_insert = 'list_insert' # list_delete <name>[seq(str)] <index> <value> 
    list_remove = 'list_remove' # list_remove <name>[seq(str)] <value> # by value
    list_setitem = 'list_setitem' # list_remove <name> <i> <value>
    set_add = 'set_add' # set_add <name> <value>
    set_remove = 'set_remove' # set_remove <name> <value>
    dict_setitem = 'dict_setitem' # dict_setitem <name> <key> <value>
    dict_delitem = 'dict_delitem' # dict_delitem <name> <key>
    dict_rename = 'dict_rename' # dict_rename <name> <key> <key2>
    all_events = [leaf_set, struct_set, increment, list_append, list_insert, list_setitem,
                  list_delete, dict_setitem, dict_delitem, dict_rename]


def event_add_prefix(prefix, event):
    ''' Returns another event with the added prefix. '''
    def add_prefix_to(prefix, event, which):
        assert which in event['arguments']
        check_isinstance(prefix, (list, tuple))
        e = deepcopy(event)
        old = e['arguments'][which]
        check_isinstance(old, (list, tuple))
        new = tuple(prefix) +  tuple(old)
        e['arguments'][which] = new
        return e
#     if event['operation'] == DataEvents.leaf_set:
#         return add_prefix_to(prefix, event, 'parent')
#     else:
    return add_prefix_to(prefix, event, 'name')
    
@contract(name='seq(str)')
def get_view_node(view, name):
    v = view
    while len(name):
        v = v.child(name[0])
        name = name[1:]
    return v

@contract(name='seq(str)', leaf=str)
def event_leaf_set(name, leaf, value, **kwargs):
    arguments = dict(name=name, leaf=leaf, value=value)
    return event_make(event_name=DataEvents.leaf_set, arguments=arguments, **kwargs)

def event_leaf_set_interpret(view, name, leaf, value):
    v = get_view_node(view, name)
    from mcdp_hdb.memdataview import ViewContext0
    check_isinstance(v, ViewContext0)
    vc = v.child(leaf)
    vc._schema.validate(value)
    vc.check_can_write()
    vc.set(value)
    
def get_the_list(view, name):
    # v = get_view_node(view, name)
    v = view.get_descendant(name)
    from mcdp_hdb.memdataview import ViewList0
    check_isinstance(v, ViewList0)
    return v

@contract(name='seq(str)')
def event_struct_set(name, value, **kwargs):
    name = list(name)
    arguments = dict(name=name, value=value)
    return event_make(event_name=DataEvents.struct_set, arguments=arguments, **kwargs)

def event_struct_set_interpret(view, arguments):
    raise NotImplementedError()

@contract(name='seq(str)')
def event_increment(name, value, **kwargs):
    name = list(name)
    arguments = dict(name=name, value=value)
    return event_make(event_name=DataEvents.increment, arguments=arguments, **kwargs)

def event_increment_interpret(view, arguments):
    raise NotImplementedError()

@contract(name='seq(str)')
def event_set_add(name, value, **kwargs):
    name = list(name)
    arguments = dict(name=name, value=value)
    return event_make(event_name=DataEvents.set_add, arguments=arguments, **kwargs)

def event_set_add_interpret(view, arguments):
    raise NotImplementedError()

@contract(name='seq(str)')
def event_set_remove(name, value, **kwargs):
    name = list(name)
    arguments = dict(name=name, value=value)
    return event_make(event_name=DataEvents.set_remove,  arguments=arguments, **kwargs)

def event_set_remove_interpret(view, name, value):
    raise NotImplementedError()

@contract(name='seq(str)')
def event_list_append(name, value, **kwargs):
    arguments = dict(name=name, value=value)
    return event_make(event_name=DataEvents.list_append, arguments=arguments, **kwargs)

def event_list_append_interpret(view, name, value):
    l = get_the_list(view, name)
    l.check_can_write()
    l.append(value)

@contract(name='seq(str)')
def event_list_setitem(name, index, value, **kwargs):
    arguments = dict(name=name,index=index, value=value)
    return event_make(event_name=DataEvents.list_setitem, arguments=arguments, **kwargs)

def event_list_setitem_interpret(view, name, index, value):
    l = get_the_list(view, name)
    l.check_can_write()
    l[index] = value
    
@contract(name='seq(str)')
def event_list_delete(name, index, **kwargs):
    name = list(name)
    arguments = dict(name=name, index=index)
    return event_make(event_name=DataEvents.list_delete, arguments=arguments, **kwargs)

def event_list_delete_interpret(view, name, index):
    l = get_the_list(view, name)
    l.check_can_write()
    l.delete(index)

@contract(name='seq(str)')
def event_list_insert(name, index, value, **kwargs):
    name = list(name)
    arguments = dict(name=name, index=index, value=value)
    return event_make(event_name=DataEvents.list_insert, arguments=arguments, **kwargs)

def event_list_insert_interpret(view, name, index, value):
    l = get_the_list(view, name)
    l.check_can_write()
    l.insert(index, value)

@contract(name='seq(str)')
def event_list_remove(name, value, **kwargs):
    name = list(name)
    arguments = dict(name=name, value=value)
    return event_make(event_name=DataEvents.list_delete, arguments=arguments, **kwargs)

def event_list_remove_interpret(view, name, value):
    l = get_the_list(view, name)
    l.check_can_write()
    l.remove(value)

@contract(name='seq(str)')
def event_dict_setitem(name, key, value, **kwargs):
    name = list(name)
    arguments = dict(name=name, key=key, value=value)
    e = event_make(event_name=DataEvents.dict_setitem,  arguments=arguments, **kwargs)
    return e

def event_dict_setitem_interpret(view, name, key, value):
    from mcdp_hdb.memdataview import ViewHash0
    v = get_view_node(view, name)
    check_isinstance(v, ViewHash0)
    # permissions
    v.check_can_write()
    # validate
    v._schema.prototype.validate(value)
    v._data[key] = value
    
def event_dict_delitem(name, key, **kwargs):
    name = list(name)
    arguments = dict(name=name, key=key)
    return event_make(event_name=DataEvents.dict_delitem, arguments=arguments, **kwargs)

def event_dict_delitem_interpret(view, name, key):
    from mcdp_hdb.memdataview import ViewHash0
    v = get_view_node(view, name)
    check_isinstance(v, ViewHash0)
    # permissions
    v.check_can_write()
    del v._data[key] 

def event_dict_rename(name, key, key2, **kwargs):
    name = list(name)
    arguments = dict(name=name, key=key, key2=key2)
    return event_make(event_name=DataEvents.dict_rename,  arguments=arguments, **kwargs)

def event_dict_rename_interpret(view, name, key, key2):
    from mcdp_hdb.memdataview import ViewHash0
    v = get_view_node(view, name)
    check_isinstance(v, ViewHash0)
    # permissions
    v.check_can_write()
    from mcdp_hdb.memdataview import InvalidOperation
    if not key in v._data:
        msg = ('Cannot rename key %r to %r if it does not exist in %s.' % 
               (key, key2, format_list(v._data)))
        raise InvalidOperation(msg)
    v._data[key2] = v._data.pop(key)

@contract(_id=str, event_name=str)
def event_make(_id, event_name, who, arguments):
    assert event_name in DataEvents.all_events
    d = OrderedDict()
    d['id'] = _id
    d['who'] = who
    d['operation'] = event_name
    d['arguments'] = arguments
    return d

def event_intepret(view_manager, db0, event):
    if event['who'] is not None:
        actor = event['who']['actor']
        principals = event['who']['principals']
        view = view_manager.view(db0, actor=actor, principals=principals)
    else:
        view = view_manager.view(db0)
    event_interpret_(view, event)
    view._schema.validate(db0) # XXX

@contract(view=ViewBase, event=dict, returns=None)
def event_interpret_(view, event):
    fs = {
        DataEvents.leaf_set: event_leaf_set_interpret,
        DataEvents.struct_set: event_struct_set_interpret,
        DataEvents.increment: event_increment_interpret,
        DataEvents.list_append: event_list_append_interpret,
        DataEvents.list_remove: event_list_remove_interpret,
        DataEvents.list_delete: event_list_delete_interpret,
        DataEvents.list_insert: event_list_insert_interpret,
        DataEvents.list_setitem: event_list_setitem_interpret,
        
        DataEvents.set_add: event_set_add_interpret,
        DataEvents.set_remove: event_set_remove_interpret,
        DataEvents.dict_setitem: event_dict_setitem_interpret,
        DataEvents.dict_delitem: event_dict_delitem_interpret,
        DataEvents.dict_rename: event_dict_rename_interpret,
    }
    ename = event['operation']
    intf = fs[ename]
    arguments = event['arguments']
    try:
        intf(view=view, **arguments)
    except Exception as e:
        msg = 'Could not complete the replay of this event: \n'
        msg += indent(yaml_dump(event), 'event: ')
        
        raise_wrapped(InvalidOperation, e, msg)


def replay_events(view_manager, db0, events):
    db0 = deepcopy(db0)
    for event in events:
        event_intepret(view_manager, db0, event)
        msg = '\nAfter playing event:\n'
        msg += indent(yaml_dump(event), '   event: ')
        msg += '\nthe DB is:\n'
        msg += indent(yaml_dump(db0), '   db: ')
        logger.debug(msg)
    return db0
