from collections import defaultdict
import urlparse
from webtest.app import AppError
from mcdp.logs import logger

class Spider():
    def __init__(self, get_maybe_follow):
        self.get_maybe_follow = get_maybe_follow
        self.queue = []
        self.skipped = set()
        self.failed = {} # url -> Exception
        self.visited = set()
        self.referrers = defaultdict(lambda: set()) # url -> url referred to
        
    def visit(self, url):
        self.queue.append(url)
                          
    def go(self):
        while self.queue:
            self.step()
            
    def step(self):
        url = self.queue.pop(0)
        if url in self.visited:
            return
        o = urlparse.urlparse(url)
        
        if ':' in o.path: # skip actions
            self.skipped.add(url)
            return 
        
        if o.netloc and o.netloc != u'localhost':
            #print('Skipping %s' % str(o))
            self.skipped.add(url)
            return

        print('%s ... ' % url)
        self.visited.add(url)
        try:
            url2, res = self.get_maybe_follow(url)
        except AppError as e:
            self.failed[url] = e
            return
            
        self.visited.add(url2)
        if url2 != url:
            print('%s -> %s' % (url, url2))
        if res.content_type == 'text/html':
            urls = find_links(res.html, url2)
            print('%s %s: %d links' % (url2, res.status, len(urls)))
            for u in urls:
                self.queue.append(u)
                self.referrers[u].add(url2)
    
    def log_summary(self):
        logger.info('Visited: %d' % len(self.visited))
        logger.info('Skipped: %d' % len(self.skipped))
        if self.failed:
            logger.error('Failed: %d' % len(self.failed))
        for url in self.skipped:
            logger.debug('skipped %s' % url)
        for url in self.failed:
            logger.error('failed %s' % url)
            for r in self.referrers[url]:
                logger.error(' referred from %s' % r)
            logger.error(unicode(self.failed[url]))

                
                
def find_links(html, url_base):   
    urls = [] 
    for a in html.select('link[href]'):
        href = a['href'] 
        url = urlparse.urljoin(url_base, href)
        urls.append(url)
        
    for a in html.select('a[href]'):
        href = a['href']
        if 'exit' in href:
            continue
        url = urlparse.urljoin(url_base, href)
        urls.append(url)
    return urls