# -*- coding: utf-8 -*-
import os
from tempfile import mkdtemp

from contracts import contract
from contracts.enabling import disable_all
from contracts.utils import raise_desc
from decent_params import UserError
from mcdp import logger
from mcdp.exceptions import mcdp_dev_warning, DPSemanticError
from mcdp_cli.utils_wildcard import expand_string
from mcdp_figures import MakeFiguresNDP, MakeFiguresPoset
from mcdp_lang.parse_interface import parse_ndp_refine
from mcdp_lang.syntax import Syntax
from mcdp_library import Librarian
from mcdp_report.dp_graph_tree_imp import dp_graph_tree
from mcdp_report.gg_utils import gg_get_formats
from mcdp_web.editor_fancy.app_editor_fancy_generic import html_mark
from mocdp.comp.recursive_name_labeling import get_labelled_version
from quickapp import QuickAppBase
from system_cmd import CmdException, system_cmd_result

from .utils_mkdir import mkdirs_thread_safe
from mcdp_docs.minimal_doc import get_minimal_document


def get_ndp(data):
    if not 'ndp' in data:
        # dirs = data['dirs']
        model_name = data['model_name']
        library = data['library']
        data['ndp'] = library.load_ndp(model_name)
    return data['ndp']


def get_dp(data):
    ndp = get_ndp(data)
    if not 'dp' in data:
        data['dp'] = ndp.get_dp()
    return data['dp']


def return_formats2(gg, prefix):
    formats = ['png', 'pdf', 'svg']
    data = gg_get_formats(gg, formats)
    res = [ (data_format, prefix, d)
            for data_format, d in zip(formats, data)]
    return res


def dp_graph_tree_labeled_(data):
    ndp = get_ndp(data)
    ndp = get_labelled_version(ndp)
    
    try:
        dp = ndp.get_dp()
    except DPSemanticError:
        logger.warn('Could not draw dp_graph_tree_labeled_')
        return []
    
    gg = dp_graph_tree(dp, compact=False)
    return return_formats2(gg, 'dp_graph_tree_labeled')


def dp_graph_tree_compact_labeled_(data):
    ndp = get_ndp(data)
    ndp = get_labelled_version(ndp)
    try:
        dp = ndp.get_dp()
    except DPSemanticError:
        logger.warn('Could not draw dp_graph_tree_compact_labeled_')
        return []
    
    gg = dp_graph_tree(dp, compact=True)
    return return_formats2(gg, 'dp_graph_tree_compact_labeled')
 

def ndp_repr_long_labeled(data):
    ndp = get_ndp(data)
    ndp = get_labelled_version(ndp)
    res1 = ('txt', 'ndp_repr_long_labeled', ndp.repr_long())
    return [res1]


def dp_repr_long_labeled(data):
    ndp = get_ndp(data)
    ndp = get_labelled_version(ndp)
    try:
        dp = ndp.get_dp()
    except DPSemanticError:
        logger.warn('Could not draw dp_graph_tree_compact_labeled_')
        return []
    res1 = ('txt', 'dp_repr_long_labeled', dp.repr_long())
    return [res1]


def get_lines_to_hide(params):
    hide = params.get('hide', '')
    if not hide:
        return []
    lines = hide.split(':')
    return [int(_) for _ in lines]


def syntax_pdf(data):
    """ Returns a PDF string """
    from mcdp_report.html import ast_to_html
    s = data['s']
    s = s.replace('\t', '    ')
    
    lines_to_hide = get_lines_to_hide(data['params'])
    def ignore_line(lineno):
        return lineno  in lines_to_hide
    contents = ast_to_html(s,  
                       ignore_line=ignore_line, 
                       parse_expr=Syntax.ndpt_dp_rvalue,
                       )
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
          
        f_pdf_crop = os.path.join(d, 'file_crop.pdf')
        cmd = ['pdfcrop', '--margins', '4', f_pdf, f_pdf_crop]
        system_cmd_result(
                d, cmd, 
                display_stdout=False,
                display_stderr=False,
                raise_on_error=True)
    
        with open(f_pdf_crop) as f:
            data = f.read()
    
        f_png = os.path.join(d, 'file.png')
        cmd = ['convert', '-density', '600', f_pdf_crop,
                '-background', 'white', '-alpha', 'remove',
                '-resize', '50%', f_png]
        system_cmd_result(
                d, cmd,
                display_stdout=False,
                display_stderr=False,
                raise_on_error=True)
    
        with open(f_png) as f:
            pngdata = f.read()
    
        return [('pdf', 'syntax_pdf', data), ('png', 'syntax_pdf', pngdata)]
    except CmdException as e:
        raise e
        
        
@contract(data=dict)
def syntax_frag(data):
    from mcdp_report.html import ast_to_html
    s = data['s']
    
    res = ast_to_html(s,
                      parse_expr=Syntax.ndpt_dp_rvalue)
    res1 = ('html', 'syntax_frag', res)
    return [res1]


@contract(data=dict)
def syntax_doc(data, mark_warnings=True):
    from mcdp_report.html import ast_to_html
    s = data['s']
    lines_to_hide = get_lines_to_hide(data['params'])
    def ignore_line(lineno):
        return lineno in lines_to_hide

    library = data['library']
    context = library._generate_context_with_hooks()
    
    class Tmp:
        string_nospaces_parse_tree_interpreted = None
        
    def postprocess(block):
        x = parse_ndp_refine(block, context)
        Tmp.string_nospaces_parse_tree_interpreted = x
         
        return x
    
    body = ast_to_html(s, 
                    ignore_line=ignore_line, 
                    parse_expr=Syntax.ndpt_dp_rvalue,
                    postprocess=postprocess)

    if mark_warnings:
        for w in context.warnings:
            if w.where is not None:
                body = html_mark(body, w.where, "language_warning", tooltip=w.format_user())
        
    res = get_minimal_document(body, add_markdown_css=True)
    
    # TODO: add minimal document
    res1 = ('html', 'syntax_doc', res)
    return [res1]


@contract(data=dict)
def ast(data):
    s = data['s']
    from mcdp_report.html import ast_to_text
    res = ast_to_text(s)
    res1 = ('txt', 'ast', res)
    return [res1]


def tex_form(data):
    filename = data['filename']
    d = os.path.dirname(filename)
    b = os.path.basename(filename)
    graphics = os.path.join(d, 'out', os.path.splitext(b)[0]) + '-syntax_pdf.pdf'
    graphics = os.path.realpath(graphics)
    res = """
    \\includegraphics{%s}
    """ % graphics
    res1 = ('tex', 'tex_form', res)
    return [res1]

allplots  = {
    ('ast', ast),
    ('syntax_doc', syntax_doc),
    ('syntax_frag', syntax_frag),
    ('syntax_pdf', syntax_pdf), 
    ('tex_form', tex_form), 
    
    # we need these because of "labeled"
    ('dp_graph_tree_labeled', dp_graph_tree_labeled_),
    ('dp_graph_tree_compact_labeled', dp_graph_tree_compact_labeled_),
    ('dp_repr_long_labeled', dp_repr_long_labeled),
    ('ndp_repr_long_labeled', ndp_repr_long_labeled),
}
 
class MFCall():
    def __init__(self, name):
        self.name = name
        
    def __call__(self, data):
        ndp = get_ndp(data)
        library = data['library']
        mf = MakeFiguresNDP(ndp=ndp, library=library, yourname=None)
         
        formats = mf.available_formats(self.name)
        res = mf.get_figure(self.name, formats)
        
        results = [(_, self.name, res[_]) for _ in formats]
        return results
        
mf = MakeFiguresNDP(ndp=None)    
for name in mf.available():
    allplots.add((name, MFCall(name))) 
    
@contract(returns='tuple(str,*)')
def parse_kv(x):
    return tuple(x.split('='))

def parse_params(p):
    p = p.strip()
    if not p:
        return {}
    seq = p.split(',')

    return dict(parse_kv(_) for _ in seq)

def do_plots(logger, model_name, plots, outdir, extra_params, 
             maindir, extra_dirs, use_cache):
    
    if '.mcdp' in model_name:
        model_name2 = model_name.replace('.mcdp', '')
        msg = 'Arguments should be model names, not file names.'
        msg += ' Interpreting %r as %r.' % (model_name, model_name2)
        logger.warn(msg)
        model_name = model_name2

    if use_cache:
        cache_dir = os.path.join(outdir, '_cached/mcdp_plot_cache')
        logger.info('using cache %s' % cache_dir)
    else:
        cache_dir = None

    librarian = Librarian()
    for e in extra_dirs:
        librarian.find_libraries(e)

    library = librarian.get_library_by_dir(maindir)
    if cache_dir is not None:
        library.use_cache_dir(cache_dir)

    assert library.library_name is not None

    is_ndp = library.file_exists(model_name + '.mcdp')
    is_poset = library.file_exists(model_name + '.mcdp_poset')
     
    if is_ndp:
        results = do_plots_ndp(model_name, library, plots, extra_params)
    elif is_poset:
        results = do_plots_poset(model_name, library, plots)
    else:
        msg = 'Cannot find anything corresponding to %r.' % model_name
        raise_desc(ValueError, msg)
            
    write_results(results, model_name, outdir)
    

def write_results(res, model_name, outdir):
    for r in res:
        assert isinstance(r, tuple), r
        mime, name, x = r
        assert isinstance(x, str), x
        ext = mime
    
        base = model_name + '-%s.%s' % (name, ext)
    
        out = os.path.join(outdir, base)
        logger.info('Writing to %s' % out)
        with open(out, 'w') as f:
            f.write(x)

def do_plots_poset(model_name, library, plots):
    poset = library.load_poset(model_name)
    mf = MakeFiguresPoset(poset, library=library)

    possible = list(mf.available())
    plots = expand_string(plots, list(possible))

    allres = []
    for plot in plots:
        formats = mf.available_formats(plot)
        res = mf.get_figure(plot, formats)
        
        results = [(_, plot, res[_]) for _ in formats]
        allres.extend(results)
    return allres
        

def do_plots_ndp(model_name, library, plots, extra_params):
    possible = [p for p, _ in allplots]
    plots = expand_string(plots, list(possible))

    filename = model_name + '.mcdp'
    x = library._get_file_data(filename)
    data = {}
    data['model_name'] = model_name

    data['s'] = x['data']
    data['filename'] = x['realpath']
    data['params'] = parse_params(extra_params)
    data['library'] = library

    d = dict(allplots)
    results = []
    for p in plots:    
        try:
            if p in d:
                res = d[p](data)
            else:
                msg = 'Unknown plot.'
                raise_desc(ValueError, msg, plot=p, available=sorted(d.keys()))
        except CmdException as e:
            mcdp_dev_warning('Add better checks of error.')
            logger.error(e)
            continue
        except Exception as e:
            logger.error('While creating %r' % p)
            raise
        assert isinstance(res, list), res
        results.extend(res)
        
    return results



class PlotDP(QuickAppBase):
    """ Plot a DP:
    
        mcdp-plot  [--plots '*'] [--out outdir] [-d dir] model_name
        
    """

    def define_program_options(self, params):
        params.accept_extra()

        possible = ", ".join(sorted([p for p, _ in allplots]))

        params.add_string('out', help='Output dir', default=None)
        params.add_string('extra_params', help='Add extra params', default="")
        #print possible
        params.add_string('plots', default='*', help='One of: %s' % possible)

        params.add_string('maindir', default='.', short='-d',
                           help='Main library directory.')
        params.add_string('extra_dirs', default='.', short='-D',
                           help='Other directories (: separated).')

        params.add_flag('cache')
        params.add_flag('contracts')

    def go(self):

        options = self.get_options()
        if not options.contracts:
            disable_all()
            
        filenames = options.get_extra()
        #print options
        if len(filenames) == 0:
            raise_desc(UserError, 'Need at least one filename.', filenames=filenames)

        if len(filenames) > 1:
            raise_desc(NotImplementedError, 'Want only 1 filename.', filenames=filenames)

        filename = filenames[0]

        if options.out is None:
            out = os.path.dirname(filename)
            if not out:
                out = 'out-mcdp_plot'
        else:
            out = options.out
        mkdirs_thread_safe(out)
        logger = self.logger  # HasLogger
        maindir = options.maindir
        extra_dirs = options.extra_dirs.split(':')
        use_cache = options.cache
        do_plots(logger, filename, options.plots, out, options.extra_params,
                maindir=maindir,
                extra_dirs=extra_dirs,
                 use_cache=use_cache) 


mcdp_plot_main = PlotDP.get_sys_main()

