# -*- coding: utf-8 -*-
from copy import deepcopy

from contracts import contract

from mcdp_hdb import DiskMap, Schema, SchemaString, ViewManager, assert_data_events_consistent
from mcdp_hdb_tests.testcases import DataTestCase


@contract(returns='dict(str:isinstance(DataTestCase))')    
def testcases_arrays():
    
    db_schema = Schema()
    
    db_schema.list('alist', SchemaString())
    
    db0 = {
        'alist': ['one', 'two']
    }

    db_schema.validate(db0)
    
    
    seqs = []
    def add_seq(f):
        seqs.append(f)
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
    
    disk_maps= {}
    disk_maps['vanilla'] = DiskMap()

    prefix = 'array1'
    res = {}
    
    for s in seqs:
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