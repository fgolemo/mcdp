


Keys:

- R: refactoring / reorganization
- F: new features
- L: language features
- B: bugs
- T: testing


Goals:

(*) Show visualization of solve-r 

(*) Make tutorial video

(*) Improve correctness of symmetrization
- T: dual chain for functionality/resources (dual chain).
    This enables to compute stable(h1 h2*) or stable(h2 h1*)
 
(*) Cleanup:

- cleanup: remove ATTRIBUTE_NDP_RECURSIVE_NAME
- cleanup: remove normal form

- core: 'ignore resources' should modify the diagram, not create a wrapper.
- core: remove caching from LoopDP; make separate class
- core: remove caching from Library, make separate class
- core: generalize InvPlus2 -> InvPlusN with placeholders

(*) Test corner cases:
- core: 

(*) Doing extra stuff:
- F: color the constants to reflect whether they are funcs or resources
- F: automatically make the constant into a new function or resource
- F: implement the n-version of everything 
- F: Create "add_top" operator. 
- F: parse custom string for PosetCoproduct

(*) Unified solving interface, for interactive and batch drawing.
    - (interactive) I can drag over and I see the shape change
    - I can see the animation.

(*) Language additions
 

- F: intervals - what happens


(*) Esthetics

- visualization: have one icon for each library (library_icon.png)
- visualization: display the dependency graph among libraries
- visualization: use greek letters in repr_map for h*
- visualization: in the dp_flow pictures, the CoProduct is not expanded.
- visualization: Introduce "Ignore" blocks, so that they can get their own icon (terminator)
- visualization: now the edges that are not connected are not purple

On hold: 

(*) Interface with cvxpy
(*) Demo for QR code


(*) Bugs / Issues

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

- F: library list: templates
- F: list links to *.md documents in the initial library page
- F: put the "new model" link everywhere (list of models, /index)
- F: better initial list for each library

- F: create library
- F: rename library
- F: delete library
- F: rename model
- F: delete model
- F: send to non-fancy for internet explorer

- B: mcdp-web: make sure that everything works when packaged
- T: mcdp-web: Testing of at least all links.

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

- L: Even fancier language:

  x + y >= ⌈√x⌉ + ⌈√y⌉ + ℕ:10


- re-add some tests from invmult2

- floor0 for resources

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
 

- add SKIP_INITIAL = False

- dp graph for ParallelN
- add wrapping for errors while editing


-  B: we might not keep track of filename when using the template
  Need to remember the filename when we have the template.

- L: remove "new"
- L: remove "load"

- Refactor: rename Constant, Limit
- Refactor: Create DPContainer 
    DPContainer(dps):
    def get_dps():
      return _dps()
    def container_construct(dps): 
      """creates a new one"""

  so that we can test whether in the switchs we are taking care of every type.

- T: test all images

- misc: switch colors in Sublime for required, provided - unknown    

- web: editor align to 4-space boundaries instead of always adding 4 characters
- web: undo
- web: "pretty printing"?
    e.g.  h = Nat:1
         constant h = Nat:1

- What is the default interpretation of the highly ambiguous
   x = `name?

  constant
  variable
  requires 
  provides
  
  resource r1 = r required by X
  function f1 = f provided by Y
  r ≼ f
  mcdptype T = 

  sub dp =
  instance dp = new 


  template T = ???

- lang: int -> natural numbers, float -> Rcomp

-  T: unit tests for all images

- implement preceq, succeq
http://127.0.0.1:8080/libraries/eversion/models/battert2_eversion_battery_loop/views/edit_fancy/
- W: choose a better font for mathematical symbols
http://127.0.0.1:8080/libraries/eversion/models/battert2_eversion_battery_loop/views/edit_fancy/



- core: do not allow libraries with '.' in their name

- core: known failure: check_subtraction2_contexts

- core: optimize gg_get_formats

- W: better formatting of warnings. Give each own <p>
  rather than using ---- as separator

- core: new ExecutionContext:
  - add_warning()
  - get_cwd()
     or context.get_file()

- display: add option not to draw extra node 
- W: make editor view options for RL - TB (start at RL because more intuitive)

- core: simplify PlusValue and MinusValue

    mcdp {
     provides f1 [dimensionless]
     provides f2 [dimensionless]
     provides f3 [dimensionless]
     requires r1 [dimensionless]
     requires r2 [dimensionless]
     requires r3 [dimensionless]

      r1 + r2 * r3 + 2 dimensionless >= f1 * f2 + f3 + 2 dimensionless
    }
 

- core: better error message:
DPSemanticError: Constraint between incompatible spaces.
  R[kWh²/kg] can be embedded in R[g]: False 
  R[g] can be embedded in R[kWh²/kg]: False 
F2: Instance of <class 'mcdp_posets.rcomp_units.RcompUnits'>.
    R[g]
R1: Instance of <class 'mcdp_posets.rcomp_units.RcompUnits'>.
    R[kWh²/kg]
| Super conversion not available.
| A: Instance of <class 'mcdp_posets.rcomp_units.RcompUnits'>.
|    R[kWh²/kg]
| B: Instance of <class 'mcdp_posets.rcomp_units.RcompUnits'>.
|    R[g]
 

- beauty: Mux visualization with more than 21 signals (after z, use '{'), 

- simplify a * a to mcdp {  
   variable a, c [dimensionless] 
   c >= a * a + Nat:1 
   a >= square(c)  
}

- refactor: move eval_statement to its own .py

- refactor: make Map::repr_map abstract
- misc: delete caches in /tmp automatically

- L: constants like pi, e
- L: remove nat_Constnat with lowercase nat
- L: syntax for primitivedp algebra: loop(series(par))
- L: add test for CDP.Rcomp: 'ℝ'
- L: log exp etc.
- L: invpower resources - provided f  <= (required r)²
- L: (integer) power for Rcomp and Natural numbers: a ^ 2

- L: detect unused functions/resources
- L: uncertainty syntax "between ... and ..."
  required mass = between 120 Wh/kg and 100 Wh/kg 
  required mass = between 100 kg and 120 kg
- L: constant keyword in setnameconstant, otherwise it doesn't get highlighted

   constant gravity = 9.8 m/s² 
   weight = mass required by battery · gravity 
- L: refactor SemanticInformation - only done for Constants so far
- L: remove [] everywhere
- L: use preceq instead of <= as suggetion

- L: clarify "choose" for types and "choose" for dps (not implemented)
- L: add choose without the labels

  instance choose(A, B) = choose(instance A, instance B)

  - for choose(a, b), then a and be need to be disconnected

- beauty: in catalogue, model2 should be in yellow (or implementation color)
- beauty: maybe the numbers and the units should not be orange

- W: add documents in library in the dropdowns

- W: interface for ignore functions/resources

  Mode 1:
    function f1 : constrain/ignore (= constrain to >= Minimals P)
    resource r1 : minimize/constrain/ignore (constrain <= Maximals R)

  Mode 2:
    function f1 : maximize/constrain/ignore (= constrain to >= Minimals P)
    resource r1 : constrain/ignore (constrain <= Maximals R)

- refactor: mv mcdp_web/render_doc in mcdp_docs

- manual/docs: automatically beautify the code in the manual, unless there is 
  a class "dontbeautify"
- manual/docs: 

- misc: make tool that looks for warning everywhere

- W: for some error messages, only the string "msg" does not make sense.
  See, e.g., http://127.0.0.1:8080/libraries/eversion/models/battert2_eversion_battery_loop/views/edit_fancy/

- W: in library view, list all contents in columns, and add "create new" links
  directly in there.

  ndp   poset doc
  ndp   poset doc
  ndp         doc
  +     +     + create

- W: add credits page
 

- L: other subscripts

  E_r

- 
- suggest: fix recursive




- throw error if 
   b >= a
   a >= b


- add short headers <h1 short="describing MCDPs">Very looooon</h1>



- ø
- V: Top


- Change "TODO: XX" in <div class="Todo">XXX</div>

- use prettified names in diagrams
- use cdot in diagrms for units like J*kg/kWh]

- h4 formatting: undo
- check the different kind of caption (caption_left, caption_top)


- manual: mark the first part in 4.1.C - Finite Posets
- manual: add brackets, succeq, etc. in the list of unicode characters




- manual:

  Support level:

    Chrome  A+
    Safari  A - clicking in SVG not supported
    Opera   A+
    Firefox: B - bug with editing
    Edge    A?
      some fonts are missing for >=
    Explorer D 
      editor does not work
      figure size is incorrect

- add in interface: primitivedps and interfaces

  interface ~= type

  interface {
    provides mass [g]
    requires mass 
  }

- mcdp_web: in list library, add icons 


- remove old catalogue interface
