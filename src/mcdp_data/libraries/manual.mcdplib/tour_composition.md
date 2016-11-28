
## Composing MCDPs

Suppose we define a simple model called ``Battery`` as follows:

<table>
<tr><td >
<pre class="mcdp" id='Battery' label='Battery.mcdp'>
mcdp {
    provides capacity [J]
    requires mass [g]
    specific_energy = 100 kWh / kg
    required mass >= provided capacity / 
                     specific_energy
}
</pre>
</td>
<td>
<pre class='ndp_graph_templatized_labeled' direction='LR' >`Battery</pre>
</td>
</tr>
</table>

Let's also define the MCDP ``Actuation1``:

<table>
<tr><td >
<pre class="mcdp" id='Actuation1' label='Actuation1.mcdp'>
mcdp {
    provides lift [N]
    requires power [W]

    l = provided lift
    p0 = 5 W
    p1 = 6 W/N
    p2 = 7 W/N^2
    required power >= p0 + p1 * l + p2 * l^2
}
</pre>
</td>
<td>
<pre class='ndp_graph_templatized_labeled' direction='LR'>`Actuation1</pre>
</td>
</tr>
</table>

<pre class='ndp_graph_enclosed' direction='LR'>`Actuation1</pre>


Then we can combine these two together.

We can re-use previously defined MCDPs using the
syntax ``instance `Name``. The backtick means "load symbols from the library".

The following creates two sub-design problems, for now unconnected.

<table>
<tr>
<td>
<pre class="mcdp" id='combined1'>
mcdp {
    actuation = instance `Actuation1
    battery = instance `Battery
}
</pre>
</td>
<td>
<pre class='ndp_graph_enclosed' direction='LR'>`combined1</pre>
</td>
</tr>
</table>
To create a complete MCDP, take "endurance" as a high-level
functionality. Then the energy required is equal to
endurance &times; power.

<pre class="mcdp" id='combined2'>
mcdp {
    actuation = instance `Actuation1
    battery = instance `Battery

    # battery must provide power for actuation
    provides endurance [s]
    energy = provided endurance * 
        (power required by actuation)

    capacity provided by battery >= energy
}
</pre>

<pre class='ndp_graph_enclosed' direction='LR' >`combined2</pre>

We can create a model with a loop by introducing another constraint.

Take ``extra_payload`` to represent the user payload that we must carry.

Then the lift provided by the actuator must be at least the mass
of the battery plus the mass of the payload times gravity:

<table>
<tr>
<td>
<pre class="mcdp" id='composition' label='Composition.mcdp'>
mcdp {
    actuation = instance `Actuation1
    battery = instance `Battery

    # battery must provide power for actuation
    provides endurance [s]
    energy = provided endurance * 
        (power required by actuation)

    capacity provided by battery >= energy

    # actuation must carry payload + battery
    provides payload [g]
    gravity = 9.81 m/s^2
    total_mass = (mass required by battery 
                         + provided payload)

    weight = total_mass * gravity
    lift provided by actuation >= weight

    # minimize total mass
    requires mass [g]
    required mass >= total_mass
}
</pre>
</td>
    <td style='vertical-align: top'>
        <pre class='ndp_graph_enclosed' style='max-height: 90ch' direction='TB'>
            `Composition
        </pre>
    </td>
</tr>
</table>



<style type='text/css'>
    td {
        vertical-align: top;
    }
    td:first-child {
        /*border: solid 1px red; */
        /*width: 25em; */
    }
</style>
