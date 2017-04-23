# -*- coding: utf-8 -*-
from copy import deepcopy

from contracts import contract

from mcdp_hdb import DiskMap, Schema, SchemaString, ViewManager, assert_data_events_consistent


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
            'andrea': {
                'name': 'Andrea', 
                'email': 'info@co-design.science',
                'groups': ['group:admin', 'group:FDM'],
            },
            'pinco': {
                'name': 'Pinco Pallo', 
                'email': None,
                'groups': ['group:FDM'],
            },
        }
    }

    db_schema.validate(db0)
    db = deepcopy(db0)
    
    viewmanager = ViewManager(db_schema) 
    view = viewmanager.view(db) 

    users = view.users
    u = users['andrea'] 
    u.name = 'not Andrea'
    u.email = None    
    users['another'] = {'name': 'Another', 'email': 'another@email.com', 'groups':['group:extra']}
    del users['another']
    users.rename('pinco', 'pallo') 
    
    events = view._events
    
    assert len(events) > 3, events
    
    assert_data_events_consistent(db_schema, db0, events, db)
    
    disk_map_with_hint = DiskMap()
    disk_map_with_hint.hint_directory(db_schema['users'], pattern='%.user')
    
    disk_map_files_are_yaml= DiskMap()
    disk_map_files_are_yaml.hint_directory(db_schema['users'], pattern='%.yaml')
    disk_map_files_are_yaml.hint_file_yaml(db_schema['users'].prototype)
    disk_maps= {}
    disk_maps['vanilla'] = DiskMap()
    disk_maps['with_hint'] = disk_map_with_hint
    disk_maps['files_are_yaml'] = disk_map_files_are_yaml

    from mcdp_hdb_tests.testcases import DataTestCase
        
    res = {}
    for k in disk_maps:
        dm = disk_maps[k]
        res[k] = DataTestCase(db_schema, db0, events, db, dm)
    return res
