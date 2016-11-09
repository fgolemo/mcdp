Keys:

- R: refactoring / reorganization
- F: features
- L: language features
- B: bugs
- T: testing


Goals:

(*) Implement solve-r 

(*) Write paper that explains language

(*) Make video

(*) Improve correctness of symmetrization
- T: dual chain for functionality/resources (dual chain).
    This enables to compute stable(h1 h2*) or stable(h2 h1*)

(*) Derivative of a diagram

(*) Cleanup:
- cleanup: remove ATTRIBUTE_NDP_RECURSIVE_NAME
- cleanup: remove normal form
- refactor: 'ignore resources' should modify the diagram, not create a wrapper.
- refactor: remove caching from LoopDP; make separate class
- refactor: remove caching from Library, make separate class
- refactor: generalize InvPlus2 -> InvPlusN with placeholders

(*) Test corner cases:
- get to 100% code coverage
- test ignore_resource  for wrong inputs
- T: what happens with recursive definitions? (a.poset = "`a")

(*) Doing extra stuff:
- F: color the constants to reflect whether they are funcs or resources
- F: automatically make the constant into a new function or resource
- F: implement the n-version of everything 
- F: Create "add_bottom(<poset>)" and "add_top" operator. 
- F: parse custom string for PosetCoproduct

(*) Unified solving interface, for interactive and batch drawing.
    - (interactive) I can drag over and I see the shape change
    - I can see the animation.


(*) Language additions
 

- F: "choose()" without labels
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


- F: "op(Poset)" => constructs opposite poset

- F: intervals - what happens

- L: Implement Python-style comments for more literate programming.

```
mcdp {
   """ this is the comment """

  provides x [J] "This is a comment for the description"
}
```
 

(*) Esthetics

- visualization: have one icon for each library (library_icon.png)
- visualization: display the dependency graph among libraries
- visualization: use greek letters in h*
- visualization: in the dp_flow pictures, the CoProduct is not expanded.
- visualization: Introduce "Ignore" blocks, so that they can get their own icon (terminator)
- visualization: now the edges that are not connected are not purple
- visualization: nice icon for  operations: take
- visualization: nice icon for  operations: meet, Join (green and red)


On hold: 

(*) Interface with cvxpy
(*) Demo for QR code


(*) Bugs / Issues

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



- B: there is now an ugly hack (Catch exception) when plotting in gg_*

- Bug in the dot drawing for this one:

  choose(
            NiMH: mcdp { a = instance mcdp {
    provides f1 <= 10g
    requires r1 >= f1
    }
    }
  )

- bug: This should have a better error message
   <code class='mcdp_value'>`my_poset: <em>element</em></code>.

    ValueError: If <pre> is empty then it needs to have an id.
    tag: <code class="mcdp_value">`my_poset: <em>element</em></code>

- performance: duckiebot_sol00 is veeery slow. Is it because we are doing "ignoring"?

- bug: > NotImplementedError: SumNLDP:solve_r: Cannot invert more than two terms.
Write "details mcdplib-actuation-ndp-duckiebot_sol00-ndp_check_solve_r_chain" to inspect the error.
 
- bug doc: Ravpower assume 110: The model says we have two options: we need to find an outlet of TypeM at either 110 V or 220 V which will provide 5 W of power. Moreover, we need at least 10.99 USD to buy the component.

- bug visualization: splits are not drawn well. See, e.g.,
http://ares-super.lids.mit.edu/~andrea/env_mcdp/src/mcdp/out/check_rendering/plugs/sockets.md.html

- bug: throw semanticerror instead of internalerror when there are repeated identifiers:

  mcdp {
     requires shape [m x m x m]
     requires shape >= <6.5in, 2in, 5.8in>



(*) MCDP-web

- R: add license information
- F: add credits to free sw in the initial page
- F: library list: templates
- F: list links to *.md documents in the initial library page
- F: better initial list for each library
- F: rename model
- F: delete model
- T: mcdp-web: Testing of at least all links.
- F: send to non-fancy for internet explorer
- B: fancy_editor: the syntax highlighting skips the whitespace at the end of the model
- B: mcdp-web: make sure that everything works when packaged

- F: put the "new model" link everywhere (list of models, /index)
- F: put the navigation bar everywhere
- B: unicode characters such as ⟨ give server-side error


- bug: refresh library does not reset the icon caches

- B: if the syntax is not correct, it is not displayed at all.
  http://127.0.0.1:8080/libraries/duckiebot_components/models/pimoroni_inc/views/syntax/

- F: SVG for dpgraph http://127.0.0.1:8080/libraries/droneD_complete.v2/models/perception/views/dp_graph/
 
- B: we need to escape # in interactive. Maybe hexify?
http://127.0.0.1:8080/interactive/mcdp_value/#finite_poset { %0A    a <= b <= c  %0A    x <= c <= d # test%0A    e <= a1 # test%0A}

- bug: we cannot visualize "ceilsqrt", see e.g. http://127.0.0.1:8080/libraries/solver/models/plusinvnat2/views/ndp_graph/

- change TakeRes, TakeFun with the identity

- check SumNDP repr_map: should be = instead of <=

- implementing user warnings:
    x ~ provided x

- bug: use Top R in http://127.0.0.1:8080/libraries/example-plusinv/models/test_conversion1/views/solver2/#Top []

- to document:
    
    variable

- Even fancier language:

  x + y >= ⌈√x⌉ + ⌈√y⌉ + ℕ:10

- Cannot create addition between R and Nat:

  mcdp {  
   variable a, c [R] 
   c >= square(a) + Nat:1 
   a >= square(c)  
  } 

- readd some tests from invmult2


- make green and red plus icons

- floor0 for resources
- generic unary for functions
- generic parsing for expressions operand(op, op, op)

- allow covariant syntax like:
    operand(op, op; opf, opf)
    mcdp {
      requires r
      provides f

      identity[r, x;f, x]

      a + b >= c + d

      leq[a+b; c+d]
    }

- reuse conversions 

- better simplifications:
  http://127.0.0.1:8080/libraries/basic/models/all_icons/views/dp_graph/

  parallel + swap = swap + parallel


- add display of warning to web interface
  (this means adding warnings to context)

- add SKIP_INITIAL = False
