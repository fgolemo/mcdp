from mcdp_hdb.schema import Schema, SchemaString, NOT_PASSED, SchemaList,\
    SchemaHash
from mcdp_hdb.disk_map import DiskMap
from mcdp_library.specs_def import specs

def schema_library():
    library = Schema()
    for spec_name, spec in specs.items():  # @UnusedVariable
        thing = SchemaString()
        library.hash(spec_name, thing)
    return library

def schema_shelf():
    shelf = Schema()
    with shelf.context_e('info') as shelf_info:
        shelf_info.string('desc_short', default=None)
        shelf_info.string('desc_long', default=None)
        acl_entry = SchemaList(SchemaString())
        shelf_info.list('acl', acl_entry, default=[])
    library = schema_library()
    shelf.hash('libraries', library, default={})
    return shelf
    
def schema_repo():
    repo = Schema()
    shelf = schema_shelf()
    repo.hash('shelves', shelf)
    return repo
    
def schema_users():
    user = Schema() 
    with user.context_e('info') as user_info:
        user_info.string('name')
        user_info.date('account_created', default=None)
        user_info.date('account_last_active', default=None)
        user_info.string('website', default=None)
        user_info.string('affiliation', default=None)
        user_info.list('subscriptions', SchemaString(), default=[])
        user_info.string('email', default=None)
        with user_info.list_e('authentication_ids', default=[]) as auth_id:
            auth_id.string('provider')
            auth_id.string('id', default=None)
            auth_id.string('password', default=None)
        user_info.list('groups', SchemaString(), default=[])
    users = SchemaHash(user)
    return users

def schema_users_hints(schema_users):
    dm = DiskMap(schema_users)
    users = schema_users
    user = users.prototype
    dm.hint_directory(users, pattern='%.mcdp_user') 
    dm.translate_children(user, {'info':'user.yaml'})
    dm.hint_file_yaml(user['info'])
#     shelves = user['shelves']
#     shelf = shelves.prototype
#     dm.hint_directory(shelves, pattern='%.mcdpshelf')
#     dm.translate_children(shelf, {'info':'mcdpshelf.yaml'})
    return dm
