# Coproducts (alternatives)


Let us consider the model of a battery in which we take 
the functionality to be the capacity 
and the resources to be the mass [g] and the cost [$].

<div style='display:none'>
<pre class='mcdp' id='Battery'>
mcdp {
	provides capacity [J]
	requires mass [g]
	requires cost [$]
	
	specific_energy = 150 Wh/kg
    specific_cost = 2.50 Wh/$

	required mass >= provided capacity / specific_energy
	required cost >= provided capacity / specific_cost
}
</pre>
</div>

<pre class='ndp_graph_templatized_labeled'>`Battery</pre>


Consider two different battery technologies, 
characterized by their specific energy (Joules per gram)
and specific cost (USD per gram).

In this example, the numbers are chosen such that
one technology leads to cheaper but heavier batteries
and viceversa.

<table>
<tr>
<td>
<pre class='mcdp' id='battery_LiPo' label='Battery_LiPo.mcdp'>
mcdp {
	provides capacity [J]
	requires mass [g]
	requires cost [$]
	
	specific_energy = 150 Wh/kg
    specific_cost = 2.50 Wh/$

	required mass >= provided capacity / specific_energy
	required cost >= provided capacity / specific_cost
}
</pre>
</td>
<td>
<pre class='mcdp' id='Battery_NiH2' label='Battery_NiH2.mcdp'>
mcdp {
	provides capacity [J]
	requires mass [g]
	requires cost [$]
	
	specific_energy = 45 Wh/kg
    specific_cost = 10.50 Wh/$ 

	required mass >= provided capacity / specific_energy
	required cost >= provided capacity / specific_cost
}
</pre>
</td>
</tr>
<tr>
<td>
<pre class='ndp_graph_templatized_labeled'>`Battery_LiPo</pre>
</td>
<td>
<pre class='ndp_graph_templatized_labeled'>`Battery_NiH2</pre>
</td>
</tr>
</table>

These two batteries do not dominate each other.

We can define the **coproduct** of the two using
the keyword ``choose``:


<pre class='mcdp' id='Batteries' label='Batteries.mcdp'>
choose(
	NiH2: `Battery_LiPo,
	LiPo: `Battery_NiH2
)
</pre>

Graphically, the choice is indicated through dashed lines:

<pre class='ndp_graph_enclosed'>`Batteries</pre>



