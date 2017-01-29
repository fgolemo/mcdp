---
title: Example 3
shortitle: Example 3
layout: default
# permalink: examples.html
---

	

## Coproduct of design problems

This is an example of a simple *[coproduct][coproduct] of design problems*. The choice between
two types of battery switches according to the energy required.

[coproduct]: https://en.wikipedia.org/wiki/Coproduct






<pre><code><span id='line1'><span class='line-gutter'> 1</span><span class='line-content'><span class='BuildProblem'><span class='MCDPKeyword'>mcdp</span> {</span></span>
<span id='line2'><span class='line-gutter'> 2</span><span class='line-content'>    <span class='SetMCDPType'><span class='DPTypeName'>battery1</span> = <span class='BuildProblem'><span class='MCDPKeyword'>mcdp</span> {</span></span>
<span id='line3'><span class='line-gutter'> 3</span><span class='line-content'>        <span class='FunStatement'><span class='ProvideKeyword'>provides</span><span class='FName'> capacity</span> [<span class='Unit'>MJ</span>]</span></span></span>
<span id='line4'><span class='line-gutter'> 4</span><span class='line-content'>        <span class='ResStatement'><span class='RequireKeyword'>requires</span><span class='RName'> mass</span> [<span class='Unit'>kg</span>]</span></span></span>
<span id='line5'><span class='line-gutter'> 5</span><span class='line-content'></span></span>
<span id='line6'><span class='line-gutter'> 6</span><span class='line-content'>        <span class='SetNameGeneric'><span class='SetNameGenericVar'>m0</span> <span class='eq'>=</span> <span class='SimpleValue'><span class='ValueExpr'>50</span> <span class='Unit'>g</span></span>
<span id='line7'><span class='line-gutter'> 7</span><span class='line-content'>        </span></span></span><span class='SetNameGeneric'><span class='SetNameGenericVar'>specific_energy</span> <span class='eq'>=</span> <span class='SimpleValue'><span class='ValueExpr'>0.6</span> <span class='Unit'>MJ / kg </span></span>
<span id='line8'><span class='line-gutter'> 8</span><span class='line-content'></span></span>
<span id='line9'><span class='line-gutter'> 9</span><span class='line-content'>        </span></span></span><span class='Constraint'><span class='NewResource'>mass</span><span class='geq'> &gt;=</span> <span class='PlusN'><span class='Divide'><span class='VariableRef'>capacity</span> <span class='bar'>/</span> <span class='VariableRef'>specific_energy</span></span> <span class='plus'>+</span> <span class='VariableRef'>m0</span></span></span></span></span>
<span id='line10'><span class='line-gutter'>10</span><span class='line-content'>    }</span></span></span></span>
<span id='line11'><span class='line-gutter'>11</span><span class='line-content'>    </span></span>
<span id='line12'><span class='line-gutter'>12</span><span class='line-content'>    <span class='SetMCDPType'><span class='DPTypeName'>battery2</span> = <span class='BuildProblem'><span class='MCDPKeyword'>mcdp</span> {</span></span>
<span id='line13'><span class='line-gutter'>13</span><span class='line-content'>        <span class='FunStatement'><span class='ProvideKeyword'>provides</span><span class='FName'> capacity</span> [<span class='Unit'>MJ</span>]</span></span></span>
<span id='line14'><span class='line-gutter'>14</span><span class='line-content'>        <span class='ResStatement'><span class='RequireKeyword'>requires</span><span class='RName'> mass</span> [<span class='Unit'>kg</span>]</span></span></span>
<span id='line15'><span class='line-gutter'>15</span><span class='line-content'></span></span>
<span id='line16'><span class='line-gutter'>16</span><span class='line-content'>        <span class='SetNameGeneric'><span class='SetNameGenericVar'>m0</span> <span class='eq'>=</span> <span class='SimpleValue'><span class='ValueExpr'>100</span> <span class='Unit'>g </span></span>
<span id='line17'><span class='line-gutter'>17</span><span class='line-content'>        </span></span></span><span class='SetNameGeneric'><span class='SetNameGenericVar'>specific_energy</span> <span class='eq'>=</span> <span class='SimpleValue'><span class='ValueExpr'>1.0</span> <span class='Unit'>MJ / kg</span></span>
<span id='line18'><span class='line-gutter'>18</span><span class='line-content'></span></span>
<span id='line19'><span class='line-gutter'>19</span><span class='line-content'>        </span></span></span><span class='Constraint'><span class='NewResource'>mass</span><span class='geq'> &gt;=</span> <span class='PlusN'><span class='Divide'><span class='VariableRef'>capacity</span> <span class='bar'>/</span> <span class='VariableRef'>specific_energy</span></span> <span class='plus'>+</span> <span class='VariableRef'>m0</span></span></span></span></span>
<span id='line20'><span class='line-gutter'>20</span><span class='line-content'>    }</span></span></span></span>
<span id='line21'><span class='line-gutter'>21</span><span class='line-content'></span></span>
<span id='line22'><span class='line-gutter'>22</span><span class='line-content'>    <span class='SetName'><span class='DPName'>battery</span> =<span class='DPInstance'> <span class='InstanceKeyword'>instance</span> (<span class='Coproduct'><span class='DPVariableRef'>battery1</span> <span class='coprod'>^</span><span class='DPVariableRef'> battery2</span></span>)</span></span></span></span>
<span id='line23'><span class='line-gutter'>23</span><span class='line-content'></span></span>
<span id='line24'><span class='line-gutter'>24</span><span class='line-content'>    <span class='ResShortcut1'><span class='RequireKeyword'>requires</span><span class='RName'> mass</span> <span class='ForKeyword'>for</span><span class='DPName'> battery</span></span></span></span>
<span id='line25'><span class='line-gutter'>25</span><span class='line-content'>    <span class='FunShortcut1'><span class='ProvideKeyword'>provides</span><span class='FName'> capacity</span> <span class='UsingKeyword'>using</span><span class='DPName'> battery</span></span></span></span>
<span id='line26'><span class='line-gutter'>26</span><span class='line-content'>}</span></span></span>
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


 <img class="output" src="choose-default.png"/> 



