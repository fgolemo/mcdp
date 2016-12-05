# -*- coding: utf-8 -*-
import urllib, urlparse
from collections import namedtuple

Resource = namedtuple('Resource', 'name type url content_type content')

def scrape(qrstring):
    """ Returns a list of Resources """
    """
        Resource(name=u'aaa_battery', 
        type=[u'mcdp/icon'], 
        url=u'file:///Users/andrea/boot-docs/ext/minimality_game/website/rdg/decks/1/cards/aaa_battery-web.png', 
        content_type=u'image/png', content='')
        
    """
    web = 'http://minimality.mit.edu/rdg/'
    local = 'file:///Users/andrea/boot-docs/ext/minimality_game/website/rdg/'
#     local = 'http://127.0.0.1:8080/rdg/'
    qrstring = qrstring.replace(web, local)

    url = qrstring

    f = urllib.urlopen(url)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(f, 'html.parser', from_encoding='utf-8')
    resources = []

    # <link href="aaa_battery-web.png" name='aaa_battery' rel="mcdp/icon" type="image/png"/>

    for tag in soup.find_all('link'):
        print(tag)
        rel = tag['rel'][0]
        if 'mcdp' in rel:
            href = tag['href']
            content_type = tag['type']
            name = tag['name']
            abs_url = urlparse.urljoin(url, href)
            content = urllib.urlopen(abs_url).read()
            r = Resource(type=str(rel), content_type=str(content_type),
                         url=str(abs_url), content=content, name=str(name))

            print r.type, r.content_type, r.url, r.name, len(r.content)
            resources.append(r)
        else:
            print('cannot parse: %s' % tag)

    return resources

def test_scraper1():
    resources = scrape('http://minimality.mit.edu/rdg/decks/1/cards/aaa_battery.html')
    print resources
    


if __name__ == '__main__':
    test_scraper1()
