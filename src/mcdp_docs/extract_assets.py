import os
import sys

from bs4 import BeautifulSoup

from .logs import logger
from mcdp_report.embedded_images import extract_img_to_file


def go():
    if len(sys.argv) != 3:
        print('Syntax:\n\n     %s input_html output_html' % 
              os.path.basename(sys.argv[0]))
        print('\n\nError: I need exactly 2 arguments.')
        sys.exit(1)
    fn = sys.argv[1]
    out = sys.argv[2]
    
    assets_dir = out + '.assets'
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    logger.debug('Using assets dir %s' % assets_dir)
    
    outd = os.path.dirname(out)
    if not os.path.exists(outd):
        os.makedirs(outd)
        
    return go_(fn, out, assets_dir)
    
    
def go_(fn, out, assets_dir):
    data = open(fn).read()
    soup = BeautifulSoup(data, "lxml", from_encoding='utf-8')
    go__(soup, out, assets_dir)
    s = str(soup)
    logger.info('writing to %r' % out)
    with open(out, 'w') as f:
        f.write(str(s))
        
        
def go__(soup, out, assets_dir):

    def savefile(filename_hint, data):
        """ must return the url (might be equal to filename) """
        where = os.path.join(assets_dir, filename_hint)
        logger.debug('writing to %s' % where)
        with open(where, 'wb') as f:
            f.write(data)
        
        relative = os.path.relpath(where, os.path.dirname(out))
        
        return relative
    
    extract_img_to_file(soup, savefile)
    
    
if __name__ == '__main__':
    go()
    