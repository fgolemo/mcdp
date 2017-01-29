
## Types universe

MCDPL has several "types universes", which we are going to call "Posets", "Values",
"Named DPs (NDPs)", "Primitive DPs (PDPs)" and "Templates". Every expression in
the language belongs to one of these universes ([](#tab:types-universes)).

The syntax is designed in such a way that the type of each expression
can be inferred directly from the abstract syntax tree (AST).



<!-- figure-class="float_top" -->
<col3 figure-id="tab:types-universes"
      figure-caption="Types universe"
      class='labels-row1'>
    <s>Type universe </s>
    <s>example</s>
    <s>Semantics</s>

    <s>Posets</s>
    <s><mcdp-poset>Nat</mcdp-poset>, <mcdp-poset>m/s^2</mcdp-poset> </s>
    <s>A "poset" describes a set of objects and an order relation.</s>

    <s>Values</s>
    <s><mcdp-value>42</mcdp-value>, <mcdp-value>9.81 m/s^2</mcdp-value></s>
    <s>Values are elements of a posets.</s>


    <s>Upper and Lower Sets</s>
    <s></s>
    <s>These are represented as antichains</s>

    <s>Uncertain values (intervals)</s>
    <s><code>between 42 and 43</code></s>
    <s></s>

    <s>Interfaces</s>
    <s> </s>
    <s> </s>


    <s>Primitive DPs</s>
    <s>\xxx</s>
    <s>These correspond to the idea of the DP category. They have
        a functionality space and a resource space.</s>

    <s>Named DPs</s>
    <s><k>mcdp{...}</k></s>
    <s>These are Primitive DPs + information about the names
        of ports.</s>

    <s>Composite Named DPs</s>
    <s><k>mcdp{...}</k></s>
    <s>These are Named DPs that are described as the composition
        of other DPs.</s>

    <s>templates</s>
    <s><k>template[...]{...}</k> </s>
    <s>These are templates for Composite Named DPs (they could be considered
    morphisms in an operad).</s>

    <s>R-quantity</s>
    <s><code>provided a + 1</code></s>
    <s>An expression that refers to a resource</s>

    <s>F-quantity</s>
    <s><code>required a + 1</code></s>
    <s>An expression that refers to a functionality</s>

</col3>

<style type='stylesheet/less'>
    #tab\:types-universes {
        td {
            font-size: smaller;
            vertical-align: top;
            padding: 0.5em;
            &amp;:nth-child(3) {
                text-align: left;
            }
            &amp;:first-child  {
                width: 10em;
                text-align: center;
            }
        }
    }
</style>

There are numerous relations among these universes ([](#fig:universe)).

<img figure-id='fig:universes'
    figure-caption='Relationships among the types universes'
    src='universes.svg' style='width: 100%'/>
