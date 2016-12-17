## Catalogues

We can also enumerate an arbitrary relation, as follows:

<pre class='mcdp' id='model3'>
catalogue {
	provides capacity [J]
	requires mass [g]

	500 kWh &lt;--| model1 |--&gt; 100 g
	600 kWh &lt;--| model2 |--&gt; 200 g
	700 kWh &lt;--| model3 |--&gt; 400 g
}
</pre>

<pre class='ndp_graph_expand'>`model3</pre>
