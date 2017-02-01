
## Other ways to specify values


### Top and bottom <k>Top</k> <k>Bottom</k>

To indicate top and bottom of a poset, use the syntax:

<col2>
        <value np>Top [["poset"]]</value>
        <value>⊤ [["poset"]]</value>
        <value np>Bottom [["poset"]]</value>
        <value>⊥ [["poset"]]</value>
</col2>

For example, <q><value>Top V</value></q> indicates the top of the <poset>V</poset>.


### Minimals and maximals  <k>Minimals</k> <k>Maximals</k>

The expressions <value>Minimals [["poset"]]</value>
and <value>Maximals [["poset"]]</value>
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
[](#fig:hasse2). Then <value>Maximals &#96;MyPoset</value> is equivalent to `b` and
`d`, and <value>Minimals &#96;MyPoset</value> is equivalent to `a`, `e`, `c`.

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
<value>EmptySet J</value> is an empty set of energies,
and <value>EmptySet V</value> is an empty set of voltages,
and the two are not equivalent.

<!-- or

<pre class='mcdp_value'>
ø [[space]]
</pre> -->
