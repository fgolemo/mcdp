## Catalogues

We can also enumerate an arbitrary relation, as follows:

<pre class='mcdp' id='model3'>
catalogue {
	provides capacity [J]
	requires mass [g]

	500 kWh <--| model1 |--> 100 g
	600 kWh <--| model2 |--> 200 g
	700 kWh <--| model3 |--> 400 g
}
</pre>

<pre class='ndp_graph_expand'>`model3</pre>
