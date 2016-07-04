Finite Posets
-------------


You can define your own posets.

For example, create a file named ``my_poset.mcdp_poset``
containing the following definition:

<pre class='mcdp_poset' id='my_poset' label='my_poset.mcdp_poset' style=''>
finite_poset {
	a <= b <= c
	c <= d
	c <= e	
}
</pre>

This defines a poset with 5 elements ``a``, ``b``, ``c``, ``d``, ``e``
and with the given order relations.

Now that this poset has been defined, it can be used in the 
definition of an MCDP, by referring to it by name using
the backtick notation ```my_poset``.

To refer to its element, use the notation ```my_poset: element``.

For example:

<table><tr><td>
	<pre class='mcdp' id='one'>
mcdp {
	provides f [`my_poset]

	f <= `my_poset : c
}
	</pre>
</td><td>
	<pre class='ndp_graph_enclosed'>`one</pre>
</td></tr></table>

