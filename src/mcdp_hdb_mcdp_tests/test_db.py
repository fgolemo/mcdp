import os
import shutil
import sys

from contracts.utils import indent
import yaml

from mcdp.logs import logger
from mcdp_hdb import ProxyDirectory
from mcdp_hdb import disk_events_from_data_event
from mcdp_hdb_mcdp.main_db_schema import DB
from mcdp_utils_misc import yaml_dump


def read_as_user_db(dirname):
    dm = DB.dm
    
    hierarchy = ProxyDirectory.from_disk(dirname)
    
    logger.info('These are the files found:\n%s' % indent(hierarchy.tree(), '  '))
    
    user_db_schema = DB.user_db
    user_db_data = dm.interpret_hierarchy_(user_db_schema, hierarchy)
    
    logger.debug('user_db schema: \n' + str(user_db_schema) )
    logger.debug('user_db:\n' + indent(yaml_dump(user_db_data), ' > '))
    
    DB.user_db.validate(user_db_data)
    
    user_db_view = DB.view_manager.create_view_instance(user_db_schema, user_db_data)
    user_db_view.set_root()
    return user_db_view

    if False:
        print ('users_data:\n%s' % yaml.dump(users_data))
    
        shelves_data = dm.interpret_hierarchy_(DB.shelves, hierarchy)
        DB.shelves.validate(shelves_data)
        
        #print ('shelves_data:\n%s' % yaml.dump(shelves_data))
         
        if len(sys.argv) >= 3:
            # serialize
            h2 = dm.create_hierarchy_(DB.shelves, shelves_data)
            where = sys.argv[2]
            print('Creating directory %s' % where)
            if os.path.exists(where):
                shutil.rmtree(where)    
            os.makedirs(where)
            print('Writing data there.')
            h2.to_disk(where)
            with open(os.path.join(where+'.yaml'), 'w') as f:
                f.write(yaml.dump(shelves_data))
            
         
if __name__ == '__main__':
    user_db_view = read_as_user_db(sys.argv[1])
    events = []    
    def notify_callback(event): 
        events.append(event)
    user_db_view._notify_callback = notify_callback
        
    user = user_db_view.best_match(None, None, 'censi@mit.edu')
    print('user: %s' % user)
    user.info.email = 'new email'
    user.info.groups.append('group:new-group')
    print yaml_dump(events)
    
    for data_event in events:
        dm = DB.dm
        disk_event = disk_events_from_data_event(disk_map=dm, 
                                                 schema=user_db_view._schema, 
                                                 data_rep=user_db_view._data, 
                                                 data_event=data_event)
        print yaml_dump(disk_event)
         
    
     
    
    