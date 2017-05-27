# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from contextlib import contextmanager
from contracts import contract
from copy import deepcopy
import datetime
from mcdp_shelf.access import ACL
from mcdp_utils_misc import format_list, get_md5, yaml_dump
import random

from contracts.interface import describe_value, describe_type
from contracts.utils import indent, check_isinstance, raise_desc, raise_wrapped


class NotValid(Exception):
    ''' Raised by SchemaBase::validate() ''' 
    
 
class SchemaBase(object):

    def __init__(self):
        self.can_be_none = False
        self._acl_rules_self = []
        self._parent = None
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def generate(self):
        ''' Generate random data compatible with this schema. '''
      
    def add_acl_rules(self, acl_rules):
        self._acl_rules_self.extend(acl_rules)
        
    def get_acl_rules(self):
        if self._parent is not None:
            others = self._parent.get_acl_rules()
        else:
            others = ()
        return others + tuple(self._acl_rules_self)
    
    def get_acl_local(self):
        return ACL(self._acl_rules_self)
    
    def get_acl(self):
        return ACL(self.get_acl_rules())
        
    def __str__(self):
        s = '%s' % type(self).__name__
        s += '(Can be none: %s)' % self.can_be_none 
        acl = self.get_acl_local()
        if acl.rules:
            s += '\n' + acl.__str__()
        return s 
    
    @abstractmethod
    def validate(self, data):
        ''' Raises NotValid '''

class SchemaRecursive(SchemaBase):
    
    @abstractmethod
    @contract(prefix='seq(str)', returns=SchemaBase)
    def get_descendant(self, prefix):
        ''' Returns the schema for a descendant. '''

    @abstractmethod
    def generate_empty(self):
        ''' Generate the simplest data compatible with this schema. '''
    

class SchemaSimple(SchemaBase):
    ''' Base class for simple data types '''
    @contract(prefix='seq(str)', returns=SchemaBase)
    def get_descendant(self, prefix):
        if not prefix:
            return self
        else:
            msg = 'A basic datatype does not have descendants.'
            raise_desc(ValueError, msg, self=self)
            
        

class SchemaHash(SchemaRecursive):
    
    
    def __init__(self, schema):
        SchemaBase.__init__(self)
        self.prototype = schema
        self.prototype._parent = self
         
        SchemaBase.__init__(self)
    
    def get_descendant(self, prefix):
        ''' Returns the schema for a descendant. '''
        if prefix:
            return self.prototype.get_descendant(prefix[1:])
        else:
            return self
    
    def get_default(self):
        return self.default 
    
    def __str__(self):
        s = 'SchemaHash' 
        acl = self.get_acl_local()
        if acl.rules:
            s += '\n' + acl.__str__()
        s += '\n' + describe({'<prototype>':self.prototype})
        return s 
    
    def generate(self):
        res = {}
        n = 2
        names = ["foo", "bar", "baz"]
        for _ in range(n):
            k = names[_]
            res[k] = self.prototype.generate()
        return res
    
    def generate_empty(self):
        return {}
  
    def validate(self, data):
        if not isinstance(data, dict):
            msg = 'Expected a dictionary object.'
            raise_desc(NotValid, msg, data=describe_value(data))
        
        for k in data:
            try:
                self.prototype.validate(data[k])
            except NotValid as e:
                msg = 'For entry "%s":' % k
                raise_wrapped(NotValid, e, msg) 
             

class SchemaContext(SchemaRecursive): 
    
    def __init__(self):
        self.children = OrderedDict() 
        SchemaBase.__init__(self)
    
    def child(self, name):
        if not name in self.children:
            msg = 'Could not find child %r; available: %s.' % (name, format_list(self.children))
            raise ValueError(msg)
        child = self.children[name]
        return child
        
    def get_descendant(self, prefix):
        ''' Returns the schema for a descendant. '''
        if prefix:
            first = prefix[0]
            child = self.child(first)
            try:
                return child.get_descendant(prefix[1:])
            except ValueError as e:
                msg = 'Could not get descendant "%s":' % str(prefix) 
                raise_wrapped(ValueError, e, msg, compact=True)
        else:
            return self
        
    def validate(self, data):
        if not isinstance(data, dict):
            msg = 'Expected a dictionary object.'
            raise_desc(NotValid, msg, data=describe_value(data))

        for k, v in self.children.items():
            if not k in data:
                msg = 'Expecting key "%s" but not found in %s.' % (k, format_list(data))
                
                raise_desc(NotValid, msg, data=describe_value(data), self=str(self))
            try:
                v.validate(data[k])
            except NotValid as e:
                msg = 'For child "%s":' % k
                raise_wrapped(NotValid, e, msg) 
            

    @contextmanager
    def hash_e(self, name):
        s = SchemaContext() 
        yield s
        self.hash(name, s)

    @contextmanager
    def context_e(self, name):
        s = SchemaContext() 
        yield s
        self.context(name, s)
    
    @contextmanager
    def list_e(self, name):
        s = SchemaContext()
        yield s
        self.list(name, s)
        
    def context(self, name, child_schema=None):     
        if child_schema is None:
            child_schema = SchemaContext()
        self._add_child(name, child_schema)
        return child_schema
    
    def hash(self, name, child_schema=None):
        check_isinstance(name, str)
        child_schema = child_schema or self._child()
        sc = SchemaHash(child_schema)
        self._add_child(name, sc)
        return child_schema
    
    def list(self, name, child_schema=None):
        child_schema = child_schema or self._child()
        sc = SchemaList(child_schema)
        self._add_child(name, sc)
        return child_schema
    
    def date(self, name,    can_be_none=False):
        schema = SchemaDate(can_be_none=can_be_none)
        self._add_child(name, schema)
    
    def string(self, name,   can_be_none=False):
        schema = SchemaString(can_be_none=can_be_none)
        self._add_child(name, schema)
        
    def bytes(self, name,  can_be_none=False):
        schema = SchemaBytes(can_be_none=can_be_none)
        self._add_child(name, schema)
        
    def __getitem__(self, name):
        if not name in self.children:
            msg = 'Could not find %r: available %s.' % (name, format_list(self.children))
            raise KeyError(msg)
        return self.children[name]
    
    def _add_child(self, name, cs):
        cs._parent = self
        check_isinstance(name, str)
        if name in self.children:
            msg =  'I already know "%s".' % name
            raise ValueError(msg)
        self.children[name] = cs
    
    def __str__(self):
        s = 'SchemaContext:' 
        
        acl = self.get_acl_local()
        if acl.rules:
            s += '\n' + acl.__str__()
        s += '\n' + indent(describe(self.children),' ')
        return s 
    
    def generate(self): 
        res = {}
        for k, c in self.children.items():
            res[k] = c.generate()
        return res
    
    def generate_empty(self, **kwargs):
        res = {}
        for k in kwargs:
            if not k in self.children:
                msg = 'Extra key %r not in %s.' % (k, format_list(self.children))
                raise ValueError(msg)
        kwargs = deepcopy(kwargs)
        for k, c in self.children.items():
            
            if isinstance(c, SchemaSimple):
                if k in kwargs:
                    res[k] = kwargs.pop(k)
                elif c.can_be_none:
                    res[k] = None
                else:
                    msg = 'Cannot generate empty for child %r: %s.' % (k, c)
                    raise ValueError(msg)
            else:
                if k in kwargs:
                    x = kwargs.pop(k)
                    if isinstance(x, dict):
                        res[k] = c.generate_empty(**x)
                    else:
                        res[k] = x
                else:
                    res[k] = c.generate_empty()
        assert not kwargs     
        return res
 
Schema = SchemaContext

def describe(children):
    s = "" 
    for k, c in children.items():
        cs = c.__str__().strip()
        if '\n' in cs:
            s += '%s:\n%s' % (k, indent(cs, ' | '))
        else:
            s += '%s: %s' % (k,cs)
        s += '\n'
    return s.rstrip()

class SchemaList(SchemaRecursive):
    def __init__(self, schema):
        self.prototype = schema
        
        SchemaBase.__init__(self)
    def generate_empty(self):
        return []
    def get_descendant(self, prefix):
        ''' Returns the schema for a descendant. '''
        if prefix:
            return self.prototype.get_descendant(prefix[1:])
        else:
            return self
      
    def validate(self, data):
        if not isinstance(data, list):
            msg = 'Expected a list object.'
            raise_desc(NotValid, msg, data=describe_value(data))
        
        for i, d in enumerate(data):
            try:
                self.prototype.validate(d)
            except NotValid as e:
                msg = 'For entry %d:' % i
                raise_wrapped(NotValid, e, msg) 
            
            
    def get_default(self):
        return self.default
      
    def __str__(self):
        s = 'SchemaList' 
        acl = self.get_acl_local()
        if acl.rules:
            s += '\n' + acl.__str__()
        s += '\n' + describe({'<prototype>':self.prototype})
        return s 
     
    
    def generate(self):
        res = []
        n = 2
        for _ in range(n):
            res.append(self.prototype.generate())
        return res
    

    
class SchemaDate(SchemaSimple):
    def __init__(self,  can_be_none=False):
        SchemaBase.__init__(self) 
        self.can_be_none = can_be_none
        
    def get_default(self):
        return self.default 

    def generate(self):
        return datetime.datetime.now()
    
    def validate(self, data):
        if self.can_be_none and data is None:
            return
        if not isinstance(data, datetime.datetime):
            msg = 'Expected a datetime.datetime object.'
            raise_desc(NotValid, msg, data=describe_value(data))
    
class SchemaString(SchemaSimple):
    
    # how to represent None
    NONE_TAG = 'null'
    
    def __init__(self,   can_be_none=False):
        SchemaBase.__init__(self) 
        self.can_be_none = can_be_none
        
    
    def get_default(self):
        return self.default 
     
    @contract(returns=bytes, s='str|None')
    def encode(self, s):
        ''' encode from memory to disk '''
        if s is None:
            return SchemaString.NONE_TAG
        else:
            return s
        
    @contract(returns='str|None', b=bytes)
    def decode(self, b):
        if b == SchemaString.NONE_TAG:
            return None
        else:
            return b
        
    def generate(self):
        words = ["boo", "bar", "fiz", "buz"]
        s = ""
        for _ in range(3):
            s += words[random.randint(0,len(words)-1)]
        return s
    
    def validate(self, data):
        if self.can_be_none and (data is None):
            return
        
        if not isinstance(data, str):
            msg = 'Expected a string object.'
            raise_desc(NotValid, msg, data=describe_value(data))

class SchemaBytes(SchemaSimple):

    def __init__(self, can_be_none=False):
        SchemaBase.__init__(self)
        self.can_be_none = can_be_none
    
    def generate(self):
        return b'somebytes'
    
    def validate(self, data):
        if self.can_be_none and data is None:
            return
        if not isinstance(data, bytes):
            msg = 'Expected a bytes object.'
            raise_desc(NotValid, msg, data=describe_value(data))

    
def data_hash_code(s):
    if s is None:
        return 'None'
    if isinstance(s, str):
        return get_md5(s)
    elif isinstance(s, datetime.datetime):
        return get_md5(yaml_dump(s))
    elif isinstance(s, list):
        return get_md5("-".join(map(data_hash_code, s)))
    elif isinstance(s, dict):
        keys = sorted(s)
        values = [s[k] for k in keys]
        codes = ['%s-%s' % (k, data_hash_code(v)) for k,v in zip(keys, values)]
        return data_hash_code("_".join(codes))
    else:
        msg = 'Invalid type %s' % describe_type(s)
        raise ValueError(msg)
    
    
    