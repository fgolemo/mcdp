

\section{Background in Order Theory}

The good news is that we are not going to use any of these:
\[
\partial\qquad\nabla\qquad\nabla^{2}.
\]
What we \emph{are} going to use are basic facts about order theory.
Possible introductory references include: 
\begin{itemize}
\item Davey and Priestley \cite{davey02} 
\item Roman \cite{roman08}
\end{itemize}
A more advanced reference is Gierz \etal \cite{gierz03continuous}


\subsection{Sets}

We will use letters $A,B,\dots$ to indicate sets.

Some famous sets are the natural numbers $\mathbb{N}$, the integers $\mathbb{Z}$,
and the reals $\reals$. The set $\mathbb{R}_{+}$ is the set of
nonnegative numbers, \uline{including} zero: $\mathbb{R}_{+}=\{x\in\reals:x\geq0\}$.
$\overline{\mathbb{R}}_{+}$ is the completion of $\mathbb{R}_{+}$\textemdash the
construction is in \exaref{Rcomp}
\begin{defn}[Cardinality of a set]
The cardinality of a set $A$ is indicated as $|A|$. The cardinality
of a finite set is the number of elements. The cardinality of $\mathbb{N}$
is $\aleph_{0}$ (``aleph-null''); the cardinality of $\reals^{n}$
is $\aleph_{1}$. 
\end{defn}
\begin{rem}
Some references refer to a set ``$\boldsymbol{\omega}$''; for
our purposes, it is a synonym of $\mathbb{N}$. The symbol ``$\omega$'',
or sometimes ``$\omega_{0}$'', denotes the smallest infinite ordinal;
for our purposes, it is a synonym of $\aleph_{0}$.
\end{rem}
\begin{defn}[Cartesian product]
For two sets $A,B$, their Cartesian product $A\times B$ is the
set of ordered pairs $\langle a,b\rangle$ for $a\in A$ and $b\in B$. 

It holds that $|A\times B|=|A||B|$. 
\end{defn}
%
\begin{defn}[Projection]
Let $\pi_{i}$ be the projection to the $i$-th component of a tuple
or a space.
\end{defn}
\begin{align*}
\pi_{1}(A\times B) & =A,\\
\pi_{2}(A\times B) & =B.
\end{align*}

\begin{align*}
\pi_{1}(\left\langle a,b\right\rangle ) & =a,\\
\pi_{2}(\left\langle a,b\right\rangle ) & =b.
\end{align*}


\subsection{Posets}
\begin{defn}[Poset]
\label{def:poset}A partially ordered set, or \emph{poset}, is a
pair $\left\langle \posA,\posAleq\right\rangle $, where $\posA$
is a set and $\posAleq$ is a \emph{partial order} $\posAleq$. A
partial order is a relation that is:
\begin{itemize}
\item \emph{reflexive}: $a\posAleq a$ always holds.
\item \emph{antisymmetric}: If $a\neq b$, then $a\posAleq b$ and $b\posAleq a$
cannot both hold. Equivalently, from $a\posAleq b$ and $b\posAleq a$
we can conclude $a=b$.
\item \emph{transitive}: If $a\posAleq b$ and $b\posAleq c$ imply $a\posAleq c$. 
\end{itemize}
The partial order ``$\posAleq$'' is written as ``$\posleq$''
if the context is clear,
\end{defn}
%
\begin{defn}[Pre-order]
\label{def:preorder}A pre-order is a slightly weaker concept of
a partial order; it is assumed to be only reflexive and transitive,
but not necessarily antisymmetric.
\end{defn}
\begin{example}[Numbers with units]
PyMCDP supports numbers with units (\xxx). Let $U$ be a set containing
many copies of $\Rcomp$, each one augmented with an indication of
the units. For example, $\Rcpu{g}$ describes the numbers with units
``grams'' and $\Rcpu{J}$ describes the numbers with units joules.
One can convert grams to pounds but not grams to joules. Let $\triangleleft_{U}$
be the relation ``can be converted to''. Then $\Rcpu{g}\triangleleft_{U}\Rcpu{kg}$
but $\Rcpu{g}$ is not related to $\Rcpu{J}$ in either direction.
This relation is obviously \emph{reflexive}. This relation is \emph{transitive},
because if we can convert from $\Rcpu{u}$ to $\Rcpu{v}$ and from
$\Rcpu{v}$ to $\Rcpu{w}$, we can convert from $\Rcpu{u}$ to $\Rcpu{v}$.
However, it is not a partial order, because it is \emph{not} \emph{antisymmetric:}
 $\Rcpu{g}\triangleleft_{U}\Rcpu{kg}$ and $\Rcpu{kg}\triangleleft_{U}\Rcpu{g}$,
but $\Rcpu{g}\neq\Rcpu{kg}$. This relation is actually \emph{symmetric}:
if we can convert from $\Rcpu{u}$ to $\Rcpu{v}$ then we can always
go back and convert $\Rcpu{v}$ to $\Rcpu{u}$. In conclusion, $\triangleleft_{U}$
is a pre-order, but not a partial order. 
\end{example}
\begin{defn}[Top and bottom]
\label{def:top}If a poset $\left\langle \posA,\posAleq\right\rangle $
has a least element, it is called ``bottom'' and it is denoted by $\bot_{\posA}$,
or simply $\bot$. If the poset has a maximum element, it is called
``top'' and denoted as $\top_{\posA}$.
\end{defn}

\subsubsection{Hasse diagram}

A hasse diagram is \xxx
\begin{center}
\begin{figure}
\begin{centering}
\noindent\begin{minipage}[t]{1\columnwidth}%
\begin{lyxcode}
<render class='hasse'>

poset \{ x &lt;= y &lt;= z \}

</render>
\end{lyxcode}
%
\end{minipage}
\par\end{centering}
\caption{Caption of figure with centered content}
\end{figure}
\par\end{center}

\subsubsection{Examples of posets }
\begin{example}
Natural number
\end{example}
%
\begin{example}
\{rare, medium, well-done\}
\end{example}
%
\begin{example}
... 
\end{example}

\subsection{Chains}
\begin{defn}[Chain]
\label{def:chain}A \emph{chain} $x\posleq y\posleq z\posleq\dots$
is a subset of a poset in which all elements are comparable. 
\end{defn}
\begin{figure}
\begin{centering}
\noindent\begin{minipage}[t]{1\columnwidth}%
\begin{lyxcode}
<render class='hasse'>

poset \{ x &lt;= y &lt;= z &lt;= dotdot \}

</render>
\end{lyxcode}
%
\end{minipage}
\par\end{centering}
\caption{centered}
\end{figure}

%

\subsection{Antichains}

An \emph{antichain} is a subset of a poset in which \emph{no} elements
are comparable. This is the mathematical concept that formalizes the
idea of ``Pareto front''.

\begin{defn}[Antichains]
\label{def:antichain}A subset $S\subseteq\posA$ is an antichain
iff no elements are comparable: for $x,y\in S$, $x\posleq y$ implies $x=y$. 
\end{defn}
Call $\antichains\posA$ the set of all antichains in $\posA$.

Notable antichains in $\antichains\posA$ include:
\begin{itemize}
\item The empty set is an antichain: $\emptyset\in\antichains\posA$.
\item Any singleton $\{x\}$ for $x\in\posA$.
\end{itemize}


\subsection{Width and height}
\begin{defn}[Width and height of a poset]
\label{def:poset-width} $\mathsf{width}(\posA)$ is the cardinality
of the largest antichain in $\posA$.
\end{defn}
%
\begin{defn}[Poset height]
\label{def:poset-height}The cardinality of the largest chain is
called the ``height'' of the poset, and referred to as $\mathsf{height}(\posA)$
.
\end{defn}
Here are some examples:
\begin{center}
\begin{table}[H]
\caption{Some examples of poset width and height}

\centering{}%
\begin{tabular}{|c|c|c||c}
\hline 
$\posA$ & $|\posA|$ & $\mathsf{height}(\posA)$ & $\mathsf{width}(\posA)$\tabularnewline
\hline 
\hline 
$\mathbb{N}$ & $\aleph_{0}$ & $\aleph_{0}$ & 1\tabularnewline
\hline 
$\mathbb{N}\times\mathbb{N}$ & $\aleph_{0}$ & $\aleph_{0}$ & $\aleph_{0}$\tabularnewline
\hline 
$\overline{\reals}$ & $\aleph_{1}$ & $\aleph_{1}$ & 1\tabularnewline
\hline 
$\overline{\reals}^{2}$ & $\aleph_{1}$ & $\aleph_{1}$ & $\aleph_{1}$\tabularnewline
\hline 
$\mathtt{int32}$ & $\sim2^{32}$ & $\sim2^{32}$ & 2\tabularnewline
\hline 
$\mathtt{float32}$ & $\sim2^{32}$ & $\sim2^{32}$ & 2\tabularnewline
\hline 
 &  &  & \tabularnewline
\hline 
\end{tabular}
\end{table}
\par\end{center}

\subsection{Minimal and least elements}
\begin{defn}[Minimal elements]
\label{def:Min}Uppercase ``$\Min$'' will denote the \emph{minimal}
elements of a set. The minimal elements are the elements that are
not dominated by any other in the set. 
\end{defn}
The set of minimal elements might be empty even if $S$ is nonempty.

\begin{defn}[Least element / minimum]
\label{def:min}Lowercase ``$\min$'' denotes\emph{ the least}
element, an element that dominates all others, if it exists. 

\[
\posAmin S=x\quad\Leftrightarrow\quad(x\in S)\wedge\left((y\in S)\Rightarrow(x\posAleq y)\right).
\]
A least element need not exist, but if it exists it is unique.
\end{defn}
If $\min S$ exists, then $\Min S=\{\min S\}$. However, $\Min S\neq\emptyset$
does not imply $\min S$ exists. 

The set of minimal elements of a set are an antichain, so $\Min$
is a map from the power set $\pset(\posA)$ to the antichains $\antichains\posA$:
\begin{align*}
\Min\colon\pset(\posA) & \rightarrow\antichains\posA,\\
S & \mapsto\{x\in S:\ (y\in S)\wedge(y\posleq x)\Rightarrow(x=y)\ \}.
\end{align*}

$\Max$ and $\max$ are similarly defined.

\subsection{Upper sets, lower sets}

An ``upper set'' is a subset of a poset that is closed upward.

\begin{defn}[Upper sets]
A subset $S\subseteq\posA$ is an upper set iff $x\in S$ and $x\posleq y$
implies $y\in S$. 
\end{defn}
Call $\upsets\posA$ the set of upper sets of $\posA$. By this
definition, the empty set is an upper set: $\emptyset\in\upsets\posA$.

The upper closure operator ``$\upit$'' maps a subset of a poset
to an upper set.
\begin{defn}[Upper closure]
\label{def:upper-closure}The upper closure operator $\upit$ maps
a subset to the smallest upper set that includes it: 
\begin{eqnarray*}
\upit\colon\pset(\posA) & \rightarrow & \upsets\posA,\\
S & \mapsto & \{y\in\posA:\exists\,x\in S:x\posleq y\}.
\end{eqnarray*}
\end{defn}

\captionsideleft{\label{fig:antichains_upsets}}{\includegraphics[scale=0.4]{boot-art/1509-gmcdp/gmcdp_antichains_upsets}}


\subsection{Our developments}
\begin{lem}
$\upsets\posA$ is a poset itself, with the order given by 
\begin{equation}
A\posleq_{\upsets\posA}B\qquad\equiv\qquad A\supseteq B.\label{eq:up_order}
\end{equation}
\end{lem}
Note in (\ref{eq:up_order}) the use of ``$\supseteq$'' instead
of ``$\subseteq$'', which might seem more natural. This choice
will make things easier later. 

In the poset $\left\langle \upsets\posA,\posleq_{\upsets\posA}\right\rangle $,
the top is the empty set, and the bottom is the entire poset $\posA$.

By using the upper closure operator, we can define an order on antichains
using the order on the upper sets (\figref{antichains_upsets}).
\begin{lem}
\label{lem:antichains-are-poset}$\antichains\posA$ is a poset with
the relation $\posleq_{\antichains\posA}$ defined by
\[
A\posleq_{\antichains\posA}B\qquad\equiv\qquad\upit A\supseteq\upit B.
\]
\end{lem}
In the poset $\left\langle \antichains\posA,\posleq_{\antichains\posA}\right\rangle $,
the top is the empty set:$\top_{\antichains\posA}=\emptyset.$ If
a bottom for $\posA$ exists, then the bottom for $\antichains\posA$
is the singleton containing only the bottom for $\posA$: $\bot_{\antichains\posA}=\{\bot_{\posA}\}.$


\subsection{Monotonicity}
\begin{defn}[Monotonicity]
\label{def:monotone}A map $f\colon\posA\rightarrow\posB$ between
two posets is \emph{monotone} iff $x\posAleq y$ implies $f(x)\posBleq f(y)$. 
\end{defn}
%

\subsection{Complete partial orders (CPOs)}
\begin{defn}[Directed set]
A set $S\subseteq\posA$ is \emph{directed} if each pair of elements
in $S$ has an upper bound: for all $a,b\in S$, there exists $c\in S$
such that $a\posleq c$ and $b\posleq c$. 
\end{defn}

\begin{defn}[Completeness]
\label{def:cpo}A poset is a \emph{directed complete partial order}
(\DCPO) if each of its directed subsets has a supremum (least of
upper bounds). It is a \emph{complete partial order} (\CPO) if it
also has a bottom.

\end{defn}
\begin{example}[Completion of $\nonNegReals$ to $\nonNegRealsComp$]
\label{exa:Rcomp}The set of real numbers $\mathbb{R}$ is not
a \CPO, because it lacks a bottom. The nonnegative reals $\nonNegReals=\{x\in\reals\mid x\geq0\}$
have a bottom $\bot=0$, however, they are not a \DCPO because some
of their directed subsets do not have an upper bound. For example,
take $\nonNegReals$, which is a subset of $\nonNegReals$. Then $\nonNegReals$
is directed, because for each $a,b\in\nonNegReals$, there exists $c=\max\{a,b\}\in\nonNegReals$
for which $a\leq c$ and $b\leq c$. One way to make $\left\langle \nonNegReals,\leq\right\rangle $
a \CPO is by adding an artificial top element $\top$, by defining $\nonNegRealsComp\triangleq\nonNegReals\cup\{\top\},$
and extending the partial order $\leq$ so that $a\leq\top$ for
all $a\in\reals^{+}$. 
\end{example}

\begin{defn}[\scottcontinuity]
\label{def:scott}A map $f:\posA\rightarrow\posB$ between DCPOs
is\textbf{ }\emph{\scottcontinuous{}}\textbf{ }iff for each directed
subset $D\subseteq\posA$, the image $f(D)$ is directed, and $f(\sup D)=\sup f(D).$
\end{defn}
\begin{rem}
\scottcontinuity implies monotonicity.
\end{rem}
%
\begin{rem}
\scottcontinuity does not imply topological continuity. A map from
the CPO $\langle\Rcomp,\leq\rangle$ to itself is \scottcontinuous
iff it is nondecreasing and left-continuous. For example, the ceiling
function $x\mapsto\left\lceil x\right\rceil $  is \scottcontinuous
(\figref{ceil}).
\end{rem}
\captionsideleft{\label{fig:ceil}}{\includegraphics[scale=0.33]{boot-art/1512-mcdp-tro/gmcdptro_ceil}}

\emph{}

\subsection{Fixed points}
\begin{defn}[Fixed point of a map]
\label{def:fixed-point}A \emph{fixed} \emph{point} of $f:\posA\rightarrow\posA$
is a point $x$ such that $f(x)=x$. 
\end{defn}
A map might have zero, one, or more fixed points.
\begin{defn}[Least fixed point of a map]
\label{def:least-fixed-point}A \emph{least fixed point} of $f:\posA\rightarrow\posA$
is the minimum (if it exists) of the set of fixed points of $f$:
\begin{equation}
\lfp(f)\,\,\doteq\,\,\min_{\posleq}\,\{x\in\posA\colon f(x)=x\}.\label{eq:lfp-one}
\end{equation}
The equality in \eqref{lfp-one} can be relaxed to ``$\posleq$''.
\end{defn}
The least fixed point need not exist. 

\subsection{Kleene's algorithms\label{sec:Monotonicity-and-fixed}}

We will use Kleene's theorem, a celebrated result that is used in
disparate fields. It is used in computer science for defining denotational
semantics (see, e.g., \cite{manes86}). It is used in embedded systems
for defining the semantics of models of computation (see, e.g., \cite{lee10}).

Monotonicity of the map $f$ plus completeness is sufficient to ensure
existence.
\begin{lem}[{\cite[CPO Fixpoint Theorem II, 8.22]{davey02}}]
\label{lem:CPO-fix-point-2}If $\posA$ is a \CPO and $f:\posA\rightarrow\posA$
is monotone, then $\lfp(f)$ exists.
\end{lem}
%

With the additional assumption of \scottcontinuity, Kleene's algorithm
is a systematic procedure to find the least fixed point.
\begin{lem}[{Kleene's fixed-point theorem \cite[CPO fixpoint theorem I, 8.15]{davey02}}]
\label{lem:kleene-1}Assume $\posA$ is a \CPO, and $f:\posA\rightarrow\posA$
is \scottcontinuous. Then the least fixed point of $f$ is the supremum
of the Kleene ascent chain 
\[
\bot\posleq f(\bot)\posleq f(f(\bot))\posleq\cdots\posleq f^{(n)}(\bot)\leq\cdots.
\]
\end{lem}

\noindent\fbox{\begin{minipage}[t]{1\columnwidth - 2\fboxsep - 2\fboxrule}%
\textbf{Parallel and divergences with fixed point theory.} For readers
from other engineering backgrounds, the best way to appreciate the
results is to see them as the parallel to Banach's theorem on metric
spaces, transcribed below as \lemref{banach}.
\begin{defn}
\label{def:complete-metric-space}A metric space $\left\langle \mathcal{X},d\right\rangle $
is \emph{complete} iff every Cauchy sequence in $\mathcal{X}$ has
a limit in $\mathcal{X}$.
\end{defn}
%
\begin{defn}
\label{def:contraction}A map $f:\mathcal{X}\rightarrow\mathcal{X}$
on a metric space $\left\langle \mathcal{X},d\right\rangle $ is
a \emph{contraction} if there exists a constant $q\in[0,1)$ such
that $d(f(x_{1}),f(x_{2}))\leq q\,d(x_{1},x_{2})$ for all $x_{1},x_{2}\in\mathcal{X}$.
\end{defn}
\begin{lem}[Banach's Fixed Point Theorem]
\label{lem:banach}Let $f$ be a contraction on a complete metric
space $\left\langle \mathcal{X},d\right\rangle $. Then $f$ has
a unique fixed point in $\mathcal{X}$, and this point can be found
by computing $\lim_{n\rightarrow\infty}f^{n}(x_{0})$ starting from
any $x_{0}\in\mathcal{X}$. 
\end{lem}
The equivalent of complete metric space (\defref{complete-metric-space})
in order theory is that of complete partial order (\defref{cpo}).

The equivalent of contractivity (\defref{contraction}) is monotonicity
(\defref{monotone}), or the stronger property of \scottcontinuity
(\defref{scott}).

Differences are:

start from a fixed point%
\end{minipage}}

%

%

\begin{defn}[Meet]
\label{def:meet} 
\end{defn}
%
\begin{defn}[Join]
\label{def:join} 
\end{defn}
%
\begin{defn}[]
{[}Power set{]}\label{def:powerset} The power set $\pset(\posA)$
of a poset $\mathcal{Q}$ is a poset with the order given by inclusion:
\[
a\preccurlyeq_{\pset(\posA)}b\quad\equiv\quad a\subseteq b.
\]
In this poset, meet and join are union and intersection, respectively.
In this order, $\varnothing$ is the top.
\end{defn}
%
\begin{defn}[Cartesian product of posets]
 \label{def:posets-cartesian-product} For two posets $\mathcal{P},\mathcal{Q}$,
the Cartesian product $\mathcal{P}\times\mathcal{Q}$ is the set of
pairs $\langle p,q\rangle$ for $p\in\mathcal{P}$ and $q\in\mathcal{Q}$.
The order is the following: 
\[
\langle p{{}_1},q{{}_1}\rangle\preccurlyeq\langle p{{}_2},q{{}_2}\rangle\quad\equiv\quad(p{{}_1}\preccurlyeq_{\mathcal{P}}p{{}_2})\bigwedge(q{{}_1}\preccurlyeq_{\mathcal{Q}}q{{}_2}).
\]

\label{def:upperset} 
\end{defn}
%
\begin{defn}[Lower set]
\label{def:lowerset} 
\end{defn}
%
\begin{defn}[Monotone map]
{[}{]}\label{def:monotone-map} 
\end{defn}
%
\begin{defn}[Monotone relation]
{[}{]}\label{def:monotone-relation} 
\end{defn}
%
\begin{defn}[Upper closure]
{[}{]}\label{def:upperclosure}
\end{defn}
%
\begin{defn}[Lower closure]
{[}{]}\label{def:lowerclosure}
\end{defn}
%
\begin{defn}[Empty product]
{]}\label{def:One} The space $\One=\{\langle\rangle\}$ is the empty
product, which contains only one element, the empty tuple $\langle\rangle$. 

Antichains of One.

You might think about $\One$ as providing one bit of information:
whether something is feasible or not.
\end{defn}

