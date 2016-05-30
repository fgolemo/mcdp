

Overview
========



Simple Types
============

MCDPL is very strongly typed.


Natural and real numbers
------------------------

Use:

	nat:5
	int:5


R+ completion with units
------------------------

Some examples:

	5 J
	5 W


Sets
----

Use ``{...}`` to describe a set.

Example:

	{0 W, 1mW, 100 W}


Upper sets
----------

Use ``↑`` or ``upperset`` in front of a set:

	↑{0 J}
	upperset {0 J}	


Describing co-design problems
=============================


Shortcuts
---------

	x = instance load S

	x = from_library "S"

	x = from_library 'S'



To write
========

* How to express +infinity?

Missing features
================

* Expressing empty typed sets: https://github.com/AndreaCensi/mcdp/issues/10
