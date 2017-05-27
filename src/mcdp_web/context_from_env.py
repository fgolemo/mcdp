
def library_from_env(e):
    ''' Creates a suitable MCDPLibrary from the environment '''
    from mcdp_hdb_mcdp.library_view import TheContext
    db_view = e.db_view
    host_cache = e.app.hi.host_cache
    subscribed_shelves = e.session.get_subscribed_shelves()
    current_library_name = e.library_name
    context = TheContext(host_cache, db_view, subscribed_shelves, current_library_name)
    mcdp_library = context.get_library()
    return mcdp_library

def image_source_from_env(e):
    from mcdp_report.image_source import ImagesFromDB
    image_source = ImagesFromDB(db_view=e.db_view, 
                                subscribed_shelves=e.session.get_subscribed_shelves(), 
                                current_repo_name=e.repo_name, 
                                current_shelf_name=e.shelf_name, 
                                current_library_name=e.library_name)
    return image_source