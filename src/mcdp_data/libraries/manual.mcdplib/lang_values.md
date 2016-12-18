
## Values


### <k>Top</k>, <k>Bottom</k>, <k>⊤</k>, <k>⊥</k>

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

### <k>Minimals</k>, <k>Maximals</k>

...

### Set-making syntax

The syntax is:


<pre class='mcdp_value'>
{[[element]], [[element]], [["..."]], [[element]]}
</pre>

For example:

<pre class='mcdp_value'>
{0 g, 1 g}
</pre>


To create an empty set:

<pre class='mcdp_value'>
EmptySet [[space]]
</pre>

<!-- or

<pre class='mcdp_value'>
ø [[space]]
</pre> -->


### <k>upperclosure</k>, <k>↑</k>, <k>lowerclosure</k>, <k>↓</k>

Using <k>upperclosure</k>

The syntax is:

<pre class='mcdp_value'>
upperclosure [[ set ]]
</pre>

<pre class='mcdp_value'>
lowerclosure [[ set ]]
</pre>


For example:

<pre class='mcdp_value'>
upperclosure {0 g, 1 g}
</pre>
