from mcdp_hdb.schema import Schema
from mcdp_hdb.disk_map import DiskMap

def get_mcdp_db_1_schema():
    
    db_with_users = Schema()
    
    with db_with_users.hash_e('users') as user: 
        with user.context_e('info') as user_info:
            user_info.string('name')
            user_info.string('email', default=None)
            with user_info.list_e('authentication_ids') as auth_id:
                auth_id.string('provider')
                auth_id.string('provider_uid')
        
    return db_with_users

def get_mcdp_db_1_representation(schema):
    dm = DiskMap(schema)
    users = schema['users']
    user = users.prototype
    dm.hint_directory(users, pattern='%.mcdp_user') 
    dm.hint_file_yaml(user['info'])
    return dm
