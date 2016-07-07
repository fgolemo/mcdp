
## Describing Monotone Co-Design Problems (MCDPs)

The simplest MCDP can be defined as:

<pre class='mcdp'>
mcdp {
	
}
</pre>

That is an empty MCDP - no functionality or resources.
 

The interface of an MCDP is defined using
the ``provides`` and ``requires`` keywords:

<pre class='mcdp' id='model1'>
mcdp {
	provides capacity [J]
	requires mass [g]

	# ...
}
</pre>

This defines a DP with one functionality, ``capacity``, measured in joules, 
and one resource, ``mass``, measured in grams. 

Graphically, this is how the interface is represented:

<pre class='ndp_graph_templatized'>`model1</pre>

<!--
The MCDP defined above is, however, unusable, because we have 
not specified how ``capacity`` and ``mass`` relate to one another.
Graphically, this is represented using purple unconnected arrows:

<pre class='ndp_graph_expand'>`model1</pre>
-->

### Constant functionality and resources

The following is a minimal example of a complete MCDP.
We have given hard bounds to both ``capacity`` and ``mass``.

<table><tr><td>
<pre class='mcdp' id='model2'>
mcdp {
	provides capacity [J]
	requires mass [g]

	capacity <= 500 J
	mass >= 100g
}
</pre>
</td><td>
<pre class='ndp_graph_expand'>`model2</pre>
</td></tr></table>

### Describing relations between functionality and resources

Functionality and resources can depend on each other
using any monotone relations. 

For example, we can describe a linear relation between
mass and capacity, given by the specific energy.

<pre class='mcdp' id='model4'>
mcdp {
	provides capacity [J]
	requires mass [g]

	specific_energy = 4 J / g
	required mass >= provided capacity / specific_energy
}
</pre>

<pre class='ndp_graph_expand'>`model4</pre>

### Units

PyMCDP is picky about units, but generally very helpful.
As long as the units have the right dimensionality,
it will insert the appropriate conversions.

For example, this is the same example with the specific
energy given in kWh/kg.

<pre class='mcdp' id='model5'>
mcdp {
	provides capacity [J]
	requires mass [g]

	specific_energy = 200 kWh / kg
	required mass >= provided capacity / specific_energy
}
</pre>

<pre class='ndp_graph_expand'>`model5</pre>
 