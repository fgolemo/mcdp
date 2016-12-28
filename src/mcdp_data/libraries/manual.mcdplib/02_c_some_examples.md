
## Some examples


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
\end{figure}
