A servo motor like the [Traxxas 2075 Digital High-Torque Waterproof Servo][Traxxas_2075]
is a device that provides the <mcdp-poset>load AngularPlacement</mcdp-poset> functionality,
and to do so requires the <mcdp-poset>load PPM</mcdp-poset> resource.



A brushless motor like the [Traxxas 3351][Traxxas_3351]
provides the <mcdp-poset>`ContinuousRotation</mcdp-poset> functionality
and requires the <mcdp-poset>&#96;PWM</mcdp-poset> resource.

## The servo/motors domain

This is a formalization of the domain of servos/DC motors and accessories.

### Continuous rotation

The functionality <mcdp-poset>ContinuousRotation</mcdp-poset> describes
a device that can provided continuous rotation along an axis.

This functionality is parameterized by:

* <f>torque</f>: maximum torque provided;
* <f>velocity</f>: maximum velocity (rad/s).

<pre class='mcdp_poset' id='ContinuousRotation' label='ContinuousRotation.mcdp_poset'></pre>


### Rotation placement

The functionality ``AngularPlacement`` describes what a servo mechanism provides:
precise placement along a rotational axis.

This functionality is parameterized by:

* ``torque``;
* ``span [deg]``: how much it can travel;
* ``transit_time_60deg``: the time it takes for the servo to travel 60 deg;
* ``resolution [deg]``: how precisely it reaches the desired position.


<pre class='mcdp_poset' id='AngularPlacement' label='AngularPlacement.mcdp_poset'></pre>


### PWM and PPM

The two main ways to drive motors are
[Pulse-Width Modulation (PWM)][PWM] and [Pulse-Position Modulation (PPM)][PPM].

<img src='pwm-ppm-signal-example.jpg' style='width: 20em'/>

[PPM]: https://en.wikipedia.org/wiki/Pulse-position_modulation
[PWM]: https://en.wikipedia.org/wiki/Pulse-width_modulation


For PWM, the variables of interest are:

* ``voltage_max``: the maximum voltage;
* ``amp_max``: maximum current that can be provided;
* ``freq_max``: the maximum switching frequency.

<pre class='mcdp_poset' id='PWM' label='PWM.mcdp_poset'></pre>

For PPM, the variables of interest are:

* ``voltage_max``: maximum voltage ;
* ``amp_max``: maximum current;
* ``freq_max``: the maximum frequency;
* ``resolution``: resolution of the generated PPM.

<pre class='mcdp_poset' id='PPM' label='PPM.mcdp_poset'></pre>


### Example: servo motor driven by PPM

Example: <mcdp-poset>`try1</mcdp-poset>

A servo motor like the [Traxxas 2075 Digital High-Torque Waterproof Servo][Traxxas_2075]
is a device that provides the <mcdp-poset>&#96;AngularPlacement</mcdp-poset> functionality,
and to do so requires the <mcdp-poset>&#96;PPM</mcdp-poset> resource.

[Traxxas_2075]: https://www.amazon.com/Traxxas-Digital-High-Torque-Waterproof-Servo/dp/B002PGW31G


<render class='ndp_graph_templatized_labeled'>`Traxxas_2075</render>

<pre class='mcdp' id='Traxxas_2075' label='Traxxas_2075.mcdp'></pre>

### Example: brushless motor driven by PWM


A brushless motor like the [Traxxas 3351][Traxxas_3351]
provides the <mcdp-poset>`ContinuousRotation</mcdp-poset> functionality
and requires the <mcdp-poset>&#96;PWM</mcdp-poset> resource.

[Traxxas_3351]: https://www.amazon.com/Traxxas-3351-Velineon-Brushless-Motor/dp/B000SU3VCG


<render class='ndp_graph_templatized_labeled'>`Traxxas_3351</render>

<pre class='mcdp' id='Traxxas_3351' label='Traxxas_3351.mcdp'></pre>

<!-- See also:
# http://www.ultimaterc.com/forums/showthread.php?t=115618 -->


### Example: Electronic Speed Controller

An electronic speed controller (ESC) like the [VESC][vesc]
can drive servos/motors using PPM/PWM.

[vesc]: http://vedder.se/2015/01/vesc-open-source-esc/

<render class='ndp_graph_templatized_labeled'>`VESC</render>
<pre class='mcdp' id='VESC'></pre>




### Example: Actuation

<pre class='mcdp_poset' id='Motion'></pre>

<pre class='mcdp_poset' id='Payload'></pre>


### Example: Dagu Chassis


Dagu Chassis used for the Duckiebot.

<render class='ndp_graph_templatized_labeled'>`DaguChassis</render>

<pre class='mcdp' id='DaguChassis'></pre>

### The Youbot Base

Youbot base

<render class='ndp_graph_templatized_labeled'>`YoubotBase</render>

<pre class='mcdp' id='YoubotBase'></pre>



### iRobot Create

iRobot Create

<render class='ndp_graph_templatized_labeled'>`IRobotCreate</render>

<pre class='mcdp' id='IRobotCreate'></pre>
