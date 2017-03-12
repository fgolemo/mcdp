from collections import defaultdict
import urlparse
from webtest.app import AppError
import logging


logger = logging.getLogger('mcdp.spider')
logger.setLevel(logging.DEBUG)

class Spider():
    def __init__(self, get_maybe_follow, ignore=None):
        self.get_maybe_follow = get_maybe_follow
        if ignore is None:
            ignore = lambda _url, _parsed: False
        self.ignore = ignore
        self.queue = []
        self.skipped = set()
        self.failed = {} # url -> Exception
        self.visited = set()
        self.referrers = defaultdict(lambda: set()) # url -> url referred to
        
    def visit(self, url):
        self.queue.append(url)
                          
    def go(self, max_fails=None):
        while self.queue:
            self.step()
            if max_fails is not None:
                if len(self.failed) >= max_fails:
                    msg = 'Exiting because of max fails reached.'
                    logger.debug(msg)
                    break
            
    def step(self):
        url = self.queue.pop(-1)
        if url in self.visited:
            return
        o = urlparse.urlparse(url)
        
        if self.ignore(url, o):
            self.skipped.add(url)
            return
        
        logger.debug('requests %s ... ' % url)
        self.visited.add(url)
        try:
            url2, res = self.get_maybe_follow(url)
        except AppError as e:
            logger.error('failed %s' % url) 
            self.failed[url] = e
            return
            
        self.visited.add(url2)
        if url2 != url:
            logger.debug('redirected %s -> %s' % (url, url2))
        if res.content_type == 'text/html':
            urls = list(find_links(res.html, url2))
            logger.debug('read %s %s: %d links' % (url2, res.status, len(urls)))
            for u in urls:
                self.queue.append(u)
                self.referrers[u].add(url2)
    
    def log_summary(self):
        logger.info('Visited: %d' % len(self.visited))
        logger.info('Skipped: %d' % len(self.skipped))
        if self.failed:
            logger.error('Failed: %d' % len(self.failed))
        for url in sorted(self.visited):
            logger.info('visisted %s' % url)
        for url in sorted(self.skipped):
            logger.debug('skipped %s' % url)
        for url in sorted(self.failed):
            logger.error('failed %s' % url)
            for r in self.referrers[url]:
                logger.error(' referred from %s' % r)
            logger.error(unicode(self.failed[url]))

                
                
def find_links(html, url_base):   
    def find(): 
        for link in html.select('link[href]'):
            yield link['href']
        for script in html.select('script[src]'):
            yield script['src']
        for img in html.select('img[src]'):
            yield img['src']
        for a in html.select('a[href]'):
            yield a['href']
    for url in find(): 
        yield urlparse.urljoin(url_base, url).encode('utf8')
