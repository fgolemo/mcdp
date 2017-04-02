# -*- coding: utf-8 -*-
from copy import deepcopy
import os
import shutil

from contracts.utils import indent
from nose.tools import assert_equal

from comptests.registrar import comptest, run_module_tests
from mcdp import logger
from mcdp_hdb.change_events import replay_events, event_intepret
from mcdp_hdb.dbview import ViewManager
from mcdp_hdb.disk_events import disk_event_interpret
from mcdp_hdb.disk_map import DiskMap, disk_events_from_data_event
from mcdp_hdb.schema import Schema, SchemaString
from mcdp_utils_misc import yaml_dump, yaml_load


def l(what, s):
    logger.info('\n' + indent(s, '%010s │  ' % what))


    
@comptest
def test_view1a():
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
    events = []
    viewmanager = ViewManager(db_schema) 
    view = viewmanager.view(db)
    def notify_callback(event):
        logger.debug('\n' + yaml_dump(event))
        events.append(event)
    view._notify_callback = notify_callback

    users = view.users
    u = users['andrea'] 
    u.name = 'not Andrea'
    u.email = None    
    users['another'] = {'name': 'Another', 'email': 'another@email.com', 'groups':[]}
    del users['another']
    users.rename('pinco', 'pallo')
    db2 = replay_events(viewmanager, db0, events) 
    assert_equal(db, db2)
    # check that we didn't modify the original
    db2 = replay_events(viewmanager, db0, events) 
    assert_equal(db, db2)

    dm = DiskMap()
    check_translation(db_schema, db0, events, db2, dm)


def check_translation(schema, data_rep0, data_events, data_rep1, disk_map):
    view_manager = ViewManager(schema)
    
    # first, make sure that the data is coherent
    data_rep1_ = replay_events(view_manager, data_rep0, data_events) 
    assert_equal(data_rep1_, data_rep1)
    
    disk_events = []
    
    data_rep = deepcopy(data_rep0)
    disk_rep = disk_map.create_hierarchy(schema, data_rep0)
        
    out = 'out/test_translation'
    if os.path.exists(out):
        shutil.rmtree(out)
    if not os.path.exists(out):
        os.makedirs(out) 
        
    def write_file_(name, what):
        name = os.path.join(out, name)
        with open(name, 'w') as f:
            f.write(what)
        logger.info('wrote on %s' % name)
        
    def write_file(i, n, what):
        name = '%d-%s.txt' % (i, n)
        write_file_(name, what)
    
    write_file_('0-aa-data_events.yaml', yaml_dump(data_events))
    
    for i, data_event in enumerate(data_events):
        write_file(i, 'a-disk_rep', disk_rep.tree())
        write_file(i, 'b-data_rep', yaml_dump(data_rep))
        write_file(i, 'c-data_event', yaml_dump(data_event))
        
        evs = disk_events_from_data_event(disk_map, schema, data_rep, data_event)
        if not evs:
            msg = 'The event resulted in 0 disk events.'
            msg += '\n' + indent(yaml_dump(data_event), ' data_event ')
            raise Exception(msg)
        
        write_file(i, 'd-evs', yaml_dump(evs))
        
        disk_events.extend(evs)
        
        # interpret data event
        event_intepret(view_manager, data_rep, data_event)
        write_file(i, 'e-data_rep-modified', yaml_dump(data_rep))
         
        disk_rep_by_translation = disk_map.create_hierarchy(schema, data_rep)
        write_file(i, 'f-data_rep-modified-translated-to-disk_rep', 
                   disk_rep_by_translation.tree())
        
        for disk_event in evs:
            disk_event_interpret(disk_rep, disk_event)
        
        write_file(i, 'g-disk_rep-with-evs-applied', disk_rep.tree())
        
        msg = 'Data event:\n'+ indent(yaml_dump(data_event), ' data_event ')
        msg += '\nDisk events:\n' + indent(yaml_dump(evs), ' events ')
        logger.debug(msg)
        
        h1 = disk_rep_by_translation.hash_code()
        h2 = disk_rep.hash_code()
        if h1 != h2:
            msg = 'Hash codes differ.'
            msg += '\n' + indent(disk_rep.tree(), 'disk_rep ')
            msg += '\n' + indent(disk_rep_by_translation.tree(), 'disk_rep_by_tr ')
            raise Exception(msg)
             

if __name__ == '__main__':
    run_module_tests()
    