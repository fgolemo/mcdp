from mcdp_hdb.schema import Schema, SchemaString, SchemaList,\
    SchemaHash
from mcdp_hdb.disk_map import DiskMap
from mcdp_library.specs_def import specs
from mcdp.constants import MCDPConstants
# from abc import abstractmethod
# class ViewBase():
#     __
#     @abstractmethod
#     @staticmethod
#     def from_data(data):
#         pass
# 
# class UserInfo(ViewBase):
    
class DB():
    
    library = Schema()
    library.hash('images', SchemaString())
    library.hash('documents', SchemaString())
    
    with library.context_e('things') as things:
        for spec_name, spec in specs.items():  # @UnusedVariable
            thing = SchemaString()
            things.hash(spec_name, thing)

    shelf = Schema()
    with shelf.context_e('info') as shelf_info:
        shelf_info.string('desc_short', default=None)
        shelf_info.string('desc_long', default=None)
        shelf_info.list("authors", SchemaString(), default=[])
        shelf_info.list("dependencies", SchemaString(), default=[])
        acl_entry = SchemaList(SchemaString())
        shelf_info.list('acl', acl_entry, default=[])
    
    shelf.hash('libraries', library)
    
    repo = Schema()
    repo.hash('shelves', shelf)

    shelves = SchemaHash(shelf)

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
    
    dm = DiskMap()
    dm.hint_directory(shelves, pattern='%.mcdpshelf')
    dm.translate_children(shelf, {'info':'mcdpshelf.yaml'})
    dm.translate_children(shelf, {'libraries':None})
    dm.hint_file_yaml(shelf['info'])
    dm.hint_directory(shelf['libraries'], pattern='%.mcdplib')
    dm.hint_directory(users, pattern='%.mcdp_user') 
    dm.translate_children(user, {'info':'user.yaml'})
    dm.hint_file_yaml(user['info'])
    
    dm.translate_children(library, {'images': None})
    dm.hint_extensions(library['images'], MCDPConstants.exts_images)
    dm.translate_children(library, {'documents': None})
    dm.hint_directory(library['documents'], pattern='%.md')
    dm.translate_children(library, {'things': None})
    for spec_name, spec in specs.items():  # @UnusedVariable
        dm.translate_children(things, {spec_name: None})
        dm.hint_directory(things[spec_name], pattern='%%.%s' % spec.extension)

        