# -*- coding: utf-8 -*-
from contracts import contract

from mcdp_hdb import DiskMap, Schema, SchemaString
from mcdp_hdb.schema import SchemaList

from .testcases import get_combinations


@contract(returns='dict(str:isinstance(DataTestCase))')    
def testcases_arrays_inside_yaml():
    
    db_schema = Schema()
    user = Schema()
    user._add_child('name', SchemaString())
    user._add_child('groups', SchemaList(SchemaString()))
    db_schema.hash('users', user)
    
    db0 = {
        'users': {
            'andrea': {
                'name': 'Andrea',
                'groups': ['one', 'two'],
            }
        }
    }

    db_schema.validate(db0)
    
    operation_sequences = []
    def add_seq(f):
        operation_sequences.append(f)
        return f
    
    @add_seq
    def seq_set(view):
        view.users['andrea'].name = 'new name'
        
    @add_seq
    def seq_append(view):
        view.users['andrea'].groups.append('newgroup')
     
    @add_seq
    def seq_delete1(view):
        view.users['andrea'].groups.remove('one')
   
    dm = DiskMap()
    dm.hint_file_yaml(user)
    disk_maps= {}
    disk_maps['vanilla'] = DiskMap()
    disk_maps['yaml'] = dm

    prefix = 'array_inside_yaml'
    
    res = get_combinations(db_schema, db0, prefix, operation_sequences, disk_maps)
    return res