#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

from bs4 import BeautifulSoup

from contracts import contract
from mcdp_report.html import get_language_css, get_markdown_css


manual_css = """

@page {
    margin: 0.5cm;
}

h1 { page-break-before: always; text-align: center;}
h1#booktitle  { page-break-before: avoid; }
.toc a { text-decoration: none; }

/* Good for safari */
pre {
     box-shadow: none;
}

.ndp_graph_expand,
.ndp_graph_enclosed,
.ndp_graph_normal,
.ndp_graph_templatized,
.ndp_graph_templatized_labeled,
.template_graph_enclosed {
    max-width: 50em;
    
}

span.language_warning { background-color: inherit !important; }

p { max-width: 40em; }

code { page-break-inside: avoid; }



body {
  font-family: "Times New Roman", Times, serif !important;
  font-size: 10pt;
}

pre, code { font-size: 8pt; }


body {
  text-align: justify;
}
 
h1 { font-size: 15pt; color: black !important;}
h2 { font-size: 12pt; color: black !important;}
h3 { font-size: 10pt; color: black !important; font-style: italic; font-weight: normal;}

code { 
    font-family: monospace, Cambria, "Cambria Math"; 
}

p code { font-size: 8pt; }
pre, pre code { 
}
pre .label { font-size: 8px; font-style: normal; }
pre { 
    margin-left: 0.4em !important; 
    border-radius: 4px !important; 
    padding: 5px !important;
}
/* without labels */
pre:not(.has_label) { 
    /*margin-top: 0 !important;*/ 
     
}
/* with labels */
pre.has_label { 
    /*margin-top: 0.7em !important; */
}

p { margin-top: 0.3em; margin-bottom: 0.3em; }
h1,h2,h3 { margin-bottom: 0.3em; margin-top: 0.3em; }
pre code { margin: 0; }
pre { padding: 3pt; }
a { color: #005; }
/*ul, li {padding: 0; padding-left: 0em !important;}*/
ul.toc { padding-left: 0; }
li {margin: 0; margin-left: 0em;}
/*.toc ul ul li { display: none; }*/
 
 
@media screen {
     body { display: inline-block; }
     html { text-align: center; } 
    body {
    
        margin-left:auto;
        margin-right:auto;
    }
    body { 
        

        width: 420pt;  /* A5 is  420pt × 595  */
        background-color: white;
        
        /** essentially these are our "page margins" **/
        border-right: solid 30pt white;
        border-left: solid 30pt white;
        margin-top: 0;
    }
    
    html {
        background-color: #eee;
        border-right: solid 1px gray;
    }

    /* zoom the page - equal to browser zoom */
    body {
         transform: scale(1.5);
         transform: scale( 100% / 1.5);
         transform-origin: top center;
    }
    
    /** add space for h1, in place of page breaks **/
    h1 ~ h1 { margin-top: 4em; }
    
        
    table.col2 { 
        max-width: 100%; width: 100%;
    }
    table.col2 td {
        width: 50%;
        text-align: center;
    }
} 


/************ TOC ***************/

@media print {
    /** two-column format */
    ul.toc { 
        column-count: 2; 
        column-gap: 20px;
    }
    
    /** add page numbers for the first two */
    ul#main_toc > li > a::after { 
        content: leader('_')  target-counter(attr(href), page) ;
        font-weight: bold;
    }

    ul#main_toc > li > ul > li > a::after { content: leader('_')  target-counter(attr(href), page) }
}

ul#main_toc > li > a > span.toc_number { 
    font-weight: bold;
}
ul#main_toc > li > a > span.toc_number::before { 
    content: 'Chapter '; 
    font-weight: bold;
}

ul#main_toc ul,
ul#main_toc ul ul {
    margin-left: 0;
}
ul#main_toc ul ul li  a {
    color: gray !important;
}
ul#main_toc ul ul li {
    display: inline;
}

ul.toc ul ul li a span.toc_number { display: none; }

ul.toc ul ul li a span.toc_name::before {
    margin-right: 3pt;
    
    content: '⟡'; /*◇';*/
    font-family: 'Cambria' !important;
    font-size: 6pt;
    /*padding-bottom: 5pt !important;*/
    /*border: solid 1px red;*/
    /*margin-top: -20pt !important;*/
    /*display: inline;*/
}
ul.toc ul ul li:first-child a span.toc_name::before {
    content: '';
    margin: 0;
}

div > ul:not(.toc)  {
    margin-left: 2em;
    margin-top: -0.3em;
    margin-bottom: -0.3em;
}


/* first header down is highlighted */
ul.chapter_toc > li > a {
    font-weight: bold;
}


/* below numbers are erased */
ul.chapter_toc > li > ul > li > a.toc_link > span.toc_number {
    color: red; 
}

ul.chapter_toc > li > ul > li > a.toc_link > span.toc_number {
    display: none;
}

ul.chapter_toc > li > ul > li > a.toc_link > span.toc_name::before {
    content: '•';
    margin-right: 0.5em;
}



/* keywords appearing in headers */
ul.toc code { 
    /*color: red !important;*/
    font-size: 7pt !important; 
}
ul.toc, ul.toc ul { padding: 0; margin-left: 1em;} 

ul.toc li { padding: 0; margin: 0;} 

ul#main_toc > li {
    /*margin-bottom: 3em;*/
    padding-bottom: 1em;
}
ul#main_toc > li > ul {
    padding-top: 4pt;
}
ul#main_toc > li > a span.toc_name { 
    font-weight: bold;  
    
/*    font-size: larger;*/
}

/*********  end TOC ************/

/********** headings *********/

#toc-heading { text-align: center; }

h2 { margin-top: 2em !important; }
h3 {
    font-style: normal !important;
    padding-top: 1em;

    width: 100%;
    padding-bottom: 3pt;
    border-bottom: solid 0.5pt grey;
}

h1:not(#booktitle), #toc-heading { font-variant: small-caps; }
h1:not(#booktitle) ::before { content: 'Chapter '; }
/***** end headings *****/


/******  latex ****/ 

div.definition::before { font-weight: bold; content: 'Definition';}
div.example::before { font-weight: bold; content: 'Example';}
div.remark::before { font-weight: bold; content: 'Remark';}
div.lemma::before { font-weight: bold; content: 'Lemma';}


.latex_env span.latex_env_label::before {content: ' (';}
.latex_env span.latex_env_label::after {content: ') ';}


/****** end latex ****/ 

/**** misc ***/


body { 
    hyphens: auto;
 }
/* No decoration for links */
a { text-decoration: none; color: darkblue;}

 p.todo {
    background-color: #fdd;
 }
 p.todo::before { content: 'TODO: '; }

pre { 
    margin-bottom: 0;
}

p + pre {
    margin-top: 0.7em;
} 
pre + br + pre { 
    margin-top: 0.3em;
    /*border: solid 1px red;*/
 /*float: left; clear: left;*/
}

"""

@contract(files_contents='list( tuple( tuple(str,str), str) )', returns='str')
def manual_join(files_contents):


#         <script src='https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML'></script>
# 
#         <script type="text/x-mathjax-config">
#             MathJax.Hub.Config({
#               tex2jax: {inlineMath: [['$','$']]},
#                 displayMath: [ ['$$','$$'], ["\\[","\\]"] ]
#             });
#         </script>


    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>PyMCDP manual</title>
        <meta charset="utf-8">
        <style type='text/css'>CSS</style>
        



    </head>
    <body>
    FIRSTPAGE
    <div id='body'/>
    </body>
    </html>
    """

    markdown_css = get_markdown_css()
    mcdp_css = get_language_css()
    template = template.replace('CSS', mcdp_css + '\n' + markdown_css + '\n' + manual_css)
    
    # title page
    (_libname, docname), first_data = files_contents.pop(0)
    assert docname == 'firstpage'
    
    first_dom = BeautifulSoup(first_data, 'lxml', from_encoding='utf-8')
    first_contents = first_dom.html.body
    first_contents.name = 'div'
    first_contents['id'] = docname
    template = template.replace('FIRSTPAGE', str(first_contents))
    
    d = BeautifulSoup(template, 'lxml', from_encoding='utf-8')
    
    # empty document
    main_body = BeautifulSoup("", 'lxml', from_encoding='utf-8')

    for (_libname, docname), data in files_contents:
        doc = BeautifulSoup(data, 'lxml', from_encoding='utf-8')
        body = doc.html.body
        body.name = 'div'
        body['id'] = docname
        main_body.append(body)

    for tag in main_body.select("a"):
        href = tag['href']
        # debug(href)
        # http://127.0.0.1:8080/libraries/tour1/types.html
        if href.endswith('html'):
            page = href.split('/')[-1]
            new_ref = '#%s' % page
            tag['href'] = new_ref

    toc = generate_doc(main_body)
    toc_ul = BeautifulSoup(toc, 'lxml', from_encoding='utf-8').html.body.ul
    toc_ul['class'] = 'toc'
    toc_ul['id'] = 'main_toc'
    toc_place = d.select('div#toc')[0]
    body_place = d.select('div#body')[0]
    
    #print('toc element: %s' % str(toc))
    toc_place.replaceWith(toc_ul)

    body_place.replaceWith(main_body)

    return str(d)

def debug(s):
    sys.stderr.write(str(s) + ' \n')

def generate_doc(soup):

    header_id = 1

    class Item():
        def __init__(self, tag, depth, name, _id, items):
            self.tag = tag
            self.name = name
            self.depth = depth
            self.id = _id
            self.items = items
#             for i in items:
#                 assert isinstance(items)

            self.number = None

        def number_items(self, prefix, level):
            self.number = prefix

            if self.tag is not None:
                # add a span inside the header
                span = soup.new_tag('span')
                span['class'] = 'toc_number'
                span.string = prefix + ' – '
                self.tag.insert(0, span)
                #self.tag.string = prefix + ' - ' + self.tag.string

            def get_number(i, level):
                if level == 0 or level == 1:
                    headings = ['%d' % (j + 1) for j in range(20)]
                elif level == 2:
                    headings = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
                        'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'Z']

                else:
                    return ''

                if i >= len(headings):
                    msg = 'i = %d level %s headings = %s' % (i, level, headings)
                    raise ValueError(msg)
                return headings[i]

            if prefix:
                prefix = prefix + '.'
            for i, item in enumerate(self.items):
                item_prefix = prefix + get_number(i, level)
                item.number_items(item_prefix, level + 1)

        def __str__(self, root=False):
            s = u''
            if not root:
                s += u"""<a class="toc_link" href="#%s">
                            <span class="toc_number">%s –</span> 
                            <span class="toc_name">%s</span></a>""" % (self.id, self.number, self.name)
            if self.items:
                s += '<ul>'
                for item in self.items:
                    s += '<li>%s</li>' % item
                s += '</ul>'
            return s

    stack = [ Item(None, 0, 'root', 'root', []) ]

    for header in soup.findAll(['h1', 'h2', 'h3']):
        header['id'] = header_id

        depth = int(header.name[1])

        # previous_depth = stack[-1].depth

        using = header.decode_contents(formatter="html")
#         print("%s or %s using %s" % (str(header), header.string, using))
        item = Item(header, depth, using, header['id'], [])

        while(stack[-1].depth >= depth):
            stack.pop()
        stack[-1].items.append(item)
        stack.append(item)
        header_id += 1


    root = stack[0]

    root.number_items(prefix='', level=0)

    # iterate over chapters (below each h1)
    for item in root.items:
        s = item.__str__(root=True)
        stoc = BeautifulSoup(s, 'lxml', from_encoding='utf-8')
        if stoc.html is not None: # empty document case
            ul = stoc.html.body.ul 
            ul['class'] = 'toc chapter_toc'
            # todo: add specific h1
            item.tag.insert_after(ul)


    return root.__str__(root=True)

