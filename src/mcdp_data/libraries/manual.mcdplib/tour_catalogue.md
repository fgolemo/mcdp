## Catalogues (enumeration)

The previous example used a linear relation between functionality
and resource. However, in general, MCDPs do not make any assumption
about continuity and differentiability of the functionality-resource
relation. The MCDPL language has a construct called "catalogue"
that allows defining an arbitrary discrete relation.

Recall from the theory that a design problem is generally defined
from a triplet of <f>functionality space</f>, <imp>implementation space</imp>, and <r>resource space</r> ([](#def:DP)). According
to the diagram in [](#fig:gmcdp_setup), one should define the two maps $\eval$ and $\exc$, which map an implementation to the functionality it provides and the resources it requires.

<center>
    <img class='art'  latex-options='scale=0.33'  src="gmcdp_setup.pdf"
        figure-id='fig:gmcdp_setup'/>
</center>

<figcaption id='fig:setup:caption'>
A design problem is defined from an mplementation space $\impsp$, functionality space $\funsp$, resource space $\ressp$, and the
maps $\eval$ and $\exc$ that relate the three spaces.
</figcaption>

MCDPL allows to define arbitrary maps $\eval$ and $\exc$,
and therefore arbitrary relations from functionality to resources, using the <k>catalogue {&hellip;}</k> construction. An example is shown
in [](#code:model3). In this case, the implementation space contains the
three elements <impname>model1</impname>, <impname>model2</impname>,
<impname>model3</impname>. Each model is explicitly associated
to a value in the functionality and in the resource space.

<center>
    <pre class='mcdp' id='model3' figure-id="code:model3">
    catalogue {
        provides capacity [J]
        requires mass [g]

        500 kWh &lt;--| model1 |--&gt; 100 g
        600 kWh &lt;--| model2 |--&gt; 200 g
        700 kWh &lt;--| model3 |--&gt; 400 g
    }
    </pre>
    <figcaption id='code:model3:caption'>
    The <k>catalogue</k> construct allows to define an arbitrary relation
    between functionality, resources, and implementation.
    </figcaption>
</center>

The icon for this construction is meant to remind of a spreadsheet ([](#fig:model3)).

<center>
    <render class='ndp_graph_expand' figure-id="fig:model3">`model3</render>
</center>

## Multiple minimal solutions

The <k>catalogue</k> construct is the first that allows to define
MCDPs that have multiple minimal solutions. To see this, let's
expand the model in [](#code:model3) to include a few more models
and one more resource, <rname>cost</rname>.

<center>
    <pre class='mcdp' id='catalogue2' figure-id="code:catalogue2">
    catalogue {
        provides capacity [J]
        requires mass [g]
        requires cost [USD]

        500 kWh &lt;--| model1 |--&gt; 100 g, 10 USD
        600 kWh &lt;--| model2 |--&gt; 200 g, 200 USD
        600 kWh &lt;--| model3 |--&gt; 250 g, 150 USD
        700 kWh &lt;--| model4 |--&gt; 400 g, 400 USD
    }
    </pre>
</center>

The numbers (not realistic) were chosen so that <impname>model2</impname>
and <impname>model3</impname> do not dominate each other:
they provide the same functionality (<fvalue>600 kWh</fvalue>)
but one is cheaper but heavier, and the other is more expensive
but lighter. This means that for the functionality value of <fvalue>600 kWh</fvalue> there are two minimal solutions: either <rvalue>⟨200 g, 200 USD⟩</rvalue> or <rvalue>⟨250 g, 150 USD⟩</rvalue>.

The number of minimal solutions is not constant: for this example,
we have:

<figcaption id='tab:catalogue2-solutions:caption' markdown="1">
Cases for model in [](#code:catalogue2)
</figcaption>

<center>
<col3 class='labels-row1' figure-id='tab:catalogue2-solutions'>
    <s>Functionality requested</s>
    <s>Optimal implementation(s)</s>
    <s>Minimal resources needed</s>
    <!--  -->
    <s>$\fun \leq$ <fvalue>500 kWh</fvalue></s>
    <s><impname>model1</impname></s>
    <s><rvalue>⟨100 g, 10 USD⟩</rvalue></s>
    <!--  -->
    <s><fvalue>500 kWh</fvalue> $\lt \fun \leq$ <fvalue>600 kWH</fvalue></s>
    <s><impname>model2</impname><br/>or<br/><impname>model3</impname></s>
    <s><rvalue>⟨200 g, 200 USD⟩</rvalue><br/>or<br/><rvalue>⟨250 g, 150 USD⟩</rvalue></s>
    <!--  -->
    <s><fvalue>600 kWh</fvalue> $\lt \fun \leq$ <fvalue>700 kWH</fvalue></s>
    <s><impname>model4</impname></s>
    <s><rvalue>⟨400 g, 400 USD⟩</rvalue></s>
    <!--  -->
    <s><fvalue>700 kWh</fvalue> $\lt \fun$</s>
    <s><impname>$\emptyset$</impname></s>
    <s><rvalue>$\emptyset$</rvalue></s>
</col3>
</center>

<style>
/*#tab\:catalogue2-solutions table {
    border-collapse: collapse;
    border: 0;
}
#tab\:catalogue2-solutions tr:first-child td {
    padding-bottom: 3pt;
}
#tab\:catalogue2-solutions tr:nth-child(even) {
    background-color: #fafafa;
}
#tab\:catalogue2-solutions tr:nth-child(odd):not(:first-child) {
    background-color: #eee;
}*/
</style>

We can verify these with <program>mcdp-solve</program>. We also
use the switch `--imp` to ask it to give also the name of the
implementations; without the switch, it only prints the value
of the minimal resources.

For example, for $\fun =$ <fvalue>50 kWH</fvalue>:

    $ mcdp-solve --imp catalogue2_try  "50 kWh"

we obtain one solution:

    Minimal resources needed: mass, cost = ↑{⟨mass:100 g, cost:10 USD⟩}
    r = ⟨mass:100 g, cost:10 USD⟩
    implementation 1 of 1: m = 'model1'

For $\fun =$ <fvalue>550 kWH</fvalue>:

    $ mcdp-solve --imp catalogue2_try  "550 kWh"

we obtain two solutions:

    Minimal resources needed: mass, cost = ↑{⟨mass:200 g, cost:200 USD⟩, ⟨mass:250 g, cost:150 USD⟩}
    r = ⟨mass:250 g, cost:150 USD⟩
      implementation 1 of 1: m = 'model3'
    r = ⟨mass:200 g, cost:200 USD⟩
      implementation 1 of 1: m = 'model2'

<program>mcdp-solve</program> displays first the set of minimal
resources required; then, for each value of the resource,
it displays the name of the implementations; in general, there could be
multiple implementations that have exactly the same resource consumption.

<!--
<render class='hasse'>
    poset {
        model
    }
</render> -->
