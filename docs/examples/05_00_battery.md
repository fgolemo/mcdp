---
title: Example 1
shortitle: Example 1
layout: default
# permalink: examples.html
---

	

## Energetics + actuation

This example shows co-design of **energetics** (choose the battery)
and **actuation**. The **recursive co-design constraint** is that the actuators
must generate lift to transport the battery, and the battery must provide
power to the actuators.






<pre><code><span id='line1'><span class='line-gutter'> 1</span><span class='line-content'><span class='BuildProblem'><span class='MCDPKeyword'>mcdp</span> {  </span></span>
<span id='line2'><span class='line-gutter'> 2</span><span class='line-content'>    <span class="comment"># We need to fly for this duration</span></span></span>
<span id='line3'><span class='line-gutter'> 3</span><span class='line-content'>    <span class='FunStatement'><span class='ProvideKeyword'>provides</span><span class='FName'> endurance</span> [<span class='Unit'>s</span>]</span> </span></span>
<span id='line4'><span class='line-gutter'> 4</span><span class='line-content'>    <span class="comment"># While carrying this extra payload</span></span></span>
<span id='line5'><span class='line-gutter'> 5</span><span class='line-content'>    <span class='FunStatement'><span class='ProvideKeyword'>provides</span><span class='FName'> extra_payload</span> [<span class='Unit'>kg</span>]</span></span></span>
<span id='line6'><span class='line-gutter'> 6</span><span class='line-content'>    <span class="comment"># And providing this extra power</span></span></span>
<span id='line7'><span class='line-gutter'> 7</span><span class='line-content'>    <span class='FunStatement'><span class='ProvideKeyword'>provides</span><span class='FName'> extra_power</span> [<span class='Unit'>W</span>]</span></span></span>
<span id='line8'><span class='line-gutter'> 8</span><span class='line-content'></span></span>
<span id='line9'><span class='line-gutter'> 9</span><span class='line-content'>    <span class="comment"># Sub-design problem: choose the battery</span></span></span>
<span id='line10'><span class='line-gutter'>10</span><span class='line-content'>    <span class='SetName'><span class='DPName'>battery</span> =<span class='DPInstance'> <span class='InstanceKeyword'>instance</span> <span class='BuildProblem'><span class='MCDPKeyword'>mcdp</span> {</span></span>
<span id='line11'><span class='line-gutter'>11</span><span class='line-content'>        <span class="comment"># A battery provides capacity</span></span></span>
<span id='line12'><span class='line-gutter'>12</span><span class='line-content'>        <span class='FunStatement'><span class='ProvideKeyword'>provides</span><span class='FName'> capacity</span> [<span class='Unit'>J</span>]</span>        </span></span>
<span id='line13'><span class='line-gutter'>13</span><span class='line-content'>        <span class="comment"># and requires some mass to be transported</span></span></span>
<span id='line14'><span class='line-gutter'>14</span><span class='line-content'>        <span class='ResStatement'><span class='RequireKeyword'>requires</span><span class='RName'> mass</span> [<span class='Unit'>kg</span>]</span> </span></span>
<span id='line15'><span class='line-gutter'>15</span><span class='line-content'>        <span class="comment"># requires cost [$]</span></span></span>
<span id='line16'><span class='line-gutter'>16</span><span class='line-content'></span></span>
<span id='line17'><span class='line-gutter'>17</span><span class='line-content'>        <span class='SetNameGeneric'><span class='SetNameGenericVar'>specific_energy_Li_Ion</span> <span class='eq'>=</span> <span class='SimpleValue'><span class='ValueExpr'>500</span> <span class='Unit'>Wh / kg </span></span>
<span id='line18'><span class='line-gutter'>18</span><span class='line-content'></span></span>
<span id='line19'><span class='line-gutter'>19</span><span class='line-content'>        </span></span></span><span class='Constraint'><span class='NewResource'>mass</span><span class='geq'> &gt;=</span> <span class='Divide'><span class='VariableRef'>capacity</span> <span class='bar'>/</span> <span class='VariableRef'>specific_energy_Li_Ion</span></span></span></span></span>
<span id='line20'><span class='line-gutter'>20</span><span class='line-content'>    }</span></span></span></span></span>
<span id='line21'><span class='line-gutter'>21</span><span class='line-content'></span></span>
<span id='line22'><span class='line-gutter'>22</span><span class='line-content'>    <span class="comment"># Sub-design problem: actuation</span></span></span>
<span id='line23'><span class='line-gutter'>23</span><span class='line-content'>    <span class='SetName'><span class='DPName'>actuation</span> =<span class='DPInstance'> <span class='InstanceKeyword'>instance</span> <span class='BuildProblem'><span class='MCDPKeyword'>mcdp</span> {</span></span>
<span id='line24'><span class='line-gutter'>24</span><span class='line-content'>        <span class="comment"># actuators need to provide this lift</span></span></span>
<span id='line25'><span class='line-gutter'>25</span><span class='line-content'>        <span class='FunStatement'><span class='ProvideKeyword'>provides</span><span class='FName'> lift</span> [<span class='Unit'>N</span>]</span></span></span>
<span id='line26'><span class='line-gutter'>26</span><span class='line-content'>        <span class="comment"># and will require power</span></span></span>
<span id='line27'><span class='line-gutter'>27</span><span class='line-content'>        <span class='ResStatement'><span class='RequireKeyword'>requires</span><span class='RName'> power</span> [<span class='Unit'>W</span>]</span></span></span>
<span id='line28'><span class='line-gutter'>28</span><span class='line-content'>        <span class="comment"># simple model: quadratic</span></span></span>
<span id='line29'><span class='line-gutter'>29</span><span class='line-content'>        <span class='SetNameGeneric'><span class='SetNameGenericVar'>c</span> <span class='eq'>=</span> <span class='SimpleValue'><span class='ValueExpr'>10.0</span> <span class='Unit'>W/N^2</span></span></span></span></span>
<span id='line30'><span class='line-gutter'>30</span><span class='line-content'>        <span class='Constraint'><span class='NewResource'>power</span><span class='geq'> &gt;=</span> <span class='MultN'><span class='VariableRef'>lift</span> <span class='times'>*</span><span class='VariableRef'> lift</span> <span class='times'>*</span><span class='VariableRef'> c</span></span></span></span></span>
<span id='line31'><span class='line-gutter'>31</span><span class='line-content'>    }</span></span></span></span></span>
<span id='line32'><span class='line-gutter'>32</span><span class='line-content'>    <span class="comment"># Co-design constraint: battery must be large enough</span></span></span>
<span id='line33'><span class='line-gutter'>33</span><span class='line-content'>    <span class='SetNameGeneric'><span class='SetNameGenericVar'>power</span> <span class='eq'>=</span> <span class='PlusN'><span class='Resource'><span class='DPName'>actuation</span><span class='DotPrep'>.</span><span class='RName'>power</span></span> <span class='plus'>+</span> <span class='VariableRef'>extra_power</span></span></span></span></span>
<span id='line34'><span class='line-gutter'>34</span><span class='line-content'>    <span class='SetNameGeneric'><span class='SetNameGenericVar'>energy</span> <span class='eq'>=</span> <span class='MultN'><span class='VariableRef'>power</span> <span class='times'>*</span><span class='VariableRef'> endurance</span></span></span></span></span>
<span id='line35'><span class='line-gutter'>35</span><span class='line-content'>    <span class='Constraint'><span class='Function'><span class='DPName'>battery</span><span class='DotPrep'>.</span><span class='FName'>capacity</span></span><span class='geq'> &gt;=</span> <span class='VariableRef'>energy</span></span></span></span>
<span id='line36'><span class='line-gutter'>36</span><span class='line-content'></span></span>
<span id='line37'><span class='line-gutter'>37</span><span class='line-content'>    <span class="comment"># Co-design constraint: actuators must be powerful enough</span></span></span>
<span id='line38'><span class='line-gutter'>38</span><span class='line-content'>    <span class='SetNameGeneric'><span class='SetNameGenericVar'>gravity</span> <span class='eq'>=</span> <span class='SimpleValue'><span class='ValueExpr'>9.81</span> <span class='Unit'>m/s^2</span></span></span></span></span>
<span id='line39'><span class='line-gutter'>39</span><span class='line-content'>    <span class='SetNameGeneric'><span class='SetNameGenericVar'>weight</span> <span class='eq'>=</span> (<span class='MultN'><span class='PlusN'><span class='Resource'><span class='DPName'>battery</span><span class='DotPrep'>.</span><span class='RName'>mass</span></span> <span class='plus'>+</span> <span class='VariableRef'>extra_payload</span></span>) <span class='times'>*</span><span class='VariableRef'> gravity</span></span></span></span></span>
<span id='line40'><span class='line-gutter'>40</span><span class='line-content'>    <span class='Constraint'><span class='Function'><span class='DPName'>actuation</span><span class='DotPrep'>.</span><span class='FName'>lift</span></span><span class='geq'> &gt;=</span> <span class='VariableRef'>weight</span></span></span></span>
<span id='line41'><span class='line-gutter'>41</span><span class='line-content'></span></span>
<span id='line42'><span class='line-gutter'>42</span><span class='line-content'>    <span class="comment"># suppose we want to optimize for size of the battery</span></span></span>
<span id='line43'><span class='line-gutter'>43</span><span class='line-content'>    <span class='ResShortcut1'><span class='RequireKeyword'>requires</span><span class='RName'> mass</span> <span class='ForKeyword'>for</span><span class='DPName'> battery</span></span></span></span>
<span id='line44'><span class='line-gutter'>44</span><span class='line-content'>}</span></span></span>
</code></pre>

<style type="text/css">
 
     span.ProvideKeyword, span.FName { color: darkgreen;}
     span.RequireKeyword, span.RName  { color: darkred;}
     
     span.NewResource { color: darkred;}
     span.NewFunction { color: darkgreen; }
     
    span.Unit, span.Nat, span.Int  {  color: #aC5600 ;}
    span.ValueExpr { color: #CC6600 ;}
     
     /*span.Function  { color: darkgreen;}*/
    span.ProvideKeyword,
    span.RequireKeyword,     
    span.MCDPKeyword,
    span.SubKeyword,
    span.CompactKeyword,
    span.AbstractKeyword,
    span.TemplateKeyword,
    span.ForKeyword,
    span.UsingKeyword,
    span.RequiredByKeyword,
    span.ProvidedByKeyword,
    span.LoadKeyword,
    span.CodeKeyword,
    span.leq, span.geq, span.OpKeyword, span.eq, span.plus, span.times, span.DPWrapToken,
    span.ImplementedbyKeyword , span.FromCatalogueKeyword, span.MCDPTypeKeywor,
    span.InstanceKeyword,
    span.MCDPTypeKeyword { 
        font-weight: bold; 
    }
       
    span.ImpName { color: #CC6600; }
    span.FuncName { color: #CC6600 ; }

    span.MCDPKeyword,
    span.SubKeyword,
    span.CompactKeyword,
    span.AbstractKeyword,
    span.TemplateKeyword,
    span.ForKeyword,
    span.UsingKeyword,
    span.RequiredByKeyword,
    span.ProvidedByKeyword,
    span.LoadKeyword, span.CodeKeyword,
    span.leq, span.geq, span.OpKeyword, span.eq, span.plus, span.times, span.DPWrapToken,
    span.ImplementedbyKeyword,  
    span.FromCatalogueKeyword, 
    span.MCDPTypeKeyword,
    span.InstanceKeyword
    {
       color: #00a;
    }
    
    span.FName, span.RName { } 
    span.DPName {  
        color: #a0a;
    }
    
    span.DPTypeName, span.DPVariableRef { 
        color:  #00F; 
        font-weight: bold; 
    }
      
    span.comment { 
        color: grey;
    }

    span.line-gutter {    
        margin-right: 1em; 
        color: grey; 
    }


</style>


 <img class="output" src="battery-default.png"/> 



