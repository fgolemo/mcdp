## Using templates

"Templates" are a way to describe reusable design patterns.

For example, the code in [](#code:composition) composes
a particular battery model, called <mcdp>Battery</mcdp>,
and a particular actuator model, called <mcdp>`Actuation1</mcdp>.
However, it is clear that the pattern of "interconnect battery
and actuators" is independent of the particular battery and
actuator. MCDPL allows to describe this situation by using the
idea of "template".

Templates are described using the keyword <k>template</k>.
The syntax is:

<pre><code>    <k>template</k> [<span>name1</span><k>:</k> <span> interface1</span>, <span>name2</span><k>:</k> <span> interface2 </span>, &hellip; ]
    <k>mcdp</k> <k>{</k>
    &hellip;
    <k>}</k>
</code></pre>

In the brackets put pairs of name and NDPs that will be used
to specify the interface.
For example, suppose that there is an interface defined in <code>Interface.mcdp</code> as in [](#code:Interface).

<pre class="mcdp" id='Interface' label='Interface.mcdp'
    figure-id="code:Interface">
mcdp {
    provides f [Nat]
    requires r [Nat]
}
</pre>

Then we can declare a template as in [](#code:ExampleTemplate).
The template is visualized as a diagram with a hole ([](#fig:ExampleTemplate)).

<col2>
    <pre class="mcdp_template" id='ExampleTemplate' label='ExampleTemplate.mcdp_template'
        figure-id="code:ExampleTemplate">
    template [
        p: `Interface
      ]
    mcdp {
        x = instance p
        f provided by x &gt;= r required by x + 1
    }
    </pre>
    <render class="template_children_summarized_TB" figure-id="fig:ExampleTemplate">
        `ExampleTemplate
    </render>
</col2>

Later, we can instance it as follows:
<!--
provided f &lt;= 10
required r &gt;= 15 -->

Suppose now that there are two specific batteries,


For example, suppose that we define the following "interfaces":

<col2>
<pre class='mcdp' id='BatteryInterface' label='BatteryInterface.mcdp'>
mcdp {
    provides capacity [kWh]
    requires mass [g]
}
</pre>
<pre class='mcdp' id='ActuationInterface' label='ActuationInterface.mcdp'>
mcdp {
    provides lift [N]
    requires power [W]
}
</pre>
</col2>

Then we can define a template that uses them.
For example the code in [](#code:CompositionTemplate)
specifies that the templates requires two parameters,
called
<code>generic_actuation</code>
and <code>generic_battery</code>,
and they must have the interfaces
defined by <poset>`ActuationInterface</poset>
and <poset>`BatteryInterface</poset>.

<col2>
<pre class="mcdp_template" id='CompositionTemplate'
    label='CompositionTemplate.mcdp'
    figure-id="code:CompositionTemplate">
template [
    actuation: `ActuationInterface,
    battery: `BatteryInterface
  ]
mcdp {
    actuation = instance `Actuation1
    battery = instance battery

    # battery must provide power for actuation
    provides endurance [s]
    energy = provided endurance *
        (power required by actuation)

    capacity provided by battery ≽ energy

    # only partial code
    <!-- # actuation must carry payload + battery
    provides payload [g]
    gravity = 9.81 m/s^2
    total_mass = (mass required by battery
                         + provided payload)

    weight = total_mass * gravity
    lift provided by actuation ≽ weight

    # minimize total mass
    requires mass [g]
    required mass ≽ total_mass -->
}
</pre>


<render class="template_children_summarized_TB" style='max-height: 30em'>
    `CompositionTemplate
</render>
</col2>

TODO: need to change this diagram

We can then obtain the previous model by specializing it ([](#code:specialize)).

<pre class='mcdp' figure-id="code:specialize">
    specialize [
        generic_battery: `Battery,
        generic_actuation: `Actuation1
    ] `CompositionTemplate
</pre>
