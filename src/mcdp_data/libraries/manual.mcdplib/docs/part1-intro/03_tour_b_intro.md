

## Graphical representations of design problems

MCDPL allows to define design problems, which are represented as in
[](#fig:complicated): a box with green arrows for functionalities and red arrows
for resources.

<style>
#fig\:complicated {
    td {
        vertical-align: top;
    }
}
</style>
<center>
    <col3 figure-id='fig:complicated'>
        <s><f>Functionalities</f> <br/><br/>
                $\langle\funsp,\funleq\rangle$</s>
        <render class='ndp_graph_templatized' id='complicated'>
        template mcdp {
            provides f_1 [g]
            provides f_2 [J]
            provides f_3 [m]
            requires r_1 [lux]
            requires r_2 [USD]
        }
        </render>
        <s><r>Resources</r><br/><br/>
             $\langle\ressp,\posleq_{\ressp}\rangle$</s>
    </col3>
    <figcaption id='fig:complicated:caption'>
        Representation of a design problem with three functionalities
        (<fname>f_1</fname>, <fname>f_2</fname>, <fname>f_3</fname>)
        and two resources (<rname>r_1</rname>, <rname>r_2</rname>).
        In this case, the functionality
        space $\funsp$ is the product of three copies
        of $\Rcomp$: $\funsp = \Rcpu{g} \times \Rcpu{J} \times \Rcpu{m}$
        and $\ressp = \Rcpu{lux} \times \Rcpu{USD}$.
    </figcaption>
</center>

The graphical representation of a co-design problem
is as a set of design problems that are interconnected
([](#fig:example_diagram)). A functionality and a resource
edge can be joined using a $\posleq$ sign. This is called
a "co-design constraint".

<center>
    <render class='ndp_graph_enclosed'
        figure-id="fig:example_diagram">
    mcdp {
        a = instance template mcdp {
            provides f1 [J]
            requires r1 [m]
            requires r3 [W]
        }
        b = instance template mcdp {
            provides f2 [m]
            provides f3 [kg]
            requires r2 [J]
        }

        provides f3 using b
        requires r3 for a
        f1 provided by a &gt;= r2 required by b
        f2 provided by b &gt;= r1 required by a

    }
    </render>
</center>

<figcaption id='fig:example_diagram:caption'>
    Example of a co-design diagram with
    two design design problems, <dpname>a</dpname>
    and <dpname>b</dpname>.
</figcaption>

## Hello, world!


The "hello world" example of an MCDP is an MCDP that has zero functionalities
and zero resources. This MCDP will be able to tell us that to
do nothing, nothing is needed. While you might have an intuitive understanding
of this fact, you might appreciate having a formal proof.

An MCDP is described in MCDPL using the construct <k>mcdp {…}</k>, as in
[](#code:empty). The body is empty, and that
means that there are no functionality and resources.
Comments in MCDPL work like in Python: everything after
<q>`#`</q> is ignored by the interpreter.

<col2><!-- &#32;&#32;&#32;&#32; -->
    <pre class='mcdp' id='empty' label='empty.mcdp'
         figure-id='code:empty'   figure-class='caption-left'>
    mcdp {
        # an empty MCDP
        # (comments are ignored)
    }
    </pre>
    <render class='fancy_editor' id='empty'
            figure-id="fig:empty" figure-class='caption-left'>
        template `empty
    </render>
</col2>

Formally, the functionality and resources spaces are $\funsp=\One$,
$\ressp=\One$. The space $\One = \{ \langle\rangle \}$ is the empty product
([](#def:One)). $\One$ contains only one element, the empty tuple
$\langle\rangle$.

The MCDP above can be queried using the program
<program>mcdp-solve</program>:

<pre><code>&#36; mcdp-solve empty "&lt;&gt;"</code></pre>

The command above means "for the MCDP <code>empty</code>, find the minimal
resources needed to perform the functionality $f=\langle\rangle$". The command
produces the output:

~~~ .output
Minimal resources needed = ↑{⟨⟩}
~~~

The output means "it is possible to perform the functionality specified,
and the minimal resources needed are $\res^\star=\langle\rangle$".

We have proved that:

1. it is possible to do nothing; and
2. we need nothing to do nothing.


## Defining functionality and resources

The functionality and resources of an MCDP are defined using the keywords
<kf>provides</kf> and <kr>requires</kr>. The code in [](#code:model1) defines an
MCDP with one functionality, <fname>capacity</fname>, measured in joules, and
one resource, <rname>mass</rname>, measured in grams.

<col2>
    <pre class='mcdp' id='model1' figure-id='code:model1'>
    mcdp {
        provides capacity [J]
        requires mass [g]
    }
    </pre>
    <render class='fancy_editor_LR' figure-id="fig:model1">
    `model1
    </render>
</col2>


That is, the functionality space is $\funsp=\overline{\reals}_{+}^{[\text{J}]}$
and the resource space is $\ressp=\overline{\reals}_{+}^{[\text{g}]}$. Here,
let $\overline{\reals}_{+}^{[g]}$ refer to the nonnegative real numbers with
units of grams. (Of course, internally this is represented using floating point
numbers. See [](#subsub:Rcomp) for more details.)

The MCDP defined above is, however, incomplete, because we have not specified
how <fname>capacity</fname> and <rname>mass</rname> relate to one another. In
the graphical notation, the co-design diagram has unconnected arrows
([](#fig:model1)).
<!--
<render class='fancy_editor_LR' figure-id="fig:model1">
    `model1
</render> -->

## Constraining functionality and resources

In the body of the <k>mcdp{&hellip;}</k> declaration one can refer to the values
of the functionality and resources using the expressions <cf>provided
<em>(functionality name)</em></cf> and <cr>required <em>(resource
name)</em></cr>. For example, [](#code:model2) shows the completion of the
previous MCDP, with hard bounds given to both <fname>capacity</fname> and
<rname>mass</rname>.

<center>
    <pre np class='mcdp' id='model2'
         figure-id="code:model2" figure-class='caption-left'>
    mcdp {
        provides capacity [J]
        requires mass [g]
        provided capacity &lt;= 500 J
        required mass &gt;= 100 g
    }
    </pre>
</center>



The visualization of these constraints is as in [](#fig:model2-verbose). Note
that there is always a <q>$\posleq$</q> node between a green and a red
edge.

<render class='fancy_editor_LR'
        figure-id="fig:model2-verbose">
    `model2
</render>

The visualization above is quite verbose. It shows one node for each
functionality and resources; here, a node can be thought of a variable on which
we are optimizing. This is the view shown in the editor; it is
helpful because it shows that while <fname>capacity</fname>
is a functionality from outside the MCDP, from inside
<rname>provided capacity</rname> is a resource.

The less verbose visualization, as in [](#fig:model2-verbose), skips the
visualization of the extra nodes.

<render class='ndp_graph_enclosed'
        figure-id="fig:model2" figure-class='caption-left'>
    `model2
</render>



It is possible to query this minimal example. For example:

    $ mcdp-solve minimal "400 J"

The answer is:

    Minimal resources needed: mass = ↑ {100 g}

If we ask for more than the MCDP can provide:

    $ mcdp-solve minimal "600 J"

we obtain no solutions (the empty set):

    Minimal resources needed: mass = ↑{ }

The notation <q>`↑{ }`</q> means "the upper closure of the empty set
$\emptyset$" ([](#def:upperclosure)), which is equal to $\emptyset$.


## Beyond ASCII - Use of Unicode glyphs in the language

To describe the inequality constraints, MCDPL allows to use <q><k>&lt;=</k></q>,
<q><k>&gt;=</k></q>, as well as their fancy Unicode version <q><k><span
class="leq">≼</span></k></q>, <q><k><span class="geq">≽</span></k></q>. These
two expressions are equivalent:

<center>
    <col2>
        <pre class='mcdp_statements' np>
        provided capacity &lt;= 500 J
        required mass &gt;= 100g
        </pre>
        <pre class='mcdp_statements'>
        provided capacity ≼ 500 J
        required mass ≽ 100g
        </pre>
    </col2>
</center>

MCDPL also allows to use some special letters in identifiers.
These two are equivalent:

<center>
    <col2>
        <pre class='mcdp_statements' noprettify="1">
        alpha_1 = beta^3 + 9.81 m/s^2
        </pre>
        <pre class='mcdp_statements'>
        α₁ = β³ + 9.81 m/s²
        </pre>
    </col2>
</center>

## Aside: an helpful interpreter

The MCDPL interpreter tries to be very helpful.

### Fixing omissions

If it is possible to disambiguate from the context, the MCDPL interpreter also
allows to drop the keywords <cf>provided</cf> and <cr>required</cr>, although it
will give a warning. For example, if one forgets the keyword <cf>provided</cf>,
the interpreter will give the following warning:

<pre>
Please use "provided capacity" rather than just "capacity".

    line  2 |    provides capacity [J]
    line  3 |    requires mass [g]
    line  4 |
    line  5 |    capacity &lt;= 500 J
                 ^^^^^^^^
</pre>

The IDE will actually automatically insert the keyword.

### Catching other problems

All inequalities will always be of the kind:
$$
    {\colF \text{functionality}} \posgeq {\colR\text{resources}}.
$$

If you mistakenly put functionality and resources on the wrong
side of the inequality, as in:

<center>
<pre class='mcdp_statements' np>
provided capacity &gt;= 500 J  # incorrect expression
</pre>
</center>

then the interpreter will display an error like:

<pre class='output'>
DPSemanticError: This constraint is invalid. Both sides are resources.

line  5 |    provided capacity &gt;= 500 J
                               ↑
</pre>



## Describing relations between functionality and resources

In MCDPs, functionality and resources can depend on each other using any
monotone relations ([](#def:monotone-relation)). MCDPL contains as primitives
addition, multiplication, and division.

For example, we can describe a linear relation between mass and capacity, given
by the specific energy $\rho$:

$$
    \text{capacity} = \rho \times \text{mass}.
$$

This relation can be described in MCDPL as

<center>
    <pre class='mcdp_statements'>
        ρ = 4 J / g
        required mass ≽ provided capacity / ρ
    </pre>
</center>

In the graphical representation (<a href="#fig:model4"/>), there is now a
connection between <f>capacity</f> and <r>mass</r>, with a DP that multiplies by
the inverse of the specific energy.


<col2>
    <pre class='mcdp' id='model4' label='linear.mcdp'>
    mcdp {
        provides capacity [J]
        requires mass [g]
        ρ = 4 J / g
        required mass ≽ provided capacity / ρ
    }
    </pre>
    <render class='ndp_graph_enclosed_TB'
    figure-id='fig:model4'>`model4</render>
</col2>


For example, if we ask for <fvalue>600 J</fvalue>:

    $ mcdp-solve linear "600 J"

we obtain this answer:

    Minimal resources needed: mass = ↑{150 g}

<!--
<pre class='print_value'>
solve(600J,`model4)
</pre> -->


## Units

PyMCDP is picky about units. It will complain if there is any dimensionality
inconsistency in the expressions. However, as long as the dimensionality is
correct, it will automatically convert to and from equivalent units. For
example, in <a href="#code:conversion"/> the specific energy given in
<mcdp-poset>kWh/kg</mcdp-poset>. The two MCDPs are equivalent. PyMCDP will take
care of the conversions that are needed, and will introduce a conversion from
<mcdp-poset>J*kg/kWh</mcdp-poset> to <mcdp-poset>g</mcdp-poset> (<a
href="#fig:conversion"/>).

<!-- TODO: add pointers to problems with conversions: Glimli Glider, Ariane? -->

For example, [](#code:conversion) is the same example with the specific energy
given in <mcdp-poset>kWh/kg</mcdp-poset>. The output of the two models are
completely equivalent (up to numerical errors).

[](#code:conversion) also shows the syntax for comments. MCDPL allows to add a
Python-style documentation strings at the beginning of the model, delimited by
three quotes. It also allows to give a short description for each functionality,
resource, or constant declaration, by writing a string at the end of the line.

<center>
    <pre class='mcdp' id='model5' figure-id='code:conversion'>
mcdp {
    '''
        Simple model of a battery as a linear relation
        between capacity and mass.
    '''
    provides capacity [J] 'Capacity provided by the battery'
    requires mass [g] 'Battery mass'
    ρ = 200 kWh / kg  'Specific energy'
    required mass ≽ provided capacity / ρ
}
    </pre>
    <!-- do not put in col2 - this is large -->
    <render class='ndp_graph_enclosed_LR'
            figure-id="fig:conversion" style='max-width: 100%'>
            `model5
    </render>
</center>

<figcaption id='code:conversion:caption'>
    Automatic conversion among <poset>g</poset>, <poset>kg</poset>,
    <poset>J</poset>, <poset>kWh</poset>.
</figcaption>

<figcaption id='fig:conversion:caption'>
    A conversion from <poset>J*kg/kWh</poset> to <poset>g</poset>
    is automatically introduced.
</figcaption>
