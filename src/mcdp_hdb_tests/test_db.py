import sys

from contracts.utils import indent
import yaml
 
from mcdp_library_tests.create_mockups import mockup_flatten, read_hierarchy
from mcdp_hdb.main_db_schema import schema_users, schema_users_hints




def read(dirname):
    schema = schema_users()
    dm = schema_users_hints(schema)
    h2 = read_hierarchy(dirname)
    s = "\n".join(mockup_flatten(h2))
    
    print('These are the files found:\n%s' % indent(s, '  '))
    data = dm.interpret_hierarchy(h2)
    print ('data:\n%s' % yaml.dump(data))

if __name__ == '__main__':
    read(sys.argv[1])