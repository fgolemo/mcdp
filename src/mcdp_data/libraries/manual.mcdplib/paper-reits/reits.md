

\title{In Robotics, Everything Is The Same}

\author{Andrea Censi\thanks{The author is with the Laboratory for Information and Decision Systems
(LIDS) at the Massachusetts Institute of Technology. E-mail: censi@mit.edu.}}
\maketitle
\begin{abstract}
One of the limitations towards creating an "automated roboticist"
that synthesizes an optimal design for an entire robotic system is
that there does not exist a unified language that is expressive enough
to describe the design constraints and performance objectives for
all subsystems (energetics, computation, communication, \ldots{}),
and that still results in tractable optimization problems.

This paper shows that the design constraints of a robot's subsystems,
as well as their interactions, are captured by a class of optimization
problems called "Monotone Co-Design Problems", and that this formalism
can be used for both the quantitative solution as well as the qualitative
analysis of robot design problems.

In this formalization, each subsystem is characterized in terms of
\F{"functionality"} (what the system \emph{provides} to other
subsystems) and \R{"resources"} (what the subsystem \emph{requires}
from other systems). The relation between functionality and resource
is "monotone", in the sense that increasing the requirements on
the functionality does not decrease the resources required. This property
of monotonicity is preserved by various types of composition that
represent the interaction of different components.

Examples are given for energetics, propulsion, actuation, computation,
communication, perception, inference, control, coordination.

\end{abstract}





\section{Introduction}

The development of robotic systems remains an eminently empirical
activity. If robotics was completely formalized, it would be possible
to create an "automated roboticist", which, given the specification
of a task, could automatically synthesize an "optimal" design
for a robot, including hardware and software.

The works by Mehta, Rus, and collaborators~\cite{mehta14cogeneration,mehta14design,mehta14end}
have shown that it is possible to create a software system that can
co-generate hardware and software blueprints for entire robot platforms,
and possibly together with the synthesis of control strategies~\cite{mehta15robot},
starting from the instantiation of existing modules selected by the
user.

Ideally, one would like the design to be completely automated, starting
from a high-level functional specification, and with guarantees of
optimality. In most cases, the concept of optimality that is useful
in robotics is one of "minimality". Given a performance specification
on the \F{functionality}, one would like to use the least amount
of \R{resources} to perform the task. For example, one could consider
the problem of performing a given task using the minimal \R{sensors};
variants of this problem were approached theoretically by O'Kane and
Lavalle~\cite{okane07localization} and more empirically by Milford~\cite{milford13vision}.
More generally, one would like to find the minimal \emph{combinations}
of sensors and \R{actuators} that are sufficient for a task~\cite{okane08comparing}.
Even more generally, an automated robot design system would allow
the user to minimize several types of resources or generalized "costs",
such as \R{production cost~&#91;\$&#93;}, \R{maintenance cost &#91;\$&#93;},
\R{power consumption &#91;W&#93;}, etc.

This paper presents a modeling language that is expressive enough
to capture the "co-design constraints" that relate all subsystems
of a robot, including energetics, propulsion, actuation, computation,
communication, perception, inference, control, coordination, etc.
The idea is to model each subsystem as a "design problem", formally
defined as a relation between the "\F{functionality}" that a
subsystem provides and the "\R{resources}" that it requires.
The relation between functionality and resource is "monotone",
in the sense that increasing the requirements on the functionality
does not decrease the resources required. This property of monotonicity
is preserved by various types of composition that represent the interaction
of different components.

This paper continues the work started in~\cite{censi15monotone,censi15same}.





\section{Design Problems (DPs)}

\noindent\begin{minipage}[t]{1\columnwidth}
\begin{wrapfigure}{r}{0\columnwidth}
\includegraphics[scale=0.33]{reits2_dp}\caption{\label{fig:dp}}
\end{wrapfigure}
Define a \emph{design problem} as a relation between \emph{\F{provided functionality}}
and \emph{\R{required resources}}~(\prettyref{fig:dp}). \F{Functionality}
and \R{resources} are partially ordered sets, indicated by by~$\langle\funsp,\funleq\rangle$
and~$\langle\ressp,\resleq\rangle$.
\end{minipage}




\begin{wrapfigure}[6]{r}{0\columnwidth}
\includegraphics[scale=0.33]{reits2_battery1}\caption{\label{fig:battery1}}
\end{wrapfigure}

\noindent
\begin{minipage}[t]{0.65\columnwidth}
\begin{example}
(Battery) The first-order characterization of a battery is as a store
of energy, in which the \F{capacity &#91;kWh&#93;} is the \F{functionality}
and the \R{mass &#91;kg&#93;} is a \R{resource}~(\prettyref{fig:battery1}).
The \F{capacity} is a functionality because it is what a battery
\emph{provides} to the system.
\end{example}


\end{minipage}

The \R{mass} is a resource: it is what the battery \emph{requires}
to provide the functionality. The functionality space is~$\funsp=\langle\mathbb{R}_{+}^{\text{J}},\leq\rangle$.
The superscript~$\text{J}$ indicates that the values have the dimensionality
of Joules. The resource space is $\ressp=\langle\mathbb{R}_{+}^{\text{g}},\leq\rangle.$

As in all modeling efforts, the level of detail depends on the application.
Other models for a battery would take into account other resources.
For example, one might want to consider the \R{cost} of the battery
in addition to the mass~(\prettyref{fig:battery2}). Other properties
of interest for a battery-like device include the \F{maximum output current},
\F{maximum power draw}, and which \F{voltage} it provides~(\prettyref{fig:battery3}).

\begin{figure}
\subfloat[\label{fig:battery2}]{
\includegraphics[scale=0.33]{reits2_battery2}
\par
}\subfloat[\label{fig:battery3}]{
\includegraphics[scale=0.33]{reits2_battery3}
\par
}

\caption{}
\end{figure}


\subsubsection{Formal definition of a DP }

A DP is described by the answer to the question
\begin{quote}
(&#42;) "Given a certain \F{functionality} $\fun\in\funsp$ to be
implemented, what are \R{the \textbf{minimal} resources}, a subset
of~$\ressp$, necessary to implement~$\fun$?".
\end{quote}
This choice imposes the direction \F{functionality}$\rightarrow$\R{resources},
but the theory is entirely symmetric, and one could choose to consider
the \emph{dual} question: "Given certain available resources~$\res\in\ressp$,
what are \F{the\textbf{ maximal} functionalities}, a subset of~$\funsp$,
that can be implemented?".

\noindent\begin{minipage}[t]{1\columnwidth}
\begin{wrapfigure}{r}{0\columnwidth}
\includegraphics[scale=0.33]{reits2_battery2_h}\caption{\label{fig:multiple}}
\end{wrapfigure}

In general, fixed a functionality~$\fun\in\funsp$, there will be
multiple resources that are sufficient to perform the functionality
that are incomparable. For example, in the case of a battery one might
consider different battery technologies that are incomparable in the
mass/cost resource space.~(\prettyref{fig:multiple}).

A subset with "minimal", "incomparable" elements is called
"antichain".
\end{minipage}
\begin{definition}
An antichain~$S$ in a poset~$\left\langle \posA,\posleq\right\rangle $
is a subset of~$\posA$ such that no element of~$S$ dominates another
element: if~$x,y\in S$ and~$x\leq y$, then~$x=y$.
\end{definition}

\begin{lemma}
Let~$\antichains\posA$ be the set of antichains of~$\posA$. $\antichains\posA$
is a poset itself, with the partial order given by
\begin{equation}
S_{1}\posleq_{\antichains\posA}S_{2}\ \equiv\ \uparrow S_{1}\supseteq\,\uparrow S_{2}.\label{eq:orderantichains}
\end{equation}
\end{lemma}

\noindent\begin{minipage}[t]{1\columnwidth}
\begin{wrapfigure}[7]{r}{0\columnwidth}
\includegraphics[scale=0.33]{reits2_dp_h_one}\caption{}
\end{wrapfigure}

Answering the question (&#42;) above is equivalent to defining a map
\[
\ftor:\funsp\rightarrow\Aressp
\]
that associates to each functionality~$\fun$ an antichain of resources~$\ftor(\fun)\subset\ressp$,
with the semantics that those are the \emph{minimal} resources needed
to provide the functionality~$\fun$. The set~$\ftor(\fun)$ need
not be finite or discrete; it can be either.
\end{minipage}


\noindent\begin{minipage}[t]{1\columnwidth}
\begin{wrapfigure}[6]{r}{0\columnwidth}
\includegraphics[scale=0.33]{reits2_dp_h_two}\caption{\label{fig:up}}
\end{wrapfigure}
A further condition is imposed on $\ftor.$ We require that the map~$\ftor$
is monotone, in the sense that
\[
\left(\fun_{2}\posgeq_{\funsp}{\fun_{1}}\right)\Rightarrow\left(\ftor(\fun_{2})\posgeq_{\Aressp}\ftor(\fun_{1})\right)
\]

This means that if~$\fun_{2}\posgeq_{\funsp}{\fun_{1}}$, the curve~$\ftor(\fun_{2})$
is higher than~$\ftor(\fun_{1})$ (\prettyref{fig:up}, right), as
implied by the order on the antichains given by~\prettyref{eq:orderantichains}.
\end{minipage}


\noindent
\noindent\begin{minipage}[t]{1\columnwidth}
\begin{wrapfigure}[8]{r}{0\columnwidth}
\includegraphics[scale=0.33]{reits2_dp_h}\caption{}
\end{wrapfigure}
We are now ready to give a formal definition of a design problem.
\begin{definition}
\label{def:A-monotone-design}A\emph{ design problem~}(DP) is a tuple~$\left\langle \funsp,\ressp,\ftor\right\rangle $
such that~$\funsp$ and~$\ressp$ are posets, and~${\colH\ftor}:{\colF\fun}\rightarrow{\colR\antichains\ressp}$
is a monotone function.
\end{definition}


\end{minipage}



\begin{example}
(battery, continued) To specify a DP, one needs to specify the poset~$\funsp$,
the poset~$\ressp$, and the function~$\ftor:\funsp\rightarrow\Aressp$
in~\prettyref{def:A-monotone-design}. It was already established
that~$\funsp=\colF\langle\mathbb{R}_{+}^{J},\leq\rangle$ and~$\ressp={\colR\langle\mathbb{R}_{+}^{g},\leq\rangle}$.
The relation between \R{battery mass}~$\batterymass$ and \F{capacity}~$\batterycapacity$
is given by the specific energy~$\rho$, with the simple linear constraint
\begin{equation}
\rho\,\batterymass\geq\batterycapacity.\label{eq:battery_se}
\end{equation}
The formal definition of the map~$\ftor$ is
\begin{align}
\ftor:{\colF\langle\mathbb{R}_{+}^{J},\leq\rangle} & \rightarrow{\colR\antichains\langle\mathbb{R}_{+}^{g},\leq\rangle},\nonumber \\
\batterycapacity & \mapsto\{\batterycapacity/\rho\}.\label{eq:ftor_battery_continuous}
\end{align}
The map~$\ftor$ associates to each value of the \F{capacity}~$\batterycapacity$
a set~$\{\batterycapacity/\rho\}$ describing the minimal \R{mass}
sufficient to provide the given \F{capacity}.

\noindent\begin{minipage}[t]{1\columnwidth}
\begin{wrapfigure}{r}{0\columnwidth}
\includegraphics[scale=0.33]{reits2_battery_h_1}\caption{\label{fig:All-batteries-that}}
\end{wrapfigure}
\leavevmode

The relation~\eqref{eq:battery_se} implicitly assumes that we can
choose one of an infinite amount of batteries of any arbitrary mass~
(\prettyref{fig:All-batteries-that}). This framework can easily accommodate
that case of only a discrete set of available battery models.

\vspace{4mm}
\end{minipage}
\end{example}

\medskip{}

\medskip{}

\begin{wrapfigure}[8]{r}{0\columnwidth}
\includegraphics[scale=0.33]{reits2_battery_h_2}\caption{\label{fig:Finite-number-of-1}}
\end{wrapfigure}
\leavevmode

\vspace*{-1.5\baselineskip}
\begin{example}
(Discrete increments) Suppose that the batteries are available in
increments of~$\Delta_{m}$ &#91;g&#93;, so that we can only have \R{mass}~$\batterymass\in\{{\colF k}\Delta_{m},\ {\colF k}\in\mathbb{N}\}.$
The map in~\eqref{eq:ftor_battery_continuous} can be amended as
follows:
\begin{align}
\ftor:{\colF\langle\mathbb{R}_{+}^{J},\leq\rangle} & \rightarrow{\colR\antichains\langle\mathbb{R}_{+}^{g},\leq\rangle},\nonumber \\
\batterycapacity & \mapsto\{\batterymass^{\star}\},\label{eq:ftor_battery_continuous-1-1}\\
 & \batterymass^{\star}=\begin{cases}
\min_{k} & k\Delta_{m}\\
\subto & \rho k\Delta_{m}\geq\batterycapacity.
\end{cases}
\end{align}
In other words, the best mass~$\batterymass^{\star}$ is the minimum
mass that satisfies the capacity constraint, searching over all the
implementation possibilities, here described by the index~$k$. The
graph of the function~$\ftor$ has a shape similar to the one pictured
in~\prettyref{fig:Finite-number-of-1}. Note that the graph is discontinuous;
in this framework, there is no continuity constraint on~$\ftor$.
\end{example}

\begin{figure}
\includegraphics[scale=0.33]{reits2_battery2_h}
\caption{\label{fig:pipe}}
\end{figure}

\begin{example}
(Different batteries technologies) Consider choosing between~$n$
competing battery technologies, characterized by the specific energy~$\rho_{i}$
&#91;kWh/g&#93; and specific cost~$\alpha_{i}$ &#91;&#96;/kWh&#93;. The resource
space is~$\ressp=\colR\langle\mathbb{R}_{+}^{g},\leq\rangle\times\langle\mathbb{R}_{+}^{\$},\leq\rangle.$
The cost~$\batterycost$ is related to the capacity linearly through
the specific cost~$\alpha_{i}$:~$\batterycost\geq\alpha_{i}\,\batterycapacity.$
The map~$\ftor$ is
\begin{align}
\ftor:{\colF\langle\mathbb{R}_{+}^{J},\leq\rangle} & \rightarrow{\colR\antichains\langle\mathbb{R}_{+}^{g},\leq\rangle\times\langle\mathbb{R}_{+}^{\$},\leq\rangle},\nonumber \\
\batterycapacity & \mapsto\{\left\langle \batterycapacity/\rho_{i},\alpha_{i}\,\batterycapacity\right\rangle \mid i=1,\dots,n\}.\label{eq:ftor_battery_continuous-2-1}
\end{align}
In this case, each capacity~$\batterycapacity$ is mapped to an antichain
of~$n$ elements.
\end{example}




<!-- 
\subsection{Examples in the robotics domain}


\subsubsection{Mechatronics}

Many mechanisms can be readily modeled as relations between a provided
functionality and required resources.


\begin{example}
The \F{functionality} of a DC motor~(\prettyref{fig:dc_motor})
is to provide a certain \F{speed} and \F{torque}, and the \R{resources}
are \R{current} and \R{voltage}.
\end{example}

\begin{figure}[H]
\subfloat[\label{fig:dc_motor}]{\includegraphics[scale=0.33]{reits2_DC_motor}}\subfloat[\label{fig:gearbox}]{
\includegraphics[scale=0.33]{reits2_gearbox}
\par
}\caption{}
\end{figure}

\begin{example}
A gearbox (\prettyref{fig:gearbox}) provides a certain \F{output
torque~$\tau_{o}$} and \F{speed~$\tau_{o}$}, given a certain
\R{input torque~$\tau_{i}$} and \R{speed~$\omega_{i}$}. For
an ideal gearbox with a reduction ratio~$r\in\mathbb{Q}_{+}$ and
efficiency ratio~$\gamma$, $0<\gamma<1$, the constraints among
those quantities are~${\colR\omega_{i}}\geq r\,{\colF\omega_{o}}$
and~${\colR\tau_{i}\omega_{i}}\geq\gamma\,{\colF\tau_{o}\omega_{o}}.$
\end{example}


\begin{example}
\emph{Propellers}~(\prettyref{fig:propeller}) generate \F{thrust}
given a certain \R{torque} and \R{speed}.
\end{example}

\begin{figure}[H]
\subfloat[\label{fig:propeller}]{\includegraphics[scale=0.33]{reits2_propellers}}
\subfloat[\label{fig:crack}]{\includegraphics[scale=0.33]{reits2_crank_rocker}}
\caption{}
\end{figure}

\begin{example}
A \emph{crank-rocker}~(\prettyref{fig:crack}) converts \R{rotational
motion} into a \F{rocking motion}.
\end{example}


\subsubsection{Geometrical constraints}

Geometrical constraints are examples of constraints that are easily
recognized as monotone, but possibly hard to write down in closed
form.
\begin{example}
(Bin packing) Suppose that each internal component occupies a volume
bounded by a parallelepiped, and that we must choose the minimal enclosure
in which to place all components~(\prettyref{fig:packing}). What
is the minimal size of the enclosure? This is a variation of the \emph{bin
packing} problem, which is in NP for both 2D and 3D~\cite{lodi02two}.
It is easy to see that the problem is monotone, by noticing that,
if one the components shapes increases, then the size of the enclosure
cannot shrink.
\end{example}

\begin{figure}[H]

\includegraphics[scale=0.33]{reits2_fit_boxes}
\par
\caption{\label{fig:packing}}
\end{figure}


\subsubsection{Inference}

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
the \F{accuracy}, and the \R{number of particles}~(\prettyref{fig:gmapping}).
\end{example}

\begin{figure}[H]
\subfloat[\label{fig:gmapping}]{
\includegraphics[scale=0.33]{reits2_particlefilter}
\par
}\subfloat[\label{fig:progressive}]{\includegraphics[scale=0.33]{reits2_progressive_stereo}}\caption{}
\end{figure}


\begin{example}
(Stereo reconstruction) Progressive reconstruction system (e.g.,~\cite{locher16progressive}),
which start with a coarse approximation of the solution that is progressively
refined, are described by a smooth relation between the \F{resolution}
and the \R{latency} to obtain the answer~(\prettyref{fig:progressive}).
A similar relation characterizes any anytime algorithms in other domains,
such as robot motion planning.
\end{example}


\begin{example}
The empirical characterization of the monotone relation between \F{the
accuracy of a visual SLAM solution} and \R{the power consumption}
is the goal of recent work by Davison and colleagues~\cite{nardi15introducing,zia16comparative}.
\end{example}


\subsubsection{Communication}
\begin{example}
(Transducers) Any type of "transducer" that bridges between different
mediums can be modeled as a DP. For example, an access point~(\prettyref{fig:accesspoint})
provides the \F{"wireless access"} functionality, and requires
that the infrastructure provides the \R{"Ethernet access"} resource.
\end{example}

\begin{figure}[H]
\subfloat[\label{fig:accesspoint}]{\includegraphics[scale=0.33]{reits2_network2}}
\subfloat[\label{fig:networklink}]{\includegraphics[scale=0.33]{reits2_communication}}\caption{\label{fig:communication}}
\end{figure}

\begin{example}
(Wireless link) The basic functionality of a wireless link is to provide
a certain \F{bandwidth}. Further refinements could include bounds
on the latency or the probability that a packet drop is dropped. Given
the established convention about the the preference relations for
functionality, in which a \emph{lower} functionality is "easier"
to achieve, one needs to choose "\F{\emph{minus} the latency}"
and "\F{\emph{minus} the packet drop probability}" for them
to count as functionality. As for the resources, apart from the \R{transmission
power &#91;W&#93;}, one should consider at least \R{the spectrum occupation},
which could be described as an interval~$[f_{0},f_{1}]$ of the frequency
axis~$\reals_{+}^{\text{Hz}}$. Thus the resources space is~$\ressp=\colR\reals_{+}^{W}\times\vmath{intervals}(\reals_{+}^{\text{Hz}})$.
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
of an agent or the number of agents~(\prettyref{fig:multirobot2}).
\end{example}

\begin{figure}[H]
\subfloat[]{
\includegraphics[scale=0.33]{reits2_multirobot}
\par
}\subfloat[\label{fig:multirobot2}]{
\includegraphics[scale=0.33]{reits2_multirobot2}
\par
}\caption{}
\end{figure}

\clearpage


\subsubsection{LQG Control}
\begin{example}
\label{exa:lqg}Consider the simple case of a linear-quadratic-Gaussian
regulation control problem. The plant is described by the time-invariant
stochastic differential equations:
\begin{eqnarray*}
\D\boldsymbol{x}_{t} & = & \MA\boldsymbol{x}_{t}\D t+\MB\boldsymbol{u}_{t}\D t+\ML\D\boldsymbol{v}_{t},\\
\D\boldsymbol{y}_{t} & = & \MC\boldsymbol{y}_{t}\D t+\MG\D\boldsymbol{w}_{t},
\end{eqnarray*}
with~$\boldsymbol{v}_{t}$ and~$\boldsymbol{w}_{t}$ two standard
Brownian processes. Let~$\MV=\ML\ML^{*}$ and~$\MW=\MG\MG^{*}$
be the effective noise covariances. Also assume that the pair~$(\MA,\MB)$
is stabilizable and~$(\MC,\MA)$ is detectable. Consider the quadratic
cost
\[
J=\lim_{T\rightarrow\infty}\tfrac{1}{T}\int_{0}^{T}\|\MQ^{\frac{1}{2}}\boldsymbol{x}_{t}\|_{2}^{2}+\|\MR^{\frac{1}{2}}\boldsymbol{u}_{t}\|_{2}^{2}\D t.
\]
Let the control objective be of the type "enforce~$\ex{\{J\}}\leq J_{0}$".
\end{example}

\begin{wrapfigure}[4]{r}{0\columnwidth}
\includegraphics[scale=0.33]{reits2_lqg}\caption{}
\end{wrapfigure}
\leavevmode
\begin{proposition}
The LQG problem admits a formulation as a monotone design problem
in which~$\colF-J_{0}$ is the functionality, and~${\colR\M{V}^{-1}}$
and~${\colR\M{W}^{-1}}$ are resources.
\end{proposition}

\begin{proof}
The performance requirements are specified by the value of~$J_{0}$.
In the DP formalization, it is required that the functionality space
is ordered so that "smaller is easier", so one should take~$\colF-J_{0}$
instead of~$J_{0}$ as the functionality.

It is possible to interpret the covariances~$\M{V}$ and~$\M{W}$
as resources; specifically, as the quality of the sensors and actuators.
Also in this case a reparameterization is necessary. Intuitively,
given a \uline{lower} bound on the functionality~$\colF-J_{0}$
, one has an upper bound on the cost function~$J$, from which one
gets an \uline{upper} bound on the sensor noise covariance matrix~$\M{W}$.
This is straightforward given the Data Processing Inequality: if increasing
the observation noise could decrease the control objective then the
optimal controller would be injecting extra noise on the observations.
However, a \uline{lower} bound on the functionality requires a
\uline{lower} bound on the resources. The solution is to choose~${\colR\M{W}^{-1}}$
as the resource.

More formally, to see that~${\colR\M{V}^{-1}}$ and~${\colR\M{W}^{-1}}$
are resources, it is sufficient to write down the value of the optimal
LQG cost~$J^{\star}$ as a function of the parameters (\prettyref{lem:The-minimum-cost})
and observe the monotonicity relations between~$\M{V},\M{W}$, $\overline{\MS}$,
$\overline{\MSigma}$ and~$J^{\star}$.
\end{proof}

\begin{lemma}
\label{lem:The-minimum-cost}The minimum cost for an LQG problem is~\cite[p. 357]{speyer08stochastic}
\begin{equation}
J^{*}=\matTrace\{\overline{\MS}\MB\MR^{-1}\MB^{*}\overline{\MS}\,\overline{\MSigma}+\overline{\MS}\MV\}\label{eq:Jlqg2}
\end{equation}
where~$\overline{\MS}$ is the solution of the Riccati equation
\[
\MA\MS+\MS\MA^{*}-\MS\MB\MR^{-1}\MB^{*}\MS+\MQ=\M{0}.
\]
and~$\overline{\MSigma}$ is solution of the algebraic Riccati equation
\begin{equation}
\MA\MSigma+\MSigma\MA^{*}-\MSigma\MC^{*}\boldsymbol{\M{W}^{-1}}\MC\MSigma+\MV=\M{0}.\label{eq:riccati2}
\end{equation}
The minimum cost~\prettyref{eq:Jlqg2} can also be written as~\cite[p. 188]{davis77linear}
\begin{equation}
J^{\star}=\matTrace\left\{ \MC\overline{\MSigma}\,\overline{\MS}\,\overline{\MSigma}\MC^{*}\M{W}^{-1}+\overline{\MSigma}\MQ\right\} .\label{eq:Jlqg}
\end{equation}
\end{lemma}



\subsubsection{Computation}

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

\begin{wrapfigure}{r}{0\columnwidth}
\includegraphics[scale=0.33]{reits2_small_app_graph}\end{wrapfigure}

Define the\emph{ application graph }(sometimes called "computation
graph") as a graph where each node is a procedure (or "actor")
and each edge is a message that needs to be passed between procedures.
Each node is labeled by the number of ops necessary to run the procedure.
Each edge is labeled by the size of the message. There is a partial
order~$\posleq$ on application graphs. In this order, it holds that~$A_{1}\posleq A_{2}$
if the application graph~$A_{2}$ needs more computation or bandwidth
for its execution than~$A_{1}$. Formally, it holds that~$A_{1}\posleq A_{2}$
if there is a homomorphism~$\varphi:A_{1}\rightarrow A_{2}$; and,
for each node~$n\in A_{1}$, the node~$\varphi(n)$ has equal or
larger computational requirements than~$n$; and for each edge~$\left\langle n_{1},n_{2}\right\rangle $
in~$A_{2}$, the edge~$\left\langle \varphi(n_{1}),\varphi(n_{2})\right\rangle $
has equal or larger message size.

\begin{wrapfigure}{r}{0\columnwidth}
\includegraphics[scale=0.33]{reits2_small_res_graph}\end{wrapfigure}

Define a\emph{ resource graph} as a graph where each node represents
a processor, and each edge represents a network link. Each node is
labeled by the processor capacity &#91;flops&#93;. Each edge is labeled
by latency &#91;s&#93; and bandwidth &#91;B/s&#93;. There is a partial order
on resources graph as well: it holds that $R_{1}\posleq R_{2}$ if
the resource graph~$R_{2}$ has more computation or network available
than~$R_{1}$. The definition is similar to the case of the application
graph: there must exist a graph homomorphism $\varphi:R_{1}\rightarrow R_{2}$
and the corresponding nodes (edges) of~$R_{2}$ must have larger
or equal computation (bandwidth) than those of~$R_{1}$.

\begin{wrapfigure}{r}{0\columnwidth}
\includegraphics[scale=0.33]{reits2_small_allocation}\end{wrapfigure}

Given an application graph~$A$ and a resource graph~$R$, a typical
resource allocation problem consists in choosing in which processor
each actor must be scheduled to maximize the throughput~$T$~&#91;Hz&#93;.
This is equivalent to the problem of finding a graph homomorphism~$\Psi:A\rightarrow R$.
Let~$T^{*}$ be the optimal throughput, and write it as a function
of the two graphs:
\[
T^{*}=T^{*}(A,R).
\]
Then the optimal throughput~$T^{*}$ is decreasing in~$A$ (a more
computationally demanding application graph decreases the throughput)
and increasing in~$R$ (more available computation/bandwidth increase
the throughput).

Therefore, we can formalize this as a design problem where the two
functionalities are \F{the throughput~$T$ &#91;Hz&#93;} and \F{the
application graph~$A$}, and the \R{resource graph~$R$} is the
resource.

\begin{figure}

\includegraphics[scale=0.33]{reits2_resourcegraph1}
\par
\caption{}
\end{figure} -->




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





\section{Monotone Co-Design Problems (MCDPs)}

A Monotone Co-Design Problem (MCDP) is a multigraph of DPs with arbitrary
interconnections, including loops and self-loops.

If two DPs have a resource~$\res_{1}\in\ressp_{1}$ and a functionality~$\fun_{2}\in\funsp_{2}$
of the same type~($\funsp=\ressp$), then they can be connected by
an edge. The edge represents a partial order constraint of the type~$\res_{1}\posleq\fun_{2}$.

The semantics of an edge is: the resources~$\res_{1}$ required by
the first system must not exceed the functionality provided by the
second system~(\prettyref{fig:sem}).
\begin{center}
\begin{figure}

\includegraphics[scale=0.33]{reits2_interconnection}
\par
\caption{\label{fig:sem}}
\end{figure}
\par\end{center}
\begin{definition}
A\emph{ }Monotone Co-Design Problem (MCDP) is a tuple~$\left\langle \funsp,\ressp,\left\langle \mathcal{N},\mathcal{E}\right\rangle \right\rangle $,
where~$\funsp$ and~$\ressp$ are two posets, and~$\left\langle \mathcal{N},\mathcal{E}\right\rangle $
is a\emph{ }multigraph of DPs:
\begin{itemize}
\item Each node~$n\in\mathcal{N}$ corresponds to a DP~$\left\langle \funsp_{n},\ressp_{n},\ftor_{n}\right\rangle $.
The spaces $\funsp_{n}$ and~$\ressp_{n}$ are composed of individually
addressable components~$\{\funsp_{n}^{i}\}_{i=1}^{F_{n}}$ and~$\{\ressp_{n}^{j}\}_{j=1}^{R_{n}}$,
so that they can be written as $\funsp_{n}=\prod_{i=1}^{F_{n}}\funsp_{n}^{i},$
$\ressp_{n}=\prod_{j}^{R_{n}}\ressp_{n}^{j}.$
\item An edge~$e\in\mathcal{E}$ is a tuple~$e=\left\langle \left\langle n_{1},i_{1}\right\rangle ,\left\langle n_{2},j_{2}\right\rangle \right\rangle $,
where~$n_{1},n_{2}\in\mathcal{N}$ are two nodes and $i_{1}$~and~$j_{2}$
are the indices of the components of the nodes' functionality and
resources. A valid edge is such that~$\funsp_{n_{1}}^{i_{1}}=\ressp_{n_{2}}^{j_{2}}$.
\item The posets~$\funsp,\ressp$ are the products of the unconnected components.
For a node~$n$, let~$\unconnectedfun(n)$ and~$\unconnectedres(n)$
be the set of unconnected functionalities and resources. Then~$\funsp$
and~$\ressp$ are defined as follows:
\[
\begin{array}{ccc}
\funsp & ={\displaystyle \prod_{n\in\mathcal{N}}\prod_{i\in\unconnectedfun(n)}}\funsp_{n}^{i},\qquad & \qquad\ressp={\displaystyle \prod_{n\in\mathcal{N}}\prod_{j\in\unconnectedres(n)}}\ressp_{n}^{i}.\end{array}
\]
\end{itemize}
\end{definition}

\begin{center}
\begin{figure}

\includegraphics[scale=0.33]{reits2_graph}
\par
\caption{\label{fig:mcdps}}
\end{figure}
\par\end{center}

\subsubsection{Compositionality and abstraction}

It can be shown~\cite{censi16codesign} that the property of monotonicity
is preserved by arbitrary interconnection, which means that there
exists a monotone function~$\ftor$ for the entire MCDP that is equivalent
to the interconnection of the simple DPs~(\prettyref{fig:mcdps},
right).

\subsubsection{Solution of MCDPs}



The function~$\ftor$ for the entire MCDP can be written as the solution
of a least-fixed-point recursive equation involving the functions~$\{\ftor_{n},\ n\in\mathcal{N}\}$.
Therefore, given a systematic procedure to solve the single DPs, in
the sense of being able to evaluate~$\ftor_{n}$ point-wise, there
exists a systematic procedure to solve the larger MCDP.



\subsection{Some related work}

Modern engineering has long since recognized the two ideas of modularity
and hierarchical decomposition, yet there is no general quantitative
theory of design that is applied to different domains. Most of the
works in the theory of design literature study abstractions that are
meant to be useful for a human designer, rather than an automated
system. For example, a \emph{function structure }diagram~\cite[p. 32]{pahl07}
decomposes the function of a system in subsystems that exchange energy,
materials, and signals~(\prettyref{fig:thatbook}). Design approaches
such as Suh's theory of \emph{axiomatic design~}\cite{suh01} provide
quantitative formalization but are limited to linear or linearized
models, and cannot deal with recursive constraints.

\begin{figure}[H]
\subfloat[\emph{Function structure diagram} from~\cite{pahl07}\label{fig:thatbook}]{\includegraphics[scale=0.33]{reits2_other_intro}}
\subfloat[Hierarchical decomposition of a watch's "form" and "function"~\cite{sussman80constraints}]{\includegraphics[scale=0.33]{reits2_steele}}
\caption{}
\end{figure}

Researchers in Optimization study much more general constraints systems
than those expressible as an MCDP~\cite{dechter03}, at the cost
of having fewer guarantees, and not having a clear compositional property.

In Computer Science, researchers have proposed models of computations
based on constraint satisfaction, such as \emph{Prolog, }or constraint
propagation~\cite{steele80definition}. Compared to these, there
are two distinct features of MCDPs: (1)~the semantics accommodates
multiple options for any quantity (the valuation of an edge is an
antichain of values, rather than a single value); (2)~inference can
accommodate arbitrary topologies of the graph of relations, including
cycles. On the other hand, the class of monotone relations is much
smaller than the set of all relations that more general-purpose constraint-based
systems can represent.





\subsection{Examples of MCDPs}

\begin{example}
(Energetics of Mars rover) The Mars Science Laboratory uses a RITEG~(Radioisotope
Thermoelectric Generator) to generate electric power. In a RITEG,
the decay of a Plutonium 238 pellet produces heat. The heat is converted
into electric power by a thermocouple. In the MCDP representation~(\prettyref{fig:rover_energetics}),
the \F{heat &#91;W&#93;} produced is the pellet's functionality. For
the thermocouple, the \R{heat} is a resource, and the \F{electric
power &#91;W&#93;} is the functionality. There is a monotone relation
between the amount of plutonium and the generated power.

When does one get a plutonium pellet? You ask the Department of Energy~\cite{nasa15radioisotope},
and the amount you will receive is a monotonic function of the scientific
value of the mission you propose.
\end{example}

\begin{center}
\begin{figure}[H]

\includegraphics[scale=0.33]{reits2_rover_energetics}
\par
\caption{\label{fig:rover_energetics}}
\end{figure}
\par\end{center}
\begin{example}
(LQG, continued from Example~\ref{exa:lqg}) Suppose that the observations~$\boldsymbol{y}$
are provided by a camera. A lower bound on the information matrix~$\colR\M{W}^{-1}$
induces a constraint on \R{the sensor resolution~$\rho$ &#91;pixels/deg&#93;}~(\prettyref{fig:lqg2}).
Assuming independent sensor elements, then the relation between~$\rho$
and~$\M{W}^{-1}$ is linear: ${\colR\rho}\geq c\ \colF\M{W}^{-1}$.
The \R{resource \emph{sensor resolution}} then induces a constraint
on the \F{functionality \emph{sensor resolution}} provided by the
sensor, as well as the amount of computation required.
\end{example}

\begin{center}
\begin{figure}

\includegraphics[scale=0.33]{reits2_lqg2}
\par
\caption{\label{fig:lqg2}}
\end{figure}
\par\end{center}
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
\text{battery capacity} & \geq\text{endurance}\times\text{total power},\\
\text{total power} & =\text{extra power}+\text{actuation power},\\
\text{lift} & \geq(\text{battery mass}+\text{actuator mass})\times\text{gravity}.
\end{align*}
The constraints create one loop in the graph~(\prettyref{fig:actuation_energetics}).
For the purpose of counting loops, consider the edges with the \F{functionality}$\rightarrow$\R{resource}
orientation. This implies that the choices of battery and actuator
are not independent.
\end{example}

\begin{center}
\begin{figure}[H]

\includegraphics[scale=0.33]{reits2_actuation_energetics}
\par
\caption{\label{fig:actuation_energetics}}
\end{figure}
\par\end{center}

Because monotonicity is preserved by composition, it is immediate
to conclude qualitative results such as "increasing the \F{endurance}
increases the \R{cost} of the solution" by simple visual inspection
of the diagram.
\begin{example}
It is easy (and fun!\textemdash for some) to arrange simple DPs into
complex MCDPs. The graphs quickly become too complex to be legible.
For example, \prettyref{fig:drone_complete} shows the MCDP corresponding
to a UAV, obtained by composing the actuation/energetics constraint.
The entire UAV is abstracted as a DP between high-level functionality
(\F{travel distance}, \F{payload}, \F{number of missions}),
and one resource (\R{total cost of ownership &#91;\$&#93;}). This MCDP
was defined using MCDP\textbf{L}, a domain-specific language to describe
MCDPs. See \url{http://mcdp.mit.edu/wafr.html} for a detailed walkthrough
of this example.
\end{example}

\begin{center}
\begin{figure}[H]

\includegraphics[scale=0.33]{reits2_drone_complete}
\par
\caption{\label{fig:drone_complete}}
\end{figure}
\par\end{center}
\begin{example}
(Customer preferences) MCDPs can also be used to describe customer
preferences. From the point of view of the customer, the role of functionality
and resources is dual with respect to the point of view of the engineer~(\prettyref{fig:customer}).
The engineering problem is: "Given a certain functionality to be
implemented, what are the minimal resources necessary to implement
it?". The customer preferences can be encoded by the answer to the
dual question: "Given the resources (\$) to be provided by the customer,
what is the minimal functionality required?". A feasible solution
to such an MCDP with a "customer in the loop" is a solution that
is feasible both from the engineering point of view, as well as from
the business point of view.
\end{example}

\begin{center}
\begin{figure}[H]

\includegraphics[scale=0.33]{reits2_customer}
\par
\caption{\label{fig:customer}}
\end{figure}
\par\end{center}






\section{Conclusions and future work}

This paper has shown that many design problems in robotics can be
described as Monotone Co-Design Problems (MCDPs), that is, as graphs
of monotone relations between functionality and resources. The monotonicity
is a compositional property, in the sense that it is preserved by
any arbitrary interconnection. Therefore, simpler problems can be
glued together to describe more complex design problems. This work
is a necessary first step towards creating an "automated roboticist"
that can synthesize an optimal design for a robot given the definition
of a task.

Current work includes the definition of a domain-specific language
in which to describe design problems in a computable form. A prototype
of language, interpreter and solver is available at \url{http://mcdp.mit.edu/}.



\printbibliography
