# -*- coding: utf-8 -*-
from copy import deepcopy
import os
import shutil
import traceback

from contracts.utils import indent

from comptests.registrar import run_module_tests
from mcdp import logger
from mcdp_hdb import ViewManager, data_hash_code, disk_event_interpret, disk_events_from_data_event, IncorrectFormat, data_events_from_disk_event_queue, event_intepret, assert_equal_disk_rep
from mcdp_hdb.diskrep_utils import assert_disk_events_consistent
from mcdp_hdb.memdata_utils import assert_data_events_consistent
from mcdp_utils_misc import yaml_dump


def l(what, s):
    logger.info('\n' + indent(s, '%010s │  ' % what))

 
def check_translation_memdata_to_diskrep(schema, data_rep0, data_events, data_rep1, disk_map, out):
    view_manager = ViewManager(schema)
    
    # first, make sure that the data is coherent
    assert_data_events_consistent(schema, data_rep0, data_events, data_rep1)
    
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
        
        assert_equal_disk_rep(disk_rep_by_translation, disk_rep)
      
    
    logger.info('test ok, written on %s' % out)
    return dict(disk_rep0=disk_rep0, disk_events=disk_events, disk_rep=disk_rep)

def check_translation_diskrep_to_memdata(schema, disk_rep0, disk_events, disk_rep1, disk_map, out):
    disk_events = deepcopy(disk_events)
    assert_disk_events_consistent(disk_rep0, disk_events, disk_rep1)
    
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
    data_rep0 = deepcopy(data_rep)
    data_events = []
    i = 0 
    while disk_events:
        write_file(i, 'a-disk_rep', disk_rep.tree())
        write_file(i, 'b-data_rep', yaml_dump(data_rep))
        write_file(i, 'c-disk_event', yaml_dump(disk_events[0]))
        
        disk_events0 = deepcopy(disk_events)
        evs, disk_events_consumed = data_events_from_disk_event_queue(disk_map, schema, disk_rep, disk_events)
        
        logger.debug('This disk_event become this data_event:' +
                     '\n'+indent(yaml_dump(disk_events0), 'disk_events : ')+
                     '\n'+indent(yaml_dump(evs), 'data_events : '))
        
        # tmp - interpret now 
        data0 = deepcopy(data_rep)
        for data_event in evs:
            event_intepret(view_manager, data0, data_event)
        # tmp 
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
            logger.error('Failed check:\n%s' %s)
            write_file(i, 'f-disk_rep-modified-translated-to-data_rep-FAIL', s)
            data_rep_by_translation = None
        else:
            write_file(i, 'f-disk_rep-modified-translated-to-data_rep', 
                       yaml_dump(data_rep_by_translation))
        
        for data_event in evs:
            event_intepret(view_manager, data_rep, data_event)
        
        write_file(i, 'g-data_rep-with-evs-applied', yaml_dump(data_rep))
        
        msg = 'Disk event:\n'+ indent(yaml_dump(disk_events_consumed), ' disk_events_consumed ')
        msg += '\nData events:\n' + indent(yaml_dump(evs), ' events ')
        logger.debug(msg)
        
        if data_rep_by_translation is not None:
            h1 = data_hash_code(data_rep_by_translation)
            h2 = data_hash_code(data_rep)
            if h1 != h2:
                msg = 'Hash codes differ.'
                msg += '\n' + indent( yaml_dump(data_rep), 'data_rep ')
                msg += '\n' + indent( yaml_dump(data_rep_by_translation), 'data_rep_by_tr ')
                raise Exception(msg)
        else:
            raise Exception()
        i += 1
    logger.info('test_inverse ok, written on %s' % out)
    return dict(data_rep0=data_rep0, data_events=data_events, data_rep=data_rep)
    
if __name__ == '__main__':
    run_module_tests()
    