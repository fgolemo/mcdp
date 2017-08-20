from comptests.registrar import comptest, run_module_tests
from mcdp_docs_tests.transformations import tryit
from mcdp_docs.pipeline import render_complete
from mcdp_library.library import MCDPLibrary
from mcdp_docs.manual_join_imp import manual_join
from mcdp_utils_xml.project_text import project_html
from mcdp_utils_xml.parsing import bs



@comptest
def tags_in_titles1():
    template = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
    <html lang="en">
    <head>
        <title>The Duckietown book</title>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    </head>
<body>
</body>
</html>
"""
    s = """


<span id='frag'>I will refer to <a href="#two" class='number_name'></a></span>

# Two with `program` {#two}

Another.
 
    
"""
    library = MCDPLibrary()
    raise_errors = True
    realpath = 'transformations.py'
    s2 = render_complete(library, s, raise_errors, realpath, generate_pdf=False)
    files_contents= [(('one', 'one'), s2)]
    stylesheet = 'v_manual_blurb_ready'
    res = manual_join(template, files_contents, 
                stylesheet, remove=None, extra_css=None,
                remove_selectors=None,
                hook_before_toc=None)
    soup = bs(res)
    element = soup.find(id='frag')
    print element
    if '&lt;code&gt;' in str(element):
        raise Exception(str(element))
        
#     r2 = project_html(res)

@comptest
def tags_in_titles2():
    template = """
    <html>
    <head>
        </head>
    <body>
        <div id='toc'></div>
    </body>
    </html>
"""
    s = """


<span id='frag'>I will refer to <a href="#two" class='number_name'></a></span>

# One is ok {#one}

Ignore

# Two with `program` {#two}

Another.
 
    
"""
    library = MCDPLibrary()
    raise_errors = True
    realpath = 'transformations.py'
    s2 = render_complete(library, s, raise_errors, realpath, generate_pdf=False)
    files_contents= [(('one', 'one'), s2)]
    stylesheet = 'v_manual_blurb_ready'
    res = manual_join(template, files_contents, 
                stylesheet, remove=None, extra_css=None,
                remove_selectors=None,
                hook_before_toc=None)
#     print res
    soup = bs(res)
    element = soup.find(id='main_toc')
    print element
    if 'fragment' in str(element):
        raise Exception(str(element))


    
    
if __name__ == '__main__':
    run_module_tests()