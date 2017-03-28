
class SpecInterface():
    def add(self, field_name, spec):
        pass

class SpecString():
    pass

class Spec():
    def __init__(self):
        pass
    
    def string(self, field_name):
        self.add(field_name, SpecString())
    
    def list(self, field_name):
        pass
    

def define_schema():
    # Define the shelf
    Root = ()
    
    Shelf_contents = Root() 
    for spec_name in ['models','posets']:
        Shelf_contents.c('models', key='spec_name').hash('{thing_name}').string('contents')
    Shelf_contents.c('documents').hash('{thing_name}').string('contents')
    image = Shelf_contents.c('images').hash('{image_name}')
    image.string('contents')
    image.string('content_type')
    
    Root = ()
    users = Root.c('users')
    user = users.hash('{user_name}.mcdp_user')
    user.string('name')
    user.string('email')
    user.list('authentication_ids')
    user.list('images')
    affiliation = user.list('affiliations')
    affiliation.string('name')
    affiliation.string('address')
    affiliation.string('website')
    repos = Root.c('repos')
    repo = repos.hash('{repo_name}')
    shelves = repo.c('shelves')
    shelf = shelves.hash('{shelf_name}.mcdp_shelf')
    versions = shelf.c('versions')
    version = shelf.hash('{version}')
    
#     
#     
# def test1():
#     schema = define_schema()
#     root = schema.instance()
#     
#     # changes:
#     #  add-key
#     #  delete-index
#     #  delete-key
#     #  create
#     CC = []
#     
#     ch_push('users')
#     ch_another()
#     ch_set_string('name', 'Andrea Censi')
#     ch_set_string('email', 'andrea@censi.org')
#     ch_another('authentication_ids')
#     ch_set_string('provider', 'password')
#     ch_set_string('password', 'xxx')
#     ch_append('authentication_ids')
#     ch_set('andrea')
#     Context('users/andrea', [
#             SetString('name', 'Andrea Censi'),
#             Context('andrea')
#     ]
#     
#     ch_push('users')
#     ch_another()
#     ch_set_string('name', 'Andrea Censi')
#     ch_set_string('email', 'andrea@censi.org')
#     ch_another('authentication_ids')
#     ch_set_string('provider', 'password')
#     ch_set_string('password', 'xxx')
#     ch_append('authentication_ids')
#     ch_set('andrea')
#     Context('users/andrea', [
#             SetString('name', 'Andrea Censi'),
#             Context('andrea')
#     ]
#     
    
    
    
    