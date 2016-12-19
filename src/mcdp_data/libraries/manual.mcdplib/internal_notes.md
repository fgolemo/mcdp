

<h2 id="mcdp-depgraph"> <program>mcdp-depgraph</program> </h2>

<h2 id="mcdp-render"> <program>mcdp-render</program> </h2>

<h2 id="mcdp-render-manual"> <program>mcdp-render-manual</program> </h2>

## Writing documentation 

### syntax highlighting

Use ``<pre>`` tags.

~~~
<pre class="mcdp" id='submodel'>
mcdp  {
	provides f [J]
	requires r [g]
	required r ≽ 10g
	provided f ≼ 10J
}
</pre>


<pre class="mcdp" id='model'>
mcdp {
	provides capacity [J]
	requires mass [g]
	s = instance `submodel
	mass ≽ r required by s
	capacity ≼  f provided by s
}
</pre>
~~~

will give you:

<pre class="mcdp" id='submodel'>
mcdp  {
	provides f [J]
	requires r [g]
	required r ≽ 10g
	provided f ≼ 10J
}
</pre>


<pre class="mcdp" id='model'>
mcdp {
	provides capacity [J]
	requires mass [g]
	s = instance `submodel
	mass ≽ r required by s
	capacity ≼  f provided by s
}
</pre>


### ``noprettify``

### mcdp_ndp_graph_templatized

~~~
<render class='ndp_graph_templatized'>`model</render>
~~~

<render class='ndp_graph_templatized'>`model</render>

### mcdp_ndp_graph_templatized_labeled

~~~
<render class='ndp_graph_templatized_labeled'>`model</render>
~~~

<render class='ndp_graph_templatized_labeled'>`model</render>


###  mcdp_ndp_graph_normal

~~~
<render class='ndp_graph_normal'>`model</render>
~~~

<render class='ndp_graph_normal'>`model</render>

### ndp_graph_enclosed

~~~
<render class='ndp_graph_enclosed'>`model</render>
~~~

<render class='ndp_graph_enclosed'>`model</render>


### ndp_graph_expand

~~~
<render class='ndp_graph_expand_LR'>`model</render>
~~~

<render class='ndp_graph_expand_LR'>`model</render>

~~~
<render class='ndp_graph_expand_TB'>`model</render>
~~~

<render class='ndp_graph_expand_TB'>`model</render>

###  ndp_template_graph_enclosed

~~~
<render class='template_graph_enclosed'>`ActuationEnergeticsTemplate</render>
~~~

<render class='template_graph_enclosed'>
template [A:mcdp{}]
mcdp {
	a = instance A
}
</render>


### Poset

<pre class="mcdp_poset" id='myposet'>
poset {
	a b
	c ≼ a
	c ≼ d
	b ≼ d
}
</pre>


~~~
<render class='hasse'>`myposet</render>
~~~

<render class='hasse'>`myposet</render>


~~~
<render class='hasse' id='myposet'></render>
~~~

<render class='hasse' id='myposet'></render>


Try to avoid this, because Markdown will get confused:

~~~
<render class='hasse' id='myposet'/>
~~~


<render class='hasse' id='myposet'/>

### Using ``plot_value_generic``

Can use ``plot_value_generic``



~~~
<pre class='plot_value_generic' style='width: 10em'>
	upperclosure{&lt;1 g, 0m&gt;, &lt;2 g, 1m&gt;}
</pre>
~~~

<pre class='plot_value_generic' style='width: 10em'>upperclosure{&lt;1 g, 0m&gt;, &lt;2 g, 1m&gt;} </pre>


<pre class='plot_value_generic' style='width: 10em'>
&lt;upperclosure {&lt;0g, 1J&gt;}, upperclosure {&lt;1g, 0.5J&gt;}&gt;
</pre>


### ``print_value``

~~~
<pre class='print_value'>
&lt;upperclosure {&lt;0g, 1J&gt;}, upperclosure {&lt;1g, 0.5J&gt;}&gt;
</pre>
~~~

<pre class='print_value'>
&lt;upperclosure {&lt;0g, 1J&gt;}, upperclosure {&lt;1g, 0.5J&gt;}&gt;
</pre>


### Using ``code``

Use ``<code>`` tags.



~~~
This is P: <code class='mcdp_poset'>`my_poset</code>.

This is P: <code class='mcdp_value'>Nat:0</code>.
~~~

This is P: <code class='mcdp_poset'>`my_poset</code>.

This is P: <code class='mcdp_value'>Nat:0</code>.


### Abbreviations

~~~
<code class='keyword'>x</code>  and <k>x</k>

<code class='mcdp_value'>Nat:0</code>

<mcdp-value>Nat:0</mcdp-value>
<mcdp-poset>Nat</mcdp-poset>.
<mcdp-fvalue>1+1</mcdp-fvalue>.
<mcdp-rvalue>1+2</mcdp-rvalue>.

~~~





<!-- This is not ok: <code class='mcdp_value'>`my_poset: <em>element</em></code>.
 -->
