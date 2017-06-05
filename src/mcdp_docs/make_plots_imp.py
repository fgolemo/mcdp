# -*- coding: utf-8 -*-
from mcdp.exceptions import DPSemanticError, DPSyntaxError
from mcdp_report.generic_report_utils import (
    NotPlottable, enlarge, get_plotters)
from mcdp_report.plotters.get_plotters_imp import get_all_available_plotters
from mcdp_utils_xml import note_error
from mocdp.comp.context import Context

from contracts.utils import raise_wrapped
from reprep import Report


def make_plots(library, soup, raise_errors, realpath):
    """
        Looks for things like:
        
         
        <img class="value_plot_generic">VALUE</img>
        <img class="value_plot_generic" id='value"/>
        
        <pre class="print_value" id='value"/>
        <pre class="print_value">VALUE</img>
    
    """ 

    def go(selector, plotter, load, parse):
        for tag in soup.select(selector):

            try:
                # load value with units in vu
                
                def parsing(source_code):
                    context = Context()
                    return parse(source_code, realpath=realpath, context=context)
                    
                from mcdp_docs.highlight import load_or_parse_from_tag
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
                else:
                    note_error(tag, e)
            except Exception as e:
                if raise_errors:
                    raise
                else:
                    note_error(tag, e)
    
    from .highlight import make_image_tag_from_png, make_pre
    
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
    go("render.plot_value_generic", plot_value_generic, **const)
    go("pre.print_value", print_value, **const)
    go("pre.print_mcdp", print_mcdp, **mcdp) 
