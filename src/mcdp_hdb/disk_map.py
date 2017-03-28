from collections import namedtuple

from contracts.interface import describe_value
from contracts.utils import raise_desc, raise_wrapped, indent, check_isinstance
import yaml

from mcdp.logs import logger_tmp
from mcdp_hdb.schema import Schema, SchemaHash, SchemaString, SchemaContext,\
    SchemaList, SchemaBytes
from mcdp_library_tests.create_mockups import mockup_flatten


Hint = namedtuple('Hint', 'serialization pattern')
SER_FILE_YAML = 'SER_FILE_YAML'
SER_DIR = 'SER_DIR'
SER_FILE = 'SER_FILE'

class IncorrectFormat(Exception):
    pass

class DiskMap():
    
    def __init__(self, schema):
        self.hints = {}
        self.schema = schema
    
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
        hint = self.get_hint(schema)
        if hint.serialization == SER_FILE_YAML:
            return yaml.load(fh)
            
        if isinstance(schema, SchemaHash):
            if hint.serialization == SER_DIR:
                return read_SchemaHash_SER_DIR(self, schema, fh)
            elif hint.serialization in [SER_FILE, SER_FILE_YAML]:
                msg = 'Invalid serialization %s for %r' % (hint.serialization, schema)
                raise_desc(ValueError, msg, hint=hint, schema=schema)
            else: assert False 
    
        if isinstance(schema, SchemaContext):
            if hint.serialization == SER_DIR:
                return read_SchemaContext_SER_DIR(self, schema, fh)
            elif hint.serialization in [SER_FILE, SER_FILE_YAML]:
                msg = 'Invalid serialization %s for %r' % (hint.serialization, schema)
                raise_desc(ValueError, msg, hint=hint, schema=schema)
            else: assert False
            
        if isinstance(schema, SchemaString):
            return fh
        
        if isinstance(schema, SchemaList): 
            if hint.serialization == SER_DIR:
                return interpret_SchemaList_SER_DIR(self, schema, fh)
            elif hint.serialization in [SER_FILE, SER_FILE_YAML]:
                msg = 'Invalid serialization %s for %r' % (hint.serialization, schema)
                raise_desc(ValueError, msg, hint=hint, schema=schema)
            else: assert False 
            return fh
        
        if isinstance(schema, SchemaBytes):
            return fh
        
        raise NotImplementedError(type(schema))
    
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
                msg = 'Invalid serialization %s for %r' % (hint.serialization, schema)
                raise_desc(ValueError, msg, hint=hint, schema=schema, data=data)
            else: assert False 
        if isinstance(schema, SchemaList):
            if hint.serialization == SER_DIR:
                return write_SchemaList_SER_DIR(self, schema, data)
            elif hint.serialization in [SER_FILE, SER_FILE_YAML]:
                msg = 'Invalid serialization %s for %r' % (hint.serialization, schema)
                raise_desc(ValueError, msg, hint=hint, schema=schema, data=data)
            else: assert False     
        if isinstance(schema, SchemaContext): 
            if hint.serialization == SER_DIR:
                return write_SchemaContext_SER_DIR(self, schema, data)
            elif hint.serialization in [SER_FILE, SER_FILE_YAML]:
                msg = 'Invalid serialization %s for %r' % (hint.serialization, schema)
                raise_desc(ValueError, msg, hint=hint, schema=schema, data=data)
            else: assert False

        if isinstance(schema, SchemaString):
            return data
        
        if isinstance(schema, SchemaList):
            return data
        
        if isinstance(schema, SchemaBytes):
            return data
        msg = 'Not implemented for %s' % schema
        raise ValueError(msg)
    
    def get_hint(self, s):
        if s in self.hints:
            return self.hints[s]
        if isinstance(s, SchemaString):
            return Hint(SER_FILE, '%')
        if isinstance(s, SchemaBytes):
            return Hint(SER_FILE, '%')
        if isinstance(s, SchemaHash):
            return Hint(SER_DIR, '%')
        if isinstance(s, Schema):
            return Hint(SER_DIR, '%')
        if isinstance(s, SchemaList):
            return Hint(SER_DIR, '%')
        msg = 'Cannot find hint for %s' % describe_value(s)
        raise ValueError(msg)

def key_from_filename(pattern, filename):
    if not '%' in pattern:
        msg = 'Cannot get key from filename.'
        raise_desc(IncorrectFormat, msg, pattern=pattern, filename=filename)    
    if pattern.startswith('%'):
        
        key = filename.replace(pattern.replace('%',''), '')
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

def interpret_SchemaList_SER_DIR(self, schema, fh):
    check_isinstance(schema, SchemaList)
    n = len(fh)
    res = [None] * n 
    for filename in fh:
        try: 
            i = int(filename)
        except ValueError as e:
            msg = 'Filename does not represent a number.' 
            raise_wrapped(IncorrectFormat, e, msg, filename=filename)
            
        if not (0 <= i < n):
            msg = 'Integer %d is not in the bounds (n = %d).' % (i, n)
            raise_desc(IncorrectFormat, msg, filename=filename)  

        res[i] = self.interpret_hierarchy_(schema.prototype, fh[filename])
    return res


def read_SchemaHash_SER_DIR(self, schema, fh):
    check_isinstance(schema, SchemaHash)
    res = {} 
    hint = self.get_hint(schema) 
    for filename in fh:
        k = key_from_filename(pattern=hint.pattern, filename=filename)
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
    filename = k
    return filename

def read_SchemaContext_SER_DIR(self, schema, fh):
    res = {} 
    for k, schema_child in schema.children.items():
        filename = filename_for_k_SchemaContext_SER_DIR(self, schema, k)
        if not filename in fh:
            msg = 'Expected filename "%s".' % filename
            raise_desc(ValueError, msg, filename=filename, available=list(fh)) 
        res[k] = self.interpret_hierarchy_(schema_child, fh[filename])
    return res

def write_SchemaContext_SER_DIR(self, schema, data):
    res = {} 
    for k, schema_child in schema.children.items(): 
        filename = filename_for_k_SchemaContext_SER_DIR(self, schema, k)
        if filename in res:
            raise_desc(ValueError, filename) 
        res[filename] = self.create_hierarchy_(schema_child, data[k])
    return res