# Staging area

## First chapter


Compositionality

Composability

Modularity

Functional requirements

Non-functional requirements

## Diagram


    Part 1
    Chapter 1
    Chapter 2
    Chapter 3
    Chapter 4
    Chapter 5


## Basics

The goal of the language is to represent all and only [MCDPs (Monotone Co-Design Problems)](#def:MCDP). For example, multiplying by a negative number is a syntax error.
<!-- <footnote>Similarly, CVX's~\cite{cvx} goal
is to describe all only convex problems.</footnote> -->

The interface of each subsystem is specified
by its <f>functionality</f> and its <r>resources</r>.

#### Composition

The language encourages a compositional approach to co-design.

There are several notions of "compositions" between two design problems (DPs) for which MCDPL provides syntactic constructs:

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

    <s>$\fun_1 + \fun_2 \posleq \res$</s>

    <s>$\fun \posleq \res_1 + \res_2$</s>

    <s>$\max(\fun_1, \fun_2) \posleq \res$</s>

    <s>$\max(\fun_1, \fun_2) \posleq \res$</s>

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



\subsection{Some related work}

Modern engineering has long since recognized the two ideas of modularity and hierarchical decomposition, yet there is no general quantitative theory of design that is applied to different domains. Most of the works in the theory of design literature study abstractions that are meant to be useful for a human designer, rather than an automated system. For example, a *function structure* diagram~\cite[p. 32]{pahl07} decomposes the function of a system in subsystems that exchange energy, materials, and signals~(\prettyref{fig:thatbook}). Design approaches such as Suh's theory of \emph{axiomatic design~}\cite{suh01} provide quantitative formalization but are limited to linear or linearized models, and cannot deal with recursive constraints.

\begin{figure}[H]
\subfloat[Function structure diagram from~\cite{pahl07}\label{fig:thatbook}]{\includegraphics[scale=0.33]{reits2_other_intro}}
\subfloat[Hierarchical decomposition of a watch's "form" and "function"~\cite{sussman80constraints}]{\includegraphics[scale=0.33]{reits2_steele}}
\caption{}
\end{figure}

Researchers in Optimization study much more general constraints systems
than those expressible as an MCDP~\cite{dechter03}, at the cost
of having fewer guarantees, and not having a clear compositional property.

In Computer Science, researchers have proposed models of computations
based on constraint satisfaction, such as \emph{Prolog,} or constraint
propagation~\cite{steele80definition}. Compared to these, there
are two distinct features of MCDPs: (1)~the semantics accommodates
multiple options for any quantity (the valuation of an edge is an
antichain of values, rather than a single value); (2)~inference can
accommodate arbitrary topologies of the graph of relations, including
cycles. On the other hand, the class of monotone relations is much
smaller than the set of all relations that more general-purpose constraint-based
systems can represent.




\subsection{Examples of non monotone relations}

Are there non monotone relations between functionality and resources?
Of course, one can create a non-monotone relation by taking a monotone
relation and applying a non-monotone transformation to either functionality
and resources.

But are there non monotone relations within a "natural" parameterization?
\begin{example}
In any decision making problem, the \F{performance} increases with
the \R{amount of data} available\textemdash except when it causes
sensory overload; then, more data is not better. (This is fixed by
introducing~\R{cognitive load} as a limited resource.)
\end{example}




\begin{example}
Some computations are quirky. Suppose that you want to compute the
Fourier transform of a vector of~$n$ pixels. Is the computation
required monotone in~$n$? Probably not. The first step in many implementations
is resampling the data so that its length is a power of 2, a step
that can be omitted when~$n$ itself is a power of~$2$. Therefore,
it might be faster to compute the answer for~$n=2^{m}$ than for~$n=2^{m}-1$.
\end{example}
