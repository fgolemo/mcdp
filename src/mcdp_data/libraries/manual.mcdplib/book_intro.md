# Introduction

## The problem of system co-design

What is a "system"?

Here is a great quote:

<blockquote id="firstquote">
    <p>A system is composed of components;<br/> a component is something you understand.</p>

    <p><a href="https://en.wikipedia.org/wiki/Howard_H._Aiken"
          title="Howard H. Aiken (1900-1973). Creator of the MARK I computer.">
          &mdash; Howard Aiken</a>,
        quoted by <a href="https://en.wikipedia.org/wiki/Kenneth_E._Iverson"
            title='Kenneth E. Iverson (1920-2004). Creator of programming language APL.'>
            Kenneth Iverson</a>,
            quoted by Donald McIntyre in <a href='http://dl.acm.org/citation.cfm?id=206985&dl=ACM&coll=DL&CFID=877903021&CFTOKEN=25689369'>this paper</a>,
            but ultimately sourceless and probably apocryphical.</p>
</blockquote>

The first part of the quote, "A system is composed of components", is plain
as day as much as it is tautological. We could equally say: "A system is partitioned in parts".

The second part, "a component is something you understand", is revelatory:
we call "system" what is too difficult to understand. Something is a "system"
if we cannot keep it in mind in its entirety at the same time.

This definition is, of course, an anthropocentric definition, as it is a
limitation of the human mind, related to the amount of neurons in the brain.

It also depends on what exactly is the task at hand with which we are confronted.

Here, we consider the task of *designing* systems. The slogan is:

<blockquote id='secondquote'>
    <p>A system is composed of components;<br/>
     a component is something <u>you can design</u>.
</blockquote>

After you know how to design all components separately, you still have the problem of designing the components in the system together. This problem of "designing things together" is what we call "**co-design**". This problem is one of the fundamental issues in engineering and computer sciences
and appears by different names everywhere.

Recently developed theory and tools allow to define these co-design problems
in a formal yet intuitive way that is cross-disciplinary... and to develop solution methods.

The idea is to formalize these components by their "functionality" and "resources".

We call "**<f>functionality</f>**" is what the component provides: why is it in the system in
the first place? For example, a battery provides capacity (kWh)
  Other words for functionality are: <f>(functional) requirements</f>, <f>specifications</f>,
  simply "<f>functions</f>".<span class='footnote'>Used extensively in embedded systems,
  a field which is familiar with these issues. This name is not used because too confusing.</span>

We call "**<r>resources</r>**" are what the component needs.
  Synonyms for resources are: <r>costs</r>, <r>dependencies</r>, ...

For the purpose of co-design, a component can be understood as
a relation between functionality and resources.

The **co-design constraints** are the ...


If we generalize beyond
"components", the physical components of engineering and the
logical components of computer sciences, we can
(as in "physical" or "logical" components) and further
abstract and generalize to *relations*. So instead of "components"
we are going to talk about **design problems**.

All the concepts used have an intuitive graphical representation.

In red and green... <span class=footnote>I apologize to colorblind people
for the choice of colors; however, note that the diagrams are not ambiguous
because of the node "leq" that joins them.</span>

<!-- <figure>
    <img width src='logo.png'/>
    <figcaption>Representations of components</figcaption>
</figure> -->




## This book

This book presents a new approach to formalizing and solving co-design problems
through the definition of a formal language, called MCDPL, and its interpreter
and design environment.

This book does not discuss the theory, which is explained in detail in [other papers].

[other papers]: #papers

By reading this book, you will learn:

* how to use the MCDPL language to describe co-design problems;
* how to use the IDE to create libraries of re-usable models;
* how to use the solution tools;
* how to model design problems in several specific domains of engineering.

#### Bugs

At this point:
* the book is an early incomplete draft;
* the software is experimental and only partially documented.

Please send any comments, suggestions, or bug reports to <a href="mailto:censi@mit.edu">censi@mit.edu</a>.


## A brief summary of the theory


### Functionality and resources

<style type='text/css'>
img.art {
    height: 6em;
}

</style>

<img class='art'  latex-options='scale=0.33'  src="gmcdp_setup.pdf" />


### Queries


<img class='art' latex-options='scale=0.33' src="gmcdp_setup_query_r.pdf"/>

<img class='art' latex-options='scale=0.33' src="gmcdp_setup_query_f.pdf"/>

<img class='art' latex-options='scale=0.33' src="gmcdp_setup_h.pdf"/>

### Composition


### Templates
* templates

### Categorical foundations

...

### Pointers to papers

These are the papers available for the theory:

* A mathematical approach to Co-Design...

These are useful background papers and books:

* ...

## A new approach to co-design

Workflow...

The tools for this do not exist yet completely.
So far, the language exists (though new constructs will be found)
and the environment is an approximation of what we need.


### Where to use it?

It can be applied in different fields...

Chapter ... shows the case when

### Advantages and limitations

Advantages of the method:

* intuitive...
* scalable...
* zooming in and out...
* multi-domain...
* ...

Limitations:

* You still need to model...

Next steps:

* ...

## Advantages and limitations

As this is work in progress; it will take some time before it
can be reliably deployed. However, it already has some advantages.

Here we list advantages and current limitations of the work.

### Theory

Advantages of the theory:

* ...

Limitations of the theory:

* ...

Next steps for the theory:

* ...

### Language

Advantages of the language:

* ...

Limitations of the language:

* It is not supposed to model anything more than MCDPs.
* ...

Next steps for the language:

* Allow mini-languages to define each MCDP. For example, a convex optimization
  mini language.

* ...


### Core implementation

Advantages of the implementation:

* The code is relatively elegant.
* It is *exhaustively* tested.
* ...

Limitations of the implementation:

* This is experimental software.
* Some of the operations are implemented using $O(n^2)$ operations
while $O(n \log(n))$ would be possible. In particular, meet and join
of antichains are not efficiently implemented.
* It is slow because of Python, generally, and the fact that there are not
* ...

Next steps for the implementation:

* ...
* Compile down to native code using LLVM.

### Environment

Advantages of the environment:

* Browsing libraries. Creating models, posets, etc.
* Semantic highlighting of code.
* Visual feedback for most objects; e.g. diagrams are shown visually.
* ...
* beutification (formatting)

Limitations of the environment:

* Not all functions are implemented from the UI. For example,
  it is not possible to create a new library from the UI.

Next steps for the environment:

* ...


### Pointers to software



## Acknowledgements

### People

I would like to acknowledge:

* Co-authors [David Spivak][spivak] and Joshua Tan, who developed the categorical
  foundations of this theory.

DRAFT

* Jerry Marsden for geometry. (Here, I'm proud that the invariance group is quite large: it
is the group of all invariants..)

/DRAFT

[spivak]: http://math.mit.edu/~dspivak/

### Funding sources

* NSF
* AFRL

### Un-related work

There is some work that is "unrelated", which I cannot find
a way to cite in my papers, though this was very inspirational.

...

<!--
* Homotopy Type Theory
* I found very useful the lessons Bartos Miliewsky -->

### Open source software

Developing this software would not have been possible without
the open source/free software ecosystem.

Particular enablers were:

* Python, Numpy, Scipy, PyParsing, ...
* NodeJS, MathJax, ...


## License information




The code is available under the GPL license.


<img id='license' src="by-nc-sa.svg"/>

The book is available under the Creative Commons Attribution NonCommercial ShareAlike
(CC BY-NC-SA) license.

<style type='text/css'>
#license {
    float: right;
}
    blockquote#firstquote  p:first-child,
    blockquote#secondquote p:first-child {
        font-style: italic;
    }
    blockquote#firstquote p:not(:first-child) {
        font-size: smaller;
    }
</style>
