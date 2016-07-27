
### A step-up/step-down voltage converter

Next, we are going to model a
[Goldsource STU-200 Step Up/Down Voltage Transformer Converter][goldsource].

[goldsource]: https://www.amazon.com/Goldsource-STU-200-Voltage-Transformer-Converter/dp/B0022TMB9A/

<img src='goldsource_STU_200.jpg' style='width: 15em'/>

This is a device with 1 input and 3 outputs:


<pre class='mcdp' id='goldsource_STU_200' label='goldsource_STU_200.mcdp'></pre>

<div style='text-align:center'>
    <pre class='ndp_graph_templatized'>`goldsource_STU_200</pre>
    <pre class='ndp_graph_enclosed'>`goldsource_STU_200</pre>
</div>

### A battery

A battery can be modeled as a device that provides <code class='mcdp_poset'>`DC_power</code>
over a period of time (endurance), and requires a DC input for charging as well as a charging time.


An example, consider the [RAVPower 10400mAh 3.5A Portable Charger Power Bank][ravpower_battery],
which is used in the [Duckiebot][duckiebot].

<img src='battery_ravpower.jpg' style='width: 15em'/>


[ravpower_battery]: https://www.amazon.com/RAVPower-10400mAh-Portable-Technology-Black/dp/B00XC1WAQ6/
[duckiebot]: http://duckietown.mit.edu/


This device provides 2 DC outputs (USB type A) and requires
one DC input (USB Micro B).

<pre class='mcdp' id='battery_ravpower' label='battery_ravpower.mcdp'></pre>

<div style='text-align:center'>
    <pre class='ndp_graph_templatized'>`battery_ravpower</pre>
    <pre class='ndp_graph_enclosed'>`battery_ravpower</pre>
</div>
