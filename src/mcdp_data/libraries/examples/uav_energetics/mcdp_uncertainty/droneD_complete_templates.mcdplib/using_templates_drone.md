## Example of using templates


Define the ActuationEnergeticsTemplate as follows

<pre class='mcdp_template' id='ActuationEnergeticsTemplate'/>

This can now be described as:

<pre class='template_graph_enclosed'>`ActuationEnergeticsTemplate</pre>


Now we can define an uncertain battery such as:


<pre class="mcdp" id='BatteryUncertain' label='BatteryUncertain.mcdp'>
mcdp {
  provides capacity [Wh]
  provides missions [dimensionless]

  requires cost     [&36;]

  requires maintenance [dimensionless]
  requires mass [g]

  missions ≼ 1000 []
  maintenance ≽ 1 []
  cost ≽ 100 &36;

  required mass ≽ 
    Uncertain(provided capacity/120 Wh/kg ,
              provided capacity/100 Wh/kg )
  
}
</pre>


and use it inside:

<pre class='mcdp' id='AE1' label='AE1.mcdp'>
specialize [
  Battery: `BatteryUncertain, 
  Actuation: `droneD_complete_v2.actuation,
  PowerApprox: `PowerApprox
] 
`ActuationEnergeticsTemplate
</pre>

<!-- <pre class='ndp_graph_enclosed'>`AE1</pre> -->

 
<!-- <pre class='print_mcdp'>approx_lower(5, `AE1)</pre> -->

<pre class='print_value'>solve(⟨10 minutes, 0g, 0W, 500[], 0 m/s⟩,approx_lower(5, `AE1))</pre>
<pre class='print_value'>solve(⟨10 minutes, 0g, 0W, 500[], 0 m/s⟩,approx_upper(5, `AE1))</pre>


