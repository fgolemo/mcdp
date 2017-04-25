# -*- coding: utf-8 -*-

from contracts import contract

from mcdp_hdb import DiskMap, Schema, SchemaString
from mcdp_hdb_tests.testcases import get_combinations
from copy import deepcopy

U1 = 'andrea'
U2 = 'pinco'

@contract(returns='dict(str:isinstance(DataTestCase))')    
def testcases_SimpleUserDB():
    
    db_schema = Schema()
    schema_user = Schema()
    schema_user.string('name')
    schema_user.string('email', can_be_none=True)
    schema_user.list('groups', SchemaString())
    db_schema.hash('users', schema_user)
    
    db0 = {
        'users': { 
            U1: {
                'name': U1, 
                'email': 'info@co-design.science',
                'groups': ['group:admin', 'group:FDM'],
            },
            U2: {
                'name': 'Pinco Pallo', 
                'email': None,
                'groups': ['group:FDM'],
            },
        }
    }

    db_schema.validate(db0) 
    disk_map_with_hint = DiskMap()
    disk_map_with_hint.hint_directory(db_schema['users'], pattern='%.user')
    
    disk_map_files_are_yaml= DiskMap()
    disk_map_files_are_yaml.hint_directory(db_schema['users'], pattern='%.yaml')
    disk_map_files_are_yaml.hint_file_yaml(db_schema['users'].prototype)
    disk_maps= {}
    disk_maps['vanilla'] = DiskMap()
    disk_maps['with_hint'] = disk_map_with_hint
    disk_maps['files_are_yaml'] = disk_map_files_are_yaml

    prefix='simpleuserdb'
    seqs = [
        seq1,
        seq_set_list,
        seq_set_hash,
        seq_set_struct,
    ]
    res = get_combinations(db_schema, db0, prefix, seqs, disk_maps)
    return res


def seq1(view):
    users = view.users
    u = users[U1] 
    u.name = 'not Andrea'
    u.email = None    
    users['another'] = {'name': 'Another', 'email': 'another@email.com', 'groups':['group:extra']}
    del users['another']
    users.rename(U2, 'pallo') 
    
def seq_set_list(view):
    users = view.users
    u = users[U1]
    u.groups = ['newgroup']

def seq_set_hash(view):
    users = view.users
    users_data = deepcopy(users._data)
    users_data[U1].name='new name'
    view.users = users_data
    
def seq_set_struct(view):
    users = view.users
    users[U1] = users[U2]
    
    
