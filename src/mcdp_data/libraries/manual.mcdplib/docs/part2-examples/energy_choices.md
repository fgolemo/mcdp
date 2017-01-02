
## Space Rovers Energetics


<img src="space_rovers.small.jpg" style='width: 20em'/>

### One option: thermocouple

A thermocouple is a device that converts heat into electrical power.

<col2>
    <pre class="mcdp" id="Thermocouple" label='Thermocouple.mcdp'></pre>
    <render class="ndp_graph_templatized_labeled">`Thermocouple</render>
</col2>

One way to get the heat is to procure a bit of Plutonium.

<col2>
      <pre class="mcdp" id="PlutoniumPellet" label='PlutoniumPellet.mcdp'></pre>
      <render class="ndp_graph_templatized_labeled">`PlutoniumPellet</render>
</col2>

We can connect the two, by specifying that the heat required by the 
thermocouple is provided by the pellet:

<render class="ndp_graph_enclosed" id="plutonium_plus_thermocouple" enclosed="false">
mcdp {
  plutonium_pellet = new PlutoniumPellet
  thermocouple = instance template `Thermocouple
  heat required by thermocouple ≼ heat provided by plutonium_pellet
}
</render>
 

The masses are summed together:

<pre class="mcdp" id='rtig'></pre>

<render class="ndp_graph_enclosed">`rtig</render>
