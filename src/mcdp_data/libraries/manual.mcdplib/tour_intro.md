
## Describing MCDPs

MCDP = Monotone Co-Design Problems...

The goal of the language is to represent all and only MCDPs.

For example, multiplying by a negative number is a syntax error.<footnote>Similarly, CVX's~\cite{cvx} goal is to describe all only convex problems.</footnote>

This section introduces MCDPL by way of a tutorial.

<a href='#this-does-not-exist'/>

The minimal MCDP can be defined as in <a href="#code:empty"/>.


<pre class='mcdp' id='empty' figure-id='code:empty'>
mcdp {

}
</pre>

The code describes an MCDP with no functionality or resources,
$\funsp=\One$, $\ressp=\One$.


The functionality and resources of an MCDP is defined using
the keywords <code>provides</code> and <code>requires</code>:

<pre class='mcdp' id='model1' figure-id='code:model1'>
mcdp {
	provides capacity [J]
	requires mass [g]

	# ...
}
</pre>

The code above defines an MCDP with one functionality, <f>capacity</f>, measured in joules,
and one resource, <r>mass</r>, measured in grams.

That is, $\funsp=\mathbb{R}_{+}^{[\text{J}]}$ and $\ressp=\mathbb{R}_{+}^{[\text{g}]}$. Here, let $\mathbb{R}$ refer to double precision floating point numbers.<footnote>(See how to describe types and type systems in <a href='#sec:types'/>.</footnote>

Graphically, the
MCDP is represented as a box with two edges (<a href="#fig:some"/>).


<render class='ndp_graph_templatized' figure-id="fig:some">
	`model1
</render>
<!--
	The MCDP defined above is, however, unusable, because we have
	not specified how ``capacity`` and ``mass`` relate to one another.
	Graphically, this is represented using purple unconnected arrows:

	<pre class='ndp_graph_expand'>`model1</pre>
-->

### Constant functionality and resources

The MCDP in <a href="#code:model1"/> is not complete, as we have not
defined what constraints <f>capacity</f> and <r>mass</r> must satisfy.

<a href='#code:model2'/> is a minimal example of a complete MCDP.
We have given hard bounds to both <f>capacity</f> and <r>mass</r>.

<col2>
	<pre class='mcdp' id='model2' figure-id="code:model2">
	mcdp {
		provides capacity [J]
		requires mass [g]

		provided capacity ≼ 500 J
		required mass ≽ 100g
	}
	</pre>
	<render class='ndp_graph_enclosed' figure-id="fig:model2">`model2</render>
</col2>

### Querying the model


It is possible to query this minimal example. For example:

	$ mcdp-solve minimal 400J

The answer is:

	Minimal resources needed: mass = ↑ 100 g


If we ask for more than the MCDP can provide:

	$ mcdp-solve minimal 600J

we obtain no solutions (the empty set):

	Minimal resources needed: mass = ↑ {}


### Describing relations between functionality and resources

In MCDPs, functionality and resources can depend on each other using
any monotone relations.

The language MCDPL contains as primitives addition,
multiplication, and division. For example, we can describe a linear relation between
mass and capacity, given by the specific energy, using the following line:

<pre class='mcdp_statements'>
	ρ = 4 J / g
	required mass ≽ provided capacity / ρ
</pre>

In the graphical representation (<a href="#fig:model4"/>), there is now
a connection between <f>capacity</f> and <r>mass</r>, with a DP that
multiplies by the inverse of the specific energy.


<col2>
		<pre class='mcdp' id='model4'>
		mcdp {
			provides capacity [J]
			requires mass [g]

			# specific energy
			ρ = 4 J / g
			required mass ≽ provided capacity / ρ
		}
		</pre>
		<render class='ndp_graph_enclosed'
			figure-id='fig:model4'>`model4</render>
</col2>



### Units

PyMCDP is picky about units. It will complain if any operation does
not have the required dimensionality. However, as long as the dimensionality
is correct, it will automatically convert to and from equivalent units.
For example, in <a href="#code:conversion"/> the specific energy given
in <mcdp-poset>kWh/kg</mcdp-poset>. The two MCDPs are equivalent. PyMCDP will take care of
the conversions that are needed, and will introduce a conversion from
<mcdp-poset>J*kg/kWh</mcdp-poset> to <mcdp-poset>g</mcdp-poset> (<a href="#fig:conversion"/>).

TODO: add pointers to problems with conversions: Glimli Glider, Ariane?

For example, this is the same example with the specific
energy given in <mcdp-poset>kWh/kg</mcdp-poset>.


<col2>
		<pre class='mcdp' id='model5' figure-id='code:conversion'
		figure-caption='Automatic conversion among g, kg, J, kWh'>
		mcdp {
			provides capacity [J]
			requires mass [g]

			# specific energy
			ρ = 200 kWh / kg
			required mass ≽ provided capacity / ρ
		}
		</pre>
		<render class='ndp_graph_enclosed_TB' figure-id="fig:conversion">`model5</render>
</col2>
