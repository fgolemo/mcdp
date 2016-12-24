## Coproducts (alternatives)

The *coproduct* construct allows to describe the idea of
"alternatives".

 <!-- The name comes from [the category-theoretical concept
of coproduct][cat-coproduct].

[cat-coproduct]: https://en.wikipedia.org/wiki/Coproduct -->

As an example, let us consider how to model the choice
between different battery technologies.

Consider the model of a battery, in which we take
the functionality to be the <f>capacity</f>
and the resources to be the <r>mass&nbsp;[g]</r> and the <r>cost&nbsp;[&#36;]</r>.


<pre class='mcdp' id='Battery1' style='display:none'>
mcdp {
    provides capacity [J]
    requires mass [g]
    requires cost [&#36;]

    rho = 150 Wh/kg # specific energy
    alpha = 2.50 Wh/&#36; # specific cost

    required mass ≽ provided capacity / rho
    required cost ≽ provided capacity / alpha
}
</pre>

<pre class='ndp_graph_templatized_labeled'
    figure-id="fig:Battery1">
    `Battery1
</pre>


Consider two different battery technologies,
characterized by their specific energy (Joules per gram)
and specific cost (USD per gram).

Specifically, consider [Nickel-Hidrogen batteries][NiH2]
and [Lithium-Polymer][LiPo] batteries.
On technology is cheaper but leads to heavier batteries
and viceversa. Because of this fact, there might be designs
in which we prefer either.

[NiH2]: https://en.wikipedia.org/wiki/Nickel%E2%80%93hydrogen_battery
[Lipo]: https://en.wikipedia.org/wiki/Lithium_polymer_battery

First we model the two battery technologies separately
as two MCDP using the same interface (same resources and same functionality).

<col2>
    <pre class='mcdp' id='Battery1_LiPo' label='Battery_LiPo.mcdp'>
    mcdp {
        provides capacity [J]
        requires mass [g]
        requires cost [&#36;]

        rho = 150 Wh/kg
        alpha = 2.50 Wh/&#36;

        required mass ≽ provided capacity / rho
        required cost ≽ provided capacity / alpha
    }
    </pre>

    <pre class='mcdp' id='Battery1_NiH2' label='Battery1_NiH2.mcdp'>
    mcdp {
        provides capacity [J]
        requires mass [g]
        requires cost [&#36;]

        rho = 45 Wh/kg
        alpha = 10.50 Wh/&#36;

        required mass ≽ provided capacity / rho
        required cost ≽ provided capacity / alpha
    }
    </pre>

    <render class='ndp_graph_templatized_labeled'>
        `Battery1_LiPo
       </render>

    <render class='ndp_graph_templatized_labeled'>
        `Battery1_NiH2
       </render>
</col2>

Then we can define the **coproduct** of the two using
the keyword <code><span class="CoproductWithNamesChooseKeyword">choose</span></code>.
Graphically, the choice is indicated through dashed lines.

<col2 class="td-valign-top">
    <pre class='mcdp' id='Batteries' label='Batteries.mcdp'>
    choose(
    NiH2: `Battery1_LiPo,
    LiPo: `Battery1_NiH2
    )
    </pre>
    <render class='ndp_graph_enclosed'>`Batteries</render>
</col2>
