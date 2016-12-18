## Describing posets

All values belong to posets.

PyMCDP knows a few built-in posets, and gives you the possibility of creating your own.

<p class=todo>Add diagram with type system</p>

### Natural numbers <mcdp-poset np>Nat</mcdp-poset>

The natural numbers with a completion are expressed as <mcdp-poset np>Nat</mcdp-poset>
and their values using the syntax <mcdp-value np>Nat:42</mcdp-value>.

Alterntively, you can use <mcdp-poset>Nat</mcdp-poset> instead of <mcdp-poset np>Nat</mcdp-poset>.

### Positive floating point numbers

Floating point with completion are indicated by <mcdp-poset>Rcomp</mcdp-poset>,
and their values as <mcdp-value>42.0</mcdp-value>.

### Positive floating point numbers with units

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
    <mcdp-value>10 g</mcdp-value>,
    <mcdp-value>20 J</mcdp-value>,
    <mcdp-value>10 m</mcdp-value>,
    <mcdp-value>10 s</mcdp-value>,
    <mcdp-value>23 m/s</mcdp-value>,
     &hellip;
</quote>


### Finite Posets <k>poset</k>

It is possible to define and use your own arbitrary finite posets.

For example, create a file named ``my_poset.mcdp_poset``
containing the following definition:

<pre class='mcdp_poset' id='my_poset' label='my_poset.mcdp_poset' style=''>
poset {
    a ≼ b
	c ≼ d
	c ≼ e
}
</pre>

This defines a poset with 5 elements ``a``, ``b``, ``c``, ``d``, ``e``
and with the given order relations.

<render class='hasse' id='my_poset'/>

Now that this poset has been defined, it can be used in the
definition of an MCDP, by referring to it by name using
the backtick notation, as in  &ldquo;<mcdp-poset>`my_poset</mcdp-poset>&rdquo;.

To refer to its elements, use the notation <mcdp-value>`my_poset: element</mcdp-value>.

For example:

<table><tr><td>
	<pre class='mcdp' id='one'>
mcdp {
	provides f [`my_poset]

	provided f ≼ `my_poset : c
}
	</pre>
</td><td>
	<render class='ndp_graph_enclosed'>`one</render>
</td></tr></table>


### Poset Products

Use the Unicode symbol "<k>×</k>" or the simple letter "<k>x</k>" to create a poset product.

The syntax is

<pre class='mcdp_poset'>
[[space]] × [[space]] × [["..."]] × [[space]]
</pre>


For example:

<pre class='mcdp_poset'>
J × A
</pre>

This represents a product of Joules and Amperes.


### Tuple making

To create a tuple, use angular brackets.

The syntax is:


<pre class='mcdp_value'>
&lt;[[element]], [[element]], [["..."]], [[element]]&gt;
</pre>


An example using regular brackets:

<pre class='mcdp_value'>
&lt;0 J, 1 A&gt;
</pre>

An example using fancy unicode brackets:

<pre class='mcdp_value'>
⟨0 J, 1 A⟩
</pre>


### Tuple accessing

To access the elements of the tuple, use the syntax

<pre class='mcdp_value'>
take([[value]], [[index]])
</pre>

For example:

<pre class='mcdp'>
mcdp {
    provides out [ J x A ]

    take(provided out, 0) ≼ 10 J
    take(provided out, 1) ≼ 2 A
}
</pre>

This is equivalent to

<pre class='mcdp'>
mcdp {
    provides out [ J x A ]

    provided out ≼ &lt;10 J, 2 A&gt;
}
</pre>


### Named Poset Products - <k>product</k>

PyMCDP also supports named products, in which each entry in the tuple
is associated to a name. For example, the following declares
a product of the two spaces <mcdp-poset>J</mcdp-poset>
and <mcdp-poset>A</mcdp-poset> with the two entries
named ``energy`` and ``current``.

<pre class='mcdp_poset'>
product(energy:J, current:A)
</pre>

Then it is possible to index those entries using one of these two syntaxes:

<pre class='mcdp_rvalue'>
take([[resource]], [[label]])
</pre>

<pre class='mcdp_fvalue'>
take([[functionality]], [[label]])
</pre>


<pre class='mcdp_rvalue'>
([[resource]]).[[label]]
</pre>

<pre class='mcdp_fvalue'>
([[resource]]).[[label]]
</pre>


For example:

<pre class='mcdp'>
mcdp {
    provides out [ product(energy:J, current:A) ]

    (provided out).energy ≼ 10 J
    (provided out).current ≼ 2 A
}
</pre>



### <k>set-of</k> <k>℘</k>

<pre class='mcdp_poset ex1'>
℘(V)
</pre>

<pre class='mcdp_poset ex1'>
set-of(V)
</pre>

### <k>UpperSets</k>, <k>LowerSets</k>

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

### Interval [experimental]

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

### Singletons [experimental]

    S(tag)

    S(tag):*
