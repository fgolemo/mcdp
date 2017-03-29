import os
import shutil
import sys

from contracts.utils import indent
import yaml

from mcdp_hdb.main_db_schema import DB
from mcdp_library_tests.create_mockups import mockup_flatten, read_hierarchy,\
    write_hierarchy


def read(dirname):
    dm = DB.dm
    
    hierarchy = read_hierarchy(dirname)
    s = "\n".join(sorted(mockup_flatten(hierarchy)))
    print('These are the files found:\n%s' % indent(s, '  '))
    
    users_data = dm.interpret_hierarchy(DB.users, hierarchy)
    
    print ('users_data:\n%s' % yaml.dump(users_data))

    shelves_data = dm.interpret_hierarchy(DB.shelves, hierarchy)
#     print ('shelves_data:\n%s' % yaml.dump(shelves_data))
     
    if len(sys.argv) >= 3:
        # serialize
        h2 = dm.create_hierarchy(DB.shelves, shelves_data)
        where = sys.argv[2]
        print('Creating directory %s' % where)
        if os.path.exists(where):
            shutil.rmtree(where)    
        os.makedirs(where)
        print('Writing data there.')
        write_hierarchy(where, h2)
        with open(os.path.join(where+'.yaml'), 'w') as f:
            f.write(yaml.dump(shelves_data))
            
        
if __name__ == '__main__':
    read(sys.argv[1])