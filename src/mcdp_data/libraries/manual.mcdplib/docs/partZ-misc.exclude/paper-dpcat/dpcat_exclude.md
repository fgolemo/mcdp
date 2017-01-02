\documentclass[10pt,oneside,article]{memoir}


\usepackage{amsmath}
\usepackage{mathtools}
\usepackage{amsthm}
\usepackage{amssymb}
\usepackage{makecell}
\usepackage{fixltx2e}
\usepackage[T1]{fontenc}


\usepackage[tracking=true,kerning=true,spacing=true,factor=1000,stretch=15,shrink=20]{microtype}
\SetTracking{encoding={*}, shape=sc}{0}

\usepackage{times}




\usepackage{bm}
\usepackage{inputenc}
\usepackage{amssymb}
\usepackage[mathscr]{eucal}

\usepackage[usenames,dvipsnames]{xcolor}
\usepackage{paralist}
\usepackage{booktabs}
\usepackage{tikz}
\usepackage{tikz-cd}
\usepackage{pgfplots}
\usepgfplotslibrary{fillbetween}
\usepackage[all]{xy}
\usepackage[textsize=tiny]{todonotes}
\usepackage[bookmarks,colorlinks, linkcolor={blue!60!black}, citecolor={red!50!black}, urlcolor={blue!80!black}]{hyperref}



\usepackage[top=1in, bottom=1in, left=0.6in, right=2in]{geometry}

\usepackage[capitalize]{cleveref}

\usetikzlibrary{decorations.markings,arrows.meta,calc,fit,quotes,cd}

\theoremstyle{definition}
\newtheorem{theorem}{Theorem}[chapter]
\newtheorem*{theorem*}{Theorem}

\newtheorem{proposition}[theorem]{Proposition}
\newtheorem*{proposition*}{Proposition}
\newtheorem{corollary}[theorem]{Corollary}
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem*{lemma*}{Lemma}

\theoremstyle{definition}
\newtheorem{definition}[theorem]{Definition}
\newtheorem{construction}[theorem]{Construction}

\theoremstyle{remark}
\newtheorem{example}[theorem]{Example}
\newtheorem{remark}[theorem]{Remark}
\newtheorem{warning}[theorem]{Warning}







\DeclareMathOperator{\id}{id}
\DeclareMathOperator{\dom}{dom}
\DeclareMathOperator{\cod}{cod}
\DeclareMathOperator{\dvert}{Vert}
\DeclareMathOperator{\Lax}{Lax}
\DeclareMathOperator{\Hom}{\mathsf{Hom}}
\DeclareMathOperator{\Mor}{Mor}
\DeclareMathOperator{\Ob}{\mathsf{Ob}}
\DeclareMathOperator{\MOb}{\lvert\mspace{2mu}\cdot\mspace{2mu}\rvert}
\DeclareMathOperator{\Tr}{Tr}
\DeclareMathOperator*{\colim}{colim\;}
\DeclareMathOperator{\Coll}{Col}



\newcommand{\cat}[1]{\mathscr{#1}}
\newcommand{\Cat}[1]{\mathbf{#1}}
\newcommand{\fun}[1]{\mathcal{#1}}
\newcommand{\Fun}[1]{\mathbf{#1}}
\newcommand{\thing}[1]{\tn{#1}}
\newcommand{\marker}{\Huge {\color{red}{Marker: continue from here.}}\newline\normalsize}
\def\too{\longrightarrow}
\newcommand{\from}{\leftarrow}
\newcommand{\From}{\xleftarrow}


\def\Set{\Cat{Set}}
\def\Poset{\Cat{Pos}}
\def\FinSet{\Cat{FinSet}}
\def\ODS{\mathbf{ODS}}
\def\VF{\mathbf{VF}}
\newcommand{\To}[1]{\xrightarrow{#1}}
\def\iso{\cong}
\def\ss{\subseteq}

\def\TFS{\Cat{TFS}}
\def\dom{\tn{dom}}
\def\cod{\tn{cod}}
\def\op{^{\text{op}}}
\def\bigid{\mathds{1}}
\def\NN{\mathbb N}
\def\ZZ{\mathbb Z}
\def\RR{\mathbb R}
\def\Vect{\mathbf{Vect}}
\newcommand{\ol}[1]{\overline{#1}}
\newcommand{\longnote}[2][4.9in]{\fcolorbox{black}{yellow}{\parbox{#1}{\color{black} #2}}}
\newcommand{\shortnote}[1]{\fcolorbox{black}{yellow}{\color{black} #1}}
\newcommand{\inp}[1]{#1^{\tn{in}}}
\newcommand{\outp}[1]{#1^{\tn{out}}}
\newcommand{\vinp}[1]{\ol{\inp{#1}}}
\newcommand{\voutp}[1]{\ol{\outp{#1}}}
\newcommand{\expt}[2]{#1_{#2}^{\text{exp}}}
\newcommand{\loc}[2]{#1_{#2}^{\text{loc}}}
\def\Man{\mathbf{Man}}
\def\Euc{\mathbf{Euc}}
\def\bfL{\mathbf{Lin}}
\def\bfW{\mathbf{W}}
\newcommand{\Opd}[1]{\mathcal{O}#1}
\def\tn{\textnormal}
\def\LCob{\Cat{LCob}}
\def\|{\;|\;}
\def\UU{\mathbf{U}}
\def\m1{{-1}}
\def\singleton{{\{\ast\}}}
\newcommand{\pair}[2]{\langle#1,#2\rangle}

\newcommand{\comp}[1]{\hat{#1}}
\newcommand{\conj}[1]{\check{#1}}



\def\DP{\Cat{DP}}
\def\DPI{\Cat{DPI}}

\def\Bool{\text{Bool}}
\def\split{\text{split}}
\def\para{\text{par}}
\def\Conw{\text{Conw}}
\def\exec{\text{exec}}
\def\eval{\text{eval}}
\def\fix{\text{fix}}


\newcommand{\funsp}{\mathsf{F}}
\newcommand{\ressp}{\mathsf{R}}
\newcommand{\impsp}{\mathsf{I}}
\newcommand{\afun}{\mathsf{f}}
\newcommand{\ares}{\mathsf{r}}
\newcommand{\adp}{g}


\newcommand{\antichains}{\mathcal{A}}
\newcommand{\uppersets}{\mathcal{U}}
\newcommand{\lowersets}{\mathcal{L}}
\newcommand{\powerset}{\mathcal{P}}
\def\slashedrightarrow{\relbar\joinrel\mapstochar\joinrel\rightarrow}

\newcommand{\grayout}[1]{{\color{gray}#1}}
\newcommand{\redout}[1]{{\color{red}#1}}

\newcommand{\marginAC}[1]{\marginpar{\footnotesize \color{blue}#1}}

\newcommand{\posleq}{\preceq}
\newcommand{\posgeq}{\succeq}
\newcommand{\One}{\mathbf{1}}

\newcommand{\False}{\mathsf{False}}
\newcommand{\True}{\mathsf{True}}
\newcommand{\unsure}[1]{{\color{red}#1}}

\def\O{\emptyset}

\begin{document}


\title{Categorical Co-Design}

\author{Andrea Censi\and David I. Spivak\and Joshua Z. Tan}

\maketitle








\chapter{Introduction}
In this paper, a ``design problem'' describes an optimization problem involving \emph{functionalities}, \emph{resources}, and \emph{implementations}.
\begin{itemize}
\item The functionality space is a poset $\funsp$. 
\item The resources space is a poset $\ressp$.
\item The implementation space is a set $\impsp$, with no further assumptions.
\end{itemize}
In the course of this paper, we will look at design problems represented as
\begin{enumerate}
\item a morphism $\adp : \funsp \slashedrightarrow \ressp$ in the category of design problems, denoted $\DP$,
\item a monotone map $\adp : \funsp\op \times \ressp \to_{\Poset} \Bool$, which we use to define the semantics of $\adp \in \Mor \DP$,
\item a monotone map $h_\adp : \funsp \to \antichains \ressp$ mappings functionalities to minimal solutions of the design problem, e.g. antichains of $\ressp$,
\item a poset map $H_\adp : \uppersets \funsp \to \uppersets \ressp$ mapping upper sets of functionalities to upper sets of possible solutions,
\item a dynamical system whose fixed point is the solution to a design problem, 
\item and a Python program that computes the dynamical system above using the Kleene ascent algorithm.
\end{enumerate}

The items above are ordered in terms of decreasing abstraction. At some point before items 5 and 6, we will need assume that $\funsp$ and $\ressp$ are not only posets but complete partial orders, or CPOs, since doing so is necessary to apply Kleene ascent in item 6.








\begin{figure}
\includegraphics[width=\textwidth]{fig1tmp}
\caption{The relation between the concepts defined in this paper}
\end{figure}

\clearpage


\chapter{Background}
Category theory became the language of 20th-century mathematics because it proved to be the right abstraction for translating ideas from one field of mathematics, e.g. topology, to another field of mathematics, e.g. algebra. More recently, category theory has become an unexpectedly useful and economical tool for modeling a range of different disciplines, including quantum mechanics \cite{coecke}, systems biology \cite{plotkin}, complex networks \cite{spivak}, database theory \cite{rosebrugh, spivak}, and programming language semantics \cite{abramsky}.

Sections~\ref{?}, \ref{?} do not require extensive understanding of category theory beyond the basic notions of category and functor. Reading the proofs will require some familiarity with category theory, up to the level of, for example, \cite{leinster}.

\emph{Posets}, or partially-ordered sets, are sets endowed with a transitive, anti-symmetric, and reflexive relation, $\leq$. Posets form a category, $\Poset$, whose objects are posets and whose morphisms are monotone (order-preserving) maps.

Directed complete partial orders, i.e. \emph{dcpo}s, are posets with the property that every directed subset has a supremum. Throughout this paper, we will always assume that dcpos are \emph{pointed}, i.e. have a bottom element, $\bot$. Dcpos form a category whose objects are DCPOs and whose morphisms are Scott-continuous maps. DCPOs and Scott-continuous maps arise very naturally in domain theory for the same reason that they arise in co-design problems: they represent just those computational processes that are guaranteed to terminate.


\emph{Please write here either definitions or clear references for all the concepts 
that are used in the paper, along with special notation used.}


Assume known and incontrovertible definition:

* basic poset theory (poset, antichain, etc.)

Assume known concept but recall definition and choice of notation:

* CPO - note that the literature is not coherent
* monotone map 
* Scott-continuous
* category theory (functor, endofunctor, hom-functor, natural bijection, product, 
  coproduct, biproduct)
* Define:
}



\clearpage


\begin{lemma}[Trace] $\DP$ is a \emph{traced symmetric monoidal category}
    when equipped with the trace \[\Tr : \Hom_\DP(A\times C, B \times C) \to \Hom_\DP(A,B)\] defined as follows.
    Suppose that we have
    \[
    \adp : A \otimes C \rightarrow_\DP B \otimes C.
    \]
    Then we can define
    \[
    \Tr_{A,B}^C(\adp) : A \rightarrow_\DP B
    \]
    as follows:
    \begin{align}
    
        [\Tr_{A,B}^C(\adp)] : A\op\times B &\rightarrow \Bool, \label{eq:trace1} \\
        \langle \overline{a}, b \rangle &\mapsto \bigvee_{c\in C}
            [\adp](
                \langle \overline {a}, c\op \rangle,
                \langle b, c  \rangle
            ). \label{eq:trace2}
    \end{align}
\end{lemma}








































\chapter{The Category of Design Problems (DP)}

\section{Intuition}
Some of the representations that we consider are ``input''--``output'' in nature, and contain only references to resources and functionality. The choice of $\Bool$ below (rather than a set of implementations, $I$) means we are calculating only the existence of a implementation rather than the particular implementation for a given functionality-resource pair $(a,b)$.

\begin{enumerate}
\item A design problem is a morphism from functionalities to resources in the category $\DP$. We will write:
\[
    \adp :  \funsp \slashedrightarrow \ressp
\]
where $\funsp$ and $\ressp$ are two posets.
\item Every such design problem in $\DP$ is concretely represented by a monotone, Boolean function, where $\Bool$ is given the ordering $0 < 1$. We write
\[
    \adp :  \funsp\op\times\ressp \to_\Poset \Bool
\]
where the map $\adp$ is monotone, i.e. preserves the ordering from $\funsp\op\times\ressp$ to $\Bool$. When we say that $\adp$ is monotone, we are saying that the set of all feasible solutions to $\adp$ forms an upper set in $\funsp\op \times \ressp$. In particular, $a \leq b$ implies that if $a$ is a resource feasible for some functionality $x$ (in the sense that $a$ can be used to provide $x$), then $b$ will also be feasible for $x$. 

$\adp$ is an instance of a \emph{profunctor} from $A$ to $B$, thus the notation $\adp : A \slashedrightarrow B$ to represent $\adp : A\op\times B \to_\Poset \Bool$.

\emph{Interpretation: for a particular $\afun\in\funsp$ and $\ares\in\ressp$, $\adp(\afun,\ares)$ answers the question ``is $\afun$ feasible with resources $\ares$?''.}

\item A design problem represented as a monotone function between functionality and sets of minimal resources. We will write
\begin{align*}
    h_{\adp} : \funsp &\to \antichains\ressp \\
    \afun &\mapsto \min_{r \in \ressp} \adp(\afun, \ares) = \text{True}
\end{align*}
where $\antichains\ressp$ are the antichains of $\ressp$.

\emph{Interpretation:  For a particular $\afun\in\funsp$, $h_\adp(\afun)$ answers the question ``what are the minimal resources needed to implement $\afun$?''.}

\end{enumerate}
 
We will show that design problems in the sense of (2) correctly form a category as defined by (1), and in fact a traced symmetric monoidal category. 











\section{Formal Definition of DP}

Let $\Bool$ be the poset $\{0,1\}$ with $0 \leq 1$, and let $\One$ be the one-element poset with $\{\ast, \leq\}$.

\begin{definition}\label{def:DP}
The category of design problems $\DP$ is a category given by the following data:
\begin{description}
\item [Objects] The objects of $\DP$ are posets:
\[
\Ob(\DP) = \Ob(\Poset).
\]
\item [Morphisms] The set of morphisms from poset $A$ to poset $B$ is defined to be the set of all monotone maps from the poset $A\op \times B$ to the poset $\Bool$:
\[
    \Hom_\DP (A,B) \simeq \Hom_\Poset (A\op \times B, \Bool).
\]

Each morphism $\adp\colon  A \to_\DP B$, called a \emph{design problem},
is defined to be a monotone function
\[
  \adp \colon  A\op \times B \rightarrow_{\Poset} \Bool.
\]

\item [Composition of morphisms] Given two morphisms $\adp_1 \colon  A \to_\DP B$ and $\adp_2 \colon  B \to_\DP C$ we can obtain a new morphism $\adp_2\circ \adp_1\colon  A \to_\DP C$, defined as
\begin{eqnarray}
  \adp_2 \circ \adp_1 \colon A\op \times C & \rightarrow_{\Poset} &  \Bool, \label{eq:composition} \\
  \langle \overline{a},c \rangle &\mapsto& \bigvee_{b \in B} \adp_1(\overline{a},b) \wedge \adp_2(b\op,c).\label{eq:composition2}
\end{eqnarray}

That is, there exists a solution for the composed design problem $\adp_2 \circ \adp_1(a,c)$ if and only if there exists some resource $b \in B$ which satisfies both design problems $\adp_1(a,b)$ and $\adp_2(b,c)$.

\item [Identity] The identity $\id_A : A \to A$ is given by
\begin{eqnarray}
  \id_A \colon A\op \times A & \rightarrow_{\Poset} &  \Bool, \label{eq:identity}\\
  \langle \overline{a}, a \rangle &\mapsto&
  \overline{a}\op \posleq_{A} a.
\end{eqnarray}

\end{description}
\end{definition}

The following lemmas show that this is, indeed, a well-defined category.

\begin{lemma} The composition operation \eqref{eq:composition} defines a morphism in $\DP$ and it is an associative operation.\end{lemma}

\begin{proof}
To show that \eqref{eq:composition2} is a morphism in $\DP$, we
need to show that $\adp_2 \circ \adp_1(\overline{a},c)$ is monotone in $\overline{a}$ and $c$. This is true because $\adp_1(\overline{a},b)$ is monotone in $\overline{a}$, $\adp_2(b\op,c)$  is monotone in $c$, and the conjunction ``$\wedge$'' is monotone in both variables.

To show that the operation is associative, we can use distributivity and commutativity in $\Bool$ to show that
\begin{align*}
&[(\adp_1 \circ \adp_2) \circ \adp_3] (\overline{a},d) \\
&= \bigvee_{c \in C} \left (\ \bigvee_{b\in B } [\adp_1](\overline{a},b) \wedge [\adp_2](b\op,c) \right ) \; \wedge \; [\adp_3] (c\op, d) \\
&= \bigvee_{c \in C} \left (\ \bigvee_{b\in B } [\adp_1](\overline{a},b)
\wedge [\adp_2](b\op,c) \wedge [\adp_3] (c\op, d)
    \right ) \\
&= \bigvee_{b \in B } [\adp_1](\overline{a},b) \wedge \left ( \bigvee_{c\in C} [\adp_2](b\op,c) \wedge [\adp_3] (c\op, d) \right ) \\
&= [\adp_1 \circ (\adp_2 \circ \adp_3 )] (\overline{a}, d).
\end{align*}
\end{proof}

\begin{lemma} Equation \eqref{eq:identity} indeed defines an identity
for the category.
\end{lemma}

\begin{proof}  If we compose $\id_A$ with $\adp : A \slashedrightarrow B$
we obtain:
\begin{align*}
[\adp \circ \id_A] (\overline{a},b) &= \bigvee_{x \in A} [\id_A] (\overline{a},x) \wedge
  [\adp] (x\op,b) \\
& \{\text{Definition of identity.}\} \\
&= \bigvee_{x\in A} (\overline{a}\op \posleq_{A} x) \wedge [\adp](x\op, b)\\
& \{\text{Let $y = x\op$.}\} \\
&= \bigvee_{y\in A\op} (\overline{a}\op \posleq_{A} y\op) \wedge [\adp](y, b)\\
& \{\text{Reverse the inequality by taking the ${}\op$ of both sides.}\} \\
&= \bigvee_{y\in A\op} (y \posleq_{A\op} \overline{a}  ) \wedge [\adp](y, b)\\

&= [\adp](\overline{a},b).
\end{align*}

\end{proof}

\subsection{Some examples of DPs}

We can define a couple of handy DPs.

\begin{definition}
    The morphism $\False_{A,B}: A \slashedrightarrow B$ is the design problem that
    is always infeasible:
\begin{eqnarray}
  \False_{A,C} \colon A\op \times B & \rightarrow_\Poset \Bool,\\
    \langle \overline{a}, b \rangle & \mapsto \False.
\end{eqnarray}
\end{definition}

\begin{definition}
    The morphism $\True_{A,B}: A \rightarrow_\DP B$ is the design problem that
    is always feasible:
\begin{eqnarray}
  \True_{A,C} \colon A\op \times B & \rightarrow_\Poset \Bool,\\
    \langle \overline{a}, b \rangle & \mapsto \True.
\end{eqnarray}
\end{definition}

Note that if one of the posets is empty, then the two morphisms are the same:
\begin{align}
    \True_{A,\emptyset}&=\False_{A,\emptyset},\\
    \True_{\emptyset,B}&=\False_{\emptyset,B}.
\end{align}


\begin{lemma}[Initial and terminal object] $\DP$ has an initial and terminal object, corresponding to the empty set~$\emptyset$, and it holds that

\[
    A \rightarrow \emptyset \rightarrow B = \False_{A,B}.
\]
\end{lemma}
\begin{proof}
    \todo{fix}
    \unsure{$\{ \ast \}$, in $\DP$ the empty set $\emptyset$ is both the terminal and initial object, since $A \times \emptyset = \emptyset \times A = \emptyset$ and there is a unique (monotone) map from $\emptyset \to \Bool$ by the definition of $\emptyset$.}
\end{proof}


\begin{remark}
    In $\Poset$, the terminal objects are the posets $\One=\{\ast\}$. However, $\One$ is not a
    terminal object in $\DP$. In fact, if both $A$ and $B$ are nonempty,
    $\False_{A,B}$ and $\True_{A,B}$ are two distinct morphisms
    from~$A$ to~$B$.
\end{remark}

\subsection{Monoidal and trace structure}
There are actual several product-like structures in $\DP$, which we list here:
\begin{table}[h!]
\begin{center}
\begin{tabular}{|c|c|c|}
 & induced design problem & type \\
$\sqcup$ & $(\adp_1, \adp_2)(c,x) = \adp_1(c,x) \text{ if }c \in A\op \text{ and } \adp_2(c,x) \text{ if } c \in B\op$ & biproduct \\
$\times$ & $\adp_1 \times \adp_2(a,b,x) = \adp_1(a,x) \wedge \adp_2(b,x)$ & Cartesian product \\
$A \otimes B$ & $\adp_1 \otimes \adp_2(a,b,c,d) = \adp_1(\overline{a}, c) \wedge  [\adp_2](\overline{b}, d).$ & monoidal product \\
\end{tabular}\label{product_list}
\end{center}
\end{table}

\begin{definition}[Monoidal structure of $\DP$]
The category $\DP$ is a monoidal category when equipped with the following monoidal structure:

\begin{itemize}
  \item The monoidal unit $I$ is the poset $\One$.
  \item The monoidal product $\otimes_{\Ob}$ on objects is the Cartesian product of posets:

\begin{eqnarray}
  \otimes_{\Ob} \colon \Ob(\DP) \times \Ob(\DP) & \rightarrow&   \Ob(\DP), \label{eq:identity}\\
  \langle A, B \rangle &\mapsto&  A \times B.
\end{eqnarray}

  \item The monoidal product $\otimes_{\Hom}$ on morphisms is:
\begin{eqnarray}
  \otimes_{\Hom} \colon \Hom_{\DP}(A,C) \times \Hom_{\DP}(A,C) & \rightarrow_\Poset & \Hom_{\DP}(A\otimes_{\Ob}B,C\otimes_{\Ob}D), \\
  \langle \adp_1, \adp_2 \rangle &\mapsto&   \adp_1 \otimes_{\Hom}  \adp_2,
\end{eqnarray}
defined by
\begin{eqnarray}
 \adp_1 \otimes_{\Hom}  \adp_2 \colon (A\times B)\op \times (C\times D) & \rightarrow_\Poset & \Bool \\
  \langle \langle\overline{a},\overline{b}\rangle,
          \langle c, d \rangle
  \rangle
  & \mapsto & \adp_1(\overline{a}, c) \wedge  \adp_2(\overline{b}, d).
\end{eqnarray}

We call $\pair{g_1}{g_2}$ the parallelization of $g_1$ and $g_2$.

\item The isomorphisms
\begin{eqnarray}
\sigma_{A,B,C} \colon &(A \otimes_{\Ob} B ) \otimes C
  &\stackrel{\simeq}{\rightarrow}
  A \otimes_{\Ob} (B \otimes_{\Ob} C) \\
  \lambda_{A} \colon & I \otimes_{\Ob} A
      &\stackrel{\simeq}{\rightarrow}
      A, \\
  \rho_{A} \colon & I \otimes_{\Ob} A
      &\stackrel{\simeq}{\rightarrow}
      A,
\end{eqnarray}
are the same as the isomorphisms for the monoidal structure that the Cartesian product induces in~$\Poset$.
\end{itemize}

\end{definition}

\begin{lemma}The maps above satisfy all properties that make
it a monoidal structure.
\end{lemma}
\begin{proof}
\todo{copy / adapt the proof given by Josh below.}
\end{proof}


\begin{remark}The monoidal product above is \emph{not} a Cartesian product.
The counterexample is that if we take the product of $\False_{A,C}$
and DP $\adp: B \rightarrow_\DP D$, we have
  \[
    \False_{A,C} \otimes \adp = \False_{A\otimes B,C\otimes D}.
  \]
Therefore, this cannot be a Cartesian product. Later, we will see
what conditions we can put on the design problem to make the monoidal
product into a Cartesian product. \todo{Is this equivalent
to characterizing the ``Cartesian center'' of $\DP$?}
\end{remark}

\begin{lemma}
    $\DP$ is a \emph{symmetric} monoidal category, with the symmetry being the one
    inherited from $\Poset$:
\begin{eqnarray}
    b_{A,B} : A \otimes B & \rightarrow B \otimes A   \label{eq:symmetry}\\
    \langle a, b \rangle & \mapsto \langle b, a \rangle.
\end{eqnarray}
\end{lemma}
\begin{proof}
    \todo{Not sure if the snippet in red refers to this part.}
    \unsure{
    The braiding inherited from $\Poset$ is a natural isomorphism $b_{A,B} : A \times B \to B \times A$ defined by $[b_{A,B}]((a,b),(b',a')) = (a \posleq a') \wedge (b \posleq b')$. Since this is equivalent to the identity morphism, the coherence conditions are trivial, making the category a symmetric monoidal category over $\times$.
    }
\end{proof}


\begin{lemma}[Trace] $\DP$ is a \emph{traced symmetric monoidal category}
    when equipped with the trace \[\Tr : \Hom_\DP(A\times C, B \times C) \to \Hom_\DP(A,B)\] defined as follows.
    Suppose that we have
    \[
    \adp : A \otimes C \rightarrow_\DP B \otimes C.
    \]
    Then we can define
    \[
    \Tr_{A,B}^C(\adp) : A \rightarrow_\DP B
    \]
    as follows:
    \begin{align}
    
        [\Tr_{A,B}^C(\adp)] : A\op\times B &\rightarrow \Bool, \label{eq:trace1} \\
        \langle \overline{a}, b \rangle &\mapsto \bigvee_{c\in C}
            [\adp](
                \langle \overline {a}, c\op \rangle,
                \langle b, c  \rangle
            ). \label{eq:trace2}
    \end{align}
\end{lemma}

\todo{Get rid of trace proof, prove that DP is compact and derive the trace from that.}

[COMPACTNESS GOES HERE.]






































For two posets $A$, $B$, the coproduct in $\Poset$ is indicated as $A \sqcup B$.

\begin{lemma}
    The category~$\DP$ admits a coproduct~$\langle\sqcup, i_X, \pair{-}{-} \rangle$,
    defined as follows:

    \begin{itemize}
        \item  The coproduct
    of objects is simply the coproduct of posets~$\sqcup$, defined as above.

    \item The inclusions $A \To{i_A} A \sqcup B \From{i_B} B$ are defined by
    \begin{align}
        i_A: A\op \times (A \sqcup B) & \rightarrow_\Poset \Bool, \\
        \langle \overline{a}, x \rangle & \mapsto
        \begin{cases}
        \overline{a}\op \posleq_A x, & \mbox{if } x \in A, \\
        \False, & \mbox{if } x \in B.
    \end{cases}\label{eq:inclusion}
    \end{align}

    \item
    Given two morphisms $\adp_1 : A \slashedrightarrow X$ and $\adp_2 : B \slashedrightarrow X$,
    we define the morphism
    \[
     \pair{\adp_1}{\adp_2}^\ast : A \sqcup B \slashedrightarrow X
    \]
    as
    \begin{align}
        \pair{\adp_1}{\adp_2}^\ast:
        (A\sqcup B)\op \times X & \rightarrow_\Poset \Bool,  \label{eq:pairing}\\
        \langle \overline{y}, x \rangle & \mapsto
        \begin{cases}
        \adp_1(\overline{y}, x) & \mbox{if } \overline{y} \in A\op, \\
        \adp_2(\overline{y}, x) & \mbox{if } \overline{y} \in B\op.
        \end{cases}
    \end{align}
\end{itemize}

\end{lemma}
\begin{proof}
For this to be a coproduct, we need to show that
the diagram below commutes, and the map $\pair{-}{-}^\ast$ is uniquely
defined.

\[
\xymatrix@R+2em@C+2em{
X \ar@{<-}[r]^{\adp_1} \ar@{<-}[d]_{\adp_2} \ar@{<--}[dr]^(0.4){\pair{\adp_1}{\adp_2}^\ast} & A \\
B & A \sqcup B \ar@{<-}[u]_{i_A} \ar@{<-}[l]^{i_B} \\
}
\]

To show commutativity, we need to show that
\[ \pair{\adp_1}{\adp_2}^\ast \circ i_A = \adp_1.\]

The map
\[
    \pair{\adp_1}{\adp_2}^\ast : A \op \times X \rightarrow_\Poset \Bool
\]
can be evaluated as follows:
\begin{align}
\pair{\adp_1}{\adp_2}^\ast \circ i_A (\overline{a},x)
&= \bigvee_{c \in A\sqcup B} [i_A](\overline{a}, c) \wedge [\pair{\adp_1}{\adp_2}^\ast](c\op,x) \\
& \{\text{Using the fact that $\overline{a}\in A\op$ and \eqref{eq:inclusion}.}\}\\

&= \bigvee_{c \in A\sqcup B} (a\op \posleq_A c)
\wedge [\pair{\adp_1}{\adp_2}^\ast](c\op,x) \\
& \{\text{Using \eqref{eq:pairing}.}\}\\
 
&= \bigvee_{c \in A\sqcup B} (a\op \posleq_A c) \wedge
\begin{cases}
[\adp_1](c\op, x) & \mbox{if } c\op \in A\op, \\
[\adp_2](c\op, x) & \mbox{if } c\op \in B\op.
\end{cases}\\
& \{\text{$a\op \posleq_A c$ implies that $c\in A$, so we take only
the first clause,}\\
& \text{and we need to ``or'' only on $A$.}\}\\
&= \bigvee_{c \in A} (a\op \posleq_A c) \wedge [\adp_1](c\op, x) \\
& \{\text{We recognize this as $\adp_1$ composed with identity.}\}\\
&= \text{id}_A \circ \adp_1(\overline{a},x)\\
&= \adp_1(\overline{a},x)
\end{align}

We prove uniqueness by contradiction.
Suppose there was another morphism $k : A \sqcup B \slashedrightarrow X$ such that $k \circ i_A = \adp_1$, and that $k \neq \pair{\adp_1}{\adp_2}^\ast$. Then the
two maps $k$ and $\pair{\adp_1}{\adp_2}^\ast$ are different on
at least an element $\overline{c} \in (A \sqcup B) \op$:
\[
    k(\overline{c},x) \neq [\pair{\adp_1}{\adp_2}^\ast](\overline{c},x).
\]
Expanding this we obtain
\[
    k(\overline{c},x) \neq
\begin{cases}
[\adp_1](\overline{c}, x) & \mbox{if } \overline{c} \in A\op, \\
[\adp_2](\overline{c}, x) & \mbox{if } \overline{c} \in B\op.
\end{cases}
\]

Without loss of generality, assume $\overline{c} \in A\op$. Then we obtain

\[
    [k](\overline{c},x) \neq [\adp_1](\overline{c}, x).
\]

On the other hand, we can evaluate $\adp_1 = k \circ i_A $ as follows:
\begin{align}
    \adp_1(\overline{c}, x) &=
    k \circ i_A (\overline{c}, x)\\ &= \bigvee_{y \in A \sqcup B}
    i_A(\overline{c}, y) \wedge
    k(y\op, x)    \\
    & \{ \text{Because $\overline{c}\in A$} \} \\
        &=\bigvee_{y \in A}
        (\overline{c}\op \posleq_A y) \wedge
        k(y\op, x) \\
    & = k(\overline{c}, x).
\end{align}
 Therefore, we have reached a contradiction.

\end{proof}

\begin{lemma} The coproduct $\sqcup$ defined above is also a product, and so is a biproduct.
\end{lemma}
\begin{proof}
    \todo{To be completed}
    The proof that $A \sqcup B$ is also a product in $\DP$ is exactly analogous, except we flip the direction of the arrows and replace $i_A$ with $\pi_A : A \sqcup B \to A$, given by $\pi_A(c,a) = (c \posleq a)$.
    \[
    \xymatrix@R+2em@C+2em{
    X \ar[r]^{\adp_1} \ar[d]_{\adp_2} \ar@{-->}[dr]^(0.4){\pair{\adp_1}{\adp_2}} & A \\
    B & A \sqcup B \ar[u]_{\pi_A} \ar[l]^{\pi_B} \\
    }
    \]
    The unique map $\pair{\adp_1}{\adp_2} : X \to A \sqcup B$ is defined by $[\pair{\adp_1}{\adp_2}](x,c) = [\adp_1](x,a) \vee [\adp_2](x,b) $.
\end{proof}

\textbf{End of Andrea's revisions}



































\begin{description}

\item [$\sqcup$ as Biproduct] The disjoint union of two posets $A \sqcup B$ is a biproduct in $\DP$, which is the usual coproduct in $\Poset$. Note, however, that the inclusions $A \To{i_A} A \sqcup B \From{\i_B} B$ are not simply the inclusions in $\Poset$ but decision problems, i.e. profunctors $[i_A] : A \slashedrightarrow A \sqcup B$ and $[i_B] : B \slashedrightarrow A \sqcup B$, respectively. We define $[i_A] : A \slashedrightarrow A \sqcup B$ by returning True on $(a,c)$ iff $a \posleq c$ for $c \in A \sqcup B$, and similarly for $[i_B]$. For morphisms $\adp_1 : A \to X$ and $\adp_2 : B \to X$, we have a unique map $\pair{\adp_1}{\adp_2}^\ast : A \sqcup B \to X$ given by $[\pair{\adp_1}{\adp_2}^\ast](c,x) = [\adp_1^\ast](c,x) \vee [\adp_2^\ast](c,x)$ where $[\adp_1^\ast](c,x) = [\adp_1](c,x)$ if $c \in A$ and False otherwise, and similarly for $[\adp_2^\ast]$,

\item [$\times$ as Monoidal Product] The standard Cartesian product $A \times B$ in $\Poset$ is \emph{not} a Cartesian product in $\DP$ as defined, but it is a monoidal product.

\begin{proof}
The unit object for $\times$ is the singleton, $\{\ast\}$. The isomorphisms are obvious, since $A \times \{\ast\} \simeq A$ as posets. We write the left and right unitors as $\lambda_A$ and $\rho_A$, which are defined, respectively, by $[\lambda_A](\ast,a,a') = (a \posleq a')$ and $[\rho_A](a,\ast,a') = (a \posleq a')$.





\end{proof}

\color{gray}
\item [Parallel] Suppose $\adp_1 : A \to B$ and $\adp_2 : C \to D$. Using $\times$, we can form ``parallel'' design problems, where the parallel of two design problems, $\para : \Hom_\DP(A,B) \times \Hom_\DP(C,D) \to \Hom(A \times C, B \times D)$, is defined by $\para(\adp_1, \adp_2)(a,b,c,d) = [\adp_1](a,b) \wedge [\adp_2][c,d]$. In this case, it is clear that the new map is monotone in $A \times C$ and $B \times D$.
\color{black}

\item [Split] Similar to $\para$, $\split$ is a graph-making operation $\split \colon \Hom_\DP(A,B) \to \Hom_\DP(A, B \times B)$ defined by \[\split (\adp)(a,b,b') = [\adp](a,b) \wedge [\adp](a,b').\]

A split design problem has a solution only when both edges of the split have a solution; it is monotone since the intersection of upper sets is an upper set.

\item[Conway] The Conway operator on design problems is defined as the composition $\Conw := \Tr \circ \; \split : \Hom(A \times B, A) \to \Hom(A \times B, A \times A) \to \Hom(B, A)$. More intuitively, the above composition is equivalent to the statement
\begin{align*}
\Conw(\adp)(b, a) &= \{ \exists a' \text{ such that } [\adp](a',b,a') \wedge [\adp](a',b,a) \}

\end{align*}

Using Conway, it is possible to construct a $h_\adp$ whose ``solution set'' is non-convex and disconnected. For $\ressp = \funsp = \mathbb{R}^+$ (note that $\ressp = \antichains \ressp$), consider the map $h_\adp : \mathbb{R}^+ \to \mathbb{R}^+$ given below.

{\centering \includegraphics{disconnected} \par}

Clearly, $h_\adp$ is (Scott-)continuous and monotone, but forming a loop in $\adp$ gives us a feasible set, $P$, which is disconnected. The point to make here is that the trace operator $\Tr$, applied to $[\adp] : A \to A$, generates a design problem $\Tr(\adp) : \ast \to \ast$ and \emph{not} a design problem $\adp' : A \to A$. Trivially, $\Tr(\adp)$ always induces a connected set on $\ast$. The interpretation is that pinging $\Tr(\adp)(\ast, \ast)$ just returns the fact of whether there is \emph{any} (functionality, resource) pair which is both feasible for $\adp$ and for which functionality $\leq$ resource. In $\DPI$, the trace operator returns the \emph{minimal} (functionality, resource) pair satisfying those conditions.

For $\adp$ as above, recall that the split operation is defined by \[\split (\adp)(a,a',a'') = [\adp](a,a') \wedge [\adp](a,a'').\] Composing with the trace gives us the Conway operator 
\begin{align*}
[\Conw(\adp)] := [\Tr \circ \; \text{split} (\adp)] : \One \times A &\to \Bool \\
(\ast, a'') &\mapsto \bigvee_{a' \in A} [\text{split}(\adp)](a', a', a'') \\
&\mapsto \bigvee_{a' \in A} [\adp](a',a') \wedge [\adp](a', a'')
\end{align*}

The feasible set of $[\adp](a',a')$ is just the intersection of the diagonal $(a',a') \in A \times A$ with the feasible set of $\adp$. This intersection may be disconnected, which \emph{implicitly} induces a feasible set on $A \times A$ which is also disconnected.

{\centering \includegraphics[width=200pt]{disconnected2} \par}


$\Conw(\adp)$ is still monotone, however, since it discards the functionality argument and varies only in the resource argument. Interpreted in $\DPI$, the feasible set of $\Conw(\adp)$ in the above diagram is just the portion of the rightmost dotted line above the diagonal.

\redout{One question we can now ask: given how we constructed the Conway operator, can we construct other operators that pick out disconnected subsets of $A \times A$?}



\item [Distributivity] $\times$ distributes over $\sqcup$, i.e. $A \times (B \sqcup C) \simeq_\DP (A \times B) \sqcup (A \times C)$. This is shown in $\Poset$ by composing two obvious bijections $f(a,k) = (a,k)$ and $g(a,k) = (a,k)$ for $a \in A, k \in B \sqcup C$. The proof in $\DP$ is similarly obvious and reduces to checking whether the composition of their $\DP$-companions, $[f]$ and $[g]$, correspond to the identity.


\item [Compact Closed] There is an internal hom functor $\hom(-,-) : \DP\op \times \DP \to \DP$ given by $\hom(A,B) = A\op \times B$. To check that
\[ \Hom_\DP(A \times B, C) \simeq \Hom_\DP(A, \hom(B, C)) \]
fix a $B$, and consider $- \times B$ and $\hom(B, -) = B\op \times -$ as endofunctors on $\DP$. For any $A,C \in \Ob \DP$, there exists a bijection natural in both $A$ and $C$ between design problems of the form
\[ A \slashedrightarrow B\op \times C \quad \leftrightarrow \quad A \times B \slashedrightarrow C \]
since this bijection is equivalent to one of the form
\[ A\op \times B\op \times C \to \Bool \quad \leftrightarrow \quad (A \times B)\op \times C \to \Bool. \]

In fact $\DP$ is compact, with monoidal dual given by $A^\ast = A\op = \hom(A,1)$.

Note that $\hom_\DP(A,B) \neq \Hom_\DP(A,B)$. However, we can recover the external hom by $\Hom_\DP(A,B) = \Hom_\DP(1, \hom(A,B))$. 







\item [Ordering on Hom] Even though $\hom_\DP(A,B) \neq \Hom_\DP(A,B)$, we can reconstruct a useful version of $\Hom_\DP(A,B)$ as a poset inside $\DP$:
\begin{gather*}
\Hom^\dagger(A,B) = \{ \adp \in \Hom_\DP(A,B) : \\
\adp \posleq \adp_x \text{ iff } [\adp](a,b) \posleq [\adp_x](a,b) \; \forall a \in A, b \in B \}
\end{gather*}

\begin{example}
Suppose two aerospace companies, Jeb's Spaceship Parts and Rockomax Conglomerate, are competing to provide rocket engines to NASA. We can conceptualize this as two design problems $[\text{Jeb}], [\text{Roc}] : \text{Fuel} \slashedrightarrow \text{Thrust}$, where $[\text{Jeb}] \posleq [\text{Roc}]$ if and only if $[\text{Jeb}](a,b) \posleq_\Bool [\text{Roc}](a,b)$ for all $a \in \text{Fuel}, b \in \text{Thrust}$, i.e. if and only if Rockomax has a solution whenever Jeb's Spaceship Parts has a solution.
\end{example}

\redout{What else can we do with this poset?}

An example of the kind of constraint introduced by trace: suppose we are given a design problem $\adp : A \to A$. Underlying $[\adp]$ is a monotone map from $A$ (as a poset of functionalities) to $A$ (as a poset of resources). Now we use $\adp$ to form a simple loop, $[\Tr_{\ast, \ast}^A(\adp)](\ast, \ast) = \bigvee_{a \in A}[\adp](\ast, a, \ast, a) = \bigvee_{a \in A}[\adp](a,a)$. In essence, the loop asks a question: does there exist \emph{any} $a \in A$ which satisfies the $[\adp](a,a)$?

\item [Fixed-Points] According to Proposition 6.8 in \cite{selinger} (originally a result of C\u az\u anescu and \c Stef\u anescu \cite{cazanescu}), any category with finite products and a trace also has a fixed-point operator $\fix^X : \Hom_\DP(A \times X, X) \to \Hom_\DP(A,X)$.

Since $\oplus$ is a (finite) biproduct in $\DP$, we know by \cite{selinger, cazanescu} that giving a trace is equivalent to giving a repetition operation, i.e. a family of operators
\[ \ast : \hom(A,A) \to \hom(A,A) \]
satisfying 
\begin{enumerate}
\item $f^\ast = \id + f \circ f^\ast$
\item $(f + g)^\ast = (f\ast \circ g)\ast \circ f^\ast$, where $f+g := \nabla_A \circ (f \oplus g) \circ \Delta_A$
\item $(f \circ g)^\ast f = f(g \circ f)^\ast$
\end{enumerate}

\redout{What is the intuitive meaning of the dual thing, iteration operators? Selinger mentions ``control flow'' in computer science. This is important because we will eventually want to show a version of Adamek's theorem (i.e. apply the Kleene ascent algorithm) to design problems with traces, for which we need to compute fixed points.}

\item [Collage] For any design problem $\adp : A \to B$, we can put $A$, $B$, and $\adp$ into a single resource poset by constructing the \emph{collage} of $\adp$, denoted $\Coll(\adp)$:
\begin{align*}
\Ob \Coll(\adp) &= \Ob A \sqcup B \\
\Coll(\adp)(a_1, a_2) &= A(a_1,a_2) \\
\Coll(\adp)(b_1, b_2) &= B(b_1,b_2) \\
\Coll(\adp)(a,b) &= [\adp](a,b) \\ 
\Coll(\adp)(b,a) &= \emptyset 
\end{align*}
In other words, $\Coll(\adp)$ is the disjoint union of $A$ and $B$ with some added morphisms (in this case, elements of $\Bool$) that capture the behavior of the profunctor $[\adp] : A\op \times B \to \Bool$. The composition across posets is easy to check: suppose $a_1 \posleq a_2$ in $A\op$ and $[\adp](a_2, b) =$ True, then their composition, an ``arrow'' from $a_1$ to $b$, must return True in $[\adp](a_1,b)$. But this is clear since $[\adp]$ is monotone---i.e. functorial---in both arguments.

One can restate the definition above by saying that $\Coll(\adp)$ has a certain universal property when considered in the 2-category $\text{Prof}$ of categories, profunctors, and natural transformations: given the 2-cell below,
\[
\begin{tikzcd}[column sep=50, row sep=50]
 & B \arrow{d}{\adp_B} \\
A \arrow[ur, "\adp", ""{name=U, below}]{} \arrow{r}{\adp_A} & \Coll(\adp) \arrow[Rightarrow, from=U]
\end{tikzcd}
\]
there is a unique (co)cone over $\Coll(\adp)$ to any other poset $X$ commuting with the diagram above and preserving the 2-cell. More succinctly, we say that $\Coll(\adp)$ is the \emph{lax colimit} of the profunctor $[\adp]$.

\item [Cographs and Heteromorphisms] The collage of a profunctor is also known as the cograph of a profunctor. As a special case, the \emph{cograph of a functor} $f : A \to B$ is defined to be the cograph of a ``representable profunctor'' $[f] : A\op \times B \to \Set$ where $\Coll([f])(a,b) := \Hom_B(f(a), b)$. For a given monotone map $f : A \to B$, it follows from the definition of $\DP$-companion that $[f]$ is also its representable profunctor, in the sense that $[f](a,b)=$ True if and only if $\Hom_B(f(a),b) \neq \O$.

In the case of a representable profunctor, $\Coll([f])(a,b)$ is also called \emph{the set of heteromorphisms} between $a$ and $b$, denoted $\text{Het}(a,b)$.

\end{description}


\begin{lemma}Let
\[

    f \colon (A\times C)\op \times(B\times C) \rightarrow \Bool
\]
and define
\begin{align}
    g\colon  A\op \times B &\rightarrow \Bool \\
    \langle a, b \rangle &\mapsto \bigvee_{c\in C} f( \langle a,c\rangle, \langle b,c \rangle).
\end{align}
Then if $f$ is monotone, $g$ is monotone.
\end{lemma}

\grayout{
For any design problems $f : A \to X$ and $g : B \to X$, we can construct a design problem $\langle f, g\rangle : A \oplus B \to X$ in which solutions of $f$ and solutions of $g$ are perfectly interchangeable; if I don't have a solution to $f$, I can always use a solution to $g$. ``I can find a workaround.'' But suppose I want to construct a design problem where only \emph{some} solutions of $f$ are interchangeable with some solutions of $g$? Is there a categorical construction that reflects this?}

\clearpage
\section{Equivalence with the other representation used}

For a poset $X$, let~$\uppersets X$ and~$\lowersets X$
represent upper and lower sets of~$X$.

For non-empty $X$, the intersection of~$\uppersets X$ and~$\lowersets X$ consists of exactly two elements, $X$ itself and the empty set:
\[
    \uppersets X \cap \lowersets X = \{ \emptyset, X\}
\]


We can make both $\uppersets X$ and~$\lowersets X$ be posets themselves,
with the partial order given by ``$\supseteq$'':
\begin{align}
    S_1 \preceq_{\uppersets X} S_2 &\equiv S_1 \supseteq S_2, \\
    S_1 \preceq_{\lowersets X} S_2 &\equiv S_1 \supseteq S_2.
\end{align}

We have that
\begin{align}
    \bot_{\uppersets X} = \bot_{\lowersets X} = X  \\
    \top_{\uppersets X} = \top_{\lowersets X} = \emptyset
\end{align}

An alternative representation of a design problem $\adp \colon
F \to_\DP R$ is as a pair of maps $\langle m_\adp, m_{\adp}^\ast \rangle$,
described by
\begin{align}
    m_{\adp} & \colon \uppersets F \rightarrow \uppersets R, \\
    m^\ast_{\adp} & \colon \lowersets R \rightarrow \lowersets F,
\end{align}
with the following semantics. The map $m_{\adp}$ gives
for each upper set $S \in \uppersets F$ the resources that are feasible:

\begin{align}
    m_{\adp}:
    S \mapsto \{ r \in R: \exists f \in S: [\adp](f\op, r) = \True \}.
\end{align}

Similarly, the map $m^\ast_\adp$ gives for each lower set the functionality that are feasible:

\begin{align}
    m^\ast_{\adp}:
    X \mapsto \{ f \in F: \exists r \in X: [\adp](f\op, r) = \True \}.
\end{align}

\begin{lemma}The following properties hold:
    \begin{enumerate}
        \item The maps $m_\adp$ and $m^\ast_\adp$ are monotone.
        \item The pair of maps $m_\adp$ and $m_\adp^\ast$
        uniquely determine $\adp$.
    \end{enumerate}
\end{lemma}

\begin{proof}
    \todo{TODO}
\end{proof}

\unsure{Q1: Is it sufficient to know only one of the
maps  $m_\adp$ and $m_\adp^\ast$ to uniquely identify $\adp$?}

\clearpage


\chapter{The category DPI (problems with implementation)}



\section{Intuition}

In the definition of design problem (Definition \ref{def:design problems}), we are given an implementation space $\impsp$ along with maps eval to a given functionality space and exec to a given resource space. The category $\DPI$ records design problems along with data about their implementations. 



\section{Definition}
In this case, we would like to track not merely the existence of a solution to a design problem but the particular solutions or implementations of that design problem. Recall that for any design problem $\adp$ on $\funsp, \ressp$, the implementation space of that design problem is a triple $(\impsp, \eval, \exec)$ of the form.

\[
\xymatrix@R+2em@C+2em{
& \impsp \ar[dl]_{\exec} \ar[dr]^{\eval} &  \\
\funsp & & \ressp \\
}
\]

\grayout{In general, the implementation space for a design problem may be finite, but the space of \emph{feasible} functionality-resource pairs may be infinite. This is because each implementation defines an upper set of feasible F-R pairs. However, we are not tracking such feasible pairs in this category.}

\begin{definition}\label{def:DPI}
The category of design problems with implementation, $\DPI$, is given by the following data:

\begin{description}
\item [Objects] The objects of $\DPI$ are partially-ordered sets.

\item [Morphisms] The morphisms $\adp : F \to R$ in $\DPI$ are given by monotone maps $[\adp_I] = [\adp] : \funsp\op\times\ressp \rightarrow \powerset(I)$ where the ordering on $\powerset(I)$ is given by subset inclusion.

When $I = \{\ast\}$, this returns the category $\DP$ (recall that $\powerset(I) = \Bool^I$). \emph{Interpretation: the result of $[\adp](a,b)$ is the set of ways to make $b$ sufficient for $a$.} As before, such maps between posets can also be read as profunctors between categories, and we can write them as $[\adp] : \funsp \slashedrightarrow \ressp$.

Monotonicity of $[\adp_1]$ describes a similar feasibility assumption as in $\DP$: if an implementation can provide functionality $a$ with resource $b$, then it can also provide the same functionality $a$ with a greater resource $b^+$, or it can provide a lower functionality $a^-$ with the same resource $b$.

\redout{
Note that assuming that $\impsp \subset \funsp \times \ressp$ (which I do \emph{not} in the rest of this article) means that the design problem can no longer distinguish between implementations providing the same functionality/resource pair. This may not be desirable. For example, we may want to distinguish two identical implementations (e.g. GE gadget vs. IBM widget) because identical performance is a common occurrence in engineering. Alternately, suppose that the initial setup of a design problem is not sufficiently fine to recognize the differences between a functionality/resource pair that are, in reality, different. A common example: when we add a new dimension to a design problem. That is, for some $i,j \in I$,
\[\exec_1(i) = \exec_1(j) \quad \eval_1(i) = \eval_1(j)\] for $\exec_1 : I \to \funsp_1$ and $\eval_1 : I \to \ressp_1$, but
\[\exec_2(i) \neq \exec_2(j) \quad \eval_2(i) \neq \eval_2(j)\]
for $\funsp_2 \supset \funsp_1$, $\ressp_2 \supset \ressp_1$.

We would like to say that $\adp_1$ is something like a subproblem of $\adp_2$, and to be able to distinguish solutions that use $i$ instead of $j$, even though, as far as $\adp_1$ is concerned, they are exactly the same. It is useful, then, to at least have the language to distinguish $i$ and $j$ in the source.

Also, I think that $I$, in principle, should not have a canonical ordering, and it would implicitly carry one if we defined it as a subset of $A\times B$. Though, to be fair, we can define an ordering from exec and eval.
}

\item [Composition] The composition of $\adp_2 \circ \adp_1 \colon A \to C$ is a functor $[\adp_2 \circ \adp_1] : A\op \times C \to \powerset(I_1 \times I_2)$ given by
\[ [\adp_2 \circ \adp_1] (a,c) = \bigcup_{\substack{(b,b') \in B \times B\op \\ b \posleq_B b'}} \Bigg[ [\adp_1](a,b) \times [\adp_2](b',c) \Bigg]. \]

Intuitively, this equation says that a given pair of implementations is a solution to the composed design problem $\adp_2 \circ \adp_1$ if and only if there exists a functionality-resource pair $b \posleq b'$ for which neither $[\adp](a,b)$ or $[\adp_2](b',c)$ are empty.



\item [Composition as Colimit] In fact, the formula for the composition above describes the colimit (here, a directed colimit) of a functor $F$ from the poset $\{(b,b') \in B \times B\op : b \posleq_B b' \}$ to $\powerset(I_1 \times I_2)$. 



The functor $F$: we index the poset $\powerset(I_1 \times I_2)$ according to the poset $B \times B\op$ in the following way: fix $a$ and $c$, and for any $(b,b')$ where $b \posleq_B b'$, assign to it the set
\[ [\adp_1](a,b) \times [\adp_2](b',c) \subset \powerset(I_1 \times I_2). \]
On morphisms, we then map every inequality
\[(b, b') \posleq (\beta, \beta')\] in $B \times B\op$ to the corresponding subset relation
\[[\adp_1](a,b) \times [\adp_2](b',c) \subseteq [\adp_1](a,\beta) \times [\adp_2](\beta',c)\]
in $\powerset(I_1 \times I_2)$. To check that this subset relation exists: recall that if an implementation $i$ is feasible with $(a,b)$, in the sense that $\exec(i) \geq_A a$ and $\eval(i) \posleq_B b$, then it is also feasible with $(a,\beta)$ where $b \posleq_B \beta$. Similarly, if an implementation is feasible with $(b',c)$, then it is also feasible with $(\beta',c)$ where $b' \posleq_{B\op} \beta'$.

The colimit is defined as the union of all the indexed sets $[\adp_1](a,b) \times [\adp_2](b',c)$:
\[ \colim F = \bigcup_{(b,b') \in B \times B\op} [\adp_1](a,b) \times [\adp_2](b,c).\]
To check that it satisfies universality: any other cocone $X$ over $F$ must contain all the indexed sets so the inclusion from $\colim F$ to $X$ exists, and uniqueness is trivial from the definition of poset (as a category whose hom-sets have at most one element).

\marginAC{I don't like this definition because it feels really arbitrary, especially $\exec$ and $\eval$, but only $I_{\id} = \{\ast\}$ satisfies the identity axiom, and we have to specify $\exec$ and $\eval$ for $\ast$. What's the canonical choice? In principle, I don't think it matters how we specify $\exec$ and $\eval$ for the identity, since it's not really an implementation that consumes resources to provide functionality; it's really more of a sieve or constraint.} 
\item [Identity] The identity $\id_A : A \to A$ is defined by $I_{\id} = \{\ast\}$ (so $\powerset(I_{\id}) = \Bool$), $\eval(\ast) = \bot \in A$ and $\exec(\ast) = \bot \in A$, and
\[ [\id_A] (a,a') = (a \posleq a').\]
In other words, $I_A = \ast$ for the identity, so $\powerset(I_A) = \Bool$. Clearly this map is monotone. It remains to check that the identity axiom is satisfied:
\begin{align*}
[\adp \circ \id_A] (a,b) &= \bigcup_{\substack{(a',a'') \in A \times A\op \\ a' \posleq_A a''}} \Bigg[ [\id_A](a,a') \times [\adp](a'',b) \Bigg] \\
&= \bigcup_{a' \posleq a''} (a \posleq a') \times [\adp](a'',b) \\
&= \bigcup_{\substack{a \posleq a' \\ a' \posleq a''}} [\adp](a'',b) \\
&= [\adp](a,b)
\end{align*}




















\item [Associativity] Obvious, since the union and Cartesian product are associative.

\item [Companions, Conjoints] For every monotone mapping of posets $f : A \to_\Poset B$, we define the companion and conjoint of $f$ in $\DPI$, $[f]$ and $[f\op]$, to be exactly the companion and conjoint as we defined them for $\DP$:
\[[f](a,b) := (f(a) \posleq b)\]
\[[f\op](a,b) := (a \posleq f(b))\]
In other words, the companion and conjoint always take the case where $I = \{\ast\}$ and $\powerset(I)=\Bool$. We set $\exec(\ast) = \top$ and $\eval(\ast) = \bot$.

\item [Initial and Terminal Object] Like $\DP$, the initial and terminal object in $\DPI$ is the empty set $\O$. 

\item [$\sqcup$ as Biproduct] We need to show that any decision problem $\adp_A : A \to X$ and $\adp_B : B \to X$ factors through decision problems $i_A : A \to A$ and $i_B : B \to A \sqcup B$. In other words, the diagram below:

\[
\xymatrix@R+2em@C+2em{
X \ar@{<-}[r]^{\adp_1} \ar@{<-}[d]_{\adp_2} \ar@{<--}[dr]^(0.4){\pair{\adp_1}{\adp_2}^\ast} & A \\
B & A \sqcup B \ar@{<-}[u]_{i_A} \ar@{<-}[l]^{i_B} \\
}
\]

Let $[\iota_A] : A \slashedrightarrow A \sqcup B$ and $[\iota_B] : B \slashedrightarrow A \sqcup B$ be the companions of the poset inclusions. Let $[\langle \adp_1, \adp_2 \rangle](c,x) = [\adp_1^\ast](c,x) \sqcup [\adp_2^\ast](c,x)$ (note that this disjoint union lives in $\powerset(I)$, so we are not being circular) where $[\adp_1^\ast](c,x) = [\adp_1](c,x)$ if $c\in A$ and $\O$ otherwise, and similarly for $[\adp_2^\ast]$. The proof then goes exactly as in $\DP$.
\marginAC{wait, what's forcing $c,c' \in A$? Oh, it's because $[\iota_A](a,c) = \O$ if $c \notin A$.}
\begin{align*}
[\langle \adp_1, \adp_2 \rangle \circ \iota_A](a,x) &= \bigcup_{c\posleq c' \in A \sqcup B} [\iota_A](a,c) \times [\langle \adp_1, \adp_2\rangle](c',x) \\
&= \bigcup_{c \posleq c' \in A \sqcup B} (a \posleq c) \times \bigg( [\adp_1^\ast](c',x) \sqcup [\adp_2^\ast](c',x) \bigg) \\
&= \bigcup_{c \posleq c' \in A\sqcup B} (a \posleq c) \times [\adp_1^\ast](c',x) \\
&= [\adp_1] (a,x)
\end{align*}

\item [$\times$ as Monoidal Product] The Cartesian product $A \times B$ in $\Poset$ extends to a monoidal product in $\DPI$, with unit object the singleton, $\{\ast\}$. The proof follows very similarly as with $\DP$.

\begin{proof}
The unit object for $\times$ is the singleton, $\{\ast\}$. The left and right unitors are defined by $[\lambda_A](\ast, a, a') = (a \posleq a')$ (so, as with the identity, $I_{\lambda_A} = \{\ast\}$) and $[\rho_A](a,\ast,a') = (a \posleq a')$.

Similarly, the associator $\alpha : (A \times B) \times C \to A \times (B \times C)$ is defined by \[ [\alpha](((a,b), c), (a', (b',c'))) = [\id_A](a,a') \cup [\id_B](b,b') \cup [\id_C](c,c'). \] Since these are all equivalent to the identity, $\DPI$ is strict monoidal for $\times$.
\end{proof}

\redout{But we're still missing the semantics for parallel! That requires a Cartesian product in $\DPI$ (which requires attaching a top element).}

\item [Distributivity] Obvious, since $\times$ distributes over $\sqcup$ in $\Poset$.

\item [Split]

\item [Symmetry] The symmetry $b_{A,B} : A \times B \to B \times A$ is the same as in $\DP$:
\[ [b_{A,B}](a,b,b',a') = (a \posleq a') \wedge (b \posleq b'). \]

\item [Compact Closed] As in $\DP$, there is an internal hom functor $\hom(-,-) : \DPI\op \times \DPI \to \DPI$ given by $\hom(A,B) = A\op \times B$, along with monoidal dual $A^\ast = A\op = \hom(A,1)$. The proof for $\DPI$ is exactly analogous to that for $\DP$, excepting that we note the natural bijection in $A$ and $C$ between design problems of the form
\[ A \slashedrightarrow B\op \times C \quad \leftrightarrow \quad A \times B \slashedrightarrow C \]
are equivalent in $\DPI$ to a bijection of the form
\[ A\op \times B\op \times C \to \powerset(I) \quad \leftrightarrow \quad (A \times B)\op \times C \to \powerset(I) \]
for arbitrary $I$.

\item [Trace] The trace is a loop-making operation $\Tr : \Hom(A\times C, B \times C) \to \Hom(A,B)$. Since $\DPI$ is compact closed (in fact, it should be a subcategory of the category $\text{Prof}$ of profunctors and so should inherit the trace), it has a canonical trace given by the composition \[\Tr_{A,B}^C : 1 \overset{\eta}{\to} C\op \times A \overset{1_{C\op} \times \adp}{\to} C\op \times B \overset{\epsilon}{\to} 1\]
where $\eta = \hom_{\DP\op}$ and $\epsilon = \hom_\DP$ are the unit and co-unit, respectively. The formula is: 
\[\Tr_{A,B}^C(\adp) (a,b) = \bigcup_{c \in C} [\adp](a,c,b,c)\] for \[\adp : (A\op \times C\op) \times (B \times C) \to \mathcal{P}(I).\] 


The trace properties are a straightforward extension from $\DP$, with $\cup$ replacing $\vee$ in those cases where necessary.
    \begin{description}
    \item [Vanishing] $[\Tr_{A,B}^1(\adp)] = \bigcup_{\ast \in 1} [\adp](a,\ast,b,\ast) = [\adp](a,b)$ for all $[\adp] \colon A \slashedrightarrow B$, and
    \begin{align*}
    [\Tr_{A,B}^{X \times Y} (\adp)] (a,b) &= \bigcup_{(x,y) \posleq (x',y') \in X\times Y} [\adp](a, (x,y), b, (x',y')) \\
    &= \bigcup_{x \posleq x' \in X, y \posleq y' \in Y} [\adp](a,x,y,b,x',y') \\
    &= \bigcup_{y \posleq y' \in Y} \left (\bigcup_{x \posleq x' \in X} [\adp](a,x,y,b,x',y') \right ) \\
    &= [\Tr_{A,B}^{X} (\Tr_{A \times X,B \times X}^Y(\adp))](a,b)
    \end{align*}
    for all $\adp \colon A \times X \to B \times X$.

    \item [Superposing] For all $\adp : A \times X \to B \times X$, we have
    \begin{align*}
    [\Tr_{C \times A, C \times B}^X(\id_C \times \; \adp)](c,a,c',b) &= \bigcup_{x \in X} (c \posleq c') \times [\adp](a, x, b, x) \\
    &= (c \posleq c') \times \bigcup_{x \in X} [\adp](a,x,b,x) \\
    &= [\id_C \times \Tr_{A,B}^X(\adp)] (c, c', a,b).
    \end{align*}

    \item [Yanking] Let $[b_{X,X}] : X \times X \slashedrightarrow X \times X$ be the symmetry. Then
    \begin{align*}
    [\Tr_{X,X}^X (b_{X,X})](x_1, x_2) &= \bigvee_{x \in X} [b_{X,X}](x_1, x, x_2, x) \\
    &= \bigvee_{x \in X} (x_1 \posleq x) \wedge (x \posleq x_2) \\
    &= (x_1 \posleq x_2) \\
    &= [\id_X](x_1,x_2).
    \end{align*}
    The second equality comes directly from the formula for the symmetry.
    \end{description}

Suppose we are given an ``original'' design problem $\adp : A \to A$. Underlying $[\adp]$ is a monotone map from $A$ (as a poset of functionalities) to $A$ (as a poset of resources). Now we use $\adp$ to form a simple loop, $[\Tr_{\ast, \ast}^A(\adp)](\ast, \ast) = \bigcup_{a \in A}[\adp](\ast, a, \ast, a) = \bigcup_{a \in A}[\adp](a,a)$. In essence, the loop asks a question: what are \emph{all} the $a \in A$ which satisfies $[\adp](a,a) =$ True?


\item [Collage]

\item [Grothendieck Construction] The \emph{Grothendieck construction} on a design problem $[\adp] : A\op \times B \to \Set$ is a category $\int \adp$ with objects $(a,b,i)$ where $i \in \adp(a,b)$ and morphisms $(f,\phi) : (a,b,i) \mapsto (a',b', i')$ satisfying the following:

\[
\xymatrix@R-1em@C-1em{
 & \ast \ar[rdd]^{i'} \ar[ldd]_i &  \\
 & \searrow^\phi & \\
\adp(a,b) \ar[rr]_{\adp(f)} & & \adp(a',b') \\
\\
(a,b) \ar[rr]^{f} & & (a',b')
}
\]

Note that $f: A \times B \to A\times B$ above is just a monotone map, \emph{not} a design problem.

(Note: changed Searrow in $\searrow$)

\redout{(What is this construction for????)}

\end{description}
\end{definition}

\chapter{$\DPI$ + Scott-continuous}
In this section, we describe a variant of $\DPI$: the Scott-continuous category of design problems, $\DPI_S$. The objects of $\DPI_S$ are directed complete partially-ordered sets (DCPOs), i.e. posets where every subset has a well-defined supremum, with a bottom element $\bot$.

The CTC story for computation and convergence comes from: Adamek's theorem, see \url{https://ncatlab.org/nlab/show/initial+algebra+of+an+endofunctor}. The idea is that in the category with initial object (in this case, a poset with a bottom and unique map ???), and transfinite composition (i.e. the poset relation, which can be composed arbitrarily), and all sequential colimits (so we can form disjoint unions of subsets of a given poset over an ordinal). Then given a functor $F : C \to C$ that preserves such sequential colimits (for us, this is the fixed point operation in Kleene ascent?), the colimit of the chain
\[ \bot \overset{i}{\to} F(0) \to ... \to F^{(n)}(0) \to F^{(n+1)}(0) \to ... \]
has the structure of an initial $F$-algebra. What this means is that...









\chapter{Theorems Revisited}
The proofs of several theorems in \cite{codesign16} are trivial, now that we have shown the properties of $\DP$ and $\DPI$.

\begin{lemma}Relates the powerset of antichains of a resource poset $P$ to the powerset of upper sets of $P$.\end{lemma}

\begin{theorem}[Banach's Fixed Point Theorem, the CT version]If $P$ is a directed set with a least element.\end{theorem}

\begin{lemma}[CPO Fixed Point Theorem] If $P$ is a directed set with a least element and $f : P \to P$ is monotone, then $f$ has a least fixed point. I.e. there is an equalizer of $f$ and the identity.\end{lemma}

\begin{theorem}[Kleene's Fixed Point Theorem] If $P$ is as above, $f$ is Scott-continuous (i.e. monotone + carries over supremums) then $f$ has a least fixed point, which is the supremum of the sequence $\perp \posleq f(\perp) \posleq f(f(\perp)) \posleq ...$\end{theorem}

\begin{theorem}The composition (``series''), coproduct (``parallel''), and trace ``loop'' of a design problem are design problems.\end{theorem}

\begin{theorem}Suppose we have a design problem whose atoms are monotone. Then $h_\adp$ has an ``explicit expression'' in term of the functions $\{ h_\adp | \adp \in \text{atoms}(\adp) \}$. Recall that $h_\adp$ is a map from functionalities to \emph{antichains} of the resources. In this case, the antichains represent the solutions, so it seems we are really talking about $\DPI$ here.\end{theorem}

\begin{proposition}[Proposition 4 in \cite{codesign16}]This an explicit representation of the algorithm that iterates through a sequence of antichains in $P$, essentially following the Kleene ascent algorithm, and halts at a fixed point. The next few lemmas are used to prove this proposition.\end{proposition}

\begin{proposition}[Proposition 5 in \cite{codesign16}]Description of the computational complexity in terms of the width of $\ressp$, the height of the antichains of $\ressp$, and $c$ (which = width$(\ressp)$??).\end{proposition}

\begin{proposition}The ``trick'': ``to compute the set of minimal resources, it is not necessary to compute the set of all feasible resources.'' And ``while the feasible set is non-convex, the `objective function' is, essentially, the identity function.''\end{proposition}

\begin{proposition}Nested loops can be converted into one loop.\end{proposition}

\chapter{Future directions}
Approximations and ``gradients'' of solutions.






\clearpage
\chapter{Related work}

\emph{Now that we defined everything, we can say exactly how this related 
to previous work.}


\grayout{

Still to define:

\begin{itemize}
\item resource category
\end{itemize}

}

\clearpage
\chapter{Notes / scratch}

\section{Moved from ccd04DP.tex, to be developed in later paper}
\begin{description}
\item [Companions, Conjoints] Every monotone mapping of posets $f : A \to_\Poset B$ induces a canonical design problem $[f] : A \slashedrightarrow B$ called its  \emph{companion}. This map is defined by the rule
\[[f](a,b) := (f(a) \posleq b). \]
The identity, inclusion, and projection maps are special examples of such $\DP$-companions:
\[ \id_\DP(a,a') = (\id_\Poset(a) \posleq a') \]
\[ \iota_\DP(a,b) = (\iota_\Poset(a) \posleq b) \]
\[ \pi_\DP(b,a) = (\pi_\Poset(b) \posleq a) \]
A related construction, called the \emph{conjoint} of $f$, is defined by the rule \[[f\op](a,b) := (a \posleq f(b)).\]

\item [Cartesian $\otimes$] $\otimes$ is not Cartesian unless we assume that every poset $A$ has a top element $\top$ (and that all maps preserve this $\top$ element), where $\top$ is a resource which can provide any functionality. To see why, note that the intended semantics of a map $\pair{\adp_A}{\adp_B} : X \to A \times B$ is
\[[\pair{\adp_A}{\adp_B}](x,a,b) = [\adp_1](x,a) \wedge [\adp_2](x,b).\]
In other words, $\times$ should model the combination of two design problems ``in parallel''. In order for $\times$ to be Cartesian, this map must make the following diagram commute:
\[
\xymatrix@R+2em@C+2em{
X \ar[r]^{\adp_1} \ar[d]_{\adp_2} \ar@{-->}[dr]^(0.4){\pair{\adp_1}{\adp_2}} & A \\
B & A \times B \ar[u]_{\pi_A} \ar[l]^{\pi_B} \\
}
\]
and to demonstrate the top half of the diagram, we would have to prove something like
\begin{align*}
& [p_A \circ \pair{\adp_1}{\adp_2}] (x,a'') \\
&= \bigvee_{\substack{(a,b), (a',b') \in A \times B \\ (a,b) \posleq (a',b')}} [\pair{\adp_1}{\adp_2}](x,(a,b)) \wedge [p_A]((a',b'),a'') \\
&= \bigvee_{\substack{a,a' \in A, b \in B \\ a\posleq a'}} [\adp_1](x,a) \wedge [\adp_2](x,b) \wedge (a' \posleq a'') \\
&= \bigvee_{\substack{a,a' \in A \\ a \posleq a'}} [\adp_1] (x,a) \wedge (a' \posleq a'') \\
&= [\adp_1](x,a''),
\end{align*}
\marginAC{What happens if we define a bottom element $\bot$; is there a variation of this diagram which requires a bottom element in order to commute?}
But note that the third equality above requires that $[\adp_2](x,b)$ be True unconditionally, for an arbitrary $x$ and arbitrary $B$. That is, every resource poset $B$ must contain a top element $\top \in B$ such that every design problem maps $(-,b)$ to True, i.e. $\top$ is a resource that can provide any functionality. \grayout{In practical computations it is often useful to keep track of a such a solution, e.g. $\top = \infty$, and we will do so in later iterations of $\DP$.}
\end{description}

\section{Relation with convex optimization}

Problem 4. (Table this. Put in background? Or future work?) what is the relationship between MCDPs and convex optimization problems? Most people come at MCDP through lens of convex optimization.

\begin{enumerate}
\item TO DO: look up papers on categorification of convex optimization. Josh: I found nothing on Google. Andrea: me neither, waiting from word from optimization guys.
\item convex optimization can also be composed (think layers of RBMs), but the number of examples explodes as you add layers. MCDPs behave much better under composition. They're still solvable, and that's surprising!
\end{enumerate}




\section{Design problems as dynamical systems}
Problem 2. articulate the relationship (functorial?) between 6 different representations or algebras over the codesign operad:  as design/optimization problems, as diagrams, in terms of antichains, as dynamical systems that compute the solution, and on the type side (as implemented in Andrea's algorithm).

Mapping $\DP$ to the dynamical systems representation, then mapping from the dynamical systems representation to the algorithmic side could be a good idea.

Problem 3. compare, write down functors from $\DP$ (the solution exists) to $\DPI$ (give me the actual implementation) and vice versa.

\begin{enumerate}
\item the objects of $\DPI$ are posets, same as $\DP$, but 
\[
    \Hom_\DPI = \{(I,f) \colon  I \text{ is a set}, f\colon  A\op \times I \times B \to \Cat{Bool} \}
\]
\item $\DPI$ is possibly enriched in $\Cat{Cat}$; ``catalog lemma'' on preserving monotonicity between implementations $I \to J$.
\end{enumerate}

Problem 4. How is the (d)cpo structure, which is required for practical computation, related to the original use in domain theory of the dcpo as a general model for computability? TODO:  this is not the biggest priority right now, but perhaps we should go talk to a domain theorist?

Problem 5. (think about it while proving closure properties for S-C versions of DPI) write down the structure for "derivative of a diagram", e.g. the monoidal closure.

Problem 6. Does $f$ Scott-continuous in the $\DP$ category imply that the corresponding abstract design problem $h_\DP$ is Scott-continuous in the dynamical system representation?

\end{document}