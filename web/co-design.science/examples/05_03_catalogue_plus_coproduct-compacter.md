---
title: Example 4
shortitle: Example 4
layout: default
# permalink: examples.html
---

	

## Complex co-product

This is a nontrivial example where we can choose either a simple 
cell, or a cell with a voltage converter.






<pre><code><span id='line1'><span class='line-gutter'> 1</span><span class='line-content'><span class='BuildProblem'><span class='MCDPKeyword'>mcdp</span> {</span></span>
<span id='line2'><span class='line-gutter'> 2</span><span class='line-content'>    </span></span>
<span id='line3'><span class='line-gutter'> 3</span><span class='line-content'>    <span class='SetMCDPType'><span class='DPTypeName'>simple_cell</span> = <span class='FromCatalogue'><span class='FromCatalogueKeyword'>catalogue</span> {</span></span>
<span id='line4'><span class='line-gutter'> 4</span><span class='line-content'>        <span class='FunStatement'><span class='ProvideKeyword'>provides</span><span class='FName'> voltage</span>  [<span class='PowerSet'>℘(<span class='Unit'>V</span>)</span>]</span></span></span>
<span id='line5'><span class='line-gutter'> 5</span><span class='line-content'>        <span class='FunStatement'><span class='ProvideKeyword'>provides</span><span class='FName'> capacity</span> [<span class='Unit'>J</span>]</span></span></span>
<span id='line6'><span class='line-gutter'> 6</span><span class='line-content'></span></span>
<span id='line7'><span class='line-gutter'> 7</span><span class='line-content'>        <span class='ResStatement'><span class='RequireKeyword'>requires</span><span class='RName'> cost</span> [<span class='Unit'>$</span>]</span></span></span>
<span id='line8'><span class='line-gutter'> 8</span><span class='line-content'>        <span class='ResStatement'><span class='RequireKeyword'>requires</span><span class='RName'> mass</span> [<span class='Unit'>kg</span>]</span><span class='CatalogueTable'><span class='ImpName'></span></span>
<span id='line9'><span class='line-gutter'> 9</span><span class='line-content'></span></span>
<span id='line10'><span class='line-gutter'>10</span><span class='line-content'>        <span class="comment"># These two have some functions, but</span></span></span>
<span id='line11'><span class='line-gutter'>11</span><span class='line-content'>        <span class="comment"># non-dominating resources</span></span></span>
<span id='line12'><span class='line-gutter'>12</span><span class='line-content'>        model1</span> | <span class='Collection'>{<span class='SimpleValue'><span class='ValueExpr'>1.5</span> <span class='Unit'>V</span></span>}</span> | <span class='SimpleValue'><span class='ValueExpr'>1</span> <span class='Unit'>MJ </span></span>|  <span class='SimpleValue'><span class='ValueExpr'>5</span> <span class='Unit'>$ </span></span>| <span class='SimpleValue'><span class='ValueExpr'>0.20</span> <span class='Unit'>kg </span></span>
<span id='line13'><span class='line-gutter'>13</span><span class='line-content'>        </span></span><span class='ImpName'>model2</span> | <span class='Collection'>{<span class='SimpleValue'><span class='ValueExpr'>1.5</span> <span class='Unit'>V</span></span>}</span> | <span class='SimpleValue'><span class='ValueExpr'>1</span> <span class='Unit'>MJ </span></span>| <span class='SimpleValue'><span class='ValueExpr'>15</span> <span class='Unit'>$ </span></span>| <span class='SimpleValue'><span class='ValueExpr'>0.10</span> <span class='Unit'>kg </span></span>
<span id='line14'><span class='line-gutter'>14</span><span class='line-content'>        <span class="comment"># This model gives 5V and needs an adapter</span></span></span>
<span id='line15'><span class='line-gutter'>15</span><span class='line-content'>        </span></span><span class='ImpName'>model3</span> | <span class='Collection'>{<span class='SimpleValue'><span class='ValueExpr'>5.0</span> <span class='Unit'>V</span></span>}</span> | <span class='SimpleValue'><span class='ValueExpr'>1</span> <span class='Unit'>MJ </span></span>|  <span class='SimpleValue'><span class='ValueExpr'>5</span> <span class='Unit'>$ </span></span>| <span class='SimpleValue'><span class='ValueExpr'>0.30</span> <span class='Unit'>kg</span></span>
<span id='line16'><span class='line-gutter'>16</span><span class='line-content'>    </span></span></span>}</span></span></span></span>
<span id='line17'><span class='line-gutter'>17</span><span class='line-content'>    </span></span>
<span id='line18'><span class='line-gutter'>18</span><span class='line-content'>    <span class='SetMCDPType'><span class='DPTypeName'>converters</span> = <span class='FromCatalogue'><span class='FromCatalogueKeyword'>catalogue</span> {</span></span>
<span id='line19'><span class='line-gutter'>19</span><span class='line-content'>        <span class='FunStatement'><span class='ProvideKeyword'>provides</span><span class='FName'> voltage</span>    [<span class='PowerSet'>set-of(<span class='Unit'>V</span>)</span>]</span></span></span>
<span id='line20'><span class='line-gutter'>20</span><span class='line-content'>        <span class='ResStatement'><span class='RequireKeyword'>requires</span><span class='RName'> v_in</span>       [<span class='PowerSet'>set-of(<span class='Unit'>V</span>)</span>]</span></span></span>
<span id='line21'><span class='line-gutter'>21</span><span class='line-content'>        <span class='ResStatement'><span class='RequireKeyword'>requires</span><span class='RName'> cost</span>       [<span class='Unit'>$</span>]</span></span></span>
<span id='line22'><span class='line-gutter'>22</span><span class='line-content'>        <span class='ResStatement'><span class='RequireKeyword'>requires</span><span class='RName'> mass</span>       [<span class='Unit'>g</span>]</span><span class='CatalogueTable'><span class='ImpName'></span></span>
<span id='line23'><span class='line-gutter'>23</span><span class='line-content'></span></span>
<span id='line24'><span class='line-gutter'>24</span><span class='line-content'>        step_up1</span> | <span class='Collection'>{<span class='SimpleValue'><span class='ValueExpr'>5</span> <span class='Unit'>V</span></span>}</span>        | <span class='Collection'>{<span class='SimpleValue'><span class='ValueExpr'>1.5</span> <span class='Unit'>V</span></span>}</span> |  <span class='SimpleValue'><span class='ValueExpr'>5</span> <span class='Unit'>$ </span></span>| <span class='SimpleValue'><span class='ValueExpr'>20</span> <span class='Unit'>g  </span></span>
<span id='line25'><span class='line-gutter'>25</span><span class='line-content'>        </span></span><span class='ImpName'>step_up2</span> |       <span class='Collection'>{<span class='SimpleValue'><span class='ValueExpr'>12</span> <span class='Unit'>V</span></span>}</span> | <span class='Collection'>{<span class='SimpleValue'><span class='ValueExpr'>1.5</span> <span class='Unit'>V</span></span>}</span> | <span class='SimpleValue'><span class='ValueExpr'>10</span> <span class='Unit'>$ </span></span>| <span class='SimpleValue'><span class='ValueExpr'>20</span> <span class='Unit'>g  </span></span>
<span id='line26'><span class='line-gutter'>26</span><span class='line-content'>        </span></span><span class='ImpName'>step_up2</span> | <span class='Collection'>{<span class='SimpleValue'><span class='ValueExpr'>5</span> <span class='Unit'>V</span></span><span class='comma'>,</span>  <span class='SimpleValue'><span class='ValueExpr'>12</span> <span class='Unit'>V</span></span>}</span> | <span class='Collection'>{<span class='SimpleValue'><span class='ValueExpr'>1.5</span> <span class='Unit'>V</span></span>}</span> | <span class='SimpleValue'><span class='ValueExpr'>10</span> <span class='Unit'>$ </span></span>| <span class='SimpleValue'><span class='ValueExpr'>20</span> <span class='Unit'>g  </span></span>
<span id='line27'><span class='line-gutter'>27</span><span class='line-content'>    </span></span></span>}</span></span></span></span>
<span id='line28'><span class='line-gutter'>28</span><span class='line-content'></span></span>
<span id='line29'><span class='line-gutter'>29</span><span class='line-content'>    <span class='SetMCDPType'><span class='DPTypeName'>cell_plus_converter</span> = <span class='BuildProblem'><span class='MCDPKeyword'>mcdp</span> { </span></span>
<span id='line30'><span class='line-gutter'>30</span><span class='line-content'></span></span>
<span id='line31'><span class='line-gutter'>31</span><span class='line-content'>        <span class='SetName'><span class='DPName'>converter</span> =<span class='DPInstance'> <span class='InstanceKeyword'>instance</span> <span class='DPVariableRef'>converters</span></span></span></span></span>
<span id='line32'><span class='line-gutter'>32</span><span class='line-content'>        <span class='SetName'><span class='DPName'>cell</span> =<span class='DPInstance'> <span class='InstanceKeyword'>instance</span> <span class='DPVariableRef'>simple_cell</span></span></span></span></span>
<span id='line33'><span class='line-gutter'>33</span><span class='line-content'></span></span>
<span id='line34'><span class='line-gutter'>34</span><span class='line-content'>        <span class='FunShortcut1'><span class='ProvideKeyword'>provides</span><span class='FName'> voltage</span>  <span class='UsingKeyword'>using</span><span class='DPName'> converter</span></span></span></span>
<span id='line35'><span class='line-gutter'>35</span><span class='line-content'>        <span class='FunShortcut1'><span class='ProvideKeyword'>provides</span><span class='FName'> capacity</span> <span class='UsingKeyword'>using</span><span class='DPName'> cell</span></span></span></span>
<span id='line36'><span class='line-gutter'>36</span><span class='line-content'></span></span>
<span id='line37'><span class='line-gutter'>37</span><span class='line-content'>        <span class='Constraint'>(<span class='Resource'><span class='RName'>v_in</span> <span class='RequiredByKeyword'>required by</span><span class='DPName'> converter</span></span>)<span class='leq'> ⊆</span> (<span class='Function'><span class='FName'>voltage</span> <span class='ProvidedByKeyword'>provided by</span><span class='DPName'> cell</span></span>)</span></span></span>
<span id='line38'><span class='line-gutter'>38</span><span class='line-content'></span></span>
<span id='line39'><span class='line-gutter'>39</span><span class='line-content'>        <span class='ResShortcut2'><span class='RequireKeyword'>requires</span><span class='RName'> cost</span><span class='geq'> ≥</span> (<span class='PlusN'><span class='Resource'><span class='RName'>cost</span> <span class='RequiredByKeyword'>required by</span><span class='DPName'> cell</span></span> <span class='plus'>+</span> <span class='Resource'><span class='RName'>cost</span> <span class='RequiredByKeyword'>required by</span><span class='DPName'> converter</span></span></span>)</span></span></span>
<span id='line40'><span class='line-gutter'>40</span><span class='line-content'>        <span class='ResShortcut2'><span class='RequireKeyword'>requires</span><span class='RName'> mass</span><span class='geq'> ≥</span> (<span class='PlusN'><span class='Resource'><span class='RName'>mass</span> <span class='RequiredByKeyword'>required by</span><span class='DPName'> cell</span></span> <span class='plus'>+</span> <span class='Resource'><span class='RName'>mass</span> <span class='RequiredByKeyword'>required by</span><span class='DPName'> converter</span></span></span>)</span></span></span>
<span id='line41'><span class='line-gutter'>41</span><span class='line-content'>    }</span></span></span></span>
<span id='line42'><span class='line-gutter'>42</span><span class='line-content'></span></span>
<span id='line43'><span class='line-gutter'>43</span><span class='line-content'>    <span class='SetName'><span class='DPName'>battery</span> =<span class='DPInstance'> <span class='InstanceKeyword'>instance</span> <span class='Coproduct'><span class='DPVariableRef'>simple_cell</span> <span class='coprod'>^</span><span class='DPVariableRef'> cell_plus_converter</span></span></span></span></span></span>
<span id='line44'><span class='line-gutter'>44</span><span class='line-content'>    <span class='ResShortcut1m'><span class='RequireKeyword'>requires</span><span class='RName'> cost</span>,<span class='RName'> mass</span> <span class='ForKeyword'>for</span><span class='DPName'> battery</span></span></span></span>
<span id='line45'><span class='line-gutter'>45</span><span class='line-content'>    <span class='FunShortcut1m'><span class='ProvideKeyword'>provides</span><span class='FName'> voltage</span>,<span class='FName'> capacity</span> <span class='UsingKeyword'>using</span><span class='DPName'> battery</span></span></span></span>
<span id='line46'><span class='line-gutter'>46</span><span class='line-content'>}</span></span></span>
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


 <img class="output" src="catalogue_plus_coproduct-compacter-default.png"/> 



