
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
