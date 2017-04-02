import os
import shutil

from contracts.utils import raise_desc, indent
import yaml

from comptests.registrar import comptest, run_module_tests
from mcdp import logger
from mcdp_hdb.disk_map import DiskMap
from mcdp_hdb.disk_struct import ProxyDirectory
from mcdp_hdb.main_db_schema import DB


@comptest
def check_db_schema_custom():
    schema = DB.shelves
    run_tests(schema, DB.dm, 'custom')

@comptest
def check_db_schema_default():
    schema = DB.shelves
    dm = DiskMap(schema) # no customization
    run_tests(schema, dm, 'default')
    
def run_tests(schema, dm, name):
    data1 = schema.generate()
    schema.validate(data1)
    print('This is the schema:\n%s' % indent(str(schema), ' ~ '))
    
    print('This is the data:\n%s' % indent(yaml.dump(data1), ' > '))
    # serialize
    h = dm.create_hierarchy_(schema, data1)
    
    print('This is the data serialized:\n')
    
    print(indent(h.tree(), ' > '))
    
    where = os.path.join('test_hdb1', name)
    
    print('Creating directory %s' % where)
    if os.path.exists(where):
        shutil.rmtree(where)    
    os.makedirs(where)
    print('Writing data there.')
    h.to_disk(where)
    
    print('Reading it back.')
    h2 = ProxyDirectory.from_disk(where)
    print('These are the files found:\n%s' % indent(h2.tree(), '  '))
    
    # now re-interpret the data
    data2 = dm.interpret_hierarchy_(schema, h2)
    
    if data1 != data2:
        print ('data1:\n%s' % yaml.dump(data1))
        print('data2:\n%s' % yaml.dump(data2)) 
        msg = 'De-serialization did not work'
        raise_desc(Exception, msg, data1=data1,data2=data2)
        
    logger.info('test_hdb1 ok')
    
if __name__ == '__main__':
    run_module_tests()
