# -*- coding: utf-8 -*-
import base64
import hashlib
import os
import shutil
import sys
from tempfile import mkdtemp
import traceback

from bs4 import BeautifulSoup
from bs4.element import NavigableString

from contracts import contract
from contracts.utils import raise_desc, raise_wrapped, indent
from mcdp_lang.parse_interface import (parse_template_refine, parse_poset_refine,
    parse_ndp_refine)
from mcdp_lang.syntax import Syntax
from mcdp_library import MCDPLibrary
from mcdp_report.generic_report_utils import (
    NotPlottable, enlarge, get_plotters)
from mcdp_report.html import ast_to_html, get_markdown_css
from mcdp_report.plotters.get_plotters_imp import get_all_available_plotters
from mcdp_web.images.images import (get_mime_for_format)
from mocdp import ATTR_LOAD_NAME, logger, get_mcdp_tmp_dir 
from mocdp.comp.context import Context
from mocdp.exceptions import DPSemanticError, DPSyntaxError, DPInternalError
from reprep import Report
from system_cmd import CmdException, system_cmd_result


from mcdp_figures import( MakeFiguresNDP, MakeFiguresTemplate, 
    MakeFiguresPoset)
from mcdp_lang.suggestions import get_suggestions, apply_suggestions
from mcdp_lang.parse_actions import parse_wrap



def bs(fragment):
    return BeautifulSoup(fragment, 'html.parser', from_encoding='utf-8')

@contract(returns=str, html=str)
def html_interpret(library, html, raise_errors=False, 
                   generate_pdf=False, realpath='unavailable'):
    # clone library?
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

    
def load_or_parse_from_tag(tag, load, parse):
    """ 
        If tag.string is not None, then it parses the contents
        using the function parse.
        
        Otherwise it tries to load the id given.
        
        If empty and no ID, raises excxception.
        
        Either 
            <tag  class=... id='poset'>
        or 
            <tag  class=...>my code </tag
    """
    if tag.string is None:
        if not tag.has_attr('id'):
            msg = "If <img> is empty then it needs to have an id."
            raise_desc(ValueError, msg, tag=str(tag))
        # load it
        tag_id = tag['id'].encode('utf-8')
        vu = load(tag_id)
    else:
        source_code = tag.string.encode('utf-8')
        vu = parse(source_code)    
    return vu

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
                
                def parsing(source_code):
                    context = Context()
                    return parse(source_code, realpath=realpath, context=context)
                    
                vu = load_or_parse_from_tag(tag, load, parsing) 
                
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
    contents = ast_to_html(s,
                       ignore_line=None, parse_expr=parse_expr,
                       add_line_gutter=False)
    html = get_minimal_document(contents)
    
    mcdp_tmp_dir = get_mcdp_tmp_dir()
    prefix = 'get_ast_as_pdf()'
    d = mkdtemp(dir=mcdp_tmp_dir, prefix=prefix)
    
    try:
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
    finally:
        shutil.rmtree(d)


def crop_pdf(pdf, margins=0):
    
    mcdp_tmp_dir = get_mcdp_tmp_dir()
    prefix = 'crop_pdf()'
    d = mkdtemp(dir=mcdp_tmp_dir, prefix=prefix)
    
    try:
        f_pdf = os.path.join(d, 'file.pdf')
        with open(f_pdf, 'w') as f:
            f.write(pdf)
        f_pdf_crop = os.path.join(d, 'file_crop.pdf')
        cmd = [
            'pdfcrop', 
            '--margins', 
            str(margins), 
            f_pdf, 
            f_pdf_crop,
        ]
        system_cmd_result(
                d, cmd,
                display_stdout=False,
                display_stderr=False,
                raise_on_error=True)
    
        with open(f_pdf_crop) as f:
            data = f.read()
        return data
    finally:
        shutil.rmtree(d)
        
def highlight_mcdp_code(library, frag, realpath, generate_pdf=False, raise_errors=False):
    """ Looks for codes like:
    
    <pre class="mcdp">mcdp {
        # empty model
    }
    </pre>
    
        and does syntax hihglighting.
    """

    soup = bs(frag)

    def go(selector, parse_expr, extension, use_pre=True, refine=None):
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
                    
                # prettify. 
                # remove spurious indentation
                source_code = source_code.strip()
                
                do_apply_suggestions = True
                # then apply suggestions
                if do_apply_suggestions:
                    x = parse_wrap(parse_expr, source_code)[0]
                    xr = parse_ndp_refine(x, Context())
                    suggestions = get_suggestions(xr)
                    source_code = apply_suggestions(source_code, suggestions)   
    
                # we are not using it
                _realpath = realpath
                context = Context()
                def postprocess(x):
                    if refine is not None:
                        return refine(x, context=context)
                    else:
                        return x
                html = ast_to_html(source_code, parse_expr=parse_expr,
                                                add_line_gutter=False,
                                                postprocess=postprocess)
                
                
                for w in context.warnings:
                    if w.where is not None:
                        from mcdp_web.editor_fancy.app_editor_fancy_generic import html_mark
                        html = html_mark(html, w.where, "language_warning")
                        
                frag2 = BeautifulSoup(html, 'lxml', from_encoding='utf-8')

                if use_pre:
                    rendered = frag2.pre
                    if tag.has_attr('label'):
                        tag_label = soup.new_tag('span', **{'class': 'label'})
                        tag_label.append(tag['label'])
                        rendered.insert(0, tag_label)

                    max_len = max_len_of_pre_html(html)
                    frag2.pre['string_len'] = max_len
                    if tag.has_attr('label'):
                        max_len = max(max_len, len(tag['label']) + 6)
                        
                    add_style_for_size(frag2.pre, max_len)
                    style = ''
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
                

    go('pre.mcdp', Syntax.ndpt_dp_rvalue,  "mcdp", use_pre=True, refine=parse_ndp_refine)
    go('pre.mcdp_poset', Syntax.space, "mcdp_poset", use_pre=True, refine=parse_poset_refine)
    go('pre.mcdp_template', Syntax.template, "mcdp_template", use_pre=True,
        refine=parse_template_refine)
       
    go('pre.mcdp_statements', Syntax.dp_model_statements, "mcdp_statements", use_pre=True)
    go('pre.mcdp_fvalue', Syntax.fvalue, "mcdp_fvalue", use_pre=True)
    go('pre.mcdp_rvalue', Syntax.rvalue, "mcdp_rvalue", use_pre=True)
    # todo: add deprecation
    go('pre.mcdp_value', Syntax.rvalue, "mcdp_value", use_pre=True)

    go('code.mcdp', Syntax.ndpt_dp_rvalue, "mcdp", use_pre=False)
    go('code.mcdp_poset', Syntax.space, "mcdp_poset", use_pre=False)
    go('code.mcdp_value', Syntax.rvalue, "mcdp_value", use_pre=False)
    go('code.mcdp_template', Syntax.template, "mcdp_template", use_pre=False)

    compute_size_for_pre_without_class(soup)

    return str(soup)

def compute_size_for_pre_without_class(soup):
    for pre in soup.select('pre'):
        if not pre.has_attr('class'):
            s = ''.join(pre.findAll(text=True))
            max_len = max_len_of_pre_html(s)
            add_style_for_size(pre, max_len)

# think of :[[space]] × [[space]] × [["..."]] × [[space]]
def max_len_of_pre_html(html):
    from mcdp_report_ndp_tests.test0 import project_html
    source2 = project_html(html)
    line_len = lambda _: len(unicode(_, 'utf-8').rstrip())
    max_len = max(map(line_len, source2.split('\n')))
    return max_len 

def add_style_for_size(element, max_len):         
    fontsize = 14 # px
    fontname = 'Courier'
    ratio = 0.65 # ratio for Courier font
    width = fontsize * (max_len) * ratio
    style = 'font-family: %s; font-size: %spx; width: %dpx;' % (fontname, fontsize, width)
    
    if element.has_attr('style'):
        style = element['style'] +';' + style
            
    element['style'] = style
    

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
                logger.error(e)
                t = soup.new_tag('pre', **{'class': 'error %s' % type(e).__name__})
                t.string = str(e)
                tag.insert_after(t)
            except Exception as e:
                if raise_error_others:
                    raise
                t = soup.new_tag('pre', **{'class': 'error %s' % type(e).__name__})
                t.string = traceback.format_exc(e)
                tag.insert_after(t)
     

    def make_tag(tag0, klass, data, ndp=None, template=None, poset=None):
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
            elif poset is not None and hasattr(poset, ATTR_LOAD_NAME):
                basename = getattr(poset, ATTR_LOAD_NAME)
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

    
    mf = MakeFiguresNDP(None, None, None)
    available = set(mf.available()) | set(mf.aliases)
    for which in available:
        def callback(tag0):
            context = Context()
            load = lambda x: library.load_ndp(x, context=context)
            parse = lambda x: library.parse_ndp(x, realpath=realpath, context=context)  
            ndp = load_or_parse_from_tag(tag0, load, parse)

            mf = MakeFiguresNDP(ndp=ndp, library=library, yourname=None) # XXX
            formats = ['svg']
            if generate_pdf: 
                formats.append('pdf')
            data = mf.get_figure(which,formats)
            tag = make_tag(tag0, which, data, ndp=ndp, template=None)
            return tag
        
        selector = 'pre.%s' % which
        go(selector, callback)
        selector = 'img.%s' % which
        go(selector, callback)
    
    mf = MakeFiguresTemplate(None,None,None)
    available = set(mf.available()) | set(mf.aliases)
    for which in available:
        def callback(tag0):
            context = Context()
            load = lambda x: library.load_template(x, context=context)
            parse = lambda x: library.parse_template(x, realpath=realpath, context=context)  
            template = load_or_parse_from_tag(tag0, load, parse)

            mf = MakeFiguresTemplate(template=template, library=library, yourname=None) # XXX
            formats = ['svg']
            if generate_pdf: 
                formats.append('pdf')
            data = mf.get_figure(which,formats)
            tag = make_tag(tag0, which, data, ndp=None, template=template)
            return tag
        
        selector = 'pre.%s' % which
        go(selector, callback)
        selector = 'img.%s' % which
        go(selector, callback)
        
    mf = MakeFiguresPoset(None)
    available = set(mf.available()) | set(mf.aliases)
    for which in available:
        def callback(tag0):
            context = Context()
            load = lambda x: library.load_poset(x, context=context)
            parse = lambda x: library.parse_poset(x, realpath=realpath, context=context)  
            poset = load_or_parse_from_tag(tag0, load, parse)
            
            mf = MakeFiguresPoset(poset=poset, library=library)
            formats = ['svg']
            if generate_pdf: 
                formats.append('pdf')
            data = mf.get_figure(which, formats)
            tag = make_tag(tag0, which, data, ndp=None, template=None, poset=poset)
            return tag
        
        selector = 'pre.%s' % which
        go(selector, callback)
        selector = 'img.%s' % which
        go(selector, callback)
         

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
    

