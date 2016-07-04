

# Composing MCDPs

Suppose we define a simple model called ``Battery`` as follows:

<table>
<tr><td width='50%'>
<pre class="mcdp" id='Battery' label='Battery.mcdp'>
mcdp {
	provides capacity [J]
	requires mass [g]
	specific_energy = 100 kWh / kg
	mass >= capacity / specific_energy
}
</pre>
</td>
<td>
<pre class='ndp_graph_templatized_labeled' direction='LR'>`Battery</pre>
</td>
</tr>
</table>

Let's also define the MCDP ``actuation``:

<table>
<tr><td  width='50%'>
<pre class="mcdp" id='Actuation' label='Actuation.mcdp'>
mcdp {
	provides lift [N]
	requires power [W]
	
	l = lift
	p0 = 5 W
	p1 = 6 W/N
	p2 = 7 W/N^2
	power >= p0 + p1 * l + p2 * l^2
}
</pre>
</td>
<td>
<pre class='ndp_graph_templatized_labeled' direction='LR'>`Actuation</pre>
</td>
</tr>
</table>


Then we can combine these two together.

We can re-use previously defined MCDPs using the 
keyword ``new``:

<pre class="mcdp" id='combined1'>
mcdp {	
	actuation = new Actuation
	battery = new Battery
}
</pre>

This creates two sub-design problems, for now unconnected:

<pre class='ndp_graph_enclosed' direction='LR'>`combined1</pre>

To create a complete MCDP, take "endurance" as a high-level
functionality. Then the energy required is equal to 
endurance &times; power. 

<pre class="mcdp" id='combined2'>
mcdp {	
	actuation = new Actuation
	battery = new Battery

	# battery must provide power for actuation
	provides endurance [s]	
	energy = endurance * (power required by actuation)

	capacity provided by battery >= energy
}
</pre>

<pre class='ndp_graph_enclosed' direction='LR'>`combined2</pre>

We can create a model with a loop by introducing another constraint.

Take ``extra_payload`` to represent the user payload that we must carry.

Then the lift provided by the actuator must be at least the mass
of the battery plus the mass of the payload times gravity:


<pre class="mcdp" id='composition' label='Composition.mcdp'>
mcdp {
	
	actuation = new Actuation
	battery = new Battery

	# battery must provide power for actuation
	provides endurance [s]	
	energy = endurance * (power required by actuation)

	capacity provided by battery >= energy

	# actuation must carry payload + battery
	provides payload [g]
	gravity = 9.81 m/s^2
	total_mass = (mass required by battery + provided payload)

	weight = total_mass * gravity

	lift provided by actuation >= weight
}


</pre>

<pre class='ndp_graph_enclosed' direction='LR'>`Composition</pre>

### Abstraction and flattening

We can completely abstract an MCDP:

<pre class='ndp_graph_templatized_labeled' direction='LR'>`Composition</pre>

And we can also completely **flatten** it, by first expanding 
the sub components:

<pre class='ndp_graph_expand' direction='LR'>`Composition</pre>

and then erasing their borders:

<pre class='ndp_graph_expand' direction='LR'>flatten `Composition</pre>


