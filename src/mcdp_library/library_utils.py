

def list_library_files(library, ext):

    """
        
        for name, realpath in  list_library_files(library, 'md'):
        
        
    
    """

    items = library._list_with_extension(ext)
    for name in items:
        basename = name + '.' + ext
        f = library._get_file_data(basename)
        realpath = f['realpath']
        yield name, realpath
