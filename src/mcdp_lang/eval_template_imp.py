from contracts import contract
from contracts.utils import raise_desc
from mcdp_lang.parse_actions import add_where_information
from mcdp_lang.parts import CDPLanguage
from mcdp_lang.utils_lists import unwrap_list
from mocdp.comp.template_for_nameddp import TemplateForNamedDP
from mocdp.exceptions import DPInternalError, DPSemanticError
from mcdp_lang.namedtuple_tricks import recursive_print


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

    r = recursive_print(r)
    raise_desc(DPInternalError, 'Invalid template.', r=r)

def eval_template_load(r, context):
    assert isinstance(r, CDP.LoadTemplate)
    assert isinstance(r.load_arg, (CDP.TemplateName, CDP.TemplateNameWithLibrary))

    arg = r.load_arg

    if isinstance(arg, CDP.TemplateNameWithLibrary):
        assert isinstance(arg.library, CDP.LibraryName), arg
        assert isinstance(arg.name, CDP.TemplateName), arg

        name = arg.name.value
        libname = arg.library.value

        library = context.load_library(libname)
        return library.load_template(name)

    if isinstance(arg, CDP.TemplateName):
        name = r.load_arg.value
        return context.load_template(name)

    raise NotImplementedError(r)

def eval_template_spec(r, context):

    assert isinstance(r, CDP.TemplateSpec)
    from .eval_ndp_imp import eval_ndp

    params_ops = unwrap_list(r.params)
    if params_ops:
        keys = params_ops[::2]
        values =  params_ops[1::2]
        keys = [_.value for _ in keys]

        if len(set(keys)) != len(keys):
            msg = 'Repeated parameters.'
            raise_desc(DPSemanticError, msg, keys=keys)

        values = [eval_ndp(_, context) for _ in values]
        d = dict(zip(keys, values))
        params = d
    else:
        params = {}
    ndpt = r.ndpt

#     libname = context.get_default_library_name()
#     if libname is None:
#         raise ValueError()
#     print('libname: %s' % libname)
    return TemplateForNamedDP(parameters=params, template_code=ndpt)

