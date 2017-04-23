# -*- coding: utf-8 -*-
from copy import deepcopy

from contracts import contract

from mcdp_hdb import DiskMap, Schema, ViewManager, assert_data_events_consistent
from mcdp_hdb_tests.testcases import DataTestCase


@contract(returns='dict(str:isinstance(DataTestCase))')    
def testcases_TranslateNone(): 
    schema = Schema()
    user = Schema()
    user.string('name')
    schema.hash('users', user)
    
    db = {'users': {'andrea': {'name': 'Andrea'}, 'john': {'name':'John'}}}
    db0 = deepcopy(db)
    
    viewmanager = ViewManager(schema) 
    view = viewmanager.view(db) 

    users = view.users
    u = users['andrea'] 
    u.name = 'not-andrea'
    users['another'] = {'name': 'Another'}
    del users['another']
    users.rename('john', 'jack') 
    
    events = view._events
    assert len(events) > 2
    
    assert_data_events_consistent(schema, db0,  events, db)
    
    disk_map_with_hint = DiskMap()
    disk_map_with_hint.hint_directory(schema, translations={'users': None})
#     disk_map_with_hint.hint_directory(schema['users'], pattern='%.user')

    res = {}
    res['x_normal'] = DataTestCase(schema, db0, events, db, DiskMap())
    res['x_none'] = DataTestCase(schema, db0, events, db, disk_map_with_hint)
    return res


