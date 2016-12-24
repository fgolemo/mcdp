# MCDPL Language reference

This chapter gives a formal description of the MCDPL language.

MCDPL is a *modeling* language, not a *programming* language. This means
that MCDPL allows to describe variables and systems of relations between variables.
Once the model is described, then it can be *queried*; and the "interpreter"
[<program>mcdp-solve</program>](#sec:mcdp-solve) runs the computation necessary to obtain the answers.

MCDPL is designed to describe all and only MCDPs. There is a core of functionality
(posets, primitive relations, etc.) that are built in, and there are extension
mechanisms. This chapter describes the built-in facilities.

## Relation to other languages

Modeling languages for optimization have a long history~\cite{kallrath12}.


CLP...

AMPL <a href="#bib:fourer02ampl"/>

[Prolog][prolog] can also be considered as a modeling language to describe
logical relations (though note that the Prolog specification describes
also how inference works in that context).

[Modelica][modelica]...

[CVX][cvx]\cite{cvx}...

AIMMS (Bisschop)...

GAMS (Bisschop and Meeraus)...

LINDO/LINGO (Cunningham and Schrage)...

MPL (Kristjansson)

[prolog]: #
[modelica]: #
[cvx]: #


#### Fortress

Some aspects of MCDPL were inspired by a language called [Fortress][fortress]\cite{bib:fortress} that was developed by Guy Steele and team at Sun during the period 2005--2012.<footnote>It was funded by the DARPA
[High Productivity Computing Systems (HPCS)][HPCS], but it didn't make the latter phase  of the program, so it was eventually abandoned.</footnote>.

MCDPL uses these ideas from Fortress:

* the liberal use of *Unicode characters*, that make the models similar to the
  mathematical expressions. This is used both for operators
  as well as identifiers (e.g. ``ρ_1`` is a synonim of ``rho₂``).
   See <a href="#sec:unicode"/> for details.
* the use of *units* in the basic type system.

<cite id="bib:fourer02ampl">
    Fourer, Robert; Brian W. Kernighan (2002). AMPL: A Modeling Language
    for Mathematical Programming. Duxbury Press. ISBN 978-0-534-38809-6.
</cite>

<cite id="bib:fortress">Fortress paper \xxx</cite>

[fortress]: https://en.wikipedia.org/wiki/Fortress_(programming_language)

[HPCS]: https://en.wikipedia.org/wiki/High_Productivity_Computing_Systems

## Types universe

MCDPL has 5 "types universes". Every expression in the language
belongs to one of these types as described in \tabref{table1}.

<col3 figure-id="tab:table1"
      figure-caption="Types universe"
      class='labels-row1'>
    <s>Type universe </s>
    <s>example</s>
    <s></s>
    <!-- -->
    <s>Posets</s>
    <s><mcdp-poset>Nat</mcdp-poset>, <mcdp-poset>m/s^2</mcdp-poset> </s>
    <s>Posets are the equivalent of what are "types" in other languages.</s>
    <!-- -->
    <s>Values</s>
    <s><mcdp-value>42</mcdp-value>, <mcdp-value>9.81 m/s^2</mcdp-value></s>
    <s>Values are the elements of the posets.</s>
    <!-- -->
    <s>NDPs</s>
    <s><k>mcdp{...}</k></s>
    <s>These correspond to the mathematical idea of MCDPs, enriched by extra
        information, such as names of "ports".</s>
    <!-- -->
    <s>templates</s>
    <s><k>template[...]{...}</k> </s>
    <s>These are templates for NDPs; could be considered morphisms in an operad</s>
    <!-- -->
    <s>DPs</s>
    <s>\xxx</s>
    <s>These correspond to primitive DPs</s>
</col3>

\tabref{table2} describes for each type the default file extension
and the base Python class.

<col3 class='labels-row1'
    figure-id="tab:table2"
    figure-caption="Types universe, file extensions and Python superclass">
    <!---->
        <s>Type universe </s>
        <s> file extensions</s>
        <s>superclass</s>
        <!---->
        <s>Posets</s>
        <s>.mcdp_poset</s>
        <s>Poset</s>
        <!---->
        <s>Values</s>
        <s><code>.mcdp_value</code></s>
        <s><code>object</code><footnote>Any Python object will do. \xxx</footnote></s>
        <!---->
        <s>NDPs</s>
        <s> <code>.mcdp</code></s>
        <s><code>NamedDP</code></s>
     <!---->
        <s>templates</s>
        <s><code>.mcdp_template</code> </s>
        <s>\xxx</s>
    <!---->
        <s>DPs</s>
        <s><code>.mcdp_primitivedp</code></s>
        <s><code>PrimitiveDP</code></s>
</col3>

It is possile to implement one's own extensions by subclassing
one of these classes. In particular, what is easy to do
is creating custom ``Poset``s as well as ``PrimitiveDP``s,
if these cannot be expressed using the operators available.

<style type='text/css'>

#tab\:table1 td,
#tab\:table2 td { padding: 0.5em;} /* fix for fix for prince */
/*
#tab\:table1 tr:first-child,
#tab\:table2 tr:first-child  {
    font-weight: bold;
}*/

#tab\:table1 td:first-child,
#tab\:table2 td:first-child  {
    width: 10em;
    text-align: center;
}

/*#tab\:table2 td {text-align: center;}*/
</style>
