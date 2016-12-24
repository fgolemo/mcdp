
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

<pre class="mcdp_statements">
    required power ≽ p0 + p1 * l + p2 * l^2
</pre>

This is really the composition of five DPs,
correponding to sum, multiplaction, and exponentiation ([](#fig:Actuation1)).

<render class='ndp_graph_enclosed' style='max-width: 100%'
figure-id="fig:Actuation1"> `Actuation1</render>

The primitive DPs are shown in [](#fig:primitive).

<col3>

$\fun_1 + \fun_2 \posleq \res$

$\fun \posleq \res_1 + \res_2$

$\max(\fun_1, \fun_2) \posleq \res$

<span>\xxx</span>

<span>\xxx</span>

<span>\xxx</span>

</col3>


Let us combine these two together.

The syntax to re-use previously defined MCDPs is:

    instance `Name

The backtick means "load the symbols from the library, from the file `name.mcdp`".

The following creates two sub-design problems, for now unconnected.

<col2 id='combined1-around'>
    <pre class="mcdp" id='combined1'>
    mcdp {
        actuation = instance `Actuation1
        battery = instance `Battery
    }
    </pre>
    <render class='ndp_graph_enclosed'>`combined1</render>
</col2>

<style type='text/css'>
#combined1-around td {
    vertical-align: c;
}
</style>

We can create a complete model with a loop by describing the co-design
constraint.


<pre class="mcdp" id='combined2'>
mcdp {
    actuation = instance `Actuation1
    battery = instance `Battery

    # battery must provide power for actuation
    provides endurance [s]
    energy = provided endurance *
        (power required by actuation)

    capacity provided by battery ≽ energy
}
</pre>

<pre class='ndp_graph_enclosed' style='max-width: 100%'>`combined2</pre>

We can create a model with a loop by introducing another constraint.

Take <f>extra_payload</f> to represent the user payload that we must carry.

Then the lift provided by the actuator must be at least the mass
of the battery plus the mass of the payload times gravity:

<col2 id='mine'>
<pre class="mcdp" id='composition' label='Composition.mcdp'
    figure-id="code:composition">
mcdp {
    actuation = instance `Actuation1
    battery = instance `Battery

    # battery must provide power for actuation
    provides endurance [s]
    energy = provided endurance *
        (power required by actuation)

    capacity provided by battery ≽ energy

    # actuation must carry payload + battery
    provides payload [g]
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
        <pre class='ndp_graph_enclosed_TB' style='max-height: 70ex'>
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
