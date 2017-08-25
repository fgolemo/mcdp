from contracts import contract
from mcdp import logger
from mcdp_utils_misc import get_mcdp_tmp_dir
import os
import shutil
from system_cmd import CmdException,  system_cmd_result
from tempfile import mkdtemp

from contracts.utils import indent


def unescape_entities(s):
    from HTMLParser import HTMLParser
    h = HTMLParser()
    s2 = h.unescape(s)
    return s2

def run_lessc(soup):
    """ Runs pre-processor on all styles nodes """
    for style in soup.select('style'):
        if 'Math' in style.attrs.get('id', ''):
            continue
        s1 = style.string
        s1 = unescape_entities(s1)
        s1 = s1.replace('AND', '&')
        s1 = s1.encode('utf-8')
        try:
            s2 = lessc_string(s1)    
        except LesscError as e:
            msg = 'Could not convert string using less (ignored)'
            msg += '\n'+indent(e, '>> ')
            logger.warning(msg)
            continue
        
        s2 = unicode(s2, 'utf-8')
#         print indent(s2, 'less |')
        s2 = '/* preprocessed with less */\n' + s2
        style.string = s2
        style['type'] = 'text/css'

class LesscError(Exception):
    pass

 

            
@contract(s1=str, returns=str)
def lessc_string(s1): 
    """
        Runs "node lessc" on the string
        
        Raises LesscError.
    """
#     print(indent(s1, 'lessc input: '))
    mcdp_tmp_dir = get_mcdp_tmp_dir()
    prefix = 'prerender_lessc'
    d = mkdtemp(dir=mcdp_tmp_dir, prefix=prefix)
    try:
        f1 = os.path.join(d, 'input.less')
        f2 = os.path.join(d, 'out.css')
        with open(f1, 'w') as f:
            f.write(s1)
            
        try:
            cmd= ['lessc', f1, f2]
            res = system_cmd_result(
                    d, cmd, 
                    display_stdout=True,
                    display_stderr=True,
                    raise_on_error=False)
            
            if res.ret:
                msg = 'lessc error (return value = %d).' % res.ret 
                msg += '\n\n' + indent(res.stderr, '',  'stderr:')
                msg += '\n\n' + indent(res.stdout, '',  'stdout:')
                raise LesscError(msg)
            
            with open(f2) as f:
                data = f.read()

            return data
        except CmdException as e:
            raise e
    finally:
        shutil.rmtree(d)
    