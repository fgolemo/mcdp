from mcdp_hdb_mcdp.cli_load_all import iterate_all
from mcdp_web.environment import cr2e
from mcdp_web.utils0 import add_std_vars_context


class AppSearch():
    
    @add_std_vars_context
    @cr2e
    def view_search(self, e):  # @UnusedVariable
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
            name = f"User {username} ({user_struct.info.name})"
            url = f"/users/{username}/"
            icon = '''
            <img id='gravatar2' src='/users/%s/small.jpg'/>
    <style>
    img#gravatar2 {
        width: 13pt;
        margin-bottom: -4pt;
    }
    </style>''' % username
            desc = ff"{s} User <a href="" class="highlight"><code>{icon}</code><a> ({url})"
            d = {'name': name,
                 'type': 'user',
                 'desc': desc,
                 'url': url}
            data.append(d)
            
        for repo_name, repo in db_view.repos.items():
            name = f"Repository {repo_name}" 
            url = f"/repos/{repo_name}/"
            desc = f"{s} Repository <a href="" class="highlight"><code>%s</code></a>' %  (
                res['icon_repo'], url, repo_name)
            d = {'name': name, 
                 'type': 'repo',
                 'desc': desc,
                 'url': url}
            data.append(d)
        
        for repo_name, repo in db_view.repos.items():
            for shelf_name, shelf in repo.shelves.items():
                name = f"Shelf {shelf_name} ({repo_name})" 
                url = f"/repos/{repo_name}/shelves/{shelf_name}/"
                desc = f"{s} Shelf <a href=""  class="highlight"><code>%s</code></a> (Repo <code>%s</code>)' % (
                    res['icon_shelf'], url, shelf_name, repo_name)
                d = {'name': name, 
                     'desc': desc,
                     'type': 'shelf',
                     'url': url}
                data.append(d)
            
        for repo_name, repo in db_view.repos.items():
            for shelf_name, shelf in repo.shelves.items():
                for library_name, _ in shelf.libraries.items():
                    url = f"/repos/{repo_name}/shelves/{shelf_name}/libraries/{library_name}/"
                    name = f"Library {library_name} (Repo {repo_name}, shelf {shelf_name})" 
                    desc = f"{s} Library <a href=""  class="highlight"><code>%s</code></a> (Repo <code>%s</code>, shelf <code>%s</code>)' %\
                         (res['icon_library'], url, library_name, repo_name, shelf_name)
                    d = {'name': name, 
                         'type': 'library',
                         'desc': desc,
                         'url': url}
                    data.append(d)
            
    
        stuff = list(iterate_all(db_view))
        for e in stuff:
            name = f"{e.spec_name} {e.thing_name} (Repo {e.repo_name}, shelf {e.shelf_name}, library {e.library_name})" 
            url = f"/repos/{e.repo_name}/shelves/{e.shelf_name}/libraries/{e.library_name}/{e.spec_name}/{e.thing_name}/views/syntax/"
            icon = res[f"icon_{e}".spec_name]
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




