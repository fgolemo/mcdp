

# Describing uncertain MCDPs


The keyword ``Uncertain`` is used to define uncertain relations.

For example, suppose there is some uncertain in the value
of the specific energy, varying between 100 Wh/kg
and 120 Wh/kg. This is one way to describe such uncertainty:

<pre class="mcdp" id='uncertain1'>
mcdp {
  provides capacity [Wh]
  requires mass     [kg]
 
  required mass >= 
    Uncertain(provided capacity/120 Wh/kg ,
              provided capacity/100 Wh/kg )
  
}
</pre>

The resulting MCDP has an uncertainty gate, marked with "?",
which joins two branches, the optimistic and the pessimistic branch.

<pre class='ndp_graph_expand'>`uncertain1</pre>


<img style='max-width: 30em' src="/libraries/uncertainty/models/uncertain_battery4/views/solver2/display1u.png?xaxis=capacity&amp;yaxis=mass&amp;xmin=0J&amp;xmax=1MJ&amp;nsamples=50"/>

<!--

This is an equivalent way to describe the same uncertainty:

<pre class="mcdp" id='uncertain2'>
mcdp {
  provides capacity [Wh]
  requires mass     [kg]
 
  required mass * Uncertain(100 Wh/kg, 120 Wh/kg) >= provided capacity
  
}
</pre>

<pre class='ndp_graph_expand'>`uncertain2</pre>

<img style='max-width: 30em' src="/libraries/uncertainty/models/uncertain_battery2/views/solver2/display1u.png?xaxis=capacity&amp;yaxis=mass&amp;xmin=0J&amp;xmax=1MJ&amp;nsamples=50"/>

-->
