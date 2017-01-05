# First part      {#part:introduction}

# Introduction

## The problem of system co-design

What is a "system"?

Here is a great quote:

<blockquote id="firstquote">
    <p>
        A system is composed of components;      <br/>
        a component is something you understand.
    </p>

    <p><a href="https://en.wikipedia.org/wiki/Howard_H._Aiken"
          title="Howard H. Aiken (1900-1973). Creator of the MARK I computer.">
          &mdash; Howard Aiken</a>
          <footnote>
        Quoted by <a href="https://en.wikipedia.org/wiki/Kenneth_E._Iverson"
            title='Kenneth E. Iverson (1920-2004). Creator of programming language APL.'>
            Kenneth Iverson</a>,
            quoted<!--  by Donald McIntyre  -->
            in <a href='http://dl.acm.org/citation.cfm?id=206985'>this paper</a>,
            but ultimately sourceless and probably apocryphal.
            </footnote>
    </p>
    <style>
     #firstquote p:nth-child(2) {
        max-width: 26em;
    }
    </style>

</blockquote>


The first part of the quote, "A system is composed of components", is plain as day as much as it is tautological. We could equally say: "A system is partitioned in parts". The second part, "a component is something you understand", is insightful: we call "system" what is too difficult to understand. Something is a "system" if we cannot keep it in mind in its entirety at the same time. This definition is, of course, an anthropocentric definition, as it is a limitation of the human mind, related to the amount of neurons in the brain. It also depends on what exactly is the task at hand with which we are confronted. Here, we consider the task of *designing* systems.

So, our slogan will be:

<blockquote id='secondquote'>
    <!-- <p>A system is composed of components;<br/>
     a component is something <u>you can design</u>;<br/>
     <u>co-design</u> is designing them all together.</p> -->

     <p>A system is composed of components;<br/>
       a component is something you understand
       <strong>how to design</strong>.</p>
</blockquote>

<style>
#newpart {
    color: purple;
}
</style>


After you know how to design all components separately, you still have the problem of designing the components in the system together. This problem of "designing things together" is what we shall call "**co-design**". This problem is one of the fundamental issues in engineering and computer sciences and appears by different names everywhere.



## A new approach

Recently developed theory and tools allow to define these co-design problems in a formal yet intuitive way that is cross-disciplinary \xxx and to develop solution methods.


Understand a component

The idea is to formalize these components by their "functionality" and
"resources". \xxx

We call <q>**<f>functionality</f>**</q> is what the component provides: why is it in the system in the first place? For example, a battery provides capacity (kWh) Other words for functionality are: <f>(functional) requirements</f>, <f>specifications</f>, simply <q><f>functions</f></q>. <footnote> Used extensively in embedded systems, a field which is familiar with these issues. This name is not used because too confusing.</footnote>

We call "**<r>resources</r>**" what the component needs. Synonyms for resources
are: <r>costs</r>, <r>dependencies</r>, \xxx

For the purpose of co-design, a component can be understood as
a relation between functionality and resources.

The **co-design constraints** are the \xxx

<img class='art' latex-options='scale=0.33' src="gmcdp_setup.pdf" />


If we generalize beyond "components", the physical components of engineering and the logical components of computer sciences, we can (as in "physical" or "logical" components) and further abstract and generalize to *relations*. So instead of "components" we are going to talk about **design problems**.

All the concepts used have an intuitive graphical representation.

In red and green \xxx <footnote>I apologize to colorblind people
for the choice of colors; however, note that the diagrams are not ambiguous
because of the node $\posleq$ that joins them.</footnote>


## A new approach to co-design

Workflow \xxx


After an MCDP has been defined, then it can be "queried". For example, the user can ask what is the optimal configuration of the system that has the least amount of resources.


MCDPL comes with a web-based GUI described in <a href="#gui"/>. The user can input a model and immediately see the graphical representation of such model.


The tools for this do not exist yet completely. So far, the language exists (though new constructs will be found) and the environment is an approximation of what we need.


## Where to use it?

It can be applied in different fields...

Chapter ... shows the case when

<center>
<img figure-id="fig:workflow"
    src='workflow.png' style='width: 14em'/>
</center>

<figcaption id='fig:workflow:caption'>
    Workflow that we imagine.
</figcaption>

<col2
    figure-id="fig:some-examples"
    figure-caption='Some examples'
    figure-class="float_bottom">

    <render class='ndp_graph_templatized' id='3D_Printer'>
    template mcdp {
        provides accuracy [1/s]
        provides shape [lux]
        requires time [s]
        requires cost [USD]
        requires materials [lux]
    }
    </render>
    <s>
    A 3D printer...
    </s>

    <render class='ndp_graph_templatized' id='Computer vision'>
    template mcdp {
        provides false_positives [1/s]
        requires latency [s]
        requires computation [USD]
        requires false_negatives [lux]
    }
    </render>
    <s>
    \xxx
    </s>

</col2>

## This book



This book presents a new approach to formalizing and solving co-design problems
through the definition of a formal language, called MCDPL, and its interpreter
and design environment.
<!--
This book does not discuss the theory, which is explained in detail in [other
papers].

[other papers]: #papers -->

By reading this book, you will learn:

* how to use the MCDPL language to describe co-design problems;
* how to use the IDE to create libraries of re-usable models;
* how to use the solution tools;
* how to model design problems in several specific domains of engineering.


But beware! At this point:

* the book is an early incomplete draft;
* the software is experimental and only partially documented.

Please send any comments, suggestions, or bug reports to <a
href="mailto:censi@mit.edu">censi@mit.edu</a>.
