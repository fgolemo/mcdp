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

## Unit tests


### Running manually

Use:

    $ make clean comptests-run-parallel-nocontracts

It takes about 40 minutes to run all the tests.

### Continuous integration using CircleCI


#### Parallelism

CircleCI supports build parallelism. If more than one container is allocated
to the test (the information provided by `CIRCLE_NODE_INDEX` and `CIRCLE_NODE_TOTAL`),
then container 0/n runs only the core tests,while containers 1...n-1 run only library tests.

### Environment variables

There are several environment variables that affect
which tests are going to be run (#[](tab:test_environment_variables)).

<col3
    figure-id='tab:test_environment_variables'
    figure-caption="Environment variables for unit tests">
    <s>Variable</s> <s>Default</s> <s></s>

    <s>`MCDP_TEST_LIBRARIES`</s> <s>`*`</s>
    <s>Comma-separated list of libraries to include</s>

    <s>`MCDP_TEST_LIBRARIES_EXCLUDE`</s> <s>`(empty)`</s>
    <s>Comma-separated list of libraries to exclude</s>

    <s>`CIRCLE_NODE_TOTAL`</s> <s>`1`</s>
    <s>The total number of test containers.</s>

    <s>`CIRCLE_NODE_INDEX`</s> <s>`0`</s>
    <s>If there are more than 1 test containers, the index
        of the current one</s>

    <s>`MCDP_TEST_SKIP_MCDPOPT`</s> <s>`false`</s>
</col3>
<!-- 
Other useful variables:

* `MPLBACKEND`:  -->
