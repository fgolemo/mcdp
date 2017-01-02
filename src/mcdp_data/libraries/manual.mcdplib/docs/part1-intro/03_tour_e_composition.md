
## Composing MCDPs


MCDPL encourages composition and code reuse.


Suppose we define a simple model called ``Battery`` as follows:

<col2>
    <pre class="mcdp" id='Battery' label='Battery.mcdp'></pre>
    <render class='ndp_graph_templatized_labeled'>`Battery</render>
</col2>

Let's also define the MCDP ``Actuation1``, as a
relation from <f>lift</f> to <r>power</r>, as in [](#code:Actuation1).

<col2>
    <pre class="mcdp" id='Actuation1' label='Actuation1.mcdp'
        figure-id="code:Actuation1"></pre>
        <render class='ndp_graph_templatized_labeled'>
            `Actuation1
        </render>
</col2>

The relation between <f>lift</f> and <r>power</r>
is described by the polynomial relation

<center>
<pre class="mcdp_statements">
    required power ≽ p₀ + p₁ * l + p₂ * l^2
</pre>
</center>
<!-- Cannot substitute _0, _1, _2, by itself because no context -->

This is really the composition of five DPs,
correponding to sum, multiplaction, and exponentiation ([](#fig:Actuation1)).

<render class='ndp_graph_enclosed' style='max-width: 100%' figure-id="fig:Actuation1">
    `Actuation1
</render>

Let us combine these two together.

The syntax to re-use previously defined MCDPs is:

<center>
<pre>
<k>instance</k> &#96;Name
</pre>
</center>

The backtick means <q>load the symbols from the library, from the file called `Name.mcdp`</q>.

The following creates two sub-design problems, for now unconnected.

<col2 id='combined1-around'>
    <pre class="mcdp" id='combined1'
        figure-id="code:combined1">
    mcdp {
        actuation = instance &#96;Actuation1
        battery = instance &#96;Battery
    }
    </pre>
    <render class='ndp_graph_enclosed'
        figure-id="fig:combined1">
        &#96;combined1
    </render>
</col2>

<style type='text/css'>
#combined1-around td {
    vertical-align: c;
}
</style>

The model in [](#code:combined1) is not usable yet because some of the edges are
unconnected. We can create a complete model by adding a co-design constraint.

For example, suppose that we know the desired <fname>endurance</fname> for the
design. Then we know that the <f>capacity provided by the battery</f> must
exceed the <r>energy</r> required by actuation, which is the product of power
and endurance. All of this can be expressed directly in MCDPL using the syntax:

<pre class="mcdp_statements">
energy = provided endurance * (power required by actuation)
capacity provided by battery ≽ energy
</pre>

The visualization of the resulting model has a connection between the two design
problems representing the co-design constraint ([](#fig:combined2)).

<center>
    <pre class="mcdp" id='combined2'
         figure-id="code:combined2" figure-class="caption-left">
    mcdp {
        provides endurance [s]
        &#32;
        actuation = instance `Actuation1
        battery = instance `Battery
        &#32;
        # battery must provide power for actuation
        energy = provided endurance * (power required by actuation)
        capacity provided by battery ≽ energy
        # still incomplete...
    }
    </pre>
    <render class='ndp_graph_enclosed' style='max-width: 100%'
        figure-id="fig:combined2">
        &#96;combined2
    </render>
</center>

We can create a model with a loop by introducing another constraint.

Take <f>extra_payload</f> to represent the user payload that we must carry.

Then the lift provided by the actuator must be at least the mass of the battery
plus the mass of the payload times gravity:

<pre class='mcdp_statements'>
gravity = 9.81 m/s^2
total_mass = (mass required by battery
                     + provided payload)
weight = total_mass * gravity
lift provided by actuation ≽ weight
</pre>

Now there is a loop in the co-design diagram ([](#fig:Composition)).

<col2 id='mine' style='float: bottom'>
<pre class="mcdp" id='composition' label='Composition.mcdp'
    figure-id="code:Composition">
mcdp {
    provides endurance [s]
    provides payload [g]

    actuation = instance `Actuation1
    battery = instance `Battery

    # battery must provide power for actuation
    energy = provided endurance *
        (power required by actuation)

    capacity provided by battery ≽ energy

    # actuation must carry payload + battery
    gravity = 9.81 m/s^2
    total_mass = (mass required by battery
                         + provided payload)
    weight = total_mass * gravity
    lift provided by actuation ≽ weight

    # minimize total mass
    requires mass [g]
    required mass ≽ total_mass
}
</pre>
        <pre class='ndp_graph_enclosed_TB' style='max-height: 70ex'
            figure-id='fig:Composition'>
            `Composition
        </pre>
</col2>


<style type='text/css'>
    #mine td {
        vertical-align: top;
    }
    #mine td:first-child {
        /*border: solid 1px red; */
        /*width: 25em; */
    }
</style>

TODO: Add example output
