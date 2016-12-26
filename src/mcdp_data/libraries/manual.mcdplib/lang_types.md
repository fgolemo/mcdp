## Posets and their values

All values of <f>functionality</f> and <r>resources</r> belong to posets. PyMCDP
knows a few built-in posets, and gives you the possibility of creating your own.
%
[](#tab:summary_posets) shows the basic posets that are built in: natural
numbers, nonnegative real numbers, and nonnegative real numbers that have units
associated to them.

<col1>
<col3 figure-id="tab:summary_posets" figure-caption="Built-in posets"
        class="labels-row1" id='id-given-to-col3'>

        <s>MCDPL poset</s>
        <s>ideal poset</s>
        <s>Python representation</s>


        <pos np>Nat</pos>

        $\langle\mathbb{N} \cup \top, \leq\rangle$

        <s><code>int</code> plus a special <code>Top</code> object</s>


        <pos np>Rcomp</pos>

        $\langle{\mathbb{R}}_+ \cup \top, \leq\rangle$

        <s><code>float</code> plus a special <code>Top</code> object</s>


        <pos np>g</pos>

        $\langle\mathbb{R}^{[\text{g}]}_+\cup \top, \leq\rangle$

        <s><code>float</code> plus a special <code>Top</code> object</s>
</col3>
</col1>


### Natural numbers <pos np>Nat</pos> <pos>Nat</pos>

By $\overline{\mathbb{N}}$ we mean the completion of  $\mathbb{N}$ to include a
top element $\top$. This makes the poset a [complete partial order](#def:cpo)
([](#def:cpo)).


The natural numbers with completion are expressed as <pos np>Nat</pos>
or with the Unicode letter "<pos>Nat</pos>".
%
Their values using the syntax <val np>Nat:42</val>
or simply <val>42</val>.

Internally, $\mathbb{N}$ is represented by the [Python type `int`][int], which
is equivalent to the 32 bits `signed long` type in C. So, it is really
a chain of $2^{31} + 1$ elements.

[int]: https://docs.python.org/2/library/stdtypes.html#numeric-types-int-float-long-complex

### Nonnegative floating point numbers <pos np>Rcomp</pos> <pos>Rcomp</pos>  {#subsub:Rcomp}

Let $\reals_{+}=\{x \mid x \geq 0\}$ be the nonnegative real numbers  and let
$\overline{\reals}_{+} = \reals_{+} \cup \top$ be its completion. The $+$ and
$\times$ operations are extended from $\reals$ to $\Rcomp$ by defining the
following:

\begin{eqnarray}
    \forall a:& \quad a + \top &= \top \\
    \forall a:& \quad a \times \top &= \top
\end{eqnarray}

This poset is indicated in MCDPL by <pos np>Rcomp</pos> or <pos>Rcomp</pos>.
Values belonging to this poset are indicates with the syntax their values as
<val np>Rcomp:42.0</val>, <val>Rcomp:42.0</val>, or simply <val>42.0</val>.

Internally, $\Rcomp$ is approximated using double precision point numbers ([IEEE
754]), corresponding to the <code>float</code> type used by Python and the
`double` type in C (in most implementations of C).
%
Of course, the floating point implementations of $+$ and $\times$ are also not
associative or commutative due to rounding errors. PyMCDP does not assume
commutativity or associativity; the assumption is just that they are
[monotone](#def:monotone-map) ([](#def:monotone-map)) in each argument (which
they are).

[IEEE 754]: https://en.wikipedia.org/wiki/IEEE_floating_point



### Nonnegative floating point numbers with units

Floating point numbers can also have **units** associated to them.
So we can distinguish $\reals^{[\text{m}]}$ from $\reals^{[\text{s}]}$
and even $\reals^{[\text{m}]}$  from $\reals^{[\text{km}]}$.
%
These posets and their values are indicated using the
syntax in [](#tab:number-units).

<col1>
<col7 figure-id="tab:number-units"
    figure-caption="Numbers with units"
    class='labels-col1'>

    <span>ideal poset</span>
    <span>$\langle\Rcomp^{[\text{g}]}, \leq\rangle$</span>
    <span>$\langle\Rcomp^{[\text{J}]}, \leq\rangle$</span>
    <span>$\langle\Rcomp^{[\text{m}]}, \leq\rangle$</span>
    <span>$\langle\Rcomp^{[\text{s}]}, \leq\rangle$</span>
    <span>$\langle\Rcomp^{[\text{m/s}]}, \leq\rangle$</span>
    <span>…</span>

    <span>syntax<br/> for posets</span>
    <pos>g</pos>
    <pos>J</pos>
    <pos>m</pos>
    <pos>s</pos>
    <pos>m/s</pos>
    <span>…</span>

     <span>syntax<br/> for values</span>
     <val>1.2 g</val>
     <val>20 J</val>
     <val>10 m</val>
     <val>10 s</val>
     <val>23 m/s</val>
     <span>…</span>

</col7>
</col1>

<style>
    #tab\:number-units tr:not(:first-child) td {
        text-align: right;
    }
</style>


<!-- #### Operations with units -->

In general, units behave as one might expect.
Units are implemented using the library [Pint][pint]; please
see its documentation for more information.
The following is the formal definition of the operations
involving units.

[pint]: http://pint.readthedocs.org/


Units in Pint form a [group] with an equivalence relation.
Call this group of units $U$ and its elements $u, v, \dots \in U$.
By $\mathbb{F}^{[u]}$, we mean a field $\mathbb{F}$
enriched with an annotation of units $u\in U$.

[group]: https://en.wikipedia.org/wiki/Group_(mathematics)#Definition


Multiplication is defined for all pairs of units. Let $|x|$ denote the absolute
numerical value of $x$ (stripping the unit away). Then, if $x \in
\mathbb{F}^{[u]}$  and $y \in \mathbb{F}^{[v]}$, their product is $x\cdot y \in
\mathbb{F}^{[uv]} $ and $|x\cdot y| = |x|\cdot|y|$.

Addition is defined only for compatible pairs of units (e.g., <pos>m</pos> and
<pos>km</pos>), but it is not possible to sum, say, <pos>m</pos> and
<pos>s</pos>. If $x \in \mathbb{F}^{[u]}$  and $y \in \mathbb{F}^{[v]}$, then $x +
y \in \mathbb{F}^{[u]} $, and $ x + y = |x| + \alpha^u_v |y| $, where
$\alpha^u_v$ is a table of conversion factors, and $|x|$ is the absolute
numerical value of $x$.


In practice, this means that MCDPL thinks that <val>1 kg + 1 g</val> is equal to
<val>1.001 kg</val>. Addition is not strictly commutative, because <val>1 g + 1
kg</val> is equal to <val>1001 g</val>, which is equivalent, but not equal, to
<val>1.001 kg</val>.



### Defining custom posets <k>poset</k>

It is possible to define custom finite posets
using the keyword <k>poset</k>.

For example, supposes that we create a file named `MyPoset.mcdp_poset`
containing the definition in [](#code:MyPoset). This declaration defines a poset
with 5 elements `a`, `b`, `c`, `d`, `e` and with the given order relations, as
displayed in [](#fig:MyPosetHasse).


<col2>
    <pre class='mcdp_poset' id='MyPoset' label='MyPoset.mcdp_poset'
         figure-id='code:MyPoset'
         figure-caption='Definition of a custom poset'
         >
    poset {
        a b c d e&#32;&#32;&#32;&#32;&#32;&#32;&#32; <!-- code for space -->

        a ≼ b
        c ≼ d
        e ≼ d
        e ≼ b
    }
    </pre>
    <render class='hasse' figure-id="fig:MyPosetHasse">`MyPoset</render>
</col2>

The name of the poset, `MyPoset`, comes from the filename `MyPoset.mcdp_poset`.
After the poset has been defined, it can be used in the definition of an MCDP,
by referring to it by name using the backtick notation, as in
<q><pos>`MyPoset</pos></q>.

To refer to its elements, use the notation <val>`MyPoset: element</val>
([](#code:one)).

<col2>
    <pre class='mcdp' id='one' figure-id='code:one'
    figure-caption='Referring to an element of a custom poset'>
mcdp {
    provides f [&#96;MyPoset]

    provided f ≼ &#96;MyPoset : c
}
    </pre>

    <render class='ndp_graph_enclosed'>&#96;one</render>
</col2>


### Poset products <k>×</k>

MCDPL allows the definition of finite cartesian products.

\begin{defn}[Product of posets]
  \label{def:product-posets}
%
For two posets $P,Q$, the Cartesian product $P\times Q$
is the set of pairs $\langle p, q \rangle$ for $p\in P$ and $q \in Q$.
The order is the following:
%
$$
    \langle p_1, q_1 \rangle \posleq \langle p_2, q_2 \rangle
    \quad \equiv \quad
    (p_1 \posleq_P p_2) \wedge (q_1 \posleq_Q q_2).
$$
\end{defn}

In MCDPL, use the Unicode symbol "<k>×</k>" or the simple letter "<k>x</k>" to
create a poset product, using the syntax:


<col2>
    <pre class='mcdp_poset'>
    [["poset"]] × [["poset"]] × [["..."]] × [["poset"]]
    </pre>

    <pre class='mcdp_poset'>
    [["poset"]] x [["poset"]] x [["..."]] x [["poset"]]
    </pre>
</col2>

For example, the expression <pos>J × A</pos> represents a product of Joules and
Amperes.

The elements of a poset product are called "tuples". These correspond exactly to
[Python's tuples][tuples]. To define a tuple, use angular brackets
<q><code>&lt;</code></q> and <q><code>&gt;</code></q>. The syntax is:

<div>
    <pre class='mcdp_value' np>
    &lt;[[valueXXX]], [[value]], [["..."]], [[value]]&gt;
    </pre>
</div>

For example, the expression <val>&lt;2 J, 1 A&gt;</val> denotes a tuple with two
elements, equal to <val>2 J</val> and <code class='mcdp_value'>2 A</code>. An
alternative syntax uses the fancy Unicode brackets <q>&#x3008;</q> and
<q>&#x3009;</q>, as in <val>⟨0 J, 1 A⟩</val>.

[tuples]: https://docs.python.org/3/tutorial/datastructures.html#tuples-and-sequences


Tuples can be nested. For example, you can describe a tuple like <val np>⟨ ⟨0 J,
1 A⟩, ⟨1 m, 1 s, 42⟩ ⟩</val>, and its poset is denoted as <code>(</code><pos
np>(J × A) × (m × s × Nat)</pos><code>)</code>.


### Named Poset Products <k>product</k>

MCDPL also supports "named products". These are semantically equivalent to
products, however, there is also a name associated to each entry. This allows to
easily refer to the elements.For example, the following declares a product of
the two spaces <pos>J</pos> and <pos>A</pos> with the two entries named
``energy`` and ``current``.

<div center>
    <pre class='mcdp_poset'>
    product(energy:J, current:A)
    </pre>
</div>

The names for the fields must be valid identifiers (starts with a letter,
contains letters, underscore, and numbers).

### Power sets <k>set-of</k> <k>℘</k>

MCDPL allows to describe the set of subsets of a poset, i.e. its [power
set][powerset]. The power set $\pset(Q)$ of a poset $Q$ is a poset with the
order given by inclusion:

$$
    a \posleq_{\pset(Q)} b
    \quad \equiv \quad
    a \subseteq b.
$$
%
In this order, $\emptyset$ is the top. Meet and join are
union and intersection, respectively.

[powerset]: https://en.wikipedia.org/wiki/Power_set
<!--
<figure class='figure'>
    <img src='Hasse_diagram_of_powerset_of_3.svg' style='width:13em'/>
    <figcaption>Power set of ${1,2,3}$ ordered by inclusion.</figcaption>
</figure> -->

The syntax is either of these:

<col2>
    <pre class='mcdp_poset ex1'>
    ℘([["poset"]])
    </pre>
    <pre class='mcdp_poset ex1'>
    set-of([["poset"]])
    </pre>
</col2>

<!-- TODO: this syntax will be changed to <k>powersets</k> -->

To describe values in a powerset, i.e. subsets, use this
set-building notation:

<pre class='mcdp_value'>
{ [[value]], [[value]], [["..."]], [[value]]}
</pre>

For example, the value <val>{1,2,3}</val>
is an element of the poset <pos>℘(Nat)</pos>.

<h3>
    Upper and lower sets and closures

   <k>UpperSets</k>
   <k>LowerSets</k>
   <k>upperclosure</k>
   <k>↑</k>
   <k>lowerclosure</k>
   <k>↓</k>
</h3>

Upper sets ([](#def:upperset)) and lower sets ([](#def:lowerset))
can be described by the syntax

<col2>
    <pre class='mcdp_poset'>
    UpperSets([[poset]])
    </pre>

    <pre class='mcdp_poset'>
    LowerSets([[poset]])
    </pre>
</col2>

For example, <poset>UpperSets(Nat)</poset> represents the space of
uppersets for the natural numbers.

To describe an upper set (i.e. an element of the space of upper sets), use the
keyword <k>upperclosure</k> or its abbreviation <k>↑</k>. The syntax is:

<col2>
    <pre class='mcdp_value'>
    upperclosure [[ set ]]
    </pre>

    <pre class='mcdp_value'>
    ↑ [[ set ]]
    </pre>
</col2>

For example: <value>↑ {2 g, 1 m}</value> denotes the principal upper set of
the element <value>{2 g, 1 m}</value> in the poset <poset>g x m</poset>.


### Interval (experimental)

The syntax is

<div center>
    <pre class='mcdp_poset'>
    Interval([["lower bound"]], [["upper bound"]])
    </pre>
</div>

<!--
<pre><code><span class="keyword">Interval</span>(<span class='ph'>lower bound</span>,<span class='ph'>upper bound</span>)</code></pre>
 -->
For example:

<pre class='mcdp_poset'>
Interval(1g, 10g)
</pre>

### Singletons (experimental)

    S(tag)

    S(tag):*



## Other ways to specify values


### Top and bottom <k>Top</k> <k>Bottom</k>

These expressions allow to indicate minimal and maximals elements.

To indicate top and bottom of a poset, use the syntax:

<col2>
        <val np>Top [["poset"]]</val>
        <val>⊤ [["poset"]]</val>
        <val np>Bottom [["poset"]]</val>
        <val>⊥ [["poset"]]</val>
</col2>

For example, <val>Top V</val> indicates
the top of the <pos>V</pos>.

TODO: syntax <code>poset: Top</code>.


### Minimals and maximals  <k>Minimals</k> <k>Maximals</k>

The expressions <val>Minimals [["poset"]]</val>
and <val>Maximals [["poset"]]</val>
denote the set of minimal and maximal elements of a poset.


<!-- <pre class='mcdp_poset' id='MyPoset' label='MyPoset.mcdp_poset'
    figure-id='code:MyPoset'></pre> -->
<div id='outside'>
    <render class='hasse' figure-id="fig:hasse2" >&#96;MyPoset</render>
</div>

<style>
#outside figure { margin: 0; }
#outside {
    width: 12em;
    float: right;
}
</style>

For example, assume that the poset <code>MyPoset</code> is defined as in
[](#fig:hasse2). % Then <val>Maximals &#96;MyPoset</val> is equivalent to `b`and
`d` and <val>Minimals &#96;MyPoset</val> is equivalent to `a`, `e`, `c`.

<!--
<pre class='mcdp_value' id='value1'>
    assert_equal(Maximals &#96;MyPoset, {&#96;MyPoset:b, &#96;MyPoset:d})
</pre>
<pre class='mcdp_value'>
    assert_equal(Minimals &#96;MyPoset, {&#96;MyPoset:a, &#96;MyPoset:e, &#96;MyPoset:c, })
</pre>

<pre class='print_value'>&#96;value1</pre> -->

### The empty set <k>EmptySet</k>

To denote the empty set, use the keyword <k>EmptySet</k>:

<pre class='mcdp_value'>
EmptySet [[poset]]
</pre>

Note that empty sets are typed---this is different from set theory.
<val>EmptySet J</val> is an empty set of energies,
and <val>EmptySet V</val> is an empty set of voltages,
and the two are not equivalent.

<!-- or

<pre class='mcdp_value'>
ø [[space]]
</pre> -->
