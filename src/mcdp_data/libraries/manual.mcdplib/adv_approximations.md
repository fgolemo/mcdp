


## Approximations


### Multiplication dual

<pre class='mcdp' id='invmult'>
mcdp  {
    provides a [R]
    requires b [R]
    requires c [R]
    a <= b * c
}
</pre>
<!-- <pre class='ndp_graph_templatized'>`invmult</pre> -->

<table class="approx">
    <tr>
        <td>$$n=1$$</td>
        <td>$$n=3$$</td>
        <td>$$n=5$$</td>
        <td>$$n=10$$</td>
        <td>$$n=25$$</td>
    </tr>
    <tr>
        <td>
        <img class='plot_value_generic'>
            &lt; solve(1 [], approx_lower(1, `invmult)),
                 solve(1 [], approx_upper(1, `invmult))  &gt;
        </img>
        </td>
        <td>
        <img class='plot_value_generic'>
            &lt; solve(1 [], approx_lower(3, `invmult)),
                 solve(1 [], approx_upper(3, `invmult))  &gt;
        </img>
        </td>
        <td>
        <img class='plot_value_generic'>
            &lt; solve(1 [], approx_lower(5, `invmult)),
                 solve(1 [], approx_upper(5, `invmult))  &gt;
        </img>
        </td>
        <td>
        <img class='plot_value_generic'>
            &lt; solve(1 [], approx_lower(10, `invmult)),
                 solve(1 [], approx_upper(10, `invmult))  &gt;
        </img>
        </td>
        <td>
        <img class='plot_value_generic'>
            &lt; solve(1 [], approx_lower(25, `invmult)),
                 solve(1 [], approx_upper(25, `invmult))  &gt;
        </img>
        </td>
    </tr>

</table>


### Addition dual

<pre class='mcdp' id='invplus'>
mcdp {
    provides a [R]
    requires b [R]
    requires c [R]
    a <= b + c
}
</pre>
<!-- <pre class='ndp_graph_templatized'>`invplus</pre> -->

<table class="approx">
    <tr>
        <td>$$n=1$$</td>
        <td>$$n=3$$</td>
        <td>$$n=5$$</td>
        <td>$$n=10$$</td>
        <td>$$n=25$$</td>
    </tr>
    <tr>
        <td>
        <img class='plot_value_generic'>
            &lt; solve(1 [], approx_lower(1, `invplus)),
                 solve(1 [], approx_upper(1, `invplus))  &gt;
        </img>
        </td>
        <td>
        <img class='plot_value_generic'>
            &lt; solve(1 [], approx_lower(3, `invplus)),
                 solve(1 [], approx_upper(3, `invplus))  &gt;
        </img>
        </td>
        <td>
        <img class='plot_value_generic'>
            &lt; solve(1 [], approx_lower(5, `invplus)),
                 solve(1 [], approx_upper(5, `invplus))  &gt;
        </img>
        </td>
        <td>
        <img class='plot_value_generic'>
            &lt; solve(1 [], approx_lower(10, `invplus)),
                 solve(1 [], approx_upper(10, `invplus))  &gt;
        </img>
        </td>
        <td>
        <img class='plot_value_generic'>
            &lt; solve(1 [], approx_lower(25, `invplus)),
                 solve(1 [], approx_upper(25, `invplus))  &gt;
        </img>
        </td>
    </tr>

</table>

<style type='text/css'>
table.approx img {
    width: 10em;
}

</style>
