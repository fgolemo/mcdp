from copy import deepcopy

from contracts import contract
from kiva.tests.agg.image_test_case import assert_equal

from mcdp_hdb import ViewManager
from mcdp_hdb import DiskMap
from mcdp_hdb import replay_events
from mcdp_hdb import SchemaBase, Schema, SchemaString


class DataTestCase(object):

    def __init__(self, schema, data1, events, data2):    
        self.data1 = data1
        self.events = events
        self.data2 = data2
        
        # verify consistency
        db1 = deepcopy(data1)
        for event in events:
            `(view, event)
            event_intepret(view_manager, db0, event)
        msg = '\nAfter playing event:\n'
        msg += indent(yaml_dump(event), '   event: ')
        msg += '\nthe DB is:\n'
        msg += indent(yaml_dump(db0), '   db: ')
        logger.debug(msg)
    return db0


    @contract(returns=SchemaBase)
    def get_schema(self):
        ''' returns the schema '''
        return self._schema
    
    def enumerate_data_diff(self):
        ''' 
            Enumerates the transitions. Use as:
            
            for d1, data_event, d2 in enumerate_data_diff():
        
        ''' 
        
@contract(returns=DataTestCase)    
def testcases_SimpleUserDB():
    
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
        #logger.debug('\n' + yaml_dump(event))
        events.append(event)
    view._notify_callback = notify_callback

    users = view.users
    u = users['andrea'] 
    u.name = 'not Andrea'
    u.email = None    
    users['another'] = {'name': 'Another', 'email': 'another@email.com', 'groups':['group:extra']}
    del users['another']
    users.rename('pinco', 'pallo')
    db2 = replay_events(viewmanager, deepcopy(db0), events) 
    assert_equal(db, db2)
    # check that we didn't modify the original
    db2 = replay_events(viewmanager, deepcopy(db0), events) 
    assert_equal(db, db2)
    
    disk_map_with_hint = DiskMap(db_schema)
    disk_map_with_hint.hint_directory(db_schema['users'], pattern='%.user')
    
    disk_map_files_are_yaml= DiskMap(db_schema)
    disk_map_files_are_yaml.hint_directory(db_schema['users'], pattern='%.yaml')
    disk_map_files_are_yaml.hint_file_yaml(db_schema['users'].prototype)
    disk_maps= {}
    disk_maps['vanilla'] = DiskMap(db_schema)
    disk_maps['with_hint'] = disk_map_with_hint
    disk_maps['files_are_yaml'] = disk_map_files_are_yaml
    return dict(db_schema=db_schema, db0=db0, events=events, db2=db2, disk_maps=disk_maps)