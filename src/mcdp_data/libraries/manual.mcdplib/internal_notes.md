## Using the web interface

### syntax highlighting

Use ``<pre>`` tags.

~~~
<pre class="mcdp" id='model'>
mcdp {
	provides capacity [J]
	requires mass [g]

	# incomplete
}
</pre>
~~~

<pre class="mcdp" id='submodel'>
mcdp  {
	provides f [J]
	requires r [g]
	required r >= 10g
	provided f <= 10J
}
</pre>


<pre class="mcdp" id='model'>
mcdp {
	provides capacity [J]
	requires mass [g]
	s = instance `submodel
	mass >= r required by s
	capacity <=  f provided by s
}
</pre>
 

### mcdp_ndp_graph_templatized

~~~
<pre class='ndp_graph_templatized'>`model</pre>
~~~

<pre class='ndp_graph_templatized'>`model</pre>

### mcdp_ndp_graph_templatized_labeled

~~~
<pre class='ndp_graph_templatized_labeled'>`model</pre>
~~~

<pre class='ndp_graph_templatized_labeled'>`model</pre>


###  mcdp_ndp_graph_normal

~~~
<pre class='ndp_graph_normal'>`model</pre>
~~~

<pre class='ndp_graph_normal'>`model</pre>

### ndp_graph_enclosed

~~~
<pre class='ndp_graph_enclosed'>`model</pre>
~~~

<pre class='ndp_graph_enclosed'>`model</pre>


### ndp_graph_expand

~~~
<img class='ndp_graph_expand_LR'>`model</img>
~~~

<img class='ndp_graph_expand_LR'>`model</img>

~~~
<img class='ndp_graph_expand_TB'>`model</img>
~~~

<img class='ndp_graph_expand_TB'>`model</img>

###  ndp_template_graph_enclosed

~~~
<img class='template_graph_enclosed'>`ActuationEnergeticsTemplate</img>
~~~

<img class='template_graph_enclosed'>
template [A:mcdp{}]
mcdp {
	a = instance A
}
</img>


### Poset

<pre class="mcdp_poset" id='myposet'>
poset { 
	a b 
	c <= a 
	c <= d
	b <= d 
}
</pre>


~~~
<img class='hasse'>`myposet</pre>
~~~

<img class='hasse'>`myposet</pre>


~~~
<img class='hasse' id='myposet'/>
~~~

<img class='hasse' id='myposet'/>


### plot_generic_value

~~~
<img class='plot_value_generic' style='width: 10em'>upperclosure{<1 g, 0m>, <2 g, 1m>} </img>
~~~

<img class='plot_value_generic' style='width: 10em'>upperclosure{<1 g, 0m>, <2 g, 1m>} </img>


<img class='plot_value_generic' style='width: 10em'>
&lt;upperclosure {<0g, 1J>}, upperclosure {<1g, 0.5J>}&gt;
</img>


### print_value

~~~
<pre class='print_value'>
&lt;upperclosure {<0g, 1J>}, upperclosure {<1g, 0.5J>}&gt;
</pre>
~~~

<pre class='print_value'>
&lt;upperclosure {<0g, 1J>}, upperclosure {<1g, 0.5J>}&gt;
</pre>


### ``<code>``


This is P: <code class='mcdp_poset'>`my_poset</code>.

This is P: <code class='mcdp_value'>Nat:0</code>.

<!-- This is not ok: <code class='mcdp_value'>`my_poset: <em>element</em></code>.
 -->
