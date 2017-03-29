'''
    Application interface  <--> Memory <--> Disk abstraction <-> Git repo
    
    User proxy:
        data = Abstracted with classes
    
        knows:
        - actor 
        - permissions. (maybe)
        
    Application interface:
        data = Abstracted with classes   
            
        db.users['andrea'].set_email(new_email)
        or
        db.users['andrea'].email = new_email
        
        db.users['andrea'].affiliation = 'affiliation:ethz' # error if it doesn't exist
    
        
    Memory:
        ## data 
        Python struct that can be serialized with yaml

        It includes: dictionary, list, strings, numbers, datatypes
        
        It also has validation constraints. 
        
        Some examples of validation constraints:
        - not null (default unless "default=None")
        - for string:
            - email
            - startswith:<prefix> 
            - (validation) is an id in another structure
              valid:/users/
            (phone, address)
        
        ## diff
        
        A diff is a yaml-serializable structure:
        
            operation: append
            context: list of strings 
            data: any yaml structure
            
        Operations:
        
            list-append <parent-list> <data>
            list-delete <prent-list> <index>
            dict-set <parent-hash> <key> <value>
            dict-rename <parent-hash> <key> <new key>
            dict-delete <parent-hash>  
        
       
    On disk structure: converts everything to disk.
    
        changes:
            add_file(filename, content)
            delete_file(filename)
            rename_file(filename)
            modify_file(new_content)
    
    Git: graphs and commits
    
        changes = commits
        
        
         There are some helper functions to create diffs:
        
            add(('users', 'andrea'))
            set(('users', 'andrea', 'email'), new_email)
            delete(('users', 'andrea'))
            rename(('users', 'andrea'), 'andrea2')
            context('users', 'andrea', 'subscriptions'))
            append((), ':newindex')
            context(':newindex')
            
            append(('users', 'andrea', 'subscription'), ':newindex')
            
            set(('users', 'andrea', 'subscriptions', ':newindex'))
            
            
            add('users', 'andrea'):
                set(
        
        
'''
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
    
    
    
    