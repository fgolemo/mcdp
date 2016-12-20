from comptests.registrar import comptest, run_module_tests, comptest_fails
from mcdp_library.library import MCDPLibrary
from mcdp_web.renderdoc.main import render_complete
from mcdp_web.renderdoc.highlight import get_minimal_document


def tryit(s, write_to=None):
    library = MCDPLibrary()
    raise_errors = True
    realpath = 'trasnformations.py'
    s2 = render_complete(library, s, raise_errors, realpath, generate_pdf=False)
    
    if write_to is not None:
        doc = get_minimal_document(s2, add_manual_css=True)
        with open(write_to, 'wb') as f:
            f.write(doc)
        print('written to %s' % write_to)
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
    s2 = tryit(s, 'out-transformation.html')
    
    print s2
    assert not '&amp;#96;Name' in s2
    assert not '&#96;' in s2
    assert not '&amp;' in s2
    assert not 'DOCTYPE' in s2


@comptest
def f3():
    s = """    
That is, $\\funsp=\\mathbb{R}_{+}^{[\\text{J}]}$ and $\\ressp=\\mathbb{R}_{+}^{[\text{g}]}$. 
"""
    s = """    
That is, $F=\\mathbb{R}_{+}^{[\\text{J}]}$ and $R=\\mathbb{R}_{+}^{[\text{g}]}$. 

and $c=d_e$ and ``code_b`` and <code>a_b</code>. 
"""
    s2 = tryit(s, write_to="f3.html")
    assert not '<em' in s2
    
    
@comptest
def f4():

    m = ' \\uparrow U = \\{ x : \\text{property}(x) \}'
    s = """    
Try: $%s $ 

Try: 
$$%s$$

""" % (m, m)
    s2 = tryit(s, write_to="f4.html")
    assert not '<em' in s2
    
@comptest
def f52():
    s ="""

\\begin{defn}[Width and height of a poset]
\\label{def:poset-width-height} $\\mathsf{width}(\\posA)$ is the maximum
cardinality of an antichain in~$\\posA$ and $\\mathsf{height}(\\posA)$
is the maximum cardinality of a chain in~$\\posA$.
\\end{defn}

"""
    s2 = tryit(s, write_to="f52.html")

@comptest
def f5():
    s ="""

This is code: `one`

This is code: ``two``

Don't get confused here: <strong>`bold</strong> and <strong>`brave</strong>.

Should be fine <strong>&#96;bold</strong> and <strong>`brave</strong>.

"""
    s2 = tryit(s, write_to="f5.html")
    assert not 'gt' in s2
    

@comptest
def f6():
    s ="""

\begin{defn}[Upper closure]
The operator~$\uparrow$ maps a subset to the smallest upper set that
includes it:
\begin{eqnarray*}
\uparrow\colon\mathcal{P}(P) & \rightarrow & UP,\\
S & \mapsto & \{y\in P:\exists\,x\in S:x\leq y\}.
\end{eqnarray*}
\end{defn}

Try outside:
\begin{eqnarray*}
\uparrow\colon\mathcal{P}(P) & \rightarrow & UP,\\
S & \mapsto & \{y\in P:\exists\,x\in S:x\leq y\}.
\end{eqnarray*}

"""
    s2 = tryit(s, write_to="f6.html")
    assert not 'em' in s2
    assert not ' {y\in' in s2
    
    
     

if __name__ == '__main__': 
    f5()
#     run_module_tests()
    