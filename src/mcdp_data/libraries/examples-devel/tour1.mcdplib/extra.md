<style type='text/css'>
.keyword {
    font-weight: bold;
    color: #00a;
}
.ph { /* placeholder */
    font-style: italic;
}
</style>

# Draft documentation

## Load

    load <name>

    `<name>

## Space expressions

### set-of

<pre class='mcdp_poset ex1'>
℘(V)
</pre>

<pre class='mcdp_poset ex1'>
set-of(V)
</pre>

### UpperSets

The syntax is

<pre><code><span class="keyword">UpperSets</span>(<span class='ph'>poset</span>)</code></pre>

For example:

<pre class='mcdp_poset'>
UpperSets(V)
</pre>

### Interval

The syntax is

<pre><code><span class="keyword">Interval</span>(<span class='ph'>lower bound</span>,<span class='ph'>upper bound</span>)</code></pre>

For example:

<pre class='mcdp_poset'>
Interval(1g, 10g)
</pre>

### Singletons

    S(tag)

    S(tag):*


## Constant expressions

### Top, Bottom

The syntax is:

    ⊤ <space>
    Top <space>
    ⊥ <space>
    Bottom <space>

For example:

<pre class='mcdp_value'>
    Top V
</pre>

<pre class='mcdp_value'>
    ⊤ V
</pre>


<pre class='mcdp_value'>
    Bottom V
</pre>

<pre class='mcdp_value'>
    ⊥ V
</pre>
### set making

The syntax is:

    {<element>, <element>, ..., <element> }

For example:

<pre class='mcdp_value'>
{0 g, 1 g}
</pre>


### upperclosure

The syntax is:

    upperclosure <set>

For example:

<pre class='mcdp_value'>
upperclosure {0 g, 1 g}
</pre>


## Operations


### ignore


Suppose f has type F. Then:

    ignore f provided by x

is equivalent to

    f provided by x >= any-of(Minimals F)


Equivalently,

    ignore r required by x

is equivalent to

    r required by x <= any-of(Maximals R)


### available math operators

    ceil
    sqrt
    square
    pow
    max
    min

## Operations on NDPs




    provides f using c
    requires r for   c

### implemented-by

### approx

    approx()


### abstract

    abstract <ndp>

### compact

    compact <ndp>

### template

    template <ndp>

### flatten

    flatten <ndp>

### canonical

    canonical <ndp>

### approx_lower, approx_upper

    approx_lower(<n>, <ndp>)
    approx_upper(<n>, <ndp>)


### solve

    solve(value, <mcdp>)


### Uncertain
