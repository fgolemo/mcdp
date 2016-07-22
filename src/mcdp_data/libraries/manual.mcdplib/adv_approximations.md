
## Operations on MCDPs

### Abstraction and flattening

It is easy to create recursive composition in MCDP.

<pre class='mcdp' id='Composition1' label='Composition1.mcdp'>
mcdp {
  a = instance mcdp {
    c = instance mcdp {
      provides f [Nat]
      requires r [Nat]
      provided f + Nat:1 <= required r
    }

    provides f using c
    requires r for   c
  }

  b = instance mcdp {
    d = instance mcdp {
      provides f [Nat]
      requires r [Nat]
      provided f + Nat:1 <= required r
    }

    provides f using d
    requires r for   d
  }

  r required by a <= f provided by b
  requires r for b
  provides f using a
}
</pre>

<pre class='ndp_graph_expand'>`Composition1</pre>


We can completely abstract an MCDP, using the <code><strong>abstract</strong></code> keyword.

<pre class='mcdp'>abstract `Composition1</pre>
<pre class='ndp_graph_expand'>abstract `Composition1</pre>

And we can also completely **flatten** it, by erasing the border between subproblems:

<pre class='mcdp'>flatten `Composition1</pre>
<pre class='ndp_graph_expand'>flatten `Composition1</pre>


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
