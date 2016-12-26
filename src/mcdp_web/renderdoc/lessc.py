import os
from tempfile import mkdtemp

from pip._vendor.distlib._backport import shutil

from contracts import contract
from mcdp_web.renderdoc.xmlutils import bs, to_html_stripping_fragment
from mocdp import get_mcdp_tmp_dir
from system_cmd.meat import system_cmd_result
from system_cmd.structures import CmdException
from contracts.utils import indent

def preprocess_lessc(s):
    soup = bs(s)
    run_lessc(soup)
    return to_html_stripping_fragment(soup)

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
        s2 = lessc_string(s1)
        
        print indent(s2, 'less |')
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
    mcdp_tmp_dir = get_mcdp_tmp_dir()
    prefix = 'prerender_lessc'
    d = mkdtemp(dir=mcdp_tmp_dir, prefix=prefix)
#     try:
#         node = get_nodejs_bin()
#     except NodeNotFound as e:
#         raise_wrapped(LesscError, e, "Could not find node", compact=True)
#         
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
#                 if 'Error: Cannot find module' in res.stderr:
#                     msg = 'You have to install the MathJax and/or jsdom libraries.'
#                     msg += '\nOn Ubuntu, you can install them using:'
#                     msg += '\n\n\tsudo apt-get install npm'
#                     msg += '\n\n\tnpm install MathJax-node jsdom'
#                     msg += '\n\n' + indent(res.stderr, '  |')
#                     raise PrerenderError(msg) 
#                 
#                 if 'parse error' in res.stderr:
#                     lines = [_ for _ in res.stderr.split('\n')
#                              if 'parse error' in _ ]
#                     assert lines
#                     msg = 'LaTeX conversion errors:\n\n' + '\n'.join(lines)
#                     raise PrerenderError(msg)
#             
                msg = 'lessc error (ret = %d).' % res.ret 
                msg += '\n\n' + indent(res.stderr, '  |')
                raise LesscError(msg)
            
            with open(f2) as f:
                data = f.read()

            return data
        except CmdException as e:
            raise e
    finally:
        shutil.rmtree(d)
    