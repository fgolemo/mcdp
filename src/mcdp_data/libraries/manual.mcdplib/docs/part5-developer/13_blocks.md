%% LyX 2.2.0 created this file.  For more info, see http://www.lyx.org/.
%% Do not edit unless you really know what you are doing.
\documentclass[twocolumn,english,draft]{IEEEtran}
\usepackage[T1]{fontenc}
\usepackage{amsmath}
\usepackage{stmaryrd}

\makeatletter

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% LyX specific LaTeX commands.
%% Because html converters don't know tabularnewline
\providecommand{\tabularnewline}{\\}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% User specified LaTeX commands.

\input{tex/preamble.tex}

\makeatother

\usepackage{babel}
\begin{document}

\subsection{The four conjuctions}

\begin{figure*}
\noindent\begin{minipage}[t]{1\columnwidth}%
\begin{center}
\begin{tabular}{cc|cc}
JoinN  &  &  & MeetN\tabularnewline
$(\fun_{1}\posleq\res)\text{ and }\cdots\text{ and }(\fun_{n}\posleq\res)$ &  &  & $(\fun_{1}\posleq\res)\text{ or }\cdots\text{ or }(\fun_{n}\posleq\res)$\tabularnewline
$\max(\fun_{1},\dots,\fun_{n})\posleq\res$ &  &  & $\min(\fun_{1},\dots,\fun_{n})\posleq\res$\tabularnewline
\begin{minipage}[t]{5cm}%
\[
\langle\fun_{1},\dots,\fun_{n}\rangle\mapsto\{\max(\fun_{1},\dots,\fun_{n})\}
\]
\[
\{\langle\res,\dots,\res\rangle\}\mapsfrom\res
\]
%
\end{minipage} &  &  & %
\begin{minipage}[t]{5cm}%
\[
\langle\fun_{1},\dots\fun_{n}\rangle\mapsto\{\min(\fun_{1},\dots,\fun_{n})\}
\]
\[
\{\langle\res,\top,\dots\rangle,\langle\top,\res,\top,\dots\rangle\dots\}\mapsfrom\res
\]
%
\end{minipage}\tabularnewline
 &  &  & \tabularnewline
\hline 
 &  &  & \tabularnewline
MeetNDual &  &  & JoinNDual \tabularnewline
$\fun\posleq\min(\res_{1},\dots,\res_{n})$ &  &  & $\fun\posleq\max(\res_{1},\dots,\res_{n})$\tabularnewline
$(\fun\posleq\res_{1})\text{ and }\cdots\text{ and }(\fun\posleq\res_{n})$ &  &  & $(\fun\posleq\res_{1})\text{ or }\cdots\text{ or }(\fun\posleq\res_{n})$\tabularnewline
\begin{minipage}[t]{5cm}%
\[
\fun\mapsto\{\langle\fun,\dots,\fun\rangle\}
\]
\[
\{\min(\res_{1},\dots,\res_{n})\}\mapsfrom\langle\res_{1},\dots,\res_{n}\rangle
\]
%
\end{minipage} &  &  & %
\begin{minipage}[t]{5cm}%
\[
\fun\mapsto\{\left\langle \fun,\bot,\dots\right\rangle ,\langle\bot,\fun,\bot,\dots\rangle\}.
\]
\[
\{\max(\res_{1},\dots,\res_{n})\}\mapsfrom\langle\res_{1},\dots,\res_{n}\rangle
\]
%
\end{minipage}\tabularnewline
\end{tabular}
\par\end{center}%
\end{minipage}

\caption{}
\end{figure*}

\begin{figure*}
\noindent\begin{minipage}[t]{1\columnwidth}%
\begin{center}
\begin{tabular}{cc|cc}
$\res+c\geq\fun$ &  &  & $\res\geq\fun+c$\tabularnewline
 &  &  & \tabularnewline
$c\neq\top$ &  &  & $c\neq\top$\tabularnewline
\begin{minipage}[t]{5cm}%
\[
\ftor:\fun\mapsto\begin{cases}
\{0\} & \fun<c\\
\{\fun-c\} & \fun\geq c
\end{cases}
\]
\[
\rtof:\res\mapsto\{\res+c\}
\]
%
\end{minipage} &  &  & %
\begin{minipage}[t]{5cm}%
\[
\ftor:\fun\mapsto\{\fun+c\}
\]

\[
\rtof:\res\mapsto\begin{cases}
\emptyset & \res<c\\
\{\res-c\} & \res\geq c
\end{cases}
\]
%
\end{minipage}\tabularnewline
$c=\top$ &  &  & $c=\top$\tabularnewline
\hline 
$\res+\top\geq\fun$ &  &  & $\res\geq\fun+\top$\tabularnewline
 &  &  & \tabularnewline
\begin{minipage}[t]{5cm}%
\[
\ftor:\fun\mapsto\{0\}
\]
\[
\rtof:\res\mapsto\{\top\}
\]
%
\end{minipage} &  &  & %
\begin{minipage}[t]{5cm}%
\[
\ftor:\fun\mapsto\{\top\}
\]
\[
\rtof:\res\mapsto\begin{cases}
\emptyset & \res<\top\\
\{\top\} & \res=\top
\end{cases}
\]
%
\end{minipage}\tabularnewline
$\res+c\geq\fun$ &  &  & $\res\geq\fun+c$\tabularnewline
\hline 
\multicolumn{1}{|c}{} &  &  & \multicolumn{1}{c|}{}\tabularnewline
\multicolumn{1}{|c}{} &  &  & \multicolumn{1}{c|}{}\tabularnewline
\multicolumn{1}{|c}{\textbf{MinusValue{*}DP}} &  &  & \multicolumn{1}{c|}{\textbf{PlusValue{*}DP}}\tabularnewline
\multicolumn{1}{|c}{MinusValue{*}Map} &  &  & \multicolumn{1}{c|}{PlusValue{*}Map}\tabularnewline
\multicolumn{1}{|c}{%
\begin{minipage}[t]{8cm}%
\[
\ftor:\fun\mapsto\begin{cases}
\{0\}, & \text{if }c=\top,\\
\left(\begin{cases}
\{0\} & \fun<c\\
\{\fun-c\} & \fun\geq c
\end{cases}\right), & \text{if }c<\top.
\end{cases}
\]
%
\end{minipage}} &  &  & \multicolumn{1}{c|}{%
\begin{minipage}[t]{8cm}%
\[
\ftor:\fun\mapsto\{\fun+c\},
\]
%
\end{minipage}}\tabularnewline
\hline 
\multicolumn{1}{|c}{(Same as PlusValue{*}Map)} &  &  & \multicolumn{1}{c|}{PlusValueDual{*}Map}\tabularnewline
\begin{minipage}[t]{8cm}%
\[
\rtof:\res\mapsto\{\res+c\}
\]
%
\end{minipage} &  &  & %
\begin{minipage}[t]{8cm}%
\[
\rtof:\res\mapsto\begin{cases}
\left(\begin{cases}
\emptyset & \res<\top\\
\{\top\} & \res=\top
\end{cases}\right) & \text{if }c=\top,\\
\left(\begin{cases}
\emptyset & \res<c\\
\{\res-c\} & \res\geq c
\end{cases}\right) & \text{if }c<\top.
\end{cases}
\]
%
\end{minipage}\tabularnewline
\end{tabular}
\par\end{center}%
\end{minipage}

\caption{}
\end{figure*}


\subsection{Multvalue}

\begin{figure*}
\noindent\begin{minipage}[t]{1\columnwidth}%
\begin{center}
\begin{tabular}{cc|cc}
$\res\cdot c\geq\fun$ &  &  & $\res\geq\fun\cdot c$\tabularnewline
$c=\top$ &  &  & $c=\top$\tabularnewline
$\res\cdot\top\geq\fun$ &  &  & $\res\geq\fun\cdot\top$\tabularnewline
InvMultValue{*}DP &  &  & MultValue{*}DP\tabularnewline
 &  &  & \tabularnewline
 &  &  & \tabularnewline
InvMultValue{*}Map &  &  & MultValue{*}Map\tabularnewline
\hline 
Lower topology ($0\cdot\top=\top$) &  &  & Upper topology ($0\cdot\top=0$)\tabularnewline
\begin{minipage}[t]{8cm}%
\[
\ftor:\fun\mapsto\begin{cases}
\begin{cases}
\{0\} & \fun=0\\
\top & \fun>0
\end{cases} & c=0\\
\begin{cases}
\{0\} & \fun=\top\\
\begin{cases}
\{\fun/c\} & \text{if }c<\top\\
\{\top\} & \text{if }c=\top
\end{cases} & \fun\neq\top
\end{cases} & c\neq0
\end{cases}
\]
%
\end{minipage} &  &  & $\ftor:\fun\mapsto\{\fun\times_{U}c\}$\tabularnewline
InvMultDualValue{*}Map &  &  & MultValueDual{*}Map\tabularnewline
$\rtof:\res\mapsto\{\res\times_{L}c\}$ &  &  & $\rtof:\res\mapsto\begin{cases}
\res/c & \text{if }c<\top\\
\{0\} & \text{if }c=\top
\end{cases}$\tabularnewline
\begin{minipage}[t]{8cm}%
Suppose $c=\top$: $\res\cdot\top\geq\fun$.

\begin{align*}
\ftor(\mathbf{0}) & =\{\mathbf{\top}\}\\
\rtof(\ftor(0)) & =\{\mathbf{\top}\}
\end{align*}

With $r=0$ we have

\begin{align*}
\rtof(\mathbf{0}) & =\downarrow\{\top\}\\
\ftor(\rtof(0)) & =\{0\}
\end{align*}
\textbf{error above!}

Also:

\begin{align*}
\ftor(\top) & =\{\top\}\\
\rtof(\ftor(\top)) & =\{\top\}
\end{align*}
and

\begin{align*}
\rtof(\top) & =\{\top\}\\
\ftor(\rtof(\top)) & =\{\top\}
\end{align*}
%
\end{minipage} &  &  & %
\begin{minipage}[t]{8cm}%
Suppose $c=\top$:

\begin{align*}
\ftor(0) & =\{0\}\\
\rtof(\ftor(0)) & =\{0\}
\end{align*}
and

\begin{align*}
\rtof(0) & =\{0\}\\
\ftor(\rtof(0)) & =\{0\}
\end{align*}
Also

\begin{align*}
\ftor(\top) & =\{\top\}\\
\rtof(\ftor(\top)) & =\{\top\}
\end{align*}
and

\begin{align*}
\rtof(\top) & =\{\top\}\\
\ftor(\rtof(\top)) & =\{\top\}
\end{align*}
%
\end{minipage}\tabularnewline
\hline 
\multicolumn{1}{|c}{} &  &  & \multicolumn{1}{c|}{}\tabularnewline
\multicolumn{1}{|c}{} &  &  & \multicolumn{1}{c|}{}\tabularnewline
\multicolumn{1}{|c}{} &  &  & \multicolumn{1}{c|}{}\tabularnewline
\multicolumn{1}{|c}{} &  &  & \multicolumn{1}{c|}{}\tabularnewline
\multicolumn{1}{|c}{} &  &  & \multicolumn{1}{c|}{}\tabularnewline
\hline 
\multicolumn{1}{|c}{} &  &  & \multicolumn{1}{c|}{}\tabularnewline
 &  &  & \tabularnewline
\end{tabular}
\par\end{center}%
\end{minipage}

\caption{}
\end{figure*}


\subsection{Multiplication}

\begin{figure*}
\noindent\begin{minipage}[t]{1\columnwidth}%
\begin{center}
\begin{tabular}{cc|cc}
 &  &  & MeetN\tabularnewline
$\fun_{1}\fun_{2}\posleq\res$ &  &  & $\fun\posleq\res_{1}\res_{2}$\tabularnewline
 &  &  & \tabularnewline
\begin{minipage}[t]{5cm}%
%
\end{minipage} &  &  & %
\begin{minipage}[t]{5cm}%
%
\end{minipage}\tabularnewline
 &  &  & $\ftor(\top)=?$\tabularnewline
\hline 
$\rtof(\top)=?$ &  &  & \tabularnewline
 &  &  & \tabularnewline
 &  &  & \tabularnewline
 &  &  & \tabularnewline
 &  &  & \tabularnewline
\end{tabular}
\par\end{center}%
\end{minipage}

\caption{}
\end{figure*}


\subsection{Linear constraints (one direction)}

\[
\res+c\geq\fun,\qquad c\geq0
\]

For $c=\top$:
\begin{align*}
\fun & \mapsto\{0\}\\
\res & \mapsto\{\top\}
\end{align*}

For $c\neq\top$:
\begin{align*}
\fun & \mapsto\{\max(0,\fun-c)\}\\
\res & \mapsto\{\res+c\}
\end{align*}


\subsection{Linear constraints (the other direction)}

\[
\res\geq\fun+c,\ c\geq0
\]

For $c=\top$, we have $\res\geq\fun+\top$. For any $\fun$, this
is equivalent to $\res\geq\top$, so we have:

\begin{align*}
\ftor:\fun & \mapsto\{\top\}\\
\end{align*}

In the other direction, we have that 
\[
\max\{\fun:\res\ge\fun+\top\}=\begin{cases}
\text{none} & \res<\top\\
\top & \res=\top
\end{cases}
\]
 
\[
\rtof:\res\mapsto\begin{cases}
\emptyset & \res<\top\\
\{\top\} & \res=\top
\end{cases}
\]
For $c\neq\top$:
\begin{align*}
\fun & \mapsto\{\max(0,\fun-c)\}\\
\res & \mapsto\begin{cases}
\emptyset & \res<c\\
\{\res-c\} & \res\geq c
\end{cases}
\end{align*}


\subsection{Other operators}

Max 1

\begin{minipage}[t]{5cm}%
\[
\fun\mapsto\{\max(\fun,c)\}
\]
$\res\mapsto\begin{cases}
\{\res\} & \text{if }\res\posleq c\\
\emptyset & \text{otherwise}
\end{cases}$%
\end{minipage}

\subsection{Notes on Natural numbers}

\begin{align*}
\res & \geq\fun^{2}\\
\fun & \leq\text{ceil}(\sqrt{\res})
\end{align*}
Implemented as (promote, sqrt, floor, coerce)

0.1+1.0=1.1 

1.1-1.0=0.10000000000000009

$\res\geq\fun-1.0$

for $\res=0.1$,

$\ftor*:\res\mapsto\res+1.0$

$H*:\res\mapsto\res\oplus repr(1.0)$

$\ftor:\fun\mapsto\fun-1.0$

$H:\fun\mapsto\fun\ominus repr(1.0)$

0.1+1.0=1.1 

1.1-1.0=0.10000000000000009

Now the problem is that $H$ is optimistic?
\end{document}
