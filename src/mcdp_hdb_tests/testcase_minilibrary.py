# -*- coding: utf-8 -*-
from contracts import contract

from mcdp_hdb import DiskMap, Schema, SchemaString, SchemaHash
from mcdp_hdb_tests.testcases import get_combinations


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
    disk_maps = {'vanilla': DiskMap()}
    prefix='minilibrary'
    res = get_combinations(schema, db0, prefix, operation_sequences, disk_maps)
    return res

    

operation_sequences = []
def add_seq(f):
    operation_sequences.append(f)
    return f

@add_seq
def seq_set(view):
    view.things.models['model2'] = 'mcdp { model2 }'
    del view.things.models['model1']
