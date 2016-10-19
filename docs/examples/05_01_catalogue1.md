---
title: Example 2
shortitle: Example 2
layout: default
# permalink: examples.html
---

	

## Simple catalogue

This is an example of a "catalogue"; MCDPs can work directly
with a "list of parts".

	




<pre><code><span id='line1'><span class='line-gutter'> 1</span><span class='line-content'><span class='FromCatalogue'><span class='FromCatalogueKeyword'>catalogue</span> {</span></span>
<span id='line2'><span class='line-gutter'> 2</span><span class='line-content'></span></span>
<span id='line3'><span class='line-gutter'> 3</span><span class='line-content'>    <span class='FunStatement'><span class='ProvideKeyword'>provides</span><span class='FName'> voltage</span> [<span class='PowerSet'>set-of(<span class='Unit'>V</span>)</span>]</span></span></span>
<span id='line4'><span class='line-gutter'> 4</span><span class='line-content'>    <span class='FunStatement'><span class='ProvideKeyword'>provides</span><span class='FName'> capacity</span> [<span class='Unit'>J</span>]</span></span></span>
<span id='line5'><span class='line-gutter'> 5</span><span class='line-content'></span></span>
<span id='line6'><span class='line-gutter'> 6</span><span class='line-content'>    <span class='ResStatement'><span class='RequireKeyword'>requires</span><span class='RName'> cost</span> [<span class='Unit'>$</span>]</span></span></span>
<span id='line7'><span class='line-gutter'> 7</span><span class='line-content'>    <span class='ResStatement'><span class='RequireKeyword'>requires</span><span class='RName'> mass</span> [<span class='Unit'>kg</span>]</span><span class='CatalogueTable'><span class='ImpName'></span></span>
<span id='line8'><span class='line-gutter'> 8</span><span class='line-content'></span></span>
<span id='line9'><span class='line-gutter'> 9</span><span class='line-content'>    model1</span> | <span class='Collection'>{<span class='SimpleValue'><span class='ValueExpr'>1.5</span> <span class='Unit'>V</span></span>}</span> | <span class='SimpleValue'><span class='ValueExpr'>1</span> <span class='Unit'>MJ </span></span>|  <span class='SimpleValue'><span class='ValueExpr'>5</span> <span class='Unit'>$ </span></span>| <span class='SimpleValue'><span class='ValueExpr'>0.20</span> <span class='Unit'>kg </span></span>
<span id='line10'><span class='line-gutter'>10</span><span class='line-content'>    </span></span><span class='ImpName'>model2</span> | <span class='Collection'>{<span class='SimpleValue'><span class='ValueExpr'>1.5</span> <span class='Unit'>V</span></span>}</span> | <span class='SimpleValue'><span class='ValueExpr'>1</span> <span class='Unit'>MJ </span></span>| <span class='SimpleValue'><span class='ValueExpr'>15</span> <span class='Unit'>$ </span></span>| <span class='SimpleValue'><span class='ValueExpr'>0.10</span> <span class='Unit'>kg </span></span>
<span id='line11'><span class='line-gutter'>11</span><span class='line-content'>    </span></span><span class='ImpName'>model3</span> | <span class='Collection'>{<span class='SimpleValue'><span class='ValueExpr'>5.0</span> <span class='Unit'>V</span></span>}</span> | <span class='SimpleValue'><span class='ValueExpr'>1</span> <span class='Unit'>MJ </span></span>|  <span class='SimpleValue'><span class='ValueExpr'>5</span> <span class='Unit'>$ </span></span>| <span class='SimpleValue'><span class='ValueExpr'>0.30</span> <span class='Unit'>kg</span></span>
<span id='line12'><span class='line-gutter'>12</span><span class='line-content'></span></span>
<span id='line13'><span class='line-gutter'>13</span><span class='line-content'></span></span></span>}</span></span></span>
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


 <img class="output" src="catalogue1-default.png"/> 



