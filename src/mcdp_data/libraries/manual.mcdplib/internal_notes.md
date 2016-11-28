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
	provides c2 [J]
	requires m2 [g]
	m2 >= 10g
	c2 <= 10J
}
</pre>


<pre class="mcdp" id='model'>
mcdp {
	provides capacity [J]
	requires mass [g]
	s = instance `submodel
	mass >= s.m2
	capacity <= s.c2
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
<pre class='ndp_graph_expand_LR'>`model</pre>
~~~

<pre class='ndp_graph_expand_LR'>`model</pre>

~~~
<pre class='ndp_graph_expand_TB'>`model</pre>
~~~

<pre class='ndp_graph_expand_TB'>`model</pre>

###  ndp_template_graph_enclosed

~~~
<pre class='template_graph_enclosed'>`ActuationEnergeticsTemplate</pre>
~~~


<pre class='template_graph_enclosed'>
template [A:mcdp{}]
mcdp {
	a = instance A
}
</pre>

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
