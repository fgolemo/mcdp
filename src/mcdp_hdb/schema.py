# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from contextlib import contextmanager
import datetime
import random

from contracts.interface import describe_value
from contracts.utils import indent, check_isinstance, raise_desc, raise_wrapped

from mcdp_utils_misc import format_list


NOT_PASSED = 'no-default-given'

class NotValid(Exception):
    ''' Raisedd by SchemaBase::validate() ''' 
    pass
 
class SchemaBase(object):

    def __init__(self):
        pass
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def generate(self):
        ''' Generate data compatible with this schema. '''
    
    def get_default(self):
        return NOT_PASSED
    
    @abstractmethod
    def validate(self, data):
        ''' Raises NotValid '''

class SchemaDate(SchemaBase):
    def __init__(self, default):
        self.default = default
        
    def get_default(self):
        return self.default 
    
    def __str__(self):
        return 'SchemaDate'
    
    def generate(self):
        return datetime.datetime.now()
    
    def validate(self, data):
        if not isinstance(data, datetime.datetime):
            msg = 'Expected a datetime.datetime object.'
            raise_desc(NotValid, msg, data=describe_value(data))
    
class SchemaString(SchemaBase):
    
    def __init__(self, default=NOT_PASSED, can_be_none=False):
        self.default = default
        self.can_be_none = can_be_none
        
    def get_default(self):
        return self.default 
    
    def __str__(self):
        return 'SchemaString'
    
    def generate(self):
        words = ["boo","bar","fiz","buz"]
        s = ""
        for _ in range(3):
            s += words[random.randint(0,len(words)-1)]
        return s
    
    def validate(self, data):
        if self.can_be_none and data is None:
            return
        
        if not isinstance(data, str):
            msg = 'Expected a string object.'
            raise_desc(NotValid, msg, data=describe_value(data))

    
class SchemaBytes(SchemaBase):

    def __init__(self, default, can_be_none=False):
        self.default = default
        self.can_be_none = can_be_none
        
    def __str__(self):
        return 'SchemaBytes'
    
    def generate(self):
        return b'somebytes'
    
    def validate(self, data):
        if self.can_be_none and data is None:
            return
        if not isinstance(data, bytes):
            msg = 'Expected a bytes object.'
            raise_desc(NotValid, msg, data=describe_value(data))


class SchemaHash(SchemaBase):
    def __init__(self, schema, default=NOT_PASSED):
        SchemaBase.__init__(self)
        self.prototype = schema
        
        self.default = default
    
    def get_default(self):
        return self.default 
    
    def __str__(self):
        return 'SchemaHash:\n' + describe({'<prototype>':self.prototype})
    
    def generate(self):
        res = {}
        n = 2
        names = ["foo", "bar", "baz"]
        for _ in range(n):
            k = names[_]
            res[k] = self.prototype.generate()
        return res
  
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
            

# def substitute_in_pattern(pattern, what):
#     return re.sub(r'{.*}', what, pattern)


class SchemaContext(SchemaBase): 
    def __init__(self):
        self.children = OrderedDict() 
    
    def validate(self, data):
        
        if not isinstance(data, dict):
            msg = 'Expected a dictionary object.'
            raise_desc(NotValid, msg, data=describe_value(data))

        for k, v in self.children.items():
            if not k in data:
                msg = 'Expecting key "%s" but not found in %s.' % (k, format_list(data))
                raise_desc(NotValid, msg, data=describe_value(data))
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
    def list_e(self, name, default=NOT_PASSED):
        s = SchemaContext()
        yield s
        self.list(name, s, default=default)
        
    def context(self, name, child_schema=None):    
#         child_schema = child_schema or self._child()
        if child_schema is None:
            child_schema = SchemaContext()
        self._add_child(name, child_schema)
        return child_schema
    
    def hash(self, name, child_schema=None, default=NOT_PASSED):
        check_isinstance(name, str)
        child_schema = child_schema or self._child()
        sc = SchemaHash(child_schema, default=default)
        self._add_child(name, sc)
        return child_schema
    
    def list(self, name, child_schema=None, default=NOT_PASSED):
        child_schema = child_schema or self._child()
        sc = SchemaList(child_schema, default=default)
        self._add_child(name, sc)
        return child_schema
    
    def date(self, name, default=NOT_PASSED):
        schema = SchemaDate(default=default)
        self._add_child(name, schema)
    
    def string(self, name, default=NOT_PASSED, can_be_none=False):
        schema = SchemaString(default=default, can_be_none=can_be_none)
        self._add_child(name, schema)
        
    def bytes(self, name, default=NOT_PASSED, can_be_none=False):
        schema = SchemaBytes(default=default, can_be_none=can_be_none)
        self._add_child(name, schema)
        
    def __getitem__(self, name):
        if not name in self.children:
            msg = 'Could not find %r: available %s.' % (name, format_list(self.children))
            raise KeyError(msg)
        return self.children[name]
    
    def _add_child(self, name, cs):
        check_isinstance(name, str)
        if name in self.children:
            msg =  'I already know "%s".' % name
            raise ValueError(msg)
        self.children[name] = cs
    
    def __str__(self):
        return "SchemaContext:\n" + indent(describe(self.children),' ')

    def generate(self): 
        res = {}
        for k, c in self.children.items():
            res[k] = c.generate()
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

class SchemaList(SchemaBase):
    def __init__(self, schema, default=NOT_PASSED):
        self.prototype = schema
        self.default = default
        
#     def __repr__(self):
#         return 'SchemaList(%r)' % self.prototype
      
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
        return 'SchemaList\n' + describe({'<prototype>': self.prototype})  
    
    def generate(self):
        res = []
        n = 2
        for _ in range(n):
            res.append(self.prototype.generate())
        return res
    
    