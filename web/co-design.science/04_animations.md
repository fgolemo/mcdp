---
layout: page
title: Animations
---

## Semantics of MCDPs

Consider the following MCDP:

<img src="media/animations/model.png" 
        width="500px"/>

This is one way to describe it in MCDPL:

<img src="media/animations/plusinvnat2-syntax_pdf.png" 
        width="350px"/>


An MCDP is a family of optimization problems. Once we fix all the inputs, an MCDP becomes a standard optimization problem. For example, by fixing the input ``c=4``, we obtain:

<img src='media/animations/plusinvnat2-nat4-problem.png' width='250px'/>


Note that whether the problem statement describes an MCDP is  absolutely not obvious using the formula representation; it becomes obvious when writing the problem as a graph.


## Solution

To solve an MCDP, one constructs **a chain of antichains** in the product poset of resources. 

The animations below show the sequence of antichains being
constructed to solve two variations of the same problem.

<table>
    <tr><td colspan="2">
       
    </td></tr>
    <tr>
     <td><img src="media/animations/plusinvnat2-nat4-problem.png" width="300px"/></td>
     <td><img src="media/animations/plusinvnat2-nat10-problem.png" width="300px"/>
     </td>
     </tr>
     <tr>
     <td><img src="media/animations/plusinvnat2-nat4.gif" width="300px"/></td>
     <td><img src="media/animations/plusinvnat2-nat10.gif" width="300px"/></td>
     </tr>
     <tr>
     <td colspan="2"><img src="media/animations/legend.png" width="500px"/></td>
     </tr>
</table>