#!/usr/bin/env python
from bs4 import BeautifulSoup
import sys, os, urllib2, codecs

files = sys.argv[1:]


def go():

    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>PyMCDP manual</title>
        <meta charset="utf-8">
        <style type='text/css'>CSS</style>

        <script src='https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML'></script>

        <script type="text/x-mathjax-config">
            MathJax.Hub.Config({
              tex2jax: {inlineMath: [['$','$']]}
            });
        </script>

    </head>
    <body>
    <h1 id='booktitle'>The PyMCDP user manual</h1>
    <div id='toc'/>
    <div id='body'/>
    </body>
    </html>
    """

    css = urllib2.urlopen('http://127.0.0.1:8080/static/css/mcdp_language_highlight.css').read()
    other =  urllib2.urlopen('http://127.0.0.1:8080/static/css/markdown.css').read()
    extra = open('manual.css').read()
    template = template.replace('CSS', css + '\n' + other + '\n' + extra)
    d = BeautifulSoup(template, 'lxml')
    main_body = BeautifulSoup("", 'lxml')

    for f in files:
        data = codecs.open(f,'r',encoding='utf8').read()
        doc = BeautifulSoup(data, 'lxml', from_encoding='utf-8')

        body = doc.body
        body.name = 'div'
        body['id'] = os.path.basename(f)
        main_body.append(body)

    for tag in main_body.select("a"):
        href = tag['href']
        #debug(href)
        # http://127.0.0.1:8080/libraries/tour1/types.html
        if href.endswith('html'):
            page = href.split('/')[-1]
            new_ref= '#%s' % page
            tag['href'] = new_ref
    
    toc = generate_doc(main_body)
    toc = BeautifulSoup(toc, 'lxml')
    toc['class'] = 'toc'
    toc['id'] = 'toc'
    toc_place = d.select('div#toc')[0]
    body_place = d.select('div#body')[0]
    toc_place.replaceWith(toc)
     
    body_place.replaceWith(main_body)

    print str(d)

def debug(s):
    sys.stderr.write(str(s) + ' \n')

def generate_doc(soup):

    header_id = 1

    class Item():
        def __init__(self, tag, depth, name, id, items):
            self.tag = tag
            self.name = name
            self.depth = depth
            self.id = id
            self.items = items
            for i in items:
                assert isinstance(items)

        def __str__(self, root=False):
            s = ''
            if not root:
                s += '<a href="#%s">%s</a>' % (self.id, self.name)
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

        item = Item(header, depth, header.string, header['id'], [])

        while(stack[-1].depth >= depth):
            stack.pop()
        stack[-1].items.append(item)
        stack.append(item)
        header_id += 1


    root = stack[0]

    for item in root.items:
        s = item.__str__(root=True)
        stoc = BeautifulSoup(s, 'lxml')
        stoc['class'] = 'toc'
        item.tag.insert_after(stoc)


    return root.__str__(root=True)



go()