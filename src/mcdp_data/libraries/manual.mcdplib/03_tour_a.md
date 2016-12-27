# Language and tools tutorial   {#sec:tutorial}

MCDPL is a modeling language that can be used to formally describe co-design
problems. MCDPL was designed to represent all and only [MCDPs (Monotone
Co-Design Problems)](#def:MCDP). For example, multiplying by a negative number
is a syntax error. There is a core of features implemented (posets,
primitive relations, etc.) that are built into the language, and there are
extension mechanisms.
<!-- For this, see [](#sec:Extension). -->

MCDPL is a *modeling* language, not a *programming* language. This means that
MCDPL allows to describe variables and systems of relations between variables.
Once the model is described, then it can be *queried*; and the "interpreter"
[<program>mcdp-solve</program>](#sub:mcdp-solve) runs the computation necessary
to obtain the answers.

This chapter describes the MCDPL modeling language, by way of a tutorial. A more
formal description is given in [](#sec:MCDPL-language-reference).
