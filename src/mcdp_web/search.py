from mcdp_web.utils0 import add_std_vars_context
from mcdp_web.environment import cr2e

from mcdp_hdb_mcdp.cli_load_all import iterate_all
from mcdp.logs import logger
from mcdp_utils_misc.my_yaml import yaml_dump


class AppSearch():
    
    @add_std_vars_context
    @cr2e
    def view_search(self, e):
        res = {
            
        }
        return res

    @cr2e
    def view_search_query(self, e):
        from mcdp_web.main import WebApp
        db_view= WebApp.singleton.hi.db_view  # @UndefinedVariable
        root = self.get_root_relative_to_here(e.request)
        
        data = []
        
        for username, user_struct in db_view.user_db.users.items():
            name = 'User %s (%s)' % (username, user_struct.info.name)
            url = '/users/%s/' % username
            desc = 'User <a href="%s" class="highlight"><code>%s</code><a> (%s)' % (url, username, user_struct.info.name)
            d = {'name': name,
                 'type': 'user',
                 'desc': desc,
                 'url': url}
            data.append(d)
            
        for repo_name, repo in db_view.repos.items():
            name = 'Repository %s' % (repo_name) 
            url = '/repos/%s/' % (repo_name)
            desc = 'Repository <a href="%s" class="highlight"><code>%s</code></a>' %  (url, repo_name)
            d = {'name': name, 
                 'type': 'repo',
                 'desc': desc,
                 'url': url}
            data.append(d)
        
        for repo_name, repo in db_view.repos.items():
            for shelf_name, shelf in repo.shelves.items():
                name = 'Shelf %s (%s)' % (shelf_name, repo_name) 
                url = '/repos/%s/shelves/%s/' % (repo_name, shelf_name)
                desc = 'Shelf <a href="%s"  class="highlight"><code>%s</code></a> (Repo <code>%s</code>)' % (url, shelf_name, repo_name)
                d = {'name': name, 
                     'desc': desc,
                     'type': 'shelf',
                     'url': url}
                data.append(d)
            
        for repo_name, repo in db_view.repos.items():
            for shelf_name, shelf in repo.shelves.items():
                for library_name, library in shelf.libraries.items():
                    url = '/repos/%s/shelves/%s/libraries/%s/' % (repo_name, shelf_name, library_name)
                    name = 'Library %s (Repo %s, shelf %s)' % (library_name, repo_name, shelf_name) 
                    desc = 'Library <a href="%s"  class="highlight"><code>%s</code></a> (Repo <code>%s</code>, shelf <code>%s</code>)' %\
                         (url, library_name, repo_name, shelf_name)
                    d = {'name': name, 
                         'type': 'library',
                         'desc': desc,
                         'url': url}
                    data.append(d)
            
    
        stuff = list(iterate_all(db_view))
        for e in stuff:
            name = '%s %s (Repo %s, shelf %s, library %s)' % (e.spec_name, e.thing_name, e.repo_name, e.shelf_name, e.library_name) 
            url = '/repos/%s/shelves/%s/libraries/%s/things/%s/%s/view/syntax/' % (e.repo_name, e.shelf_name, e.library_name, e.spec_name, e.thing_name)
            
            desc = '''
                %s <a href="%s" class='highlight'><code>%s</code></a>
                (Repo <code>%s</code>, shelf <code>%s</code>, library <code>%s</code>)
            ''' % (e.spec_name, url, e.thing_name, e.repo_name, e.shelf_name, e.library_name)
            d = {'name': name, 
                 'type': 'thing',
                 'spec_name':  e.spec_name,
                 'desc': desc ,
                 'url': url}
            data.append(d)
        
        
        for d in data:
            u =  d['url']
            d['url'] = root + u
            d['desc'] = d['desc'].replace(u, d['url'])
            
        
        res = {'data': data}
#         print yaml_dump(res)
        
        return res




