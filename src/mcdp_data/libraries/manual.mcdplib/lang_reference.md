# MCDPL Language reference                       {#sec:MCDPL-language-reference}

This chapter gives a formal description of the MCDPL language.



## Types universe

MCDPL has 5 "types universes". Every expression in the language
belongs to one of these types as described in \tabref{table1}.

<style>
#tab\:table1 td:nth-child(3) {
    text-align: center;
}
</style>
<col3 figure-id="tab:table1"
      figure-caption="Types universe"
      class='labels-row1'>
    <s>Type universe </s>
    <s>example</s>
    <s></s>
    <!-- -->
    <s>Posets</s>
    <s><mcdp-poset>Nat</mcdp-poset>, <mcdp-poset>m/s^2</mcdp-poset> </s>
    <s>Posets are the equivalent of what are "types" in other languages.</s>
    <!-- -->
    <s>Values</s>
    <s><mcdp-value>42</mcdp-value>, <mcdp-value>9.81 m/s^2</mcdp-value></s>
    <s>Values are the elements of the posets.</s>
    <!-- -->
    <s>NDPs</s>
    <s><k>mcdp{...}</k></s>
    <s>These correspond to the mathematical idea of MCDPs, enriched by extra
        information, such as names of "ports".</s>
    <!-- -->
    <s>templates</s>
    <s><k>template[...]{...}</k> </s>
    <s>These are templates for NDPs; could be considered morphisms in an operad</s>
    <!-- -->
    <s>DPs</s>
    <s>\xxx</s>
    <s>These correspond to primitive DPs</s>
</col3>

[](#tab:table2) describes for each type the default file extension
and the base Python class.

<col3 class='labels-row1'
    figure-id="tab:table2"
    figure-caption="Types universe, file extensions and Python superclass">
    <!---->
        <s>Type universe </s>
        <s> file extensions</s>
        <s>superclass</s>
        <!---->
        <s>Posets</s>
        <s>.mcdp_poset</s>
        <s>Poset</s>
        <!---->
        <s>Values</s>
        <s><code>.mcdp_value</code></s>
        <s><code>object</code><footnote>Any Python object will do. \xxx</footnote></s>
        <!---->
        <s>NDPs</s>
        <s> <code>.mcdp</code></s>
        <s><code>NamedDP</code></s>
     <!---->
        <s>templates</s>
        <s><code>.mcdp_template</code> </s>
        <s>\xxx</s>
    <!---->
        <s>DPs</s>
        <s><code>.mcdp_primitivedp</code></s>
        <s><code>PrimitiveDP</code></s>
</col3>

It is possile to implement one's own extensions by subclassing
one of these classes. In particular, what is easy to do
is creating custom ``Poset``s as well as ``PrimitiveDP``s,
if these cannot be expressed using the operators available.

<style type='text/css'>

#tab\:table1 td,
#tab\:table2 td { padding: 0.5em;} /* fix for fix for prince */
/*
#tab\:table1 tr:first-child,
#tab\:table2 tr:first-child  {
    font-weight: bold;
}*/

#tab\:table1 td:first-child,
#tab\:table2 td:first-child  {
    width: 10em;
    text-align: center;
}

/*#tab\:table2 td {text-align: center;}*/
</style>
