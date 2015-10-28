from conf_tools.utils import expand_string
from mocdp.dp_report.gg_ndp import gvgen_from_ndp
from mocdp.dp_report.gg_utils import gg_figure
from mocdp.lang.parse_actions import parse_ndp
from quickapp import QuickAppBase
from reprep import Report
import os
from reprep.constants import MIME_PNG
from contracts import contract


def get_ndp(data):
    if not 'ndp' in data:
        data['ndp'] = parse_ndp(data['s'])
    return data['ndp']

def get_dp(data):
    ndp = get_ndp(data)
    if not 'dp' in data:
        data['dp'] = ndp.get_dp()
    return data['dp']

def png_from_gg(gg):
    r = Report()
    gg_figure(r, 'graph', gg)
    node = r.resolve_url('graph/graph')
    return node.raw_data

def ndp_visualization(data, style):
    ndp = get_ndp(data) 
    gg = gvgen_from_ndp(ndp, style)
    res1 = ('png', style, png_from_gg(gg))
    return [res1]

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
    'ndp_default': lambda data: ndp_visualization(data, 'default'),
    'ndp_clean': lambda data: ndp_visualization(data, 'clean'),
    'syntax_doc': syntax_doc,
    'syntax_frag': syntax_frag,
}

def do_plots(filename, plots, outdir):
    s = open(filename).read()
    data = {}
    data['s'] = s
    
    results = []
    for p in plots:    
        print('plotting %r ' % p)
        res = allplots[p](data)
        assert isinstance(res, list)
        for r in res:
            assert isinstance(r, tuple), r
            mime, name, x = r
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
        params.add_string('filename')
        params.add_string('out', help='Output dir', default=None)
        params.add_string_list('plots', default='*')

    def go(self):
        options = self.get_options()
        filename = options.filename
        if options.out is None:
            out = os.path.dirname(filename)
            if not out:
                out = '.'
        else:
            out = options.out
        plots = expand_string(options.plots, list(allplots))
        do_plots(filename, plots, out)


mcdp_plot_main = PlotDP.get_sys_main()

