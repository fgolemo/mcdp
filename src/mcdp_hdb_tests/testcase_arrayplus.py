# -*- coding: utf-8 -*-
from contracts import contract

from mcdp_hdb import DiskMap, Schema
from mcdp_hdb_tests.testcases import get_combinations


@contract(returns='dict(str:isinstance(DataTestCase))')    
def testcases_arrayplus():
    
    db_schema = Schema()
    
    # - first: ciao 
    #   last: ciao
    # - first: 
    #   last: 
    entry = Schema()
    entry.string('first')
    entry.string('last')
    db_schema.list('thelist', entry)
    
    db0 = {
        'thelist': [
            {'first': 'John', 'last': 'Lennon'},
            {'first': 'Max', 'last': 'Power'},
        ]
    }

    db_schema.validate(db0)
    
    disk_maps= {}
    disk_maps['vanilla'] = DiskMap()

    prefix = 'arrayplus' 

    res = get_combinations(db_schema, db0, prefix, operation_sequences, disk_maps)
    return res


operation_sequences = []
def add_seq(f):
    operation_sequences.append(f)
    return f

@add_seq
def seq_delete0(view):
    view.thelist.delete(0)

@add_seq
def seq_delete1(view):
    view.thelist.delete(1)

@add_seq
def seq_delete_all(view):
    view.thelist.delete(0)
    view.thelist.delete(0)

@add_seq
def seq_append(view):
    entry =  dict(first='Kim', last='Possible')
    view.thelist.append(entry)
    
@add_seq
def seq_insert(view):
    entry =  dict(first='Kim', last='Possible')
    view.thelist.insert(1, entry)
