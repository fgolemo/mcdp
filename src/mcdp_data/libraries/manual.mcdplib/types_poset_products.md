### Poset Products

Use the Unicode symbol "``×``" or the simple letter ``x`` to create a poset product.

The syntax is

<pre>
<em>space</em> × <em>space</em> × &hellip; × <em>space</em>
</pre>

For example:

<pre class='mcdp_poset'>
J × A
</pre>

This represents a product of Joules and Amperes.


### Tuple making

To create a tuple, use angular brackets.

The syntax is:

<pre>
&lt; <em>element</em>, <em>element</em>, &hellip; &gt;
⟨ <em>element</em>, <em>element</em>, &hellip; ⟩
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

<pre>
<strong>take</strong>(<em>value</em>, <em>index</em>)
</pre>

For example:

<pre class='mcdp'>
mcdp {
    provides out [ J x A ]

    take(out, 0) <= 10 J
    take(out, 1) <= 2 A
}
</pre>

This is equivalent to

<pre class='mcdp'>
mcdp {
    provides out [ J x A ]

    out <= <10 J, 2 A>
}
</pre>


### Named Poset Products  

PyMCDP also supports named products, in which each entry in the tuple
is associated to a name. For example, the following declares
a product of the two spaces <code class='mcdp_poset'>J</code>
and <code class='mcdp_poset'>A</code> with the two entries
named ``energy`` and ``current``.

<pre class='mcdp_poset'>
product(energy:J, current:A)
</pre>

Then it is possible to index those entries using one of these two syntaxes:

<pre>
<strong>take</strong>(<em>value</em>, <em>label</em>)
(<em>value</em>).<em>label</em>
</pre>

For example:

<pre class='mcdp'>
mcdp {
    provides out [ product(energy:J, current:A) ]

    (out).energy <= 10 J
    (out).current <= 2 A
}
</pre>
