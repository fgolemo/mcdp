
## Defining uncertain constants <k>between</k> <k>±</k>

MCDPL allows to describe interval uncertainty for variables and expressions.

There are three syntaxes accepted ([](#tab:uncertainty-syntax)).


<col2 style='text-align: left' figure-id="tab:uncertainty-syntax">
<s> Explicit bounds </s>
<pre class="mcdp_statements">
    x = between [["lower bound"]] and [["upper bound"]]
</pre>

<s> Median plus or minus tolerance </s>
<pre class="mcdp_statements">
    x = [[median]] ± [["absolute tolerance"]]
</pre>

<s> Median plus or minus percent </s>
<pre class="mcdp_statements">
    x = [[median]] ± [["percent tolerance"]] &#37;
</pre>

</col2>

The character <q>`±`</q> can be written as <q>`+-`</q>.


For example, [](#tab:uncertainty-example)
shows the different ways in which a constant
can be declared to be between <value>9.95 kg</value> and
<value>10.05 kg</value>.

<col2  style='text-align: left' figure-id='tab:uncertainty-example'>

<s> Explicit bounds </s>
<pre class='mcdp_statements'>
c = between 9.95 kg and 10.05 kg
</pre>

<s></s>
<pre class='mcdp_statements'>
c = 10 kg
δ = 50 g
x = between c-δ and c+δ
</pre>

<s> Median plus or minus tolerance </s>

<pre class='mcdp_statements'>
c = 10 kg ± 50 g
</pre>

<s> Median plus or minus percent </s>
<pre class='mcdp_statements'>
c = 10 kg ± 0.5&#37;
</pre>

</col2>


<style>
#tab\:uncertainty-example,
#tab\:uncertainty-syntax {
    td {
        padding-top: 3pt;
    }
}
</style>

These expressions can be used also in tables ([](#code:catalogue-uncertainty)).

<pre class='mcdp' figure-id="code:catalogue-uncertainty">
catalogue {
    provides energy [J]
    requires mass [kg]

    100 kWh ± 5&#37; ⟷ 1.2 kg ± 100 g
}
</pre>


It is also possible to describe parametric uncertain relations:

<pre class='mcdp' figure-id="code:parametric-uncertainty">
mcdp {
    provides energy [J]
    requires mass [kg]

    specific_energy = between 100 kWh/kg and 120 kWh/kg
    required mass * specific_energy &gt;= provided energy
}
</pre>
