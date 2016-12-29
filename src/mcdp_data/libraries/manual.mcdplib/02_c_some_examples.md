# Introduction to the theory

## Design Problems (DPs)

Define a \emph{design problem} as a relation between \emph{\F{provided functionality}}
and \emph{\R{required resources}}~(\figref{dp}). \F{Functionality}
and \R{resources} are partially ordered sets, indicated by by $⟨ℱ,\funleq⟩$
and $⟨ℛ,\resleq⟩$.

\begin{figure}
\includegraphics[scale=0.33]{reits2_dp}\caption{\label{fig:dp}}
\end{figure}

\begin{example}
(Battery) The first-order characterization of a battery is as a store
of energy, in which the \F{capacity &#91;kWh&#93;} is the \F{functionality}
and the \R{mass &#91;kg&#93;} is a \R{resource}~(\figref{battery1}).
The \F{capacity} is a functionality because it is what a battery
\emph{provides} to the system.
\end{example}

\begin{figure}
\includegraphics[scale=0.33]{reits2_battery1}\caption{\label{fig:battery1}}
\end{figure}

The \R{mass} is a resource: it is what the battery \emph{requires}
to provide the functionality. The functionality space is $ℱ=\Rcpu{J},≤⟩$.
The superscript $\text{J}$ indicates that the values have the dimensionality
of Joules. The resource space is $ℛ=⟨\Rcpu{g},≤⟩.$

As in all modeling efforts, the level of detail depends on the application.
Other models for a battery would take into account other resources.
For example, one might want to consider the \R{cost} of the battery
in addition to the mass~(\figref{battery2}). Other properties
of interest for a battery-like device include the \F{maximum output current},
\F{maximum power draw}, and which \F{voltage} it provides~(\figref{battery3}).

\begin{figure}
\subfloat[\label{fig:battery2}]{\includegraphics[scale=0.33]{reits2_battery2}}
\subfloat[\label{fig:battery3}]{\includegraphics[scale=0.33]{reits2_battery3}}
\caption{}
\end{figure}

\subsubsection{Formal definition of a DP }

A DP is described by the answer to the question

\begin{quote}
(&#42;) "Given a certain \F{functionality} $\fun∈ℱ$ to be
implemented, what are \R{the \textbf{minimal} resources}, a subset
of $ℛ$, necessary to implement $\fun$?".
\end{quote}

This choice imposes the direction \F{functionality}$⇒$\R{resources},
but the theory is entirely symmetric, and one could choose to consider
the \emph{dual} question: "Given certain available resources $\res∈ℛ$,
what are \F{the\textbf{ maximal} functionalities}, a subset of $ℱ$,
that can be implemented?".

In general, fixed a functionality $\fun∈ℱ$, there will be
multiple resources that are sufficient to perform the functionality
that are incomparable. For example, in the case of a battery one might
consider different battery technologies that are incomparable in the
mass/cost resource space.~(\figref{multiple}).

\begin{figure}
\includegraphics[scale=0.33]{reits2_battery2_h}\caption{\label{fig:multiple}}
\end{figure}


A subset with "minimal", "incomparable" elements is called
"antichain".

\begin{definition}
An antichain $S$ in a poset $⟨\posA,≼⟩ $
is a subset of $\posA$ such that no element of $S$ dominates another
element: if $x,y∈S$ and $x≤ y$, then $x=y$.
\end{definition}

\begin{lemma}
Let $\antichains\posA$ be the set of antichains of $\posA$. $\antichains\posA$
is a poset itself, with the partial order given by
\begin{equation}
S₁≼_{\antichains\posA}S₂␣≡␣\uparrow S₁⊃eq\,\uparrow S₂.\label{eq:orderantichains}
\end{equation}
\end{lemma}


\begin{figure}
\includegraphics[scale=0.33]{reits2_dp_h_one}\caption{}
\end{figure}

Answering the question (&#42;) above is equivalent to defining a map
\[
\ftor:ℱ⇒\Aressp
\]
that associates to each functionality $\fun$ an antichain of resources $\ftor(\fun)⊂ℛ$,
with the semantics that those are the \emph{minimal} resources needed
to provide the functionality $\fun$. The set $\ftor(\fun)$ need
not be finite or discrete; it can be either.
\end{minipage}


A further condition is imposed on $\ftor.$ We require that the map $\ftor$
is monotone, in the sense that
\[
(\fun₂≽_{ℱ}{\fun₁})⇒(\ftor(\fun₂)≽_{\Aressp}\ftor(\fun₁))
\]
\begin{figure}
\includegraphics[scale=0.33]{reits2_dp_h_two}\caption{\label{fig:up}}
\end{figure}

This means that if $\fun₂≽_{ℱ}{\fun₁}$, the curve $\ftor(\fun₂)$
is higher than $\ftor(\fun₁)$ (\figref{up}, right), as
implied by the order on the antichains given by~\eqref{orderantichains}.
\end{minipage}


We are now ready to give a formal definition of a design problem.
\begin{definition}
\label{def:A-monotone-design}A\emph{ design problem~}(DP) is a tuple $⟨ℱ,ℛ,\ftor⟩ $
such that $ℱ$ and $ℛ$ are posets, and ${\colH\ftor}:{\colF\fun}⇒{\colR\antichainsℛ}$
is a monotone function.
\end{definition}

\begin{figure}
\includegraphics[scale=0.33]{reits2_dp_h}\caption{}
\end{figure}



\begin{example}
(battery, continued) To specify a DP, one needs to specify the poset $ℱ$,
the poset $ℛ$, and the function $\ftor:ℱ⇒\Aressp$
in~\prettyref{def:A-monotone-design}. It was already established
that $ℱ=\colF⟨ℝ₊^{J},≤⟩$ and $ℛ={\colR⟨ℝ₊^{g},≤⟩}$.
The relation between \R{battery mass} $\batterymass$ and \F{capacity} $\batterycapacity$
is given by the specific energy $ρ$, with the simple linear constraint
\begin{equation}
ρ\,\batterymass≥\batterycapacity.\label{eq:battery_se}
\end{equation}
The formal definition of the map $\ftor$ is
\begin{align}
\ftor:{\colF⟨ℝ₊^{J},≤⟩} & ⇒{\colR\antichains⟨ℝ₊^{g},≤⟩},\nonumber \\
\batterycapacity & ⟼\{\batterycapacity/ρ\}.\label{eq:ftor_battery_continuous}
\end{align}
The map $\ftor$ associates to each value of the \F{capacity} $\batterycapacity$
a set $\{\batterycapacity/ρ\}$ describing the minimal \R{mass}
sufficient to provide the given \F{capacity}.

The relation~\eqref{eq:battery_se} implicitly assumes that we can
choose one of an infinite amount of batteries of any arbitrary mass~
(\figref{All-batteries-that}). This framework can easily accommodate
that case of only a discrete set of available battery models.

\begin{figure}
\includegraphics[scale=0.33]{reits2_battery_h_1}\caption{\label{fig:All-batteries-that}}
\end{figure}
\end{example}


\begin{figure}
\includegraphics[scale=0.33]{reits2_battery_h_2}\caption{\label{fig:Finite-number-of-1}}
\end{figure}

\begin{example}
(Discrete increments) Suppose that the batteries are available in
increments of $\Delta_{m}$ &#91;g&#93;, so that we can only have \R{mass} $\batterymass∈\{{\colF k}\Delta_{m},␣{\colF k}∈\mathbb{N}\}.$
The map in~\eqref{eq:ftor_battery_continuous} can be amended as
follows:
\begin{align}
    \ftor:{\colF⟨ℝ₊^{J},≤⟩} & ⇒{\colR\antichains⟨ℝ₊^{g},≤⟩},\nonumber \\
    \batterycapacity & ⟼\{\batterymass^{★}\},\label{eq:ftor_battery_continuous-1-1}\\
     & \batterymass^{★}=\begin{cases}
    \min_{k} & k\Delta_{m}\\
    \subto & ρ k\Delta_{m}≥\batterycapacity.
    \end{cases}
\end{align}
In other words, the best mass $\batterymass^{★}$ is the minimum
mass that satisfies the capacity constraint, searching over all the
implementation possibilities, here described by the index $k$. The
graph of the function $\ftor$ has a shape similar to the one pictured
in~\figref{Finite-number-of-1}. Note that the graph is discontinuous;
in this framework, there is no continuity constraint on $\ftor$.
\end{example}

\begin{figure}
\includegraphics[scale=0.33]{reits2_battery2_h}
\caption{\label{fig:pipe}}
\end{figure}

\begin{example}
(Different batteries technologies) Consider choosing between $n$
competing battery technologies, characterized by the specific energy $ρᵢ$
&#91;kWh/g&#93; and specific cost $αᵢ$ &#91;&#96;/kWh&#93;. The resource
space is $ℛ=\colR⟨ℝ₊^{g},≤⟩×⟨ℝ₊^{\$},≤⟩.$
The cost $\batterycost$ is related to the capacity linearly through
the specific cost $αᵢ$: $\batterycost≥αᵢ\,\batterycapacity.$
The map $\ftor$ is
\begin{align}
    \ftor:{\colF⟨\Rcpu{J},≤⟩} & ⇒{\colR\antichains⟨\Rcpu{g},≤⟩×⟨\Rcpu{\$},≤⟩},\nonumber \\
    \batterycapacity & ⟼\{⟨\batterycapacity/ρᵢ,αᵢ\,\batterycapacity⟩ \mid i=1, …, n\}.\label{eq:ftor_battery_continuous-2-1}
\end{align}
In this case, each capacity $\batterycapacity$ is mapped to an antichain
of $n$ elements.
\end{example}

## Some examples of design problems


### Mechatronics

Many mechanisms can be readily modeled as relations between a provided
functionality and required resources.


\begin{example}
The \F{functionality} of a DC motor~(\figref{dc_motor})
is to provide a certain \F{speed} and \F{torque}, and the \R{resources}
are \R{current} and \R{voltage}.
\end{example}

\begin{figure}[H]
\subfloat[\label{fig:dc_motor}]{\includegraphics[scale=0.33]{reits2_DC_motor}}
\subfloat[\label{fig:gearbox}]{\includegraphics[scale=0.33]{reits2_gearbox}}}
\caption{}
\end{figure}

\begin{example}
A gearbox (\figref{gearbox}) provides a certain \F{output
torque $τₒ$} and \F{speed $τₒ$}, given a certain
\R{input torque $τᵢ$} and \R{speed $ωᵢ$}. For
an ideal gearbox with a reduction ratio $r∈ℚ₊$ and
efficiency ratio $γ$, $0<γ<1$, the constraints among
those quantities are ${\colRωᵢ}≥ r\,{\colFωₒ}$
and ${\colRτᵢωᵢ}≥γ\,{\colFτₒωₒ}.$
\end{example}


\begin{example}
\emph{Propellers}~(\figref{propeller}) generate \F{thrust}
given a certain \R{torque} and \R{speed}.
\end{example}

\begin{figure}[H]
\subfloat[\label{fig:propeller}]{\includegraphics[scale=0.33]{reits2_propellers}}
\subfloat[\label{fig:crack}]{\includegraphics[scale=0.33]{reits2_crank_rocker}}
\caption{}
\end{figure}

\begin{example}
A *crank-rocker*~(\figref{crack}) converts \R{rotational
motion} into a \F{rocking motion}.
\end{example}


### Geometrical constraints

Geometrical constraints are examples of constraints that are easily
recognized as monotone, but possibly hard to write down in closed
form.

\begin{example}[Bin packing]
Suppose that each internal component occupies a volume
bounded by a parallelepiped, and that we must choose the minimal enclosure
in which to place all components~(\figref{packing}). What
is the minimal size of the enclosure? This is a variation of the \emph{bin
packing} problem, which is in NP for both 2D and 3D~\cite{lodi02two}.
It is easy to see that the problem is monotone, by noticing that,
if one the components shapes increases, then the size of the enclosure
cannot shrink.
\end{example}

\begin{figure}[H]
\includegraphics[scale=0.33]{reits2_fit_boxes}
\caption{\label{fig:packing}}
\end{figure}


### Inference

Many inference problems have a monotone formalization, taking the
\F{accuracy} or \F{robustness} as functionality, and \R{computation}
or \R{sensing} as resources. Typically these bounds are known in
a closed form only for restricted classes of systems, such as the
linear/Gaussian setting.
\begin{example}
(SLAM) One issue with particle-filter-based estimation procedures,
such as the ones used in the popular GMapping~\cite{grisetti07improved}
method, is that the filter might diverge if there aren't enough particles.
Although the relation might be hard to characterize, there is a monotone
relation between the \F{robustness} (1 - probability of failure),
the \F{accuracy}, and the \R{number of particles}~(\figref{gmapping}).
\end{example}

\begin{figure}[H]
\subfloat[\label{fig:gmapping}]{
\includegraphics[scale=0.33]{reits2_particlefilter}

}\subfloat[\label{fig:progressive}]{\includegraphics[scale=0.33]{reits2_progressive_stereo}}\caption{}
\end{figure}


\begin{example}
(Stereo reconstruction) Progressive reconstruction system (e.g.,~\cite{locher16progressive}),
which start with a coarse approximation of the solution that is progressively
refined, are described by a smooth relation between the \F{resolution}
and the \R{latency} to obtain the answer~(\figref{progressive}).
A similar relation characterizes any anytime algorithms in other domains,
such as robot motion planning.
\end{example}


\begin{example}
The empirical characterization of the monotone relation between \F{the
accuracy of a visual SLAM solution} and \R{the power consumption}
is the goal of recent work by Davison and colleagues~\cite{nardi15introducing,zia16comparative}.
\end{example}


### Communication

\begin{example}[Transducers]
Any type of "transducer" that bridges between different
mediums can be modeled as a DP. For example, an access point~(\figref{accesspoint})
provides the \F{"wireless access"} functionality, and requires
that the infrastructure provides the \R{"Ethernet access"} resource.
\end{example}

\begin{figure}[H]
\subfloat[\label{fig:accesspoint}]{\includegraphics[scale=0.33]{reits2_network2}}
\subfloat[\label{fig:networklink}]{\includegraphics[scale=0.33]{reits2_communication}}\caption{\label{fig:communication}}
\end{figure}

\begin{example}[Wireless link]
The basic functionality of a wireless link is to provide
a certain \F{bandwidth}. Further refinements could include bounds
on the latency or the probability that a packet drop is dropped. Given
the established convention about the the preference relations for
functionality, in which a \emph{lower} functionality is "easier"
to achieve, one needs to choose "\F{\emph{minus} the latency}"
and "\F{\emph{minus} the packet drop probability}" for them
to count as functionality. As for the resources, apart from the \R{transmission
power &#91;W&#93;}, one should consider at least \R{the spectrum occupation},
which could be described as an interval $[f₀,f₁]$ of the frequency
axis $\Rcpu{Hz}$. Thus the resources space is $ℛ=\colR\Rcpu{W}×\vmath{intervals}(\Rcpu{Hz})$.
\end{example}



\subsubsection{Multi-robot systems}

In a multi-robot system there is always a trade-off between the number
of robots and the capabilities of the single robot.
\begin{example}
Suppose we need to create a swarm of agents whose functionality is
\F{to sweep an area}. If the functionality is fixed, one expects
a three-way trade-off between the three resources: number of agents,
the speed of a single agent, and the execution time. For example,
if the time available decreases, one has to increase either the speed
of an agent or the number of agents~(\figref{multirobot2}).
\end{example}

\begin{figure}[H]
\subfloat[]{
\includegraphics[scale=0.33]{reits2_multirobot}

}\subfloat[\label{fig:multirobot2}]{
\includegraphics[scale=0.33]{reits2_multirobot2}

}\caption{}
\end{figure}

\clearpage


\subsubsection{LQG Control}
\begin{example}
\label{exa:lqg}Consider the simple case of a linear-quadratic-Gaussian
regulation control problem. The plant is described by the time-invariant
stochastic differential equations:
\begin{eqnarray*}
\D\boldsymbol{x}ₜ & = & \MA\boldsymbol{x}ₜ\D t+\MB\boldsymbol{u}ₜ\D t+\ML\D\boldsymbol{v}ₜ,\\
\D\boldsymbol{y}ₜ & = & \MC\boldsymbol{y}ₜ\D t+\MG\D\boldsymbol{w}ₜ,
\end{eqnarray*}
with $\boldsymbol{v}ₜ$ and $\boldsymbol{w}ₜ$ two standard
Brownian processes. Let $\MV=\ML\ML^{*}$ and $\MW=\MG\MG^{*}$
be the effective noise covariances. Also assume that the pair $(\MA,\MB)$
is stabilizable and $(\MC,\MA)$ is detectable. Consider the quadratic
cost
\[
J=\lim_{T⇒∞}\tfrac{1}{T}∫₀^{T}\|\MQ^{½}\boldsymbol{x}ₜ\|₂^{2}+\|\MR^{½}\boldsymbol{u}ₜ\|₂^{2}\D t.
\]
Let the control objective be of the type "enforce $\ex{\{J\}}≤ J₀$".
\end{example}


\begin{proposition}
The LQG problem admits a formulation as a monotone design problem
in which $\colF-J₀$ is the functionality, and ${\colR\M{V}^{-1}}$
and ${\colR\M{W}^{-1}}$ are resources.
\end{proposition}

\begin{figure}
\includegraphics[scale=0.33]{reits2_lqg}\caption{}
\end{figure}


\begin{proof}
The performance requirements are specified by the value of $J₀$.
In the DP formalization, it is required that the functionality space
is ordered so that "smaller is easier", so one should take $\colF-J₀$
instead of $J₀$ as the functionality.

It is possible to interpret the covariances $\M{V}$ and $\M{W}$
as resources; specifically, as the quality of the sensors and actuators.
Also in this case a reparameterization is necessary. Intuitively,
given a \uline{lower} bound on the functionality $\colF-J₀$
, one has an upper bound on the cost function $J$, from which one
gets an \uline{upper} bound on the sensor noise covariance matrix $\M{W}$.
This is straightforward given the Data Processing Inequality: if increasing
the observation noise could decrease the control objective then the
optimal controller would be injecting extra noise on the observations.
However, a \uline{lower} bound on the functionality requires a
\uline{lower} bound on the resources. The solution is to choose ${\colR\M{W}^{-1}}$
as the resource.

More formally, to see that ${\colR\M{V}^{-1}}$ and ${\colR\M{W}^{-1}}$
are resources, it is sufficient to write down the value of the optimal
LQG cost $J^{★}$ as a function of the parameters (\prettyref{lem:The-minimum-cost})
and observe the monotonicity relations between $\M{V},\M{W}$, $\overline{\MS}$,
$\overline{\MSigma}$ and $J^{★}$.
\end{proof}

\begin{lemma}
\label{lem:The-minimum-cost}The minimum cost for an LQG problem is~\cite[p. 357]{speyer08stochastic}
\begin{equation}
J^{\ast}=\matTrace\{\overline{\MS}\MB\MR^{-1}\MB^{\ast}\overline{\MS}\,\overline{\MSigma}+\overline{\MS}\MV\}\label{eq:Jlqg2}
\end{equation}
where $\overline{\MS}$ is the solution of the Riccati equation
\[
\MA\MS+\MS\MA^{\ast}-\MS\MB\MR^{-1}\MB^{\ast}\MS+\MQ=\M{0}.
\]
and $\overline{\MSigma}$ is solution of the algebraic Riccati equation
\begin{equation}
\MA\MSigma+\MSigma\MA^{\ast}-\MSigma\MC^{\ast}\boldsymbol{\M{W}^{-1}}\MC\MSigma+\MV=\M{0}.\label{eq:riccati2}
\end{equation}
The minimum cost~\eqref{Jlqg2} can also be written as~\cite[p. 188]{davis77linear}
\begin{equation}
J^{★}=\matTrace\{ \MC\overline{\MSigma}\,\overline{\MS}\,\overline{\MSigma}\MC^{*}\M{W}^{-1}+\overline{\MSigma}\MQ\} .\label{eq:Jlqg}
\end{equation}
\end{lemma}



\subsubsection{Computation}

% keep wrapped
\begin{wrapfigure}{r}{0\columnwidth}
\includegraphics[scale=0.33]{reits2_cpu_simple}\caption{}
\end{wrapfigure}
\leavevmode

The trivial model of a CPU is as a device that provides \F{computation,
measured in flops}, and requires \R{power &#91;W&#93;}. Clearly there
is a monotone relation between the two.

A similar monotone relation between application requirements and computation
resources holds in a much more general setting, where both application
and computation resources are represented by graphs. This will be
an example of a monotone relation between nontrivial partial orders.

In the Static Data Flow (SDF) model of computation~\cite[Chapter 3]{sriram00,lee10},
the application is represented as a graph of procedures that need
to be allocated on a network of processors.

% keep wrapped
\begin{wrapfigure}{r}{0\columnwidth}
\includegraphics[scale=0.33]{reits2_small_app_graph}
\end{wrapfigure}

Define the\emph{ application graph }(sometimes called "computation
graph") as a graph where each node is a procedure (or "actor")
and each edge is a message that needs to be passed between procedures.
Each node is labeled by the number of ops necessary to run the procedure.
Each edge is labeled by the size of the message. There is a partial
order $≼$ on application graphs. In this order, it holds that $A₁≼ A₂$
if the application graph $A₂$ needs more computation or bandwidth
for its execution than $A₁$. Formally, it holds that $A₁≼ A₂$
if there is a homomorphism $\varphi:A₁ ⇒ A₂$; and,
for each node $n∈A₁$, the node $\varphi(n)$ has equal or
larger computational requirements than $n$; and for each edge $⟨n₁,n₂⟩ $
in $A₂$, the edge $⟨\varphi(n₁),\varphi(n₂)⟩ $
has equal or larger message size.

\begin{wrapfigure}{r}{0\columnwidth}
\includegraphics[scale=0.33]{reits2_small_res_graph}\end{wrapfigure}

Define a\emph{ resource graph} as a graph where each node represents
a processor, and each edge represents a network link. Each node is
labeled by the processor capacity &#91;flops&#93;. Each edge is labeled
by latency &#91;s&#93; and bandwidth &#91;B/s&#93;. There is a partial order
on resources graph as well: it holds that $R₁≼ R₂$ if
the resource graph $R₂$ has more computation or network available
than $R₁$. The definition is similar to the case of the application
graph: there must exist a graph homomorphism $\varphi:R₁⇒ R₂$
and the corresponding nodes (edges) of $R₂$ must have larger
or equal computation (bandwidth) than those of $R₁$.

\begin{wrapfigure}{r}{0\columnwidth}
\includegraphics[scale=0.33]{reits2_small_allocation}\end{wrapfigure}

Given an application graph $A$ and a resource graph $R$, a typical
resource allocation problem consists in choosing in which processor
each actor must be scheduled to maximize the throughput $T$~&#91;Hz&#93;.
This is equivalent to the problem of finding a graph homomorphism $\Psi:A⇒ R$.
Let $T^{\ast}$ be the optimal throughput, and write it as a function
of the two graphs:
\[
T^{\ast}=T^{\ast}(A,R).
\]
Then the optimal throughput $T^{*}$ is decreasing in $A$ (a more
computationally demanding application graph decreases the throughput)
and increasing in $R$ (more available computation/bandwidth increase
the throughput).

Therefore, we can formalize this as a design problem where the two
functionalities are \F{the throughput $T$ &#91;Hz&#93;} and \F{the
application graph $A$}, and the \R{resource graph $R$} is the
resource.

\begin{figure}

\includegraphics[scale=0.33]{reits2_resourcegraph1}

\caption{}
\end{figure}




\section{Monotone Co-Design Problems (MCDPs)}

A Monotone Co-Design Problem (MCDP) is a multigraph of DPs with arbitrary
interconnections, including loops and self-loops.

If two DPs have a resource $\res₁∈ ℛ₁$ and a functionality $\fun₂∈ℱ₂$
of the same type~($ℱ=ℛ$), then they can be connected by
an edge. The edge represents a partial order constraint of the type $\res₁≼\fun₂$.

The semantics of an edge is: the resources $\res₁$ required by
the first system must not exceed the functionality provided by the
second system~(\figref{sem}).

\begin{figure}

\includegraphics[scale=0.33]{reits2_interconnection}

\caption{\label{fig:sem}}
\end{figure}

\begin{definition}
A\emph{ }Monotone Co-Design Problem (MCDP) is a tuple $⟨ℱ,ℛ,⟨𝒩,ℰ⟩⟩$,
where $ℱ$ and $ℛ$ are two posets, and $⟨𝒩,ℰ⟩ $
is a\emph{ }multigraph of DPs:
\begin{itemize}
\item Each node $n∈𝒩$ corresponds to a DP $⟨ℱₙ,ℛₙ,\ftorₙ⟩ $.
The spaces $ℱₙ$ and $ℛₙ$ are composed of individually
addressable components $\{ℱₙⁱ\}_{i=1}^{Fₙ}$ and $\{ℛₙ^{j}\}_{j=1}^{Rₙ}$,
so that they can be written as $ℱₙ=∏_{i=1}^{Fₙ}ℱₙⁱ,$
$ℛₙ=∏ⱼ^{Rₙ}ℛₙ^{j}.$
\item An edge $e∈ℰ$ is a tuple $e=⟨⟨n₁,i₁⟩, ⟨n₂,j₂⟩⟩ $,
where $n₁,n₂∈𝒩$ are two nodes and $i₁$~and $j₂$
are the indices of the components of the nodes' functionality and
resources. A valid edge is such that $ℱ_{n₁}^{i₁}=ℛ_{n₂}^{j₂}$.
\item The posets $ℱ,ℛ$ are the products of the unconnected components.
For a node $n$, let $\unconnectedfun(n)$ and $\unconnectedres(n)$
be the set of unconnected functionalities and resources. Then $ℱ$
and $ℛ$ are defined as follows:
\[
\begin{array}{ccc}
ℱ & ={\displaystyle ∏_{n∈𝒩}∏_{i∈\unconnectedfun(n)}}ℱₙⁱ,\qquad & \qquadℛ={\displaystyle ∏_{n∈𝒩}∏_{j∈\unconnectedres(n)}}ℛₙⁱ.\end{array}
\]`
\end{itemize}
\end{definition}


\begin{figure}

\includegraphics[scale=0.33]{reits2_graph}

\caption{\label{fig:mcdps}}
\end{figure}


\subsubsection{Compositionality and abstraction}

It can be shown~\cite{censi16codesign} that the property of monotonicity
is preserved by arbitrary interconnection, which means that there
exists a monotone function $\ftor$ for the entire MCDP that is equivalent
to the interconnection of the simple DPs~(\figref{mcdps},
right).

\subsubsection{Solution of MCDPs}



The function $\ftor$ for the entire MCDP can be written as the solution
of a least-fixed-point recursive equation involving the functions $\{\ftorₙ,␣n∈𝒩\}$.
Therefore, given a systematic procedure to solve the single DPs, in
the sense of being able to evaluate $\ftorₙ$ point-wise, there
exists a systematic procedure to solve the larger MCDP.




\subsection{Examples of MCDPs}

\begin{example}
(Energetics of Mars rover) The Mars Science Laboratory uses a RITEG~(Radioisotope
Thermoelectric Generator) to generate electric power. In a RITEG,
the decay of a Plutonium 238 pellet produces heat. The heat is converted
into electric power by a thermocouple. In the MCDP representation~(\figref{rover_energetics}),
the \F{heat &#91;W&#93;} produced is the pellet's functionality. For
the thermocouple, the \R{heat} is a resource, and the \F{electric
power &#91;W&#93;} is the functionality. There is a monotone relation
between the amount of plutonium and the generated power.

When does one get a plutonium pellet? You ask the Department of Energy~\cite{nasa15radioisotope},
and the amount you will receive is a monotonic function of the scientific
value of the mission you propose.
\end{example}


\begin{figure}[H]

\includegraphics[scale=0.33]{reits2_rover_energetics}

\caption{\label{fig:rover_energetics}}
\end{figure}

\begin{example}
(LQG, continued from Example~\ref{exa:lqg}) Suppose that the observations $\boldsymbol{y}$
are provided by a camera. A lower bound on the information matrix $\colR\M{W}^{-1}$
induces a constraint on \R{the sensor resolution $ρ$ &#91;pixels/deg&#93;}~(\figref{lqg2}).
Assuming independent sensor elements, then the relation between $ρ$
and $\M{W}^{-1}$ is linear: ${\colRρ}≤ c␣\colF\M{W}^{-1}$.
The \R{resource \emph{sensor resolution}} then induces a constraint
on the \F{functionality \emph{sensor resolution}} provided by the
sensor, as well as the amount of computation required.
\end{example}


\begin{figure}
    \includegraphics[scale=0.33]{reits2_lqg2}
    \caption{\label{fig:lqg2}}
\end{figure}

\begin{example}
(UAV energetics and actuation) Suppose we need to choose batteries
and actuators for a UAV. This a simple case that introduces a loop
in the diagram: the battery must provide power for the actuation,
and the actuation needs to lift the battery's weight. Let the battery
be a DP with \F{capacity &#91;J&#93;} and \F{life span &#91; number of
missions&#93;} as functionalities and \R{mass} and \R{cost} as
resources. Let the actuation be formalized a DP with functionality
\F{lift &#91;N&#93;} and resources \R{power &#91;W&#93;} and \R{cost
&#91;\$&#93;}. Assume that other mission requirements include \F{extra
payload &#91;g&#93;}, \F{extra power &#91;W&#93;} and \F{endurance &#91;s&#93;}.
Then one can write down the following constraints:
\begin{align*}
\text{battery capacity} & ≤\text{endurance}×\text{total power},\\
\text{total power} & =\text{extra power}+\text{actuation power},\\
\text{lift} & ≤(\text{battery mass}+\text{actuator mass})×\text{gravity}.
\end{align*}
The constraints create one loop in the graph~(\figref{actuation_energetics}).
For the purpose of counting loops, consider the edges with the \F{functionality}$arrow$\R{resource}
orientation. This implies that the choices of battery and actuator
are not independent.
\end{example}


\begin{figure}[H]
    \includegraphics[scale=0.33]{reits2_actuation_energetics}
    \caption{\label{fig:actuation_energetics}}
\end{figure}


Because monotonicity is preserved by composition, it is immediate
to conclude qualitative results such as "increasing the \F{endurance}
increases the \R{cost} of the solution" by simple visual inspection
of the diagram.
\begin{example}
It is easy (and fun!\textemdash for some) to arrange simple DPs into
complex MCDPs. The graphs quickly become too complex to be legible.
For example, \figref{drone_complete} shows the MCDP corresponding
to a UAV, obtained by composing the actuation/energetics constraint.
The entire UAV is abstracted as a DP between high-level functionality
(\F{travel distance}, \F{payload}, \F{number of missions}),
and one resource (\R{total cost of ownership &#91;\$&#93;}). This MCDP
was defined using MCDP\textbf{L}, a domain-specific language to describe
MCDPs. See \url{http://mcdp.mit.edu/wafr.html} for a detailed walkthrough
of this example.
\end{example}

\begin{figure}[H]

\includegraphics[scale=0.33]{reits2_drone_complete}

\caption{\label{fig:drone_complete}}
\end{figure}
\begin{example}
(Customer preferences) MCDPs can also be used to describe customer
preferences. From the point of view of the customer, the role of functionality
and resources is dual with respect to the point of view of the engineer~(\figref{customer}).
The engineering problem is: "Given a certain functionality to be
implemented, what are the minimal resources necessary to implement
it?". The customer preferences can be encoded by the answer to the
dual question: "Given the resources (\$) to be provided by the customer,
what is the minimal functionality required?". A feasible solution
to such an MCDP with a "customer in the loop" is a solution that
is feasible both from the engineering point of view, as well as from
the business point of view.
\end{example}


\begin{figure}[H]

\includegraphics[scale=0.33]{reits2_customer}

\caption{\label{fig:customer}}
\end{figure}
