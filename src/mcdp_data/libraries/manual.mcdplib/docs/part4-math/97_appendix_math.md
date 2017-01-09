
# Basic order theory  {#app:basic-order-theory}

<!-- Ligature: efficient affe cafilo. Digits: 1 2 3 4 5 000123679 -->

We will use basic facts about order theory. Davey and Priestley~\cite{davey02}
and Roman~\cite{roman08} are possible reference texts.

I can also cite <a href='#bib:davey02'>that paragraph x.y</a>.


Let $⟨ 𝒫,≼_𝒫⟩ $ be a partially ordered set
(poset), which is a set $𝒫$ together with a partial order $≼_𝒫$ (a
reflexive, antisymmetric, and transitive relation). The partial
order~"$≼_𝒫$" is written as "$≼$" if the context is clear. If a poset
has a least element, it is called "bottom" and it is denoted by $⊥_{𝒫}$.
If the poset has a maximum element, it is called "top" and denoted
as $⊤_{𝒫}$.


### Chains and antichains

\begin{defn}[Chain]
A <em>chain</em> $x ≼ y ≼ z≼\dots$ is a subset of a poset in
which all elements are comparable.
\end{defn}

An <em>antichain</em> is a subset of a poset in which <em>no</em> elements are
comparable. This is the mathematical concept that formalizes the idea of "Pareto
front".

\begin{defn}[Antichain] \label{def:antichain}
A subset $S⊆𝒫$ is an antichain iff no elements are comparable:
for $x, y ∈ S$, $x ≼ y$ implies $x=y$.
\end{defn}

Call $\antichains𝒫$ the set of all antichains in $𝒫$. By this
definition, the empty set is an antichain: $∅ ∈ \antichains𝒫$.

\begin{defn}[Width and height of a poset] \label{def:poset-width-height}
$\mathsf{width}(𝒫)$ is the maximum cardinality of an antichain in $𝒫$
and $\mathsf{height}(𝒫)$ is the maximum cardinality of a chain in $𝒫$.
\end{defn}


### Minimal elements

Uppercase "$\Min$" will denote the \emph{minimal} elements of a set. The minimal
elements are the elements that are not dominated by any other in the set.
Lowercase "$\min$" denotes \emph{ the least} element, an element that dominates
all others, if it exists. (If $\min S$ exists, then $\Min S=\{\min S\}$.)

The set of minimal elements of a set are an antichain, so $\Min$ is a map from
the power set $\pset(𝒫)$ to the antichains $\antichains𝒫$:

\begin{align*}
\Min:\pset(𝒫) & →\antichains𝒫,\\
S & ↦\{x ∈ S:\ (y ∈ S)∧(y ≼ x)⇒(x=y)\ \}.
\end{align*}

$\Max$ and $\max$ are similarly defined.

### Upper sets

An "upper set" is a subset of a poset that is closed upward.

\begin{defn}[Upper sets]
A subset $S⊆𝒫$ is an upper set iff $x ∈ S$ and $x ≼ y$
implies $y ∈ S$.
\end{defn}

Call $\upsets𝒫$ the set of upper sets of $𝒫$. By this
definition, the empty set is an upper set: $∅ ∈ \upsets𝒫$.

\begin{lem}
$\upsets𝒫$ is a poset itself, with the order given by
\begin{equation}
A≼_{\upsets𝒫}B⎵ ≡ ⎵ A⊇ B.\label{eq:up_order}
\end{equation}
\end{lem}

Note in (\ref{eq:up_order}) the use of~"$⊇$" instead
of~"$⊆$", which might seem more natural. This choice
will make things easier later.

In the poset $⟨ \upsets𝒫,≼_{\upsets𝒫}⟩ $,
the top is the empty set, and the bottom is the entire poset $𝒫$.


### Order on antichains

The upper closure operator "$↑$" maps a subset of a poset
to an upper set.
\begin{defn}[Upper closure]
The operator $↑$ maps a subset to the smallest upper set that
includes it:
\begin{eqnarray*}
↑ :   \pset(𝒫)   & → & \upsets𝒫,\\
               S & ↦ & \{ y ∈ 𝒫:  ∃ ⌑ x ∈ S: x ≼ y\}.
\end{eqnarray*}
\end{defn}

\captionsideleft{\label{fig:antichains_upsets}}{\includegraphics[scale=0.4]{boot-art/1509-gmcdp/gmcdp_antichains_upsets}}

By using the upper closure operator, we can define an order on antichains
using the order on the upper sets~(\figref{antichains_upsets}).
\begin{lem}
\label{lem:antichains-are-poset}$\antichains𝒫$ is a poset with
the relation $≼_{\antichains𝒫}$ defined by
\[
A ≼_{\antichains𝒫} B⎵ ≡ ⎵ ↑A ⊇ ↑B.
\]
\end{lem}
In the poset $⟨ \antichains𝒫,≼_{\antichains𝒫}⟩ $,
the top is the empty set:$⊤_{\antichains𝒫}=∅.$ If
a bottom for $𝒫$ exists, then the bottom for $\antichains𝒫$
is the singleton containing only the bottom for $𝒫$: $⊥_{\antichains𝒫}=\{⊥_{𝒫}\}.$


### Monotonicity and fixed points     {#sub:Monotonicity-and-fixed}

We will use Kleene's theorem, a celebrated result that is used in
disparate fields. It is used in computer science for defining denotational
semantics~(see, e.g.,~\cite{manes86}). It is used in embedded systems
for defining the semantics of models of computation~(see, e.g.,~\cite{lee10}).

\begin{defn}[Directed set]
A set $S ⊆ 𝒫$ is *directed* if each pair of elements
in $S$ has an upper bound: for all $a,b ∈ S$, there exists $c ∈ S$
such that $a ≼ c$ and $b ≼ c$.
\end{defn}

\begin{defn}[Completeness]  \label{def:cpo}
A poset is a *directed complete partial order* (\DCPO)
if each of its directed subsets has a supremum (least of
upper bounds). It is a *complete partial order* (\CPO) if it
also has a bottom.

\end{defn}
\begin{example}[Completion of $\nonNegReals$ to $\nonNegRealsComp$]
\label{exa:Rcomp}The set of real numbers $ℝ$ is not
a \CPO, because it lacks a bottom. The nonnegative reals $\nonNegReals=\{x ∈ ℝ \mid x ≥ 0\}$
have a bottom $⊥=0$, however, they are not a \DCPO because some
of their directed subsets do not have an upper bound. For example,
take $\nonNegReals$, which is a subset of $\nonNegReals$. Then $\nonNegReals$
is directed, because for each $a,b ∈ \nonNegReals$, there exists $c=\max\{a,b\} ∈ \nonNegReals$
for which $a ≤ c$ and $b ≤ c$. One way to make $⟨\nonNegReals,≤⟩ $
a \CPO is by adding an artificial top element $⊤$, by defining $\nonNegRealsComp\triangleq\nonNegReals\cup\{⊤\},$
and extending the partial order $≤$ so that $a ≤ ⊤$ for
all $a ∈ ℝ^{+}$.
\end{example}

Two properties of maps that will be important are monotonicity and
the stronger property of \scottcontinuity.
\begin{defn}[Monotonicity] \label{def:monotone}
A map $f:𝒫→𝒬$ between
two posets is \emph{monotone} iff $x ≼_𝒫 y$ implies $f(x) ≼_𝒬 f(y)$.
\end{defn}
%
\begin{defn}[\scottcontinuity]
\label{def:scott}A map $f:𝒫→𝒬$ between DCPOs
is\textbf{ }\emph{\scottcontinuous{}}\textbf{ }iff for each directed
subset $D⊆𝒫$, the image $f(D)$ is directed, and $f(\sup D)=\sup f(D).$
\end{defn}
\begin{rem}
\scottcontinuity implies monotonicity.
\end{rem}
%
\begin{rem}
\scottcontinuity does not imply topological continuity. A map from
the CPO $⟨\Rcomp,≤⟩$ to itself is \scottcontinuous
iff it is nondecreasing and left-continuous. For example, the ceiling
function $x ↦ ⌈x⌉$~ is \scottcontinuous (\figref{ceil}).
\end{rem}
\captionsideleft{\label{fig:ceil}}{\includegraphics[scale=0.33]{boot-art/1512-mcdp-tro/gmcdptro_ceil}}

\begin{defn}[fixed point]
A *fixed point* of $f:𝒫→𝒫$ is a point $x$ such that $f(x)=x$.
\end{defn}

\begin{defn}[least fixed point]
A \emph{least fixed point} of $f:𝒫→𝒫$ is the minimum
(if it exists) of the set of fixed points of $f$:
\begin{equation}
    \lfp(f)⌑⌑≐⌑⌑\min_{≼}⌑\{ x ∈ 𝒫: f(x) = x\}.\label{eq:lfp-one}
\end{equation}
\end{defn}

The equality in \eqref{lfp-one} can be relaxed to "$≼$".

The least fixed point need not exist. Monotonicity of the map $f$
plus completeness is sufficient to ensure existence.
\begin{lem}[\cite[CPO Fixpoint Theorem II, 8.22]{davey02}] \label{lem:CPO-fix-point-2}
If $𝒫$ is a \CPO and $f:𝒫→𝒫$ is monotone, then $\lfp(f)$ exists.
\end{lem}
%

With the additional assumption of \scottcontinuity, Kleene's algorithm
is a systematic procedure to find the least fixed point.
\begin{lem}[Kleene's fixed-point theorem \cite[CPO fixpoint theorem I, 8.15]{davey02}]
\label{lem:kleene-1}
Assume $𝒫$ is a \CPO, and $f:𝒫→𝒫$ is \scottcontinuous.
Then the least fixed point of $f$ is the supremum
of the Kleene ascent chain
\[
    ⊥≼ f(⊥) ≼ f(f(⊥)) ≼ ⋯ ≼ f^{(n)}(⊥) ≼ ⋯.
\]
\end{lem}
