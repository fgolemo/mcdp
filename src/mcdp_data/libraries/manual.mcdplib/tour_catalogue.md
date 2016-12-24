## Catalogues (enumeration)

We can also enumerate an arbitrary relation, as in
[](#code:model3).

The icon for this construction is a spreadsheet ([](#fig:model3)).

<col2>
    <pre class='mcdp' id='model3' figure-id="code:model3">
    catalogue {
        provides capacity [J]
        requires mass [g]

        500 kWh &lt;--| model1 |--&gt; 100 g
        600 kWh &lt;--| model2 |--&gt; 200 g
        700 kWh &lt;--| model3 |--&gt; 400 g
    }
    </pre>

    <render class='ndp_graph_expand' figure-id="fig:model3">`model3</render>

</col2>


TODO: Add here the idea of multiple solutions
