

def move_things_around(soup):
    
    '''
        Looks for tags like:
        
            <move-here src="#line_detector2-line_detector_node2-autogenerated"/> 
    
    '''
    
    for e in soup.select('move-here'):
        if not 'src' in e.attrs:
            msg = 'Expected attribute "src" for element %s' % str(e)
            raise ValueError(msg)
        src = e.attrs['src']
        if not src.startswith('#'):
            msg = 'Expected that attribute "src" started with "#" for element %s.' % str(e)
            raise ValueError(msg)
        nid = src[1:]
        el = soup.find(id=nid)
        if not el:
            msg = 'Could not find ID %r.' % nid
            raise ValueError(msg)
        el.extract()
        e.replace_with(el)
        
        