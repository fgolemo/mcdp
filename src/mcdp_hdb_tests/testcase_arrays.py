# -*- coding: utf-8 -*-
from contracts import contract

from mcdp_hdb import DiskMap, Schema, SchemaString


from mcdp_hdb_tests.testcases import get_combinations


@contract(returns='dict(str:isinstance(DataTestCase))')    
def testcases_arrays():
    
    db_schema = Schema()
    
    db_schema.list('alist', SchemaString())
    
    db0 = {
        'alist': ['one', 'two']
    }

    db_schema.validate(db0)
    
    disk_maps= {}
    disk_maps['vanilla'] = DiskMap()

    prefix = 'array1' 

    res = get_combinations(db_schema, db0, prefix, operation_sequences, disk_maps)
    return res


operation_sequences = []
def add_seq(f):
    operation_sequences.append(f)
    return f

@add_seq
def seq_delete0(view):
    view.alist.delete(0)

@add_seq
def seq_delete1(view):
    view.alist.delete(1)

@add_seq
def seq_delete_all(view):
    view.alist.delete(0)
    view.alist.delete(0)

@add_seq
def seq_append(view):
    view.alist.append('appended')
    
@add_seq
def seq_insert(view):
    view.alist.insert(1, 'between')
