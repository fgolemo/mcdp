# Installation and quickstart

## Supported platforms

The code has been tested on the following platforms:

* Ubuntu 14.04 and 16.04, using the system Python.
* OS X using the Enthought Python distribution.


#### Windows support

In principle, there is nothing that prevents the software
to run on Windows, however, there are probably lots of subtle
adjustments to be done. Porting contributions are welcome.

#### Python 3 support

PyMCDP works on Python 2.7, not Python 3.
Porting is not difficult, but it is not done yet.


## Installing dependencies

### Installing dependencies on Ubuntu

On Ubuntu:

    $ sudo apt-get install python-numpy python-matplotlib python-yaml python-pip python-dev python-setproctitle python-psutil

    $ sudo apt-get install graphviz wkhtmltopdf
    $ sudo apt-get install git

For math support:

    $ sudo apt-get install nodejs npm
    $ sudo npm install MathJax-node jsdom

For printing to PDF, install Prince from https://www.princexml.com/download/.

### Installing dependencies on OS X

Canopy...

## Installing PyMCDP

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

## Troubleshooting

### ``wkhtmltopdf``

If you get an error like "cannot connect to X server", try  [this solution](http://stackoverflow.com/a/34947479/334788).



## Verifying the installation worked

### Running the web interface

Run the command:

    $ mcdp-web

Then point your browser to the address <http://127.0.0.1:8080/>.

### Running command-line programs

The program ``mcdp-solve`` is a solver.

    $ mcdp-solve -d <library> <model_name> <functionality>

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
