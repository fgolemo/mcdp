<meta name="mcdp-library" content='rover_energetics'/>

# Space Rovers Energetics


<img figure-id="fig:space_rovers"
       src="space_rovers.small.jpg" style='width: 20em'/>


<figcaption id='fig:space_rovers:caption'>
 Two spacecraft engineers stand with a group of vehicles providing a comparison of three generations of Mars rovers developed at NASA's Jet Propulsion Laboratory, Pasadena, Calif. The setting is JPL's Mars Yard testing area. Front and center is the flight spare for the first Mars rover, Sojourner, which landed on Mars in 1997 as part of the Mars Pathfinder Project. On the left is a Mars Exploration Rover Project test rover that is a working sibling to Spirit and Opportunity, which landed on Mars in 2004. On the right is a Mars Science Laboratory test rover the size of that project's Mars rover, Curiosity, which landed on Mars in 2012. Sojourner and its flight spare, named Marie Curie, are 2 feet (65 centimeters) long. The Mars Exploration Rover Project's rover, including the "Surface System Test Bed" rover in this photo, are 5.2 feet (1.6 meters) long. The Mars Science Laboratory Project's Curiosity rover and "Vehicle System Test Bed" rover, on the right, are 10 feet (3 meters) long. The engineers are JPL's Matt Robinson, left, and Wesley Kuykendall. The California Institute of Technology, in Pasadena, operates JPL for NASA.

 <!-- Source: [NASA/JPL/Caltech](http://marsrovers.jpl.nasa.gov/gallery/press/opportunity/20120117a.html). -->
</figcaption>

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

<render style='max-width: 100%' class="ndp_graph_enclosed" id="plutonium_plus_thermocouple" enclosed="false">
mcdp {
  plutonium_pellet = new PlutoniumPellet
  thermocouple = instance template `Thermocouple
  heat required by thermocouple ≼ heat provided by plutonium_pellet
}
</render>


The masses are summed together:

<col1>
<pre class="mcdp" id='rtig'></pre>

<render  style='max-width: 100%' class="ndp_graph_enclosed">`rtig</render>
</col1>

Putting everything together


<render  style='max-width: 100%' class='ndp_graph_normal'>
  `EnergySources
</render>
