# -*- coding: utf-8 -*-
from copy import deepcopy

from contracts import contract

from mcdp_hdb import DiskMap, SchemaBase, ViewManager, assert_data_events_consistent, event_interpret_

__all__ = [
    'get_combinations',
    'DataTestCase',
]

class DataTestCase(object):
    

    @contract(schema=SchemaBase, events=list, disk_map=DiskMap)
    def __init__(self, schema, data1, events, data2, disk_map):   
        schema.validate(data1)
        schema.validate(data2) 
        assert_data_events_consistent(schema, data1, events, data2)
        self.data1 = data1
        self.events = events
        self.data2 = data2
        self.disk_map = disk_map
        self.schema = schema
        
    def get_data1(self):
        ''' Returns a copy of data1 (safe to modify) '''
        return deepcopy(self.data1)
    
    def get_data2(self):
        ''' Returns a copy of data2 (safe to modify) '''
        return deepcopy(self.data2)
    
    @contract(returns=SchemaBase)
    def get_schema(self):
        ''' returns the schema '''
        return self.schema

    @contract(returns=list)
    def get_events(self):
        return deepcopy(self.events)
    
    @contract(returns=DiskMap)
    def get_disk_map(self):
        return self.disk_map
    
    def enumerate_data_diff(self):
        ''' 
            Enumerates the transitions. Use as:
            for d1, data_event, d2 in enumerate_data_diff():
        ''' 
        data_i = self.get_data1()
        view_manager = ViewManager(self.schema)
        for e in self.events:
            current = deepcopy(data_i)
            view = view_manager.view(data_i)
            event_interpret_(view, e)
            yield current, e, data_i


def get_combinations(db_schema, db0, prefix, operation_sequences, disk_maps):
    res = {}
    
    for s in operation_sequences:
        db = deepcopy(db0)
        viewmanager = ViewManager(db_schema) 
        view = viewmanager.view(db) 
        s(view)
        events = view._events
        assert_data_events_consistent(db_schema, db0, events, db)
        
        for id_dm, dm in disk_maps.items():
            dtc = DataTestCase(db_schema, db0, events, db, dm)
            k = '%s-%s-%s' % (prefix, s.__name__, id_dm)
            res[k] = dtc 
     
    return res
