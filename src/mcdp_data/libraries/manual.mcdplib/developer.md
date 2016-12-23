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
