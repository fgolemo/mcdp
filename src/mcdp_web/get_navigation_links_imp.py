
from mcdp.constants import MCDPConstants
from mcdp.logs import logger
from mcdp_shelf import PRIVILEGE_WRITE
from mcdp_utils_misc import natural_sorted
from mcdp_library.specs_def import SPEC_VALUES, SPEC_POSETS, SPEC_TEMPLATES, SPEC_MODELS

def get_navigation_links_context(e):
    """ Pass this as "navigation" to the page. """
    if e.shelf is not None:
        shelf_write_permission = e.shelf.get_acl().allowed2(PRIVILEGE_WRITE, e.user)
    else:
        shelf_write_permission = False
        
    if e.library is not None:
        if not e.library_name in e.session.libraries:
            msg = 'The library %r is not available. Maybe a permission issue?' % e.library_name
            msg += '\n context: %s' % e.context.show_ancestors()
            logger.error(msg) 

    d = {}
    
    d['repo_name'] = e.repo_name
    d['repo'] = e.repo
    d['repos'] = e.app.repos

    d['shelf_name'] = e.shelf_name
    d['shelf'] = e.shelf
    d['shelf_write_permission'] = shelf_write_permission
    d['shelves_available'] = e.session.get_shelves_available()
    d['shelves_used'] = e.session.get_shelves_used()
    d['shelves_unused'] = {}
    for x in d['shelves_available']:
        if not x in  d['shelves_used']:
            d['shelves_unused'][x] = d['shelves_available'][x] 
    
    d['library_name'] = e.library_name

    d['current_view'] = e.view_name 

    if e.library is not None:
        
        VIEW_EDITOR = 'views/edit_fancy/'
        VIEW_DELETE = ':delete'
        VIEW_SYNTAX = 'views/syntax/'
        
        p = '/repos/{repo_name}/shelves/{shelf_name}/libraries/{library_name}/'
        library_url = e.app.make_relative(e.request, p.format(**d))

        documents = e.library._list_with_extension(MCDPConstants.ext_doc_md)

        d['documents'] = []
        for id_doc in documents:
            url = library_url + '%s.html' %  id_doc
            desc = dict(id=id_doc,id_document=id_doc, name=id_doc, url=url, current=False)
            d['documents'].append(desc)

        
        d[SPEC_MODELS] = []
        models = e.library.list_spec(SPEC_MODELS)
        for _ in natural_sorted(models):
            is_current = (e.spec_name == SPEC_MODELS) and (e.thing_name == _)

            url0 =  library_url + SPEC_MODELS + '/' + _ + '/'
            url = url0 + VIEW_SYNTAX
            url_edit = url0 + VIEW_EDITOR  
            url_delete = url0 + VIEW_DELETE  
             
            name = "Model %s" % _
            desc = dict(id=_, id_ndp=_, name=name, url=url, url_edit=url_edit, 
                        url_delete=url_delete, current=is_current)
            d[SPEC_MODELS].append(desc) 
       
        templates = e.library.list_spec(SPEC_TEMPLATES)
        d[SPEC_TEMPLATES] = []
        for _ in natural_sorted(templates):
            is_current = (e.spec_name == SPEC_TEMPLATES) and (e.thing_name == _)

            url0 =  library_url + SPEC_TEMPLATES + '/' + _ + '/'
            url = url0 + VIEW_SYNTAX
            url_edit = url0 + VIEW_EDITOR  
            url_delete = url0 + VIEW_DELETE  
            
            name = "Template: %s" % _
            desc = dict(id=_, name=name, url=url, current=is_current, url_edit=url_edit, url_delete=url_delete)
            d[SPEC_TEMPLATES].append(desc)

        
        posets = e.library.list_spec(SPEC_POSETS)
        d[SPEC_POSETS] = []
        for _ in natural_sorted(posets):
            is_current = (e.spec_name == SPEC_POSETS) and (e.thing_name == _)
            
            url0 =  library_url + SPEC_POSETS + '/' + _ + '/'
            url = url0 + VIEW_SYNTAX
            url_edit = url0 + VIEW_EDITOR  
            url_delete = url0 + VIEW_DELETE  

            name = "Poset: %s" % _
            desc = dict(id=_, name=name, url=url, current=is_current, url_edit=url_edit, url_delete=url_delete)
            d[SPEC_POSETS].append(desc)

        values =e.library.list_spec(SPEC_VALUES)
        d[SPEC_VALUES] = []
        for _ in natural_sorted(values):
            is_current = (e.spec_name == SPEC_VALUES) and (e.thing_name == _)
            
            url0 =  library_url + SPEC_VALUES + '/' + _ + '/'
            url = url0 + VIEW_SYNTAX
            url_edit = url0 + VIEW_EDITOR  
            url_delete = url0 + VIEW_DELETE  

            name = "Value: %s" % _
            desc = dict(id=_, name=name, url=url, current=is_current, url_edit=url_edit, url_delete=url_delete)
            d[SPEC_VALUES].append(desc)

            

        d['views'] = []
        
        if e.spec_name == SPEC_MODELS and e.thing_name is not None:
            views = e.app._get_views()
            for v in views:
                view = e.app.views[v] 
                is_current = v == e.view_name
    
                url = library_url + SPEC_MODELS + '/' + e.thing_name + '/' + 'views/' + v + '/'
                name = "View: %s" % view['desc']
                desc = dict(name=name, url=url, current=is_current)
                d['views'].append(desc)
            
    # endif library not None
    
    libraries = e.session.list_libraries()

    # just the list of names
    d['libraries'] = []
    
    libname2desc = {}
    for l in natural_sorted(libraries):
        is_current = l == e.library_name
        p = '/repos/{repo_name}/shelves/{shelf_name}/libraries/%s/' % l
        url = e.app.make_relative(e.request, p.format(**d))

        #name = "Library: %s" % l
        name = l
        desc = dict(id=l,name=name, url=url, current=is_current)
        libname2desc[l] =desc
        d['libraries'].append(desc)

    indexed = e.session.get_libraries_indexed_by_shelf()
    indexed = [(sup, [libname2desc[_] for _ in l]) 
               for sup, l in indexed]
    
    
    d['libraries_indexed'] = indexed 
    
    return d