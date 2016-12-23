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

Some aspects of MCDPL were inspired by a language called Fortress\cite{bib:fortress} that was developed by \xxx and team at Sun during the period 2005--2012.<footnote>It was funded out of a DARPA program for high-performance computing, but it didn't make the latter phase  of the program, so it was eventually abandoned.</footnote>.

MCDPL uses these ideas from Fortress:

* the liberal use of *Unicode characters*, that make the models similar to the
  mathematical expressions. This is used both for operators
  as well as identifiers (e.g. ``ρ_1`` is a synonim of ``rho₂``).
   See <a href="#sec:unicode"/> for details.
* the use of *units* in the basic type system.

<cite id="bib:fourer02ampl">Fourer, Robert; Brian W. Kernighan (2002). AMPL: A Modeling Language
for Mathematical Programming. Duxbury Press. ISBN 978-0-534-38809-6.</cite>

<cite id="bib:fortress">Fortress paper \xxx</cite>


## Types universe

MCDPL has 5 "types universes". Every expression in the language
belongs to one of these types as described in \tabref{table1}.

\begin{table}\caption{Types universe \label{tab:table1}}
\begin{tabular}{cll}
Type universe & example \\
Posets &  <mcdp-poset>Nat</mcdp-poset>, <mcdp-poset>m/s^2</mcdp-poset> &
        Posets are the equivalent of what are "types" in other languages.
\\
Values & <mcdp-value>42</mcdp-value>, <mcdp-value>9.81 m/s^2</mcdp-value>
& Values are the elements of the posets. \\
NDPs & <k>mcdp{...}</k>
    & These correspond to the mathematical idea of MCDPs, enriched by extra
        information, such as names of "ports". \\
templates & <k>template[...]{...}</k> & These are templates for NDPs; could be considered morphisms in an operad \\
DPs & \xxx & These correspond to primitive DPs \\
\end{tabular}
\end{table}

\tabref{table2} describes for each type the default file extension
and the base Python class.


\begin{table}\caption{Types universe, file extensions and Python superclass \label{tab:table2}}
\begin{tabular}{cll}
Type universe & file extension & Python superclass  \\
Posets & <code>.mcdp_poset</code> & <code>Poset</code> \\
Values & <code>.mcdp_value</code> & <code>object</code> <footnote>Any Python object will do. \xxx</footnote> \\
NDPs & <code>.mcdp</code> & <code>NamedDP</code> \\
templates & <code>.mcdp_template</code> & \xxx \\
DPs & <code>.mcdp_primitivedp</code> & <code>PrimitiveDP</code>
\end{tabular}
\end{table}

It is possile to implement one's own extensions by subclassing
one of these classes. In particular, what is easy to do
is creating custom ``Poset``s as well as ``PrimitiveDP``s,
if these cannot be expressed using the operators available.

<style type='text/css'>

#tab\:table1 td,
#tab\:table2 td { padding: 0.5em;} /* fix for fix for prince */

#tab\:table1 tr:first-child,
#tab\:table2 tr:first-child  {
    font-weight: bold;
}

#tab\:table1 td:first-child,
#tab\:table2 td:first-child  {
    width: 10em;
    text-align: center;
}

/*#tab\:table2 td {text-align: center;}*/
</style>
