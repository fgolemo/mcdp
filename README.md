
**PyMCDP** is a Python interpreter and solver for Monotone Co-Design Problems.
It is currently in beta-testing. Please email censi@mit.edu if you wish to help.

Please see <http://mcdp.mit.edu> for the theory behind it.


*Below, an example of a graphical representation of an MCDP (left)
along with the MCDPL snippet that describes it (right)*

<img src="http://mcdp.mit.edu/mcdp_intro/1510_mcdp_examples01_battery_actuation.png"/>

## Installation

If you install from source, first install the dependencies:

    pip install -r requirements.txt

The dependencies are: ...

Then install the main module:
    
    python setup.py develop

If you install from repos

    pip install -U PyMCDP 

## Getting started

There are a few ``*.mcdp`` files scattered around the repository.

#### Drawing diagrams 

The programs ``mcdp-plot`` will parse and plot the MCDP in a variety of representations.

    $ mcdp-plot <filename>.mcdp

#### Solving diagrams
    
The program ``mcdp-solve`` is a solver.

    $ mcdp-solve <filename>.mcdp <f1> <f2> ...
    
For example,

    $ mcdp-solve example-battery/battery.mcdp "1 hour" "1 kg" "1 W"




