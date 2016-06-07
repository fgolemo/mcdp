The MCDP Language
=================


[TOC]

Overview {: #overview}
=====================




Simple Types
============

MCDPL is very strongly typed.


Natural and real numbers
------------------------

Use:

~~~~~~
nat:5
int:5
~~~~~~

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

This is an example of an MCDP:

~~~~~~.mcdp_model
mcdp {
	
}
~~~~~~


~~~~~~.mcdp_model
mcdp {
	provides x [J]
}
~~~~~~


Shortcuts
---------

~~~~~~.mcdp_line
x = instance load S
~~~~~~

~~~~~~.mcdp_line
x = from_library "S"
~~~~~~

~~~~~~.mcdp_line
x = from_library 'S'
~~~~~~


To write
========

* How to express +infinity?

### New {:#FromLibraryKeyword}
### Instance {:#InstanceKeyword}
### Template {:#TemplateKeyword}
### MCDP {:#MCDPKeyword}
### Approx {:#ApproxKeyword}
### Provides {:#ProvideKeyword}
### Requires {:#RequiresKeyword}


Missing features
================

* Expressing empty typed sets: https://github.com/AndreaCensi/mcdp/issues/10
