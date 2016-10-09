
### A battery

A battery can be modeled as a device that provides <code class='mcdp_poset'>`DC_power</code>
over a period of time (endurance), and requires a DC input for charging as well as a charging time.


An example, consider the [RAVPower 10400mAh 3.5A Portable Charger Power Bank][ravpower_battery],
which is used in the [Duckiebot][duckiebot].

<img src='BatteryRavpower.jpg' style='width: 15em'/>


[ravpower_battery]: https://www.amazon.com/RAVPower-10400mAh-Portable-Technology-Black/dp/B00XC1WAQ6/
[duckiebot]: http://duckietown.mit.edu/


This device provides 2 DC outputs (USB type A) and requires
one DC input (USB Micro B).

<pre class='mcdp' id='BatteryRavpower' label='BatteryRavpower.mcdp'></pre>

<div style='text-align:center'>
    <pre class='ndp_graph_templatized'>`BatteryRavpower</pre>
    <pre class='ndp_graph_enclosed'>`BatteryRavpower</pre>
</div>

<!-- 

<pre class='ndp_graph_enclosed'>`BarrelCharger</pre>
<pre class='mcdp' id='BarrelCharger' label='BarrelCharger.mcdp'></pre>
 -->