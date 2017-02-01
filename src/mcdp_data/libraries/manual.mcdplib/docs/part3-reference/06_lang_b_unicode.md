
## MCDPL grammar

### Characters

A MCDP file is a sequence of Unicode code-points
that belong to one of the classes described in [](#tab:characters).

In the current implementation, all files on disk are assumed to be encoded in UTF-8.

<style>
#characters {
    column-count: 2;
    td:first-child {
        text-align: right;
    }
    td:last-child {
        text-align: left;
    }
    td {
        vertical-align: top;
    }
}
</style>

<center>
    <col2 id='characters' figure-id='tab:characters' class='labels-row1'
        figure-caption='Character classes'>
        <s>Class</s><s>Characters</s>
        <s>Latin&nbsp;letters</s><code>abcdefghijklm<br/>nopqrstuvxwyz</code>
        <s>             </s><code>ABCDEFGHIJKLM<br/>NOPQRSTUVXWYZ</code>
        <s>Underscore</s>
        <code>_</code>
        <s>Greek&nbsp;letters</s>  <code>αβγδεζηθικλμν<br/>ξοπρστυφχψω</code>
        <s>              </s> <code>ΓΔΕΖΗΘΙΚΛΜΝΞ<br/>ΟΠΡΣΤΥΦΧΨΩ</code>

        <s>Digits</s>
        <code>0123456789</code>

        <s>Superscripts</s>
        <code>¹²³⁴⁵⁶⁷⁸⁹</code>

        <s>Subscripts</s>
        <code>₀₁₂₃₄₅₆₇₈₉</code>

        <s>Comment&nbsp;delimiter</s>
        <code>#</code>

        <s>String&nbsp;delimiters</s>
        <code>'"</code>

        <s>Backtick</s>
        <code>&#96;</code>

        <s>Parentheses</s>
        <code>[](){}</code>

        <s>Operators</s>
        <code>&lt;= &gt; ≤≥ ≼≽ = </code>

        <s>Tuple-making</s>
        <code>&lt;&gt;⟨⟩ </code>

        <s>Arrows glyphs</s>
        <code>↔⟷ ⟻↤⟼↦</code>

        <s>Math</s>
        <code>·*-+^</code>

        <s>Other glyphs</s>
        <code>×⊤⊥℘ℕℝℤ<br/>/±↑↓%&#36;⊔∅</code>
    </col2>
</center>

<style>
    #tab\:characters {
        code {
            font-family: "Input Sans", monospace;
            background-color: lightgrey;
        }
        td {
            text-align: left;
        }
    }
</style>


### Comments

Comments work as in Python.
Anything between the symbol `#` and a newline is ignored. Comments can include any Unicode character.

<!-- TODO: markdown comments -->



### Identifiers and reserved keywords


An identifier is a string that is not a reserved keyword
and follows these rules:

1. It starts with a Latin or Greek letter (not underscore).
2. It contains Latin letters, Greek letters, underscore, digit,
3. It ends with Latin letters, Greek letters, underscore, digit, or a subscript.

<pre>
identifier = [latin|greek][latin|greek|_|digit]*[latin|greek|_|digit|subcript]?
</pre>

Here are some examples of good identifiers:
`a`, `a_4`, `a₄`, `alpha`, `α`.

The reserved keywords are shown in [](#tab:keywords).



<style>
.keywords {
    column-count: 4;
    text-align: left;
}
</style>

<center>
    <col1 id='keywords' class='float_bottom keywords'
        figure-id='tab:keywords'
        figure-caption='Reserved keywords'>
        <k>and</k>
        <k>between</k>
        <k>bottom</k>
        <k>emptyset</k>
        <k>Int</k>
        <k>lowersets</k>
        <k>maximals</k>
        <k>minimals</k>
        <k>Nat</k>
        <k>Rcomp</k>
        <k>top</k>
        <k>uncertain</k>
        <k>uppersets</k>
        <k>abstract</k>
        <k>add_bottom</k>
        <k>approx</k>
        <k>approx_lower</k>
        <k>approx_upper</k>
        <k>approxu</k>
        <k>assert_empty</k>
        <k>assert_equal</k>
        <k>assert_geq</k>
        <k>assert_gt</k>
        <k>assert_leq</k>
        <k>assert_lt</k>
        <k>assert_nonempty</k>
        <k>by</k>
        <k>canonical</k>
        <k>catalogue</k>

        <k>choose</k>
        <k>code</k>
        <k>compact</k>
        <k>constant</k>
        <k>coproduct</k>

        <k>eversion</k>
        <k>flatten</k>
        <r><code>for</code></r>
        <k>ignore</k>
        <k>ignore_resources</k>
        <k>implemented-by</k>
        <k>implements</k>
        <k>instance</k>
        <k>interface</k>
        <k>lowerclosure</k>
        <k>mcdp</k>

        <k>namedproduct</k>
        <k>poset</k>
        <k>powerset</k>
        <k>product</k>
        <f><code>provided</code></f>
        <kf>provides</kf>
        <r><code>required</code></r>
        <kr>requires</kr>

        <k>solve</k>
        <k>solve_f</k>
        <k>solve_r</k>
        <k>specialize</k>
        <k>take</k>
        <k>template</k>
        <k>upperclosure</k>
        <r><code>using</code></r>
        <k>variable</k>
</col1>
</center>

<center>
    <col1 id='' class='keywords'
        figure-id='tab:deprecated'
        figure-caption='Deprecated keywords'>
        <s></s>
        <s><br/>deprecated</s>
        <k>ceilsqrt</k>
        <k>set-of</k>
        <k>any-of</k>
        <k>load</k>
        <k>s</k>
        <k>finite_poset</k>
        <k>dp</k>
        <k>from</k>
        <k>sub</k>

        <k>dptype</k>
        <k>interval</k>

        <s></s>
        <s><br/>no need to be keyword</s>
        <k>pow</k>
        <k>dimensionless</k>
        <s></s>
        <s><br/>experimental</s>
        <k>addmake</k>
        <k>mcdp-type</k>
        <k>new</k>
    </col1>
</center>

## Syntactic equivalents {#sub:unicode-operators}

MCDPL allows a number of Unicode glyphs as an abbreviations of a few operators ([](#tab:glyphs)).

### Superscripts

Every occurrence of a superscript of the digit *d* is interpreted as a power
<q>`^d`</q>. It is syntactically equivalent to write <q>`x^2`</q> or
<q>`x²`</q>.


<col2 id='glyphs' class='labels-row1'
    figure-id='tab:glyphs'
    figure-caption='Unicode glyphs and syntactically equivalent ASCII'>
    <s>Unicode</s> <s>ASCII</s>
    <s><k>≽</k> or <k>≥</k></s>    <k>&gt;=</k>
    <s><k>≼</k> or <k>≤</k></s>    <k>&lt;=</k>
    <k>·</k>    <k>*</k>
    <k>⟨⋯⟩</k>  <k>&lt;⋯&gt;</k>
    <k>⊤</k>    <k>Top</k>
    <k>⊥</k>    <k>Bottom</k>
    <k>℘</k>    <k>powerset</k>
    <k>±</k> <k>+-</k>

    <s><k>↔</k> or <k>⟷</k></s>
     <k>&lt;--&gt;</k>

    <s><kf>↤</kf> or <kf>⟻</kf></s>
    <s><kf>&lt;--|</kf></s>

    <s><kr>↦</kr> or <kr>⟼</kr></s>
    <kr>|--&gt;</kr>

    <code>∅</code> <code>Emptyset</code>

    <code>ℕ</code> <code>Nat</code>
    <code>ℝ</code> <code>Rcomp</code>
    <code>ℤ</code> <code>Int</code>
    <code>↑</code> <code>upperclosure</code>
    <code>↓</code> <code>lowerclosure</code>

    <code>a¹</code> <code>a^1</code>
    <code>a²</code> <code>a^2</code>
    <code>a³</code> <code>a^3</code>
    <code>a⁴</code> <code>a^4</code>
    <code>a⁵</code> <code>a^5</code>
    <code>a⁶</code> <code>a^6</code>
    <code>a⁷</code> <code>a^7</code>
    <code>a⁸</code> <code>a^8</code>
    <code>a⁹</code> <code>a^9</code>

    <code>a₀</code> <code>a_0</code>
    <code>a₁</code> <code>a_1</code>
    <code>a₂</code> <code>a_2</code>
    <code>a₃</code> <code>a_3</code>
    <code>a₄</code> <code>a_4</code>
    <code>a₅</code> <code>a_5</code>
    <code>a₆</code> <code>a_6</code>
    <code>a₇</code> <code>a_7</code>
    <code>a₈</code> <code>a_8</code>
    <code>a₉</code> <code>a_9</code>
    <!-- <code>&#36;</code> <code>USD</code> -->
    <code>×</code> <code>x</code>
</col2>

<style>
    #glyphs {
        column-count: 3;
        td:nth-child(3) {
            text-align: left;
            vertical-align: top;
        }
    }
</style>

### Subscripts
<!--
These are the subscripts supported:

    x₀ x₁ x₂ x₃ x₄ x₅ x₆ x₇ x₈ x₉ -->

For subscripts, every occurrence of a subscript of the digit *d* is converted to
the fragment <q>`_d`</q>.  It is syntactically equivalent to write <q>`_1`</q> or <q>`₁`</q>.

Subscripts can only occur at the end of an identifier: ``a₁`` is valid, while
<q>`a₁b`</q> is not a valid identifier.


### Use of Greek letters as part of identifiers  {#sub:unicode-in-identifiers}

MCDPL allows to use some Unicode characters, Greek letters and subscripts, also
in identifiers and expressions. For example, it is equivalent to write
<q>`alpha_1`</q> and <q>`α₁`</q>.

Every Greek letter is converted to its name. It is syntactically equivalent to
write <q>`alpha_material`</q> or <q>`α_material`</q>.

Greek letter names are only considered at the beginning of the identifier and
only if they are followed by a non-word character. For example, the identifer
<q>`alphabet`</q> is not converted to <q>`αbet`</q>.

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
