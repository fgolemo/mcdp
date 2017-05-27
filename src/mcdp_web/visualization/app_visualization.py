# -*- coding: utf-8 -*-

from collections import namedtuple
from mcdp.exceptions import DPSyntaxError, DPSemanticError, DPNotImplementedError, DPInternalError
from mcdp.logs import logger
from mcdp_lang.namedtuple_tricks import recursive_print
from mcdp_lang.parts import CDPLanguage
from mcdp_lang.utils_lists import unwrap_list
from mcdp_lang_utils.where import format_where
from mcdp_report.html import ast_to_html
from mcdp_utils_xml import add_style, to_html_stripping_fragment, bs
from mcdp_web.context_from_env import library_from_env, image_source_from_env
from mcdp_web.editor_fancy.html_mark_imp import NoLocationFound
from mcdp_web.environment import cr2e
from mcdp_web.resource_tree import ResourceThingViewSyntax, ResourceThingViewNDPGraph,\
    ResourceThingViewDPTree, ResourceThingViewDPGraph, ResourceThingViewNDPRepr,\
    ResourceThingViews
from mcdp_web.sessions import NoSuchLibrary
from mcdp_web.utils0 import add_other_fields, add_std_vars_context
from mocdp.comp.context import Context
import traceback

from bs4.element import Declaration, ProcessingInstruction, Doctype, Comment, Tag
from contracts.utils import check_isinstance, indent, raise_wrapped
from pyramid.httpexceptions import HTTPFound

from .add_html_links_imp import add_html_links


class AppVisualization(object):

    def __init__(self):
        pass

    def config(self, config): 
        config.add_view(self.view_syntax, context=ResourceThingViewSyntax, renderer='visualization/syntax.jinja2')
        config.add_view(self.redirect_things_to_syntax, context=ResourceThingViews)
            
        # these are images view for which the only change is the jinja2 template
        config.add_view(self.view_dummy, context=ResourceThingViewDPGraph, renderer='visualization/model_dp_graph.jinja2')
        config.add_view(self.view_dummy, context=ResourceThingViewDPTree, renderer='visualization/model_dp_tree.jinja2')
        config.add_view(self.view_dummy, context=ResourceThingViewNDPGraph, renderer='visualization/model_ndp_graph.jinja2')
        config.add_view(self.view_model_ndp_repr, context=ResourceThingViewNDPRepr, renderer='visualization/model_generic_text_content.jinja2')

    @add_std_vars_context
    @cr2e
    def redirect_things_to_syntax(self, e):
        ''' Redirect
                libraries/basic/models/test2/views/ ->
                libraries/basic/models/test2/views/syntax/
        '''
        url = e.request.url
        assert url.endswith('/')
        url2 = url+'syntax/'
        raise HTTPFound(url2)
        
    @add_std_vars_context
    @cr2e
    def view_model_ndp_repr(self, e):
        res = {}
        try:
            library = library_from_env(e)
            ndp = library.load_ndp(e.thing_name)
            ndp_string = ndp.__repr__()
            ndp_string = ndp_string.decode("utf8", 'ignore')
            res['content'] = ndp_string
            
        except (DPSyntaxError, DPSemanticError, DPNotImplementedError) as exc:
            self.note_exception(exc, request=e.request, context=e.context)
            s = str(exc)
            res['error'] = s.decode('utf8')
        return res

    @add_std_vars_context
    @cr2e
    def view_syntax(self, e):
        make_relative = lambda _: self.make_relative(e.request, _)
        res = generate_view_syntax(e,  make_relative)
        add_other_fields(self, res, e.request, e.context)
        url_edit0 = ("/repos/%s/shelves/%s/libraries/%s/%s/%s/views/edit_fancy/" %  
                    (e.repo_name, e.shelf_name, e.library_name, e.spec.url_part, e.thing_name))
        res['url_edit'] = make_relative(url_edit0)
        return res
    
    
def generate_view_syntax(e, make_relative):
    expr = e.spec.parse_expr
    parse_refine = e.spec.parse_refine
    source_code = e.thing
        
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
        
        def get_link_library(libname):
            try:
                rname, sname = e.session.get_repo_shelf_for_libname(libname)
            except NoSuchLibrary:
                raise
            url0 =  "/repos/%s/shelves/%s/libraries/%s/" % (rname, sname, libname)
            return make_relative(url0)
            
        def get_link(specname, libname, thingname):
            # find library. Returns a string or raises error 
            try:
                rname, sname = e.session.get_repo_shelf_for_libname(libname)
            except NoSuchLibrary:
                msg = 'No such library %r' % libname
                logger.debug(msg)
                raise
#                 return None
            things = e.db_view.repos[rname].shelves[sname].libraries[libname].things.child(specname)
            
            if thingname in things:
                
            # check if the thing exists
            
                res = get_link_library(libname) + '%s/%s/views/syntax/' % (specname, thingname)
#                 logger.debug(' link for %s = %s' % (thingname, res))
                return res
            else:
                msg = 'No such thing %r' % thingname
                logger.debug(msg)
                raise NoSuchLibrary(msg) 
        
        highlight = add_html_links(highlight, e.library_name, get_link, get_link_library)
        parses = True 
        error = ''
    except (DPSyntaxError, DPNotImplementedError ) as exc:
        highlight = '<pre class="source_code_with_error">%s</pre>' % source_code
        error = exc.__str__()
        parses = False
     
    
    if parses:
        mcdp_library = library_from_env(e)
        image_source = image_source_from_env(e)

        try:
            thing = e.spec.load(mcdp_library, e.thing_name, context=context)
                
            svg_data = get_svg_for_visualization(e, image_source, e.library_name, e.spec, 
                                                     e.thing_name, thing, Tmp.refined, 
                                                     make_relative, library=mcdp_library)
        except (DPSemanticError, DPNotImplementedError) as exc:
            logger.error(exc)
            from mcdp_web.editor_fancy.app_editor_fancy_generic import html_mark
            
            if exc.where.string != source_code:
                msg = 'This exception refers to another file.'
                msg += '\n source_code: %r' % source_code
                msg += '\n exception.where.string: %r' % exc.where.string
                msg += '\n' + indent(traceback.format_exc(exc), 'exc > ')
                raise DPInternalError(msg)
            try:
                highlight = html_mark(highlight, exc.where, "semantic_error")
            except NoLocationFound as e:
                msg = 'While trying to annotate the exception:'
                msg += '\n' + indent(exc, 'exc > ')
                raise_wrapped(NoLocationFound, e, msg)
            error = exc.error + "\n" + format_where(exc.where)
            
            svg_data = None
    else:
        svg_data = None
        
    check_isinstance(highlight, str)
    res= {
        'source_code': source_code,
        'error': unicode(error, 'utf-8'),
        'highlight': unicode(highlight, 'utf-8'),
#         'realpath': realpath,
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
def get_svg_for_visualization(e, image_source, library_name, spec, name, thing, refined, make_relative, library):

    svg_data0 = spec.get_png_data_syntax(image_source=image_source, name=name, thing=thing, data_format='svg',
                                         library=library)
    
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
         
    def link_for_dp_name(identifier0):
        identifier = identifier0 # todo translate
        if identifier in table:
            a = table[identifier]
            libname = a.libname if a.libname is not None else library_name
            href0 = '/repos/%s/shelves/%s/libraries/%s/models/%s/views/syntax/' % (e.repo_name, e.shelf_name, libname, a.name)
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
            
            