

## Operations on NDPs


### <k>abstract</k>

<pre class='mcdp'>
    abstract [["mcdp"]]
</pre>


### <k>compact</k>

The command <k>compact</k> takes an MCDP and produces another with "compacted" edges:

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
      a.r1 ≼ b.f1
      a.r2 ≼ b.f2
    }
</pre>

Original:

<render class='ndp_graph_expand'>`compact_example</render>

Compacted:

<render class='ndp_graph_expand'>compact `compact_example</render>

### <k>template</k>   {#keyword-template}

<pre class='mcdp'>
    template [["mcdp"]]
</pre>


### <k>flatten</k>

<pre class='mcdp'>
    flatten [["mcdp"]]
</pre>


### <k>canonical</k>

This puts the MCDP in a canonical form:

<pre class='mcdp'>
    canonical [["mcdp"]]
</pre>



### <k>approx_lower</k> <k>approx_upper</k>

This creates a lower and upper bound for the MCDP:

<pre class='mcdp'>
  approx_lower([[n]], [["mcdp"]])
</pre>

<pre class='mcdp'>
  approx_upper([[n]], [["mcdp"]])
</pre>



### <k>ignore</k>


Suppose f has type F. Then:

<pre class='mcdp_statements'>
    ignore [[functionality]] provided by [["dp"]]
</pre>

is equivalent to

<pre class='mcdp_statements'>
    [[functionality]] provided by [["dp"]] ≽ any-of(Minimals [[space]])
</pre>

Equivalently,

<pre class='mcdp_statements'>
    ignore [[resource]] required by [["dp"]]
</pre>

is equivalent to

<pre class='mcdp_statements'>
    [[resource]] required by [["dp"]] ≼ any-of(Maximals [[space]])
</pre>


### Abstraction and flattening <k>abstract</k> <k>flatten</k>

It is easy to create recursive composition in MCDP.

<pre class='mcdp' id='Composition1' label='Composition1.mcdp'>
mcdp {
  a = instance mcdp {
    c = instance mcdp {
      provides f [Nat]
      requires r [Nat]
      provided f + Nat:1 ≼ required r
    }

    provides f using c
    requires r for   c
  }

  b = instance mcdp {
    d = instance mcdp {
      provides f [Nat]
      requires r [Nat]
      provided f + Nat:1 ≼ required r
    }

    provides f using d
    requires r for   d
  }

  r required by a ≼ f provided by b
  requires r for b
  provides f using a
}
</pre>

<render class='ndp_graph_expand'>`Composition1</render>


We can completely abstract an MCDP, using the <k>abstract</k> keyword.

<pre class='mcdp'>abstract [[ "mcdp" ]]</pre>

For example:

<pre class='mcdp'>abstract `Composition1</pre>

<render class='ndp_graph_expand'>abstract `Composition1</render>

And we can also completely **flatten** it, by erasing the border between subproblems:


<pre class='mcdp'>flatten `Composition1</pre>

<render class='ndp_graph_expand'>flatten `Composition1</render>
