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
        
        res = {}
        res['icon_repo'] = '&#9730;'
        res['icon_repo_css'] = r'\9730;'
        res['icon_library'] = '&#x1F4D6;'
        res['icon_library_css'] = r'\1F4D6'
        res['icon_shelf'] = '&#x1F3DB;'
        res['icon_shelf_css'] = r'\1F3DB'
    
        res['icon_models'] = '&#10213;'
        res['icon_templates'] = '&#x2661;'
        res['icon_posets'] = '&#x28B6;'
        res['icon_values'] = '&#x2723;'
        res['icon_primitivedps'] = '&#x2712;'
    
        res['icon_documents'] = '&#128196;'
        
        data = []
        
        for username, user_struct in db_view.user_db.users.items():
            name = 'User %s (%s)' % (username, user_struct.info.name)
            url = '/users/%s/' % username
            icon = '''
            <img id='gravatar2' src='/users/%s/small.jpg'/>
    <style>
    img#gravatar2 {
        width: 13pt;
        margin-bottom: -4pt;
    }
    </style>''' % username
            desc = '%s User <a href="%s" class="highlight"><code>%s</code><a> (%s)' % (icon, url, username, user_struct.info.name)
            d = {'name': name,
                 'type': 'user',
                 'desc': desc,
                 'url': url}
            data.append(d)
            
        for repo_name, repo in db_view.repos.items():
            name = 'Repository %s' % (repo_name) 
            url = '/repos/%s/' % (repo_name)
            desc = '%s Repository <a href="%s" class="highlight"><code>%s</code></a>' %  (
                res['icon_repo'], url, repo_name)
            d = {'name': name, 
                 'type': 'repo',
                 'desc': desc,
                 'url': url}
            data.append(d)
        
        for repo_name, repo in db_view.repos.items():
            for shelf_name, shelf in repo.shelves.items():
                name = 'Shelf %s (%s)' % (shelf_name, repo_name) 
                url = '/repos/%s/shelves/%s/' % (repo_name, shelf_name)
                desc = '%s Shelf <a href="%s"  class="highlight"><code>%s</code></a> (Repo <code>%s</code>)' % (
                    res['icon_shelf'], url, shelf_name, repo_name)
                d = {'name': name, 
                     'desc': desc,
                     'type': 'shelf',
                     'url': url}
                data.append(d)
            
        for repo_name, repo in db_view.repos.items():
            for shelf_name, shelf in repo.shelves.items():
                for library_name, _ in shelf.libraries.items():
                    url = '/repos/%s/shelves/%s/libraries/%s/' % (repo_name, shelf_name, library_name)
                    name = 'Library %s (Repo %s, shelf %s)' % (library_name, repo_name, shelf_name) 
                    desc = '%s Library <a href="%s"  class="highlight"><code>%s</code></a> (Repo <code>%s</code>, shelf <code>%s</code>)' %\
                         (res['icon_library'], url, library_name, repo_name, shelf_name)
                    d = {'name': name, 
                         'type': 'library',
                         'desc': desc,
                         'url': url}
                    data.append(d)
            
    
        stuff = list(iterate_all(db_view))
        for e in stuff:
            name = '%s %s (Repo %s, shelf %s, library %s)' % (e.spec_name, e.thing_name, e.repo_name, e.shelf_name, e.library_name) 
            url = '/repos/%s/shelves/%s/libraries/%s/%s/%s/views/syntax/' % (e.repo_name, e.shelf_name, e.library_name, e.spec_name, e.thing_name)
            icon = res['icon_%s' % e.spec_name]
            t = {'models': 'Model',
                 'templates': 'Template',
                 'values': 'Value',
                 'posets': 'Poset',
                 'primitivedps': 'Primitive DP '}
            what = t[e.spec_name]
            desc = '''
                %s %s <a href="%s" class='highlight'><code>%s</code></a>
                (Repo <code>%s</code>, shelf <code>%s</code>, library <code>%s</code>)
            ''' % (icon, what, url, e.thing_name, e.repo_name, e.shelf_name, e.library_name)
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




