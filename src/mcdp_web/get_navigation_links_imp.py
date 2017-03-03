from mcdp_library.library import MCDPLibrary
from mcdp_utils_misc.natsort import natural_sorted
from mcdp_web.resource_tree import ResourceThing, ResourceThings, ResourceThingView, ResourceLibrary, get_from_context


def get_navigation_links_context(app, context, request):
    """ Pass this as "navigation" to the page. """
    session = app.get_session(request)
    
    current_thing = None
    
    rlibrary = get_from_context(ResourceLibrary, context)
    if rlibrary is not None:
        current_library = rlibrary.name
        library = session.libraries[current_library]['library']
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

    d['shelves_available'] = session.get_shelves_available()
    d['shelves_used'] = session.get_shelves_used()
    d['shelves_unused'] = {}
    for x in d['shelves_available']:
        if not x in  d['shelves_used']:
            d['shelves_unused'][x] = d['shelves_available'][x] 
    
    d['current_thing'] = current_thing
    d['current_library'] = current_library
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
        
        VIEW_EDITOR = 'edit_fancy'
        
        models = library.list_ndps()
        for m in natural_sorted(models):
            is_current = m == current_model

            url = app.get_lmv_url2(library=current_library,
                                   model=m,
                                   view='syntax', request=request)
            url_edit =  app.get_lmv_url2(library=current_library,
                                   model=m,
                                   view=VIEW_EDITOR, request=request)
            name = "Model %s" % m
            desc = dict(id=m, id_ndp=m, name=name, url=url, url_edit=url_edit, current=is_current)
            d['models'].append(desc)


        templates = library.list_templates()
        d['templates'] = []
        for t in natural_sorted(templates):
            is_current = (t == current_template)

            url = app.get_lib_template_view_url2(library=current_library,
                                                 template=t,
                                                 view='syntax', request=request) 
            url_edit = app.get_lib_template_view_url2(library=current_library,
                                                 template=t,
                                                 view=VIEW_EDITOR,request= request)  

            name = "Template: %s" % t
            desc = dict(id=t, name=name, url=url, current=is_current, url_edit=url_edit)
            d['templates'].append(desc)

        posets = library.list_posets()
        d['posets'] = []
        for p in natural_sorted(posets):
            is_current = (p == current_poset)
            url = app.get_lpv_url2(library=current_library,
                                   poset=p,
                                   view='syntax', request=request)
            url_edit = app.get_lpv_url2(library=current_library,
                                   poset=p,
                                   view=VIEW_EDITOR,request= request)
            name = "Poset: %s" % p
            desc = dict(id=p, name=name, url=url, current=is_current, url_edit=url_edit)
            d['posets'].append(desc)

        values = library.list_values()
        d['values'] = []
        for v in natural_sorted(values):
            is_current = (v == current_value)
            url = '/libraries/%s/values/%s/views/syntax/' % (current_library, v)
            url_edit = '/libraries/%s/values/%s/views/%s/' % (current_library, v, VIEW_EDITOR)
            name = "Value: %s" % v
            desc = dict(id=v,name=name, url=url, current=is_current, url_edit=url_edit)
            d['values'].append(desc)


        d['views'] = []
        views = app._get_views()
        for v in views:
            view = app.views[v]
            is_current = v == current_view

            url = app.get_lmv_url2(library=current_library,
                                   model=current_model,
                                   view=v, request=request)

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