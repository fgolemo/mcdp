
# Basic order theory  {#app:basic-order-theory}

<!-- Ligature: efficient affe cafilo. Digits: 1 2 3 4 5 000123679 -->

We will use basic facts about order theory. Davey and Priestley~\cite{davey02}
and Roman~\cite{roman08} are possible reference texts.

I can also cite <a href='#bib:davey02'>that paragraph x.y</a>.


Let $⟨ 𝒫,≼_𝒫⟩ $ be a partially ordered set
(poset), which is a set 𝒫 together with a partial order $≼_𝒫$ (a
reflexive, antisymmetric, and transitive relation). The partial
order~"$≼_𝒫$" is written as "$≼$" if the context is clear. If a poset
has a least element, it is called "bottom" and it is denoted by $⊥_𝒫$.
If the poset has a maximum element, it is called "top" and denoted
as $⊤_𝒫$.


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

Call $𝖠𝒫$ the set of all antichains in 𝒫. By this
definition, the empty set is an antichain: $∅ ∈ 𝖠𝒫$.

\begin{defn}[Width and height of a poset] \label{def:poset-width-height}
$\mathsf{width}(𝒫)$ is the maximum cardinality of an antichain in 𝒫
and $\mathsf{height}(𝒫)$ is the maximum cardinality of a chain in 𝒫.
\end{defn}


### Minimal elements

Uppercase "$𝖬𝗂𝗇$" will denote the \emph{minimal} elements of a set. The minimal
elements are the elements that are not dominated by any other in the set.
Lowercase "$𝗆𝗂𝗇$" denotes \emph{ the least} element, an element that dominates
all others, if it exists. (If $𝗆𝗂𝗇 S$ exists, then $𝖬𝗂𝗇 S=⦃𝗆𝗂𝗇 S⦄$.)

The set of minimal elements of a set are an antichain, so $𝖬𝗂𝗇$ is a map from
the power set $\pset(𝒫)$ to the antichains $𝖠𝒫$:

\begin{align*}
𝖬𝗂𝗇: \pset(𝒫) & → 𝖠𝒫,\\
S             & ↦ ⦃ x ∈ S:\ (y ∈ S)∧(y ≼ x)⇒(x=y)\ ⦄.
\end{align*}

$\Max$ and $\max$ are similarly defined.

### Upper sets

An "upper set" is a subset of a poset that is closed upward.

\begin{defn}[Upper sets]
A subset $S⊆𝒫$ is an upper set iff $x ∈ S$ and $x ≼ y$
implies $y ∈ S$.
\end{defn}

Call $𝖴𝒫$ the set of upper sets of 𝒫. By this
definition, the empty set is an upper set: $∅ ∈ 𝖴𝒫$.

\begin{lem}
$𝖴𝒫$ is a poset itself, with the order given by
\begin{equation}
    A ≼_{𝖴𝒫} B ⎵ ≡ ⎵ A ⊇ B.\label{eq:up_order}
\end{equation}
\end{lem}

Note in (\ref{eq:up_order}) the use of~"$⊇$" instead
of~"$⊆$", which might seem more natural. This choice
will make things easier later.

In the poset $⟨ 𝖴𝒫,≼_{𝖴𝒫}⟩ $,
the top is the empty set, and the bottom is the entire poset 𝒫.


### Order on antichains

The upper closure operator "$↑$" maps a subset of a poset
to an upper set.
\begin{defn}[Upper closure]
The operator $↑$ maps a subset to the smallest upper set that
includes it:
\begin{eqnarray*}
↑ :   \pset(𝒫)   & → & 𝖴𝒫,\\
                S & ↦ & ⦃ y ∈ 𝒫:  ∃ ⌑ x ∈ S: x ≼ y⦄.
\end{eqnarray*}
\end{defn}

\captionsideleft{\label{fig:antichains_upsets}}{\includegraphics[scale=0.4]{boot-art/1509-gmcdp/gmcdp_antichains_upsets}}

By using the upper closure operator, we can define an order on antichains
using the order on the upper sets~(\figref{antichains_upsets}).
\begin{lem}
\label{lem:antichains-are-poset}$𝖠𝒫$ is a poset with
the relation $≼_{𝖠𝒫}$ defined by
\[
A ≼_{𝖠𝒫} B⎵ ≡ ⎵ ↑A ⊇ ↑B.
\]
\end{lem}

In the poset $⟨ 𝖠𝒫,≼_{𝖠𝒫}⟩$, the top is the empty set: $⊤_{𝖠𝒫}=∅.$ If a
bottom for 𝒫 exists, then the bottom for $𝖠𝒫$ is the singleton containing
only the bottom for 𝒫: $⊥_{𝖠𝒫}=⦃⊥_{𝒫}⦄.$


### Monotonicity and fixed points     {#sub:Monotonicity-and-fixed}

We will use Kleene's theorem, a celebrated result that is used in
disparate fields. It is used in computer science for defining denotational
semantics~(see, e.g.,~\cite{manes86}). It is used in embedded systems
for defining the semantics of models of computation~(see, e.g.,~\cite{lee10}).

\begin{defn}[Directed set]
A set $S ⊆ 𝒫$ is *directed* if each pair of elements
in $S$ has an upper bound: for all $a, b ∈ S$, there exists $c ∈ S$
such that $a ≼ c$ and $b ≼ c$.
\end{defn}

\begin{defn}[Completeness]  \label{def:cpo}
A poset is a *directed complete partial order* (𝖣𝖢𝖯𝖮)
if each of its directed subsets has a supremum (least of
upper bounds). It is a *complete partial order* (𝖢𝖯𝖮) if it
also has a bottom.

\end{defn}
\begin{example}[Completion of $ℝ₊$ to $\Rcomp$]
\label{exa:Rcomp}
The set of real numbers $ℝ$ is not a 𝖢𝖯𝖮, because it lacks a bottom. The
nonnegative reals $ℝ₊=⦃x ∈ ℝ ∣ x ≥ 0⦄$ have a bottom $⊥ = 0$, however, they are
not a 𝖣𝖢𝖯𝖮 because some of their directed subsets do not have an upper
bound. For example, take $ℝ₊$, which is a subset of $ℝ₊$. Then $ℝ₊$ is directed,
because for each $a,b ∈ ℝ₊$, there exists $c=\max⦃a, b⦄ ∈ ℝ₊$ for which $a ≤ c$
and $b ≤ c$. One way to make $⟨ℝ₊,≤⟩$ a 𝖢𝖯𝖮 is by adding an artificial top
element $⊤$, by defining $\Rcomp ≐ ℝ₊ ∪ ⦃⊤⦄,$ and extending the partial order $≤$
so that $a ≤ ⊤$ for all $a ∈ ℝ₊$.
\end{example}

Two properties of maps that will be important are monotonicity and
the stronger property of 𝖲𝖼𝗈𝗍𝗍𝖼𝗈𝗇𝗍𝗂𝗇𝗎𝗂𝗍𝗒.
\begin{defn}[Monotonicity] \label{def:monotone}
A map $f:𝒫→𝒬$ between
two posets is *monotone* iff $x ≼_𝒫 y$ implies $f(x) ≼_𝒬 f(y)$.
\end{defn}
%
\begin{defn}[𝖲𝖼𝗈𝗍𝗍𝖼𝗈𝗇𝗍𝗂𝗇𝗎𝗂𝗍𝗒]
\label{def:scott}A map $f: 𝒫 → 𝒬$ between DCPOs
is *𝖲𝖼𝗈𝗍𝗍𝖼𝗈𝗇𝗍𝗂𝗇𝗎𝗈𝗎𝗌* iff for each directed
subset $D ⊆ 𝒫$, the image $f(D)$ is directed, and $f(𝗌𝗎𝗉 D)= 𝗌𝗎𝗉 f(D).$
\end{defn}
\begin{rem}
𝖲𝖼𝗈𝗍𝗍𝖼𝗈𝗇𝗍𝗂𝗇𝗎𝗂𝗍𝗒 implies monotonicity.
\end{rem}
%
\begin{rem}
𝖲𝖼𝗈𝗍𝗍𝖼𝗈𝗇𝗍𝗂𝗇𝗎𝗂𝗍𝗒 does not imply topological continuity. A map from
the CPO $⟨\Rcomp,≤⟩$ to itself is 𝖲𝖼𝗈𝗍𝗍𝖼𝗈𝗇𝗍𝗂𝗇𝗎𝗈𝗎𝗌
iff it is nondecreasing and left-continuous. For example, the ceiling
function $x ↦ ⌈x⌉$~ is 𝖲𝖼𝗈𝗍𝗍𝖼𝗈𝗇𝗍𝗂𝗇𝗎𝗈𝗎𝗌 (\figref{ceil}).
\end{rem}
\captionsideleft{\label{fig:ceil}}{\includegraphics[scale=0.33]{boot-art/1512-mcdp-tro/gmcdptro_ceil}}

\begin{defn}[fixed point]
A *fixed point* of $f:𝒫→𝒫$ is a point $x$ such that $f(x)=x$.
\end{defn}

\begin{defn}[least fixed point]
A \emph{least fixed point} of $f:𝒫→𝒫$ is the minimum
(if it exists) of the set of fixed points of $f$:
\begin{equation}
    𝗅𝖿𝗉(f) ⎵ ≐ ⎵  𝗆𝗂𝗇_≼ ⌑ ⦃ x ∈ 𝒫: f(x) = x⦄.     \label{eq:lfp-one}
\end{equation}
\end{defn}

The equality in \eqref{lfp-one} can be relaxed to "$≼$".

The least fixed point need not exist. Monotonicity of the map $f$
plus completeness is sufficient to ensure existence.
\begin{lem}[\cite[CPO Fixpoint Theorem II, 8.22]{davey02}] \label{lem:CPO-fix-point-2}
If 𝒫 is a 𝖢𝖯𝖮 and $f:𝒫→𝒫$ is monotone, then $𝗅𝖿𝗉(f)$ exists.
\end{lem}
%

With the additional assumption of 𝖲𝖼𝗈𝗍𝗍𝖼𝗈𝗇𝗍𝗂𝗇𝗎𝗂𝗍𝗒, Kleene's algorithm
is a systematic procedure to find the least fixed point.
\begin{lem}[Kleene's fixed-point theorem \cite[CPO fixpoint theorem I, 8.15]{davey02}]
\label{lem:kleene-1}
Assume 𝒫 is a 𝖢𝖯𝖮, and $f:𝒫→𝒫$ is 𝖲𝖼𝗈𝗍𝗍𝖼𝗈𝗇𝗍𝗂𝗇𝗎𝗈𝗎𝗌.
Then the least fixed point of $f$ is the supremum
of the Kleene ascent chain
\[
    ⊥≼ f(⊥) ≼ f(f(⊥)) ≼ ⋯ ≼ f^{(n)}(⊥) ≼ ⋯.
\]
\end{lem}


### Other definitions to be written

\begin{defn}[Meet]\label{def:meet} 𝖷𝖷𝖷
\end{defn}

\begin{defn}[Join]\label{def:join} 𝖷𝖷𝖷
\end{defn}


\begin{defn}[Power set]\label{def:powerset}
The power set $\pset(𝒬)$ of a poset $𝒬$ is a poset with the
order given by inclusion:
$$
   a ≼_{\pset(𝒬)} b ⍽  ≡  ⍽   a ⊆ b.
$$
In this poset, [meet](#def:meet) and [join](#def:join) are
union and intersection, respectively.
\end{defn}
<!-- %
In this order, $∅$ is the top.  -->


\begin{defn}[Cartesian product of posets]
  \label{def:posets-cartesian-product}
%
For two posets $𝒫, 𝒬$, the Cartesian product $𝒫 × 𝒬$
is the set of pairs $⟨p, q⟩$ for $p ∈ 𝒫$ and $q ∈ 𝒬$.
The order is the following:
%
$$
    ⟨p₁, q₁⟩ ≼ ⟨p₂, q₂⟩  ⍽  ≡  ⍽   (p₁ ≼_𝒫 p₂) ∧ (q₁ ≼_𝒬 q₂).
$$
\end{defn}

\begin{defn}[Upper set]\label{def:upperset} \xxx
\end{defn}

\begin{defn}[Lower set]\label{def:lowerset} \xxx
\end{defn}

\begin{defn}[Monotone map]\label{def:monotone-map} \xxx
\end{defn}

\begin{defn}[Monotone relation]\label{def:monotone-relation} \xxx
\end{defn}

\begin{defn}[Upper closure]\label{def:upperclosure} \xxx
\end{defn}

\begin{defn}[Lower closure]\label{def:lowerclosure} \xxx
\end{defn}

\begin{defn}[Empty product]\label{def:One}
The space $𝟏 = ⦃ ⟨⟩ ⦄$ is the empty product, which contains only one element, the empty tuple $⟨⟩$.
\end{defn}

Antichains of One.

You might think about $𝟏$ as providing one bit of information:
whether something is feasible or not.

\begin{defn}\label{def:MCDP} 𝖷𝖷𝖷
\end{defn}
