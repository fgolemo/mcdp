
I will use this:

\[
\res\in\ftor(\fun)
\]


\subsubsection*{Model of a battery}

The choice of a battery can be modeled as a DPI (\figref{battery})
with functionalities \F{capacity {[}J{]}} and \F{number of missions}
and with resources \R{mass {[}kg{]}}, \R{cost {[}\${]}} and ``\R{maintenance}'',
defined as the number of times that the battery needs to be replaced
over the lifetime of the robot. 

Each battery technology is described by the three parameters specific
energy, specific cost, and lifetime (number of cycles):
\begin{align*}
\rho & \doteq\text{specific energy [Wh/kg]},\\
\alpha & \doteq\text{specific cost [Wh/\$]},\\
c & \doteq\text{battery lifetime [\# of cycles]}.
\end{align*}
The relation between functionality and resources is described by three
nonlinear monotone constraints: 
\begin{align}
\R{\text{mass}} & \geq\F{\text{capacity}}/\rho,\label{eq:mass}\\
\R{\text{maintenance}} & \geq\left\lceil \F{\text{missions}}/c\right\rceil ,\label{eq:maintenance}\\
\R{\text{cost}} & \geq\left\lceil \F{\text{missions}}/c\right\rceil (\F{\text{capacity}}/\alpha).\label{eq:cost}
\end{align}
Model of a battery

The choice of a battery can be modeled as a DPI (\figref{battery})
with functionalities \F{capacity {[}J{]}} and \F{number of missions}
and with resources \R{mass {[}kg{]}}, \R{cost {[}\${]}} and ``\R{maintenance}'',
defined as the number of times that the battery needs to be replaced
over the lifetime of the robot. 

Each battery technology is described by the three parameters specific
energy, specific cost, and lifetime (number of cycles):
\begin{align*}
\rho & \doteq\text{specific energy [Wh/kg]},\\
\alpha & \doteq\text{specific cost [Wh/\$]},\\
c & \doteq\text{battery lifetime [\# of cycles]}.
\end{align*}
The relation between functionality and resources is described by three
nonlinear monotone constraints: 
\begin{align}
\R{\text{mass}} & \geq\F{\text{capacity}}/\rho,\label{eq:mass-1}\\
\R{\text{maintenance}} & \geq\left\lceil \F{\text{missions}}/c\right\rceil ,\label{eq:maintenance-1}\\
\R{\text{cost}} & \geq\left\lceil \F{\text{missions}}/c\right\rceil (\F{\text{capacity}}/\alpha).\label{eq:cost-1}
\end{align}

