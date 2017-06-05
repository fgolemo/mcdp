# -*- coding: utf-8 -*-
from mcdp.exceptions import mcdp_dev_warning

from contracts.utils import check_isinstance

from .dealing_with_special_letters import greek_letters, subscripts, subscripts_utf8, greek_letters_utf8
from .parse_actions import (divide_parse_action,
                            funshortcut1m, mult_inv_parse_action, mult_parse_action, parse_pint_unit,
                            plus_inv_parse_action, plus_parse_action, resshortcut1m,
                            space_product_parse_action, rvalue_minus_parse_action, fvalue_minus_parse_action,
                            dp_model_statements_parse_action, add_where_to_empty_list, copy_expr_remove_action, integer_fraction_from_superscript)
from .parts import CDPLanguage
from .pyparsing_bundled import (
    CaselessLiteral, Combine, Forward, Group, Keyword, Literal, MatchFirst,
    NotAny, OneOrMore, Optional, ParserElement, Word, ZeroOrMore, alphanums,
    alphas, dblQuotedString, nums, oneOf, opAssoc, operatorPrecedence,
    sglQuotedString, FollowedBy, QuotedString, ParseExpression)
from .syntax_utils import (
    COMMA, L, O, S, SCOLON, SCOMMA, SLPAR, SRPAR, keyword, sp, spk)
from .utils_lists import make_list


ParserElement.enablePackrat()


K = Keyword
SL = lambda x: S(L(x))


CDP = CDPLanguage


class SyntaxBasics(object):
    # numbers
    number = Word(nums).setName('number')
    point = Literal('.')
    e = CaselessLiteral('E')
    plus = Literal('+')
    plusorminus = plus | Literal('-')
    nonneg_integer = sp(Combine(O(plus) + number),
                        lambda t: int(t[0])).setName('nonneg_integer')
    integer = sp(Combine(O(plusorminus) + number),
                 lambda t: int(t[0])).setName('integer')

    # Note that '42' is not a valid float...
    floatnumber = sp((Combine(O(plusorminus) + number + point + O(number) + O(e + integer)) |
                      Combine(O(plusorminus) + number + e + number)),
                     lambda t: float(t[0])).setName('floatnumber')

    integer_or_float = sp(floatnumber | integer,
                          lambda t: CDP.ValueExpr(t[0])).setName('integer_or_float')

def not_any_of_these(ks):
    return NotAny(MatchFirst([Keyword(_) for _ in ks]))

class SyntaxIdentifiers(object):
    # unfortunately this needs to be maintained manually
    keywords = [
        'sum',
        'pi',
        'π',
        'e',
        'constant',
        'take',
        'load',
        'compact',
        'required',
        'provides',
        'abstract',
        'dp',
        'mcdp',
        'template',
        'interface',
        'sub',
        'for',
        'instance',
        'provided',
        'requires',
        'implemented-by',
        'using',
        'by',
        'catalogue',
        'set-of',
        'mcdp-type',
        'dptype',
        'Nat',
        'Int',
        'pow',
        'approx',
        'approx_lower',
        'approx_upper',
        'Top',
        'Bottom',
        'Maximals',
        'Minimals',
        'finite_poset',
        'choose',
        'flatten',
        'new',
        'canonical',
        'UpperSets',
        'LowerSets',  # TODO
        'specialize',
        'Uncertain',
        'Interval',
        'product',
        'namedproduct',
        'S',
        'any-of',
        'coproduct',
        'ignore',
        'addmake',
        'approxu',
        # 'import',
        'from',
        'upperclosure',
        'lowerclosure',
        'code',
        'assert_equal',
        'assert_leq',
        'assert_geq',
        'assert_lt',
        'assert_gt',
        'assert_empty',
        'assert_nonempty',
        'ignore_resources',
        'dimensionless',
        'EmptySet',
        'solve',
        'solve_r',
        'solve_f',
        'ceilsqrt',
        'Rcomp',
        'variable',
        'eversion',
        'poset',
        'add_bottom',
        'implements',
        'and',
    ]

    # remember to .copy() this otherwise things don't work
    
    not_keyword = not_any_of_these(keywords)

    """
        Valid identifiers:

            first letter:  _a-Z_a-z + the greek letters
            middle letter: _a-Z_a-z1-9 + the greek letters
            last letter:   _a-Z_a-z1-9 + the greek letters + subscripts

        plus the constraint that it cannot be a keyword.

        Greek letters are translated to their spelling.
        Subscripts are translated; from '₁' to '_1'.
    """

    greek = list(greek_letters_utf8.values())
    subs = list(subscripts_utf8.values())
    first_letter = list('_' + alphas) + greek
    mid_letter = list('_' + alphanums) + greek
    last_letter = list('_' + alphanums) + greek + subs

    combined = Combine(
        oneOf(first_letter) + O(Word(''.join(mid_letter))) + O(oneOf(last_letter)))
    _identifier = sp(combined,
                     lambda t: decode_identifier(t[0]))

    _idn = (not_keyword.copy() + _identifier).setName('identifier except keywords')

    @staticmethod
    def get_idn():
        return SyntaxIdentifiers._idn.copy()

    normal_identifier_first = '_' + alphas
    normal_identifier_middle = '_' + alphanums
    normal_identifier = Combine(oneOf(list(normal_identifier_first)) +
                                O(Word(normal_identifier_middle)))

    @staticmethod
    def get_identifier_unconstrained():
        """
            Returns an identifier expression ([_a-Z(_a-z1-9)*]
            This can be a keyword.
        """
        return SyntaxIdentifiers.normal_identifier.copy()


def decode_identifier(s):
    ''' Decodes '₁' to '_1', Ψ to Psi '''
    check_isinstance(s, bytes)
    for part, letter in greek_letters.items():
        part = part.encode('utf8')
        letter = letter.encode('utf8')
        while letter in s:
            s = s.replace(letter, part)
    for num, glyph in subscripts.items():
        glyph = glyph.encode('utf8')
        if glyph in s:
            s = s.replace(glyph, '_%d' % num)
    return s


class Syntax(object):
    
    __version__ = '1.0.0'
    __changelog__ = {   
        '1.0.0': "Arbitrarily named on 2017-02-01."
    }
    __deprecated__ = """
        - `new`, to be replaced by instance 
        - The old catalogue definition.
    """

    # An expression that evaluates to a constant value
    constant_value = Forward()
    definitely_constant_value = Forward()  # no variable refs allowed
    # An expression that evaluates to a resource reference
    rvalue = Forward()
    # An expression that evaluates to a function reference
    fvalue = Forward()
    # An expression that evaluates to a Poset
    space = Forward()
    # An expression that evaluates to a NamedDP
    ndpt_dp_rvalue = Forward()

    # An expression that evaluates to a Template
    template = Forward()

    get_idn = SyntaxIdentifiers.get_idn
    # a quoted string
    quoted = sp(dblQuotedString | sglQuotedString, lambda t: t[0][1:-1])

    lbrace = sp(L('{'), lambda t: CDP.LBRACE(t[0]))
    rbrace = sp(L('}'), lambda t: CDP.RBRACE(t[0]))
    lbracket = sp(L('['), lambda t: CDP.LBRACKET(t[0]))
    rbracket = sp(L(']'), lambda t: CDP.RBRACKET(t[0]))
#     lpar = sp(L('('), lambda t: CDP.LPAR(t[0]))
#     rpar = sp(L(')'), lambda t: CDP.RPAR(t[0]))
#
    python_style_multiline1 = QuotedString(quoteChar='"""', escChar='\\', unquoteResults=True, multiline=True)
    python_style_multiline2 = QuotedString(quoteChar="'''", escChar='\\', unquoteResults=True, multiline=True)
    python_style_multiline = python_style_multiline1 | python_style_multiline2
    comment_string_simple = sp(copy_expr_remove_action(quoted),
                               lambda t: CDP.CommentStringSimple(t[0]))
    comment_string_complex = sp(copy_expr_remove_action(python_style_multiline),
                                lambda t: CDP.CommentStringTriple(t[0]))

    comment_model = sp(comment_string_simple | comment_string_complex,
                       lambda t: CDP.CommentModel(t[0]))
    comment_con = sp(copy_expr_remove_action(comment_string_simple), lambda t: CDP.CommentCon(t[0]))
    comment_fun = sp(copy_expr_remove_action(comment_string_simple), lambda t: CDP.CommentFun(t[0]))
    comment_res = sp(copy_expr_remove_action(comment_string_simple), lambda t: CDP.CommentRes(t[0]))
    comment_var = sp(copy_expr_remove_action(comment_string_simple), lambda t: CDP.CommentVar(t[0]))

    placeholder = SL('[') + SL('[') - (SyntaxIdentifiers.get_identifier_unconstrained()
                                       | quoted) + SL(']') + SL(']')

    dpname_placeholder = sp(copy_expr_remove_action(placeholder), lambda t: CDP.Placeholder_dpname(t[0]))
    constant_placeholder = sp(copy_expr_remove_action(placeholder), lambda t: CDP.Placeholder_constant(t[0]))
    rvalue_placeholder = sp(copy_expr_remove_action(
        placeholder), lambda t: CDP.Placeholder_rvalue(t[0]))
    fvalue_placeholder = sp(copy_expr_remove_action(
        placeholder), lambda t: CDP.Placeholder_fvalue(t[0]))
    fname_placeholder = sp(copy_expr_remove_action(
        placeholder), lambda t: CDP.Placeholder_fname(t[0]))
    rname_placeholder = sp(copy_expr_remove_action(
        placeholder), lambda t: CDP.Placeholder_rname(t[0]))
    space_placeholder = sp(copy_expr_remove_action(
        placeholder), lambda t: CDP.Placeholder_poset(t[0]))
    ndpt_placeholder = sp(copy_expr_remove_action(
        placeholder), lambda t: CDP.Placeholder_constant(t[0]))
    template_placeholder = sp(copy_expr_remove_action(
        placeholder), lambda t: CDP.Placeholder_template(t[0]))
    primitivedp_placeholder = sp(copy_expr_remove_action(
        placeholder), lambda t: CDP.Placeholder_primitivedp(t[0]))
    collection_placeholder = sp(copy_expr_remove_action(
        placeholder), lambda t: CDP.Placeholder_collection(t[0]))
    integer_placeholder = sp(copy_expr_remove_action(
        placeholder), lambda t: CDP.Placeholder_integer(t[0]))
    nonneg_integer_placeholder = sp(copy_expr_remove_action(
        placeholder), lambda t: CDP.Placeholder_nonneg_integer(t[0]))
    index_label_placeholder = sp(copy_expr_remove_action(
        placeholder), lambda t: CDP.Placeholder_index_label(t[0]))
    integer_or_float_placeholder = sp(copy_expr_remove_action(
        placeholder), lambda t: CDP.Placeholder_integer_or_float(t[0]))

    integer = SyntaxBasics.integer | integer_placeholder
    integer_or_float = SyntaxBasics.integer_or_float | integer_or_float_placeholder
    nonneg_integer = SyntaxBasics.nonneg_integer | nonneg_integer_placeholder

    REQUIRED_BY = sp((K('required') | K('req.') | K('r.')) - K('by'),
                     lambda _: CDP.RequiredByKeyword('required by'))
    mcdp_dev_warning('these variations are not tested')
    PROVIDED_BY = sp((K('provided') | K('prov.') | K('p.')) - K('by'),
                     lambda _: CDP.ProvidedByKeyword('provided by'))

    IMPLEMENTS = keyword('implements', CDP.ImplementsKeyword)
    PROVIDED = keyword('provided', CDP.ProvidedKeyword)
    REQUIRED = keyword('required', CDP.RequiredKeyword)
    GEQ = spk(L('>=') | L('≥') | L('≽'), CDP.geq)
    LEQ = spk(L('<=') | L('≤') | L('≼'), CDP.leq)
    PERCENT = spk(L('%'), CDP.percent)
    MAPSTO = spk(L('⟼') ^ L('↦') ^ L('|->') ^ L('|-->') ^ L('|--->') ^ L('|---->') ^
                 L('->') ^ L('-->') ^ L('--->') ^ L('---->'),
                 CDP.MAPSTO)
    MAPSFROM = spk(L('↤') ^ L('⟻') ^
                   L('<-|') ^  L('<--|') ^ L('<---|') ^ L('<----|') ^
                   L('<-') ^ L('<--') ^ L('<---') ^ L('<----'),
                   CDP.MAPSFROM).setName('⟻')
    LEFTRIGHTARROW = spk(L('↔') | L('⟷') | L('<->') | L('<-->') | L('<--->')
                         | L('<---->'), CDP.LEFTRIGHTARROW)

    EQ = spk(L('='), CDP.eq)
    DOT = spk(L('.'), CDP.DotPrep)
    PLUS = spk(L('+'), CDP.plus)
    MINUS = spk(L('-'), CDP.minus)
    PLUS_OR_MINUS = spk(L('+-') | L('±'), CDP.plus_or_minus)
    
    TIMES = spk(L('*') | L('·'), CDP.times)
    BAR = spk(L('/'), CDP.bar)

    SUM = spk(L('sum') | L('∑'), CDP.sum)


    # "call"
#     C = lambda x, b: x.setResultsName(b)

    # optional whitespace
    ow = S(ZeroOrMore(L(' ')))

    # do not load earlier
    from .syntax_codespec import get_code_spec_expr
    code_spec = get_code_spec_expr()

    pint_alphas = Word(alphas + '$')
    pint_alphas.setWhitespaceChars(' ')
    
    cant_be_units_kw = SyntaxIdentifiers.keywords + ['x']
    cant_be_units = not_any_of_these(cant_be_units_kw)
    pint_unit_base = cant_be_units + pint_alphas
    pint_unit_base.setWhitespaceChars(' ')
    pint_unit_power = ((L('^') + Word(nums)) | L('¹') | L('²') |  L('³') |  L('⁴') | \
        L('⁵') | L('⁶') | L('⁷') | L('⁸') | L('⁹'))
    pint_unit_simple = pint_unit_base + O(pint_unit_power)
    pint_unit_simple.setWhitespaceChars(' ')
    pint_unit_connector = L('/') | L('*')

    pint_unit = ((Keyword('1') | pint_unit_simple) + ZeroOrMore(pint_unit_connector + pint_unit_simple))
    space_pint_unit = sp(pint_unit.copy(), parse_pint_unit)

    space_dimensionless = sp(Keyword('dimensionless'),
                             lambda _: CDP.RcompUnit('m/m'))

    library_name = sp(SyntaxIdentifiers.get_identifier_unconstrained(),
                      lambda t: CDP.LibraryName(t[0]))

    # load <name>
    LOAD = spk(K('load') ^ L('`'), CDP.LoadKeyword)

    posetname = sp(SyntaxIdentifiers.get_identifier_unconstrained(),
                   lambda t: CDP.PosetName(t[0]))

    posetname_with_library = sp(library_name + L('.') + posetname,
                                lambda t: CDP.PosetNameWithLibrary(library=t[0], glyph=t[1], name=t[2]))

    load_poset = sp(LOAD - (posetname_with_library | posetname),
                    lambda t: CDP.LoadPoset(keyword=t[0], load_arg=t[1]))
#
    # UpperSets(<poset>)
    UPPERSETS = keyword('UpperSets', CDP.UpperSetsKeyword)
    space_uppersets = sp(UPPERSETS + SLPAR + space + SRPAR,
                         lambda t: CDP.MakeUpperSets(t[0], t[1]))

    LOWERSETS = keyword('LowerSets', CDP.LowerSetsKeyword)
    space_lowersets = sp(LOWERSETS + SLPAR + space + SRPAR,
                         lambda t: CDP.MakeLowerSets(t[0], t[1]))

    # finite_poset {
    #     a
    #     b  c  d  e
    #
    #     a <= b <= c
    #   }
    #
    # evaluates to CDP.FinitePoset

    FINITE_POSET = keyword('finite_poset', CDP.FinitePosetKeyword)
    POSET = keyword('poset', CDP.FinitePosetKeyword)
    
    # we allow 'e' to be an element
    deny = list(set(SyntaxIdentifiers.keywords) - set(['e']))
    poset_el = ( not_any_of_these(deny) + SyntaxIdentifiers._identifier)
        
    finite_poset_el = sp(poset_el, 
                         lambda t: CDP.FinitePosetElement(t[0]))

    finite_poset_chain_leq = sp(finite_poset_el + ZeroOrMore(LEQ + finite_poset_el),
                                lambda t: CDP.FinitePosetChainLEQ(make_list(t)))

    finite_poset_chain_geq = sp(finite_poset_el + OneOrMore(GEQ + finite_poset_el),
                                lambda t: CDP.FinitePosetChainGEQ(make_list(t)))

    space_finite_poset = sp((FINITE_POSET | POSET) - lbrace +
                            ZeroOrMore(
                                finite_poset_chain_leq ^ finite_poset_chain_geq) + rbrace,
                            lambda t: CDP.FinitePoset(t[0], t[1], make_list(t[2:-1], where=t[0].where), t[-1]))

    ADD_BOTTOM = keyword('add_bottom', CDP.AddBottomKeyword)

    add_bottom = sp(ADD_BOTTOM + space,
                    lambda t: CDP.AddBottom(t[0], t[1]))

    space_powerset_keyword = spk(L('℘') | L('set-of'), CDP.PowerSetKeyword)
    space_powerset = sp(space_powerset_keyword - L('(') + space + L(')'),
                        lambda t: CDP.PowerSet(t[0], t[1],
                                               t[2], t[3]))

    PRODUCTWITHLABELS = spk(
        K('product') | K('namedproduct'), CDP.ProductKeyword)
    space_product_label = sp(
        get_idn(), lambda t: CDP.ProductWithLabelsLabel(t[0]))
    space_product_entry = space_product_label + SCOLON + space
    space_product_with_labels = sp(PRODUCTWITHLABELS + SLPAR + O(space_product_entry) +
                                   ZeroOrMore(
                                       SCOMMA + space_product_entry) + SRPAR,
                                   lambda t:
                                   CDP.ProductWithLabels(keyword=t[0],
                                                         entries=make_list(t[1:])))

    COPRODUCT = keyword('coproduct', CDP.SpaceCoproductKeyword)
    space_coproduct_label = sp(
        get_idn(), lambda t: CDP.ProductWithLabelsLabel(t[0]))
    space_coproduct_entry = space_product_label + SCOLON + space
    space_coproduct = sp(COPRODUCT + SLPAR +
                         O(space) + ZeroOrMore(SCOMMA + space) + SRPAR,
                         lambda t:
                         CDP.SpaceCoproduct(keyword=t[0],
                                            entries=make_list(t[1:])))

    INTERVAL = keyword('Interval', CDP.IntervalKeyword)

    space_interval = sp(INTERVAL - SLPAR + constant_value + SCOMMA + constant_value + SRPAR,
                        lambda t: CDP.SpaceInterval(keyword=t[0], a=t[1], b=t[2]))

    space_nat = sp(Keyword('Nat') | Keyword('ℕ'), lambda t: CDP.Nat(t[0]))
    space_int = sp(Keyword('Int') | Keyword('ℤ'), lambda t: CDP.Int(t[0]))
    space_rcomp = sp(
        Keyword('Rcomp') | Keyword('ℝ'), lambda t: CDP.Rcomp(t[0]))

    space_single_element_poset_tag = sp(
        get_idn(), lambda t: CDP.SingleElementPosetTag(t[0]))
    space_single_element_poset_keyword = keyword(
        'S', CDP.SingleElementPosetKeyword)
    space_single_element_poset = sp(space_single_element_poset_keyword +
                                    SLPAR + space_single_element_poset_tag +
                                    SRPAR,
                                    lambda t: CDP.SingleElementPoset(t[0], t[1]))

    space_operand = (
        space_pint_unit
        | space_powerset
        | space_nat
        | space_int
        | space_rcomp
        | load_poset
        | code_spec
        | space_finite_poset
        | space_uppersets
        | space_lowersets
        | space_interval
        | space_product_with_labels
        | space_single_element_poset
        | space_coproduct
        | space_placeholder
        | space_dimensionless
        | add_bottom
    )

    PRODUCT = sp(L('x') | L('×'), lambda t: CDP.product(t[0]))
    space << operatorPrecedence(space_operand, [
        (PRODUCT, 2, opAssoc.LEFT, space_product_parse_action),
    ])  # , lpar='(', rpar=')')
#     space_prec

    nat_constant = sp(K('nat') - L(':') - nonneg_integer,
                      lambda t: CDP.NatConstant(t[0], t[1], t[2]))

    nat_constant2 = sp(nonneg_integer.copy().setName('nonneg_integer'),
                       lambda t: CDP.NatConstant(None, None, t[0]))

    rcomp_constant = sp(copy_expr_remove_action(SyntaxBasics.floatnumber),
                        lambda t: CDP.RcompConstant(float(t[0])))

    int_constant = sp(K('int') - L(':') - integer,
                      lambda t: CDP.IntConstant(t[0], t[1], t[2]))

    fname = sp(get_idn(), lambda t: CDP.FName(t[0])) | fname_placeholder
    rname = sp(get_idn(), lambda t: CDP.RName(t[0])) | rname_placeholder
    vname = sp(get_idn(), lambda t: CDP.VName(t[0])) | rname_placeholder

    PROVIDES = keyword('provides', CDP.ProvideKeyword)
    REQUIRES = keyword('requires', CDP.RequireKeyword)
    VARIABLE = keyword('variable', CDP.VarStatementKeyword)

    # These two are only used in catalogue - there is the generalization below
    fun_statement = sp(PROVIDES + fname + lbracket + space + rbracket + O(comment_fun),
                       lambda t: CDP.FunStatement(keyword=t[0],
                                                  fname=t[1],
                                                  lbracket=t[2],
                                                  unit=t[3],
                                                  rbracket=t[4],
                                                  comment=t[5] if len(t) == 6 else None))

    res_statement = sp(REQUIRES + rname + lbracket + space + rbracket + O(comment_res),
                       lambda t: CDP.ResStatement(keyword=t[0],
                                                  rname=t[1],
                                                  lbracket=t[2],
                                                  unit=t[3],
                                                  rbracket=t[4],
                                                  comment=t[5] if len(t) == 6 else None))

    var_list = sp(vname + ZeroOrMore(COMMA + vname),
                  lambda t: make_list(t))

# 'keyword vnames lbracket unit rbracket')
    var_statement = sp(VARIABLE - var_list + lbracket + space + rbracket + O(comment_var),
                       lambda t: CDP.VarStatement(
                           keyword=t[0], vnames=t[1], lbracket=t[2],
                           unit=t[3], rbracket=t[4],
                           comment=t[5] if len(t) == 6 else None))

    # import statements:
    #    from libname import a, b
#     IMPORT = spk(L('import'), CDP.ImportSymbolsKeywordImport)
#     FROM = spk(L('from'), CDP.ImportSymbolsKeywordFrom)
#     import_libname = sp(get_idn(), lambda t: CDP.ImportSymbolsLibname(t[0]))
#     import_symbol = sp(get_idn(), lambda t: CDP.ImportSymbolsSymbolname(t[0]))
#     import_statement = sp(FROM + import_libname +
#                           IMPORT + import_symbol + ZeroOrMore(SCOMMA + import_symbol),
#                           lambda t:
#                             CDP.ImportSymbols(keyword1=t[0],
#                                               keyword2=t[2],
#                                               libname=t[1],
# symbols=make_list(t[3:], where=t[2].where)))

    valuewithunit_numbers = sp(integer_or_float + S(lbracket) + space + S(rbracket),
                               lambda t: CDP.SimpleValue(t[0], t[1]))
    constant_e = sp(L('e'), lambda t: CDP.SpecialConstant(t[0]))
    constant_pi = sp(L('π') | L('pi'), lambda t: CDP.SpecialConstant(t[0]))
    
    mcdp_dev_warning('dimensionless not tested')
    dimensionless = sp((L('[') + L(']')) ^ Keyword('dimensionless'),
                       lambda _: CDP.RcompUnit('m/m'))

    valuewithunits_numbers_dimensionless = sp(integer_or_float + dimensionless,
                                              lambda t: CDP.SimpleValue(t[0], t[1]))
    pint_unit_simple.setWhitespaceChars(' ')
    valuewithunit_number_with_units = sp(integer_or_float + space_pint_unit,
                                         lambda t: CDP.SimpleValue(t[0], t[1]))
    integer_or_float.setWhitespaceChars(' ')
    space_pint_unit.setWhitespaceChars(' ')
    valuewithunit_number_with_units = valuewithunit_number_with_units.setWhitespaceChars(
        ' ')  # no newline
    # Top <space>
    TOP_LITERAL = 'Top'
    TOP = spk(K(TOP_LITERAL) | K('⊤'), CDP.TopKeyword)

    valuewithunit_top = sp(TOP - space,
                           lambda t: CDP.Top(t[0], t[1]))

    # Bottom <space>
    BOTTOM_LITERAL = 'Bottom'
    BOTTOM = spk(K(BOTTOM_LITERAL) | K('⊥'), CDP.BottomKeyword)

    valuewithunit_bottom = sp(BOTTOM + space,
                              lambda t: CDP.Bottom(t[0], t[1]))

    # Minimals <space>
    MINIMALS = keyword('Minimals', CDP.MinimalsKeyword)
    valuewithunit_minimals = sp(MINIMALS + space,
                                lambda t: CDP.Minimals(t[0], t[1]))

    # Maximals <space>
    MAXIMALS = keyword('Maximals', CDP.MaximalsKeyword)
    valuewithunit_maximals = sp(MAXIMALS + space,
                                lambda t: CDP.Maximals(t[0], t[1]))

    valuewithunit = (
        valuewithunit_top |
        valuewithunit_bottom |
        valuewithunit_minimals |
        valuewithunit_maximals |
        valuewithunit_numbers |
        valuewithunits_numbers_dimensionless |
        valuewithunit_number_with_units
    )

    # TODO: change

    ndpname = sp(get_idn() | quoted, lambda t: CDP.NDPName(t[0]))

    ndpname_with_library = sp(library_name + L('.') + ndpname,
                              lambda t: CDP.NDPNameWithLibrary(library=t[0], glyph=t[1], name=t[2]))

    ndpt_load = sp(LOAD - (ndpname_with_library | ndpname | SLPAR - ndpname - SRPAR),
                   lambda t: CDP.LoadNDP(t[0], t[1]))

    # <dpname> = ...
    dpname_real = sp(get_idn(), lambda t: CDP.DPName(t[0]))
    dpname = dpname_real | dpname_placeholder

    dptypename = sp(get_idn(), lambda t: CDP.DPTypeName(t[0]))

    # instance <type>
    INSTANCE = keyword('instance', CDP.InstanceKeyword)
    dpinstance_from_type = sp(INSTANCE - ((SLPAR - ndpt_dp_rvalue - SRPAR) | ndpt_dp_rvalue),
                              lambda t: CDP.DPInstance(t[0], t[1]))

    # new Name ~= instance `Name
#     NEW = keyword('new', CDP.FromLibraryKeyword)
#     dpinstance_from_library_shortcut = \
#         sp(NEW - (ndpname_with_library | ndpname | (SLPAR - ndpname + SRPAR)),
#            lambda t: CDP.DPInstanceFromLibrary(t[0], t[1]))

    dpinstance_expr = dpinstance_from_type # | dpinstance_from_library_shortcut

    SUB = keyword('sub', CDP.SubKeyword)
    setname_ndp_instance1 = sp(SUB - dpname - EQ - dpinstance_expr,
                               lambda t: CDP.SetNameNDPInstance(t[0], t[1], t[2], t[3]))

    setname_ndp_instance2 = sp(dpname + EQ + dpinstance_expr,
                               lambda t: CDP.SetNameNDPInstance(None, t[0], t[1], t[2]))

    MCDPTYPE = keyword('mcdp', CDP.MCDPTypeKeyword)
    setname_ndp_type1 = sp(MCDPTYPE - dptypename - EQ - ndpt_dp_rvalue,
                           lambda t: CDP.SetNameMCDPType(t[0], t[1], t[2], t[3]))

    setname_ndp_type2 = sp(dptypename - EQ - ndpt_dp_rvalue,
                           lambda t: CDP.SetNameMCDPType(None, t[0], t[1], t[2]))

    # For pretty printing
    ELLIPSIS = keyword('...', CDP.Ellipsis)

    setname_generic_var = sp(get_idn(),
                             lambda t: CDP.SetNameGenericVar(t[0]))
    # a = ...
    # a = 10 g
    # TODO: use specific constant name
    constant_name = sp(get_idn(), lambda t: CDP.CName(t[0]))
    CONSTANT = keyword('constant', CDP.ConstantKeyword)
#     RESOURCE = keyword('resource', CDP.ResourceKeyword)
#     FUNCTION = keyword('function', CDP.FunctionKeyword)

    setname_constant1 = sp(CONSTANT +
                           constant_name + EQ + (rvalue)
                           + S(O(comment_con)),
                           lambda t: CDP.SetNameConstant(t[0], t[1], t[2], t[3]))
    setname_constant2a = sp(CONSTANT +
                           constant_name + EQ + (definitely_constant_value)
                           + S(O(comment_con)),
                           lambda t: CDP.SetNameConstant(t[0], t[1], t[2], t[3]))
    setname_constant2b = sp( 
                           constant_name + EQ + (definitely_constant_value)
                           + S(O(comment_con)),
                           lambda t: CDP.SetNameConstant(None, t[0], t[1], t[2]))

    constant_value_divided = sp('1' + BAR + constant_value,
                                lambda t: CDP.ConstantDivision(t[0],t[1],t[2]))

    setname_constant = setname_constant1 | setname_constant2a | setname_constant2b
    setname_rvalue = sp(setname_generic_var + EQ + (ELLIPSIS | rvalue)
                        + S(O(comment_res)),
                        lambda t: CDP.SetNameRValue(t[0], t[1], t[2]))

    setname_fvalue = sp(setname_generic_var + EQ + fvalue
                        + S(O(comment_fun)),
                        lambda t: CDP.SetNameFValue(t[0], t[1], t[2]))

    variable_ref = sp(get_idn(),
                      lambda t: CDPLanguage.VariableRef(t[0]))

    ndpt_dp_variable_ref = sp(get_idn(),
                              lambda t: CDP.VariableRefNDPType(t[0]))

    # solve( <0 g>, `model )
    # solve_F
    SOLVE_F = (keyword('solve', CDP.SolveModelKeyword)
               | keyword('solve_f', CDP.SolveModelKeyword))
    solve_model = sp(SOLVE_F - SLPAR - constant_value - SCOMMA - ndpt_dp_rvalue - SRPAR,
                     lambda t: CDP.SolveModel(keyword=t[0], f=t[1], model=t[2]))

    SOLVE_R = keyword('solve_r', CDP.SolveRModelKeyword)
    solve_r_model = sp(SOLVE_R - SLPAR - constant_value - SCOMMA - ndpt_dp_rvalue - SRPAR,
                       lambda t: CDP.SolveRModel(keyword=t[0], r=t[1], model=t[2]))

    # <> or ⟨⟩
    OPEN_BRACE = spk(L('<') | L('⟨'), CDP.OpenBraceKeyword)
    CLOSE_BRACE = spk(L('>') | L('⟩'), CDP.CloseBraceKeyword)
    tuple_of_constants = sp(OPEN_BRACE - O(constant_value -
                                           ZeroOrMore(COMMA - constant_value)) - CLOSE_BRACE,
                            lambda t: CDP.MakeTuple(t[0], make_list(list(t)[1:-1], where=t[0].where), t[-1]))

    ASTERISK = spk(L('*'), CDP.asterisk)
    rvalue_sum_over_resources = sp(SUM + rname + REQUIRED_BY + ASTERISK,
                            lambda t: CDP.SumResources(t[0],t[1],t[2],t[3]))
    fvalue_sum_over_functions = sp(SUM + fname + PROVIDED_BY + ASTERISK,
                            lambda t: CDP.SumFunctions(t[0],t[1],t[2],t[3]))    

    rvalue_make_tuple = sp(OPEN_BRACE - rvalue -
                           ZeroOrMore(COMMA - rvalue) - CLOSE_BRACE,
                           lambda t: CDP.MakeTuple(t[0], make_list(list(t)[1:-1]), t[-1]))

    EMPTYSET = keyword('EmptySet', CDP.EmptySetKeyword)
    constant_emptyset = sp(EMPTYSET + space,
                           lambda t: CDP.EmptySet(t[0], t[1]))

    # TODO: how to express empty typed list? "{g}"
    collection_of_constants1 = sp(S(L('{')) + constant_value +
                                  ZeroOrMore(
                                      COMMA - constant_value) - S(L('}')),
                                  lambda t: CDP.Collection(make_list(list(t))))
    collection_of_constants2 = valuewithunit_minimals

    collection_of_constants = (collection_of_constants1
                               | collection_of_constants2
                               | constant_emptyset
                               | collection_placeholder)

    # upperclosure <set>
    # ↑ <set>
    upper_set_from_collection_keyword = spk(K('upperclosure') | L('↑'),
                                            CDP.UpperSetFromCollectionKeyword)
    upper_set_from_collection = sp(upper_set_from_collection_keyword - collection_of_constants,
                                   lambda t: CDP.UpperSetFromCollection(t[0], t[1]))

    # lowerclosure <set>

    lower_set_from_collection_keyword = spk(K('lowerclosure') | L('↓'),
                                            CDP.LowerSetFromCollectionKeyword)
    lower_set_from_collection = sp(lower_set_from_collection_keyword - collection_of_constants,
                                   lambda t: CDP.LowerSetFromCollection(t[0], t[1]))

    # <space> : identifier
    # `plugs : european
#     short_identifiers = Word(nums + alphas + '_')

    short_identifiers = Combine(
        oneOf(list('_' + alphas)) + Optional(Word('_' + alphanums)))

    space_custom_value1 = sp(space + L(":") + (L('*') | short_identifiers | SyntaxBasics.integer_or_float),
                             lambda t: CDP.SpaceCustomValue(t[0], t[1], t[2]))

    # assert_equal(v1, v2)
    # assert_leq(v1, v2)
    # assert_geq(v1, v2)
    # assert_lt(v1, v2)
    # assert_gt(v1, v2)
    # assert_nonempty(v1, v2)
    # assert_empty(v1, v2)

    ASSERT_EQUAL = keyword('assert_equal', CDP.AssertEqualKeyword)
    ASSERT_LEQ = keyword('assert_leq', CDP.AssertLEQKeyword)
    ASSERT_GEQ = keyword('assert_geq', CDP.AssertGEQKeyword)
    ASSERT_LT = keyword('assert_lt', CDP.AssertLTKeyword)
    ASSERT_GT = keyword('assert_gt', CDP.AssertGTKeyword)
    ASSERT_NONEMPTY = keyword('assert_nonempty', CDP.AssertNonemptyKeyword)
    ASSERT_EMPTY = keyword('assert_empty', CDP.AssertEmptyKeyword)

    assert_equal = sp(ASSERT_EQUAL - SLPAR - constant_value - SCOMMA - constant_value - SRPAR,
                      lambda t: CDP.AssertEqual(keyword=t[0], v1=t[1], v2=t[2]))
    assert_leq = sp(ASSERT_LEQ - SLPAR - constant_value - SCOMMA - constant_value - SRPAR,
                    lambda t: CDP.AssertLEQ(keyword=t[0], v1=t[1], v2=t[2]))
    assert_geq = sp(ASSERT_GEQ - SLPAR + constant_value - SCOMMA - constant_value - SRPAR,
                    lambda t: CDP.AssertGEQ(keyword=t[0], v1=t[1], v2=t[2]))
    assert_lt = sp(ASSERT_LT - SLPAR + constant_value - SCOMMA - constant_value - SRPAR,
                   lambda t: CDP.AssertLT(keyword=t[0], v1=t[1], v2=t[2]))
    assert_gt = sp(ASSERT_GT - SLPAR + constant_value - SCOMMA - constant_value - SRPAR,
                   lambda t: CDP.AssertGT(keyword=t[0], v1=t[1], v2=t[2]))
    assert_nonempty = sp(ASSERT_NONEMPTY - SLPAR - constant_value - SRPAR,
                         lambda t: CDP.AssertNonempty(keyword=t[0], value=t[1]))
    assert_empty = sp(ASSERT_EMPTY - SLPAR - constant_value - SRPAR,
                      lambda t: CDP.AssertEmpty(keyword=t[0], value=t[1]))

    asserts = (assert_equal | assert_leq | assert_leq | assert_geq
               | assert_lt | assert_gt | assert_nonempty | assert_empty)

    constant_value_op = (
        collection_of_constants
        | tuple_of_constants
        | nat_constant
        | int_constant
        | upper_set_from_collection
        | lower_set_from_collection
        | solve_model
        | solve_r_model
        | space_custom_value1
        | valuewithunit
        | variable_ref
        | asserts
        | constant_placeholder
        | constant_emptyset
        | rcomp_constant  # after valuewithunit
        | nat_constant2   # after valuewithunit and rcomp_constant
        | constant_pi
        | constant_e
    )
    definitely_constant_value_operand = (
        collection_of_constants
        | tuple_of_constants
        | nat_constant
        | int_constant
        | upper_set_from_collection
        | lower_set_from_collection
        | solve_model
        | solve_r_model
        | space_custom_value1
        | valuewithunit
        | asserts
        | constant_placeholder
        | constant_emptyset
        | rcomp_constant  # after valuewithunit
        | nat_constant2  # after valuewithunit and rcomp_constant
        | constant_pi
        | constant_e

    )
    definitely_constant_value << definitely_constant_value_operand
#
#     definitely_constant_value << operatorPrecedence(definitely_constant_value_operand, [
#         (TIMES, 2, opAssoc.LEFT, mult_parse_action),
#         (BAR, 2, opAssoc.LEFT, divide_parse_action),
#         (PLUS, 2, opAssoc.LEFT, plus_parse_action),
#         (MINUS, 2, opAssoc.LEFT, rvalue_minus_parse_action),
#     ])

    constant_value << constant_value_op

    rvalue_resource_simple = sp(dpname + DOT - rname,
                                lambda t: CDP.Resource(s=t[2], keyword=t[1], dp=t[0]))

    rvalue_resource_fancy = sp(rname + REQUIRED_BY - dpname,
                               lambda t: CDP.Resource(s=t[0], keyword=t[1], dp=t[2]))

    rvalue_resource = rvalue_resource_simple ^ rvalue_resource_fancy

    # Just <name>
    rvalue_new_function1 = sp(get_idn(),
                              lambda t: CDPLanguage.VariableRef(t[0]))

    # provided <name>
    rvalue_new_function2 = sp(PROVIDED - fname,
                              lambda t: CDP.NewFunction(t[0], t[1]))

    rvalue_new_function = rvalue_new_function2 | rvalue_new_function1
    # any-of(set)
    ANYOF = keyword('any-of', CDP.AnyOfKeyword)
    rvalue_any_of = sp(ANYOF - SLPAR - constant_value - SRPAR,
                       lambda t: CDP.AnyOfRes(t[0], t[1]))
    fvalue_any_of = sp(ANYOF - SLPAR - constant_value - SRPAR,
                       lambda t: CDP.AnyOfFun(t[0], t[1]))

    # Uncertain(<lower>, <upper>)
    UNCERTAIN = keyword('Uncertain', CDP.UncertainKeyword)
    constant_uncertain1 = sp(UNCERTAIN + SLPAR + rvalue + SCOMMA + rvalue + SRPAR,
                            lambda t: CDP.UncertainConstant(keyword=t[0], lower=t[1], upper=t[2]))

    BETWEEN = keyword('between', CDP.BetweenKeyword)
    BETWEEN_AND = keyword('and', CDP.BetweenAndKeyword)

    constant_between = sp(BETWEEN + fvalue + BETWEEN_AND + fvalue,
                        lambda t: CDP.ConstantBetween(t[0], t[1], t[2], t[3]))

    rvalue_between = sp(BETWEEN + rvalue + BETWEEN_AND + rvalue,
                        lambda t: CDP.RValueBetween(t[0], t[1], t[2], t[3]))
    fvalue_between = sp(BETWEEN + fvalue + BETWEEN_AND + fvalue,
                        lambda t: CDP.FValueBetween(t[0], t[1], t[2], t[3]))
     
    constant_plus_or_minus = sp(constant_value + PLUS_OR_MINUS + constant_value + NotAny(PERCENT),
                              lambda t: CDP.ConstantPlusOrMinus(t[0], t[1], t[2]))
    fvalue_plus_or_minus = sp(constant_value + PLUS_OR_MINUS + constant_value + NotAny(PERCENT),
                              lambda t: CDP.FValuePlusOrMinus(t[0], t[1], t[2]))
    rvalue_plus_or_minus = sp(constant_value + PLUS_OR_MINUS + constant_value + NotAny(PERCENT),
                              lambda t: CDP.RValuePlusOrMinus(t[0], t[1], t[2]))
    rvalue_uncertain = sp(UNCERTAIN + SLPAR + rvalue + SCOMMA + rvalue + SRPAR,
                          lambda t: CDP.UncertainRes(keyword=t[0], lower=t[1], upper=t[2]))

    constant_plus_or_minus_percent = sp(constant_value + PLUS_OR_MINUS + integer_or_float + PERCENT,
                              lambda t: CDP.ConstantPlusOrMinusPercent(t[0], t[1], t[2], t[3]))
    fvalue_plus_or_minus_percent = sp(constant_value + PLUS_OR_MINUS + integer_or_float + PERCENT,
                              lambda t: CDP.FValuePlusOrMinusPercent(t[0], t[1], t[2], t[3]))
    rvalue_plus_or_minus_percent = sp(constant_value + PLUS_OR_MINUS + integer_or_float + PERCENT,
                              lambda t: CDP.RValuePlusOrMinusPercent(t[0], t[1], t[2], t[3]))    
    fvalue_uncertain = sp(UNCERTAIN + SLPAR + fvalue + SCOMMA + fvalue + SRPAR,
                          lambda t: CDP.UncertainFun(keyword=t[0], lower=t[1], upper=t[2]))

    constant_uncertain2 = constant_between | constant_plus_or_minus | constant_plus_or_minus_percent
    



    # take(<a, b>, 0)
    TAKE = keyword('take', CDP.TakeKeyword)

    rvalue_tuple_indexing = sp(TAKE + SLPAR + rvalue + SCOMMA +
                               integer + SRPAR,
                               lambda t: CDP.TupleIndexRes(keyword=t[0], value=t[1], index=t[2]))

    lf_tuple_indexing = sp(TAKE + SLPAR + fvalue + SCOMMA +
                           integer + SRPAR,
                           lambda t: CDP.TupleIndexFun(keyword=t[0], value=t[1], index=t[2]))

    index_label = sp(
        get_idn(), lambda t: CDP.IndexLabel(t[0])) | index_label_placeholder
    # rvalue instead of rvalue_new_function

    # approximating a resource

    # approx(<rvalue>, 5g)
    APPROXRES = keyword('approx', CDP.ApproxKeyword)
    rvalue_approx_step = sp(APPROXRES - SLPAR + rvalue + SCOMMA + constant_value + SRPAR,
                            lambda t: CDP.ApproxStepRes(t[0], t[1], t[2]))

    # approxu(<rvalue>, 5g)
    APPROXU = keyword('approxu', CDP.ApproxUKeyword)
    rvalue_approx_u = sp(APPROXU - SLPAR + rvalue + SCOMMA + constant_value + SRPAR,
                         lambda t: CDP.ApproxURes(t[0], t[1], t[2]))

    # take(provided a, sub)
    rvalue_label_indexing2 = sp(TAKE + SLPAR + rvalue + SCOMMA + index_label + SRPAR,
                                lambda t: CDP.ResourceLabelIndex(keyword=t[0],
                                                                 rvalue=t[1], label=t[2]))

    # (provided a).label
    rvalue_label_indexing3 = sp(SLPAR + rvalue + SRPAR + DOT + index_label,
                                lambda t: CDP.ResourceLabelIndex(keyword=t[1],
                                                                 rvalue=t[0], label=t[2]))

    # TODO: remove
    ICOMMA = L('..')
    rvalue_label_indexing = sp(rvalue_new_function + ICOMMA + index_label,
                               lambda t: CDP.ResourceLabelIndex(keyword=t[1],
                                                                rvalue=t[0], label=t[2]))

    # TODO: remove
    fvalue_disambiguation_tag = sp(Combine(L('(') + L('f') + L(')')),
                                   lambda t: CDP.DisambiguationFunTag(t[0]))

    fvalue_disambiguation = sp(fvalue_disambiguation_tag + fvalue,
                               lambda t: CDP.DisambiguationFun(tag=t[0], fvalue=t[1]))

    fvalue_new_resource2 = sp(REQUIRED - rname,
                              lambda t: CDP.NewResource(t[0], t[1]))

    fvalue_new_resource = sp(get_idn(),
                             lambda t: CDPLanguage.VariableRef(t[0]))
#
#
#     fvalue_new_resource = sp(rname,
#                              lambda t: CDP.NewResource(None, t[0])) # XXX

    fvalue_label_indexing_ref = fvalue_new_resource2 | fvalue_new_resource
    fvalue_label_indexing = sp(fvalue_label_indexing_ref + ICOMMA + index_label,
                               lambda t: CDP.FunctionLabelIndex(keyword=t[1],
                                                                fvalue=t[0], label=t[2]))
    # take(provided a, sub)
    fvalue_label_indexing2 = sp(TAKE + SLPAR + fvalue + S(COMMA) + index_label + SRPAR,
                                lambda t: CDP.FunctionLabelIndex(keyword=t[0],
                                                                 fvalue=t[1], label=t[2]))

    # (provided a).label
    fvalue_label_indexing3 = sp(SLPAR + fvalue + SRPAR + DOT + index_label,
                                lambda t: CDP.FunctionLabelIndex(keyword=t[1],
                                                                 fvalue=t[0], label=t[2]))

    opname = sp(get_idn(), lambda t: CDP.GenericOperationName(t[0]))

    rvalue_generic_op_ops = sp(rvalue + ZeroOrMore(SCOMMA + rvalue),
                               lambda t: make_list(list(t)))

    # The ~FollowedBy is due to situations like this:
    #     >  line 26 >   power = power1 + power2 + power3
    #     >  line 27 >   (required in).watts >= power
    # which would be interpreted as power3(required in)
    rvalue_generic_op = sp(opname + SLPAR + rvalue_generic_op_ops + SRPAR
                           + ~FollowedBy(DOT),
                           lambda t: CDP.GenericOperationRes(t[0], t[1]))

    fvalue_generic_op_ops = sp(fvalue + ZeroOrMore(SCOMMA + fvalue),
                               lambda t: make_list(list(t)))
    fvalue_generic_op = sp(opname + SLPAR + fvalue_generic_op_ops + SRPAR
                           + ~FollowedBy(DOT),
                           lambda t: CDP.GenericOperationFun(t[0], t[1]))

    fvalue_simple = sp(dpname + DOT - fname,
                       lambda t: CDP.Function(dp=t[0], s=t[2], keyword=t[1]))

    fvalue_fancy = sp(fname + PROVIDED_BY - dpname,
                      lambda t: CDP.Function(dp=t[2], s=t[0], keyword=t[1]))

    fvalue_function = fvalue_simple | fvalue_fancy

    fvalue_maketuple = sp(OPEN_BRACE - fvalue + ZeroOrMore(COMMA + fvalue) + CLOSE_BRACE,
                          lambda t: CDP.MakeTuple(t[0], make_list(list(t)[1:-1]), t[-1]))

    # Fractions

    integer_fraction = sp(SyntaxBasics.integer + S(L('/')) + SyntaxBasics.integer,
                          lambda t: CDP.IntegerFraction(num=t[0], den=t[1]))

    integer_fraction_one = sp(copy_expr_remove_action(SyntaxBasics.integer),
                              lambda t: CDP.IntegerFraction(num=int(t[0]), den=1))

    rat_power_exponent = integer_fraction | integer_fraction_one

    POW = keyword('pow', CDP.PowerKeyword)

    rvalue_power_expr_1 = sp(POW - SLPAR - rvalue - SCOMMA - rat_power_exponent - SRPAR,
                             lambda t: CDP.Power(keyword=t[0], op1=t[1], exponent=t[2]))

    EXPONENT = spk(L('^'), CDP.exponent)

    # note: we cannot use "rvalue" because that makes the thing recursive
    rvalue_power_base = (rvalue_resource ^ rvalue_new_function) | (
        SLPAR + (rvalue_resource ^ rvalue_new_function) + SRPAR)
    rvalue_power_expr_2 = sp(rvalue_power_base + EXPONENT - rat_power_exponent,
                             lambda t: CDP.PowerShort(op1=t[0], glyph=t[1], exponent=t[2]))

    superscripts = sp(oneOf(['²', '³', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹']),
                      lambda t: integer_fraction_from_superscript(t[0]))

    rvalue_power_expr_3 = sp(rvalue_power_base + superscripts,
                             lambda t: CDP.PowerShort(op1=t[0], glyph=None,
                                                      exponent=t[1]))

    rvalue_power_expr = rvalue_power_expr_1 | rvalue_power_expr_2 | rvalue_power_expr_3

    constraint_expr_geq = sp(fvalue + GEQ - rvalue,
                             lambda t: CDP.Constraint(fvalue=t[0],
                                                      rvalue=t[2],
                                                      prep=t[1]))

    constraint_expr_leq = sp(rvalue +  LEQ - fvalue,
                             lambda t: CDP.Constraint(fvalue=t[2],
                                                      rvalue=t[0],
                                                      prep=t[1]))

    constraint_invalid1a = sp(fvalue   + GEQ + fvalue,
                              lambda t: CDP.ConstraintInvalidFF(fvalue1=t[0],
                                                                fvalue2=t[2],
                                                                prep=t[1]))
    constraint_invalid2a = sp(rvalue + GEQ + rvalue,
                              lambda t: CDP.ConstraintInvalidRR(rvalue1=t[0],
                                                                rvalue2=t[2],
                                                                prep=t[1]))
    constraint_invalid1b = sp(fvalue  + LEQ + fvalue,
                              lambda t: CDP.ConstraintInvalidFF(fvalue1=t[0],
                                                                fvalue2=t[2],
                                                                prep=t[1]))
    constraint_invalid2b = sp(rvalue  + LEQ + rvalue,
                              lambda t: CDP.ConstraintInvalidRR(rvalue1=t[0],
                                                                rvalue2=t[2],
                                                                prep=t[1]))
    constraint_invalid3a = sp(rvalue  + GEQ + fvalue,
                              lambda t: CDP.ConstraintInvalidSwapped(rvalue=t[0],
                                                                     fvalue=t[
                                  2],
                                  prep=t[1]))

    constraint_invalid3b = sp(fvalue   + LEQ + rvalue,
                              lambda t: CDP.ConstraintInvalidSwapped(rvalue=t[2],
                                                                     fvalue=t[
                                  0],
                                  prep=t[1]))

    constraint_invalid = (constraint_invalid1a
                          ^ constraint_invalid2a
                          ^ constraint_invalid3a
                          ^ constraint_invalid1b
                          ^ constraint_invalid2b
                          ^ constraint_invalid3b
                          )

    USING = keyword('using', CDP.UsingKeyword)
    fun_shortcut1 = sp(PROVIDES  +  fname + USING - dpname,
                       lambda t: CDP.FunShortcut1(provides=t[0],
                                                  fname=t[1],
                                                  prep_using=t[2],
                                                  name=t[3]))

    FOR = keyword('for', CDP.ForKeyword)

    one_or_more_rnames = sp(rname + ZeroOrMore(COMMA + rname),
                            lambda t: make_list(list(t)))

    one_or_more_fnames = sp(fname + ZeroOrMore(COMMA + fname),
                            lambda t: make_list(list(t)))

    res_shortcut4 = sp(REQUIRES  + one_or_more_rnames + S(O(comment_res)),
                       lambda t: CDP.ResShortcut4(t[0], t[1]))

    fun_shortcut5 = sp(PROVIDES   + one_or_more_fnames + lbracket + space + rbracket + O(comment_fun),
                       lambda t: CDP.FunShortcut5(keyword=t[0],
                                                  fnames=t[1],
                                                  lbracket=t[2],
                                                  unit=t[3],
                                                  rbracket=t[4],
                                                  comment=t[5] if len(t) == 6 else None))

    res_shortcut5 = sp(REQUIRES + one_or_more_rnames + lbracket + space + rbracket + O(comment_res),
                       lambda t: CDP.ResShortcut5(keyword=t[0],
                                                  rnames=t[1],
                                                  lbracket=t[2],
                                                  unit=t[3],
                                                  rbracket=t[4],
                                                  comment=t[5] if len(t) == 6 else None))

    fun_shortcut4 = sp(PROVIDES + one_or_more_fnames + S(O(comment_fun)),
                       lambda t: CDP.FunShortcut4(t[0], t[1]))

    res_shortcut1 = sp(REQUIRES  + rname + FOR - dpname,
                       lambda t: CDP.ResShortcut1(t[0], t[1], t[2], t[3]))

    fun_shortcut2 = sp(PROVIDES +  fname   + (LEQ | EQ) - fvalue,
                       lambda t: CDP.FunShortcut2(t[0], t[1], t[2], t[3]))

    res_shortcut2 = sp(REQUIRES   + rname  + (GEQ | EQ) - rvalue,
                       lambda t: CDP.ResShortcut2(t[0], t[1], t[2], t[3]))

    fun_shortcut3 = sp(PROVIDES  + one_or_more_fnames + USING + dpname,
                       lambda t: funshortcut1m(provides=t[0],
                                               fnames=t[1],
                                               prep_using=t[2],
                                               name=t[3]))

    IGNORE_RESOURCES = sp(K('ignore_resources'), CDP.IgnoreResourcesKeyword)
    ndpt_ignore_resources = sp(IGNORE_RESOURCES - SLPAR - one_or_more_rnames
                               + SRPAR + ndpt_dp_rvalue,
                               lambda t: CDP.IgnoreResources(keyword=t[0],
                                                             rnames=t[1],
                                                             dp_rvalue=t[2]))

    res_shortcut3 = sp(REQUIRES  + one_or_more_rnames + FOR + dpname,
                       lambda t: resshortcut1m(requires=t[0],
                                               rnames=t[1],
                                               prep_for=t[2],
                                               name=t[3]))

    IGNORE = keyword('ignore', CDP.IgnoreKeyword)
    ignore_fun = sp(IGNORE + fvalue_function,
                    lambda t: CDP.IgnoreFun(t[0], t[1]))
    ignore_res = sp(IGNORE + rvalue_resource,
                    lambda t: CDP.IgnoreRes(t[0], t[1]))
    implements_statement = sp(IMPLEMENTS + ndpt_dp_rvalue,
                              lambda t: CDP.Implements(t[0], t[1]) )
    line_expr = (
        setname_ndp_instance1 |
        setname_ndp_instance2 |
        implements_statement |
        ((constraint_expr_geq ^ constraint_expr_leq) | constraint_invalid)
        ^
        (setname_constant ^ (
            setname_rvalue ^
            setname_fvalue ^

            setname_ndp_type1 ^
            setname_ndp_type2))
        #                  ^ fun_statement ^ res_statement ^
        ^ fun_shortcut1 ^ fun_shortcut2
        ^ res_shortcut1 ^ res_shortcut2 ^ res_shortcut3 ^ fun_shortcut3
        ^ res_shortcut4
        ^ fun_shortcut4
        ^ res_shortcut5
        ^ fun_shortcut5
        ^ var_statement
        ^ ignore_res
        ^ ignore_fun) + ow
    line_expr = line_expr

    # This is for syntax highlighting only (mcdp_web/renderdoc/highlight.py",
    # line 424)
    dp_model_statements = sp(OneOrMore(line_expr),
                             lambda t: CDP.ModelStatements(make_list(list(t))))

    MCDPTOKEN = keyword('mcdp', CDP.MCDPKeyword)
#     MCDPTOKEN.leaveWhitespace()
    ndpt_dp_model_statements = sp(ZeroOrMore(line_expr),
                                  dp_model_statements_parse_action)

    def ndpt_dp_model_parse(tokens):  # @NoSelf
        if len(tokens) == 5:
            keyword, lbrace, comment, statements, rbrace = tokens
        else:
            keyword, lbrace, statements, rbrace = tokens
            comment = None

        statements = add_where_to_empty_list(statements)

        return CDP.BuildProblem(keyword=keyword, lbrace=lbrace, comment=comment,
                                statements=statements, rbrace=rbrace)

    ndpt_dp_model = sp(MCDPTOKEN
                       - lbrace
#                        + ow - O(comment_model)
                       - O(comment_model)
                       - ndpt_dp_model_statements
                       - rbrace,
                       ndpt_dp_model_parse)
#     ndpt_dp_model.leaveWhitespace()

    # load
    primitivedp_name = sp(get_idn(), lambda t: CDP.FuncName(t[0]))  # XXX
    primitivedp_load = sp(
        LOAD - primitivedp_name, lambda t: CDP.LoadDP(t[0], t[1]))

    primitivedp_expr = (primitivedp_load | code_spec)

    simple_dp_model_stats = sp(ZeroOrMore(fun_statement | res_statement),
                               lambda t: make_list(list(t)))

    DPTOKEN = keyword('dp', CDP.DPWrapToken)
    IMPLEMENTEDBY = keyword('implemented-by', CDP.ImplementedbyKeyword)
    ndpt_simple_dp_model = sp(DPTOKEN -
                              S(L('{')) -
                              simple_dp_model_stats -
                              IMPLEMENTEDBY -
                              primitivedp_expr -
                              S(L('}')),
                              lambda t: CDP.DPWrap(token=t[0], statements=t[1],
                                                   prep=t[2], impl=t[3]))

    entry = rvalue
    imp_name = sp(get_idn(), lambda t: CDP.ImpName(t[0]))
    col_separator = L('|') | L('│')  # box drawing

    catalogue_entry_constant = sp(copy_expr_remove_action(constant_value),
                                  lambda t: CDP.CatalogueEntryConstant(t[0]))
    catalogue_entry_constant_uncertain = sp(copy_expr_remove_action(constant_uncertain2),
                                  lambda t: CDP.CatalogueEntryConstantUncertain(t[0]))
    
    catalogue_entry =catalogue_entry_constant_uncertain |  catalogue_entry_constant  # order important 
    catalogue_entry_list = catalogue_entry + ZeroOrMore(COMMA + catalogue_entry)
    
    catalogue_func = sp(catalogue_entry_list.copy(),
                        lambda t: CDP.CatalogueFunc(make_list(list(t))))
    catalogue_res = sp(catalogue_entry_list.copy(),
                       lambda t: CDP.CatalogueRes(make_list(list(t))))
    catalogue_row2 = sp(catalogue_func + MAPSFROM - imp_name - MAPSTO - catalogue_res,
                        lambda t: CDP.CatalogueRowMapsfromto(t[0], t[1], t[2], t[3], t[4]))

    CATALOGUE = keyword('catalogue', CDP.FromCatalogueKeyword)

#     'keyword lbrace funres table rbrace')
    ndpt_catalogue2a = sp(CATALOGUE +
                         lbrace
                         + comment_model
                         + # now we know
                         simple_dp_model_stats +
                         ZeroOrMore(catalogue_row2 + S(ow)) +
                         rbrace,
                         lambda t: CDP.Catalogue2(t[0], t[2], t[3], make_list(list(t[4:-1]),
                                                                              where=t[-1].where),
                                                  t[-1]))
    ndpt_catalogue2b = sp(CATALOGUE +
                         lbrace
                         # no comment
                         + simple_dp_model_stats
                         + # now we don't know beacuse of catalogu3
                         ZeroOrMore(catalogue_row2 + S(ow)) +
                         rbrace,
                         lambda t: CDP.Catalogue2(t[0], t[1], t[2], make_list(list(t[3:-1]),
                                                                              where=t[-1].where),
                                                  t[-1]))
    ndpt_catalogue2 = ndpt_catalogue2a | ndpt_catalogue2b

    # f <-> r
    catalogue_row3 = sp(catalogue_func + LEFTRIGHTARROW + catalogue_res,
                        lambda t: CDP.CatalogueRow3(t[0], t[1], t[2]))

    ndpt_catalogue3 = sp(CATALOGUE +
                         lbrace +
                         simple_dp_model_stats +
                         ZeroOrMore(catalogue_row3) +
                         rbrace,
                         lambda t: CDP.Catalogue3(t[0], t[1], t[2], make_list(list(t[3:-1]), where=t[-1].where),
                                                  t[-1]))

    if True:
        catalogue_row = sp(imp_name +
                           ZeroOrMore(S(col_separator) + entry),
                           lambda t: make_list(list(t)))
        catalogue_table = sp(OneOrMore(catalogue_row),
                             lambda t: CDP.CatalogueTable(make_list(list(t))))


        ndpt_catalogue_dp = sp(CATALOGUE +
                               S(lbrace) +
                               simple_dp_model_stats +
                               catalogue_table +
                               S(rbrace),
                               lambda t: CDP.FromCatalogue(t[0], t[1], t[2]))
    # Example:
    #    choose(name: <dp>, name2: <dp>)
    CHOOSE = keyword('choose', CDP.CoproductWithNamesChooseKeyword)
    ndpt_coproduct_with_names_name = \
        sp(get_idn(), lambda t: CDP.CoproductWithNamesName(t[0]))
    ndpt_coproduct_with_names_one = ndpt_coproduct_with_names_name + \
        SCOLON + (ndpt_dp_rvalue | dpinstance_expr)
    ndpt_coproduct_with_names = sp(CHOOSE - SLPAR - ndpt_coproduct_with_names_one
                                   -
                                   ZeroOrMore(
                                       SCOMMA + ndpt_coproduct_with_names_one)
                                   - SRPAR,
                                   lambda t: CDP.CoproductWithNames(keyword=t[0],
                                                                    elements=make_list(t[1:])))

    # Example:
    #   approx(mass,0%,0g,%)
    APPROX = keyword('approx', CDP.ApproxKeyword)
    ndpt_approx = sp(APPROX - SLPAR - fname - SCOMMA
                     - SyntaxBasics.integer_or_float - S(L('%'))
                     - SCOMMA - constant_value  # step
                     - SCOMMA - constant_value  # max value
                     - SRPAR - ndpt_dp_rvalue,
                     lambda t: CDP.ApproxDPModel(keyword=t[0],
                                                 name=t[1],
                                                 perc=t[2],
                                                 abs=t[3],
                                                 max_value=t[4],
                                                 dp=t[5]))

    # Example:
    # addmake(code module.func) mcdp { ... }
    ADDMAKE = keyword('addmake', CDP.AddMakeKeyword)
    from mcdp_lang.syntax_codespec import SyntaxCodeSpec
    addmake_what = sp(get_idn(), lambda t: CDP.AddMakeWhat(t[0]))
    ndpt_addmake = sp(ADDMAKE - SLPAR - addmake_what - SCOLON -
                      SyntaxCodeSpec.code_spec_simple - SRPAR
                      - ndpt_dp_rvalue,
                      lambda t: CDP.AddMake(keyword=t[0], what=t[1],
                                            code=t[2], dp_rvalue=t[3]))

    ABSTRACT = keyword('abstract', CDP.AbstractKeyword)
    ndpt_abstract = sp(ABSTRACT - ndpt_dp_rvalue,
                       lambda t: CDP.AbstractAway(t[0], t[1]))

    COMPACT = keyword('compact', CDP.CompactKeyword)
    ndpt_compact = sp(COMPACT - ndpt_dp_rvalue,
                      lambda t: CDP.Compact(t[0], t[1]))

    TEMPLATE = spk(L('template'), CDP.TemplateKeyword)
    INTERFACE = spk(L('interface'), CDP.TemplateKeyword)
    ndpt_template = sp((TEMPLATE | INTERFACE) - ndpt_dp_rvalue,
                       lambda t: CDP.MakeTemplate(t[0], t[1]))

    FLATTEN = keyword('flatten', CDP.FlattenKeyword)
    ndpt_flatten = sp(FLATTEN - ndpt_dp_rvalue,
                      lambda t: CDP.Flatten(t[0], t[1]))

    CANONICAL = keyword('canonical', CDP.FlattenKeyword)
    ndpt_canonical = sp(CANONICAL - ndpt_dp_rvalue,
                        lambda t: CDP.MakeCanonical(t[0], t[1]))

    # approx_lower(n, <dp>)
    APPROX_LOWER = keyword('approx_lower', CDP.ApproxLowerKeyword)
    ndpt_approx_lower = sp(APPROX_LOWER - SLPAR - integer -
                           SCOMMA - ndpt_dp_rvalue - SRPAR,
                           lambda t: CDP.ApproxLower(t[0], t[1], t[2]))

    APPROX_UPPER = keyword('approx_upper', CDP.ApproxUpperKeyword)
    ndpt_approx_upper = sp(APPROX_UPPER - SLPAR - integer -
                           SCOMMA - ndpt_dp_rvalue - SRPAR,
                           lambda t: CDP.ApproxUpper(t[0], t[1], t[2]))

    EVERSION = keyword('eversion', CDP.EversionKeyword)
    ndpt_eversion = sp(EVERSION + SLPAR + ndpname + SCOMMA + ndpt_dp_rvalue + SRPAR,
                       lambda t: CDP.Eversion(t[0], t[1], t[2]))
    ndpt_eversion = ndpt_eversion

    templatename = sp(get_idn() | quoted, lambda t: CDP.TemplateName(t[0]))
    templatename_with_library = sp(library_name + L('.') - templatename,
                                   lambda t: CDP.TemplateNameWithLibrary(library=t[0], glyph=t[1], name=t[2]))

    template_load = sp(LOAD - (templatename_with_library | templatename),  # | (SLPAR - templatename - SRPAR)),
                       lambda t: CDP.LoadTemplate(t[0], t[1]))

    template_spec_param_name = sp(
        get_idn(), lambda t: CDP.TemplateParamName(t[0]))
    template_spec_param = template_spec_param_name + S(L(':')) + ndpt_dp_rvalue
    parameters = O(template_spec_param) + \
        ZeroOrMore(SCOMMA + template_spec_param)
    LSQ = spk(L('['), CDP.LSQ)
    RSQ = spk(L(']'), CDP.RSQ)

    template_spec = sp(TEMPLATE - LSQ - Group(parameters) - RSQ
                       - ndpt_dp_rvalue,
                       lambda t: CDP.TemplateSpec(keyword=t[0],
                                                  params=make_list(
                                                      t[2], t[1].where),
                                                  ndpt=t[4]))

    # deriv(<name>, <ndp>)
    DERIV = keyword('deriv', CDP.DerivKeyword)

    # not sure about ndpname
    template_deriv = sp(DERIV - SLPAR - ndpname - SCOMMA - ndpt_dp_rvalue - SRPAR,
                        lambda t: CDP.Deriv(t[0], t[1], t[2]))

    template << (code_spec
                 | template_load
                 | template_spec
                 | template_deriv
                 | template_placeholder)  # mind the (...)

    SPECIALIZE = keyword('specialize', CDP.SpecializeKeyword)

    ndpt_specialize = sp(SPECIALIZE - LSQ - Group(parameters) - RSQ - template,
                         lambda t: CDP.Specialize(keyword=t[0],
                                                  params=make_list(
                                                      t[2], t[1].where),
                                                  template=t[4]))

    ndpt_dp_operand = (
        code_spec |
        ndpt_load |
        ndpt_simple_dp_model |
        ndpt_dp_model |
        ndpt_abstract |
        ndpt_template |
        ndpt_compact |
        ndpt_catalogue_dp | # to remove
        ndpt_catalogue2 |
        ndpt_catalogue3 |
        ndpt_approx_lower |
        ndpt_approx_upper |
        ndpt_approx |
        ndpt_coproduct_with_names |
        ndpt_flatten |
        ndpt_canonical |
        ndpt_dp_variable_ref |
        ndpt_specialize |
        ndpt_addmake |
        ndpt_ignore_resources |
        ndpt_eversion |
        ndpt_placeholder
    )

    ndpt_dp_rvalue << (ndpt_dp_operand | (SLPAR - ndpt_dp_operand - SRPAR))

    rvalue_operand = (
        rvalue_sum_over_resources 
        |
        rvalue_new_function
        ^ rvalue_new_function2
        ^ rvalue_resource
        ^ constant_value
        ^ rvalue_power_expr
        ^ rvalue_tuple_indexing
        ^ rvalue_make_tuple
        ^ rvalue_uncertain
        ^ rvalue_label_indexing
        ^ rvalue_label_indexing2
        ^ rvalue_label_indexing3
        ^ rvalue_any_of
        ^ rvalue_approx_step
        ^ rvalue_approx_u
        ^ rvalue_placeholder
        ^ rvalue_generic_op
        ^ rvalue_between
        ^ rvalue_plus_or_minus
        ^ rvalue_plus_or_minus_percent
    )

    rvalue << operatorPrecedence(rvalue_operand, [
        (TIMES, 2, opAssoc.LEFT, mult_parse_action),
        (BAR, 2, opAssoc.LEFT, divide_parse_action),
        (PLUS, 2, opAssoc.LEFT, plus_parse_action),
        (MINUS, 2, opAssoc.LEFT, rvalue_minus_parse_action),
    ])

    fvalue_operand = (
        fvalue_sum_over_functions 
        | constant_value
        ^ fvalue_simple
        ^ fvalue_fancy
        ^ fvalue_new_resource2
        ^ fvalue_maketuple
        ^ fvalue_uncertain
        ^ fvalue_disambiguation
        ^ fvalue_label_indexing
        ^ fvalue_label_indexing2
        ^ fvalue_label_indexing3
        ^ lf_tuple_indexing
        ^ fvalue_any_of
        ^ fvalue_placeholder
        ^ fvalue_generic_op
        ^ constant_value_divided
        ^ fvalue_between
        ^ fvalue_plus_or_minus
        ^ fvalue_plus_or_minus_percent 
    )

    # here we cannot use "|" because otherwise (cokode).id is not
    # parsedcorrectly

    # fvalue_operand = (SLPAR - fvalue_operands - SRPAR) ^ fvalue_operands

    fvalue << operatorPrecedence(fvalue_operand, [
        (TIMES, 2, opAssoc.LEFT, mult_inv_parse_action),
        (PLUS, 2, opAssoc.LEFT, plus_inv_parse_action),
        (MINUS, 2, opAssoc.LEFT, fvalue_minus_parse_action),
    ])

for x, expr in Syntax.__dict__.items():  # @UndefinedVariable
    #print x, type(expr)
    if isinstance(expr, ParseExpression):
        #print('setting name %s' % expr)
        expr.setName(x)

