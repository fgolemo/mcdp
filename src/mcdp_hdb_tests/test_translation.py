# -*- coding: utf-8 -*-
from copy import deepcopy
import os
import shutil
import traceback

from contracts.utils import indent
from nose.tools import assert_equal

from comptests.registrar import run_module_tests
from mcdp import logger
from mcdp_hdb import ViewManager
from mcdp_hdb import data_hash_code
from mcdp_hdb import disk_event_interpret
from mcdp_hdb import disk_events_from_data_event, IncorrectFormat, data_events_from_disk_event_queue
from mcdp_hdb import replay_events, event_intepret
from mcdp_utils_misc import yaml_dump
from mcdp_hdb.memdata_utils import assert_data_equal


def l(what, s):
    logger.info('\n' + indent(s, '%010s │  ' % what))

# 
# def get_schema_and_data():
#     db_schema = Schema()
#     schema_user = Schema()
#     schema_user.string('name')
#     schema_user.string('email', can_be_none=True)
#     schema_user.list('groups', SchemaString())
#     db_schema.hash('users', schema_user)
#     
#     db0 = {
#         'users': { 
#             'andrea': {
#                 'name': 'Andrea', 
#                 'email': 'info@co-design.science',
#                 'groups': ['group:admin', 'group:FDM'],
#             },
#             'pinco': {
#                 'name': 'Pinco Pallo', 
#                 'email': None,
#                 'groups': ['group:FDM'],
#             },
#         }
#     }
# 
#     db_schema.validate(db0)
#     db = deepcopy(db0)
#     events = []
#     viewmanager = ViewManager(db_schema) 
#     view = viewmanager.view(db)
#     def notify_callback(event):
#         logger.debug('\n' + yaml_dump(event))
#         events.append(event)
#     view._notify_callback = notify_callback
# 
#     users = view.users
#     u = users['andrea'] 
#     u.name = 'not Andrea'
#     u.email = None    
#     users['another'] = {'name': 'Another', 'email': 'another@email.com', 'groups':['group:extra']}
#     del users['another']
#     users.rename('pinco', 'pallo')
#     db2 = replay_events(viewmanager, db0, events) 
#     assert_equal(db, db2)
#     # check that we didn't modify the original
#     db2 = replay_events(viewmanager, db0, events) 
#     assert_equal(db, db2)
#     
#     disk_map_with_hint = DiskMap(db_schema)
#     disk_map_with_hint.hint_directory(db_schema['users'], pattern='%.user')
#     
#     disk_map_files_are_yaml= DiskMap(db_schema)
#     disk_map_files_are_yaml.hint_directory(db_schema['users'], pattern='%.yaml')
#     disk_map_files_are_yaml.hint_file_yaml(db_schema['users'].prototype)
#     disk_maps= {}
#     disk_maps['vanilla'] = DiskMap(db_schema)
#     disk_maps['with_hint'] = disk_map_with_hint
#     disk_maps['files_are_yaml'] = disk_map_files_are_yaml
#     return dict(db_schema=db_schema, db0=db0, events=events, db2=db2, disk_maps=disk_maps)
# # 
# @comptest
# def test_regular_schema():
#     ts = get_schema_and_data()
#     db_schema = ts['db_schema']
#     db0 = ts['db0']
#     db2 = ts['db2']
#     events = ts['events']
#     dm = ts['disk_maps']['vanilla']
#     out = 'out/test_translation/vanilla'
#     check_translation(db_schema, db0, events, db2, dm, out)
# 
# @comptest
# def test_disk_map_with_hint():
#     ts = get_schema_and_data()
#     db_schema = ts['db_schema']
#     db0 = ts['db0']
#     db2 = ts['db2']
#     events = ts['events']
#     dm = ts['disk_maps']['with_hint']
#     out = 'out/test_translation/with_hint'
#     check_translation(db_schema, db0, events, db2, dm, out)
#  
# 
# @comptest
# def test_disk_map_files_are_yaml():
#     ts = get_schema_and_data()
#     db_schema = ts['db_schema']
#     db0 = ts['db0']
#     db2 = ts['db2']
#     events = ts['events']
#     dm = ts['disk_maps']['files_are_yaml']
#     out = 'out/test_translation/files_are_yaml'
#     check_translation(db_schema, db0, events, db2, dm, out)
 
 
def check_translation(schema, data_rep0, data_events, data_rep1, disk_map, out):
    view_manager = ViewManager(schema)
    
    # first, make sure that the data is coherent
    data_rep1_ = replay_events(view_manager, data_rep0, data_events) 
    assert_data_equal(schema, data_rep1_, data_rep1)
    
    disk_events = []
    
    data_rep = deepcopy(data_rep0)
    disk_rep = disk_map.create_hierarchy_(schema, data_rep0)
    disk_rep0 = deepcopy(disk_rep)

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
         
        disk_rep_by_translation = disk_map.create_hierarchy_(schema, data_rep)
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
    
    logger.info('test ok, written on %s' % out)
    out = out + '_inverse'
    check_translation_inverse(schema, disk_rep0, disk_events, disk_rep, disk_map, out)
    
def check_translation_inverse(schema, disk_rep0, disk_events, disk_rep1, disk_map, out):
    view_manager = ViewManager(schema)
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
    
    write_file_('0-aa-disk_events.yaml', yaml_dump(disk_events))
    
    # first translate the data 
    disk_rep = deepcopy(disk_rep0)
    data_rep = disk_map.interpret_hierarchy_(schema, disk_rep)


    data_events = []
    i = 0
#     for i, disk_event in enumerate(disk_events):
    while disk_events:
        write_file(i, 'a-disk_rep', disk_rep.tree())
        write_file(i, 'b-data_rep', yaml_dump(data_rep))
        write_file(i, 'c-disk_event', yaml_dump(disk_events[0]))
        
        
        evs, disk_events_consumed = data_events_from_disk_event_queue(disk_map, schema, disk_rep, disk_events)
        
        if not evs:
            msg = 'The disk event resulted in 0 data events.'
            msg += '\n' + indent(yaml_dump(disk_events[0]), ' disk_event ')
            raise Exception(msg)
        
        write_file(i, 'c-disk_event-consumed', yaml_dump(disk_events_consumed))
        write_file(i, 'd-evs', yaml_dump(evs))
        
        data_events.extend(evs)
        
        # interpret disk event
        for disk_event in disk_events_consumed:
            disk_event_interpret(disk_rep, disk_event)
        write_file(i, 'e-disk_rep-modified', disk_rep.tree())
         
        try:
            data_rep_by_translation = disk_map.interpret_hierarchy_(schema, disk_rep)
        except IncorrectFormat as exc:
            s = traceback.format_exc(exc)
            logger.warning('Failed check')
            write_file(i, 'f-disk_rep-modified-translated-to-data_rep-FAIL', s)
        
        else:
            write_file(i, 'f-disk_rep-modified-translated-to-data_rep', 
                       yaml_dump(data_rep_by_translation))
        
        for data_event in evs:
            event_intepret(view_manager, data_rep, data_event)
        
        write_file(i, 'g-data_rep-with-evs-applied', yaml_dump(data_rep))
        
        msg = 'Disk event:\n'+ indent(yaml_dump(disk_events_consumed), ' disk_events_consumed ')
        msg += '\Data events:\n' + indent(yaml_dump(evs), ' events ')
        logger.debug(msg)
        
        h1 = data_hash_code(data_rep_by_translation)
        h2 = data_hash_code(data_rep)
        if h1 != h2:
            msg = 'Hash codes differ.'
            msg += '\n' + indent( yaml_dump(data_rep), 'data_rep ')
            msg += '\n' + indent( yaml_dump(data_rep_by_translation), 'data_rep_by_tr ')
            raise Exception(msg)
    
        i += 1
    logger.info('test_inverse ok, written on %s' % out)
    
if __name__ == '__main__':
    run_module_tests()
    