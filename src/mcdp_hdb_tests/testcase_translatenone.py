# -*- coding: utf-8 -*-
from contracts import contract

from mcdp_hdb import DiskMap, Schema


from mcdp_hdb_tests.testcases import get_combinations


@contract(returns='dict(str:isinstance(DataTestCase))')    
def testcases_TranslateNone(): 
    schema = Schema()
    user = Schema()
    user.string('name')
    schema.hash('users', user)
    
    db0 = {'users': {'andrea': {'name': 'Andrea'}, 'john': {'name':'John'}}}
        
    disk_map_with_hint = DiskMap()
    disk_map_with_hint.hint_directory(schema, translations={'users': None})
    disk_maps = {'vanilla': DiskMap(), 'hint': disk_map_with_hint}
#     disk_map_with_hint.hint_directory(schema['users'], pattern='%.user')
    prefix = 'tranlatenone'
    operation_sequences = [seq1]
    res = get_combinations(schema, db0, prefix, operation_sequences, disk_maps)
    return res

def seq1(view):
    users = view.users
    u = users['andrea'] 
    u.name = 'not-andrea'
    users['another'] = {'name': 'Another'}
    del users['another']
    users.rename('john', 'jack') 
    