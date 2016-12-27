
## Use of Unicode glyphs to represent operators {#sub:unicode-operators}

MCDPL allows a number of Unicode glyphs as an abbreviations of a few operators.


<col3 id='glyphs' class='labels-row1'
    figure-id='tab:glyphs'
    figure-caption='Unicode glyphs and syntactically equivalent ASCII'>
    <s>Unicode</s> <s>ASCII</s>  <s>Context</s>
    <k>≽</k>    <k>&gt;=</k>      <s></s>
    <k>≼</k>    <k>&lt;=</k>      <s></s>
    <k>·</k>    <k>*</k>          <s>Multiplication</s>
    <k>⟨⋯⟩</k>  <k>&lt;⋯&gt;</k>  <s>Tuple-building </s>
    <k>⊤</k>    <k>Top</k>        <s></s>
    <k>⊥</k>    <k>Bottom</k>     <s></s>
    <k>℘</k>    <k>powerset</k>
                    <s><a href="#subsub:syntax-powerset">Power set</a></s>
    <s><kf>⟻</kf><br/><kr>⟼</kr></s>
    <s><kf>&lt;--|</kf><br/><kr>|--&gt;</kr></s>
    <s><a href="#subsub:syntax-catalogue">Catalogue</a></s>
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
<q>`^d`</q>. It is syntactically equivalent to write <q>`x^2`</q> or
<q>`x²`</q>.
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

[](#tab:greek-letters) shows the Greek letters supported and their
translitteration. Note that there is a difference between lower case and upper
case.

<center>
<col2 id='greek-letters'
    figure-id='tab:greek-letters'
    figure-caption="Greek letters supported by MCDPL"
    figure-class='float_top'>
    <code>α</code> <code>alpha</code>
    <code>β</code> <code>beta</code>
    <code>Χ</code> <code>Gamma</code>
    <code>χ</code> <code>gamma</code>
    <code>Δ</code> <code>Delta</code>
    <code>δ</code> <code>delta</code>
    <code>Ε</code> <code>Epsilon</code>
    <code>ε</code> <code>epsilon</code>
    <code>Η</code> <code>Eta</code>
    <code>η</code> <code>eta</code>
    <code>Γ</code> <code>Gamma</code>
    <code>γ</code> <code>gamma</code>
    <code>Ι</code> <code>Iota</code>
    <code>ι</code> <code>iota</code>
    <code>Κ</code> <code>Kappa</code>
    <code>κ</code> <code>kappa</code>
    <code>Λ</code> <code>Lambda</code>
    <code>λ</code> <code>lambda</code>
    <code>Μ</code> <code>Mu</code>
    <code>μ</code> <code>mu</code>
    <code>Ν</code> <code>Nu</code>
    <code>ν</code> <code>nu</code>
    <code>Ω</code> <code>Omega</code>
    <code>ω</code> <code>omega</code>
    <code>Ο</code> <code>Omicron</code>
    <code>ο</code> <code>omicron</code>
    <code>Φ</code> <code>Phi</code>
    <code>φ</code> <code>phi</code>
    <code>Π</code> <code>Pi</code>
    <code>π</code> <code>pi</code>
    <code>Ψ</code> <code>Psi</code>
    <code>ψ</code> <code>psi</code>
    <code>Χ</code> <code>Chi</code>
    <code>χ</code> <code>chi</code>
    <code>Ρ</code> <code>Rho</code>
    <code>ρ</code> <code>rho</code>
    <code>Σ</code> <code>Sigma</code>
    <code>σ</code> <code>sigma</code>
    <code>Τ</code> <code>Tau</code>
    <code>τ</code> <code>tau</code>
    <code>Θ</code> <code>Theta</code>
    <code>θ</code> <code>theta</code>
    <code>Υ</code> <code>Upsilon</code>
    <code>υ</code> <code>upsilon</code>
    <code>Ξ</code> <code>Xi</code>
    <code>ξ</code> <code>xi</code>
    <code>Ζ</code> <code>Zeta</code>
    <code>ζ</code> <code>zeta</code>
</col2>
</center>

<style>
#greek-letters {
    column-count: 4;
    td:last-child {
        text-align: left;
    }
}
</style>

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
