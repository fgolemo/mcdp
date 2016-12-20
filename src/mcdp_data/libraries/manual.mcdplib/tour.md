# Quickly - the MCDPL modeling language

This chapter describes a modeling language called MCDPL that is expressive
enough to capture many interesting aspects of the designs of robots
and other domains in which there are many heterogenous subsystems.

The language encourages a recursive and compositional approach to
design. The interface of each subsystem is specified by its functionality
and its resources. There is a notion of composition, in which two
subsystem can be connected if the second provides the resources required
by the first. MCDPL supports a modules system that allows to re-use
commonly used models. An MCDP can be queried. For
example, the user can ask what is the optimal configuration of the
system that has the least amount of resources.

MCDPL comes with a web-based GUI described in <ref>Chapter ???</ref>. The user can input a model and immediately see the graphical representation of such model.
