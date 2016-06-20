from contracts import contract
from contracts.utils import raise_desc
from mcdp_lang.parse_actions import add_where_information
from mocdp.comp.template_for_nameddp import TemplateForNamedDP
from mocdp.exceptions import DPInternalError
from mcdp_lang.parts import CDPLanguage
from mcdp_lang.utils_lists import unwrap_list, get_odd_ops


CDP = CDPLanguage

@contract(returns=TemplateForNamedDP)
def eval_template(r, context):  # @UnusedVariable
    with add_where_information(r.where):
        cases = {
            CDP.LoadTemplate: eval_template_load,
            CDP.TemplateSpec: eval_template_spec,
        }

        for klass, hook in cases.items():
            if isinstance(r, klass):
                return hook(r, context)

    raise_desc(DPInternalError, 'Invalid template.', r=r)

def eval_template_load(r, context):
    assert isinstance(r, CDP.LoadCommand)
    name = r.load_arg.value
    return context.load_template(name)

def eval_template_spec(r, context):
    assert isinstance(r, CDP.TemplateSpec)
    from .eval_ndp_imp import eval_ndp

    params_ops = unwrap_list(r.params)
    if params_ops:
        keys = params_ops[::2]
        values =  params_ops[1::2]
        keys = [_.value for _ in keys]
        values = [eval_ndp(_, context) for _ in values]
        d = dict(zip(keys, values))
        params = d
    else:
        params = {}
    ndpt = r.ndpt
    return TemplateForNamedDP(parameters=params, template_code=ndpt)

