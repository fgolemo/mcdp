from .utils_mkdir import mkdirs_thread_safe
from contracts import contract
from contracts.utils import raise_desc
from decent_params.utils import UserError
from mcdp_cli.utils_wildcard import expand_string
from mcdp_report.gg_ndp import STYLE_GREENRED, STYLE_GREENREDSYM, gvgen_from_ndp
from mcdp_report.gg_utils import get_dot_string, gg_figure
from mcdp_report.report import gvgen_from_dp
from mocdp.exceptions import mcdp_dev_warning
from quickapp import QuickAppBase
from reprep import Report
from system_cmd import CmdException, system_cmd_result
from tempfile import mkdtemp
import os
from mcdp_library.libraries import Librarian

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

def png_pdf_from_gg(gg):
    r = Report()
    gg_figure(r, 'graph', gg, do_svg=False, do_dot=False)
    png_node = r.resolve_url('graph/graph')
    pdf_node = r.resolve_url('graph_pdf')
    return png_node.get_raw_data(), pdf_node.get_raw_data()

def dp_visualization(data):
    dp = get_dp(data)
    gg = gvgen_from_dp(dp)
    png, pdf = png_pdf_from_gg(gg)
    res1 = ('png', 'dp_tree', png)
    res2 = ('pdf', 'dp_tree', pdf)
    return [res1, res2]


def simple_print(data):
    ndp = get_ndp(data)
    res1 = ('txt', 'print', str(ndp))
    return [res1]

def ndp_visualization(data, style):
    ndp = get_ndp(data) 
    gg = gvgen_from_ndp(ndp, style)
    png, pdf = png_pdf_from_gg(gg)

    # do it again
    gg = gvgen_from_ndp(ndp, style)
    dot = get_dot_string(gg)

    res1 = ('png', style, png)
    res2 = ('pdf', style, pdf)
    res3 = ('dot', style, dot)

    return [res1, res2, res3]

def create_extra_css(params):  # @UnusedVariable
    out = ''
    return out

def get_lines_to_hide(params):
    hide = params.get('hide', '')
    if not hide:
        return []
    lines = hide.split(':')
    return [int(_) for _ in lines]

def syntax_pdf(data):
    from mcdp_report.html import ast_to_html
    s = data['s']
    s = s.replace('\t', '    ')
    extra_css = create_extra_css(data['params'])
    lines_to_hide = get_lines_to_hide(data['params'])
    def ignore_line(lineno):
        return lineno  in lines_to_hide
    html = ast_to_html(s, complete_document=True, extra_css=extra_css,
                       ignore_line=ignore_line)

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
    extra_css = create_extra_css(data['params'])
    res = ast_to_html(s, complete_document=False, extra_css=extra_css)
    res1 = ('html', 'syntax_frag', res)
    return [res1]

@contract(data=dict)
def syntax_doc(data):
    from mcdp_report.html import ast_to_html
    s = data['s']
    extra_css = create_extra_css(data['params'])
    lines_to_hide = get_lines_to_hide(data['params'])
    def ignore_line(lineno):
        return lineno  in lines_to_hide

    res = ast_to_html(s, complete_document=True, extra_css=extra_css,
                      ignore_line=ignore_line)
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
    ('dp_tree', dp_visualization),
    ('tex_form', tex_form),
    ('print', simple_print),
}

class Vis():
    def __init__(self, s):
        self.s = s
    def __call__(self, data):
        return ndp_visualization(data, style=self.s)

for s in [STYLE_GREENRED, 'default', 'clean', STYLE_GREENREDSYM]:
    x = ('ndp_%s' % s, Vis(s))
    allplots.add(x)
    
def ndp_graph_enclosed_(data):
    library = data['library']
    ndp = get_ndp(data)
    style = STYLE_GREENREDSYM
    yourname = None
    data_format = 'png'
    from mcdp_web.images.images import ndp_graph_enclosed
    png = ndp_graph_enclosed(library, ndp, style, yourname,
                            data_format, direction='TB',
                            enclosed=True)
    return [('png', 'ndp_graph_enclosed', png)]

allplots.add(('ndp_graph_enclosed', ndp_graph_enclosed_))

@contract(returns='tuple(str,*)')
def parse_kv(x):
    return tuple(x.split('='))

def parse_params(p):
    p = p.strip()
    if not p:
        return {}
    seq = p.split(',')

    return dict(parse_kv(_) for _ in seq)

def do_plots(logger, model_name, plots, outdir, extra_params, maindir, extra_dirs, use_cache):
    data = {}

    if '.mcdp' in model_name:
        model_name2 = model_name.replace('.mcdp', '')
        msg = 'Arguments should be model names, not file names.'
        msg += ' Interpreting %r as %r.' % (model_name, model_name2)
        logger.warn(msg)
        model_name = model_name2

    data['model_name'] = model_name

    if use_cache:
        cache_dir = os.path.join(outdir, '_cached/mcdp_plot_cache')
        print('using cache %s' % cache_dir)
    else:
        cache_dir = None

    librarian = Librarian()
    for e in extra_dirs:
        librarian.find_libraries(e)

    library = librarian.get_library_by_dir(maindir)
    if cache_dir is not None:
        library.use_cache_dir(cache_dir)


    filename = model_name + '.mcdp'
    x = library._get_file_data(filename)
    data['s'] = x['data']
    data['filename'] = x['realpath']
    data['params'] = parse_params(extra_params)
    data['library'] = library

    d = dict(allplots)
    results = []
    for p in plots:    
        # print('plotting %r ' % p)
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
        assert isinstance(res, list), res
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

            results.append(r)

    return results



class PlotDP(QuickAppBase):
    """ Plot a DP:
    
        mcdp-plot [--watch] [--plots '*'] [--out outdir] [-d dir] model_name
        
    """

    def define_program_options(self, params):
        params.add_flag('watch')
        params.accept_extra()

        possible = [p for p, _ in allplots]

        params.add_string('out', help='Output dir', default=None)
        params.add_string('extra_params', help='Add extra params', default="")
        print possible
        params.add_string('plots', default='*', help='One of: %s' % possible)

        params.add_string('maindir', default='.', short='-d',
                           help='Main library directory.')
        params.add_string('extra_dirs', default='.', short='-D',
                           help='Other directories (: separated).')

        params.add_flag('cache')

    def go(self):

        options = self.get_options()
        filenames = options.get_extra()
        print options
        if len(filenames) == 0:
            raise_desc(UserError, 'Need at least one filename.', filenames=filenames)

        if len(filenames) > 1:
            raise_desc(NotImplementedError, 'Want only 1 filename.', filenames=filenames)

        filename = filenames[0]

        if options.out is None:
            out = os.path.dirname(filename)
            if not out:
                out = '.'
        else:
            out = options.out
        mkdirs_thread_safe(out)
        possible = [p for p, _ in allplots]
        plots = expand_string(options.plots, list(possible))
        logger = self.logger  # HasLogger
        maindir = options.maindir
        extra_dirs = options.extra_dirs.split(':')
        use_cache = options.cache
        do_plots(logger, filename, plots, out, options.extra_params,
                maindir=maindir,
                extra_dirs=extra_dirs,
                 use_cache=use_cache)

        if options.watch:
            def handler():
                do_plots(filename, plots, out)

            from .go import watch
            d = os.path.dirname(filename)
            if d == '':
                d = '.'
            watch(path=d, handler=handler)


mcdp_plot_main = PlotDP.get_sys_main()

