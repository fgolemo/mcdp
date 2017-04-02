import os
import shutil
import sys


import yaml

from mcdp_hdb.main_db_schema import DB
from mcdp_hdb.disk_struct import ProxyDirectory
from contracts.utils import indent


def read(dirname):
    dm = DB.dm
    
    hierarchy = ProxyDirectory.from_disk(dirname)
    
    print('These are the files found:\n%s' % indent(hierarchy.tree(), '  '))
    
    users_data = dm.interpret_hierarchy(DB.users, hierarchy)
    DB.users.validate(users_data)
    
    print ('users_data:\n%s' % yaml.dump(users_data))

    shelves_data = dm.interpret_hierarchy(DB.shelves, hierarchy)
    DB.shelves.validate(shelves_data)
    
    #print ('shelves_data:\n%s' % yaml.dump(shelves_data))
     
    if len(sys.argv) >= 3:
        # serialize
        h2 = dm.create_hierarchy(DB.shelves, shelves_data)
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
    read(sys.argv[1])
    
    
    