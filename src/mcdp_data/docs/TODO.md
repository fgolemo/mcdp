




Goals:

(*) Unified solving interface, for interactive and batch drawing.
    - (interactive) I can drag over and I see the shape change
    - I can see the animation 


(*) Symmetrization for functionality/resources

    The challenge is creating dual of certain DPs, such as Mux DPs.

    This enables to compute stable(h1 h2*) or stable(h2 h1*)


(*) Esthetics

    - have one icon for each library (library_icon.png)

    - display the dependency graph among libraries


On hold:
(*) Create a video?

(*) Interface with cvxpy
(*) Demo for QR code
Discarded:
(*) Feature-parity with new Loop2, including normal transform - on hold 


Technical debt:

- revise the implementation of subtraction, done very quickly
- 'ignore resources' should modify the diagram, not create a wrapper.
- remove all the symlinks

- remove normal form
- remove caching from LoopDP; make separate class
- remove caching from Library, make separate class

--------------------





Keys:

- R: refactoring / reorganization
- F: features
- L: language features
- B: bugs
- T: testing


Bugs
-----

- throw semanticerror instead of internalerror when there are repeated identifiers
mcdp {
   requires shape [m x m x m]
   requires shape >= <6.5in, 2in, 5.8in>



- is a device that provides the <code class='mcdp_poset'>`AngularPlacement</code> functionality
and to do so requires the <code class='mcdp_poset'>`PPM</code> functionality.


ValueError: If <pre> is empty then it needs to have an id.
tag: <code class="mcdp_poset"><code>AngularPlacement&lt;/code&gt; functionality
     and to do so requires the &lt;code class='mcdp_poset'&gt;</code>PPM</code>

==> use backtick escape  &#96;

- F: parse custom string for PosetCoproduct
- B: refresh library does not reset the icon caches
- B: what happens with recursive definitions? (a.poset = "`a")

- now the edges that are not connected are not purple

- B: if the syntax is not correct, it is not displayed at all.
  http://127.0.0.1:8080/libraries/duckiebot_components/models/pimoroni_inc/views/syntax/

- F: SVG for dpgraph http://127.0.0.1:8080/libraries/droneD_complete.v2/models/perception/views/dp_graph/




Meat
----
- "op(Poset)" => constructs opposite poset

- intervals - what happens


- L: Add something like:

  my_npd.mcdp
  from-code('module.function', {param1=..., param2=...})


- F: better compiler that re-uses previous uses of take()
# This converts from TypeC to TypeL
mcdp {
    provides out [`power]
    requires in  [`power]
    requires cost [USD]

    # This device costs $5
    cost >= 5 USD

    take(in,  0) >= `socket_type : TypeL
    take(out, 0) <= `socket_type : TypeC

    take(in, 1) >=  take(out, 1) # voltages
    take(in, 2) >=  take(out, 2) # amperes
}


Misc
-----

- F: create operator approx(10g, -)

- B: automatically load CSS from that file. (introduces dependency on mcdp_web)


MCDP-web
----------

- R: add license information

- F: add credits to free sw in the initial page

- F: library list: templates


- R: drop "/list"


- F: list links to *.md documents in the initial library page
- F: better initial list for each library

- F: rename model

- F: delete model

- T: mcdp-web: Testing of at least all links.


- B: (low) when drawing images, use a unicode font
- F: send to non-fancy for internet explorer

- F: mcdp-web: nice CSS all around

- F: mcdp-web: let images be zoomable

- B: fancy_editor: the syntax highlighting skips the whitespace at the end of the model

- B: mcdp-web: make sure that everything works when packaged

- F: create static versions of documents

- B: we need to escape # in interactive. Maybe hexify?
http://127.0.0.1:8080/interactive/mcdp_value/#finite_poset { %0A    a <= b <= c  %0A    x <= c <= d # test%0A    e <= a1 # test%0A}


MCDP-web / QR
-------------

- put the "new model" link everywhere (list of models, /index)
- put the navigation bar everywhere


- B: unicode characters such as ⟨ give server-side error


Bugs
----

- B: FinitePoset does not have Join, Meet

- B: Sometimes Pint does not simplify the units. For example,
      J * kg / Wh has the same dimensionality of kg

- B: compact() is bugged - it has to do with splits. Try compact DroneComplete.

- B: "(provided lift)^2" does not parse
- B: "nat:2 / 1 []"

There is already a connection to function 'r1' of '_res_r1'.


 line  4 >  requires r2 [R]
 line  5 >
 line  6 >  f1  <= 1 [] + (r1 * (r2 + r1)  )
            ^
            |
            here or nearby
```

- F: nice icon for  operations: take
- F: nice icon for  operations: meet, Join


- B: there is now an ugly hack (Catch exception ) when plotting in gg_*

Language additions
------------------

- L: New language feature: templates

- L: types: Sets without the order. For example, given V, use set(V).
- L: values: Indexing. For example:

	```
	mcdp {
	   provides f [X x USD]
	   requires cost [USD]

	   cost >= f[1]
	}
	```

- L: Syntax for empty sets. ``{} g`` or  ``empty g``


- L: Implement Python-style comments for more literate programming.

```
mcdp {
   """ this is the comment """

  provides x [J] "This is a comment for the description"
}
```

- L: named tuples

  T = namedtuple(T: Type, U: Type)



- Bug in the dot drawing for this one:

choose(
        NiMH: mcdp { a = instance mcdp {
provides f1 <= 10g
requires r1 >= f1
}
}
)

- F: "choose()" without labels
   (get rid of ^?)


- F: better catalouge syntax - implicit point


  Putin = catalogue {
     provides plutonium [g]
     requires science [`scientific_objectives]
     100g | `scientific_objectives : find_current_life
     implicit : 100g | `scientific_objectives : find_current_life
  }

  catalouge {
     provides resolution [pixels]
     requires latency [s]


     500 pixels => 10
  }



- g: visualize PlusNat as "+ x"


- bug: This should have a better error message
   <code class='mcdp_value'>`my_poset: <em>element</em></code>.

    ValueError: If <pre> is empty then it needs to have an id.
    tag: <code class="mcdp_value">`my_poset: <em>element</em></code>
