import os
import sys
import warnings

from contracts import contract, describe_value
from contracts.utils import raise_desc, raise_wrapped, indent, check_isinstance

from mcdp import logger
from mcdp_utils_misc import format_list, yaml_dump, yaml_load

from .disk_struct import ProxyDirectory, ProxyFile
from .exceptions import IncorrectFormat, NotKey
from .hints import HintDir, HintExtensions, HintFileYAML, HintFile
from .schema import SchemaHash, SchemaString, SchemaContext, SchemaList, SchemaBytes, SchemaDate, SchemaBase
from .schema import SchemaSimple


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
    raise_desc(IncorrectFormat, msg2, schema=str(schema))
 
class DiskMap(object):
    def __init__(self):
        self.hints = {} 

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
    
    @contract(schema=SchemaBase)
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
            if not first in schema.children:
                msg = ('Could not translate data url %r because could not find child %r: found %s' %
                       (data_url, first, format_list(schema.children)))
                raise_desc(ValueError, msg, schema=str(schema))
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
#                 msg = 'This is a situation in which there are more than one child that have no translation.'
#                 msg += ' These are children_with_none = %s' % children_with_none
#                 msg += ' first = %s rest = %s first_translated %s' % (first, rest, first_translated)
#                 logger.debug(msg)
                successful = {}
                for maybe_child in children_with_none:
                    schema_child = schema.children[maybe_child]
                    try:
                        rest_translated = self.data_url_from_dirname_(schema_child, dirname)
                    except NotKey:
                        continue
                    successful[maybe_child] = rest_translated
                if not successful:
                    msg = 'Could not translate rest = %s '% str(rest)
                    raise ValueError(msg)
                if len(successful) > 1: 
                    msg = 'Too many ways to translate rest = %s : %s'% (str(rest), successful)
                    raise ValueError(msg)
                child_succeded = list(successful)[0]
                rest_translated = successful[child_succeded]
                res = (child_succeded,) + rest_translated
#                 logger.debug('special: Result is dirname %r -> res %r' % (dirname, res))
                return res
            elif len(children_with_none) == 0:
                # easy case: 
                schema_child = schema.children[first_translated]
                rest_translated = self.data_url_from_dirname_(schema_child, rest)
                return (first_translated,) + rest_translated
            else:
                child_with_none = children_with_none[0]
                logger.debug('We found one descendant with translation None: %r' % child_with_none)
                schema_child = schema.children[child_with_none]
                warnings.warn('I think it should be rest but who knows')
                # rest_translated = self.data_url_from_dirname_(schema_child, rest)
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
    found = []
    for filename in fh:
        try:
            i = int(filename)
        except ValueError:
            msg = 'Filename "%s" does not represent a number.' % filename
            logger.warning(msg + ' -- ignoring')
            #raise_incorrect_format(msg, schema, fh.tree())
        found.append(i)
    if not found:
        return []
    max_found = max(found)
    n = max_found + 1
    res = [None] * n
    if len(found) != n:
        msg = 'Incomplete data. Found %s' % found
        raise_incorrect_format(msg, schema, fh.tree())
    for filename in fh:
        try:
            i = int(filename)
        except ValueError:
            continue
        if not (0 <= i < n):
            assert False

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

def fill_in_none(schema, data):
    ''' Fills in the fields not passed and that can be None '''
    if isinstance(schema, SchemaString):
        if isinstance(data, unicode):
            return data.encode('utf8')
        else:
            return data
    elif isinstance(schema, SchemaSimple):
        schema.validate(data)
        return data
    elif isinstance(schema, SchemaList):
        check_isinstance(data, list)
        res = [fill_in_none(schema.prototype, _) for _ in data]
        schema.validate(res)
        return res
    elif isinstance(schema, SchemaHash):
        check_isinstance(data, dict)
        res = dict([(k, fill_in_none(schema.prototype, v)) for k, v in data.items()])
        schema.validate(res)
        return res
    elif isinstance(schema, SchemaContext):
        check_isinstance(data, dict)
        # some of the fields might be missing
        res = {}
        present = set(data)
        
        for k, schema_child in schema.children.items():
            if k in data:
                # have it
                res[k] = fill_in_none(schema_child, data[k])
            else:
                # dont' have it
                if schema_child.can_be_none:
                    res[k] = None
                else: 
                    # no default
                    msg = 'Expected key "%s".' % k
                    raise_incorrect_format(msg, schema, data,                    )
        needed = set(schema.children)
        extra = set(present) - needed
    
        if extra:
            msg = 'Extra fields: %s.' % format_list(sorted(extra))
            msg += '\nPresent: %s' % format_list(present)
            msg += '\nNeeded: %s' % format_list(needed)
            raise_incorrect_format(msg, schema, data)
        schema.validate(res)
        return res
    else:
        assert False, schema

@contract(f=ProxyFile)
def read_SchemaContext_SER_FILE_YAML(self, schema, f):
    data = yaml_load(f.contents)
    # now we need to iterate and fill the missing keys
    res = fill_in_none(schema, data)
    schema.validate(res)
    logger.info('OK validation for \n %s' % yaml_dump(res))
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
                
                if schema_child.can_be_none:
                    res[k] = None
#                     logger.debug('Using default for key %s' % k)
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
