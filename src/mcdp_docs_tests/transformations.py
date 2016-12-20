from comptests.registrar import comptest, run_module_tests, comptest_fails
from mcdp_library.library import MCDPLibrary
from mcdp_web.renderdoc.main import render_complete
from mcdp_web.renderdoc.highlight import get_minimal_document


def tryit(s):
    library = MCDPLibrary()
    raise_errors = True
    realpath = 'trasnformations.py'
    s2 = render_complete(library, s, raise_errors, realpath, generate_pdf=False)
    
    assert not 'DOCTYPE' in s2, s2
    return s2      

@comptest
def f():
    s = """
    <mcdp-poset>`Name</mcdp-poset> and `` `code``.
"""
    tryit(s)
    

@comptest
def f2():
    s = """
    Use the syntax ``instance &#96;Name``.
"""
    tryit(s)
    
@comptest
def test_documentation1():
    s = """
    
This is a test:

    $ sudo pip

Also code <mcdp-poset>`poset</mcdp-poset>
    
And this is how you quote code:

    <mcdp-poset>`poset</mcdp-poset>
    
End.

Also math: $x^2$ cite \\ref{mia}

First:

$$ y = x \\label{mia} $$

Second:

\\begin{equation}
z = 2
\\end{equation}

\\begin{eqnarray*}
A & B & C\\\\
A & B & C
\\end{eqnarray*}

Second is \\ref{ciao}

\\begin{eqnarray}
A & B & C\\\\
A & B & C\\label{ciao}
\\end{eqnarray}

<style type='text/css'>
asvg { border: solid 1px red; }
</style>

A brushless motor like the [Traxxas 3351][Traxxas_3351]
provides the <mcdp-poset>`ContinuousRotation</mcdp-poset> functionality
and requires the <mcdp-poset>`PWM</mcdp-poset> resource.

Need code: ``code``

And this is the rest.

~~~
<render class='ndp_graph_templatized'>`model</render>
~~~

end

We can re-use previously defined MCDPs using the
syntax ``instance `Name``. The backtick means "load symbols from the library".



"""
    s2 = tryit(s)
    
    print s2
    
    fn = 'out-transformation.html'
    
    with open(fn,'w') as f:
        doc = get_minimal_document(s2, add_manual_css=True)
        f.write(doc)
    print('Written in %r' % fn)
    
    assert not '&amp;#96;Name' in s2
    assert not '&#96;' in s2
    assert not '&amp;' in s2
    assert not 'DOCTYPE' in s2


    
if __name__ == '__main__': 
#     overlapping()
    run_module_tests()
    