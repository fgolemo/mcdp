


## Approximations


### Multiplication dual

<pre class='mcdp' id='invmult'>
mcdp {
    x = instance mcdp  {
        provides f [dimensionless]
        requires r_1 [dimensionless]
        requires r_2 [dimensionless]
        f ≼ r_1 * r_2
    }

    provides f using x
    requires r_1, r_2 for x

    r_1 required by x ≼ 5
    r_2 required by x ≼ 5
}
</pre>


<table class="approx">
    <tr>
        <!-- <td>$$n=1$$</td> -->
        <td>$$n=3$$</td>
        <td>$$n=5$$</td>
        <td>$$n=10$$</td>
        <td>$$n=25$$</td>
    </tr>
    <tr>
        <!-- <td>
        <render class='plot_value_generic'>
            &lt; solve(1 [], approx_lower(1, `invmult)),
                 solve(1 [], approx_upper(1, `invmult))  &gt;
        </render>
        </td> -->
        <td>
        <render class='plot_value_generic'>
            &lt; solve(1 [], approx_lower(3, `invmult)),
                 solve(1 [], approx_upper(3, `invmult))  &gt;
        </render>
        </td>
        <td>
        <render class='plot_value_generic'>
            &lt; solve(1 [], approx_lower(5, `invmult)),
                 solve(1 [], approx_upper(5, `invmult))  &gt;
        </render>
        </td>
        <td>
        <render class='plot_value_generic'>
            &lt; solve(1 [], approx_lower(10, `invmult)),
                 solve(1 [], approx_upper(10, `invmult))  &gt;
        </render>
        </td>
        <td>
        <render class='plot_value_generic'>
            &lt; solve(1 [], approx_lower(25, `invmult)),
                 solve(1 [], approx_upper(25, `invmult))  &gt;
        </render>
        </td>
    </tr>

</table>


### Addition dual

<pre class='mcdp' id='invplus'>
mcdp {
    provides f [dimensionless]
    requires r_1 [dimensionless]
    requires r_2 [dimensionless]
    f ≼ r_1 + r_2
}
</pre>

<!-- <render class='ndp_graph_templatized'>`invplus</render> -->

<table class="approx">
    <tr>
        <!-- <td>$$n=1$$</td> -->
        <td>$$n=3$$</td>
        <td>$$n=5$$</td>
        <td>$$n=10$$</td>
        <td>$$n=25$$</td>
    </tr>
    <tr>
        <!-- <td>
        <render class='plot_value_generic'>
            &lt; solve(1 [], approx_lower(1, `invplus)),
                 solve(1 [], approx_upper(1, `invplus))  &gt;
        </render>
        </td> -->
        <td>
        <render class='plot_value_generic'>
            &lt; solve(1 [], approx_lower(3, `invplus)),
                 solve(1 [], approx_upper(3, `invplus))  &gt;
        </render>
        </td>
        <td>
        <render class='plot_value_generic'>
            &lt; solve(1 [], approx_lower(5, `invplus)),
                 solve(1 [], approx_upper(5, `invplus))  &gt;
        </render>
        </td>
        <td>
        <render class='plot_value_generic'>
            &lt; solve(1 [], approx_lower(10, `invplus)),
                 solve(1 [], approx_upper(10, `invplus))  &gt;
        </render>
        </td>
        <td>
        <render class='plot_value_generic'>
            &lt; solve(1 [], approx_lower(25, `invplus)),
                 solve(1 [], approx_upper(25, `invplus))  &gt;
        </render>
        </td>
    </tr>

</table>

<style type='text/css'>
    table.approx img {
        width: 10em;
    }
</style>
