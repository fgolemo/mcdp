from copy import deepcopy

from contracts import contract

from mcdp_hdb import DiskMap
from mcdp_hdb import SchemaBase, Schema, SchemaString
from mcdp_hdb import SchemaHash
from mcdp_hdb import ViewManager
from mcdp_hdb import assert_data_events_consistent
from mcdp_hdb import event_interpret_
from mcdp_hdb.schema import SchemaList


class DataTestCase(object):
    

    @contract(schema=SchemaBase, events=list, disk_map=DiskMap)
    def __init__(self, schema, data1, events, data2, disk_map):   
        schema.validate(data1)
        schema.validate(data2) 
        assert_data_events_consistent(schema, data1, events, data2)
        self.data1 = data1
        self.events = events
        self.data2 = data2
        self.disk_map = disk_map
        self.schema = schema
        
    def get_data1(self):
        ''' Returns a copy of data1 (safe to modify) '''
        return deepcopy(self.data1)
    
    def get_data2(self):
        ''' Returns a copy of data2 (safe to modify) '''
        return deepcopy(self.data2)
    
    @contract(returns=SchemaBase)
    def get_schema(self):
        ''' returns the schema '''
        return self.schema

    @contract(returns=list)
    def get_events(self):
        return deepcopy(self.events)
    
    @contract(returns=DiskMap)
    def get_disk_map(self):
        return self.disk_map
    
    def enumerate_data_diff(self):
        ''' 
            Enumerates the transitions. Use as:
            for d1, data_event, d2 in enumerate_data_diff():
        ''' 
        data_i = self.get_data1()
        view_manager = ViewManager(self.schema)
        for e in self.events:
            current = deepcopy(data_i)
            view = view_manager.view(data_i)
            event_interpret_(view, e)
            yield current, e, data_i

@contract(returns='dict(str:isinstance(DataTestCase))')    
def testcases_minilibrary(): 
    schema = Schema()
    things = Schema()
    models = SchemaHash(SchemaString())
    posets = SchemaHash(SchemaString())
    things._add_child('models', models)
    things._add_child('posets', posets)
    schema._add_child('things', things)
    
    dm = DiskMap()
    dm.hint_directory(schema, translations={'things': None})
    dm.hint_directory(things, translations={'models': None, 'posets':None})
    dm.hint_directory(posets, pattern='%.poset')
    dm.hint_directory(models, pattern='%.mcdp')

    db0 = {
        'things': {
            'models': {
                'model1': 'mcdp {}',
            },
            'posets': {
                'poset1': 'poset {}',
            },     
        },
    }
    db = deepcopy(db0)

    viewmanager = ViewManager(schema) 
    view = viewmanager.view(db) 
    view.things.models['model2'] = 'mcdp { model2 }'
    del view.things.models['model1']

    events = view._events
    assert len(events) >= 2    
    assert_data_events_consistent(schema, db0,  events, db)


    res = {}
    res['minilib1'] = DataTestCase(schema, db0, events, db, dm)
    return res

@contract(returns='dict(str:isinstance(DataTestCase))')    
def testcases_TranslateNone(): 
    schema = Schema()
    user = Schema()
    user.string('name')
    schema.hash('users', user)
    
    db = {'users': {'andrea': {'name': 'Andrea'}, 'john': {'name':'John'}}}
    db0 = deepcopy(db)
    
    viewmanager = ViewManager(schema) 
    view = viewmanager.view(db) 

    users = view.users
    u = users['andrea'] 
    u.name = 'not-andrea'
    users['another'] = {'name': 'Another'}
    del users['another']
    users.rename('john', 'jack') 
    
    events = view._events
    assert len(events) > 2
    
    assert_data_events_consistent(schema, db0,  events, db)
    
    disk_map_with_hint = DiskMap()
    disk_map_with_hint.hint_directory(schema, translations={'users': None})
#     disk_map_with_hint.hint_directory(schema['users'], pattern='%.user')

    res = {}
    res['x_normal'] = DataTestCase(schema, db0, events, db, DiskMap())
    res['x_none'] = DataTestCase(schema, db0, events, db, disk_map_with_hint)
    return res

@contract(returns='dict(str:isinstance(DataTestCase))')    
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
    
    viewmanager = ViewManager(db_schema) 
    view = viewmanager.view(db) 

    users = view.users
    u = users['andrea'] 
    u.name = 'not Andrea'
    u.email = None    
    users['another'] = {'name': 'Another', 'email': 'another@email.com', 'groups':['group:extra']}
    del users['another']
    users.rename('pinco', 'pallo') 
    
    events = view._events
    
    assert len(events) > 3, events
    
    assert_data_events_consistent(db_schema, db0, events, db)
    
    disk_map_with_hint = DiskMap()
    disk_map_with_hint.hint_directory(db_schema['users'], pattern='%.user')
    
    disk_map_files_are_yaml= DiskMap()
    disk_map_files_are_yaml.hint_directory(db_schema['users'], pattern='%.yaml')
    disk_map_files_are_yaml.hint_file_yaml(db_schema['users'].prototype)
    disk_maps= {}
    disk_maps['vanilla'] = DiskMap()
    disk_maps['with_hint'] = disk_map_with_hint
    disk_maps['files_are_yaml'] = disk_map_files_are_yaml
    
    res = {}
    for k in disk_maps:
        dm = disk_maps[k]
        res[k] = DataTestCase(db_schema, db0, events, db, dm)
    return res



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

@contract(returns='dict(str:isinstance(DataTestCase))')    
def testcases_arrays_inside_yaml():
    
    db_schema = Schema()
    user = Schema()
    user._add_child('name', SchemaString())
    user._add_child('groups', SchemaList(SchemaString()))
    db_schema.hash('users', user)
    
    db0 = {
        'users': {
            'andrea': {
                'name': 'Andrea',
                'groups': ['one', 'two'],
            }
        }
    }

    db_schema.validate(db0)
    
    operation_sequences = []
    def add_seq(f):
        operation_sequences.append(f)
        return f
    
    @add_seq
    def seq_set(view):
        view.users['andrea'].name = 'new name'
    @add_seq
    def seq_append(view):
        view.users['andrea'].groups.append('newgroup')
        
    dm = DiskMap()
    dm.hint_file_yaml(user)
    disk_maps= {}
    disk_maps['vanilla'] = DiskMap()
    disk_maps['yaml'] = dm

    prefix = 'array_inside_yaml'
    
    res = get_combinations(db_schema, db0, prefix, operation_sequences, disk_maps)
    return res

def get_combinations(db_schema, db0, prefix, operation_sequences, disk_maps):
    res = {}
    
    for s in operation_sequences:
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
