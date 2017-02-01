
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


        <poset np>Nat</poset>

        <s>$\langle\mathbb{N} \cup \top, \leq\rangle$</s>

        <s><code>int</code> plus a special <code>Top</code> object</s>


        <poset np>Rcomp</poset>

        <s>$\langle{\mathbb{R}}_+ \cup \top, \leq\rangle$</s>

        <s><code>float</code> plus a special <code>Top</code> object</s>


        <poset np>g</poset>

        <s>$\langle\mathbb{R}^{[\text{g}]}_+\cup \top, \leq\rangle$</s>

        <s><code>float</code> plus a special <code>Top</code> object</s>
</col3>
</col1>


### Natural numbers <poset np>Nat</poset> <poset>Nat</poset>

By $\overline{\mathbb{N}}$ we mean the completion of  $\mathbb{N}$ to include a
top element $\top$. This makes the poset a [complete partial order](#def:cpo)
([](#def:cpo)).


The natural numbers with completion are expressed as <q><poset np>Nat</poset></q>
or with the Unicode letter <q><poset>Nat</poset></q>.
%
Their values are denoted using the syntax <q><value np>Nat:42</value></q>
or simply <q><value>42</value></q>.

Internally, $\mathbb{N}$ is represented by the [Python type `int`][int], which
is equivalent to the 32 bits `signed long` type in C. So, it is really
a chain of $2^{31} + 1$ elements.

[int]: https://docs.python.org/2/library/stdtypes.html#numeric-types-int-float-long-complex

### Nonnegative floating point numbers <poset np>Rcomp</poset> <poset>Rcomp</poset>  {#subsub:Rcomp}

Let $\reals_{+}=\{x \mid x \geq 0\}$ be the nonnegative real numbers  and let
$\overline{\reals}_{+} = \reals_{+} \cup \top$ be its completion. The $+$ and
$\times$ operations are extended from $\reals$ to $\Rcomp$ by defining the
following:

\begin{eqnarray}
    \forall a:& \quad a + \top &= \top \\
    \forall a:& \quad a \times \top &= \top
\end{eqnarray}

This poset is indicated in MCDPL by <poset np>Rcomp</poset> or <poset>Rcomp</poset>.
Values belonging to this poset are indicates with the syntax their values as
<value np>Rcomp:42.0</value>, <value>Rcomp:42.0</value>, or simply <value>42.0</value>.

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

<center>
    <col4  class='labels-col1'
        figure-id="tab:number-units" figure-caption="Numbers with units" >
        <span>ideal&nbsp;poset</span>
        <span>$\langle\Rcomp^{[\text{g}]}, \leq\rangle$</span>
        <span>$\langle\Rcomp^{[\text{J}]}, \leq\rangle$</span>
        <span>$\langle\Rcomp^{[\text{m/s}]}, \leq\rangle$</span>
        <!-- <span>…</span> -->

        <span>syntax&nbsp;for&nbsp;poset</span>
        <poset>g</poset>
        <poset>J</poset>
        <poset>m/s</poset>
        <!-- <span>…</span> -->

         <span>syntax&nbsp;for&nbsp;values</span>
         <value>1.2 g</value>
         <value>20 J</value>
         <value>23 m/s</value>
         <!-- <span>…</span> -->
    </col4>
</center>

<style>
    #tab\:number-units {
        /*tr:not(:first-child) */
        td {
            text-align: right;
        }
    }
</style>


<!-- #### Operations with units -->

In general, units behave as one might expect.
Units are implemented using the library [Pint][pint]; please
see its documentation for more information.
The following is the formal definition of the operations
involving units.

[pint]: http://pint.readthedocs.org/


Units in Pint form a [group][group].
Call this group of units $U$ and its elements $u, v, \dots \in U$.
By $\mathbb{F}^{[u]}$, we mean a field $\mathbb{F}$
enriched with an annotation of units $u\in U$.

 with an equivalence relation.
[group]: https://en.wikipedia.org/wiki/Group_(mathematics)#Definition


Multiplication is defined for all pairs of units. Let $|x|$ denote the absolute
numerical value of $x$ (stripping the unit away). Then, if $x \in
\mathbb{F}^{[u]}$  and $y \in \mathbb{F}^{[v]}$, their product is $x\cdot y \in
\mathbb{F}^{[uv]} $ and $|x\cdot y| = |x|\cdot|y|$.

Addition is defined only for compatible pairs of units (e.g., <poset>m</poset> and
<poset>km</poset>), but it is not possible to sum, say, <poset>m</poset> and
<poset>s</poset>. If $x \in \mathbb{F}^{[u]}$  and $y \in \mathbb{F}^{[v]}$, then $x +
y \in \mathbb{F}^{[u]} $, and $ x + y = |x| + \alpha^u_v |y| $, where
$\alpha^u_v$ is a table of conversion factors, and $|x|$ is the absolute
numerical value of $x$.


In practice, this means that MCDPL thinks that <value>1 kg + 1 g</value> is equal to
<value>1.001 kg</value>. Addition is not strictly commutative, because <value>1 g + 1
kg</value> is equal to <value>1001 g</value>, which is equivalent, but not equal, to
<value>1.001 kg</value>.



### Defining custom posets <k>poset</k>

It is possible to define custom finite posets using the keyword
<q><k>poset</k></q>.

For example, suppose that we create a file named <q>`MyPoset.mcdp_poset`</q>
containing the definition in [](#code:MyPoset). This declaration defines a poset
with 5 elements `a`, `b`, `c`, `d`, `e` and with the given order relations, as
displayed in [](#fig:MyPosetHasse).


<col2>
    <pre class='mcdp_poset' id='MyPoset' label='MyPoset.mcdp_poset'
         figure-id='code:MyPoset'
         figure-caption='Definition of a custom poset'
         ></pre>
    <!-- poset {
        a b c d e&#32;&#32;&#32;&#32;&#32;&#32;&#32;

        a ≼ b
        c ≼ d
        e ≼ d
        e ≼ b
    }
    </pre> -->
    <render class='hasse' figure-id="fig:MyPosetHasse">`MyPoset</render>
</col2>

The name of the poset, `MyPoset`, comes from the filename `MyPoset.mcdp_poset`.
After the poset has been defined, it can be used in the definition of an MCDP,
by referring to it by name using the backtick notation, as in
<q><poset>`MyPoset</poset></q>.

To refer to its elements, use the notation <value>`MyPoset: element</value>
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

MCDPL allows the definition of finite Cartesian products ([](#def:posets-cartesian-product)).

Use the Unicode symbol "<k>×</k>" or the simple letter "<k>x</k>" to
create a poset product, using the syntax:


<col2>
    <pre class='mcdp_poset'>
    [["poset"]] × [["poset"]] × [["..."]] × [["poset"]]
    </pre>

    <pre class='mcdp_poset'>
    [["poset"]] x [["poset"]] x [["..."]] x [["poset"]]
    </pre>
</col2>

For example, the expression <poset>J × A</poset> represents a product of Joules and
Amperes.

The elements of a poset product are called "tuples". These correspond exactly to
[Python's tuples][tuples]. To define a tuple, use angular brackets
<q><code>&lt;</code></q> and <q><code>&gt;</code></q>. The syntax is:

<center>
    <pre class='mcdp_value' np>
    &lt;[[value]], [[value]], [["..."]], [[value]]&gt;
    </pre>
</center>

For example, the expression <q><value>&lt;2 J, 1 A&gt;</value></q> denotes a tuple
with two elements, equal to <value>2 J</value> and <value>2 A</value>. An alternative
syntax uses the fancy Unicode brackets <q>&#x3008;</q> and <q>&#x3009;</q>, as
in <q><value>⟨0 J, 1 A⟩</value></q>.

[tuples]: https://docs.python.org/3/tutorial/datastructures.html#tuples-and-sequences


Tuples can be nested. For example, you can describe a tuple like <value np>⟨ ⟨0 J,
1 A⟩, ⟨1 m, 1 s, 42⟩ ⟩</value>, and its poset is denoted as <code>(</code><poset np="1">(J × A) × (m × s × Nat)</poset><code>)</code>.


### Named Poset Products <k>product</k>

MCDPL also supports "named products". These are semantically equivalent to
products, however, there is also a name associated to each entry. This allows to
easily refer to the elements. For example, the following declares a product of
the two spaces <poset>J</poset> and <poset>A</poset> with the two entries named
``energy`` and ``current``.

<center>
    <pre class='mcdp_poset'>
    product(energy:J, current:A)
    </pre>
</center>

The names for the fields must be valid identifiers (starts with a letter,
contains letters, underscore, and numbers).

### Power sets <k>set-of</k> <k>℘</k>   {#syntax-powerset}

MCDPL allows to describe the set of subsets of a poset, i.e. its power
set ([](#def:powerset)).

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

<center>
<pre class='mcdp_value'>
{ [[value]], [[value]], [["..."]], [[value]]}
</pre>
</center>

For example, the value <value>{1,2,3}</value>
is an element of the poset <poset>℘(Nat)</poset>.

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
upper sets for the natural numbers.

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

For example: <value>↑ {&lt;2 g, 1 m&gt;}</value> denotes the principal upper set of
the element <value>{2 g, 1 m}</value> in the poset <poset>g x m</poset>.
