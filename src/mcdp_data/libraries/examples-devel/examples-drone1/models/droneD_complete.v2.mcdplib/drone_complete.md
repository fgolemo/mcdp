## Modeling energetics constraints in a UAV



### Battery model

A battery is specified as a DP with functionality
<span class=F>capacity</span> used for each missiong and
<span class=F>number of missions</span>,
and resources
<span class=R>cost</span>,
<span class=R>inertial mass</span>,
<span class=R>maintenance</span> (number of times the battery needs to be replaced).


<pre class='ndp_graph_templatized'>`Battery_LiPo</pre>
<pre class='mcdp' id='Battery_LiPo' label='Battery_LiPo.mcdp'></pre>
<pre class='ndp_graph_expand'>`Battery_LiPo</pre>

### Actuation

<pre class='ndp_graph_templatized'>`Actuation</pre>
<pre class='mcdp' id='Actuation' label='Actuation.mcdp'></pre>
<pre class='ndp_graph_expand'>`Actuation</pre>

### Actuation + energetics

<pre class='ndp_graph_templatized'>`ActuationEnergetics</pre>
<pre class='mcdp' id='ActuationEnergetics' label='ActuationEnergetics.mcdp'></pre>
<pre class='ndp_graph_enclosed'>`ActuationEnergetics</pre>

### Other parts

These are other parts that we need.

A **computer** provides computation.

<pre class='ndp_graph_templatized'>`Computer</pre>
<pre class='mcdp' id='Computer' label='Computer.mcdp'></pre>

<pre class='ndp_graph_templatized'>`Perception</pre>
<pre class='mcdp' id='Perception' label='Perception.mcdp'></pre>

<pre class='ndp_graph_templatized'>`Sensor</pre>
<pre class='mcdp' id='Sensor' label='Sensor.mcdp'></pre>

<pre class='ndp_graph_templatized'>`Strategy</pre>
<pre class='mcdp' id='Strategy' label='Strategy.mcdp'></pre>
<pre class='ndp_graph_enclosed'>`Strategy</pre>

<pre class='ndp_graph_templatized'>`Computer</pre>
<pre class='mcdp' id='Computer' label='Computer.mcdp'></pre>


<pre class='mcdp' id='Shipping' label='Shipping.mcdp'></pre>

### Other parts

<pre class='ndp_graph_templatized'>`DroneComplete</pre>
<pre class='mcdp' id='DroneComplete' label='DroneComplete.mcdp'></pre>
<pre class='ndp_graph_enclosed'>`DroneComplete</pre>



<pre class='mcdp' id='CustomerPlusEngineering' label='CustomerPlusEngineering.mcdp'></pre>
<pre class='ndp_graph_enclosed'>`CustomerPlusEngineering</pre>
