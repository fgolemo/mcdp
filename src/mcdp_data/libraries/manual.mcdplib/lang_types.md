## Posets and their values

All values of <f>functionality</f> and <r>resources</r> belong to posets.
PyMCDP knows a few built-in posets, and gives you the possibility of creating your own.

\tabref{summary_posets} shows the basic posets that are built in:
natural numbers, nonnegative real numbers, and nonnegative real numbers
that have units associated to them.


\begin{table} \caption{Built-in posets\label{tab:summary_posets}}
\begin{tabular}{ccc}
    MCDPL poset & ideal poset & Python object \\
    <mcdp-poset np>Nat</mcdp-poset> & $\langle\mathbb{N} \cup \top, \leq\rangle$ & <code>int</code> plus <code>Top</code>  \\

    <mcdp-poset np>Rcomp</mcdp-poset> & $\langle{\mathbb{R}}_+ \cup \top, \leq\rangle$ & <code>float</code> plus a special <code>Top</code> object \\

    <mcdp-poset np>g</mcdp-poset> &
     $\langle\overline{\mathbb{R}}^{[\text{g}]}_+, \leq\rangle$ &
     <code>float</code> plus a special <code>Top</code> object
\end{tabular}
\end{table}

<style type='text/css'>
#tab\:summary_posets tr:first-child {
    font-weight: bold;
}
</style>

### Natural numbers <mcdp-poset np>Nat</mcdp-poset> <mcdp-poset>Nat</mcdp-poset>

By $\overline{\mathbb{N}}$ we mean the completion of  $\mathbb{N}$ to include a top element $\top$. This makes the poset a [complete partial order](#def:cpo)
([](#def:cpo)).


The natural numbers with completion are expressed as <mcdp-poset np>Nat</mcdp-poset>
or with the Unicode letter "<mcdp-poset>Nat</mcdp-poset>".

Their values using the syntax <mcdp-value np>Nat:42</mcdp-value>
or simply <mcdp-value>42</mcdp-value>.

Internally, $\mathbb{N}$ is represented by the [Python type `int`][int], which
is equivalent to the 32 bits `signed long` type in C. So, it is really
a chain of $2^{31} + 1$ elements.

[int]: https://docs.python.org/2/library/stdtypes.html#numeric-types-int-float-long-complex

### Nonnegative floating point numbers <mcdp-poset np>Rcomp</mcdp-poset> <mcdp-poset>Rcomp</mcdp-poset>

Let $\reals_{+}\{x \mid x \geq 0\}$ be the nonnegative real numbers  and let $\overline{\reals}_{+} = \reals \cup \top$ be its completion.

Floating point with completion are indicated by <mcdp-poset>Rcomp</mcdp-poset>
or <mcdp-poset np>Rcomp</mcdp-poset>, and their values as <mcdp-value>Rcomp:42.0</mcdp-value> or simply <mcdp-value>42.0</mcdp-value>.

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
    <mcdp-poset>g</mcdp-poset>,
    <mcdp-poset>J</mcdp-poset>,
    <mcdp-poset>m</mcdp-poset>,
    <mcdp-poset>s</mcdp-poset>,
    <mcdp-poset>m/s</mcdp-poset>,
     &hellip;
</quote>

Their values are indicated as follows:

<quote markdown="1" style='padding-left: 3em'>
    <mcdp-value>1.2 g</mcdp-value>,
    <mcdp-value>20 J</mcdp-value>,
    <mcdp-value>10 m</mcdp-value>,
    <mcdp-value>10 s</mcdp-value>,
    <mcdp-value>23 m/s</mcdp-value>,
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

Addition is defined only for compatible pairs of units (e.g., <mcdp-poset>m</mcdp-poset> and <mcdp-poset>km</mcdp-poset>),
     but it is not possible to sum, say, <mcdp-poset>m</mcdp-poset>
     and <mcdp-poset>s</mcdp-poset>.

If $x \in \mathbb{F}^{[u]}$  and $y \in \mathbb{F}^{[v]}$,
    then $x + y \in \mathbb{F}^{[u]} $, and
    $ x + y = |x| + \alpha^u_v |y| $, where
     $\alpha^u_v$ is a table of conversion factors, and $|x|$ is
     the absolute numerical value of $x$.


In practice, this means that MCDPL thinks that <mcdp-value>1 kg + 1 g</mcdp-value> is equal to <mcdp-value>1.001 kg</mcdp-value>. Addition is not strictly commutative, because <mcdp-value>1 g + 1 kg</mcdp-value> is equal to <mcdp-value>1001 g</mcdp-value>, which is equivalent, but not equal, to <mcdp-value>1.001 kg</mcdp-value>.



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
    c ≼ e
}
</pre>

This declaration defines a poset with 5 elements `a`, `b`, `c`, `d`, `e` and with the given order relations, as displayed in [](#fig:my_poset_hasse).

<render class='hasse' id='my_poset' figure-id="fig:my_poset_hasse"></render>

The name of the poset, `my_poset`, comes from the filename `my_poset.mcdp_poset`.
After the poset has been defined, it can be used in the
definition of an MCDP, by referring to it by name using
the backtick notation, as in &ldquo;<mcdp-poset>`my_poset</mcdp-poset>&rdquo;.

To refer to its elements, use the notation <mcdp-value>`my_poset: element</mcdp-value> ([](#code:one)).

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

For example, the expression <mcdp-poset>J × A</mcdp-poset> represents a product of Joules and Amperes.

The elements of a poset product are called "tuples". These correspond
exactly to [Python's tuples][tuples].
To define a tuple, use angular brackets &ldquo;<code>&lt;</code>&rdquo; and &ldquo;<code>&gt;</code>&rdquo;. The syntax is:

<pre class='mcdp_value' np>
&lt;[[value]], [[value]], [["..."]], [[value]]&gt;
</pre>

For example, the expression <mcdp-value>&lt;2 J, 1 A&gt;</mcdp-value>
denotes a tuple with two elements, equal to <mcdp-value>2 J</mcdp-value>
and <code class='mcdp_value'>2 A</code>.
An alternative syntax uses the fancy Unicode brackets &ldquo;&#x3008;&rdquo; and &ldquo;&#x3009;&rdquo;, as in <mcdp-value>⟨0 J, 1 A⟩</mcdp-value>.

[tuples]: https://docs.python.org/3/tutorial/datastructures.html#tuples-and-sequences


Tuples can be nested. For example, you can describe a tuple like
 <mcdp-value np>⟨ ⟨0 J, 1 A⟩, ⟨1 m, 1 s, 42⟩ ⟩</mcdp-value>,
and its poset is denoted as <code>(</code><mcdp-poset np>(J × A) × (m × s × Nat)</mcdp-poset><code>)</code>.


### Named Poset Products <k>product</k>

MCDPL also supports "named products". These are semantically equivalent
to products, however, there is also a name associated to each entry. This allows to easily refer to the elements.For example, the following declares
a product of the two spaces <mcdp-poset>J</mcdp-poset>
and <mcdp-poset>A</mcdp-poset> with the two entries
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

For example, the value <mcdp-value>{1,2,3}</mcdp-value>
is an element of the poset <mcdp-poset>℘(Nat)</mcdp-poset>.

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
<mcdp-value>{2 g, 1 m}</mcdp-value> in the poset <mcdp-poset>g x m</mcdp-poset>.


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

        <mcdp-value np>Top [["poset"]]</mcdp-value>

        <mcdp-value   >⊤ [["poset"]]</mcdp-value>
</col2>

<col2>
        <mcdp-value np>Bottom [["poset"]]</mcdp-value>

        <mcdp-value   >⊥ [["poset"]]</mcdp-value>
</col2>

For example, <mcdp-value>Top V</mcdp-value> indicates
the top of the <mcdp-poset>V</mcdp-poset>.

TODO: syntax <code>poset: Top</code>.


### Minimals and maximals  <k>Minimals</k> <k>Maximals</k>

The expressions <mcdp-value>Minimals [["poset"]]</mcdp-value>
and <mcdp-value>Maximals [["poset"]]</mcdp-value>
denote the set of minimal and maximal elements of a poset.

For example, assume that the poset <k>MyPoset</k> is defined as
in \coderef{MyPoset}:

<figure id='code:MyPoset'>
    <col2>
            <pre class='mcdp_poset' id='MyPoset' label='MyPoset.mcdp_poset'>
                poset {
                    a ≼ b
                    a ≼ c
                    d ≼ c
                }
            </pre>
            <render class='hasse'>&#96;MyPoset</render>
    </col2>
    <figcaption/>
</figure>

Then <mcdp-value>Maximals &#96;MyPoset</mcdp-value> is equivalent
to <mcdp-value>{&#96;MyPoset:b, &#96;MyPoset:c}</mcdp-value>
and  <mcdp-value>Minimals &#96;MyPoset</mcdp-value> is equivalent
to <mcdp-value>{&#96;MyPoset:a, &#96;MyPoset:d}</mcdp-value>.

### The empty set <k>EmptySet</k>

To denote the empty set, use the keyword <k>EmptySet</k>:

<pre class='mcdp_value'>
EmptySet [[poset]]
</pre>

Note that empty sets are typed---this is different from set theory.
<mcdp-value>EmptySet J</mcdp-value> is an empty set of energies,
and <mcdp-value>EmptySet V</mcdp-value> is an empty set of voltages,
and the two are not equivalent.

<!-- or

<pre class='mcdp_value'>
ø [[space]]
</pre> -->
