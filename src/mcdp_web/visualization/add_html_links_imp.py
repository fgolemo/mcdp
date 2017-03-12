from bs4.element import NavigableString, Tag

from mcdp_utils_xml import bs
from mcdp_utils_xml.parsing import to_html_stripping_fragment


def add_html_links(frag, library_name, get_link, get_link_library):
    """ Adds links to models.
    
        get_link(specname, libname, thingname) -> url
        get_link_library(libname) -> url
    
     """
    soup = bs(frag)

    # look for links of the type:
    # <span class="FromLibraryKeyword">new</span>
    #     <span class="NDPName"> Actuation_a2_vel</span>
    # </span>

    def get_name_from_tag(tag):
        _, middle, _ = break_string(tag.string)
        return middle.encode('utf-8')

    def add_link_to_ndpname(tag, href):
        initial, middle, final = break_string(tag.string)
        tag.string = ''
        name = middle
        attrs = {'class': 'link-to-model', 'href': href, 'target': '_blank'}
        new_tag = Tag(name="a", attrs=attrs)
        new_tag.string = name
        tag.append(NavigableString(initial))
        tag.append(new_tag)
        tag.append(NavigableString(final))

    def sub_ndpname():

        for tag in soup.select('span.NDPName'):
            if 'NDPNameWithLibrary' in tag.parent['class']:
                continue

            ndpname = get_name_from_tag(tag)
            href = get_link('models', library_name, ndpname)
            add_link_to_ndpname(tag=tag, href=href)

    def sub_ndpname_with_library():
        for tag in soup.select('span.NDPNameWithLibrary'):
            tag_libraryname = list(tag.select('span.LibraryName'))[0]
            tag_ndpname = list(tag.select('span.NDPName'))[0]

            ndpname = get_name_from_tag(tag_ndpname)
            libname = get_name_from_tag(tag_libraryname) 
            href = get_link('models', libname, ndpname)

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
            href = get_link('templates', library_name, templatename)

            add_link_to_ndpname(tag=tag, href=href)

    def sub_template_name_with_library():
        for tag in soup.select('span.TemplateNameWithLibrary'):
            tag_libraryname = list(tag.select('span.LibraryName'))[0]
            tag_templatename = list(tag.select('span.TemplateName'))[0]

            templatename = get_name_from_tag(tag_templatename)
            libname = get_name_from_tag(tag_libraryname)
            href = get_link('templates', libname, templatename)
            add_link_to_ndpname(tag=tag_templatename, href=href)

    def sub_poset_name():
        for tag in soup.select('span.PosetName'):
            if 'PosetNameWithLibrary' in tag.parent['class']:
                continue

            posetname = get_name_from_tag(tag)
            href = get_link('templates', library_name, posetname)
            add_link_to_ndpname(tag=tag, href=href)

    def sub_poset_name_with_library():
        for tag in soup.select('span.PosetNameWithLibrary'):
            tag_libraryname = list(tag.select('span.LibraryName'))[0]
            tag_posetname = list(tag.select('span.PosetName'))[0]

            posetname = get_name_from_tag(tag_posetname)
            libname = get_name_from_tag(tag_libraryname)
            
            href = get_link('templates', libname, posetname)
            add_link_to_ndpname(tag=tag_posetname, href=href)

    def sub_libraryname():
        # Need to be last
        for tag in soup.select('span.LibraryName'):
            libname = get_name_from_tag(tag)
            href = get_link_library(libname)
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
        # print soup
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
            new_tag = Tag(name="a", attrs=attrs)
            new_tag.string = text
            tag.append(new_tag)

    return to_html_stripping_fragment(soup)
    #return soup.prettify()

def break_string(s):
    """ Returns initial ws, middle, final ws. """
    middle = s.strip()
    initial = s[:len(s) - len(s.lstrip())]
    final = s[len(s.rstrip()):]
    assert initial + middle + final == s, (initial, middle, final, s)
    return initial, middle, final

