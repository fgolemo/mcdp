<style type='text/css'>
.F { color: darkgreen; }
.R { color: darkred;}
</style>

## Modeling energetics constraints in a UAV


### Battery model

A battery is specified as a DP with the functionalities:

* <span class=F>capacity</span> used for each mission;
* <span class=F>number of missions</span>;

and resources

* <span class=R>cost</span>;
* <span class=R>inertial mass</span>;
* <span class=R>maintenance</span> (number of times the battery needs to be replaced).

<render class='ndp_graph_templatized'>`Battery_LiPo1</render>

The parameters for the model are the specific energy, the specific cost, and
the number of cycles:

<pre class='mcdp_statements'>
specific_energy = 150 Wh/kg
specific_cost = 2.50 Wh/$
cycles = 600 []
</pre>

The cost for one battery is given by

<pre class='mcdp_statements'>
unit_cost = provided capacity / specific_cost
</pre>

The number of replacements is:

<pre class='mcdp_statements'>
num_replacements = ceil(provided missions / cycles)
</pre>

The total budget for the solution is given by the unit cost times
the number of replacements:

<pre class='mcdp_statements'>
required cost ≽ unit_cost  * num_replacements
</pre>

The code below is the complete model for the battery:

<pre class='mcdp' id='Battery_LiPo1' label='Battery_LiPo1.mcdp'></pre>

This is a graphical representation of the network of constraints:

<render class='ndp_graph_enclosed'>`Battery_LiPo1</render>

### Actuation


The actuation is defined as a DP where the functionalities are:

* <span class=F>the maximum platform velocity</span>;
* <span class=F>the maximum lift</span>;

and the resources are:

* <span class=R>cost</span>;
* <span class=R>actuator inertial mass</span>;
* <span class=R>power</span>.

<render class='ndp_graph_templatized'>`Actuation</render>

The model first describes some hard constraints for the quantities:

<pre class='mcdp_statements'>
provided lift ≼ 100N
required actuator_mass ≽ 100 g
required cost ≽ 100 $
provided velocity ≼ 3 m/s
</pre>

Then it describes a nonlinear polynomial (and monotone) relation
between <span class=F>lift</span> and <span class=R>power</span>:

<pre class='mcdp_statements'>
p0 = 2 W
p1 = 1.5 W/N^2

required power ≽ p0 + (lift^2) * p1
</pre>

This is the complete MCDP:

<pre class='mcdp' id='Actuation' label='Actuation.mcdp'></pre>

This is the graphical representation:

<pre class='ndp_graph_enclosed'>`Actuation</pre>

### Actuation + energetics

Next, we will define an MCDP that contains both
actuation and energetics as sub-MCDPs.

We will take as high-level functionality:

* <span class=F>endurance</span> (length of mission)
* <span class=F>extra payload</span>: things that must be carried on board
* <span class=F>extra power</span>: power to be provided for other subsystems

<pre class='ndp_graph_templatized'>`ActuationEnergetics</pre>


In the model below, first we instantiate the models of battery and actuation:

<pre class='mcdp_statements'>
battery = new Battery_LCO
actuation = new Actuation
</pre>


The **power constraint** can be written as follows:

<pre class='mcdp_statements'>
total_power = power required by actuation + extra_power
capacity provided by battery ≽ endurance * total_power
</pre>

The **lift constraint** is the following:

<pre class='mcdp_statements'>
total_mass = (
     mass required by battery +
     actuator_mass required by actuation
     + extra_payload)

gravity = 9.81 m/s^2
weight = total_mass * gravity

lift provided by actuation ≽ weight
</pre>

The **cost constraint** is the following:

<pre class=mcdp_statements>
labor_cost = (10 $) * (maintenance required by battery)

total_cost ≽ (
   cost required by actuation +
   cost required by battery +
   labor_cost)
</pre>

<pre class='mcdp' id='ActuationEnergetics' label='ActuationEnergetics.mcdp'></pre>
<pre class='ndp_graph_enclosed'>`ActuationEnergetics</pre>

### Other parts

These are other parts that we need.


<table>
    <tr>
        <td>
            <pre class='ndp_graph_templatized'>`Computer</pre>
        </td>
        <td>
            <pre class='ndp_graph_templatized'>`Sensor</pre>
        </td>
    </tr>
    <tr>
    <td>
        <pre class='ndp_graph_templatized'>`Perception</pre>
    </td>
    <td>
        <pre class='ndp_graph_templatized'>`Strategy</pre>
    </td>
    </tr>
</table>


<table>
    <tr>
        <td>
        <pre class='mcdp' id='Computer' label='Computer.mcdp'></pre>
        </td>
        <td>
            <pre class='mcdp' id='Sensor' label='Sensor.mcdp'></pre>
        </td>
    </tr>
    <tr>
    <td>
    <pre class='mcdp' id='Perception' label='Perception.mcdp'></pre>

    </td>
    <td>
        <pre class='mcdp' id='Strategy' label='Strategy.mcdp'></pre>
    </td>
    </tr>
</table>

<!-- ### Shipping

<pre class='mcdp' id='Shipping' label='Shipping.mcdp'></pre>
<pre class='ndp_graph_templatized'>`Shipping</pre>
 -->

### Complete drone model

Based on the previous models, we can assemble the model
for the entire drone, with high-level functionality:
* <span class=F>travel_distance</span>
* <span class=F>carry payload</span>
* <span class=F>num_missions</span>

<pre class='ndp_graph_templatized'>`DroneComplete</pre>
<pre class='ndp_graph_enclosed'>`DroneComplete</pre>
<pre class='mcdp' id='DroneComplete' label='DroneComplete.mcdp'></pre>


### Customer preferences in the loop

Finally, we can define a model of the customer:

<pre class='ndp_graph_templatized'>`Customer</pre>


and put it in the loop:

<pre class='mcdp' id='CustomerPlusEngineering' label='CustomerPlusEngineering.mcdp'></pre>
<pre class='ndp_graph_enclosed'>`CustomerPlusEngineering</pre>
