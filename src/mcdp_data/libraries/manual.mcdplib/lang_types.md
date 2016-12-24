## Posets and their values

All values of <f>functionality</f> and <r>resources</r> belong to posets.
PyMCDP knows a few built-in posets, and gives you the possibility of creating your own.

\tabref{summary_posets} shows the basic posets that are built in:
natural numbers, nonnegative real numbers, and nonnegative real numbers
that have units associated to them.

<table figure-id="tab:summary_posets" figure-caption="Build-in posets">
    <tr>
        <td>MCDPL poset</td><td>ideal poset</td><td>Python object</td>
    </tr>

    <tr>
        <td>
            <pos np>Nat</pos>
        </td><td>
            $\langle\mathbb{N} \cup \top, \leq\rangle$
        </td><td>
            <code>int</code> plus <code>Top</code>
        </td>
    </tr>

    <tr>
        <td>
            <pos np>Rcomp</pos>
        </td><td>
             $\langle{\mathbb{R}}_+ \cup \top, \leq\rangle$
        </td><td>
            <code>float</code> plus a special <code>Top</code> object
        </td>
    </tr>
    <tr>
        <td>
            <pos np>g</pos>
        </td>
        <td>
            $\langle\overline{\mathbb{R}}^{[\text{g}]}_+, \leq\rangle$
        </td>
        <td>
            <code>float</code> plus a special <code>Top</code> object
        </td>
    </tr>
</table>

<style type='text/css'>
#tab\:summary_posets tr:first-child {
    font-weight: bold;
}
</style>

### Natural numbers <pos np>Nat</pos> <pos>Nat</pos>

By $\overline{\mathbb{N}}$ we mean the completion of  $\mathbb{N}$ to include a top element $\top$. This makes the poset a [complete partial order](#def:cpo)
([](#def:cpo)).


The natural numbers with completion are expressed as <pos np>Nat</pos>
or with the Unicode letter "<pos>Nat</pos>".

Their values using the syntax <val np>Nat:42</val>
or simply <val>42</val>.

Internally, $\mathbb{N}$ is represented by the [Python type `int`][int], which
is equivalent to the 32 bits `signed long` type in C. So, it is really
a chain of $2^{31} + 1$ elements.

[int]: https://docs.python.org/2/library/stdtypes.html#numeric-types-int-float-long-complex

### Nonnegative floating point numbers <pos np>Rcomp</pos> <pos>Rcomp</pos>  {#sub:Rcomp}

Let $\reals_{+}\{x \mid x \geq 0\}$ be the nonnegative real numbers  and let $\overline{\reals}_{+} = \reals \cup \top$ be its completion.

Floating point with completion are indicated by <pos>Rcomp</pos>
or <pos np>Rcomp</pos>, and their values as <val>Rcomp:42.0</val> or simply <val>42.0</val>.

Internally, ${\Rcomp}_{+}$ is approximated using double precision
point numbers ([IEEE 754]), corresponding to the <code>float</code> type used by Python and the `double` type in C (in most implementations of C).

[IEEE 754]: https://en.wikipedia.org/wiki/IEEE_floating_point


The $+$ and $\times$ operations are extended from $\reals$ to $\Rcomp$
by defining the following:

\begin{eqnarray}
    \forall a:& \quad a + \top &= \top \\
    \forall a:& \quad a \times \top &= \top
\end{eqnarray}

Of course, the floating point implementations of $+$ and $\times$
are also not associative or commutative due to rounding errors.
PyMCDP does not assume  commutativity or associativity; the assumption
is just that they are [monotone](#def:monotone-function) in each
argument (which they are).


### Nonnegative floating point numbers with units

Floating point numbers can also have **units** associated to them.
So we can distinguish $\reals^{[\text{m}]}$ from $\reals^{[\text{s}]}$
and even $\reals^{[\text{m}]}$  from $\reals^{[\text{km}]}$.

These posets are indicated using the following syntax:

<quote markdown="1" style='padding-left: 3em'>
    <pos>g</pos>,
    <pos>J</pos>,
    <pos>m</pos>,
    <pos>s</pos>,
    <pos>m/s</pos>,
     &hellip;
</quote>

Their values are indicated as follows:

<quote markdown="1" style='padding-left: 3em'>
    <val>1.2 g</val>,
    <val>20 J</val>,
    <val>10 m</val>,
    <val>10 s</val>,
    <val>23 m/s</val>,
     &hellip;
</quote>

#### Operations with units

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


Multiplication is defined for all pairs of units. If $x \in \mathbb{F}^{[u]}$  and $y \in \mathbb{F}^{[v]}$, then $x\cdot y \in \mathbb{F}^{[uv]} $.

Addition is defined only for compatible pairs of units (e.g., <pos>m</pos> and <pos>km</pos>),
     but it is not possible to sum, say, <pos>m</pos>
     and <pos>s</pos>.

If $x \in \mathbb{F}^{[u]}$  and $y \in \mathbb{F}^{[v]}$,
    then $x + y \in \mathbb{F}^{[u]} $, and
    $ x + y = |x| + \alpha^u_v |y| $, where
     $\alpha^u_v$ is a table of conversion factors, and $|x|$ is
     the absolute numerical value of $x$.


In practice, this means that MCDPL thinks that <val>1 kg + 1 g</val> is equal to <val>1.001 kg</val>. Addition is not strictly commutative, because <val>1 g + 1 kg</val> is equal to <val>1001 g</val>, which is equivalent, but not equal, to <val>1.001 kg</val>.



### Defining custom posets <k>poset</k>

It is possible to define custom finite posets
using the keyword <k>poset</k>.

For example, supposes that we create a file named `my_poset.mcdp_poset`
containing the definition in \coderef{my_poset}.

<pre class='mcdp_poset' id='my_poset' label='my_poset.mcdp_poset'
     figure-id='code:my_poset' figure-caption='Definition of a custom poset'>
poset {
    a ≼ b
    c ≼ d
    c ≼ d
}
</pre>

This declaration defines a poset with 5 elements `a`, `b`, `c`, `d`, `e` and with the given order relations, as displayed in [](#fig:my_poset_hasse).

<render class='hasse' id='my_poset' figure-id="fig:my_poset_hasse"></render>

The name of the poset, `my_poset`, comes from the filename `my_poset.mcdp_poset`.
After the poset has been defined, it can be used in the
definition of an MCDP, by referring to it by name using
the backtick notation, as in &ldquo;<pos>`my_poset</pos>&rdquo;.

To refer to its elements, use the notation <val>`my_poset: element</val> ([](#code:one)).

<col2>
    <pre class='mcdp' id='one' figure-id='code:one'
    figure-caption='Referring to an element of a custom poset'>
mcdp {
    provides f [&#96;my_poset]

    provided f ≼ &#96;my_poset : c
}
    </pre>

    <render class='ndp_graph_enclosed'>&#96;one</render>
</col2>


### Poset products <k>×</k>

MCDPL allows the definition of finite cartesian products.

\begin{defn}[Product of posets]\label{def:product-posets}
For two posets $P,Q$, the Cartesian product $P\times Q$
is the set of pairs $\langle p, q \rangle$ for $p\in P$ and $q \in Q$.
The order is the following:
$$
    \langle p_1, q_1 \rangle \posleq \langle p_2, q_2 \rangle
    \quad \equiv \quad
    (p_1 \posleq_P p_2) \wedge (q_1 \posleq_P q_2).
$$
\end{defn}

In MCDPL, use the Unicode symbol "<k>×</k>" or the simple letter "<k>x</k>" to create a poset product, using the syntax:


<col2>
    <pre class='mcdp_poset'>
    [["poset"]] × [["poset"]] × [["..."]] × [["poset"]]
    </pre>

    <pre class='mcdp_poset'>
    [["poset"]] x [["poset"]] x [["..."]] x [["poset"]]
    </pre>
</col2>

For example, the expression <pos>J × A</pos> represents a product of Joules and Amperes.

The elements of a poset product are called "tuples". These correspond
exactly to [Python's tuples][tuples].
To define a tuple, use angular brackets &ldquo;<code>&lt;</code>&rdquo; and &ldquo;<code>&gt;</code>&rdquo;. The syntax is:

<pre class='mcdp_value' np>
&lt;[[value]], [[value]], [["..."]], [[value]]&gt;
</pre>

For example, the expression <val>&lt;2 J, 1 A&gt;</val>
denotes a tuple with two elements, equal to <val>2 J</val>
and <code class='mcdp_value'>2 A</code>.
An alternative syntax uses the fancy Unicode brackets &ldquo;&#x3008;&rdquo; and &ldquo;&#x3009;&rdquo;, as in <val>⟨0 J, 1 A⟩</val>.

[tuples]: https://docs.python.org/3/tutorial/datastructures.html#tuples-and-sequences


Tuples can be nested. For example, you can describe a tuple like
 <val np>⟨ ⟨0 J, 1 A⟩, ⟨1 m, 1 s, 42⟩ ⟩</val>,
and its poset is denoted as <code>(</code><pos np>(J × A) × (m × s × Nat)</pos><code>)</code>.


### Named Poset Products <k>product</k>

MCDPL also supports "named products". These are semantically equivalent
to products, however, there is also a name associated to each entry. This allows to easily refer to the elements.For example, the following declares
a product of the two spaces <pos>J</pos>
and <pos>A</pos> with the two entries
named ``energy`` and ``current``.

<pre class='mcdp_poset'>
product(energy:J, current:A)
</pre>

The names for the fields must be valid identifiers (starts with a letter,
contains letters, underscore, and numbers).

### Power sets <k>set-of</k> <k>℘</k>

MCDPL allows to describe the set of subsets of a poset, i.e.
its [power set][powerset].
The power set $\pset(Q)$ of a poset $Q$ is a poset with
the order given by inclusion:
$$
    a \posleq_{\pset{Q}} b
    \quad \equiv \quad
    a \subseteq b.
$$
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

### Upper and lower sets and closures <k>UpperSets</k> <k>LowerSets</k> <k>upperclosure</k> <k>↑</k> <k>lowerclosure</k> <k>↓</k>

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

For example:

<pre class='mcdp_poset'>
UpperSets(V)
</pre>

To describe an upper set, use the keyword <k>upperclosure</k>
or its abbreviation <k>↑</k>. The syntax is:

<col2>
<pre class='mcdp_value'>
upperclosure [[ set ]]
</pre>

<pre class='mcdp_value'>
↑ [[ set ]]
</pre>
</col2>

For example:
<pre class='mcdp_value'>
↑ {2 g, 1 m}
</pre>
denotes the principal upper set of the element
<val>{2 g, 1 m}</val> in the poset <pos>g x m</pos>.


### Interval (experimental)

The syntax is

<pre class='mcdp_poset'>
Interval([["lower bound"]], [["upper bound"]])
</pre>

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

For example, assume that the poset <k>MyPoset</k> is defined as
in \coderef{MyPoset}:


<col2>
        <pre class='mcdp_poset' id='MyPoset' label='MyPoset.mcdp_poset'
            figure-id='code:MyPoset'>
            poset {
                a ≼ b
                a ≼ c
                d ≼ c
            }
        </pre>
        <render class='hasse'>&#96;MyPoset</render>
</col2>


Then <val>Maximals &#96;MyPoset</val> is equivalent
to <val>{&#96;MyPoset:b, &#96;MyPoset:c}</val>
and  <val>Minimals &#96;MyPoset</val> is equivalent
to <val>{&#96;MyPoset:a, &#96;MyPoset:d}</val>.

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
