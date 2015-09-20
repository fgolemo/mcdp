# -*- coding: utf-8 -*-
from .configuration import *
from .defs import *
from .dp_series import *

from .dp_bat import *

def jobs_comptests(context):
    # configuration
    from conf_tools import GlobalConfig
    GlobalConfig.global_load_dir("mocdp.configs")

    # tests
    from . import unittests

    # instantiation
    from comptests import jobs_registrar
    from mocdp.configuration import get_conftools_mocdp_config
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

