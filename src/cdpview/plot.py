from conf_tools.utils import expand_string
from mocdp.dp_report.gg_ndp import gvgen_from_ndp
from mocdp.dp_report.gg_utils import gg_figure
from mocdp.lang.parse_actions import parse_ndp
from quickapp import QuickAppBase
from reprep import Report
import os
from contracts import contract
from tempfile import mkdtemp
from system_cmd import system_cmd_result
from conf_tools.global_config import GlobalConfig
from mocdp.dp_report.report import gvgen_from_dp
from cdpview.utils_mkdir import mkdirs_thread_safe

def get_ndp(data):
    if not 'ndp' in data:
        data['ndp'] = parse_ndp(data['s'])
    return data['ndp']

def get_dp(data):
    ndp = get_ndp(data)
    if not 'dp' in data:
        data['dp'] = ndp.get_dp()
    return data['dp']

def png_pdf_from_gg(gg):
    r = Report()
    gg_figure(r, 'graph', gg)
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

def ndp_visualization(data, style):
    ndp = get_ndp(data) 
    gg = gvgen_from_ndp(ndp, style)
    png, pdf = png_pdf_from_gg(gg)
    res1 = ('png', style, png)
    res2 = ('pdf', style, pdf)
    return [res1, res2]

def syntax_pdf(data):
    from mocdp.dp_report.html import ast_to_html
    s = data['s']
    s = s.replace('\t', '    ')
    html = ast_to_html(s, complete_document=True)

    d = mkdtemp()
    
    f_html = os.path.join(d, 'file.html')
    with open(f_html, 'w') as f:
        f.write(html)
        
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
    cmd = ['convert', '-density', '300', f_pdf_crop,
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

@contract(data=dict)
def syntax_frag(data):
    from mocdp.dp_report.html import ast_to_html
    s = data['s']
    res = ast_to_html(s, complete_document=False)
    res1 = ('html', 'syntax_frag', res)
    return [res1]

@contract(data=dict)
def syntax_doc(data):
    from mocdp.dp_report.html import ast_to_html
    s = data['s']
    res = ast_to_html(s, complete_document=True)
    res1 = ('html', 'syntax_doc', res)
    return [res1]

allplots  = {
    ('syntax_doc', syntax_doc),
    ('syntax_frag', syntax_frag),
    ('syntax_pdf', syntax_pdf),
    ('ndp_default', lambda data: ndp_visualization(data, 'default')),
    ('ndp_clean', lambda data: ndp_visualization(data, 'clean')),
    ('dp_tree', dp_visualization),
}

def do_plots(filename, plots, outdir):
    s = open(filename).read()
    data = {}
    data['s'] = s
    
    d = dict(allplots)
    results = []
    for p in plots:    
        print('plotting %r ' % p)
        res = d[p](data)
        assert isinstance(res, list)
        for r in res:
            assert isinstance(r, tuple), r
            mime, name, x = r
            assert isinstance(x, str), x
            ext = mime

            base = os.path.splitext(os.path.basename(filename))[0]
            base += '-%s.%s' % (name, ext)

            out = os.path.join(outdir, base)
            print('Writing to %s' % out)
            with open(out, 'w') as f:
                f.write(x)

            results.append(r)

    return results



class PlotDP(QuickAppBase):
    """ Plot a design program """
    def define_program_options(self, params):
        params.add_flag('watch')
        params.accept_extra()

        params.add_string('out', help='Output dir', default=None)
        params.add_string_list('plots', default='*')

    def go(self):
        GlobalConfig.global_load_dir("mocdp")

        options = self.get_options()
        filenames = options.get_extra()

        if len(filenames) > 1:
            raise NotImplementedError('Only one filename')

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
        do_plots(filename, plots, out)

        if options.watch:
            def handler():
                do_plots(filename, plots, out)

            from cdpview.go import watch
            watch(path=os.path.dirname(options.filename), handler=handler)


mcdp_plot_main = PlotDP.get_sys_main()

