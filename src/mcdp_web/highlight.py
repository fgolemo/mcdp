from bs4 import BeautifulSoup
from contracts.utils import raise_desc
from mcdp_report.html import ast_to_html
from mcdp_web.images.images import (ndp_graph_enclosed, ndp_graph_expand,
    ndp_graph_normal, ndp_graph_templatized)
from mocdp.exceptions import DPSemanticError, DPSyntaxError
import base64

def html_interpret(library, html):
    # clone linrary?
    library = library.clone()
    load_fragments(library, html)
    html = highlight_mcdp_code(html)
    html = make_figures(library, html)
    return html.decode('utf-8')


def load_fragments(library, frag):
    """
        loads all the codes 
        
            <pre class='mcdp' id='id_ndp>
            code
            </pre>
    """
    soup = BeautifulSoup(frag, 'html.parser')

    for tag in soup.select('pre.mcdp'):
        if tag.has_attr('id'):
            id_ndp = tag['id']
            source_code = str(tag.string)

            basename = '%s.mcdp' % id_ndp
            res = dict(data=source_code, realpath="(unavailable)")

            if basename in library.file_to_contents:
                msg = 'Duplicated model.'
                raise_desc(ValueError, msg, tag=str(tag),
                           known=library.file_to_contents[basename])

            library.file_to_contents[basename] = res


def highlight_mcdp_code(frag):
    """ Looks for codes like:
    
    <pre class="mcdp">mcdp {
        # empty model
    }
    </pre>
    
        and does syntax hihglighting.
    """

    soup = BeautifulSoup(frag, 'html.parser')

    for tag in soup.select('pre.mcdp'):
        source_code = tag.string
        while source_code[0] == '\n':
            source_code = source_code[1:]


            
        try:
            html = ast_to_html(source_code,
                        complete_document=False,
                        add_line_gutter=False)            
            frag2 = BeautifulSoup(html,'lxml')
            rendered = frag2.pre
            print rendered
            if tag.has_attr('label'):
                tag_label = soup.new_tag('span', **{'class': 'label'})
                tag_label.append(tag['label'])
                rendered.insert(0, tag_label)

            tag.replaceWith(rendered)
            
        except DPSyntaxError as e:
            print(e)
            t = soup.new_tag('pre', **{'class': 'error %s' % type(e).__name__})
            t.string = str(e)
            tag.insert_after(t)


    return str(soup)

def make_figures(library, frag):
    """ Looks for codes like:

    <pre><code class="mcdp_ndp_graph_templatized">mcdp {
        # empty model
    }
    </code></pre>
    
        and creates a link to the image
    """

    soup = BeautifulSoup(frag, 'html.parser')

    def go(selector, func):

        for tag in soup.select(selector):
            try:
                r = func(tag) 
                tag.replaceWith(r)
            except (DPSyntaxError, DPSemanticError) as e:
                print(e)
                t = soup.new_tag('pre', **{'class': 'error %s' % type(e).__name__})
                t.string = str(e)
                tag.insert_after(t)
    
    from mcdp_report.gdc import STYLE_GREENREDSYM

    default_direction = 'LR'

    def call(func, klass, **args):
        if False:
            png = func(data_format='png', **args)
            r = create_img_png_base64(soup, png, **{'class': klass})
            return r
        else:
            svg = func(data_format='svg', **args)
            tag = BeautifulSoup(svg, 'lxml').svg
            tag['class'] = klass
            return tag


    def func1(tag):
        source_code = tag.string
        source_code = str(source_code)  # unicode
        ndp = library.parse_ndp(source_code)
        yourname = ''

        direction = str(tag.get('direction', default_direction))

        
        return call(ndp_graph_normal, library=library, ndp=ndp,
                    style=STYLE_GREENREDSYM,
                           yourname=yourname,
                         direction=direction, klass='ndp_graph_normal')
        
    def func2(tag):
        source_code = tag.string
        source_code = str(source_code)  # unicode
        ndp = library.parse_ndp(source_code)
        # note
        yourname = ''
        direction = str(tag.get('direction', default_direction))

        return call(ndp_graph_templatized, library=library, ndp=ndp, yourname=yourname,
                                    direction=direction, klass='ndp_graph_templatized')

    def func2b(tag):
        source_code = tag.string
        source_code = str(source_code)  # unicode
        ndp = library.parse_ndp(source_code)
        # note
        yourname = None
        from mcdp_library.library import ATTR_LOAD_NAME
        if hasattr(ndp, ATTR_LOAD_NAME):
            yourname = getattr(ndp, ATTR_LOAD_NAME)
        direction = str(tag.get('direction', default_direction))

        return call(ndp_graph_templatized, library=library, ndp=ndp,
                    direction=direction,
                    yourname=yourname, klass='ndp_graph_templatized_labeled')

    
    def func3(tag):
        source_code = tag.string
        source_code = str(source_code)  # unicode
        ndp = library.parse_ndp(source_code)
        yourname = ''

        direction = str(tag.get('direction', default_direction))

        return call(ndp_graph_enclosed, library=library, ndp=ndp, style=STYLE_GREENREDSYM,
                                 yourname=yourname,
                                 direction=direction, klass='ndp_graph_enclosed')


    def func4(tag):
        source_code = tag.string
        source_code = str(source_code)  # unicode
        ndp = library.parse_ndp(source_code)

        yourname = ''

        direction = str(tag.get('direction', default_direction))

        return call(ndp_graph_expand, library=library, ndp=ndp, style=STYLE_GREENREDSYM,
                                 yourname=yourname,
                                 direction=direction,
                                 klass='ndp_graph_expand')

    go('pre.ndp_graph_normal', func1)
    go('pre.ndp_graph_templatized', func2)
    go('pre.ndp_graph_templatized_labeled', func2b)
    go('pre.ndp_graph_enclosed', func3)
    go('pre.ndp_graph_expand', func4)
#
#     return soup.prettify()
    return str(soup)

def create_img_png_base64(soup, png, **attrs):
    encoded = base64.b64encode(png)
    src = 'data:image/png;base64,%s' % encoded
    return soup.new_tag('img', src=src, **attrs)

    
    
