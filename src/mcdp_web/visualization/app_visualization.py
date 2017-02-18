# -*- coding: utf-8 -*-

from collections import namedtuple

from bs4.element import Declaration, ProcessingInstruction, Doctype, Comment,\
    Tag

from contracts.utils import check_isinstance, indent
from mcdp.exceptions import DPSyntaxError, DPSemanticError,\
    DPNotImplementedError, DPInternalError
from mcdp_lang.namedtuple_tricks import recursive_print
from mcdp_lang.parts import CDPLanguage
from mcdp_lang.utils_lists import unwrap_list
from mcdp_report.html import ast_to_html
from mcdp_utils_xml import to_html_stripping_fragment, bs
from mcdp_web.editor_fancy.app_editor_fancy_generic import specs
from mcdp_web.renderdoc.highlight import add_style
from mcdp_web.utils0 import add_std_vars, add_other_fields
from mcdp_web.visualization.add_html_links_imp import add_html_links
from mocdp.comp.context import Context


class AppVisualization():

    def __init__(self):
        pass

    def config(self, config):
        
        renderer = 'visualization/syntax.jinja2'
        generate_view = self.generate_view
#         generate_graph = self.generate_graph
        
        for s in specs:
            url = ('/libraries/{library}/%s/{%s}/views/syntax/' % 
                   (specs[s].url_part, specs[s].url_variable))
            route = 'visualization_%s_syntax' % s
            
            config.add_route(route, url)    
            
            class G():
                def __init__(self, spec):
                    self.spec = spec

                def __call__(self, request):
                    return generate_view(request, self.spec)

            # scoping bug!                    
            #view = lambda request: self.generate_view(request, specs[s])
            config.add_view(G(specs[s]), route_name=route, renderer=renderer)
            
            graph_route = 'visualization_%s_graph' % s
            graph_url = url + 'graph.{data_format}'
            config.add_route(graph_route, graph_url)    

# 
#             class H():
#                 def __init__(self, spec):
#                     self.spec = spec
# 
#                 def __call__(self, request):
#                     return generate_graph(request, self.spec)
# 
#             
#             config.add_view(H(specs[s]), route_name=graph_route, renderer=renderer)


        # these are images view for which the only change is the jinja2 template
        image_views = [
            'dp_graph', 
            'dp_tree', 
            'ndp_graph',
        ]
        for image_view in image_views:
            route = 'model_%s' % image_view
            url = self.get_lmv_url2('{library}', '{model_name}', image_view, None)
            renderer = 'visualization/model_%s.jinja2' % image_view
            config.add_route(route, url)
            config.add_view(self.view_model_info, route_name=route, renderer=renderer)
 

        config.add_route('model_ndp_repr',
                         self.get_lmv_url2('{library}', '{model_name}', 'ndp_repr', None))
        config.add_view(self.view_model_ndp_repr, route_name='model_ndp_repr',
                        renderer='visualization/model_generic_text_content.jinja2')


    @add_std_vars
    def view_model_info(self, request):
        return {
            'model_name': self.get_model_name(request),
            'views': self._get_views(),
            'navigation': self.get_navigation_links(request),
        }
 
    @add_std_vars
    def view_model_ndp_repr(self, request):
        model_name = str(request.matchdict['model_name'])  # unicode

        ndp = self.get_library(request).load_ndp(model_name)
        ndp_string = ndp.__repr__()
        ndp_string = ndp_string.decode("utf8")

        return {
            'model_name': model_name,
            'content': ndp_string,
            'navigation': self.get_navigation_links(request),
        }
 
  
#     def generate_graph(self, request, spec):
#         def go():
#             with timeit_wall('generate_graph', 1.0):
#                 library = self.get_library(request)
#                 widget_name = self.get_widget_name(request, spec)
#                 l = self.get_library(request)
#                 data_format = str(request.matchdict['data_format'])  # unicode
# 
#                 context = l._generate_context_with_hooks()
#                 thing = spec.load(l, widget_name, context=context)
#     
#                 with timeit_wall('graph_generic - get_png_data', 1.0):
#                     data = spec.get_png_data_syntax(library, widget_name, thing, 
#                                              data_format=data_format)
#                     
#                 from mcdp_web.images.images import get_mime_for_format
#                 mime = get_mime_for_format(data_format)
#                 return response_data(request, data, mime)
#         return self.png_error_catch2(request, go)
    
    def generate_view(self, request, spec):
        name = str(request.matchdict[spec.url_variable])  # unicode
        library = self.get_library(request)
        make_relative = lambda _: self.make_relative(request, _)
        library_name = self.get_current_library_name(request)

        res = generate_view_syntax(library_name, library, name,  spec, make_relative)
        add_other_fields(self, res, request)
        
        navigation = self.get_navigation_links(request)
        
        res['navigation'] = navigation
        
        url_edit0 = ("/libraries/%s/%s/%s/views/edit_fancy/" %  
                    (navigation['current_library'], spec.url_part, name))
        res['url_edit'] = make_relative(url_edit0)
        
        return res
    
    
def generate_view_syntax(library_name, library, name,  spec, make_relative):
    ext = spec.extension
    expr = spec.parse_expr
    parse_refine = spec.parse_refine

    filename = '%s.%s' % (name, ext)
    f = library._get_file_data(filename)
    source_code = f['data']
    realpath = f['realpath']
        
    context = Context()
    class Tmp:
        refined = None
    def postprocess(block):
        if parse_refine is None:
            return block
        try:
            Tmp.refined = parse_refine(block, context) 
            return Tmp.refined
        except DPSemanticError:
            return block 
          
    try:
        highlight = ast_to_html(source_code,
                                add_line_gutter=False,
                                parse_expr=expr,
                                postprocess=postprocess)
        
        def get_link(specname, libname, thingname):
            spec = specs[specname]
            url0 =  ("/libraries/%s/%s/%s/views/syntax/" %  
                        (libname, spec.url_part, thingname))
            return make_relative(url0)
            
        highlight = add_html_links(highlight, library_name, get_link)
        parses = True 
        error = ''
    except (DPSyntaxError, DPNotImplementedError ) as e:
        highlight = '<pre class="source_code_with_error">%s</pre>' % source_code
        error = e.__str__()
        parses = False
     
    
    if parses:
        context = library._generate_context_with_hooks()
        try:
            thing = spec.load(library, name, context=context)
                
            svg_data = get_svg_for_visualization(library, library_name, spec, 
                                                     name, thing, Tmp.refined, 
                                                     make_relative)
        except (DPSemanticError, DPNotImplementedError) as e:
            
            from mcdp_web.editor_fancy.app_editor_fancy_generic import html_mark
            highlight = html_mark(highlight, e.where, "semantic_error")

            error = e.error
            svg_data = None
    else:
        svg_data = None
        
    check_isinstance(highlight, str)
    res= {
        'source_code': source_code,
        'error': unicode(error, 'utf-8'),
        'highlight': unicode(highlight, 'utf-8'),
        'realpath': realpath,
        'current_view': 'syntax', 
        'explanation1_html': None,
        'explanation2_html': None,
        'svg_data': unicode(svg_data, 'utf-8') if svg_data is not None else None,
        'parses': parses, # whether it parses
    }
    return res

    

def remove_all_titles(svg):
    assert isinstance(svg, Tag) and svg.name == 'svg'
    for e in svg.select('[title]'):
        del e.attrs['title']
    for e in svg.select('title'):
        e.extract()

def add_html_links_to_svg(svg, link_for_dpname):
    assert isinstance(svg, Tag) and svg.name == 'svg'
    
    def enclose_in_link(element, href):
        a = Tag(name='a')
        a['href'] = href
        a.append(element.__copy__())
        element.replace_with(a)
        
#     <text font-family="Anka/Coder Narrow" font-size="14.00" text-anchor="start" x="421.092" y="-863.288">nozzle</text>
    for e in svg.select('text'):
        t = e.text.encode('utf-8')
        is_identifier = not ' ' in t and not '[' in t
        if is_identifier:
            href = link_for_dpname(t)
            if href is not None:
                s0 = e.next_sibling
                while s0 != None:
                    if isinstance(s0, Tag) and s0.name == 'image':
                        enclose_in_link(s0, href)
                        break
                    s0 = s0.next_sibling
                
                enclose_in_link(e, href)
                
                
        
# with timeit_wall('graph_generic - get_png_data', 1.0):
def get_svg_for_visualization(library, library_name, spec, name, thing, refined, make_relative):

    svg_data0 = spec.get_png_data_syntax(library, name, thing, data_format='svg')
    fragment = bs(svg_data0)
    if fragment.svg is None:
        msg = 'Cannot interpret fragment.'
        msg += '\n'+ indent(svg_data0, '> ')
        raise DPInternalError(msg)
    assert fragment.svg is not None 
    style = {}
    for a in ['width', 'height']:
        if a in fragment.svg.attrs:
            value = fragment.svg.attrs[a]
            del fragment.svg.attrs[a]
            style['max-%s' %a ]= value
    add_style(fragment.svg, **style)
            
    remove_doctype_etc(fragment)
    remove_all_titles(fragment.svg)
    
    if refined is not None:
        table = identifier2ndp(refined)
    else:
        table = {}
        
#         print table
    def link_for_dp_name(identifier0):
        identifier = identifier0 # todo translate
        if identifier in table:
            a = table[identifier]
            libname = a.libname if a.libname is not None else library_name
#                 href = self.get_lmv_url(libname, a.name, 'syntax')
            href0 = '/libraries/%s/models/%s/views/syntax/' % (libname, a.name)
            return make_relative(href0)
        else:
            return None
                                
    add_html_links_to_svg(fragment.svg, link_for_dp_name)
    svg_data = to_html_stripping_fragment(fragment)
    return svg_data
    
LibnameName = namedtuple('LibnameName', 'libname name')
   
CDP = CDPLanguage

def identifier2ndp(xr):
    """ Returns a map identifier -> (libname, ndpname) where libname can be None """
    
    res = {}
    
    if isinstance(xr, CDP.BuildProblem):
        for s in unwrap_list(xr.statements.statements):
            if isinstance(s, CDP.SetNameNDPInstance):
                #print recursive_print(s)
                name = s.name.value
                ndp = s.dp_rvalue
                if isinstance(ndp, CDP.DPInstance):
                    x = ndp.dp_rvalue
                    if isinstance(x, CDP.LoadNDP):
                        load_arg = x.load_arg
                        res[name] = get_from_load_arg(load_arg)
                    elif isinstance(x, CDP.CoproductWithNames):
                        look_in_coproduct_with_names(x, res)
                    else:
                        pass
#                         print('cannot identify %s' % type(x).__name__)
                    
    elif isinstance(xr, CDP.CoproductWithNames):
        look_in_coproduct_with_names(xr, res)
    return res

def get_from_load_arg(load_arg):
    if isinstance(load_arg, CDP.NDPName):
        model = load_arg.value
        libname = None
    elif isinstance(load_arg, CDP.NDPNameWithLibrary):
        libname = load_arg.library.value 
        model = load_arg.name.value
    else:
        raise Exception(recursive_print(load_arg))
    return LibnameName(libname, model)

def look_in_coproduct_with_names(x, res):
    check_isinstance(x, CDP.CoproductWithNames)

    ops = unwrap_list(x.elements)
    nops = len(ops)
    n = nops/2
    for i in range(n):
        e, load = ops[i*2], ops[i*2 +1]
        assert isinstance(e, CDP.CoproductWithNamesName)
        name = e.value
        
        if isinstance(load, CDP.LoadNDP):
            res[name] = get_from_load_arg(load.load_arg)
                

def remove_doctype_etc(fragment):
    for e in list(fragment):
        remove = (Declaration, ProcessingInstruction, Doctype)
        if isinstance(e, remove):
            c = Comment('Removed object of type %s' % type(e).__name__)
            e.replace_with(c)
            
            