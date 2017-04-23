from collections import namedtuple
from copy import deepcopy

from contracts import contract
from contracts.utils import raise_wrapped, indent, check_isinstance

from mcdp import logger
from mcdp_utils_misc import format_list, yaml_dump

from .disk_events import disk_event_disk_event_group
from .disk_events import disk_event_file_modify, disk_event_dir_delete, disk_event_file_create, disk_event_dir_create, disk_event_file_delete, disk_event_file_rename, disk_event_dir_rename
from .disk_map import HintFileYAML
from .disk_struct import ProxyDirectory, ProxyFile
from .hints import HintDir
from .memdata_events import DataEvents, get_view_node
from .memdataview import InvalidOperation
from .memdataview_manager import ViewManager
from .schema import SchemaHash, SchemaContext, SchemaList, SchemaBase
from mcdp_hdb.memdata_events import event_list_append, event_interpret_
from mcdp.exceptions import DPInternalError
from mcdp_hdb.memdataview import ViewBase



@contract(returns='list(dict)', schema=SchemaBase)
def disk_events_from_data_event(disk_map, schema, data_rep, data_event):
    viewmanager = ViewManager(schema) 
    view = viewmanager.create_view_instance(schema, data_rep)
    view._schema.validate(data_rep  )

    # As a preliminary check, we check whether this change happened 
    # inside a YAML representation.
    inside_yaml, name_of_yaml = change_was_inside_YAML(view=view, data_event=data_event, disk_map=disk_map)
    # If yes, then the result will be a file_modify event for the YAML file.
    if inside_yaml:
        return disk_events_from_data_event_inside_yaml(disk_map, data_event, view, p=name_of_yaml)
    
    handlers = {
        DataEvents.leaf_set: disk_events_from_leaf_set,
        DataEvents.dict_setitem: disk_events_from_dict_setitem,
        DataEvents.dict_delitem: disk_events_from_dict_delitem,
        DataEvents.dict_rename: disk_events_from_dict_rename,
        DataEvents.list_append: disk_events_from_list_append,
        DataEvents.list_delete: disk_events_from_list_delete,
        DataEvents.list_insert: disk_events_from_list_insert,
        DataEvents.list_remove: disk_events_from_list_remove,
    }
    operation = data_event['operation']
    if operation in handlers:
        f = handlers[operation]
        arguments = data_event['arguments']
        who = data_event['who']
        try:
            evs = f(disk_map=disk_map, view=view, _id='tmp-id', who=who, **arguments)
            _id = data_event['id']
            for i, ev in enumerate(evs):
                ev['id'] = _id + '-translated-%d' % i
            return evs 
        except Exception as e:
            msg = 'Could not succesfully translate using %r:' % f.__name__
            msg += '\n' + 'Schema: ' + '\n' + indent(schema, ' schema ')
            msg += '\n' + 'Data event: ' + '\n' + indent(yaml_dump(data_event), ' data_event ')
            raise_wrapped(Exception, e, msg)
    else:
        raise NotImplementedError(operation)

@contract(view=ViewBase, p='seq(str)', schema=SchemaBase)
def disk_events_from_data_event_inside_yaml(disk_map, data_event, view, p):
    # we now know that we are inside a YAML
    # Just checking though:
    p_schema = view._schema.get_descendant(p)
    p_hint = disk_map.get_hint(p_schema)
    assert isinstance(p_hint, HintFileYAML)
    
    # make the data_event relative
    relative_data_event = deepcopy(data_event)
    name = data_event['arguments']['name']
    relative_name = name[len(p):]
    relative_data_event['arguments']['name'] = relative_name
    
    parent_of_yaml = p[:-1]
    parent_of_yaml_schema = view._schema.get_descendant(parent_of_yaml)
    parent_of_yaml_hint = disk_map.get_hint(parent_of_yaml_schema)
    dirname = disk_map.dirname_from_data_url_(view._schema, parent_of_yaml)
    filename = parent_of_yaml_hint.filename_for_key(p[-1])
    
    # this is the current data to go in yaml
    relative_data_view = view.get_descendant(p)
    # make a copy of the data
    relative_data_view._data = deepcopy(relative_data_view._data)
    # now make the change by applying the relative_data_event
    relative_data_view.set_root()
    event_interpret_(relative_data_view, relative_data_event)
    # now create the YAML file
    fh = disk_map.create_hierarchy_(p_schema, relative_data_view._data)
    check_isinstance(fh, ProxyFile)
    contents = fh.contents
    _id = relative_data_event['id'] + '-tran'
    who = relative_data_event['who']
    disk_event = disk_event_file_modify(_id, who, dirname, filename, contents)
    return [disk_event]


@contract(returns='tuple(bool, *)')
def change_was_inside_YAML(view, data_event, disk_map):
    ''' Checks whether the change was inside a YAML file. '''
    if not 'name' in data_event['arguments']:
        msg = 'Expected all events to have a "name" argument.'
        raise DPInternalError(msg)
    name = data_event['arguments']["name"]
    
    for i in range(len(name)+1):
        p = name[:i]
        p_schema = view._schema.get_descendant(p)
        p_hint = disk_map.get_hint(p_schema)
        if isinstance(p_hint, HintFileYAML):
            return True, p
    else:
        return False, None

    
def disk_events_from_leaf_set_in_yaml(disk_map, view, _id, who, name, leaf, value, parent_with_yaml):
    p_schema = view._schema.get_descendant(parent_with_yaml)
    p_hint = disk_map.get_hint(p_schema)
    check_isinstance(p_hint, HintFileYAML)
    
    relative_url = name[len(parent_with_yaml):]
    msg = 'Inside yaml:  set %s.%s = %s' % (relative_url, leaf, value)
    logger.info(msg)
    
    parent_of_yaml = parent_with_yaml[:-1]
    parent_of_yaml_schema = view._schema.get_descendant(parent_of_yaml)
    parent_of_yaml_hint = disk_map.get_hint(parent_of_yaml_schema)
    dirname = disk_map.dirname_from_data_url_(view._schema, parent_of_yaml)
    filename = parent_of_yaml_hint.filename_for_key(parent_with_yaml[-1])
    
    # this is the current data to go in yaml
    data_view = get_view_node(view, parent_with_yaml)
    # make a copy
    data_view._data = deepcopy(data_view._data)
    # now make the change
    _data= get_view_node(data_view, relative_url)._data
    _data[leaf] = value
    fh = disk_map.create_hierarchy_(p_schema, data_view._data)
    check_isinstance(fh, ProxyFile)
    contents = fh.contents
    disk_event = disk_event_file_modify(_id, who, dirname, filename, contents)
    return [disk_event]
 

def disk_events_from_leaf_set(disk_map, view, _id, who, name, leaf, value):
    # check if it is contained in any dir that has HintFileYAML
#     logger.debug('leaf_set %s . %s = %s' % (parent, name, value))
    for i in range(len(name)+1):
        p = name[:i]
        p_schema = view._schema.get_descendant(p)
        p_hint = disk_map.get_hint(p_schema)
        if isinstance(p_hint, HintFileYAML):
            return disk_events_from_leaf_set_in_yaml(disk_map, view, _id, who, name, leaf, value, p)
    
    view_parent = get_view_node(view, name)
    schema_parent = view_parent._schema
    check_isinstance(schema_parent, SchemaContext)
    view_child = view_parent.child(leaf)
    schema_child = view_child._schema
    
    hint = disk_map.get_hint(schema_parent)
    if isinstance(hint, HintDir):
        sub = disk_map.create_hierarchy_(schema_child, value)
        dirname = disk_map.dirname_from_data_url_(view._schema, name)
        
        if isinstance(sub, ProxyFile):
            filename = leaf
            contents = sub.contents
            disk_event = disk_event_file_modify(_id, who, dirname, filename, contents)
            return [disk_event]
        else: 
            assert False 
    elif isinstance(hint, HintFileYAML):
        sub = disk_map.create_hierarchy_(schema_child, value)
        check_isinstance(sub, ProxyFile)
        dirname = disk_map.dirname_from_data_url_(view._schema, name)
        filename = leaf
        contents = sub.contents
        disk_event = disk_event_file_modify(_id, who, dirname, filename, contents)
        return [disk_event]
    else:
        raise NotImplementedError(hint)



PP = namedtuple('PP', 'prefix schema hint parent_hint parent_schema')
def iterate_prefix(disk_map, view, name):
    n = len(name)
    for i in range(n):
        prefix = name[:i]
        schema = view._schema.get_descendant(prefix)
        hint = disk_map.get_hint(schema)
        parent_schema = view._schema.get_descendant(prefix[:-1])
        parent_hint = disk_map.get_hint(parent_schema)
        yield PP(schema=schema, hint=hint, prefix=prefix, parent_hint=parent_hint, parent_schema=parent_schema)

def is_inside_yaml(disk_map, view, name):
    ''' Checks if we are inside a YAML file '''
    for pp in iterate_prefix(disk_map, view, name):
        if isinstance(pp.hint, HintFileYAML):
            return pp
    else:
        return None

def disk_events_from_list_append(disk_map, view, _id, who, name, value):
    logger.debug('list append to %s for value %s' % (name, value))
    pp = is_inside_yaml(disk_map, view, name)
    if pp is not None:
        logger.debug('we are inside YAML --  append to %s for value %s' % (name, value))
        # copy the entire data:
        logger.debug('pp.prefix = %s' % str(pp.prefix))
        data_relative_to_yaml = name[len(pp.prefix):]
        logger.debug('relative to prefix: %s' % data_relative_to_yaml)
        data_at_yaml = view.get_descendant(pp.prefix)
        data_at_yaml_copy = data_at_yaml.deepcopy()
        data_at_yaml_copy.set_root()
#         logger.debug('data at YAML:\n%s' % yaml_dump(data_at_yaml_copy._data))
        # apply the event
        name2 = name[len(pp.prefix):]
        event2 = event_list_append(name=name2, value=value, _id='None', who=None)
        event_interpret_(data_at_yaml_copy, event2)
        fh = disk_map.create_hierarchy_(pp.schema, data_at_yaml_copy._data)
        check_isinstance(fh, ProxyFile)
        contents = fh.contents
        dirname = disk_map.dirname_from_data_url_(view._schema, pp.prefix[:-1])
        
        filename = pp.parent_hint.filename_for_key(pp.prefix[-1]) 
        disk_event = disk_event_file_modify(_id, who, dirname, filename, contents)
        logger.info('name %s -> dirname = %s, filename = %s' % (name, dirname, filename))
        return [disk_event]
        
        
        
    # First, check if we are inside a YAML file
    
    view_parent = get_view_node(view, name)
    schema_parent = view_parent._schema
    check_isinstance(schema_parent, SchemaList)
    hint = disk_map.get_hint(schema_parent)
    if isinstance(hint, HintDir):
        sub = disk_map.create_hierarchy_(schema_parent.prototype, value)
        dirname = disk_map.dirname_from_data_url_(view._schema, name)
        next_index = len(view_parent._data)
        filename = hint.filename_for_key(str(next_index))
        if isinstance(sub, ProxyFile):
            contents = sub.contents
            disk_event = disk_event_file_create(_id, who, dirname, filename, contents)
            return [disk_event]
        else: 
            assert False 

    else:
        raise NotImplementedError(hint)

def disk_events_from_list_insert(disk_map, view, _id, who, name, index, value):
    view_parent = get_view_node(view, name)
    schema_parent = view_parent._schema
    check_isinstance(schema_parent, SchemaList)
    hint = disk_map.get_hint(schema_parent)
    length = len(view_parent._data)
#     logger.debug('list:\n%s' % yaml_dump(view_parent._data))
#     logger.debug('inserting at index %d value %s' % (index, value))
    if isinstance(hint, HintDir):
        # TODO: what about it is not a list of files, but directories?
#         dirname = disk_map.dirname_from_data_url(name)
        dirname = disk_map.dirname_from_data_url_(view._schema, name)
        events = []
        # first rename everything to i+1
        to_rename = []
        for i in range(index, length):
            to_rename.append((i, i+1))
#         logger.debug('to rename: %s' % to_rename)
        for i in reversed(range(index, length)):
            i2 = i + 1
            filename1 = hint.filename_for_key(str(i))
            filename2 = hint.filename_for_key(str(i2))
            dr = disk_event_file_rename(_id, who, dirname, filename1, filename2) 
            events.append(dr)
#         logger.debug('Renaming events:\n %s' % yaml_dump(events))
        # now create the file
        sub = disk_map.create_hierarchy_(schema_parent.prototype, value)
        if isinstance(sub, ProxyFile):
            filename = hint.filename_for_key(str(index))
            creation = disk_event_file_create(_id, who, dirname, filename, sub.contents)
            events.append(creation)
        else:
            raise NotImplementedError()
        
        e = disk_event_disk_event_group(_id, who, events)
        return [e]
    else:
        raise NotImplementedError(hint)
    
def disk_events_from_list_delete(disk_map, view, _id, who, name, index):
    view_parent = view.get_descendant(name)
    schema_parent = view_parent._schema
    check_isinstance(schema_parent, SchemaList)
    hint = disk_map.get_hint(schema_parent)
    length = len(view_parent._data)
    if isinstance(hint, HintDir):
        # TODO: what about it is not a list of files, but directories? 
        dirname = disk_map.dirname_from_data_url_(view._schema, name)
        filename = hint.filename_for_key(str(index))
        disk_event = disk_event_file_delete(_id, who, dirname, filename)
        events = [disk_event]
        for i in range(index+1, length):
            i2 = i - 1
            filename1 = hint.filename_for_key(str(i))
            filename2 = hint.filename_for_key(str(i2))
            dr = disk_event_file_rename(_id, who, dirname, filename1, filename2) 
            events.append(dr)
        e = disk_event_disk_event_group(_id, who, events)
        return [e]
    else:
        raise NotImplementedError(hint)

def disk_events_from_list_remove(disk_map, view, _id, who, name, value):
    view_parent = view.get_descendant(name)
    data = view_parent._data
    for index, v in enumerate(data):
        if v == value:
            return disk_events_from_list_delete(disk_map, view, _id, who, name, index)
    msg = 'There is no value %s in the list.' % value
    msg += '\n values: %s' % format_list(data) 
    raise InvalidOperation(msg)

def disk_events_from_dict_setitem(disk_map, view, _id, who, name, key, value):
    view_parent = get_view_node(view, name)
    schema_parent = view_parent._schema
    check_isinstance(schema_parent, SchemaHash)
    prototype = schema_parent.prototype
    
    hint = disk_map.get_hint(schema_parent)
    if isinstance(hint, HintDir):
        d = disk_map.create_hierarchy_(prototype, value)
        its_name = hint.filename_for_key(key)
        dirname = disk_map.dirname_from_data_url_(view._schema, name)
        
        if isinstance(d, ProxyFile):
            contents = d.contents
            filename = its_name
            existed = key in view_parent._data
            if existed: 
                disk_event = disk_event_file_modify(_id, who, 
                                                    dirname=dirname, 
                                                    name=filename, 
                                                    contents=contents)
            else:
                disk_event = disk_event_file_create(_id, who, 
                                                    dirname=dirname, 
                                                    name=filename, 
                                                    contents=contents)
            return [disk_event]
        elif isinstance(d, ProxyDirectory):
            events = []
            # delete directory only if it exists already
            if key in view_parent._data:
                events.append(disk_event_dir_delete(_id, who, dirname=list(dirname), name=its_name))
            events.extend(disk_events_for_creating(_id, who, d, tuple(dirname) + (its_name,)))
            
            e = disk_event_disk_event_group(_id, who, events=events)
            return [e]
        else:
            assert False 
    else:
        raise NotImplementedError(hint)

def disk_events_from_dict_delitem(disk_map, view, _id, who, name, key):
    view_parent = get_view_node(view, name)
    schema_parent = view_parent._schema
    check_isinstance(schema_parent, SchemaHash)
    prototype = schema_parent.prototype
    
    hint = disk_map.get_hint(schema_parent)
    if isinstance(hint, HintDir):
        dirname = disk_map.dirname_from_data_url_(view._schema, name) 
        its_name = hint.filename_for_key(key)
        # I just need to find out whether it would be ProxyDir or ProxyFile
        value = view_parent._data[key]
        d = disk_map.create_hierarchy_(prototype, value)
        if isinstance(d, ProxyFile):
            disk_event = disk_event_file_delete(_id, who, 
                                                dirname=dirname, 
                                                name=its_name)
            return [disk_event]
        elif isinstance(d, ProxyDirectory):
            disk_event = disk_event_dir_delete(_id, who, 
                                                dirname=dirname, 
                                                name=its_name)
            return [disk_event]
        else:
            assert False 
    else:
        raise NotImplementedError(hint)
    
def disk_events_from_dict_rename(disk_map, view, _id, who, name, key, key2):
    view_parent = get_view_node(view, name)
    schema_parent = view_parent._schema
    check_isinstance(schema_parent, SchemaHash)
    prototype = schema_parent.prototype
    
    hint = disk_map.get_hint(schema_parent)
    if isinstance(hint, HintDir):
        dirname = disk_map.dirname_from_data_url_(view._schema, name)
        its_name = hint.filename_for_key(key)
        its_name2 = hint.filename_for_key(key2)
        # I just need to find out whether it would be ProxyDir or ProxyFile
        if not key in view_parent._data:
            msg = 'Cannot rename key %r that does not exist in %s.'  % (key, format_list(view_parent._data))
            raise InvalidOperation(msg)
        value = view_parent._data[key]
        d = disk_map.create_hierarchy_(prototype, value)
        if isinstance(d, ProxyFile):
            disk_event = disk_event_file_rename(_id, who, 
                                                dirname=dirname, 
                                                name=its_name,
                                                name2=its_name2)
            return [disk_event]
        elif isinstance(d, ProxyDirectory):
            disk_event = disk_event_dir_rename(_id, who, 
                                                dirname=dirname, 
                                                name=its_name,
                                                name2=its_name2)
            return [disk_event]
        else:
            assert False 
    else:
        raise NotImplementedError(hint)
    
    
@contract(prefix='tuple,seq(str)', d=ProxyDirectory)
def disk_events_for_creating(_id, who, d, prefix):
    # create this dir
    yield disk_event_dir_create(_id, who, dirname=prefix[:-1], name=prefix[-1])
    for fn, f in d.get_files().items():
        yield disk_event_file_create(_id, who, 
                                     dirname=list(prefix), 
                                     name=fn, 
                                     contents=f.contents)
    for d2_name, d2 in d.get_directories().items():
        prefix2 = prefix + (d2_name,)
        for _ in disk_events_for_creating(_id, who, d2, prefix2):
            yield _
