

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

And now I can refer to \eqref{mass} and \eqref{cost}.