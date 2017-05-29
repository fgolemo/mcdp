---
layout: default
title: Home
permalink: index.html
---

This site contains materials describing a new **mathematical theory of co-design**
that helps in designing complex systems with many components that are functionally dependent on each other.

"Monotone Co-Design Problems" (**MCDPs**) are a class of extremely expressive optimization problems. They can express: non-convex constraints, non-differentiable, discontinuous and non-scalarizable objective functions, and work with non-continuous design spaces.

<strong>MCDP<span style='color:darkred'>L</span></strong> is an extremely expressive language to describe MCDPs.

**[PyMCDP][PyMCDP]** is a Python interpreter and solver for MCDPL.

For more information, please see:

* [the papers](/papers/)
* a [live demo site: `demo.co-design.science`][demo]
* the [software manual (PDF)][manual].
* the [source code, on github][PyMCDP].

[manual]: https://andreacensi.github.io/mcdp-manual/mcdp-manual.pdf
[PyMCDP]: http://github.com/AndreaCensi/mcdp
[demo]: http://demo.co-design.science/


*Below, an example of a graphical representation of an MCDP (left)
along with the MCDPL snippet that describes it (right).*

<table>
 <tr>
 <td><img src="media/battery-out_expected/battery_minimal-greenredsym.png" width="400px"/></td>
 <td><img src="media/battery-out_expected/battery_minimal-syntax_pdf.png" width="300px"/>
 </td>
 </tr>
</table>


<div class="home">

  <!-- <h1 class="page-heading">News</h1> -->


  <!-- <h2 style='margin-top: 10em'> News </h2> -->
  <ul class="post-list">
    {% for post in site.posts %}
      <li>
        <span class="my-post-date">{{ post.date | date: "%Y-%m-%d" }}</span>

        <span class="my-post-title">{{ post.title }}</span>

        <!-- <a href="{{ post.url | prepend: site.baseurl }}">{{ post.title }}</a> -->

        {{ post.content }}
      </li>
    {% endfor %}
  </ul>
<!--
  <p class="rss-subscribe">subscribe <a href="{{ "/feed.xml" | prepend: site.baseurl }}">via RSS</a></p> -->

</div>
