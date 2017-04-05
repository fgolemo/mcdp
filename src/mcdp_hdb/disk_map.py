from copy import deepcopy
import copy
import os
import sys

from contracts import contract, describe_value
from contracts.utils import raise_desc, raise_wrapped, indent, check_isinstance

from mcdp import logger
from mcdp_utils_misc import format_list, yaml_dump, yaml_load

from .disk_events import DiskEvents, disk_event_file_modify, disk_event_dir_delete, disk_event_file_create, disk_event_dir_create, disk_event_file_delete, disk_event_file_rename, disk_event_dir_rename
from .disk_events import disk_event_interpret
from .disk_struct import ProxyDirectory, ProxyFile
from .memdata_diff import data_diff
from .memdata_events import DataEvents, get_view_node,  event_leaf_set, event_dict_setitem, event_dict_delitem, event_dict_rename
from .memdata_utils import assert_data_events_consistent
from .memdataview import InvalidOperation
from .memdataview_manager import ViewManager
from .schema import SchemaHash, SchemaString, SchemaContext, SchemaList, SchemaBytes, NOT_PASSED, SchemaDate, SchemaBase


# from mcdp_library_tests.create_mockups import mockup_flatten
class IncorrectFormat(Exception):
    pass

def raise_incorrect_format(msg, schema, data):
    msg2 = 'Incorrect format:\n'
    msg2 += indent(msg, '  ') 
    if isinstance(data, str):
        datas = data
    else:
        datas = yaml_dump(data).encode('utf8')
    MAX = 512
    if len(datas) > MAX:
        datas = datas[:MAX] + ' [truncated]'
    if False:
        msg2 += '\nData:\n'
        msg2 += indent(datas, '  ')
    #     msg2 += 'repr: '+ datas.__repr__()
    raise_desc(IncorrectFormat, msg2, schema=schema)
 
class HintExtensions(object):
    
    def __init__(self, extensions):
        self.extensions = extensions

    def __repr__(self):
        return 'HintExtensions(%r)' % self.extensions
     
class HintFile(object):
     
    def __init__(self):
        pass
 
    def __repr__(self):
        return 'HintFile()'  
            
class HintDir(object):
    
    def __init__(self, pattern='%', translations=None):
        self.pattern = pattern
        if translations is None:
            translations = {}
        self.translations = translations
 
    def __repr__(self):
        return 'HintDir(%r, %r)' % (self.pattern, self.translations)
    
    def filename_for_key(self, key):
        if key in self.translations:
            return self.translations[key]
        else:
            return self.pattern.replace('%', key)

    def key_from_filename(self, filename):
        pattern = self.pattern
        if not '%' in pattern:
            msg = 'Cannot get key from filename.'
            raise_desc(IncorrectFormat, msg, pattern=pattern, filename=filename)
            
        if pattern.startswith('%'):
            key = filename.replace(pattern.replace('%', ''), '')
            
            filename2 = pattern.replace('%', key)
            if filename2 != filename:
                msg = 'Filename "%s" does not follow pattern "%s".' % (filename, pattern)
                raise NotKey(msg)
            return key
        else:
            raise NotImplementedError(pattern)
        
class HintFileYAML(object):
    def __init__(self):
        pass
        
    def __repr__(self):
        return 'HintFileYAML()'
        
class DiskMap(object):

    @contract(schema=SchemaBase)
    def __init__(self, schema):
        self.hints = {}
        self.schema = schema 

    def get_hint(self, s):
        check_isinstance(s, SchemaBase) 
        if s in self.hints:
            return self.hints[s]
        if isinstance(s, (SchemaString, SchemaBytes, SchemaDate)):
            return HintFile()
        if isinstance(s, SchemaHash):
            return HintDir()
        if isinstance(s, SchemaContext):
            return HintDir()
        if isinstance(s, SchemaList):
            return HintDir() 
        msg = 'Cannot find hint for %s' % describe_value(s)
        raise ValueError(msg)
 
    @contract(s=SchemaBase,pattern=str,translations='None|dict(str:(str|None))')
    def hint_directory(self, s, pattern='%', translations=None):
        if isinstance(s, SchemaHash):
            if translations:
                msg = 'Cannot specify translations with SchemaHash'
                raise ValueError(msg)
        self.hints[s] = HintDir(pattern=pattern, translations=translations)

    def hint_extensions(self, s, extensions):
        self.hints[s] = HintExtensions(extensions)
 
    def hint_file_yaml(self, s):
        self.hints[s] = HintFileYAML() 
        
    @contract(dirname='seq(str)')
    def data_url_from_dirname(self, dirname):
        return self.data_url_from_dirname_(self.schema, tuple(dirname))
    
    @contract(data_url='seq(str)')
    def dirname_from_data_url(self, data_url):
        return self.dirname_from_data_url_(self.schema, tuple(data_url))
    
    def dirname_from_data_url_(self, schema, data_url):
        if not data_url:
            return ()
        # We know we will only get Context, List and Hash
        check_isinstance(schema, (SchemaHash, SchemaList, SchemaContext))
        # things that are serialized using hintdir
        hint = self.get_hint(schema)
        check_isinstance(hint, HintDir)
        
        first = data_url[0]
        rest = data_url[1:]
        first_translated = hint.filename_for_key(first)
        
        if isinstance(schema, SchemaHash):
            rest_translated = self.dirname_from_data_url_(schema.prototype, rest)
        
        if isinstance(schema, SchemaList):
            rest_translated = self.dirname_from_data_url_(schema.prototype, rest)
        
        if isinstance(schema, SchemaContext):
            schema_child = schema.children[first]
            rest_translated = self.dirname_from_data_url_(schema_child, rest)
           
        if first_translated is not None: 
            res = (first_translated,) + rest_translated
        else:
            res = rest_translated
        
        return res
        
    @contract(dirname='tuple,seq(str)')
    def data_url_from_dirname_(self, schema, dirname):
        if not dirname:
            return ()
        # We know we will only get Context, List and Hash
        check_isinstance(schema, (SchemaHash, SchemaList, SchemaContext))
        # things that are serialized using hintdir
        hint = self.get_hint(schema)
        check_isinstance(hint, HintDir)
        
        first = dirname[0]
        rest = dirname[1:]
        first_translated = hint.key_from_filename(first)
        
        if isinstance(schema, SchemaHash):
            rest_translated = self.data_url_from_dirname_(schema.prototype, rest)
            return (first_translated,) + rest_translated
        elif isinstance(schema, SchemaList):
            rest_translated = self.data_url_from_dirname_(schema.prototype, rest)
            return (first_translated,) + rest_translated
        elif isinstance(schema, SchemaContext):
            # all right, what could happen here is that we have one or more children
            # whose file translation is None. What to do?
            
            # Let's first look at how many children have translation "None".
            children_with_none = [k for k in schema.children if hint.translations.get(k, 'ok') is None]
            if len(children_with_none) > 1:
                msg = 'This is an ambiguous situation.'
                raise_desc(NotImplementedError, msg, hint=hint, schema=schema)
            elif len(children_with_none) == 0:
                # easy case: 
                schema_child = schema.children[first_translated]
                rest_translated = self.data_url_from_dirname_(schema_child, rest)
                return (first_translated,) + rest_translated
            else:
                
                child_with_none = children_with_none[0]
                logger.debug('We found one descendant with translation None: %r' % child_with_none)
                schema_child = schema.children[child_with_none]
                rest_translated = self.data_url_from_dirname_(schema_child, dirname)
                res = (child_with_none,) + rest_translated
                logger.debug('Result is dirname %r -> res %r' % (dirname, res))
                return res
            
         
        
    @contract(fh='isinstance(ProxyDirectory)|isinstance(ProxyFile)')
    def interpret_hierarchy_(self, schema, fh):
        try:
            hint = self.get_hint(schema)

            if isinstance(schema, SchemaHash):
                if isinstance(hint, HintDir):
                    return read_SchemaHash_SER_DIR(self, schema, fh)
                if isinstance(hint, HintExtensions):
                    return read_SchemaHash_Extensions(self, schema, fh)

            if isinstance(schema, SchemaContext):
                if isinstance(hint, HintDir):
                    return read_SchemaContext_SER_DIR(self, schema, fh) 
                if isinstance(hint, HintFileYAML):
                    return read_SchemaContext_SER_FILE_YAML(self, schema, fh)

            if isinstance(schema, SchemaList):
                if isinstance(hint, HintDir):
                    return interpret_SchemaList_SER_DIR(self, schema, fh) 

            if isinstance(schema, SchemaBytes):
                if isinstance(hint, HintFile):
                    return fh.contents

            if isinstance(schema, SchemaString):
                if isinstance(hint, HintFile):
                    return schema.decode(fh.contents) # todo: encode to UTF-8

            if isinstance(schema, SchemaDate):
                if isinstance(hint, HintFile): 
                    return yaml_load(fh)

            msg = 'NotImplemented'
            raise_desc(NotImplementedError, msg, schema=type(schema), hint=hint)
        except IncorrectFormat as e:
            msg = 'While interpreting schema %s' % type(schema)
            msg += ', hint: %s' % str(self.get_hint(schema))
            msg += '\nDisk representation (1) level:\n%s' % indent(fh.tree(1), ' tree(1) ')
            raise_wrapped(IncorrectFormat, e, msg, compact=True, 
                          exc = sys.exc_info()) 

    def create_hierarchy_(self, schema, data):
        hint = self.get_hint(schema)
        
        if isinstance(hint, HintFileYAML):
            return ProxyFile(yaml_dump(data))

        if isinstance(schema, SchemaHash):
            if isinstance(hint, HintDir):
                return write_SchemaHash_SER_DIR(self, schema, data)
            
            if isinstance(hint, HintExtensions):
                return write_SchemaHash_Extensions(self, schema, data)
            
        if isinstance(schema, SchemaList):
            if isinstance(hint, HintDir):
                return write_SchemaList_SER_DIR(self, schema, data)
            
        if isinstance(schema, SchemaContext):
            if isinstance(hint, HintDir):
                return write_SchemaContext_SER_DIR(self, schema, data)
    
        if isinstance(schema, SchemaBytes):
            if isinstance(hint, HintFile):
                return ProxyFile(data)
        
        if isinstance(schema, SchemaString):
            if isinstance(hint, HintFile):
                return ProxyFile(schema.encode(data))
        
        if isinstance(schema, SchemaDate):
            if isinstance(hint, HintFile):
                return ProxyFile(yaml_dump(data)) 
        
        msg = 'Not implemented for %s, hint %s' % (schema, hint)
        raise ValueError(msg)

@contract(returns='tuple(list(dict), list(dict))')
def data_events_from_disk_event_queue(disk_map, schema, disk_rep, disk_events_queue):
#     def not_implement():
#         raise NotImplementedError(yaml_dump(disk_events_queue[0]))
#     
    handlers = {
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
            res= f(disk_map=disk_map, disk_rep=disk_rep, disk_events_queue=disk_events_queue,
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
    
def data_events_from_dir_create(disk_map, disk_rep, disk_events_queue, _id, who, dirname, name):
    
    parent = disk_map.data_url_from_dirname(tuple(dirname) + (name,))[:-1]     
    schema_parent = disk_map.schema.get_descendant(parent)
    hint = disk_map.get_hint(schema_parent)
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
    
def data_events_from_dir_rename(disk_map, disk_rep, disk_events_queue, _id, who, dirname, name, name2):
    parent = disk_map.data_url_from_dirname(tuple(dirname) + (name,))[:-1]
    
    disk_rep = deepcopy(disk_rep)
    schema_parent = disk_map.schema.get_descendant(parent)
    hint = disk_map.get_hint(schema_parent)
    if isinstance(schema_parent, SchemaHash):
        if isinstance(hint, HintDir):
            key = hint.key_from_filename(name)
            key2 = hint.key_from_filename(name2)
            e = event_dict_rename(name=parent, key=key, key2=key2, _id=_id, who=who)
            return [e], []
    msg = 'Not implemented %s with %s' % (schema_parent, hint)
    raise NotImplementedError(msg)

def data_events_from_dir_delete(disk_map, disk_rep, disk_events_queue, _id, who, dirname, name):
    parent = disk_map.data_url_from_dirname(tuple(dirname) + (name,))[:-1]
    
    disk_rep = deepcopy(disk_rep)
    schema_parent = disk_map.schema.get_descendant(parent)
    hint = disk_map.get_hint(schema_parent)
    if isinstance(schema_parent, SchemaHash):
        if isinstance(hint, HintDir):
            key = hint.key_from_filename(name)
            e = event_dict_delitem(name=parent, key=key, _id=_id, who=who)
            return [e], []
    msg = 'Not implemented %s with %s' % (schema_parent, hint)
    raise NotImplementedError(msg)

def data_events_from_file_create(disk_map, disk_rep, disk_events_queue, _id, who, dirname, name, contents):
    parent = disk_map.data_url_from_dirname(tuple(dirname) + (name,))[:-1]
    schema_parent = disk_map.schema.get_descendant(parent)
    hint = disk_map.get_hint(schema_parent)
    if isinstance(schema_parent, SchemaHash):
        if isinstance(hint, HintDir):
            # creating a file
            logger.debug('data_events_from_file_create dirname %r name %r contents = %r' % (dirname, name, contents))
                         
            # the interesting case is when it is yaml file
            prototype = schema_parent.prototype
            is_yaml = isinstance(disk_map.get_hint(prototype), HintFileYAML)
            if is_yaml:
                key = hint.key_from_filename(name)
                schema_child = schema_parent.get_descendant((key,))
                data = disk_map.interpret_hierarchy_(schema_child, ProxyFile(contents))
                e = event_dict_setitem(name=parent, key=key, value=data, _id=_id, who=who)
                events = [e]
                consumed = [] 
                return events, consumed

    msg = 'Not implemented %s with %s' % (type(schema_parent), hint)
    raise NotImplementedError(msg)

def data_events_from_file_modify(disk_map, disk_rep, disk_events_queue, _id, who, dirname, name, contents):
    name1 = disk_map.data_url_from_dirname(tuple(dirname) + (name,))
    
    parent = name1[:-1]
    logger.debug('name1 %r dirname %s -> parent %s' % (name1, dirname, parent))
    schema_parent = disk_map.schema.get_descendant(parent)
    hint = disk_map.get_hint(schema_parent)
    if isinstance(schema_parent, SchemaContext):
        if isinstance(hint, HintDir):
            key = hint.key_from_filename(name)
            schema_child = schema_parent.get_descendant((key,))
            value = disk_map.interpret_hierarchy_(schema_child, ProxyFile(contents))
            e = event_leaf_set(parent=parent, name=key, value=value, _id=_id, who=who)
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
                
                def add_prefix(e):
                    e2 = deepcopy(e) 
                    if 'parent' in e2['arguments']:
                        e2['arguments']['parent'] = parent+ (key,) + e2['arguments']['parent'] 
                    return e2
                
                diff2 = map(add_prefix, diff) 
                return diff2, [] 
            else: 
                # if a file is modified, it means that it was a leaf node
                pass
#                 data2 = disk_map.interpret_hierarchy_(schema_child, ProxyFile(contents))  
# #                 e = data_event_dict_
#                 return [e], [] 
                
                
                
    msg = 'Not implemented %s with %s' % (type(schema_parent), hint)
    raise NotImplementedError(msg)

def data_events_from_file_rename(disk_map, disk_rep, disk_events_queue, _id, who, dirname, name, name2):
    parent = disk_map.data_url_from_dirname(tuple(dirname) + (name,))[:-1]
    schema_parent = disk_map.schema.get_descendant(parent)
    hint = disk_map.get_hint(schema_parent)
    if isinstance(schema_parent, SchemaHash):
        if isinstance(hint, HintDir):
            key = hint.key_from_filename(name)
            key2 = hint.key_from_filename(name2)                        
            e = event_dict_rename(name=parent, key=key, key2=key2, _id=_id, who=who)
            return [e],[]

    msg = 'Not implemented %s with %s' % (type(schema_parent), hint)
    raise NotImplementedError(msg)

def data_events_from_file_delete(disk_map, disk_rep, disk_events_queue, _id, who, dirname, name):
    parent = disk_map.data_url_from_dirname(tuple(dirname) + (name,))[:-1]
    schema_parent = disk_map.schema.get_descendant(parent)
    hint = disk_map.get_hint(schema_parent)
    if isinstance(schema_parent, SchemaHash):
        if isinstance(hint, HintDir):
            key = hint.key_from_filename(name)                     
            e = event_dict_delitem(name=parent, key=key, _id=_id, who=who)
            return [e],[]

    msg = 'Not implemented %s with %s' % (type(schema_parent), hint)
    raise NotImplementedError(msg)
     
@contract(returns='list(dict)')
def disk_events_from_data_event(disk_map, schema, data_rep, data_event):
    handlers = {
        DataEvents.leaf_set: disk_events_from_leaf_set,
        DataEvents.dict_setitem: disk_events_from_dict_setitem,
        DataEvents.dict_delitem: disk_events_from_dict_delitem,
        DataEvents.dict_rename: disk_events_from_dict_rename,
    }
    viewmanager = ViewManager(schema) 
    view = viewmanager.view(data_rep)
    
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
    
def disk_events_from_leaf_set_in_yaml(disk_map, view, _id, who, parent, name, value, parent_with_yaml):
    p_schema = view._schema.get_descendant(parent_with_yaml)
    p_hint = disk_map.get_hint(p_schema)
    check_isinstance(p_hint, HintFileYAML)
    
    relative_url = parent[len(parent_with_yaml):]
    msg = 'Inside yaml:  set %s.%s = %s' % (relative_url, name, value)
    logger.info(msg)
    
    parent_of_yaml = parent_with_yaml[:-1]
    parent_of_yaml_schema = view._schema.get_descendant(parent_of_yaml)
    parent_of_yaml_hint = disk_map.get_hint(parent_of_yaml_schema)
    dirname = disk_map.dirname_from_data_url(parent_of_yaml)
    filename = parent_of_yaml_hint.filename_for_key(parent_with_yaml[-1])
    
    # this is the current data to go in yaml
    data_view = get_view_node(view, parent_with_yaml)
    # make a copy
    data_view._data = deepcopy(data_view._data)
    # now make the change
    _data= get_view_node(data_view, relative_url)._data
    _data[name] = value
    fh = disk_map.create_hierarchy_(p_schema, data_view._data)
    check_isinstance(fh, ProxyFile)
    contents = fh.contents
    disk_event = disk_event_file_modify(_id, who, dirname, filename, contents)
    return [disk_event]
 

def disk_events_from_leaf_set(disk_map, view, _id, who, parent, name, value):
    # check if it is contained in any dir that has HintFileYAML
#     logger.debug('leaf_set %s . %s = %s' % (parent, name, value))
    for i in range(len(parent)+1):
        p = parent[:i]
        p_schema = view._schema.get_descendant(p)
        p_hint = disk_map.get_hint(p_schema)
#         logger.debug('parent %s p %s hint %s' % (parent, p,p_hint))
        if isinstance(p_hint, HintFileYAML):
#             msg = 'For leaf set %s.%s=%s, detected yaml at %s' % (parent, name, value, p)
#             logger.debug(msg)
            return disk_events_from_leaf_set_in_yaml(disk_map, view, _id, who, parent, name, value, p)
    
    view_parent = get_view_node(view, parent)
    schema_parent = view_parent._schema
    check_isinstance(schema_parent, SchemaContext)
    view_child = view_parent.child(name)
    schema_child = view_child._schema
    
    hint = disk_map.get_hint(schema_parent)
    if isinstance(hint, HintDir):
        sub = disk_map.create_hierarchy_(schema_child, value)
        dirname = disk_map.dirname_from_data_url(parent)
        
        if isinstance(sub, ProxyFile):
            filename = name
            contents = sub.contents
            disk_event = disk_event_file_modify(_id, who, dirname, filename, contents)
            return [disk_event]
        else: 
            assert False 
    elif isinstance(hint, HintFileYAML):
        sub = disk_map.create_hierarchy_(schema_child, value)
        check_isinstance(sub, ProxyFile)
        dirname = disk_map.dirname_from_data_url(parent)
        filename = name
        contents = sub.contents
        disk_event = disk_event_file_modify(_id, who, dirname, filename, contents)
        return [disk_event]
    else:
        raise NotImplementedError(hint)

def disk_events_from_dict_setitem(disk_map, view, _id, who, name, key, value):
    view_parent = get_view_node(view, name)
    schema_parent = view_parent._schema
    check_isinstance(schema_parent, SchemaHash)
    prototype = schema_parent.prototype
    
    hint = disk_map.get_hint(schema_parent)
    if isinstance(hint, HintDir):
        d = disk_map.create_hierarchy_(prototype, value)
        its_name = hint.filename_for_key(key)
        dirname = disk_map.dirname_from_data_url(name)
        
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
            return events
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
        dirname = disk_map.dirname_from_data_url(name) 
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
        dirname = disk_map.dirname_from_data_url(name)
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

    
class NotKey(Exception):
    pass

 


def write_SchemaList_SER_DIR(self, schema, data):
    check_isinstance(schema, SchemaList)
    hint = self.get_hint(schema)
    res = ProxyDirectory()
    for i, d in enumerate(data):
        filename = hint.pattern.replace('%', str(i))
        res[filename] = self.create_hierarchy_(schema.prototype, d)
    return res 


def interpret_SchemaList_SER_DIR(self, schema, fh):
    check_isinstance(schema, SchemaList)
    n = len(fh)
    res = [None] * n
    for filename in fh:
        try:
            i = int(filename)
        except ValueError:
            msg = 'Filename "%s" does not represent a number.' % filename
            raise_incorrect_format(msg, schema, fh.tree())
        if not (0 <= i < n):
            msg = 'Integer %d is not in the bounds (n = %d).' % (i, n)
            raise_incorrect_format(msg, schema, fh.tree())

        res[i] = self.interpret_hierarchy_(schema.prototype, fh[filename])
    return res


@contract(fh=ProxyDirectory)
def read_SchemaHash_Extensions(self, schema, fh):
    check_isinstance(schema, SchemaHash)
    res = {}
    extensions = self.get_hint(schema).extensions 
    
    found = [] 
    for filename, data in fh.recursive_list_files():
        found.append(filename)

        name, ext = os.path.splitext(filename)
        if not ext:
            continue
        ext = ext[1:]
        
        if ext in extensions: 
            if not name in res:
                res[name] = {}
                
            check_isinstance(data, ProxyFile)
            res[name][ext] = self.interpret_hierarchy_(schema.prototype[ext], data)
            # fill nulls for other extensions
            for ext2 in extensions:
                if not ext2 in res[name]: # do not overwrite
                    res[name][ext2] = None 
    return res


def read_SchemaHash_SER_DIR(self, schema, fh):
    check_isinstance(schema, SchemaHash)
    res = {} 
    hint = self.get_hint(schema)
    if hint.pattern == '%': 
        seq = fh.items() 
    else:
        seq = recursive_list_dir(fh, hint)
 
    seq = list(seq)
    msg = 'read_SchemaHash_SER_DIR\n'
    msg += indent(fh.tree(0), 'files  ') + '\n'
    msg += 'pattern is %r\n' % hint.pattern
    msg += 'list is %s\n' % seq 
    
    for filename, data in seq:
        try:
            k = hint.key_from_filename(filename)
        except NotKey:
            logger.warning('Ignoring file "%s": not a key' % filename)
            continue
        assert not k in res, (k, hint.pattern, filename)
        
        try:
            res[k] = self.interpret_hierarchy_(schema.prototype, data)
        except IncorrectFormat as e:
            msg = 'While interpreting filename "%s":' % filename
            raise_wrapped(IncorrectFormat, e, msg, compact=True, exc=sys.exc_info())
             
    return res


def recursive_list_dir(fh, hint):
    for filename, data in fh.items():
        if isinstance(data, dict):
            for x in recursive_list_dir(data, hint):
                yield x
        try: 
            hint.key_from_filename(filename)
            yield filename, data
        except NotKey:
            pass
        
        
@contract(returns=ProxyDirectory)
def write_SchemaHash_SER_DIR(self, schema, data):
    check_isinstance(schema, SchemaHash)
    check_isinstance(data, dict)
    res = ProxyDirectory()
    hint = self.get_hint(schema)
    for k in data:
        filename = hint.pattern.replace('%', k)
        assert not filename in res, (k, hint.pattern, filename)
        res[filename] = self.create_hierarchy_(schema.prototype, data[k])
    return res


@contract(returns=ProxyDirectory)
def write_SchemaHash_Extensions(self, schema, data):
    check_isinstance(schema, SchemaHash)
    check_isinstance(data, dict)
    res = ProxyDirectory()
    hint = self.get_hint(schema) 
    for k in data:
        for ext in hint.extensions:
            filedata = data[k][ext]
            if filedata is not None:
                filename = '%s.%s' % (k, ext)
                res[filename] = self.create_hierarchy_(schema.prototype[ext], filedata)
    return res 


@contract(f=ProxyFile)
def read_SchemaContext_SER_FILE_YAML(self, schema, f):
    import yaml
    data = yaml.load(f.contents)
    res = {}
    present = set(data)
    used = set()
    for k, schema_child in schema.children.items():
        if k in data:
            # have it
            pass
        else:
            # dont' have it
            default = schema_child.get_default()
            if default != NOT_PASSED:
                # use default
                res[k] = copy.copy(schema_child.default)
                logger.warning('Using default for key %s' % k)
                continue
            else:
                # no default
                msg = 'Expected key "%s".' % k
                raise_incorrect_format(msg, schema, data)
        used.add(k)
        res[k] = data[k] 
    extra = set(present) - set(used)

    if extra:
        msg = 'Extra fields: %s.' % format_list(sorted(extra))
        msg += '\nPresent: %s' % format_list(present)
        msg += '\nUsed: %s' % format_list(used)
        raise_incorrect_format(msg, schema, data)
    schema.validate(res)
    return res 

def read_SchemaContext_SER_DIR(self, schema, fh):
    if not isinstance(fh, ProxyDirectory):
        msg = 'I expected a ProxyDirectory representing dir entries.'
        msg += indent(str(schema), 'schema ')
        raise_desc(IncorrectFormat, msg, fh=fh)
    res = {}
    hint = self.get_hint(schema)
    for k, schema_child in schema.children.items():
        filename = hint.filename_for_key(k)
        if filename is None:
            # skip directory
            res[k] = self.interpret_hierarchy_(schema_child, fh)
            
        else:
            if not filename in fh:
                default = schema_child.get_default()
                if default != NOT_PASSED:
                    res[k] =copy.copy( default)
                    logger.debug('Using default for key %s' % k)
                else:
                    msg = 'Expected filename "%s".' % filename
                    msg += '\n available: %s' % format_list(fh)
                    raise_incorrect_format(msg, schema, fh.tree())
            else:
                try:
                    res[k] = self.interpret_hierarchy_(schema_child, fh[filename])
                except IncorrectFormat as e:
                    msg = 'While interpreting child "%s", filename "%s":' % (k, filename)
                    raise_wrapped(IncorrectFormat, e, msg, compact=True, exc=sys.exc_info())
    schema.validate(res)
    return res
 
 
@contract(returns=ProxyDirectory)
def write_SchemaContext_SER_DIR(self, schema, data):
    res = ProxyDirectory()
    hint = self.get_hint(schema)
    for k, schema_child in schema.children.items():
        rec = self.create_hierarchy_(schema_child, data[k])
        filename = hint.filename_for_key(k)
        if filename is None:
            for kk, vv in rec.items():
                if kk in res:
                    msg = 'Already set file %r' % kk
                    raise Exception(msg)
                res[kk] = vv 
        else:
            if filename in res:
                msg = 'I already saw filename "%s".' % filename
                raise_incorrect_format(msg, schema, data)
            res[filename] = rec
    return res
