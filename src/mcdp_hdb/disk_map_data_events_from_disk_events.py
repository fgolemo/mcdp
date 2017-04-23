from copy import deepcopy

from contracts import contract, describe_value
from contracts.utils import raise_wrapped, indent

from mcdp import logger
from mcdp_utils_misc import yaml_dump

from .disk_events import DiskEvents
from .disk_events import disk_event_interpret
from .disk_map import DiskMap
from .disk_struct import ProxyFile
from .hints import HintDir, HintFileYAML
from .memdata_diff import data_diff
from .memdata_events import event_leaf_set, event_dict_setitem, event_dict_delitem, event_dict_rename
from .memdata_events import event_list_append, event_list_delete, event_list_insert
from .memdata_utils import assert_data_events_consistent
from .schema import SchemaHash, SchemaContext, SchemaList, SchemaBase
from .memdata_events import  event_add_prefix


@contract(returns='tuple(list(dict), list(dict))')
def data_events_from_disk_event_queue(disk_map, schema, disk_rep, disk_events_queue):

    handlers = {
        DiskEvents.disk_event_group: data_events_from_disk_event_group,
        DiskEvents.dir_create: data_events_from_dir_create,
        DiskEvents.dir_rename: data_events_from_dir_rename,
        DiskEvents.dir_delete: data_events_from_dir_delete,
        DiskEvents.file_create: data_events_from_file_create,
        DiskEvents.file_modify: data_events_from_file_modify,
        DiskEvents.file_delete: data_events_from_file_delete,
        DiskEvents.file_rename: data_events_from_file_rename,
    } 
    disk_event_consumed = []
    disk_event = disk_events_queue.pop(0)
    disk_event_consumed.append(disk_event)
    operation = disk_event['operation']
    if operation in handlers:
        f = handlers[operation]
        arguments = disk_event['arguments']
        who = disk_event['who']
        _id = disk_event['id']
        try:
            res= f(schema=schema, 
                   disk_map=disk_map, 
                   disk_rep=disk_rep, 
                   disk_events_queue=disk_events_queue,
                               _id='tmp-id', who=who, **arguments)
            if not isinstance(res, tuple) or len(res) != 2:
                msg = 'Expected %r to return a tuple of len 2, got %s' % (f, describe_value(res))
                raise Exception(msg)
            evs, consumed = res
            for i, ev in enumerate(evs):
                ev['id'] = _id + '-translated_inverse-%d' % i
            disk_event_consumed.extend(consumed)
            return evs, disk_event_consumed 
        except Exception as e:
            msg = 'Could not succesfully translate using %r:' % f.__name__
            msg += '\n' + 'Schema: ' + '\n' + indent(schema, ' schema ')
            msg += '\n' + 'Current disk representation: ' + '\n' + indent(disk_rep.tree(), ' tree ')
            msg += '\n' + 'Disk event: ' + '\n' + indent(yaml_dump(disk_event), ' disk_event ')
            
            raise_wrapped(Exception, e, msg, arguments=arguments)
    else:
        raise NotImplementedError(operation)
    
    
def data_events_from_disk_event_group(schema, disk_map, disk_rep, disk_events_queue, _id, who, events):  # @UnusedVariable
    if not events:
        msg = 'Group with no events?'
        raise ValueError(msg)
    es, _consumed = data_events_from_disk_event_queue(disk_map, schema, disk_rep, list(events))
    return es, []
    
def data_events_from_dir_create(schema, disk_map, disk_rep, disk_events_queue, _id, who, dirname, name):
    parent, schema_parent, hint = get_parent_data(schema, disk_map, dirname, name)    

    if isinstance(schema_parent, SchemaHash):
        if isinstance(hint, HintDir):
            key = hint.key_from_filename(name)
            schema_child = schema_parent.prototype
            # get more events that create file in this directory
            related_disk_events = get_disk_events_for_dir(dirname, disk_events_queue)
            
            disk_rep = deepcopy(disk_rep)
            disk_rep.get_descendant(dirname).dir_create(name)
            for re in related_disk_events:
                disk_event_interpret(disk_rep, re)
            disk_rep_child = disk_rep.get_descendant(dirname + (name,))
            value = disk_map.interpret_hierarchy_(schema_child, disk_rep_child)

            e = event_dict_setitem(name=parent, key=key, value=value, _id=_id, who=who)
            return [e], related_disk_events
    msg = 'Not implemented\n %s\nwith\n%s' % (schema_parent, hint)
    raise NotImplementedError(msg)

def get_disk_events_for_dir(dirname, disk_events_queue):
    consumed = []
    while disk_events_queue:
        e = disk_events_queue[0]
        accept = e['operation'] in [DiskEvents.dir_create, DiskEvents.file_create]
        if not accept:
            break
        accept = a_is_prefix_of_b(dirname, e['arguments']['dirname'])
        if accept:
            disk_events_queue.pop(0)
            consumed.append(e)
        else: 
            break
    return consumed

def a_is_prefix_of_b(l1, l2):
    if len(l2) < len(l1): 
        return False
    for a, b in zip(l1, l2):
        if a != b:
            return False
    return True
    
def data_events_from_dir_rename(schema, disk_map, disk_rep, disk_events_queue, _id, who, dirname, name, name2):  # @UnusedVariable
    parent, schema_parent, hint = get_parent_data(schema, disk_map, dirname, name)
    
    disk_rep = deepcopy(disk_rep)

    if isinstance(schema_parent, SchemaHash):
        if isinstance(hint, HintDir):
            key = hint.key_from_filename(name)
            key2 = hint.key_from_filename(name2)
            e = event_dict_rename(name=parent, key=key, key2=key2, _id=_id, who=who)
            return [e], []
    msg = 'Not implemented %s with %s' % (schema_parent, hint)
    raise NotImplementedError(msg)

def data_events_from_dir_delete(schema, disk_map, disk_rep, disk_events_queue, _id, who, dirname, name):  # @UnusedVariable
    parent, schema_parent, hint = get_parent_data(schema, disk_map, dirname, name)
    
    disk_rep = deepcopy(disk_rep) 
    if isinstance(schema_parent, SchemaHash):
        if isinstance(hint, HintDir):
            key = hint.key_from_filename(name)
            e = event_dict_delitem(name=parent, key=key, _id=_id, who=who)
            return [e], []
    msg = 'Not implemented %s with %s' % (schema_parent, hint)
    raise NotImplementedError(msg)

def data_events_from_file_create(schema, disk_map, disk_rep, disk_events_queue, _id, who, dirname, name, contents):  # @UnusedVariable
    parent, schema_parent, hint = get_parent_data(schema, disk_map, dirname, name)
    if isinstance(schema_parent, SchemaHash):
        if isinstance(hint, HintDir):
            # creating a file
            #logger.debug('data_events_from_file_create dirname %r name %r contents = %r' % (dirname, name, contents))
            key = hint.key_from_filename(name)
            # the interesting case is when it is yaml file
            prototype = schema_parent.prototype 
            data = disk_map.interpret_hierarchy_(prototype, ProxyFile(contents))
            e = event_dict_setitem(name=parent, key=key, value=data, _id=_id, who=who)
            events = [e]
            consumed = [] 
            return events, consumed
            
    if isinstance(schema_parent, SchemaList):
        if isinstance(hint, HintDir):
            # creating a file
            # logger.debug('data_events_from_file_create dirname %r name %r contents = %r' % (dirname, name, contents))
               
            key = hint.key_from_filename(name)
            # XXX: not used?
            # index = int(key)
            
            # if it is the last, then it is an append
            is_last = True # XXX
            if is_last:
                prototype = schema_parent.prototype
                data = disk_map.interpret_hierarchy_(prototype, ProxyFile(contents))
                e = event_list_append(name=parent, value=data, _id=_id, who=who)    
                events = [e]
                consumed = [] 
                return events, consumed

    msg = 'Not implemented %s with %s' % (type(schema_parent), hint)
    raise NotImplementedError(msg)

def data_events_from_file_modify(schema, disk_map, disk_rep, disk_events_queue, _id, who, dirname, name, contents):  # @UnusedVariable
    parent, schema_parent, hint = get_parent_data(schema, disk_map, dirname, name)
    if isinstance(schema_parent, SchemaContext):
        if isinstance(hint, HintDir):
            key = hint.key_from_filename(name)
            schema_child = schema_parent.get_descendant((key,))
            value = disk_map.interpret_hierarchy_(schema_child, ProxyFile(contents))
            e = event_leaf_set(name=parent, leaf=key, value=value, _id=_id, who=who)
            consumed = []
            return [e], consumed

    logger.debug('dirname %r -> parent %r' % (dirname, parent))
        
    if isinstance(schema_parent, SchemaHash):
        if isinstance(hint, HintDir):
            # modified a file
            logger.debug('data_events_from_file_modify dirname %r name %r contents = %r' % (dirname, name, contents))
            logger.debug('hint %r' % hint)

            key = hint.key_from_filename(name)         
            # the interesting case is when it is yaml file
            prototype = schema_parent.prototype
            logger.debug('key %r' % key)
            logger.debug('prototype %r' % prototype)
            is_yaml = isinstance(disk_map.get_hint(prototype), HintFileYAML)
            if is_yaml:
                # let's get the new yaml file contents
                data2 = disk_map.interpret_hierarchy_(prototype, ProxyFile(contents))
                # now take the difference with respect to the current data
                current_file = disk_rep.get_descendant(dirname)[name]
                data1 = disk_map.interpret_hierarchy_(prototype, current_file)
                diff = data_diff(prototype, data1, data2)
                assert_data_events_consistent(prototype, data1, diff, data2) 
                
#                 def add_prefix(e):
#                     e2 = deepcopy(e) 
#                     if 'parent' in e2['arguments']:
#                         prev = e2['arguments']['parent']
#                         
#                         logger.info('parent %s key %s prev %s' % (parent, key, prev))
#                         new = parent + (key,) + prev
#                         logger.info('add_prefix %s %s' % (prev, new))
#                         e2['arguments']['parent'] = new 
#                     return e2
                
                prefix = parent + (key,)
                diff2 = [event_add_prefix(prefix, d) for d in diff]
                logger.info('diff2:\n'+indent(diff2, '> ')) 
                return diff2, [] 
            else: 
                # if a file is modified, it means that it was a leaf node
                pass 
                
                
                
    msg = 'Not implemented %s with %s' % (type(schema_parent), hint)
    raise NotImplementedError(msg)

@contract(schema=SchemaBase, disk_map=DiskMap, name=str)
def get_parent_data(schema, disk_map, dirname, name):
    '''
        returns parent, schema_parent, hint_parent 
    '''
    name_both = disk_map.data_url_from_dirname_(schema, tuple(dirname) + (name,))
    parent = name_both[:-1]
    schema_parent = schema.get_descendant(parent)
    hint = disk_map.get_hint(schema_parent)
    return parent, schema_parent, hint
    
def data_events_from_file_rename(schema, disk_map, disk_rep, disk_events_queue, _id, who, dirname, name, name2):  # @UnusedVariable
    parent, schema_parent, hint = get_parent_data(schema, disk_map, dirname, name)
    
    if isinstance(schema_parent, SchemaHash):
        if isinstance(hint, HintDir):
            key = hint.key_from_filename(name)
            key2 = hint.key_from_filename(name2)                        
            e = event_dict_rename(name=parent, key=key, key2=key2, _id=_id, who=who)
            return [e],[]

    if isinstance(schema_parent, SchemaList):
        if isinstance(hint, HintDir):
            index = int(hint.key_from_filename(name))
            index2 = int(hint.key_from_filename(name2))
            logger.debug('renaming %s to %s' % (index, index2))
            # this is now an operation with insert index
            logger.debug('Next events:\n%s'%yaml_dump(disk_events_queue))
            consumed = []
            while disk_events_queue:
                nexte = disk_events_queue.pop(0)
                consumed.append(nexte)
                if nexte['operation'] == 'file_create':
                    assert nexte['arguments']['name'] == name
                    contents = nexte['arguments']['contents']
                    value = disk_map.interpret_hierarchy_(schema_parent.prototype, ProxyFile(contents))
                    e = event_list_insert(_id=_id, who=who, name=parent, index=index, value=value)
                                                      
                    return [e], consumed
            msg = 'I was waiting for a file_create_event'
            raise Exception(msg)
            
    msg = 'Not implemented %s with %s' % (type(schema_parent), hint)
    raise NotImplementedError(msg)

@contract(schema=SchemaBase)
def data_events_from_file_delete(schema, disk_map, disk_rep, disk_events_queue, _id, who, dirname, name):  # @UnusedVariable
    parent, schema_parent, hint = get_parent_data(schema, disk_map, dirname, name)

    if isinstance(schema_parent, SchemaHash):
        if isinstance(hint, HintDir):
            key = hint.key_from_filename(name)                     
            e = event_dict_delitem(name=parent, key=key, _id=_id, who=who)
            return [e],[]
    
    if isinstance(schema_parent, SchemaList):
        if isinstance(hint, HintDir):
            index = int(hint.key_from_filename(name))                     
            e = event_list_delete(name=parent, index=index, _id=_id, who=who)
            return [e],[]

    msg = 'Not implemented %s with %s' % (type(schema_parent), hint)
    raise NotImplementedError(msg)

