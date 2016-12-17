
## Space Rovers Energetics


<img src="space_rovers.small.jpg" style='width: 20em'/>

### One option: thermocouple

A thermocouple is a device that converts heat into electrical power.

<table><tr><td>
    <pre class="mcdp" id="Thermocouple" label='Thermocouple.mcdp'></pre>
</td><td>
    <pre class="ndp_graph_templatized_labeled"
        style='height: 10em'
        >`Thermocouple</pre>
</td></tr>
</table>


One way to get the heat is to procure a bit of Plutonium.

<table>
  <tr>
    <td>
      <pre class="mcdp" id="PlutoniumPellet" label='PlutoniumPellet.mcdp'></pre>
    </td><td>
      <pre class="ndp_graph_templatized_labeled"
          style='sheight: 10em'>`PlutoniumPellet</pre>
    </td>
  </tr>
</table>

We can connect the two, by specifying that the heat required by the 
thermocouple is provided by the pellet:

<p>
  <img class="ndp_graph_enclosed" id="plutonium_plus_thermocouple" enclosed="false">mcdp {
    plutonium_pellet = new PlutoniumPellet
    thermocouple = instance template `Thermocouple
    heat required by thermocouple <= heat provided by plutonium_pellet
  }</img>
</p>
 

The masses are summed together:

<pre class="mcdp" id='rtig'></pre>

<pre class="ndp_graph_enclosed">`rtig</pre>
