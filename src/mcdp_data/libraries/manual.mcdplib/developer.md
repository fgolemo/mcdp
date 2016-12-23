# Developer notes

## Extending PyMCDP


### Defining new posets

A new poset can be added by using:

    code myimplementation

And this is the interface that must be implemented:

    class MyPoset:

    def belongs(x):


    def leq(self, a,b)

    def join(self, a, b):

    def minimal_elements(self):

    def maximal_elements(self):


## Library API

## Running unit tests

Use:

    $ make clean comptests-run-parallel-nocontracts

It takes about 40 minutes to run all the tests.


### Using LaTeX


The basic relation is $\res \geq \ftor(\fun)$.


Simple test to show MathJax is working: $x = y^2 + \sin(\int_a^b D x)$.

$$\begin{eqnarray}
y &=& x^4 + 4      \nonumber \\
  &=& (x^2+2)^2 -4x^2 \nonumber \\
  &\le&(x^2+2)^2    \nonumber
\end{eqnarray}$$


Define this:

$$a := x^2-y^3 \tag{eq}\label{eq}$$

Refer to it as in \eqref{eq}.

Also:

$$ a+y^3 \stackrel{\eqref{eq}}= x^2 $$
