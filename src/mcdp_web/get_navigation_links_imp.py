from mcdp.logs import logger
from mcdp_library import MCDPLibrary
from mcdp_shelf import PRIVILEGE_WRITE
from mcdp_utils_misc import natural_sorted
from mcdp_web.resource_tree import ResourceThing, ResourceThings, ResourceThingView, ResourceLibrary, get_from_context,\
    ResourceShelf


def get_navigation_links_context(app, context, request):
    """ Pass this as "navigation" to the page. """
    session = app.get_session(request)
    
    current_thing = None
    
    rshelf = get_from_context(ResourceShelf, context)
    if rshelf is not None:
        shelf_name = rshelf.name
        shelf = session.get_shelf(shelf_name)
        user = session.get_user()
        shelf_write_permission = shelf.get_acl().allowed2(PRIVILEGE_WRITE, user)
    else:
        shelf_name = None
        shelf = None
        shelf_write_permission = False
        
    rlibrary = get_from_context(ResourceLibrary, context)
    if rlibrary is not None:
        current_library = rlibrary.name
        if current_library in session.libraries:
            library = session.libraries[current_library]['library']
        else:
            msg = 'The library %r is not available. Maybe a permission issue?' % current_library
            msg += '\n context: %s' % context.show_ancestors()
            logger.error(msg)
            current_library = None
            library = None
    else:
        current_library = None
        library = None
        
    rthing = get_from_context(ResourceThing, context)
    if rthing is not None:
        current_thing = rthing.name    
        rthings = get_from_context(ResourceThings, context)
        current_model = current_thing if rthings.specname == 'models' else None
        current_template = current_thing if rthings.specname == 'templates' else None
        current_poset = current_thing if rthings.specname == 'posets' else None
        current_value = current_thing if rthings.specname == 'values' else None
    else:
        current_thing = None
        current_model = None
        current_template = None
        current_poset = None
        current_value = None
        
    rview = get_from_context(ResourceThingView, context)
    current_view = rview.name if rview is not None else None
 
    d = {}

    d['shelfname'] = shelf_name
    d['shelf_name'] = shelf_name
    d['shelf'] = shelf
    d['shelf_write_permission'] = shelf_write_permission
    d['shelves_available'] = session.get_shelves_available()
    d['shelves_used'] = session.get_shelves_used()
    d['shelves_unused'] = {}
    for x in d['shelves_available']:
        if not x in  d['shelves_used']:
            d['shelves_unused'][x] = d['shelves_available'][x] 
    
    d['current_thing'] = current_thing
    d['current_library'] = current_library
    d['library_name'] = current_library
    
    d['current_template'] = current_template
    d['current_poset'] = current_poset
    d['current_model'] = current_model
    d['current_view'] = current_view

    make_relative = lambda _: app.make_relative(request, _)

    if library is not None:
        documents = library._list_with_extension(MCDPLibrary.ext_doc_md)

        d['documents'] = []
        for id_doc in documents:
            url = make_relative('/libraries/%s/%s.html' % (current_library, id_doc))
            desc = dict(id=id_doc,id_document=id_doc, name=id_doc, url=url, current=False)
            d['documents'].append(desc)

        d['models'] = []
        
        VIEW_EDITOR = 'views/edit_fancy/'
        VIEW_DELETE = ':delete'
        VIEW_SYNTAX = 'views/syntax/'
        
        library_url = app.make_relative(request, '/shelves/{shelf_name}/libraries/{library_name}/'.format(**d))
        
        models = library.list_ndps()
        for _ in natural_sorted(models):
            is_current = _ == current_model

            url0 =  library_url + 'models/' + _ + '/'
            url = url0 + VIEW_SYNTAX
            url_edit = url0 + VIEW_EDITOR  
            url_delete = url0 + VIEW_DELETE  
             
            name = "Model %s" % _
            desc = dict(id=_, id_ndp=_, name=name, url=url, url_edit=url_edit, url_delete=url_delete, current=is_current)
            d['models'].append(desc) 
       
        templates = library.list_templates()
        d['templates'] = []
        for _ in natural_sorted(templates):
            is_current = (_ == current_template)

            url0 =  library_url + 'templates/' + _ + '/'
            url = url0 + VIEW_SYNTAX
            url_edit = url0 + VIEW_EDITOR  
            url_delete = url0 + VIEW_DELETE  
            
            name = "Template: %s" % _
            desc = dict(id=_, name=name, url=url, current=is_current, url_edit=url_edit, url_delete=url_delete)
            d['templates'].append(desc)

        
        posets = library.list_posets()
        d['posets'] = []
        for _ in natural_sorted(posets):
            is_current = (_ == current_poset)
            
            url0 =  library_url + 'posets/' + _ + '/'
            url = url0 + VIEW_SYNTAX
            url_edit = url0 + VIEW_EDITOR  
            url_delete = url0 + VIEW_DELETE  

            name = "Poset: %s" % _
            desc = dict(id=_, name=name, url=url, current=is_current, url_edit=url_edit, url_delete=url_delete)
            d['posets'].append(desc)

        values = library.list_values()
        d['values'] = []
        for _ in natural_sorted(values):
            is_current = (_ == current_value)
            
            url0 =  library_url + 'values/' + _ + '/'
            url = url0 + VIEW_SYNTAX
            url_edit = url0 + VIEW_EDITOR  
            url_delete = url0 + VIEW_DELETE  

            name = "Value: %s" % _
            desc = dict(id=_, name=name, url=url, current=is_current, url_edit=url_edit, url_delete=url_delete)
            d['values'].append(desc)

            

        d['views'] = []
        
        if current_model is not None:
            views = app._get_views()
            for v in views:
                view = app.views[v] 
                is_current = v == current_view
    
                url = library_url + 'models/' + current_model + '/' + 'views/' + v + '/'
                name = "View: %s" % view['desc']
                desc = dict(name=name, url=url, current=is_current)
                d['views'].append(desc)
            
    # endif library not None
    session = app.get_session(request)
    libraries = session.list_libraries()

    # just the list of names
    d['libraries'] = []
    libname2desc = {}
    for l in natural_sorted(libraries):
        is_current = l == current_library
        url = make_relative('/libraries/%s/' % l)
        #name = "Library: %s" % l
        name = l
        desc = dict(id=l,name=name, url=url, current=is_current)
        libname2desc[l] =desc
        d['libraries'].append(desc)

    indexed = session.get_libraries_indexed_by_dir()
    indexed = [(sup, [libname2desc[_] for _ in l]) 
               for sup, l in indexed]
    
    # for sup, libraries in libraries_indexed
    #   for l in libraries
    #      l['name'], l['url']
    d['libraries_indexed'] = indexed
    
    
    return d