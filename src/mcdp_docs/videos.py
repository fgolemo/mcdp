from collections import namedtuple
from contracts.utils import raise_desc
import json
import urllib2

from bs4.element import Tag, Comment


def make_videos(soup):
    """
        Looks for tags of the kind:
        
        <dtvideo src="vimeo:XXXX"/>
    
    
    """
    
    for o in soup.find_all('dtvideo'):
        make_videos_(o)
        
def make_videos_(o):
    if not 'src' in o.attrs:
        msg = 'The video does not have a "src" attribute.'
        raise_desc(ValueError, msg, element=str(o))
    
    src = o.attrs['src']
    prefix = 'vimeo:'
    if not src.startswith(prefix):
        msg = 'Invalid attribute "src": it does not start with %r.' % (src, prefix)
        raise_desc(ValueError, msg, element=str(o))
        
    vimeo_id = src[len(prefix):]
    
#     <iframe src="https://player.vimeo.com/video/152233002" 
#         class="embed-responsive-item" 
#         frameborder="0" webkitallowfullscreen="" mozallowfullscreen="" allowfullscreen="">
    
    vimeo_info = get_vimeo_info(vimeo_id)    
    
    
    d = Tag(name='div')
    d.attrs['class'] = 'video'
    
    ONLY_WEB ='only-web'
    ONLY_EBOOK ='only-ebook'
    ONLY_DEADTREE ='only-deadtree'
    
    d.append(Comment('This is the iframe, for online playing.'))
    C = Tag(name='div')
    C.attrs['class'] = ONLY_WEB
    if True:
        r = Tag(name='iframe')
        r.attrs['class'] = 'video-vimeo-player'
        r.attrs['src'] = 'https://player.vimeo.com/video/' + vimeo_id
        r.attrs['frameborder'] = 0
        r.attrs['webkitallowfullscreen'] = 1
        r.attrs['mozallowfullscreen'] = 1
        r.attrs['allowfullscreen'] = 1
        C.append(r)
    d.append(C)
    
    d.append(Comment('This is the thumbnail, for ebook'))
    C = Tag(name='div')
    C.attrs['class'] = ONLY_EBOOK
    if True:
        a = Tag(name='a')
        a.attrs['href'] = vimeo_info.url
        img = Tag(name='img')
        img.attrs['class'] = 'video-vimeo-thumbnail-ebook'
        img.attrs['src'] = vimeo_info.thumbnail_large
        img.attrs['title'] = vimeo_info.title
        a.append(img)
        C.append(a)
    d.append(C)
    
    d.append(Comment('This is the textual version for printing.'))
    C = Tag(name='div')
    C.attrs['class'] = ONLY_DEADTREE
    if True:
        
        img = Tag(name='img')
        img.attrs['class'] = 'video-vimeo-thumbnail-deadtree'
        img.attrs['src'] = vimeo_info.thumbnail_large
        img.attrs['title'] = vimeo_info.title
        C.append(img)
        p = Tag(name='p') 
        p.append("The video is at %s." % vimeo_info.url )
        C.append(p)
    d.append(C)
    
    o.replace_with(d)
    
VimeoInfo = namedtuple('VimeoInfo', 'title thumbnail_large url')

def get_vimeo_info(vimeo_id):
    url = 'http://vimeo.com/api/v2/video/%s.json' % vimeo_id

    response = urllib2.urlopen(url) 
    data = response.read()
    #logger.debug(data)
    
    data = json.loads(data)
    #logger.debug(json.dumps(data))
    v = data[0]
    
    assert v['id'] == int(vimeo_id)
    title = v['title']
    thumbnail_large = v['thumbnail_large']
    
    return VimeoInfo(title=title, thumbnail_large=thumbnail_large, url=v['url'])
    
    
    