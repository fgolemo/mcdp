# -*- coding: utf-8 -*-
from mcdp_lang.syntax import Syntax
from mcdp_library import MCDPLibrary
from mcdp_report.gg_ndp import STYLE_GREENREDSYM
from mcdp_report.html import ast_to_html
from mocdp.exceptions import DPSyntaxError


class AppVisualization():

    def __init__(self):
        pass

    def config(self, config):
        config.add_route('model_syntax',
                         self.get_lmv_url('{library}', '{model_name}', 'syntax'))

        config.add_view(self.view_model_syntax, route_name='model_syntax',
                        renderer='visualization/model_syntax.jinja2')

        config.add_route('template_syntax',
                         self.get_ltv_url('{library}', '{template_name}', 'syntax'))

        config.add_view(self.view_template_syntax, route_name='template_syntax',
                        renderer='visualization/template_syntax.jinja2')

        config.add_route('poset_syntax',
                         self.get_lpv_url('{library}', '{poset_name}', 'syntax'))

        config.add_view(self.view_poset_syntax, route_name='poset_syntax',
                        renderer='visualization/poset_syntax.jinja2')



        config.add_route('model_ndp_graph',
                         self.get_lmv_url('{library}', '{model_name}', 'ndp_graph'))

        config.add_view(self.view_model_ndp_graph, route_name='model_ndp_graph',
                        renderer='visualization/model_ndp_graph.jinja2')


        config.add_route('model_dp_graph',
                         self.get_lmv_url('{library}', '{model_name}', 'dp_graph'))
        config.add_view(self.view_model_dp_graph, route_name='model_dp_graph',
                        renderer='visualization/model_dp_graph.jinja2')

        config.add_route('model_ndp_repr',
                         self.get_lmv_url('{library}', '{model_name}', 'ndp_repr'))
        config.add_view(self.view_model_ndp_repr, route_name='model_ndp_repr',
                        renderer='visualization/model_generic_text_content.jinja2')


    def view_model_ndp_graph(self, request):
        model_name = str(request.matchdict['model_name'])  # unicode

        return {'model_name': model_name,
                'views': self._get_views(),
                'current_view': 'ndp_graph',
                'navigation': self.get_navigation_links(request),
                'style': STYLE_GREENREDSYM}



    def view_model_dp_graph(self, request):
        model_name = str(request.matchdict['model_name'])  # unicode


        return {'model_name': model_name,
                'navigation': self.get_navigation_links(request),
                'current_view': 'dp_graph',
                }

    def view_model_ndp_repr(self, request):
        model_name = str(request.matchdict['model_name'])  # unicode

        ndp = self.get_library(request).load_ndp(model_name)
        ndp_string = ndp.__repr__()
        ndp_string = ndp_string.decode("utf8")

        return {'model_name': model_name,
                'content': ndp_string,
                'navigation': self.get_navigation_links(request),
                'current_view': 'ndp_repr'}


    def view_model_syntax(self, request):
        name = str(request.matchdict['model_name'])  # unicode
        ext = MCDPLibrary.ext_ndps
        expr = Syntax.ndpt_dp_rvalue
        res = self._generate_view_syntax(request, name, ext, expr)
        return res

    def view_template_syntax(self, request):
        name = str(request.matchdict['template_name'])  # unicode
        ext = MCDPLibrary.ext_templates
        expr = Syntax.template
        res = self._generate_view_syntax(request, name, ext, expr)
        return res

    def view_poset_syntax(self, request):
        name = str(request.matchdict['poset_name'])  # unicode
        ext = MCDPLibrary.ext_posets
        expr = Syntax.space
        res = self._generate_view_syntax(request, name, ext, expr)
        return res

    def _generate_view_syntax(self, request, name, ext, expr):
        filename = '%s.%s' % (name, ext)
        l = self.get_library(request)
        f = l._get_file_data(filename)
        source_code = f['data']
        realpath = f['realpath']
        
        md1 = '%s.%s' % (name, MCDPLibrary.ext_explanation1)
        if l.file_exists(md1):
            fd = l._get_file_data(md1)
            html1 = self.render_markdown(fd['data'])
        else:
            html1 = None

        md2 = '%s.%s' % (name, MCDPLibrary.ext_explanation2)
        if l.file_exists(md2):
            fd = l._get_file_data(md2)
            html2 = self.render_markdown(fd['data'])
        else:
            html2 = None

        try:
            highlight = ast_to_html(source_code,
                                    complete_document=False,
                                    add_line_gutter=False,
                                    parse_expr=expr)
            
            highlight = self.add_html_links(request, highlight)
            error = ''
        except DPSyntaxError as e:
            highlight = '<pre class="source_code_with_error">%s</pre>' % source_code
            error = e.__str__()
            
        return {'source_code': source_code,
                'error': unicode(error, 'utf-8'),
                'highlight': highlight,
                'realpath': realpath,
                'navigation': self.get_navigation_links(request),
                'current_view': 'syntax',
                'explanation1_html': html1,
                'explanation2_html': html2, }

    def add_html_links(self, request, frag):
        """ Puts links to the models. """
        library = self.get_current_library_name(request)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(frag, 'html.parser')
        from bs4.element import NavigableString

        # look for links of the type:
        # <span class="FromLibraryKeyword">new</span>
        #     <span class="NDPName"> Actuation_a2_vel</span>
        # </span>

        def break_string(s):
            """ Returns initial ws, middle, final ws. """
            middle = s.strip()
            initial = s[:len(s) - len(s.lstrip())]
            final = s[len(s.rstrip()):]
            assert initial + middle + final == s, (initial, middle, final, s)
            return initial, middle, final

        def get_name_from_tag(tag):
            _, middle, _ = break_string(tag.string)
            return middle.encode('utf-8')

        def add_link_to_ndpname(tag, href):
            initial, middle, final = break_string(tag.string)
            tag.string = ''
            name = middle
            attrs = {'class': 'link-to-model', 'href': href, 'target': '_blank'}
            new_tag = soup.new_tag("a", **attrs)
            new_tag.string = name
            tag.append(NavigableString(initial))
            tag.append(new_tag)
            tag.append(NavigableString(final))

        def sub_ndpname():

            for tag in soup.select('span.NDPName'):
                if 'NDPNameWithLibrary' in tag.parent['class']:
                    continue

                ndpname = get_name_from_tag(tag)
                href = self.get_lmv_url(library, ndpname, 'syntax')
                add_link_to_ndpname(tag=tag, href=href)

        def sub_ndpname_with_library():
            for tag in soup.select('span.NDPNameWithLibrary'):
                tag_libraryname = list(tag.select('span.LibraryName'))[0]
                tag_ndpname = list(tag.select('span.NDPName'))[0]

                ndpname = get_name_from_tag(tag_ndpname)
                libname = get_name_from_tag(tag_libraryname)
                href = self.get_lmv_url(libname, ndpname, 'syntax')
                add_link_to_ndpname(tag=tag_ndpname, href=href)

#             if False:
#                 # TODO: add this as a feature
#                 img = '/solver/%s/compact_graph' % name
#                 attrs = {'src': img, 'class': 'popup'}
#                 new_tag = soup.new_tag("img", **attrs)
#                 tag.append(new_tag)

        def sub_template_name():
            for tag in soup.select('span.TemplateName'):
                if 'TemplateNameWithLibrary' in tag.parent['class']:
                    continue

                templatename = get_name_from_tag(tag)
                href = self.get_ltv_url(library, templatename, 'syntax')

                add_link_to_ndpname(tag=tag, href=href)

        def sub_template_name_with_library():
            for tag in soup.select('span.TemplateNameWithLibrary'):
                tag_libraryname = list(tag.select('span.LibraryName'))[0]
                tag_templatename = list(tag.select('span.TemplateName'))[0]

                templatename = get_name_from_tag(tag_templatename)
                libname = get_name_from_tag(tag_libraryname)
                href = self.get_ltv_url(libname, templatename, 'syntax')
                add_link_to_ndpname(tag=tag_templatename, href=href)

        def sub_poset_name():
            for tag in soup.select('span.PosetName'):
                if 'PosetNameWithLibrary' in tag.parent['class']:
                    continue

                posetname = get_name_from_tag(tag)
                href = self.get_lpv_url(library, posetname, 'syntax')

                add_link_to_ndpname(tag=tag, href=href)

        def sub_poset_name_with_library():
            for tag in soup.select('span.PosetNameWithLibrary'):
                tag_libraryname = list(tag.select('span.LibraryName'))[0]
                tag_posetname = list(tag.select('span.PosetName'))[0]

                posetname = get_name_from_tag(tag_posetname)
                libname = get_name_from_tag(tag_libraryname)
                href = self.get_lpv_url(libname, posetname, 'syntax')
                add_link_to_ndpname(tag=tag_posetname, href=href)


        def sub_libraryname():
            # Need to be last
            for tag in soup.select('span.LibraryName'):
                libname = get_name_from_tag(tag)
                href = '/libraries/%s/' % libname
                add_link_to_ndpname(tag=tag, href=href)

        try:
            sub_ndpname()
            sub_ndpname_with_library()
            sub_template_name()
            sub_template_name_with_library()
            sub_poset_name()
            sub_poset_name_with_library()
            sub_libraryname()  # keep last
        except:
            print soup
            raise
        # keep above last!

        # Add documentation links for each span
        # that has a class that finishes in "Keyword"
        if False:
            def select_tags():
                for tag in soup.select('span'):
                    if 'class' in tag.attrs:
                        klass = tag.attrs['class'][0]
                        if 'Keyword' in klass:
                            yield tag

            manual = '/docs/language_notes/'

            for tag in select_tags():
                keyword = tag.attrs['class'][0]
                link = manual + '#' + keyword
                text = tag.string
                tag.string = ''
                attrs = {'class': 'link-to-keyword', 'href': link, 'target': '_blank'}
                new_tag = soup.new_tag("a", **attrs)
                new_tag.string = text
                tag.append(new_tag)

        return soup.prettify()


