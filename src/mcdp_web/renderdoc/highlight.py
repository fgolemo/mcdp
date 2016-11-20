# -*- coding: utf-8 -*-
import base64
import hashlib
import os
from tempfile import mkdtemp
import traceback

from bs4 import BeautifulSoup
from bs4.element import NavigableString

from contracts import contract
from contracts.utils import raise_desc, raise_wrapped, indent
from mcdp_lang.syntax import Syntax
from mcdp_library import MCDPLibrary
from mcdp_report.generic_report_utils import (
    NotPlottable, enlarge, get_plotters)
from mcdp_report.html import ast_to_html, get_markdown_css
from mcdp_report.plotters.get_plotters_imp import get_all_available_plotters
from mcdp_web.images.images import (get_mime_for_format, ndp_graph_enclosed,
    ndp_graph_expand, ndp_graph_normal, ndp_graph_templatized)
from mocdp import ATTR_LOAD_NAME, logger
from mocdp.exceptions import DPSemanticError, DPSyntaxError, DPInternalError
from reprep import Report
from system_cmd import CmdException, system_cmd_result
from mocdp.comp.context import Context
from mcdp_figures.figure_interface import MakeFiguresNDP, MakeFiguresTemplate


def bs(fragment):
    return BeautifulSoup(fragment, 'html.parser', from_encoding='utf-8')

@contract(returns=str, html=str)
def html_interpret(library, html, raise_errors=False, 
                   generate_pdf=False, realpath='unavailable'):
    # clone linrary?
    library = library.clone()
    load_fragments(library, html,
                   realpath=realpath)

    html = highlight_mcdp_code(library, html,
                               generate_pdf=generate_pdf,
                               raise_errors=raise_errors,
                               realpath=realpath)

    html = make_figures(library, html,
                        generate_pdf=generate_pdf,
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
                    tag_id = tag['id'].encode('utf-8')
                    vu = load(tag_id)
                else:
                    source_code = tag.string.encode('utf-8')
                    context = Context()
                    vu = parse(source_code, realpath=realpath, context=context)

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
            available = dict(get_plotters(get_all_available_plotters(), vu.unit))
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
        loads all the codes specified as "mcdp" and "mcdp_poset"
        
            <pre class='mcdp' id='id_ndp>
            code
            </pre>
    """
    soup = bs(frag)

    for tag in soup.select('pre.mcdp'):
        if tag.string is None:
            continue

        if tag.has_attr('id'):
            id_ndp = tag['id'].encode('utf-8')
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
            id_ndp = tag['id'].encode('utf-8')
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


@contract(body_contents=str, returns=str)
def get_minimal_document(body_contents, add_markdown_css=False):
    """ Creates the minimal html document with MCDPL css. """
    soup = bs("<html></html>")
    html = soup.html
    head = soup.new_tag('head')
    body = soup.new_tag('body')
    css = soup.new_tag('style', type='text/css')
    # <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    meta = soup.new_tag('meta')
    meta['http-equiv'] = "Content-Type"
    meta['content'] = "text/html; charset=utf-8"
    head.append(meta)
    from mcdp_report.html import get_language_css
    mcdp_css = get_language_css()
    markdown_css = get_markdown_css() if add_markdown_css else ""
    allcss = mcdp_css + '\n' + markdown_css
    css.append(NavigableString(allcss))
    head.append(css)
    body.append(bs(body_contents))
    html.append(head)
    html.append(body)
    s = str(html)
    return s

def get_ast_as_pdf(s, parse_expr):
    s = s.replace('\t', '    ')
    contents = ast_to_html(s, complete_document=False, extra_css=None,
                       ignore_line=None, parse_expr=parse_expr,
                       add_line_gutter=False, add_css=False)
    html = get_minimal_document(contents)
    d = mkdtemp()
    
    f_html = os.path.join(d, 'file.html')
    with open(f_html, 'w') as f:
        f.write(html)
        
    try:
        f_pdf = os.path.join(d, 'file.pdf')
        cmd= ['wkhtmltopdf','-s','A1',f_html,f_pdf]
        system_cmd_result(
                d, cmd, 
                display_stdout=False,
                display_stderr=False,
                raise_on_error=True)

        with open(f_pdf) as f:
            data = f.read()
        
        data = crop_pdf(data, margins=0)

        return data
    except CmdException as e:
        raise e

def crop_pdf(pdf, margins=0):
    d = mkdtemp()
    f_pdf = os.path.join(d, 'file.pdf')
    with open(f_pdf, 'w') as f:
        f.write(pdf)
    f_pdf_crop = os.path.join(d, 'file_crop.pdf')
    cmd = ['pdfcrop', '--margins', str(margins), f_pdf, f_pdf_crop]
    system_cmd_result(
            d, cmd,
            display_stdout=False,
            display_stderr=False,
            raise_on_error=True)

    with open(f_pdf_crop) as f:
        data = f.read()
    return data

def highlight_mcdp_code(library, frag, realpath, generate_pdf=False, raise_errors=False):
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
                    tag_id = tag['id'].encode('utf-8')
                    basename = '%s.%s' % (tag_id, extension)
                    data = library._get_file_data(basename)
                    source_code = data['data']
                    source_code = source_code.replace('\t', ' ' * 4)
                else:
                    source_code = get_source_code(tag)

                # we are not using it
                _realpath = realpath
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

                if use_pre:
                    if generate_pdf:
                        pdf = get_ast_as_pdf(source_code, parse_expr)
                        if tag.has_attr('id'):
                            basename = tag['id']
                        else:
                            hashcode = hashlib.sha224(source_code).hexdigest()[-8:]
                            basename = 'code-%s' % (hashcode)

                        docname = os.path.splitext(os.path.basename(realpath))[0]
                        download = docname + '.' + basename + '.source_code.pdf'
                        a = create_a_to_data(soup, download=download,
                                             data_format='pdf', data=pdf)
                        a['class'] = 'pdf_data'
                        a.append(NavigableString(download))
                        div = soup.new_tag('div')
                        div.append(rendered)
                        div.append(a)
                        tag.replaceWith(div)
                    else:
                        tag.replaceWith(rendered)
                else:
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
                    
            except DPInternalError as e:
                msg = 'Error while interpreting the code:\n\n'
                msg += indent(source_code, '  | ')
                raise_wrapped(DPInternalError, e,msg, exc=sys.exc_info())
                

    go('pre.mcdp', Syntax.ndpt_dp_rvalue, "mcdp", use_pre=True)
    go('pre.mcdp_poset', Syntax.space, "mcdp_poset", use_pre=True)
    go('pre.mcdp_template', Syntax.template, "mcdp_template", use_pre=True)
    go('pre.mcdp_statements', Syntax.dp_model_statements, "mcdp_statements", use_pre=True)
    go('pre.mcdp_fvalue', Syntax.fvalue, "mcdp_fvalue", use_pre=True)
    go('pre.mcdp_rvalue', Syntax.rvalue, "mcdp_rvalue", use_pre=True)
    # todo: add deprecation
    go('pre.mcdp_value', Syntax.rvalue, "mcdp_value", use_pre=True)

    go('code.mcdp', Syntax.ndpt_dp_rvalue, "mcdp", use_pre=False)
    go('code.mcdp_poset', Syntax.space, "mcdp_poset", use_pre=False)
    go('code.mcdp_value', Syntax.rvalue, "mcdp_value", use_pre=False)
    go('code.mcdp_template', Syntax.template, "mcdp_template", use_pre=False)

    return str(soup)

import sys

@contract(frag=str, returns=str)
def make_figures(library, frag, raise_error_dp, raise_error_others, realpath, generate_pdf):
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
     

    def make_tag(tag0, klass, data, ndp=None, template=None):
        
        if False:
            png = data['png']
            r = create_img_png_base64(soup, png, **{'class': klass})
            return r
        else:
            svg = data['svg']

            tag_svg = BeautifulSoup(svg, 'lxml', from_encoding='utf-8').svg
            tag_svg['class'] = klass

            if tag0.has_attr('style'):
                tag_svg['style'] = tag0['style']
            if tag0.has_attr('id'):
                tag_svg['id'] = tag0['id']

            if generate_pdf:
                pdf0 = data['pdf']
                pdf = crop_pdf(pdf0, margins=0)

                div = soup.new_tag('div')

                if tag0.has_attr('id'):
                    basename = tag0['id']
                elif ndp is not None and hasattr(ndp, ATTR_LOAD_NAME):
                    basename = getattr(ndp, ATTR_LOAD_NAME)
                elif template is not None and hasattr(template, ATTR_LOAD_NAME):
                    basename = getattr(template, ATTR_LOAD_NAME)
                else:
                    hashcode = hashlib.sha224(tag0.string).hexdigest()[-8:]
                    basename = 'code-%s' % (hashcode)

                docname = os.path.splitext(os.path.basename(realpath))[0]
                download = docname + "." + basename + "." + klass + '.pdf'
                a = create_a_to_data(soup, download=download, data_format='pdf', data=pdf)
                a['class'] = 'pdf_data'
                a.append(NavigableString(download))
                div.append(tag_svg)
                div.append(a)
                return div
            else:
                return tag_svg

    
    mf = MakeFiguresNDP(None,None,None)
    available = set(mf.available()) | set(mf.aliases)
    for which in available:
        selector = 'pre.%s' % which
        def callback(tag0):
            source_code = tag0.string.encode('utf-8')
            context = Context()
            ndp = library.parse_ndp(source_code, realpath=realpath, context=context)
            mf = MakeFiguresNDP(ndp=ndp, library=library, yourname=None) # XXX
            formats = ['svg']
            if generate_pdf: 
                formats.append('pdf')
            data = mf.get_figure(which,formats)
            tag = make_tag(tag0, which, data, ndp=ndp, template=None)
            return tag
        
        go(selector, callback)
    
    mf = MakeFiguresTemplate(None,None,None)
    available = set(mf.available()) | set(mf.aliases)
    for which in available:
        selector = 'pre.%s' % which
        def callback(tag0):
            source_code = tag0.string.encode('utf-8')
            context = Context()
            template = library.parse_template(source_code, realpath=realpath, context=context)

            mf = MakeFiguresTemplate(template=template, library=library, yourname=None) # XXX
            formats = ['svg']
            if generate_pdf: 
                formats.append('pdf')
            data = mf.get_figure(which,formats)
            tag = make_tag(tag0, which, data, ndp=None, template=template)
            return tag
        
        go(selector, callback)
        

#     go('pre.ndp_graph_normal', ndp_graph_normal_)
#     go('pre.ndp_graph_templatized', ndp_graph_templatized_)
#     go('pre.ndp_graph_templatized_labeled', ndp_graph_templatized_labeled_)
#     go('pre.ndp_graph_enclosed', ndp_graph_enclosed_)
#     go('pre.ndp_graph_expand', ndp_graph_expand_)
#     go('pre.template_graph_enclosed', template_graph_enclosed_)

    return str(soup)

@contract(data_format=str, data=str, download=str)
def create_a_to_data(soup, download, data_format, data):
    """ Returns a tag with base64 encoded data """
    assert data_format in ['pdf', 'png']
    mime = get_mime_for_format(data_format)
    encoded = base64.b64encode(data)
    href = 'data:%s;base64,%s' % (mime, encoded)
    attrs = dict(href=href, download=download)
    print('download: %s' % download)
    return soup.new_tag('a', **attrs)

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
    


#     def ndp_graph_normal_(tag):
#         source_code = tag.string.encode('utf-8')
#         context = Context()
#         ndp = library.parse_ndp(source_code, realpath=realpath, context=context)
#         yourname = ''
#         direction = str(tag.get('direction', default_direction))
#         
#         return call(tag, ndp_graph_normal,
#                     library=library,
#                     ndp=ndp,
#                     style=STYLE_GREENREDSYM,
#                     yourname=yourname,
#                     direction=direction,
#                     klass='ndp_graph_normal')
#         
#     def ndp_graph_templatized_(tag):
#         source_code = tag.string.encode('utf-8')
#         context = Context()
#         ndp = library.parse_ndp(source_code, realpath=realpath, context=context)
#         yourname = ''
#         direction = str(tag.get('direction', default_direction))
# 
#         return call(tag, ndp_graph_templatized, library=library, ndp=ndp,
#                     yourname=yourname,
#                     direction=direction, klass='ndp_graph_templatized')
# 
#     def ndp_graph_templatized_labeled_(tag):
#         source_code = tag.string.encode('utf-8')
#         context = Context()
#         ndp = library.parse_ndp(source_code, realpath=realpath, context=context)
#         yourname = None 
#         if hasattr(ndp, ATTR_LOAD_NAME):
#             yourname = getattr(ndp, ATTR_LOAD_NAME)
#         direction = str(tag.get('direction', default_direction))
# 
#         return call(tag, ndp_graph_templatized, library=library, ndp=ndp,
#                     direction=direction,
#                     yourname=yourname, klass='ndp_graph_templatized_labeled')
# 
#     def ndp_graph_enclosed_(tag):  # ndp_graph_enclosed
#         source_code = tag.string.encode('utf-8')
#         context = Context()
#         ndp = library.parse_ndp(source_code, realpath=realpath, context=context)
#         yourname = ''
# #         raise Exception()
#         direction = str(tag.get('direction', default_direction))
#         enclosed = bool_from_string(tag.get('enclosed', 'True'))
#         
#         return call(tag, ndp_graph_enclosed, library=library, ndp=ndp,
#                     style=STYLE_GREENREDSYM,
#                      yourname=yourname, enclosed=enclosed,
#                      direction=direction, klass='ndp_graph_enclosed')
# 
#     def ndp_graph_expand_(tag):
#         source_code = tag.string.encode('utf-8')
#         context = Context()
#         ndp = library.parse_ndp(source_code, realpath=realpath, context=context)
#         yourname = ''
# 
#         direction = str(tag.get('direction', default_direction))
# 
#         return call(tag, ndp_graph_expand, library=library, ndp=ndp,
#                     style=STYLE_GREENREDSYM,
#                      yourname=yourname,
#                      direction=direction,
#                      klass='ndp_graph_expand')
# 
#     def template_graph_enclosed_(tag):  # ndp_graph_enclosed
#         source_code = tag.string.encode('utf-8')
#         context = Context()
#         template = library.parse_template(source_code, realpath=realpath, context=context)
#         yourname = ''
#         direction = str(tag.get('direction', default_direction))
#         enclosed = bool_from_string(tag.get('enclosed', 'True'))
#         from mcdp_web.images.images import ndp_template_graph_enclosed
#         return call(tag, ndp_template_graph_enclosed, library=library,
#                     template=template, style=STYLE_GREENREDSYM,
#                      yourname=yourname, enclosed=enclosed,
#                      direction=direction, klass='template_graph_enclosed')
