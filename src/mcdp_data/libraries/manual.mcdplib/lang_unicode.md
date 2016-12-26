
## Use of Unicode glyphs to represent operators {#sub:unicode-operators}

MCDPL allows a number of Unicode glyphs as an abbreviations of a few operators.


<col3 id='glyphs' class='labels-row1'>
    <s>Unicode</s> <s>ASCII</s>  <s>Context</s>
    <k>≽</k>    <k>&gt;=</k>      <s></s>
    <k>≼</k>    <k>&lt;=</k>      <s></s>
    <k>·</k>    <k>*</k>          <s>Multiplication</s>
    <k>⟨⋯⟩</k>  <k>&lt;⋯&gt;</k>  <s>Tuple-building </s>
    <k>⊤</k>    <k>Top</k>        <s></s>
    <k>⊥</k>    <k>Bottom</k>     <s></s>
    <k>℘</k>    <k>powerset</k>   <s><a href="#syntax-powerset">Power set</a></s>
    <s><kf>⟻</kf><br/><kr>⟼</kr></s> <s><kf>&lt;--|</kf><br/><kr>|--&gt;</kr></s>
    <s><a href="#syntax-catalogue">Catalogue</a></s>
</col3>
<style>
    #glyphs {
        column-count: 2;
        td:nth-child(3) {
            text-align: left;
            vertical-align: top;
        }
    }
</style>

#### Superscripts to indicate powers

Every occurrence of a superscript of the digit *d* is interpreted as a power
<q>`^d`</q>.  It is syntactically equivalent to write <q>`x^2`</q> or <q>`x²`</q>.
<!-- x¹ x² x³ x⁴ x⁵ x⁶ x⁷ x⁸ x⁹ -->

<col2 id='subscripts'>
    <code>x¹</code> <code>x^1</code>
    <code>x²</code> <code>x^2</code>
    <code>x³</code> <code>x^3</code>
    <code>x⁴</code> <code>x^4</code>
    <code>x⁵</code> <code>x^5</code>
    <code>x⁶</code> <code>x^6</code>
    <code>x⁷</code> <code>x^7</code>
    <code>x⁸</code> <code>x^8</code>
    <code>x⁹</code> <code>x^9</code>
</col2>

<style>
    #subscripts {
        column-count: 5;
    }
</style>



## Use of Unicode letters as part of identifiers ## {#sub:unicode-in-identifiers}

MCDPL allows to use some Unicode characters, Greek letters and subscripts, also
in identifiers and expressions. For exmple, it is equivalent to write
<q>`alpha_1`</q> and <q>`α₁`</q>.

The rules are that:

1. Greek letters can only appear at the beginning of an identifier.
2. Subscripts can only appear at the end of an identifier.

### Greek letters

The following are the Greek letters supported and their translitteration.
Note that there is a difference between lower case and upper case.

    α alpha     Λ Lambda    Ρ Rho
    β beta      λ lambda    ρ rho
    Χ Chi       Μ Mu        Σ Sigma
    χ chi       μ mu        σ sigma
    Δ Delta     Ν Nu        Τ Tau
    δ delta     ν nu        τ tau
    Ε Epsilon   Ω Omega     Θ Theta
    ε epsilon   ω omega     θ theta
    Η Eta       Ο Omicron   Υ Upsilon
    η eta       ο omicron   υ upsilon
    Γ Gamma     Φ Phi       Ξ Xi
    γ gamma     φ phi       ξ xi
    Ι Iota      Π Pi        Ζ Zeta
    ι iota      π pi        ζ zeta
    Κ Kappa     Ψ Psi
    κ kappa     ψ psi

Every Greek letter is converted to its name. It is syntactically equivalent to
write <q>`alpha_material`</q> or <q>`α_material`</q>.

Greek letter names are only considered at the beginning of the identifier
and if they are followed by a non-word character.
For example, the identifer <q>`alphabet`</q> is not converted to <q>`αbet`</q>.

### Subscripts

These are the subscripts supported:

    x₀ x₁ x₂ x₃ x₄ x₅ x₆ x₇ x₈ x₉

For subscripts, every occurrence of a subscript of the digit *d* is converted to
the fragment <q>`_d`</q>.  It is syntactically equivalent to write <q>`_1`</q> or <q>`₁`</q>.

Subscripts can only occur at the end of an identifier: ``a₁`` is valid, while
<q>`a₁b`</q> is not valid.
