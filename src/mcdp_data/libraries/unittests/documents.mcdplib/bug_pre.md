
A

~~~
<pre class="mcdp" id='submodel'>
mcdp  {
    provides f [J]
    requires r [g]
    required r ≽ 10g
    provided f ≼ 10J
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

And this is still a bug:

    <pre class="mcdp" id='submodel'>
    mcdp  {
        provides f [J]
        requires r [g]
        required r ≽ 10g
        provided f ≼ 10J
    }
    </pre>