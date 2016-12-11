
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


To create an empty set:

<pre class='mcdp_value'>
    EmptySet [[space]]
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

The command ``compact`` takes an MCDP and produces another with "compacted" edges:

<pre class='mcdp'>
    compact [["mcdp"]]
</pre>


For every pair of DPS that have more than one edge between them,
those edges are being replaced.

<pre class='mcdp' id='compact_example'>
    mcdp {
      a = instance template mcdp {
          provides f [Nat]
          requires r1 [Nat]
          requires r2 [Nat]
      }
      b = instance template mcdp {
          provides f1 [Nat]
          provides f2 [Nat]
          requires r [Nat]
      }
      a.r1 <= b.f1
      a.r2 <= b.f2
    }
</pre>

Original:

<pre class='ndp_graph_expand'>`compact_example</pre>

Compacted:

<pre class='ndp_graph_expand'>compact `compact_example</pre>

### template

<pre class='mcdp'>
    template [["mcdp"]]
</pre>


### flatten

<pre class='mcdp'>
    flatten [["mcdp"]]
</pre>


### canonical

This puts the MCDP in a canonical form:

<pre class='mcdp'>
    canonical [["mcdp"]]
</pre>



### approx_lower, approx_upper

This creates a lower and upper bound for the MCDP:

<pre class='mcdp'>
  approx_lower([[n]], [["mcdp"]])
</pre>

<pre class='mcdp'>
  approx_upper([[n]], [["mcdp"]])
</pre>


### solve and solve_r

Evaluates the model:

<pre class='mcdp_value'>
    solve([[functionality]], [["mcdp"]])
</pre>

<pre class='mcdp_value'>
    solve_f([[functionality]], [["mcdp"]])
</pre>

<!-- <pre class='mcdp_value'>
    solve_r( [[f]], [["mcdp"]])
</pre>
 -->

### Uncertain

TODO

### Asserts

Some asserts:

<pre>
assert_equal
assert_leq
assert_geq
assert_lt
assert_gt
assert_empty
assert_nonempty
</pre>


### Use of Unicode letters and glyphs 

MCDPL allows to use some Unicode characters in identifiers and expressions.

#### Greek letters

The following are the Greek letters supported and their translitteration.
Note that there is a difference between lower case and upper case.

    α alpha     Λ Lambda    Ρ Rho
    β beta      λ lambda    ρ rho
    Χ Chi       Μ Mu        Σ Sigma
    χ chi       μ mu        σ sigma
    Δ Delta     Ν Nu        Τ Tau
    δ delta     ν nu        τ tau
    Ε Epsilon   Ω Omega     Θ Theta
    ε epsilon   ω omega     θ theta
    Η Eta       Ο Omicron   Υ Upsilon
    η eta       ο omicron   υ upsilon
    Γ Gamma     Φ Phi       Ξ Xi
    γ gamma     φ phi       ξ xi
    Ι Iota      Π Pi        Ζ Zeta
    ι iota      π pi        ζ zeta  
    Κ Kappa     Ψ Psi       
    κ kappa     ψ psi      

The way MCDPL considers these glyphs is that they are immediately
converted to an extended form. 

Every Greek letter is 
converted to its name. It is syntactically equivalent to write
"``alpha``" or "``α``". 

#### Subscripts

These are the subscripts supported:

    x₀ x₁ x₂ x₃ x₄ x₅ x₆ x₇ x₈ x₉

Subscripts can only occur at the end of an identifier: ``a₁`` is valid, 
while ``a₁b`` is not valid.

For subscripts, every occurrence of a subscript of the digit *d* is converted to the fragment "``_d``".  It is syntactically equivalent to write
"``_1``" or "``₁``".

#### Superscripts

These are the superscripts:
   
    x¹ x² x³ x⁴ x⁵ x⁶ x⁷ x⁸ x⁹

Every occurrence of a superscript of the digit *d* is interpreted as a power "``^d``".  It is syntactically equivalent to write "``x^2``" or "``x²``".


#### Example of syntactic equivalence

Putting all together, it is equivalent to write

<pre class='mcdp_statements'>
alpha_1 = beta^3 + 9.81 m/s^2
</pre>

and 

<pre class='mcdp_statements'>
α₁ = β³ + 9.81 m/s²
</pre>








