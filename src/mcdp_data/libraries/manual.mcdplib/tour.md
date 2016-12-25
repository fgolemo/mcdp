# Language and tools tutorial   {#sec:tutorial}

MCDPL is a modeling language that allows the formal definition of co-design problems.
MCDPL is designed to describe all and only MCDPs. There is a core of functionality
(posets, primitive relations, etc.) that are built in, and there are extension
mechanisms.

MCDPL is a *modeling* language, not a *programming* language. This means
that MCDPL allows to describe variables and systems of relations between
variables. Once the model is described, then it can be *queried*; and the
"interpreter" [<program>mcdp-solve</program>](#sec:mcdp-solve) runs the
computation necessary to obtain the answers.

This chapter describes the MCDPL modeling language, by way of a tutorial.
A more formal description is given in [](#sec:MCDPL-language-reference).
