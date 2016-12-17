### Poset Products

Use the Unicode symbol "``×``" or the simple letter ``x`` to create a poset product.

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
