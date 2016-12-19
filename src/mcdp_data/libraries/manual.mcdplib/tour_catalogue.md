## Catalogues

We can also enumerate an arbitrary relation, as follows:



<table class="col2">
    <tr><td>
    <pre class='mcdp' id='model3'>
    catalogue {
        provides capacity [J]
        requires mass [g]

        500 kWh &lt;--| model1 |--&gt; 100 g
        600 kWh &lt;--| model2 |--&gt; 200 g
        700 kWh &lt;--| model3 |--&gt; 400 g
    }
    </pre>
    </td><td>
    <render class='ndp_graph_expand'>`model3</render>
    </td></tr>
</table>
