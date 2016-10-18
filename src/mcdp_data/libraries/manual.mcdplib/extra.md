
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

<pre class='mcdp'>abstract [[ "mcdp" ]]</pre>

For example:

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

<pre class='mcdp_poset'>
UpperSets([[poset]])
</pre>

For example:

<pre class='mcdp_poset'>
UpperSets(V)
</pre>

### Interval

The syntax is


<pre class='mcdp_poset'>
Interval([["lower bound"]], [["upper bound"]])
</pre>

<!-- 
<pre><code><span class="keyword">Interval</span>(<span class='ph'>lower bound</span>,<span class='ph'>upper bound</span>)</code></pre>
 -->
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



<pre class='mcdp_value'>
    Top [[space]]
</pre>

<pre class='mcdp_value'>
    ⊤ [[space]]
</pre>

<pre class='mcdp_value'>
    Bottom [[space]]
</pre>

<pre class='mcdp_value'>
    ⊥  [[space]]
</pre>

    

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


<pre class='mcdp_value'>
{[[element]], [[element]], [["..."]], [[element]]}
</pre>

For example:

<pre class='mcdp_value'>
{0 g, 1 g}
</pre>


### upperclosure

The syntax is:

<pre class='mcdp_value'>
    upperclosure [[ set ]]
</pre>

For example:

<pre class='mcdp_value'>
upperclosure {0 g, 1 g}
</pre>


## Operations


### ignore


Suppose f has type F. Then:

<pre class='mcdp_statements'>
    ignore [[functionality]] provided by [["dp"]]
</pre>

is equivalent to

<pre class='mcdp_statements'>
    [[functionality]] provided by [["dp"]] >= any-of(Minimals [[space]])
</pre>

Equivalently,

<pre class='mcdp_statements'>
    ignore [[resource]] required by [["dp"]]
</pre>

is equivalent to

<pre class='mcdp_statements'>
    [[resource]] required by [["dp"]] <= any-of(Maximals [[space]])
</pre>

### available math operators

    ceil
    sqrt
    square
    pow
    max
    min

## Operations on NDPs


<pre class='mcdp_statements'>
    provides [[functionality]] using [["dp"]]
</pre>

<pre class='mcdp_statements'>
    requires [[resource]] for [["dp"]]
</pre>

### implemented-by

### approx

    approx()


### abstract

<pre class='mcdp'>
    abstract [["mcdp"]]
</pre>

### compact

<pre class='mcdp'>
    compact [["mcdp"]]
</ndp>

### template

<pre class='mcdp'>
    template [["mcdp"]]
</ndp>

### flatten

<pre class='mcdp'>
    flatten [["mcdp"]]
</ndp>

### canonical


<pre class='mcdp'>
    canonical [["mcdp"]]
</ndp>

### approx_lower, approx_upper

    approx_lower(<n>, [["mcdp"]])
    approx_upper(<n>, [["mcdp"]])


### solve

<pre class='mcdp_value'>
    solve(value, [["mcdp"]])
</pre>


### Uncertain
