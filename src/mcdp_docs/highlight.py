# -*- coding: utf-8 -*-
import hashlib
import os
import sys
import textwrap

from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag
from contracts.utils import raise_desc, raise_wrapped, indent

from mcdp import logger, MCDPConstants
from mcdp.development import mcdp_dev_warning
from mcdp.exceptions import DPSemanticError, DPSyntaxError, DPInternalError
from mcdp_docs.make_plots_imp import make_plots
from mcdp_docs.pdf_ops import crop_pdf, get_ast_as_pdf
from mcdp_figures import MakeFiguresNDP, MakeFiguresTemplate, MakeFiguresPoset
from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.parse_interface import (parse_template_refine, parse_poset_refine,
                                       parse_ndp_refine)
from mcdp_lang.suggestions import get_suggestions, apply_suggestions, get_suggested_identifier
from mcdp_lang.syntax import Syntax
from mcdp_library.specs_def import SPEC_TEMPLATES
from mcdp_report.html import ast_to_html
from mcdp_utils_xml import to_html_stripping_fragment, describe_tag, project_html
from mcdp_utils_xml.add_class_and_style import add_class
from mcdp_utils_xml.images import create_img_png_base64, create_a_to_data
from mcdp_utils_xml.note_errors_inline import note_error
from mocdp.comp.context import Context


def html_interpret(library, soup, raise_errors=False,
                   generate_pdf=False, realpath='unavailable'):
    # clone library, so that we don't pollute it
    # with our private definitions

#     
#     if not raise_errors:
#         logger.error('raise_errors is False: we add errors in the document')

    library = library.clone()
    load_fragments(library, soup, realpath=realpath)

    highlight_mcdp_code(library, soup,
                               generate_pdf=generate_pdf,
                               raise_errors=raise_errors,
                               realpath=realpath)

    make_plots(library, soup,
                      raise_errors=raise_errors,
                      realpath=realpath)
    # let's do make_plots first; then make_figures will
    # check for remaining <render> elements.
    make_figures(library, soup,
                        generate_pdf=generate_pdf,
                        raise_error_dp=raise_errors,
                        raise_error_others=raise_errors,
                        realpath=realpath)


def make_image_tag_from_png(f):
    def ff(*args, **kwargs):
        png = f(*args, **kwargs)
        rendered = create_img_png_base64( png)
        return rendered
    return ff

def make_pre(f):
    def ff(*args, **kwargs):
        res = f(*args, **kwargs)
        pre = Tag(name='pre')  #  **{'class': 'print_value'})
        code = Tag(name='code')
        code.string = res
        pre.append(code)
        return pre
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
    if tag.string is None: # or not tag.string.strip():
        if not tag.has_attr('id'):
            msg = "If <img> is empty then it needs to have an id."
            raise_desc(ValueError, msg, tag=str(tag))
        # load it
        tag_id = tag['id'].encode('utf-8')
        vu = load(tag_id)
    else:
        source_code = get_source_code(tag)
        vu = parse(source_code)
    return vu

def load_fragments(library, soup, realpath):
    """
        loads all the codes specified as

            <pre class="mcdp" id='...'>...</pre>
            <pre class="mcdp_poset" id='...'>...</pre>
            <pre class="mcdp_template" id='...'>...</pre>

    """

    for tag in soup.select('pre.mcdp'):
        if tag.string is None or not tag.string.strip():
            continue

        if tag.has_attr('id'):
            id_ndp = tag['id'].encode('utf-8')
            source_code = get_source_code(tag)

            basename = '%s.%s' % (id_ndp, MCDPConstants.ext_ndps)
            res = dict(data=source_code, realpath=realpath)

            if basename in library.file_to_contents:
                msg = 'The id %r has already been used previously.' % basename
                raise_desc(ValueError, msg, tag=str(tag),
                           known=library.file_to_contents[basename])

            library.file_to_contents[basename] = res

    for tag in soup.select('pre.mcdp_poset'):
        if tag.string is None:# or not tag.string.strip():
            continue

        if tag.has_attr('id'):
            id_ndp = tag['id'].encode('utf-8')
            source_code = get_source_code(tag)

            basename = '%s.%s' % (id_ndp, MCDPConstants.ext_posets)
            res = dict(data=source_code, realpath=realpath)

            if basename in library.file_to_contents:
                msg = 'Duplicated entry.'
                raise_desc(ValueError, msg, tag=str(tag),
                           known=library.file_to_contents[basename])

            library.file_to_contents[basename] = res

    for tag in soup.select('pre.mcdp_template'):
        if tag.string is None:# or not tag.string.strip():
            continue

        if tag.has_attr('id'):
            id_ndp = tag['id'].encode('utf-8')
            source_code = get_source_code(tag)

            basename = '%s.%s' % (id_ndp, MCDPConstants.ext_templates)
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

        decodes entities
    """
    if tag.string is None:
        raise ValueError(str(tag))

    s0 = tag.string

    from HTMLParser import HTMLParser
    h = HTMLParser()
    s1 = h.unescape(s0)
#     if False:
#         if s1 != s0:
# #             print('decoded %r -> %r' % (s0, s1))
#             pass

    source_code = s1.encode('utf-8')

    # remove first newline
    while source_code and source_code[0] == '\n':
        source_code = source_code[1:]

#     print(indent(source_code, 'bef|'))
    # remove common whitespace (so that we can indent html elements)
    source_code = textwrap.dedent(source_code)
#     print(indent(source_code, 'aft|'))
    #source_code = source_code.replace('\t', ' ' * 4)

    if tag.name == 'code':
        if '\n' in source_code:
            logger.debug('Treating newline in %r as space' % source_code)
            source_code = source_code.replace('\n', ' ')

    return source_code


def highlight_mcdp_code(library, soup, realpath, generate_pdf=False, raise_errors=False):
#     print(indent(frag, 'highlight_mcdp_code '))
    """ Looks for codes like:

    <pre class="mcdp">mcdp {
        # empty model
    }
    </pre>

        and does syntax hihglighting.
    """

    assert soup.name == 'fragment'

    def go(selector, parse_expr, extension, use_pre=True, refine=None):
        for tag in soup.select(selector):
            try:
                if tag.string is None: # or not tag.string.strip():
                    if not tag.has_attr('id'):
                        msg = "If <pre> is empty then it needs to have an id."
                        raise_desc(ValueError, msg, tag=describe_tag(tag))

                    # load it
                    tag_id = tag['id'].encode('utf-8')
                    if '.' in tag_id:
                        i = tag_id.index('.')
                        libname, name = tag_id[:i], tag_id[i+1:]
                        use_library = library.load_library(libname)
                    else:
                        name = tag_id
                        use_library= library
                    basename = '%s.%s' % (name, extension)
                    data = use_library._get_file_data(basename)
                    source_code = data['data']
                else:
                    source_code = get_source_code(tag)

                # prettify.
                # remove spurious indentation
                source_code = source_code.strip()

                do_apply_suggestions = (not tag.has_attr('noprettify') and
                                        not tag.has_attr('np'))
                # then apply suggestions
                try:
                    if do_apply_suggestions:
                        x = parse_wrap(parse_expr, source_code)[0]
                        xr = parse_ndp_refine(x, Context())
                        suggestions = get_suggestions(xr)
                        source_code = apply_suggestions(source_code, suggestions)
                except DPSyntaxError as e:
                    if raise_errors:
                        raise
                    else:
                        note_error(tag, e)
                        continue
                # we don't want the browser to choose different tab size
                #source_code = source_code.replace('\t', ' ' * 4)

                # we are not using it
                _realpath = realpath
                context = Context()
                def postprocess(x):
                    if refine is not None:
                        return refine(x, context=context)
                    else:
                        return x
#                 print('rendering source code %r' % source_code)
                html = ast_to_html(source_code, parse_expr=parse_expr,
                                                add_line_gutter=False,
                                                postprocess=postprocess)

                for w in context.warnings:
                    if w.where is not None:
                        from mcdp_web.editor_fancy.app_editor_fancy_generic import html_mark
                        html = html_mark(html, w.where, "language_warning")

                frag2 = BeautifulSoup(html, 'lxml', from_encoding='utf-8')

                if use_pre:
                    rendered = Tag(name='div', attrs={'class':'rendered'})
                    pre = frag2.pre
                    pre.extract()
                    rendered.append(pre)
                    if not rendered.has_attr('class'):
                        rendered['class'] = ""
                    if tag.has_attr('label'):
                        text = tag['label']
                        tag_label = Tag(name='span')
                        add_class(tag_label, 'label')
                        add_class(tag_label, 'label_inside')
                        tag_label.append(NavigableString(text))

                        pre.insert(0, tag_label)

                        tag_label_outside = Tag(name='span')
                        add_class(tag_label_outside, 'label')
                        add_class(tag_label_outside, 'label_outside')
                        tag_label_outside.append(NavigableString(text))
                        rendered.insert(0, tag_label_outside)

                    max_len = max_len_of_pre_html(html)

                    if tag.has_attr('label'):
                        add_class(rendered, 'has_label')
                        max_len = max(max_len, len(tag['label']) + 6)

                    style = ''
                else:
                    # using <code>
                    rendered =  frag2.pre.code
                    rendered.extract()
                    if not rendered.has_attr('class'):
                        rendered['class'] = ""

                    style = ''

                if tag.has_attr('style'):
                    style = style + tag['style']

                if style:
                    rendered['style'] = style

                if tag.has_attr('class'):
                    add_class(rendered, tag['class'])

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
                        a = create_a_to_data(download=download,
                                             data_format='pdf', data=pdf)
                        a['class'] = 'pdf_data'
                        a.append(NavigableString(download))
                        div = Tag(name='div')
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
                else:
                    note_error(tag, e)
                    if tag.string is None:
                        tag.string = "`%s" % tag['id']
                    continue

            except DPSemanticError as e:
                if raise_errors:
                    raise
                else:
                    note_error(tag, e)
                    if tag.string is None:
                        tag.string = "`%s" % tag['id']
                    continue

            except DPInternalError as e:
                msg = 'Error while interpreting the code:\n\n'
                msg += indent(source_code, '  | ')
                raise_wrapped(DPInternalError, e,msg, exc=sys.exc_info())


    abbrevs = {
        # tag name:  (new name, classes to add)
        'fname': ('code', ['FName']),
        'rname': ('code', ['RName']),
        'poset': ('code', ['mcdp_poset']),
        'value': ('code', ['mcdp_value']),
        'fvalue': ('code', ['mcdp_value', 'fvalue']),
        'rvalue': ('code', ['mcdp_value', 'rvalue']),
        'impname': ('code', ['impname']),
        'k': ('code', ['keyword']),
        'program': ('code', ['program']),

        'f': ('span', ['f']),
        'r': ('span', ['r']),
        'imp': ('span', ['imp']),
        'kf': ('code', ['f', 'keyword']),
        'kr': ('code', ['r', 'keyword']),
        'cf': ('code', ['f']),
        'cr': ('code', ['r']),
    }
    for original_tag_name, (new_tag_name, classes_to_add) in abbrevs.items():
        for e in soup.select(original_tag_name):
            e.name = new_tag_name
            for c in classes_to_add:
                add_class(e, c)

    # warn not to get confused ith '_' and '-'
    special_classes = ['mcdp_poset', 'mcdp_fvalue', 'mcdp_rvalue', 'mcdp_value']
    for x in special_classes:
        # we do not expect to see an element that has class with '-' instead of '_'
        erroring = x.replace('_', '-')
        mistakes = list(soup.select('.%s' % erroring))
        if mistakes:
            msg = 'You cannot use %r as a class; use lowercase.' % erroring
            tags = "\n\n".join(indent(describe_tag(_),' | ') for _ in mistakes)
            raise_desc(ValueError, msg, tags=tags)

    for x in special_classes:
        # mcdp_poset -> mcdp-poset
        corresponding = x.replace('_', '-')

        for e in soup.select(corresponding):
#             e2 = Tag(name='code')
#             copy_string_and_attrs(e, e2)
            e.name = 'code'
            # THEN add class
            add_class(e, x)

    prettify = list(soup.select('fname')) + list(soup.select('rname'))
    for e in prettify:
        if e.has_attr('np') or e.has_attr('noprettify'):
            x0 = e.text.encode('utf-88')
            x1 = get_suggested_identifier(x0)
            e.text = unicode(x1, 'utf-8')


    mcdp_dev_warning('lets try if this goes away') # XXX
    # this is a bug with bs4. The replace_with above only adds an escaped
    # text rather than the actual tag (!).
    #soup = bs(to_html_stripping_fragment(soup))
    #assert soup.name == 'fragment'


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


    # this is a bug with bs4...
    for pre in soup.select('pre + pre'):
#         print('adding br between PREs')
        br = Tag(name='br')
        br['class'] = 'pre_after_pre'
        pre.parent.insert(pre.parent.index(pre), br)


def max_len_of_pre_html(html):
    source2 = project_html(html)
    line_len = lambda _: len(unicode(_, 'utf-8').rstrip())
    max_len = max(map(line_len, source2.split('\n')))
    return max_len

def make_figures(library, soup, raise_error_dp, raise_error_others, realpath, generate_pdf):
    """ Looks for codes like:

    <pre><code class="mcdp_ndp_graph_templatized">mcdp {
        # empty model
    }
    </code></pre>

        and creates a link to the image
    """

    def go(s0, func):
        selectors = s0.split(',')
        for selector in selectors:
            for tag in soup.select(selector):
                try:
                    r = func(tag)
                    tag.replaceWith(r)
                except (DPSyntaxError, DPSemanticError) as e:
                    if raise_error_dp:
                        raise
                    else:
                        note_error(tag, e)
                        continue
                except Exception as e:
                    if raise_error_others:
                        raise
                    else:
                        note_error(tag, e)
                        continue

    def make_tag(tag0, klass, data, ndp=None, template=None, poset=None):
        svg = data['svg']

        tag_svg = BeautifulSoup(svg, 'lxml', from_encoding='utf-8').svg

        assert tag_svg.name == 'svg'
        if tag_svg.has_attr('width'):
            ws = tag_svg['width']
            hs = tag_svg['height']
            assert 'pt' in ws
            w = float(ws.replace('pt',''))
            h = float(hs.replace('pt',''))
            scale = MCDPConstants.scale_svg

            w2 = w * scale
            h2 = h * scale
            tag_svg['width'] = w2
            tag_svg['height'] = h2
            tag_svg['rescaled'] = 'Rescaled from %s %s, scale = %s' % (ws, hs, scale)
        else:
            print('no width in SVG tag: %s' % tag_svg)

        tag_svg['class'] = klass

        if tag0.has_attr('style'):
            tag_svg['style'] = tag0['style']
        if tag0.has_attr('id'):
            tag_svg['id'] = tag0['id']

        if generate_pdf:
            pdf0 = data['pdf']
            pdf = crop_pdf(pdf0, margins=0)

            div = Tag(name='div')

            att = MCDPConstants.ATTR_LOAD_NAME
            if tag0.has_attr('id'):
                basename = tag0['id']
            elif ndp is not None and hasattr(ndp, att):
                basename = getattr(ndp, att)
            elif template is not None and hasattr(template, att):
                basename = getattr(template, att)
            elif poset is not None and hasattr(poset, att):
                basename = getattr(poset, att)
            else:
                hashcode = hashlib.sha224(tag0.string).hexdigest()[-8:]
                basename = 'code-%s' % (hashcode)

            docname = os.path.splitext(os.path.basename(realpath))[0]
            download = docname + "." + basename + "." + klass + '.pdf'
            a = create_a_to_data(download=download, data_format='pdf', data=pdf)
            a['class'] = 'pdf_data'
            a.append(NavigableString(download))
            div.append(tag_svg)
            div.append(a)
            return div
        else:
            return tag_svg


    mf = MakeFiguresNDP(None, None, None)
    available_ndp = set(mf.available()) | set(mf.aliases)
    for which in available_ndp:
        def callback(tag0):
            assert tag0.parent is not None
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
        selector = 'render.%s,pre.%s,img.%s' % (which, which, which)
        go(selector, callback)


    mf = MakeFiguresTemplate(None,None,None)
    available_template = set(mf.available()) | set(mf.aliases)
    for which in available_template:
        def callback(tag0):
            context = Context()
            load = lambda x: library.load_spec(SPEC_TEMPLATES, x, context=context)
            parse = lambda x: library.parse_template(x, realpath=realpath, context=context)
            template = load_or_parse_from_tag(tag0, load, parse)

            mf = MakeFiguresTemplate(template=template, library=library, yourname=None) # XXX
            formats = ['svg']
            if generate_pdf:
                formats.append('pdf')
            data = mf.get_figure(which,formats)
            tag = make_tag(tag0, which, data, ndp=None, template=template)
            return tag

        selector = 'render.%s,pre.%s,img.%s' % (which, which, which)
        go(selector, callback)


    mf = MakeFiguresPoset(None)
    available_poset = set(mf.available()) | set(mf.aliases)
    for which in available_poset:
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
        selector = 'render.%s,pre.%s,img.%s' % (which, which, which)
        go(selector, callback)

    unsure = list(soup.select('render'))
    unsure = [_ for _ in unsure if not 'errored' in _.attrs.get('class','')]
    if unsure:
        msg = 'Invalid "render" elements.'
        msg += '\n\n' + '\n\n'.join(str(_) for _ in unsure)

        msg += '\n\n' + " Available for NDPs: %s." % ", ".join(sorted(available_ndp))
        msg += '\n\n' + " Available for templates: %s." % ", ".join(sorted(available_template))
        msg += '\n\n' + " Available for posets: %s." % ", ".join(sorted(available_poset))
        raise ValueError(msg)
    return to_html_stripping_fragment(soup)


#
# def bool_from_string(b):
#     yes = ['True', 'true', '1', 'yes']
#     no = ['False', 'false', '0', 'no']
#     if b in yes:
#         return True
#     if b in no:
#         return False
#     msg = 'Cannot interpret string as boolean.'
#     raise_desc(ValueError, msg, b=b)
