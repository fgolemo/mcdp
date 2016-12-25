

## <program>mcdp-depgraph</program> {#sub:mcdp-depgraph}

## <program>mcdp-render</program> {#sub:mcdp-render}

## <program>mcdp-render-manual</program> {#sub:mcdp-render-manual}

## Writing documentation


### Markdown Extra

This is to set the ID:

~~~
## header ## {#sec:the_id}
~~~


### Using LaTeX


The basic relation is $\res \geq \ftor(\fun)$.


Simple test to show MathJax is working: $x = y^2 + \sin(\int_a^b D x)$.

\begin{eqnarray}
y &=& x^4 + 4      \nonumber \\
  &=& (x^2+2)^2 -4x^2 \nonumber \\
  &\le&(x^2+2)^2    \nonumber
\end{eqnarray}


Define this:

$$a := x^2-y^3 \tag{eq}\label{eq} $$

Refer to it as in \eqref{eq}.

Also:

$$ a+y^3 \stackrel{\eqref{eq}}= x^2 $$


### syntax highlighting

Remember to escape:

* use `&#96;` instead of &#96;
* use `&#36;` instead of &#36;
* use `&lt;` instead of &lt;
* use `&gt;` instead of &gt;

Use <code>&lt;pre&gt;</code> tags.

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
    s = instance &#96;submodel
    mass ≽ r required by s
    capacity ≼  f provided by s
}
</pre>


### `noprettify`

### Other substitutions

col2, col3, col4, col5

~~~
<col2>
    <p></p>
    <p></p>
    <p></p>
    <p></p>
</col2>
~~~

Other abbreviations

<col2>
    <code>&lt;val&gt;</code>
    <code>&lt;code class="mcdp_value"&gt;</code>
    <code>&lt;mcdp-value&gt;</code>
    <code>&lt;code class="mcdp_value"&gt;</code>
    <code>&lt;pos&gt;</code>
    <code>&lt;code class="mcdp_poset"&gt;</code>
    <code>&lt;mcdp-poset&gt;</code>
    <code>&lt;code class="mcdp_poset"&gt;</code>
</col2>

~~~
<pre mcdp-value>
~~~
instead of
~~~
<pre class='mcdp_value'>
</pre>
~~~

~~~
<center>
</center>
~~~


~~~
<pre mcdp-poset>
~~~
instead of
~~~
<pre class='mcdp_poset'>
</pre>
~~~

### mcdp_ndp_graph_templatized

~~~
<render class='ndp_graph_templatized'>&#96;model</render>
~~~

<render class='ndp_graph_templatized'>&#96;model</render>

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


Avoid this, because Markdown will get confused:

<pre>
&lt;render class='hasse' id='myposet'/&gt;
</pre>

### Using `plot_value_generic`

Can use `plot_value_generic`



~~~
<pre class='plot_value_generic' style='width: 10em'>
    upperclosure{&lt;1 g, 0m&gt;, &lt;2 g, 1m&gt;}
</pre>
~~~

<pre class='plot_value_generic'>
    upperclosure{&lt;1 g, 0m&gt;, &lt;2 g, 1m&gt;}
</pre>


<pre class='plot_value_generic'>
    &lt;upperclosure {&lt;0g, 1J&gt;}, upperclosure {&lt;1g, 0.5J&gt;}&gt;
</pre>


### `print_value`

~~~
<pre class='print_value'>
&lt;upperclosure {&lt;0g, 1J&gt;}, upperclosure {&lt;1g, 0.5J&gt;}&gt;
</pre>
~~~

<pre class='print_value'>
&lt;upperclosure {&lt;0g, 1J&gt;}, upperclosure {&lt;1g, 0.5J&gt;}&gt;
</pre>


### Using `code`

Use &lt;code&gt; tags.



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

### Bugs and limitations


Always close the render and pre elements:

    <render ...></render>

Never:

    <render .../>


Avoid two backticks in the same paragraph, it will give an error:

    Don't get confused here: <strong>`bold</strong> and <strong>`brave</strong>.

because MD gets confused.



<!-- This is not ok: <code class='mcdp_value'>`my_poset: <em>element</em></code>.
 -->
