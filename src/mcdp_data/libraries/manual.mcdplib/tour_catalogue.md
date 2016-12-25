## Catalogues (enumeration)

We can also enumerate an arbitrary relation, as in
[](#code:model3).

<center>
    <img class='art'  latex-options='scale=0.33'  src="gmcdp_setup.pdf"
        figure-id='fig:setup'/>

        <pre class='mcdp' id='model3' figure-id="code:model3">
        catalogue {
            provides capacity [J]
            requires mass [g]

            500 kWh &lt;--| model1 |--&gt; 100 g
            600 kWh &lt;--| model2 |--&gt; 200 g
            700 kWh &lt;--| model3 |--&gt; 400 g
        }
        </pre>
</center>

<figcaption id='fig:setup:caption'>
Implementation space $\impsp$, functionality space $\funsp$,
resource space $\ressp$.
</figcaption>

<figcaption id='code:model3:caption'>
The <k>catalouge</k> construct allows to enumerate an arbitrary relation.
</figcaption>


The icon for this construction is a spreadsheet ([](#fig:model3)).

<center>
    <render class='ndp_graph_expand' figure-id="fig:model3">`model3</render>

</center>


TODO: Add here the idea of multiple solutions
