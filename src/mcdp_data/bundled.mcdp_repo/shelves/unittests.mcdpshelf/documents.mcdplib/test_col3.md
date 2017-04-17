
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
            provides f1 [g]
            provides f2 [J]
            provides f3 [m]
            requires r1 [lux]
            requires r2 [USD]
        }
        </render>
        <s><r>Resources</r><br/><br/>
             $\langle\ressp,\posleq_{\ressp}\rangle$</s>
    </col3>
    <figcaption id='fig:complicated:caption'>
        Representation of a design problem with three functionalities
        (<fname>f1</fname>, <fname>f2</fname>, <fname>f3</fname>)
        and three resources (<rname>r1</rname>, <rname>r2</rname>,
        <rname>r3</rname>). In this case, the functionality
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
