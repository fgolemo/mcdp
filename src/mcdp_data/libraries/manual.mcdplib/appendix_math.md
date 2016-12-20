$\newcommand{\posA}{\mathcal{P}}$
$\newcommand{\posB}{\mathcal{Q}}$

$\newcommand{\posAleq}{\posleq_{\posA}}$
$\newcommand{\posBleq}{\posleq_{\posB}}$
$\newcommand{\posleq}{\preceq}$

$\newcommand{\antichains}{\mathrm{A}}$
$\newcommand{\upsets}{\mathrm{U}}$

$\newcommand{\CPO}{CPO}$

$\newcommand{\Min}{\mathsf{Min}}$
$\newcommand{\Max}{\mathsf{Max}}$

$\newcommand{\pset}{\mathscr{P}}$

$\newcommand{\upit}{\uparrow}$

$\newcommand{\lfp}{\mathsf{lfp}}$
$\newcommand{\Rcomp}{\overline{\mathbb{R}}_{+}}$

$\newcommand{\reals}{\mathbb{R}}$
$\newcommand{\nonNegReals}{\mathbb{R}_{+}}$
$\newcommand{\nonNegRealsComp}{\Rcomp}$


# Appendix: basic order theory

<!-- Ligature: efficient affe cafilo. Digits: 1 2 3 4 5 000123679 -->

We will use basic facts about order theory. Davey and Priestley~\cite{davey02}
and Roman~\cite{roman08} are possible reference texts.

Let $\left\langle \posA,\posAleq\right\rangle $ be a partially ordered
set (poset), which is a set~$\posA$ together with a partial order~$\posAleq$
(a reflexive, antisymmetric, and transitive relation). The partial
order~"$\posAleq$" is written as "$\posleq$" if the context
is clear. If a poset has a least element, it is called "bottom"
and it is denoted by~$\bot_{\posA}$. If the poset has a maximum
element, it is called "top" and denoted as~$\top_{\posA}$.

### Chains and antichains

A <em>chain</em> $x\posleq y\posleq z\posleq\dots$ is a subset of a
poset in which all elements are comparable. An <em>antichain</em> is
a subset of a poset in which <em>no</em> elements are comparable. This
is the mathematical concept that formalizes the idea of "Pareto
front".

\begin{defn}[Antichain] \label{def:antichain}
A subset $S\subseteq\posA$ is an antichain iff no elements are comparable:
for~$x,y\in S$, $x\posleq y$ implies~$x=y$.
\end{defn}

Call~$\antichains\posA$ the set of all antichains in~$\posA$.
By this definition, the empty set is an antichain: $\emptyset\in\antichains\posA$.

\begin{defn}[Width and height of a poset]
\label{def:poset-width-height} $\mathsf{width}(\posA)$ is the maximum
cardinality of an antichain in~$\posA$ and $\mathsf{height}(\posA)$
is the maximum cardinality of a chain in~$\posA$.
\end{defn}


### Minimal elements

Uppercase "$\Min$" will denote the \emph{minimal} elements of
a set. The minimal elements are the elements that are not dominated
by any other in the set. Lowercase "$\min$" denotes \emph{ the
least} element, an element that dominates all others, if it exists.
(If~$\min S$ exists, then~$\Min S=\{\min S\}$.)

The set of minimal elements of a set are an antichain, so~$\Min$
is a map from the power set $\pset(\posA)$ to the antichains~$\antichains\posA$:

\begin{align*}
\Min\colon\pset(\posA) & \rightarrow\antichains\posA,\\
S & \mapsto\{x\in S:\ (y\in S)\wedge(y\posleq x)\Rightarrow(x=y)\ \}.
\end{align*}

$\Max$ and $\max$ are similarly defined.

### Upper sets

An "upper set" is a subset of a poset that is closed upward.

\begin{defn}[Upper sets]
A subset $S\subseteq\posA$ is an upper set iff~$x\in S$ and~$x\posleq y$
implies~$y\in S$.
\end{defn}
Call~$\upsets\posA$ the set of upper sets of~$\posA$. By this
definition, the empty set is an upper set: $\emptyset\in\upsets\posA$.
\begin{lem}
$\upsets\posA$ is a poset itself, with the order given by
\begin{equation}
A\posleq_{\upsets\posA}B\qquad\equiv\qquad A\supseteq B.\label{eq:up_order}
\end{equation}
\end{lem}
Note in (\ref{eq:up_order}) the use of~"$\supseteq$" instead
of~"$\subseteq$", which might seem more natural. This choice
will make things easier later.

In the poset~$\left\langle \upsets\posA,\posleq_{\upsets\posA}\right\rangle $,
the top is the empty set, and the bottom is the entire poset~$\posA$.


### Order on antichains

The upper closure operator "$\upit$" maps a subset of a poset
to an upper set.
\begin{defn}[Upper closure]
The operator~$\upit$ maps a subset to the smallest upper set that
includes it:
\begin{eqnarray*}
\upit\colon\pset(\posA) & \rightarrow & \upsets\posA,\\
S & \mapsto & \{y\in\posA:\exists\,x\in S:x\posleq y\}.
\end{eqnarray*}
\end{defn}

\captionsideleft{\label{fig:antichains_upsets}}{\includegraphics[scale=0.4]{boot-art/1509-gmcdp/gmcdp_antichains_upsets}}

By using the upper closure operator, we can define an order on antichains
using the order on the upper sets~(\figref{antichains_upsets}).
\begin{lem}
\label{lem:antichains-are-poset}$\antichains\posA$ is a poset with
the relation~$\posleq_{\antichains\posA}$ defined by
\[
A\posleq_{\antichains\posA}B\qquad\equiv\qquad\upit A\supseteq\upit B.
\]
\end{lem}
In the poset $\left\langle \antichains\posA,\posleq_{\antichains\posA}\right\rangle $,
the top is the empty set:$\top_{\antichains\posA}=\emptyset.$ If
a bottom for $\posA$ exists, then the bottom for~$\antichains\posA$
is the singleton containing only the bottom for~$\posA$: $\bot_{\antichains\posA}=\{\bot_{\posA}\}.$


## Monotonicity and fixed points \label{sec:Monotonicity-and-fixed}

We will use Kleene's theorem, a celebrated result that is used in
disparate fields. It is used in computer science for defining denotational
semantics~(see, e.g.,~\cite{manes86}). It is used in embedded systems
for defining the semantics of models of computation~(see, e.g.,~\cite{lee10}).

\begin{defn}[Directed set]
A set~$S\subseteq\posA$ is \emph{directed} if each pair of elements
in~$S$ has an upper bound: for all~$a,b\in S$, there exists~$c\in S$
such that~$a\posleq c$ and~$b\posleq c$.
\end{defn}

\begin{defn}[Completeness]
\label{def:cpo}A poset is a \emph{directed complete partial order}
(\DCPO) if each of its directed subsets has a supremum (least of
upper bounds). It is a \emph{complete partial order} (\CPO) if it
also has a bottom.

\end{defn}
\begin{example}[Completion of $\nonNegReals$ to~$\nonNegRealsComp$]
\label{exa:Rcomp}The set of real numbers~$\mathbb{R}$ is not
a \CPO, because it lacks a bottom. The nonnegative reals~$\nonNegReals=\{x\in\reals\mid x\geq0\}$
have a bottom~$\bot=0$, however, they are not a \DCPO because some
of their directed subsets do not have an upper bound. For example,
take~$\nonNegReals$, which is a subset of~$\nonNegReals$. Then~$\nonNegReals$
is directed, because for each~$a,b\in\nonNegReals$, there exists~$c=\max\{a,b\}\in\nonNegReals$
for which~$a\leq c$ and~$b\leq c$. One way to make~$\left\langle \nonNegReals,\leq\right\rangle $
a \CPO is by adding an artificial top element~$\top$, by defining~$\nonNegRealsComp\triangleq\nonNegReals\cup\{\top\},$
and extending the partial order~$\leq$ so that~$a\leq\top$ for
all~$a\in\reals^{+}$.
\end{example}

Two properties of maps that will be important are monotonicity and
the stronger property of \scottcontinuity.
\begin{defn}[Monotonicity]
\label{def:monotone}A map~$f\colon\posA\rightarrow\posB$ between
two posets is \emph{monotone} iff~$x\posAleq y$ implies~$f(x)\posBleq f(y)$.
\end{defn}
%
\begin{defn}[\scottcontinuity]
\label{def:scott}A map~$f:\posA\rightarrow\posB$ between DCPOs
is\textbf{ }\emph{\scottcontinuous{}}\textbf{ }iff for each directed
subset~$D\subseteq\posA$, the image~$f(D)$ is directed, and $f(\sup D)=\sup f(D).$
\end{defn}
\begin{rem}
\scottcontinuity implies monotonicity.
\end{rem}
%
\begin{rem}
\scottcontinuity does not imply topological continuity. A map from
the CPO $\langle\Rcomp,\leq\rangle$ to itself is \scottcontinuous
iff it is nondecreasing and left-continuous. For example, the ceiling
function $x\mapsto\left\lceil x\right\rceil $~ is \scottcontinuous
(\figref{ceil}).
\end{rem}
\captionsideleft{\label{fig:ceil}}{\includegraphics[scale=0.33]{boot-art/1512-mcdp-tro/gmcdptro_ceil}}


A \emph{fixed} \emph{point} of $f:\posA\rightarrow\posA$ is a point~$x$
such that $f(x)=x$.
\begin{defn}
A \emph{least fixed point} of~$f:\posA\rightarrow\posA$ is the minimum
(if it exists) of the set of fixed points of~$f$:
\begin{equation}
\lfp(f)\,\,\doteq\,\,\min_{\posleq}\,\{x\in\posA\colon f(x)=x\}.\label{eq:lfp-one}
\end{equation}
The equality in \eqref{lfp-one} can be relaxed to "$\posleq$".
\end{defn}
The least fixed point need not exist. Monotonicity of the map~$f$
plus completeness is sufficient to ensure existence.
\begin{lem}[{\cite[CPO Fixpoint Theorem II, 8.22]{davey02}}]
\label{lem:CPO-fix-point-2}If~$\posA$ is a \CPO and~$f:\posA\rightarrow\posA$
is monotone, then $\lfp(f)$ exists.
\end{lem}
%

With the additional assumption of \scottcontinuity, Kleene's algorithm
is a systematic procedure to find the least fixed point.
\begin{lem}[{Kleene's fixed-point theorem \cite[CPO fixpoint theorem I, 8.15]{davey02}}]
\label{lem:kleene-1}Assume $\posA$ is a \CPO, and~$f:\posA\rightarrow\posA$
is \scottcontinuous. Then the least fixed point of~$f$ is the supremum
of the Kleene ascent chain
\[
\bot\posleq f(\bot)\posleq f(f(\bot))\posleq\cdots\posleq f^{(n)}(\bot)\leq\cdots.
\]
\end{lem}

Citing lemma: <a href="#lem:kleene-1"></a>
Citing def: <a href='#def:poset-width-height'></a>
