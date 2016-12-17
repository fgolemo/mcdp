import os
import shutil
from tempfile import mkdtemp

from contracts import contract
from mcdp_library.utils.dir_from_package_nam import dir_from_package_name
from mocdp import get_mcdp_tmp_dir
from system_cmd.meat import system_cmd_result
from system_cmd.structures import CmdException
from contracts.utils import raise_wrapped


__all__ = ['prerender_mathjax']

def get_prerender_js():
    package = dir_from_package_name('mcdp_data')
    fn = os.path.join(package, 'libraries', 'manual.mcdplib', 'prerender.js')
    assert os.path.exists(fn), fn
    return fn

class PrerenderError(Exception):
    pass

@contract(returns=str, html=str)
def prerender_mathjax(html):
    """
        Raises PrerenderError
    """
    tries = ['nodejs', 'node']
    try:
        cmd= [tries[0], '--version']
        res = system_cmd_result(
                os.getcwd(), cmd, 
                display_stdout=True,
                display_stderr=True,
                raise_on_error=True)
        use = tries[0]
    except CmdException as e:
        try:
            cmd= [tries[1], '--version']
            res = system_cmd_result(
                    os.getcwd(), cmd, 
                    display_stdout=True,
                    display_stderr=True,
                    raise_on_error=True)
            use = tries[1]
        except CmdException as e:
            msg = 'Node.js executable "node" or "nodejs" not found.'
            msg += '\nIt can be installed using: sudo apt-get install -y nodejs'
            raise_wrapped(PrerenderError, e, msg, compact=True)
        
    html = html.replace('<p>$$', '\n$$')
    html = html.replace('$$</p>', '$$\n')
    script = get_prerender_js()
    mcdp_tmp_dir = get_mcdp_tmp_dir()
    prefix = 'prerender_mathjax_'
    d = mkdtemp(dir=mcdp_tmp_dir, prefix=prefix)
    
    try:
        f_html = os.path.join(d, 'file.html')
        with open(f_html, 'w') as f:
            f.write(html)
            
        try:
            f_out = os.path.join(d, 'out.html')
            cmd= [use, script, f_html, f_out]
            res = system_cmd_result(
                    d, cmd, 
                    display_stdout=True,
                    display_stderr=True,
                    raise_on_error=True)
            
            if 'parse error' in res.stderr:
                lines = [_ for _ in res.stderr.split('\n')
                         if 'parse error' in _ ]
                assert lines
                msg = 'LaTeX conversion errors:\n\n' + '\n'.join(lines)
                raise PrerenderError(msg) 
    
            with open(f_out) as f:
                data = f.read()
            
            return data
        except CmdException as e:
            raise e
    finally:
        shutil.rmtree(d)
