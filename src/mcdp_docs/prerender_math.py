from contracts import contract
from mcdp import logger
from mcdp_utils_misc import dir_from_package_name, get_mcdp_tmp_dir, memoize_simple
from mcdp_utils_xml import bs, to_html_stripping_fragment
import os
import shutil
from system_cmd import CmdException, system_cmd_result
from tempfile import mkdtemp

from contracts.utils import raise_wrapped, indent, raise_desc


__all__ = [
    'prerender_mathjax',
]

      
TAG_DOLLAR = 'tag-dollar'
which = 'code, mcdp-poset, mcdp-value, mcdp-fvalue, mcdp-rvalue, render'

def escape_for_mathjax(soup):
    """ Escapes dollars in code 
     
    """
    for code in soup.select(which):
        if not code.string:
            continue
        #unicode
        s = code.string
        if '$' in code.string:
            s = s.replace('$', TAG_DOLLAR)
            
        code.string = s
    

def escape_for_mathjax_back(soup):

    for code in soup.select(which):
        if not code.string:
            continue
        s = code.string
        if TAG_DOLLAR in code.string:
            s = s.replace(TAG_DOLLAR, '$')
            
        code.string = s
     

@memoize_simple
def get_prerender_js():
    package = dir_from_package_name('mcdp_docs')
    fn = os.path.join(package, 'prerender.js')
    assert os.path.exists(fn), fn
    return fn

class PrerenderError(Exception):
    pass

def prerender_mathjax(s, symbols):
    
    if symbols:
        lines = symbols.split('\n')
        lines = [l for l in lines if l.strip()]
        m = '$$' + "\n".join(lines) +'$$\n\n'
    else:
        m = ''

    STARTTAG = 'STARTHERE'
    ENDTAG = 'ENDHERE'
    s = STARTTAG +  get_mathjax_preamble() + ENDTAG + m + s

    try:
        s = prerender_mathjax_(s)
    except PrerenderError: # pragma: no cover
        if 'CIRCLECI' in os.environ:
            msg = 'Ignoring PrerenderError because of CircleCI.'
            logger.error(msg)
            return s
        else:
            raise

    c0 = s.index(STARTTAG)
    c1 = s.index(ENDTAG) + len(ENDTAG)
    s = s[:c0] + s[c1:]

#     s = fix_vertical_align(s)
    return s
# 
# def fix_vertical_align(s, scale=0.8):
#     """ For all vertical-align: (.*?)ex in svg, multiplies by scale """
#     frag = bs(s)
#     for element in frag.select('svg'):
#         if element.has_attr('style'):
#             s = element.attrs['style']
#             def f(m):
#                 x0 = float(m.group(1))
#                 x1 = x0/scale
#                 return 'vertical-align: %.4fex' % x1
#             s2 = re.sub(r'vertical-align: (.*?)ex', f, s)
#             print('%s -> %s' % (s, s2))
#             element['style'] = s2
# 
#     return to_html_stripping_fragment(frag)


@memoize_simple
def get_mathjax_preamble():
    package = dir_from_package_name('mcdp_docs')
    fn = os.path.join(package, 'symbols.tex')
    if not os.path.exists(fn): # pragma: no cover
        raise ValueError(fn)
    tex = open(fn).read()
    f = '$$'+tex+'$$'
    f += """
<script type="text/x-mathjax-config">
    console.log('here!');

   MathJax.Hub.Config({
       TeX: { extensions: ["color.js"] },
       SVG: {font:'STIX-Web'}
   });
</script>"""

    return f


@memoize_simple
def get_nodejs_bin():
    """ Raises NodeNotFound (XXX) """
    tries = ['nodejs', 'node']
    try:
        cmd= [tries[0], '--version']
        _res = system_cmd_result(
                os.getcwd(), cmd,
                display_stdout=False,
                display_stderr=False,
                raise_on_error=True)
        return tries[0]# pragma: no cover
    except CmdException as e:
        try:
            cmd= [tries[1], '--version']
            _res = system_cmd_result(
                    os.getcwd(), cmd,
                    display_stdout=False,
                    display_stderr=False,
                    raise_on_error=True)
            return tries[1]
        except CmdException as e: # pragma: no cover
            msg = 'Node.js executable "node" or "nodejs" not found.'
            msg += '\nOn Ubuntu, it can be installed using:'
            msg += '\n\n\tsudo apt-get install -y nodejs'
            raise_wrapped(PrerenderError, e, msg, compact=True)


@contract(returns=str, html=str)
def prerender_mathjax_(html):
    """
        Runs the prerender.js script to pre-render the MathJax into images.

        Raises PrerenderError.
    """
    assert not '<html>' in html, html

    use = get_nodejs_bin()

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
            pwd = os.getcwd()
            res = system_cmd_result(
                    pwd, cmd,
                    display_stdout=False,
                    display_stderr=False,
                    raise_on_error=False)

            if res.ret:# pragma: no cover
                if 'Error: Cannot find module' in res.stderr:
                    msg = 'You have to install the MathJax and/or jsdom libraries.'
                    msg += '\nOn Ubuntu, you can install them using:'
                    msg += '\n\n\tsudo apt-get install npm'
                    msg += '\n\n\tnpm install MathJax-node jsdom'
                    msg += '\n\n' + indent(res.stderr, '  |')
                    raise PrerenderError(msg)

                if 'parse error' in res.stderr:
                    lines = [_ for _ in res.stderr.split('\n')
                             if 'parse error' in _ ]
                    assert lines
                    msg = 'LaTeX conversion errors:\n\n' + '\n'.join(lines)
                    raise PrerenderError(msg)

                msg = 'Unknown error (ret = %d).' % res.ret
                msg += '\n\n' + indent(res.stderr, '  |')
                raise PrerenderError(msg)

            with open(f_out) as f:
                data = f.read()

            # Read the data 
            soup = bs(data)
            # find this and move it at the end
            # <style id="MathJax_SVG_styles"
            tag_style = soup.find(id='MathJax_SVG_styles')
            if not tag_style:
                msg = 'Expected to find style MathJax_SVG_styles'
                raise_desc(Exception, msg, soup=str(soup))
            # <svg style="display: none;"><defs id="MathJax_SVG_glyphs">
            tag_svg_defs = soup.find('svg', style="display: none;")
            if not tag_svg_defs:
                msg = 'Expected to find tag <svg display=none>'
                raise_desc(Exception, msg, soup=str(soup))
            
            other_tag = soup.find('div', style="display:none")
            if not other_tag:
                msg = 'Expected to find tag <div style="display:none">'
                raise_desc(Exception, msg, soup=str(soup))
                
            #<div style="display:none">Because of mathjax bug</div>
            soup.append(other_tag.extract()) 
            soup.append(tag_svg_defs.extract()) 
            soup.append(tag_style.extract()) 
            data = to_html_stripping_fragment(soup)

            return data
        except CmdException as e: # pragma: no cover
            raise e
    finally:
        shutil.rmtree(d)
