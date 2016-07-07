from bs4 import BeautifulSoup
from contracts.utils import raise_desc, raise_wrapped
from mcdp_lang.syntax import Syntax
from mcdp_library.library import MCDPLibrary
from mcdp_report.generic_report_utils import (
    NotPlottable, enlarge, get_plotters, plotters)
from mcdp_report.html import ast_to_html
from mcdp_web.images.images import (ndp_graph_enclosed, ndp_graph_expand,
    ndp_graph_normal, ndp_graph_templatized)
from mocdp.exceptions import DPSemanticError, DPSyntaxError
from reprep import Report
import base64
import traceback


def html_interpret(library, html, raise_errors=False):
    # clone linrary?
    library = library.clone()
    load_fragments(library, html, realpath='unavailable')
    html = highlight_mcdp_code(library, html)
    html = make_figures(library, html,
                        raise_error_dp=raise_errors, raise_error_others=raise_errors)
    html = make_plots(library, html, raise_errors=raise_errors)
    return html.decode('utf-8')

def make_image_tag_from_png(f):
    soup = BeautifulSoup("", 'html.parser')
    def ff(*args, **kwargs):
        png = f(*args, **kwargs)
        rendered = create_img_png_base64(soup, png)
        return rendered
    return ff

# def get_string_or_cdata(tag):
#     print tag
#     if tag.string is not None:
#         return tag.string
#     for cd in tag.findAll(text=True):
#         if isinstance(cd, bs4.CData):
#             print 'CData value: %r' % cd
#             return cd
#     assert False

def make_plots(library, frag, raise_errors):
    """
        Looks for things like:
        
        
        <img class="value_plot_generic">VALUE</img>
        
        <img class="value_plot_generic" id='value"/>
    
    """
    soup = BeautifulSoup(frag, 'html.parser')

    def go(selector, plotter):
        for tag in soup.select(selector):

#             source_code = get_string_or_cdata(tag)
            # load value with units in vu
            if tag.string is None:
                if not tag.has_attr('id'):
                    msg = "If <img> is empty then it needs to have an id."
                    raise_desc(ValueError, msg, tag=str(tag))
                # load it
                vu = library.load_constant(tag['id'])
            else:
                source_code = tag.string
                vu = library.parse_constant(source_code)

            try:
                rendered = plotter(tag, vu)

                if tag.has_attr('style'):
                    style = tag['style']
                else:
                    style = ''

                if style:
                    rendered['style'] = style
                tag.replaceWith(rendered)

            except DPSyntaxError as e:
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
    def plot_value_generic(tag, vu):
        r = Report()
        f = r.figure()
        # generic_plot(f, space=vu.unit, value=vu.value)
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
        return  png
    
    go("img.plot_value_generic", plot_value_generic)
    return str(soup)

def load_fragments(library, frag, realpath):
    """
        loads all the codes 
        
            <pre class='mcdp' id='id_ndp>
            code
            </pre>
    """
    soup = BeautifulSoup(frag, 'html.parser')

    for tag in soup.select('pre.mcdp'):
        if tag.string is None:
            continue

        if tag.has_attr('id'):
            id_ndp = tag['id']
            source_code = str(tag.string)

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
            source_code = str(tag.string)

            basename = '%s.%s' % (id_ndp, MCDPLibrary.ext_posets)
            res = dict(data=source_code, realpath=realpath)

            if basename in library.file_to_contents:
                msg = 'Duplicated entry.'
                raise_desc(ValueError, msg, tag=str(tag),
                           known=library.file_to_contents[basename])

            library.file_to_contents[basename] = res


def highlight_mcdp_code(library, frag):
    """ Looks for codes like:
    
    <pre class="mcdp">mcdp {
        # empty model
    }
    </pre>
    
        and does syntax hihglighting.
    """

    soup = BeautifulSoup(frag, 'html.parser')

    def go(selector, parse_expr, extension):
        for tag in soup.select(selector):
            
            if tag.string is None:
                if not tag.has_attr('id'):
                    msg = "If <pre> is empty then it needs to have an id."
                    raise_desc(ValueError, msg, tag=str(tag))
                # load it
                basename = '%s.%s' % (tag['id'], extension)
                data = library._get_file_data(basename)
                source_code = data['data']
            else:
                source_code = tag.string
                while source_code and source_code[0] == '\n':
                    source_code = source_code[1:]

            source_code = source_code.replace('\t', ' ' * 4)
            try:
                html = ast_to_html(source_code, parse_expr=parse_expr,
                                            complete_document=False,
                                            add_line_gutter=False)
                frag2 = BeautifulSoup(html, 'lxml')
                rendered = frag2.pre
                if tag.has_attr('label'):
                    tag_label = soup.new_tag('span', **{'class': 'label'})
                    tag_label.append(tag['label'])
                    rendered.insert(0, tag_label)

#                 if tag.has_attr('style'):
#                     rendered['style'] = tag['style']

                max_len = max(map(len, source_code.split('\n')))
                # account for the label
                if tag.has_attr('label'):
                    max_len = max(max_len, len(tag['label']) + 6)

                style = 'width: %dch;' % (max_len + 3)
                if tag.has_attr('style'):
                    style = style + tag['style']

                rendered['style'] = style
                tag.replaceWith(rendered)

            except DPSyntaxError as e:
                print(e)  # XXX
                t = soup.new_tag('pre', **{'class': 'error %s' % type(e).__name__})
                t.string = str(e)
                tag.insert_after(t)

    go('pre.mcdp', Syntax.ndpt_dp_rvalue, "mcdp")
    go('pre.mcdp_poset', Syntax.space, "mcdp_poset")
    go('pre.mcdp_value', Syntax.rvalue, "mcdp_value")
    go('pre.mcdp_template', Syntax.template, "mcdp_template")
    return str(soup)

def make_figures(library, frag, raise_error_dp, raise_error_others):
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
                if tag.has_attr('style'):
                    r['style'] = tag['style']
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

    
    def func3(tag):  # ndp_graph_enclosed
        source_code = tag.string
        source_code = str(source_code)  # unicode
        ndp = library.parse_ndp(source_code)
        yourname = ''

        direction = str(tag.get('direction', default_direction))
        enclosed = bool_from_string(tag.get('enclosed', 'True'))
#         print "enclosed: %r %r" % (tag.get('enclosed', False), enclosed)
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

def bool_from_string(b):
    yes = ['True', 'true', '1', 'yes']
    no = ['False', 'false', '0', 'no']
    if b in yes:
        return True
    if b in no:
        return False
    msg = 'Cannot interpret string as boolean.'
    raise_desc(ValueError, msg, b=b)
    
