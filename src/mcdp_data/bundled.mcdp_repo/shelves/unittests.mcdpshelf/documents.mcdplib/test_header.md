
Citing them in order:

* <a href="#sec:sA"/> (should be: sA)
* no label:
  
  <ul>
  <li> child</li>
  <li> child: <a href="#sub:child_second"/> (should be 2.2)</li>
  </ul>

* <a href="#sec:sB"/> (should be: sB)
* sC
  
  <ul>
  <li>no</li>
  <li> <a href="#sub:sC_child"/></li>
  </ul>

* <a href="#sub:sssF"/> (should be: sssF)

# Part 1    {#part:1}

\section{sA \label{sec:sA} (should be 1)} 
\section{second bu without label (should be 2)}
\subsection{child of second (should be 2.1)} 
\subsection{child of second \label{sub:child_second} (should be 2.2)}
\subsubsection{child of child of sA}

\section{sB \label{sec:sB}}

\section*{sB-not numbered}

\subsection{child of sB - this will be 3.0 however it's a bug - no numbered inside nn}

# Part 2    {#part:2}

\section{sC (should be Section 4)}

\subsection{ssC \label{sub:sC_child} (should be Subsection 4.1)}
\subsection{ssD (should be Subsection 4.2)}


\subsubsection{sssF \label{sub:sssF} should be 4.2-A}
\subsubsection*{sssG unnumbered}
\subsubsection{sssF2 \label{sub:sssF2} should be 4.2-B}



\subsection*{ssE unnumbered}


<style>
h1 {page-break-before: avoid !important;}

h1 { text-align: left !important; }
h2 { margin-left: 3em !important; }
h3 { margin-left: 6em !important; }
</style>