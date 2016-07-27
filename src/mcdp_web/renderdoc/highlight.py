from bs4 import BeautifulSoup
from contracts import contract
from contracts.utils import raise_desc, raise_wrapped
from mcdp_lang.syntax import Syntax
from mcdp_library.library import MCDPLibrary
from mcdp_report.generic_report_utils import (
    NotPlottable, enlarge, get_plotters, plotters)
from mcdp_report.html import ast_to_html
from mcdp_web.images.images import (ndp_graph_enclosed, ndp_graph_expand,
    ndp_graph_normal, ndp_graph_templatized)
from mocdp import logger
from mocdp.exceptions import DPSemanticError, DPSyntaxError
from reprep import Report
import base64
import traceback

def bs(fragment):
    return BeautifulSoup(fragment, 'html.parser', from_encoding='utf-8')

@contract(returns=str, html=str)
def html_interpret(library, html, raise_errors=False, realpath='unavailable'):
    # clone linrary?
    library = library.clone()
    load_fragments(library, html,
                   realpath=realpath)

    html = highlight_mcdp_code(library, html,
                               raise_errors=raise_errors,
                               realpath=realpath)

    html = make_figures(library, html,
                        raise_error_dp=raise_errors,
                        raise_error_others=raise_errors,
                        realpath=realpath)

    html = make_plots(library, html,
                      raise_errors=raise_errors,
                      realpath=realpath)

    return html

def make_image_tag_from_png(f):
    soup = bs("")
    def ff(*args, **kwargs):
        png = f(*args, **kwargs)
        rendered = create_img_png_base64(soup, png)
        return rendered
    return ff

def make_pre(f):
    soup = bs("")
    def ff(*args, **kwargs):
        res = f(*args, **kwargs)
        t = soup.new_tag('pre')  #  **{'class': 'print_value'})
        t.string = res
        return t
    return ff

@contract(frag=str, returns=str)
def make_plots(library, frag, raise_errors, realpath):
    """
        Looks for things like:
        
         
        <img class="value_plot_generic">VALUE</img>
        <img class="value_plot_generic" id='value"/>
        
        <pre class="print_value" id='value"/>
        <pre class="print_value">VALUE</img>
    
    """
    soup = bs(frag)

    def go(selector, plotter, load, parse):
        for tag in soup.select(selector):

            try:
                # load value with units in vu
                if tag.string is None:
                    if not tag.has_attr('id'):
                        msg = "If <img> is empty then it needs to have an id."
                        raise_desc(ValueError, msg, tag=str(tag))
                    # load it
                    vu = load(tag['id'])
                else:
                    source_code = tag.string.encode('utf-8')
                    vu = parse(source_code, realpath=realpath)

                rendered = plotter(tag, vu)

                if tag.has_attr('style'):
                    style = tag['style']
                else:
                    style = ''

                if style:
                    rendered['style'] = style
                tag.replaceWith(rendered)

            except (DPSyntaxError, DPSemanticError) as e:
                if raise_errors:
                    raise
                print(e)  # XXX
                t = soup.new_tag('pre', **{'class': 'error %s' % type(e).__name__})
                t.string = str(e)
                tag.insert_after(t)
            except Exception as e:
                if raise_errors:
                    raise
                t = soup.new_tag('pre', **{'class': 'error %s' % type(e).__name__})
                t.string = traceback.format_exc(e)
                tag.insert_after(t)
    
    @make_image_tag_from_png
    def plot_value_generic(tag, vu):  # @UnusedVariable
        r = Report()
        f = r.figure()
        try:
            available = dict(get_plotters(plotters, vu.unit))
            assert available
        except NotPlottable as e:
            msg = 'No plotters available for %s' % vu.unit
            raise_wrapped(ValueError, e, msg, compact=True)

        plotter = list(available.values())[0]

        axis = plotter.axis_for_sequence(vu.unit, [vu.value])
        axis = enlarge(axis, 0.15)
        with f.plot('generic') as pylab:
            plotter.plot(pylab, axis, vu.unit, vu.value, params={})
            pylab.axis(axis)
        png_node = r.resolve_url('png')
        png = png_node.get_raw_data()
        return png
    
    @make_pre
    def print_value(tag, vu):  # @UnusedVariable
        s = vu.unit.format(vu.value)
        return s
    
    @make_pre
    def print_mcdp(tag, ndp):  # @UnusedVariable
        return ndp.__str__()
    
    # parse(string, realpath)
    const = dict(load=library.load_constant, parse=library.parse_constant)
    mcdp = dict(load=library.load_ndp, parse=library.parse_ndp)
    go("img.plot_value_generic", plot_value_generic, **const)
    go("pre.print_value", print_value, **const)
    go("pre.print_mcdp", print_mcdp, **mcdp)
    return str(soup)

def load_fragments(library, frag, realpath):
    """
        loads all the codes 
        
            <pre class='mcdp' id='id_ndp>
            code
            </pre>
    """
    soup = bs(frag)

    for tag in soup.select('pre.mcdp'):
        if tag.string is None:
            continue

        if tag.has_attr('id'):
            id_ndp = tag['id']
            source_code = tag.string.encode('utf-8')

            basename = '%s.%s' % (id_ndp, MCDPLibrary.ext_ndps)
            res = dict(data=source_code, realpath=realpath)

            if basename in library.file_to_contents:
                msg = 'Duplicated entry.'
                raise_desc(ValueError, msg, tag=str(tag),
                           known=library.file_to_contents[basename])

            library.file_to_contents[basename] = res

    for tag in soup.select('pre.mcdp_poset'):
        if tag.string is None:
            continue

        if tag.has_attr('id'):
            id_ndp = tag['id']
            source_code = tag.string.encode('utf-8')

            basename = '%s.%s' % (id_ndp, MCDPLibrary.ext_posets)
            res = dict(data=source_code, realpath=realpath)

            if basename in library.file_to_contents:
                msg = 'Duplicated entry.'
                raise_desc(ValueError, msg, tag=str(tag),
                           known=library.file_to_contents[basename])

            library.file_to_contents[basename] = res


def get_source_code(tag):
    """ Gets the string attribute. 
    
        encodes as utf-8
        removes initial whitespace newlines
        converts tabs to spaces
    """
    if tag.string is None:
        raise ValueError(str(tag))

    source_code = tag.string.encode('utf-8')

    while source_code and source_code[0] == '\n':
        source_code = source_code[1:]

    source_code = source_code.replace('\t', ' ' * 4)
    return source_code

def highlight_mcdp_code(library, frag, realpath, raise_errors=False):
    """ Looks for codes like:
    
    <pre class="mcdp">mcdp {
        # empty model
    }
    </pre>
    
        and does syntax hihglighting.
    """

    soup = bs(frag)

    def go(selector, parse_expr, extension, use_pre=True):
        for tag in soup.select(selector):
            
            try:
                if tag.string is None:
                    if not tag.has_attr('id'):
                        msg = "If <pre> is empty then it needs to have an id."
                        raise_desc(ValueError, msg, tag=str(tag))
                    # load it
                    basename = '%s.%s' % (tag['id'], extension)
                    data = library._get_file_data(basename)
                    source_code = data['data']
                    source_code = source_code.replace('\t', ' ' * 4)
                else:
                    source_code = get_source_code(tag)

                html = ast_to_html(source_code, parse_expr=parse_expr,
                                                complete_document=False,
                                                add_line_gutter=False,
                                                add_css=False)

                frag2 = BeautifulSoup(html, 'lxml', from_encoding='utf-8')

                if use_pre:
                    rendered = frag2.pre
                    if tag.has_attr('label'):
                        tag_label = soup.new_tag('span', **{'class': 'label'})
                        tag_label.append(tag['label'])
                        rendered.insert(0, tag_label)

                    max_len = max(map(len, source_code.split('\n')))
                    # account for the label
                    if tag.has_attr('label'):
                        max_len = max(max_len, len(tag['label']) + 6)

                    # need at least 1 to account for padding etc.
                    bonus = 1
                    style = 'width: %dch;' % (max_len + bonus)
                else:
                    # using <code>
                    rendered = frag2.pre.code
                    style = ''

                if tag.has_attr('style'):
                    style = style + tag['style']
                if style:
                    rendered['style'] = style

                if tag.has_attr('class'):
                    rendered['class'] = tag['class']

                if tag.has_attr('id'):
                    rendered['id'] = tag['id']

                tag.replaceWith(rendered)

            except DPSyntaxError as e:
                if raise_errors:
                    raise
                logger.error(unicode(e.__str__(), 'utf-8'))
                t = soup.new_tag('pre', **{'class': 'error %s' % type(e).__name__})
                t.string = str(e)
                tag.insert_after(t)

                if tag.string is None:
                    tag.string = "`%s" % tag['id']

            except DPSemanticError as e:
                if raise_errors:
                    raise
                logger.error(unicode(e.__str__(), 'utf-8'))
                t = soup.new_tag('pre', **{'class': 'error %s' % type(e).__name__})
                t.string = str(e)
                tag.insert_after(t)
                if tag.string is None:
                    tag.string = "`%s" % tag['id']

    go('pre.mcdp', Syntax.ndpt_dp_rvalue, "mcdp", use_pre=True)
    go('pre.mcdp_poset', Syntax.space, "mcdp_poset", use_pre=True)
    go('pre.mcdp_value', Syntax.rvalue, "mcdp_value", use_pre=True)
    go('pre.mcdp_template', Syntax.template, "mcdp_template", use_pre=True)
    go('pre.mcdp_statements', Syntax.dp_model_statements, "mcdp_statements", use_pre=True)

    go('code.mcdp', Syntax.ndpt_dp_rvalue, "mcdp", use_pre=False)
    go('code.mcdp_poset', Syntax.space, "mcdp_poset", use_pre=False)
    go('code.mcdp_value', Syntax.rvalue, "mcdp_value", use_pre=False)
    go('code.mcdp_template', Syntax.template, "mcdp_template", use_pre=False)

    return str(soup)

@contract(frag=str, returns=str)
def make_figures(library, frag, raise_error_dp, raise_error_others, realpath):
    """ Looks for codes like:

    <pre><code class="mcdp_ndp_graph_templatized">mcdp {
        # empty model
    }
    </code></pre>
    
        and creates a link to the image
    """

    soup = bs(frag)

    def go(selector, func):

        for tag in soup.select(selector):
            try:
                r = func(tag) 
                if tag.has_attr('style'):
                    r['style'] = tag['style']
                if tag.has_attr('class'):
                    r['class'] = tag['class']
                if tag.has_attr('id'):
                    r['id'] = tag['id']
                tag.replaceWith(r)
            except (DPSyntaxError, DPSemanticError) as e:
                if raise_error_dp:
                    raise
                print(e)
                t = soup.new_tag('pre', **{'class': 'error %s' % type(e).__name__})
                t.string = str(e)
                tag.insert_after(t)
            except Exception as e:
                if raise_error_others:
                    raise
                t = soup.new_tag('pre', **{'class': 'error %s' % type(e).__name__})
                t.string = traceback.format_exc(e)
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
            tag = BeautifulSoup(svg, 'lxml', from_encoding='utf-8').svg
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

    
    def func3(tag):  # ndp_graph_enclosed
        source_code = tag.string
        source_code = str(source_code)  # unicode
        ndp = library.parse_ndp(source_code)
        yourname = ''

        direction = str(tag.get('direction', default_direction))
        enclosed = bool_from_string(tag.get('enclosed', 'True'))
        return call(ndp_graph_enclosed, library=library, ndp=ndp, style=STYLE_GREENREDSYM,
                                 yourname=yourname, enclosed=enclosed,
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

    def func5(tag):  # ndp_graph_enclosed
        source_code = tag.string
        source_code = str(source_code)  # unicode
        template = library.parse_template(source_code)
        yourname = ''
        direction = str(tag.get('direction', default_direction))
        enclosed = bool_from_string(tag.get('enclosed', 'True'))
        from mcdp_web.images.images import ndp_template_graph_enclosed
        return call(ndp_template_graph_enclosed, library=library, template=template, style=STYLE_GREENREDSYM,
                                 yourname=yourname, enclosed=enclosed,
                                 direction=direction, klass='template_graph_enclosed')

    go('pre.ndp_graph_normal', func1)
    go('pre.ndp_graph_templatized', func2)
    go('pre.ndp_graph_templatized_labeled', func2b)
    go('pre.ndp_graph_enclosed', func3)
    go('pre.ndp_graph_expand', func4)
    go('pre.template_graph_enclosed', func5)

    return str(soup)

def create_img_png_base64(soup, png, **attrs):
    encoded = base64.b64encode(png)
    src = 'data:image/png;base64,%s' % encoded
    return soup.new_tag('img', src=src, **attrs)

def bool_from_string(b):
    yes = ['True', 'true', '1', 'yes']
    no = ['False', 'false', '0', 'no']
    if b in yes:
        return True
    if b in no:
        return False
    msg = 'Cannot interpret string as boolean.'
    raise_desc(ValueError, msg, b=b)
    
