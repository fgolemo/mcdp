# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import raise_desc, check_isinstance
from mcdp_lang.parse_actions import decorate_add_where
from mocdp.comp.template_for_nameddp import TemplateForNamedDP
from mocdp.exceptions import DPInternalError, DPSemanticError

from .namedtuple_tricks import recursive_print
from .parts import CDPLanguage
from .utils_lists import unwrap_list


CDP = CDPLanguage

@decorate_add_where
@contract(returns=TemplateForNamedDP)
def eval_template(r, context):  # @UnusedVariable
    cases = {
        CDP.LoadTemplate: eval_template_load,
        CDP.TemplateSpec: eval_template_spec,
        CDP.Deriv: eval_template_deriv,
    }

    for klass, hook in cases.items():
        if isinstance(r, klass):
            return hook(r, context)

    if True: # pragma: no cover    
        r = recursive_print(r)
        msg = 'Cannot interpret this as a template.'
        raise_desc(DPInternalError, msg, r=r)

def eval_template_deriv(r, context):
    from .eval_ndp_imp import eval_ndp

    check_isinstance(r, CDP.Deriv)
    
#     name = r.dpname.value
#     ndp = eval_ndp(r.ndp, context)
    
#     return ndp_deriv(r.ndp, name)

    raise NotImplementedError
    
    
def eval_template_load(r, context):
    from .eval_warnings import warnings_copy_from_child_make_nested2

    assert isinstance(r, CDP.LoadTemplate)
    assert isinstance(r.load_arg, (CDP.TemplateName, CDP.TemplateNameWithLibrary))

    arg = r.load_arg

    if isinstance(arg, CDP.TemplateNameWithLibrary):
        assert isinstance(arg.library, CDP.LibraryName), arg
        assert isinstance(arg.name, CDP.TemplateName), arg

        name = arg.name.value
        libname = arg.library.value

        library = context.load_library(libname)
        
        context2 = context.child()
        template = library.load_template(name, context2)
        
        msg = 'While loading template %r from library %r:' % (name, libname)
        warnings_copy_from_child_make_nested2(context, context2, r.where, msg)
        return template
        
    if isinstance(arg, CDP.TemplateName):
        
        context2 = context.child()
        name = r.load_arg.value
        template = context2.load_template(name)

        msg = 'While loading %r:' % (name)
        warnings_copy_from_child_make_nested2(context, context2, r.where, msg)

        return template

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

