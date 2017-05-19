<!--

<table>
<tr>
<td>Production server (EU)</td>
<td><a href="https://circleci.com/gh/AndreaCensi/mcdp/tree/inst00"><img src="https://circleci.com/gh/AndreaCensi/mcdp/tree/inst00.png?style=shield&amp;circle-token=f59172bb200232cffc45e43473c4eaf5c2b3e776"/></a>
</td>
</tr>
<tr>
<td>Master</td>
<td><a href="https://circleci.com/gh/AndreaCensi/mcdp/tree/master"><img src="https://circleci.com/gh/AndreaCensi/mcdp/tree/master.png?style=shield&amp;circle-token=f59172bb200232cffc45e43473c4eaf5c2b3e776"/></a>
</td>
</tr>
<tr>
<td>Development</td>
<td><a href="https://circleci.com/gh/AndreaCensi/mcdp/tree/devel"><img src="https://circleci.com/gh/AndreaCensi/mcdp/tree/devel.png?style=shield&amp;circle-token=f59172bb200232cffc45e43473c4eaf5c2b3e776"/></a>
</td>
</tr>
<tr>
<td>Daily</td>
<td><a href="https://circleci.com/gh/AndreaCensi/mcdp/tree/last"><img src="https://circleci.com/gh/AndreaCensi/mcdp/tree/last.png?style=shield&amp;circle-token=f59172bb200232cffc45e43473c4eaf5c2b3e776"/></a>
</td>
</tr>
</table> -->


**PyMCDP** is a Python interpreter and solver for Monotone Co-Design Problems.

Please see the website <http://co-design.science> and in particular [the manual (PDF)][manual], which contains up-to-date installation instructions.

[manual]: https://andreacensi.github.io/mcdp-manual/mcdp-manual.pdf

<!--
*Below, an example of a graphical representation of an MCDP (left)
along with the MCDPL snippet that describes it (right)*

<table>
 <tr>
 <td><img src="web/co-design.science/media/battery-out_expected3/battery_minimal-ndp_greenredsym.png" width="400px"/></td>
 <td><img src="web/co-design.science/media/battery-out_expected3/battery_minimal-syntax_pdf.png" width="300px"/>
 </td>
 </tr>
</table>


## Installation

The code has been tested on Ubuntu 14.04, Ubuntu 16.04, and OS X using Enthought Python distribution.


### Installing dependencies

On Ubuntu:

    $ sudo apt-get install python-numpy python-matplotlib python-yaml python-pip python-dev python-setproctitle python-psutil graphviz wkhtmltopdf git

For math support:

    $ sudo apt-get install nodejs npm
    $ sudo npm install MathJax-node jsdom

For printing to PDF, install Prince from https://www.princexml.com/download/.


### Option 1: Install using pip

Run this command:

    $ sudo pip install -U PyMCDP conftools quickapp decentlogs systemcmd

Note that if you omit the ``sudo``, modern Ubuntu 16 will install
correctly in the directory ``~/.local/``. In this case,
make sure you have ``~/.local/bin/`` in your ``PATH``.

### Option 2: Installation from source (preferred)

Clone the repo using:

    $ git clone https://github.com/AndreaCensi/mcdp.git

Jump into the directory:

	$ cd mcdp

Then install the main module:

    $ sudo python setup.py develop

Omit the sudo if you have already set up a virtual environment.


## wkhtmltopdf

If you get an error like "cannot connect to X server", try  [this solution](http://stackoverflow.com/a/34947479/334788).

## Getting started


#### Running the web interface

Run the command:

    $ mcdp-web

Then point your browser to the address <http://127.0.0.1:8080/>.


#### Solving Monotone Co-Design Problems

The program ``mcdp-solve`` is a solver.

    $ mcdp-solve -d <library> <model_name>  <functionality>

For example, to solve the MCDP specified in the file ``battery.mcdp`` in
the library ``src/mcdp_data/libraries/examples/example-battery.mcdplib``, use:

    $ mcdp-solve -d src/mcdp_data/libraries/examples/example-battery.mcdplib battery "<1 hour, 0.1 kg, 1 W>"

The expected output is:

    ...
    Minimal resources needed: mass = ↑{0.039404 kg}

This is the case of unreasonable demands (1 kg of extra payload):

    $ mcdp-solve -d src/mcdp_data/libraries/examples/example-battery.mcdplib battery "<1 hour, 1.0 kg, 1 W>"

This is the expected output:

    Minimal resources needed: mass = ↑{+∞ kg}

#### Visualization of Co-Design Problems

The programs ``mcdp-plot`` will parse and plot the MCDP in a variety of representations.

    $ mcdp-plot  -d <library> <model name>

For example, the command

    $ mcdp-plot  -d src/mcdp_data/libraries/examples/example-battery.mcdplib battery

will produce these graphs:

<table>
    <tr>
        <td>Syntax highlighting</td>
        <td><a href="web/co-design.science/media/battery-out_expected3/battery-syntax_pdf.png">
            <img src="web/co-design.science/media/battery-out_expected3/battery-syntax_pdf.png" height="500px"/>
            </a>
        </td>
    </tr>
    <tr><td>Verbose graph</td><td><a href="web/co-design.science/media/battery-out_expected3/battery-ndp_graph_enclosed_LR.png"><img src="web/co-design.science/media/battery-out_expected3/battery-ndp_graph_enclosed_LR.png"/></a></td></tr>
    <tr><td>Tree representation</td><td><img src="web/co-design.science/media/battery-out_expected3/battery-dp_graph_tree.png"/></td></tr>
    </tr>
</table>


<h2>Visualization of the solution</h2>

To solve an MCDP, one constructs a chain of antichains in the product poset of resources.

The animations below show the sequence of antichains being
constructed to solve two variations of the same problem.

(Whether the problem statement describes an MCDP is
absolutely not obvious using the formula representation;  it becomes obvious when writing the problem as a graph
of monotone problems.)

<table>
    <tr><td colspan="2">
        <img src="web/co-design.science/media/animations/model.png" width="500px"/>
    </td></tr>
    <tr>
     <td><img src="web/co-design.science/media/animations/plusinvnat2-nat4-problem.png" width="300px"/></td>
     <td><img src="web/co-design.science/media/animations/plusinvnat2-nat10-problem.png" width="300px"/>
     </td>
     </tr>
     <tr>
     <td><img src="web/co-design.science/media/animations/plusinvnat2-nat4.gif" width="300px"/></td>
     <td><img src="web/co-design.science/media/animations/plusinvnat2-nat10.gif" width="300px"/></td>
     </tr>
     <tr>
     <td colspan="2"><img src="web/co-design.science/media/animations/legend.png" width="500px"/></td>
     </tr>
</table>

<h2>More information</h2>

For more information, please see <http://co-design.science>. -->
