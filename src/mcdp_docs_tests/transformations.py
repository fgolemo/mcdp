# -*- coding: utf-8 -*-
from comptests.registrar import comptest, run_module_tests, comptest_fails
from contracts.utils import raise_desc, indent
from mcdp_library.library import MCDPLibrary
from mcdp_web.renderdoc.highlight import get_minimal_document, TAG_DOLLAR
from mcdp_web.renderdoc.main import render_complete
from mcdp_web.renderdoc.markdown_transform import censor_markdown_code_blocks
from mcdp_lang_tests.syntax_spaces import indent_plus_invisibles


def tryit(s, write_to=None, forbid=[]):
    library = MCDPLibrary()
    raise_errors = True
    realpath = 'transformations.py'
    s2 = render_complete(library, s, raise_errors, realpath, generate_pdf=False)
    
    if False:
        if write_to is not None:
            doc = get_minimal_document(s2, add_manual_css=True)
            with open(write_to, 'wb') as f:
                f.write(doc)
            print('written to %s' % write_to)
        
    tests = {
     'doctype': not 'DOCTYPE' in s2,
     'warn_caption': not 'caption' in s2,
     'warn_centering': not 'centering' in s2,
     'warn_tabular': not 'tabular' in s2,
     'funny': not '&amp;#96;' in s2,
     'dollarfix': not TAG_DOLLAR in s2,
#     assert not '&#96;' in s2
#     assert not '&amp;' in s2

    }
    for x in forbid:
        tests['contains %r' % x] = not x in s2
    msg = ''
    summary = {'warn': 0, 'error': 0}
    for k in sorted(tests):
        level = 'warn' if 'warn' in k else 'error'
        passed = tests[k]
        if not passed:
            summary[level] += 1
        mark = '✓' if passed else 'no'
        msg += '\n %20s : %s' % (k, mark)
    
    if summary['error']:
        msg += '\nSee output in %s'%  (write_to)
        raise_desc(Exception, msg)
    
    return s2      

@comptest
def conv_f():
    s = """
    <mcdp-poset>`Name</mcdp-poset> and `` `code``.
"""
    tryit(s)
    

@comptest
def conv_f2():
    s = """
    Use the syntax ``instance `Name``.
"""
    tryit(s)


@comptest
def conv_test_documentation1():
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
    


@comptest
def conv_f3():
#     s = """    
# That is, $\\funsp=\\mathbb{R}_{+}^{[\\text{J}]}$ and $\\ressp=\\mathbb{R}_{+}^{[\text{g}]}$. 
# """
    s = r"""    
That is, $F=\mathbb{R}_{+}^{[\text{J}]}$ and $R=\mathbb{R}_{+}^{[\text{g}]}$. 

and $c=d_e$ and ``code_b`` and <code>a_b</code>. 
"""
    s2 = tryit(s, write_to="f3.html", forbid=['<em'])
#     print s2
    
    
@comptest
def conv_f4():

    m = ' \\uparrow U = \\{ x : \\text{property}(x) \}'
    s = """    
Try: $%s $ 

Try: 
$$%s$$

""" % (m, m)
    s2 = tryit(s, write_to="f4.html",
               forbid=['<em'])
    
@comptest
def conv_f52():
    s ="""

\\begin{defn}[Width and height of a poset]
\\label{def:poset-width-height} $\\mathsf{width}(\\posA)$ is the maximum
cardinality of an antichain in~$\\posA$ and $\\mathsf{height}(\\posA)$
is the maximum cardinality of a chain in~$\\posA$.
\\end{defn}

"""
    s2 = tryit(s, write_to="f52.html")

@comptest
def conv_f5():
    s ="""

This is code: `one`

This is code: ``two``

<!-- known bug:  <strong>`bold</strong> and <strong>`brave</strong>. -->

Should be fine <strong>&#96;bold</strong> and <strong>`brave</strong>.

"""
    s2 = tryit(s, write_to="f5.html",
               forbid=['&gt;'])
    

@comptest
def conv_f6():
    s ="""

\\begin{defn}[Upper closure]
The operator~$\\uparrow$ maps a subset to the smallest upper set that
includes it:
\\begin{eqnarray*}
\\uparrow\\colon\\mathcal{P}(P) & \\rightarrow & UP,\\
S & \\mapsto & \\{y\\in P:\\exists\\,x\\in S:x\\leq y\\}.
\\end{eqnarray*}
\\end{defn}

Try outside:
\\begin{eqnarray*}
\\uparrow\\colon\\mathcal{P}(P) & \\rightarrow & UP,\\\\
S & \\mapsto & \\{y\\in P:\\exists\\,x\\in S:x\\leq y\\}.
\\end{eqnarray*}

"""
    tryit(s, write_to="f6.html",
               forbid=['<em', ' {y'])

others = [
    """
\\begin{defn}[Upper closure]
The operator~$\\uparrow$ maps a subset to the smallest upper set that
includes it:
\\begin{eqnarray*}
\\uparrow\\colon\\mathcal{P}(P) & \\rightarrow & UP,\\\\
S & \\mapsto & \\{y\\in P:\\exists\\,x\\in S:x\\leq y\\}.
\\end{eqnarray*}
\\end{defn}

    """,
    r"""
    

(if it exists) of the set of fixed points of~$f$:
\begin{equation}
x = y .\label{eq:lfp-one}
\end{equation}
The equality in \eqref{lfp-one} can be relaxed to ``$xxx$''.

The equality in \ref{eq:lfp-one} can be relaxed to ``$xxx$''.


The least fixed point need not exist. Monotonicity of the map~$f$
plus completeness is sufficient to ensure existence. 

    """,
    """

For example, to solve the MCDP specified in the file ``battery.mcdp`` in
the library ``src/mcdp_data/libraries/examples/example-battery.mcdplib``, use:

    $ mcdp-solve -d src/mcdp_data/libraries/examples/example-battery.mcdplib battery "<1 hour, 0.1 kg, 1 W>"
""",
r"""
Requires <strong>`bold</strong>.

Requires <mcdp-poset>`bold</mcdp-poset>.

Requires <mcdp-poset>`bold</mcdp-poset> and <mcdp-poset>`bold</mcdp-poset> 

Requires <strong>`bold</strong> and <strong>`brave</strong>.
""",
"""
This is fbox: \\fbox{ ciao !!! }

This is fbox2: \\fbox{ ciao !!! }
""",
"""
A:

r~~~
<strong>This should be pre, not strong</strong>
~~~
""",
"""
\\begin{figure}[H]
\\hfill{}\\subfloat[\\label{fig:Simple-DP}]{\\centering{}
\\includegraphics[scale=0.33]{gmcdptro_nonconvex1b}}
\\caption{\\label{fig:ceil-1}One feedback connection and a topologically continuous~$\\ftor$
are sufficient to induce a disconnected feasible set.}
\\end{figure}
""",
"""
The minimal MCDP can be defined as in <a href="#code:empty"/>.

<pre class='mcdp' id='empty' figure-id='code:empty'>
mcdp {

}
</pre>
""",
"""

Citing them in order:

* <a href="#sec:sA"/> (should be: sA)
* no label:
  
  <ul>
  <li> child</li>
  <li> child: <a href="#sub:child_second"/> (should be 2.2)</li>
  </ul>

* <a href="#sec:sB"/> (should be: sB)
* sC
  
  <ul>
  <li>no</li>
  <li> <a href="#sub:sC_child"/></li>
  </ul>

* <a href="#sub:sssF"/> (should be: sssF)



\\section{sA \\label{sec:sA} (should be 1)} 
\\section{second bu without label (should be 2)}
\\subsection{child of second (should be 2.1)} 
\\subsection{child of second \\label{sub:child_second} (should be 2.2)}
\\subsubsection{child of child of sA}

\\section{sB \\label{sec:sB}}

\\section*{sB-not numbered}
\\subsection{child of sB - this will be 3.0 however it's a bug - no numbered inside nn}
\\section{sC (should be Section 4)}
\\subsection{ssC \\label{sub:sC_child} (should be Subsection 4.1)}
\\subsection{ssD (should be Subsection 4.2)}
\\subsubsection{sssF \\label{sub:sssF} should be 4.2-A}
\\subsubsection*{sssG unnumbered}
\\subsubsection{sssF2 \\label{sub:sssF2} should be 4.2-B}
\\subsection*{ssE unnumbered}

<style>
h1 {page-break-before: avoid !important;}

h1 { text-align: left !important; }
h2 { margin-left: 3em !important; }
h3 { margin-left: 6em !important; }
</style>
""",
"""
This is a ``best'' occasion for you. This is code: ``ciao``.
This is confusing: ``twosingle''twosingle``
This is a ``best`` occasion for you.
""",
"""
I would like to acknowledge:

* Co-authors [David Spivak][spivak] and Joshua Tan, who developed the categorical
  foundations of this theory.

DRAFT

* Jerry Marsden for geometry. (Here, I'm proud that the invariance group is quite large: it
is the group of all invariants..)

/DRAFT

[spivak]: http://math.mit.edu/%7edspivak/
""",
"""

"""
]
    


@comptest
def other0(): tryit(others[0]) 
@comptest
def other1(): tryit(others[1]) 
@comptest
def other2(): tryit(others[2]) 
@comptest
def other3(): tryit(others[3]) 
@comptest
def other4(): tryit(others[4]) 
@comptest
def other5(): tryit(others[5]) 
@comptest
def other6(): tryit(others[6]) 
@comptest
def other7(): tryit(others[7]) 
@comptest
def other8(): tryit(others[8]) 
@comptest
def other9(): tryit(others[9]) 
@comptest
def other10(): tryit(others[10]) 
@comptest
def other11(): tryit(others[11]) 

@comptest
def another():
    s = """
This is the case of unreasonable demands (1 kg of extra payload):

    $ mcdp-solve -d src/mcdp_data/libraries/examples/example-battery.mcdplib battery "<1 hour, 1.0 kg, 1 W>"
    """
    s2 = tryit(s)
    print indent(s2, 's2: ')
    assert '1 hour' in s2
    
assert len(others) == 12, len(others)

@comptest
def another2():
    # four spaces in the first line
    s = r"""
    
(if it exists) of the set of fixed points of~$f$:
\begin{equation}
x = y .\label{eq:lfp-one}
\end{equation}
The equality in \eqref{lfp-one} can be relaxed to ``$xxx$''.

The equality in \ref{eq:lfp-one} can be relaxed to ``$xxx$''.


The least fixed point need not exist. Monotonicity of the map~$f$
plus completeness is sufficient to ensure existence. 
"""
    s2 = censor_markdown_code_blocks(s)
    
    print('original:')
    print indent_plus_invisibles(s)
    print('later:')
    print indent_plus_invisibles(s2)
    
    assert not 'censored-code' in s



@comptest
def no_dollar():
    # four spaces in the first line
    s = r"""
    
<col2>
    <span>&#36;</span> <span>alphanumeric</span>
    <code>a₆</code> <code>a_6</code>
    <code>&#36;</code> <code>USD</code>
    <code>×</code> <code>x</code>
</col2>

"""
    s2 = tryit(s)
    
#     print('original:')
#     print indent_plus_invisibles(s)
#     print('later:')
#     print indent_plus_invisibles(s2)
#     
    assert not 'DOLLAR' in s2
    

@comptest_fails
def splittag():
    # four spaces in the first line
    s = r"""
        
Please send any comments, suggestions, or bug reports to <a
href="mailto:censi@mit.edu">censi@mit.edu</a>.

"""
    s2 = tryit(s) 
    print s2
    
    sub = r"""<p>Please send any comments, suggestions, or bug reports to <a href="mailto:censi@mit.edu">censi@mit.edu.</p>"""
    assert sub in s2
    
if __name__ == '__main__': 
#     another2()
    run_module_tests()
    