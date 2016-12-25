
## Hello, world!

The "hello world" example of an MCDP is a degenerate MCDP that
can tell us that, to do nothing, nothing is needed.

The minimal MCDP can be defined as in [](#code:empty).
The code describes an MCDP with zero functionality and zero resources.

<col2>
    <pre class='mcdp' id='empty' figure-id='code:empty' label='empty.mcdp'>
    mcdp {&#32;&#32;&#32;&#32;
        # an empty model
    }
    </pre>
    <render class='fancy_editor' figure-id="fig:empty">`empty</render>
</col2>

Formally, the functionality and resources spaces are $\funsp=\One$, $\ressp=\One$.
%
The space $\One = \{ \langle\rangle \}$ is the empty product ([](#def:One)). $\One$ contains only one element, the empty tuple $\langle\rangle$.

The MCDP above can already be queried using the program <program>mcdp-solve</program>. The command

    $ mcdp-solve empty "<>"

means "for the MCDP <code>empty</code>, find the minimal resources
needed to perform the functionality $f=\langle\rangle$".
%
The command produces the output:

    Minimal resources needed = ↑{⟨⟩}

The output means "it is possible to perform the functionality specified,
and the minimal resources needed are $\res^\star=\langle\rangle$".
So, we learned that we need nothing to do nothing.


## Defining functionality and resources

The functionality and resources of an MCDP are defined using
the keywords <kf>provides</kf> and <kr>requires</kr>.
The code in [](#code:model1) defines an MCDP with one functionality,
<fname>capacity</fname>, measured in joules,
and one resource, <rname>mass</rname>, measured in grams.

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


That is, the functionality space is~$\funsp=\overline{\reals}_{+}^{[\text{J}]}$ and
the resource space is $\ressp=\overline{\reals}_{+}^{[\text{g}]}$. Here, let~$\overline{\reals}_{+}^{[g]}$ refers to the nonnegative real numbers with units of grams. (Of course, internally this is
represented using floating point numbers. See~[](#sub:Rcomp) for more details.)

The MCDP defined above is, however, incomplete, because we have
not specified how <fname>capacity</fname> and <rname>mass</rname> relate to one another.
In the graphical notation, the co-design diagram has unconnected arrows
([](#fig:model1)).
<!--
<render class='fancy_editor_LR' figure-id="fig:model1">
    `model1
</render> -->

### Constraining functionality and resources

In the body of the <k>mcdp{}</k> declaration one
can refer to the values of the functionality and resources
using the expressions <cf>provided <em>(functionality name)</em></cf>
and <cr>required <em>(resource name)</em></cr>
and declaring an inequality of the type
$$
    {\colF \text{functionality}} \posgeq {\colR\text{resources}}.
$$

For example, [](#code:model2) shows the completion of the
previous MCDP, with hard bounds given to both <fname>capacity</fname> and <rname>mass</rname>.

<center>
    <pre class='mcdp' id='model2' figure-id="code:model2" np>
    mcdp {
        provides capacity [J]
        requires mass [g]

        provided capacity &lt;= 500 J
        required mass &gt;= 100g
    }
    </pre>
</center>

To describe the inequality constraints, MCDPL allows to use <k>&lt;=</k>, <k>&gt;=</k>, as well as their fancy Unicode version <k>≼</k>, <k>≽</k>.
These two expressions are completely equivalent:
%
<col2>
    <pre class='mcdp_statements'>
    provided capacity &lt;= 500 J
    required mass &gt;= 100g
    </pre>
    <pre class='mcdp_statements'>
    provided capacity ≼ 500 J
    required mass ≽ 100g
    </pre>
    <!-- -->
    <pre class='mcdp_statements'>
    provided capacity &lt;= 500 J
    required mass &gt;= 100g
    </pre>
</col2>

The verbose visualization is as in [](#fig:model2-verbose).

<render class='fancy_editor_LR' figure-id="fig:model2-verbose"
    figure-caption="Verbose visualization">
    `model2
</render>

The visualization in [](#fig:model2-verbose) is quite verbose.  It shows one node for each functionality
and resources; here, a node can be thought of a variable on which
we are optimizing. This is the view shown in the editor.

The less verbose visualization, as in [](#fig:model2-verbose),
skips the visualization of the initial node.

<render class='ndp_graph_enclosed' figure-id="fig:model2"
    figure-caption="Synthetic visualization">
    `model2
</render>


If it is possible to disambiguate from the context, the MCDPL
interpreter also allows to drop the keywords <cf>provided</cf>
and <cr>required</cr>, although it will give a warning.
%
For example, if one forgets the keyword <cf>provided</cf>,
the interpreter will give the following warning:

<pre>
Please use "provided capacity" rather than just "capacity".

    line  2 |    provides capacity [J]
    line  3 |    requires mass [g]
    line  4 |
    line  5 |    capacity ≼ 500 J
                 ^^^^^^^^
</pre>


It is possible to query this minimal example. For example:

    $ mcdp-solve minimal "400 J"

The answer is:

    Minimal resources needed: mass = ↑ {100 g}


If we ask for more than the MCDP can provide:

    $ mcdp-solve minimal "600 J"

we obtain no solutions (the empty set):

    Minimal resources needed: mass = ↑{}

The notation &ldquo;`↑{}`&rdquo; means "the upper closure of the empty set $\emptyset$" ([](#def:upperclosure)), which is equal to $\emptyset$.


### Describing relations between functionality and resources

In MCDPs, functionality and resources can depend on each other using
any monotone relations ([](#def:monotone-relation)).

The language MCDPL contains as primitives addition,
multiplication, and division. For example, we can describe a linear relation between
mass and capacity, given by the specific energy $\rho$:
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

In the graphical representation (<a href="#fig:model4"/>), there is now
a connection between <f>capacity</f> and <r>mass</r>, with a DP that
multiplies by the inverse of the specific energy.


<col2>
    <pre class='mcdp' id='model4' label='linear.mcdp'>
    mcdp {
        provides capacity [J]
        requires mass [g]
        ρ = 4 J / g
        required mass ≽ provided capacity / ρ
    }
    </pre>
    <render class='ndp_graph_enclosed'
    figure-id='fig:model4'>`model4</render>
</col2>


If we ask for more than the MCDP can provide:

    $ mcdp-solve linear "600 J"

we obtain no solutions (the empty set):

    Minimal resources needed: mass = ↑{150 g}

<!--
<pre class='print_value'>
solve(600J,`model4)
</pre> -->


### Units

PyMCDP is picky about units. It will complain if any operation does
not have the required dimensionality. However, as long as the dimensionality
is correct, it will automatically convert to and from equivalent units.
For example, in <a href="#code:conversion"/> the specific energy given
in <mcdp-poset>kWh/kg</mcdp-poset>. The two MCDPs are equivalent. PyMCDP will take care of
the conversions that are needed, and will introduce a conversion from
<mcdp-poset>J*kg/kWh</mcdp-poset> to <mcdp-poset>g</mcdp-poset> (<a href="#fig:conversion"/>).

<!-- TODO: add pointers to problems with conversions: Glimli Glider, Ariane? -->

For example, [](#code:conversion) is the same example with the specific
energy given in <mcdp-poset>kWh/kg</mcdp-poset>.
The output of the two models are completely equivalent (up to numerical errors).

[](#code:conversion) also shows the syntax for comments.
MCDPL allows to add a Python-style documentation strings at the beginning
of the model, delimited by three quotes.
It also allows to give a short description for each
functionality, resource, or constant declaration, by writing a
string at the end of the line.

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
