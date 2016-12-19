
## Describing MCDPs

MCDP = Monotone Co-Design Problems...

The simplest MCDP can be defined as:

<pre class='mcdp'>
mcdp {

}
</pre>

That is an empty MCDP - it has no functionality or resources.


The interface of an MCDP is defined using
the keywords ``provides`` and ``requires``:

<pre class='mcdp' id='model1'>
mcdp {
	provides capacity [J]
	requires mass [g]

	# ...
}
</pre>

The code above defines an MCDP with one functionality, ``capacity``, measured in joules,
and one resource, ``mass``, measured in grams. ([See how to describe types.](types.html))

Graphically, this is how the interface is represented:

<render class='ndp_graph_templatized'>`model1</render>

<!--
The MCDP defined above is, however, unusable, because we have
not specified how ``capacity`` and ``mass`` relate to one another.
Graphically, this is represented using purple unconnected arrows:

<pre class='ndp_graph_expand'>`model1</pre>
-->

### Constant functionality and resources

The following is a minimal example of a complete MCDP.
We have given hard bounds to both ``capacity`` and ``mass``.

<table class="col2">
	<tr>
	<td>
	<pre class='mcdp' id='model2'>
	mcdp {
		provides capacity [J]
		requires mass [g]

		provided capacity ≼ 500 J
		required mass ≽ 100g
	}
	</pre>
	</td><td>
		<render class='ndp_graph_enclosed'>`model2</render>
	</td></tr>
</table>

### Describing relations between functionality and resources

Functionality and resources can depend on each other
using any monotone relations.

For example, we can describe a linear relation between
mass and capacity, given by the specific energy.


<table class="col2">
	<tr><td>
		<pre class='mcdp' id='model4'>
		mcdp {
			provides capacity [J]
			requires mass [g]

			# specific energy
			ρ = 4 J / g
			required mass ≽ provided capacity / ρ
		}
		</pre>
	</td><td>
		<render class='ndp_graph_enclosed'>`model4</render>
	</td></tr>
</table>



### Units

PyMCDP is picky about units, but generally very helpful.
As long as the units have the right dimensionality,
it will insert the appropriate conversions.

TODO: add pointers to problems with conversions: Glimli Glider, Ariane?

For example, this is the same example with the specific
energy given in kWh/kg.


<table class="col2">
	<tr><td>
		<pre class='mcdp' id='model5'>
		mcdp {
			provides capacity [J]
			requires mass [g]

			# specific energy
			ρ = 200 kWh / kg
			required mass ≽ provided capacity / ρ
		}
		</pre>
	</td><td>
		<render class='ndp_graph_enclosed_TB'>`model5</render>
	</td></tr>
</table>
