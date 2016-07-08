
**Basic Definitions**

<a class='hidden' href='tour.html'/>

[Basics](tour_intro.html)

[Composition](tour_composition.html)

[Catalogues](tour_catalogue.html)

[Coproducts](tour_coproduct.html)

[Templates](tour_templates.html)

[Uncertainty](tour_uncertainty.html)

**Language reference**

<a class='hidden' href='reference.html'/>

[**Posets**](types.html)

[Scalars](types_scalar.html)
[Discrete Posets](types_finite_posets.html)
[Products](types_poset_products.html)



**Approximations**

[Upper/lower bounds of MCPDs](adv_approximations.html)


**Extended examples**

<a href='scenarios.html'/>

[Space Rovers energetics](energy_choices.html)
[Space Rovers energetics](energy_choices2.html)
[Space Rovers energetics](energy_choices3.html)

[The plug/socket domain](plugs.html)


<style type='text/css'>
.current { color: red; }
</style>
<script type='text/javascript'>

$("a").each(function(){
	href = $(this).attr('href');
	//base = window.location.pathname;
	//resolved = resolve(href, base);
	s1 = href.split("/");
	s2 = window.location.pathname.split('/');
	s1 = s1[s1.length-1];
	s2 = s2[s2.length-1];

   if (s1 == s2) {
           $(this).addClass("current");
   }
});
</script>