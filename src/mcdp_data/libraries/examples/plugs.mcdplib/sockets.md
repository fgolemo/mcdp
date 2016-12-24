## The socket/plugs/converters domain

We are going to model the domain of AC sockets and plugs.


### Sockets

There are many [AC power plugs and sockets][wiki].

[wiki]: https://en.wikipedia.org/wiki/AC_power_plugs_and_sockets

<style type='text/css'>
    table.sockets td { 
        font-style: italic; 
        text-align:center; 
        font-size: smaller;
    }
    table.sockets img {
        width: 5em; 
        margin-top: 0.5em;
    }
</style>

<col5>
    <!--  -->
    <s>Type A<br/><img src='typeA.jpg'/></s>
    <s>Type B<br/><img src='typeB.jpg'/></s>
    <s>Type C<br/><img src='typeC.jpg'/></s>
    <s>Type D<br/><img src='typeD.jpg'/></s>
    <s>Type E<br/><img src='typeE.jpg'/></s>
    <!--  -->
    <s>Type F<br/><img src='typeF.jpg'/></s>
    <s>Type G<br/><img src='typeG.jpg'/></s>
    <s>Type H<br/><img src='typeH.jpg'/></s>
    <s>Type I<br/><img src='typeI.jpg'/></s>
    <s>Type J<br/><img src='typeJ.jpg'/></s>
    <!--  -->
    <s>Type K<br/><img src='typeK.jpg'/></s>
    <s>Type L<br/><img src='typeL.jpg'/></s>
    <s>Type M<br/><img src='typeM.jpg'/></s>
    <s>Type N<br/><img src='typeN.jpg'/></s>
    <s>Type O<br/><img src='typeO.jpg'/></s>
</col5>

Some of them are compatible. For example we can fit
a plug ot Type A into a socket of Type B. This
creates a natural partial order structure.

We can use a ``poset`` to describe the poset [](#fig:socket_type):

<pre class='mcdp_poset' id='socket_type' label='socket_type.mcdp_poset'></pre>

<render class='hasse_icons' figure-id='fig:socket_type' 
    figure-caption='The poset of plugs.' style='width: 10em'>
   `socket_type
</render>


### Voltages 

Around the world, the two main voltages are <code class='mcdp_value'>110V</code> and <code class='mcdp_value'>220V</code>.
In this case, we cannot use the usual Volt poset indicated
by <code class='mcdp_poset'>V</code>, because that would mean
that <code class='mcdp_value'>220V</code> is always 
preferable to <code class='mcdp_value'>110V</code>.

Thus we create a discrete poset as follows:

<pre class='mcdp_poset' id='AC_voltages' label='AC_voltages.mcdp_poset'></pre>

### Frequencies

Similarly, we model different frequencies with the poset


<pre class='mcdp_poset' id='AC_frequencies' label='AC_frequencies.mcdp_poset'></pre>


### Power consumption

The function of a socket in the wall is 
to provide power. This function is parameterized (at least) by:

* The socket shape, indicated by <code class='mcdp_poset'>`socket_type</code>

* The voltage, indicated by <code class='mcdp_poset'>`AC_voltages</code>

* The frequency, indicated by <code class='mcdp_poset'>`AC_frequencies</code>

* The maximum power draw, measured in Watts. (Alternatively, this 
could be parameterized by current.)

Therefore, we can create the poset <code class='mcdp_poset'>`AC_power</code> as follows:

<pre class='mcdp_poset' id='AC_power' label='AC_power.mcdp_poset'></pre>

### Modeling a plug adapter


Based on these definitions, we can define the function of 
a socket adapter.

Consider [one of these OREI adapters][orei], which you can buy for $7.31:

<img src='OREI.png' style='width: 10em'/>

[orei]: https://www.amazon.com/OREI-Grounded-Universal-Adapter-Uruguay/dp/B004SY9OVA/

This is an adapter from Type L to either Type C or Type A:

<col3>
    <s>Type L<br/><img src='typeL.jpg'/></s>
    <s>Type A<br/><img src='typeA.jpg'/></s>
    <s>Type C<br/><img src='typeC.jpg'/></s>
</col3>

A plug adapter can be modeled as follows:

<pre class='mcdp' id='orei' label='orei.mcdp'></pre>

<pre class='ndp_graph_templatized'>`orei</pre>
<pre class='ndp_graph_enclosed'>`orei</pre>


### A 2-in-1 adapter


This is another [handy 2-in-1 adapter][another] that 
sells for 6.31:

<img src='orei_2in1.png' style='width: 10em'/>

[another]: https://www.amazon.com/OREI-Grounded-Universal-Adapter-Africa/dp/B005JK61MW/

This one provides 2 outputs:

<pre class='mcdp' id='orei_2in1' label='orei_2in1.mcdp'></pre>

We can forget all this complexity and consider the block:

<div style='text-align: center'>
    <pre class='ndp_graph_templatized'>`orei_2in1</pre>
    <pre class='ndp_graph_enclosed'>`orei_2in1</pre>
</div>


### DC connectors

We can repeat the same story with DC connectors.

<img src='DC_connectors.jpg' 
    style='width: 15em;'/>

<pre class='mcdp_poset' id='barrel_connectors'
    label='barrel_connectors.mcdp_poset'></pre>


### USB connectors
    
<style type='text/css'>
    table#usb img {width: 5em;}
</style>

<col4 figure-id="tab:usb" figure-caption="USB Shapes">
        <s><img src='USB_Micro_A.png'/></s>
        <s><img src='USB_Micro_B.png'/></s>
        <s><img src='USB_Mini_A.png'/></s>
        <s><img src='USB_Mini_B.png'/></s>

        <s><img src='USB_Std_A.png'/></s>
        <s><img src='USB_Std_B.png'/></s>
        <s><img src='USB_Type_C.png'/></s>
</col4>

<pre class='mcdp_poset' id='USB_connectors' label='USB_connectors.mcdp_poset'></pre>

### DC connectors

We can define DC connectors to be the union (co-product)
of the two sets:

<pre class='mcdp_poset' id='DC_connectors' 
     label='DC_connectors.mcdp_poset'></pre>


### DC power

<pre class='mcdp_poset' id='DC_voltages' 
     label='DC_voltages.mcdp_poset'></pre>

<pre class='mcdp_poset' id='DC_power'
     label='DC_power.mcdp_poset'></pre>



### AC-DC converters

[This wall charger][converter] can be used to convert
from AC power to DC power.

<img src='ravpower.png' style='height: 8em'/>
    
[converter]: https://www.amazon.com/RAVPower-Charger-Technology-Foldable-indicator/dp/B00OQ1I2C2/

<pre class='mcdp' id='Ravpower' label='Ravpower.mcdp'></pre>

<div style='text-align: center'>
    <pre class='ndp_graph_templatized'>`Ravpower</pre>
    <pre class='ndp_graph_enclosed'>`Ravpower</pre>
</div>

We can query the model as follows. Suppose we need 2 outputs, each of 0.5A.

<pre class='mcdp_value'>solve(
    ⟨ ⟨ `USB_connectors:USB_Std_A, `DC_voltages: v5, 0.5 A⟩,
      ⟨ `USB_connectors:USB_Std_A, `DC_voltages: v5, 0.5 A⟩ ⟩, 
    `Ravpower)
</pre>

This is the output:

<pre class='print_value'>
    solve(
    ⟨ ⟨ `USB_connectors:USB_Std_A, `DC_voltages: v5, 0.5 A⟩,
      ⟨ `USB_connectors:USB_Std_A, `DC_voltages: v5, 0.5 A⟩ ⟩, 
    `Ravpower)
</pre>

The model says we have two options: we need to find an outlet of ``TypeM``
at either 110 V or 220 V which will provide 5 W of power. Moreover, we need 
at least 10.99 USD to buy the component.


### Composition

This is an example of composition of the <a href="#Ravpower">Ravpower charger</a>
and the <a href="#Orei_2in1">Orei_2in1 adapter</a>. 

<pre class='mcdp' id='orei_plus_ravpower' label='orei_plus_ravpower.mcdp'></pre>

Note the use of the keyword "<code class='keyword'>ignore</code>" to ignore the 
functionality that we do not need.

<pre class='ndp_graph_enclosed'>`orei_plus_ravpower</pre>

We can ask now for what resources we would need for a 0.5 A load:

<pre class='mcdp_value'>
    solve(
    ⟨ `USB_connectors:USB_Std_A, `DC_voltages: v5, 0.5 A⟩,
    `orei_plus_ravpower)
</pre>

and obtain

<pre class='print_value'>
    solve(
    ⟨ `USB_connectors:USB_Std_A, `DC_voltages: v5, 0.5 A⟩,

    `orei_plus_ravpower)
</pre>


