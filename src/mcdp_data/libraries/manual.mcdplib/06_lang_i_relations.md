
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

Some aspects of MCDPL were inspired by a language called
[Fortress][fortress]\cite{fortress} that was developed by Guy Steele and team at
Sun during the period 2005--2012.<footnote>It was funded by the DARPA [High
Productivity Computing Systems (HPCS)][HPCS], but it didn't make the latter
phase  of the program, so it was eventually abandoned.</footnote>.

MCDPL uses these ideas from Fortress:

* the liberal use of *Unicode characters*, that make the models similar to the
  mathematical expressions. This is used both for operators
  as well as identifiers (e.g. ``ρ_1`` is a synonim of ``rho₂``).
   See <a href="#sub:unicode"/> for details.
* the use of *units* in the basic type system.

<cite id="bib:fourer02ampl">
    Fourer, Robert; Brian W. Kernighan (2002). AMPL: A Modeling Language
    for Mathematical Programming. Duxbury Press. ISBN 978-0-534-38809-6.
</cite>

<cite id="bib:fortress">Fortress paper \xxx</cite>

[fortress]: https://en.wikipedia.org/wiki/Fortress_(programming_language)

[HPCS]: https://en.wikipedia.org/wiki/High_Productivity_Computing_Systems
