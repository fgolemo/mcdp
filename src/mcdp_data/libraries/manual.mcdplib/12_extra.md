# Staging area



## Basics

The goal of the language is to represent all and only [MCDPs (Monotone Co-Design
Problems)](#def:MCDP). For example, multiplying by a negative number is a syntax
error.
<!-- <footnote>Similarly, CVX's~\cite{cvx} goal
is to describe all only convex problems.</footnote> -->

The interface of each subsystem is specified
by its <f>functionality</f> and its <r>resources</r>.

#### Composition

The language encourages a compositional approach to co-design.

There are several notions of "compositions" between two design problems (DPs)
for which MCDPL provides syntactic constructs:

* *series* ([](#subfig:series)): two DPs can be connected in series
  if the second provides
  the resources required by the first.
* *parallel* ([](#subfig:parallel)): \xxx
* *coproduct* ([](#subfig:coproduct)): Two DPs can describe two alternatives
* *recursive* ([](#subfig:hierarchical)): A larger DPs can be defined as the
  interconnection of smaller, primitive DPs.
* *templating* ([](#subfig:templating)): \xxx

<col3 figure-id="fig:main"
      figure-caption="DPs can be composed in a variety of ways">
    <span figure-id="subfig:series" figure-caption="Series">\xxx</span>
    <span figure-id="subfig:parallel"  figure-caption="Parallel">\xxx</span>
    <span figure-id='subfig:coproduct'  figure-caption="Coproduct">\xxx</span>
    <span figure-id='subfig:hierarchical'  figure-caption="Hierarchical"> \xxx</span>
    <span figure-id='subfig:templating' figure-caption="Templating">\xxx</span>
</col3>




The primitive DPs are shown in [](#fig:primitive).

<col4>

    $\fun_1 + \fun_2 \posleq \res$

    $\fun \posleq \res_1 + \res_2$

    $\max(\fun_1, \fun_2) \posleq \res$

    $\max(\fun_1, \fun_2) \posleq \res$

    <span>\xxx</span>
    <span>\xxx</span>

    <span>\xxx</span>

    <span>\xxx</span>

</col4>

### Interval (experimental)

The syntax is

<center>
    <pre class='mcdp_poset'>
    Interval([["lower bound"]], [["upper bound"]])
    </pre>
</center>

<!--
<pre><code><span class="keyword">Interval</span>(<span class='ph'>lower bound</span>,<span class='ph'>upper bound</span>)</code></pre>
 -->
For example:

<pre class='mcdp_poset'>
Interval(1g, 10g)
</pre>

### Singletons (experimental)

    S(tag)

    S(tag):*
