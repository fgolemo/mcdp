## Posets and their values

All values of <f>functionality</f> and <r>resources</r> belong to posets.
PyMCDP knows a few built-in posets, and gives you the possibility of creating your own.

\tabref{summary_posets} shows the basic posets that are built in:
natural numbers, nonnegative real numbers, and nonnegative real numbers
that have units associated to them

$\reals_+$ is the nonnegative real numbers $\{x \mid x \geq 0\}$.
By $\overline{\reals}_+$ and $\overline{\mathbb{N}}$ we
mean the completion of $\reals_+$ and $\mathbb{N}$ to include
a top element $\top$. This makes the posets a [complete partial order](#def:cpo)
([](#def:cpo)).

Note also that we will use $\reals$ to mean double-precision 64bits floating
point numbers ([IEEE 754]), which is the internal representation used by Python.
Similarly, $\mathbb{N}$ indicates the [Python type `int`][int], which
is equivalent to the 32bits `long` type.

[int]: https://docs.python.org/2/library/stdtypes.html#numeric-types-int-float-long-complex
[IEEE 754]: https://en.wikipedia.org/wiki/IEEE_floating_point


\begin{table} \caption{Built-in posets\label{tab:summary_posets}}
\begin{tabular}{ccc}
    MCDPL poset & ideal poset & Python object \\
    <mcdp-poset np>Nat</mcdp-poset> & $\langle\overline{\mathbb{N}}, \leq\rangle$ & <code>int</code> plus <code>Top</code>  \\

    <mcdp-poset np>Rcomp</mcdp-poset> & $\langle\overline{\mathbb{R}}_+, \leq\rangle$ & <code>float</code> plus a special <code>Top</code> object \\

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



<p class=todo>Add diagram with type system</p>

### Natural numbers <mcdp-poset np>Nat</mcdp-poset>/<mcdp-poset>Nat</mcdp-poset>

The natural numbers with a completion are expressed as <mcdp-poset np>Nat</mcdp-poset>
and their values using the syntax <mcdp-value np>Nat:42</mcdp-value>.

Alterntively, you can use the Unicode letter "<mcdp-poset>Nat</mcdp-poset>" in place of "<mcdp-poset np>Nat</mcdp-poset>".

### Positive floating point numbers <mcdp-poset np>Rcomp</mcdp-poset>/<mcdp-poset>Rcomp</mcdp-poset>

Floating point with completion are indicated by <mcdp-poset>Rcomp</mcdp-poset>
or <mcdp-poset np>Rcomp</mcdp-poset>, and their values as <mcdp-value>42.0</mcdp-value>.

### Numbers with units

Floating point with completion and **units**
are indicated using units, such as:

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

In general, units behave as one might expect.

Units are implemented using the library [Pint][pint]; please
see its documentation for more information.

[pint]: http://pint.readthedocs.org/

The following is the formal definition of the operations
involving units.

Units in Pint form a [group] with an equivalence relation.
Call this group of units $U$ and its elements $u, v, \dots$.
By $\mathbb{F}^{[u]}$ we mean a field $\mathbb{F}$
enriched with an annotation of units $u\in U$.

[group]: https://en.wikipedia.org/wiki/Group_(mathematics)#Definition


These are the operations which involve units:

* Multiplication: If $x \in \mathbb{F}^{[u]}$  and $y \in \mathbb{F}^{[v]}$,
  then $x\cdot y \in \mathbb{F}^{[uv]} $.

* Addition: If $x \in \mathbb{F}^{[u]}$  and $y \in \mathbb{F}^{[v]}$,
    then $x + y \in \mathbb{F}^{[u]} $, and
    $ x + y = |x| + \alpha^u_v |y| $, where
     $\alpha^u_v$ is a table of convertion factors, and $|x|$ is
     the absolute numerical value of $x$.

In practice, this means that MCDPL thinks that <mcdp-value>1 kg + 1g</mcdp-value> is equal to <mcdp-value>1.001 kg</mcdp-value>. Addition is not strictly commutative, because <mcdp-value>1 g + 1 kg</mcdp-value> is equal to <mcdp-value>1001 g</mcdp-value>, which is equivalent, but not equal, to <mcdp-value>1.001 kg</mcdp-value>.<footnote>
In general, PyMCDP does not assume that any of the operations
such as $+$, $\times$, $-$, $/$ on floating point numbers
are either commutative or associative (which are not); just that they are
[monotone](#def:monotone-function).</footnote>


### Defining finite posets <k>poset</k>

It is possible to define and use your own arbitrary finite posets
using the keyword <k>poset</k>.

For example, supposes that we create a file named `my_poset.mcdp_poset`
containing the definition (<a href="#code:my_poset").

<pre class='mcdp_poset' id='my_poset' label='my_poset.mcdp_poset'
     figure-id='code:my_poset' figure-caption='Definition of a custom poset <code>my_poset</code>'>
poset {
    a ≼ b
	c ≼ d
	c ≼ e
}
</pre>

This declaration defines a poset with 5 elements ``a``, ``b``, ``c``, ``d``, ``e``and with the given order relations ([](#fig:my_poset_hasse)).
The name of the poset, `my_poset`, comes from the filename `my_poset.mcdp_poset`.

<render class='hasse' id='my_poset' figure-id:"fig:my_poset_hasse"/>

After the poset has been defined, it can be used in the
definition of an MCDP, by referring to it by name using
the backtick notation, as in &ldquo;<mcdp-poset>`my_poset</mcdp-poset>&rdquo;.

To refer to its elements, use the notation <mcdp-value>`my_poset: element</mcdp-value> ([](#code:one)).

<table><tr><td>
	<pre class='mcdp' id='one' figure-id='code:one'
    figure-caption='Referring to an element of a custom poset'>
mcdp {
	provides f [&#96;my_poset]

	provided f ≼ &#96;my_poset : c
}
	</pre>
</td><td>
	<render class='ndp_graph_enclosed'>&#96;one</render>
</td></tr></table>


### Poset products

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

<pre class='mcdp_poset'>
[["poset"]] × [["poset"]] × [["..."]] × [["poset"]]
</pre>


For example, the expression <mcdp-poset>J × A</mcdp-poset> represents a product of Joules and Amperes.

The elements of a poset product are called "tuples". These correspond
exactly to [Python's tuples][tuples].

[tuples]: https://docs.python.org/3/tutorial/datastructures.html#tuples-and-sequences

To define a tuple, use angular brackets &ldquo;<code>&lt;</code>&rdquo; and &ldquo;<code>&gt;</code>&rdquo;. The syntax is:

<pre class='mcdp_value' np>
&lt;[[value]], [[value]], [["..."]], [[value]]&gt;
</pre>


For example, the expression <mcdp-value>&lt;2 J, 1 A&gt;</mcdp-value>
denotes a tuple with two elements, equal to <mcdp-value>2 J</mcdp-value>
and <code class='mcdp-value'>2 A</code>.

An alternative syntax uses the fancy Unicode brackets &ldquo;&#x3008;&rdquo; and &ldquo;&#x3009;&rdquo;, as in <mcdp-value>⟨0 J, 1 A⟩</mcdp-value>.

Tuples can be nested. For example, you can describe a tuple like
 <mcdp-value np>⟨ ⟨0 J, 1 A⟩, ⟨1 m, 1 s, 42⟩ ⟩</mcdp-value>,
and its poset is denoted as <code np>(J × A) × (m × s × Nat)</code>.

TODO: fix bug that makes the above bomb

### Named Poset Products - <k>product</k>

MCDPL also supports "named products". These are semantically equivalent
to products, however, there is also a name associated to each entry. This allows to easily refer to the elements.

For example, the following declares
a product of the two spaces <mcdp-poset>J</mcdp-poset>
and <mcdp-poset>A</mcdp-poset> with the two entries
named ``energy`` and ``current``.

<pre class='mcdp_poset'>
product(energy:J, current:A)
</pre>

The names for the fields must be valid identifiers (starts with a letter,
contains letters, underscore, and numbers).

### <k>set-of</k> <k>℘</k>

MCDPL allows to describe the set of subsets of a poset, i.e.
its [power set][powerset].

[powerset]: https://en.wikipedia.org/wiki/Power_set

<figure class='figure'>
    <img src='Hasse_diagram_of_powerset_of_3.svg' width='13em'/>
    <figcaption>I, KSmrq [GFDL (http://www.gnu.org/copyleft/fdl.html), CC-BY-SA-3.0 (http://creativecommons.org/licenses/by-sa/3.0/) or CC BY-SA 2.5 (http://creativecommons.org/licenses/by-sa/2.5)], via Wikimedia Commons</figcaption>
</figure>

The syntax is either of these:

<pre class='mcdp_poset ex1'>
℘([["poset"]])
</pre>

<pre class='mcdp_poset ex1'>
set-of([["poset"]])
</pre>

TODO: this syntax will be changed to <k>powersets</k>

To describe values in a powerset of P, i.e. subsets of P, use the
set-building notation

<mcdp-value>
{ [[value]], [[value]], [["..."]], [[value]]}
</mcdp-value>

For example, the value <mcdp-value>{1,2,3}</mcdp-value>
is an element of the poset <mcdp-poset>℘(Nat)</mcdp-poset>.

### <k>UpperSets</k>, <k>LowerSets</k>, <k>upperclosure</k>, <k>↑</k>, <k>lowerclosure</k>, <k>↓</k>

Upper sets ([](#def:upperset)) and lower sets ([](#def:lowerset))

The syntax is

<pre class='mcdp_poset'>
UpperSets([[poset]])
</pre>

<pre class='mcdp_poset'>
LowerSets([[poset]])
</pre>

For example:

<pre class='mcdp_poset'>
UpperSets(V)
</pre>

To describe an upper set, use the keyword <k>upperclosure</k>
or its abbreviation <k>↑</k>. The syntax is:

<pre class='mcdp_value'>
upperclosure [[ set ]]
</pre>

<pre class='mcdp_value'>
↑ [[ set ]]
</pre>


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


### <k>Top</k>, <k>Bottom</k>, <k>⊤</k>, <k>⊥</k>, <k>Minimals</k>, <k>Maximals</k>

The syntax is:


<pre class='mcdp_value' noprettify>
    Top [[space]]
</pre>

<pre class='mcdp_value'>
    ⊤ [[space]]
</pre>

<pre class='mcdp_value' noprettify>
    Bottom [[space]]
</pre>

<pre class='mcdp_value'>
    ⊥  [[space]]
</pre>

For example:

<pre class='mcdp_value' noprettify>
Top V
</pre>

<pre class='mcdp_value'>
⊤ V
</pre>


<pre class='mcdp_value' noprettify>
Bottom V
</pre>

<pre class='mcdp_value'>
⊥ V
</pre>

Equivalenty, the keywords <k>Minimals</k>, <k>Maximals</k>
allow to denote the set of minimal and maximal elements of a poset.

For example, assuming that the poset <k>MyPoset</k> is defined as follows:

<table class='col2'>
<tr><td>
<pre class='mcdp_poset' id='MyPoset' label='MyPoset.mcdp_poset'>
poset {
    a ≼ b
    a ≼ c
    d ≼ c
}
</pre></td><td>
<render class='hasse'>&#96;MyPoset</render>
</td></tr>
</table>

Then <mcdp-value>Maximals &#96;MyPoset</mcdp-value> is equivalent
to <mcdp-value>{&#96;MyPoset:b, &#96;MyPoset:c}</mcdp-value>
and  <mcdp-value>Minimals &#96;MyPoset</mcdp-value> is equivalent
to <mcdp-value>{&#96;MyPoset:a, &#96;MyPoset:d}</mcdp-value>.

### Empty set

To denote the empty set, use the keyword <k>EmptySet</k>:

<pre class='mcdp_value'>
EmptySet [[space]]
</pre>

Note that empty sets are typed---this is different from set theory.
<mcdp-value>EmptySet J</mcdp-value> is an empty set of energies,
and <mcdp-value>EmptySet V</mcdp-value> is an empty set of voltages,
and the two are not equivalent.

<!-- or

<pre class='mcdp_value'>
ø [[space]]
</pre> -->
