# -*- coding: utf-8 -*-
from copy import deepcopy

from contracts import contract

from mcdp_hdb import DiskMap, Schema, SchemaString, SchemaHash, ViewManager, assert_data_events_consistent

from .testcases import DataTestCase


@contract(returns='dict(str:isinstance(DataTestCase))')    
def testcases_minilibrary(): 
    schema = Schema()
    things = Schema()
    models = SchemaHash(SchemaString())
    posets = SchemaHash(SchemaString())
    things._add_child('models', models)
    things._add_child('posets', posets)
    schema._add_child('things', things)
    
    dm = DiskMap()
    dm.hint_directory(schema, translations={'things': None})
    dm.hint_directory(things, translations={'models': None, 'posets':None})
    dm.hint_directory(posets, pattern='%.poset')
    dm.hint_directory(models, pattern='%.mcdp')

    db0 = {
        'things': {
            'models': {
                'model1': 'mcdp {}',
            },
            'posets': {
                'poset1': 'poset {}',
            },     
        },
    }
    db = deepcopy(db0)

    viewmanager = ViewManager(schema) 
    view = viewmanager.view(db) 
    view.things.models['model2'] = 'mcdp { model2 }'
    del view.things.models['model1']

    events = view._events
    assert len(events) >= 2    
    assert_data_events_consistent(schema, db0,  events, db)


    res = {}
    res['minilib1'] = DataTestCase(schema, db0, events, db, dm)
    return res
