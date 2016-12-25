## Use of Unicode letters and glyphs ## {#sub:unicode}

MCDPL allows to use some Unicode characters in identifiers and expressions.

### Pure substitutions

The following are equivalent

    ⟻
    ⟼
    ≽
    ≼
    ·
    ⟨⟩
    ℘
    ⊤
    ⊥


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

The way MCDPL considers these glyphs is that they are immediately
converted to an extended form.

Every Greek letter is
converted to its name. It is syntactically equivalent to write
"``alpha``" or "``α``".

### Subscripts

These are the subscripts supported:

    x₀ x₁ x₂ x₃ x₄ x₅ x₆ x₇ x₈ x₉

Subscripts can only occur at the end of an identifier: ``a₁`` is valid,
while ``a₁b`` is not valid.

For subscripts, every occurrence of a subscript of the digit *d* is converted to the fragment "``_d``".  It is syntactically equivalent to write
"``_1``" or "``₁``".

### Superscripts

These are the superscripts:

    x¹ x² x³ x⁴ x⁵ x⁶ x⁷ x⁸ x⁹

Every occurrence of a superscript of the digit *d* is interpreted as a power "``^d``".  It is syntactically equivalent to write "``x^2``" or "``x²``".


### Example of syntactic equivalence

Putting all together, it is equivalent to write

<pre class='mcdp_statements' noprettify="1">
alpha_1 = beta^3 + 9.81 m/s^2
</pre>

and

<pre class='mcdp_statements'>
α₁ = β³ + 9.81 m/s²
</pre>
