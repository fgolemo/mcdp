# -*- coding: utf-8 -*-
__version__ = '1.1.0'

from .configuration import *
from . import posets
from . import dp

import numpy
numpy.seterr('raise')

def jobs_comptests(context):
    # configuration
    from conf_tools import GlobalConfig
    GlobalConfig.global_load_dir("mocdp")

    # tests
    from . import unittests

    from .posets import tests
    from .dp import tests  # @Reimport
    from .dp_report import tests  # @Reimport
    from .example_battery import tests  # @Reimport
    from .comp import tests  # @Reimport
    from .lang import tests  # @Reimport

    from mocdp.lang.tests.examples import define_tests
    define_tests(context)

    # instantiation
    from comptests import jobs_registrar
    jobs_registrar(context, get_conftools_mocdp_config())

# # have fun: ≤  ≥  ├─ ─┤ ≠ ⊂ ⊃ ° × ∩ ∪ ∨ ∧ ∞ ∉ ∈ ∃ ∀ → ± ·
#     ≤ \leq        ≥ \geq        ≡ \equiv
#     ≺ \prec        ≻ \succ        ∼ \sim
#     ≼ \preceq    ≽ \succeq    ≃ \simeq
#     ≪ \ll        ≫ \gg        ≍ \asymp
#     ⊂ \subset    ⊃ \supset    ≈ \approx
#     ⊆ \subseteq    ⊇ \supseteq    ≅ \cong
#     ⊑ \sqsubseteq    ⊒ \sqsupseteq    ⋈ \bowtie
#     ∈ \in        ∋ \ni        ∝ \propto
#     ⊢ \vdash    ⊣ \dashv    ⊨ \models
#     ⌣ \smile    ∣ \mid        ≐ \doteq
#     ⌢ \frown    ∥ \parallel    ⊥ \perp
#
#     ≮ \not<          ≯ \not>        ≠ \not=
#     ≰ \not\leq      ≱ \not\geq        ≢ \not\equiv
#     ⊀ \not\prec      ⊁ \not\succ        ≁ \not\sim
#     ⋠ \not\preceq      ⋡ \not\succeq        ≄ \not\simeq
#     ⊄ \not\subset      ⊅ \not\supset        ≉ \not\approx
#     ⊈ \not\subseteq      ⊉ \not\supseteq   ≇ \not\cong
#     ⋢ \not\sqsubseteq ⋣ \not\sqsupseteq ≭ \not\asymp

