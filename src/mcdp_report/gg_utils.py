# -*- coding: utf-8 -*-
""" Utils for graphgen """
import codecs
from copy import deepcopy
import os
import traceback

from contracts import contract
from contracts.utils import check_isinstance, raise_desc, indent
from mcdp import logger, MCDPConstants
from mcdp.exceptions import mcdp_dev_warning, DPSemanticError
from mcdp_utils_misc.string_utils import get_md5
from mcdp_utils_misc.timing import timeit_wall
from mcdp_utils_xml import bs
import networkx as nx  # @UnresolvedImport
from reprep.constants import MIME_PDF, MIME_PLAIN, MIME_PNG, MIME_SVG
from system_cmd import CmdException, system_cmd_result
from mcdp_utils_misc.fileutils import tmpfile


def graphviz_run(filename_dot, output, prog='dot'):
    suff = os.path.splitext(output)[1][1:]
    if not suff in ['png', 'pdf', 'ps', 'svg']:
        raise ValueError((output, suff))

    encoder = suff

    cmd = [prog, '-T%s' % encoder, '-o', output, filename_dot]
    
    with timeit_wall('running graphviz on %s' % filename_dot, 1.0):
        try:
            # print('running graphviz')
            system_cmd_result(cwd='.', cmd=cmd,
                     display_stdout=False,
                     display_stderr=False,
                     raise_on_error=True,
                     )
            # print('done')
        except (CmdException, KeyboardInterrupt):
            emergency = 'emergency.dot'
            logger.error('saving to %r' % emergency)  # XXX
            contents = open(filename_dot).read()
            with open(emergency, 'w') as f:
                f.write(contents)
            raise
    

def gg_deepcopy(ggraph):
    try:
        return deepcopy(ggraph)
    except Exception as e:
        logger.error(traceback.format_exc(e))
        mcdp_dev_warning('Deep copy of gvgen graph failed: happens when in IPython.')
        return ggraph


def graphvizgen_plot(ggraph, output, prog='dot'):
    gg = gg_deepcopy(ggraph)
    with tmpfile(".dot") as filename_dot:
        with open(filename_dot, 'w') as f:
            gg.dot(f)
        try:
            graphviz_run(filename_dot, output, prog=prog)
        except:
            contents = open(filename_dot).read()
            s = get_md5(contents)
            filename = 'out-%s.dot' % s
            with open(filename, 'w') as f:
                f.write(contents)
            print('Saved problematic dot as %r.' % filename)
            raise

def nx_generic_graphviz_plot(G, output, prog='dot'):
    """ Converts to dot and writes on the file output """
    with tmpfile(".dot") as filename_dot:
        nx.write_dot(G, filename_dot)  # @UndefinedVariable
        graphviz_run(filename_dot, output, prog=prog)

def get_dot_string(gg):
    with tmpfile(".dot") as filename_dot:
        if False:
            with open(filename_dot, 'w') as fo:
                gg.dot(fo)
            contents = open(filename_dot).read()
        else:
            contents = gg.dot2()
        contents = contents.replace('"<TABLE', '<<TABLE')
        contents = contents.replace('</TABLE>"', '</TABLE>>')
        return contents


def gg_figure(r, name, ggraph, do_png=True, do_pdf=True, do_svg=True,
              do_dot=True):
    """ Adds a figure to the Report r that displays this graph
        and also its source. """
    f = r.figure(name, cols=1)

    # save file in dot file
    with tmpfile(".dot") as filename_dot:
        with open(filename_dot, 'w') as fo:
            s = get_dot_string(ggraph)
            fo.write(s)

#         if False:
#             ff = '%s.dot' % id(r)
#             print('writing to %r' % ff)
#             with open(ff, 'w') as f2:
#                 f2.write(s)

        prog = 'dot'
        try:
                
            if do_png:
                with f.data_file('graph', MIME_PNG) as filename:
                    graphviz_run(filename_dot, filename, prog=prog)
    
            if do_pdf:
                with f.data_file('graph_pdf', MIME_PDF) as filename:
                    graphviz_run(filename_dot, filename, prog=prog)
    
            if do_svg:
                with f.data_file('graph_svg', MIME_SVG) as filename:
                    graphviz_run(filename_dot, filename, prog=prog)
                    
                    from mcdp_report.embedded_images import embed_svg_images
                    data = open(filename).read()
                    soup = bs(data)
                    embed_svg_images(soup)
                    # does not keep doctype: s = to_html_stripping_fragment(soup)
                    # this will keep the doctype
                    s = str(soup)
                    s = s.replace('<fragment>','')
                    s = s.replace('</fragment>','')
                    write_bytes_to_file_as_utf8(s, filename)

        except CmdException:
            if MCDPConstants.test_ignore_graphviz_errors:
                mcdp_dev_warning('suppressing errors from graphviz')
                logger.error('Graphivz failed, but I will ignore it '
                             'because of MCDPConstants.test_ignore_graphviz_errors.')
            else:
                raise

        # MIME_GRAPHVIZ
        if do_dot:
            with f.data_file('dot', MIME_PLAIN) as filename:
                with open(filename, 'w') as f:
                    f.write(s)
        
    return f

    
def write_bytes_to_file_as_utf8(s, filename):
    """ Accept a string s (internally using utf-8) and writes
        it to a file in UTF-8 (first converting to unicode, to do it properly)."""
    check_isinstance(s, bytes)
    u = unicode(s, 'utf-8')
    with codecs.open(filename, 'w', encoding='utf-8') as ff:
        ff.write(u)     

allowed_formats = ['png', 'pdf', 'svg', 'dot']

@contract(returns='tuple')
def gg_get_formats(gg, data_formats):
    check_isinstance(data_formats, (list, tuple))
    res = []
    mcdp_dev_warning('TODO: optimize gg_get_formats')
    for data_format in data_formats:
        if not data_format in allowed_formats:
            msg = 'Invalid data format.' 
            raise_desc(ValueError, msg, data_formats=data_formats)

        if data_format == 'dot':
            d = get_dot_string(gg)
        else:
            d = gg_get_format(gg, data_format)
            
        res.append(d)
    return tuple(res)
 
     
    
def gg_get_format(gg, data_format):
    from reprep import Report
    r = Report()
    do_dot = data_format == 'dot'
    do_png = data_format == 'png'
    do_pdf = data_format == 'pdf'
    do_svg = data_format == 'svg'

    with timeit_wall('gg_figure %s' % data_format): 
        gg_figure(r, 'graph', gg, do_dot=do_dot,
                    do_png=do_png, do_pdf=do_pdf, do_svg=do_svg)

    if data_format == 'pdf':
        pdf = r.resolve_url('graph_pdf').get_raw_data()
        return pdf
    elif data_format == 'png':
        png = r.resolve_url('graph/graph').get_raw_data()
        return png
    elif data_format == 'dot':
        dot = r.resolve_url('dot').get_raw_data()
        return dot
    elif data_format == 'svg':
        svg = r.resolve_url('graph_svg').get_raw_data()
        if '<html>' in svg:
            msg = 'I did not expect a tag <html> in the SVG output'
            svg = indent(svg, '> ')
            raise_desc(Exception, msg, svg=svg) 
        return svg
    else:
        raise ValueError('No known format %r.' % data_format)


def embed_images_from_library2(soup, library, raise_errors):
    """ Resolves images from library """
    
    def resolve(href):
        #print('resolving %r' % href)
        if href.startswith('http'):
            msg = 'I am not able to download external resources, such as:'
            msg += '\n  '  + href
            logger.error(msg)
            return None
        
        try:
            f = library._get_file_data(href)
        except DPSemanticError as e:
#             if raise_errors:
#                 raise
#             else:
            msg = 'Could not find file %r.' % href
            logger.error(msg)
            logger.error(str(e))
            return None
        data = f['data']
        
        check_not_lfs_pointer(f['realpath'], data)
        # realpath = f['realpath']
        return data
            
    density = MCDPConstants.pdf_to_png_dpi # dots per inch
    
    from mcdp_report.embedded_images import embed_img_data, embed_pdf_images
    
    embed_pdf_images(soup, resolve, density, raise_on_error=raise_errors)
    embed_img_data(soup, resolve, raise_on_error=raise_errors)
    
         

def check_not_lfs_pointer(label, contents):
    if 'git-lfs.github.com' in contents:
        msg = 'File %s is actually a git lfs pointer.' % label
        msg += '\nThis means that you have not installed Git LFS.'
        msg += '\nAfter that, perhaps you might recover using `git lfs pull`.'
        raise Exception(msg )
        
