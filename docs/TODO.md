
Keys:

- R: refactoring / reorganization
- F: features
- L: language features
- B: bugs
- T: testing


Meat
----


- the meat! make sure we close all the loops at the same time.

Incoming
---------

- Expand MCDPLibrary to load types, values, interfaces, as well.

- R: Replace conf_tools completely.
- R: Remove battery example
- L: Add something like:

  my_npd.mcdp
  from-code('module.function', {param1=..., param2=...})


- B: the @comptests inside example_battery are not used now. Use make w/ comptest command?

- add library hooks for types, etc.


Misc
-----

- R: change cdp_view -> ``mcdp_cli``
- R: add license information



- T: mcdplib: create stand-alone ``mcdp-test`` for each ``.mcdplib``
- T: mcddlib: make sure that we parse / run all the models

- B: automatically load CSS from that file.



MCDP-web
----------
- F: send to non-fancy for internet explorer
- B: change ``/language`` to ``/docs/language_notes``
- F: mcdp-web: nice CSS all around
- T: mcdp-web: Testing of at least all links.

- F: mcdp-web/fancy_editor: Submit changes 

- B: fancy_editor: the syntax highlighting skips the whitespace at the end of the model

- R: mcdp-web: reorganize by folder

- B: mcdp-web: make sure that everything works when packaged

- F: mcdp-web: allow browsing multiple libraries 

- F: the created models are in a folder "created/" (just like imported/)

- F: automatically parse and execute the snippets in the documents
- F: create static versions of documents


- B: we need to escape # in interactive. Maybe hexify?
http://127.0.0.1:8080/interactive/mcdp_value/#finite_poset { %0A    a <= b <= c  %0A    x <= c <= d # test%0A    e <= a1 # test%0A}



MCDP-web / QR
-------------

- put the "new model" link everywhere (list of models, /index)
- put the navigation bar everywhere

- only give option to import if there are more resources
- display all imported cards on the gui

- B: unicode characters such as ⟨ give server-side error

Bugs
----

- B: for testing, MCDPLibrary should not use the _cached directory; rather a temp dir. Otherwise there is a race condition.
- B: FinitePoset does not have Join, Meet

- B: Sometimes Pint does not simplify the units. For example,
      J * kg / Wh has the same dimensionality of kg

- B: compact() is bugged - it has to do with splits. Try compact DroneComplete.

- B: "(provided lift)^2" does not parse
- B: "nat:2 / 1 []"
- B: This does not parse cleanly:
```
mcdp {
  provides f1 [R] 
  requires r1 [R]
  requires r2 [R]

  f1  <= 1 [] + (r1 * (r2 + r1)  )

}

There is already a connection to function 'r1' of '_res_r1'.


 line  4 >  requires r2 [R]
 line  5 >
 line  6 >  f1  <= 1 [] + (r1 * (r2 + r1)  )
            ^
            |
            here or nearby
```

- B: there is an asymmetri for functions and resources

mcdp {
 provides f [g]
 requires r [g]
 required r >= 10 g
 provided f <= 14 g

# this is ok
 provided f <= 10 g
# this will cause an error:
# required r >= 20 g
}


- F: nice icon for take operation


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





