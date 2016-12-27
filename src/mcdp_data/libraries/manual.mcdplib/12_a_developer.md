# Developer notes

<div class='section-abstract'>
    These are developer notes for who is interested in extending PyMCDP
    using Python code.
</div>

## Extending PyMCDP

<col2 class='labels-row1'
    figure-id="tab:table-objects"
    figure-caption="Types universe and file extensions">
        <!--  -->
        <s>Type universe </s>
        <s>superclass to use</s>
        <!--  -->
        <s>Posets</s>
        <s><code>mcdp_posets.Poset</code></s>
        <!--  -->
        <s>NDPs</s>
        <s><code>mcdp_posets.???.NamedDP</code></s>
        <!--  -->
        <s>DPs</s>
        <s><code>mcdp_posets.???.PrimitiveDP</code></s>
        <!--  -->
        <s>templates</s>
        <s>(Cannot extend)</s>
        <!--  -->
        <s>Values</s>
        <s><code>object</code></s>
        <!--  -->
</col2>

It is possile to implement one's own extensions by subclassing
one of these classes. In particular, what is easy to do
is creating custom ``Poset``s as well as ``PrimitiveDP``s,
if these cannot be expressed using the operators available.



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
