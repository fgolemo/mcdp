from collections import defaultdict
import copy
import datetime
import os
import sys

from contracts import contract
from contracts.interface import describe_value
from contracts.utils import raise_desc, raise_wrapped, indent, check_isinstance

from mcdp.logs import logger_tmp, logger
from mcdp_utils_misc import format_list, yaml_dump, yaml_load

from .change_events import DataEvents, get_view_node
from .dbview import ViewManager, InvalidOperation
from .disk_events import disk_event_file_modify, disk_event_dir_delete, disk_event_file_create, disk_event_dir_create, disk_event_file_delete, disk_event_file_rename, disk_event_dir_rename
from .disk_struct import ProxyDirectory, ProxyFile
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
 
class HintExtensions():
    def __init__(self, extensions):
        self.extensions = extensions

    def __repr__(self):
        return 'HintExtensions(%r)' % self.extensions
    
class HintFile():
    def __init__(self, pattern='%'):
        self.pattern = pattern

    def __repr__(self):
        return 'HintFile(%r)' % self.pattern

class HintStruct():
    def __init__(self):
        pass
    def __repr__(self):
        return 'HintStruct()'
            
class HintDir():
    def __init__(self, pattern='%'):
        self.pattern = pattern
 
    def __repr__(self):
        return 'HintDir(%r)' % self.pattern
    
    def filename_for_key(self, key):
        return self.pattern.replace('%', key)


class HintFileYAML():
    def __init__(self, pattern='%'):
        self.pattern = pattern
    def __repr__(self):
        return 'HintFileYAML(%r)' % self.pattern
        
class DiskMap():

    def __init__(self):
        self.hints = {}

        self.inside_yaml = False
        self.hint_translation = defaultdict(lambda: dict())

    def get_hint(self, s):
        check_isinstance(s, SchemaBase)
        if self.inside_yaml:
            return HintStruct()
        if s in self.hints:
            return self.hints[s]
        if isinstance(s, SchemaString):
            return HintFile()
        if isinstance(s, SchemaBytes):
            return HintFile()
        if isinstance(s, SchemaHash):
            return HintDir()
        if isinstance(s, SchemaContext):
            return HintDir()
        if isinstance(s, SchemaList):
            return HintDir()
        if isinstance(s, SchemaDate):
            return HintFile()
        msg = 'Cannot find hint for %s' % describe_value(s)
        raise ValueError(msg)

    def translate_children(self, s, dic):
        self.hint_translation[s].update(**dic)

    def hint_directory(self, s, pattern='%'):
        self.hints[s] = HintDir(pattern)

    def hint_extensions(self, s, extensions):
        self.hints[s] = HintExtensions(extensions)

    def hint_file(self, s, pattern='%'):
        if isinstance(s, SchemaHash):
            if not '%' in pattern:
                raise ValueError(s)
        self.hints[s] = HintFile(pattern)

    def hint_file_yaml(self, s, pattern='%'):
        self.hints[s] = HintFileYAML(pattern)

    @contract(fh=ProxyDirectory)
    def interpret_hierarchy(self, schema, fh):
        '''
            fh = Files in recursive dictionary format:
            {'dir': {'file': 'filecontents'}} 
        '''
        try:
            return self.interpret_hierarchy_(schema, fh=fh)
        except IncorrectFormat as e:
            msg = 'While parsing: \n'
            msg += indent(str(schema), ' ')
            msg += '\n\nfiles:\n\n'
            msg += indent(fh.tree(), '  ')
            raise_wrapped(IncorrectFormat, e, msg)

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
                elif isinstance(hint, HintStruct):
                    return read_SchemaContext_SER_STRUCT(self, schema, fh)
                if isinstance(hint, HintFileYAML):
                    return read_SchemaContext_SER_FILE_YAML(self, schema, fh)


            if isinstance(schema, SchemaList):
                if isinstance(hint, HintDir):
                    return interpret_SchemaList_SER_DIR(self, schema, fh)
                elif isinstance(hint, HintStruct):
                    return interpret_SchemaList_SER_STRUCT(self, schema, fh)
                return fh.contents

            if isinstance(schema, SchemaBytes):
                return fh.contents

            if isinstance(schema, SchemaString):
                return yaml_load(fh.contents)

            if isinstance(schema, SchemaDate):
#                 if isinstance(fh, datetime.datetime):
#                     return fh.contents
#                 else:
#                     logger_tmp.debug('looking at %r' % fh)
                    return yaml_load(fh)

            msg = 'NotImplemented'
            raise_desc(NotImplementedError, msg, schema=type(schema), hint=hint)
        except IncorrectFormat as e:
            msg = 'While interpreting schema %s' % type(schema)
            msg += ', hint: %s' % str(self.get_hint(schema))
            raise_wrapped(IncorrectFormat, e, msg, compact=True, 
                          exc = sys.exc_info())

    @contract(returns=ProxyDirectory)
    def create_hierarchy(self, schema, data):
        return self.create_hierarchy_(schema=schema, data=data)

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
            return ProxyFile(data)
        
        if isinstance(schema, (SchemaString, SchemaDate)):
            return ProxyFile(yaml_dump(data))

        if isinstance(schema, SchemaList):
            return data # XXXX
        
        msg = 'Not implemented for %s, hint %s' % (schema, hint)
        raise ValueError(msg)
 
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
    
def disk_events_from_leaf_set(disk_map, view, _id, who, parent, name, value):
    view_parent = get_view_node(view, parent)
    schema_parent = view_parent._schema
    check_isinstance(schema_parent, SchemaContext)
    view_child = view_parent.child(name)
    schema_child = view_child._schema
    
    hint = disk_map.get_hint(schema_parent)
    if isinstance(hint, HintDir):
        sub = disk_map.create_hierarchy_(schema_child, value)
        if isinstance(sub, ProxyFile):
            dirname = parent
            filename = name
            contents = sub.contents
            disk_event = disk_event_file_modify(_id, who, dirname, filename, contents)
            return [disk_event]
        else: 
            assert False 
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
        if isinstance(d, ProxyFile):
            dirname = name
            contents = d.contents
            filename = its_name
            disk_event = disk_event_file_modify(_id, who, 
                                                dirname=dirname, 
                                                filename=filename, 
                                                contents=contents)
            return [disk_event]
        elif isinstance(d, ProxyDirectory):
            events = []
            dirname = name
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
        its_name = hint.filename_for_key(key)
        # I just need to find out whether it would be ProxyDir or ProxyFile
        value = view_parent._data[key]
        d = disk_map.create_hierarchy_(prototype, value)
        if isinstance(d, ProxyFile):
            dirname = name
            disk_event = disk_event_file_delete(_id, who, 
                                                dirname=dirname, 
                                                name=its_name)
            return [disk_event]
        elif isinstance(d, ProxyDirectory):
            dirname = name
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
        its_name = hint.filename_for_key(key)
        its_name2 = hint.filename_for_key(key2)
        # I just need to find out whether it would be ProxyDir or ProxyFile
        if not key in view_parent._data:
            msg = 'Cannot rename key %r that does not exist in %s.'  % (key, format_list(view_parent._data))
            raise InvalidOperation(msg)
        value = view_parent._data[key]
        d = disk_map.create_hierarchy_(prototype, value)
        dirname = name
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


def key_from_filename(pattern, filename):
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


def write_SchemaList_SER_DIR(self, schema, data):
    check_isinstance(schema, SchemaList)
    hint = self.get_hint(schema)
    res = ProxyDirectory()
    for i, d in enumerate(data):
        filename = hint.pattern.replace('%', str(i))
        res[filename] = self.create_hierarchy_(schema.prototype, d)
    return res


def interpret_SchemaList_SER_STRUCT(self, schema, data):
    check_isinstance(schema, SchemaList)
    check_isinstance(data, list)
    n = len(data)
    res = [None] * n
    for i, x in enumerate(data):
        res[i] = self.interpret_hierarchy_(schema.prototype, x)
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
            raise_incorrect_format(msg, schema, fh)
        if not (0 <= i < n):
            msg = 'Integer %d is not in the bounds (n = %d).' % (i, n)
            raise_incorrect_format(msg, schema, fh)

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
        seq = recursive_list(fh, hint.pattern)
 
    seq = list(seq)
    msg = 'read_SchemaHash_SER_DIR\n'
    msg += indent(fh.tree(0), 'files  ') + '\n'
    msg += 'pattern is %r\n' % hint.pattern
    msg += 'list is %s\n' % seq
    #logger.info(msg)
    
    for filename, data in seq:
        try:
            k = key_from_filename(pattern=hint.pattern, filename=filename)
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


def recursive_list(fh, pattern):
    for filename, data in fh.items():
        if isinstance(data, dict):
            for x in recursive_list(data, pattern):
                yield x
        try: 
            key_from_filename(pattern=pattern, filename=filename)
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


def filename_for_k_SchemaContext_SER_DIR(self, schema, k):
    dic = self.hint_translation[schema]
    filename = dic.get(k, k)
    return filename


@contract(f=ProxyFile)
def read_SchemaContext_SER_FILE_YAML(self, schema, f):
    data = yaml_load(f.contents)
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


def read_SchemaContext_SER_STRUCT(self, schema, fh):
    res = {}
    remaining = set(fh)
    for k, schema_child in schema.children.items():
        if not k in fh:
            default = schema_child.get_default()
            if default != NOT_PASSED:
                res[k] = copy.copy(default)
                logger.debug('Using default for key %s' % k)
            else:
                msg = 'Expected element "%s".' % k
                raise_incorrect_format(msg, schema, fh)
        else:
            res[k] = self.interpret_hierarchy_(schema_child, fh[k])
            remaining.remove(k)
    if remaining:
        msg = 'Extra keys: %s' % format_list(remaining)
        raise_incorrect_format(msg, schema, fh)
    schema.validate(res)
    return res


def read_SchemaContext_SER_DIR(self, schema, fh):
    if not isinstance(fh, ProxyDirectory):
        msg = 'I expected a ProxyDirectory representing dir entries.'
        msg += indent(str(schema), 'schema ')
        raise_desc(IncorrectFormat, msg, fh=fh)
    res = {}
    for k, schema_child in schema.children.items():
        filename = filename_for_k_SchemaContext_SER_DIR(self, schema, k)
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
                    raise_incorrect_format(msg, schema, fh)
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
    for k, schema_child in schema.children.items():
        rec = self.create_hierarchy_(schema_child, data[k])
        filename = filename_for_k_SchemaContext_SER_DIR(self, schema, k)
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
