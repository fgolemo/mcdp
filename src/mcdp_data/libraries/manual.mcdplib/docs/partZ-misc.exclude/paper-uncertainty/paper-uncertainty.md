
\title{Handling Uncertainty in Monotone Co-Design Problems}

\author{Andrea Censi}
\maketitle
\begin{abstract}
The work presented here contributes to a compositional theory of
``co-design'' that allows to optimally design a robotic platform.
In this framework, a user models each subsystem as a monotone relation
between \F{functionality provided} and \R{resources required}.
These models can be easily composed to express the co-design constraints
between different subsystems. The user then queries the model, to
obtain the design with minimal resources usage, subject to a lower
bound on the provided functionality. This paper concerns the introduction
of uncertainty in the framework. Uncertainty has two roles: first,
it allows to deal with limited knowledge in the models; second, it
also can be used to generate consistent relaxations of a problem,
as the computation requirements can be lowered should the user accept
some uncertainty in the answer.
\end{abstract}


\section{Introduction}

The design of a robotic platform involves the choice and configuration
of many hardware and software subsystems (actuation, energetics, perception,
control, …) in an harmonious entity in which all \emph{co-design
constraints} are respected. Because robotics is a relatively young
discipline, there is still little work towards obtaining systematic
procedures to derive optimal designs. Therefore, robot design is a
lengthly design process mainly based on empirical evaluation and trial
and error. The work presented here contributes to a theory of co-design
that allows to optimally design a robotic platform based on formal
models of the performance of its subsystems. The goal is to allow
a designer to create better designs, faster. This paper describes
the introduction of uncertainty in the theory.

\begin{figure}

\includegraphics[scale=0.33]{unc_bigproblem}
\par
\caption{\label{fig:Example1}Monotone Co-Design Problems (MCDPs) can capture
much of the complexity of the optimal robot design process. The user
defines a co-design diagram by hierarchical composition and arbitrary
interconnection of primitive ``design problems'', modeled as monotone
relations between \F{functionality} and \R{resources}. The semantics
of the MCDP of the figure is the minimization of the \R{total mass}
and \R{cost} of the platform, subject to functionality constraints
(\F{distance}, \F{payload}, \F{number of missions}). This paper
describes how to introduce uncertainty in this framework, which allows,
for example, to introduce parametric uncertainty in the definition
of components properties (e.g. specific cost of batteries).}
\end{figure}


\subsubsection*{Previous work}

In previous work~\cite{censi15monotone,censi15same,censi16codesign_sep16},
I have proposed a compositional theory for co-design. The user defines
``design problems'' (DPs) that describe the constraints for each
subsystem. These DPs can then be hierarchically composed and interconnected
to obtain the class of Monotone Co-Design Problems (MCDPs).

An example of MCDP is sketched in~\figref{Example1}. The
design problem consists in finding an optimal configuration of a UAV,
optimizing over actuators, sensors, processors, and batteries. Each
design problem (DP) is formalized as a relation between \F{functionality}
and \R{resources}. For example, the functionality of the UAV is parameterized
by three numbers: the \F{distance to travel} for each mission; the
\F{payload to transport}; the \F{number of missions} to fly. The
optimal design is defined as the one that satisfies the functionality
constraints while using the minimal amount of \R{resources} (\R{cost}
and \R{mass}).

The convenience of the MCDP framework is that the user can define
design problems for each subsystem and then compose them. The definition
of the DPs is specified using a domain-specific language that promotes
composition and code reuse; the formal specification is contained
in the supplementary materials. In the figure, the model is exploded
to show how actuation and energetics are modeled. Perception is modeled
as a relation between \F{the velocity of the platform} and the \R{power}
required. Actuation is modeled as a relation between \F{lift} and
\R{power}/\R{cost}. Batteries are described by a relation between
\F{capacity} and \R{mass}/\R{cost}. The interconnection between
these describe the ``co-design constraints'': e.g., actuators must
lift the batteries, the batteries must power the actuators. In this
example, there are different battery technologies (LiPo, etc.), each
specified by specific energy, specific cost, and lifetime, thus characterized
by a different relation between \F{capacity}, \F{number of missions}
and \R{mass} and \R{cost}.

Once the model is defined, it can be queried to obtain the \emph{minimal}
solution in terms of resources \textemdash{} here, \R{total cost}
and \R{total mass}. The output to the user is the Pareto front containing
all non-dominated solutions. The corresponding optimization problem
is, in general, nonconvex. Yet, with few assumptions, it is possible
to obtain a systematic solution procedure, and show that there exists
a dynamical system whose fixed point corresponding to the set of minimal
solutions.


\subsubsection*{Contribution}

This paper describes how to add a notion of \emph{uncertainty} in
the MCDP framework. The model of uncertainty considered is interval
uncertainty on arbitrary partial orders. For a poset $⟨\posA, ≼⟩$,
these are sets of the type $\{x ∈ \posA\colon a ≼ x ≼ b\}$.
I will show how one can introduce this type of uncertainty in the
MCDP framework by considering ordered pairs of design problems. Each
pair describes lower and upper bounds for resources usage. These \emph{uncertain
design problems} (UDPs) can be composed using series, parallel, and
feedback interconnection, just like their non-uncertain counterparts.

The user is then presented with \emph{two} Pareto fronts, corresponding
to a lower bound and an upper bound for resource consumption, in the
best case and in the worst case, respectively.

This is different from the usual formalization of ``robust optimization''~(see
e.g., \cite{bertsimas11theory,ben-tal09}), usually formulated as
a ``worst case'' analysis, in which one the uncertainty in the problem
is described by a set of possible parameters, and the optimization
problem is posed as finding the one design that is valid for all cases.

Uncertainty plays two roles: it can be used as a \emph{modeling} \emph{tool},
where the relations are uncertain because of our limited knowledge,
and it can be used as a \emph{computational} \emph{tool}, in which
we deliberately choose to consider uncertain relations as a relaxation
of the problem, to reduce the computational load, while maintaining
precise consistency guarantees. With these additions, the MCDP framework
allows to describe even richer design problems and to efficiently
solve them.


\subsubsection*{Paper organization}

Section \ref{sec:Design-Problems} and \ref{sec:Monotone-Co-Design-Problems}
summarize previous work. They give a formal definition of design problems
(DPs) and their composition, called Monotone Co-Design Problems (MCDPs).
Section~\ref{sec:UDP} through~\ref{sec:Approximation-results}
describe the notion of Uncertain Design Problem (UDP), the semantics
of their interconnection, and the general theoretical results. Section~\ref{sec:Applications}
describes three specific applications of the theory with numerical
results. The supplementary materials include detailed models written
in MCDPL and pointers to obtain the source code and a virtual machine
for reproducing the experiments.

\section{Design Problems\label{sec:Design-Problems}}

\emph{A design problem} (DP) is a monotone relation between \emph{\F{provided functionality}}
and \emph{\R{required resources}}. \F{Functionality} and \R{resources}
are complete partial orders (CPO)~\cite{davey02}, indicated by $⟨\funsp, ≼_{\funsp}⟩$
and $⟨\ressp, ≼_{\ressp}⟩$. The graphical representations
uses nodes for DPs and green (red) edges for \F{functionality} and
\R{resources}~(\figref{dp}).

\captionsideleft{\label{fig:dp}}{\includegraphics[scale=0.33]{unc_dpcartoon}}
\begin{example}
The first-order characterization of a battery is as a store of energy,
in which the \F{capacity {[}kWh{]}} is the \F{functionality} (what
the battery provides) and \R{mass} {[}kg{]} and \R{cost} {[}\${]}
are \R{resources} (what the battery requires)~(\figref{battery1}).
\end{example}
\captionsideleft{\label{fig:battery1}}{\includegraphics[scale=0.33]{unc_battery_masscost}}

\noindent In general, fixed a functionality $\fun ∈ \funsp$, there
will be multiple resources in $\ressp$ sufficient to perform the
functionality that are incomparable with respect to $ ≼_{\ressp}$.
For example, in the case of a battery one might consider different
battery technologies that are incomparable in the \R{mass}/\R{cost}
resource space~(\figref{multiple}).

\captionsideleft{\label{fig:multiple}}{\includegraphics[scale=0.33]{reits2_battery2_h}}

A subset with ``minimal'', ``incomparable'' elements is called
``antichain''. This is the mathematical formalization of what is
informally called a ``Pareto front''.


\begin{defn}
An \emph{antichain} $S$ in a poset $⟨\posA, ≼⟩$
is a subset of $\posA$ such that no element of $S$ dominates another
element: if $x,y ∈ S$ and $x ≼ y$, then $x=y$.
\end{defn}
\begin{lem}
Let $\antichains\posA$ be the set of antichains of $\posA$. $\antichains\posA$
is a poset itself, with the partial order $ ≼_{\antichains\posA}$
defined as
\begin{equation}
S₁ ≼_{\antichains\posA}S₂␣≡␣ ↑ S₁⊇⌑ ↑ S₂.\label{eq:orderantichains}
\end{equation}
\end{lem}
\begin{defn}
\label{def:A-monotone-design}A\emph{ monotone design problem~}(DP)
is a tuple $⟨\funsp,\ressp,\ftor⟩$ such
that $\funsp$ and $\ressp$ are CPOs, and ${\colH\ftor}:{\colF\fun}⟶{\colR\antichains\ressp}$
is a monotone and Scott-continuous function~(\cite{gierz03continuous}
or \cite[Definition 11]{censi16codesign_sep16}).
\end{defn}
\captionsideleft{}{\includegraphics[scale=0.33]{unc_ftor}}

\noindent Each functionality $\fun$ corresponds to an antichain
of resources $\ftor(\fun) ∈ \Aressp$~(\figref{antichain}).

\captionsideleft{\label{fig:antichain}}{\includegraphics[scale=0.33]{unc_ftorgraph}}

\noindent Monotonicity implies that, if the functionality is increased,
then the required resources increase as well~(\figref{antichain2}).

\captionsideleft{\label{fig:antichain2}}{\includegraphics[scale=0.33]{unc_ftorgraph2}}


\section{Monotone Co-Design Problems \label{sec:Monotone-Co-Design-Problems}}

A Monotone Co-Design Problem is a multigraph of DPs. Two DPs can be
connected by adding an edge~(\figref{connection}). The semantics
of the interconnection is that the resources required by the first
DP must be provided by the second DP. Mathematically, this is a partial
order inequality constraint of the type $\res₁ ≼\fun₂$.
Self-loops are allowed as well.

\captionsideleft{\label{fig:connection}}{\includegraphics[scale=0.33]{unc_connection}}
\begin{example}
The MCDP in~\figref{example} is the interconnection of 3
DPs $\ftorₐ,\ftor_{b},\ftor_{c}.$ The semantics of the MCDP as
an optimization problem is shown in~\figref{example-semantics}.\\
\captionsideleft{\label{fig:example}}{\hspace{-7mm}\includegraphics[scale=0.33]{unc_atoms_g_v_graph}}\\
\captionsideleft{\label{fig:example-semantics}}{\hspace{-2mm}\includegraphics[scale=0.33]{unc_semantics}}
\end{example}
To describe the interconnection, the obvious choice is to describe
it as a graph, as a set of nodes and of edges. For our goals, it is
more convenient to use an algebraic definition. In the algebraic definition,
the graph is a represented by a tree, where the leaves are the nodes,
and the junctions are one of three operators ($\dpseries,\dppar,\dploop$),
as in~\figref{series-par-loop}.

Similar constructions are widespread in computer science. One can
see this in the spirit of series-parallel graphs (see, e.g.,~\cite{duffin65topology}),
with an additional feedback operator to be able to represent all graphs.
Equivalently, we are defining a symmetric traced monoidal category
(see, e.g.,~\cite{joyal96traced} or~\cite{spivak14category} for
an introduction); note that the $\dploop$ operator is related to
the ``trace'' operator but not exactly equivalent, though they can
be defined in terms of each other. An equivalent construction for
network processes is given in Stefanescu~\cite{stefanescu00}.

\begin{figure}[H]
\subfloat[$\dpseries(a,b)$]{\includegraphics[scale=0.33]{unc_dpseries}}
\subfloat[$\dppar(a,b)$]{\includegraphics[scale=0.33]{unc_dppar}}
\subfloat[$\dploop(a)$]{\includegraphics[scale=0.33]{unc_dploop}}
\caption{\label{fig:series-par-loop}The three operators used in the inductive
definition of MCDPs.}
\end{figure}

Let us use a standard definition of ``operators'', ``terms'',
and ``atoms'' (see, e.g., ~\cite[p.41]{jezek08}). Given a set
of operators $\ops$ and a set of atoms $\atoms$, let $\terms(\ops,\atoms)$
be the set of all inductively defined expressions. For example, if
the operator set contains only an operator $f$ of \emph{arity} 1,
and there is only one atom $a$, then the terms are $\terms(\{f\},\{a\})=\{a,f(a),f(f(a)),…\}.$



\begin{defn}[Algebraic definition Monotone Co-Design Problems]
\label{def:MCDP-algebraic}An MCDP is a tuple $⟨\atoms,\atree,\val⟩$,
where:
\begin{enumerate}
\item $\atoms$ is any set of atoms, to be used as labels.
\item The term $\atree$ in the $\{\dpseries,\dppar,\dploop\}$ algebra
describes the structure of the graph:
\[
\atree ∈ \terms(\{\dpseries,\dppar,\dploop\},\atoms).
\]
\item The \emph{valuation} $\val$ is a map $\val:\atoms⟶\dpsp$
that assigns a DP to each atom.
\end{enumerate}
\end{defn}
\begin{example}
The MCDP in~\figref{example} can be described by the atoms
$\atoms=\{a,b,c\}$, the term $\atree=\dploop(\dpseries(a,\dppar(b,c)),$
plus the valuation $\val:\{a⟼\ftorₐ,b⟼\ftor_{b},c⟼\ftor_{c}\}.$
The tuple $⟨\atoms,\atree,\val⟩$ for this
example is shown in \figref{example-b}.
\end{example}
\captionsideleft{\label{fig:example-b}}{\includegraphics[scale=0.33]{unc_atoms_g_v}}
\begin{example}
A sketch of the algebraic representation for part of the example in~\figref{Example1}
is shown in~\figref{tree2}. The supplementary materials contain
more detailed visualizations of the trees for the numerical examples,
which take too much space for including in this paper.
\end{example}
\captionsideleft{\label{fig:tree2}}{\includegraphics[scale=0.33]{unc_tree}}


\subsection{Semantics of MCDPs}

We can now define the \emph{semantics} of an MCDP. The \emph{semantics}
is a function $\dpsem$ that, given an algebraic definition of an
MCDP, returns a $\dpsp$. Thanks to the algebraic definition, to
define $\dpsem$, we need to only define what happens in the base
case (equation~\ref{eq:base}), and what happens for each operator
$\dpseries,\dppar,\dploop$ (equations~\ref{eq:series}\textendash \ref{eq:loop}).
\begin{defn}[Semantics of MCDP]
\label{def:dpsem}Given an MCDP in algebraic form $⟨\atoms,\atree,\val⟩$,
the semantics
\[
\dpsem⟦⟨\atoms,\atree,\val⟩⟧ ∈ \dpsp
\]
is defined as follows:

\vspace{-5mm}\adjustbox{max width=8.6cm}{{\small{}}
\begin{minipage}[t]{1.05\columnwidth}
{\small{}
\begin{align}
\dpsem⟦⟨\atoms,a,\val⟩⟧& ≐\val(a),\qquad\text{for all}␣a ∈ \atoms,\label{eq:base}\\
\dpsem⟦⟨\atoms,\dpseries(\atree₁,\atree₂),\val⟩⟧& ≐\dpsem⟦⟨\atoms,\atree₁,\val⟩⟧⌑\opseries⌑\dpsem⟦⟨\atoms,\atree₂,\val⟩⟧,\label{eq:series}\\
\dpsem⟦⟨\atoms,\dppar(\atree₁,\atree₂),\val⟩⟧& ≐\dpsem⟦⟨\atoms,\atree₁,\val⟩⟧⌑\oppar⌑\dpsem⟦⟨\atoms,\atree₂,\val⟩⟧,\label{eq:par}\\
\dpsem⟦⟨\atoms,\dploop(\atree),\val⟩⟧& ≐\dpsem⟦⟨\atoms,\atree,\val⟩⟧^{\oploop}.\label{eq:loop}
\end{align}
}
\end{minipage}{\small{}}}{\small \par}
\end{defn}
The operators $\opseries,\oppar,\oploop$ are defined in~\prettyref{def:opseries}\textendash \prettyref{def:oploop}.
Please see~\cite[Section VI]{censi16codesign_sep16} for details
about the interpretation of these operators and how they are derived.

The $\oppar$ operator is a regular product in category theory: we
are considering all possible combinations of resources required by $\ftor₁$
and $\ftor₂$.
\begin{defn}[Product operator $\oppar$]
\label{def:opmaps}For two maps $\ftor₁\colon\funsp₁⟶\Aressp₁$
and $\ftor₂\colon\funsp₂⟶\Aressp₂$, define
\begin{align*}
\ftor₁\oppar\ftor₂:(\funsp₁×\funsp₂) & ⟶\antichains(\ressp₁×\ressp₂),\\
⟨\fun₁,\fun₂⟩ & ⟼\ftor₁(\fun₁)\acprod\ftor₂(\fun₂),
\end{align*}
where $\acprod$ is the product of two antichains.
\end{defn}
The $\opseries$ operator is similar to a convolution: fixed $\fun₁$,
one evaluates the resources $\res₁ ∈ \ftor₁(\fun)$, and for
each $\res₁$, $\ftor₂(\res₁)$ is evaluated. The $\Min$
operator then chooses the minimal elements.
\begin{defn}[Series operator $\opseries$]
\label{def:opseries}For two maps $\ftor₁\colon\funsp₁⟶\Aressp₁$
and $\ftor₂\colon\funsp₂⟶\Aressp₂$, if $\ressp₁=\funsp₂$
, define
\begin{align*}
{\displaystyle \ftor₁\opseries\ftor₂\colon\funsp₁} & ⟶\Aressp₂,\\
\ftor₁ & ⟼\Min_{ ≼_{\ressp₂}}\bigcup_{\res₁ ∈ \ftor₁(\fun)}\ftor₂(\res₁).
\end{align*}

\end{defn}


The dagger operator $\oploop$ is actually a standard operator used
in domain theory (see, e.g., \cite[II-2.29]{gierz03continuous}).
\begin{defn}[Loop operator $\oploop$]
\label{def:oploop}For a map $\ftor:\funsp₁×\funsp₂⟶\Aressp$,
define
\begin{align}
\ftor^{\oploop}:\funsp₁ & ⟶\Aressp,\nonumber \\
\fun₁ & ⟼\lfp(Ψ_{\fun₁}^{\ftor}),\label{eq:lfp}
\end{align}
where $\lfp$ is the least-fixed point operator, and $Ψ_{\fun₁}^{\ftor}$
is defined as
\begin{align*}
Ψ_{\fun₁}^{\ftor}:\Aressp & ⟶\Aressp,\\
{\colR R} & ⟼\Min_{ ≼_{\ressp}}\bigcup_{\res ∈ {\colR R}}\ftor(\fun₁,\res)␣∩ ↑\res.
\end{align*}
\end{defn}

\subsection{Solution of MCDPs}

\prettyref{def:dpsem} gives a way to evaluate the map $\ftor$ for
the graph, given the maps $\{\ftor{}ₐ\mid a ∈ \atoms\}$ for the
leaves. Following those instructions, we can compute $\ftor(\fun)$,
and thus find the minimal resources needed for the entire MCDP.
\begin{example}
The MCDP in~\figref{example} is so small that we can do this
explicitly. From~\prettyref{def:dpsem}, we can compute the semantics
as follows:
\begin{align*}
\ftor & =\dpsem⟦⟨\atoms,\dploop(\dpseries(a,\dppar(b,c)),\val⟩⟧\\
 & =(\ftorₐ⌑\opseries⌑(\ftor_{b}⌑\oppar⌑\ftor_{c}))^{\oploop}.
\end{align*}
Substituting the definitions~\ref{def:opmaps}\textendash \ref{def:oploop}
above, one finds that $\ftor(\fun)=\lfp(Ψ_{\fun}),$
with
\begin{align*}
Ψ_{\fun}:\Aressp & ⟶\Aressp,\\
{\colR R} & ⟼\bigcup_{\res ∈ {\colR R}}\Big[\Min_{ ≼} ↑\bigcup_{s ∈ \ftorₐ(\fun₁,\res)}\ftor_{b}(s)\acprod\ftor_{c}(s)\Big]␣∩ ↑\res.
\end{align*}
The least fixed point equation can be solved using Kleene's algorithm~\cite[CPO Fixpoint theorem I, 8.15]{davey02}.
A dynamical system that computes the set of solutions is given by
\[
\begin{cases}
{\colR R}_{0} & arrow\{⊥_{\ressp}\},\\
{\colR R}_{k+1} & arrowΨ_{\fun}({\colR R}_{k}).
\end{cases}
\]
The limit $\sup{\colR R}_{k}$ is the set of minimal solutions, which
might be an empty set if the problem is unfeasible.

This dynamical system is a proper algorithm only if each step can
be performed with bounded computation. An example in which this is
not the case are relations that give an infinite number of solutions
for each functionality. For example, the very first DP appearing in~\figref{Example1}
corresponds to the relation ${\colF\text{travel distance}}≤{\colR\text{velocity}}×{\colR\text{endurance}},$
for which there are infinite numbers of pairs $⟨{\colR\text{velocity}},{\colR\text{endurance}}⟩$
for each value of ${\colF\text{travel distance}}$. The machinery
developed in this paper will make it possible to deal with these infinite-cardinality
relations by relaxation.
\end{example}

\section{Uncertain Design Problems\label{sec:UDP}}

We now consider the introduction of uncertainty. This section describes
objects called Uncertain DPs (UDPs), which are an ordered pair of
DPs. Each pair can be interpreted as upper and lower bounds for resource
consumptions~(\figref{udp-bounds}).

\captionsideleft{\label{fig:udp-bounds}}{\includegraphics[scale=0.33]{unc_ftorLU}}

We will be able to propagate this interval uncertainty through an
arbitrary interconnection of DPs. The result presented to the user
will be a \emph{pair} of antichains \textemdash{} a lower and an upper
bound for the resource consumption.

\subsection{Partial order $\dpleq$}

Being able to provide both upper and lower bounds comes from the fact
that in this framework everything is ordered \textendash{} there are
a poset of resources, lifted to posets of antichains, which is lifted
to posets of DPs, and finally, to the poset of uncertain DPs.

The first step is defining a partial order $\dpleq$ on $\dpsp$.
\begin{defn}[Partial order $\dpleq$]
Consider two DPs $\ftor₁,\ftor₂:\funsp⟶\Aressp$.
The DP $\ftor₁$ precedes $\ftor₂$ if it requires fewer resources
for all functionality $\fun$:
\[
\ftor₁\dpleq\ftor₂⍽≡⍽\ftor₁(\fun) ≼_{\Aressp}\ftor₂(\fun),␣\text{for all }\fun ∈ \funsp.
\]
\end{defn}
\captionsideleft{}{\includegraphics[scale=0.33]{unc_dporder}\includegraphics[scale=0.33]{unc_dpleq2}}

In this partial order, there is both a top $⊤_{\dpsp}$ and a
bottom $⊥_{\dpsp}$, defined as follows:

\vspace{-5mm}

\begin{minipage}[t]{0.4\columnwidth}
\begin{align*}
⊥_{\dpsp}:\funsp & ⟶\Aressp,\\
\fun & ⟼\{⊥_{\ressp}\}.
\end{align*}

\end{minipage}
\begin{minipage}[t]{0.4\columnwidth}
\begin{align}
⊤_{\dpsp}:\funsp & ⟶\Aressp,\nonumber \\
\fun & ⟼\emptyset.\label{eq:top}
\end{align}

\end{minipage}

\smallskip{}

$⊥_{\dpsp}$~means that any functionality can be done with zero
resources, and $⊤_{\dpsp}$ means that the problem is always infeasible
(``the set of feasible resources is empty'').

\subsection{Uncertain DPs (UDPs)}
\begin{defn}[Uncertain DPs]
An Uncertain DP (UDP) $\boldsymbol{u}$ is a pair of DPs $⟨\udpL\boldsymbol{u},\udpU\boldsymbol{u}⟩$
such that $\udpL\boldsymbol{u}\dpleq\udpU\boldsymbol{u}$.
\end{defn}
\captionsideleft{}{\includegraphics[scale=0.33]{unc_udpdef}}


\subsection{Order on UDP}
\begin{defn}[Partial order $\udpleq$]
A UDP $\udpa$ precedes another UDP $\udpb$ if the interval $[\udpL\udpa,\udpU\udpa]$
is contained in the interval $[\udpL\udpa,\udpU\udpa]$ (\figref{udpspace}):
\[
\udpa\udpleq\udpb⍽≡⍽\udpL\udpb\dpleq\udpL\udpa\dpleq\udpU\udpa\dpleq\udpU\udpb.
\]
\end{defn}
\captionsideleft{\label{fig:udpspace}}{\includegraphics[scale=0.33]{unc_udpab2}\includegraphics[scale=0.33]{unc_udpab}}

The partial order $\udpleq$ has a top $⊤_{\udpsp}=⟨⊥_{\dpsp},⊤_{\dpsp}⟩.$
This pair describes maximum uncertainty about the DP: we do not know
if the DP is feasible with 0 resources~($⊥_{\dpsp}$), or if it
is completely infeasible~($⊤_{\dpsp}$).

\subsection{DPs as degenerate UDPs}

A DP $\ftor$ is equivalent to a degenerate UDP $⟨\ftor,\ftor⟩$.

A UDP $\boldsymbol{u}$ is a bound for a DP $\ftor$ if $\boldsymbol{u}\udpleq⟨\ftor,\ftor⟩$,
or, equivalently, if $\udpL\boldsymbol{u}\udpleq\ftor\udpleq\udpU\boldsymbol{u}$.

\captionsideleft{\label{fig:pyr1}}{\hspace{-9mm}\includegraphics[scale=0.33]{unc_dpcones2}\includegraphics[scale=0.33]{unc_dpcones}}

A pair $⟨\ftor,\ftor⟩$ is a minimal element of $\udpsp$,
because it cannot be dominated by any other. Thus, we can imagine
the space $\udpsp$ as a pyramid~(\figref{pyr1}), with the
space $\dpsp$ forming the base. The base represents non-uncertain
DPs. The top of the pyramid is $⊤_{\udpsp}$, which represents
maximum uncertainty.

\section{Interconnection of Uncertain Design Problems\label{sec:UMCDP}}

We now define the interconnection of UDPs, in an equivalent way to
the definition of MCDPs. The only difference between \prettyref{def:MCDP-algebraic}
and~\prettyref{def:umcdp} below is that the valuation assigns to
each atom an UDP, rather than a~DP.
\begin{defn}[Algebraic definition of UMCDPs]
\label{def:umcdp}An Uncertain MCDP (UMCDP) is a tuple $⟨\atoms,\atree,\val⟩$,
where $\atoms$ is a set of atoms, $\atree ∈ \terms(\{\dpseries,\dppar,\dploop\},\atoms)$
is the algebraic representation of the graph, and $\val:\atoms⟶\udpsp$
is a valuation that assigns to each atom a UDP.
\end{defn}


Next, the semantics of a UMCDP is defined as a map $\udpsem$ that
computes the UDP. \prettyref{def:semantics-udp}~below is analogous
to~\prettyref{def:dpsem}.
\begin{defn}[Semantics of UMCDPs]
\label{def:semantics-udp}Given an UMCDP $⟨\atoms,\atree,\val⟩$,
the semantics function $\udpsem$ computes a UDP
\[
\udpsem⟦⟨\atoms,\atree,\val⟩⟧ ∈ \udpsp,
\]
and it is recursively defined as follows:

\adjustbox{max width=8.6cm}{
\noindent\begin{minipage}[t]{1\columnwidth}
\[
\udpsem⟦⟨\atoms,a,\val⟩⟧=\val(a),\qquad\text{for all}␣a ∈ \atoms.
\]
\begin{align*}
\udpL\udpsem⟦⟨\atoms,\dpseries(\atree₁,\atree₂),\val⟩⟧& =(\udpL\udpsem⟦⟨\atoms,\atree₁,\val⟩⟧)⌑\opseries⌑(\udpL\udpsem⟦⟨\atoms,\atree₂,\val⟩⟧),\\
\udpU\udpsem⟦⟨\atoms,\dpseries(\atree₁,\atree₂),\val⟩⟧& =(\udpU\udpsem⟦⟨\atoms,\atree₁,\val⟩⟧)⌑\opseries⌑(\udpU\udpsem⟦⟨\atoms,\atree₂,\val⟩⟧),
\end{align*}
\begin{align*}
\udpL\udpsem⟦⟨\atoms,\dppar(\atree₁,\atree₂),\val⟩] & =(\udpL\udpsem⟦⟨\atoms,\atree₁,\val⟩⟧)␣\oppar␣(\udpL\udpsem⟦⟨\atoms,\atree₂,\val⟩⟧),\\
\udpU\udpsem⟦⟨\atoms,\dppar(\atree₁,\atree₂),\val⟩] & =(\udpU\udpsem⟦⟨\atoms,\atree₁,\val⟩⟧)␣\oppar␣(\udpU\udpsem⟦⟨\atoms,\atree₂,\val⟩⟧),
\end{align*}
\begin{align*}
\udpL\udpsem⟦⟨\atoms,\dploop(\atree),\val⟩⟧& =(\udpL\udpsem⟦⟨\atoms,\atree,\val⟩⟧)^{\oploop},\\
\udpU\udpsem⟦⟨\atoms,\dploop(\atree),\val⟩⟧& =(\udpU\udpsem⟦⟨\atoms,\atree,\val⟩⟧)^{\oploop}.
\end{align*}

\end{minipage}}
\end{defn}
The operators $\oploop,\opseries,\oppar$ are defined in \prettyref{def:opseries}\textendash \prettyref{def:oploop}.

\section{Approximation results\label{sec:Approximation-results}}

The main result of this section is a relaxation result stated as \prettyref{thm:udpsem-monotone}
below.

\subsubsection*{Informal statement}

Suppose that we have an MCDP composed of many DPs, and one of those
is $\ftorₐ$~(\figref{consider1}).

\captionsideleft{\label{fig:consider1}}{\includegraphics[scale=0.33]{unc_f1}}

\noindent Suppose that we can find two DPs $\boldsymbol{\mathsf{L}}$,
$\boldsymbol{\mathsf{U}}$ that bound the DP $\ftorₐ$~(\figref{consider2}).

\captionsideleft{\label{fig:consider2}}{\includegraphics[scale=0.33]{unc_f2}}

\noindent This can model either (a)~uncertainty in our knowledge
of $\ftorₐ$, or (b)~a relaxation that we willingly introduce.

\noindent Then we can consider the pair $\boldsymbol{\mathsf{L}}$,
$\boldsymbol{\mathsf{U}}$ as a UDP $⟨\boldsymbol{\mathsf{L}},\boldsymbol{\mathsf{U}}⟩$
and we can plug it in the original MCDP in place of $\ftorₐ$~(\figref{luinside}).
\begin{center}
\captionsideleft{\label{fig:luinside}}{\includegraphics[scale=0.33]{unc_f3}}
\par\end{center}

\noindent Given the semantics of interconnections of UDPs (\prettyref{def:semantics-udp}),
this is equivalent to considering a pair of MCDPs, in which we choose
either the lower bound or the upper bound~(\figref{pair}).
\begin{center}
\captionsideleft{\label{fig:pair}}{\includegraphics[scale=0.33]{unc_result}}
\par\end{center}

\noindent We can then show that the solution of the original MCDP
is bounded below and above by the solution of the new pair of MCDPs~(\figref{domin}).
\begin{center}
\captionsideleft{\label{fig:domin}}{\includegraphics[scale=0.33]{unc_f4}}
\par\end{center}

This result generalizes for any number of substitutions.

\subsubsection*{Formal statement}

First, we define a partial order on the valuations. A valuation precedes
another if it gives more information on each DP.
\begin{defn}[Partial order $≼_{V}$ on valuations]
\label{def:For-two-valuations,}For two valuations $\val₁,\val₂:\atoms⟶\udpsp$,
say that $\val₁ ≼_{V}\val₂$ if $\val₁(a)\udpleq\val₂(a)$
for all $a ∈ \atoms$.
\end{defn}
At this point, we have enough machinery in place that we can simply
state the result as ``the semantics is monotone in the valuation''.
\begin{thm}[$\udpsem$ is monotone in the valuation]
\label{thm:udpsem-monotone}If $\val₁ ≼_{V}\val₂$, then
\[
\udpsem⟦⟨\atoms,\atree,\val₁⟩⟧\udpleq\udpsem⟦⟨\atoms,\atree,\val₂⟩⟧.
\]
\end{thm}
The proof is given in Appendix~\prettyref{subsec:proof-main-result}
in the supplementary materials.

This result says that we can swap any DP in a MCDP with a UDP relaxation,
obtain a UMCDP, which we can solve to obtain inner and outer approximations
to the solution of the original MCDP. This shows that considering
uncertainty in the MCDP framework is easy; as the problem reduces
to solving a pair of problems instead of one. This

The rest of the paper consists of applications of this result.

\section{Applications\label{sec:Applications}}

This section shows three example applications of the theory:
\begin{enumerate}
\item The first example deals with \emph{parametric uncertainty}.
\item The second example deals with the idea of relaxation of a scalar relation.
This is equivalent to accepting a tolerance for a given variable,
in exchange for a reduced number of iterations.
\item The third example deals with the relaxation of relations with infinite
cardinality. In particular it shows how one can obtain consistent
estimates with a finite and prescribed amount of computation.
\end{enumerate}

\subsection{Application: Dealing with Parametric Uncertainty\label{sec:Application-uncertainty}}

To instantiate the model in~\figref{Example1}, we need to
obtain numbers for energy density, specific cost, and operating life
for all batteries technologies we want to examine.

By browsing Wikipedia, one can find the figures in~\prettyref{tab:batteries}.

\begin{table}[H]

\caption{\label{tab:batteries}Specifications of common batteries technologies}
\par
{\footnotesize{}}
\begin{tabular}{crr@{\extracolsep{0pt}.}lr}
\multirow{2}{*}{{\footnotesize{}\tableColors}\emph{\footnotesize{}technology}} & \emph{\footnotesize{}energy density} & \multicolumn{2}{c}{\emph{\footnotesize{}specific cost}} & \emph{\footnotesize{}operating life}\tabularnewline
 & {\footnotesize{}{[}Wh/kg{]}} & \multicolumn{2}{c}{{\footnotesize{}{[}Wh/\${]}}} & \# cycles\tabularnewline
{\footnotesize{}NiMH} & {\footnotesize{}100} & {\footnotesize{}3}&{\footnotesize{}41 } & {\footnotesize{}500 }\tabularnewline
{\footnotesize{}NiH2} & {\footnotesize{}45} & {\footnotesize{}10}&{\footnotesize{}50 } & {\footnotesize{}20000}\tabularnewline
{\footnotesize{}LCO} & {\footnotesize{}195} & {\footnotesize{}2}&{\footnotesize{}84} & {\footnotesize{}750}\tabularnewline
{\footnotesize{}LMO} & {\footnotesize{}150} & {\footnotesize{}2}&{\footnotesize{}84 } & {\footnotesize{}500}\tabularnewline
{\footnotesize{}NiCad} & {\footnotesize{}30} & {\footnotesize{}7}&{\footnotesize{}50 } & {\footnotesize{}500}\tabularnewline
{\footnotesize{}SLA} & {\footnotesize{}30} & {\footnotesize{}7}&{\footnotesize{}00} & {\footnotesize{}500}\tabularnewline
{\footnotesize{}LiPo} & {\footnotesize{}150} & {\footnotesize{}2}&{\footnotesize{}50} & {\footnotesize{}600}\tabularnewline
{\footnotesize{}LFP} & {\footnotesize{}90} & {\footnotesize{}1}&{\footnotesize{}50} & {\footnotesize{}1500}\tabularnewline
\end{tabular}{\footnotesize \par}
\end{table}

Should we trust those figures? Fortunately, we can easily deal with
possible mistrust by introducing uncertain DPs.

Formally, we replace the DPs for\emph{ energy density}, \emph{specific
cost}, \emph{operating life} in~\figref{Example1} with the
corresponding Uncertain DPs with a configurable uncertainty. We can
then solve the UDPs to obtain a lower bound and an upper bound to
the solutions that can be presented to the user.

\figref{unc_battery_uncertain} shows the relation between
the provided \F{endurance} and the minimal \R{total mass} required,
when using uncertainty of $5\%$, $10\%$, $25\%$ on the numbers
above. Each panel shows two curves: the lower bound (best case analysis)
and the upper bound (worst case analysis). In some cases, the lower
bound is feasible, but the upper bound is not. For example, in panel~\emph{b},
for 10\% uncertainty, we can conclude that, notwithstanding the uncertainty,
there exists a solution for endurance $≤1.3⌑\text{hours}$, while
for higher endurance, because the upper bound is infeasible, we cannot
conclude that there is a solution \textemdash{} though, because the
lower bound is feasible, we cannot conclude that a solution does not
exist~(\figref{unc_battery_uncertain}c).
\begin{center}
\begin{figure}[H]

\includegraphics[scale=0.33]{unc_battery_uncertain}
\par
\caption{\label{fig:unc_battery_uncertain}Uncertain relation between \F{endurance}
and the minimal \R{total mass} required, obtained by solving the
example in \figref{Example1} for different values of the uncertainty
on the characteristics of the batteries. As the uncertainty increases,
there are no solutions for the worst case.}
\end{figure}
\par\end{center}

\subsection{Application: Introducing Tolerances\label{sec:Application-tolerance}}

Another application of the theory is the introduction of tolerances
for any variable in the optimization problem. For example, one might
not care about the variations of the battery mass below, say, $1⌑\text{g}$.
One can then introduce a $±1⌑\text{\ensuremath{\text{g}} }$ uncertainty
in the definition of the problem by adding a UDP hereby called ``uncertain
identity''.


\subsubsection{The uncertain identity}

Let $α>0$ be a step size. Define $\ufloor_{α}$ and $\uceil_{α}$
to be the floor and ceil with step size $α$~(\figref{identity_approximation}).
By construction, $\ufloor_{α}\dpleq\mathsf{Id}\dpleq\uceil_{α}.$

\begin{figure}[H]
\subfloat{\includegraphics[scale=0.33]{unc_approx1a}}
\subfloat{\includegraphics[scale=0.33]{unc_approx1b}}
\subfloat{\includegraphics[scale=0.33]{unc_approx1c}}
\caption{\label{fig:identity_approximation}The identity and its two relaxations $\ufloor_{α}$
and $\uceil_{α}$.}
\end{figure}

Let $\UId_{α}≐⟨\ufloor_{α},\uceil_{α}⟩$
be the ``uncertain identity''. For $0<α<β$, it holds
that
\[
\mathsf{Id}\poslt_{\udpsp}\UId_{α}\poslt_{\udpsp}\UId_{β}.
\]
Therefore, the sequence $\UId_{α}$ is a descending chain that
converges to $\mathsf{Id}$ as $α⟶0$~(\figref{other}).

\captionsideleft{\label{fig:other}}{\includegraphics[scale=0.33]{unc_uid1}\includegraphics[scale=0.33]{unc_uid2}}


\subsubsection{Approximations in MCDP}

We can take any edge in an MCDP and apply this relaxation. Formally,
we first introduce an identity $\mathsf{Id}$ and then relax it using $\UId_{α}$~(\figref{introduce}).

\captionsideleft{\label{fig:introduce}}{\includegraphics[scale=0.33]{unc_introduce}}

Mathematically, given an MCDP $⟨\atoms,\atree,\val⟩$,
we generate a UMCDP $⟨\atoms,\atree,\val_{α}⟩$,
where the new valuation $\val_{α}$ agrees with $\val$ except
on a particular atom $a ∈ \atoms$, which is replaced by the series
of the original $\val(a)$ and the approximation $\text{UId}_{α}$:
\begin{align*}
\val_{α}(a) & ≐\dpseries(\UId_{α},\val(a))
\end{align*}
Call the original and approximated DPs $\dprob$ and $\dprob_{α}$:
\[
\begin{array}{ccc}
\dprob≐\udpsem ⟦⟨\atoms,\atree,\val⟩⟧, &  & \dprob{}_{α}≐\udpsem⟦⟨\atoms,\atree,\val_{α}⟩⟧.\end{array}
\]
Because $\val ≼_{V}\val_{α}$ (in the sense of~\prettyref{def:For-two-valuations,}),
\prettyref{thm:udpsem-monotone} implies that
\[
\dprob\udpleq\dprob_{α}.
\]
This means that we can solve $\udpL\dprob_{α}$ and $\udpU\dprob_{α}$
and obtain upper and lower bounds for $\dprob$. Furthermore, by
varying $α$, we can construct an approximating sequence of
DPs whose solution will converge to the solution of the original MCDP.


\paragraph*{Numerical results}

This procedure was applied to the example model in~\figref{Example1}
by introducing a tolerance to the ``power'' variable for the actuation.
The tolerance $α$ is chosen at logarithmic intervals between $0.01⌑\text{mW}$
and $1⌑\text{W}$. \figref{mass}~shows the solutions of
the minimal mass required for $\udpL\dprob_{α}$ and $\udpU\dprob_{α}$,
as a function of $α$. \figref{mass} confirms the consistency
results predicted by the theory. First, if the solutions for both $\udpL\dprob_{α}$
and $\udpU\dprob_{α}$ exist, then they are ordered ($\udpL\dprob_{α}(\fun) ≼\udpU\dprob_{α}(\fun)$).
Second, as $α$ decreases, the interval shrinks. Third, the
bounds are consistent (the solution for the original DP is always
contained in the bound).

\begin{figure}[H]
\subfloat[\label{fig:mass}]{\includegraphics[scale=0.4]{unc_approx2a}}
\subfloat[\label{fig:num_iterations}]{\includegraphics[scale=0.4]{unc_approx2c}}
\caption{Results of model in \figref{Example1} when tolerance is applied
to the actuation \R{power} resource. Please see the supplementary
materials for more details.}
\end{figure}

Next, it is interesting to consider the computational complexity.
\figref{num_iterations}~shows the number of iterations as
a function of the resolution $α$, and the trade-off of the
uncertainty of the solution and the computational resources spent.
This shows that this approximation scheme is an effective way to reduce
the computation load while maintaining a consistent estimate.


\subsection{Application: Relaxation for relations with infinite cardinality\label{sec:Application-relax}}

Another way in which uncertain DPs can be used is to construct approximations
of DPs that would be too expensive to solve exactly. For example,
consider a relation like
\begin{equation}
{\colF\text{travel\_distance}}≤{\colR\text{velocity}}×{\colR\text{endurance}},\label{eq:qun}
\end{equation}
which appears in the model in \figref{Example1}. If we take
these three quantities in \prettyref{eq:qun} as belonging to $ℝ$,
then, for each value of the \F{travel distance}, there are infinite
pairs of $⟨{\colR\text{velocity}},{\colR\text{endurance}}⟩$
that are feasible. (On a computer, where the quantities could be represented
as floating point numbers, the combinations are properly not ``infinite'',
but, still, extremely large.)

We can avoid considering all combinations by creating a sequence of
uncertain DPs that use finite and prescribed computation.

\subsubsection{Relaxations for addition}

Consider a monotone relation between some functionality $\fun₁ ∈ ℝ₊$ and
resources $\res₁,\res₂ ∈ ℝ₊$ described by the constraint that
$\fun₁≤\res₁+\res₂$ (\figref{example-invplus}). For example, this could
represent the case where there are two batteries providing the power $\fun₁$,
and we need to decide how much to allocate to the first~($\res₁$) or the
second~($\res₂$).

\captionsideleft{\label{fig:example-invplus}}{\includegraphics[scale=0.33]{unc_plusinv}}

The formal definition of this constraint as an DP is
\begin{align*}
\overline{+}:{\colFℝ₊} & ⟶{\colR\antichains(ℝ₊×ℝ₊)},\\
\fun₁ & ⟼\{⟨x,\fun₁-x⟩\mid x ∈ ℝ₊\}.
\end{align*}
Note that, for each value $\fun₁$, $\overline{+}(\fun₁)$
is a set of infinite cardinality.

We will now define two sequences of relaxations for $\overline{+}$
with a fixed number of solutions $n≥1$.

\subsubsection*{Using uniform sampling}

We will first define a sequence of UDPs $Sₙ$ based on uniform
sampling. Let $\udpU Sₙ$ consist of $n$ points sampled on the
segment with extrema $⟨0,\fun₁⟩$ and $⟨\fun₁,0⟩$.
For $\udpL Sₙ$, sample $n+1$ points on the segment and take
the \emph{meet} of successive points~(\figref{make_lower}).
\begin{center}
\captionsideleft{\label{fig:make_lower}}{\includegraphics[scale=0.33]{unc_make_lower}}
\par\end{center}

The first elements of the sequences are shown in~\figref{approx_invplus}.
One can easily prove that $\udpL Sₙ\dpleq\overline{+}\dpleq\udpU Sₙ$,
and thus $Sₙ$ is a relaxation of $\overline{+}$, in the sense
that $\overline{+}\udpleq Sₙ$. Moreover, $Sₙ$ converges to
$\overline{+}$ as $n⟶∞$.
\begin{center}
\begin{figure}[H]
\includegraphics[scale=0.33]{unc_sampling}\caption{\label{fig:approx_invplus}Approximations to $\overline{+}$ using
the uniform sampling sequence $Sₙ$. }
\end{figure}
\par\end{center}

However, note that the convergence is not monotonic: $S_{n+1}{\not ≼}_{\udpsp}Sₙ.$
The situation can be represented graphically as in~\figref{notchain}.
The sequence $Sₙ$ eventually converges to $\overline{+}$, but
it is not a descending chain. This means that it is not true, in general,
that the solution to the MCDP obtained by plugging in $S_{n+1}$
gives smaller bounds than $Sₙ$.

\subsubsection*{Relaxation based on Van Der Corput sequence}

We can easily create an approximation sequence $V:ℕ⟶\udpsp$
that converges monotonically using Var Der Corput (VDC) sampling~\cite[Section 5.2]{LaValle2006Planning}.
Let $\vdc(n)$ be the VDC sequence of $n$ elements in the interval $[0,1]$.
The first elements of the VDC are $0,0.5,0.25,0.75,0.125,…$.
The sequence is guaranteed to satisfy $\vdc(n)⊆\vdc(n+1)$
and to minimize the discrepancy. The upper bound $\udpU Vₙ$
is defined as sampling the segment with extrema $⟨0,\fun₁⟩$
and $⟨\fun₁,0⟩$ using the VDC sequence:
\[
\udpU Vₙ\colon\fun₁⟼\{⟨\fun₁x,\fun₁(1-x)⟩\mid x ∈ \vdc(n)\}.
\]
 The lower bound $\udpL Vₙ$ is defined by taking meets of successive
points, according to the procedure in~\figref{make_lower}.
\begin{center}
\begin{figure}[H]
\adjustbox{max width=8.6cm}{\includegraphics[scale=0.33]{unc_samplingb}}
\par
\caption{\label{fig:Vn}Approximations to $\overline{+}$ using the Van Der
Corput sequence $Vₙ$.}
\end{figure}
\par\end{center}

For this sequence, one can prove that not only $\overline{+}\udpleq Vₙ$,
but also that the convergence is uniform, in the sense that $\overline{+}\udpleq V_{n+1}\udpleq Vₙ.$
The situation is represented graphically in~\figref{convergence_pyramid}:
the sequence is a descending chain that converges to $\overline{+}$.

\subsubsection{Inverse of multiplication}

The case of multiplication can be treated analogously to the case
of addition. By taking the logarithm, the inequality $\fun₁≤\res₁\res₂$
can be rewritten as $\log(\fun₁)≤\log(\res₁)+\log(\res₂).$
So we can repeat the constructions done for addition. The VDC sequence
are shown in~\figref{approx_invmult}.

\begin{figure}[H]

\adjustbox{max width=8.6cm}{\includegraphics[scale=0.33]{unc_sampling2b}}
\par
\caption{\label{fig:approx_invmult}Van Der Corput relaxations for the relation
$\fun₁≤\res₁\res₂$.}
\end{figure}


\subsubsection{Numerical example}

We have applied this relaxation to the relation ${\colF\text{travel distance}}≤{\colR\text{velocity}}×{\colR\text{endurance}}$
in the MCDP in~\figref{Example1}. Thanks to this theory,
we can obtain estimates of the solutions using bounded computation,
even though that relation has infinite cardinality.

\figref{invplus1}~shows the result using uniform sampling,
and~\figref{invplus2} shows the result using VDC sampling.
As predicted by the theory, uniform sampling does not give monotone
convergence, while VDC sampling does.
\begin{center}
\begin{figure}[t]

\subfloat[\label{fig:notchain}Qualitative behavior for $Sₙ$]{\includegraphics[scale=0.33]{unc_convergence_pyramid}}\subfloat[\label{fig:convergence_pyramid}Qualitative behavior for $Vₙ$]{
\includegraphics[scale=0.33]{unc_convergence_pyramid2}
\par
}
\par

\subfloat[\label{fig:invplus1}Numerical results for $Sₙ$]{
\adjustbox{max width=4.0cm}{\includegraphics[scale=0.33]{unc_convergence}}
\par
}\subfloat[\label{fig:invplus2}Numerical results for $Vₙ$]{
\adjustbox{max width=4.0cm}{\includegraphics[scale=0.33]{unc_convergence2}}
\par
}
\par
\caption{Solutions to the example in~\figref{Example1}, applying relaxations
for the relation ${\colF\text{travel\_distance}}≤{\colR\text{velocity}}×{\colR\text{endurance}}$
using the uniform sampling sequence and the VDC sampling sequence.
The uniform sampling sequence $Sₙ$ does not converge monotonically
(panel~\emph{a}); therefore the progress is not monotonic~(panel\emph{~c}).
Conversely, the Van Der Corput sequence $Vₙ$ is a descending
chain (panel~\emph{b}), which results in monotonic progress (panel~\emph{d}).}
\end{figure}
\par\end{center}

\section{Conclusions and future work}

Monotone Co-Design Problems (MCDPs) provide a compositional theory
of ``co-design'' that describes co-design constraints among different
subsystems in a complex system, such as a robotic system.

This paper dealt with the introduction of uncertainty in the framework,
specifically, interval uncertainty.

Uncertainty can be used in two roles. First, it can be used to describe
limited knowledge in the models. For example, in \prettyref{sec:Application-uncertainty},
we have seen how this can be applied to model mistrust about numbers
from Wikipedia. Second, uncertainty allows to generate relaxations
of the problem. We have seen two applications: introducing an allowed
tolerance in one particular variable (\prettyref{sec:Application-tolerance}),
and dealing with relations with infinite cardinality using bounded
computation resources (\prettyref{sec:Application-relax}).

Future work includes strengthening these results. For example, we
are not able to predict the resulting uncertainty in the solution
before actually computing it; ideally, one would like to know how
much computation is needed (measured by the number of points in the
antichain approximation) for a given value of the uncertainty that
the user can accept.

{

\footnotesize



\setcounter{page}{1}


\printbibliography

}

\clearpage

\appendix

\section{{\normalsize{}Appendix}}

\subsection{Proofs}

\subsubsection{Proofs of well-formedness of \prettyref{def:semantics-udp}}

As some preliminary business, we need to prove that \prettyref{def:semantics-udp}
is well formed, in the sense that the way the semantics function $\udpsem$
is defined, it returns a UDP for each argument. This is not obvious
from~\prettyref{def:semantics-udp}.

For example, for $\udpsem⟦\atoms,\dpseries(\atree₁,\atree₂),\val⟧$,
the definition gives values for $\udpL\udpsem⟦\atoms,\dpseries(\atree₁,\atree₂),\val⟧$
and $\udpU\udpsem⟦\atoms,\dpseries(\atree₁,\atree₂),\val⟧$
separately, without checking that
\[
\udpL\udpsem⟦\atoms,\dpseries(\atree₁,\atree₂),\val⟧\dpleq\udpU\udpsem⟦\atoms,\dpseries(\atree₁,\atree₂),\val⟧.
\]
 The following lemma provides the proof for that.
\begin{lem}
\label{lem:udpsem-well-formed}\prettyref{def:semantics-udp} is well
formed, in the sense that {\small{}
\begin{equation}
\udpL\udpsem⟦⟨\atoms,\dpseries(\atree₁,\atree₂),\val⟩⟧\dpleq\udpU\udpsem⟦⟨\atoms,\dpseries(\atree₁,\atree₂),\val⟩⟧,\label{eq:wf1}
\end{equation}
\begin{equation}
\udpL\udpsem⟦⟨\atoms,\dppar(\atree₁,\atree₂),\val⟩⟧\dpleq\udpU\udpsem⟦⟨\atoms,\dppar(\atree₁,\atree₂),\val⟩⟧,\label{eq:wf2}
\end{equation}
\begin{equation}
\udpL\udpsem⟦⟨\atoms,\dploop(\atree),\val⟩⟧\dpleq\udpU\udpsem⟦⟨\atoms,\dploop(\atree),\val⟩⟧.\label{eq:wf3}
\end{equation}
}{\small \par}
\end{lem}
\begin{IEEEproof}
Proving \prettyref{eq:wf1}\textemdash \prettyref{eq:wf3} can be
reduced to proving the following three results, for any $x,y ∈ \udpsp$:
\begin{align*}
(\udpL x\opseries\udpL y) & \dpleq(\udpU x\opseries\udpU y),\\
(\udpL x\oppar\udpL y) & \dpleq(\udpU x\oppar\udpU y),\\
(\udpL x)^{\oploop} & \dpleq(\udpU x)^{\oploop}.
\end{align*}
These are given in \prettyref{lem:well-formed-series}, \prettyref{lem:well-formed-par},
\prettyref{lem:well-formed-loop}.
\end{IEEEproof}
\begin{lem}
\label{lem:well-formed-series}$(\udpL x\opseries\udpL y)\dpleq(\udpU x\opseries\udpU y)$.
\end{lem}
\begin{IEEEproof}
First prove that $\opseries$ is monotone in each argument (proved
as~\prettyref{lem:series-monotone}). Then note that
\[
(\udpL x\opseries\udpL y)\dpleq(\udpL x\opseries\udpU y)\dpleq(\udpU x\opseries\udpU y).
\]
\end{IEEEproof}
\begin{lem}
\label{lem:well-formed-par}$(\udpL x\oppar\udpL y)\dpleq(\udpU x\oppar\udpU y)$.
\end{lem}
\begin{IEEEproof}
The proof is entirely equivalent to the proof of~\prettyref{lem:well-formed-series}.
First prove that $\dppar$ is monotone in each argument (proved as~\prettyref{lem:par-monotone}).
Then note that~
\[
(\udpL x\oppar\udpL y)\dpleq(\udpL x\oppar\udpU y)\dpleq(\udpU x\oppar\udpU y).
\]
\end{IEEEproof}

\begin{lem}
\label{lem:well-formed-loop}$(\udpL x)^{\oploop}\dpleq(\udpU x)^{\oploop}$.
\end{lem}
\begin{IEEEproof}
This follows from the fact that $\oploop$ is monotone (\prettyref{lem:loop-monotone}).
\end{IEEEproof}


\subsubsection{Monotonicity lemmas for DP}

These lemmas are used in the proofs above.
\begin{lem}
\label{lem:series-monotone}$\opseries:\dpsp×\dpsp⟶\dpsp$
is monotone on $⟨\dpsp,\dpleq⟩$.
\end{lem}
\begin{IEEEproof}
In~\prettyref{def:opseries}, $\opseries$ is defined as follows
for two maps $\ftor₁\colon\funsp₁⟶\Aressp₁$ and $\ftor₂\colon\funsp₂⟶\Aressp₂$:
\[
{\displaystyle \ftor₁\opseries\ftor₂=\Min_{ ≼_{\ressp₂}} ↑\bigcup_{s ∈ \ftor₁(\fun)}\ftor₂(s)}.
\]
It is useful to decompose this expression as the composition of three
maps:
\[
\ftor₁\opseries\ftor₂=m○ g[\ftor₂]○\ftor₁,
\]
where~``$○$'' is the usual map composition, and $g$ and $m$
are defined as follows:
\begin{align*}
g[\ftor₂]:\antichains\ressp₁ & ⟶\upsets\ressp₂,\\
R & ⟼ ↑\bigcup_{s ∈ R}\ftor₂(s),
\end{align*}
and
\begin{align*}
m:\upsets\ressp₂ & ⟶\antichains\ressp₂,\\
R & ⟼\Min_{ ≼_{\ressp₂}}R.
\end{align*}

From the following facts:
\begin{itemize}
\item $m$ is monotone.
\item $g[\ftor₂]$ is monotone in $\ftor₂$.
\item $f₁○ f₂$ is monotone in each argument if the other argument
is monotone.
\end{itemize}
Then the thesis follows.
\end{IEEEproof}

\begin{lem}
\label{lem:par-monotone}$\oppar:\dpsp×\dpsp⟶\dpsp$
is monotone on $⟨\dpsp,\dpleq⟩$.
\end{lem}
\begin{IEEEproof}
The definition of $\oppar$ (\prettyref{def:opmaps}) is:
\begin{align*}
\ftor₁\oppar\ftor₂:(\funsp₁×\funsp₂) & ⟶\antichains(\ressp₁×\ressp₂),\\
⟨\fun₁,\fun₂⟩ & ⟼\ftor₁(\fun₁)×\ftor₂(\fun₂).
\end{align*}
Because of symmetry, it suffices to prove that $\oppar$ is monotone
in the first argument, leaving the second fixed.

We need to prove that for any two DPs $\ftorₐ,\ftor_{b}$ such
that
\begin{equation}
\ftorₐ\dpleq\ftor_{b},\label{eq:Ikno}
\end{equation}
and for any fixed $\overline{\ftor}$, then
\[
\ftorₐ\oppar\overline{\ftor}\dpleq\ftor_{b}\oppar\overline{\ftor}.
\]
Let $R=\overline{\ftor}(\fun₂)$. Then we have that
\begin{align*}
[\ftorₐ\oppar\overline{\ftor}](\fun₁,\fun₂) & =\ftorₐ(\fun₁)\acprod R,\\{}
[\ftor_{b}\oppar\overline{\ftor}](\fun₁,\fun₂) & =\ftor_{b}(\fun₁)\acprod R.
\end{align*}
Because of \prettyref{eq:Ikno}, we know that
\[
\ftorₐ(\fun₁) ≼_{\antichains\ressp₁}\ftor_{b}(\fun₁).
\]
So the thesis follows from proving that the product of antichains
is monotone~(\prettyref{lem:product-monotone}).
\end{IEEEproof}
\begin{lem}
\label{lem:product-monotone}The product of antichains $\acprod:\antichains\ressp₁×\antichains\ressp₂⟶\antichains(\ressp₁×\ressp₂)$
is monotone.
\end{lem}

\begin{lem}
\label{lem:loop-monotone}$\oploop:\dpsp⟶\dpsp$ is monotone
on $⟨\dpsp,\dpleq⟩$.
\end{lem}
\begin{IEEEproof}
Let $\ftor₁\dpleq\ftor₂$. Then we can prove that $\ftor₁^{\oploop}\dpleq\ftor₂^{\oploop}$.
From the definition of $\oploop$~(\prettyref{def:oploop}), we
have that
\begin{align*}
\ftor₁^{\oploop}(\fun₁) & =\lfp(Ψ_{\fun}^{\ftor₁}),\\
\ftor₂^{\oploop}(\fun₂) & =\lfp(Ψ_{\fun}^{\ftor₂}),
\end{align*}
with $Ψ_{\fun₁}^{\ftor}$ defined as
\begin{align*}
Ψ_{\fun₁}^{\ftor}:\Aressp & ⟶\Aressp,\\
{\colR R} & ⟼\Min_{ ≼_{\ressp}}\bigcup_{\res ∈ {\colR R}}\ftor(\fun₁,\res)␣∩ ↑\res.
\end{align*}
The least fixed point operator $\lfp$ is monotone, so we are left
to check that the map
\[
\ftor⟼Ψ_{\fun₁}^{\ftor}
\]
is monotone. That is the case, because if $\ftor₁\dpleq\ftor₂$
then
\[
[\bigcup_{\res ∈ {\colR R}}\ftor₁(\fun₁,\res)␣∩ ↑\res] ≼_{\Aressp}[\bigcup_{\res ∈ {\colR R}}\ftor₂(\fun₁,\res)␣∩ ↑\res].
\]
\end{IEEEproof}


\subsubsection{Monotonicity of semantics $\dpsem$}


\begin{lem}[$\dpsem$ is monotone in the valuation]
\label{lem:dpsem-monotone}Suppose that $\val₁,\val₂:\atoms⟶\dpsp$
are two valuations for which it holds that $\val₁(a)\dpleq\val₂(a)$.
Then $\dpsem⟦⟨\atoms,\atree,\val₁⟩⟧\dpleq\dpsem⟦⟨\atoms,\atree,\val₂⟩⟧$.
\end{lem}
\begin{IEEEproof}
Given the recursive definition of \prettyref{def:dpsem}, we need
to prove this just for the base case and for the recursive cases.

The base case, given in \eqref{eq:base}, is
\[
\dpsem⟦⟨\atoms,a,\val⟩⟧≐\val(a),\qquad\text{for all}␣a ∈ \atoms.
\]
We have
\begin{align*}
\dpsem⟦⟨\atoms,\atree,\val₁⟩⟧& =\val₁(a)\\
\dpsem⟦⟨\atoms,\atree,\val₂⟩⟧& =\val₂(a)
\end{align*}
and $\val₁(a)\dpleq\val₂(a)$ by assumption.

For the recursive cases, \eqref{eq:series}\textendash \eqref{eq:loop},
the thesis follows from the monotonicity of $\opseries$, $\oppar$,
$\oploop$, proved in \prettyref{lem:par-monotone}, \prettyref{lem:series-monotone},
\prettyref{lem:loop-monotone}.
\end{IEEEproof}

\subsubsection{Proof of the main result, \prettyref{thm:udpsem-monotone}}

\label{subsec:proof-main-result}

We restate the theorem.

\textbf{Theorem~\ref{thm:udpsem-monotone}}. \emph{If
\[
\val₁ ≼_{V}\val₂
\]
then
\[
\udpsem⟦⟨\atoms,\atree,\val₁⟩⟧\udpleq\udpsem⟦⟨\atoms,\atree,\val₂⟩⟧.
\]
}
\begin{IEEEproof}
From the definition of $\udpsem$ and $\dpsem$, we can derive that
\begin{align}
\udpL\udpsem⟦⟨\atoms,\atree,\val⟩⟧& =\dpsem⟦⟨\atoms,\atree,\udpL○\val⟩⟧.\label{eq:equiv1}
\end{align}
In particular, for $\val=\val₁$,
\begin{equation}
\udpL\udpsem⟦⟨\atoms,\atree,\val₁⟩⟧=\dpsem⟦⟨\atoms,\atree,\udpL○\val₁⟩⟧.\label{eq:w1}
\end{equation}
Because $\val₁(a)\udpleq\val₂(a),$ from \prettyref{lem:dpsem-monotone},
\begin{equation}
\dpsem⟦⟨\atoms,\atree,\udpL○\val₁⟩⟧\dpleq\dpsem⟦⟨\atoms,\atree,\udpL○\val₂⟩⟧.\label{eq:w2}
\end{equation}
From~\prettyref{eq:equiv1} again,
\begin{equation}
\dpsem⟦⟨\atoms,\atree,\udpL○\val₂⟩⟧=\udpL\udpsem⟦⟨\atoms,\atree,\val₂⟩⟧.\label{eq:w3}
\end{equation}
From \eqref{eq:w1},~\eqref{eq:w2}, \eqref{eq:w3} together,
\[
\udpL\udpsem⟦⟨\atoms,\atree,\val₁⟩⟧\dpleq\udpL\udpsem⟦⟨\atoms,\atree,\val₂⟩⟧.
\]
 Repeating the same reasoning for $\udpU$, we have
\[
\udpU\udpsem⟦⟨\atoms,\atree,\val₂⟩⟧\dpleq\udpU\udpsem⟦⟨\atoms,\atree,\val₁⟩⟧.
\]
 Therefore
\[
\udpsem⟦⟨\atoms,\atree,\val₁⟩⟧\udpleq\udpsem⟦⟨\atoms,\atree,\val₂⟩⟧.
\]
\end{IEEEproof}

\vfill\pagebreak

\section{Software}

\subsection{Source code}

The implementation is available at the repository \url{http://github.com/AndreaCensi/mcdp/},
in the branch ``uncertainty\_sep16''.

\subsection{Virtual machine }

A VMWare virtual machine is available to reproduce the experiments
at the URL \url{https://www.dropbox.com/sh/nfpnfgjh9hpcgvh/AACVZfdVXxMoVqTYiHWaOwHAa?dl=0}.

To reproduce the figures, log in with user password ``mcdp''/''mcdp''.
Then execute the following commands:

\footnotesize
\begin{lyxcode}
\$~cd~\textasciitilde{}/mcdp

\$~source~environment.sh

\$~cd~libraries/examples/uav\_energetics/

~~~~~~~droneD\_complete\_templates.mcdplib

\$~make~clean

\$~make~paper-figures
\end{lyxcode}

\clearpage

\includepdf[pages={-}]{mcdp_icra_uncertainty_models.pdf}
<!-- \end{document} -->
