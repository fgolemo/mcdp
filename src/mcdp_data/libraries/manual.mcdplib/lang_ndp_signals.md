you can use
## Signals

### Available math operators

These are the available operators:

<table>
    <tr><td><k>ceil</k></td></tr>
    <tr><td><k>floor</k></td></tr>
    <tr><td><k>floor0</k></td></tr>
    <tr><td><k>sqrt</k></td></tr>
    <tr><td><k>pow</k></td></tr>
    <tr><td><k>max</k></td></tr>
    <tr><td><k>min</k></td></tr>
</table>

These are not ``functions``; rather, they are __relations__.

For example, a statement of the kind:

<pre class='mcdp_statements'>
    a >= sqrt(b)
</pre>

In fact, it is different than:

<pre class='mcdp_statements'>
    sqrt(a) >= b
</pre>

#### <k>pow</k>, <k>sqrt</k>

#### <k>min</k>, <k>max</k>

#### <k>floor</k>, <k>floor0</k>, <k>ceil</k>



<!-- Also: ``square`` -->

### <k>approx</k>

    approx()

### <k>approxu</k>

    approxu()

### Accessing elements of a product

To access the elements of a tuple, use the syntax

<pre class='mcdp_value'>
take([[signal]], [[index]])
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

### Accessing elements of a named product by name

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
