from collections import defaultdict
from collections import namedtuple
from contextlib import contextmanager

from contracts.interface import describe_value
from contracts.utils import raise_desc, raise_wrapped, indent, check_isinstance
import yaml

from mcdp.logs import logger_tmp, logger
from mcdp_hdb.schema import SchemaHash, SchemaString, SchemaContext,\
    SchemaList, SchemaBytes, NOT_PASSED, SchemaDate
from mcdp_library_tests.create_mockups import mockup_flatten
from mcdp_utils_misc.string_utils import format_list
import datetime
import sys
import copy


Hint = namedtuple('Hint', 'serialization pattern')
SER_FILE_YAML = 'SER_FILE_YAML'
SER_DIR = 'SER_DIR'
SER_FILE = 'SER_FILE'
SER_STRUCT = 'SER_STRUCT'


class IncorrectFormat(Exception):
    pass


def raise_incorrect_format(msg, schema, data):
    msg2 = 'Incorrect format:\n'
    msg2 += indent(msg, '  ')
#     datas = yaml.dump(data).encode('utf8')
    if isinstance(data, str):
        datas = data
    else:
        datas = yaml.dump(data).encode('utf8')
    MAX = 512
    if len(datas) > MAX:
        datas = datas[:MAX] + ' [truncated]'
    if False:
        msg2 += '\nData:\n'
        msg2 += indent(datas, '  ')
    #     msg2 += 'repr: '+ datas.__repr__()
    raise_desc(IncorrectFormat, msg2, schema=schema)

# 
# @contextmanager
# def error_context(schema, data):  # @UnusedVariable
#     try:
#         yield
#     except IncorrectFormat as e:
#         msg = 'While interpreting schema %s' % type(schema)
#         raise_wrapped(IncorrectFormat, e, msg,# compact=True, 
#                       exc = sys.exc_info())


class DiskMap():

    def __init__(self, schema):
        self.hints = {}
        self.schema = schema

        self.inside_yaml = False
        self.hint_translation = defaultdict(lambda: dict())

    def get_hint(self, s):
        if self.inside_yaml:
            return Hint(SER_STRUCT, '%')
        if s in self.hints:
            return self.hints[s]
        if isinstance(s, SchemaString):
            return Hint(SER_FILE, '%')
        if isinstance(s, SchemaBytes):
            return Hint(SER_FILE, '%')
        if isinstance(s, SchemaHash):
            return Hint(SER_DIR, '%')
        if isinstance(s, SchemaContext):
            return Hint(SER_DIR, '%')
        if isinstance(s, SchemaList):
            return Hint(SER_DIR, '%')
        if isinstance(s, SchemaDate):
            return Hint(SER_FILE, '%')
        msg = 'Cannot find hint for %s' % describe_value(s)
        raise ValueError(msg)

    def translate_children(self, s, dic):
        self.hint_translation[s].update(**dic)

    def hint_directory(self, s, pattern='%'):
        self.hints[s] = Hint(SER_DIR, pattern)

    def hint_file(self, s, pattern='%'):
        if isinstance(s, SchemaHash):
            if not '%' in pattern:
                raise ValueError(s)
        self.hints[s] = Hint(SER_FILE, pattern)

    def hint_file_yaml(self, s, pattern='%'):
        self.hints[s] = Hint(SER_FILE_YAML, pattern)

    def interpret_hierarchy(self, fh):
        '''
            fh = Files in recursive dictionary format:
            {'dir': {'file': 'filecontents'}} 
        '''
        try:
            return self.interpret_hierarchy_(schema=self.schema, fh=fh)
        except IncorrectFormat as e:
            msg = 'While parsing: \n'
            msg += indent(str(self.schema), ' ')
            msg += '\n\nfiles:\n\n'
            flattened = mockup_flatten(fh)
            msg += indent("\n".join(flattened), '  ')
            raise_wrapped(IncorrectFormat, e, msg)

    def interpret_hierarchy_(self, schema, fh):
        try:
            hint = self.get_hint(schema)

            if isinstance(schema, SchemaHash):
                if hint.serialization == SER_DIR:
                    return read_SchemaHash_SER_DIR(self, schema, fh)
                elif hint.serialization in [SER_FILE, SER_FILE_YAML]:
                    msg = 'Invalid serialization %s for %r' % (
                        hint.serialization, schema)
                    raise_desc(ValueError, msg, hint=hint, schema=schema)
                else:
                    assert False

            if isinstance(schema, SchemaContext):
                if hint.serialization == SER_DIR:
                    check_isinstance(fh, dict)
                    return read_SchemaContext_SER_DIR(self, schema, fh)
                elif hint.serialization == SER_STRUCT:
                    return read_SchemaContext_SER_STRUCT(self, schema, fh)
                elif hint.serialization == SER_FILE_YAML:
                    return read_SchemaContext_SER_FILE_YAML(self, schema, fh)
                elif hint.serialization in [SER_FILE, SER_FILE_YAML]:
                    msg = 'Invalid serialization %s for %r' % (
                        hint.serialization, schema)
                    raise_desc(ValueError, msg, hint=hint, schema=schema)
                else:
                    assert False

            if isinstance(schema, SchemaString):
                return fh

            if isinstance(schema, SchemaList):
                if hint.serialization == SER_DIR:
                    return interpret_SchemaList_SER_DIR(self, schema, fh)
                elif hint.serialization == SER_STRUCT:
                    return interpret_SchemaList_SER_STRUCT(self, schema, fh)
                elif hint.serialization in [SER_FILE, SER_FILE_YAML]:
                    msg = 'Invalid serialization %s for %r' % (
                        hint.serialization, schema)
                    raise_desc(ValueError, msg, hint=hint, schema=schema)
                else:
                    assert False
                return fh

            if isinstance(schema, SchemaBytes):
                return fh

            if isinstance(schema, SchemaDate):
                if isinstance(fh, datetime.datetime):
                    return fh
                else:
                    logger_tmp.debug('looking at %r' % fh)
                    return yaml.load(fh)

            raise NotImplementedError(type(schema))
        except IncorrectFormat as e:
            msg = 'While interpreting schema %s' % type(schema)
            msg += '\n hint: %s' % str(self.get_hint(schema))
            raise_wrapped(IncorrectFormat, e, msg, #compact=True, 
                          exc = sys.exc_info())

    def create_hierarchy(self, data):
        return self.create_hierarchy_(schema=self.schema, data=data)

    def create_hierarchy_(self,  schema, data):
        hint = self.get_hint(schema)
        if hint.serialization == SER_FILE_YAML:
            return yaml.dump(data)

        if isinstance(schema, SchemaHash):
            if hint.serialization == SER_DIR:
                return write_SchemaHash_SER_DIR(self, schema, data)
            elif hint.serialization in [SER_FILE, SER_FILE_YAML]:
                msg = 'Invalid serialization %s for %r' % (
                    hint.serialization, schema)
                raise_desc(
                    ValueError, msg, hint=hint, schema=schema, data=data)
            else:
                assert False
        if isinstance(schema, SchemaList):
            if hint.serialization == SER_DIR:
                return write_SchemaList_SER_DIR(self, schema, data)
            elif hint.serialization in [SER_FILE, SER_FILE_YAML]:
                msg = 'Invalid serialization %s for %r' % (
                    hint.serialization, schema)
                raise_desc(
                    ValueError, msg, hint=hint, schema=schema, data=data)
            else:
                assert False
        if isinstance(schema, SchemaContext):
            if hint.serialization == SER_DIR:
                return write_SchemaContext_SER_DIR(self, schema, data)
            elif hint.serialization in [SER_FILE, SER_FILE_YAML]:
                msg = 'Invalid serialization %s for %r' % (
                    hint.serialization, schema)
                raise_desc(
                    ValueError, msg, hint=hint, schema=schema, data=data)
            else:
                assert False

        if isinstance(schema, SchemaString):
            return data

        if isinstance(schema, SchemaList):
            return data

        if isinstance(schema, SchemaBytes):
            return data
        
        if isinstance(schema, SchemaDate):
            return yaml.dump(data)
        
        msg = 'Not implemented for %s' % schema
        raise ValueError(msg)

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
    res = {}
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


def read_SchemaHash_SER_DIR(self, schema, fh):
    check_isinstance(schema, SchemaHash)
    res = {}
    hint = self.get_hint(schema)
    for filename in fh:
        try:
            k = key_from_filename(pattern=hint.pattern, filename=filename)
        except NotKey:
            logger.warning('Ignoring file "%s": not a key' % filename)
            continue
        
        #logger.debug('filename %s -> key %s' % (filename, k))
        assert not k in res, (k, hint.pattern, filename)

        res[k] = self.interpret_hierarchy_(schema.prototype, fh[filename])
    return res


def write_SchemaHash_SER_DIR(self, schema, data):
    check_isinstance(schema, SchemaHash)
    res = {}
    logger_tmp.info('write_SchemaHash_SER_DIR  %s' % (list(data)))
    hint = self.get_hint(schema)
    for k in data:
        filename = hint.pattern.replace('%', k)
        assert not filename in res, (k, hint.pattern, filename)
        res[filename] = self.create_hierarchy_(schema.prototype, data[k])
    logger_tmp.info('Result of %s: \n %s' % (schema, res))
    return res


def filename_for_k_SchemaContext_SER_DIR(self, schema, k):
    dic = self.hint_translation[schema]
    filename = dic.get(k, k)
    return filename


def read_SchemaContext_SER_FILE_YAML(self, schema, yaml_data):
    data = yaml.load(yaml_data)
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
                use = schema_child.default
                if use is not None:
                    use = copy.copy(use)
                res[k] = use
                continue
            else:
                # no default
                msg = 'Expected key "%s".' % k
                raise_incorrect_format(msg, schema, yaml_data)
        used.add(k)
        self.inside_yaml = True
        try:
            res[k] = self.interpret_hierarchy_(schema_child, data[k])
        finally:
            self.inside_yaml = False
    extra = set(present) - set(used)

    if extra:
        msg = 'Extra fields: %s.' % format_list(sorted(extra))
        msg += '\nPresent: %s' % format_list(present)
        msg += '\nUsed: %s' % format_list(used)
        raise_incorrect_format(msg, schema, yaml_data)
    return res


def read_SchemaContext_SER_STRUCT(self, schema, fh):
    res = {}
    remaining = set(fh)
    for k, schema_child in schema.children.items():
        if not k in fh:
            default = schema_child.get_default()
            if default != NOT_PASSED:
                res[k] = default
            else:
                msg = 'Expected element "%s".' % k
                raise_incorrect_format(msg, schema, fh)
        else:
            res[k] = self.interpret_hierarchy_(schema_child, fh[k])
            remaining.remove(k)
    if remaining:
        msg = 'Extra keys: %s' % format_list(remaining)
        raise_incorrect_format(msg, schema, fh)
    return res


def read_SchemaContext_SER_DIR(self, schema, fh):
    check_isinstance(fh, dict)
    res = {}
    for k, schema_child in schema.children.items():
        filename = filename_for_k_SchemaContext_SER_DIR(self, schema, k)
        if not filename in fh:
            default = schema_child.get_default()
            if default != NOT_PASSED:
                res[k] = default
            else:
                msg = 'Expected filename "%s".' % filename
                msg += '\n available: %s' % format_list(fh)
                raise_incorrect_format(msg, schema, fh)
        else:
            res[k] = self.interpret_hierarchy_(schema_child, fh[filename])
    return res


def write_SchemaContext_SER_DIR(self, schema, data):
    res = {}
    for k, schema_child in schema.children.items():
        filename = filename_for_k_SchemaContext_SER_DIR(self, schema, k)
        if filename in res:
            msg = 'I already saw filename "%s".' % filename
            raise_incorrect_format(msg, schema, data)
        res[filename] = self.create_hierarchy_(schema_child, data[k])
    return res
